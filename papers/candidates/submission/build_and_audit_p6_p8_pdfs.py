#!/usr/bin/env python3
"""Build and audit the P6-P8 journal PDFs on the exact source head.

The source-only submission linter cannot see clipped or overflowing text.  This
gate compiles each manuscript in an isolated output directory, rejects the
layout/reference warnings that invalidate a submission PDF, and emits a
machine-readable receipt for the CI artifact.  It does not claim peer review or
scientific validity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPERS = ROOT / "papers"


@dataclass(frozen=True)
class Manuscript:
    paper: str
    source: Path


MANUSCRIPTS = (
    Manuscript(
        "P6",
        PAPERS
        / "paper-06-formal-epistemic-structures-and-mechanics"
        / "submission"
        / "AIJ_MANUSCRIPT.tex",
    ),
    Manuscript(
        "P7",
        PAPERS
        / "paper-07-epistemic-navigation-open-worlds"
        / "submission"
        / "AIJ_MANUSCRIPT.tex",
    ),
    Manuscript(
        "P8",
        PAPERS
        / "paper-08-epistemic-authority-autonomous-science"
        / "submission"
        / "JAAMAS_MANUSCRIPT.tex",
    ),
)

FORBIDDEN_LOG_PATTERNS = (
    (re.compile(r"Overfull \\hbox"), "overfull horizontal box"),
    (re.compile(r"Overfull \\vbox"), "overfull vertical box"),
    (re.compile(r"LaTeX Warning: Citation .* undefined"), "undefined citation"),
    (re.compile(r"LaTeX Warning: Reference .* undefined"), "undefined reference"),
    (re.compile(r"There were undefined references"), "undefined references"),
    (re.compile(r"multiply defined", re.IGNORECASE), "multiply-defined label"),
)


#: `Overfull \\hbox (12.3pt too wide) in paragraph at lines 120--124` and friends.
#: The width and the line range are the whole diagnosis; without them the message
#: names a class of defect and leaves the reader to rebuild the document to find
#: the instance.
_DIAGNOSTIC_LINE = re.compile(
    r"^(?:Overfull|Underfull)\s+\\[hv]box.*$"
    r"|^LaTeX Warning: (?:Citation|Reference).*$"
    r"|^There were undefined references\.?$",
    re.MULTILINE,
)


def audit_log(log_text: str) -> tuple[str, ...]:
    """Return distinct forbidden warning labels found in one LaTeX log."""
    return tuple(
        sorted(
            {
                label
                for pattern, label in FORBIDDEN_LOG_PATTERNS
                if pattern.search(log_text)
            }
        )
    )


def _explain(log_text: str, limit: int = 25) -> str:
    """Quote the log lines that caused the rejection.

    The audit previously reported only the violation class -- "overfull horizontal
    box" -- which is true, unactionable, and requires a local TeX install to turn
    into a location. Every one of these findings carries its own coordinates in the
    log; not printing them was throwing away the diagnosis and keeping the verdict.
    """

    found = _DIAGNOSTIC_LINE.findall(log_text)
    if not found:
        return (
            "    (the forbidden pattern matched but no diagnostic line could be "
            "extracted; inspect the archived .log)"
        )
    shown = found[:limit]
    body = "\n".join(f"    {line.strip()}" for line in shown)
    if len(found) > limit:
        body += f"\n    ... and {len(found) - limit} more"
    return body


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(manuscript: Manuscript, output_root: Path) -> dict[str, object]:
    if not manuscript.source.is_file():
        raise AssertionError(f"missing manuscript: {manuscript.source.relative_to(ROOT)}")

    outdir = output_root / manuscript.paper.lower()
    outdir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        {
            "FORCE_SOURCE_DATE": "1",
            "LC_ALL": "C.UTF-8",
            "SOURCE_DATE_EPOCH": "0",
            "TZ": "UTC",
        }
    )
    command = [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={outdir}",
        str(manuscript.source.relative_to(ROOT)),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
    )
    if completed.returncode != 0:
        tail = (completed.stdout + "\n" + completed.stderr)[-8000:]
        raise AssertionError(f"{manuscript.paper} PDF build failed:\n{tail}")

    stem = manuscript.source.stem
    pdf = outdir / f"{stem}.pdf"
    log = outdir / f"{stem}.log"
    if not pdf.is_file() or not log.is_file():
        raise AssertionError(f"{manuscript.paper} build did not emit PDF and log")
    if pdf.stat().st_size < 10_000 or not pdf.read_bytes().startswith(b"%PDF-"):
        raise AssertionError(f"{manuscript.paper} emitted an invalid or empty PDF")

    log_text = log.read_text(encoding="utf-8", errors="replace")
    violations = audit_log(log_text)
    if violations:
        raise AssertionError(
            f"{manuscript.paper} PDF audit failed: {', '.join(violations)}\n" + _explain(log_text)
        )

    return {
        "paper": manuscript.paper,
        "source": str(manuscript.source.relative_to(ROOT)),
        "source_sha256": sha256(manuscript.source),
        "pdf": str(pdf.relative_to(output_root)),
        "pdf_bytes": pdf.stat().st_size,
        "pdf_sha256": sha256(pdf),
        "log_sha256": sha256(log),
        "forbidden_warning_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    output_root = args.output_root.resolve()
    if args.clean and output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    receipt = {
        "schema": "P6P8SubmissionPdfAudit.v1",
        "source_date_epoch": 0,
        "manuscripts": [build(manuscript, output_root) for manuscript in MANUSCRIPTS],
        "terminal": "PASS",
    }
    receipt_path = output_root / "PDF_AUDIT_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("P6-P8 submission PDF build/audit: PASS")
    print(receipt_path)


if __name__ == "__main__":
    main()
