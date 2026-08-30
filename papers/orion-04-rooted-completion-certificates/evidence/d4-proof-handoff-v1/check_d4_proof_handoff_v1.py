#!/usr/bin/env python3
"""Fail-closed structural checker for ORION04.D4_EXACT_PROOF_HANDOFF.v1.

This checker validates only the pre-outcome proof-object contract.  It neither
computes D4 nor authorizes an execution.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PROTOCOL_V1.json"

REQUIRED_TERMINALS = {
    "EXACT_D4_30_PROVED",
    "CONSTRUCTION_ONLY__LOWER_BOUND_OPEN",
    "LOWER_BOUND_ONLY__CONSTRUCTION_OPEN",
    "CANNOT_CHECK_CERTIFICATE_REPLAY",
    "CANNOT_CHECK_INDEPENDENCE",
    "CANNOT_CHECK_SYMMETRY_COVERAGE",
    "CANNOT_CHECK_CUSTODY_OR_AUTHORIZATION",
    "ADVERSE_ROUTE_DISAGREEMENT",
}
REQUIRED_MUTATIONS = {
    "alter_size_30_construction_element",
    "change_primitive_semantic_predicate",
    "corrupt_lower_bound_certificate_step",
    "perturb_symmetry_generator_or_multiplicity",
    "mismatch_source_or_environment_digest",
    "reuse_consumed_nonduplication_key_or_omit_authorization",
    "force_route_disagreement_on_small_control",
}
REQUIRED_CONTROLS = {
    "known_constructible",
    "known_impossible",
    "symmetry_rich",
    "malformed_proof_object",
}


def validate(p: dict) -> None:
    assert p["schema_version"] == "orion04.d4-proof-handoff.v1"
    assert p["identity"] == "ORION04.D4_EXACT_PROOF_HANDOFF.v1"
    assert p["status"] == "DESIGN_ONLY__NO_D4_OUTCOME_AUTHORITY"
    assert p["scientific_authority_delta"] == "NONE"
    assert p["target_statement"] == "D_4(C_5^3)=30"

    authority = p["current_authority_state"]
    assert authority == {
        "live_authorization": "ABSENT",
        "d4_rounds_consumed": 0,
        "execution_authorized_by_this_file": False,
    }

    halves = p["proof_halves"]
    assert halves["upper_bound"]["target"] == "D_4(C_5^3)<=30"
    upper = set(halves["upper_bound"]["required"])
    assert {
        "machine_readable_size_30_construction",
        "primitive_semantics_standalone_verifier",
        "deterministic_predicate_transcript",
        "source_environment_and_artifact_digests",
    } <= upper

    assert halves["lower_bound"]["target"] == "D_4(C_5^3)>=30"
    routes = {route["id"]: route for route in halves["lower_bound"]["routes"]}
    assert set(routes) == {"L-A", "L-B"}
    assert routes["L-A"]["kind"] == "declarative_encoding_plus_checkable_certificate"
    assert "solver_exit_code_only" in routes["L-A"]["forbidden_as_terminal_evidence"]
    assert routes["L-B"]["kind"] == "independently_derived_primitive_semantics_route"
    assert {
        "normalized_candidate_stream",
        "learned_clauses",
        "orbit_table",
        "decision_trace",
    } <= set(routes["L-B"]["must_not_consume_from_L_A"])

    independence = p["independence"]
    assert independence["minimum_lower_bound_routes"] >= 2
    assert "same_generated_cnf_different_solver" in independence["disallowed_claims_of_independence"]
    assert "shared_candidate_normalizer_or_orbit_module" in independence["disallowed_claims_of_independence"]

    assert set(p["small_instance_calibration"]["required_control_kinds"]) >= REQUIRED_CONTROLS
    assert p["small_instance_calibration"]["freeze_before_d4_outcome"] is True
    assert set(p["hostile_mutations"]) >= REQUIRED_MUTATIONS
    assert set(p["terminals"]) >= REQUIRED_TERMINALS

    gate = p["promotion_gate"]
    for key in (
        "requires_upper_bound",
        "requires_L_A",
        "requires_L_B",
        "requires_all_hostile_mutations_rejected",
        "requires_small_instance_calibration",
        "requires_separate_repository_one_shot_authorization",
        "requires_external_or_journal_authority_if_claimed",
    ):
        assert gate[key] is True, key
    assert gate["route_disagreement_policy"] == "retain_adverse_no_majority_vote"


def expect_reject(base: dict, mutate) -> None:
    candidate = copy.deepcopy(base)
    mutate(candidate)
    try:
        validate(candidate)
    except (AssertionError, KeyError, TypeError):
        return
    raise AssertionError("hostile protocol mutation was accepted")


def main() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    validate(protocol)

    mutations = [
        lambda p: p["current_authority_state"].__setitem__("live_authorization", "PRESENT"),
        lambda p: p["current_authority_state"].__setitem__("d4_rounds_consumed", 1),
        lambda p: p["proof_halves"]["lower_bound"].__setitem__("routes", p["proof_halves"]["lower_bound"]["routes"][:1]),
        lambda p: p["hostile_mutations"].remove("corrupt_lower_bound_certificate_step"),
        lambda p: p["terminals"].remove("ADVERSE_ROUTE_DISAGREEMENT"),
        lambda p: p["promotion_gate"].__setitem__("requires_separate_repository_one_shot_authorization", False),
        lambda p: p["promotion_gate"].__setitem__("route_disagreement_policy", "majority_vote"),
        lambda p: p["small_instance_calibration"].__setitem__("freeze_before_d4_outcome", False),
    ]
    for mutate in mutations:
        expect_reject(protocol, mutate)

    print(
        "ORION04_D4_PROOF_HANDOFF_V1_PASS "
        f"hostile_protocol_mutations={len(mutations)} "
        "d4_outcome_access=NONE execution_authority=NONE"
    )


if __name__ == "__main__":
    main()
