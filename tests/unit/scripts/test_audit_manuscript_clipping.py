from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys

import pytest


pytest.importorskip(
    "fitz",
    reason="PyMuPDF is exercised by the dedicated manuscript-clipping workflow",
)


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "audit_manuscript_clipping_test", ROOT / "scripts/audit_manuscript_clipping.py"
)
assert SPEC is not None and SPEC.loader is not None
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


@dataclass
class _Rect:
    x1: float = 612.0


class _Page:
    def __init__(self, right_edges: list[float]) -> None:
        self.rect = _Rect()
        self._right_edges = right_edges

    def get_text(self, _kind: str) -> dict:
        return {
            "blocks": [
                {
                    "lines": [
                        {"bbox": (72.0, 0.0, edge, 10.0), "spans": [{"text": str(edge)}]}
                        for edge in self._right_edges
                    ]
                }
            ]
        }


def test_small_glyph_ink_protrusion_is_not_reported(monkeypatch, tmp_path) -> None:
    # pdfTeX can place a justified line box exactly at 540 pt while the glyph-ink
    # bbox reported by PyMuPDF extends a few points farther. The TeX log remains
    # free of overfull boxes, so this is not manuscript clipping.
    doc = [_Page([540.0] * 8 + [543.3])]
    monkeypatch.setattr(audit.fitz, "open", lambda _path: doc)

    findings, unreadable = audit.audit_one(tmp_path / "paper.pdf", "paper.pdf")

    assert unreadable is None
    assert findings == []


def test_material_margin_overflow_and_off_page_text_still_fail(monkeypatch, tmp_path) -> None:
    doc = [_Page([540.0] * 8 + [552.0, 613.0])]
    monkeypatch.setattr(audit.fitz, "open", lambda _path: doc)

    findings, unreadable = audit.audit_one(tmp_path / "paper.pdf", "paper.pdf")

    assert unreadable is None
    assert [finding["kind"] for finding in findings] == ["OVERFULL", "OFF_PAGE"]
    assert [finding["overhang_pt"] for finding in findings] == [12.0, 73.0]


def test_discovery_excludes_explicitly_superseded_journal_package(tmp_path) -> None:
    paper = tmp_path / "papers" / "orion-02-example"
    working = paper / "manuscript" / "main.pdf"
    historical = paper / "journal_package" / "manuscript.pdf"
    working.parent.mkdir(parents=True)
    historical.parent.mkdir(parents=True)
    working.write_bytes(b"current")
    historical.write_bytes(b"historical")
    (historical.parent / "RENDER_CLOSURE_STATE.json").write_text(
        json.dumps({"state": "SUPERSEDED"}), encoding="utf-8"
    )

    current, skipped = audit.discover_current_pdfs(tmp_path)

    assert current == [working]
    assert skipped == [(historical, "SUPERSEDED")]


def test_repeated_overflow_lines_cannot_become_the_inferred_margin(monkeypatch, tmp_path) -> None:
    doc = [_Page([540.0] * 8 + [600.0] * 5)]
    monkeypatch.setattr(audit.fitz, "open", lambda _path: doc)

    findings, unreadable = audit.audit_one(tmp_path / "paper.pdf", "paper.pdf")

    assert unreadable is None
    assert audit.infer_right_margin(doc) == 540.0
    assert len(findings) == 5
    assert all(finding["kind"] == "OVERFULL" for finding in findings)


def test_baseline_write_fails_closed_when_any_pdf_is_unreadable(
    monkeypatch, tmp_path
) -> None:
    target = tmp_path / "baseline.json"
    monkeypatch.setattr(
        audit, "audit_one", lambda _path, label: ([], f"{label}: unreadable")
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_manuscript_clipping.py",
            str(tmp_path / "bad.pdf"),
            "--write-baseline",
            str(target),
        ],
    )

    assert audit.main() == 3
    assert not target.exists()


def test_main_fails_closed_when_pymupdf_is_unavailable(monkeypatch, capsys) -> None:
    monkeypatch.setattr(audit, "fitz", None)

    assert audit.main() == 3
    assert capsys.readouterr().out == (
        "CANNOT_CHECK: PyMuPDF (fitz) is not installed; cannot audit any PDF\n"
    )


def test_unreadable_pdf_takes_precedence_over_simultaneous_findings(
    monkeypatch, tmp_path
) -> None:
    baseline = tmp_path / "baseline.json"
    baseline.write_text("[]\n", encoding="utf-8")
    finding = {
        "file": "good.pdf",
        "page": 1,
        "kind": "OVERFULL",
        "overhang_pt": 12.0,
        "text": "material overflow",
    }

    def fake_audit(_path, label):
        return ([], f"{label}: unreadable") if label.endswith("bad.pdf") else ([finding], None)

    monkeypatch.setattr(audit, "audit_one", fake_audit)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_manuscript_clipping.py",
            str(tmp_path / "good.pdf"),
            str(tmp_path / "bad.pdf"),
            "--baseline",
            str(baseline),
            "--root",
            str(tmp_path),
        ],
    )

    assert audit.main() == 3
