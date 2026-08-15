from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class StorageLayer(str, Enum):
    RAW_SOURCE = "RAW_SOURCE"
    CANONICAL = "CANONICAL"
    WORKING_VIEW = "WORKING_VIEW"
    EPISODE = "EPISODE"
    RECEIPT = "RECEIPT"
    ARTIFACT = "ARTIFACT"
    INDEX_CACHE = "INDEX_CACHE"


@dataclass(frozen=True)
class StorageRequirement:
    storage_id: str
    mechanic_id: str
    layer: StorageLayer
    identity_semantics: str
    mutability_semantics: str
    retention_semantics: str
    reconstruction_semantics: str
    eviction_semantics: str

    def __post_init__(self) -> None:
        required = (
            self.storage_id,
            self.mechanic_id,
            self.identity_semantics,
            self.mutability_semantics,
            self.retention_semantics,
            self.reconstruction_semantics,
            self.eviction_semantics,
        )
        if any(not value.strip() for value in required):
            raise ValueError("storage requirement fields cannot be empty")


def default_storage_requirements(cell: MechanicCell) -> tuple[StorageRequirement, ...]:
    def req(layer: StorageLayer, identity: str, mutable: str, retain: str, reconstruct: str, evict: str) -> StorageRequirement:
        return StorageRequirement(f"storage:{cell.mechanic_id}:{layer.value.lower()}", cell.mechanic_id, layer, identity, mutable, retain, reconstruct, evict)

    return (
        req(StorageLayer.RAW_SOURCE, "stable source URI/selector plus source content/version identity", "append/reference only; raw evidence is not silently overwritten", "retain while any claim/receipt/benchmark depends on it", "re-fetch only when immutable identity/content equality can be established; otherwise preserve version distinction", "never evict the only recoverable evidence behind an authoritative claim"),
        req(StorageLayer.CANONICAL, "content-addressed or stable canonical object identity with supersession lineage", "canonical mutation occurs by versioned/superseding update, not hidden in-place rewrite", "retain current and historically authority-relevant versions", "reconstruct from source/evidence/transformation receipts", "may compact projections/indexes, not provenance-bearing canonical history"),
        req(StorageLayer.WORKING_VIEW, "operation/run/context identity", "ephemeral/recomputable under the bound run state", "retain only as required for active execution/debug/replay obligations", "compile from canonical/mandatory context under a declared context policy", "safe to evict only if mandatory material and reconstruction pointers remain"),
        req(StorageLayer.EPISODE, "immutable task/mechanic episode identity including variation and pre/post state", "append-only", "preserve success, failure, partial, blocked and cannot-check episodes used for learning/evaluation", "not reconstructed from summaries when exact episode evidence is required", "do not delete negative episodes because later performance improves"),
        req(StorageLayer.RECEIPT, "execution/verification/promotion receipt identity bound to exact inputs/state/version", "append-only except explicit supersession metadata", "retain as long as downstream state/authority/claims depend on it", "replay receipt rather than re-execute side effects when the contract permits", "not evictable while load-bearing"),
        req(StorageLayer.ARTIFACT, "content digest plus producing run/mechanic identity", "immutable content; new content receives new identity", "retain when cited by evidence, paper, benchmark or reproducibility receipt", "rebuild only under a deterministic/version-bound build contract", "derived disposable artifacts may be evicted when reproducible from retained parents"),
        req(StorageLayer.INDEX_CACHE, "cache/index version bound to underlying canonical/source set", "rebuildable", "performance convenience only", "rebuild from canonical/raw layers", "may evict freely if cache loss cannot erase epistemic content or authority"),
    )


def apply_default_storage_contract(cell: MechanicCell) -> MechanicCell:
    requirements = default_storage_requirements(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific storage volume/indexing strategy, retention horizon, privacy/security classification, compaction loss and retrieval performance",)))
    return replace(
        cell,
        storage_contracts=tuple(f"{item.storage_id}:{item.identity_semantics}:{item.mutability_semantics}:{item.retention_semantics}:{item.reconstruction_semantics}:{item.eviction_semantics}" for item in requirements),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_storage_contracts(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_storage_contract(cell) for cell in cells)
