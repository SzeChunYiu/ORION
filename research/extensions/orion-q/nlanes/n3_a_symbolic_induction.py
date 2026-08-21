"""ORION-Q N3-A deterministic exact-synthetic study: finite optimum -> symbolic family induction.

Implements the frozen protocol
development/orion-q-nlane-closure/N3_A_SYMBOLIC_INDUCTION_PROTOCOL.md
(issue #676, successor family A). Exact-synthetic bounded diagnostic only:
no real-quantum, no novelty, no P10 authority.

Run:
    python research/extensions/orion-q/nlanes/n3_a_symbolic_induction.py
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import deque

SEED = 20260821
SCHEMA = "ORIONQ.N3A.SymbolicFamilyInduction.v1"
AUTHORITY = "exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority"
CLAIM_BOUNDARY = (
    "exact-synthetic CNOT/GF(2) worlds only; symbolic-family induction above a "
    "supplied concrete grammar; supplied-parametric donor holds first right of "
    "refusal; no claim about real quantum synthesis, QSynth-class tools, or novelty"
)

TRAIN_N = (2, 3, 4, 5)
HELDOUT_A1 = (8, 10, 12)
HELDOUT_A3 = (6, 8, 10)
DONOR_BFS_BUDGET = 200_000
TRAIN_BFS_BUDGET = 1_000_000
COEFF_RANGE = (-2, -1, 0, 1, 2)
ALPHA_RANGE = (0, 1, 2)
BETA_RANGE = (-2, -1, 0, 1, 2)


def identity_rows(n: int) -> tuple[int, ...]:
    return tuple(1 << i for i in range(n))


def apply_program(n: int, gates: list[tuple[int, int]]) -> tuple[int, ...]:
    rows = list(identity_rows(n))
    for c, t in gates:
        rows[t] ^= rows[c]
    return tuple(rows)


def prefix_parity_target(n: int) -> tuple[int, ...]:
    return tuple((1 << (i + 1)) - 1 for i in range(n))


def hostile_target(n: int) -> tuple[int, ...]:
    rows = list(prefix_parity_target(n))
    if n >= 6:
        rows[n - 2], rows[n - 1] = rows[n - 1], rows[n - 2]
    return tuple(rows)


def all_gates(n: int) -> list[tuple[int, int]]:
    return [(c, t) for c in range(n) for t in range(n) if c != t]


def bfs_search(n: int, target: tuple[int, ...], budget: int) -> dict[str, object]:
    """BFS over CNOT applications; first hit is a proved minimal-length program."""
    start = identity_rows(n)
    gates = all_gates(n)
    if start == target:
        return {"found": True, "min_length": 0, "program": [], "expansions": 0}
    parent: dict[tuple[int, ...], tuple[tuple[int, ...], tuple[int, int]]] = {}
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
                return {
                    "found": False,
                    "min_length": None,
                    "program": None,
                    "expansions": expansions - 1,
                    "max_depth_reached": max_depth,
                    "budget_exhausted": True,
                }
            rows = list(state)
            rows[t] ^= rows[c]
            child = tuple(rows)
            if child in depth:
                continue
            depth[child] = d + 1
            max_depth = max(max_depth, d + 1)
            parent[child] = (state, (c, t))
            if child == target:
                prog: list[tuple[int, int]] = []
                cur = child
                while cur != start:
                    prev, g = parent[cur]
                    prog.append(g)
                    cur = prev
                prog.reverse()
                return {
                    "found": True,
                    "min_length": d + 1,
                    "program": prog,
                    "expansions": expansions,
                }
            queue.append(child)
    return {"found": False, "min_length": None, "program": None, "expansions": expansions}


def schema_program(n: int, a: int, b: int, c: int, d: int, alpha: int, beta: int):
    length = alpha * n + beta
    if length < 0:
        return None
    gates = []
    for t in range(length):
        src = a * t + b
        dst = c * t + d
        if not (0 <= src < n and 0 <= dst < n) or src == dst:
            return None
        gates.append((src, dst))
    return gates


def induce_family(train_artifacts: dict[int, dict[str, object]], counter: dict[str, int]):
    """First lexicographic schema tuple exactly matching all train targets at proved minimal length."""
    for a in COEFF_RANGE:
        for b in COEFF_RANGE:
            for c in COEFF_RANGE:
                for d in COEFF_RANGE:
                    for alpha in ALPHA_RANGE:
                        for beta in BETA_RANGE:
                            ok = True
                            for n in TRAIN_N:
                                counter["constructed"] += 1
                                gates = schema_program(n, a, b, c, d, alpha, beta)
                                art = train_artifacts[n]
                                if (
                                    gates is None
                                    or len(gates) != art["min_length"]
                                    or apply_program(n, gates) != tuple(art["target"])
                                ):
                                    ok = False
                                    break
                            if ok:
                                return (a, b, c, d, alpha, beta)
    return None


def macro_expansion(name: str, n: int) -> list[tuple[int, int]]:
    if name == "CHAIN":
        return [(t, t + 1) for t in range(n - 1)]
    if name == "FAN":
        return [(0, t + 1) for t in range(n - 1)]
    if name == "REV_CHAIN":
        return [(n - 2 - t, n - 1 - t) for t in range(n - 1)]
    raise ValueError(name)


def run_study() -> dict[str, object]:
    counter = {"constructed": 0}

    # Donor-supplied proved-optimal train artifacts (world A1/A3 share train targets).
    train_artifacts: dict[int, dict[str, object]] = {}
    for n in TRAIN_N:
        res = bfs_search(n, prefix_parity_target(n), TRAIN_BFS_BUDGET)
        train_artifacts[n] = {
            "target": list(prefix_parity_target(n)),
            "found": res["found"],
            "min_length": res["min_length"],
            "program": res["program"],
            "bfs_expansions": res["expansions"],
        }

    induced = induce_family(train_artifacts, counter)

    # ---- World A1 (residual arm) ----
    a1_heldout = {}
    for n in HELDOUT_A1:
        target = prefix_parity_target(n)
        cand_ok = False
        cand_len = None
        if induced is not None:
            counter["constructed"] += 1
            gates = schema_program(n, *induced)
            cand_ok = gates is not None and apply_program(n, gates) == target
            cand_len = None if gates is None else len(gates)
        donor = bfs_search(n, target, DONOR_BFS_BUDGET)
        # trivial baseline: replay largest train artifact embedded on n wires
        counter["constructed"] += 1
        trivial_prog = train_artifacts[5]["program"] or []
        trivial_ok = apply_program(n, list(trivial_prog)) == target
        a1_heldout[str(n)] = {
            "candidate_exact_verified": bool(cand_ok),
            "candidate_program_length": cand_len,
            "donor_found": bool(donor["found"]),
            "donor_expansions": donor["expansions"],
            "donor_max_depth_reached": donor.get("max_depth_reached"),
            "trivial_baseline_verified": bool(trivial_ok),
        }
    a1_family_claim = induced is not None and all(
        v["candidate_exact_verified"] for v in a1_heldout.values()
    )

    # ---- World A2 (donor-sufficient arm: supplied parametric grammar) ----
    a2_heldout = {}
    for n in HELDOUT_A1:
        target = prefix_parity_target(n)
        matches = {}
        for name in ("CHAIN", "FAN", "REV_CHAIN"):
            counter["constructed"] += 1
            matches[name] = apply_program(n, macro_expansion(name, n)) == target
        a2_heldout[str(n)] = {"parametric_donor_matched": bool(any(matches.values())), "macro_matches": matches}
    a2_parent_sufficient = all(v["parametric_donor_matched"] for v in a2_heldout.values())
    a2_candidate_residual_claim = not a2_parent_sufficient  # prespecified rule: donor first refusal

    # ---- World A3 (hostile arm) ----
    a3_heldout = {}
    for n in HELDOUT_A3:
        target = hostile_target(n)
        cand_ok = False
        if induced is not None:
            counter["constructed"] += 1
            gates = schema_program(n, *induced)
            cand_ok = gates is not None and apply_program(n, gates) == target
        a3_heldout[str(n)] = {"candidate_exact_verified": bool(cand_ok)}
    a3_schema_fit_train = induced is not None
    a3_verifier_rejected = any(not v["candidate_exact_verified"] for v in a3_heldout.values())
    a3_family_claim = a3_schema_fit_train and all(
        v["candidate_exact_verified"] for v in a3_heldout.values()
    )

    return {
        "train": {
            str(n): {
                "min_length": train_artifacts[n]["min_length"],
                "program": train_artifacts[n]["program"],
                "bfs_expansions": train_artifacts[n]["bfs_expansions"],
            }
            for n in TRAIN_N
        },
        "induced_schema_tuple": list(induced) if induced is not None else None,
        "candidate_constructed_programs": counter["constructed"],
        "world_A1": {"heldout": a1_heldout, "family_claim": bool(a1_family_claim)},
        "world_A2": {
            "heldout": a2_heldout,
            "parent_sufficient": bool(a2_parent_sufficient),
            "candidate_residual_claim": bool(a2_candidate_residual_claim),
        },
        "world_A3": {
            "heldout": a3_heldout,
            "schema_fit_train": bool(a3_schema_fit_train),
            "verifier_rejected": bool(a3_verifier_rejected),
            "family_claim": bool(a3_family_claim),
        },
    }


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    run1 = run_study()
    run2 = run_study()
    d1 = hashlib.sha256(canonical(run1).encode()).hexdigest()
    d2 = hashlib.sha256(canonical(run2).encode()).hexdigest()

    s = run1
    a1 = s["world_A1"]
    donor_matched_any = any(v["donor_found"] for v in a1["heldout"].values())
    trivial_matched_any = any(v["trivial_baseline_verified"] for v in a1["heldout"].values())
    gates = {
        "GA0_budget_sanity": s["candidate_constructed_programs"] <= DONOR_BFS_BUDGET,
        "GA1_residual_value": (
            a1["family_claim"] and not donor_matched_any and not trivial_matched_any
        ),
        "GA2_donor_first_refusal": (
            s["world_A2"]["parent_sufficient"]
            and not s["world_A2"]["candidate_residual_claim"]
        ),
        "GA3_hostile_catch": (
            s["world_A3"]["schema_fit_train"]
            and s["world_A3"]["verifier_rejected"]
            and not s["world_A3"]["family_claim"]
        ),
        "GA4_determinism": d1 == d2,
    }
    if all(gates.values()):
        terminal = "N3A_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC"
    elif (donor_matched_any or trivial_matched_any) and a1["family_claim"]:
        terminal = "N3A_PARENT_SUFFICIENT_NEGATIVE"
    else:
        terminal = "N3A_MECHANISM_FAILED_NEGATIVE"

    result = {
        "schema": SCHEMA,
        "issue": 676,
        "family": "A_finite_optimum_symbolic_family_induction",
        "seed": SEED,
        "authority": AUTHORITY,
        "claim_boundary": CLAIM_BOUNDARY,
        "protocol": "development/orion-q-nlane-closure/N3_A_SYMBOLIC_INDUCTION_PROTOCOL.md",
        "budgets": {
            "donor_bfs_budget_per_heldout_n": DONOR_BFS_BUDGET,
            "train_bfs_budget": TRAIN_BFS_BUDGET,
        },
        "study": s,
        "determinism": {"run1_sha256": d1, "run2_sha256": d2, "identical": d1 == d2},
        "gates": gates,
        "terminal": terminal,
        "p10_authorized": False,
        "novelty_authorized": False,
    }

    print("ORIONQ_N3_A_SYMBOLIC_INDUCTION=" + canonical(result))
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N3_A_SYMBOLIC_INDUCTION_RESULTS.json")
    with open(out, "w") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
