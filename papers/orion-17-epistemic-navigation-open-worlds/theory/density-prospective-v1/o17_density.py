#!/usr/bin/env python3
"""Density-only pass for ORION-17's prospective test.

Computes modules and declared import edges for held-out packages using the
campaign's own build_import_graph. Deliberately computes NO policy outcome:
the prediction must be stamped from graph structure alone.
"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, "/tmp/o17")
from measure_p7_closure_retention_v1 import build_import_graph

ROOT = Path("/tmp/o17/repos"); ROOT.mkdir(parents=True, exist_ok=True)
HELD_OUT = [("sympy", "https://github.com/sympy/sympy", "sympy"),
            ("requests", "https://github.com/psf/requests", "src/requests"),
            ("networkx", "https://github.com/networkx/networkx", "networkx"),
            ("django", "https://github.com/django/django", "django"),
            ("tornado", "https://github.com/tornadoweb/tornado", "tornado")]

def sh(a, cwd=None): 
    p = subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=1800)
    return p.returncode, p.stderr

out = []
for name, url, pkg in HELD_OUT:
    d = ROOT / name
    if not (d / ".git").exists():
        d.mkdir(parents=True, exist_ok=True)
        sh(["git", "init", "-q", "--initial-branch=main", str(d)])
        sh(["git", "remote", "add", "origin", url], cwd=d)
        rc, e = sh(["git", "fetch", "-q", "--filter=blob:none", "--depth", "800", "origin", "HEAD"], cwd=d)
        if rc: out.append({"domain": name, "usable": False, "reason": e[:120]}); continue
        sh(["git", "checkout", "-q", "FETCH_HEAD"], cwd=d)
    if not (d / pkg).is_dir():
        out.append({"domain": name, "usable": False, "reason": f"package dir {pkg} absent"}); continue
    mods, edges = build_import_graph(d, pkg)
    m, e = len(mods), sum(len(v) for v in edges.values())
    out.append({"domain": name, "package": pkg, "usable": True, "modules": m,
                "import_edges": e, "edges_per_module": round(e / m, 4) if m else None})
print(json.dumps({"stage": "DENSITY_ONLY__NO_POLICY_OUTCOME_COMPUTED", "held_out": out}, indent=1))
Path("/tmp/o17/DENSITY.json").write_text(json.dumps({"stage": "DENSITY_ONLY", "held_out": out}, indent=1) + "\n")
