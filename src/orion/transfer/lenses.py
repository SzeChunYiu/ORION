from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class ConsistencyStatus(str, Enum):
    GLOBALIZABLE = "GLOBALIZABLE"
    OBSTRUCTION = "OBSTRUCTION"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class AffineLens:
    scale: float
    offset: float = 0.0

    def __post_init__(self) -> None:
        if abs(self.scale) <= 1e-15:
            raise ValueError("scale must be non-zero")

    def forward(self, source: float) -> float:
        return self.scale * source + self.offset

    def backward(self, view: float) -> float:
        return (view - self.offset) / self.scale

    def inverse(self) -> "AffineLens":
        return AffineLens(scale=1.0 / self.scale, offset=-self.offset / self.scale)

    def then(self, nxt: "AffineLens") -> "AffineLens":
        """Compose ``self`` then ``nxt``."""
        return AffineLens(
            scale=nxt.scale * self.scale,
            offset=nxt.scale * self.offset + nxt.offset,
        )

    def round_trip_error(self, source: float) -> float:
        return abs(self.backward(self.forward(source)) - source)


@dataclass(frozen=True)
class LensEdge:
    source: str
    target: str
    lens: AffineLens


class ScientificLensNetwork:
    def __init__(self, edges: Sequence[LensEdge]) -> None:
        self._edges = {(edge.source, edge.target): edge.lens for edge in edges}
        for edge in edges:
            self._edges.setdefault((edge.target, edge.source), edge.lens.inverse())

    def compose_path(self, path: Sequence[str]) -> AffineLens:
        if len(path) < 2:
            raise ValueError("path requires at least two nodes")
        composed = AffineLens(1.0, 0.0)
        for source, target in zip(path, path[1:]):
            edge = self._edges.get((source, target))
            if edge is None:
                raise KeyError((source, target))
            composed = composed.then(edge)
        return composed

    def cycle_error(self, cycle: Sequence[str], anchor: float) -> float:
        if len(cycle) < 3 or cycle[0] != cycle[-1]:
            raise ValueError("cycle must contain at least two edges and return to its start")
        lens = self.compose_path(cycle)
        return abs(lens.forward(anchor) - anchor)

    def assess_cycle(
        self,
        cycle: Sequence[str],
        anchors: Sequence[float],
        *,
        tolerance: float = 1e-9,
    ) -> ConsistencyStatus:
        if not anchors:
            return ConsistencyStatus.CANNOT_CHECK
        worst = max(self.cycle_error(cycle, anchor) for anchor in anchors)
        if worst <= tolerance:
            return ConsistencyStatus.GLOBALIZABLE
        return ConsistencyStatus.OBSTRUCTION
