"""Prospectively bind the O1 route-stop FP/FN publication projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p2.corpus import canonical_bytes
from orion.study.p2.freeze import load_suite, verify
from orion.study.p2.offline_analysis import run_offline_companion
from orion.study.p2.offline_route_stop import build_route_stop_projection

PAPER = Path("papers/paper-02-open-world-scientific-discovery")
MANIFEST = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.json"
MANIFEST_SHA = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.sha256"


def _manifest_hash() -> str:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    computed = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    recorded = MANIFEST_SHA.read_text(encoding="utf-8").split()[0]
    assert computed == recorded
    return computed


def test_emit_route_stop_projection_before_snapshot_commit() -> None:
    report = verify()
    assert report.ok, report.problems
    suite = load_suite()
    archive = run_offline_companion(
        suite.world,
        suite.tasks,
        run_manifest_hash=_manifest_hash(),
    )
    projection = build_route_stop_projection(suite.tasks, archive.outcomes)
    raise AssertionError(
        "P2_ROUTE_STOP_ORACLE_SNAPSHOT="
        + json.dumps(projection, sort_keys=True, separators=(",", ":"))
    )
