from orion.experience import EpisodeOutcome, episode_from_receipt
from orion.mechanics import MechanicReceipt, MechanicRunStatus, MetricDirection, MetricKind, MetricObservation


def test_mechanic_receipt_becomes_an_immutable_learning_episode():
    receipt = MechanicReceipt(
        "receipt:1",
        "SEARCH.v1",
        MechanicRunStatus.FAILED,
        metric_observations=(MetricObservation("recall-proxy", 0.0, "fraction", evidence_ids=("e:metric",)),),
        residual_ids=("residual:coverage",),
        failure_signature=("missed_parent_domain",),
        evidence_ids=("e:search",),
        cost_units=3.0,
    )
    episode = episode_from_receipt(
        receipt,
        episode_id="episode:1",
        task_id="task:1",
        problem_signature=("research", "search"),
        variation_signature=("lexical-route",),
        pre_state_hash="pre",
        post_state_hash="post",
        action_ids=("execute-search",),
        timestamp="2026-08-15T20:00:00+02:00",
    )
    assert episode.outcome is EpisodeOutcome.FAILURE
    assert episode.failure_signature == ("missed_parent_domain",)
    assert "metric:recall-proxy" in episode.observation_ids
    assert episode.cost_units == 3.0
