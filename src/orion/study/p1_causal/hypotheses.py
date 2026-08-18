"""Frozen competing hypotheses H-R1..H-R6 — names only, no outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .protocol import load_protocol


class HypothesisId(str, Enum):
    H_R1 = "H-R1"
    H_R2 = "H-R2"
    H_R3 = "H-R3"
    H_R4 = "H-R4"
    H_R5 = "H-R5"
    H_R6 = "H-R6"


@dataclass(frozen=True)
class CompetingHypothesis:
    hypothesis_id: HypothesisId
    claim: str
    discriminator: str
    pass_if: str
    fail_if: str
    confusable_with: tuple[HypothesisId, ...]

    def to_payload(self) -> dict:
        return {
            "id": self.hypothesis_id.value,
            "claim": self.claim,
            "discriminator": self.discriminator,
            "pass_if": self.pass_if,
            "fail_if": self.fail_if,
            "confusable_with": [item.value for item in self.confusable_with],
        }


def _from_protocol() -> tuple[CompetingHypothesis, ...]:
    payload = load_protocol()
    rows = []
    for row in payload["competing_root_cause_hypotheses"]:
        rows.append(
            CompetingHypothesis(
                hypothesis_id=HypothesisId(row["id"]),
                claim=row["claim"],
                discriminator=row["discriminator"],
                pass_if=row["pass_if"],
                fail_if=row["fail_if"],
                confusable_with=tuple(
                    HypothesisId(item) for item in row["confusable_with"]
                ),
            )
        )
    return tuple(rows)


COMPETING_HYPOTHESES: tuple[CompetingHypothesis, ...] = _from_protocol()

if tuple(item.hypothesis_id.value for item in COMPETING_HYPOTHESES) != tuple(
    item.value for item in HypothesisId
):
    raise RuntimeError("H-R1..H-R6 must be frozen as a total, ordered set")
