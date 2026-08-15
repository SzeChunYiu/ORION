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

    @property
    def flat(self) -> bool:
        return not (
            self.new_claim_ids
            or self.new_evidence_ids
            or self.new_domain_ids
            or self.residual_ids
            or self.changed_coordinates
        )
