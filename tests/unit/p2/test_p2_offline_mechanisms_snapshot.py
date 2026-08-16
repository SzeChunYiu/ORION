"""Bind the evaluator-side projection for P2-3/P2-4/P2-5."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p2.corpus import canonical_bytes
from orion.study.p2.freeze import load_suite, verify
from orion.study.p2.offline_analysis import run_offline_companion
from orion.study.p2.offline_mechanisms import build_offline_mechanism_projection

PAPER = Path("papers/paper-02-open-world-scientific-discovery")
MANIFEST = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.json"
MANIFEST_SHA = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.sha256"
EXPECTED = PAPER / "evidence" / "offline_results" / "OFFLINE_MECHANISMS_V1.json"


def _manifest_hash() -> str:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    computed = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    recorded = MANIFEST_SHA.read_text(encoding="utf-8").split()[0]
    assert computed == recorded
    assert payload["outcome_accessed_before_freeze"] is False
    return computed


def test_offline_mechanism_projection_matches_frozen_snapshot() -> None:
    report = verify()
    assert report.ok, report.problems
    suite = load_suite()
    archive = run_offline_companion(
        suite.world,
        suite.tasks,
        run_manifest_hash=_manifest_hash(),
    )
    projection = build_offline_mechanism_projection(suite.tasks, archive.outcomes)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert projection == expected
    assert projection["source_record_digest_sha256"] == (
        "611808dc80846d5057c84c12af7ff8ec3fa88ef15a6ede91807e590f4edb6f1f"
    )
    assert projection["source_raw_artifact_hash_list_digest_sha256"] == (
        "2da59dc21e6473e4a81eb93910501a67bed008dbc3e29c26116041b68dfbb325"
    )
