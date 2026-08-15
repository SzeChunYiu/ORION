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
    problem_signature: tuple[str, ...],
    variation_signature: tuple[str, ...],
    pre_state_hash: str,
    post_state_hash: str,
    action_ids: tuple[str, ...],
    timestamp: str,
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
        mechanic_id=receipt.mechanic_id,
        problem_signature=problem_signature,
        variation_signature=variation_signature,
        pre_state_hash=pre_state_hash,
        action_ids=action_ids,
        observation_ids=observations,
        outcome=_OUTCOME_MAP[receipt.status],
        failure_signature=receipt.failure_signature,
        residual_ids=receipt.residual_ids,
        evidence_ids=receipt.evidence_ids,
        post_state_hash=post_state_hash,
        timestamp=timestamp,
        cost_units=receipt.cost_units,
    )
