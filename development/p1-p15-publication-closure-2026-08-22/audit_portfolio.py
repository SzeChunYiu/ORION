#!/usr/bin/env python3
"""Fail-closed structural audit for the P1-P15 publication source trees."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PAPER_RE = re.compile(r"paper-(\d{2})-")
CITE_RE = re.compile(r"\\cite\w*\s*(?:\[[^]]*\]\s*)*\{([^}]*)\}")
BIB_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)", re.IGNORECASE)
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
MARKDOWN_INPUT_RE = re.compile(r"\\markdownInput\s*\{")
BRANDING_RE = re.compile(r"\borion(?:-q|-rse)?\b", re.IGNORECASE)
CODEBASE_RE = re.compile(
    r"github\.com/SzeChunYiu/ORION|packages/orion|src/orion|"
    r"this repository|repository-local|codebase",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(
    r"TODO|TBD|PLACEHOLDER|AUTHOR_INPUT_NEEDED|to be (?:written|added|completed)",
    re.IGNORECASE,
)
NEGATIVE_RE = re.compile(
    r"\b(?:negative|null|failed?|cannot[_ -]?check|not[_ -]?reached|non-authoritative)\b",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def resolve_input(manuscript: Path, source: Path, raw: str) -> bool:
    candidate = Path(raw)
    candidates = [manuscript / candidate, source.parent / candidate]
    if candidate.suffix == "":
        candidates += [path.with_suffix(".tex") for path in candidates]
    return any(path.is_file() for path in candidates)


def audit_paper(paper: Path, paper_id: int) -> dict[str, object]:
    manuscript = paper / "manuscript"
    main = manuscript / "main.tex"
    chapter_roots = [
        path for path in (manuscript / "sections", manuscript / "chapters") if path.is_dir()
    ]
    chapter_files = sorted(
        path for chapter_root in chapter_roots for path in chapter_root.rglob("*.tex")
    )
    markdown_chapters = sorted(
        path for chapter_root in chapter_roots for path in chapter_root.rglob("*.md")
    )
    tex_files = ([main] if main.is_file() else []) + chapter_files
    pdfs = sorted(manuscript.glob("*.pdf")) if manuscript.is_dir() else []
    bib_files = sorted(paper.rglob("*.bib"))

    cite_keys: set[str] = set()
    bib_keys: set[str] = set()
    missing_inputs: list[dict[str, str]] = []
    branding_hits: list[dict[str, object]] = []
    codebase_hits: list[dict[str, object]] = []
    placeholder_hits: list[dict[str, object]] = []
    negative_hits = 0
    markdown_import_wrappers = 0

    for path in tex_files:
        text = read_text(path)
        markdown_import_wrappers += len(MARKDOWN_INPUT_RE.findall(text))
        for match in CITE_RE.finditer(text):
            cite_keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
        for line_number, line in enumerate(text.splitlines(), start=1):
            if BRANDING_RE.search(line):
                branding_hits.append(
                    {"path": str(path.relative_to(paper)), "line": line_number}
                )
            if CODEBASE_RE.search(line):
                codebase_hits.append(
                    {"path": str(path.relative_to(paper)), "line": line_number}
                )
            if PLACEHOLDER_RE.search(line):
                placeholder_hits.append(
                    {"path": str(path.relative_to(paper)), "line": line_number}
                )
        negative_hits += len(NEGATIVE_RE.findall(text))
        for match in INPUT_RE.finditer(text):
            raw = match.group(1).strip()
            if not resolve_input(manuscript, path, raw):
                missing_inputs.append(
                    {"path": str(path.relative_to(paper)), "input": raw}
                )

    for path in markdown_chapters:
        text = read_text(path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if BRANDING_RE.search(line):
                branding_hits.append(
                    {"path": str(path.relative_to(paper)), "line": line_number}
                )
            if CODEBASE_RE.search(line):
                codebase_hits.append(
                    {"path": str(path.relative_to(paper)), "line": line_number}
                )
            if PLACEHOLDER_RE.search(line):
                placeholder_hits.append(
                    {"path": str(path.relative_to(paper)), "line": line_number}
                )
        negative_hits += len(NEGATIVE_RE.findall(text))

    for path in bib_files:
        bib_keys.update(BIB_RE.findall(read_text(path)))

    if not main.is_file() or not chapter_files:
        structural_status = "INCOMPLETE"
    elif missing_inputs or placeholder_hits or markdown_import_wrappers:
        structural_status = "BLOCKED"
    else:
        structural_status = "STRUCTURAL_REVIEW"

    return {
        "paper_id": f"P{paper_id}",
        "directory": paper.name,
        "structural_status": structural_status,
        "main_tex": main.is_file(),
        "main_tex_sha256": sha256(main) if main.is_file() else None,
        "tex_file_count": len(tex_files),
        "chapter_tex_count": len(chapter_files),
        "self_contained_tex_chapter_count": len(chapter_files) - markdown_import_wrappers,
        "markdown_chapter_count": len(markdown_chapters),
        "markdown_import_wrapper_count": markdown_import_wrappers,
        "manuscript_pdf_count": len(pdfs),
        "bibliography_file_count": len(bib_files),
        "citation_key_count": len(cite_keys),
        "missing_citation_keys": sorted(cite_keys - bib_keys),
        "missing_inputs": missing_inputs,
        "branding_hits": branding_hits,
        "codebase_hits": codebase_hits,
        "placeholder_hits": placeholder_hits,
        "negative_marker_count": negative_hits,
    }


def audit(root: Path) -> dict[str, object]:
    papers_root = root / "papers"
    found: dict[int, Path] = {}
    for paper in papers_root.glob("paper-??-*"):
        match = PAPER_RE.match(paper.name)
        if match:
            paper_id = int(match.group(1))
            if 1 <= paper_id <= 15:
                found[paper_id] = paper

    papers = [
        audit_paper(found[paper_id], paper_id)
        if paper_id in found
        else {
            "paper_id": f"P{paper_id}",
            "directory": None,
            "structural_status": "MISSING",
        }
        for paper_id in range(1, 16)
    ]
    return {
        "schema_version": "p1-p15-publication-structure-audit-v1",
        "root": str(root.resolve()),
        "papers": papers,
        "portfolio_pass": all(
            paper["structural_status"] == "STRUCTURAL_REVIEW" for paper in papers
        ),
    }


def markdown(report: dict[str, object]) -> str:
    lines = [
        "# P1-P15 structural audit",
        "",
        "| Paper | Status | TeX | Chapters | Self-contained | Markdown wrappers | PDF | Missing cites | Missing inputs | Branding | Codebase | Placeholders | Negative markers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for paper in report["papers"]:
        if paper["structural_status"] == "MISSING":
            lines.append(f"| {paper['paper_id']} | MISSING | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |")
            continue
        lines.append(
            "| {paper_id} | {structural_status} | {tex_file_count} | "
            "{chapter_tex_count} | {self_contained_tex_chapter_count} | {markdown_import_wrapper_count} | "
            "{manuscript_pdf_count} | {missing_cite_count} | "
            "{missing_input_count} | {branding_count} | {codebase_count} | {placeholder_count} | "
            "{negative_marker_count} |".format(
                **paper,
                missing_cite_count=len(paper["missing_citation_keys"]),
                missing_input_count=len(paper["missing_inputs"]),
                branding_count=len(paper["branding_hits"]),
                codebase_count=len(paper["codebase_hits"]),
                placeholder_count=len(paper["placeholder_hits"]),
            )
        )
    lines.extend(["", f"Portfolio structural pass: `{report['portfolio_pass']}`", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="repository/archive root")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    report = audit(args.root)
    print(markdown(report) if args.format == "markdown" else json.dumps(report, indent=2))
    return 0 if report["portfolio_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
