"""P1 must declare a terminal the scoreboard can read.

An unparseable terminal is not a neutral state. The scoreboard is the one place
the programme reads readiness from, and a paper it cannot score is absent from
it rather than cautious in it.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P1 = ROOT / "papers/paper-01-recursive-epistemic-reconstruction/JOURNAL_READINESS.md"
PEER_REVIEW_READY_TOKEN = re.compile(r"PEER_REVIEW_READY(?![A-Za-z0-9_])")


def _scoreboard() -> dict:
    import json

    out = subprocess.run(
        [sys.executable, str(ROOT / "research/publication/scoreboard.py")],
        capture_output=True, text=True, cwd=ROOT, check=False,
    )
    return json.loads(out.stdout)


def test_p1_declares_a_scorable_terminal() -> None:
    record = next(p for p in _scoreboard()["papers"] if p["paper_id"] == "P1")
    assert record["journal_readiness_terminal"] is not None
    assert record["journal_readiness_terminal"] in {"PEER_REVIEW_READY", "CANNOT_CHECK"}


def test_p1_carries_no_stale_peer_review_ready_authority() -> None:
    assert PEER_REVIEW_READY_TOKEN.search(P1.read_text()) is None


def test_p1_blockers_are_enumerated_rather_than_the_paper_being_absent() -> None:
    record = next(p for p in _scoreboard()["papers"] if p["paper_id"] == "P1")
    assert record["missing_artifacts"], "a blocked paper must name its blockers"
    assert "unparseable" not in " ".join(record["missing_artifacts"])
