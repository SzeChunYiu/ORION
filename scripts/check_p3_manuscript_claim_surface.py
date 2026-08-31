#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
paper = repo / "papers/orion-13-global-knowledge-portrait"
root = paper / "manuscript"
main_text = (root / "main.tex").read_text(encoding="utf-8")
tex_files = [root / "main.tex", *sorted((root / "sections").glob("*.tex"))]
text = "\n".join(path.read_text(encoding="utf-8") for path in tex_files)

abstract = (root / "sections/00-abstract.tex").read_text(encoding="utf-8")
introduction = (root / "sections/10-introduction.tex").read_text(encoding="utf-8")
dataset = (root / "sections/40-dataset.tex").read_text(encoding="utf-8")
evaluation = (root / "sections/50-evaluation.tex").read_text(encoding="utf-8")
conclusion = (root / "sections/08-conclusion.tex").read_text(encoding="utf-8")
limitations = (root / "sections/07-limitations.tex").read_text(encoding="utf-8")
scoped = (paper / "SCOPED_PUBLICATION_TRACK_V1.md").read_text(encoding="utf-8")

errors: list[str] = []
for name, fragment in [
    ("abstract", abstract),
    ("introduction", introduction),
    ("conclusion", conclusion),
]:
    if "0.1875" not in fragment or "-0.1875" not in fragment:
        errors.append(f"{name}_missing_confirmatory_effect")
    if "0.125 for flat predicate" in fragment or "$-0.125$" in fragment:
        errors.append(f"{name}_still_uses_exploratory_headline")

sys.path.insert(0, str(repo / "tests"))
from test_paper_manuscript_integrity import _states_the_three_valued_boundary

for name, fragment in [("abstract", abstract), ("conclusion", conclusion)]:
    token = "CANNOT\\_CHECK" in fragment or "\\conststatus{}" in fragment
    if not token and not _states_the_three_valued_boundary(fragment):
        errors.append(f"{name}_missing_evidence_boundary")

if "has not been executed" not in limitations:
    errors.append("limitations_do_not_mark_broad_study_unexecuted")
if "ORION-13.C7" not in scoped or "ORION-13.C8" not in scoped:
    errors.append("scoped_track_missing_nonclaim_ids")

for name, phrases in {
    "introduction": [
        "independently annotated gold dataset spanning four disciplines",
        "gold study is designed to test",
    ],
    "dataset": [
        "The released manifest is \\texttt{SEED}",
        "Final gold replaces these",
        "all 32 samples annotated and adjudicated",
    ],
    "evaluation": [
        "same gold dataset",
        "five stochastic seeds",
        "deepseek-v4-pro",
        "Six baselines are implemented",
        "Eight ablations are implemented",
        "Seventeen metrics are computed per run",
    ],
}.items():
    fragment = {
        "introduction": introduction,
        "dataset": dataset,
        "evaluation": evaluation,
    }[name]
    for phrase in phrases:
        if phrase in fragment:
            errors.append(f"{name}_reintroduces_unexecuted_broad_claim:{phrase}")

bib_files: list[Path] = []
for group in re.findall(r"\\bibliography\{([^}]+)\}", main_text):
    for stem in group.split(","):
        stem = stem.strip()
        if stem:
            bib_files.append(root / f"{stem}.bib")
bib_text = "\n".join(path.read_text(encoding="utf-8") for path in bib_files if path.is_file())
bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib_text))
cite_keys: set[str] = set()
for group in re.findall(r"\\cite\w*\{([^}]+)\}", text):
    cite_keys.update(key.strip() for key in group.split(",") if key.strip())
forbidden_removed_keys = {
    "adias2026",
    "raghunathan2022stance",
    "liu2022scholar",
    "oh2017unified",
    "sebastian2017measurement",
    "chang2012",
    "swanson1990",
}
stale_keys = sorted((cite_keys | bib_keys) & forbidden_removed_keys)
if stale_keys:
    errors.append("stale_or_invalid_reference_keys:" + ",".join(stale_keys))

if errors:
    for error in errors:
        print(f"P3_CLAIM_SURFACE_ERROR: {error}")
    raise SystemExit(1)
print("P3_BOUNDED_CLAIM_SURFACE_OK")
