"""State-aware publication guard for ORION P11-P14.

The original #715-era tests assumed all four directories must remain empty
placeholders forever. Canonical paper PRs #771-#774 supersede that ownership one
paper at a time. This guard preserves the useful invariant without treating
publication progress as a failure.
"""

import re
from pathlib import Path

from orion.programme.superiority_terminals import FUTURE_PAPER_DIRECTORIES

REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER_IDS = ("P11", "P12", "P13", "P14")

EXPECTED_CURRENT_DECISIONS = {
    "P11": ("READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_SUPERIORITY_RESULT",),
    "P12": ("CONTROLLED_LIFECYCLE_RESULT_BOUND__PUBLIC_TRANSFER_OPEN",),
    "P13": (
        "READY_FOR_CONTROLLED_P13B_CLAIM__EXTERNAL_VALIDATION_OPEN",
        "NOT_READY__P13A_SELF_SCORED_SAFETY_ENDPOINT",
    ),
    "P14": ("READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT",),
}


def test_p11_to_p14_are_either_honest_placeholders_or_complete_canonical_packages() -> None:
    for paper_id in PAPER_IDS:
        directory = FUTURE_PAPER_DIRECTORIES[paper_id]
        root = REPO_ROOT / directory
        assert root.is_dir(), f"{paper_id} has no directory at {directory}"

        readme = root / "README.md"
        assert readme.is_file(), f"{paper_id} has no README"
        text = readme.read_text(encoding="utf-8")
        # R0 renamed these papers, so the identity is not "ORION-" + the legacy
        # P-number: PAPER_ALIASES maps P11..P14 onto ORION-21..ORION-24. Deriving
        # it from the directory keeps this checking the paper's real stable ID
        # rather than a concatenation that names nothing.
        stable_id = re.match(r"papers/(orion-\d+)", directory).group(1).upper()
        assert stable_id in text, f"{paper_id} README does not carry {stable_id}"

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
        for expected in EXPECTED_CURRENT_DECISIONS[paper_id]:
            assert expected in readiness_text, (
                f"{paper_id} canonical package lacks the current bounded decision "
                f"{expected!r}"
            )


def test_draft_715_no_longer_has_exclusive_manuscript_ownership_after_canonical_transition() -> None:
    transitioned = []
    for paper_id in PAPER_IDS:
        root = REPO_ROOT / FUTURE_PAPER_DIRECTORIES[paper_id]
        if (root / "MANUSCRIPT.md").is_file():
            transitioned.append(paper_id)
            assert "NO_PROTECTED_RESULT" not in (root / "README.md").read_text(encoding="utf-8")

    assert transitioned, "publication-transition guard installed without any canonical P11-P14 paper"
