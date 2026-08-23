"""Generic-ORION independent replay of the ORION-QG QG-28 local-Clifford orbit
census (issue SzeChunYiu/ORION#888).  Nothing is imported from the production
R6M tables: the phase-free one-qubit Pauli algebra is rebuilt from F_2^2.
"""
from itertools import product, permutations
import json

# --- rebuild F_2^2 from primitives -------------------------------------------
# letter -> (x,z) symplectic coordinates, phase-free
LET = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
INV = {v: k for k, v in LET.items()}
def local_mul(a, b):
    (ax, az), (bx, bz) = LET[a], LET[b]
    return INV[((ax ^ bx), (az ^ bz))]
def local_symp(a, b):
    (ax, az), (bx, bz) = LET[a], LET[b]
    return (ax * bz + az * bx) % 2
def local_wt(a):
    return 0 if a == "I" else 1

# --- the 6 automorphisms of {I,X,Y,Z} fixing I and permuting X,Y,Z -----------
NONID = ["X", "Y", "Z"]
AUTS = []
for perm in permutations(NONID):
    phi = {"I": "I"}
    for src, dst in zip(NONID, perm):
        phi[src] = dst
    AUTS.append(phi)

checks = {"n_automorphisms": len(AUTS), "mul_equivariant": True,
          "symp_invariant": True, "wt_invariant": True}
for phi in AUTS:
    for a in LET:
        if local_wt(phi[a]) != local_wt(a): checks["wt_invariant"] = False
        for b in LET:
            if phi[local_mul(a, b)] != local_mul(phi[a], phi[b]):
                checks["mul_equivariant"] = False
            if local_symp(phi[a], phi[b]) != local_symp(a, b):
                checks["symp_invariant"] = False
assert checks["n_automorphisms"] == 6

# --- Burnside, computed (not asserted) ---------------------------------------
def cycle_type(phi):
    moved = [a for a in NONID if phi[a] != a]
    if not moved: return "identity"
    return "transposition" if len(moved) == 2 else "three_cycle"
burnside = {}
for phi in AUTS:
    fixed_letters = [a for a in LET if phi[a] == a]
    burnside.setdefault(cycle_type(phi), []).append(len(fixed_letters) ** 6)
bsum = sum(sum(v) for v in burnside.values())
burnside_count = bsum // len(AUTS)

# --- explicit orbit enumeration over the 4096 target-column types -----------
TYPES = list(product("IXYZ", repeat=6))
def apply_phi(phi, t): return tuple(phi[c] for c in t)
seen, orbits = set(), []
for t in TYPES:
    if t in seen: continue
    orb = {apply_phi(phi, t) for phi in AUTS}
    seen |= orb
    orbits.append(sorted(orb))
size_hist = {}
for o in orbits: size_hist[len(o)] = size_hist.get(len(o), 0) + 1
canon = {t: min(o) for o in orbits for t in o}
canon_is_lexmin = all(canon[t] <= t for t in TYPES)

# --- the barrier the issue forbids: adding independent per-column position
#     relabelling  S_2^3 (swap the two targets in each block) x S_3 (blocks)  --
POSG = []
for blocks in permutations(range(3)):
    for sw in product((0, 1), repeat=3):
        p = []
        for bi in range(3):
            src = blocks[bi]
            a, b = 2 * src, 2 * src + 1
            p += [b, a] if sw[bi] else [a, b]
        POSG.append(tuple(p))
POSG = sorted(set(POSG))
seen2, n2 = set(), 0
for t in TYPES:
    if t in seen2: continue
    orb = {tuple(apply_phi(phi, t)[i] for i in p) for phi in AUTS for p in POSG}
    seen2 |= orb; n2 += 1

res = {
 "schema": "ORION.QG.QG28.GenericReplay.v1",
 "issue": "SzeChunYiu/ORION#888",
 "rebuilt_from": "F_2^2 symplectic coordinates; no production R6M table imported",
 "equivariance_checks": checks,
 "burnside": {"identity_fixed": burnside["identity"],
              "transposition_fixed": burnside["transposition"],
              "three_cycle_fixed": burnside["three_cycle"],
              "sum": bsum, "group_order": len(AUTS), "orbit_count": burnside_count},
 "explicit_enumeration": {"types": len(TYPES), "orbit_count": len(orbits),
                          "orbit_size_histogram": {str(k): v for k, v in sorted(size_hist.items())},
                          "canonical_rep_is_lex_min": canon_is_lexmin},
 "burnside_matches_enumeration": burnside_count == len(orbits),
 "issue_888_expected": {"orbit_count": 715, "size_1": 1, "size_3": 63, "size_6": 651},
 "unsafe_symmetry_barrier": {
     "group": "S_3(letters) x (S_2^3 : S_3)(positions)",
     "position_group_order": len(POSG),
     "combined_orbit_count": n2,
     "strictly_coarser_than_715": n2 < len(orbits),
     "verdict": "aggregating under the position group is a strictly coarser quotient; "
                "INDEPENDENT_POSITION_RELABEL_PER_COLUMN must stay false"},
}
print(json.dumps(res, indent=2, sort_keys=True))
