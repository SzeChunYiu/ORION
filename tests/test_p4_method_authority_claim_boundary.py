from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-14-verified-scientific-discovery"
# Derived from the package directory, so a later rename cannot silently
# decouple this test's label from the artifact it asserts about.
PAPER_ID = "-".join(PAPER.name.split("-")[:2]).upper()


def test_method_authority_extension_does_not_rewrite_current_p4_submission():
    readiness = (PAPER / "JOURNAL_READINESS.md").read_text(encoding="utf-8")
    manuscript = (PAPER / "manuscript" / "main.tex").read_text(encoding="utf-8")
    extension = (PAPER / "manuscript" / "METHOD_TRANSFER_AUTHORITY_EXTENSION_V1.md").read_text(
        encoding="utf-8"
    )

    assert f"{PAPER_ID} = PEER_REVIEW_READY" in readiness
    # Negative assertion, asserted under both spellings: a claim token must not
    # be able to re-enter the manuscript merely by being renamed.
    assert "P4_METHOD_AUTHORITY_SUPPORTED" not in manuscript
    assert f"{PAPER_ID}_METHOD_AUTHORITY_SUPPORTED" not in manuscript
    assert f"citation-saturated peer-review-ready {PAPER_ID} manuscript/PDF" in extension
    assert f"does not rewrite the existing {PAPER_ID} headline result" in extension
