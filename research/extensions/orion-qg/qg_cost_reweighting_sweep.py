"""Reprice the QG-39 selection-regret curve under alternative frozen objectives.

At n=1 every one of the six frame Paulis has weight 1, so the frame term is
identically 3*(t_nc+t_c) and the base-constant subtraction annihilates it for
EVERY weight vector.  K therefore depends only on (t_tag, t_r).  We verify that
numerically against r6s.config_cost rather than assuming it.
"""
import itertools, json, sys
from collections import defaultdict, Counter
from pathlib import Path

QDIR = Path("/Users/billy/Desktop/projects/ORION-claude/research/extensions/orion-q").resolve()
sys.path.insert(0, str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6s_all_n_composition as r6s

def sy(a, b): return int(p10.h.local_symp(a, b))
def f3(a, b, c): return 1 if a == b == c != 0 else int(a != 0) + int(b != 0) + int(c != 0)
def autos(): return [(0,) + p for p in itertools.permutations((1, 2, 3))]
def orbit(t, aa): return {tuple(a[x] for x in t) for a in aa}

def perm(t, p):
    o = []
    for j in range(3):
        a, b = t[2 * j], t[2 * j + 1]
        o.extend((a, b) if p[j] == 0 else (b, a))
    return tuple(o)

def baseline(t, p):
    q = perm(t, p)
    return f3(q[0], q[2], q[4]) + f3(q[1], q[3], q[5])

def key1(c): return p10.key_from_codes([c])

def aux48():
    pairs = [(a, b) for a in range(1, 4) for b in range(1, 4) if sy(a, b) == 1]
    rows = []
    for ps in itertools.product(pairs, repeat=3):
        fr = tuple(x for z in ps for x in z)
        for tag in range(4):
            l0, l1 = sy(tag, fr[0]), sy(tag, fr[1])
            if l0 != l1 and all(sy(tag, fr[2 * j]) == l0 and sy(tag, fr[2 * j + 1]) == l1 for j in (1, 2)):
                rows.append((fr, tag, tuple(key1(x) for x in fr), key1(tag)))
    return rows

aa = autos(); ps = list(itertools.product((0, 1), repeat=3)); aux = aux48()
obs = {}
for t in itertools.product(range(4), repeat=6):
    o = orbit(t, aa)
    obs.setdefault(min(o), set()).update(o)
reps = sorted(obs)
c = (0, 0, 0)

# ---- decompose every (type, probe) into (w_s, dF3); verify against config_cost
WS, DF, K0 = [], [], []
for r in reps:
    ws_row, df_row, k_row = [], [], []
    for p in ps:
        pt = perm(r, p)
        tkeys = tuple(key1(x) for x in pt)
        b = baseline(r, p)
        for fr, tag, fkeys, tkey in aux:
            cc = int(r6s.config_cost(tkeys, fkeys, tkey, c, 1))
            k = cc - b
            w_s = p10.wt(tkey)
            dF3 = k - 2 * w_s          # by hypothesis K = 2*w_s + dF3
            ws_row.append(w_s); df_row.append(dF3); k_row.append(k)
    WS.append(ws_row); DF.append(df_row); K0.append(k_row)
NP = len(ps) * len(aux)
print(f"reps={len(reps)}  probes={NP}")

# HARNESS VALIDATION 1: dF3 must equal the true framed-minus-unframed factor support.
bad = 0
for i, r in enumerate(reps):
    idx = 0
    for p in ps:
        pt = perm(r, p); b = baseline(r, p)
        for fr, tag, fkeys, tkey in aux:
            tt = [p10.mul(tkeys[m], fkeys[m]) for m in range(6)]
            lets = [p10.h.BITS_CODE[((x[0] >> 0) & 1, (x[1] >> 0) & 1)] for x in tt]
            true_f3 = f3(lets[0], lets[2], lets[4]) + f3(lets[1], lets[3], lets[5])
            if DF[i][idx] != true_f3 - b:
                bad += 1
            idx += 1
print(f"HARNESS CHECK dF3 decomposition mismatches: {bad}   (must be 0)")

# HARNESS VALIDATION 2: frame term must be a constant 18 at n=1 (so it cancels).
frame_terms = set()
for fr, tag, fkeys, tkey in aux:
    raw = 0
    for j in range(3):
        m0 = 2 if c[j] == 0 else 4
        m1 = 2 if c[j] == 1 else 4
        raw += m0 * p10.wt(fkeys[2 * j]) + m1 * p10.wt(fkeys[2 * j + 1])
    frame_terms.add(raw)
print(f"HARNESS CHECK distinct frame-support terms over all 48 frames: {sorted(frame_terms)} (base constant 3*(t_nc+t_c)=18)")

def build_K(t_tag, t_r):
    return [[t_tag * WS[i][j] + t_r * DF[i][j] for j in range(NP)] for i in range(len(reps))]

def joint_classes(K):
    """Summary a bulk-and-spectrum-only compiler sees, recomputed under these weights."""
    jc = defaultdict(list)
    for i, r in enumerate(reps):
        bulk = tuple(baseline(r, p) for p in ps[:4])
        spec = tuple(sorted(K[i]))
        jc[(bulk, spec)].append(i)
    return [sorted(v) for v in jc.values()]

def regret_curve(K, joint, kmax=6):
    n = len(K); best = [min(K[i]) for i in range(n)]
    def commit(S): return min(max(K[o][p] - best[o] for o in S) for p in range(NP))
    def parts(S):
        seen = set()
        for p in range(NP):
            g = defaultdict(list)
            for o in S: g[K[o][p]].append(o)
            if len(g) > 1: seen.add(tuple(sorted(tuple(v) for v in g.values())))
        return seen
    memo = {}
    def R(S, k):
        S = tuple(sorted(S))
        if len(S) == 1: return 0
        key = (S, k)
        if key in memo: return memo[key]
        v = commit(S)
        if k > 0 and v > 0:
            for blocks in parts(S):
                w = max(R(b, k - 1) for b in blocks)
                if w < v: v = w
                if v == 0: break
        memo[key] = v; return v
    out = []
    for k in range(kmax + 1):
        vals = [R(tuple(cl), k) for cl in joint]
        out.append((max(vals), sum(1 for v in vals if v > 0), Counter(vals)))
        if out[-1][0] == 0: break
    allK = [v for row in K for v in row]
    return out, (min(allK), max(allK)), (min(best), max(best))

def argmin_sets(K):
    return [frozenset(p for p in range(NP) if K[i][p] == min(K[i])) for i in range(len(reps))]

OBJ = {"O0 (frozen/committed)": (2, 1), "O1 (T-count-weighted)": (4, 3), "O2 (rotation-coupled)": (2, 1)}
results = {}
base_arg = None
for name, (t_tag, t_r) in OBJ.items():
    K = build_K(t_tag, t_r)
    joint = joint_classes(K)
    curve, Krange, optrange = regret_curve(K, joint)
    arg = argmin_sets(K)
    if base_arg is None: base_arg = arg
    moved = sum(1 for a, b in zip(arg, base_arg) if a != b)
    spread = optrange[1] - optrange[0]
    r0 = curve[0][0]
    depth = next((k for k, cc in enumerate(curve) if cc[0] == 0), None)
    results[name] = {
        "weights_t_tag_t_r": [t_tag, t_r], "n_joint_classes": len(joint),
        "regret_by_budget": [cc[0] for cc in curve],
        "nonzero_classes_by_budget": [cc[1] for cc in curve],
        "budget_to_zero": depth, "K_range": list(Krange), "optimal_value_range": list(optrange),
        "spread_of_optima": spread, "regret_over_spread": round(r0 / spread, 4) if spread else None,
        "argmin_sets_changed_vs_O0": moved, "types": len(reps),
        "budget0_histogram": dict(sorted(curve[0][2].items())),
    }
    print(f"\n=== {name}   (t_tag={t_tag}, t_r={t_r}) ===")
    print(f"  joint classes (recomputed under these weights): {len(joint)}")
    print(f"  worst-case regret by budget : {[cc[0] for cc in curve]}")
    print(f"  classes with nonzero regret : {[cc[1] for cc in curve]}")
    print(f"  budget to reach regret 0    : {depth}")
    print(f"  K range {Krange}   optima range {optrange}   spread {spread}")
    print(f"  regret/spread at budget 0   : {r0}/{spread} = {r0/spread:.4f}" if spread else "")
    print(f"  types whose optimal-frame set differs from O0 : {moved}/{len(reps)}")

json.dump(results, open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/calib/reprice_results.json", "w"), indent=2, default=str)
