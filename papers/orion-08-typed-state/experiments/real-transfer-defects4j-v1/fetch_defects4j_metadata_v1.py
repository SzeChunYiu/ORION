#!/usr/bin/env python3
"""Fetch Defects4J metadata and report STRUCTURE ONLY.

No catch rate, no utility, no terminal. This runs before the scoring script so
that a degenerate binding can be found and amended from structural facts alone,
with no outcome visible.
"""
from __future__ import annotations
import json, os, sys, urllib.request, urllib.error
from collections import defaultdict

PIN = os.environ.get("D4J_PIN", "master")
BASE = f"https://raw.githubusercontent.com/rjust/defects4j/{PIN}/framework/projects"
CACHE = os.path.expanduser("~/d4j_cache")
os.makedirs(CACHE, exist_ok=True)

PROJECTS = ["Lang","Math","Time","Chart","Closure","Mockito","Cli","Codec",
            "Collections","Compress","Csv","Gson"]

def get(url, key):
    p = os.path.join(CACHE, key.replace("/", "__"))
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            t = r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        t = f"__HTTP_{e.code}__"
    except Exception as e:
        t = f"__ERR_{type(e).__name__}__"
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(t)
    return t

def missing(t): return t.startswith("__HTTP_") or t.startswith("__ERR_")

def parse_classes(t):
    return sorted({ln.strip() for ln in t.splitlines() if ln.strip() and "." in ln})

def parse_triggers(t):
    out = set()
    for ln in t.splitlines():
        ln = ln.strip().lstrip("-").strip()
        if "::" in ln:
            out.add(ln.split("::", 1)[0].strip())
    return sorted(out)

def pkg(fqn, n=3):
    return ".".join(fqn.split(".")[:n])

data = {}
for proj in PROJECTS:
    ab = get(f"{BASE}/{proj}/active-bugs.csv", f"{proj}/active-bugs.csv")
    if missing(ab):
        print(f"{proj}: active-bugs {ab}", file=sys.stderr); continue
    ids = []
    for ln in ab.splitlines()[1:]:
        ln = ln.strip()
        if ln:
            ids.append(ln.split(",")[0].strip())
    bugs = {}
    for b in ids:
        mc = get(f"{BASE}/{proj}/modified_classes/{b}.src", f"{proj}/mc/{b}")
        tt = get(f"{BASE}/{proj}/trigger_tests/{b}", f"{proj}/tt/{b}")
        rt = get(f"{BASE}/{proj}/relevant_tests/{b}", f"{proj}/rt/{b}")
        if missing(mc) or missing(tt) or missing(rt):
            continue
        mods, trigs, rels = parse_classes(mc), parse_triggers(tt), parse_classes(rt)
        if not mods or not trigs or not rels:
            continue
        bugs[b] = {"mods": mods, "trigs": trigs, "rels": rels}
    if bugs:
        data[proj] = bugs
    print(f"{proj}: {len(bugs)}/{len(ids)} bugs usable", flush=True)

with open(os.path.expanduser("~/d4j_data.json"), "w") as fh:
    json.dump(data, fh)

# ---- structure only ----
rep = {}
for proj, bugs in data.items():
    T = sorted({t for b in bugs.values() for t in b["rels"]})
    rows = len(bugs) * len(T)
    # committed binding: (pkg3(mod0), pkg3(test)) -> (full mod0, full test)
    cf, rf = defaultdict(int), defaultdict(int)
    # candidate binding: same_pkg3 -> (same_pkg3, name_match)
    cf2, rf2 = defaultdict(int), defaultdict(int)
    for b in bugs.values():
        m0 = b["mods"][0]
        simples = {m.split(".")[-1] for m in b["mods"]}
        for t in T:
            cf[(pkg(m0), pkg(t))] += 1
            rf[(m0, t)] += 1
            sp = pkg(m0) == pkg(t)
            ts = t.split(".")[-1]
            if any(ts == s + "Test" or ts == "Test" + s for s in simples):
                nm = "exact"
            elif any(s in ts for s in simples):
                nm = "prefix"
            else:
                nm = "none"
            cf2[sp] += 1
            rf2[(sp, nm)] += 1
    def stat(d):
        v = list(d.values())
        return {"fibres": len(v), "singleton": sum(1 for x in v if x == 1),
                "median": sorted(v)[len(v)//2] if v else 0}
    rep[proj] = {"bugs": len(bugs), "test_universe": len(T), "rows": rows,
                 "committed_coarse": stat(cf), "committed_refined": stat(rf),
                 "candidate_coarse": stat(cf2), "candidate_refined": stat(rf2)}

print(json.dumps(rep, indent=1, sort_keys=True))
tot = sum(r["rows"] for r in rep.values())
sing = sum(r["committed_refined"]["singleton"] for r in rep.values())
allf = sum(r["committed_refined"]["fibres"] for r in rep.values())
print(f"\nTOTAL rows {tot}")
print(f"committed refined: {allf} fibres, {sing} singletons ({100*sing/max(allf,1):.1f}%)")
