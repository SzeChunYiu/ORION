#!/usr/bin/env python3
"""Re-measure candidates lost to ENOSPC, using sparse checkouts.

The parallel sweep filled the disk while cloning very large generated monorepos
(google-cloud-python, azure-sdk-for-python). Those failures are NOT random: they
hit large repositories, which is exactly the population the sparse stratum draws
from, so leaving them out would bias stratum B.

This pass re-measures them one at a time with `--sparse`, so only the package
subtree's blobs are fetched, and with a free-space guard before each clone.
Outcomes are appended to a separate shard file so the rank-ordered merge picks
them up. Anything still unmeasurable is recorded as a reason, never as a pass.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from measure_p7 import build_import_graph  # noqa: E402
from select_o17 import FORBIDDEN, FORBIDDEN_REPOS, stratum  # noqa: E402

WORK = HERE / "repair_work"
OUT = HERE / "shard_90_repair.jsonl"
MIN_FREE_GB = 1.5
SKIP = {"test", "tests", "doc", "docs", "example", "examples", "bench",
        "benchmark", "benchmarks", "script", "scripts", "tool", "tools",
        "util", "utils", "contrib", "build", "dist", "vendor", "third_party"}


def free_gb():
    st = os.statvfs("/")
    return st.f_bavail * st.f_frsize / 1e9


def sh(a, cwd=None, t=900):
    try:
        p = subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=t)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def pkg_dir_from_tree(d, project):
    """Find the package dir from the git tree, without checking anything out."""
    rc, out, _ = sh(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=d)
    if rc:
        return None
    inits = [p for p in out.splitlines() if p.endswith("__init__.py")]
    tops = {}
    for p in inits:
        parts = p.split("/")
        if len(parts) == 2:
            tops.setdefault(parts[0], 0)
            tops[parts[0]] += 1
        elif len(parts) == 3 and parts[0] == "src":
            tops.setdefault("src/" + parts[1], 0)
            tops["src/" + parts[1]] += 1
    base = project.lower().replace("-", "_").replace(".", "_")
    for cand in (base, f"src/{base}", project.lower(),
                 project.lower().replace("-", "")):
        if cand in tops:
            return cand
    plain = [k for k in tops if k.split("/")[-1].lower() not in SKIP]
    return plain[0] if len(plain) == 1 else None


def measure_sparse(project, slug):
    d = WORK / project.replace("/", "_")
    shutil.rmtree(d, ignore_errors=True)
    if free_gb() < MIN_FREE_GB:
        return {"usable": False, "reason": "repair_skipped_low_disk"}
    rc, _, err = sh(["git", "clone", "-q", "--depth", "1", "--filter=blob:none",
                     "--sparse", f"https://github.com/{slug}", str(d)])
    if rc:
        shutil.rmtree(d, ignore_errors=True)
        return {"usable": False, "reason": f"clone_failed:{err.strip()[:70]}"}
    _, sha, _ = sh(["git", "rev-parse", "HEAD"], cwd=d)
    pkg = pkg_dir_from_tree(d, project)
    if not pkg:
        shutil.rmtree(d, ignore_errors=True)
        return {"usable": False, "reason": "package_dir_not_found", "sha": sha.strip()}
    rc, _, err = sh(["git", "sparse-checkout", "set", pkg], cwd=d)
    if rc:
        shutil.rmtree(d, ignore_errors=True)
        return {"usable": False, "reason": f"sparse_failed:{err.strip()[:70]}",
                "sha": sha.strip()}
    try:
        mods, edges = build_import_graph(d, pkg)
        m, e = len(mods), sum(len(v) for v in edges.values())
    except Exception as exc:
        shutil.rmtree(d, ignore_errors=True)
        return {"usable": False, "reason": f"build_failed:{type(exc).__name__}"}
    shutil.rmtree(d, ignore_errors=True)
    if m == 0:
        return {"usable": False, "reason": "sparse_checkout_yielded_no_modules",
                "sha": sha.strip()}
    return {"usable": True, "sha": sha.strip(), "package": pkg, "modules": m,
            "import_edges": e, "edges_per_module": round(e / m, 4),
            "measured_via": "sparse_checkout_repair"}


def main():
    rows = []
    for f in sorted(glob.glob(str(HERE / "shard_*.jsonl"))):
        if "repair" in f:
            continue
        for line in open(f):
            if line.strip():
                rows.append(json.loads(line))
    lost = [r for r in rows if not r.get("usable")
            and "No space left" in str(r.get("reason", ""))]
    lost.sort(key=lambda r: r["rank"])
    done = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["project"])
    WORK.mkdir(parents=True, exist_ok=True)
    print(f"ENOSPC-lost candidates to repair: {len(lost)}", flush=True)

    for r in lost:
        if r["project"] in done:
            continue
        rec = {"rank": r["rank"], "project": r["project"],
               "download_count": r.get("download_count"), "repo": r.get("repo"),
               "repair_pass": True}
        if r["project"].lower() in FORBIDDEN or \
           str(r.get("repo", "")).lower() in {f.lower() for f in FORBIDDEN_REPOS}:
            rec.update({"usable": False, "reason": "FORBIDDEN_dev_eval_repo"})
        else:
            rec.update(measure_sparse(r["project"], r["repo"]))
        if rec.get("usable"):
            rec["stratum"] = stratum(rec["modules"], rec["import_edges"])
        with OUT.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"[{rec['rank']:5d}] {rec['project']:38s} "
              f"{'m=%d e=%d d=%.3f' % (rec['modules'], rec['import_edges'], rec['edges_per_module']) if rec.get('usable') else rec.get('reason','')[:40]}"
              f"  stratum={rec.get('stratum')}  free={free_gb():.1f}GB", flush=True)
    shutil.rmtree(WORK, ignore_errors=True)


if __name__ == "__main__":
    main()
