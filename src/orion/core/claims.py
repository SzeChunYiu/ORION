from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClaimAuthority(str, Enum):
    PROPOSED = "PROPOSED"
    SOURCE_PROJECTION = "SOURCE_PROJECTION"
    VERIFIED = "VERIFIED"


@dataclass(frozen=True)
class ClaimRecord:
    claim_id: str
    text: str
    evidence_ids: tuple[str, ...]
    authority: ClaimAuthority = ClaimAuthority.SOURCE_PROJECTION
    certificate_ids: tuple[str, ...] = ()
    contradicts_claim_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.claim_id.strip() or not self.text.strip():
            raise ValueError("claim identity and text are required")
        if self.authority is ClaimAuthority.VERIFIED and not self.certificate_ids:
            raise ValueError("verified claim requires verification certificate")
