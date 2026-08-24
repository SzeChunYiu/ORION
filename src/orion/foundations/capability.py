"""Finite reachability, diagnosis, method expansion, responsibility, and resource laws."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import ceil
from typing import Hashable, Iterable, Mapping, Sequence

from .model import ResourceVector, Terminal
from .sufficiency import FiniteInterface, is_target_sufficient


@dataclass(frozen=True, order=True)
class MethodRule:
    premises: frozenset[str]
    conclusion: str


@dataclass(frozen=True)
class MethodLanguage:
    language_id: str
    seeds: frozenset[str]
    rules: tuple[MethodRule, ...]

    def closure(self) -> frozenset[str]:
        reached = set(self.seeds)
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if rule.premises.issubset(reached) and rule.conclusion not in reached:
                    reached.add(rule.conclusion)
                    changed = True
        return frozenset(reached)


@dataclass(frozen=True)
class ObstructionCertificate:
    language_id: str
    target: str
    closure: frozenset[str]

    @property
    def valid(self) -> bool:
        return self.target not in self.closure


@dataclass(frozen=True)
class ExpansionCertificate:
    old_language_id: str
    extension: str
    target: str
    held_out_targets: frozenset[str]
    old_closure: frozenset[str]
    new_closure: frozenset[str]

    @property
    def valid(self) -> bool:
        return (
            self.extension not in self.old_closure
            and self.target not in self.old_closure
            and self.target in self.new_closure
            and self.held_out_targets.issubset(self.new_closure)
        )


def certify_obstruction(language: MethodLanguage, target: str) -> ObstructionCertificate:
    return ObstructionCertificate(language.language_id, target, language.closure())


def certify_expansion(
    old: MethodLanguage,
    extended: MethodLanguage,
    extension: str,
    target: str,
    held_out_targets: Iterable[str],
) -> ExpansionCertificate:
    return ExpansionCertificate(
        old_language_id=old.language_id,
        extension=extension,
        target=target,
        held_out_targets=frozenset(held_out_targets),
        old_closure=old.closure(),
        new_closure=extended.closure(),
    )


@dataclass(frozen=True)
class DiagnosticModel:
    causes: tuple[str, ...]
    interventions: tuple[str, ...]
    signatures: Mapping[str, tuple[Hashable, ...]]

    def __post_init__(self) -> None:
        for cause in self.causes:
            if len(self.signatures[cause]) != len(self.interventions):
                raise ValueError(f"signature length mismatch for {cause}")

    def identifiable(self, selected: Sequence[int] | None = None) -> bool:
        indices = tuple(range(len(self.interventions))) if selected is None else tuple(selected)
        seen: set[tuple[Hashable, ...]] = set()
        for cause in self.causes:
            signature = tuple(self.signatures[cause][index] for index in indices)
            if signature in seen:
                return False
            seen.add(signature)
        return True

    def minimal_intervention_set(self) -> tuple[str, ...] | None:
        for width in range(len(self.interventions) + 1):
            for selected in combinations(range(len(self.interventions)), width):
                if self.identifiable(selected):
                    return tuple(self.interventions[index] for index in selected)
        return None

    def compatible_causes(self, observations: Mapping[str, Hashable]) -> frozenset[str]:
        selected = [self.interventions.index(name) for name in observations]
        compatible: set[str] = set()
        for cause in self.causes:
            if all(
                self.signatures[cause][index] == observations[self.interventions[index]]
                for index in selected
            ):
                compatible.add(cause)
        return frozenset(compatible)


@dataclass(frozen=True)
class PlacementLaw:
    compile_cost: Fraction
    raw_per_query: Fraction
    compiled_per_query: Fraction
    recovery_cost: Fraction = Fraction(0)

    def compiled_total(self, queries: int, *, include_recovery: bool = False) -> Fraction:
        return self.compile_cost + queries * self.compiled_per_query + (
            self.recovery_cost if include_recovery else Fraction(0)
        )

    def raw_total(self, queries: int) -> Fraction:
        return queries * self.raw_per_query

    def break_even_horizon(self, *, include_recovery: bool = False) -> int | None:
        saving = self.raw_per_query - self.compiled_per_query
        if saving <= 0:
            return None
        fixed = self.compile_cost + (self.recovery_cost if include_recovery else Fraction(0))
        return ceil(fixed / saving)

    def compiled_is_cheaper(self, queries: int, *, include_recovery: bool = False) -> bool:
        return self.compiled_total(queries, include_recovery=include_recovery) <= self.raw_total(
            queries
        )


@dataclass(frozen=True)
class ResourceAction:
    action_id: str
    resources: ResourceVector
    utility: Fraction


def pareto_frontier(actions: Sequence[ResourceAction]) -> tuple[ResourceAction, ...]:
    frontier = []
    for candidate in actions:
        dominated = False
        for other in actions:
            if other.action_id == candidate.action_id:
                continue
            resource_better = other.resources.weakly_dominates(candidate.resources)
            utility_better = other.utility >= candidate.utility
            strict = other.resources != candidate.resources or other.utility > candidate.utility
            if resource_better and utility_better and strict:
                dominated = True
                break
        if not dominated:
            frontier.append(candidate)
    return tuple(sorted(frontier, key=lambda action: action.action_id))


def choose_with_prices(actions: Sequence[ResourceAction], prices: ResourceVector) -> ResourceAction:
    def score(action: ResourceAction) -> tuple[Fraction, str]:
        return (action.resources.weighted_cost(prices) - action.utility, action.action_id)

    return min(actions, key=score)


@dataclass(frozen=True)
class AllocationWorld:
    world_id: str
    certificate: Hashable
    optimal_action: str


def allocation_certificate_sufficient(worlds: Sequence[AllocationWorld]) -> bool:
    by_certificate: dict[Hashable, str] = {}
    for world in worlds:
        previous = by_certificate.setdefault(world.certificate, world.optimal_action)
        if previous != world.optimal_action:
            return False
    return True


@dataclass(frozen=True)
class ResponsibilityModel:
    states: tuple[str, ...]
    targets: Mapping[str, Mapping[str, Terminal]]

    def refines(self, stronger: str, weaker: str) -> bool:
        stronger_target = self.targets[stronger]
        weaker_target = self.targets[weaker]
        for left, right in combinations(self.states, 2):
            if stronger_target[left] == stronger_target[right]:
                if weaker_target[left] != weaker_target[right]:
                    return False
        return True

    def join_labels(self, responsibilities: Sequence[str]) -> dict[str, tuple[Terminal, ...]]:
        return {
            state_id: tuple(self.targets[name][state_id] for name in responsibilities)
            for state_id in self.states
        }

    def interface_supports(self, responsibility: str, interface: FiniteInterface) -> bool:
        return is_target_sufficient(self.states, interface, self.targets[responsibility])
