from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NegativeHistoryEntry:
    entry_id: str
    failure_class: str
    description: str
    residual_id: str | None = None


@dataclass(frozen=True)
class IterationRecord:
    iteration: int
    new_claim_ids: tuple[str, ...] = ()
    new_evidence_ids: tuple[str, ...] = ()
    new_domain_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    changed_coordinates: tuple[str, ...] = ()
    route_kind_ids: tuple[str, ...] = ()

    @property
    def semantic_flat(self) -> bool:
        return not (self.new_claim_ids or self.new_evidence_ids or self.residual_ids)

    @property
    def search_universe_flat(self) -> bool:
        return not self.new_domain_ids and not any(
            coordinate.startswith("W.") for coordinate in self.changed_coordinates
        )

    @property
    def formulation_flat(self) -> bool:
        formulation_prefixes = ("QUESTION", "FRAME", "W.REPRESENTATIONS", "METHOD", "EVALUATOR")
        return not any(
            coordinate == prefix or coordinate.startswith(prefix + ".")
            for coordinate in self.changed_coordinates
            for prefix in formulation_prefixes
        )

    @property
    def flat(self) -> bool:
        return self.semantic_flat and self.search_universe_flat and self.formulation_flat
