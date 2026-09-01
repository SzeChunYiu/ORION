"""The clean-room receipt's binding count is a snapshot, not a live identity.

`check_p6_cleanroom_replay_v1.py` asserted `bindings_checked == len(pairs)`,
comparing a number frozen into the receipt on 2026-08-24 against a count
recomputed from today's manifest. The receipt records 21 and was right: on that
date the paper was still `paper-06-...` with 8 contract entries, 12 bound files
and 1 environment lock. The manifest has since grown to 148 bound files as the
paper was finished, so the identity had to fail, and did -- for weeks, while every
binding it nominally guarded recomputed cleanly.

A check that must break as a paper is completed is not an integrity check. These
tests hold the replacement to the standard the old one failed: it must still catch
a receipt that lies, and must not fire on legitimate growth.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/orion-16-formal-epistemic-structures-and-mechanics"
CHECKER = PAPER / "evidence/independent/check_p6_cleanroom_replay_v1.py"
RECEIPT = PAPER / "evidence/independent/P6_CLEANROOM_REPLAY_RECEIPT_V1.json"


def _run() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_the_checker_passes_on_the_committed_tree() -> None:
    result = _run()
    assert "CHECK PASSED" in result.stdout, result.stdout


def test_the_snapshot_is_reported_rather_than_hidden() -> None:
    """Silently accepting the gap would be as bad as failing on it.

    A reader has to be able to see that the receipt covered fewer bindings than
    exist now, and that the shortfall is growth rather than an unchecked file.
    """

    stdout = _run().stdout
    assert "receipt is a snapshot" in stdout
    assert "recompute" in stdout


def test_the_recorded_count_was_correct_when_it_was_written() -> None:
    """21 is not a wrong number. It is a right number from another day."""

    custody = json.loads(RECEIPT.read_text(encoding="utf-8"))["facts"]["custody"]
    assert custody["bindings_checked"] == 21
    assert custody["bindings_matched"] == 21
    assert custody["all_matched"] is True
    assert custody["failures"] == []


@pytest.mark.parametrize(
    ("mutation", "expected_failure"),
    [
        (
            {"bindings_checked": 9999, "bindings_matched": 9999},
            "receipt cannot have checked more bindings than exist",
        ),
        (
            {"bindings_matched": 20},
            "receipt checked and matched the same number of bindings",
        ),
    ],
)
def test_a_lying_receipt_is_still_caught(
    mutation: dict, expected_failure: str, tmp_path: Path
) -> None:
    """The replacement must lose no detection power against a tampered receipt."""

    original = RECEIPT.read_bytes()
    payload = json.loads(original.decode("utf-8"))
    payload["facts"]["custody"].update(mutation)
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        result = _run()
        assert "CHECK FAILED" in result.stdout, result.stdout
        assert expected_failure in result.stdout, result.stdout
    finally:
        RECEIPT.write_bytes(original)

    # The tree must be exactly as it was, or this test has broken the repository.
    assert RECEIPT.read_bytes() == original
    assert "CHECK PASSED" in _run().stdout
