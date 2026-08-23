"""ORION-Q N3-C deterministic exact-synthetic study: cross-family operator induction.

Implements the frozen protocol
development/orion-q-nlane-closure/N3_C_OPERATOR_INDUCTION_PROTOCOL.md
(issue #676, successor family C). Exact-synthetic bounded diagnostic only:
no real-quantum, no novelty, no P10 authority.

Run:
    python research/extensions/orion-q/nlanes/n3_c_operator_induction.py
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import deque

SEED = 20260821
SCHEMA = "ORIONQ.N3C.CrossFamilyOperatorInduction.v1"
AUTHORITY = "exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority"
CLAIM_BOUNDARY = (
    "exact-synthetic CNOT/GF(2) program families only; higher-order composition "
    "law induced across donor-produced atoms; donor search and trivial replay "
    "hold first right of refusal on every held-out size; no claim about "
    "DreamCoder-class library learning, real quantum families, or novelty"
)

TRAIN_ATOM_N = (2, 3, 4, 5)
HELDOUT_ATOM_N = (2, 3, 4)
HELDOUT_EVAL_N = (8, 10)
DONOR_BFS_BUDGET = 200_000
COEFF_RANGE = (-2, -1, 0, 1, 2)


# ---- exact semantics ----------------------------------------------------
def identity_rows(n: int) -> tuple[int, ...]:
    return tuple(1 << i for i in range(n))


def apply_program(n: int, gates) -> tuple[int, ...]:
    rows = list(identity_rows(n))
    for c, t in gates:
        rows[t] ^= rows[c]
    return tuple(rows)


# ---- ground-truth generators -------------------------------------------
def gen_F1(n: int):  # chain
    return [(t, t + 1) for t in range(n - 1)]


def gen_F2(n: int):  # fan
    return [(0, t + 1) for t in range(n - 1)]


def gen_F3(n: int):  # chain+fan double layer
    out = []
    for t in range(n - 1):
        out.append((t, t + 1))
        out.append((0, t + 1))
    return out


def gen_F4(n: int):  # reverse fan with base (residual held-out family)
    out = [(1, 0)]
    for m in range(1, n - 1):
        out.append((m + 1, 0))
    return out


def gen_F5(n: int):  # constant family (donor-sufficient held-out)
    return [(0, 1)]


def gen_F6(n: int):  # hostile: chain, plus a correction gate from n >= 5
    out = [(t, t + 1) for t in range(n - 1)]
    if n >= 5:
        out.append((0, n - 1))
    return out


TRAIN_FAMILIES = {"F1": gen_F1, "F2": gen_F2, "F3": gen_F3}
HELDOUT_FAMILIES = {"F4": gen_F4, "F5": gen_F5, "F6": gen_F6}


# ---- operator induction -------------------------------------------------
def fit_affine(points):
    """points: list of (m, value). Exact integer affine fit a*m+b with a,b in COEFF_RANGE."""
    for a in COEFF_RANGE:
        for b in COEFF_RANGE:
            if all(a * m + b == v for m, v in points):
                return (a, b)
    return None


def fit_fold(atoms: dict[int, list], counter: dict[str, int]):
    """Fit the prefix-incremental affine fold law to a family's atoms.

    Returns {"base": P(min_n), "k": block size, "coeffs": per-gate affine
    ((a,b),(c,d))} or None. m = n - 2 indexes the delta appended to reach n.
    """
    ns = sorted(atoms)
    base = atoms[ns[0]]
    deltas = {}
    for i in range(1, len(ns)):
        n_prev, n_cur = ns[i - 1], ns[i]
        prev, cur = atoms[n_prev], atoms[n_cur]
        if cur[: len(prev)] != prev:
            return None
        deltas[n_cur - 2] = cur[len(prev):]
    sizes = {len(d) for d in deltas.values()}
    if len(sizes) != 1:
        return None
    k = sizes.pop()
    if k == 0:
        return None
    coeffs = []
    for j in range(k):
        src = fit_affine([(m, deltas[m][j][0]) for m in deltas])
        dst = fit_affine([(m, deltas[m][j][1]) for m in deltas])
        counter["constructed"] += 1
        if src is None or dst is None:
            return None
        coeffs.append((src, dst))
    return {"base": base, "k": k, "coeffs": coeffs}


def unroll(fit: dict, n: int):
    gates = list(fit["base"])
    base_n = 2  # atoms start at n = 2 by construction
    for m in range(base_n - 1, n - 1):
        for (a, b), (c, d) in fit["coeffs"]:
            src, dst = a * m + b, c * m + d
            if not (0 <= src < n and 0 <= dst < n) or src == dst:
                return None
            gates.append((src, dst))
    return gates


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


def run_study() -> dict[str, object]:
    counter = {"constructed": 0}

    # 1. induce the operator across the three train families
    train_fits = {}
    for name, gen in TRAIN_FAMILIES.items():
        atoms = {n: gen(n) for n in TRAIN_ATOM_N}
        fit = fit_fold(atoms, counter)
        train_fits[name] = {
            "fits_fold_law": fit is not None,
            "block_size": None if fit is None else fit["k"],
            "coeffs": None if fit is None else fit["coeffs"],
        }
    operator_induced = all(v["fits_fold_law"] for v in train_fits.values())

    # 2. held-out families: donor/trivial first, then candidate transfer
    heldout = {}
    for name, gen in HELDOUT_FAMILIES.items():
        atoms = {n: gen(n) for n in HELDOUT_ATOM_N}
        per_n = {}
        parent_matched_all = True
        for n in HELDOUT_EVAL_N:
            target = apply_program(n, gen(n))
            counter["constructed"] += 1
            trivial_ok = apply_program(n, atoms[max(HELDOUT_ATOM_N)]) == target
            if trivial_ok:
                donor = {"found": True, "via": "trivial_replay", "expansions": 0}
            else:
                donor = bfs_search(n, target, DONOR_BFS_BUDGET)
                donor["via"] = "bfs"
            per_n[str(n)] = {
                "trivial_baseline_verified": bool(trivial_ok),
                "donor_found": bool(donor["found"]),
                "donor_via": donor["via"],
                "donor_expansions": donor["expansions"],
                "donor_max_depth_reached": donor.get("max_depth_reached"),
            }
            parent_matched_all = parent_matched_all and bool(donor["found"])
        parent_sufficient = parent_matched_all

        fit = fit_fold(atoms, counter) if operator_induced else None
        transfer = {}
        for n in HELDOUT_EVAL_N:
            ok = False
            if fit is not None:
                counter["constructed"] += 1
                pred = unroll(fit, n)
                ok = pred is not None and apply_program(n, pred) == apply_program(n, gen(n))
            transfer[str(n)] = bool(ok)
        transfer_claim = (
            (not parent_sufficient)
            and fit is not None
            and all(transfer.values())
        )
        heldout[name] = {
            "fold_fit_on_atoms": fit is not None,
            "per_n": per_n,
            "parent_sufficient": bool(parent_sufficient),
            "transfer_verified": transfer,
            "transfer_claim": bool(transfer_claim),
            "operator_value_claim": bool(transfer_claim),
        }

    return {
        "train_fits": train_fits,
        "operator_induced": bool(operator_induced),
        "heldout": heldout,
        "candidate_constructed_programs": counter["constructed"],
    }


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    run1 = run_study()
    run2 = run_study()
    d1 = hashlib.sha256(canonical(run1).encode()).hexdigest()
    d2 = hashlib.sha256(canonical(run2).encode()).hexdigest()

    f4 = run1["heldout"]["F4"]
    f5 = run1["heldout"]["F5"]
    f6 = run1["heldout"]["F6"]
    f4_donor_matched = any(v["donor_found"] or v["trivial_baseline_verified"] for v in f4["per_n"].values())

    gates = {
        "GC0_budget_sanity": run1["candidate_constructed_programs"] <= DONOR_BFS_BUDGET,
        "GC1_residual_transfer": (
            run1["operator_induced"]
            and f4["transfer_claim"]
            and all(f4["transfer_verified"].values())
            and not f4_donor_matched
        ),
        "GC2_donor_first_refusal": (
            f5["parent_sufficient"] and not f5["operator_value_claim"]
        ),
        "GC3_hostile_catch": (
            f6["fold_fit_on_atoms"]
            and not any(f6["transfer_verified"].values())
            and not f6["transfer_claim"]
        ),
        "GC4_determinism": d1 == d2,
    }
    if all(gates.values()):
        terminal = "N3C_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC"
    elif f4_donor_matched:
        terminal = "N3C_PARENT_SUFFICIENT_NEGATIVE"
    else:
        terminal = "N3C_MECHANISM_FAILED_NEGATIVE"

    result = {
        "schema": SCHEMA,
        "issue": 676,
        "family": "C_cross_family_operator_induction",
        "seed": SEED,
        "authority": AUTHORITY,
        "claim_boundary": CLAIM_BOUNDARY,
        "protocol": "development/orion-q-nlane-closure/N3_C_OPERATOR_INDUCTION_PROTOCOL.md",
        "budgets": {"donor_bfs_budget_per_heldout_n": DONOR_BFS_BUDGET},
        "study": run1,
        "determinism": {"run1_sha256": d1, "run2_sha256": d2, "identical": d1 == d2},
        "gates": gates,
        "terminal": terminal,
        "p10_authorized": False,
        "novelty_authorized": False,
    }

    print("ORIONQ_N3_C_OPERATOR_INDUCTION=" + canonical(result))
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N3_C_OPERATOR_INDUCTION_RESULTS.json")
    with open(out, "w") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
