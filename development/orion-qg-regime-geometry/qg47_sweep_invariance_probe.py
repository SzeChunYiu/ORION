"""QG47 design probe: frame-permutation invariance of the frozen machinery.

Question (preregistration input, no claims): is (C_DP, C_Dxx) invariant under
permutation of the 3 frames (consecutive target pairs) for gap != 0 rows?

If YES exactly (exhaustive over all 3! = 6 permutations, on every gap<0 row of
the QG45 receipt), the full-alphabet n=2 sweep collapses from 15^6 = 11,393,390
ordered instances to C(15^2 + 3 - 1, 3) = 1,923,825 frame multisets (225
possible frames, multisets of size 3) — a 6x reduction, and the enumeration is
exactly the non-decreasing frame-sequence enumeration. QG47 does NOT rely on
this reduction for exactness (ordered enumeration is airtight).

Also probes: within-frame x/z swap is NOT assumed (x and z are distinct
Pauli coordinates); full target permutation is already known FALSE.
"""
import itertools
import json
import sys

sys.path.insert(0, "research/extensions/orion-qg")
import qg2_objective_robustness as qg2  # noqa: E402

REC = "research/extensions/orion-qg/QG45_WITNESS8_ANATOMY_RESULTS.json"

rec = json.load(open(REC))
objs = {}
for name, cell in rec["objectives"].items():
    w = cell["weights"]
    objs[name] = qg2.Objective(name, w["t_nc"], w["t_c"], w["t_tag"], w["t_r"], w.get("rho", 0))

rows = rec["witness_rows"]
checked = invariant = 0
violations = []
gaps_seen = set()
for r in rows:
    n = r["n"]
    targets = [tuple(t) for t in r["targets"]]
    ob = objs[r["objective"]]
    tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
    base = (qg2.dp_cost_pairs_ob(tp, n, ob), qg2.dxx_cost_ob(tp, n, ob))
    assert base[0] - base[1] == r["gap"], (r["instance"], base, r["gap"])
    gaps_seen.add(r["gap"])
    checked += 1
    frames = [(targets[0], targets[1]), (targets[2], targets[3]), (targets[4], targets[5])]
    bad = None
    for perm in itertools.permutations(frames):
        flat = [t for fr in perm for t in fr]
        tp2 = tuple((flat[2 * j], flat[2 * j + 1]) for j in range(3))
        if (qg2.dp_cost_pairs_ob(tp2, n, ob), qg2.dxx_cost_ob(tp2, n, ob)) != base:
            bad = perm
            break
    if bad is None:
        invariant += 1
    else:
        violations.append((r["instance"], r["objective"], bad))

print(f"gap<0 rows checked: {checked} (distinct gaps {sorted(gaps_seen)})")
print(f"frame-perm invariant (all 6 perms exhaustive): {invariant}")
print(f"violations: {len(violations)}")
for v in violations[:10]:
    print("VIOLATION:", v)

# Secondary probe: is the ORDER of frames ever *cost-relevant* at gap == 0?
# Sample random n=2 gap-0 instances and permute frames.
import random  # noqa: E402

rng = random.Random(20260903)
n2_letters = [(x, z) for x in range(4) for z in range(4) if (x, z) != (0, 0)]
g0_checked = g0_inv = 0
g0_viol = 0
for _ in range(300):
    ts = [rng.choice(n2_letters) for _ in range(6)]
    ob = objs["Q45G_tr2_dc-3_dnc0_tag2"]
    tp = tuple((ts[2 * j], ts[2 * j + 1]) for j in range(3))
    base = (qg2.dp_cost_pairs_ob(tp, 2, ob), qg2.dxx_cost_ob(tp, 2, ob))
    g0_checked += 1
    ok = True
    for perm in itertools.permutations(range(3)):
        fr = [(ts[2 * k], ts[2 * k + 1]) for k in perm]
        flat = [t for f in fr for t in f]
        tp2 = tuple((flat[2 * j], flat[2 * j + 1]) for j in range(3))
        if (qg2.dp_cost_pairs_ob(tp2, 2, ob), qg2.dxx_cost_ob(tp2, 2, ob)) != base:
            ok = False
            break
    if ok:
        g0_inv += 1
    else:
        g0_viol += 1
print(f"n=2 gap-0 random sample: {g0_checked} checked, invariant {g0_inv}, violations {g0_viol}")
