"""The two readiness files per candidate must not contradict each other.

Each of P6, P7 and P8 carries `JOURNAL_READINESS.md` and
`JOURNAL_READINESS_V2_1.md`. The V2.1 file says the peer-review terminal is
"computed by ../../PEER_REVIEW_READY_PACKAGE.md from exact-head GitHub checks".
The older file asserted a flat `CANNOT_CHECK / not a promoted paper / not
peer-review ready`, written before the submission package existed.

Both statements were sincere when written and they stopped being compatible. A
reader consulting one file got a different answer than a reader consulting the
other, and nothing failed.

Two rules are pinned, and the second matters more than the first:

1. no readiness file may assert a flat terminal that the package computes;
2. no readiness file may hard-code `PEER_REVIEW_READY` either.

The second is the one that stops this being a way to promote a paper by editing
a sentence. The package file says it "does not hard-code a claim that could
become stale after a content edit"; storing the favourable answer would be the
same defect as storing the unfavourable one, just in the direction nobody
complains about.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CANDIDATES = ROOT / "papers" / "candidates"
PAPERS = {
    "P6": "orion-16-formal-epistemic-structures-and-mechanics",
    "P7": "orion-17-epistemic-navigation-open-worlds",
    "P8": "orion-18-epistemic-authority-autonomous-science",
}
PACKAGE = CANDIDATES / "PEER_REVIEW_READY_PACKAGE.md"

#: `PEER_REVIEW_READY` as a whole token, so `PEER_REVIEW_READY_PACKAGE.md` and
#: `PEER_REVIEW_READY_GATE_...` -- which are filenames, not claims -- do not match.
READY_TOKEN = re.compile(r"PEER_REVIEW_READY(?![A-Za-z0-9_.])")
STALE_TERMINAL = "**Current terminal:** `CANNOT_CHECK`"


def _readiness_files(paper: str) -> list[Path]:
    return sorted((ROOT / "papers" / PAPERS[paper]).glob("JOURNAL_READINESS*.md"))


@pytest.mark.parametrize("paper", sorted(PAPERS))
def test_no_readiness_file_asserts_a_stale_flat_terminal(paper: str) -> None:
    """The contradiction that prompted this."""

    for path in _readiness_files(paper):
        text = path.read_text(encoding="utf-8")
        assert STALE_TERMINAL not in text, (
            f"{paper} {path.name} asserts a flat CANNOT_CHECK terminal while "
            f"PEER_REVIEW_READY_PACKAGE.md computes it per commit; the two files "
            f"in this directory then disagree"
        )


@pytest.mark.parametrize("paper", sorted(PAPERS))
def test_no_readiness_file_hard_codes_the_favourable_terminal(paper: str) -> None:
    """The direction nobody complains about, which is why it needs a test.

    Storing PEER_REVIEW_READY is the same defect as storing CANNOT_CHECK: a claim
    that outlives the commit it was true for. A sentence must not be able to
    promote a paper.
    """

    for path in _readiness_files(paper):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip().startswith(("**Current terminal:**", "**Terminal:**")):
                continue
            assert not READY_TOKEN.search(line), (
                f"{paper} {path.name}:{lineno} hard-codes PEER_REVIEW_READY on a "
                f"terminal line. The terminal is computed from CI on an exact head; "
                f"record the observation and its commit instead."
            )


@pytest.mark.parametrize("paper", sorted(PAPERS))
def test_each_paper_points_at_the_computation(paper: str) -> None:
    """A file that neither asserts nor delegates leaves the reader with nothing."""

    texts = [path.read_text(encoding="utf-8") for path in _readiness_files(paper)]
    assert texts, f"{paper} has no readiness file at all"
    assert any("PEER_REVIEW_READY_PACKAGE.md" in text for text in texts), (
        f"{paper} has readiness files but none refers to the package that computes "
        f"the terminal"
    )


def test_the_package_still_defines_the_predicate_these_files_defer_to() -> None:
    """Guard the target of the delegation, not only the delegation."""

    text = PACKAGE.read_text(encoding="utf-8")
    assert "p6-p8-candidate-ci" in text and "ci ==" in text, (
        "PEER_REVIEW_READY_PACKAGE.md no longer states the CI predicates the "
        "readiness files defer to"
    )
    assert "does not hard-code" in text, (
        "the package dropped its own statement that it does not hard-code a "
        "terminal; that sentence is why the readiness files delegate"
    )
