from __future__ import annotations

import hashlib
from types import SimpleNamespace

import orion.self_orion.phase2_terminal_audit as terminal
from orion.self_orion.evidence_admission import (
    EvidenceArtifactBinding,
    Phase2EvidenceReceipt,
)
from orion.self_orion.phase2_campaign import (
    Phase2CampaignCriterion,
    Phase2CampaignReport,
    Phase2CampaignStage,
    Phase2ExternalObservation,
    Phase2ExternalObservationBundle,
    Phase2ExternalObservationStatus,
)


SUBJECT = "1" * 64
EVALUATOR = "2" * 64
PRODUCER = "3" * 64
VERIFIER = "4" * 64
EPOCH = "epoch-terminal"


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _campaign(*, ready: bool) -> Phase2CampaignReport:
    return Phase2CampaignReport(
        stage=(
            Phase2CampaignStage.READY_FOR_TERMINAL_AUDIT
            if ready
            else Phase2CampaignStage.EXECUTE_LIVE_TRIAL
        ),
        blockers=() if ready else ("live_trial_artifact_missing",),
        packet_fingerprint=None,
        live_trial_artifact_hash=None,
        development_trial_artifact_hash=None,
        authority_trial_artifact_hash=None,
        authority_benchmark_panel_hash=None,
        authority_campaign_artifact_hash=None,
        external_observation_bundle_hash=None,
    )


def _bundle(artifact_hash: str) -> Phase2ExternalObservationBundle:
    observation = Phase2ExternalObservation(
        criterion=Phase2CampaignCriterion.LIVE_TRIAL,
        evidence_artifact_id="live",
        evidence_artifact_hash=artifact_hash,
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        producer_process_lineage_hash=PRODUCER,
        verifier_process_lineage_hash=VERIFIER,
        evaluation_epoch_id=EPOCH,
        split_id="fresh",
        status=Phase2ExternalObservationStatus.COMPLETE,
        frozen_before_candidate=True,
        fresh_split=True,
        note="host observation",
    )
    return Phase2ExternalObservationBundle(
        bundle_id="terminal-bundle",
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id=EPOCH,
        observations=(observation,),
    )


def _receipt(artifact_hash: str) -> Phase2EvidenceReceipt:
    return Phase2EvidenceReceipt(
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id=EPOCH,
        artifacts=(
            EvidenceArtifactBinding(
                artifact_id="live",
                relative_path="live.json",
                sha256=artifact_hash,
            ),
        ),
    )


def test_terminal_audit_recomputes_campaign_and_stops_before_artifact_admission(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(terminal, "assess_phase2_campaign", lambda _: _campaign(ready=False))

    def should_not_run(*args, **kwargs):  # pragma: no cover - failure sentinel
        raise AssertionError("artifact admission must not run for an unready campaign")

    monkeypatch.setattr(terminal, "verify_phase2_observation_bundle_artifacts", should_not_run)
    evidence = SimpleNamespace(external_observations=_bundle("a" * 64))

    report = terminal.audit_phase2_terminal(evidence, _receipt("a" * 64), tmp_path)

    assert report.status is terminal.Phase2TerminalAuditStatus.CAMPAIGN_NOT_READY
    assert report.blockers == ("campaign:live_trial_artifact_missing",)
    assert not report.eligible_for_external_closure
    assert not report.grants_phase2_closure
    assert not report.grants_governed_self_orion


def test_ready_campaign_with_only_a_summary_and_missing_bytes_cannot_close(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(terminal, "assess_phase2_campaign", lambda _: _campaign(ready=True))
    evidence = SimpleNamespace(external_observations=_bundle("a" * 64))

    report = terminal.audit_phase2_terminal(evidence, _receipt("a" * 64), tmp_path)

    assert report.status is terminal.Phase2TerminalAuditStatus.EXTERNAL_EVIDENCE_NOT_ADMITTED
    assert "evidence:artifact_missing:live" in report.blockers
    assert not report.eligible_for_external_closure
    assert not report.grants_phase2_closure


def test_ready_campaign_with_exact_host_visible_bytes_is_only_eligible_for_external_closure(
    tmp_path, monkeypatch
) -> None:
    payload = b'{"status":"COMPLETE"}\n'
    (tmp_path / "live.json").write_bytes(payload)
    digest = _hash(payload)
    monkeypatch.setattr(terminal, "assess_phase2_campaign", lambda _: _campaign(ready=True))
    evidence = SimpleNamespace(external_observations=_bundle(digest))

    report = terminal.audit_phase2_terminal(evidence, _receipt(digest), tmp_path)

    assert report.status is terminal.Phase2TerminalAuditStatus.ELIGIBLE_FOR_EXTERNAL_CLOSURE
    assert report.eligible_for_external_closure
    assert report.blockers == ()
    assert report.evidence_admission is not None
    assert report.evidence_admission.admitted
    # Eligibility is a hand-off to external authority, never an in-process promotion.
    assert not report.grants_phase2_closure
    assert not report.grants_governed_self_orion


def test_terminal_audit_defensively_rejects_missing_observation_bundle(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(terminal, "assess_phase2_campaign", lambda _: _campaign(ready=True))
    evidence = SimpleNamespace(external_observations=None)

    report = terminal.audit_phase2_terminal(evidence, _receipt("a" * 64), tmp_path)

    assert report.status is terminal.Phase2TerminalAuditStatus.EXTERNAL_EVIDENCE_NOT_ADMITTED
    assert report.blockers == ("external_observation_bundle_missing_at_terminal_audit",)
    assert not report.eligible_for_external_closure
