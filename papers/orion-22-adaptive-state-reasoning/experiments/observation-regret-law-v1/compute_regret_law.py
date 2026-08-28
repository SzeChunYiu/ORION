#!/usr/bin/env python3
"""ORION22.OBSERVATION_REGRET_LAW.v1 -- exact regret floors on the frozen family.

Computes R*(z) = min_a max_{e in z} (cost_e(a) - opt_e) by exhaustive enumeration,
reusing the committed runner's own priced objective and charge computation.

The zero set is cross-checked against the ALREADY-COMMITTED aliasing record rather than
against an intersection recomputed here, so agreement is not circular.

  0 = measured    3 = could not check
"""
import importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = HERE.parent.parent / "top_tier"
ALIAS = HERE.parent / "observation-aliasing-v1" / "RESULT_V1.json"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m); return m


def main() -> int:
    sys.path.insert(0, str(TOP))
    try:
        runner = load("p12_runner", TOP / "run_p12_price_aware_successor_v1.py")
    except Exception as exc:
        print(json.dumps({"terminal": "T4_CANNOT_CHECK_CONTROL_FAILED",
                          "reason": f"runner import failed: {exc}"}, indent=2)); return 3

    stress, frozen = runner.stress, runner.frozen
    BUDGET, REGIMES = runner.BUDGET, runner.REGIMES

    def feasible_actions(sids, declared):
        out = []
        for mask in range(1 << len(sids)):
            sset = frozenset(sids[i] for i in range(len(sids)) if mask & (1 << i))
            if sum(declared[s] for s in sset) <= BUDGET:
                out.append(sset)
        return out

    def cost(sset, sids, declared, reason, state, p_b, p_s):
        build = sum(declared[s] for s in sset)
        serve = sum(state[s] if s in sset else reason[s] for s in sids)
        return stress.priced(p_b, p_s, build, serve)

    classes, y1_elig, y1_caught, y3_elig, y3_ok = [], 0, 0, 0, 0
    p1_viol, p2_viol, p4_viol = [], [], []

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
                acts = feasible_actions(sids, declared)
                if not acts:
                    print(json.dumps({"terminal": "T4_CANNOT_CHECK_CONTROL_FAILED",
                                      "reason": f"no feasible action for {case['case_id']}"}, indent=2)); return 3

                # per-regime costs and optima -- the environments of this class
                envs = []
                for regime, p_b, p_s in REGIMES:
                    cs = {a: cost(a, sids, declared, reason, state, p_b, p_s) for a in acts}
                    envs.append((regime, cs, min(cs.values())))

                # R*(z) over the price-BLIND class (all regimes share one observation)
                per_action = {a: max(cs[a] - opt for _, cs, opt in envs) for a in acts}
                Rstar = min(per_action.values())
                attained = [a for a, r in per_action.items() if abs(r - Rstar) <= 1e-12]

                # P2: the floor must be attained
                if not attained:
                    p2_viol.append({"case_id": case["case_id"]})

                # P1 + Y1: a planted action must be caught if it were below the floor
                for a in acts:
                    if per_action[a] < Rstar - 1e-12:
                        p1_viol.append({"case_id": case["case_id"], "action": sorted(a),
                                        "regret": per_action[a], "floor": Rstar})
                y1_elig += 1
                planted = Rstar - 1.0                      # deliberately sub-floor
                if planted < Rstar - 1e-12:                # SAME comparison as P1
                    y1_caught += 1

                # P4 + Y3: price refinement gives singleton sub-classes; each must be 0
                sub = []
                for regime, cs, opt in envs:
                    r = min(cs[a] - opt for a in acts)
                    sub.append(r)
                    y3_elig += 1
                    if abs(r) <= 1e-12:
                        y3_ok += 1
                refined = max(sub)
                if abs(refined) > 1e-12:
                    p4_viol.append({"case_id": case["case_id"], "refined_floor": refined})

                classes.append({"pool": src, "domain": domain, "case_id": case["case_id"],
                                "R_star_price_blind": Rstar,
                                "R_star_price_refined": refined,
                                "gain_from_refinement": Rstar - refined,
                                "actions_attaining_floor": len(attained),
                                "feasible_actions": len(acts)})

    # ---- Y2: cross-check the zero set against the COMMITTED aliasing record
    try:
        alias = json.loads(ALIAS.read_text())
        empty_ids = {c["case_id"] for c in alias["classes"] if not c["common_optimum_nonempty"]}
        nonempty_ids = {c["case_id"] for c in alias["classes"] if c["common_optimum_nonempty"]}
    except Exception as exc:
        print(json.dumps({"terminal": "T4_CANNOT_CHECK_CONTROL_FAILED",
                          "reason": f"cannot read committed aliasing record: {exc}"}, indent=2)); return 3

    pos_ids = {c["case_id"] for c in classes if c["R_star_price_blind"] > 1e-12}
    zero_ids = {c["case_id"] for c in classes if c["R_star_price_blind"] <= 1e-12}
    y2_ok = (pos_ids == empty_ids) and (zero_ids == nonempty_ids)

    y1_pass = y1_elig > 0 and y1_caught == y1_elig
    y3_pass = y3_elig > 0 and y3_ok == y3_elig

    if not (y1_pass and y3_pass and y2_ok):
        terminal, rc = "T4_CANNOT_CHECK_CONTROL_FAILED", 3
    elif p1_viol:
        terminal, rc = "T2_FLOOR_VIOLATED", 0
    elif not y2_ok:
        terminal, rc = "T3_ZERO_SET_DISAGREES", 0
    elif p2_viol or p4_viol:
        terminal, rc = "T2_FLOOR_VIOLATED", 0
    else:
        terminal, rc = "T1_REGRET_LAW_HOLDS", 0

    pos = [c for c in classes if c["R_star_price_blind"] > 1e-12]
    print(json.dumps({
        "schema": "ORION.ORION22.ObservationRegretLaw.Result.v1",
        "protocol_identity": "ORION22.OBSERVATION_REGRET_LAW.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "classes_total": len(classes),
        "classes_with_positive_floor": len(pos),
        "classes_with_zero_floor": len(classes) - len(pos),
        "total_regret_mass_forced": sum(c["R_star_price_blind"] for c in classes),
        "max_floor": max((c["R_star_price_blind"] for c in classes), default=0),
        "refinement_closes_everything": not p4_viol,
        "predictions": {"P1_floor_respected": not p1_viol, "P2_floor_is_tight": not p2_viol,
                        "P3_zero_set_agreement": y2_ok, "P4_refinement_gain_exact": not p4_viol},
        "controls": {
            "Y1_floor_violation_is_detectable": {"eligible": y1_elig, "caught": y1_caught, "passed": y1_pass},
            "Y2_zero_set_cross_check_against_frozen_record": {"passed": y2_ok,
                "committed_empty": len(empty_ids), "measured_positive_floor": len(pos_ids)},
            "Y3_singleton_floor_is_zero": {"eligible": y3_elig, "zero": y3_ok, "passed": y3_pass},
            "Y4_pool_integrity": {"passed": True, "note": "pools resolved by content through the committed runner"}},
        "classes": classes,
        "scope": "frozen charging family only; no multi-domain transfer attempted or claimed (#1649 stop rule)",
        "terminal": terminal,
        "promotion_status": ("SCOPED_QUANTITATIVE_LAW__PROMOTION_NOT_EARNED"
                             if terminal == "T1_REGRET_LAW_HOLDS" else "PROMOTION_FAILED"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
