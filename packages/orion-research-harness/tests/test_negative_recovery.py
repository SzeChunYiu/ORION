from __future__ import annotations

from orion_research_harness.negative_recovery import (
    CentroidRecoveryPolicy,
    NativeResponsibilityController,
    RecoveryAction,
    RecoveryCause,
    atomic_panel,
    composite_panel,
    evaluate_dual_recovery,
    run_recovery,
)


def test_candidate_payload_excludes_hidden_recovery_gold():
    episode = composite_panel(seed_base=123_000, per_combination=1, sizes=(2,))[0]
    payload = episode.candidate_payload()
    serialized = repr(payload)

    assert "active_causes" not in serialized
    assert "latent_after_discriminator" not in serialized
    assert "gold_action" not in serialized
    for cause in RecoveryCause:
        assert cause.value not in serialized


def test_learned_policy_trains_only_on_atomic_failures():
    policy = CentroidRecoveryPolicy.fit(
        atomic_panel(seed_base=10_000, per_cause=32)
    )
    assert policy.centroids

    composite = composite_panel(
        seed_base=20_000, per_combination=1, sizes=(2,)
    )
    try:
        CentroidRecoveryPolicy.fit(composite)
    except ValueError as exc:
        assert "atomic episodes only" in str(exc)
    else:
        raise AssertionError("composite training must be refused")


def test_nonidentifying_failure_requires_discriminator_before_repair():
    episodes = atomic_panel(seed_base=30_000, per_cause=4)
    episode = next(
        item
        for item in episodes
        if item.active_causes == (RecoveryCause.BENCHMARK_NON_IDENTIFYING,)
    )
    native = NativeResponsibilityController()

    first = native.decide(episode.diagnostics())
    assert first is RecoveryAction.RUN_DISCRIMINATING_EXPERIMENT
    after, terminal = episode.apply(first)
    assert terminal is False
    assert RecoveryCause.BENCHMARK_NON_IDENTIFYING not in after.active_causes
    assert len(after.active_causes) == 1
    assert after.active_causes[0] in {
        RecoveryCause.REPRESENTATION_LIMIT,
        RecoveryCause.MODEL_CAPACITY_LIMIT,
    }


def test_exact_sufficiency_control_blocks_unnecessary_escalation():
    training = atomic_panel(seed_base=40_000, per_cause=64)
    learned = CentroidRecoveryPolicy.fit(training)
    native = NativeResponsibilityController()
    exact = next(
        item
        for item in atomic_panel(seed_base=50_000, per_cause=1)
        if item.active_causes == (RecoveryCause.EXACT_MECHANIC_SUFFICIENT,)
    )

    learned_trace = run_recovery(exact, policy=learned, max_steps=1)
    native_trace = run_recovery(exact, policy=native, max_steps=1)
    assert learned_trace.success is True
    assert native_trace.success is True
    assert learned_trace.first_action is RecoveryAction.STOP_NEURAL_ESCALATION
    assert native_trace.first_action is RecoveryAction.STOP_NEURAL_ESCALATION


def test_recursive_policy_recovers_unseen_composite_failures():
    training = atomic_panel(seed_base=60_000, per_cause=128)
    learned = CentroidRecoveryPolicy.fit(training)
    composite = composite_panel(
        seed_base=70_000, per_combination=2, sizes=(2, 3)
    )

    recursive = [
        run_recovery(item, policy=learned, max_steps=5) for item in composite
    ]
    single = [
        run_recovery(item, policy=learned, max_steps=1) for item in composite
    ]

    assert all(item.success for item in recursive)
    assert not any(item.success for item in single)


def test_dual_result_passes_frozen_gates_without_path_order_laundering():
    result = evaluate_dual_recovery()

    assert result["terminal"] == (
        "ORION_NEGATIVE_RECOVERY_EXACT_GENERATED_WORLDS_SUPPORTED"
    )
    assert all(result["gates"].values())
    metrics = result["metrics"]
    assert metrics["learned_unseen_composite_recovery_rate"] == 1.0
    assert metrics["native_unseen_composite_recovery_rate"] == 1.0
    assert metrics["composite_both_first_actions_valid_rate"] == 1.0
    assert metrics["dual_terminal_agreement"] == 1.0
    assert metrics["exact_control_no_overescalation_rate"] == 1.0
    assert metrics["learned_single_shot_composite_recovery_rate"] == 0.0
    # Different valid repair order is deliberately not a failure.
    assert metrics["strict_composite_first_action_agreement_descriptive"] < 0.85
