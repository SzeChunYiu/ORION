from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from nq_engine_a.augmentation import ConstraintProfile, generate_canonical_classes
from nq_engine_a.checkpoint import (
    CheckpointConfig,
    CheckpointTerminal,
    RangeManifestError,
    advance_child_level,
    build_donor_range_manifest,
    canonical_records_sha256,
    merge_donor_range_manifests,
)
from nq_engine_a.group import GroupSpec
from nq_engine_a.receipt import canonical_json_sha256

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_SHA256 = "059970ec26cd0767028a75aae92de70e53fbb0cb9f7439cff7696cc237351f69"
PARENT_SHA256 = "4de1ffc69d855e58f7f05fd11778dc3e46aca058ccd69b362f0a7b24a7766a10"
TEST_SOURCE_SHA256 = "a" * 64


@pytest.fixture(scope="module")
def frozen_parents() -> tuple[tuple[tuple[int, ...], ...], ...]:
    records = generate_canonical_classes(GroupSpec(5, 3), 3).records
    assert len(records) == 20
    assert canonical_records_sha256(records) == PARENT_SHA256
    return records


def frozen_config(**changes: object) -> CheckpointConfig:
    values: dict[str, object] = {
        "p": 5,
        "d": 3,
        "parent_level": 3,
        "target_level": 4,
        "range_start": 0,
        "range_stop": 20,
        "parent_records_sha256": PARENT_SHA256,
        "protocol_sha256": PROTOCOL_SHA256,
        "source_manifest_sha256": TEST_SOURCE_SHA256,
        "candidate_edge_budget": 7,
        "profile": ConstraintProfile(),
    }
    values.update(changes)
    return CheckpointConfig(**values)


def resign_checkpoint(payload: dict[str, object]) -> dict[str, object]:
    unsigned = {key: value for key, value in payload.items() if key != "checkpoint_sha256"}
    payload["checkpoint_sha256"] = canonical_json_sha256(unsigned)
    return payload


def test_prospective_protocol_is_hash_bound_schema_valid_and_non_authoritative() -> None:
    protocol_bytes = (ROOT / "TARGET_RESOURCE_PILOT_PROTOCOL.json").read_bytes()
    declared_hash = (ROOT / "TARGET_RESOURCE_PILOT_PROTOCOL.sha256").read_text().split()[0]
    import hashlib

    assert hashlib.sha256(protocol_bytes).hexdigest() == declared_hash == PROTOCOL_SHA256
    protocol = json.loads(protocol_bytes)
    schema = json.loads((ROOT / "schemas" / "target-resource-pilot.schema.json").read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(protocol, schema)
    assert protocol["execution"] == {
        "full_census_authorized": False,
        "lunarc_submission_authorized": False,
        "prospective_terminal": "PILOT_PLANNED_STOP__NOT_EXECUTED__CANNOT_CHECK",
        "scientific_terminal": "CANNOT_CHECK",
    }


def test_checkpoint_receipts_are_schema_valid_and_partial_state_is_not_consumable(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...],
) -> None:
    result = advance_child_level(GroupSpec(5, 3), frozen_parents, frozen_config(), edge_budget=7)
    assert result.terminal is CheckpointTerminal.CHECKPOINT_SAVED
    assert result.checkpoint is not None
    assert result.checkpoint.cursor_parent_index < 20
    assert result.full_range_coverage is False
    with pytest.raises(RuntimeError):
        _ = result.records

    schema = json.loads((ROOT / "schemas" / "checkpoint.schema.json").read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(result.to_dict(), schema)


def test_repeated_seven_edge_restarts_equal_uninterrupted_traversal_byte_for_byte(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...],
) -> None:
    spec = GroupSpec(5, 3)
    config = frozen_config()
    uninterrupted = advance_child_level(
        spec,
        frozen_parents,
        config,
        edge_budget=100_000,
        reference_uninterrupted=True,
    )
    assert uninterrupted.terminal is CheckpointTerminal.CHECKPOINT_LEVEL_COMPLETE

    restarted = advance_child_level(spec, frozen_parents, config, edge_budget=7)
    while restarted.terminal is CheckpointTerminal.CHECKPOINT_SAVED:
        assert restarted.checkpoint is not None
        restarted = advance_child_level(
            spec,
            frozen_parents,
            config,
            checkpoint=restarted.checkpoint.to_dict(),
            edge_budget=7,
        )
    assert restarted.terminal is CheckpointTerminal.CHECKPOINT_LEVEL_COMPLETE
    assert restarted.checkpoint is not None
    assert uninterrupted.checkpoint is not None
    assert restarted.checkpoint.to_dict() == uninterrupted.checkpoint.to_dict()
    assert restarted.to_dict() == uninterrupted.to_dict()
    assert restarted.records == uninterrupted.records


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload.__setitem__("protocol_sha256", "0" * 64),
        lambda payload: payload.__setitem__("parent_records_sha256", "1" * 64),
        lambda payload: payload["cursor"].__setitem__("parent_index", 21),
        lambda payload: payload["accepted_children"].append([[4, 4, 4]]),
        lambda payload: payload.__setitem__("checkpoint_sha256", "2" * 64),
    ],
)
def test_corrupted_checkpoint_configuration_digest_cursor_or_payload_fails_closed(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...], mutation
) -> None:
    first = advance_child_level(GroupSpec(5, 3), frozen_parents, frozen_config(), edge_budget=7)
    assert first.checkpoint is not None
    corrupted = copy.deepcopy(first.checkpoint.to_dict())
    mutation(corrupted)
    result = advance_child_level(
        GroupSpec(5, 3),
        frozen_parents,
        frozen_config(),
        checkpoint=corrupted,
        edge_budget=7,
    )
    assert result.terminal is CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH
    assert result.checkpoint is None
    assert result.full_range_coverage is False
    assert result.records_error == "checkpoint mismatch cannot support child records"


