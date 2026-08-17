from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p3_confirmatory_receipt import (
    FROZEN_CLAIM,
    GoldUnavailableError,
    RECEIPT_PATH,
    build_receipt,
    require_gold_file,
)


def test_confirmatory_reproduction_matches_frozen_claim() -> None:
    receipt = build_receipt(write=False)
    assert receipt["reproduction_verdict"] == "REPRODUCED"
    assert receipt["v1_confirmatory_immutable"] is True
    assert receipt["frozen_claim"] == FROZEN_CLAIM
    assert receipt["checks"]["matched"] is True
    assert receipt["overlap"]["case_id_overlap_count"] == 0
    assert receipt["overlap"]["confirmatory_n"] == 32
    observed = receipt["checks"]["observed"]
    assert observed["orion_false_merge"] == 0.0
    assert observed["flat_false_merge"] == 0.1875
    assert observed["false_merge_difference"] == -0.1875
    assert observed["false_merge_ci95"] == [-0.34375, -0.0625]
    assert observed["false_split_difference"] == 0.0
    assert observed["false_split_ci95"] == [0.0, 0.0]
    assert observed["primary_verdict"] == "PASS"
    assert len(receipt["receipt_sha256"]) == 64
    assert receipt["regenerated"]["frozen_analysis_canonical_match"] is True
    assert receipt["publication_regeneration"]["matched"] is True
    committed = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert committed["receipt_sha256"] == receipt["receipt_sha256"]
    assert committed["reproduction_verdict"] == "REPRODUCED"


def test_missing_gold_is_cannot_check(tmp_path: Path) -> None:
    missing = tmp_path / "absent.jsonl"
    with pytest.raises(GoldUnavailableError, match="CANNOT_CHECK"):
        require_gold_file(missing, "0" * 64)


def test_drifted_gold_hash_is_cannot_check(tmp_path: Path) -> None:
    path = tmp_path / "gold.jsonl"
    path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(GoldUnavailableError, match="gold hash mismatch"):
        require_gold_file(path, "0" * 64)
