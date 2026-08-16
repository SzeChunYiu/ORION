"""Freeze the P2 offline result archive after the run manifest, never before it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p2.corpus import canonical_bytes
from orion.study.p2.freeze import load_suite, verify
from orion.study.p2.offline_analysis import run_offline_companion

PAPER = Path("papers/paper-02-open-world-scientific-discovery")
MANIFEST = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.json"
MANIFEST_SHA = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.sha256"
EXPECTED = PAPER / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"


def _manifest_hash() -> str:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    computed = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    recorded = MANIFEST_SHA.read_text(encoding="utf-8").split()[0]
    assert computed == recorded
    assert payload["outcome_accessed_before_freeze"] is False
    return computed


def test_offline_archive_is_reproducible_and_matches_committed_snapshot() -> None:
    report = verify()
    assert report.ok, report.problems
    suite = load_suite()
    archive = run_offline_companion(
        suite.world,
        suite.tasks,
        run_manifest_hash=_manifest_hash(),
    )
    assert len(archive.outcomes) == 20 * 3 * 14
    assert not any(item.record["status"] == "INVALID" for item in archive.outcomes)
    if not EXPECTED.is_file():
        # Deliberate RED phase: the first outcome access happens only after the
        # manifest is frozen. CI prints the deterministic candidate snapshot;
        # the next commit records it and turns this into a permanent drift test.
        raise AssertionError(
            "RESULTS_SNAPSHOT::" + json.dumps(archive.summary, sort_keys=True, separators=(",", ":"))
        )
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert archive.summary == expected