def test_resource_stop_keeps_cursor_and_counters_before_uncommitted_edge() -> None:
    spec = GroupSpec(2, 2)
    parents = ((),)
    parent_sha = canonical_records_sha256(parents)
    config = frozen_config(
        p=2,
        d=2,
        parent_level=0,
        target_level=1,
        range_start=0,
        range_stop=1,
        parent_records_sha256=parent_sha,
        profile=ConstraintProfile(forbid_k_disjoint=2, max_factor_states=1),
    )
    result = advance_child_level(spec, parents, config, edge_budget=7)
    assert result.terminal is CheckpointTerminal.CANNOT_CHECK_RESOURCE_BOUND
    assert result.checkpoint is not None
    assert result.checkpoint.cursor_parent_index == 1
    assert result.checkpoint.cursor_representative_index == 0
    assert result.checkpoint.candidate_edges == 2
    assert result.checkpoint.accepted_children == ()
    assert result.full_range_coverage is False
    with pytest.raises(RuntimeError):
        _ = result.records


def test_donor_range_split_merge_equals_uninterrupted_and_is_schema_valid(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...],
) -> None:
    spec = GroupSpec(5, 3)
    ranges = ((0, 8), (8, 16), (16, 20))
    manifests = tuple(
        build_donor_range_manifest(
            spec,
            frozen_parents,
            start,
            stop,
            parent_records_sha256=PARENT_SHA256,
            protocol_sha256=PROTOCOL_SHA256,
        )
        for start, stop in ranges
    )
    full = build_donor_range_manifest(
        spec,
        frozen_parents,
        0,
        20,
        parent_records_sha256=PARENT_SHA256,
        protocol_sha256=PROTOCOL_SHA256,
    )
    merged = merge_donor_range_manifests(
        spec,
        frozen_parents,
        manifests,
        expected_ranges=ranges,
        parent_records_sha256=PARENT_SHA256,
        protocol_sha256=PROTOCOL_SHA256,
    )
    assert merged["terminal"] == "RANGE_COMPLETE__NOT_GLOBAL"
    assert merged["global_coverage"] is False
    assert merged["scientific_terminal"] == "CANNOT_CHECK"
    assert merged["output_sha256"] == full["output_sha256"]
    assert merged["output_record_count"] == full["output_record_count"]
    assert merged["union_dedup_equal_to_uninterrupted"] is True

    schema = json.loads((ROOT / "schemas" / "donor-range-manifest.schema.json").read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    for manifest in manifests:
        jsonschema.validate(manifest, schema)


@pytest.mark.parametrize("case", ["overlap", "gap", "wrong_digest", "duplicate", "reordered"])
def test_donor_range_merge_rejects_overlap_gap_digest_duplicate_and_reordering(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...], case: str
) -> None:
    spec = GroupSpec(5, 3)
    expected_ranges = ((0, 8), (8, 16), (16, 20))
    manifests = [
        build_donor_range_manifest(
            spec,
            frozen_parents,
            start,
            stop,
            parent_records_sha256=PARENT_SHA256,
            protocol_sha256=PROTOCOL_SHA256,
        )
        for start, stop in expected_ranges
    ]
    hostile = copy.deepcopy(manifests)
    if case == "overlap":
        hostile[1]["range"][0] = 7
    elif case == "gap":
        hostile[1]["range"][0] = 9
    elif case == "wrong_digest":
        hostile[1]["output_sha256"] = "f" * 64
    elif case == "duplicate":
        hostile = [hostile[0], hostile[0], hostile[2]]
    else:
        hostile = [hostile[1], hostile[0], hostile[2]]
    with pytest.raises(RangeManifestError):
        merge_donor_range_manifests(
            spec,
            frozen_parents,
            hostile,
            expected_ranges=expected_ranges,
            parent_records_sha256=PARENT_SHA256,
            protocol_sha256=PROTOCOL_SHA256,
        )


