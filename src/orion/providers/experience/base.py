from __future__ import annotations

from typing import Protocol

from orion.experience.model import TaskEpisode


class ExperienceStore(Protocol):
    """Persistence boundary for immutable ORION task episodes."""

    def append(self, episode: TaskEpisode) -> None:
        ...

    def episodes(self) -> tuple[TaskEpisode, ...]:
        ...
