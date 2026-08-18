"""Evaluator-side information-sufficiency analysis for P9 hostile worlds.

A view is non-identifying on a frozen set when two valid worlds collapse to the
same model-visible fingerprint while requiring different evaluator gold.  This
is an information lower bound, not a claim about a particular learning
algorithm: no learner restricted to that exact view can deterministically solve
both cases without extra information or leakage.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from .structural_world import P9StructuralWorld, ViewMode


@dataclass(frozen=True)
class IdentifiabilityCollision:
    fingerprint: str
    world_ids: tuple[str, ...]
    targets: tuple[str, ...]


@dataclass(frozen=True)
class IdentifiabilityReport:
    mode: ViewMode
    sample_count: int
    unique_fingerprint_count: int
    deterministic_accuracy_ceiling: float
    collisions: tuple[IdentifiabilityCollision, ...]

    @property
    def is_identifying(self) -> bool:
        return not self.collisions


def _target_key(world: P9StructuralWorld) -> str:
    return f"{world.gold.kind.value}:{world.gold.value}"


def analyze_identifiability(
    worlds: Sequence[P9StructuralWorld],
    mode: ViewMode,
) -> IdentifiabilityReport:
    """Return exact collisions and the empirical deterministic accuracy ceiling.

    The ceiling is the best possible accuracy of any deterministic predictor that
    receives *only* the selected fingerprint on this exact frozen sample.  For
    each fingerprint equivalence class, such a predictor can choose only one
    output, so its best score is the size of that class's majority target.
    """

    if not worlds:
        raise ValueError("at least one world is required")

    seen_world_ids: set[str] = set()
    groups: dict[str, list[P9StructuralWorld]] = {}

    for world in worlds:
        world.verify()
        if world.world_id in seen_world_ids:
            raise ValueError(f"duplicate world id: {world.world_id}")
        seen_world_ids.add(world.world_id)
        groups.setdefault(world.fingerprint(mode), []).append(world)

    collisions: list[IdentifiabilityCollision] = []
    ceiling_correct = 0
    for fingerprint, group in groups.items():
        target_counts = Counter(_target_key(world) for world in group)
        targets = tuple(sorted(target_counts))
        ceiling_correct += max(target_counts.values())
        if len(targets) <= 1:
            continue
        collisions.append(
            IdentifiabilityCollision(
                fingerprint=fingerprint,
                world_ids=tuple(sorted(world.world_id for world in group)),
                targets=targets,
            )
        )

    collisions.sort(key=lambda item: (item.fingerprint, item.world_ids, item.targets))
    return IdentifiabilityReport(
        mode=mode,
        sample_count=len(worlds),
        unique_fingerprint_count=len(groups),
        deterministic_accuracy_ceiling=ceiling_correct / len(worlds),
        collisions=tuple(collisions),
    )
