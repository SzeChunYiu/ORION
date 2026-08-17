"""Synthetic known-answer bundles. These are not published V1 outcomes."""

from __future__ import annotations

from orion.study.global_positive.outcomes import (
    CandidateOutcomeBundle,
    NegativeHistory,
    NegativeHistoryRecord,
    ObservationStatus,
    family_outcome,
)
from orion.study.global_positive.portfolio import FrozenPortfolio, load_portfolio
from orion.study.global_positive.schema import digest, load_schema

ADOPTION_BOUNDARY = "V2_ADDITIVE"

PASSING_DELTAS = {
    "abstention_correctness": 0.0,
    "correctness": 0.05,
    "cost": 0.0,
    "false_authority": 0.0,
    "fresh_transfer": 0.03,
    "harmful_transfer": 0.0,
    "obstruction_safety": 0.0,
    "retrieval_recall": 0.0,
}

KNOWN_ANSWER_NONCE = "issue-285-known-answer"


def known_answer_freeze() -> FrozenPortfolio:
    return load_portfolio().bind_for_tests(KNOWN_ANSWER_NONCE)


def complete_bundle(
    *,
    candidate_id: str = "cand-pass",
    deltas: dict[str, float] | None = None,
    evaluator_integrity: ObservationStatus = ObservationStatus.PASS,
    omit_families: tuple[str, ...] = (),
    family_overrides: dict[str, dict[str, float]] | None = None,
    cannot_check: dict[str, tuple[str, ...]] | None = None,
    extra_keys: tuple[str, ...] = (),
    failure_classes: tuple[str, ...] = (),
    split_coverage: tuple[str, ...] | None = None,
) -> CandidateOutcomeBundle:
    freeze = known_answer_freeze()
    schema = load_schema()
    used = dict(PASSING_DELTAS if deltas is None else deltas)
    families = []
    for family_id in freeze.required_family_ids:
        if family_id in omit_families:
            continue
        local = dict(used)
        if family_overrides and family_id in family_overrides:
            local.update(family_overrides[family_id])
        families.append(
            family_outcome(
                family_id,
                local,
                split_coverage=split_coverage,
                cannot_check=(cannot_check or {}).get(family_id, ()),
            )
        )
    if not schema.spec("evaluator_integrity").mandatory:
        raise AssertionError("evaluator_integrity must remain mandatory")
    return CandidateOutcomeBundle(
        candidate_id=candidate_id,
        candidate_digest=digest({"candidate_id": candidate_id, "deltas": used}),
        family_outcomes=tuple(families),
        evaluator_integrity=evaluator_integrity,
        failure_classes=failure_classes,
        extra_keys=extra_keys,
    )


def harmful_history(failure_class: str) -> NegativeHistory:
    return NegativeHistory(
        (
            NegativeHistoryRecord(
                failure_class=failure_class,
                candidate_digest="a" * 64,
                terminal="HARMFUL_REGRESSION",
                dimension_ids=("harmful_transfer",),
                family_ids=("software_debugging_development",),
            ),
        )
    )
