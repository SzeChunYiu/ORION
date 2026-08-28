#!/usr/bin/env python3
"""Verify scientific, package, anonymity and reader-facing leakage gates."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "submission_tmlr"
REPO = ROOT.parents[1]

PUBLIC_TEXT = [
    PACKAGE / "main.tex",
    PACKAGE / "references.bib",
    PACKAGE / "COVER_LETTER.md",
    PACKAGE / "AVAILABILITY_STATEMENT.md",
    PACKAGE / "review_materials/README.md",
    PACKAGE / "review_materials/case_series.json",
    PACKAGE / "review_materials/verify_case_series.py",
    PACKAGE / "review_materials/LICENSES.txt",
]
BLIND_TEXT = [
    PACKAGE / "main.tex",
    PACKAGE / "references.bib",
    PACKAGE / "review_materials/README.md",
    PACKAGE / "review_materials/case_series.json",
    PACKAGE / "review_materials/verify_case_series.py",
    PACKAGE / "review_materials/LICENSES.txt",
]

FORBIDDEN = {
    "programme identity": re.compile(r"\bORION\b", re.I),
    "internal study number": re.compile(r"\b(?:QG|R6|V0|D2|D3|P0|ORION[- ]?\d+)\b", re.I),
    "internal tree": re.compile(r"(?:papers|research|development|artifacts|packages)/", re.I),
    "repository service or owner": re.compile(r"github|szechunyiu/orion", re.I),
    "version-control history": re.compile(r"\b(?:git commit|git branch|pull request|issue #|workflow (?:run|history)|continuous integration)\b", re.I),
    "machine authority string": re.compile(r"\b(?:PASS|FAIL|READY_TO_SUBMIT|CANNOT_CHECK)\b"),
    "cryptographic digest": re.compile(r"\b[0-9a-f]{40,64}\b", re.I),
}
IDENTITY = re.compile(r"Sze[ -]?Chun|SzeChunYiu|sze-chun\.yiu@|Billy Yiu", re.I)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


errors: list[str] = []

required = PUBLIC_TEXT + [
    PACKAGE / "main.pdf",
    PACKAGE / "anonymous-source.zip",
    PACKAGE / "anonymous-review-supplement.zip",
]
for path in required:
    if not path.is_file() or path.stat().st_size == 0:
        fail(errors, f"missing or empty required object: {path.relative_to(ROOT)}")

for path in PUBLIC_TEXT:
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    for label, pattern in FORBIDDEN.items():
        match = pattern.search(text)
        if match:
            fail(errors, f"{label} leaked in {path.relative_to(ROOT)}: {match.group(0)!r}")

for path in BLIND_TEXT:
    if path.is_file() and IDENTITY.search(path.read_text(encoding="utf-8")):
        fail(errors, f"author identity leaked in blind material: {path.relative_to(ROOT)}")

pdf_path = PACKAGE / "main.pdf"
if pdf_path.is_file():
    pdf_text_result = run(["pdftotext", str(pdf_path), "-"], ROOT)
    if pdf_text_result.returncode != 0:
        fail(errors, "could not extract the canonical PDF text")
    else:
        pdf_text = pdf_text_result.stdout
        if IDENTITY.search(pdf_text):
            fail(errors, "author identity leaked in canonical PDF")
        for label, pattern in FORBIDDEN.items():
            match = pattern.search(pdf_text)
            if match:
                fail(errors, f"{label} leaked in canonical PDF: {match.group(0)!r}")
        for required_pdf_token in ("39,489", "53 frozen rows", "Anonymous authors"):
            if required_pdf_token not in pdf_text:
                fail(errors, f"canonical PDF lacks required text: {required_pdf_token!r}")

for archive_name in ("anonymous-source.zip", "anonymous-review-supplement.zip"):
    archive = PACKAGE / archive_name
    if not archive.is_file():
        continue
    with ZipFile(archive) as zf:
        names = zf.namelist()
        if names != sorted(names):
            fail(errors, f"archive entries not deterministic/sorted: {archive_name}")
        for name in names:
            for label, pattern in FORBIDDEN.items():
                match = pattern.search(name)
                if match:
                    fail(errors, f"{label} leaked in archive entry name {archive_name}:{name}")
            if name.lower().endswith((".md", ".txt", ".tex", ".bib", ".py", ".json", ".sty", ".bst")):
                text = zf.read(name).decode("utf-8", errors="replace")
                if IDENTITY.search(text):
                    fail(errors, f"author identity leaked in archive payload {archive_name}:{name}")
                if name not in {"tmlr.sty", "tmlr.bst", "fancyhdr.sty"}:
                    for label, pattern in FORBIDDEN.items():
                        match = pattern.search(text)
                        if match:
                            fail(errors, f"{label} leaked in archive payload {archive_name}:{name}: {match.group(0)!r}")

review = run([sys.executable, "verify_case_series.py"], PACKAGE / "review_materials")
if review.returncode != 0:
    fail(errors, "anonymous review verifier failed:\n" + review.stdout + review.stderr)

source = (PACKAGE / "main.tex").read_text(encoding="utf-8") if (PACKAGE / "main.tex").is_file() else ""
for token in (
    "three-question dual-instrument case series",
    "39{,}489",
    "53 frozen rows",
    "both instruments are misaligned",
    "were not repaired between cases",
    "estimate no agreement rate, reliability, calibration",
):
    if token not in source:
        fail(errors, f"required manuscript boundary/result token missing: {token!r}")

record_path = PACKAGE / "review_materials/case_series.json"
if record_path.is_file():
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record["study_boundary"]["valid_question_count"] != 3:
        fail(errors, "review record does not preserve exactly three valid questions")
    if len(record["retired_candidates"]) != 2:
        fail(errors, "review record does not preserve both contaminated candidates")

if errors:
    print("closeout verification failed")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("closeout verification passed")
print(review.stdout.strip())