def test_no_checkpoint_or_range_terminal_is_a_global_scientific_terminal(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...],
) -> None:
    checkpoint = advance_child_level(
        GroupSpec(5, 3), frozen_parents, frozen_config(), edge_budget=7
    ).to_dict()
    donor_range = build_donor_range_manifest(
        GroupSpec(5, 3),
        frozen_parents,
        0,
        8,
        parent_records_sha256=PARENT_SHA256,
        protocol_sha256=PROTOCOL_SHA256,
    )
    assert checkpoint["terminal"] == "CHECKPOINT_SAVED__NOT_GLOBAL"
    assert checkpoint["full_range_coverage"] is False
    assert checkpoint["scientific_terminal"] == "CANNOT_CHECK"
    assert donor_range["terminal"] == "RANGE_COMPLETE__NOT_GLOBAL"
    assert donor_range["global_coverage"] is False
    assert donor_range["scientific_terminal"] == "CANNOT_CHECK"


def test_self_signed_hostile_checkpoint_metadata_and_structures_fail_closed(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...],
) -> None:
    spec = GroupSpec(5, 3)
    partial = advance_child_level(spec, frozen_parents, frozen_config(), edge_budget=7)
    assert partial.checkpoint is not None
    base = partial.checkpoint.to_dict()

    mutations = []
    for field, value in (
        ("schema_version", "hostile"),
        ("independence_terminal", "PASS"),
        ("exposure_markers", []),
        ("scientific_terminal", "PASS"),
        ("configuration_sha256", "0" * 64),
        ("group", []),
        ("parent_range", [0]),
        ("profile", {}),
        ("cursor", []),
        ("counters", []),
    ):
        payload = copy.deepcopy(base)
        payload[field] = value
        mutations.append(resign_checkpoint(payload))
    missing = copy.deepcopy(base)
    del missing["phase"]
    mutations.append(missing)
    mutations.append("not-an-object")

    duplicate_candidates = copy.deepcopy(base)
    duplicate_candidates["candidates"].append(duplicate_candidates["candidates"][0])
    mutations.append(resign_checkpoint(duplicate_candidates))
    duplicate_accepted = copy.deepcopy(base)
    duplicate_accepted["accepted_children"] = [
        duplicate_accepted["candidates"][0],
        duplicate_accepted["candidates"][0],
    ]
    mutations.append(resign_checkpoint(duplicate_accepted))

    for hostile in mutations:
        result = advance_child_level(
            spec,
            frozen_parents,
            frozen_config(),
            checkpoint=hostile,
            edge_budget=7,
        )
        assert result.terminal is CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH
        assert result.checkpoint is None


