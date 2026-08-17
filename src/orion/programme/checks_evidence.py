"""Anti-collapse checks over protected evidence, evaluators and archives.

Each check answers one question and returns ``CANNOT_CHECK`` the moment its own
precondition is absent. The preconditions are stated in the reason string, so a
blocked report says what it could not see rather than merely that it blocked.
"""

from __future__ import annotations

from orion.programme.dependency import InvalidationTrigger
from orion.programme.hostile import CheckResult, HostileCheck, cannot_check, failed, passed
from orion.programme.programme_state import EXTERNAL_CUSTODY, ProgrammeState

BENCHMARK_OVERFIT = "HC-BENCHMARK-OVERFIT"
EVALUATOR_GAMING = "HC-EVALUATOR-GAMING"
STALE_AUTHORITY = "HC-STALE-AUTHORITY"
HIDDEN_DELETION = "HC-HIDDEN-DELETION"
INSUFFICIENT_PROTECTED_EVIDENCE = "HC-INSUFFICIENT-PROTECTED-EVIDENCE"


def _check_benchmark_overfit(state: ProgrammeState) -> CheckResult:
    epochs = [
        epoch
        for epoch in state.ordered_epochs
        if epoch.protected_metric is not None and epoch.fresh_transfer_metric is not None
    ]
    if len(epochs) < state.min_epochs_for_trend:
        return cannot_check(
            BENCHMARK_OVERFIT,
            "fewer than min_epochs_for_trend epochs carry both a protected and a"
            " fresh-transfer metric; divergence is not observable",
        )
    findings = [
        f"{later.epoch_id}: protected {earlier.protected_metric}->{later.protected_metric}"
        f" while fresh transfer {earlier.fresh_transfer_metric}"
        f"->{later.fresh_transfer_metric}"
        for earlier, later in zip(epochs, epochs[1:])
        if later.protected_metric > earlier.protected_metric
        and later.fresh_transfer_metric < earlier.fresh_transfer_metric
    ]
    if findings:
        return failed(
            BENCHMARK_OVERFIT,
            "protected score rose while independent fresh transfer fell",
            tuple(findings),
        )
    return passed(BENCHMARK_OVERFIT, "no protected/fresh-transfer divergence across epochs")


def _check_evaluator_gaming(state: ProgrammeState) -> CheckResult:
    epochs = state.ordered_epochs
    if not epochs:
        return cannot_check(EVALUATOR_GAMING, "no evaluation epochs recorded")
    unbound = [
        epoch.epoch_id
        for epoch in epochs
        if epoch.evaluator_artifact_hash is None or epoch.evaluator_custody is None
    ]
    if unbound:
        return cannot_check(
            EVALUATOR_GAMING,
            f"epochs without an evaluator hash or custody record: {sorted(unbound)}",
        )

    findings = [
        f"{epoch.epoch_id}: evaluator custody {epoch.evaluator_custody}"
        for epoch in epochs
        if epoch.evaluator_custody != EXTERNAL_CUSTODY
    ]

    # A declared revision is one where a reopen event sits at the same point in
    # the epoch ordering as the swap. ``ReopenEvent.epoch`` and
    # ``EpochSnapshot.sequence`` are the same ordinal under different names; the
    # pass branch of this correspondence is exercised by
    # ``test_evaluator_gaming_passes_on_a_declared_revision``.
    declared = {
        event.epoch
        for event in state.reopen_events
        if event.trigger is InvalidationTrigger.EVALUATOR_REVISION
    }
    for earlier, later in zip(epochs, epochs[1:]):
        if earlier.evaluator_artifact_hash == later.evaluator_artifact_hash:
            continue
        if later.sequence not in declared:
            findings.append(
                f"{later.epoch_id}: evaluator artifact changed with no"
                " EVALUATOR_REVISION reopen event at that epoch"
            )
    if findings:
        return failed(
            EVALUATOR_GAMING,
            "evaluator was inside candidate custody or changed undeclared",
            tuple(findings),
        )
    return passed(EVALUATOR_GAMING, "evaluator externally held and version-declared")


def _check_stale_authority(state: ProgrammeState) -> CheckResult:
    if not state.object_records:
        return cannot_check(STALE_AUTHORITY, "no object-knowledge records to check")
    current = state.source_version_map
    if not current:
        return cannot_check(
            STALE_AUTHORITY,
            "no current source-version map supplied; substitution is undetectable",
        )
    findings: list[str] = []
    for record in state.object_records:
        for binding in record.provenance:
            live = current.get(binding.source_id)
            if live is None:
                findings.append(
                    f"{record.object_id}: source {binding.source_id} has no current version"
                )
            elif live != binding.source_version:
                findings.append(
                    f"{record.object_id}: source {binding.source_id} bound at"
                    f" {binding.source_version} but is now {live}"
                )
    if findings:
        return failed(
            STALE_AUTHORITY,
            "claims rest on source versions that have since been substituted",
            tuple(findings),
        )
    return passed(STALE_AUTHORITY, "every provenance binding matches its live source version")


