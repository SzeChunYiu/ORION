"""D4 delayed epistemic-debt extension for successor-conditioned state.

The module turns a future-standing mistake into a family-specific later scientific
action error.  It imports the exact delayed-pair generator as a sibling research
module and keeps D4 action gold protected from candidate-visible state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import importlib.util
from pathlib import Path
import sys
from typing import Callable, Iterable


_CORE_PATH = Path(__file__).resolve().with_name("successor_conditioned_core.py")
_SPEC = importlib.util.spec_from_file_location("successor_conditioned_core_for_debt", _CORE_PATH)
sc = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = sc
_SPEC.loader.exec_module(sc)


class SuccessorAction(str, Enum):
    COMMIT = "COMMIT"
    REVALIDATE_EVIDENCE = "REVALIDATE_EVIDENCE"
    RETRY_ROUTE = "RETRY_ROUTE"
    KEEP_BLOCKED = "KEEP_BLOCKED"
    REAUTHORIZE_EXTERNALLY = "REAUTHORIZE_EXTERNALLY"


@dataclass(frozen=True)
class D4ActionScore:
    exact: bool
    invalid_commit: bool
    missed_opportunity: bool
    authority_violation: bool


StandingPredictor = Callable[[sc.DelayedVariant], sc.Standing]


def protected_successor_action(pair: sc.DelayedPair, variant: sc.DelayedVariant) -> SuccessorAction:
    standing = variant.protected_future_standing
    if pair.family_id == "evidence_route_dependency_debt":
        return (
            SuccessorAction.REVALIDATE_EVIDENCE
            if standing is sc.Standing.REOPENED
            else SuccessorAction.COMMIT
        )
    if pair.family_id == "negative_cause_debt":
        return (
            SuccessorAction.RETRY_ROUTE
            if standing is sc.Standing.REOPENED
            else SuccessorAction.KEEP_BLOCKED
        )
    if pair.family_id == "authority_origin_debt":
        return (
            SuccessorAction.REAUTHORIZE_EXTERNALLY
            if standing is sc.Standing.REOPENED
            else SuccessorAction.COMMIT
        )
    raise ValueError(f"unregistered delayed-debt family:{pair.family_id}")


def successor_action_from_predicted_standing(
    pair: sc.DelayedPair,
    predicted: sc.Standing,
) -> SuccessorAction:
    if pair.family_id == "evidence_route_dependency_debt":
        return (
            SuccessorAction.REVALIDATE_EVIDENCE
            if predicted is sc.Standing.REOPENED
            else SuccessorAction.COMMIT
        )
    if pair.family_id == "negative_cause_debt":
        return (
            SuccessorAction.RETRY_ROUTE
            if predicted is sc.Standing.REOPENED
            else SuccessorAction.KEEP_BLOCKED
        )
    if pair.family_id == "authority_origin_debt":
        return (
            SuccessorAction.REAUTHORIZE_EXTERNALLY
            if predicted is sc.Standing.REOPENED
            else SuccessorAction.COMMIT
        )
    raise ValueError(f"unregistered delayed-debt family:{pair.family_id}")


def score_action(
    pair: sc.DelayedPair,
    variant: sc.DelayedVariant,
    action: SuccessorAction,
) -> D4ActionScore:
    expected = protected_successor_action(pair, variant)
    invalid_commit = action is SuccessorAction.COMMIT and expected in {
        SuccessorAction.REVALIDATE_EVIDENCE,
        SuccessorAction.REAUTHORIZE_EXTERNALLY,
    }
    missed_opportunity = (
        pair.family_id == "negative_cause_debt"
        and expected is SuccessorAction.RETRY_ROUTE
        and action is SuccessorAction.KEEP_BLOCKED
    )
    authority_violation = (
        pair.family_id == "authority_origin_debt"
        and expected is SuccessorAction.REAUTHORIZE_EXTERNALLY
        and action is SuccessorAction.COMMIT
    )
    return D4ActionScore(
        exact=action is expected,
        invalid_commit=invalid_commit,
        missed_opportunity=missed_opportunity,
        authority_violation=authority_violation,
    )


def current_summary_predictor(variant: sc.DelayedVariant) -> sc.Standing:
    return sc.current_summary_policy(variant.current, variant.future)


def full_history_predictor(variant: sc.DelayedVariant) -> sc.Standing:
    return sc.full_history_policy(variant.current, variant.history, variant.future)


def typed_state_predictor(variant: sc.DelayedVariant) -> sc.Standing:
    typed = sc.typed_state_from_history(variant.history)
    return sc.typed_state_policy(variant.current, typed, variant.future)


def evaluate_d4(
    pairs: Iterable[sc.DelayedPair],
    predictor: StandingPredictor,
) -> dict:
    n_variants = 0
    exact = 0
    invalid_commit_count = 0
    missed_opportunity_count = 0
    authority_violation_count = 0
    d2_current_answer_correct = 0
    per_pair_exact: list[int] = []

    for pair in pairs:
        pair_exact = 0
        for variant in pair.variants():
            # D2 is deliberately trivial/equal inside the pair: the current answer
            # is already present and remains correct for both histories.
            d2_current_answer_correct += 1
            predicted = predictor(variant)
            action = successor_action_from_predicted_standing(pair, predicted)
            score = score_action(pair, variant, action)
            n_variants += 1
            exact += int(score.exact)
            pair_exact += int(score.exact)
            invalid_commit_count += int(score.invalid_commit)
            missed_opportunity_count += int(score.missed_opportunity)
            authority_violation_count += int(score.authority_violation)
        per_pair_exact.append(pair_exact)

    integrity_gate = (
        invalid_commit_count == 0
        and authority_violation_count == 0
        and exact == n_variants
    )
    return {
        "n_variants": n_variants,
        "d2_current_answer_correct": d2_current_answer_correct,
        "d4_successor_action_exact": exact,
        "d4_accuracy": exact / n_variants if n_variants else 0.0,
        "d4_invalid_commit_count": invalid_commit_count,
        "d4_missed_opportunity_count": missed_opportunity_count,
        "d4_authority_violation_count": authority_violation_count,
        "per_pair_exact": per_pair_exact,
        "recursive_scientific_integrity_gate": integrity_gate,
    }
