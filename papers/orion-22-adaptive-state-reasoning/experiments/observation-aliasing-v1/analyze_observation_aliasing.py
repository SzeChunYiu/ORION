#!/usr/bin/env python3
"""ORION22.OBSERVATION_ALIASING_ROBUSTNESS.v1 -- the common-optimum analyzer.

Decides, on the frozen pool, whether the ORION-22 robustness negative was a POLICY
failure or an INFORMATION failure.

Criterion (PROTOCOL.json): a deterministic observation-based zero-regret policy exists
iff every observation class z has a nonempty intersection of optimal action sets over
the environments sharing z.

Under the PRICE-BLIND surface the five regimes of a case share one observation, because
regimes differ only in the price vector. So each case is one class with five
environments, and the question is whether one allocation is optimal in all five.

Reuses the committed runner's own charge computation and priced objective. O(e) collects
EVERY optimal allocation, not one tie-broken representative -- recording a single argmin
would make every intersection a singleton and fabricate the answer.

  0 = measured    3 = could not check
"""
import importlib.util, json, sys
from pathlib import Path

TOP = Path(__file__).resolve().parents[2] / "top_tier"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m); return m


def main() -> int:
    sys.path.insert(0, str(TOP))
    try:
        runner = load("p12_runner", TOP / "run_p12_price_aware_successor_v1.py")
    except Exception as exc:
        print(json.dumps({"terminal": "T4_CANNOT_CHECK_POOL_OR_REGENERATION",
                          "reason": f"runner import failed: {exc}"}, indent=2))
        return 3

    stress, frozen = runner.stress, runner.frozen
    BUDGET, REGIMES = runner.BUDGET, runner.REGIMES

    def optimal_set(sids, declared, reason, state, p_b, p_s):
        """Every budget-feasible allocation attaining the priced optimum."""
        best, opts = None, []
        for mask in range(1 << len(sids)):
            sset = frozenset(sids[i] for i in range(len(sids)) if mask & (1 << i))
            if sum(declared[s] for s in sset) > BUDGET:
                continue
            build = sum(declared[s] for s in sset)
            serve = sum(state[s] if s in sset else reason[s] for s in sids)
            val = stress.priced(p_b, p_s, build, serve)
            if best is None or val < best:
                best, opts = val, [sset]
            elif val == best:
                opts.append(sset)
        return best, opts

    classes = []
    for src in ("p12_transfer_cases_v1.json", "p12_transfer_cases_expanded_v1.json"):
        pool = json.loads((TOP / src).read_text())
        for dom in pool["domains"]:
            domain = dom["domain"]
            for case in dom["cases"]:
                structures = case["structures"]
                sids = [st["sid"] for st in structures]
                declared = {st["sid"]: st["declared_cost"] for st in structures}
                frozen.prime_caches(domain, structures)
                reason, state, _, _ = stress.per_structure_charges(domain, structures)

                per_regime = {}
                for regime, p_b, p_s in REGIMES:
                    best, opts = optimal_set(sids, declared, reason, state, p_b, p_s)
                    if not opts:                       # control: O(e) is never empty
                        print(json.dumps({"terminal": "T4_CANNOT_CHECK_POOL_OR_REGENERATION",
                                          "reason": f"empty optimum for {case['case_id']}/{regime}"},
                                         indent=2))
                        return 3
                    per_regime[regime] = {"optimum": best, "optimal_actions": opts}

                inter = set.intersection(*[set(v["optimal_actions"]) for v in per_regime.values()])
                classes.append({
                    "pool": src, "domain": domain, "case_id": case["case_id"],
                    "structures": sids, "environments_in_class": len(per_regime),
                    "optimal_action_counts": {r: len(v["optimal_actions"]) for r, v in per_regime.items()},
                    "common_optimum_nonempty": bool(inter),
                    "common_optimum_size": len(inter),
                    "per_regime_optimum": {r: v["optimum"] for r, v in per_regime.items()},
                })

    singleton_bad = [c for c in classes if c["environments_in_class"] == 1 and not c["common_optimum_nonempty"]]
    if singleton_bad:                                  # control: singleton classes cannot be empty
        print(json.dumps({"terminal": "T4_CANNOT_CHECK_POOL_OR_REGENERATION",
                          "reason": "singleton class reported empty; analyzer defect",
                          "cases": [c["case_id"] for c in singleton_bad]}, indent=2))
        return 3

    empty = [c for c in classes if not c["common_optimum_nonempty"]]
    terminal = ("T1_EVERY_PRICE_BLIND_CLASS_HAS_A_COMMON_OPTIMUM" if not empty
                else "T2_SOME_PRICE_BLIND_CLASSES_EMPTY__PRICE_REFINEMENT_RESOLVES_ALL")

    print(json.dumps({
        "schema": "orion.orion22.observation-aliasing-robustness.result.v1",
        "protocol_identity": "ORION22.OBSERVATION_ALIASING_ROBUSTNESS.v1",
        "authority": "MEASUREMENT_ONLY", "scientific_authority_delta": "NONE",
        "surface": "price_blind", "regimes": [r[0] for r in REGIMES],
        "classes_total": len(classes),
        "classes_with_empty_common_optimum": len(empty),
        "empty_classes": [{"case_id": c["case_id"], "domain": c["domain"],
                           "per_regime_optimum": c["per_regime_optimum"]} for c in empty],
        "classes": classes,
        "price_aware_surface_note": (
            "Under the price-aware surface each (case, regime) is its own class because "
            "the price vector is readable, so every class is a singleton and its "
            "intersection equals O(e), which is nonempty by construction. Price "
            "refinement therefore resolves every empty class by splitting it."),
        "terminal": terminal,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
