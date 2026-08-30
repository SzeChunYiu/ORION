#!/usr/bin/env python3
"""ORION-08 submission gate: independent replay of the final cited receipts.

`JOURNAL_READINESS.md` lists "independent replay of the final cited receipts" as an open
submission gate. This closes it by re-deriving each committed receipt from its own
generator and comparing, rather than asserting reproducibility at manuscript level.

Comparison is on canonicalised JSON (sorted keys, tight separators) so that formatting
differences cannot mask, or manufacture, a mismatch. Where a committed artifact carries
provenance keys its generator does not emit, those keys are reported explicitly rather
than ignored -- an extra key is a real difference between the file and what the code
produces, even when every shared value agrees.

Exit codes
  0  REPLAY_EXACT       every shared value agrees for every receipt
  1  REPLAY_DIVERGENT   at least one shared value differs
  3  CANNOT_CHECK       a generator or committed artifact is missing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

EXIT_EXACT, EXIT_DIVERGENT, EXIT_CANNOT_CHECK = 0, 1, 3

PAPER = "papers/orion-08-typed-state"
RECEIPTS = [
    {
        "name": "publication_paired_analysis",
        "generator": f"{PAPER}/publication_analysis.py",
        "args": [],
        "committed": f"{PAPER}/PUBLICATION_PAIRED_ANALYSIS_V1.json",
    },
    {
        "name": "binding_sufficiency_lattice",
        "generator": f"{PAPER}/theory/binding-sufficiency-lattice-v1/independent_checker/check_binding_sufficiency.py",
        "args": [],
        "committed": f"{PAPER}/theory/binding-sufficiency-lattice-v1/RESULT.json",
    },
    {
        "name": "familywise_multiplicity",
        "generator": f"{PAPER}/analysis/familywise-multiplicity-v1/check_familywise_multiplicity_v1.py",
        "args": ["--source", f"{PAPER}/PUBLICATION_PAIRED_ANALYSIS_V1.json"],
        "committed": f"{PAPER}/analysis/familywise-multiplicity-v1/FAMILYWISE_MULTIPLICITY_V1.json",
        # This generator writes its result to --emit rather than stdout. Reading stdout
        # here would report a false CANNOT_CHECK, so the harness honours the convention.
        "emit_flag": "--emit",
    },
]


def _repo_root(start: str) -> str:
    d = os.path.abspath(start)
    while d != "/":
        # .git is a directory in a clone and a FILE inside a git worktree.
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def digest(o) -> str:
    return hashlib.sha256(canon(o).encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", default="")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    root = _repo_root(os.path.dirname(os.path.abspath(__file__)))
    rows, divergent, uncheckable = [], [], []

    for r in RECEIPTS:
        gen = os.path.join(root, r["generator"])
        com = os.path.join(root, r["committed"])
        if not os.path.isfile(gen) or not os.path.isfile(com):
            uncheckable.append(r["name"])
            rows.append({"receipt": r["name"], "status": "CANNOT_CHECK",
                         "reason": "GENERATOR_OR_ARTIFACT_ABSENT"})
            continue
        emit_path = None
        cmd = [sys.executable, gen, *r["args"]]
        if r.get("emit_flag"):
            emit_path = os.path.join(tempfile.mkdtemp(), "emit.json")
            cmd += [r["emit_flag"], emit_path]
        proc = subprocess.run(
            cmd, capture_output=True, text=True, cwd=root, timeout=args.timeout)
        try:
            if emit_path:
                replayed = json.load(open(emit_path, encoding="utf-8"))
            else:
                replayed = json.loads(proc.stdout)
        except Exception as exc:
            uncheckable.append(r["name"])
            rows.append({"receipt": r["name"], "status": "CANNOT_CHECK",
                         "reason": f"GENERATOR_OUTPUT_NOT_JSON: {exc}",
                         "generator_exit": proc.returncode})
            continue
        committed = json.load(open(com, encoding="utf-8"))
        ka, kb = set(replayed), set(committed)
        differing = sorted(k for k in ka & kb if canon(replayed[k]) != canon(committed[k]))
        row = {
            "receipt": r["name"],
            "generator": r["generator"],
            "committed": r["committed"],
            "generator_exit": proc.returncode,
            "replay_digest": digest(replayed)[:16],
            "committed_digest": digest(committed)[:16],
            "identical": digest(replayed) == digest(committed),
            "shared_keys_differing": differing,
            "committed_only_keys": sorted(kb - ka),
            "replay_only_keys": sorted(ka - kb),
        }
        row["status"] = "EXACT" if not differing else "DIVERGENT"
        if differing:
            divergent.append(r["name"])
        rows.append(row)

    out = {
        "checker": "orion08_independent_replay_v1",
        "gate": "independent replay of the final cited receipts",
        "receipts": rows,
        "summary": {
            "total": len(RECEIPTS),
            "exact": sum(1 for x in rows if x.get("status") == "EXACT"),
            "divergent": len(divergent),
            "cannot_check": len(uncheckable),
        },
        "note": (
            "A committed artifact may carry provenance keys its generator does not emit; "
            "those are reported under committed_only_keys rather than silently accepted."
        ),
    }
    if uncheckable:
        out["status"] = "CANNOT_CHECK"
        rc = EXIT_CANNOT_CHECK
    elif divergent:
        out["status"] = "REPLAY_DIVERGENT"
        rc = EXIT_DIVERGENT
    else:
        out["status"] = "REPLAY_EXACT"
        rc = EXIT_EXACT
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
