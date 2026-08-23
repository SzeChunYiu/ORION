#!/usr/bin/env python3
"""Two implementation lanes for answer-free P1-P15 source-tree diagnostics.

This is deliberately narrower than scientific review.  Both lanes derive the
same mechanical facts from source bytes without any LLM or host-completed
capability.  Agreement therefore supports only those facts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Mapping

from audit_portfolio import audit


PAPER_NAME = re.compile(r"paper-(\d\d)-")
BRANDING = re.compile(r"\borion(?:-q|-rse)?\b", re.IGNORECASE)
PLACEHOLDER = re.compile(
    r"TODO|TBD|PLACEHOLDER|AUTHOR_INPUT_NEEDED|to be (?:written|added|completed)",
    re.IGNORECASE,
)


def lane_a(root: Path) -> dict[str, dict[str, object]]:
    report = audit(root)
    normalized: dict[str, dict[str, object]] = {}
    for paper in report["papers"]:
        paper_id = str(paper["paper_id"])
        if paper["structural_status"] == "MISSING":
            normalized[paper_id] = {
                "main_tex": False,
                "chapter_tex_count": 0,
                "markdown_import_wrapper_count": 0,
                "manuscript_pdf_count": 0,
                "branding_count": 0,
                "placeholder_count": 0,
            }
            continue
        normalized[paper_id] = {
            "main_tex": bool(paper["main_tex"]),
            "chapter_tex_count": int(paper["chapter_tex_count"]),
            "markdown_import_wrapper_count": int(paper["markdown_import_wrapper_count"]),
            "manuscript_pdf_count": int(paper["manuscript_pdf_count"]),
            "branding_count": len(paper["branding_hits"]),
            "placeholder_count": len(paper["placeholder_hits"]),
        }
    return normalized


def lane_b(root: Path) -> dict[str, dict[str, object]]:
    """Independent walk implementation; does not call the Lane A scanner."""
    result = {
        f"P{paper_id}": {
            "main_tex": False,
            "chapter_tex_count": 0,
            "markdown_import_wrapper_count": 0,
            "manuscript_pdf_count": 0,
            "branding_count": 0,
            "placeholder_count": 0,
        }
        for paper_id in range(1, 16)
    }
    papers_root = root / "papers"
    if not papers_root.is_dir():
        return result

    for entry in os.scandir(papers_root):
        if not entry.is_dir():
            continue
        match = PAPER_NAME.match(entry.name)
        if not match:
            continue
        number = int(match.group(1))
        if not 1 <= number <= 15:
            continue
        paper_id = f"P{number}"
        manuscript = Path(entry.path) / "manuscript"
        if not manuscript.is_dir():
            continue
        tex_files: list[Path] = []
        pdf_count = 0
        for directory, _, filenames in os.walk(manuscript):
            for filename in filenames:
                path = Path(directory) / filename
                if path.suffix == ".tex" and (
                    path == manuscript / "main.tex"
                    or path.parent in (manuscript / "sections", manuscript / "chapters")
                ):
                    tex_files.append(path)
                if path.parent == manuscript and path.suffix == ".pdf":
                    pdf_count += 1
        branding_count = 0
        placeholder_count = 0
        markdown_import_wrapper_count = 0
        for path in tex_files:
            text = path.read_text(encoding="utf-8", errors="replace")
            branding_count += sum(1 for line in text.splitlines() if BRANDING.search(line))
            placeholder_count += sum(
                1 for line in text.splitlines() if PLACEHOLDER.search(line)
            )
            markdown_import_wrapper_count += text.count("\\markdownInput{")
        chapter_roots = [
            path
            for path in (manuscript / "sections", manuscript / "chapters")
            if path.is_dir()
        ]
        markdown_files = [
            path for chapter_root in chapter_roots for path in chapter_root.glob("*.md")
        ]
        for path in markdown_files:
            text = path.read_text(encoding="utf-8", errors="replace")
            branding_count += sum(1 for line in text.splitlines() if BRANDING.search(line))
            placeholder_count += sum(
                1 for line in text.splitlines() if PLACEHOLDER.search(line)
            )
        result[paper_id] = {
            "main_tex": (manuscript / "main.tex").is_file(),
            "chapter_tex_count": sum(
                path.parent in (manuscript / "sections", manuscript / "chapters")
                for path in tex_files
            ),
            "markdown_import_wrapper_count": markdown_import_wrapper_count,
            "manuscript_pdf_count": pdf_count,
            "branding_count": branding_count,
            "placeholder_count": placeholder_count,
        }
    return result


def compare(
    first: Mapping[str, Mapping[str, object]],
    second: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    disagreements: list[dict[str, object]] = []
    for paper_id in sorted(set(first) | set(second), key=lambda value: int(value[1:])):
        if first.get(paper_id) != second.get(paper_id):
            disagreements.append(
                {
                    "paper_id": paper_id,
                    "lane_a": first.get(paper_id),
                    "lane_b": second.get(paper_id),
                }
            )
    return disagreements


def source_digest(root: Path) -> str:
    digest = hashlib.sha256()
    source_paths = list((root / "papers").glob("paper-??-*/manuscript/main.tex"))
    source_paths += list((root / "papers").glob("paper-??-*/manuscript/sections/*.tex"))
    source_paths += list((root / "papers").glob("paper-??-*/manuscript/sections/*.md"))
    source_paths += list((root / "papers").glob("paper-??-*/manuscript/chapters/*.tex"))
    source_paths += list((root / "papers").glob("paper-??-*/manuscript/chapters/*.md"))
    for path in sorted(source_paths):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        payload = path.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return "sha256:" + digest.hexdigest()


def run(root: Path) -> dict[str, object]:
    first = lane_a(root)
    second = lane_b(root)
    disagreements = compare(first, second)
    return {
        "schema": "P1P15.DualPortfolioSourceAudit.v1",
        "source_digest": source_digest(root),
        "lane_a": {
            "implementation": "audit_portfolio.py",
            "decision_type": "deterministic-source-scan",
            "llm_calls": 0,
            "facts": first,
        },
        "lane_b": {
            "implementation": "independent-os-walk-scan",
            "decision_type": "deterministic-source-scan",
            "llm_calls": 0,
            "facts": second,
        },
        "disagreements": disagreements,
        "terminal": (
            "P1_P15_DUAL_SOURCE_AUDIT_AGREEMENT"
            if not disagreements
            else "P1_P15_DUAL_SOURCE_AUDIT_DISAGREEMENT"
        ),
        "authority_boundary": {
            "scientific": False,
            "novelty": False,
            "publication_readiness": False,
            "global_stop": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    result = run(args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not result["disagreements"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
