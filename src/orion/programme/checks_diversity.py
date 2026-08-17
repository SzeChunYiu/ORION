"""Anti-collapse checks over search-universe and method diversity.

Collapse here is quiet. A programme narrowing to one source family, one method,
or one self-referential citation loop keeps producing confident output the whole
way down; the only visible symptom is that the variety of what it consults stops
changing. These checks look for exactly that, and refuse to judge when the
variety was never recorded.
"""

from __future__ import annotations

from orion.programme.hostile import CheckResult, HostileCheck, cannot_check, failed, passed
from orion.programme.programme_state import ProgrammeState

UNIVERSE_COLLAPSE = "HC-UNIVERSE-COLLAPSE"
METHOD_MONOCULTURE = "HC-METHOD-MONOCULTURE"
FORGOTTEN_NEGATIVE_HISTORY = "HC-FORGOTTEN-NEGATIVE-HISTORY"
CIRCULAR_SELF_CITATION = "HC-CIRCULAR-SELF-CITATION"
REPEATED_FAILURE_CLASS = "HC-REPEATED-FAILURE-CLASS"


def _check_universe_collapse(state: ProgrammeState) -> CheckResult:
    epochs = [epoch for epoch in state.ordered_epochs if epoch.source_family_evidence_counts]
    if not epochs:
        return cannot_check(
            UNIVERSE_COLLAPSE, "no epoch records per-source-family evidence counts"
        )
    ceiling = state.source_family_share_ceiling
    if ceiling is None:
        return cannot_check(
            UNIVERSE_COLLAPSE,
            "no declared source-family share ceiling; monoculture has no threshold",
        )

    findings: list[str] = []
    for epoch in epochs:
        total = epoch.total_family_evidence
        if total <= 0:
            findings.append(f"{epoch.epoch_id}: family counts sum to zero")
            continue
        for family, count in epoch.source_family_evidence_counts:
            share = count / total
            if share > ceiling:
                findings.append(
                    f"{epoch.epoch_id}: source family {family} holds"
                    f" {share:.2f} of evidence, above the {ceiling:.2f} ceiling"
                )
    for earlier, later in zip(epochs, epochs[1:]):
        lost = set(earlier.source_families) - set(later.source_families)
        if lost and len(later.source_families) < len(earlier.source_families):
            findings.append(
                f"{later.epoch_id}: source families dropped out without replacement:"
                f" {sorted(lost)}"
            )
    if findings:
        return failed(
            UNIVERSE_COLLAPSE,
            "the search universe is narrowing onto a source-family monoculture",
            tuple(findings),
        )
    return passed(UNIVERSE_COLLAPSE, "source-family spread stays inside the declared ceiling")


def _check_method_monoculture(state: ProgrammeState) -> CheckResult:
    epochs = [epoch for epoch in state.ordered_epochs if epoch.selected_method_ids]
    if len(epochs) < state.min_epochs_for_trend:
        return cannot_check(
            METHOD_MONOCULTURE,
            "fewer than min_epochs_for_trend epochs record a method selection",
        )
    selected = {method for epoch in epochs for method in epoch.selected_method_ids}
    if len(selected) > 1:
        return passed(METHOD_MONOCULTURE, "more than one method has been selected across epochs")

    challengers = {
        method
        for epoch in epochs
        for method in epoch.evaluated_method_ids
        if method not in selected
    }
    if not challengers:
        return failed(
            METHOD_MONOCULTURE,
            "one method has been selected in every epoch and no challenger was"
            " ever evaluated against it",
            (f"selected: {sorted(selected)}",),
        )
    return passed(
        METHOD_MONOCULTURE,
        "a single method holds, but challengers were evaluated against it",
    )


def _check_forgotten_negative_history(state: ProgrammeState) -> CheckResult:
    if not state.method_records:
        return cannot_check(FORGOTTEN_NEGATIVE_HISTORY, "no method records to check")
    findings: list[str] = []
    for record in state.method_records:
        if record.known_failure_classes and record.negative_history_chain_digest is None:
            findings.append(
                f"{record.method_id}@{record.method_version}: cites failure classes"
                " with no negative-history chain binding"
            )
        answered = {link.failure_class for link in record.causal_support}
        unanswered = sorted(set(record.known_failure_classes) - answered)
        if unanswered:
            findings.append(
                f"{record.method_id}@{record.method_version}: known failure classes"
                f" re-proposed with no causal support: {unanswered}"
            )
    if findings:
        return failed(
            FORGOTTEN_NEGATIVE_HISTORY,
            "a method carries recognized failure classes without answering them",
            tuple(findings),
        )
    return passed(
        FORGOTTEN_NEGATIVE_HISTORY,
        "every known failure class carries a causal-support link",
    )


