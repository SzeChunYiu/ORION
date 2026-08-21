"""State-aware publication guard for ORION P11-P14.

The original #715-era tests assumed all four directories must remain empty
placeholders forever. Canonical paper PRs #771-#774 supersede that ownership one
paper at a time. This guard preserves the useful invariant without treating
publication progress as a failure.
"""

from pathlib import Path

from orion.programme.superiority_terminals import FUTURE_PAPER_DIRECTORIES

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_p11_to_p14_are_either_honest_placeholders_or_complete_canonical_packages() -> None:
    for paper_id, directory in FUTURE_PAPER_DIRECTORIES.items():
        root = REPO_ROOT / directory
        assert root.is_dir(), f"{paper_id} has no directory at {directory}"

        readme = root / "README.md"
        assert readme.is_file(), f"{paper_id} has no README"
        text = readme.read_text(encoding="utf-8")
        assert f"ORION-{paper_id}" in text

        manuscript = root / "MANUSCRIPT.md"
        placeholder = "NO_PROTECTED_RESULT" in text
        if placeholder:
            assert not manuscript.exists(), (
                f"{paper_id} says NO_PROTECTED_RESULT but already has MANUSCRIPT.md"
            )
            continue

        assert manuscript.is_file(), (
            f"{paper_id} left placeholder mode without a canonical manuscript"
        )
        assert (root / "CLAIM_EVIDENCE_LEDGER.md").is_file(), (
            f"{paper_id} canonical package lacks claim/evidence ledger"
        )
        readiness = root / "PEER_REVIEW_READINESS.md"
        assert readiness.is_file(), f"{paper_id} canonical package lacks readiness report"
        readiness_text = readiness.read_text(encoding="utf-8")
        assert "READY_FOR_EXTERNAL_REVIEW" in readiness_text, (
            f"{paper_id} canonical package lacks an explicit external-review decision"
        )


def test_draft_715_no_longer_has_exclusive_manuscript_ownership_after_canonical_transition() -> None:
    transitioned = []
    for paper_id, directory in FUTURE_PAPER_DIRECTORIES.items():
        root = REPO_ROOT / directory
        if (root / "MANUSCRIPT.md").is_file():
            transitioned.append(paper_id)
            assert "NO_PROTECTED_RESULT" not in (root / "README.md").read_text(encoding="utf-8")

    # On a canonical paper PR at least that paper must have transitioned. On the
    # eventual merged programme all four will satisfy the same invariant.
    assert transitioned, "publication-transition guard installed without any canonical paper"
