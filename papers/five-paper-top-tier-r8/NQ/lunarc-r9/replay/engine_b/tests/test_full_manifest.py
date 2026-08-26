from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

import engine_b as eb
import full_manifest as fm


def test_full_plan_freezes_exact_denominators_and_contiguous_partitions() -> None:
    plan = fm.build_partition_plan()
    fm.verify_partition_plan(plan)
    scopes = {scope["scope"]: scope for scope in plan["scopes"]}
    d2 = scopes[fm.D2_SPEC.scope]
    d3 = scopes[fm.D3_SPEC.scope]
    assert d2["expected_record_count"] == 98_622
    assert d3["expected_record_count"] == 230_983
    assert d2["partition_count"] == 25
    assert d3["partition_count"] == 57
    assert sum(part["record_count"] for part in d2["partitions"]) == 98_622
    assert sum(part["record_count"] for part in d3["partitions"]) == 230_983
    assert d2["partitions"][-1]["record_count"] == 318
    assert d3["partitions"][-1]["record_count"] == 1_607


def test_partition_plan_is_deterministic_and_tamper_evident() -> None:
    assert fm.build_partition_plan() == fm.build_partition_plan()
    plan = fm.build_partition_plan()
    mutated = copy.deepcopy(plan)
    mutated["scopes"][0]["partitions"][1]["ordinal_start"] -= 1
    mutated["plan_sha256"] = fm.payload_sha256(mutated, digest_field="plan_sha256")
    with pytest.raises(fm.PartitionPlanMismatch, match="contiguous"):
        fm.verify_partition_plan(mutated)

    mutated = copy.deepcopy(plan)
    mutated["authority"]["d3_replay"] = "PASS"
    mutated["plan_sha256"] = fm.payload_sha256(mutated, digest_field="plan_sha256")
    with pytest.raises(fm.PartitionPlanMismatch, match="authority"):
        fm.verify_partition_plan(mutated)


def test_gl3_matrix_manifest_is_complete_and_reproducible() -> None:
    manifest = fm.build_matrix_action_manifest(3)
    assert manifest["matrix_count"] == 1_488_000
    assert manifest["payload_bytes"] == 9 * 1_488_000
    assert manifest["matrix_sha256"] == fm.build_matrix_action_manifest(3)["matrix_sha256"]
    fm.verify_matrix_action_manifest(manifest, regenerate=True)


def test_candidate_records_are_exact_canonical_and_outcome_free(tmp_path: Path) -> None:
    spec = fm.CensusSpec("TEST_SCOPE", "test", 2, 3, 2, "t")
    record = fm.build_candidate_record(
        spec,
        ordinal=0,
        sequence=(1, 4, 5),
        matrix_witness_sha256="a" * 64,
        orbit_key_sha256="b" * 64,
        derivation_sha256="c" * 64,
    )
    line = eb.canonical_json_bytes(record) + b"\n"
    assert fm.parse_candidate_line(line, spec, expected_ordinal=0) == record

    noncanonical = json.dumps(record, indent=2).encode() + b"\n"
    with pytest.raises(fm.CandidateStreamMismatch, match="canonical"):
        fm.parse_candidate_line(noncanonical, spec, expected_ordinal=0)

    promoted = dict(record, status="SAT")
    promoted["candidate_sha256"] = fm.payload_sha256(promoted, digest_field="candidate_sha256")
    with pytest.raises(fm.CandidateStreamMismatch, match="fields"):
        fm.parse_candidate_line(eb.canonical_json_bytes(promoted) + b"\n", spec, expected_ordinal=0)


def test_materializer_writes_exact_frozen_shards_and_rejects_gaps(tmp_path: Path) -> None:
    spec = fm.CensusSpec("TEST_SCOPE", "test", 5, 2, 1, "t")
    plan = fm.build_partition_plan(specs=(spec,), partition_size=2)
    stream = tmp_path / "records.jsonl"
    records = [
        fm.build_candidate_record(
            spec,
            ordinal=index,
            sequence=(index % 5, (index + 1) % 5),
            matrix_witness_sha256=hashlib.sha256(f"m{index}".encode()).hexdigest(),
            orbit_key_sha256=hashlib.sha256(f"o{index}".encode()).hexdigest(),
            derivation_sha256=hashlib.sha256(f"d{index}".encode()).hexdigest(),
        )
        for index in range(5)
    ]
    stream.write_bytes(b"".join(eb.canonical_json_bytes(record) + b"\n" for record in records))
    output = tmp_path / "bundle"
    manifest = fm.materialize_scope(stream, plan["scopes"][0], output)
    fm.verify_materialized_scope(output, plan["scopes"][0], manifest)
    assert [part["record_count"] for part in manifest["partitions"]] == [2, 2, 1]
    assert manifest["authority"]["scientific_authority_delta"] == "NONE"
    assert manifest["authority"]["normalization_completeness"] == "CANNOT_CHECK"

    stream.write_bytes(b"".join(eb.canonical_json_bytes(record) + b"\n" for record in records[:-1]))
    with pytest.raises(fm.CandidateStreamMismatch, match="expected 5"):
        fm.materialize_scope(stream, plan["scopes"][0], tmp_path / "short")


def test_declaration_receipt_preserves_non_execution_authority() -> None:
    plan = fm.build_partition_plan()
    receipt = fm.build_declaration_receipt(
        plan,
        origin_main_commit="e" * 40,
        stack_parent_commit="f" * 40,
        source_sha256="a" * 64,
    )
    fm.verify_declaration_receipt(receipt, plan)
    assert receipt["terminal"] == "NQ_CR_B_FULL_CENSUS_PARTITION_PLAN_FROZEN"
    assert receipt["aggregate_results_consumed"] is False
    assert receipt["materialized_candidate_records"] == 0
    assert receipt["lunarc_submission"] == "NOT_SUBMITTED"
    assert receipt["d3_replay"] == "CANNOT_CHECK"
    assert receipt["scientific_authority_delta"] == "NONE"


def test_committed_plan_and_receipt_replay_from_builder() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root / "FULL_CENSUS_DECLARED_MANIFEST.json").read_text())
    receipt = json.loads((root / "FULL_CENSUS_DECLARATION_RECEIPT.json").read_text())
    assert plan == fm.build_partition_plan()
    fm.verify_partition_plan(plan)
    fm.verify_declaration_receipt(receipt, plan)
    schema = json.loads((root / "FULL_CENSUS_MANIFEST_SCHEMA.json").read_text())
    assert schema["$id"] == "ORION.NQ.EngineB.FullCensusManifestSchemas.v1"
