#!/usr/bin/env python3
"""ORION-16 real-system minimal-revalidation discriminator.

Executes the arms frozen in PROTOCOL_AND_PREDICTIONS.md on declared dependency
graphs from independently sourced real systems. Extracts G* by parsing declared
edges; builds nothing and runs no validator. A system whose extraction fails is
reported CANNOT_CHECK and contributes no result.
"""
from __future__ import annotations
import collections, json, os, random, re, statistics, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/o16")
ROOT.mkdir(parents=True, exist_ok=True)
SEED = 20260828
FRACTIONS = [0.01, 0.05, 0.10]
N_COMMITS = 200

SYSTEMS = [
    {"id": "mathlib4", "url": "https://github.com/leanprover-community/mathlib4",
     "ext": ".lean", "kind": "lean", "root": "Mathlib"},
    {"id": "nf-core-rnaseq", "url": "https://github.com/nf-core/rnaseq",
     "ext": ".nf", "kind": "nextflow", "root": ""},
    {"id": "gene-ontology", "kind": "obo",
     "releases": ["2024-11-03", "2025-02-06", "2025-03-16", "2025-06-01", "2025-07-22"]},
]

def sh(args, cwd=None, timeout=3600):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

def clone(url, d):
    if (d / ".git").exists():
        return True, None
    d.mkdir(parents=True, exist_ok=True)
    rc, _, e = sh(["git", "init", "-q", "--initial-branch=main", str(d)])
    if rc: return False, f"init: {e[:150]}"
    sh(["git", "remote", "add", "origin", url], cwd=d)
    rc, _, e = sh(["git", "fetch", "-q", "--filter=blob:none", "--depth", str(N_COMMITS + 5), "origin", "HEAD"], cwd=d)
    if rc: return False, f"fetch: {e[:150]}"
    rc, _, e = sh(["git", "checkout", "-q", "FETCH_HEAD"], cwd=d)
    if rc: return False, f"checkout: {e[:150]}"
    return True, None

def mod_lean(p, root):
    return p[:-5].replace("/", ".")


LEAN_IMPORT = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|meta\s+)*import\s+(\S+)")
NF_INCLUDE = re.compile(r"include\s*\{[^}]*\}\s*from\s*['\"]([^'\"]+)['\"]")


def edges_lean(d, root):
    """Declared Lean imports.

    Mathlib4 uses Lean's module system, so an import may be written
    `public import Mathlib.X.Y`; matching only a bare `import` drops most of the
    graph. Every declared import is classified resolved or unresolved.
    """
    g = collections.defaultdict(set)
    files = list((d / root).rglob("*.lean")) if (d / root).exists() else []
    known = {mod_lean(str(f.relative_to(d)), root) for f in files}
    declared = resolved = 0
    for f in files:
        m = mod_lean(str(f.relative_to(d)), root)
        try: txt = f.read_text(errors="replace")
        except Exception: continue
        for line in txt.splitlines():
            mm = LEAN_IMPORT.match(line)
            if not mm: continue
            tgt = mm.group(1).strip()
            if not tgt.startswith(root): continue
            declared += 1
            if tgt in known:
                resolved += 1; g[m].add(tgt)
    g["__fidelity__"] = {"declared": declared, "resolved": resolved}
    return g


def edges_nextflow(d, root):
    """Declared Nextflow DSL2 includes. Leaf process modules legitimately have
    none, so authority is measured by resolution fidelity, not by how many files
    carry an edge."""
    g = collections.defaultdict(set)
    base = d.resolve()
    declared = resolved = 0
    for f in d.rglob("*.nf"):
        m = str(f.relative_to(d))
        try: txt = f.read_text(errors="replace")
        except Exception: continue
        for mm in NF_INCLUDE.finditer(txt):
            declared += 1
            q = (f.parent / mm.group(1)).resolve()
            for cand in (q, q.with_suffix(".nf"), q / "main.nf"):
                if cand.exists():
                    try: r = cand.relative_to(base)
                    except Exception: break
                    g[m].add(str(r)); resolved += 1; break
    g["__fidelity__"] = {"declared": declared, "resolved": resolved}
    return g


def changesets_git(d, ext, root, n):
    rc, out, _ = sh(["git", "log", f"-{n}", "--name-only", "--pretty=format:@@%H"], cwd=d)
    if rc: return []
    sets, cur = [], None
    for line in out.splitlines():
        if line.startswith("@@"):
            if cur: sets.append(cur)
            cur = set()
        elif line.strip() and cur is not None and line.endswith(ext):
            if root and not line.startswith(root + "/"): continue
            cur.add(mod_lean(line, root) if ext == ".lean" else line)
    if cur: sets.append(cur)
    return [s for s in sets if s]

def fetch_obo(rel, d):
    f = d / f"go-{rel}.obo"
    if f.exists() and f.stat().st_size > 1_000_000: return f
    url = f"http://release.geneontology.org/{rel}/ontology/go-basic.obo"
    rc, _, _ = sh(["curl", "-sSL", "--max-time", "900", "-o", str(f), url], timeout=960)
    if rc == 0 and f.exists() and f.stat().st_size > 1_000_000:
        return f
    return None

def parse_obo(f):
    g, cur, defs = collections.defaultdict(set), None, {}
    body = []
    for line in f.read_text(errors="replace").splitlines():
        if line.startswith("[Term]"):
            if cur: defs[cur] = "\n".join(body)
            cur, body = None, []
        elif line.startswith("id: GO:"): cur = line[4:].strip()
        elif cur and line.startswith("is_a: "): g[cur].add(line[6:].split("!")[0].strip()); body.append(line)
        elif cur and line.startswith("relationship: part_of "):
            g[cur].add(line.split()[2].strip()); body.append(line)
        elif cur: body.append(line)
    if cur: defs[cur] = "\n".join(body)
    return g, defs

