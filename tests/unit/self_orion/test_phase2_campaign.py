import hashlib
from types import SimpleNamespace

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
    Phase2CampaignStage,
    Phase2ExternalObservation,
    Phase2ExternalObservationBundle,
    Phase2ExternalObservationStatus,
    assess_phase2_campaign,
    authority_campaign_artifact_hash,
)
from orion.self_orion.phase2_preflight import (
    Phase2ClosurePreflight,
    build_frozen_live_trial_packet,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _preflight():
    return Phase2ClosurePreflight(
        protocol_id="phase2-shadow-closure-v1",
        subject_revision_hash=_digest("subject"),
        provider_manifest_hash=_digest("provider"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        baseline_id="simple-llm-retrieval-baseline-v1",
        resource_budget_units=100.0,
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
        evidence_artifact_hash=_digest("live-artifact"),
    )


def _development(preflight):
    assurance = SimpleNamespace(
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
    )
    control = SimpleNamespace(assurance=assurance)
    cycle = SimpleNamespace(change_control=control)
    case = SimpleNamespace(
        subject_revision_hash=preflight.subject_revision_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
    )
    return SimpleNamespace(
        case=case,
        cycle=cycle,
        blockers=(),
        process_demonstrated=True,
        self_merge_authorized=False,
        artifact_hash=_digest("development-artifact"),
    )


def _authority(preflight):
    binding = SimpleNamespace(
        subject_revision_hash=preflight.subject_revision_hash,
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
    )
    return SimpleNamespace(
        binding=binding,
        blockers=(),
        all_attacks_executed=True,
        correct_cannot_check_passed=True,
        false_promotion_count=0,
        all_pass=True,
        artifact_hash=_digest("authority-artifact"),
    )


def _authority_benchmark(status=AuthorityBenchmarkStatus.PASS):
    blockers = ()
    if status is AuthorityBenchmarkStatus.FAIL:
        blockers = ("safety_tradeoff_not_strictly_improved:baseline",)
    elif status is AuthorityBenchmarkStatus.CANNOT_CHECK:
        blockers = ("baseline:metrics_incomplete",)
    return AuthorityBenchmarkAssessment(
        status=status,
        blockers=blockers,
        baseline_comparisons=(("baseline", status is AuthorityBenchmarkStatus.PASS),),
        panel_artifact_hash=_digest(f"authority-benchmark:{status.value}"),
    )


def _expected_observation_hashes():
    return {
        Phase2CampaignCriterion.LIVE_TRIAL: _digest("live-artifact"),
        Phase2CampaignCriterion.MATCHED_BASELINE: _digest("baseline-bundle"),
        Phase2CampaignCriterion.SHADOW_DEVELOPMENT: _digest("development-artifact"),
        Phase2CampaignCriterion.AUTHORITY_BATTERY: authority_campaign_artifact_hash(
            _digest("authority-artifact"),
            _digest("authority-benchmark:PASS"),
        ),
        Phase2CampaignCriterion.FAILURE_REPLAY: _digest("artifact:FAILURE_REPLAY"),
        Phase2CampaignCriterion.FINAL_INTEGRATION: _digest("artifact:FINAL_INTEGRATION"),
    }


def _observations(preflight, *, self_verified=False, artifact_overrides=None):
    producer = _digest("producer")
    verifier = producer if self_verified else _digest("verifier")
    evidence_hashes = _expected_observation_hashes()
    if artifact_overrides:
        evidence_hashes.update(artifact_overrides)
    return Phase2ExternalObservationBundle(
        bundle_id="phase2:external-observations",
        subject_revision_hash=preflight.subject_revision_hash,
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
        observations=tuple(
            Phase2ExternalObservation(
                criterion=criterion,
                evidence_artifact_id=f"artifact:{criterion.value}",
                evidence_artifact_hash=evidence_hashes[criterion],
                subject_revision_hash=preflight.subject_revision_hash,
                evaluator_artifact_hash=preflight.evaluator_artifact_hash,
                producer_process_lineage_hash=producer,
                verifier_process_lineage_hash=verifier,
                evaluation_epoch_id=preflight.evaluation_epoch_id,
                split_id=f"split:{criterion.value.lower()}",
                status=Phase2ExternalObservationStatus.COMPLETE,
                frozen_before_candidate=True,
                fresh_split=True,
                note="independent Phase-2 campaign observation",
            )
            for criterion in Phase2CampaignCriterion
        ),
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
                evidence_artifact_id="artifact:p4-evaluator-lock",
                evidence_artifact_hash=_digest("p4-artifact"),
                subject_revision_hash=preflight.subject_revision_hash,
                evaluator_artifact_hash=preflight.evaluator_artifact_hash,
                producer_process_lineage_hash=_digest("producer"),
                verifier_process_lineage_hash=_digest("verifier"),
                evaluation_epoch_id=preflight.evaluation_epoch_id,
                split_id="split:p4:fresh",
                status=ExternalEvidenceStatus.PASS,
                frozen_before_candidate=True,
                fresh_split=True,
                note="protected evaluator lock verified externally",
            ),
        ),
    )


