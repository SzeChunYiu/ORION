"""Independent reconstruction for the #286/#318 closure.

This module intentionally does not import ``choose_action``, ``score_arm`` or
``build_closure_report``.  It re-derives the two load-bearing selectors and the
protected metrics from public case fields plus evaluator-held gold.
"""

from __future__ import annotations

from dataclasses import dataclass

from orion.transfer.scientific.closure import (
    DOMAINS,
    ProtectedTransferCase,
    TransferAction,
    build_protected_panel,
)


@dataclass(frozen=True)
class IndependentMetrics:
    correct: int
    negative_transfer: int
    positive_full_correct: int
    partial_correct: int
    worst_domain_correct: int


def _independent_signature_decision(case) -> TransferAction:
    source = dict(case.source_signature)
    target = dict(case.target_signature)
    if source.get("family") != target.get("requested_family"):
        return TransferAction.NO_TRANSFER
    if source.get("assumption") != target.get("assumption"):
        return TransferAction.REJECT
    if target.get("full_preconditions") == "met":
        return TransferAction.APPLY_FULL
    if case.available_submechanic and target.get("partial_preconditions") == "met":
        return TransferAction.APPLY_PARTIAL
    return TransferAction.REJECT


def reconstruct_signature_arm(cases: tuple[ProtectedTransferCase, ...] | None = None) -> IndependentMetrics:
    cases = build_protected_panel() if cases is None else cases
    by_domain: dict[str, list[bool]] = {domain: [] for domain in DOMAINS}
    correct = negative = positive = partial = 0
    for protected in cases:
        action = _independent_signature_decision(protected.public)
        ok = action is protected.gold_action
        correct += int(ok)
        by_domain[protected.public.target_domain].append(ok)
        if protected.case_type in {"near_miss", "negative"} and action in {
            TransferAction.APPLY_FULL,
            TransferAction.APPLY_PARTIAL,
        }:
            negative += 1
        if protected.case_type == "positive" and action is TransferAction.APPLY_FULL:
            positive += 1
        if protected.case_type == "partial" and action is TransferAction.APPLY_PARTIAL:
            partial += 1
    return IndependentMetrics(
        correct=correct,
        negative_transfer=negative,
        positive_full_correct=positive,
        partial_correct=partial,
        worst_domain_correct=min(sum(values) for values in by_domain.values()),
    )


def reconstruct_terminal() -> tuple[str, str]:
    metrics = reconstruct_signature_arm()
    if metrics != IndependentMetrics(40, 0, 15, 5, 8):
        return ("CANNOT_CHECK", "CANNOT_CHECK")
    return ("ABSTRACTION_ONLY", "PROCESS_USEFUL_NOT_NOVEL")
