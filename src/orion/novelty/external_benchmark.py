"""External novelty-benchmark protocol for #287.

The protocol freezes benchmark identity and evaluation semantics before outcomes.  It
never maps CANNOT_CHECK to a novelty label: abstention is evaluated as coverage/risk,
not converted into success.  This module is intentionally independent of any model
provider so the exact same evaluator can be replayed under #283.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from orion.novelty.types import NoveltyFinalState


class BenchmarkDisposition(str, Enum):
    NON_NOVEL = "NON_NOVEL"
    NARROWED = "NARROWED"
    NOVEL = "NOVEL"
    ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class BenchmarkPrediction:
    item_id: str
    human_label: int
    final_state: NoveltyFinalState

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError("benchmark item id is required")
        if self.human_label not in {1, 2, 3, 4, 5}:
            raise ValueError("RINoBench human label must be 1..5")
        object.__setattr__(self, "final_state", NoveltyFinalState(self.final_state))


@dataclass(frozen=True)
class BenchmarkMetrics:
    n: int
    covered: int
    correct_covered: int
    false_positive_novelty: int
    low_novelty_denominator: int
    abstained: int

    @property
    def coverage(self) -> float:
        return self.covered / self.n if self.n else 0.0

    @property
    def selective_accuracy(self) -> float:
        return self.correct_covered / self.covered if self.covered else 0.0

    @property
    def abstention_rate(self) -> float:
        return self.abstained / self.n if self.n else 0.0

    @property
    def false_positive_novelty_rate(self) -> float:
        if not self.low_novelty_denominator:
            return 0.0
        return self.false_positive_novelty / self.low_novelty_denominator


def disposition_for_state(state: NoveltyFinalState) -> BenchmarkDisposition:
    state = NoveltyFinalState(state)
    if state is NoveltyFinalState.CANNOT_CHECK:
        return BenchmarkDisposition.ABSTAIN
    if state is NoveltyFinalState.ALREADY_SOLVED:
        return BenchmarkDisposition.NON_NOVEL
    if state is NoveltyFinalState.NOVELTY_NARROWED:
        return BenchmarkDisposition.NARROWED
    if state is NoveltyFinalState.NOVELTY_SUPPORTED:
        return BenchmarkDisposition.NOVEL
    raise AssertionError(state)


def _compatible(label: int, disposition: BenchmarkDisposition) -> bool:
    if disposition is BenchmarkDisposition.NON_NOVEL:
        return label in {1, 2}
    if disposition is BenchmarkDisposition.NARROWED:
        return label == 3
    if disposition is BenchmarkDisposition.NOVEL:
        return label in {4, 5}
    return False


def evaluate_predictions(predictions: Iterable[BenchmarkPrediction]) -> BenchmarkMetrics:
    rows = tuple(predictions)
    covered = correct = false_positive = low_denominator = abstained = 0
    for row in rows:
        disposition = disposition_for_state(row.final_state)
        if row.human_label in {1, 2}:
            low_denominator += 1
            if disposition is BenchmarkDisposition.NOVEL:
                false_positive += 1
        if disposition is BenchmarkDisposition.ABSTAIN:
            abstained += 1
            continue
        covered += 1
        correct += int(_compatible(row.human_label, disposition))
    return BenchmarkMetrics(
        n=len(rows),
        covered=covered,
        correct_covered=correct,
        false_positive_novelty=false_positive,
        low_novelty_denominator=low_denominator,
        abstained=abstained,
    )
