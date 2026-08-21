#!/usr/bin/env python3
"""MAX-R6C matched canonical-ORION / ORION-Q residual diagnosis.

Consumes one already-generated frozen R6B donor-reuse receipt. It does not run
chemistry, read the protected stretched-N2 subject, or grant scientific authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.transfer.v2.epistemic_responsibility import (
    assess_responsibility,
    build_responsibility_hypothesis,
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
    canonical = canonical_diagnosis(sign)
    specialized = orion_q_diagnosis(sign)
    agreement = (
        canonical["normalized_next_residual"]
        == specialized["normalized_next_residual"]
    )
    result = {
        "schema": "ORIONQ.MAXR6C.DualLaneResidualDiagnosis.v1",
        "authority": "RESIDUAL_DIAGNOSIS_ONLY__NOT_R6",
        "r6b_scientific_sign": sign,
        "canonical_orion": canonical,
        "orion_q": specialized,
        "normalized_residual_agreement": agreement,
        "new_method_protocol_eligible": agreement,
        "reserved_stretched_n2_accessed": False,
        "r6_earned": False,
    }
    print("ORIONQ_MAX_R6C_DUAL_LANE=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
