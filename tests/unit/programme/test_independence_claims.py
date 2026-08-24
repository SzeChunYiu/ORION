"""No paper may call a shared public substrate an independent validation."""

from __future__ import annotations

from pathlib import Path

from orion.programme.portfolio_integrity import (
    EXIT_CANNOT_CHECK,
    EXIT_PASS,
    EXIT_SHARED_SUBSTRATE_CLAIM,
    audit_repository_independence_claims,
    classify_independence_occurrence,
    independence_claim_occurrences,
)


def _paper(tmp_path: Path, text: str) -> Path:
    d = tmp_path / "papers" / "paper-99-fake"
    d.mkdir(parents=True)
    (d / "MANUSCRIPT.md").write_text(text)
    return tmp_path


def test_affirmed_claim_is_a_violation(tmp_path: Path) -> None:
    root = _paper(tmp_path, "This constitutes independent validation of the result.\n")
    audit = audit_repository_independence_claims(root)
    assert audit.exit_code == EXIT_SHARED_SUBSTRATE_CLAIM


def test_disclaimer_is_not_a_violation(tmp_path: Path) -> None:
    """The regression that would make this checker worse than nothing.

    P14 writes "rather than independent validation" and P15 records
    ``CANNOT_CHECK`` pending it. Both are the honest thing to do.
    """
    root = _paper(
        tmp_path,
        "We treat it as an internal result rather than independent validation.\n",
    )
    assert audit_repository_independence_claims(root).exit_code == EXIT_PASS


def test_pending_is_not_a_claim(tmp_path: Path) -> None:
    root = _paper(tmp_path, "Authority: CANNOT_CHECK pending external independent validation.\n")
    assert audit_repository_independence_claims(root).exit_code == EXIT_PASS


def test_missing_tree_is_not_a_pass(tmp_path: Path) -> None:
    audit = audit_repository_independence_claims(tmp_path / "absent")
    assert audit.exit_code == EXIT_CANNOT_CHECK
    assert audit.exit_code != EXIT_PASS


def test_classifier_reads_the_preceding_window() -> None:
    text = "a result rather than independent validation"
    assert classify_independence_occurrence(text, text.index("independent")) == "NEGATED"
    text2 = "we provide independent validation"
    assert classify_independence_occurrence(text2, text2.index("independent")) == "AFFIRMED"


def test_live_repository_makes_no_affirmed_independence_claim() -> None:
    occurrences = independence_claim_occurrences()
    assert occurrences, "markers must be findable, or the audit proves nothing"
    assert [o for o in occurrences if o["verdict"] == "AFFIRMED"] == []
    assert audit_repository_independence_claims().exit_code == EXIT_PASS
