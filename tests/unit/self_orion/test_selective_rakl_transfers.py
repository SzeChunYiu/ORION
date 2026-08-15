from types import SimpleNamespace

from orion.experience.model import EpisodeOutcome, TaskEpisode
from orion.self_orion.change_control import ChangeControlVerdict
from orion.self_orion.development_driver import DevelopmentKnowledgeClass, EmpiricalWorkItem
from orion.self_orion.evolution_archive import (
    OrionVariant,
    VariantStatus,
    initialize_evolution_archive,
    record_change_control_result,
    recommend_host_promotion,
    register_challenger,
)
from orion.self_orion.experience_policy import rank_empirical_work_with_experience
from orion.self_orion.novelty import (
    DevelopmentNoveltyClass,
    DevelopmentNoveltyEvidence,
    classify_development_novelty,
)
from orion.self_orion.saturation_vector import (
    DevelopmentNoveltyRound,
    DevelopmentSaturationAxis,
    assess_development_saturation,
)


def _episode(episode_id: str, mechanic_id: str, outcome: EpisodeOutcome, *, cost=1.0):
    residuals = () if outcome is EpisodeOutcome.SUCCESS else ("residual:failure",)
    return TaskEpisode(
        episode_id=episode_id,
        task_id=f"task:{episode_id}",
        run_id=f"run:{episode_id}",
        parent_run_id=None,
        evaluation_epoch_id="epoch:test",
        split_id="split:test",
        mechanic_id=mechanic_id,
        problem_signature=("test problem",),
        variation_signature=(episode_id,),
        pre_state_hash="pre",
        action_ids=("act",),
        observation_ids=("obs",),
        outcome=outcome,
        failure_signature=() if outcome is EpisodeOutcome.SUCCESS else ("failure",),
        residual_ids=residuals,
        evidence_ids=(),
        evidence_bindings=(),
        post_state_hash="post",
        timestamp="2026-08-15T00:00:00+00:00",
        cost_units=cost,
    )


def test_saturation_vector_requires_independent_flatness_on_every_axis_and_resource_bound_never_closes():
    zero = tuple((axis, 0) for axis in DevelopmentSaturationAxis)
    rounds = (
        DevelopmentNoveltyRound("r1", "function-only", True, zero),
        DevelopmentNoveltyRound("r2", "parent-discipline", True, zero),
    )
    report = assess_development_saturation(rounds)
    assert report.bounded_saturated
    assert not report.grants_absolute_completeness
    assert not report.grants_self_promotion

    reopened = assess_development_saturation(
        rounds + (
            DevelopmentNoveltyRound(
                "r3",
                "adversarial",
                True,
                zero,
                residual_axes=(DevelopmentSaturationAxis.OPERATOR,),
                residual_signature=("missing-operator",),
            ),
        )
    )
    assert not reopened.bounded_saturated
    assert "OPERATOR:reopened_by_native_residual" in reopened.reasons

    resource_bound = assess_development_saturation(
        rounds + (DevelopmentNoveltyRound("r4", "freshness", True, zero, resource_bound=True),)
    )
    assert not resource_bound.bounded_saturated
    assert resource_bound.cannot_check_resource_bound


def test_novelty_classifier_separates_transfer_from_new_operator_and_refuses_unverified_classification():
    transfer = classify_development_novelty(
        DevelopmentNoveltyEvidence(
            "subject:transfer",
            True,
            ("e:1",),
            used_operator_ids=("op:old",),
            preexisting_operator_ids=("op:old",),
            transfer_witness_ids=("w:1",),
            all_required_resources_preexisting=True,
        )
    )
    assert transfer.novelty_class is DevelopmentNoveltyClass.TRANSFER_NOVEL
    assert not transfer.requires_new_problem_solving_structure

    invented = classify_development_novelty(
        DevelopmentNoveltyEvidence(
            "subject:operator",
            True,
            ("e:2",),
            used_operator_ids=("op:old", "op:new"),
            preexisting_operator_ids=("op:old",),
            new_operator_ids=("op:new",),
        )
    )
    assert invented.novelty_class is DevelopmentNoveltyClass.OPERATOR_NOVEL
    assert invented.requires_new_operator

    unresolved = classify_development_novelty(DevelopmentNoveltyEvidence("subject:unverified", False, ()))
    assert unresolved.novelty_class is DevelopmentNoveltyClass.UNRESOLVED


def test_experience_changes_work_priority_only_and_failure_prone_mechanic_moves_up():
    work = (
        EmpiricalWorkItem("w:stable", "SEARCH.SOURCE.v0", "fresh benchmark", DevelopmentKnowledgeClass.LIVE_EVIDENCE, 8, "test"),
        EmpiricalWorkItem("w:failing", "SEARCH.QUERY.v0", "fresh benchmark", DevelopmentKnowledgeClass.LIVE_EVIDENCE, 8, "test"),
    )
    episodes = (
        _episode("s1", "SEARCH.SOURCE.v0", EpisodeOutcome.SUCCESS),
        _episode("s2", "SEARCH.SOURCE.v0", EpisodeOutcome.SUCCESS),
        _episode("f1", "SEARCH.QUERY.v0", EpisodeOutcome.FAILURE),
        _episode("f2", "SEARCH.QUERY.v0", EpisodeOutcome.BLOCKED),
    )
    ranked = rank_empirical_work_with_experience(work, episodes)
    assert ranked[0].work.mechanic_id == "SEARCH.QUERY.v0"
    assert all("experience_changes_scheduling_priority_only" in item.reasons for item in ranked)


def test_evolution_archive_preserves_challenger_history_and_cannot_self_promote():
    incumbent = OrionVariant("v0", "a" * 64, (), ("base",), (("cost", 1.0),), (), VariantStatus.INCUMBENT)
    archive = initialize_evolution_archive(incumbent)
    challenger = OrionVariant("v1", "b" * 64, ("v0",), ("query",), (("cost", 1.0),), ("episode:1",), VariantStatus.CHALLENGER)
    archive = register_challenger(archive, challenger)
    result = SimpleNamespace(
        verdict=ChangeControlVerdict.RECOMMEND_HOST_PROMOTION,
        execution=SimpleNamespace(candidate_revision_hash="b" * 64),
        proposal=SimpleNamespace(proposal_id="proposal:1"),
        assurance=SimpleNamespace(development_delta=1.0, fresh_assurance_delta=0.5),
        reasons=(),
    )
    archive = record_change_control_result(
        archive,
        trial_id="trial:1",
        parent_variant_id="v0",
        child_variant_id="v1",
        result=result,
    )
    assured = next(item for item in archive.variants if item.variant_id == "v1")
    assert assured.status is VariantStatus.ASSURED
    assert archive.incumbent_id == "v0"
    recommendation = recommend_host_promotion(archive, "v1")
    assert recommendation.supporting_trial_ids == ("trial:1",)
    assert not recommendation.authorizes_promotion
