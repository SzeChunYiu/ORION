"""Zero-clipping audit for the built manuscript PDFs.

A line whose right edge passes the text block's right margin is an overfull box.
A line that passes the media-box edge is text physically off the paper. Neither
shows up in a text extraction -- ``pdftotext`` returns characters no reader can
see -- so the defect survives every text-level check the programme already runs.

The right margin is inferred per document from the modal right edge of its
justified lines rather than assumed, so the audit is geometry-independent.

Known clipping is carried in a baseline file so the gate reds on *new* clipping
from the day it lands, while the outstanding debt stays counted and visible
instead of silently tolerated. A baseline entry that no longer reproduces is
reported too: stale suppression is its own defect.

Exit codes
----------
0   no clipping outside the baseline
2   new clipping, or a stale baseline entry
3   CANNOT_CHECK -- the audit could not run, which is not the same as clean
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# PyMuPDF reports glyph-ink bounds, not TeX line-box bounds. On a justified
# pdfTeX line whose box ends exactly at the margin, italic/round glyph ink can
# extend about 3.3 pt farther even though the TeX log has no overfull box. Keep
# that renderer-level protrusion distinct from material layout overflow.
GLYPH_INK_TOLERANCE_PT = 4.0
PAGE_EDGE_TOLERANCE_PT = 1.0
MIN_LINES_FOR_MARGIN = 5


def discover_current_pdfs(root: Path) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Return working manuscripts plus journal packages not marked superseded.

    A ``SUPERSEDED`` package is an immutable historical receipt, not the current
    submission object. Auditing it as if it were current both creates stale-page
    noise and invites callers to overwrite custody evidence merely to green CI.
    The working ``manuscript/main.pdf`` remains in scope for every paper.
    """

    papers = root / "papers"
    current = set(papers.glob("orion-??-*/manuscript/main.pdf"))
    skipped: list[tuple[Path, str]] = []
    for pdf in papers.glob("orion-??-*/journal_package/manuscript.pdf"):
        closure = pdf.parent / "RENDER_CLOSURE_STATE.json"
        state = None
        if closure.is_file():
            payload = json.loads(closure.read_text(encoding="utf-8"))
            state = payload.get("state")
        if state == "SUPERSEDED":
            skipped.append((pdf, state))
        else:
            current.add(pdf)
    return sorted(current), sorted(skipped)


def infer_right_margin(doc) -> float | None:
    """The modal right edge of justified lines, or None if there is too little text."""
    edges: collections.Counter[int] = collections.Counter()
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                edges[round(line["bbox"][2])] += 1
    modal = next(
        (edge for edge, count in edges.most_common() if count >= MIN_LINES_FOR_MARGIN),
        None,
    )
    return float(modal) if modal is not None else None


def audit_one(path: Path, label: str) -> tuple[list[dict], str | None]:
    doc = fitz.open(path)
    margin = infer_right_margin(doc)
    if margin is None:
        return [], f"{label}: too little text to infer a right margin"
    findings = []
    for number, page in enumerate(doc, start=1):
        page_edge = page.rect.x1
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                x1 = line["bbox"][2]
                if x1 <= margin + GLYPH_INK_TOLERANCE_PT:
                    continue
                findings.append(
                    {
                        "file": label,
                        "page": number,
                        "kind": (
                            "OFF_PAGE"
                            if x1 > page_edge - PAGE_EDGE_TOLERANCE_PT
                            else "OVERFULL"
                        ),
                        "overhang_pt": round(x1 - margin, 1),
                        "text": "".join(s["text"] for s in line["spans"])[:120],
                    }
                )
    return findings, None


def key(finding: dict) -> str:
    return f"{finding['file']}:p{finding['page']}:{finding['kind']}:{finding['text'][:60]}"


def main() -> int:
    if fitz is None:
        print("CANNOT_CHECK: PyMuPDF (fitz) is not installed; cannot audit any PDF")
        return 3

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="*", type=Path)
    parser.add_argument(
        "--discover-current",
        action="store_true",
        help="audit working manuscripts and non-superseded journal packages under --root",
    )
    parser.add_argument("--baseline", type=Path, help="JSON list of accepted finding keys")
    parser.add_argument(
        "--write-baseline",
        type=Path,
        help="record current findings and exit 0; fails closed if any PDF is unreadable",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="paths are labelled relative to this")
    args = parser.parse_args()

    pdfs = list(args.pdfs)
    if args.discover_current:
        try:
            discovered, skipped = discover_current_pdfs(args.root)
        except Exception as exc:
            print(f"CANNOT_CHECK current-PDF discovery failed: {exc}")
            return 3
        pdfs.extend(discovered)
        for path, state in skipped:
            print(f"SKIP_{state} {path.relative_to(args.root)}")
    pdfs = sorted(set(pdfs))
    if not pdfs:
        print("CANNOT_CHECK: no manuscript PDF selected")
        return 3

    findings, unreadable = [], []
    for path in pdfs:
        try:
            label = str(path.resolve().relative_to(args.root.resolve()))
        except ValueError:
            label = str(path)
        try:
            found, note = audit_one(path, label)
        except Exception as exc:
            unreadable.append(f"{label}: {exc}")
            continue
        if note:
            unreadable.append(note)
        findings.extend(found)

    if args.write_baseline:
        if unreadable:
            for note in unreadable:
                print(f"CANNOT_CHECK {note}")
            print("CANNOT_CHECK: baseline not written because at least one PDF was unreadable")
            return 3
        args.write_baseline.write_text(json.dumps(sorted(key(f) for f in findings), indent=2) + "\n")
        print(f"baseline written: {len(findings)} findings over {len(pdfs)} PDFs")
        return 0

    accepted = set(json.loads(args.baseline.read_text())) if args.baseline else set()
    seen = {key(f) for f in findings}
    new = [f for f in findings if key(f) not in accepted]
    stale = sorted(accepted - seen)

    for finding in sorted(new, key=lambda f: (f["file"], f["page"])):
        print(
            f"NEW {finding['kind']:8s} {finding['file']}:p{finding['page']} "
            f"+{finding['overhang_pt']}pt :: {finding['text'][:90]}"
        )
    for entry in stale:
        print(f"STALE_BASELINE {entry}")
    for note in unreadable:
        print(f"CANNOT_CHECK {note}")

    remaining = len(findings) - len(new)
    print(
        f"\naudited={len(pdfs)} findings={len(findings)} "
        f"new={len(new)} accepted_debt={remaining} stale_baseline={len(stale)} "
        f"unreadable={len(unreadable)}"
    )
    if unreadable:
        return 3
    return 2 if (new or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
