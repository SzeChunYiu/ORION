import pytest

import dataclasses

from orion.self_orion.phase2_preflight import (
    AUTHORITY_ATTACK_IDS,
    DEEP_TARGET_TASK,
    FrozenPacketBinding,
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


def _binding(**overrides):
    """A frozen expectation consistent with `_bound()` below."""
    values = dict(
        packet_fingerprint="f" * 64,
        subject_revision_hash="a" * 64,
        provider_manifest_hash="b" * 64,
        evaluator_artifact_hash="c" * 64,
        evaluation_epoch_id="phase2:epoch:frozen-before-outcomes",
        baseline_id="simple-llm-retrieval-baseline-v1",
        resource_budget_units=100.0,
        task_ids=(WIDE_LITERATURE_TASK.task_id, DEEP_TARGET_TASK.task_id),
    )
    values.update(overrides)
    return FrozenPacketBinding(**values)


def _bound(**overrides):
    """A preflight whose declared identities match `_binding()` exactly."""
    values = dict(
        subject_revision_hash="a" * 64,
        provider_manifest_hash="b" * 64,
        evaluator_artifact_hash="c" * 64,
        frozen_packet=_binding(),
    )
    values.update(overrides)
    return _preflight(**values)


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
    # This assertion previously read READY_TO_EXECUTE_SHADOW_TRIAL: three
    # arbitrary well-formed hex strings certified the entire live campaign
    # ready. Shape is now checked in this order, then identity is checked,
    # so an unbacked triple stops at the frozen-packet gate instead.
    assert assess_phase2_preflight(_preflight(subject_revision_hash=subject, provider_manifest_hash=provider, evaluator_artifact_hash=evaluator)).status is Phase2PreflightStatus.BIND_FROZEN_PACKET


def test_only_fully_bound_preflight_can_build_live_packet():
    with pytest.raises(RuntimeError):
        build_frozen_live_trial_packet(_preflight())
    with pytest.raises(RuntimeError):
        build_frozen_live_trial_packet(
            _preflight(subject_revision_hash="a" * 64, provider_manifest_hash="b" * 64, evaluator_artifact_hash="c" * 64)
        )
    packet = build_frozen_live_trial_packet(_bound())
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
            frozen_packet=FrozenPacketBinding(
                packet_fingerprint="f" * 64,
                subject_revision_hash=digest,
                provider_manifest_hash=digest,
                evaluator_artifact_hash=digest,
                evaluation_epoch_id="E",
                baseline_id="B",
                resource_budget_units=10,
                task_ids=("t1", "t2"),
            ),
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
    # (The preflight above declares a matching frozen packet, so the identity
    # gate is satisfied and only the attack registry is under test here.)
    genuine = assess_phase2_preflight(preflight(tuple(AUTHORITY_ATTACK_IDS)))
    assert genuine.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL


# ---------------------------------------------------------------------------
# Fail-closed frozen-packet identity gate.
#
# Before this gate existed, `assess_phase2_preflight` validated only the SHAPE
# of the three binding hashes -- 64 hex characters, not all zero -- and then
# returned READY_TO_EXECUTE_SHADOW_TRIAL. Every test below fabricates input the
# old gate accepted. The last one is the no-alarm case: a gate that rejects
# everything is not fixed, it is broken shut.
# ---------------------------------------------------------------------------


def test_three_arbitrary_well_formed_hashes_do_not_certify_the_live_campaign():
    report = assess_phase2_preflight(
        _preflight(
            subject_revision_hash="a" * 64,
            provider_manifest_hash="b" * 64,
            evaluator_artifact_hash="c" * 64,
        )
    )
    assert report.status is Phase2PreflightStatus.BIND_FROZEN_PACKET
    assert "frozen_packet_binding_absent" in report.blockers
    assert not report.grants_phase2_closure


def test_well_formed_but_unmatched_hashes_are_blocked():
    for field, blocker in (
        ("subject_revision_hash", "subject_revision_hash_mismatch"),
        ("provider_manifest_hash", "provider_manifest_hash_mismatch"),
        ("evaluator_artifact_hash", "evaluator_artifact_hash_mismatch"),
    ):
        report = assess_phase2_preflight(_bound(**{field: "d" * 64}))
        assert report.status is Phase2PreflightStatus.BIND_FROZEN_PACKET
        assert blocker in report.blockers


def test_substituted_provider_manifest_cannot_pass_as_the_frozen_one():
    # A provider swap necessarily changes the manifest hash, because the hash
    # covers the reasoner model and the verifier endpoint. The old gate admitted
    # any replacement silently; this one names it.
    report = assess_phase2_preflight(_bound(provider_manifest_hash="e" * 64))
    assert report.status is Phase2PreflightStatus.BIND_FROZEN_PACKET
    assert "provider_manifest_hash_mismatch" in report.blockers


def test_epoch_generated_at_run_time_is_blocked():
    report = assess_phase2_preflight(
        _bound(evaluation_epoch_id="github-actions-32003937947-attempt-1")
    )
    assert report.status is Phase2PreflightStatus.BIND_FROZEN_PACKET
    assert "evaluation_epoch_id_mismatch" in report.blockers


def test_budget_inflated_above_the_frozen_limit_is_blocked():
    # The live workflow defaults to 32 resource units; the published packet
    # freezes 24.0 for both the ORION arm and its matched baseline.
    report = assess_phase2_preflight(
        _bound(
            resource_budget_units=32.0,
            frozen_packet=_binding(resource_budget_units=24.0),
        )
    )
    assert report.status is Phase2PreflightStatus.BIND_FROZEN_PACKET
    assert "resource_budget_mismatch" in report.blockers


def test_task_id_divergence_blocks_and_names_both_registries():
    substituted = dataclasses.replace(WIDE_LITERATURE_TASK, task_id="phase2:wide:substituted")
    report = assess_phase2_preflight(_bound(tasks=(substituted, DEEP_TARGET_TASK)))
    assert report.status is Phase2PreflightStatus.CANNOT_CHECK
    divergence = [b for b in report.blockers if b.startswith("frozen_packet_registry_divergence:")]
    assert len(divergence) == 1
    # Both sides are reported. The gate must not resolve which registry is
    # canonical -- that is a governance decision, not a checker's.
    assert "phase2:wide:substituted" in divergence[0]
    assert WIDE_LITERATURE_TASK.task_id in divergence[0]


def test_task_id_order_alone_is_not_registry_divergence():
    """Membership is the identity of a registry; sequence is not.

    The published packet serializes task_bindings alphabetically. The in-source
    defaults are wide-then-deep. After the ids themselves agree, that order
    difference must not keep the gate shut.
    """

    reversed_ids = (DEEP_TARGET_TASK.task_id, WIDE_LITERATURE_TASK.task_id)
    report = assess_phase2_preflight(_bound(frozen_packet=_binding(task_ids=reversed_ids)))
    assert report.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
    assert report.blockers == ()


def test_undeclared_subject_revision_in_frozen_packet_is_cannot_check():
    """The published packet schema does not carry subject_revision_hash.

    Comparing against "" would look like a mismatch with a declared empty
    hash. Undeclared is CANNOT_CHECK: the freeze never stated a value.
    """

    report = assess_phase2_preflight(_bound(frozen_packet=_binding(subject_revision_hash="")))
    assert report.status is Phase2PreflightStatus.CANNOT_CHECK
    assert "subject_revision_hash_undeclared_in_frozen_packet" in report.blockers
    assert "subject_revision_hash_mismatch" not in report.blockers
    assert report.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL


def test_deep_task_without_declared_ground_truth_is_blocked():
    report = assess_phase2_preflight(
        _bound(frozen_packet=_binding(ground_truth_bound_task_ids=(DEEP_TARGET_TASK.task_id,)))
    )
    assert report.status is Phase2PreflightStatus.BIND_FROZEN_PACKET
    assert any(b.startswith("frozen_ground_truth_not_bound:") for b in report.blockers)


def test_declared_ground_truth_task_satisfies_the_gate():
    deep = dataclasses.replace(DEEP_TARGET_TASK, ground_truth_bound=True)
    report = assess_phase2_preflight(
        _bound(
            tasks=(WIDE_LITERATURE_TASK, deep),
            frozen_packet=_binding(ground_truth_bound_task_ids=(DEEP_TARGET_TASK.task_id,)),
        )
    )
    assert report.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL


def test_no_alarm_a_genuinely_bound_preflight_still_reaches_ready():
    """The gate must still pass correct input, or it is broken shut, not fixed."""
    report = assess_phase2_preflight(_bound())
    assert report.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
    assert report.blockers == ()
    # Reaching READY is permission to execute a trial, never closure authority.
    assert not report.grants_phase2_closure
    assert not report.grants_governed_self_orion


def test_existing_shape_gates_are_retained_and_still_ordered_first():
    # Non-weakening: the identity gate is additive. Malformed input must still
    # stop at the original subject/provider/evaluator statuses, not skip ahead.
    assert assess_phase2_preflight(_preflight()).status is Phase2PreflightStatus.BIND_FINAL_PHASE1_SUBJECT
    assert assess_phase2_preflight(
        _preflight(subject_revision_hash="a" * 64)
    ).status is Phase2PreflightStatus.BIND_EXTERNAL_PROVIDER
    assert assess_phase2_preflight(
        _preflight(subject_revision_hash="a" * 64, provider_manifest_hash="b" * 64)
    ).status is Phase2PreflightStatus.BIND_PROTECTED_EVALUATOR
    assert assess_phase2_preflight(_preflight(resource_budget_units=0)).status is Phase2PreflightStatus.INVALID


def test_published_packet_is_actually_compared_against_the_in_source_registry():
    """The freeze of record must be consulted, not merely exist on disk.

    Divergence is CANNOT_CHECK: the gate names both registries and refuses to
    pick a canonical one. Written as a strict implication on the id sets so it
    stays correct whichever way the governance decision eventually goes.
    """

    from orion.self_orion.live_packet import DEEP_TASK_ID, WIDE_TASK_ID, load_packet_document

    binding = FrozenPacketBinding.from_packet_document(load_packet_document())
    report = assess_phase2_preflight(_bound(frozen_packet=binding))
    divergent = [b for b in report.blockers if b.startswith("frozen_packet_registry_divergence:")]
    in_source = (WIDE_LITERATURE_TASK.task_id, DEEP_TARGET_TASK.task_id)
    if frozenset(binding.task_ids) != frozenset(in_source):
        assert report.status is Phase2PreflightStatus.CANNOT_CHECK
        assert len(divergent) == 1
        for task_id in (*in_source, WIDE_TASK_ID, DEEP_TASK_ID):
            assert task_id in divergent[0]
    else:
        assert not divergent
    # An undeclared subject hash must not be treated as a match against "".
    assert "subject_revision_hash_undeclared_in_frozen_packet" in report.blockers
    # Fabricated a/b/c hashes against the published packet must never certify.
    assert report.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
    assert not report.grants_phase2_closure


def test_from_packet_document_does_not_invent_a_matchable_empty_subject():
    binding = FrozenPacketBinding.from_packet_document(
        {
            "packet_fingerprint": "f" * 64,
            "provider_manifest_hash": "b" * 64,
            "evaluator_artifact_hash": "c" * 64,
            "evaluation_epoch_id": "phase2:epoch:frozen-before-outcomes",
            "matched_baseline": {"baseline_id": "simple-llm-retrieval-baseline-v1"},
            "resource_limits": {"budget_units": 100.0},
            "task_bindings": [
                {"task_id": WIDE_LITERATURE_TASK.task_id},
                {"task_id": DEEP_TARGET_TASK.task_id},
            ],
        }
    )
    assert binding.subject_revision_hash == ""
    report = assess_phase2_preflight(_bound(frozen_packet=binding))
    assert report.status is Phase2PreflightStatus.CANNOT_CHECK
    assert "subject_revision_hash_undeclared_in_frozen_packet" in report.blockers
    assert report.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
