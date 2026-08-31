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
errors: list[str] = []

bib_files: list[Path] = []
for group in re.findall(r"\\bibliography\{([^}]+)\}", main_text):
    for stem in group.split(","):
        stem = stem.strip()
        if stem:
            bib_files.append(root / f"{stem}.bib")
missing_bib_files = [str(path.relative_to(root)) for path in bib_files if not path.is_file()]
bib_text = "\n".join(path.read_text(encoding="utf-8") for path in bib_files if path.is_file())
bib_keys_list = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib_text)
bib_keys = set(bib_keys_list)
cite_keys: set[str] = set()
for group in re.findall(r"\\cite\w*\{([^}]+)\}", text):
    cite_keys.update(key.strip() for key in group.split(",") if key.strip())
missing_cites = sorted(cite_keys - bib_keys)
duplicate_bib_keys = sorted({key for key in bib_keys_list if bib_keys_list.count(key) > 1})

missing_inputs: list[str] = []
for target in re.findall(r"\\input\{([^}]+)\}", main_text):
    path = root / target
    if not path.suffix:
        path = path.with_suffix(".tex")
    if not path.is_file():
        missing_inputs.append(str(path.relative_to(root)))
labels = re.findall(r"\\label\{([^}]+)\}", text)
duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})

if missing_bib_files:
    errors.append("missing_bibliography_files:" + ",".join(missing_bib_files))
if missing_cites:
    errors.append("missing_citation_keys:" + ",".join(missing_cites))
if duplicate_bib_keys:
    errors.append("duplicate_bibliography_keys:" + ",".join(duplicate_bib_keys))
if missing_inputs:
    errors.append("missing_input_files:" + ",".join(missing_inputs))
if duplicate_labels:
    errors.append("duplicate_labels:" + ",".join(duplicate_labels))

abstract = (root / "sections/00-abstract.tex").read_text(encoding="utf-8")
introduction = (root / "sections/10-introduction.tex").read_text(encoding="utf-8")
dataset = (root / "sections/40-dataset.tex").read_text(encoding="utf-8")
evaluation = (root / "sections/50-evaluation.tex").read_text(encoding="utf-8")
conclusion = (root / "sections/08-conclusion.tex").read_text(encoding="utf-8")
limitations = (root / "sections/07-limitations.tex").read_text(encoding="utf-8")
scoped = (paper / "SCOPED_PUBLICATION_TRACK_V1.md").read_text(encoding="utf-8")

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
        print(f"P3_MANUSCRIPT_AUDIT_ERROR: {error}")
    raise SystemExit(1)
print("P3_MANUSCRIPT_STATIC_AND_BOUNDED_CLAIM_SURFACE_OK")
