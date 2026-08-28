from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
# Derived from the package directory, so a later rename cannot silently
# decouple this test's label from the artifact it asserts about.
PAPER_ID = "-".join(PAPER.name.split("-")[:2]).upper()


def test_structural_extension_does_not_rewrite_current_submission_claim():
    readiness = (PAPER / "JOURNAL_READINESS.md").read_text(encoding="utf-8")
    manuscript = (PAPER / "manuscript" / "main.tex").read_text(encoding="utf-8")
    extension = (PAPER / "manuscript" / "STRUCTURE_CONDITIONED_DISCOVERY_EXTENSION_V1.md").read_text(
        encoding="utf-8"
    )

    assert f"{PAPER_ID} = PEER_REVIEW_READY" in readiness
    assert "External ORION-vs-baseline superiority remains `CANNOT_CHECK`" in readiness
    # Negative assertion, asserted under both spellings: a claim token must not
    # be able to re-enter the manuscript merely by being renamed.
    assert "P2_STRUCTURAL_DISCOVERY_SUPPORTED" not in manuscript
    assert f"{PAPER_ID}_STRUCTURAL_DISCOVERY_SUPPORTED" not in manuscript
    assert f"The already peer-review-ready narrowed {PAPER_ID} manuscript" in extension
    assert f"does **not** broaden the current {PAPER_ID} headline" in extension
