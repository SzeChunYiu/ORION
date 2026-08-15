from __future__ import annotations

from dataclasses import dataclass, field, replace

from orion.core.claims import ClaimRecord
from orion.core.closure import ClosureCertificate
from orion.core.evidence import EvidenceRecord
from orion.core.history import IterationRecord, NegativeHistoryEntry
from orion.core.method import MethodState
from orion.core.portrait import GlobalPortrait
from orion.core.residuals import Residual
from orion.core.search_universe import SearchUniverseState


@dataclass(frozen=True)
class KnowledgeState:
    """K_t: provenance-preserving portrait of the research object."""

    claims: tuple[ClaimRecord, ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()
    portraits: tuple[GlobalPortrait, ...] = ()
    residuals: tuple[Residual, ...] = ()
    negative_history: tuple[NegativeHistoryEntry, ...] = ()

    @property
    def evidence_ids(self) -> tuple[str, ...]:
        return tuple(item.evidence_id for item in self.evidence)

    @property
    def residual_ids(self) -> tuple[str, ...]:
        return tuple(item.residual_id for item in self.residuals)

    @property
    def negative_history_ids(self) -> tuple[str, ...]:
        return tuple(item.entry_id for item in self.negative_history)


@dataclass(frozen=True)
class OrionState:
    """ORION state: object knowledge K, search universe W, method M."""

    knowledge: KnowledgeState
    search_universe: SearchUniverseState
    method: MethodState
    closure_certificates: tuple[ClosureCertificate, ...] = ()
    iterations: tuple[IterationRecord, ...] = ()
    epoch: int = 0
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def advance(self) -> OrionState:
        return replace(self, epoch=self.epoch + 1)
