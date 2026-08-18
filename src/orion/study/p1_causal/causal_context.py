"""Absorbed causal-context construction for richer P1 executable traces.

This is a protocol-level abstraction of the useful structural lesson from
CausalRepair (arXiv:2608.10613): repair reasoning should receive the union of
context-aware static dependencies and dependencies actually exercised in the
failing execution trace, rather than the whole environment or a single noisy
slice.  The slice is evidence/context only and never grants mutation authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CausalDependency:
    source: str
    target: str
    kind: str

    def __post_init__(self) -> None:
        if self.kind not in {"STATIC", "DYNAMIC"}:
            raise ValueError(f"unsupported dependency kind:{self.kind}")
        if not self.source or not self.target:
            raise ValueError("dependency endpoints are required")


@dataclass(frozen=True)
class CausalContext:
    seed_ids: tuple[str, ...]
    included_ids: tuple[str, ...]
    static_ids: tuple[str, ...]
    dynamic_ids: tuple[str, ...]


def _backward_closure(
    seeds: Iterable[str],
    dependencies: tuple[CausalDependency, ...],
) -> tuple[str, ...]:
    selected = set(str(item) for item in seeds)
    progress = True
    while progress:
        progress = False
        for edge in dependencies:
            if edge.target in selected and edge.source not in selected:
                selected.add(edge.source)
                progress = True
    return tuple(sorted(selected))


def dual_slice_causal_context(
    *,
    failing_ids: Iterable[str],
    static_dependencies: Iterable[CausalDependency],
    dynamic_dependencies: Iterable[CausalDependency],
) -> CausalContext:
    """Union static semantic context with actually exercised trace context."""

    seeds = tuple(dict.fromkeys(str(item) for item in failing_ids))
    if not seeds:
        raise ValueError("at least one failing seed is required")
    static = tuple(static_dependencies)
    dynamic = tuple(dynamic_dependencies)
    if any(edge.kind != "STATIC" for edge in static):
        raise ValueError("static slice contains non-static edge")
    if any(edge.kind != "DYNAMIC" for edge in dynamic):
        raise ValueError("dynamic slice contains non-dynamic edge")

    static_ids = _backward_closure(seeds, static)
    dynamic_ids = _backward_closure(seeds, dynamic)
    included = tuple(sorted(set(static_ids).union(dynamic_ids)))
    return CausalContext(
        seed_ids=seeds,
        included_ids=included,
        static_ids=static_ids,
        dynamic_ids=dynamic_ids,
    )


__all__ = ["CausalContext", "CausalDependency", "dual_slice_causal_context"]
