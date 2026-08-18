from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = ROOT / "papers" / "candidates" / "submission"
sys.path.insert(0, str(SUBMISSION))
from build_and_audit_p6_p8_pdfs import audit_log, _explain  # noqa: E402


def test_audit_log_deduplicates_forbidden_warning_classes() -> None:
    log = "\n".join(
        (
            "Overfull \\hbox (2.5pt too wide) in paragraph at lines 10--11",
            "Overfull \\hbox (1.0pt too wide) in paragraph at lines 20--21",
            "LaTeX Warning: Citation `missing' undefined.",
            "There were undefined references.",
        )
    )
    assert audit_log(log) == (
        "overfull horizontal box",
        "undefined citation",
        "undefined references",
    )


def test_explain_includes_coordinates_and_terminal_diagnostic() -> None:
    log = (
        "Overfull \\hbox (2.50513pt too wide) in paragraph at lines 184--185\n"
        "There were undefined references.\n"
    )
    explanation = _explain(log)
    assert "Overfull \\hbox (2.50513pt too wide) in paragraph at lines 184--185" in explanation
    assert "There were undefined references." in explanation


def test_p6_p8_peer_review_ready_package() -> None:
    root = Path(__file__).resolve().parents[3]
    script = root / "papers" / "candidates" / "submission" / "check_peer_review_ready.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "peer-review-ready structural gate: PASS" in result.stdout
