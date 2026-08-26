from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from nq_engine_a.group import GroupSpec
from nq_engine_a.pilot import (
    build_target_resource_pilot_receipt,
    derive_slurm_pilot_envelope,
    deterministic_gl_matrices,
    measure_target_case,
)

ROOT = Path(__file__).resolve().parents[1]
SEED_LABEL = "orion-nq-engine-a-target-resource-pilot-v1"
EXPECTED_MATRICES = (
    ((2, 0, 1), (2, 4, 3), (1, 2, 2)),
    ((3, 0, 2), (1, 1, 0), (3, 4, 0)),
    ((2, 3, 1), (3, 3, 1), (3, 0, 4)),
    ((0, 0, 4), (2, 1, 2), (3, 2, 3)),
    ((2, 2, 1), (4, 2, 1), (2, 2, 2)),
    ((2, 3, 1), (4, 3, 1), (1, 2, 2)),
    ((4, 0, 2), (4, 4, 1), (4, 0, 3)),
    ((1, 0, 1), (2, 0, 4), (3, 1, 1)),
    ((1, 1, 0), (2, 4, 2), (2, 0, 4)),
    ((3, 2, 3), (4, 0, 1), (0, 3, 2)),
    ((2, 0, 1), (0, 0, 1), (3, 3, 3)),
    ((2, 1, 4), (3, 3, 3), (2, 3, 3)),
    ((0, 3, 4), (1, 0, 4), (2, 0, 2)),
    ((1, 2, 3), (2, 1, 4), (0, 0, 3)),
    ((2, 2, 0), (4, 3, 1), (4, 0, 0)),
    ((2, 0, 0), (3, 0, 2), (4, 4, 1)),
)


def lower_witness() -> tuple[tuple[int, ...], ...]:
    fixture = json.loads((ROOT / "fixtures" / "d2_lower_witness.json").read_text())
    return tuple(tuple(vector) for vector in fixture["witness"])


def test_frozen_seed_generates_exactly_the_declared_sixteen_unique_gl_matrices() -> None:
    spec = GroupSpec(5, 3)
    observed = deterministic_gl_matrices(spec, SEED_LABEL, 16)
    assert observed == EXPECTED_MATRICES
    assert len(set(observed)) == 16
    assert all(spec.rank(matrix) == 3 for matrix in observed)


def test_single_target_length_case_measures_all_four_bounded_engineering_kernels() -> None:
    case = measure_target_case(
        GroupSpec(5, 3),
        lower_witness(),
        EXPECTED_MATRICES[0],
        case_index=0,
        factorization_k=2,
        factorization_max_states=250_000,
    )
    assert case["case_index"] == 0
    assert case["witness_length"] == 19
    assert case["matrix"] == [list(row) for row in EXPECTED_MATRICES[0]]
    assert set(case["kernels"]) == {
        "canonicalization",
        "donor_slice_expansion",
        "extension_orbit_stabilizer_construction",
        "exact_two_bin_factorization_dp",
    }
    assert all(kernel["elapsed_ns"] >= 0 for kernel in case["kernels"].values())
    factor = case["kernels"]["exact_two_bin_factorization_dp"]
    assert factor["max_states"] == 250_000
    assert factor["status"] in {"POSITIVE", "NEGATIVE", "CANNOT_CHECK_RESOURCE_BOUND"}
    assert case["scientific_terminal"] == "CANNOT_CHECK"


def test_slurm_envelope_rule_is_conservative_bounded_and_not_a_census_estimate() -> None:
    floor = derive_slurm_pilot_envelope(total_elapsed_ns=1_000_000_000, max_rss_bytes=100_000_000)
    assert floor == {
        "cpu_count": 1,
        "memory_gib": 4,
        "wall_minutes": 30,
        "scope": "future_same_pilot_only_not_full_census",
    }
    scaled = derive_slurm_pilot_envelope(
        total_elapsed_ns=20 * 60 * 1_000_000_000,
        max_rss_bytes=2 * 1024**3,
    )
    assert scaled["memory_gib"] == 8
    assert scaled["wall_minutes"] == 200


def test_receipt_builder_executes_only_the_frozen_local_bounded_pilot() -> None:
    receipt = build_target_resource_pilot_receipt(ROOT, source_manifest_sha256="b" * 64)
    assert receipt["source_manifest_sha256"] == "b" * 64
    assert receipt["checkpoint_restart"]["uninterrupted_restart_byte_identical"] is True
    assert receipt["checkpoint_restart"]["candidate_edge_budget_per_invocation"] == 7
    assert receipt["donor_slice_ranges"]["ranges"] == [[0, 8], [8, 16], [16, 20]]
    assert len(receipt["target_kernel_panel"]["cases"]) == 16
    assert receipt["full_census_executed"] is False
    assert receipt["lunarc_submission"] is None
    assert receipt["scientific_terminal"] == "CANNOT_CHECK"


def test_frozen_target_resource_receipt_is_schema_valid_and_preserves_boundaries() -> None:
    receipt = json.loads((ROOT / "TARGET_RESOURCE_PILOT_RECEIPT.json").read_text())
    schema = json.loads(
        (ROOT / "schemas" / "target-resource-pilot-receipt.schema.json").read_text()
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)
    assert len(receipt["target_kernel_panel"]["cases"]) == 16
    assert receipt["authority"] == "engineering_resource_pilot_only"
    assert receipt["full_census_executed"] is False
    assert receipt["lunarc_submission"] is None
    assert receipt["scientific_terminal"] == "CANNOT_CHECK"
    assert receipt["independence_terminal"] == "CANNOT_CHECK"
    assert receipt["two_engine_pass_increment"] == 0
