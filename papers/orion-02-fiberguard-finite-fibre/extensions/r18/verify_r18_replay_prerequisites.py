#!/usr/bin/env python3
"""Data-free import, version, protocol, and synthetic preflight for R18 replay.

The pinned ASlib corpus is intentionally not vendored. This check proves that
all exact donor modules import and their data-free self-tests run; it is not a
fresh corpus replay or a new scientific result.
"""
from __future__ import annotations

from importlib.metadata import version
import json
from pathlib import Path
import sys

import fiberguard_aslib_sat12_all_r11 as r11
import fiberguard_paired_route_r18_data as data_module
import fiberguard_paired_route_r18_policy as policy
import fiberguard_paired_route_r18_sources as sources


TERMINAL = "R18_REPLAY_CODE_PREFLIGHT_PASS__PINNED_ASLIB_CORPUS_NOT_VENDORED"
EXPECTED_VERSIONS = {
    "numpy": "2.1.3",
    "scikit-learn": "1.5.2",
    "PyYAML": "6.0.2",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    require(sys.version_info[:2] == (3, 12), "R18 replay requires Python 3.12.x")
    observed_versions = {name: version(name) for name in EXPECTED_VERSIONS}
    require(observed_versions == EXPECTED_VERSIONS, "R18 replay dependency drift")

    root = Path(__file__).resolve().parent
    protocol = json.loads((root / "PAIRED_ROUTE_PROTOCOL_R18.json").read_text(encoding="utf-8"))
    sources.validate_protocol(protocol)
    require(r11.ASLIB_COMMIT == sources.EXPECTED_UPSTREAM, "R11 parser source drift")
    require(data_module.self_test().get("status") == "GREEN", "R18 data self-test")
    require(policy.self_test().get("status") == "GREEN", "R18 policy self-test")

    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
