from orion.experience import EpisodeOutcome, episode_from_receipt
from orion.mechanics import (
    MechanicReceipt,
    MechanicRunStatus,
    MetricObservation,
)


def test_mechanic_receipt_becomes_an_immutable_learning_episode():
    receipt = MechanicReceipt(
        "receipt:1",
        "SEARCH.v1",
        MechanicRunStatus.FAILED,
        action_ids=("execute-search",),
        output_artifact_ids=("artifact:query-log",),
        handoff_values=(("coverage-status", "OPEN"),),
        metric_observations=(
            MetricObservation(
                "recall-proxy", 0.0, "fraction", evidence_ids=("e:metric",)
            ),
        ),
        residual_ids=("residual:coverage",),
        failure_signature=("missed_parent_domain",),
        evidence_ids=("e:search",),
        evidence_bindings=(("e:search", "a" * 64),),
        provenance_ids=("source:retriever-v1",),
        cost_units=3.0,
        latency_seconds=0.25,
    )
    episode = episode_from_receipt(
        receipt,
        episode_id="episode:1",
        task_id="task:1",
        run_id="run:1",
        parent_run_id="run:root",
        evaluation_epoch_id="evaluation:fixture",
        split_id="split:fixture",
        problem_signature=("research", "search"),
        variation_signature=("lexical-route",),
        pre_state_hash="pre",
        post_state_hash="post",
        timestamp="2026-08-15T20:00:00+02:00",
    )
    assert episode.outcome is EpisodeOutcome.FAILURE
    assert episode.failure_signature == ("missed_parent_domain",)
    assert "metric:recall-proxy" in episode.observation_ids
    assert episode.cost_units == 3.0
    assert episode.latency_seconds == 0.25
    assert episode.source_receipt_id == receipt.receipt_id
    assert episode.action_ids == receipt.action_ids
    assert episode.output_artifact_ids == receipt.output_artifact_ids
    assert episode.handoff_values == receipt.handoff_values
    assert episode.metric_observations == receipt.metric_observations
    assert episode.provenance_ids == receipt.provenance_ids
    assert episode.evidence_bindings == receipt.evidence_bindings
