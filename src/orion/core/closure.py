from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ClosureCertificate:
    certificate_id: str
    scope: str
    dependency_coordinates: tuple[str, ...]
    stale: bool = False
    stale_reason: str | None = None

    def invalidate(self, reason: str) -> "ClosureCertificate":
        return replace(self, stale=True, stale_reason=reason)
