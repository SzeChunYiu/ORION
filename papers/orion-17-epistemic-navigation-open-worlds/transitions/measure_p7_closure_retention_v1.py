#!/usr/bin/env python3
"""P7 closure retention across transitions in non-retrieval domains.

A closure is the premise set a conclusion was established over. A TRANSITION is
one version-to-version step. After a transition the closure either still holds
(PRESERVE) or must be reopened (REOPEN).

P7's gate asks three things, and they pull against each other:

  zero false closure retention   never preserve a closure whose premises moved
  both outcomes occur            a policy that always reopens, or never does,
                                 has not been tested by the data
  fewer unnecessary reopenings   reopening a closure whose premises did NOT
    than the donor baseline      move is wasted work, and the donor baseline is
                                 the bar to beat

The third is what makes the first two non-trivial: always-reopen achieves zero
false retention by refusing to preserve anything, and is useless for exactly
that reason. Reporting all three together is the point.

Domains are non-retrieval by construction: Python package import structure, not
search or ranking.
"""


from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def git(args, cwd, timeout=300):
    try:
        p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout
    except Exception:
        return 127, ""


def module_name(root: Path, path: Path) -> str | None:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None
    if rel.suffix != ".py":
        return None
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else None


def build_import_graph(root: Path, pkg: str):
    """Direct import edges among modules of one package, parsed with ast."""
    mods: dict[str, Path] = {}
    for p in (root / pkg).rglob("*.py"):
        m = module_name(root, p)
        if m:
            mods[m] = p
    edges: dict[str, set[str]] = defaultdict(set)
    for m, p in mods.items():
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name in mods:
                        edges[m].add(a.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level:                       # relative import
                    base = m.split(".")[: max(0, len(m.split(".")) - node.level + 1)]
                    prefix = ".".join(base + ([node.module] if node.module else []))
                else:
                    prefix = node.module or ""
                for cand in (prefix, *(f"{prefix}.{a.name}" for a in node.names)):
                    if cand in mods:
                        edges[m].add(cand)
    return mods, edges


def transitive_reads(mods, edges):
    """Read-set of each module: itself plus everything it transitively imports."""
    reads: dict[str, set[str]] = {}

    def walk(m, seen):
        if m in reads:
            return reads[m]
        if m in seen:
            return set()
        seen.add(m)
        acc = {m}
        for d in edges.get(m, ()):
            acc |= walk(d, seen)
        reads[m] = acc
        return acc

    for m in mods:
        walk(m, set())
    return reads


def main():
    root = Path(sys.argv[1])
    out = Path(sys.argv[2])
    domains = json.loads(sys.argv[3])          # [{"repo_dir":..., "pkg":...}, ...]
    n_changes = int(sys.argv[4]) if len(sys.argv) > 4 else 120

    report = {"schema_version": "orion.p7.closure-retention-transitions.v1",
              "campaign_executed": True, "results_exist": True, "outcome_accessed": True,
              "domains": []}

    for spec in domains:
        d = root / spec["repo_dir"]
        pkg = spec["pkg"]
        if not (d / ".git").exists() or not (d / pkg).is_dir():
            report["domains"].append({"domain": spec["repo_dir"], "usable": False,
                                      "reason": "clone or package directory absent"})
            continue
        mods, edges = build_import_graph(d, pkg)
        reads = transitive_reads(mods, edges)
        rc, log = git(["log", f"-{n_changes}", "--format=%H", "--", pkg], d)
        commits = [c for c in log.split() if c][:n_changes]

        stats = {p: {"retained": 0, "retained_invalid": 0, "discarded": 0,
                     "unnecessary_reopen": 0}
                 for p in ("always-reopen", "donor-coarse", "exact-containment")}
        used = 0
        for sha in commits:
            rc, files = git(["show", "--name-only", "--format=", sha], d)
            changed = {module_name(d, d / f.strip()) for f in files.splitlines() if f.strip()}
            changed = {c for c in changed if c in mods}
            if not changed:
                continue
            used += 1
            changed_pkgs = {c.split(".")[1] if c.count(".") >= 1 else c for c in changed}
            for m in mods:
                invalid = bool(reads[m] & changed)          # ground truth
                keep = {
                    "always-reopen": False,
                    "donor-coarse": (m.split(".")[1] if m.count(".") >= 1 else m) not in changed_pkgs,
                    "exact-containment": not invalid,
                }
                for pol, k in keep.items():
                    if k:
                        stats[pol]["retained"] += 1
                        if invalid:
                            stats[pol]["retained_invalid"] += 1
                    else:
                        stats[pol]["discarded"] += 1
                        if not invalid:
                            stats[pol]["unnecessary_reopen"] += 1

        total = sum(stats["always-reopen"].values()) // 4 if used else 0
        dom = {"domain": spec["repo_dir"], "package": pkg, "usable": True,
               "modules": len(mods), "import_edges": sum(len(v) for v in edges.values()),
               "commits_examined": len(commits), "changes_used": used,
               "certificate_decisions": used * len(mods),
               "policies": {}}
        base = stats["always-reopen"]["retained"]
        for pol, s in stats.items():
            denom = max(1, used * len(mods))
            # P7 vocabulary over the same decisions:
            #   preserve                 = retained
            #   reopen                   = discarded
            #   false closure retention  = preserved while premises moved
            #   unnecessary reopening    = reopened while premises did NOT move
            unnecessary = s["unnecessary_reopen"]
            dom["policies"][pol] = {
                "preserve": s["retained"],
                "reopen": s["discarded"],
                "false_closure_retention": s["retained_invalid"],
                "unnecessary_reopenings": unnecessary,
                "preserve_rate": round(s["retained"] / denom, 4),
                "both_outcomes_occur": s["retained"] > 0 and s["discarded"] > 0,
            }
        report["domains"].append(dom)

    usable = [d for d in report["domains"] if d.get("usable")]
    exact = "exact-containment"; donor = "donor-coarse"
    report["summary"] = {
        "domains_usable": len(usable),
        "transitions_per_domain": {d["domain"]: d["changes_used"] for d in usable},
        "zero_false_closure_retention": {d["domain"]: d["policies"][exact]["false_closure_retention"] == 0
                                         for d in usable},
        "donor_false_closure_retention": {d["domain"]: d["policies"][donor]["false_closure_retention"]
                                          for d in usable},
        "both_outcomes_occur": {d["domain"]: d["policies"][exact]["both_outcomes_occur"] for d in usable},
        "unnecessary_reopenings": {d["domain"]: {p: d["policies"][p]["unnecessary_reopenings"]
                                                 for p in d["policies"]} for d in usable},
        "fewer_unnecessary_reopenings_than_donor": {
            d["domain"]: d["policies"][exact]["unnecessary_reopenings"]
                          < d["policies"][donor]["unnecessary_reopenings"] for d in usable},
    }
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps(report["summary"], indent=1))
    for d in usable:
        print(f"\n{d['domain']} ({d['package']}): {d['modules']} modules, "
              f"{d['import_edges']} edges, {d['changes_used']} transitions")
        for pol, s in d["policies"].items():
            print(f"   {pol:18s} preserve={s['preserve']:>8d} reopen={s['reopen']:>8d} "
                  f"false_retention={s['false_closure_retention']:>6d} "
                  f"unnecessary_reopen={s['unnecessary_reopenings']:>8d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