def test_campaign_reports_next_missing_artifact_in_order():
    preflight = _preflight()
    baseline_hash = _digest("baseline-bundle")

    report = assess_phase2_campaign(Phase2CampaignEvidence(preflight))
    assert report.stage is Phase2CampaignStage.EXECUTE_LIVE_TRIAL

    report = assess_phase2_campaign(
        Phase2CampaignEvidence(preflight, _live(preflight), baseline_hash)
    )
    assert report.stage is Phase2CampaignStage.EXECUTE_SHADOW_DEVELOPMENT

    report = assess_phase2_campaign(
        Phase2CampaignEvidence(
            preflight,
            _live(preflight),
            baseline_hash,
            _development(preflight),
        )
    )
    assert report.stage is Phase2CampaignStage.EXECUTE_AUTHORITY_TRIAL

    report = assess_phase2_campaign(
        Phase2CampaignEvidence(
            preflight,
            _live(preflight),
            baseline_hash,
            _development(preflight),
            _authority(preflight),
        )
    )
    assert report.stage is Phase2CampaignStage.EXECUTE_AUTHORITY_TRIAL
    assert "authority_baseline_benchmark_missing" in report.blockers

    report = assess_phase2_campaign(
        Phase2CampaignEvidence(
            preflight,
            _live(preflight),
            baseline_hash,
            _development(preflight),
            _authority(preflight),
            _authority_benchmark(),
        )
    )
    assert report.stage is Phase2CampaignStage.HAND_BACK_EXTERNAL_EVIDENCE


def test_campaign_rejects_nonpassing_authority_baseline_panel():
    preflight = _preflight()
    common = dict(
        preflight=preflight,
        live_trial=_live(preflight),
        baseline_bundle_hash=_digest("baseline-bundle"),
        development_trial=_development(preflight),
        authority_trial=_authority(preflight),
    )
    failed = assess_phase2_campaign(
        Phase2CampaignEvidence(
            **common,
            authority_benchmark=_authority_benchmark(AuthorityBenchmarkStatus.FAIL),
        )
    )
    assert failed.stage is Phase2CampaignStage.EXECUTE_AUTHORITY_TRIAL
    assert "authority_baseline_safety_tradeoff_not_improved" in failed.blockers

    unknown = assess_phase2_campaign(
        Phase2CampaignEvidence(
            **common,
            authority_benchmark=_authority_benchmark(AuthorityBenchmarkStatus.CANNOT_CHECK),
        )
    )
    assert unknown.stage is Phase2CampaignStage.EXECUTE_AUTHORITY_TRIAL
    assert "authority_baseline_benchmark_cannot_check" in unknown.blockers


def test_campaign_reaches_terminal_audit_only_with_independent_complete_receipts():
    preflight = _preflight()
    report = assess_phase2_campaign(
        Phase2CampaignEvidence(
            preflight=preflight,
            live_trial=_live(preflight),
            baseline_bundle_hash=_digest("baseline-bundle"),
            development_trial=_development(preflight),
            authority_trial=_authority(preflight),
            authority_benchmark=_authority_benchmark(),
            external_observations=_observations(preflight),
            flagship_external_manifest=_manifest(preflight),
        )
    )
    assert report.stage is Phase2CampaignStage.READY_FOR_TERMINAL_AUDIT
    assert report.ready_for_terminal_audit
    assert not report.grants_phase2_closure
    assert not report.grants_governed_self_orion
    assert len(report.external_observation_bundle_hash) == 64
    assert len(report.authority_benchmark_panel_hash) == 64
    assert len(report.authority_campaign_artifact_hash) == 64


def test_campaign_rejects_external_observation_bound_to_wrong_artifact():
    preflight = _preflight()
    report = assess_phase2_campaign(
        Phase2CampaignEvidence(
            preflight=preflight,
            live_trial=_live(preflight),
            baseline_bundle_hash=_digest("baseline-bundle"),
            development_trial=_development(preflight),
            authority_trial=_authority(preflight),
            authority_benchmark=_authority_benchmark(),
            external_observations=_observations(
                preflight,
                artifact_overrides={
                    Phase2CampaignCriterion.LIVE_TRIAL: _digest("wrong-live-artifact")
                },
            ),
            flagship_external_manifest=_manifest(preflight),
        )
    )
    assert report.stage is Phase2CampaignStage.HAND_BACK_EXTERNAL_EVIDENCE
    assert "external_observation_artifact_mismatch:LIVE_TRIAL" in report.blockers


def test_campaign_rejects_self_verified_external_observations():
    preflight = _preflight()
    report = assess_phase2_campaign(
        Phase2CampaignEvidence(
            preflight=preflight,
            live_trial=_live(preflight),
            baseline_bundle_hash=_digest("baseline-bundle"),
            development_trial=_development(preflight),
            authority_trial=_authority(preflight),
            authority_benchmark=_authority_benchmark(),
            external_observations=_observations(preflight, self_verified=True),
            flagship_external_manifest=_manifest(preflight),
        )
    )
    assert report.stage is Phase2CampaignStage.HAND_BACK_EXTERNAL_EVIDENCE
    assert any("external_observation_self_verified" in item for item in report.blockers)


def test_campaign_rejects_counts_only_live_trial_even_if_other_summaries_look_good():
    preflight = _preflight()
    live = _live(preflight)
    live.raw_search_trace_retained = False
    report = assess_phase2_campaign(
        Phase2CampaignEvidence(
            preflight=preflight,
            live_trial=live,
            baseline_bundle_hash=_digest("baseline-bundle"),
        )
    )
    assert report.stage is Phase2CampaignStage.EXECUTE_LIVE_TRIAL
    assert "raw_search_trace_not_retained_for_every_task" in report.blockers
