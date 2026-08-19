from __future__ import annotations

import copy
import inspect
import json
from dataclasses import replace
from pathlib import Path

from orion.discovery import zero_error_jump_independent
from orion.discovery.zero_error_jump_benchmark import (
    JumpArm,
    RepresentationMove,
    ZeroErrorJumpTerminal,
    build_zero_error_jump_benchmark_report,
    generate_jump_worlds,
    prove_old_regime,
    propose,
    public_projection,
    select_registered_probe,
)
from orion.discovery.zero_error_jump_independent import (
    independently_verify_zero_error_jump,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = (
    ROOT
    / "research"
    / "extensions"
    / "orion-jump-recursive-atoms"
    / "zero_error_jump"
)
PROTOCOL = RESEARCH / "ZERO_ERROR_JUMP_PROTOCOL_V2.json"
EXPECTED = RESEARCH / "ZERO_ERROR_JUMP_EXPECTED_V2.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report(
    protocol: dict[str, object] | None = None,
    expected: dict[str, object] | None = None,
):
    return build_zero_error_jump_benchmark_report(
        protocol=protocol or _load(PROTOCOL),
        expected=expected or _load(EXPECTED),
    )


def test_zero_error_jump_v2_matches_pre_frozen_primary_replication_and_terminal() -> None:
    expected = _load(EXPECTED)
    report = _report()

    assert report.primary.case_count == 42
    assert report.primary.positive_count == 24
    assert report.primary.control_count == 18
    assert report.replication.case_count == 42
    assert report.replication.positive_count == 24
    assert report.replication.control_count == 18

    for split in (report.primary, report.replication):
        for arm_name, expected_metric in expected["per_split_arm_metrics"].items():
            assert split.metric(JumpArm(arm_name)).metric_payload() == expected_metric

    assert report.verified_parent_equals_orion_decisions_primary is True
    assert report.verified_parent_equals_orion_decisions_replication is True
    assert report.verified_parent_equals_orion_metrics_primary is True
    assert report.verified_parent_equals_orion_metrics_replication is True
    assert report.orion_strong_parent_incremental_gap_primary == 0
    assert report.orion_strong_parent_incremental_gap_replication == 0
    assert report.primary_replication_terminal_equal is True
    assert report.terminal.value == expected["candidate_terminal"]
    assert report.terminal is ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE
    assert report.all_checks_passed is True
    assert report.grants_scientific_adoption is False
    assert report.grants_open_ended_creativity is False
    assert report.grants_novelty_authority is False
    assert report.grants_issue_closure_authority is False


def test_v2_public_projection_has_no_pre_experiment_class_label_or_cardinality_side_channel() -> None:
    protocol = _load(PROTOCOL)
    signatures = set()
    for split_id in ("primary", "replication"):
        for world in generate_jump_worlds(
            seed=protocol["seeds"][split_id], split_id=split_id
        ):
            public = public_projection(world)
            public.verify()
            assert not hasattr(public, "family_id")
            assert not hasattr(public, "is_jump_case")
            assert not hasattr(public, "public_tension_kind")
            assert not hasattr(public, "gold_representation_move")
            assert not hasattr(public, "protected_full_contract_signature")
            assert not hasattr(public, "protected_novel_consequence_token")
            assert not hasattr(public, "gold_old_solution_id")
            assert "-p" not in public.case_id.lower()
            assert "-c" not in public.case_id.lower()
            assert len(public.opaque_object_ids) == 3
            assert len(public.opaque_relation_ids) == 2
            assert len(public.public_observations) == 4
            assert len(public.old_language_public_signatures) == 8
            assert len(public.open_discriminator_ids) == 2
            assert len(public.thought_experiment_menu) == 2
            assert len(public.correspondence_obligation_ids) == 2
            assert len(public.public_validation_interface_ids) == 2
            assert {row.operation_kind for row in public.thought_experiment_menu} == {
                "REGISTERED_PROBE"
            }
            assert {row.cost for row in public.thought_experiment_menu} == {1}
            overlaps = sorted(
                len(
                    set(row.covered_discriminator_ids)
                    & set(public.open_discriminator_ids)
                )
                for row in public.thought_experiment_menu
            )
            assert overlaps == [0, 2]
            signatures.add(
                (
                    len(public.opaque_object_ids),
                    len(public.opaque_relation_ids),
                    len(public.public_observations),
                    len(public.old_language_public_signatures),
                    len(public.open_discriminator_ids),
                    len(public.thought_experiment_menu),
                    tuple(row.operation_kind for row in public.thought_experiment_menu),
                    tuple(row.cost for row in public.thought_experiment_menu),
                    len(public.correspondence_obligation_ids),
                    len(public.public_validation_interface_ids),
                )
            )
    assert len(signatures) == 1


