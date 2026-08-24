"""Superseded authority records cited as current.

The auditor's job is to separate three things that all mention an old record:
an inventory listing it, a history section preserving it, and a surface
declaring it current. Only the third is stale, and the tests below are mostly
about the first two not being flagged -- a staleness auditor that fires on
changelogs gets switched off within a day.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from orion.programme.authority_staleness import (
    EXIT_CANNOT_CHECK,
    EXIT_PASS,
    EXIT_STALE_CITATION,
    audit_repository,
    authority_chains,
)


def _paper(tmp_path: Path, name: str, versions: list[int]) -> Path:
    d = tmp_path / "papers" / name
    d.mkdir(parents=True, exist_ok=True)
    for v in versions:
        (d / f"P99_ACTIVE_CLAIM_AUTHORITY_V{v}.json").write_text("{}", encoding="utf-8")
    return d


def test_the_chain_head_is_the_highest_version(tmp_path):
    _paper(tmp_path, "paper-99", [1, 2, 3])
    chains = authority_chains(tmp_path / "papers")
    c = chains["paper-99"]
    assert c["active"] == "P99_ACTIVE_CLAIM_AUTHORITY_V3.json"
    assert len(c["superseded"]) == 2


def test_version_order_is_numeric_not_lexical(tmp_path):
    """V10 succeeds V9; string ordering would put V10 first."""

    _paper(tmp_path, "paper-99", [9, 10])
    assert authority_chains(tmp_path / "papers")["paper-99"]["active"].endswith("V10.json")


def test_a_single_record_is_not_a_chain(tmp_path):
    _paper(tmp_path, "paper-99", [1])
    assert audit_repository(tmp_path).exit_code == EXIT_PASS


def test_declaring_a_superseded_record_active_is_caught(tmp_path):
    d = _paper(tmp_path, "paper-99", [1, 2])
    (d / "LEDGER.md").write_text(
        "**Active authority:** `P99_ACTIVE_CLAIM_AUTHORITY_V1.json`\n", encoding="utf-8"
    )
    report = audit_repository(tmp_path)
    assert report.exit_code == EXIT_STALE_CITATION
    assert "V1" in report.problems[0]


def test_declaring_the_active_record_active_is_fine(tmp_path):
    d = _paper(tmp_path, "paper-99", [1, 2])
    (d / "LEDGER.md").write_text(
        "**Active authority:** `P99_ACTIVE_CLAIM_AUTHORITY_V2.json`\n", encoding="utf-8"
    )
    assert audit_repository(tmp_path).exit_code == EXIT_PASS


# --- the three things that must NOT be flagged ----------------------------


def test_a_history_section_naming_an_old_record_is_not_stale(tmp_path):
    """A paper must be able to say what it superseded."""

    d = _paper(tmp_path, "paper-99", [1, 2])
    (d / "README.md").write_text(
        "Lifecycle records are preserved: `P99_ACTIVE_CLAIM_AUTHORITY_V1.json` "
        "was the state before the successor landed.\n",
        encoding="utf-8",
    )
    assert audit_repository(tmp_path).exit_code == EXIT_PASS


def test_an_explicit_supersession_note_is_not_stale(tmp_path):
    d = _paper(tmp_path, "paper-99", [1, 2])
    (d / "NOTES.md").write_text(
        "The current authority supersedes `P99_ACTIVE_CLAIM_AUTHORITY_V1.json`.\n",
        encoding="utf-8",
    )
    assert audit_repository(tmp_path).exit_code == EXIT_PASS


def test_a_content_manifest_listing_every_file_is_not_a_claim(tmp_path):
    """An inventory enumerates paths by design; that is not a currency claim."""

    d = _paper(tmp_path, "paper-99", [1, 2])
    (d / "CONTENT_MANIFEST_V1.json").write_text(
        '{"active authority": "papers/paper-99/P99_ACTIVE_CLAIM_AUTHORITY_V1.json"}',
        encoding="utf-8",
    )
    assert audit_repository(tmp_path).exit_code == EXIT_PASS


def test_a_record_naming_itself_is_not_a_citation(tmp_path):
    d = _paper(tmp_path, "paper-99", [1, 2])
    (d / "P99_ACTIVE_CLAIM_AUTHORITY_V1.json").write_text(
        '{"note": "active authority P99_ACTIVE_CLAIM_AUTHORITY_V1.json"}', encoding="utf-8"
    )
    assert audit_repository(tmp_path).exit_code == EXIT_PASS


def test_a_distant_mention_of_current_does_not_make_a_claim(tmp_path):
    """The marker must precede the reference closely, not sit paragraphs away."""

    d = _paper(tmp_path, "paper-99", [1, 2])
    (d / "LONG.md").write_text(
        "The current authority is discussed below.\n" + ("filler text. " * 40) +
        "\nSee also `P99_ACTIVE_CLAIM_AUTHORITY_V1.json` in the appendix.\n",
        encoding="utf-8",
    )
    assert audit_repository(tmp_path).exit_code == EXIT_PASS


def test_two_conflicting_active_declarations_are_both_caught(tmp_path):
    """The shape actually found in P15's ledger."""

    d = _paper(tmp_path, "paper-99", [1, 2, 3])
    (d / "LEDGER.md").write_text(
        "**Active authority:** `P99_ACTIVE_CLAIM_AUTHORITY_V2.json`\n\n"
        "**Active authority:** `P99_ACTIVE_CLAIM_AUTHORITY_V1.json`\n",
        encoding="utf-8",
    )
    report = audit_repository(tmp_path)
    assert report.exit_code == EXIT_STALE_CITATION
    assert len(report.problems) == 2


def test_no_papers_directory_cannot_be_checked(tmp_path):
    assert audit_repository(tmp_path).exit_code == EXIT_CANNOT_CHECK


def test_each_outcome_has_its_own_exit_code():
    assert len({EXIT_PASS, EXIT_STALE_CITATION, EXIT_CANNOT_CHECK}) == 3
