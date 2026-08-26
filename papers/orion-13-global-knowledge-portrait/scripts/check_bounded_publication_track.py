#!/usr/bin/env python3
"""Fail-closed guard for the bounded ORION-P3 publication track."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TRACK = (
    ROOT
    / "papers"
    / "paper-03-global-knowledge-portrait"
    / "evidence"
    / "P3_BOUNDED_PUBLICATION_TRACK_V1.json"
)


def _fail(message: str) -> None:
    raise SystemExit(f"P3_BOUNDED_TRACK_FAIL: {message}")


def main() -> int:
    if not TRACK.is_file():
        _fail("track record missing")

    data = json.loads(TRACK.read_text(encoding="utf-8"))
    if data.get("schema_version") != "orion.p3.bounded-publication-track.v1":
        _fail("wrong schema")
    if data.get("paper_id") != "P3" or data.get("status") != "FROZEN_BOUNDED_TRACK":
        _fail("wrong paper/status")

    result = data.get("confirmatory_result", {})
    expected = {
        "n": 32,
        "orion_false_merges": 0,
        "flat_false_merges": 6,
        "flat_false_merge_rate": 0.1875,
        "paired_absolute_difference": -0.1875,
        "false_split_difference": 0.0,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            _fail(f"confirmatory result drift: {key}")
    if result.get("reported_95_interval") != [-0.34375, -0.0625]:
        _fail("false-merge interval drift")
    if result.get("reported_false_split_interval") != [0.0, 0.0]:
        _fail("false-split interval drift")

    if data.get("evidence_scope") != "already_structured_public_reference_mapping_only":
        _fail("scope broadened")

    atlas = data.get("expert_atlas", {})
    if atlas.get("preserved") is not True:
        _fail("expert-atlas follow-up was erased")
    if atlas.get("current_publication_blocker") is not False:
        _fail("bounded paper was re-blocked without a claim change")
    if atlas.get("disposition") != "FOLLOW_UP_GENERALIZATION":
        _fail("expert-atlas disposition drift")

    required_nonclaims = {
        "universal cross-domain ontology construction",
        "raw-document-to-global-portrait extraction",
        "expert-atlas generality",
        "unrestricted real-world scientific-integration superiority",
    }
    nonclaims = set(data.get("nonclaims", []))
    missing = sorted(required_nonclaims - nonclaims)
    if missing:
        _fail("missing nonclaims: " + ", ".join(missing))

    authority = data.get("authority", {})
    for field in (
        "may_claim_peer_review_ready_from_this_record_alone",
        "may_claim_novelty_from_this_record_alone",
        "may_claim_external_generality_from_this_record_alone",
    ):
        if authority.get(field) is not False:
            _fail(f"authority laundering through {field}")
    if authority.get("negative_null_history_must_remain_visible") is not True:
        _fail("negative/null history preservation disabled")

    required_paths = [
        ROOT / "papers" / "paper-03-global-knowledge-portrait" / "JOURNAL_READINESS.md",
        ROOT / "papers" / "paper-03-global-knowledge-portrait" / "manuscript" / "main.tex",
        ROOT / "research" / "verification" / "records",
    ]
    missing_paths = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing_paths:
        _fail("required P3 publication substrate missing: " + ", ".join(missing_paths))

    print("P3_BOUNDED_PUBLICATION_TRACK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
