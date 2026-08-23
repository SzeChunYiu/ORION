#!/usr/bin/env python3
"""MAX-R6C matched canonical-ORION / ORION-Q residual diagnosis.

Consumes one already-generated frozen R6B donor-reuse receipt. It does not run
chemistry, read the protected stretched-N2 subject, or grant scientific authority.
The canonical lane deliberately executes the production OrionRuntime/OrionSolver
with deterministic local providers and verifies the shared 59-cell mechanics
surface before emitting its responsibility receipt.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.core.problem import Problem
from orion.engine.solver import SolverConfig
from orion.providers.llm import CallableLLMProvider
from orion.providers.retrieval import InMemoryRetrievalProvider
from orion.providers.verification import InMemoryVerificationProvider
from orion.runtime import OrionRuntime
from orion.transfer.v2.epistemic_responsibility import (
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion_research_harness.mechanics_bridge import (
    mechanic_catalog,
    mechanics_coverage,
    navigate_mechanics,
    special_surface_catalog,
)

PREFIX = "ORIONQ_MAX_R6B_TARE_REUSE="
CLAIM = "orion-q:max-r6c-dual-lane-residual"


def _load_receipt(path: Path) -> dict:
    lines = [line for line in path.read_text().splitlines() if line.startswith(PREFIX)]
    if len(lines) != 1:
        raise ValueError(f"expected exactly one R6B receipt, got {len(lines)}")
    payload = json.loads(lines[0][len(PREFIX):])
    gates = payload.get("gates")
    if not isinstance(gates, dict) or not gates:
        raise ValueError("R6B receipt has no gate map")
    if payload.get("development_supported") is not all(value is True for value in gates.values()):
        raise ValueError("R6B support bit disagrees with frozen gate conjunction")
    if payload.get("reserved_stretched_n2_accessed") is not False:
        raise ValueError("protected stretched-N2 was accessed during R6B")
    if payload.get("novelty_credit") is not False:
        raise ValueError("R6B donor capability was assigned novelty credit")
    hostile = payload.get("hostile")
    if not isinstance(hostile, dict) or hostile.get("all_pass") is not True:
        raise ValueError("R6B hostile verification is not green")
    return payload


def _hypothesis(hypothesis_id: str, expected: dict[str, list[str]]):
    return build_responsibility_hypothesis(
        hypothesis_id=hypothesis_id,
        claim_id=CLAIM,
        expected_observations=expected,
        support_evidence_ids=("R6B_RECEIPT", "EXACT_TARE3_FRAME_ONLY_COLLAPSE"),
    )


def canonical_runtime_probe(sign: str) -> dict:
    """Exercise production OrionRuntime/OrionSolver without external authority."""
    llm = CallableLLMProvider(lambda _request: '{"queries":[]}', model_id="r6c-deterministic")
    runtime = OrionRuntime.from_providers(
        llm=llm,
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        config=SolverConfig(max_iterations=1),
    )
    result = runtime.solve(
        Problem(
            "orion-q:max-r6c-canonical-runtime-probe",
            (
                "Diagnose the post-exact-TARE3 residual after the verified R6B "
                f"donor-reuse sign {sign}; preserve donor-first refusal and protected-subject closure."
            ),
        )
    )
    return {
        "executed": True,
        "problem_id": result.solution.problem_id,
        "solution_status": result.solution.status.value,
        "trace_id": result.trace.trace_id,
        "operator_sequence": [item.value for item in result.trace.operator_sequence],
        "evidence_ids": list(result.solution.evidence_ids),
        "residual_ids": list(result.solution.residual_ids),
        "scientific_authority_from_probe": False,
    }


def canonical_mechanics_probe() -> dict:
    coverage = mechanics_coverage()
    ids = {str(row["surface_id"]) for row in mechanic_catalog()}
    ids.update(str(row["surface_id"]) for row in special_surface_catalog())
    required = {
        "FRAME.DECOMPOSE.v0",
        "REFRAME.METHOD.v0",
        "REOPEN.FIBRE.v0",
        "SATURATE_BOUNDED.v3",
        "SELF_ORION.DEVELOPMENT_FIBRE.v1",
    }
    missing = sorted(required - ids)
    method_nav = navigate_mechanics("method fibre", limit=12)
    fibre_nav = navigate_mechanics("fibre problem solver", limit=12)
    passed = (
        coverage.get("mechanic_cell_count") == 59
        and coverage.get("structurally_discoverable") is True
        and coverage.get("missing_anchor_ids") == []
        and coverage.get("missing_runtime_cells") == []
        and not missing
    )
    if not passed:
        raise AssertionError(
            {
                "canonical_mechanics_probe_failed": True,
                "coverage": coverage,
                "missing_required_surfaces": missing,
            }
        )
    return {
        "passed": True,
        "coverage": coverage,
        "required_surface_ids": sorted(required),
        "missing_required_surface_ids": missing,
        "method_fibre_navigation": method_nav,
        "development_fibre_navigation": fibre_nav,
    }


def canonical_diagnosis(sign: str) -> dict:
    hypotheses = [
        _hypothesis(
            "RESP:R6B_DONOR_REUSE_UNABSORBED",
            {
                "R6B_INTEGRITY": ["PASS"],
                "R6B_DONOR_REUSE": ["POSITIVE"],
            },
        ),
        _hypothesis(
            "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_DONOR_CLOSURE",
            {
                "R6B_INTEGRITY": ["PASS"],
                "R6B_DONOR_REUSE": ["NEGATIVE"],
                "EXACT_TARE3_INCREMENTAL_VS_STRONG_INCUMBENT": ["NONE"],
            },
        ),
        _hypothesis(
            "RESP:SOFTWARE_OR_EVIDENCE_UNRESOLVED",
            {"R6B_INTEGRITY": ["FAIL", "CANNOT_CHECK"]},
        ),
    ]
    observed = {
        "R6B_INTEGRITY": "PASS",
        "R6B_DONOR_REUSE": sign,
        "EXACT_TARE3_INCREMENTAL_VS_STRONG_INCUMBENT": "NONE",
    }
    immediate = assess_responsibility(hypotheses, observed_outcomes=observed)
    if immediate.identified_hypothesis_id is None:
        raise AssertionError({"canonical_responsibility_not_identified": immediate.unsigned()})

    if sign == "POSITIVE":
        post_hypotheses = [
            _hypothesis(
                "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_DONOR_CLOSURE",
                {
                    "R6B_DONOR_REUSE_ABSORBED": ["YES"],
                    "EXACT_TARE3_INCREMENTAL_VS_STRONG_INCUMBENT": ["NONE"],
                },
            ),
            _hypothesis(
                "RESP:R6B_DONOR_REUSE_UNABSORBED",
                {"R6B_DONOR_REUSE_ABSORBED": ["NO"]},
            ),
        ]
        post = assess_responsibility(
            post_hypotheses,
            observed_outcomes={
                "R6B_DONOR_REUSE_ABSORBED": "YES",
                "EXACT_TARE3_INCREMENTAL_VS_STRONG_INCUMBENT": "NONE",
            },
        )
        next_residual = post.identified_hypothesis_id
        immediate_action = "ABSORB_DONOR_REUSE"
        next_action = "REFRAME.METHOD.v0"
    else:
        post = None
        next_residual = immediate.identified_hypothesis_id
        immediate_action = "REFRAME.METHOD.v0"
        next_action = "REOPEN.FIBRE.v0"

    if next_residual != "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_DONOR_CLOSURE":
        raise AssertionError({"unexpected_canonical_residual": next_residual})

    return {
        "responsibility": immediate.unsigned(),
        "immediate_action": immediate_action,
        "post_absorption_responsibility": None if post is None else post.unsigned(),
        "normalized_next_residual": next_residual,
        "normalized_next_action": next_action,
        "required_mechanics": [
            "FRAME.DECOMPOSE.v0",
            "REFRAME.METHOD.v0",
            "REOPEN.FIBRE.v0",
            "SATURATE_BOUNDED.v3",
            "SELF_ORION.DEVELOPMENT_FIBRE.v1",
        ],
    }


def orion_q_diagnosis(sign: str) -> dict:
    if sign == "POSITIVE":
        immediate = "ABSORB_TARE_TRANSFORMATION_REUSE"
        normalized = "GROW_METHOD_LANGUAGE_BEYOND_ABSORBED_TARE_REUSE"
    else:
        immediate = "GROW_METHOD_LANGUAGE_BEYOND_INDEPENDENT_TARE3"
        normalized = immediate
    return {
        "immediate_action": immediate,
        "normalized_next_residual": "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_DONOR_CLOSURE",
        "normalized_next_action": normalized,
        "novelty_credit_for_r6b": False,
        "protected_subject_may_open": False,
    }


def main() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    r6b = _load_receipt(args.receipt)
    sign = "POSITIVE" if r6b["development_supported"] is True else "NEGATIVE"

    runtime_probe = canonical_runtime_probe(sign)
    mechanics_probe = canonical_mechanics_probe()
    canonical = canonical_diagnosis(sign)
    canonical["runtime_probe"] = runtime_probe
    canonical["mechanics_probe"] = mechanics_probe
    specialized = orion_q_diagnosis(sign)
    agreement = (
        canonical["normalized_next_residual"]
        == specialized["normalized_next_residual"]
    )
    implementation_ready = (
        runtime_probe["executed"] is True
        and runtime_probe["scientific_authority_from_probe"] is False
        and mechanics_probe["passed"] is True
    )
    result = {
        "schema": "ORIONQ.MAXR6C.DualLaneResidualDiagnosis.v2",
        "authority": "RESIDUAL_DIAGNOSIS_ONLY__NOT_R6",
        "r6b_scientific_sign": sign,
        "canonical_orion": canonical,
        "orion_q": specialized,
        "canonical_runtime_and_mechanics_executed": implementation_ready,
        "normalized_residual_agreement": agreement,
        "new_method_protocol_eligible": agreement and implementation_ready,
        "reserved_stretched_n2_accessed": False,
        "r6_earned": False,
    }
    print("ORIONQ_MAX_R6C_DUAL_LANE=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
