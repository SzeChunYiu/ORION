from __future__ import annotations

import copy
import json
from pathlib import Path

from orion.discovery.failure_atlas_closure import (
    FailureAtlasTerminal,
    build_failure_atlas_closure_report,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "orion-jump-recursive-atoms"
ATLAS = RESEARCH / "failure_atlas"
SCHEMA = RESEARCH / "FAILURE_ATLAS_SCHEMA_V1.json"
MANIFEST = ATLAS / "FAILURE_ATLAS_PILOT_V1.json"
NORMALIZATION = ATLAS / "FAILURE_ATLAS_NORMALIZATION_V1.json"
SATURATION = ATLAS / "FAILURE_ATLAS_SATURATION_V1.json"
EXPECTED = ATLAS / "FAILURE_ATLAS_CLOSURE_EXPECTED_V1.json"
SHARDS = (
    ATLAS / "FAILURE_ATLAS_PILOT_V1_A.json",
    ATLAS / "FAILURE_ATLAS_PILOT_V1_B.json",
    ATLAS / "FAILURE_ATLAS_PILOT_V1_C.json",
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report(
    *,
    schema: dict[str, object] | None = None,
    manifest: dict[str, object] | None = None,
    shards: list[dict[str, object]] | None = None,
    normalization: dict[str, object] | None = None,
    saturation: dict[str, object] | None = None,
):
    return build_failure_atlas_closure_report(
        schema=schema or _load(SCHEMA),
        manifest=manifest or _load(MANIFEST),
        shards=shards or [_load(path) for path in SHARDS],
        normalization=normalization or _load(NORMALIZATION),
        saturation=saturation or _load(SATURATION),
        expected=_load(EXPECTED),
    )


def _episode(shards: list[dict[str, object]], episode_id: str) -> dict[str, object]:
    for shard in shards:
        for episode in shard["episodes"]:
            if episode["episode_id"] == episode_id:
                return episode
    raise AssertionError(episode_id)


def test_failure_atlas_matches_pre_frozen_schema_stable_terminal() -> None:
    expected = _load(EXPECTED)
    report = _report()

    assert report.episode_count == expected["pilot"]["episodes"] == 30
    assert report.shard_count == expected["pilot"]["shards"] == 3
    assert dict(report.domain_counts) == expected["pilot"]["domain_counts"] == {
        "SCIENCE_MEASUREMENT": 8,
        "CLINICAL_BIOMEDICAL": 6,
        "MATHEMATICS_FORMAL": 6,
        "ENGINEERING_SAFETY": 6,
        "AI_AUTONOMOUS_SCIENCE": 4,
    }
    assert report.malformed_episode_ids == ()
    assert report.enum_violation_episode_ids == ()
    assert report.source_boundary_violation_episode_ids == ()
    assert report.pair_mismatch_ids == ()
    assert report.formal_scope_violation_episode_ids == ()
    assert report.external_review_agreement_count == 0
    assert report.external_review_not_obtained_count == 30
    assert report.corpus_ready_eligible is False
    assert report.normalization_material_schema_change is False
    assert report.post_schema_round_count == 2
    assert report.post_schema_primary_source_count == 7
    assert report.material_change_round_ids == ()
    assert report.terminal.value == expected["candidate_terminal"]
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_SCHEMA_STABLE
    assert report.all_checks_passed is True

    assert report.grants_scientific_refutation is False
    assert report.grants_global_prohibition is False
    assert report.grants_historical_causal_truth is False
    assert report.grants_corpus_ready_authority is False
    assert report.grants_issue_closure_authority is False


def test_all_rows_preserve_hindsight_and_external_review_boundaries() -> None:
    for shard_path in SHARDS:
        shard = _load(shard_path)
        for episode in shard["episodes"]:
            assert episode["private_cognition"] == "CANNOT_INFER"
            assert episode["historical_use"] == "MECHANISM_EXTRACTION_ONLY"
            assert episode["protected_confirmatory_gold"] is False
            assert episode["independent_domain_expert_review_status"] == "NOT_OBTAINED"
            assert len(episode["source_records"]) >= 2
            assert len(set(episode["alternative_interpretations"])) >= 2


def test_post_cutoff_sources_are_explicitly_registered_not_silently_used_as_contemporaneous() -> None:
    shards = [_load(path) for path in SHARDS]

    gfa = _episode(shards, "F006")
    assert gfa["post_cutoff_source_ids"] == ["F006-S3"]
    gfa_source = next(
        source for source in gfa["source_records"] if source["source_id"] == "F006-S3"
    )
    assert gfa_source["temporal_relation"] == "POST_CUTOFF"

    euler = _episode(shards, "F015")
    assert euler["post_cutoff_source_ids"] == ["F015-S2"]
    followup = next(
        source for source in euler["source_records"] if source["source_id"] == "F015-S2"
    )
    assert followup["temporal_relation"] == "POST_CUTOFF"


def test_mathematical_counterexamples_are_exact_scope_but_failed_proof_preserves_theorem() -> None:
    shards = [_load(path) for path in SHARDS]
    for episode_id in ("F015", "F016", "F017", "F018", "F019"):
        episode = _episode(shards, episode_id)
        assert episode["first_negative_outcome_class"] == "FORMAL_COUNTEREXAMPLE"
        assert episode["first_negative_decisive_status"] == "DECISIVE_FOR_REGISTERED_CLAIM"
        assert episode["excluded_scope_ids"]
        assert episode["still_live_alternative_ids"]

    kempe = _episode(shards, "F020")
    assert kempe["first_negative_outcome_class"] == "PROOF_GAP_OR_INVALID_INFERENCE"
    assert any(
        "FOUR_COLOUR_THEOREM" in item for item in kempe["still_live_alternative_ids"]
    )
    assert "FIVE_COLOUR_THEOREM_FROM_REPAIRED_ARGUMENT" in kempe["preserved_success_ids"]


def test_same_surface_symptom_does_not_force_one_responsibility_signature() -> None:
    shards = [_load(path) for path in SHARDS]
    unexpected_signal = [_episode(shards, item) for item in ("F002", "F003", "F008")]
    signatures = {
        tuple(sorted(episode["responsibility_hypothesis_ids"]))
        for episode in unexpected_signal
    }
    assert len(signatures) == 3

    engineering = [_episode(shards, item) for item in ("F022", "F023", "F024", "F025", "F026")]
    engineering_signatures = {
        tuple(sorted(episode["responsibility_hypothesis_ids"]))
        for episode in engineering
    }
    assert len(engineering_signatures) == 5


def test_surrogate_success_is_preserved_when_clinical_endpoint_is_harmful() -> None:
    shards = [_load(path) for path in SHARDS]
    cast = _episode(shards, "F009")
    torcetrapib = _episode(shards, "F011")

    assert cast["first_negative_outcome_class"] == "HARM_OR_ADVERSE_ENDPOINT"
    assert torcetrapib["first_negative_outcome_class"] == "HARM_OR_ADVERSE_ENDPOINT"
    assert cast["preserved_success_ids"]
    assert torcetrapib["preserved_success_ids"]
    assert "SURROGATE_ENDPOINT_CONFUSION" in cast["misstep_class_ids"]
    assert "SURROGATE_ENDPOINT_CONFUSION" in torcetrapib["misstep_class_ids"]


def test_self_attested_external_agreement_cannot_upgrade_the_pre_frozen_pilot() -> None:
    shards = [_load(path) for path in SHARDS]
    tampered = copy.deepcopy(shards)
    _episode(tampered, "F001")["independent_domain_expert_review_status"] = "OBTAINED_AGREEMENT"

    report = _report(shards=tampered)

    assert report.external_review_agreement_count == 1
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE
    assert report.all_checks_passed is False
    assert report.grants_corpus_ready_authority is False


def test_private_cognition_or_historical_gold_leak_fails_closed() -> None:
    shards = [_load(path) for path in SHARDS]
    cognition = copy.deepcopy(shards)
    _episode(cognition, "F003")["private_cognition"] = "researchers-believed-dust-was-impossible"
    report = _report(shards=cognition)
    assert "F003" in report.malformed_episode_ids
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE

    gold = copy.deepcopy(shards)
    _episode(gold, "F005")["protected_confirmatory_gold"] = True
    report = _report(shards=gold)
    assert "F005" in report.malformed_episode_ids
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE


def test_post_cutoff_bookkeeping_mismatch_fails_closed() -> None:
    shards = [_load(path) for path in SHARDS]
    tampered = copy.deepcopy(shards)
    _episode(tampered, "F006")["post_cutoff_source_ids"] = []

    report = _report(shards=tampered)

    assert "F006" in report.source_boundary_violation_episode_ids
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE


def test_failed_proof_cannot_be_rewritten_as_a_counterexample() -> None:
    shards = [_load(path) for path in SHARDS]
    tampered = copy.deepcopy(shards)
    kempe = _episode(tampered, "F020")
    kempe["first_negative_outcome_class"] = "FORMAL_COUNTEREXAMPLE"
    kempe["still_live_alternative_ids"] = ["NONE_AFTER_EXACT_FORMAL_REFUTATION"]

    report = _report(shards=tampered)

    assert "F020" in report.formal_scope_violation_episode_ids
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE


def test_material_new_post_schema_coordinate_reopens_schema() -> None:
    saturation = _load(SATURATION)
    tampered = copy.deepcopy(saturation)
    round_2 = tampered["rounds"][1]
    round_2["new_schema_coordinate_ids"] = ["SOME_NEW_REVISION_AWARE_FAILURE_COORDINATE"]
    round_2["material_change"] = True
    round_2["result"] = "MATERIAL_CHANGE"

    report = _report(saturation=tampered)

    assert report.material_change_round_ids == ("POST_SCHEMA_ROUND_2",)
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE


def test_nonstructural_normalization_does_not_add_a_schema_coordinate() -> None:
    normalization = _load(NORMALIZATION)
    assert normalization["material_schema_change"] is False
    assert normalization["aliases"]["response_type_ids"] == {
        "AUTHORITY_OR_VALIDATION_REPAIR": "REDESIGN_INTERFACE_OR_SYSTEM"
    }
    assert normalization["aliases"]["successor_transition_class"] == {
        "NARROW_CLAIM_OR_DOMAIN": "PARAMETER_OR_METHOD_UPDATE",
        "OPEN_SUCCESSOR_SEARCH": "CANNOT_INFER",
        "REDESIGN_INTERFACE_OR_SYSTEM": "MODEL_CLASS_EXPANSION",
    }
