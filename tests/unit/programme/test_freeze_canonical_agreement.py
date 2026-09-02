"""Guard: a CANONICAL_* decision file and the newest freeze addendum must
name the same canonical manuscript/ledger (authority-surface drift class,
ORION-paper issue #78 cross-cutting sweep)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "check_freeze_canonical_agreement_v1.py"


def run_script(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_repo_freeze_canonical_agreement() -> None:
    """The real repo tree must be drift-free."""
    result = run_script(REPO)
    assert result.returncode == 0, (
        f"freeze/canonical drift:\n{result.stderr}\n{result.stdout}"
    )
    assert "FREEZE_CANONICAL_AGREEMENT_OK" in result.stdout


def write_surfaces(paper: Path, *, canonical: str, addendum: str) -> None:
    paper.mkdir(parents=True)
    for token in ("MANUSCRIPT_V2.md", "MANUSCRIPT_V4.md",
                  "CLAIM_LEDGER_V2.md", "CLAIM_LEDGER_V4.md"):
        (paper / token).write_text(f"# {token}\n", encoding="utf-8")
    (paper / "CANONICAL_SUBMISSION_V4.md").write_text(canonical, encoding="utf-8")
    (paper / "PUBLICATION_FREEZE_ADDENDUM_V1.md").write_text(addendum, encoding="utf-8")


def test_checker_detects_the_drift_class(tmp_path: Path) -> None:
    """Canonical designates V4 while the addendum freezes V2 -> exit 1.

    This is the exact 2026-09-02 orion-01/orion-02 drift shape; a checker
    that cannot catch it on a minimal synthetic tree cannot be trusted on
    the real one.
    """
    paper = tmp_path / "papers" / "orion-99-synthetic"
    write_surfaces(
        paper,
        canonical=(
            "# canonical V4\n\n`MANUSCRIPT_V4.md` is the only manuscript "
            "authorized. The live claim ledger is `CLAIM_LEDGER_V4.md`. "
            "`MANUSCRIPT_V2.md` remains superseded historical evidence.\n"
        ),
        addendum=(
            "# addendum V1\n\nThe frozen content surface is "
            "`MANUSCRIPT_V2.md` + `CLAIM_LEDGER_V2.md`.\n"
        ),
    )
    result = run_script(tmp_path)
    assert result.returncode == 1
    assert "MANUSCRIPT_V4.md" in result.stderr
    assert "CLAIM_LEDGER_V4.md" in result.stderr


def test_checker_passes_the_synced_successor(tmp_path: Path) -> None:
    """Addendum successor naming the designated V4 surface -> exit 0."""
    paper = tmp_path / "papers" / "orion-99-synthetic"
    write_surfaces(
        paper,
        canonical=(
            "# canonical V4\n\n`MANUSCRIPT_V4.md` is the only manuscript "
            "authorized. The live claim ledger is `CLAIM_LEDGER_V4.md`.\n"
        ),
        addendum=(
            "# addendum V1\n\nThe frozen content surface is "
            "`MANUSCRIPT_V4.md` + `CLAIM_LEDGER_V4.md`.\n"
        ),
    )
    result = run_script(tmp_path)
    assert result.returncode == 0, result.stderr


def test_checker_flags_dangling_frozen_token(tmp_path: Path) -> None:
    """An addendum freezing a token that no longer exists -> exit 1."""
    paper = tmp_path / "papers" / "orion-99-synthetic"
    write_surfaces(
        paper,
        canonical=(
            "# canonical V4\n\n`MANUSCRIPT_V4.md` is the only manuscript "
            "authorized. The live claim ledger is `CLAIM_LEDGER_V4.md`.\n"
        ),
        addendum=(
            "# addendum V1\n\nThe frozen content surface is "
            "`MANUSCRIPT_V4.md` + `CLAIM_LEDGER_V4.md`; the historical "
            "`CLAIM_LEDGER_V2.md` and the removed `MANUSCRIPT_V1.md` "
            "remain records.\n"
        ),
    )
    result = run_script(tmp_path)
    assert result.returncode == 1
    assert "MANUSCRIPT_V1.md" in result.stderr
