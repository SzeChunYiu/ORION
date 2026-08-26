from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"


def test_structural_extension_does_not_rewrite_current_submission_claim():
    readiness = (PAPER / "JOURNAL_READINESS.md").read_text(encoding="utf-8")
    manuscript = (PAPER / "manuscript" / "main.tex").read_text(encoding="utf-8")
    extension = (PAPER / "manuscript" / "STRUCTURE_CONDITIONED_DISCOVERY_EXTENSION_V1.md").read_text(
        encoding="utf-8"
    )

    assert "ORION-P2 = PEER_REVIEW_READY" in readiness
    assert "External ORION-vs-baseline superiority remains `CANNOT_CHECK`" in readiness
    assert "P2_STRUCTURAL_DISCOVERY_SUPPORTED" not in manuscript
    assert "The already peer-review-ready narrowed P2 manuscript" in extension
    assert "does **not** broaden the current P2 headline" in extension
