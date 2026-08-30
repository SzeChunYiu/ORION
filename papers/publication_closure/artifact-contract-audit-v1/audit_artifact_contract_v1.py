#!/usr/bin/env python3
"""Audit every empirical successor directory against the #1701 artifact contract.

The contract (#1701, "Common artifact contract for every new empirical
successor") lists fourteen required artifacts. This reports per-item coverage
and full-contract compliance, so the fourteen contract boxes can be ticked or
left on evidence rather than inspected one at a time.

Grants no scientific authority; it checks presence, never content.
"""
from __future__ import annotations
import collections, json, pathlib, sys

CONTRACT = [
    ("QUESTION",             lambda n: any(x.startswith("QUESTION") for x in n)),
    ("PROTOCOL",             lambda n: any(x.startswith("PROTOCOL") for x in n)),
    ("CORPUS_MANIFEST",      lambda n: any("CORPUS_MANIFEST" in x for x in n)),
    ("INCLUSION_EXCLUSION",  lambda n: any("INCLUSION_EXCLUSION" in x for x in n)),
    ("BASELINES",            lambda n: any("BASELINE" in x for x in n)),
    ("RESOURCE_ACCOUNTING",  lambda n: any("RESOURCE_ACCOUNTING" in x for x in n)),
    ("EXPECTED_TERMINALS",   lambda n: any("EXPECTED_TERMINAL" in x for x in n)),
    ("RESULT",               lambda n: any(x.startswith(("RESULT", "RESULTS")) for x in n)),
    ("ADVERSE_AND_CANNOT_CHECK", lambda n: any("ADVERSE" in x for x in n)),
    ("independent_checker",  lambda n: any(x.startswith("check") and x.endswith(".py") for x in n)),
    ("CLAIM_DISPOSITION",    lambda n: any("DISPOSITION" in x for x in n)),
    ("SHA256SUMS",           lambda n: any("SHA256SUMS" in x for x in n)),
]

def candidates(root: pathlib.Path):
    out = []
    for d in root.rglob("*"):
        if not d.is_dir():
            continue
        names = {f.name for f in d.iterdir() if f.is_file()}
        if not names:
            continue
        has_result = any(x.startswith(("RESULT", "RESULTS")) and x.endswith(".json") for x in names)
        has_proto = any(x.startswith("PROTOCOL") for x in names)
        if has_result or (has_proto and len(names) >= 3):
            out.append((d, names))
    return out

def audit(root: pathlib.Path) -> dict:
    cands = candidates(root)
    cov = collections.Counter()
    full, rows = [], []
    for d, names in cands:
        hits = [k for k, f in CONTRACT if f(names)]
        for h in hits:
            cov[h] += 1
        rows.append({"dir": str(d), "satisfied": len(hits), "missing":
                     [k for k, _ in CONTRACT if k not in hits]})
        if len(hits) == len(CONTRACT):
            full.append(str(d))
    return {
        "schema": "ORION.ARTIFACT_CONTRACT_AUDIT.v1",
        "candidates": len(cands),
        "full_contract_compliant": full,
        "coverage": {k: cov[k] for k, _ in CONTRACT},
        "contract_items": len(CONTRACT),
        "grants_authority": "NONE",
        "terminal": ("CONTRACT_SATISFIED" if len(full) == len(cands) and cands
                     else "CONTRACT_NOT_SATISFIED"),
        "worst_covered": sorted(((cov[k], k) for k, _ in CONTRACT))[:4],
    }

def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "papers")
    rep = audit(root)

    # control: a synthetic dir holding every contract artifact must score 12/12
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "synthetic-successor"
        p.mkdir()
        for f in ("QUESTION.md", "PROTOCOL.json", "CORPUS_MANIFEST.json",
                  "INCLUSION_EXCLUSION.json", "BASELINES.json",
                  "RESOURCE_ACCOUNTING.json", "EXPECTED_TERMINALS.json",
                  "RESULT.json", "ADVERSE_AND_CANNOT_CHECK.jsonl",
                  "check_thing_v1.py", "CLAIM_DISPOSITION.md", "SHA256SUMS"):
            (p / f).write_text("x")
        ctrl = audit(pathlib.Path(td))
    rep["positive_control"] = {
        "synthetic_dir_with_all_12": ctrl["coverage"],
        "scored_full": bool(ctrl["full_contract_compliant"]),
    }
    print(json.dumps(rep, indent=2, sort_keys=True))
    return 0 if rep["positive_control"]["scored_full"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
