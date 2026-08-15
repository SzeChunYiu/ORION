from __future__ import annotations

from .model import EpisodeOutcome, TaskEpisode

_FAILURE_OUTCOMES = {EpisodeOutcome.FAILURE, EpisodeOutcome.PARTIAL_SUCCESS, EpisodeOutcome.BLOCKED}


def signature_similarity(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    """Deterministic Jaccard similarity over typed signature coordinates."""

    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def related_failure_episodes(
    target: TaskEpisode,
    episodes: tuple[TaskEpisode, ...],
    *,
    min_similarity: float = 0.5,
) -> tuple[TaskEpisode, ...]:
    if not 0.0 <= min_similarity <= 1.0:
        raise ValueError("failure similarity threshold must be in [0,1]")
    if target.outcome not in _FAILURE_OUTCOMES:
        return ()
    rows: list[tuple[float, str, TaskEpisode]] = []
    for episode in episodes:
        if episode.episode_id == target.episode_id or episode.mechanic_id != target.mechanic_id or episode.outcome not in _FAILURE_OUTCOMES:
            continue
        score = signature_similarity(target.failure_signature, episode.failure_signature)
        if score >= min_similarity:
            rows.append((-score, episode.episode_id, episode))
    rows.sort(key=lambda row: (row[0], row[1]))
    return tuple(item for _, _, item in rows)
