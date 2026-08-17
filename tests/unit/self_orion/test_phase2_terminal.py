import hashlib
from types import SimpleNamespace

import pytest

from orion.benchmarks.authority_external import (
    AuthorityBenchmarkAssessment,
    AuthorityBenchmarkStatus,
)
from orion.benchmarks.external_evidence import (
    ExternalCriterion,
    ExternalEvidenceManifest,
    ExternalEvidenceRecord,
    ExternalEvidenceStatus,
)
from orion.self_orion.phase2_campaign import (
    Phase2CampaignCriterion,
    Phase2CampaignEvidence,
    Phase2ExternalObservation,
    Phase2ExternalObservationBundle,
    Phase2ExternalObservationStatus,
    authority_campaign_artifact_hash,
)
from orion.self_orion.phase2_preflight import (
    FrozenPacketBinding,
    Phase2ClosurePreflight,
    build_frozen_live_trial_packet,
)
from orion.self_orion.phase2_terminal import (
    Phase2TerminalEvidence,
    Phase2TerminalStage,
    assess_phase2_terminal,
)
from orion.self_orion.phase2_terminal_receipts import (
    FailureReplayDisposition,
    FailureReplayEntry,
    FailureReplayReceipt,
    FinalIntegrationReceipt,
    FinalIntegrationStatus,
    RecurrenceOutcome,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _preflight() -> Phase2ClosurePreflight:
    return Phase2ClosurePreflight(
        protocol_id="phase2-shadow-closure-v1",
        subject_revision_hash=_digest("subject"),
        provider_manifest_hash=_digest("provider"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        baseline_id="simple-llm-retrieval-baseline-v1",
        resource_budget_units=100.0,
        # Declare what this preflight was frozen against; the identity gate
        # blocks without it, which is its purpose.
        frozen_packet=FrozenPacketBinding(
            packet_fingerprint=_digest("packet"),
            subject_revision_hash=_digest("subject"),
            provider_manifest_hash=_digest("provider"),
            evaluator_artifact_hash=_digest("evaluator"),
            evaluation_epoch_id="epoch:frozen",
            baseline_id="simple-llm-retrieval-baseline-v1",
            resource_budget_units=100.0,
            task_ids=tuple(
                task.task_id
                for task in Phase2ClosurePreflight.__dataclass_fields__["tasks"].default
            ),
        ),
    )


def _live(preflight):
    packet = build_frozen_live_trial_packet(preflight)
    return SimpleNamespace(
        packet_id=packet.packet_id,
        packet_fingerprint=packet.fingerprint,
        raw_search_trace_retained=True,
        all_resource_matched=True,
        all_failures_recordable=True,
        wide_task_count=1,
        deep_task_count=1,
        grants_self_promotion=False,
        evidence_artifact_hash=_digest("live"),
    )


def _development(preflight):
    assurance = SimpleNamespace(
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
    )
    return SimpleNamespace(
        case=SimpleNamespace(
            subject_revision_hash=preflight.subject_revision_hash,
            evaluation_epoch_id=preflight.evaluation_epoch_id,
        ),
        cycle=SimpleNamespace(change_control=SimpleNamespace(assurance=assurance)),
        blockers=(),
        process_demonstrated=True,
        self_merge_authorized=False,
        artifact_hash=_digest("development"),
    )


def _authority(preflight):
    return SimpleNamespace(
        binding=SimpleNamespace(
            subject_revision_hash=preflight.subject_revision_hash,
            evaluator_artifact_hash=preflight.evaluator_artifact_hash,
            evaluation_epoch_id=preflight.evaluation_epoch_id,
        ),
        blockers=(),
        all_attacks_executed=True,
        correct_cannot_check_passed=True,
        false_promotion_count=0,
        all_pass=True,
        artifact_hash=_digest("authority"),
    )


def _authority_benchmark():
    return AuthorityBenchmarkAssessment(
        status=AuthorityBenchmarkStatus.PASS,
        blockers=(),
        baseline_comparisons=(("baseline", True),),
        panel_artifact_hash=_digest("authority-panel"),
    )


def _replay(preflight, *, retained=False, self_verified=False):
    disposition = (
        FailureReplayDisposition.RETAINED_BLOCKING_FIBRE
        if retained
        else FailureReplayDisposition.REPAIRED_REPLAYED_FRESH_TRANSFER
    )
    entry = FailureReplayEntry(
        failure_id="failure:1",
        failure_class="retrieved-but-unused",
        source_failure_artifact_hash=_digest("failure"),
        negative_history_artifact_hash=_digest("negative-history"),
        discriminator_artifact_hash=_digest("discriminator"),
        recurrence_probe_artifact_hash=_digest("recurrence-probe"),
        disposition=disposition,
        recurrence_outcome=(
            RecurrenceOutcome.RECOGNIZED_AND_BLOCKED
            if retained
            else RecurrenceOutcome.NO_UNNOTICED_RECURRENCE
        ),
        replay_artifact_hash="" if retained else _digest("replay"),
        fresh_transfer_artifact_hash="" if retained else _digest("fresh-transfer"),
        blocking_fibre_artifact_hash=_digest("blocking-fibre") if retained else "",
        reopen_condition="new evidence or implementation change" if retained else "",
    )
    producer = _digest("lineage:producer")
    verifier = producer if self_verified else _digest("lineage:verifier")
    return FailureReplayReceipt(
        receipt_id="phase2:failure-replay",
        subject_revision_hash=preflight.subject_revision_hash,
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
        frozen_failure_index_artifact_hash=_digest("failure-index"),
        important_failure_ids=("failure:1",),
        entries=(entry,),
        producer_process_lineage_hash=producer,
        verifier_process_lineage_hash=verifier,
    )


def _integration(preflight, replay, *, status=FinalIntegrationStatus.PASS):
    return FinalIntegrationReceipt(
        receipt_id="phase2:final-integration",
        subject_revision_hash=preflight.subject_revision_hash,
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
        integration_commit_oid="abc123",
        integration_tree_sha256=_digest("integration-tree"),
        ci_run_id="31950000000",
        ci_head_commit_oid="abc123",
        ci_evidence_artifact_hash=_digest("ci-evidence"),
        external_manifest_artifact_hash=_digest("external-manifest-file"),
        papers_claim_ledger_artifact_hash=_digest("paper-ledger"),
        failure_replay_artifact_hash=replay.artifact_hash,
        producer_process_lineage_hash=_digest("integration-producer"),
        verifier_process_lineage_hash=_digest("integration-verifier"),
        status=status,
        note="exact-main integration checked externally",
    )


def _manifest(preflight):
    return ExternalEvidenceManifest(
        manifest_id="external:phase2",
        subject_revision_hash=preflight.subject_revision_hash,
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
        records=(
            ExternalEvidenceRecord(
                paper_id="P4",
                criterion=ExternalCriterion.P4_EVALUATOR_LOCKED,
                evidence_artifact_id="artifact:p4",
                evidence_artifact_hash=_digest("p4"),
                subject_revision_hash=preflight.subject_revision_hash,
                evaluator_artifact_hash=preflight.evaluator_artifact_hash,
                producer_process_lineage_hash=_digest("manifest-producer"),
                verifier_process_lineage_hash=_digest("manifest-verifier"),
                evaluation_epoch_id=preflight.evaluation_epoch_id,
                split_id="split:p4",
                status=ExternalEvidenceStatus.PASS,
                frozen_before_candidate=True,
                fresh_split=True,
                note="external evaluator frozen",
            ),
        ),
    )


def _campaign(preflight, replay=None, integration=None, *, observations=True):
    authority = _authority(preflight)
    benchmark = _authority_benchmark()
    bundle = None
    if observations:
        hashes = {
            Phase2CampaignCriterion.LIVE_TRIAL: _digest("live"),
            Phase2CampaignCriterion.MATCHED_BASELINE: _digest("baseline"),
            Phase2CampaignCriterion.SHADOW_DEVELOPMENT: _digest("development"),
            Phase2CampaignCriterion.AUTHORITY_BATTERY: authority_campaign_artifact_hash(
                authority.artifact_hash, benchmark.panel_artifact_hash
            ),
            Phase2CampaignCriterion.FAILURE_REPLAY: (
                replay.artifact_hash if replay is not None else _digest("unbound-replay")
            ),
            Phase2CampaignCriterion.FINAL_INTEGRATION: (
                integration.artifact_hash
                if integration is not None
                else _digest("unbound-integration")
            ),
        }
        bundle = Phase2ExternalObservationBundle(
            bundle_id="phase2:observations",
            subject_revision_hash=preflight.subject_revision_hash,
            evaluator_artifact_hash=preflight.evaluator_artifact_hash,
            evaluation_epoch_id=preflight.evaluation_epoch_id,
            observations=tuple(
                Phase2ExternalObservation(
                    criterion=criterion,
                    evidence_artifact_id=f"artifact:{criterion.value}",
                    evidence_artifact_hash=hashes[criterion],
                    subject_revision_hash=preflight.subject_revision_hash,
                    evaluator_artifact_hash=preflight.evaluator_artifact_hash,
                    producer_process_lineage_hash=_digest("obs-producer"),
                    verifier_process_lineage_hash=_digest("obs-verifier"),
                    evaluation_epoch_id=preflight.evaluation_epoch_id,
                    split_id=f"split:{criterion.value}",
                    status=Phase2ExternalObservationStatus.COMPLETE,
                    frozen_before_candidate=True,
                    fresh_split=True,
                    note="external observation",
                )
                for criterion in Phase2CampaignCriterion
            ),
        )
    return Phase2CampaignEvidence(
        preflight=preflight,
        live_trial=_live(preflight),
        baseline_bundle_hash=_digest("baseline"),
        development_trial=_development(preflight),
        authority_trial=authority,
        authority_benchmark=benchmark,
        external_observations=bundle,
        flagship_external_manifest=_manifest(preflight),
    )


def test_terminal_progression_requires_replay_then_integration_then_handback():
    preflight = _preflight()
    report = assess_phase2_terminal(Phase2TerminalEvidence(_campaign(preflight)))
    assert report.stage is Phase2TerminalStage.COMPLETE_FAILURE_REPLAY

    replay = _replay(preflight)
    report = assess_phase2_terminal(
        Phase2TerminalEvidence(_campaign(preflight, replay=replay), failure_replay=replay)
    )
    assert report.stage is Phase2TerminalStage.VERIFY_FINAL_INTEGRATION

    integration = _integration(preflight, replay)
    report = assess_phase2_terminal(
        Phase2TerminalEvidence(
            _campaign(preflight, replay=replay, integration=integration, observations=False),
            failure_replay=replay,
            final_integration=integration,
        )
    )
    assert report.stage is Phase2TerminalStage.HAND_BACK_EXTERNAL_EVIDENCE

    report = assess_phase2_terminal(
        Phase2TerminalEvidence(
            _campaign(preflight, replay=replay, integration=integration),
            failure_replay=replay,
            final_integration=integration,
        )
    )
    assert report.stage is Phase2TerminalStage.READY_FOR_TERMINAL_AUDIT
    assert report.ready_for_terminal_audit
    assert not report.grants_phase2_closure


def test_retained_blocking_fibre_is_valid_replay_process_evidence():
    preflight = _preflight()
    replay = _replay(preflight, retained=True)
    assert replay.entries[0].disposition is FailureReplayDisposition.RETAINED_BLOCKING_FIBRE
    assert replay.entries[0].reopen_condition


def test_unnoticed_recurrence_is_rejected_at_receipt_construction():
    with pytest.raises(ValueError, match="unnoticed recurrence"):
        FailureReplayEntry(
            failure_id="f",
            failure_class="class",
            source_failure_artifact_hash=_digest("a"),
            negative_history_artifact_hash=_digest("b"),
            discriminator_artifact_hash=_digest("c"),
            recurrence_probe_artifact_hash=_digest("d"),
            disposition=FailureReplayDisposition.REPAIRED_REPLAYED_FRESH_TRANSFER,
            recurrence_outcome=RecurrenceOutcome.UNNOTICED_RECURRENCE,
            replay_artifact_hash=_digest("e"),
            fresh_transfer_artifact_hash=_digest("f"),
        )


def test_terminal_rejects_self_verified_failure_replay():
    preflight = _preflight()
    replay = _replay(preflight, self_verified=True)
    report = assess_phase2_terminal(
        Phase2TerminalEvidence(_campaign(preflight, replay=replay), failure_replay=replay)
    )
    assert report.stage is Phase2TerminalStage.COMPLETE_FAILURE_REPLAY
    assert "failure_replay_self_verified" in report.blockers


def test_final_integration_must_bind_exact_ci_head():
    preflight = _preflight()
    replay = _replay(preflight)
    with pytest.raises(ValueError, match="exact integration commit"):
        FinalIntegrationReceipt(
            receipt_id="integration",
            subject_revision_hash=preflight.subject_revision_hash,
            evaluator_artifact_hash=preflight.evaluator_artifact_hash,
            evaluation_epoch_id=preflight.evaluation_epoch_id,
            integration_commit_oid="commit-a",
            integration_tree_sha256=_digest("tree"),
            ci_run_id="run",
            ci_head_commit_oid="commit-b",
            ci_evidence_artifact_hash=_digest("ci"),
            external_manifest_artifact_hash=_digest("manifest"),
            papers_claim_ledger_artifact_hash=_digest("ledger"),
            failure_replay_artifact_hash=replay.artifact_hash,
            producer_process_lineage_hash=_digest("p"),
            verifier_process_lineage_hash=_digest("v"),
            status=FinalIntegrationStatus.PASS,
            note="mismatch",
        )
