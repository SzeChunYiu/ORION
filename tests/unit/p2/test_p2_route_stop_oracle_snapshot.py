"""Bind the O1 route-stop FP/FN publication projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p2.corpus import canonical_bytes
from orion.study.p2.freeze import load_suite, verify
from orion.study.p2.offline_analysis import run_offline_companion
from orion.study.p2.offline_route_stop import build_route_stop_projection

PAPER = Path("papers/orion-12-open-world-scientific-discovery")
MANIFEST = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.json"
MANIFEST_SHA = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.sha256"
EXPECTED = PAPER / "evidence" / "offline_results" / "ROUTE_STOP_ORACLE_V1.json"


def _manifest_hash() -> str:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    computed = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    recorded = MANIFEST_SHA.read_text(encoding="utf-8").split()[0]
    assert computed == recorded
    return computed


def test_route_stop_projection_matches_frozen_snapshot() -> None:
    report = verify()
    assert report.ok, report.problems
    suite = load_suite()
    archive = run_offline_companion(
        suite.world,
        suite.tasks,
        run_manifest_hash=_manifest_hash(),
    )
    projection = build_route_stop_projection(suite.tasks, archive.outcomes)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert projection == expected
    assert projection["n_tasks"] == len(suite.tasks)

    # The oracle's load-bearing property is the *direction*: ORION must never declare
    # a route exhausted while that route still had reachable relevant material (a
    # false negative on route-stop is the failure that licenses closing a task
    # early). The false-positive count is a conservatism cost and scales with the
    # suite, so it is bounded as a rate rather than pinned to the integer a
    # 20-task run happened to produce.
    orion = projection["systems"]["orion_full"]
    assert orion["route_stop_false_negative_count"] == 0
    assert orion["route_stop_false_negative_rate"] == 0.0
    assert orion["route_stop_false_positive_rate"] < 0.05
    assert projection["orion_full_by_route"]["RESTRICTED"][
        "attempts_after_exhaustion_total"
    ] > 0
