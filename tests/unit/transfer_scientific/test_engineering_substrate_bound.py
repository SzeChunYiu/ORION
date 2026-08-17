"""Existing #136 transfer tests are engineering substrate, not scientific transfer."""

from __future__ import annotations

from pathlib import Path

from orion.transfer.scientific.engineering_bound import (
    ENGINEERING_ONLY_AUTHORITY,
    ENGINEERING_ONLY_TEST_FILES,
    bound_transfer_test_files,
)

ROOT = Path(__file__).resolve().parents[3]


def test_listed_local_transfer_tests_exist_and_are_labelled_engineering_only() -> None:
    paths = bound_transfer_test_files(ROOT)
    assert paths == tuple(ROOT / relative for relative in ENGINEERING_ONLY_TEST_FILES)
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert path.is_file()
        assert ENGINEERING_ONLY_AUTHORITY in text
        assert "#286" in text


def test_engineering_bound_does_not_claim_scientific_transfer() -> None:
    assert ENGINEERING_ONLY_AUTHORITY == "LOCAL_ENGINEERING_ONLY"
    assert "SCIENTIFIC_TRANSFER" not in ENGINEERING_ONLY_AUTHORITY
