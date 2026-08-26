from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "paper-02-open-world-scientific-discovery"


def test_structural_extension_does_not_rewrite_current_submission_claim():
    readiness = (PAPER / "JOURNAL_READINESS.md").read_text(encoding="utf-8")
    manuscript = (PAPER / "manuscript" / "main.tex").read_text(encoding="utf-8")
    extension = (PAPER / "manuscript" / "STRUCTURE_CONDITIONED_DISCOVERY_EXTENSION_V1.md").read_text(
        encoding="utf-8"
    )

    assert "P2_NARROWED_RETAINED__CURRENT_PACKAGE_NOT_SUBMISSION_READY" in readiness
    assert "External ORION-vs-baseline superiority remains" in readiness
    assert "`CANNOT_CHECK` and is not claimed" in readiness
    assert "P2_STRUCTURAL_DISCOVERY_SUPPORTED" not in manuscript
    assert "The bounded narrowed P2 manuscript" in extension
    assert "historical submission PDF remain immutable historical authority" in extension
    assert "does **not** broaden the current P2 headline" in extension