def test_primary_and_replication_are_disjoint_and_incumbent_public_error_is_zero() -> None:
    protocol = _load(PROTOCOL)
    primary = generate_jump_worlds(seed=protocol["seeds"]["primary"], split_id="primary")
    replication = generate_jump_worlds(
        seed=protocol["seeds"]["replication"], split_id="replication"
    )

    assert {world.case_id for world in primary}.isdisjoint(
        {world.case_id for world in replication}
    )
    assert {world.opaque_object_ids for world in primary}.isdisjoint(
        {world.opaque_object_ids for world in replication}
    )
    for world in (*primary, *replication):
        assert world.public_observations == world.incumbent_public_predictions


def test_v2_registered_probe_selection_uses_only_opaque_public_overlap() -> None:
    protocol = _load(PROTOCOL)
    for world in generate_jump_worlds(
        seed=protocol["seeds"]["primary"], split_id="primary"
    ):
        public = public_projection(world)
        selected = select_registered_probe(public)
        assert selected == world.informative_experiment_id
        option = next(
            row for row in public.thought_experiment_menu if row.experiment_id == selected
        )
        assert set(option.covered_discriminator_ids) == set(public.open_discriminator_ids)


def test_old_language_impossibility_is_exact_and_public_candidate_count_is_balanced() -> None:
    protocol = _load(PROTOCOL)
    for split_id in ("primary", "replication"):
        worlds = generate_jump_worlds(seed=protocol["seeds"][split_id], split_id=split_id)
        for world in worlds:
            proof = prove_old_regime(world)
            proof.verify()
            assert proof.old_candidate_count == 8
            assert proof.matching_public_count == 8
            if world.is_jump_case:
                assert proof.old_regime_insufficient is True
                assert proof.full_contract_solution_ids == ()
                assert world.gold_old_solution_id is None
            else:
                assert proof.old_regime_insufficient is False
                assert len(proof.full_contract_solution_ids) >= 1
                assert world.gold_old_solution_id in proof.full_contract_solution_ids


def test_search_hard_control_places_solution_last_but_remains_no_jump() -> None:
    protocol = _load(PROTOCOL)
    hard = next(
        world
        for world in generate_jump_worlds(
            seed=protocol["seeds"]["primary"], split_id="primary"
        )
        if world.family_id == "SEARCH_HARD_BUT_EXPRESSIBLE"
    )
    assert hard.old_language_hypotheses[-1].hypothesis_id == hard.gold_old_solution_id
    assert prove_old_regime(hard).old_regime_insufficient is False
    for arm in (
        JumpArm.OLD_DSL_EXHAUSTIVE,
        JumpArm.VERIFIED_REGIME_REVISION_PARENT,
        JumpArm.ORION_JUMP,
    ):
        proposal = propose(hard, arm)
        assert proposal.selected_experiment_id == hard.informative_experiment_id
        assert proposal.jump_requested is False
        assert proposal.representation_move is RepresentationMove.NO_REPRESENTATION_CHANGE
        assert proposal.old_regime_action_id == "KEEP_OLD_REGIME"


def test_fixed_representation_arms_use_probe_evidence_not_hidden_class_state() -> None:
    protocol = _load(PROTOCOL)
    positive = next(
        world
        for world in generate_jump_worlds(
            seed=protocol["seeds"]["primary"], split_id="primary"
        )
        if world.is_jump_case
    )
    control = next(
        world
        for world in generate_jump_worlds(
            seed=protocol["seeds"]["primary"], split_id="primary"
        )
        if not world.is_jump_case
    )
    for arm in (
        JumpArm.OLD_DSL_EXHAUSTIVE,
        JumpArm.M_OPEN_SAME_REPRESENTATION,
        JumpArm.FIXED_REP_WORLD_MODEL,
    ):
        pos = propose(positive, arm)
        neg = propose(control, arm)
        assert pos.selected_experiment_id == positive.informative_experiment_id
        assert pos.experiment_outcome == positive.informative_outcome
        assert pos.jump_requested is False
        assert pos.old_regime_action_id == "UNRESOLVED_REPRESENTATION_CEILING"
        assert pos.recognizes_old_regime_insufficiency is True
        assert neg.selected_experiment_id == control.informative_experiment_id
        assert neg.experiment_outcome == control.informative_outcome
        assert neg.jump_requested is False
        assert neg.old_regime_action_id == "KEEP_OLD_REGIME"
        assert neg.recognizes_old_regime_insufficiency is False


def test_strong_parent_and_orion_have_identical_decisions_and_metrics_on_both_splits() -> None:
    report = _report()
    for split in (report.primary, report.replication):
        parent = split.metric(JumpArm.VERIFIED_REGIME_REVISION_PARENT)
        orion = split.metric(JumpArm.ORION_JUMP)
        assert parent.decision_keys == orion.decision_keys
        assert parent.metric_payload() == orion.metric_payload()
        assert parent.positive_jump_success == 24
        assert parent.control_no_jump_correct == 18
        assert parent.false_jump_on_control == 0


