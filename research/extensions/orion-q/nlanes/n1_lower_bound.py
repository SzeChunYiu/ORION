"""ORION-Q N1 lower bound: machine-checked closure of the old QC2 finite-candidate class.

Frozen protocol: development/orion-q-nlane-closure/N1_LOWER_BOUND_PROTOCOL.md (issue #674,
lower-bound programme; registered in issue comment 5355100391, never committed).

Proposition: with a finite candidate edit set C, an exact deterministic validity predicate V, and a
budget permitting full enumeration, exhaustive verification succeeds iff any valid candidate
exists; therefore every policy restricted to C satisfies Success(pi) <= Success(exhaustive)
pointwise. This closes exactly FINITE_COMPLETE_EDIT_SET + EXACT_VERIFIER +
FULL_ENUMERATION_BUDGET and nothing else.

Run:
    python research/extensions/orion-q/nlanes/n1_lower_bound.py
"""

from __future__ import annotations

import json
import os

import numpy as np

SCHEMA = "ORIONQ.N1_FiniteCandidateLowerBound.v1"
AUTHORITY = "N1_LOWER_BOUND__BENCHMARK_CLASS_CLOSURE_ONLY__EXACT_SYNTHETIC_ONLY"

C_SIZE = 12
SEED = 20260821
N_TASKS = 5_000
P_VALID = 0.08


def main() -> None:
    # --- Check 1: complete enumeration over all worlds and all policy outputs.
    # Any policy realization (deterministic, randomized, or adaptive in verification order)
    # terminates by emitting some output o in C or abstaining; its success on world V is V(o)
    # (0 for abstain). Exhaustive succeeds iff any(V). Checking V(o) <= any(V) for every world and
    # every output therefore exhausts the entire policy-outcome space of the class.
    comparisons = 0
    violations = 0
    for world in range(2**C_SIZE):
        v = [(world >> i) & 1 for i in range(C_SIZE)]
        exhaustive = int(any(v))
        for o in range(C_SIZE + 1):  # C_SIZE == ABSTAIN
            success = 0 if o == C_SIZE else v[o]
            comparisons += 1
            violations += int(success > exhaustive)
    g1 = violations == 0

    # --- Check 2: verification-order invariance of exhaustive success.
    order_checks = 0
    order_violations = 0
    base = list(range(C_SIZE))
    orders = [base[i:] + base[:i] for i in range(C_SIZE)] + [base[::-1]]
    for world in range(2**C_SIZE):
        v = [(world >> i) & 1 for i in range(C_SIZE)]
        ref = int(any(v))
        for order in orders:
            found = 0
            for c in order:  # full enumeration budget: every c may be verified
                if v[c]:
                    found = 1
                    break
            order_checks += 1
            order_violations += int(found != ref)
    g2 = order_violations == 0

    # --- Check 3: illustrative battery of concrete policies on sampled tasks.
    rng = np.random.default_rng(SEED)
    validity = rng.random((N_TASKS, C_SIZE)) < P_VALID
    exhaustive = validity.any(axis=1).astype(int)

    def first_valid(order_rows: np.ndarray) -> np.ndarray:
        out = np.zeros(N_TASKS, int)
        for i in range(N_TASKS):
            for c in order_rows[i]:
                if validity[i, c]:
                    out[i] = 1
                    break
        return out

    policies = {
        "EXHAUSTIVE": exhaustive,
        "FIXED_SINGLE_GUESS_C0": validity[:, 0].astype(int),
        "RANDOM_ORDER_FIRST_VALID": first_valid(
            np.argsort(rng.random((N_TASKS, C_SIZE)), axis=1)
        ),
        "GREEDY_LEARNED_ORDER": first_valid(
            np.tile(np.argsort(-validity.mean(axis=0)), (N_TASKS, 1))
        ),
    }
    battery = {}
    g3 = True
    for name, succ in policies.items():
        pointwise_ok = bool(np.all(succ <= exhaustive))
        g3 &= pointwise_ok
        battery[name] = {
            "solve_rate": float(succ.mean()),
            "pointwise_dominated_by_exhaustive": pointwise_ok,
        }

    gates = {
        "G1_COMPLETE_ENUMERATION_CHECK": bool(g1),
        "G2_ORDER_INVARIANCE": bool(g2),
        "G3_BATTERY_POINTWISE": bool(g3),
    }
    terminal = (
        "LOWER_BOUND_CLOSED_FOR_FINITE_COMPLETE_CLASS"
        if all(gates.values())
        else "LOWER_BOUND_CHECK_FAILED"
    )

    result = {
        "schema": SCHEMA,
        "issue": 674,
        "registered_in": "issue-674 comment 5355100391 (proposition never committed before)",
        "protocol": "development/orion-q-nlane-closure/N1_LOWER_BOUND_PROTOCOL.md",
        "date": "2026-08-21",
        "seed": SEED,
        "proposition": (
            "For finite C, exact V, and full-enumeration budget: Success(pi) <= "
            "Success(exhaustive) pointwise for every policy restricted to C; policies can improve "
            "only secondary quantities (number/cost/order of verifier calls), never solve rate."
        ),
        "checks": {
            "complete_enumeration": {
                "candidate_set_size": C_SIZE,
                "worlds_checked": 2**C_SIZE,
                "policy_outputs_per_world": C_SIZE + 1,
                "comparisons": comparisons,
                "violations": violations,
            },
            "order_invariance": {
                "orders_per_world": len(orders),
                "checks": order_checks,
                "violations": order_violations,
            },
            "battery": {"tasks": N_TASKS, "p_valid": P_VALID, "policies": battery},
        },
        "gates": gates,
        "terminal": terminal,
        "closed_class": "FINITE_COMPLETE_EDIT_SET + EXACT_VERIFIER + FULL_ENUMERATION_BUDGET",
        "not_closed": [
            "parameterized/infinite schemas",
            "generated representations",
            "incomplete applicability (VERIFIED/REFUTED/UNKNOWN)",
            "costly verification / bounded verifier budget",
            "resource-bounded search",
            "edits that change the candidate language itself",
        ],
        "consequence": (
            "The old QC2_NO_INCREMENTAL_VALUE solve-rate result is explained by a structural "
            "ceiling of its benchmark class, not evidence about P10 globally."
        ),
        "authority": AUTHORITY,
        "claim_boundary": (
            "Exact-synthetic machine-checked closure of one finite benchmark class only; grants no "
            "statement about method-space editing outside the closed class and no real-quantum "
            "authority."
        ),
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N1_LOWER_BOUND_RESULTS.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N1_LOWER_BOUND=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
