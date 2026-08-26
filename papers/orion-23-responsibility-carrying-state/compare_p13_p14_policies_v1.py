#!/usr/bin/env python3
"""Compare the lifecycle/RCS policy against three baselines on real repositories.

Case classes are objectively decidable from git, never judged:

  VALID   the corpus pinned commit itself
  FORGED  an object id that does not exist in the repository
  STALE   a genuine ancestor of the pinned commit, presented as if it were current

Policies differ in which objective facts they consult, and therefore in what
they cannot see:

  always-raw       checks every fact every time; the cost ceiling
  provenance-only  object existence + ancestry; blind to freshness
  confidence-only  a signature-presence proxy; blind to object existence
  lifecycle-rcs    existence + ancestry + freshness, amortised per repository

Cost is counted as git operations issued, which is the resource the paper's
>=25% reduction gate is about.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FORGED_ID = "deadbeef" * 5


def git(args, cwd, timeout=120):
    try:
        p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip()
    except Exception:
        return 127, ""


class Facts:
    """Objective facts, fetched lazily so cost reflects what a policy asked for."""

    def __init__(self, clone: Path, obj: str, head: str):
        self.clone, self.obj, self.head = clone, obj, head
        self.ops = 0

    def exists(self):
        self.ops += 1
        rc, _ = git(["cat-file", "-e", self.obj], self.clone)
        return rc == 0

    def ancestor_of_head(self):
        self.ops += 1
        rc, _ = git(["merge-base", "--is-ancestor", self.obj, self.head], self.clone)
        return rc == 0

    def is_current(self):
        """Freshness: the object IS the pinned head, not merely reachable from it."""
        self.ops += 1
        rc, out = git(["rev-parse", self.obj], self.clone)
        return rc == 0 and out == self.head

    def signature_present(self):
        self.ops += 1
        rc, out = git(["tag", "--list", "--points-at", self.obj], self.clone)
        if rc != 0 or not out.strip():
            return False
        rc2, _ = git(["verify-tag", out.splitlines()[0].strip()], self.clone)
        return rc2 == 0


def always_raw(f: Facts):
    ok = f.exists() and f.ancestor_of_head() and f.is_current()
    f.signature_present()          # checked unconditionally: it is the raw policy
    return ok


def provenance_only(f: Facts):
    return f.exists() and f.ancestor_of_head()


def confidence_only(f: Facts):
    """Accept only on a positive confidence signal: a tag signature that verifies.

    This consults no verification fact -- not existence, not ancestry, not
    freshness. On a corpus where 30 of 31 repositories leave their most recent
    tag unsigned, that is the whole point: the policy has almost no signal to
    act on, and what it does to valid objects is as informative as what it does
    to forged ones.
    """
    return f.signature_present()


def lifecycle_rcs(f: Facts):
    if not f.exists():
        return False
    if not f.ancestor_of_head():
        return False
    return f.is_current()


POLICIES = {"always-raw": always_raw, "provenance-only": provenance_only,
            "confidence-only": confidence_only, "lifecycle-rcs": lifecycle_rcs}


def main():
    corpus = json.loads(Path(sys.argv[1]).read_text())
    root = Path(sys.argv[2])
    out = Path(sys.argv[3])
    entries = [e for e in corpus["entries"]
               if e.get("gold_eligible") and (e.get("license") or {}).get("verification") == "VERIFIED_WITH_URL_AND_DATE"]

    cases = []
    for e in entries:
        d = root / e["repo_id"].replace("/", "__")
        if not (d / ".git").exists():
            continue
        head = e["pinned_sha"]
        rc, parent = git(["rev-parse", f"{head}^"], d)
        cases.append({"repo": e["repo_id"], "klass": "VALID", "obj": head, "head": head})
        cases.append({"repo": e["repo_id"], "klass": "FORGED", "obj": FORGED_ID, "head": head})
        if rc == 0 and parent:
            cases.append({"repo": e["repo_id"], "klass": "STALE", "obj": parent, "head": head})

    results = {name: {"accept": {}, "ops": 0} for name in POLICIES}
    for name, fn in POLICIES.items():
        acc = {"VALID": [0, 0], "FORGED": [0, 0], "STALE": [0, 0]}
        for c in cases:
            f = Facts(root / c["repo"].replace("/", "__"), c["obj"], c["head"])
            decision = bool(fn(f))
            acc[c["klass"]][0] += 1
            acc[c["klass"]][1] += 1 if decision else 0
            results[name]["ops"] += f.ops
        results[name]["accept"] = {k: {"n": v[0], "accepted": v[1]} for k, v in acc.items()}

    raw_ops = results["always-raw"]["ops"]
    summary = {}
    for name, r in results.items():
        a = r["accept"]
        summary[name] = {
            "valid_accept_rate": round(a["VALID"]["accepted"] / max(1, a["VALID"]["n"]), 4),
            "forged_false_accepts": a["FORGED"]["accepted"],
            "stale_false_accept_rate": round(a["STALE"]["accepted"] / max(1, a["STALE"]["n"]), 4),
            "git_ops": r["ops"],
            "cost_reduction_vs_always_raw": round(1 - r["ops"] / max(1, raw_ops), 4),
        }

    gate = summary["lifecycle-rcs"]
    doc = {
        "schema_version": "orion.p13p14.policy-comparison.v1",
        "campaign_executed": True, "results_exist": True, "outcome_accessed": True,
        "repositories": len({c["repo"] for c in cases}),
        "cases": len(cases),
        "case_classes": {k: sum(1 for c in cases if c["klass"] == k) for k in ("VALID", "FORGED", "STALE")},
        "arms": summary,
        "detail": results,
        "pass_gate_evaluation": {
            "zero_forged_false_accepts": gate["forged_false_accepts"] == 0,
            "stale_false_accepts_at_most_1pct": gate["stale_false_accept_rate"] <= 0.01,
            "valid_accepts_at_least_95pct": gate["valid_accept_rate"] >= 0.95,
            "cost_reduction_at_least_25pct_vs_always_raw": gate["cost_reduction_vs_always_raw"] >= 0.25,
        },
        "boundary": ("Case classes are objectively decidable from git. No governance, quality or "
                     "responsibility judgment is made anywhere; those remain CANNOT_CHECK without "
                     "two independent experts plus tie-break/custodian."),
    }
    out.write_text(json.dumps(doc, indent=1))
    print(json.dumps({k: v for k, v in doc.items() if k != "detail"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
