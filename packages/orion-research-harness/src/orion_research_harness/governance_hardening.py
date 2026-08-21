from __future__ import annotations

from collections.abc import Mapping

from . import governance_runtime as _governance


def _strict_no_authority(value) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("external governance result keys must be strings")
            if key in _governance._FORBIDDEN_AUTHORITY_KEYS and item is not False:
                raise ValueError(
                    "external governance authority fields, when present, must be literal false: "
                    + key
                )
            _strict_no_authority(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _strict_no_authority(item)


def install_governance_hardening() -> None:
    _governance._scan_no_authority = _strict_no_authority
    _governance._strict_authority_scan_installed = True


install_governance_hardening()


__all__ = ["install_governance_hardening"]
