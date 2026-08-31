#!/usr/bin/env python3
"""Triage which executed studies CAN be given a derived corpus definition.

The artifact-contract audit found CORPUS_MANIFEST / INCLUSION_EXCLUSION at 2/65.
This does not fix that: it says where a fix is possible from already-frozen data
and where it is not, so the repair effort goes where evidence exists.

It deliberately DOES NOT emit manifests. A key matching a heuristic is not a
corpus definition - the field has to be read and understood, and the result has
to balance against something independent. Auto-emitting would manufacture
exactly the evidence the contract exists to guarantee.
"""
from __future__ import annotations
import json, pathlib, sys

POP = ("task", "case", "row", "instance", "item", "unit", "corpus", "sample")
CNT = ("n_total", "count", "total", "parsed", "usable", "size")
EXC = ("exclud", "skip", "omit", "filter")

def scan(d: pathlib.Path):
    pop, exc = {}, {}
    for f in sorted(d.iterdir()):
        if not (f.is_file() and f.suffix == ".json"):
            continue
        try:
            o = json.loads(f.read_text())
        except Exception:
            continue
        def walk(o, path="", depth=0):
            if depth > 2 or not isinstance(o, dict):
                return
            for k, v in o.items():
                kl, p = k.lower(), f"{f.name}:{path}{k}"
                if isinstance(v, list) and len(v) >= 2 and any(s in kl for s in POP):
                    pop[p] = len(v)
                if isinstance(v, int) and v >= 2 and any(s in kl for s in CNT):
                    pop[p] = v
                if any(s in kl for s in EXC) and isinstance(v, (list, int)):
                    exc[p] = len(v) if isinstance(v, list) else v
                walk(v, p + ".", depth + 1)
        walk(o)
    return pop, exc

def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "papers")
    derivable, blocked, done = [], [], []
    for d in sorted(root.rglob("*")):
        if not d.is_dir():
            continue
        names = {f.name for f in d.iterdir() if f.is_file()}
        if not any("RESULT" in x.upper() and x.endswith(".json") for x in names):
            continue
        if any("CORPUS_MANIFEST" in x for x in names):
            done.append(str(d)); continue
        pop, exc = scan(d)
        rec = {"dir": str(d), "population_signals": len(pop),
               "exclusion_signals": len(exc),
               "strongest": sorted(pop.items(), key=lambda kv: -kv[1])[:3]}
        (derivable if pop else blocked).append(rec)
    out = {
        "schema": "ORION.CORPUS_DEFINITION_TRIAGE.v1",
        "executed_studies": len(derivable) + len(blocked) + len(done),
        "already_defined": done,
        "derivable_from_frozen_data": derivable,
        "not_derivable_no_population_signal": blocked,
        "counts": {"already": len(done), "derivable": len(derivable),
                   "blocked": len(blocked)},
        "emits_manifests": False,
        "why_not": ("a key matching a heuristic is not a corpus definition; each "
                    "derivation must be read and must balance against an "
                    "independent artifact, as ORION-03 round-2 does "
                    "(192 parsed = 191 usable + 1 excluded, cross-checked "
                    "against UPSTREAM_TABLE_V2 191 rows)"),
        "grants_authority": "NONE",
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
