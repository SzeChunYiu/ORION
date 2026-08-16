import pytest

from orion.self_orion.phase2_preflight import (
    AUTHORITY_ATTACK_IDS,
    DEEP_TARGET_TASK,
    Phase2ClosurePreflight,
    Phase2PreflightStatus,
    WIDE_LITERATURE_TASK,
    assess_phase2_preflight,
    build_frozen_live_trial_packet,
)


def _preflight(**overrides):
    values = dict(
        protocol_id="phase2-shadow-closure-v1",
        subject_revision_hash="0" * 64,
        provider_manifest_hash="0" * 64,
        evaluator_artifact_hash="0" * 64,
        evaluation_epoch_id="phase2:epoch:frozen-before-outcomes",
        baseline_id="simple-llm-retrieval-baseline-v1",
        resource_budget_units=100.0,
    )
    values.update(overrides)
    return Phase2ClosurePreflight(**values)


def test_repository_preflight_is_frozen_but_not_runnable_before_phase1_closes():
    report = assess_phase2_preflight(_preflight())
    assert report.status is Phase2PreflightStatus.BIND_FINAL_PHASE1_SUBJECT
    assert report.frozen_task_ids == (WIDE_LITERATURE_TASK.task_id, DEEP_TARGET_TASK.task_id)
    assert len(report.attack_ids) == 10
    assert not report.grants_phase2_closure
    assert not report.grants_governed_self_orion


def test_binding_order_requires_subject_then_provider_then_evaluator():
    subject = "a" * 64
    provider = "b" * 64
    evaluator = "c" * 64
    assert assess_phase2_preflight(_preflight(subject_revision_hash=subject)).status is Phase2PreflightStatus.BIND_EXTERNAL_PROVIDER
    assert assess_phase2_preflight(_preflight(subject_revision_hash=subject, provider_manifest_hash=provider)).status is Phase2PreflightStatus.BIND_PROTECTED_EVALUATOR
    assert assess_phase2_preflight(_preflight(subject_revision_hash=subject, provider_manifest_hash=provider, evaluator_artifact_hash=evaluator)).status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL


def test_only_fully_bound_preflight_can_build_live_packet():
    with pytest.raises(RuntimeError):
        build_frozen_live_trial_packet(_preflight())
    packet = build_frozen_live_trial_packet(
        _preflight(
            subject_revision_hash="a" * 64,
            provider_manifest_hash="b" * 64,
            evaluator_artifact_hash="c" * 64,
        )
    )
    assert packet.packet_id == "phase2-shadow-closure-v1"
    assert len(packet.tasks) == 2
    assert {task.kind.value for task in packet.tasks} == {"WIDE_LITERATURE", "DEEP_TARGET"}
    assert not packet.fingerprint.startswith("0" * 64)


def test_task_prompts_and_success_criteria_are_nonempty_and_scoped():
    for task in (WIDE_LITERATURE_TASK, DEEP_TARGET_TASK):
        assert task.question.strip()
        assert task.scope.strip()
        assert task.success_criteria
        assert task.variation_signature
        assert "heldout" in task.split_id


def test_authority_attack_battery_is_exactly_ten_unique_frozen_attacks():
    assert len(AUTHORITY_ATTACK_IDS) == 10
    assert len(set(AUTHORITY_ATTACK_IDS)) == 10
    assert any("WRONG-SOURCE" in attack for attack in AUTHORITY_ATTACK_IDS)
    assert any("SUBSTITUTED-CONTENT" in attack for attack in AUTHORITY_ATTACK_IDS)
    assert any("SAME-LANE" in attack for attack in AUTHORITY_ATTACK_IDS)
    assert any("CONTAMINATION" in attack for attack in AUTHORITY_ATTACK_IDS)
    assert any("HELDOUT" in attack for attack in AUTHORITY_ATTACK_IDS)
    assert any("CANNOT-CHECK" in attack for attack in AUTHORITY_ATTACK_IDS)


def test_invalid_protocol_never_advances_to_binding_or_execution():
    report = assess_phase2_preflight(_preflight(resource_budget_units=0))
    assert report.status is Phase2PreflightStatus.INVALID
    assert "positive_resource_budget_required" in report.blockers


def test_fabricated_attack_ids_cannot_open_the_shadow_trial() -> None:
    """The gate guarding the entire live campaign used to count strings.

    Ten unique caller-supplied ids satisfied it, so
    READY_TO_EXECUTE_SHADOW_TRIAL was reachable with attack ids literally named
    "totally-made-up-0" through "-9". Counting a caller's strings certifies the
    caller, not the attacks. Identity against the frozen registry is the only
    thing that certifies the attacks.
    """

    from orion.core.problem import Problem
    from orion.self_orion.phase2_preflight import (
        AUTHORITY_ATTACK_IDS,
        FrozenTrialTask,
        Phase2ClosurePreflight,
        Phase2PreflightStatus,
        ResearchTrialKind,
        assess_phase2_preflight,
    )

    digest = "a" * 64

    def task(task_id, kind):
        return FrozenTrialTask(
            task_id=task_id,
            kind=kind,
            problem=Problem(problem_id=task_id, question="q"),
            variation_signature="v",
            split_id="s",
            required_evidence_ids=("e1",),
        )

    def preflight(attack_ids):
        return Phase2ClosurePreflight(
            protocol_id="P",
            subject_revision_hash=digest,
            provider_manifest_hash=digest,
            evaluator_artifact_hash=digest,
            evaluation_epoch_id="E",
            baseline_id="B",
            resource_budget_units=10,
            tasks=(
                task("t1", ResearchTrialKind.WIDE_LITERATURE),
                task("t2", ResearchTrialKind.DEEP_TARGET),
            ),
            authority_attack_ids=attack_ids,
        )

    fabricated = assess_phase2_preflight(
        preflight(tuple(f"totally-made-up-{index}" for index in range(10)))
    )
    assert fabricated.status is Phase2PreflightStatus.INVALID
    assert any("unknown_authority_attack_ids" in item for item in fabricated.blockers)

    # A missing frozen attack is named, not merely counted.
    incomplete = assess_phase2_preflight(preflight(tuple(AUTHORITY_ATTACK_IDS)[:9]))
    assert incomplete.status is Phase2PreflightStatus.INVALID
    assert any("frozen_authority_attacks_not_declared" in item for item in incomplete.blockers)

    # And the real ten still open the trial, so this is not refusal-by-default.
    genuine = assess_phase2_preflight(preflight(tuple(AUTHORITY_ATTACK_IDS)))
    assert genuine.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
