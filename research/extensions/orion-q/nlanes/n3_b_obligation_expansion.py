"""ORION-Q N3-B deterministic exact-synthetic study: proof-obligation-driven grammar expansion.

Implements the frozen protocol
development/orion-q-nlane-closure/N3_B_OBLIGATION_EXPANSION_PROTOCOL.md
(issue #676, successor family B). Exact-synthetic bounded diagnostic only:
no real-quantum, no novelty, no P10 authority. Inexpressibility statements
are bounded-exhaustive (size-limited), never absolute.

Run:
    python research/extensions/orion-q/nlanes/n3_b_obligation_expansion.py
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os

SEED = 20260821
SCHEMA = "ORIONQ.N3B.ObligationGrammarExpansion.v1"
AUTHORITY = "exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority"
CLAIM_BOUNDARY = (
    "finite Z16 expression world only; bounded-exhaustive inexpressibility proofs "
    "at explicit size bounds, never absolute; minimal grammar expansion above a "
    "supplied grammar with donor first right of refusal; no claim about "
    "CEGIS/abstraction-refinement tooling or novelty"
)

S_CAND = 7
DONOR_BUDGET = 2_000_000
DOMAIN = tuple(range(16))

# --- G0 supplied grammar -------------------------------------------------
LEAVES = [tuple(DOMAIN)] + [tuple(c for _ in DOMAIN) for c in (0, 1, 2, 3)]

G0_BIN = {
    "ADD16": lambda a, b: tuple((x + y) % 16 for x, y in zip(a, b)),
    "MUL16": lambda a, b: tuple((x * y) % 16 for x, y in zip(a, b)),
    "MAX": lambda a, b: tuple(max(x, y) for x, y in zip(a, b)),
    "MIN": lambda a, b: tuple(min(x, y) for x, y in zip(a, b)),
}
G0_UN: dict[str, object] = {}

# --- extension library (each cost 1) ------------------------------------
EXT_BIN = {"XOR": lambda a, b: tuple(x ^ y for x, y in zip(a, b))}
EXT_UN = {
    "SHR1": lambda a: tuple(x >> 1 for x in a),
    "NOT16": lambda a: tuple(15 - x for x in a),
    "MOD2": lambda a: tuple(x & 1 for x in a),
}
EXT_NAMES = sorted(list(EXT_BIN) + list(EXT_UN))  # MOD2, NOT16, SHR1, XOR

SPEC_B1 = tuple(x ^ (x >> 1) for x in DOMAIN)  # Gray code
SPEC_B2 = tuple((2 * x + 3) % 16 for x in DOMAIN)
SPEC_B3 = (7, 12, 1, 14, 9, 0, 5, 11, 3, 15, 6, 2, 13, 8, 10, 4)  # fixed hostile table


def enumerate_language(un_ops, bin_ops, max_size, budget):
    """Bottom-up exact enumeration by AST size with value-table dedup.

    Returns (seen: table -> minimal size, evals, largest fully exhausted size,
    budget_hit). If budget is hit mid-size, that size is NOT counted exhausted.
    """
    seen: dict[tuple[int, ...], int] = {}
    by_size: dict[int, list[tuple[int, ...]]] = {}
    evals = 0
    exhausted = 0
    for leaf in LEAVES:
        if leaf not in seen:
            seen[leaf] = 1
            by_size.setdefault(1, []).append(leaf)
    size = 1
    exhausted = 1
    while size < max_size:
        size += 1
        new: list[tuple[int, ...]] = []
        # unary: argument of size-1
        for arg in by_size.get(size - 1, ()):
            for fn in un_ops.values():
                evals += 1
                if evals > budget:
                    return seen, evals - 1, exhausted, True
                t = fn(arg)
                if t not in seen:
                    seen[t] = size
                    new.append(t)
        # binary: left size ls, right size size-1-ls
        for ls in range(1, size - 1):
            rs = size - 1 - ls
            for a in by_size.get(ls, ()):
                for b in by_size.get(rs, ()):
                    for fn in bin_ops.values():
                        evals += 1
                        if evals > budget:
                            return seen, evals - 1, exhausted, True
                        t = fn(a, b)
                        if t not in seen:
                            seen[t] = size
                            new.append(t)
        by_size[size] = new
        exhausted = size
    return seen, evals, exhausted, False


def subset_ops(subset: tuple[str, ...]):
    un = dict(G0_UN)
    bi = dict(G0_BIN)
    for name in subset:
        if name in EXT_UN:
            un[name] = EXT_UN[name]
        else:
            bi[name] = EXT_BIN[name]
    return un, bi


def candidate(spec: tuple[int, ...], counter: dict[str, int]) -> dict[str, object]:
    """Prespecified N3-B candidate mechanism."""
    seen, ev, exhausted, _ = enumerate_language(G0_UN, G0_BIN, S_CAND, DONOR_BUDGET)
    counter["evals"] += ev
    if spec in seen:
        return {
            "g0_sufficient": True,
            "expansion_proposed": [],
            "expansion_cost": 0,
            "synthesized_size": seen[spec],
            "parent_sufficient": True,
            "obligation_unresolved": False,
            "subsets_tried": 0,
            "cheaper_subsets_all_failed": None,
        }
    # proof obligation: bounded inexpressibility of spec in G0 at size <= exhausted
    tried = []
    for cost in range(1, len(EXT_NAMES) + 1):
        for subset in itertools.combinations(EXT_NAMES, cost):
            un, bi = subset_ops(subset)
            sseen, sev, _, _ = enumerate_language(un, bi, S_CAND, DONOR_BUDGET)
            counter["evals"] += sev
            found = spec in sseen
            tried.append({"subset": list(subset), "cost": cost, "found": bool(found)})
            if found:
                cheaper_failed = all(not t["found"] for t in tried[:-1])
                return {
                    "g0_sufficient": False,
                    "g0_obligation_bound": exhausted,
                    "expansion_proposed": list(subset),
                    "expansion_cost": cost,
                    "synthesized_size": sseen[spec],
                    "parent_sufficient": False,
                    "obligation_unresolved": False,
                    "subsets_tried": len(tried),
                    "cheaper_subsets_all_failed": bool(cheaper_failed),
                    "subset_trace": tried,
                }
    return {
        "g0_sufficient": False,
        "g0_obligation_bound": exhausted,
        "expansion_proposed": None,
        "expansion_cost": None,
        "synthesized_size": None,
        "parent_sufficient": False,
        "obligation_unresolved": True,
        "subsets_tried": len(tried),
        "cheaper_subsets_all_failed": None,
        "subset_trace": tried,
    }


def donor_g0(spec: tuple[int, ...]) -> dict[str, object]:
    """Supplied-grammar donor at full matched budget, increasing size until budget binds."""
    seen, ev, exhausted, budget_hit = enumerate_language(G0_UN, G0_BIN, 40, DONOR_BUDGET)
    return {
        "found": spec in seen,
        "size_if_found": seen.get(spec),
        "evals": ev,
        "largest_fully_exhausted_size": exhausted,
        "budget_hit": bool(budget_hit),
        "distinct_tables": len(seen),
    }


def run_study() -> dict[str, object]:
    counter = {"evals": 0}
    arms = {}
    for arm, spec in (("B1", SPEC_B1), ("B2", SPEC_B2), ("B3", SPEC_B3)):
        cand = candidate(spec, counter)
        donor = donor_g0(spec)
        # trivial-bloat baseline: all extensions at once (cost 4)
        un, bi = subset_ops(tuple(EXT_NAMES))
        bseen, bev, _, _ = enumerate_language(un, bi, S_CAND, DONOR_BUDGET)
        arms[arm] = {
            "spec": list(spec),
            "candidate": cand,
            "donor_g0": donor,
            "bloat_baseline": {
                "cost": len(EXT_NAMES),
                "found": spec in bseen,
                "size_if_found": bseen.get(spec),
                "evals": bev,
            },
        }
    return {"arms": arms, "candidate_total_evals": counter["evals"]}


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    run1 = run_study()
    run2 = run_study()
    d1 = hashlib.sha256(canonical(run1).encode()).hexdigest()
    d2 = hashlib.sha256(canonical(run2).encode()).hexdigest()

    b1 = run1["arms"]["B1"]
    b2 = run1["arms"]["B2"]
    b3 = run1["arms"]["B3"]

    gates = {
        "GB0_budget_sanity": run1["candidate_total_evals"] <= DONOR_BUDGET,
        "GB1_residual_value": (
            not b1["donor_g0"]["found"]
            and not b1["candidate"]["g0_sufficient"]
            and b1["candidate"]["expansion_proposed"] is not None
            and b1["candidate"]["expansion_cost"] == 2
            and bool(b1["candidate"]["cheaper_subsets_all_failed"])
            and b1["candidate"]["expansion_cost"] < b1["bloat_baseline"]["cost"]
            and b1["bloat_baseline"]["found"]
        ),
        "GB2_donor_first_refusal": (
            b2["donor_g0"]["found"]
            and b2["candidate"]["g0_sufficient"]
            and b2["candidate"]["expansion_proposed"] == []
            and b2["candidate"]["parent_sufficient"]
        ),
        "GB3_hostile_catch": (
            not b3["donor_g0"]["found"]
            and b3["candidate"]["obligation_unresolved"]
            and b3["candidate"]["expansion_proposed"] is None
        ),
        "GB4_determinism": d1 == d2,
    }
    if all(gates.values()):
        terminal = "N3B_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC"
    elif b1["donor_g0"]["found"]:
        terminal = "N3B_PARENT_SUFFICIENT_NEGATIVE"
    else:
        terminal = "N3B_MECHANISM_FAILED_NEGATIVE"

    result = {
        "schema": SCHEMA,
        "issue": 676,
        "family": "B_proof_obligation_driven_grammar_expansion",
        "seed": SEED,
        "authority": AUTHORITY,
        "claim_boundary": CLAIM_BOUNDARY,
        "protocol": "development/orion-q-nlane-closure/N3_B_OBLIGATION_EXPANSION_PROTOCOL.md",
        "budgets": {"candidate_size_bound": S_CAND, "donor_eval_budget": DONOR_BUDGET},
        "study": run1,
        "determinism": {"run1_sha256": d1, "run2_sha256": d2, "identical": d1 == d2},
        "gates": gates,
        "terminal": terminal,
        "p10_authorized": False,
        "novelty_authorized": False,
    }

    print("ORIONQ_N3_B_OBLIGATION_EXPANSION=" + canonical(result))
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N3_B_OBLIGATION_EXPANSION_RESULTS.json")
    with open(out, "w") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
