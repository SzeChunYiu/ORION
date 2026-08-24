"""Finite indistinguishability and regime-transport laws."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Hashable, Mapping, Sequence


@dataclass(frozen=True)
class OpenWorldCompletion:
    world_id: str
    observed_history: tuple[Hashable, ...]
    task_closed: bool


def deterministic_closure_error(
    completions: Sequence[OpenWorldCompletion],
    decision_by_history: Mapping[tuple[Hashable, ...], bool],
    probabilities: Mapping[str, Fraction],
) -> Fraction:
    return sum(
        (
            probabilities[world.world_id]
            for world in completions
            if decision_by_history[world.observed_history] != world.task_closed
        ),
        Fraction(0),
    )


def best_deterministic_closure_error(
    completions: Sequence[OpenWorldCompletion],
    probabilities: Mapping[str, Fraction],
) -> Fraction:
    histories = sorted({world.observed_history for world in completions}, key=repr)
    best: Fraction | None = None
    for decisions in product((False, True), repeat=len(histories)):
        policy = dict(zip(histories, decisions, strict=True))
        error = deterministic_closure_error(completions, policy, probabilities)
        best = error if best is None else min(best, error)
    if best is None:
        raise ValueError("at least one completion is required")
    return best


@dataclass(frozen=True)
class RegimeTransport:
    transport_id: str
    source_regime: str
    target_regime: str
    obligation_map: Mapping[str, str]
    evidence_semantics_preserved: bool
    objective_semantics_preserved: bool
    epoch_bound: bool

    @property
    def sound(self) -> bool:
        return (
            self.evidence_semantics_preserved
            and self.objective_semantics_preserved
            and self.epoch_bound
        )


def compose_transport(first: RegimeTransport, second: RegimeTransport) -> RegimeTransport:
    if first.target_regime != second.source_regime:
        raise ValueError("transport endpoints do not compose")
    mapped: dict[str, str] = {}
    for source, intermediate in first.obligation_map.items():
        if intermediate not in second.obligation_map:
            continue
        mapped[source] = second.obligation_map[intermediate]
    return RegimeTransport(
        transport_id=f"{second.transport_id}∘{first.transport_id}",
        source_regime=first.source_regime,
        target_regime=second.target_regime,
        obligation_map=mapped,
        evidence_semantics_preserved=(
            first.evidence_semantics_preserved and second.evidence_semantics_preserved
        ),
        objective_semantics_preserved=(
            first.objective_semantics_preserved and second.objective_semantics_preserved
        ),
        epoch_bound=first.epoch_bound and second.epoch_bound,
    )
