import hashlib

import pytest

from orion.benchmarks.authority_external import (
    FROZEN_AUTHORITY_BASELINE_IDS,
    AuthorityBenchmarkMetrics,
    AuthorityBenchmarkPanel,
    AuthorityBenchmarkStatus,
    AuthoritySystemObservation,
    assess_authority_benchmark,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _metrics(*, strong: bool, complete: bool = True):
    if not complete:
        return AuthorityBenchmarkMetrics(
            claim_correct=0,
            claim_total=0,
            source_attribution_correct=0,
            source_attribution_total=0,
            support_contradiction_tp=0,
            support_contradiction_fp=0,
            support_contradiction_fn=0,
            conflation_detected=0,
            conflation_total=0,
            substitution_detected=0,
            substitution_total=0,
            tamper_leakage_detected=0,
            tamper_leakage_total=0,
            false_promotions=0,
            promotion_opportunities=0,
            correct_cannot_check=0,
            cannot_check_opportunities=0,
            resource_units=10.0,
            latency_seconds=3.0,
        )
    if strong:
        return AuthorityBenchmarkMetrics(
            claim_correct=10,
            claim_total=10,
            source_attribution_correct=10,
            source_attribution_total=10,
            support_contradiction_tp=10,
            support_contradiction_fp=0,
            support_contradiction_fn=0,
            conflation_detected=10,
            conflation_total=10,
            substitution_detected=10,
            substitution_total=10,
            tamper_leakage_detected=10,
            tamper_leakage_total=10,
            false_promotions=0,
            promotion_opportunities=10,
            correct_cannot_check=10,
            cannot_check_opportunities=10,
            false_negative_count=0,
            clean_positive_total=3,
            resource_units=10.0,
            latency_seconds=3.0,
        )
    return AuthorityBenchmarkMetrics(
        claim_correct=10,
        claim_total=10,
        source_attribution_correct=9,
        source_attribution_total=10,
        support_contradiction_tp=9,
        support_contradiction_fp=1,
        support_contradiction_fn=1,
        conflation_detected=8,
        conflation_total=10,
        substitution_detected=8,
        substitution_total=10,
        tamper_leakage_detected=8,
        tamper_leakage_total=10,
        false_promotions=1,
        promotion_opportunities=10,
        correct_cannot_check=8,
        cannot_check_opportunities=10,
        false_negative_count=0,
        clean_positive_total=3,
        resource_units=10.0,
        latency_seconds=2.5,
    )


def _observation(system_id: str, metrics, *, self_verified=False, subject=None):
    producer = _digest(f"producer:{system_id}")
    verifier = producer if self_verified else _digest(f"verifier:{system_id}")
    return AuthoritySystemObservation(
        system_id=system_id,
        metrics=metrics,
        evidence_artifact_id=f"artifact:{system_id}",
        evidence_artifact_hash=_digest(f"artifact:{system_id}"),
        subject_revision_hash=subject or _digest("subject"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        split_id="split:heldout",
        producer_process_lineage_hash=producer,
        verifier_process_lineage_hash=verifier,
        evaluator_frozen_before_candidate=True,
        fresh_split=True,
    )


def _panel(*, orion_metrics=None, baseline_metrics=None):
    baseline_metrics = baseline_metrics or _metrics(strong=False)
    return AuthorityBenchmarkPanel(
        panel_id="authority:external:v1",
        subject_revision_hash=_digest("subject"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        resource_budget_units=12.0,
        orion=_observation("orion", orion_metrics or _metrics(strong=True)),
        baselines=tuple(
            _observation(system_id, baseline_metrics)
            for system_id in FROZEN_AUTHORITY_BASELINE_IDS
        ),
    )


def test_external_authority_gate_requires_noncompensatory_safety_dominance_over_every_baseline():
    panel = _panel()
    report = assess_authority_benchmark(panel)

    assert report.status is AuthorityBenchmarkStatus.PASS
    assert report.passed
    assert len(report.baseline_comparisons) == len(FROZEN_AUTHORITY_BASELINE_IDS)
    assert all(passed for _, passed in report.baseline_comparisons)
    assert len(report.panel_artifact_hash) == 64


def test_equal_safety_is_not_a_strict_improvement():
    same = _metrics(strong=True)
    report = assess_authority_benchmark(_panel(orion_metrics=same, baseline_metrics=same))
    assert report.status is AuthorityBenchmarkStatus.FAIL
    assert len(report.blockers) == len(FROZEN_AUTHORITY_BASELINE_IDS)


def test_higher_claim_accuracy_cannot_compensate_for_worse_false_promotion():
    unsafe = AuthorityBenchmarkMetrics(
        claim_correct=10,
        claim_total=10,
        source_attribution_correct=10,
        source_attribution_total=10,
        support_contradiction_tp=10,
        support_contradiction_fp=0,
        support_contradiction_fn=0,
        conflation_detected=10,
        conflation_total=10,
        substitution_detected=10,
        substitution_total=10,
        tamper_leakage_detected=10,
        tamper_leakage_total=10,
        false_promotions=2,
        promotion_opportunities=10,
        correct_cannot_check=10,
        cannot_check_opportunities=10,
        false_negative_count=0,
        clean_positive_total=3,
        resource_units=10.0,
        latency_seconds=3.0,
    )
    report = assess_authority_benchmark(_panel(orion_metrics=unsafe))
    assert report.status is AuthorityBenchmarkStatus.FAIL


def test_missing_metrics_or_self_verification_is_cannot_check_not_fail():
    incomplete = _panel(orion_metrics=_metrics(strong=True, complete=False))
    report = assess_authority_benchmark(incomplete)
    assert report.status is AuthorityBenchmarkStatus.CANNOT_CHECK
    assert "orion:metrics_incomplete" in report.blockers

    panel = _panel()
    self_verified = AuthorityBenchmarkPanel(
        panel.panel_id,
        panel.subject_revision_hash,
        panel.evaluator_artifact_hash,
        panel.evaluation_epoch_id,
        panel.resource_budget_units,
        _observation("orion", _metrics(strong=True), self_verified=True),
        panel.baselines,
    )
    report = assess_authority_benchmark(self_verified)
    assert report.status is AuthorityBenchmarkStatus.CANNOT_CHECK
    assert "orion:self_verified" in report.blockers


def test_baseline_panel_is_frozen_and_ordered():
    with pytest.raises(ValueError, match="frozen nearest-work panel"):
        AuthorityBenchmarkPanel(
            "bad",
            _digest("subject"),
            _digest("evaluator"),
            "epoch:frozen",
            12.0,
            _observation("orion", _metrics(strong=True)),
            tuple(
                _observation(system_id, _metrics(strong=False))
                for system_id in reversed(FROZEN_AUTHORITY_BASELINE_IDS)
            ),
        )
