from __future__ import annotations

from . import paper_programme_conformance as _programme
from .ocme_runtime import LowerLevelResult, REQUIRED_LOWER_LEVEL_ROUTE_KINDS


_INSTALLED = False


def install_ocme_programme_hardening() -> None:
    """Bind the P1-P15 P10 probe to the frozen eight-family O1 contract."""

    global _INSTALLED
    if _INSTALLED:
        return

    def _ocme_lower() -> tuple[LowerLevelResult, ...]:
        return tuple(
            LowerLevelResult(
                check_id=route_kind,
                route_kind=route_kind,
                succeeded=False,
                evidence_ids=(f"e:{route_kind}",),
            )
            for route_kind in REQUIRED_LOWER_LEVEL_ROUTE_KINDS
        )

    _programme._ocme_lower = _ocme_lower
    _programme._ocme_programme_hardening_installed = True
    _INSTALLED = True


install_ocme_programme_hardening()


__all__ = ["install_ocme_programme_hardening"]