def _check_circular_self_citation(state: ProgrammeState) -> CheckResult:
    settled = [record for record in state.object_records if record.authority.is_settled]
    if not settled:
        return cannot_check(
            CIRCULAR_SELF_CITATION,
            "no settled object claims; self-citation is only a defect for settled claims",
        )
    if not state.internal_source_families:
        return cannot_check(
            CIRCULAR_SELF_CITATION,
            "no internal source families declared; programme-internal sources are"
            " indistinguishable from external ones",
        )
    internal = set(state.internal_source_families)
    findings: list[str] = []
    for record in settled:
        families = {binding.source_family for binding in record.provenance}
        if not families:
            findings.append(f"{record.object_id}: settled with no provenance family")
        elif families <= internal:
            findings.append(
                f"{record.object_id}: every supporting source is programme-internal"
                f" ({sorted(families)})"
            )
    if findings:
        return failed(
            CIRCULAR_SELF_CITATION,
            "settled claims are supported only by the programme's own output",
            tuple(findings),
        )
    return passed(CIRCULAR_SELF_CITATION, "every settled claim has external support")


def _check_repeated_failure_class(state: ProgrammeState) -> CheckResult:
    epochs = [epoch for epoch in state.ordered_epochs if epoch.cycle_failure_interventions]
    if not epochs:
        return cannot_check(
            REPEATED_FAILURE_CLASS,
            "no epoch records failure-class/intervention pairs",
        )
    seen: dict[tuple[str, str], list[str]] = {}
    for epoch in epochs:
        for failure_class, intervention_id in epoch.cycle_failure_interventions:
            seen.setdefault((failure_class, intervention_id), []).append(epoch.epoch_id)
    findings = [
        f"{failure_class} met with the same intervention {intervention_id} in"
        f" epochs {epoch_ids}"
        for (failure_class, intervention_id), epoch_ids in sorted(seen.items())
        if len(epoch_ids) > 1
    ]
    if findings:
        return failed(
            REPEATED_FAILURE_CLASS,
            "a recognized failure class recurred and drew the same intervention",
            tuple(findings),
        )
    return passed(REPEATED_FAILURE_CLASS, "no failure class recurred under an unchanged response")


DIVERSITY_CHECKS: tuple[HostileCheck, ...] = (
    HostileCheck(
        check_id=UNIVERSE_COLLAPSE,
        title="Search universe collapsing onto one source family",
        failure_class="SEARCH_UNIVERSE_COLLAPSE",
        negative_fixture_id="test_universe_collapse_fails_on_source_family_monoculture",
        evaluate=_check_universe_collapse,
    ),
    HostileCheck(
        check_id=METHOD_MONOCULTURE,
        title="One method selected forever with no challenger",
        failure_class="METHOD_MONOCULTURE",
        negative_fixture_id="test_method_monoculture_fails_without_challenger",
        evaluate=_check_method_monoculture,
    ),
    HostileCheck(
        check_id=FORGOTTEN_NEGATIVE_HISTORY,
        title="Known failure classes re-proposed without causal support",
        failure_class="FORGOTTEN_NEGATIVE_HISTORY",
        negative_fixture_id="test_forgotten_negative_history_fails_on_unanswered_class",
        evaluate=_check_forgotten_negative_history,
    ),
    HostileCheck(
        check_id=CIRCULAR_SELF_CITATION,
        title="Settled claims supported only by programme-internal sources",
        failure_class="CIRCULAR_SELF_CITATION",
        negative_fixture_id="test_circular_self_citation_fails_on_internal_only_support",
        evaluate=_check_circular_self_citation,
    ),
    HostileCheck(
        check_id=REPEATED_FAILURE_CLASS,
        title="Same failure class, same intervention, more than once",
        failure_class="REPEATED_FAILURE_CLASS",
        negative_fixture_id="test_repeated_failure_class_fails_on_unchanged_response",
        evaluate=_check_repeated_failure_class,
    ),
)


__all__ = [
    "CIRCULAR_SELF_CITATION",
    "DIVERSITY_CHECKS",
    "FORGOTTEN_NEGATIVE_HISTORY",
    "METHOD_MONOCULTURE",
    "REPEATED_FAILURE_CLASS",
    "UNIVERSE_COLLAPSE",
]
