"""P7 may only cite sources it has actually retrieved.

Section 2.3 of the P7 manuscript opened with a claim about a body of work --
"Planning research has long shown that representation and abstraction affect
solvability, search complexity and solution preservation" -- and cited nothing.
That is a desk-reject independent of whether P7's own contribution is novel: a
reviewer need not dispute the contribution to object that a related-work section
characterises a field without a reference.

The fix is not simply "add citations". It is to keep citations bound to
retrieval, so a name in the manuscript always corresponds to a source someone
actually opened. These tests enforce that direction: a record may exist without
being cited (it is a lead), but nothing may be cited without a `VERIFIED` record.

The asymmetry is deliberate. Promoting `UNVERIFIED_SECONDARY` to `VERIFIED`
requires retrieving the primary source, so the only way to make a new citation
legal is to do the work.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P7 = ROOT / "papers" / "orion-17-epistemic-navigation-open-worlds"
LITERATURE = P7 / "evidence" / "literature"
MANUSCRIPT = P7 / "manuscript" / "FINAL.md"

VALID_VERDICTS = {"VERIFIED", "UNVERIFIED_SECONDARY"}
#: `[Author 1994]` -- the convention P7 introduces, since no candidate paper had one.
CITATION = re.compile(r"\[([A-Z][A-Za-z]+)\s+(\d{4})\]")


def _records() -> dict[str, dict]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(LITERATURE.glob("*.json"))
    }


def test_every_record_declares_how_it_was_checked() -> None:
    records = _records()
    assert records, "P7 has no literature records at all"
    for key, record in records.items():
        assert record["bib_key"] == key, f"{key}: bib_key disagrees with filename"
        assert record["verdict"] in VALID_VERDICTS, (
            f"{key}: unknown verdict {record['verdict']!r}. A new verdict must be added "
            f"here deliberately, so that an unrecognised one cannot pass as verified."
        )
        assert record.get("verdict_reason"), f"{key}: verdict with no stated reason"
        if record["verdict"] == "VERIFIED":
            assert record.get("fetched_utc"), f"{key}: VERIFIED without a retrieval time"
            assert record.get("fetched_title"), f"{key}: VERIFIED without a fetched title"
        else:
            assert record.get("promotion_requires"), (
                f"{key}: an unverified record must say what would verify it, or it is "
                f"just a note that will never be actioned"
            )


def test_the_manuscript_only_cites_verified_records() -> None:
    """The load-bearing direction: no citation without retrieval."""

    records = _records()
    verified = {
        key for key, record in records.items() if record["verdict"] == "VERIFIED"
    }
    text = MANUSCRIPT.read_text(encoding="utf-8")

    cited = {f"{author.lower()}{year}" for author, year in CITATION.findall(text)}
    if not cited:
        return  # nothing cited yet is a legal state; nothing unbacked is cited

    unbacked = sorted(
        key
        for key in cited
        if not any(v.startswith(key) or key.startswith(v[:12]) for v in verified)
    )
    assert not unbacked, (
        f"manuscript cites {unbacked} with no VERIFIED record under "
        f"evidence/literature/. Verified records available: {sorted(verified)}"
    )


def test_the_section_that_prompted_this_now_carries_a_citation() -> None:
    """Guard the specific gap, so it cannot silently reopen.

    Section 2.3 makes an explicit claim about what planning research has shown. If
    that sentence survives while its citation is removed, the paper is back to
    asserting a literature it does not reference.
    """

    text = MANUSCRIPT.read_text(encoding="utf-8")
    assert "### 2.3 Planning abstraction and representation change" in text
    section = text.split("### 2.3 Planning abstraction and representation change", 1)[1]
    section = section.split("### 2.4", 1)[0]

    assert "Planning research has long shown" in section, (
        "the claim moved or was reworded; update this test to track it"
    )
    assert CITATION.search(section), (
        "section 2.3 claims what planning research has shown and cites nobody"
    )
    # The negative result must stay visible: a related-work section that cites only
    # the favourable half of a field is not a survey.
    assert "exponentially worse" in section, (
        "the counterweight is gone; 2.3 would again read as though abstraction is "
        "uniformly beneficial"
    )
