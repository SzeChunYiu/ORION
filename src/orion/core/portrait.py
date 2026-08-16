from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GlobalPortrait:
    portrait_id: str
    summary: str
    claim_ids: tuple[str, ...]
    verified_claim_ids: tuple[str, ...] = ()
    unresolved_residual_ids: tuple[str, ...] = ()
    source_projection_ids: tuple[str, ...] = ()
    representation_mapping_ids: tuple[str, ...] = ()
