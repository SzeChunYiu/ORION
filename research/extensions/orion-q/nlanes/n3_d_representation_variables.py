"""ORION-Q N3-D deterministic exact-synthetic study: representation variable synthesis.

Implements the frozen protocol
development/orion-q-nlane-closure/N3_D_REPRESENTATION_VARIABLES_PROTOCOL.md
(issue #676, successor family D). Exact-synthetic bounded diagnostic only:
no real-quantum, no novelty, no P10 authority.

Run:
    python research/extensions/orion-q/nlanes/n3_d_representation_variables.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
from collections import deque

SEED = 20260821
SCHEMA = "ORIONQ.N3D.RepresentationVariableSynthesis.v1"
AUTHORITY = "exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority"
CLAIM_BOUNDARY = (
    "exact-synthetic CNOT/GF(2) worlds on prime wire counts only; representation "
    "variable chosen from a fixed library at explicit transport cost; identity "
    "(supplied) representation holds first right of refusal; no claim about "
    "compiler/IR tooling, real qubit routing, or novelty"
)

TRAIN_N = (5, 7)
HELDOUT_N = (11, 13)
DONOR_BFS_BUDGET = 200_000
COEFF_RANGE = (-3, -2, -1, 0, 1, 2, 3)
ALPHA_RANGE = (0, 1)
BETA_RANGE = (-3, -2, -1, 0, 1, 2, 3)


# ---- exact semantics ----------------------------------------------------
def identity_rows(n: int) -> tuple[int, ...]:
    return tuple(1 << i for i in range(n))


def apply_program(n: int, gates) -> tuple[int, ...]:
    rows = list(identity_rows(n))
    for c, t in gates:
        rows[t] ^= rows[c]
    return tuple(rows)


# ---- representation library (fixed order; identity first refusal) -------
def rep_map(name: str, n: int):
    """Return forward bijection i -> r(i) on range(n), or None if inapplicable."""
    if name == "identity":
        return lambda i: i
    if name == "reversal":
        return lambda i: n - 1 - i
    if name.startswith("mul"):
        c = int(name[3:])
        if math.gcd(c, n) != 1:
            return None
        return lambda i: (c * i) % n
    raise ValueError(name)


def rep_inverse(name: str, n: int):
    fwd = rep_map(name, n)
    if fwd is None:
        return None
    inv = {fwd(i): i for i in range(n)}
    return lambda i: inv[i]


REP_LIBRARY = (("identity", 0), ("reversal", 1), ("mul2", 1), ("mul3", 1), ("mul5", 1))


# ---- affine schema (integer arithmetic, no modular wrap) ----------------
def schema_program(n: int, p: int, q: int, r: int, s: int, alpha: int, beta: int):
    length = alpha * n + beta
    if length < 0:
        return None
    gates = []
    for t in range(length):
        src = p * t + q
        dst = r * t + s
        if not (0 <= src < n and 0 <= dst < n) or src == dst:
            return None
        gates.append((src, dst))
    return gates


def fit_schema(artifacts: dict[int, list], counter: dict[str, int]):
    """Exact schema-fit predicate of the frozen protocol, computed constructively.

    A tuple (p,q,r,s,alpha,beta) within the frozen ranges fits iff its
    generated tokens equal every artifact's token list. With artifact lengths
    >= 2 the tokens at t = 0,1 uniquely determine (p,q,r,s) and the two train
    lengths uniquely determine (alpha,beta), so deriving those values and
    verifying is mathematically equivalent to enumerating the frozen grid
    (implementation revision r2; predicate, ranges, and gates unchanged)."""
    ns = sorted(artifacts)
    lens = {n: len(artifacts[n]) for n in ns}
    if len(ns) < 2 or min(lens.values()) < 2:
        return None
    n0, n1 = ns[0], ns[1]
    dn = n1 - n0
    if (lens[n1] - lens[n0]) % dn != 0:
        return None
    alpha = (lens[n1] - lens[n0]) // dn
    beta = lens[n0] - alpha * n0
    a0 = [tuple(g) for g in artifacts[n0]]
    p = a0[1][0] - a0[0][0]
    q = a0[0][0]
    r = a0[1][1] - a0[0][1]
    s = a0[0][1]
    if not (
        p in COEFF_RANGE and q in COEFF_RANGE and r in COEFF_RANGE and s in COEFF_RANGE
        and alpha in ALPHA_RANGE and beta in BETA_RANGE
    ):
        return None
    for n, art in artifacts.items():
        counter["constructed"] += 1
        gates = schema_program(n, p, q, r, s, alpha, beta)
        if gates is None or gates != [tuple(g) for g in art]:
            return None
    return (p, q, r, s, alpha, beta)


# ---- ground-truth worlds ------------------------------------------------
def gen_D1(n: int):  # logical chain hidden under i -> 3i mod n
    return [((3 * t) % n, (3 * (t + 1)) % n) for t in range(n - 1)]


def gen_D2(n: int):  # plain chain (identity representation sufficient)
    return [(t, t + 1) for t in range(n - 1)]


def make_D3_perms():
    rng = random.Random(SEED)
    perms = {}
    for n in TRAIN_N + HELDOUT_N:
        p = list(range(n))
        rng.shuffle(p)
        perms[n] = p
    return perms


D3_PERMS = make_D3_perms()


def gen_D3(n: int):  # keyed pseudorandom permutation indexing (hostile)
    p = D3_PERMS[n]
    return [(p[t], p[t + 1]) for t in range(n - 1)]


WORLDS = {"D1": gen_D1, "D2": gen_D2, "D3": gen_D3}


# ---- donor baselines ----------------------------------------------------
def bfs_search(n: int, target: tuple[int, ...], budget: int) -> dict[str, object]:
    start = identity_rows(n)
    if start == target:
        return {"found": True, "expansions": 0}
    gates = [(c, t) for c in range(n) for t in range(n) if c != t]
    depth = {start: 0}
    queue = deque([start])
    expansions = 0
    max_depth = 0
    while queue:
        state = queue.popleft()
        d = depth[state]
        for c, t in gates:
            expansions += 1
            if expansions > budget:
                return {"found": False, "expansions": expansions - 1, "max_depth_reached": max_depth}
            rows = list(state)
            rows[t] ^= rows[c]
            child = tuple(rows)
            if child in depth:
                continue
            depth[child] = d + 1
            max_depth = max(max_depth, d + 1)
            if child == target:
                return {"found": True, "expansions": expansions, "min_length": d + 1}
            queue.append(child)
    return {"found": False, "expansions": expansions, "max_depth_reached": max_depth}


def run_world(name: str, gen, counter: dict[str, int]) -> dict[str, object]:
    artifacts = {n: gen(n) for n in TRAIN_N}

    # candidate: walk the representation library in order (identity first refusal)
    selected = None
    selected_cost = None
    selected_schema = None
    rep_trace = []
    for rep_name, cost in REP_LIBRARY:
        invs = {n: rep_inverse(rep_name, n) for n in TRAIN_N}
        if any(v is None for v in invs.values()):
            rep_trace.append({"rep": rep_name, "applicable": False, "fits_both_train": False})
            continue
        transformed = {
            n: [(invs[n](c), invs[n](t)) for c, t in artifacts[n]] for n in TRAIN_N
        }
        tup = fit_schema(transformed, counter)
        rep_trace.append({"rep": rep_name, "applicable": True, "fits_both_train": tup is not None})
        if tup is not None:
            selected, selected_cost, selected_schema = rep_name, cost, tup
            break

    raw_induction_fits = bool(rep_trace) and rep_trace[0]["rep"] == "identity" and rep_trace[0]["fits_both_train"]
    parent_sufficient = raw_induction_fits

    heldout = {}
    for n in HELDOUT_N:
        target = apply_program(n, gen(n))
        cand_ok = False
        if selected is not None:
            fwd = rep_map(selected, n)
            if fwd is not None:
                counter["constructed"] += 1
                logical = schema_program(n, *selected_schema)
                if logical is not None:
                    concrete = [(fwd(c), fwd(t)) for c, t in logical]
                    cand_ok = apply_program(n, concrete) == target
        counter["constructed"] += 1
        trivial_ok = apply_program(n, artifacts[max(TRAIN_N)]) == target
        entry = {
            "candidate_exact_verified": bool(cand_ok),
            "trivial_baseline_verified": bool(trivial_ok),
        }
        if name == "D1":
            donor = bfs_search(n, target, DONOR_BFS_BUDGET)
            entry["donor_found"] = bool(donor["found"])
            entry["donor_expansions"] = donor["expansions"]
            entry["donor_max_depth_reached"] = donor.get("max_depth_reached")
        heldout[str(n)] = entry

    family_claim = (
        selected is not None
        and not parent_sufficient
        and all(v["candidate_exact_verified"] for v in heldout.values())
    )
    return {
        "selected_representation": selected,
        "transport_cost": selected_cost,
        "schema_tuple": list(selected_schema) if selected_schema else None,
        "rep_trace": rep_trace,
        "raw_induction_fits": bool(raw_induction_fits),
        "parent_sufficient": bool(parent_sufficient),
        "no_valid_representation": selected is None,
        "heldout": heldout,
        "family_claim": bool(family_claim),
        "residual_claim": bool(family_claim),
    }


def run_study() -> dict[str, object]:
    counter = {"constructed": 0}
    worlds = {name: run_world(name, gen, counter) for name, gen in WORLDS.items()}
    return {"worlds": worlds, "candidate_constructed_programs": counter["constructed"]}


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    run1 = run_study()
    run2 = run_study()
    d1 = hashlib.sha256(canonical(run1).encode()).hexdigest()
    d2 = hashlib.sha256(canonical(run2).encode()).hexdigest()

    w1 = run1["worlds"]["D1"]
    w2 = run1["worlds"]["D2"]
    w3 = run1["worlds"]["D3"]
    d1_donor_matched = any(
        v.get("donor_found", False) or v["trivial_baseline_verified"] for v in w1["heldout"].values()
    )

    gates = {
        "GD0_budget_sanity": run1["candidate_constructed_programs"] <= DONOR_BFS_BUDGET,
        "GD1_residual_value": (
            not w1["raw_induction_fits"]
            and w1["selected_representation"] not in (None, "identity")
            and w1["transport_cost"] == 1
            and w1["family_claim"]
            and not d1_donor_matched
        ),
        "GD2_donor_first_refusal": (
            w2["selected_representation"] == "identity"
            and w2["transport_cost"] == 0
            and w2["parent_sufficient"]
            and not w2["residual_claim"]
        ),
        "GD3_hostile_catch": (
            w3["no_valid_representation"] and not w3["family_claim"]
        ),
        "GD4_determinism": d1 == d2,
    }
    if all(gates.values()):
        terminal = "N3D_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC"
    elif w1["raw_induction_fits"] or d1_donor_matched:
        terminal = "N3D_PARENT_SUFFICIENT_NEGATIVE"
    else:
        terminal = "N3D_MECHANISM_FAILED_NEGATIVE"

    result = {
        "schema": SCHEMA,
        "issue": 676,
        "family": "D_representation_variable_synthesis",
        "seed": SEED,
        "authority": AUTHORITY,
        "claim_boundary": CLAIM_BOUNDARY,
        "protocol": "development/orion-q-nlane-closure/N3_D_REPRESENTATION_VARIABLES_PROTOCOL.md",
        "budgets": {"donor_bfs_budget_per_heldout_n": DONOR_BFS_BUDGET},
        "study": run1,
        "determinism": {"run1_sha256": d1, "run2_sha256": d2, "identical": d1 == d2},
        "gates": gates,
        "terminal": terminal,
        "p10_authorized": False,
        "novelty_authorized": False,
    }

    print("ORIONQ_N3_D_REPRESENTATION_VARIABLES=" + canonical(result))
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "N3_D_REPRESENTATION_VARIABLES_RESULTS.json"
    )
    with open(out, "w") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