def _check_hidden_deletion(state: ProgrammeState) -> CheckResult:
    epochs = state.ordered_epochs
    if len(epochs) < state.min_epochs_for_trend:
        return cannot_check(
            HIDDEN_DELETION,
            "fewer than min_epochs_for_trend epochs; an archive cannot be compared to itself",
        )
    findings: list[str] = []
    for earlier, later in zip(epochs, epochs[1:]):
        for label, before, after in (
            ("negative history", earlier.negative_history_entry_ids,
             later.negative_history_entry_ids),
            ("rejected results", earlier.rejected_result_ids, later.rejected_result_ids),
            ("harmful results", earlier.harmful_result_ids, later.harmful_result_ids),
        ):
            dropped = set(before) - set(after)
            if dropped:
                findings.append(
                    f"{later.epoch_id}: {label} entries disappeared: {sorted(dropped)}"
                )
    # A superseded record must be replaced, not merely retired. A supersession
    # event with an empty successor list is a deletion wearing a reopening's name.
    laundered = sorted(
        {
            digest
            for event in state.reopen_events
            if not event.successor_record_digests
            for digest in event.superseded_record_digests
        }
    )
    if laundered:
        findings.append(f"records superseded with no successor recorded: {laundered}")
    if findings:
        return failed(
            HIDDEN_DELETION,
            "archived negative or harmful results were removed rather than superseded",
            tuple(findings),
        )
    return passed(HIDDEN_DELETION, "negative, rejected and harmful archives are append-only")


def _check_insufficient_protected_evidence(state: ProgrammeState) -> CheckResult:
    epochs = state.ordered_epochs
    if not epochs:
        return cannot_check(
            INSUFFICIENT_PROTECTED_EVIDENCE,
            "no evaluation epochs recorded; there is no protected evidence to be sufficient",
        )
    findings = [
        f"{epoch.epoch_id}: conclusion claimed without protected evidence"
        for epoch in epochs
        if epoch.conclusion_claimed and not epoch.protected_evidence_present
    ]
    if findings:
        return failed(
            INSUFFICIENT_PROTECTED_EVIDENCE,
            "a conclusion was asserted from an epoch that holds no protected evidence",
            tuple(findings),
        )
    unevidenced = [epoch.epoch_id for epoch in epochs if not epoch.protected_evidence_present]
    if unevidenced:
        return cannot_check(
            INSUFFICIENT_PROTECTED_EVIDENCE,
            f"epochs without protected evidence: {sorted(unevidenced)}",
        )
    return passed(
        INSUFFICIENT_PROTECTED_EVIDENCE,
        "every epoch carries protected evidence and no claim outruns it",
    )


EVIDENCE_CHECKS: tuple[HostileCheck, ...] = (
    HostileCheck(
        check_id=BENCHMARK_OVERFIT,
        title="Protected score rises while fresh transfer falls",
        failure_class="BENCHMARK_OVERFIT",
        negative_fixture_id="test_benchmark_overfit_fails_on_diverging_epochs",
        evaluate=_check_benchmark_overfit,
    ),
    HostileCheck(
        check_id=EVALUATOR_GAMING,
        title="Evaluator inside candidate custody or silently revised",
        failure_class="EVALUATOR_GAMING",
        negative_fixture_id="test_evaluator_gaming_fails_on_candidate_custody",
        evaluate=_check_evaluator_gaming,
    ),
    HostileCheck(
        check_id=STALE_AUTHORITY,
        title="Claims resting on substituted source versions",
        failure_class="STALE_AUTHORITY",
        negative_fixture_id="test_stale_authority_fails_on_source_version_substitution",
        evaluate=_check_stale_authority,
    ),
    HostileCheck(
        check_id=HIDDEN_DELETION,
        title="Negative or harmful results removed rather than superseded",
        failure_class="HIDDEN_DELETION",
        negative_fixture_id="test_hidden_deletion_fails_when_negative_history_shrinks",
        evaluate=_check_hidden_deletion,
    ),
    HostileCheck(
        check_id=INSUFFICIENT_PROTECTED_EVIDENCE,
        title="Conclusion outruns the protected evidence behind it",
        failure_class="INSUFFICIENT_PROTECTED_EVIDENCE",
        negative_fixture_id="test_insufficient_protected_evidence_fails_on_unbacked_claim",
        evaluate=_check_insufficient_protected_evidence,
    ),
)


__all__ = [
    "BENCHMARK_OVERFIT",
    "EVALUATOR_GAMING",
    "EVIDENCE_CHECKS",
    "HIDDEN_DELETION",
    "INSUFFICIENT_PROTECTED_EVIDENCE",
    "STALE_AUTHORITY",
]
