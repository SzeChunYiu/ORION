"""Current P13A authority after auditing its self-scored safety endpoint.

P13A's RCS arm reuses exactly when its certificate says the responsibility is
supported.  Its primary harm counter calls a reuse unsafe exactly when that
same certificate says the responsibility is not supported.  The conjunction is
therefore false by definition, even under a wrong certificate.  This module
enumerates that identity and contrasts it with an independently gold-scored
endpoint that a future P13B can actually press.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from orion.programme.outcome_entailment import (
    ArmPolicy,
    ReportedOutcome,
    WorldVariant,
    measure_outcome_entailment,
)

SCHEMA = "ORION.P13A.OutcomeEntailmentAdjudication.v1"
ACTIVE_SCHEMA = "ORION.P13.ActiveClaimAuthority.v1"
AUTHORITY_TERMINAL = "P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD"
HISTORICAL_TERMINAL = "P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-23-responsibility-carrying-state"
RESULT = PAPER / "P13A_RCS_SAFETY_COST_RESULT_RECEIPT_V1.json"
REPLAY = PAPER / "P13A_PROTOCOL_ADJUDICATION_V2.json"

TASKS = ("PREDICT", "DECIDE", "INTERVENE", "VERIFY", "REPAIR")
SUPPORT = {
    "Z1": frozenset(("PREDICT", "DECIDE")),
    "Z2": frozenset(("PREDICT", "DECIDE", "INTERVENE", "VERIFY")),
}


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def enumerated_space() -> tuple[dict[str, Any], ...]:
    """Twenty-four fixed strata over every P13A truth/task/recovery state."""

    points: list[dict[str, Any]] = []
    for stratum in range(24):
        for x in (-1, 1):
            for mechanic in (-1, 1):
                for repair in (-1, 1):
                    for z in ("Z1", "Z2"):
                        for task in TASKS:
                            for recover in (False, True):
                                supported = task in SUPPORT[z]
                                points.append(
                                    {
                                        "stratum": stratum,
                                        "x": x,
                                        "mechanic": mechanic,
                                        "repair": repair,
                                        "z": z,
                                        "task": task,
                                        "recover": recover,
                                        "gold_supported": supported,
                                        "declared_supported": supported,
                                    }
                                )
    return tuple(points)


def rcs_action(point: dict[str, Any]) -> str:
    if point["declared_supported"]:
        return "REUSE"
    return "REOPEN" if point["recover"] else "CANNOT_CHECK"


RCS = ArmPolicy(
    arm_id="RCS",
    decides="reuse exactly when the certificate declares the responsibility supported",
    action=rcs_action,
)

SELF_SCORED_UNSAFE = ReportedOutcome(
    outcome_id="unsafe_reuse_declared_support",
    measures="REUSE while the same certificate declares support absent",
    holds=lambda point, decision: decision == "REUSE" and not point["declared_supported"],
)

GOLD_SCORED_UNSAFE = ReportedOutcome(
    outcome_id="unsafe_reuse_gold_support",
    measures="REUSE while independently defined gold support is absent",
    holds=lambda point, decision: decision == "REUSE" and not point["gold_supported"],
)

OMITTED_SUPPORT = WorldVariant(
    world_id="certificate_omits_true_support",
    wrong="a stale or incomplete certificate drops every genuinely supported responsibility",
    rewrite=lambda point: {**point, "declared_supported": False},
)

OVERBROAD_SUPPORT = WorldVariant(
    world_id="certificate_claims_missing_support",
    wrong="an overbroad certificate declares every unsupported responsibility supported",
    rewrite=lambda point: {**point, "declared_supported": True},
)


def build_outcome_adjudication() -> dict[str, Any]:
    space = enumerated_space()
    self_scored = measure_outcome_entailment(
        SELF_SCORED_UNSAFE, policy=RCS, space=space, worlds=(OMITTED_SUPPORT,)
    )
    gold_scored = measure_outcome_entailment(
        GOLD_SCORED_UNSAFE, policy=RCS, space=space, worlds=(OVERBROAD_SUPPORT,)
    )
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    duplicate = result["summary"]["PROVENANCE_ONLY"] == result["summary"]["UNQUALIFIED"]

    return {
        "schema": SCHEMA,
        "paper_id": "P13",
        "claim_id": "P13A_EMPIRICAL_SAFETY_COST_SUPERIORITY",
        "terminal_retained_verbatim": HISTORICAL_TERMINAL,
        "historical_evidence": {
            "result_artifact": str(RESULT.relative_to(REPO_ROOT)),
            "result_sha256": file_sha256(RESULT),
            "replay_artifact": str(REPLAY.relative_to(REPO_ROOT)),
            "replay_sha256": file_sha256(REPLAY),
            "replay_establishes": ["deterministic_reexecution", "frozen_gate_execution"],
            "replay_does_not_establish": [
                "outcome_contingency",
                "certificate_correctness",
                "comparator_distinctness",
            ],
        },
        "audit": {
            "instrument_module": "src/orion/study/p13/outcome_authority.py",
            "enumerated_points": len(space),
            "self_scored_endpoint": self_scored.as_json(),
            "independent_gold_endpoint_control": gold_scored.as_json(),
            "duplicate_arms": (
                [["PROVENANCE_ONLY", "UNQUALIFIED"]] if duplicate else []
            ),
            "instrument_only_endpoints": [
                "cannot_check_count",
                "correct_cannot_check_rate",
                "unnecessary_reopen_rate",
            ],
        },
        "authorized_claims": [
            "exact responsibility-relative support matrix in the registered finite world",
            "conditional interface invariant: RCS refuses reuse when declared support omits the responsibility",
            "descriptive frozen-run actions, rates, costs, and deterministic replay",
            "constructed existence example that current/provenanced/high-confidence state can omit a responsibility-relevant distinction",
        ],
        "withheld_claims": [
            "empirical elimination of unsafe reuse",
            "overall safety-cost superiority",
            "robustness to wrong, stale, forged, or overbroad certificates",
            "benefit attributable to provenance",
            "real-agent or population generalization",
        ],
        "scientific_authority": {
            "active_terminal": AUTHORITY_TERMINAL,
            "superiority_claim": "NONE",
            "outcome": "CANNOT_CHECK",
            "reason": "SELF_SCORED_OUTCOME_NOT_CONTINGENT",
            "detail": (
                "The RCS action changes under registered certificate corruption while the "
                "published unsafe-reuse endpoint cannot change. A separately gold-scored "
                "endpoint has live opportunities and is required for P13B."
            ),
        },
        "successor_requirement": (
            "Freeze P13B with gold support independent of the certificate; wrong, stale, forged "
            "and overbroad witness worlds; a live unsafe-reuse denominator; matched cost and "
            "correctness frontiers; family/domain-block inference; and noncompensatory worst-domain gates."
        ),
    }


def build_active_authority(adjudication_sha256: str) -> dict[str, Any]:
    if len(adjudication_sha256) != 64:
        raise ValueError("P13 adjudication SHA-256 must contain 64 hexadecimal characters")
    int(adjudication_sha256, 16)
    return {
        "schema": ACTIVE_SCHEMA,
        "paper_id": "P13",
        "active_terminal": AUTHORITY_TERMINAL,
        "claim_leaves": [
            {
                "claim_id": "P13.EXACT.RESPONSIBILITY_RELATIVE_SUPPORT",
                "outcome": "SUPPORTED_EXACT",
                "scope": "REGISTERED_FINITE_CONSTRUCTED_WORLD",
            },
            {
                "claim_id": "P13A.EMPIRICAL.SAFETY_COST_SUPERIORITY",
                "outcome": "CANNOT_CHECK",
                "authority": "NONE",
            },
        ],
        "historical_terminal": HISTORICAL_TERMINAL,
        "historical_terminal_authority": "RETAINED_AS_EXECUTION_HISTORY_ONLY",
        "adjudication_artifact": (
            "papers/orion-23-responsibility-carrying-state/"
            "P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json"
        ),
        "adjudication_sha256": adjudication_sha256,
        "superiority_promotion_allowed": False,
        "next_claim_id": "P13B_INDEPENDENTLY_GRADED_CERTIFICATE_SAFETY",
    }


__all__ = [
    "AUTHORITY_TERMINAL",
    "GOLD_SCORED_UNSAFE",
    "OVERBROAD_SUPPORT",
    "RCS",
    "SELF_SCORED_UNSAFE",
    "build_active_authority",
    "build_outcome_adjudication",
    "enumerated_space",
]
