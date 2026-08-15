from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class KnowledgeState:
    """Current provenance-preserving portrait of the research object."""

    claims: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    negative_history_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class SearchUniverseState:
    """Current model of what kinds of knowledge may be relevant."""

    domain_ids: tuple[str, ...] = ()
    route_ids: tuple[str, ...] = ()
    representation_ids: tuple[str, ...] = ()
    open_coverage_residual_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MethodState:
    """Current ORION method identity and protected evaluator binding."""

    method_version: str
    operator_ids: tuple[str, ...] = ()
    evaluator_id: str | None = None


@dataclass(frozen=True)
class OrionState:
    """Minimal bootstrap state: object knowledge K, search universe W, method M."""

    knowledge: KnowledgeState
    search_universe: SearchUniverseState
    method: MethodState
    epoch: int = 0
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def advance(self) -> "OrionState":
        return OrionState(
            knowledge=self.knowledge,
            search_universe=self.search_universe,
            method=self.method,
            epoch=self.epoch + 1,
            metadata=self.metadata,
        )
