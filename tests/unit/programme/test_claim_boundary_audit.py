"""Three Definition-of-done properties, and proof the scan that clears one can see.

A bypass-claim scan that returns zero is worthless unless it is shown to catch a
real bypass claim, so the decisive test here plants one in a temporary tree and
asserts it is found. The rest break the real records.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.programme.claim_boundary_audit import (
    BYPASS_LEXICON,
    EXCLUDED_EVIDENCE_MARKERS,
    EXIT_BYPASS_CLAIM,
    EXIT_PASS,
    EXIT_RETENTION,
    EXIT_SILENT_RETUNING,
    audit_cannot_check_retention,
    audit_negative_revival,
    run_audit,
    scan_bypass_claims,
)

P5 = "papers/orion-15-self-orion/evidence/CLAIM_LEDGER_V1.json"
P10 = "papers/orion-20-structured-problem-solving/P10_ACTIVE_CLAIM_AUTHORITY_V1.json"
BACKLOG = "research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.json"


def _root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / P5).is_file():
            return parent
    pytest.skip("repository root not found")


@pytest.fixture(scope="module")
def root() -> Path:
    return _root()


@pytest.fixture(scope="module")
def records(root: Path):
    load = lambda rel: json.loads((root / rel).read_text(encoding="utf-8"))
    return load(P5), load(P10), load(BACKLOG)


# --- the whole audit ------------------------------------------------------


def test_the_real_tree_passes(root):
    audit = run_audit(root)
    assert audit.exit_code == EXIT_PASS, audit.problems


# --- P5 / P10 retain CANNOT_CHECK ----------------------------------------


def test_p5_and_p10_currently_retain_cannot_check(records):
    p5, p10, _ = records
    problems, detail = audit_cannot_check_retention(p5, p10)
    assert problems == []
    assert p5["empirical_authority"] == "CANNOT_CHECK"
    assert p10["active_empirical_claim"] is None
    assert any("P5" in line for line in detail)


def test_a_promoted_p5_authority_is_refused(records):
    p5, p10, _ = records
    mutated = copy.deepcopy(p5)
    mutated["empirical_authority"] = "PASS"
    problems, _ = audit_cannot_check_retention(mutated, p10)
    assert any("empirical_authority" in problem for problem in problems)


def test_p5_marked_peer_review_ready_while_cannot_check_is_refused(records):
    p5, p10, _ = records
    mutated = copy.deepcopy(p5)
    mutated["peer_review_ready"] = True
    problems, _ = audit_cannot_check_retention(mutated, p10)
    assert any("peer_review_ready" in problem for problem in problems)


def test_p10_carrying_an_active_empirical_claim_is_refused(records):
    p5, p10, _ = records
    mutated = copy.deepcopy(p10)
    mutated["active_empirical_claim"] = "P10_SUPERIORITY_SUPPORTED"
    problems, _ = audit_cannot_check_retention(p5, mutated)
    assert any("active empirical claim" in problem for problem in problems)


def test_p10_allowing_promotion_is_refused(records):
    p5, p10, _ = records
    mutated = copy.deepcopy(p10)
    mutated["promotion_allowed"] = True
    problems, _ = audit_cannot_check_retention(p5, mutated)
    assert any("promotion" in problem for problem in problems)


# --- no silent retuning ---------------------------------------------------


def test_the_backlog_records_revived_negatives_with_successors(records):
    _, _, backlog = records
    problems, detail = audit_negative_revival(backlog)
    assert problems == []
    assert len(backlog["already_revived"]) >= 1
    assert all(entry.get("successor") for entry in backlog["already_revived"])
    assert any("revived negatives" in line for line in detail)


def test_a_revived_negative_without_a_successor_is_refused(records):
    """A status change with nothing named to replace it is silent retuning."""

    _, _, backlog = records
    mutated = copy.deepcopy(backlog)
    mutated["already_revived"][0]["successor"] = ""
    problems, _ = audit_negative_revival(mutated)
    assert any("silent retuning" in problem for problem in problems)


def test_a_protected_negative_that_permits_repair_is_refused(records):
    _, _, backlog = records
    mutated = copy.deepcopy(backlog)
    mutated["protected_negatives"][0]["reason"] = "we may revisit this later"
    problems, _ = audit_negative_revival(mutated)
    assert any("forbid repair" in problem for problem in problems)


def test_removing_the_anti_tuning_directive_is_refused(records):
    _, _, backlog = records
    mutated = copy.deepcopy(backlog)
    mutated["operator_directive"] = ""
    problems, _ = audit_negative_revival(mutated)
    assert any("directive" in problem for problem in problems)


def test_the_directive_forbids_tuning_outcomes(records):
    _, _, backlog = records
    assert "never by tuning outcomes" in backlog["operator_directive"].lower()


# --- no bypass claims -----------------------------------------------------


def test_the_real_paper_tree_carries_no_bypass_claim(root):
    violations, detail = scan_bypass_claims(root)
    assert violations == [], violations
    assert any("files scanned" in line for line in detail)


def test_the_scan_actually_finds_a_planted_bypass_claim(tmp_path):
    """The decisive test: a zero result is meaningless if the scan cannot see."""

    papers = tmp_path / "papers" / "paper-99"
    papers.mkdir(parents=True)
    (papers / "CLAIM_LEDGER.md").write_text(
        "Our same-owner CI run establishes independent adjudication of the result.\n",
        encoding="utf-8",
    )
    violations, _ = scan_bypass_claims(tmp_path)
    assert len(violations) == 1
    assert "paper-99" in violations[0]


@pytest.mark.parametrize(
    "sentence",
    [
        "This does not establish independent adjudication.",
        "No local hash constitutes independent confirmation.",
        "A route counts as independent only from content/provenance evidence, not tool naming.",
        "We treat replay as evidence about execution rather than a substitute for independent validity.",
    ],
)
def test_boundary_and_restriction_statements_are_not_flagged(tmp_path, sentence):
    """The corpus is full of these; flagging them would switch the scan off."""

    papers = tmp_path / "papers" / "paper-99"
    papers.mkdir(parents=True)
    (papers / "notes.md").write_text(sentence + "\n", encoding="utf-8")
    violations, _ = scan_bypass_claims(tmp_path)
    assert violations == []


def test_retrieved_corpus_rows_are_excluded_and_the_exclusion_is_reported(tmp_path):
    """A third-party paper title is data the system fetched, not a claim it makes."""

    evidence = tmp_path / "papers" / "paper-02" / "evidence" / "offline_results"
    evidence.mkdir(parents=True)
    (evidence / "candidates_x.jsonl").write_text(
        '{"title": "A cAMP analogue demonstrates independent regulation of Rap1"}\n',
        encoding="utf-8",
    )
    violations, detail = scan_bypass_claims(tmp_path)
    assert violations == []
    assert any("excluded" in line for line in detail)


def test_the_lexicon_and_exclusions_are_closed_and_non_empty():
    assert len(BYPASS_LEXICON) >= 10
    assert all(phrase == phrase.lower() for phrase in BYPASS_LEXICON)
    assert EXCLUDED_EVIDENCE_MARKERS


# --- exit codes are distinct ---------------------------------------------


def test_each_failure_mode_has_its_own_exit_code():
    assert len({EXIT_PASS, EXIT_RETENTION, EXIT_SILENT_RETUNING, EXIT_BYPASS_CLAIM}) == 4
