"""Current authority for P12A after the comparator-capability audit.

The P12A protocol, result and replay adjudication are historical facts.  This
module does not reinterpret their arithmetic.  It asks the later, load-bearing
question the protocol omitted: could either named one-axis comparator have
earned the winner's score if its signal were perfect while its shipped action
set stayed fixed?
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

from orion.programme.attainable_margin import assess_attainable_margin
from orion.study.p12.allocation_arms import (
    ALL_ARMS,
    MATCHED_ARMS,
    SHIPPED_ARMS,
    SHIPPED_TERMINAL,
    arm_capability,
    gate_battery,
    run_families,
)

SCHEMA = "ORION.P12A.ComparisonValidityAdjudication.v1"
ACTIVE_SCHEMA = "ORION.P12.ActiveClaimAuthority.v1"
AUTHORITY_TERMINAL = "P12A_SUPERIORITY_AUTHORITY_WITHHELD"
MATCHED_PAIR = ("STATE_SIGNAL_ONLY_MATCHED", "REASON_SIGNAL_ONLY_MATCHED")
ONE_AXIS = ("ADAPTIVE_STATE_ONLY", "ADAPTIVE_REASON_ONLY")

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-12-adaptive-state-reasoning"
RESULT = PAPER / "P12A_MATCHED_BUDGET_RESULT_RECEIPT_V1.json"
REPLAY = PAPER / "P12A_PROTOCOL_ADJUDICATION_V2.json"
AUDIT = REPO_ROOT / "research/failures/2026-08-handicapped-baseline-unattainable-margin/README.md"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_comparison_adjudication() -> dict[str, Any]:
    """Recompute the hostile comparison audit from the protected seed."""

    families = run_families(ALL_ARMS)
    arms = {arm.arm_id: arm for arm in (*SHIPPED_ARMS, *MATCHED_ARMS)}
    winner = arm_capability(families, arms["JOINT_FROZEN"])
    assessments = [
        assess_attainable_margin(
            f"P12A_JOINT_VS_{arm_id}",
            winner=winner,
            baseline=arm_capability(families, arms[arm_id]),
            min_attainable_margin=0.15,
        )
        for arm_id in ONE_AXIS
    ]
    matched = gate_battery(families, one_axis_arms=MATCHED_PAIR)
    failed = sorted(name for name, passed in matched["gates"].items() if not passed)

    return {
        "schema": SCHEMA,
        "paper_id": "P12",
        "claim_id": "P12A_TWO_SIGNAL_SUPERIORITY_OVER_ONE_SIGNAL_POLICIES",
        "terminal_retained_verbatim": SHIPPED_TERMINAL,
        "historical_evidence": {
            "result_artifact": str(RESULT.relative_to(REPO_ROOT)),
            "result_sha256": file_sha256(RESULT),
            "replay_artifact": str(REPLAY.relative_to(REPO_ROOT)),
            "replay_sha256": file_sha256(REPLAY),
            "replay_establishes": ["deterministic_reexecution", "frozen_gate_execution"],
            "replay_does_not_establish": [
                "comparator_capability_match",
                "causal_signal_axis_attribution",
            ],
        },
        "audit": {
            "failure_class": "HANDICAPPED_BASELINE_UNATTAINABLE_MARGIN",
            "audit_artifact": str(AUDIT.relative_to(REPO_ROOT)),
            "audit_sha256": file_sha256(AUDIT),
            "instrument_modules": [
                "src/orion/study/p12/allocation_arms.py",
                "src/orion/programme/attainable_margin.py",
            ],
            "comparisons": [item.as_json() for item in assessments],
            "capability_matched_reading": {
                "one_axis_arms": list(MATCHED_PAIR),
                "mean_gain": matched["mean_joint_gain"],
                "family_block_bootstrap_95ci": matched["family_bootstrap_95ci"],
                "worst_family_gain": matched["worst_family_joint_gain"],
                "failed_gates": failed,
                "terminal": matched["terminal"],
            },
        },
        "scientific_authority": {
            "active_terminal": AUTHORITY_TERMINAL,
            "superiority_claim": "NONE",
            "outcome": "CANNOT_CHECK",
            "reason": "BASELINE_CEILING_BELOW_WINNER",
            "detail": (
                "The historical margin is not attributable to reading a second signal because "
                "both shipped one-axis baselines have action-set ceilings below the winner's "
                "achieved score. Matching the four-action capability flips the registered gate."
            ),
        },
        "successor_requirement": (
            "Freeze P12B before outcomes with identical four-action sets for one- and two-signal "
            "arms, fixed policies, family/domain-block inference, and an attainable positive gate."
        ),
    }


def build_active_authority(adjudication_sha256: str) -> dict[str, Any]:
    if len(adjudication_sha256) != 64:
        raise ValueError("P12 adjudication SHA-256 must contain 64 hexadecimal characters")
    int(adjudication_sha256, 16)
    return {
        "schema": ACTIVE_SCHEMA,
        "paper_id": "P12",
        "active_claim": "NO_ACTIVE_SUPERIORITY_LEAF",
        "active_terminal": AUTHORITY_TERMINAL,
        "historical_terminal": SHIPPED_TERMINAL,
        "historical_terminal_authority": "RETAINED_AS_EXECUTION_HISTORY_ONLY",
        "adjudication_artifact": (
            "papers/paper-12-adaptive-state-reasoning/"
            "P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json"
        ),
        "adjudication_sha256": adjudication_sha256,
        "promotion_allowed": False,
        "next_claim_id": "P12B_CAPABILITY_MATCHED_SIGNAL_VALUE",
    }


__all__ = [
    "ACTIVE_SCHEMA",
    "AUTHORITY_TERMINAL",
    "SCHEMA",
    "build_active_authority",
    "build_comparison_adjudication",
    "file_sha256",
]
