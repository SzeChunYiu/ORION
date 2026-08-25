"""Import every module in the package and report what fails, and why.

This exists because a smoke test that imports two modules will pass on a
package whose dependency metadata is incomplete. That happened here: the
reproduction path reported OK while five source files imported scipy, which
pyproject.toml declared nowhere.

The distinction that matters is between:
  - a CORE module failing            -> a real defect, exit 1
  - an EXTRA module failing on a
    third-party import when that
    extra is not installed           -> expected, reported, exit 0

Collapsing those two would either cry wolf on every base install or hide
genuine metadata defects. Both are worse than reporting the split.
"""
from __future__ import annotations

import importlib
import pkgutil
import sys

CORE_PREFIXES = ("orion.kernel", "orion.programme")


def main() -> int:
    import orion

    core_failures: list[tuple[str, str]] = []
    extra_failures: list[tuple[str, str]] = []
    ok = 0

    skipped = 0
    for mod in pkgutil.walk_packages(orion.__path__, prefix="orion."):
        name = mod.name
        # __main__ modules are meant to be EXECUTED, not imported: importing
        # one runs its argparse and raises SystemExit, which derives from
        # BaseException and so escapes `except Exception` entirely. The first
        # version of this sweep died on orion.benchmarks.__main__ for exactly
        # that reason.
        if name.endswith(".__main__"):
            skipped += 1
            continue
        try:
            importlib.import_module(name)
            ok += 1
        except ModuleNotFoundError as exc:
            missing = (exc.name or "?")
            entry = (name, f"missing third-party module '{missing}'")
            (core_failures if name.startswith(CORE_PREFIXES) else extra_failures).append(entry)
        except BaseException as exc:  # noqa: BLE001
            # BaseException, not Exception: a module that calls sys.exit() or
            # raises KeyboardInterrupt at import time must be REPORTED, not
            # allowed to abort the sweep and take every later module with it.
            entry = (name, f"{type(exc).__name__}: {exc}")
            (core_failures if name.startswith(CORE_PREFIXES) else extra_failures).append(entry)

    print(f"imported cleanly : {ok}")
    print(f"skipped (__main__): {skipped}")
    print(f"core failures    : {len(core_failures)}")
    print(f"optional failures: {len(extra_failures)}")

    if extra_failures:
        print("\nModules needing an optional extra (expected on a base install):")
        for n, why in extra_failures[:12]:
            print(f"  - {n}: {why}")
        if len(extra_failures) > 12:
            print(f"  ... and {len(extra_failures) - 12} more")
        print("  Install with:  pip install -e '.[candidates]'")

    if core_failures:
        print("\nDEFECT -- core modules must import with declared dependencies alone:")
        for n, why in core_failures:
            print(f"  - {n}: {why}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
