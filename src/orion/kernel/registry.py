from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Mapping

from .gate import DiscriminatingCheck

_CHECKS_PACKAGE = "orion.kernel.checks"


class CheckRegistryError(ValueError):
    """A lane module declared checks that violate the registry contract."""


def load_registered_checks(
    package: str = _CHECKS_PACKAGE,
) -> Mapping[str, DiscriminatingCheck]:
    """Discover discriminating checks from per-lane modules.

    Each module under ``orion.kernel.checks`` declares ``LANE`` (one lane per
    module, so authorship is file-visible in review) and ``CHECKS``, a tuple of
    :class:`DiscriminatingCheck`. The registry enforces what the gate cannot
    see from a single check: every check in a module carries that module's
    lane, check ids are globally unique, and every check is chronology-pinned
    (``frozen_at_round`` set) — an unpinned check can never verify, so
    registering one is a defect, not a preference.

    Trust boundary: checks are executable code and enter only through ordinary
    reviewed imports of this package — the registry never loads code from
    data directories.
    """

    try:
        root = importlib.import_module(package)
    except ModuleNotFoundError:
        return {}

    checks: dict[str, DiscriminatingCheck] = {}
    for module_info in sorted(pkgutil.iter_modules(root.__path__), key=lambda m: m.name):
        module = importlib.import_module(f"{package}.{module_info.name}")
        lane = getattr(module, "LANE", "")
        declared = getattr(module, "CHECKS", ())
        if not isinstance(lane, str) or not lane.strip():
            raise CheckRegistryError(
                f"check module '{module_info.name}' must declare a non-empty LANE"
            )
        for check in declared:
            if not isinstance(check, DiscriminatingCheck):
                raise CheckRegistryError(
                    f"check module '{module_info.name}' declared a non-check object"
                )
            if check.lane != lane:
                raise CheckRegistryError(
                    f"check '{check.check_id}' carries lane '{check.lane}' but lives in"
                    f" lane-'{lane}' module '{module_info.name}'"
                )
            if check.frozen_at_round is None:
                raise CheckRegistryError(
                    f"check '{check.check_id}' is not chronology-pinned (frozen_at_round)"
                )
            if not check.negative_fixtures:
                raise CheckRegistryError(
                    f"check '{check.check_id}' declares no negative fixtures; a check"
                    " that has never exhibited a failing case of its own is not"
                    " demonstrably failable (seed-failability analogue)"
                )
            if check.check_id in checks:
                raise CheckRegistryError(f"duplicate check id '{check.check_id}'")
            checks[check.check_id] = check
    return checks
