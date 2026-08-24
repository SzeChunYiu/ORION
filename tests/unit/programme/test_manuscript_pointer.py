"""A README that names a superseded manuscript sends every reader to it."""

from __future__ import annotations

from pathlib import Path

from orion.programme.manuscript_pointer import (
    EXIT_CANNOT_CHECK,
    EXIT_DISAGREE,
    EXIT_PASS,
    audit_repository,
    main,
)

POINTER = "**Current science manuscript:** `manuscript/{}`.\n"


def _paper(tmp_path: Path, readme_target: str, ledgers: dict[str, str | None]) -> Path:
    d = tmp_path / "papers" / "paper-99-fake"
    d.mkdir(parents=True)
    (d / "README.md").write_text("# P99\n\n" + POINTER.format(readme_target))
    for name, target in ledgers.items():
        body = "# ledger\n\n" + (POINTER.format(target) if target else "no pointer here\n")
        (d / name).write_text(body)
    return tmp_path


def test_matching_pointers_pass(tmp_path: Path) -> None:
    root = _paper(tmp_path, "FINAL_V5.md", {"CLAIM_LEDGER_V4.md": "FINAL_V5.md"})
    assert main(["--root", str(root)]) == EXIT_PASS


def test_a_readme_naming_a_superseded_manuscript_disagrees(tmp_path: Path) -> None:
    """P6's live case: README on V4, ledger and main.tex on V5."""
    root = _paper(tmp_path, "FINAL_V4.md", {"CLAIM_LEDGER_V4.md": "FINAL_V5.md"})
    assert main(["--root", str(root)]) == EXIT_DISAGREE


def test_pointer_from_a_superseded_ledger_cannot_adjudicate(tmp_path: Path) -> None:
    """P4's live case: the newest ledger has no pointer, an older one does.

    Falling back to the older pointer reports a disagreement with a document the
    paper itself calls the preserved pre-ascent record -- a finding manufactured
    entirely by the reader's choice of file.
    """
    root = _paper(
        tmp_path,
        "main.tex",
        {"CLAIM_LEDGER_V3.md": "FINAL_V3.md", "CLAIM_LEDGER_V4.md": None},
    )
    assert main(["--root", str(root)]) == EXIT_CANNOT_CHECK
    rec = audit_repository(root)[0]
    assert rec.state == "STALE_LEDGER_ONLY"
    assert "CLAIM_LEDGER_V4.md is newer" in rec.note


def test_ledger_versions_order_numerically(tmp_path: Path) -> None:
    """V10 sorts before V9 alphabetically, so the newest would stop being read."""
    root = _paper(
        tmp_path,
        "FINAL_V10.md",
        {"CLAIM_LEDGER_V9.md": "FINAL_V9.md", "CLAIM_LEDGER_V10.md": "FINAL_V10.md"},
    )
    assert main(["--root", str(root)]) == EXIT_PASS


def test_live_repository_has_no_disagreement() -> None:
    """P6 and P7 were both repointed; this fails if either regresses."""
    bad = [r.paper for r in audit_repository() if r.state == "DISAGREE"]
    assert not bad, bad
