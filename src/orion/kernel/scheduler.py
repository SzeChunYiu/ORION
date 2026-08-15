from __future__ import annotations

import math
from dataclasses import dataclass

from orion.mechanics.questioning import MechanicQuestion

from .gate import AnswerAuthority
from .store import EntryKind, LedgerStore

_EVIDENCE_BOUND_CREDIT = 0.5


@dataclass(frozen=True)
class DimensionYield:
    """What ORION has actually observed about working on one dimension."""

    dimension: str
    attempts: int = 0
    verified: int = 0
    evidence_bound: int = 0
    refused: int = 0

    @property
    def observed_value(self) -> float:
        """Verified closure per attempt, with partial credit for bound content.

        Evidence-bound answers are real knowledge that failed to earn authority,
        so they score above a refusal and below a closure. Without the partial
        term the scheduler cannot tell "we are learning but cannot verify yet"
        from "nothing is happening here", and those need different repairs.
        """

        if self.attempts == 0:
            return 0.0
        return (
            self.verified + _EVIDENCE_BOUND_CREDIT * self.evidence_bound
        ) / self.attempts

    def priority_score(self, total_attempts: int) -> float:
        """Upper-confidence score: exploit observed yield, explore the untried.

        An untried dimension scores infinitely high, so no dimension can be
        starved forever by early bad luck. That matters beyond efficiency: a
        scheduler that quietly abandons the dimensions it finds hard would
        manufacture flatness, which is the failure mode bounded saturation
        exists to prevent.
        """

        if self.attempts == 0:
            return math.inf
        return self.observed_value + math.sqrt(
            2.0 * math.log(max(total_attempts, 2)) / self.attempts
        )


def observe_dimension_yields(store: LedgerStore) -> dict[str, DimensionYield]:
    """Read the run's own grading history back out of the ledger."""

    counts: dict[str, dict[str, int]] = {}
    for entry in store.entries(EntryKind.GRADING):
        dimension = str(entry.payload.get("dimension", ""))
        if not dimension:
            continue
        bucket = counts.setdefault(
            dimension, {"attempts": 0, "verified": 0, "evidence_bound": 0, "refused": 0}
        )
        bucket["attempts"] += 1
        authority = str(entry.payload.get("authority", ""))
        if authority == AnswerAuthority.VERIFIED.value:
            bucket["verified"] += 1
        elif authority == AnswerAuthority.EVIDENCE_BOUND.value:
            bucket["evidence_bound"] += 1
        else:
            bucket["refused"] += 1
    return {
        dimension: DimensionYield(
            dimension=dimension,
            attempts=values["attempts"],
            verified=values["verified"],
            evidence_bound=values["evidence_bound"],
            refused=values["refused"],
        )
        for dimension, values in counts.items()
    }


def order_by_observed_yield(
    questions: tuple[MechanicQuestion, ...],
    yields: dict[str, DimensionYield],
) -> tuple[MechanicQuestion, ...]:
    """Reorder open questions toward the directions that have been paying off.

    This is the metareasoning step `plan_program_questions` left as future work:
    the run consumes its own grading history instead of following a fixed
    breadth-first policy. It is strictly a reordering — the returned set is
    always the input set, because dropping a question would let the scheduler
    close the audit by looking away from it.
    """

    if not questions:
        return questions
    total = sum(item.attempts for item in yields.values())
    scored = sorted(
        enumerate(questions),
        key=lambda pair: (
            -yields.get(
                pair[1].dimension.value, DimensionYield(pair[1].dimension.value)
            ).priority_score(total),
            pair[0],
        ),
    )
    return tuple(question for _, question in scored)


@dataclass(frozen=True)
class YieldReport:
    """The measured surface the scheduler is climbing, for human inspection."""

    rows: tuple[DimensionYield, ...]
    total_attempts: int

    @property
    def unexplored(self) -> tuple[str, ...]:
        return tuple(item.dimension for item in self.rows if item.attempts == 0)

    @property
    def best(self) -> DimensionYield | None:
        scored = [item for item in self.rows if item.attempts]
        if not scored:
            return None
        return max(scored, key=lambda item: item.observed_value)

    @property
    def stalled(self) -> tuple[str, ...]:
        """Dimensions attempted repeatedly that have never verified anything."""

        return tuple(
            item.dimension
            for item in self.rows
            if item.attempts >= 2 and item.verified == 0
        )


def build_yield_report(store: LedgerStore) -> YieldReport:
    yields = observe_dimension_yields(store)
    rows = tuple(sorted(yields.values(), key=lambda item: item.dimension))
    return YieldReport(rows=rows, total_attempts=sum(item.attempts for item in rows))
