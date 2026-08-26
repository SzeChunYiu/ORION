from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-14-verified-scientific-discovery"


def test_method_authority_extension_does_not_rewrite_current_p4_submission():
    readiness = (PAPER / "JOURNAL_READINESS.md").read_text(encoding="utf-8")
    manuscript = (PAPER / "manuscript" / "main.tex").read_text(encoding="utf-8")
    extension = (PAPER / "manuscript" / "METHOD_TRANSFER_AUTHORITY_EXTENSION_V1.md").read_text(
        encoding="utf-8"
    )

    assert "ORION-P4 = PEER_REVIEW_READY" in readiness
    assert "P4_METHOD_AUTHORITY_SUPPORTED" not in manuscript
    assert "citation-saturated peer-review-ready P4 manuscript/PDF" in extension
    assert "does not rewrite the existing P4 headline result" in extension
