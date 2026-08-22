#!/usr/bin/env python3
"""Validate paper-specific science manifests against their declared frozen git cuts.

The checker resolves git blob IDs directly from each cut. Publication-branch mutation of
pre-existing science and Q3's exact prospective-extension allowance are separately guarded
by check_q_qg_publication.py / q3-completion.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "papers/Q_QG_SCIENCE_MANIFESTS_V1.json"
EXPECTED = {"Q1": 10, "Q3": 7, "Q4": 8, "QG1": 11, "QG2": 5}


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stdout.strip()


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    papers = data.get("papers", {})
    if set(papers) != set(EXPECTED):
        errors.append(f"PAPER_SET_MISMATCH:{sorted(papers)}")

    total = 0
    bound: dict[str, list[dict[str, str]]] = {}
    for paper, expected_count in EXPECTED.items():
        entry = papers.get(paper, {})
        cut = entry.get("scientific_cut")
        manuscript = entry.get("final_manuscript")
        artifacts = entry.get("science_artifacts", [])
        if not cut or not manuscript:
            errors.append(f"INCOMPLETE_PAPER_ENTRY:{paper}")
            continue
        if not (ROOT / manuscript).is_file():
            errors.append(f"MISSING_FINAL_MANUSCRIPT:{paper}:{manuscript}")
        if len(artifacts) != expected_count:
            errors.append(f"ARTIFACT_COUNT_DRIFT:{paper}:{len(artifacts)}!={expected_count}")

        paths = [a.get("path") for a in artifacts]
        if len(paths) != len(set(paths)):
            errors.append(f"DUPLICATE_ARTIFACT_PATH:{paper}")

        bound[paper] = []
        for art in artifacts:
            path = art.get("path")
            klass = art.get("class")
            if not path or not klass:
                errors.append(f"INCOMPLETE_ARTIFACT:{paper}:{art}")
                continue
            try:
                blob = git("rev-parse", f"{cut}:{path}")
            except subprocess.CalledProcessError:
                errors.append(f"ARTIFACT_NOT_AT_DECLARED_CUT:{paper}:{cut}:{path}")
                continue
            if len(blob) != 40:
                errors.append(f"INVALID_BLOB_ID:{paper}:{path}:{blob}")
            bound[paper].append({"path": path, "class": klass, "blob": blob})
            total += 1

    if errors:
        print("Q_QG_SCIENCE_MANIFEST_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q_QG_SCIENCE_MANIFEST_CHECK=PASS")
    print(f"BOUND_SCIENCE_ARTIFACTS={total}")
    for paper in sorted(bound):
        print(f"{paper}_ARTIFACTS={len(bound[paper])}")
        for row in bound[paper]:
            print(f"{paper}\t{row['class']}\t{row['blob']}\t{row['path']}")
    print("SCIENTIFIC_AUTHORITY=UNCHANGED_BY_MANIFEST")
    return 0


if __name__ == "__main__":
    sys.exit(main())
