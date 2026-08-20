"""Exact successor-conditioned scientific-state benchmark.

Research-only deterministic generator/scorer.  The benchmark constructs pairs
whose candidate-visible current summaries and future transitions are identical,
while protected lineage makes the correct future scientific standing differ.

A current-summary-only policy therefore faces an exact information ceiling.  A
full-history or registered compact typed-lineage policy is expected to recover
the distinction; that is a control, not an ORION superiority claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import random
from typing import Callable, Iterable


class Standing(str, Enum):
    VERIFIED = "VERIFIED"
    AUTHORIZED = "AUTHORIZED"
    REOPENED = "REOPENED"


class FutureKind(str, Enum):
    EXIT_REPRESENTATION_SCOPE = "EXIT_REPRESENTATION_SCOPE"
    ADD_OPERATOR = "ADD_OPERATOR"
    MIGRATE_SCHEMA = "MIGRATE_SCHEMA"


class LineageKind(str, Enum):
    EVIDENCE_ROUTE = "EVIDENCE_ROUTE"
    NEGATIVE_CAUSE = "NEGATIVE_CAUSE"
    AUTHORITY_ORIGIN = "AUTHORITY_ORIGIN"


@dataclass(frozen=True)
class CurrentSummary:
    proposition: str
    object_kind: str
    current_answer: str
    current_standing: Standing

    def payload(self) -> dict:
        return {
            "proposition": self.proposition,
            "object_kind": self.object_kind,
            "current_answer": self.current_answer,
            "current_standing": self.current_standing.value,
        }


@dataclass(frozen=True)
class FutureTransition:
    kind: FutureKind
    target: str

    def payload(self) -> dict:
        return {"kind": self.kind.value, "target": self.target}


@dataclass(frozen=True)
class HistoryState:
    lineage_kind: LineageKind
    evidence_scope: str = ""
    independent_evidence_route: bool = False
    failure_cause: str = ""
    hard_invariant: str = ""
    authority_scope: str = ""
    transported_authority_target: str = ""

    def payload(self) -> dict:
        return {
            "lineage_kind": self.lineage_kind.value,
            "evidence_scope": self.evidence_scope,
            "independent_evidence_route": self.independent_evidence_route,
            "failure_cause": self.failure_cause,
            "hard_invariant": self.hard_invariant,
            "authority_scope": self.authority_scope,
            "transported_authority_target": self.transported_authority_target,
        }


@dataclass(frozen=True)
class TypedLineageState:
    """Minimal registered future-relevant coordinates for the V0 families."""

    evidence_scope_bound: bool = False
    has_independent_evidence_route: bool = False
    failure_was_missing_operator: str = ""
    failure_was_hard_invariant: bool = False
    authority_scope: str = ""
    authority_transport_target: str = ""

    def payload(self) -> dict:
        return {
            "evidence_scope_bound": self.evidence_scope_bound,
            "has_independent_evidence_route": self.has_independent_evidence_route,
            "failure_was_missing_operator": self.failure_was_missing_operator,
            "failure_was_hard_invariant": self.failure_was_hard_invariant,
            "authority_scope": self.authority_scope,
            "authority_transport_target": self.authority_transport_target,
        }


@dataclass(frozen=True)
class DelayedVariant:
    variant_id: str
    current: CurrentSummary
    future: FutureTransition
    history: HistoryState
    protected_future_standing: Standing

    def candidate_payload(self) -> dict:
        """Candidate-visible input: deliberately excludes variant id/history/gold."""
        return {
            "current": self.current.payload(),
            "future": self.future.payload(),
        }

    def protected_payload(self) -> dict:
        return {
            "variant_id": self.variant_id,
            "history": self.history.payload(),
            "protected_future_standing": self.protected_future_standing.value,
        }


@dataclass(frozen=True)
class DelayedPair:
    pair_id: str
    family_id: str
    left: DelayedVariant
    right: DelayedVariant

    def variants(self) -> tuple[DelayedVariant, DelayedVariant]:
        return (self.left, self.right)


@dataclass(frozen=True)
class FutureScore:
    exact: bool
    predicted: Standing
    expected: Standing


Policy = Callable[[CurrentSummary, FutureTransition], Standing]
HistoryPolicy = Callable[[CurrentSummary, HistoryState, FutureTransition], Standing]
TypedPolicy = Callable[[CurrentSummary, TypedLineageState, FutureTransition], Standing]


def _opaque(seed: int, tag: str) -> str:
    return hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()[:16]


def _base_summary(seed: int, family: str, index: int, standing: Standing) -> CurrentSummary:
    # Both members of a pair receive this exact same object.
    return CurrentSummary(
        proposition=f"p-{_opaque(seed + index, family + ':proposition')}",
        object_kind="CLAIM" if family != "negative_cause_debt" else "NEGATIVE_KNOWLEDGE",
        current_answer=f"ans-{_opaque(seed + index, family + ':answer')}",
        current_standing=standing,
    )


def _evidence_route_pair(seed: int, index: int) -> DelayedPair:
    family = "evidence_route_dependency_debt"
    pair_id = f"dpair-{_opaque(seed, family + ':' + str(index))}"
    current = _base_summary(seed, family, index, Standing.AUTHORIZED)
    target = f"rep-{_opaque(seed + index, 'new-representation')}"
    future = FutureTransition(FutureKind.EXIT_REPRESENTATION_SCOPE, target)
    scoped = f"rep-{_opaque(seed + index, 'old-representation')}"
    left = DelayedVariant(
        variant_id=f"v-{_opaque(seed + index, 'evidence-left')}",
        current=current,
        future=future,
        history=HistoryState(
            lineage_kind=LineageKind.EVIDENCE_ROUTE,
            evidence_scope=scoped,
            independent_evidence_route=False,
        ),
        protected_future_standing=Standing.REOPENED,
    )
    right = DelayedVariant(
        variant_id=f"v-{_opaque(seed + index, 'evidence-right')}",
        current=current,
        future=future,
        history=HistoryState(
            lineage_kind=LineageKind.EVIDENCE_ROUTE,
            evidence_scope="",
            independent_evidence_route=True,
        ),
        protected_future_standing=Standing.AUTHORIZED,
    )
    return DelayedPair(pair_id, family, left, right)


def _negative_cause_pair(seed: int, index: int) -> DelayedPair:
    family = "negative_cause_debt"
    pair_id = f"dpair-{_opaque(seed, family + ':' + str(index))}"
    current = _base_summary(seed, family, index, Standing.VERIFIED)
    operator = f"op-{_opaque(seed + index, 'future-operator')}"
    future = FutureTransition(FutureKind.ADD_OPERATOR, operator)
    left = DelayedVariant(
        variant_id=f"v-{_opaque(seed + index, 'negative-left')}",
        current=current,
        future=future,
        history=HistoryState(
            lineage_kind=LineageKind.NEGATIVE_CAUSE,
            failure_cause=f"MISSING_OPERATOR:{operator}",
        ),
        protected_future_standing=Standing.REOPENED,
    )
    right = DelayedVariant(
        variant_id=f"v-{_opaque(seed + index, 'negative-right')}",
        current=current,
        future=future,
        history=HistoryState(
            lineage_kind=LineageKind.NEGATIVE_CAUSE,
            failure_cause="HARD_INVARIANT_VIOLATION",
            hard_invariant=f"inv-{_opaque(seed + index, 'invariant')}",
        ),
        protected_future_standing=Standing.VERIFIED,
    )
    return DelayedPair(pair_id, family, left, right)


def _authority_origin_pair(seed: int, index: int) -> DelayedPair:
    family = "authority_origin_debt"
    pair_id = f"dpair-{_opaque(seed, family + ':' + str(index))}"
    current = _base_summary(seed, family, index, Standing.AUTHORIZED)
    old_schema = f"schema-{_opaque(seed + index, 's1')}"
    new_schema = f"schema-{_opaque(seed + index, 's2')}"
    future = FutureTransition(FutureKind.MIGRATE_SCHEMA, new_schema)
    left = DelayedVariant(
        variant_id=f"v-{_opaque(seed + index, 'authority-left')}",
        current=current,
        future=future,
        history=HistoryState(
            lineage_kind=LineageKind.AUTHORITY_ORIGIN,
            authority_scope=old_schema,
            transported_authority_target="",
        ),
        protected_future_standing=Standing.REOPENED,
    )
    right = DelayedVariant(
        variant_id=f"v-{_opaque(seed + index, 'authority-right')}",
        current=current,
        future=future,
        history=HistoryState(
            lineage_kind=LineageKind.AUTHORITY_ORIGIN,
            authority_scope=old_schema,
            transported_authority_target=new_schema,
        ),
        protected_future_standing=Standing.AUTHORIZED,
    )
    return DelayedPair(pair_id, family, left, right)


def generate_pairs(seed: int = 20260820, per_family: int = 4) -> tuple[DelayedPair, ...]:
    pairs: list[DelayedPair] = []
    for index in range(per_family):
        pairs.extend(
            (
                _evidence_route_pair(seed, index),
                _negative_cause_pair(seed, index),
                _authority_origin_pair(seed, index),
            )
        )
    rng = random.Random(seed ^ 0xD304)
    rng.shuffle(pairs)
    return tuple(pairs)


def candidate_jsonl(pairs: Iterable[DelayedPair]) -> str:
    rows: list[dict] = []
    for pair in pairs:
        for variant in pair.variants():
            rows.append(variant.candidate_payload())
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def protected_jsonl(pairs: Iterable[DelayedPair]) -> str:
    rows: list[dict] = []
    for pair in pairs:
        for variant in pair.variants():
            rows.append(variant.protected_payload())
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def typed_state_from_history(history: HistoryState) -> TypedLineageState:
    missing_operator = ""
    if history.failure_cause.startswith("MISSING_OPERATOR:"):
        missing_operator = history.failure_cause.split(":", 1)[1]
    return TypedLineageState(
        evidence_scope_bound=bool(history.evidence_scope),
        has_independent_evidence_route=history.independent_evidence_route,
        failure_was_missing_operator=missing_operator,
        failure_was_hard_invariant=bool(history.hard_invariant),
        authority_scope=history.authority_scope,
        authority_transport_target=history.transported_authority_target,
    )


def current_summary_policy(current: CurrentSummary, future: FutureTransition) -> Standing:
    """Best simple lossy policy for these pairs: preserve current standing.

    Because each pair has identical candidate input but opposite protected future
    consequence, *any deterministic current-summary-only policy* has a 1/2 per-pair
    ceiling. This specific policy witnesses that ceiling on the generated families.
    """
    del future
    return current.current_standing


def full_history_policy(
    current: CurrentSummary, history: HistoryState, future: FutureTransition
) -> Standing:
    if history.lineage_kind is LineageKind.EVIDENCE_ROUTE:
        if future.kind is FutureKind.EXIT_REPRESENTATION_SCOPE:
            if history.evidence_scope and not history.independent_evidence_route:
                return Standing.REOPENED
            return current.current_standing
    if history.lineage_kind is LineageKind.NEGATIVE_CAUSE:
        if future.kind is FutureKind.ADD_OPERATOR:
            if history.failure_cause == f"MISSING_OPERATOR:{future.target}":
                return Standing.REOPENED
            return current.current_standing
    if history.lineage_kind is LineageKind.AUTHORITY_ORIGIN:
        if future.kind is FutureKind.MIGRATE_SCHEMA:
            if history.transported_authority_target == future.target:
                return current.current_standing
            return Standing.REOPENED
    return current.current_standing


def typed_state_policy(
    current: CurrentSummary, typed: TypedLineageState, future: FutureTransition
) -> Standing:
    if future.kind is FutureKind.EXIT_REPRESENTATION_SCOPE:
        if typed.evidence_scope_bound and not typed.has_independent_evidence_route:
            return Standing.REOPENED
        return current.current_standing
    if future.kind is FutureKind.ADD_OPERATOR:
        if typed.failure_was_missing_operator == future.target:
            return Standing.REOPENED
        return current.current_standing
    if future.kind is FutureKind.MIGRATE_SCHEMA:
        if typed.authority_transport_target == future.target:
            return current.current_standing
        if typed.authority_scope:
            return Standing.REOPENED
    return current.current_standing


def score_variant(expected: Standing, predicted: Standing) -> FutureScore:
    return FutureScore(predicted == expected, predicted, expected)


def evaluate_current_summary(pairs: Iterable[DelayedPair]) -> dict:
    total = 0
    exact = 0
    per_pair_exact: list[int] = []
    for pair in pairs:
        pair_exact = 0
        for variant in pair.variants():
            predicted = current_summary_policy(variant.current, variant.future)
            result = score_variant(variant.protected_future_standing, predicted)
            total += 1
            exact += int(result.exact)
            pair_exact += int(result.exact)
        per_pair_exact.append(pair_exact)
    return {
        "n_variants": total,
        "exact": exact,
        "accuracy": exact / total if total else 0.0,
        "per_pair_exact": per_pair_exact,
    }


def evaluate_full_history(pairs: Iterable[DelayedPair]) -> dict:
    total = 0
    exact = 0
    for pair in pairs:
        for variant in pair.variants():
            predicted = full_history_policy(variant.current, variant.history, variant.future)
            total += 1
            exact += int(predicted == variant.protected_future_standing)
    return {"n_variants": total, "exact": exact, "accuracy": exact / total if total else 0.0}


def evaluate_typed_state(pairs: Iterable[DelayedPair]) -> dict:
    total = 0
    exact = 0
    for pair in pairs:
        for variant in pair.variants():
            typed = typed_state_from_history(variant.history)
            predicted = typed_state_policy(variant.current, typed, variant.future)
            total += 1
            exact += int(predicted == variant.protected_future_standing)
    return {"n_variants": total, "exact": exact, "accuracy": exact / total if total else 0.0}


def nonidentifiability_report(pairs: Iterable[DelayedPair]) -> dict:
    """Check the exact current-input ceiling conditions pair by pair."""
    n_pairs = 0
    identical_candidate_input = 0
    different_gold = 0
    same_future = 0
    for pair in pairs:
        n_pairs += 1
        if pair.left.candidate_payload() == pair.right.candidate_payload():
            identical_candidate_input += 1
        if pair.left.future == pair.right.future:
            same_future += 1
        if pair.left.protected_future_standing != pair.right.protected_future_standing:
            different_gold += 1
    ceiling = 0.5 if n_pairs and all(
        value == n_pairs
        for value in (identical_candidate_input, same_future, different_gold)
    ) else None
    return {
        "n_pairs": n_pairs,
        "identical_candidate_input_pairs": identical_candidate_input,
        "same_future_transition_pairs": same_future,
        "different_protected_future_standing_pairs": different_gold,
        "deterministic_current_summary_accuracy_ceiling": ceiling,
    }
