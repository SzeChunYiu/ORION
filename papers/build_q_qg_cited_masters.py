#!/usr/bin/env python3
"""Generate cited publication masters from the final scientific manuscripts.

This script is deliberately narrow: it inserts verified citation tokens at frozen textual
anchors and concatenates the verified BibTeX sources. It may not rewrite scientific prose.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAP = ROOT / "papers/Q_QG_CITATION_INSERTION_MAP_V1.json"
KEY_RE = re.compile(r"@[A-Za-z]+\s*\{\s*([^,\s]+)")
CITE_KEY_RE = re.compile(r"@([A-Za-z0-9_:\-.]+)")


def nth_index(text: str, needle: str, occurrence: int) -> int:
    if occurrence < 1:
        raise ValueError("occurrence must be >=1")
    start = 0
    idx = -1
    for _ in range(occurrence):
        idx = text.find(needle, start)
        if idx < 0:
            return -1
        start = idx + len(needle)
    return idx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", default="build/q_qg_cited")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    out_root = ROOT / args.out_root
    if args.clean and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    config = json.loads(MAP.read_text(encoding="utf-8"))
    errors: list[str] = []

    # Build one reusable verified bibliography and collect valid keys.
    bib_parts: list[str] = []
    bib_keys: set[str] = set()
    for rel in config.get("bibliographies", []):
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"MISSING_BIB:{rel}")
            continue
        body = path.read_text(encoding="utf-8")
        bib_parts.append(body.rstrip() + "\n")
        bib_keys.update(KEY_RE.findall(body))
    combined_bib = "\n".join(bib_parts)
    (out_root / "references.bib").write_text(combined_bib, encoding="utf-8")

    report: dict[str, object] = {
        "schema": "ORIONQ.CitedMasterBuildReport.v1",
        "map": str(MAP.relative_to(ROOT)),
        "bibliography_keys": sorted(bib_keys),
        "papers": {},
    }

    for paper_id, spec in config.get("papers", {}).items():
        source_rel = spec.get("source")
        if not source_rel:
            errors.append(f"MISSING_SOURCE_FIELD:{paper_id}")
            continue
        source = ROOT / source_rel
        if not source.is_file():
            errors.append(f"MISSING_SOURCE:{paper_id}:{source_rel}")
            continue
        original = source.read_text(encoding="utf-8")
        cited = original
        placements: list[dict[str, object]] = []

        for insertion in spec.get("insertions", []):
            needle = insertion.get("needle", "")
            citation = insertion.get("citation", "")
            occurrence = int(insertion.get("occurrence", 1))
            if not needle or not citation:
                errors.append(f"INVALID_INSERTION:{paper_id}:{insertion}")
                continue
            for key in CITE_KEY_RE.findall(citation):
                if key not in bib_keys:
                    errors.append(f"UNKNOWN_CITATION_KEY:{paper_id}:{key}")
            idx = nth_index(cited, needle, occurrence)
            if idx < 0:
                errors.append(f"CITATION_NEEDLE_NOT_FOUND:{paper_id}:{occurrence}:{needle}")
                continue
            end = idx + len(needle)
            tail = cited[end : end + len(citation) + 2]
            if citation in tail:
                errors.append(f"CITATION_ALREADY_PRESENT:{paper_id}:{needle}")
                continue
            cited = cited[:end] + " " + citation + cited[end:]
            placements.append(
                {"needle": needle, "citation": citation, "occurrence": occurrence}
            )

        # Citation generation is allowed to add only citation tokens/one separating space.
        # Preserve a hash-like length accounting to catch accidental prose edits.
        expected_delta = sum(len(p["citation"]) + 1 for p in placements)
        actual_delta = len(cited) - len(original)
        if actual_delta != expected_delta:
            errors.append(
                f"NON_CITATION_TEXT_DELTA:{paper_id}:actual={actual_delta}:expected={expected_delta}"
            )

        paper_dir = out_root / paper_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        out_path = paper_dir / "MANUSCRIPT_CITED.md"
        out_path.write_text(cited, encoding="utf-8")
        (paper_dir / "references.bib").write_text(combined_bib, encoding="utf-8")
        report["papers"][paper_id] = {
            "source": source_rel,
            "output": str(out_path.relative_to(ROOT)),
            "insertions_applied": len(placements),
            "placements": placements,
            "source_chars": len(original),
            "output_chars": len(cited),
        }

    report_path = out_root / "build_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        print("Q_QG_CITED_MASTER_BUILD=FAIL")
        for err in errors:
            print(f"- {err}")
        print(f"REPORT={report_path.relative_to(ROOT)}")
        return 1

    print("Q_QG_CITED_MASTER_BUILD=PASS")
    print(f"PAPERS={len(report['papers'])}")
    print(f"BIB_KEYS={len(bib_keys)}")
    for paper_id in sorted(report["papers"]):
        row = report["papers"][paper_id]
        print(f"{paper_id}_CITATIONS_INSERTED={row['insertions_applied']}")
    print(f"OUTPUT_ROOT={out_root.relative_to(ROOT)}")
    print("SCIENTIFIC_PROSE_REWRITE=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
