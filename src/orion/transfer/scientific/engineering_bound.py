"""Bound the #136 transfer substrate as engineering-only, not scientific transfer."""

from __future__ import annotations

from pathlib import Path

ENGINEERING_ONLY_AUTHORITY = "LOCAL_ENGINEERING_ONLY"

ENGINEERING_ONLY_TEST_FILES = (
    "tests/test_verified_structural_transfer.py",
    "tests/test_transfer_v2.py",
    "tests/test_transfer_v2_assets.py",
)


def bound_transfer_test_files(root: Path) -> tuple[Path, ...]:
    return tuple(root / relative for relative in ENGINEERING_ONLY_TEST_FILES)