def test_fixed_representation_arms_cannot_cross_representation_ceiling_even_after_probe() -> None:
    report = _report()
    for split in (report.primary, report.replication):
        for arm in (
            JumpArm.OLD_DSL_EXHAUSTIVE,
            JumpArm.M_OPEN_SAME_REPRESENTATION,
            JumpArm.FIXED_REP_WORLD_MODEL,
        ):
            metric = split.metric(arm)
            assert metric.positive_jump_success == 0
            assert metric.old_regime_insufficiency_correct == 24
            assert metric.thought_experiment_success == 24
            assert metric.control_no_jump_correct == 18
            assert metric.false_jump_on_control == 0


def test_correspondence_is_noncompensatory_and_overjump_controls_are_retained() -> None:
    report = _report()
    for split in (report.primary, report.replication):
        no_corr = split.metric(JumpArm.ORION_NO_CORRESPONDENCE)
        assert no_corr.thought_experiment_success == 24
        assert no_corr.protected_consequence_success == 24
        assert no_corr.correspondence_success == 0
        assert no_corr.positive_jump_success == 0
        assert no_corr.unresolved_or_rejected == 24

        overjump = split.metric(JumpArm.OVERJUMP_ALWAYS)
        assert overjump.false_jump_on_control == 18
        assert overjump.positive_jump_success == 4
        assert overjump.unresolved_or_rejected == 20


def test_load_bearing_probe_outcome_changes_parent_and_orion_proposal() -> None:
    protocol = _load(PROTOCOL)
    world = next(
        world
        for world in generate_jump_worlds(
            seed=protocol["seeds"]["primary"], split_id="primary"
        )
        if world.gold_representation_move is RepresentationMove.FRAME_COORDINATE
    )
    tampered = replace(world, informative_outcome="pattern:E0:tampered")

    for arm in (JumpArm.VERIFIED_REGIME_REVISION_PARENT, JumpArm.ORION_JUMP):
        original = propose(world, arm)
        changed = propose(tampered, arm)
        assert original.representation_move is RepresentationMove.FRAME_COORDINATE
        assert changed.representation_move is RepresentationMove.BRIDGE_CORRESPONDENCE
        assert changed.protected_consequence_prediction != world.protected_novel_consequence_token


def test_control_candidate_visible_outcome_does_not_embed_control_family_identity() -> None:
    protocol = _load(PROTOCOL)
    for world in generate_jump_worlds(
        seed=protocol["seeds"]["primary"], split_id="primary"
    ):
        if world.is_jump_case:
            continue
        assert world.informative_outcome.startswith("pattern:OLD_SUFFICIENT:")
        assert world.family_id not in world.informative_outcome


def test_structural_performance_is_seed_invariant_but_identifiers_change() -> None:
    protocol = _load(PROTOCOL)
    primary = generate_jump_worlds(seed=protocol["seeds"]["primary"], split_id="primary")
    replication = generate_jump_worlds(
        seed=protocol["seeds"]["replication"], split_id="replication"
    )
    assert primary[0].case_id != replication[0].case_id
    assert primary[0].opaque_object_ids != replication[0].opaque_object_ids
    assert primary[0].protected_novel_consequence_token != replication[0].protected_novel_consequence_token
    report = _report()
    for arm in JumpArm:
        assert report.primary.metric(arm).metric_payload() == report.replication.metric(arm).metric_payload()


def test_outcome_access_or_expected_metric_tampering_fails_closed() -> None:
    protocol = _load(PROTOCOL)
    accessed = copy.deepcopy(protocol)
    accessed["outcome_accessed"] = True
    try:
        _report(protocol=accessed)
    except ValueError as exc:
        assert "outcome access" in str(exc)
    else:
        raise AssertionError("outcome-accessed V2 protocol should reject")

    expected = _load(EXPECTED)
    tampered = copy.deepcopy(expected)
    tampered["per_split_arm_metrics"]["ORION_JUMP"]["positive_jump_success"] = 23
    report = _report(expected=tampered)
    assert report.terminal is ZeroErrorJumpTerminal.CANNOT_CHECK
    assert report.all_checks_passed is False


def test_independent_reconstruction_matches_v2_without_main_score_split() -> None:
    protocol = _load(PROTOCOL)
    expected = _load(EXPECTED)
    independent = independently_verify_zero_error_jump(protocol=protocol, expected=expected)
    main = _report()

    assert independent.expected_match is True
    assert independent.terminal is ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE
    assert independent.parent_orion_decisions_equal_primary is True
    assert independent.parent_orion_decisions_equal_replication is True
    assert independent.parent_orion_metrics_equal_primary is True
    assert independent.parent_orion_metrics_equal_replication is True
    for split_name in ("primary", "replication"):
        independent_split = getattr(independent, split_name)
        main_split = getattr(main, split_name)
        for arm in JumpArm:
            assert independent_split.metric(arm).payload() == main_split.metric(arm).metric_payload()

    source = inspect.getsource(zero_error_jump_independent)
    assert "score_split(" not in source
    assert "build_zero_error_jump_benchmark_report(" not in source