def reverse(g):
    r = collections.defaultdict(set)
    for a, bs in g.items():
        for b in bs: r[b].add(a)
    return r

def closure(rev, delta):
    seen, stack = set(delta), list(delta)
    while stack:
        x = stack.pop()
        for y in rev.get(x, ()):
            if y not in seen: seen.add(y); stack.append(y)
    return seen

def mutate(g, nodes, frac, add, rng):
    h = {k: set(v) for k, v in g.items()}
    alledges = [(a, b) for a, bs in g.items() for b in bs]
    k = max(1, int(len(alledges) * frac))
    if add:
        for _ in range(k):
            a, b = rng.choice(nodes), rng.choice(nodes)
            if a != b: h.setdefault(a, set()).add(b)
    else:
        for a, b in rng.sample(alledges, min(k, len(alledges))): h[a].discard(b)
    return h

def run_system(sysdef):
    sid = sysdef["id"]; d = ROOT / sid
    if sysdef["kind"] == "obo":
        d.mkdir(parents=True, exist_ok=True)
        files = [(r, fetch_obo(r, d)) for r in sysdef["releases"]]
        files = [(r, f) for r, f in files if f]
        if len(files) < 3: return {"system": sid, "status": "CANNOT_CHECK", "reason": f"only {len(files)} GO releases retrievable"}
        graphs = [(r, *parse_obo(f)) for r, f in files]
        g = graphs[-1][1]; nodes = sorted(set(g) | {b for bs in g.values() for b in bs})
        sets = []
        for (r0, g0, d0), (r1, g1, d1) in zip(graphs, graphs[1:]):
            ch = {t for t in d1 if t in d0 and d1[t] != d0[t]} | (set(d0) - set(d1))
            ch &= set(nodes)
            if ch: sets.append(ch)
        if not sets: return {"system": sid, "status": "CANNOT_CHECK", "reason": "no inter-release term changes recovered"}
    else:
        ok, err = clone(sysdef["url"], d)
        if not ok: return {"system": sid, "status": "CANNOT_CHECK", "reason": err}
        g = (edges_lean if sysdef["kind"] == "lean" else edges_nextflow)(d, sysdef["root"])
        fid = g.pop("__fidelity__", None)
        if not g: return {"system": sid, "status": "CANNOT_CHECK", "reason": "no declared edges extracted"}
        if not fid or fid["declared"] == 0:
            return {"system": sid, "status": "CANNOT_CHECK", "reason": "no declared dependency statements found"}
        frac = fid["resolved"] / fid["declared"]
        if frac < 0.95:
            return {"system": sid, "status": "CANNOT_CHECK",
                    "reason": f"only {fid['resolved']}/{fid['declared']} declared statements "
                              f"({frac:.1%}) resolve to known modules; graph not authoritative",
                    "resolution_fidelity": round(frac, 4)}
        nodes = sorted(set(g) | {b for bs in g.values() for b in bs})
        sets = [s & set(nodes) for s in changesets_git(d, sysdef["ext"], sysdef["root"], N_COMMITS)]
        sets = [s for s in sets if s]
        if len(sets) < 10: return {"system": sid, "status": "CANNOT_CHECK", "reason": f"only {len(sets)} usable change sets"}

    rng = random.Random(SEED)
    rev = reverse(g); N = len(nodes)
    per = {a: [] for a in ("full", "changed-set-only", "direct-neighbours", "affected-closure")}
    strand = {a: 0 for a in per}
    for delta in sets:
        truth = closure(rev, delta)
        arms = {"full": set(nodes), "changed-set-only": set(delta),
                "direct-neighbours": set(delta) | {y for x in delta for y in rev.get(x, ())},
                "affected-closure": truth}
        for a, s in arms.items():
            per[a].append(len(s)); strand[a] += len(truth - s)
    out = {"system": sid, "status": "OK", "resolution_fidelity": round(frac, 4) if sysdef["kind"] != "obo" else None, "nodes": N, "edges": sum(len(v) for v in g.values()),
           "change_sets": len(sets),
           "median_delta": statistics.median(len(s) for s in sets),
           "arms": {a: {"median_cost": statistics.median(per[a]),
                        "mean_cost": round(statistics.mean(per[a]), 2),
                        "stranded_total": strand[a],
                        "median_cost_frac_of_full": round(statistics.median(per[a]) / N, 4)} for a in per}}
    cons, inc = {}, {}
    sub = sets[: min(40, len(sets))]
    for fr in FRACTIONS:
        gc = mutate(g, nodes, fr, True, random.Random(SEED)); rc_ = reverse(gc)
        gi = mutate(g, nodes, fr, False, random.Random(SEED)); ri = reverse(gi)
        cc, rr = [], 0
        for delta in sub:
            truth = closure(rev, delta)
            cc.append(len(closure(rc_, delta)))
            rr += len(truth - closure(ri, delta))
        cons[str(fr)] = statistics.median(cc); inc[str(fr)] = rr
    out["conservative_median_cost"] = cons
    out["incomplete_stranded_total"] = inc
    out["affected_closure_median_cost_on_subset"] = statistics.median(
        [len(closure(rev, s)) for s in sub])
    return out

res = [run_system(s) for s in SYSTEMS]
ok = [r for r in res if r["status"] == "OK"]
report = {"schema": "ORION.ORION16.RealSystemDiscriminator.Result.v1",
          "seed": SEED, "fractions": FRACTIONS, "systems": res,
          "systems_evaluable": len(ok)}
print(json.dumps(report, indent=1))
Path(ROOT / "RESULT.json").write_text(json.dumps(report, indent=1) + "\n")