def test_self_signed_prefix_counter_evaluation_and_cursor_forgery_fails_closed(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...],
) -> None:
    spec = GroupSpec(5, 3)
    config = frozen_config()
    partial_run = advance_child_level(spec, frozen_parents, config, edge_budget=7)
    assert partial_run.checkpoint is not None
    partial = partial_run.checkpoint.to_dict()
    complete_run = advance_child_level(
        spec,
        frozen_parents,
        config,
        edge_budget=100_000,
        reference_uninterrupted=True,
    )
    assert complete_run.checkpoint is not None
    complete = complete_run.checkpoint.to_dict()

    hostile_payloads = []
    bad_candidates = copy.deepcopy(partial)
    bad_candidates["candidates"] = bad_candidates["candidates"][:-1]
    hostile_payloads.append(resign_checkpoint(bad_candidates))
    bad_counter = copy.deepcopy(partial)
    bad_counter["counters"]["candidate_edges"] += 1
    hostile_payloads.append(resign_checkpoint(bad_counter))
    collection_output = copy.deepcopy(partial)
    collection_output["accepted_children"] = [collection_output["candidates"][0]]
    hostile_payloads.append(resign_checkpoint(collection_output))
    collection_prune = copy.deepcopy(partial)
    collection_prune["counters"]["pruned_short_zero_sum"] = 1
    hostile_payloads.append(resign_checkpoint(collection_prune))
    outside_parent = copy.deepcopy(partial)
    outside_parent["cursor"]["parent_index"] = 21
    hostile_payloads.append(resign_checkpoint(outside_parent))
    outside_representative = copy.deepcopy(partial)
    outside_representative["cursor"]["representative_index"] = 999
    hostile_payloads.append(resign_checkpoint(outside_representative))
    terminal_representative = copy.deepcopy(complete)
    terminal_representative["cursor"]["representative_index"] = 1
    hostile_payloads.append(resign_checkpoint(terminal_representative))
    evaluation_outside = copy.deepcopy(complete)
    evaluation_outside["cursor"]["evaluation_index"] += 1
    hostile_payloads.append(resign_checkpoint(evaluation_outside))
    accepted_mismatch = copy.deepcopy(complete)
    accepted_mismatch["accepted_children"] = accepted_mismatch["accepted_children"][:-1]
    hostile_payloads.append(resign_checkpoint(accepted_mismatch))
    short_counter = copy.deepcopy(complete)
    short_counter["counters"]["pruned_short_zero_sum"] = 1
    hostile_payloads.append(resign_checkpoint(short_counter))
    factor_counter = copy.deepcopy(complete)
    factor_counter["counters"]["pruned_k_disjoint"] = 1
    hostile_payloads.append(resign_checkpoint(factor_counter))
    incomplete_complete = copy.deepcopy(complete)
    incomplete_complete["cursor"]["evaluation_index"] -= 1
    incomplete_complete["accepted_children"] = incomplete_complete["accepted_children"][:-1]
    hostile_payloads.append(resign_checkpoint(incomplete_complete))
    evaluation_before_edge_completion = copy.deepcopy(partial)
    evaluation_before_edge_completion["phase"] = "EVALUATE_CANDIDATES"
    hostile_payloads.append(resign_checkpoint(evaluation_before_edge_completion))

    for hostile in hostile_payloads:
        result = advance_child_level(
            spec,
            frozen_parents,
            config,
            checkpoint=hostile,
            edge_budget=7,
        )
        assert result.terminal is CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH


def test_hostile_parent_bindings_and_donor_sources_fail_closed(
    frozen_parents: tuple[tuple[tuple[int, ...], ...], ...],
) -> None:
    spec = GroupSpec(5, 3)
    config = frozen_config()
    assert advance_child_level(GroupSpec(5, 2), frozen_parents, config, edge_budget=7).terminal is (
        CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH
    )
    assert advance_child_level(spec, "bad", config, edge_budget=7).terminal is (
        CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH
    )
    assert advance_child_level(spec, frozen_parents[:-1], config, edge_budget=7).terminal is (
        CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH
    )
    assert advance_child_level(
        spec, tuple(reversed(frozen_parents)), config, edge_budget=7
    ).terminal is (CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH)
    assert advance_child_level(spec, frozen_parents, config, edge_budget=6).terminal is (
        CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH
    )
    assert (
        advance_child_level(
            spec,
            frozen_parents,
            config,
            checkpoint={},
            edge_budget=100_000,
            reference_uninterrupted=True,
        ).terminal
        is CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH
    )

    with pytest.raises(RangeManifestError):
        build_donor_range_manifest(
            GroupSpec(5, 2),
            frozen_parents,
            0,
            8,
            parent_records_sha256=PARENT_SHA256,
            protocol_sha256=PROTOCOL_SHA256,
        )
    with pytest.raises(RangeManifestError):
        build_donor_range_manifest(
            spec,
            [*frozen_parents, frozen_parents[0]],
            0,
            8,
            parent_records_sha256=PARENT_SHA256,
            protocol_sha256=PROTOCOL_SHA256,
        )
    with pytest.raises(RangeManifestError):
        build_donor_range_manifest(
            spec,
            frozen_parents,
            8,
            8,
            parent_records_sha256=PARENT_SHA256,
            protocol_sha256=PROTOCOL_SHA256,
        )
