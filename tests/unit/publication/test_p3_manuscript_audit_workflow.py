"""P3 CI must inspect the current render without promoting its historical PDF."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/p3-manuscript-audit.yml"


def test_p3_workflow_enforces_superseded_package_authority() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "python scripts/write_render_closure_state.py --check" in workflow
    assert "P3_HISTORICAL_PACKAGE_SUPERSEDED_CURRENT_BUILD_INSPECTED" in workflow
    for marker in (
        '"package_status", "SUPERSEDED"',
        '"current_submission_authorized", False',
        '"binding_status", "HISTORICAL_SUPERSEDED"',
        '"current_revision_binding", False',
        '"state", "SUPERSEDED"',
    ):
        assert marker in workflow


def test_p3_workflow_does_not_promote_historical_pdf_as_current() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "cmp /tmp/p3-rebuilt.txt /tmp/p3-tracked.txt" not in workflow
    assert "Verify tracked PDF matches rebuilt manuscript content" not in workflow
    assert 'pdftotext "$rebuilt" /tmp/p3-rebuilt.txt' in workflow
    assert 'test -s /tmp/p3-rebuilt.txt' in workflow
