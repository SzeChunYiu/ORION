from __future__ import annotations

from orion.mechanics.receipt import MechanicReceipt, MechanicRunStatus

from .model import EpisodeOutcome, TaskEpisode

_OUTCOME_MAP = {
    MechanicRunStatus.SUCCEEDED: EpisodeOutcome.SUCCESS,
    MechanicRunStatus.PARTIAL: EpisodeOutcome.PARTIAL_SUCCESS,
    MechanicRunStatus.FAILED: EpisodeOutcome.FAILURE,
    MechanicRunStatus.BLOCKED: EpisodeOutcome.BLOCKED,
    MechanicRunStatus.CANNOT_CHECK: EpisodeOutcome.CANNOT_CHECK,
}


def episode_from_receipt(
    receipt: MechanicReceipt,
    *,
    episode_id: str,
    task_id: str,
    run_id: str,
    parent_run_id: str | None,
    evaluation_epoch_id: str,
    split_id: str,
    problem_signature: tuple[str, ...],
    variation_signature: tuple[str, ...],
    pre_state_hash: str,
    post_state_hash: str,
    timestamp: str,
    producer_process_lineage_hash: str | None = None,
    evaluator_artifact_hash: str | None = None,
) -> TaskEpisode:
    """Project an execution receipt into immutable experience without adding authority."""

    observations = tuple(
        dict.fromkeys(
            receipt.output_artifact_ids
            + tuple(f"metric:{item.metric_id}" for item in receipt.metric_observations)
        )
    )
    return TaskEpisode(
        episode_id=episode_id,
        task_id=task_id,
        run_id=run_id,
        parent_run_id=parent_run_id,
        evaluation_epoch_id=evaluation_epoch_id,
        split_id=split_id,
        mechanic_id=receipt.mechanic_id,
        problem_signature=problem_signature,
        variation_signature=variation_signature,
        pre_state_hash=pre_state_hash,
        action_ids=receipt.action_ids,
        observation_ids=observations,
        outcome=_OUTCOME_MAP[receipt.status],
        failure_signature=receipt.failure_signature,
        residual_ids=receipt.residual_ids,
        evidence_ids=receipt.evidence_ids,
        evidence_bindings=receipt.evidence_bindings,
        post_state_hash=post_state_hash,
        timestamp=timestamp,
        producer_process_lineage_hash=producer_process_lineage_hash,
        evaluator_artifact_hash=evaluator_artifact_hash,
        source_receipt_id=receipt.receipt_id,
        output_artifact_ids=receipt.output_artifact_ids,
        handoff_values=receipt.handoff_values,
        metric_observations=receipt.metric_observations,
        provenance_ids=receipt.provenance_ids,
        cost_units=receipt.cost_units,
        latency_seconds=receipt.latency_seconds,
    )
