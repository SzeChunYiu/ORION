"""P1-P4 may not claim a 75+ score before their external gates pass."""

from __future__ import annotations

from pathlib import Path

from orion.programme.publication_score_gate import (
    EXIT_CANNOT_CHECK,
    EXIT_PASS,
    EXIT_UNGATED_CLAIM,
    audit_repository,
    main,
)


def _paper(tmp_path: Path, doc: str, gate: str | None = None) -> Path:
    # Must be one of publication_score_gate.GATED_PAPERS. With a name outside
    # that set the checker skips the directory, scans nothing and returns PASS,
    # so every expectation in this file would hold vacuously.
    d = tmp_path / "papers" / "orion-11-fake"
    d.mkdir(parents=True, exist_ok=True)
    (d / "READINESS.md").write_text(doc)
    if gate:
        (d / "GATE.json").write_text(gate)
    return tmp_path


def test_a_score_claim_without_gate_evidence_fails(tmp_path: Path) -> None:
    root = _paper(tmp_path, "# P1\n\nPublication score: 82. Ready for submission.\n")
    assert main(["--root", str(root)]) == EXIT_UNGATED_CLAIM


def test_the_same_claim_passes_once_the_gate_is_evidenced(tmp_path: Path) -> None:
    root = _paper(tmp_path, "# P1\n\nPublication score: 82.\n", '{"gate_passed": true}\n')
    assert main(["--root", str(root)]) == EXIT_PASS


def test_the_rules_own_wording_is_not_a_violation(tmp_path: Path) -> None:
    """P10 says it "cannot reach 75 until H1-H6 execute". That is the rule
    being obeyed. A checker that flagged it would punish compliance."""
    root = _paper(tmp_path, "# P1\n\nThis paper cannot reach 75 until H1-H6 execute.\n")
    assert main(["--root", str(root)]) == EXIT_PASS


def test_a_target_is_not_an_achievement(tmp_path: Path) -> None:
    root = _paper(tmp_path, "# P1\n\nThe target score is 75; we are not yet there.\n")
    assert main(["--root", str(root)]) == EXIT_PASS


def test_silence_passes(tmp_path: Path) -> None:
    root = _paper(tmp_path, "# P1\n\nNo score is claimed anywhere in this document.\n")
    assert main(["--root", str(root)]) == EXIT_PASS


def test_a_score_below_the_bar_is_not_gated(tmp_path: Path) -> None:
    root = _paper(tmp_path, "# P1\n\nPublication score: 60.\n")
    assert main(["--root", str(root)]) == EXIT_PASS


def test_missing_tree_is_not_a_pass(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path / "absent")]) == EXIT_CANNOT_CHECK


def test_live_repository_makes_no_ungated_claim() -> None:
    report = audit_repository()
    assert report.papers_scanned > 0
    assert report.documents_scanned > 0
    assert report.ungated == []
