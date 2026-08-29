#!/usr/bin/env python3
"""ORION-17 rule-disagreement cohort selector (outcome-blind).

Enumerates PyPI projects in a FIXED external order (download rank, descending)
and measures modules / internal import edges with the campaign's own
`build_import_graph`. Computes NO policy outcome: the only symbol imported from
the campaign is `build_import_graph`, exactly as `o17_density.py` does.

Stratum assignment is mechanical. Every candidate examined is written to the
JSONL log with its measured counts, including rejects.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from measure_p7 import build_import_graph  # noqa: E402  (ONLY this symbol)

REPOS = HERE / "repos"
REPOS.mkdir(parents=True, exist_ok=True)
LOG = HERE / "o17_candidates.jsonl"

# The 8 calibration+evaluation projects. Reuse is FORBIDDEN by the protocol.
FORBIDDEN = {"numpy", "scipy", "flask", "requests", "networkx", "django",
             "tornado", "sympy"}
FORBIDDEN_REPOS = {
    "numpy/numpy", "scipy/scipy", "pallets/flask", "psf/requests",
    "networkx/networkx", "django/django", "tornadoweb/tornado", "sympy/sympy",
}

# Frozen thresholds (historical constants; NOT re-derived here).
DENSITY_T, MODULE_T, EDGE_T = 1.5, 49, 216


def stratum(m, e):
    """Mechanical stratum assignment from the frozen criteria."""
    if m <= 0:
        return None
    d = e / m
    if d >= DENSITY_T and m < MODULE_T and e < EDGE_T:
        return "small_fewedge_dense"
    if d < DENSITY_T and m >= MODULE_T and e >= EDGE_T:
        return "large_manyedge_sparse"
    return None


def sh(args, cwd=None, timeout=300):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def pypi_repo(project):
    """Resolve project -> github owner/repo from the PyPI JSON API."""
    url = f"https://pypi.org/pypi/{project}/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "orion17-selector"})
        with urllib.request.urlopen(req, timeout=30) as r:
            info = json.load(r).get("info", {})
    except Exception as exc:
        return None, f"pypi_api:{type(exc).__name__}"
    cands = []
    for k, v in (info.get("project_urls") or {}).items():
        if v:
            cands.append((k.lower(), v))
    if info.get("home_page"):
        cands.append(("home_page", info["home_page"]))
    pref = ("source", "repository", "code", "github", "home")
    cands.sort(key=lambda kv: min([i for i, p in enumerate(pref) if p in kv[0]] or [99]))
    for _, v in cands:
        m = re.search(r"github\.com/([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)", v)
        if m:
            owner, repo = m.group(1), m.group(2)
            if repo.endswith(".git"):
                repo = repo[:-4]
            return f"{owner}/{repo}", None
    return None, "no_github_url"


def find_pkg_dir(root, project):
    """Locate the importable package directory inside a checkout.

    General rule (revised once, 2026-08-29, BEFORE any outcome existed, because
    the first heuristic silently dropped 21 of the 90 candidates it saw, whose import name
    differs from their PyPI project name -- a systematic exclusion unrelated to
    any outcome):
      1. prefer a top-level package whose name matches the normalised project
         name, under the repo root or ./src;
      2. otherwise, if exactly one top-level package exists there, take it;
      3. otherwise reject as ambiguous, and record that.
    """
    base = project.lower().replace("-", "_").replace(".", "_")
    alts = [base, project.lower().replace("-", ""), project.lower(),
            base.replace("python_", ""), base.replace("py_", "")]
    for a in dict.fromkeys(alts):
        for cand in (a, f"src/{a}"):
            p = root / cand
            if p.is_dir() and (p / "__init__.py").exists():
                return cand
    skip = {"test", "tests", "doc", "docs", "example", "examples", "bench",
            "benchmark", "benchmarks", "script", "scripts", "tool", "tools",
            "util", "utils", "contrib", "build", "dist", "vendor", "third_party"}
    for parent, prefix in ((root, ""), (root / "src", "src/")):
        if not parent.is_dir():
            continue
        pkgs = [d.name for d in sorted(parent.iterdir())
                if d.is_dir() and (d / "__init__.py").exists()
                and d.name.lower() not in skip and not d.name.startswith(".")]
        if len(pkgs) == 1:
            return f"{prefix}{pkgs[0]}"
        if len(pkgs) > 1:
            return None
    return None


def measure(project, slug):
    """Shallow-clone, pin SHA, measure counts, delete checkout."""
    d = REPOS / project.replace("/", "_")
    sh(["rm", "-rf", str(d)])
    d.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{slug}"
    rc, _, err = sh(["git", "clone", "-q", "--depth", "1",
                     "--filter=blob:none", url, str(d)], timeout=300)
    if rc:
        sh(["rm", "-rf", str(d)])
        return {"usable": False, "reason": f"clone_failed:{err.strip()[:80]}"}
    rc, sha, _ = sh(["git", "rev-parse", "HEAD"], cwd=d)
    sha = sha.strip()
    pkg = find_pkg_dir(d, project)
    if pkg is None:
        sh(["rm", "-rf", str(d)])
        return {"usable": False, "reason": "package_dir_not_found", "sha": sha}
    try:
        mods, edges = build_import_graph(d, pkg)
        m, e = len(mods), sum(len(v) for v in edges.values())
    except Exception as exc:
        sh(["rm", "-rf", str(d)])
        return {"usable": False, "reason": f"build_failed:{type(exc).__name__}", "sha": sha}
    sh(["rm", "-rf", str(d)])
    return {"usable": True, "sha": sha, "package": pkg, "modules": m,
            "import_edges": e,
            "edges_per_module": round(e / m, 4) if m else None}


def main():
    """Measure one shard of the fixed rank-ordered enumeration.

    Shards do NOT apply the acceptance rule; they only measure. Acceptance
    ("first N qualifying in rank order") is applied once, at merge time, over
    the union of shards sorted by rank -- which is identical to what a single
    sequential pass would have selected.
    """
    shard = int(os.environ.get("O17_SHARD", "0"))
    nshards = int(os.environ.get("O17_NSHARDS", "1"))
    start = int(os.environ.get("O17_START", "0"))
    limit = int(os.environ.get("O17_LIMIT", "400"))
    rows = json.load(open(HERE / "top-pypi.json"))["rows"]
    log = HERE / f"shard_{shard:02d}.jsonl"

    seen = set()
    if log.exists():
        for line in log.read_text().splitlines():
            if line.strip():
                seen.add(json.loads(line)["project"])

    examined = 0
    for idx, row in enumerate(rows[start:start + limit]):
        if idx % nshards != shard:
            continue
        rank = start + idx + 1
        project = row["project"]
        if project in seen:
            continue
        rec = {"rank": rank, "project": project,
               "download_count": row["download_count"]}
        if project.lower() in FORBIDDEN:
            rec.update({"usable": False, "reason": "FORBIDDEN_dev_eval_repo"})
        else:
            slug, err = pypi_repo(project)
            if slug is None:
                rec.update({"usable": False, "reason": err})
            elif slug.lower() in {f.lower() for f in FORBIDDEN_REPOS}:
                rec.update({"usable": False, "reason": "FORBIDDEN_dev_eval_repo",
                            "repo": slug})
            else:
                rec["repo"] = slug
                rec.update(measure(project, slug))
        if rec.get("usable"):
            rec["stratum"] = stratum(rec["modules"], rec["import_edges"])
        with log.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        examined += 1
        if examined % 25 == 0:
            print(f"shard{shard} examined={examined} rank={rank}", flush=True)
    print(json.dumps({"stage": "MEASURE_ONLY__NO_POLICY_OUTCOME_COMPUTED",
                      "shard": shard, "examined": examined}))


if __name__ == "__main__":
    main()
