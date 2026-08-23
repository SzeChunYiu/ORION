#!/usr/bin/env python3
"""Check Q/QG shared bibliography identity and final citation use.

This is a metadata/placement gate, not a literature-support or novelty authority gate.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIBS = [
    ROOT / "papers/Q_QG_VERIFIED_CORE_REFERENCES_V1.bib",
    ROOT / "papers/Q2_Q3_VERIFIED_BENCHMARK_REFERENCES_V1.bib",
    ROOT / "papers/Q3_VERIFIED_CURRENT_REFERENCES_V2.bib",
]
FINAL = [
    ROOT / "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md",
    ROOT / "papers/Q-paper-02-recursive-recovery/MANUSCRIPT_V3.md",
    ROOT / "papers/Q-paper-03-dual-instrument/MANUSCRIPT_V3.md",
    ROOT / "papers/Q-paper-04-typed-state/MANUSCRIPT_V3.md",
    ROOT / "papers/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V3.md",
    ROOT / "papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V3.md",
]
ENTRY_RE = re.compile(r"@[A-Za-z]+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.S)
DOI_RE = re.compile(r"\bdoi\s*=\s*[\{\"]([^}\"]+)", re.I)
EPRINT_RE = re.compile(r"\beprint\s*=\s*[\{\"]([^}\"]+)", re.I)
CITE_RE = re.compile(r"@([A-Za-z0-9_:\-.]+)")

REQUIRED_KEYS = {
    "schillo2026tare", "izmaylov2020unitary", "harrigan2024qualtran",
    "moser2026qet", "leblond2023realistic", "rice1976algorithm",
    "smithmiles2023isa", "chen2025scienceagentbench", "bragg2025astabench",
    "meng2026scientistone", "liu2026sciagentarena", "chao2026stale",
    "sulpovar2026contextnest", "russell1991rightthing", "buneman2001provenance",
    "cheney2009provenance", "chang2026valueblindbench", "wang2026reflect",
    "rao2026agreementmetrics", "panigrahi2026heurekabench",
}

EXPECTED_DOIS = {
    "izmaylov2020unitary": "10.1021/acs.jctc.9b00791",
    "rice1976algorithm": "10.1016/S0065-2458(08)60520-3",
    "smithmiles2023isa": "10.1145/3572895",
    "buneman2001provenance": "10.1007/3-540-44503-X_20",
    "cheney2009provenance": "10.1561/1900000006",
    "chang2026valueblindbench": "10.48550/arXiv.2604.25224",
    "wang2026reflect": "10.48550/arXiv.2605.19196",
    "rao2026agreementmetrics": "10.48550/arXiv.2606.00093",
}
EXPECTED_EPRINTS = {
    "schillo2026tare": "2601.05740",
    "harrigan2024qualtran": "2409.04643",
    "moser2026qet": "2604.03971",
    "leblond2023realistic": "2311.10686",
    "chen2025scienceagentbench": "2410.05080",
    "bragg2025astabench": "2510.21652",
    "meng2026scientistone": "2605.26340",
    "liu2026sciagentarena": "2606.12736",
    "chao2026stale": "2605.06527",
    "sulpovar2026contextnest": "2607.02116",
    "chang2026valueblindbench": "2604.25224",
    "wang2026reflect": "2605.19196",
    "rao2026agreementmetrics": "2606.00093",
    "panigrahi2026heurekabench": "2601.01678",
}


def normalize_doi(s: str) -> str:
    return s.strip().lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def main() -> int:
    errors: list[str] = []
    entries: dict[str, str] = {}
    doi_owner: dict[str, str] = {}

    for path in BIBS:
        if not path.is_file():
            errors.append(f"MISSING_BIB:{path.relative_to(ROOT)}")
            continue
        body = path.read_text(encoding="utf-8")
        for key, entry in ENTRY_RE.findall(body):
            if key in entries:
                errors.append(f"DUPLICATE_BIB_KEY:{key}")
            entries[key] = entry
            m = DOI_RE.search(entry)
            if m:
                doi = normalize_doi(m.group(1))
                if doi in doi_owner and doi_owner[doi] != key:
                    errors.append(f"DUPLICATE_DOI:{doi}:{doi_owner[doi]}:{key}")
                doi_owner[doi] = key

    missing = REQUIRED_KEYS - set(entries)
    if missing:
        errors.append(f"MISSING_REQUIRED_KEYS:{sorted(missing)}")

    for key, expected in EXPECTED_DOIS.items():
        entry = entries.get(key, "")
        m = DOI_RE.search(entry)
        if not m:
            errors.append(f"MISSING_EXPECTED_DOI:{key}:{expected}")
        elif normalize_doi(m.group(1)) != normalize_doi(expected):
            errors.append(f"DOI_MISMATCH:{key}:{m.group(1)}!={expected}")

    for key, expected in EXPECTED_EPRINTS.items():
        entry = entries.get(key, "")
        m = EPRINT_RE.search(entry)
        if not m:
            errors.append(f"MISSING_EXPECTED_EPRINT:{key}:{expected}")
        else:
            got = m.group(1).strip().lower().removeprefix("arxiv:")
            if got.split("v", 1)[0] != expected.lower():
                errors.append(f"EPRINT_MISMATCH:{key}:{got}!={expected}")

    map_body = (ROOT / "papers/Q_QG_CITATION_INSERTION_MAP_V1.json").read_text(encoding="utf-8")
    map_keys = set(CITE_RE.findall(map_body))
    unknown_map = map_keys - set(entries)
    if unknown_map:
        errors.append(f"CITATION_MAP_UNKNOWN_KEYS:{sorted(unknown_map)}")

    # Scientific masters remain citation-token free; venue masters are generated.
    for path in FINAL:
        body = path.read_text(encoding="utf-8")
        direct = set(CITE_RE.findall(body)) & set(entries)
        if direct:
            errors.append(f"DIRECT_CITATION_TOKEN_IN_SCIENTIFIC_MASTER:{path.relative_to(ROOT)}:{sorted(direct)}")

    if errors:
        print("Q_QG_REFERENCE_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q_QG_REFERENCE_CHECK=PASS")
    print(f"BIB_ENTRIES={len(entries)}")
    print(f"UNIQUE_DOIS={len(doi_owner)}")
    print(f"CITATION_MAP_KEYS={len(map_keys)}")
    print("METADATA_AUTHORITY=VERIFIED_FIELDS_ONLY")
    print("NOVELTY_AUTHORITY=NOT_GRANTED_BY_REFERENCE_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
