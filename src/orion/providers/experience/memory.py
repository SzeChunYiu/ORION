from __future__ import annotations

from orion.experience.model import TaskEpisode


class InMemoryExperienceStore:
    """Deterministic V0 store used for tests and local Shadow trials."""

    def __init__(self, episodes: tuple[TaskEpisode, ...] = ()) -> None:
        self._episodes = list(episodes)
        if len({item.episode_id for item in self._episodes}) != len(self._episodes):
            raise ValueError("experience store episode ids must be unique")

    def append(self, episode: TaskEpisode) -> None:
        if any(item.episode_id == episode.episode_id for item in self._episodes):
            raise ValueError(f"duplicate experience episode id: {episode.episode_id}")
        self._episodes.append(episode)

    def episodes(self) -> tuple[TaskEpisode, ...]:
        return tuple(self._episodes)
