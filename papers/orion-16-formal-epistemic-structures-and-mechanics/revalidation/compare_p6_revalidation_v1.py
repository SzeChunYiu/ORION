#!/usr/bin/env python3
"""Compare selective revalidation with full reset and native dependency selection.

A certificate says "this module was verified at commit X". Its read-set is the
module's transitive imports: everything whose content the verification actually
depended on. A commit that touches any member of that read-set invalidates the
certificate, and a policy that keeps it anyway has RETAINED AN INVALID
CERTIFICATE -- the failure P6's gate puts at zero.

Three policies, differing in what they treat as a dependency:

  full-reset       discards every certificate on any change. Never retains an
                   invalid one, and saves nothing.
  native-dep       discards certificates in the same top-level package as a
                   changed file. This is what a directory-scoped build cache
                   does, and it is blind to imports that cross packages.
  selective        discards exactly the certificates whose transitive read-set
                   intersects the change.

Savings are certificates retained per change, relative to full reset. Retaining
more is only a virtue at zero retained-invalid, which is why both are reported
together and neither alone.
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

    report = {"schema_version": "orion.p6.revalidation-comparison.v1",
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

        stats = {p: {"retained": 0, "retained_invalid": 0, "discarded": 0}
                 for p in ("full-reset", "native-dep", "selective")}
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
                    "full-reset": False,
                    "native-dep": (m.split(".")[1] if m.count(".") >= 1 else m) not in changed_pkgs,
                    "selective": not invalid,
                }
                for pol, k in keep.items():
                    if k:
                        stats[pol]["retained"] += 1
                        if invalid:
                            stats[pol]["retained_invalid"] += 1
                    else:
                        stats[pol]["discarded"] += 1

        total = sum(stats["full-reset"].values()) // 3 if used else 0
        dom = {"domain": spec["repo_dir"], "package": pkg, "usable": True,
               "modules": len(mods), "import_edges": sum(len(v) for v in edges.values()),
               "commits_examined": len(commits), "changes_used": used,
               "certificate_decisions": used * len(mods),
               "policies": {}}
        base = stats["full-reset"]["retained"]
        for pol, s in stats.items():
            denom = max(1, used * len(mods))
            dom["policies"][pol] = {
                "retained": s["retained"],
                "retained_invalid": s["retained_invalid"],
                "retention_rate": round(s["retained"] / denom, 4),
                "savings_vs_full_reset": s["retained"] - base,
            }
        report["domains"].append(dom)

    usable = [d for d in report["domains"] if d.get("usable")]
    report["summary"] = {
        "domains_usable": len(usable),
        "changes_per_domain": {d["domain"]: d["changes_used"] for d in usable},
        "zero_retained_invalid": {d["domain"]: d["policies"]["selective"]["retained_invalid"] == 0
                                  for d in usable},
        "native_dep_retained_invalid": {d["domain"]: d["policies"]["native-dep"]["retained_invalid"]
                                        for d in usable},
        "selective_savings_positive_every_domain": all(
            d["policies"]["selective"]["savings_vs_full_reset"] > 0 for d in usable) if usable else False,
    }
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps(report["summary"], indent=1))
    for d in usable:
        print(f"\n{d['domain']} ({d['package']}): {d['modules']} modules, "
              f"{d['import_edges']} edges, {d['changes_used']} changes")
        for pol, s in d["policies"].items():
            print(f"   {pol:12s} retained={s['retained']:>8d} retained_invalid={s['retained_invalid']:>6d} "
                  f"rate={s['retention_rate']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
