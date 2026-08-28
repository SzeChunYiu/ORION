#!/usr/bin/env python3
"""Idempotently normalize known branch-local documentation/test details.

This script exists because the issue branch is assembled through atomic GitHub
writes. It converts early draft references into the canonical versioned checker
and keeps the manual package checksum command aligned with CI.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PAPER = REPO / "papers/orion-01-certificate-realization/v3-bounded-closeout-2026-08-29"


def replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise AssertionError(f"neither old nor normalized text found in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def main() -> int:
    changed: list[str] = []

    operations = [
        (
            HERE / "README.md",
            "- `registry_protocol_checker.py` — implementation-independent protocol checker",
            "- `registry_protocol_checker_v1.py` — canonical implementation-independent protocol checker\n- `test_registry_protocol_checker_v1_corrected.py` — canonical checker tests",
        ),
        (
            HERE / "CANONICAL_CHECKER.md",
            "- `test_registry_protocol_checker_v1.py`",
            "- `test_registry_protocol_checker_v1_corrected.py`",
        ),
        (
            HERE / "test_registry_protocol_checker_v1.py",
            'by_name["required_files_and_no_outcome_leakage"]["future_only_files_absent"], 18',
            'by_name["required_files_and_no_outcome_leakage"]["future_only_files_absent"], 17',
        ),
        (
            HERE / "QUESTION.md",
            "- the old terminal `CANNOT_CHECK_MOVE_COMPLETENESS` can be upgraded retrospectively.",
            "- The old terminal `CANNOT_CHECK_MOVE_COMPLETENESS` can be upgraded retrospectively.",
        ),
        (
            PAPER / "COMPILE.md",
            "  DATA_CODE_AVAILABILITY.md LICENSE.md COVER_LETTER_A.md COVER_LETTER_B.md \\\n  SUBMISSION_MANIFEST_V3.json > SHA256SUMS",
            "  DATA_CODE_AVAILABILITY.md LICENSE.md COVER_LETTER_A.md COVER_LETTER_B.md \\\n  COMPILE.md build_manifest_v3.py SUBMISSION_MANIFEST_V3.json > SHA256SUMS",
        ),
    ]

    for path, old, new in operations:
        if replace_once(path, old, new):
            changed.append(str(path.relative_to(REPO)))

    print("normalized files:" if changed else "sources already normalized")
    for path in changed:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
