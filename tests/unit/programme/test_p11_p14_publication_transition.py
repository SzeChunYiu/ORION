"""State-aware publication guard for ORION P11-P14.

The original #715-era tests assumed all four directories must remain empty
placeholders forever. Canonical paper PRs #771-#774 supersede that ownership one
paper at a time. This guard preserves the useful invariant without treating
publication progress as a failure.
"""

from pathlib import Path

from orion.programme.superiority_terminals import FUTURE_PAPER_DIRECTORIES

REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER_IDS = ("P11", "P12", "P13", "P14")

EXPECTED_READY_DECISIONS = {
    "P11": "READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_SUPERIORITY_RESULT",
    "P12": "READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_MATCHED-BUDGET_SUPERIORITY_RESULT",
    "P13": "READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_RESPONSIBILITY-SAFE-REUSE_RESULT",
    "P14": "READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT",
}


def test_p11_to_p14_are_either_honest_placeholders_or_complete_canonical_packages() -> None:
    for paper_id in PAPER_IDS:
        directory = FUTURE_PAPER_DIRECTORIES[paper_id]
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
        decision_lines = [
            line.strip()
            for line in readiness.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith("**Decision:**")
        ]
        expected = f"**Decision:** `{EXPECTED_READY_DECISIONS[paper_id]}`"
        assert decision_lines == [expected], (
            f"{paper_id} canonical package lacks the exact external-review decision: "
            f"expected {expected!r}, got {decision_lines!r}"
        )


def test_draft_715_no_longer_has_exclusive_manuscript_ownership_after_canonical_transition() -> None:
    transitioned = []
    for paper_id in PAPER_IDS:
        root = REPO_ROOT / FUTURE_PAPER_DIRECTORIES[paper_id]
        if (root / "MANUSCRIPT.md").is_file():
            transitioned.append(paper_id)
            assert "NO_PROTECTED_RESULT" not in (root / "README.md").read_text(encoding="utf-8")

    assert transitioned, "publication-transition guard installed without any canonical P11-P14 paper"
