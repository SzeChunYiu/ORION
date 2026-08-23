#!/usr/bin/env python3
"""P12 robustness stress runner V1 (prices, distribution shift, expansion).

Executes P12_ROBUSTNESS_PROTOCOL_V2 over the frozen V1 case set
(p12_transfer_cases_v1.json, 9 cases) and the frozen expanded set
(p12_transfer_cases_expanded_v1.json, 27 cases).

The allocator, the locus engines and the cost accounting are imported
UNMODIFIED from the frozen V1 runner (run_transfer_allocation_v1.py):
  frozen.allocator_selection        — the unchanged, price-oblivious rule
  frozen.state_always_selection     — STATE restriction
  frozen.serve_case / build_cost    — frozen locus charge accounting
  frozen.ground_truth               — exact truth path (RG1)
Only the priced objective wrapper (p_build, p_serve), the mixes and the
reporting are new. Stdlib only; deterministic byte-for-byte stdout.

Budget semantics (pre-registered):
  S1 (gates):  nominal budget on unpriced declared construction cost (<=500)
  S2 (report): priced-budget violation flags, characterization only
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_transfer_allocation_v1 as frozen  # noqa: E402

ALLOC = frozen.ALLOCATOR_NAME
ARMS = ["REASON_ONLY", "STATE_ALWAYS", ALLOC]

REGIMES = [
    ("FLAT", 1, 1),
    ("MEM2X", 2, 1),
    ("CMP2X", 1, 2),
    ("MEM4X", 4, 1),
    ("CMP4X", 1, 4),
]

B1_MIXES = [
    ("MIX_BAL_27", {"SAT_PROPAGATION": 9, "PATH_PLANNING": 9, "KNAPSACK": 9}),
    ("MIX_KNAP_HEAVY", {"SAT_PROPAGATION": 4, "PATH_PLANNING": 4,
                        "KNAPSACK": 9}),
    ("MIX_PATH_HEAVY", {"SAT_PROPAGATION": 4, "PATH_PLANNING": 9,
                        "KNAPSACK": 4}),
    ("MIX_SAT_HEAVY", {"SAT_PROPAGATION": 9, "PATH_PLANNING": 4,
                       "KNAPSACK": 4}),
]

B2_MIXES = [
    ("JOINT_BAL", {"SAT_PROPAGATION": 3, "PATH_PLANNING": 3, "KNAPSACK": 3}),
    ("JOINT_KNAP_HEAVY", {"SAT_PROPAGATION": 2, "PATH_PLANNING": 2,
                          "KNAPSACK": 6}),
    ("JOINT_PATH_HEAVY", {"SAT_PROPAGATION": 2, "PATH_PLANNING": 6,
                          "KNAPSACK": 2}),
]

DOMAIN_ORDER = ["SAT_PROPAGATION", "PATH_PLANNING", "KNAPSACK"]


def load_cases(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


def per_structure_charges(domain, structures):
    """Frozen charge decomposition per structure (additive by construction).

    reason_serve: serve_case with the structure never materialized.
    state_serve:  serve_case with the structure materialized (cache primed
                  for the singleton case, matching frozen accounting).
    Outputs are captured for RG1 exactness.
    """
    reason = {}
    state = {}
    reason_out = {}
    state_out = {}
    for st in structures:
        sid = st["sid"]
        ops, outs = frozen.serve_case([st], set(), domain)
        reason[sid], reason_out[sid] = ops, outs
        frozen.prime_caches(domain, [st])
        ops, outs = frozen.serve_case([st], {sid}, domain)
        state[sid], state_out[sid] = ops, outs
    return reason, state, reason_out, state_out


def priced(p_build, p_serve, build, serve):
    return p_build * build + p_serve * serve


def evaluate_case(domain, case):
    """All arms + priced oracle for one case, all regimes."""
    structures = case["structures"]
    sids = [st["sid"] for st in structures]
    declared = {st["sid"]: st["declared_cost"] for st in structures}
    truth, verify_ops = frozen.ground_truth(domain, structures)
    reason, state, reason_out, state_out = per_structure_charges(
        domain, structures)

    selections = {
        "REASON_ONLY": [],
        "STATE_ALWAYS": frozen.state_always_selection(structures),
        ALLOC: frozen.allocator_selection(structures),
    }

    # S1 nominal-budget priced oracle (exhaustive, pre-registered)
    n = len(structures)
    subsets = []
    for mask in range(1 << n):
        sset = frozenset(sids[i] for i in range(n) if mask & (1 << i))
        if sum(declared[s] for s in sset) > frozen.BUDGET:
            continue
        subsets.append(sset)

    # outputs are regime-invariant (selection is price-oblivious); record
    # once for the independent checker's exactness comparison
    arm_outputs = {}
    for arm in ARMS:
        sel = set(selections[arm])
        arm_outputs[arm] = [state_out[s] if s in sel else reason_out[s]
                            for s in sids]

    cells = {}
    exact_all = True
    for regime, p_b, p_s in REGIMES:
        oracle_best = None
        oracle_set = None
        for sset in subsets:
            build = sum(declared[s] for s in sset)
            serve = sum(state[s] if s in sset else reason[s]
                        for s in sids)
            val = priced(p_b, p_s, build, serve)
            if oracle_best is None or val < oracle_best:
                oracle_best, oracle_set = val, sset
        arm_cells = {}
        for arm in ARMS:
            sel = set(selections[arm])
            build = sum(declared[s] for s in sel)
            serve = sum(state[s] if s in sel else reason[s] for s in sids)
            outputs = [state_out[s] if s in sel else reason_out[s]
                       for s in sids]
            exact = outputs == truth
            exact_all = exact_all and exact
            val = priced(p_b, p_s, build, serve)
            arm_cells[arm] = {
                "materialized": sorted(sel),
                "build_charge": build,
                "serve_charge": serve,
                "priced_realized": val,
                "priced_regret": val - oracle_best,
                "outputs_exact": exact,
            }
        alloc_build = sum(declared[s] for s in set(selections[ALLOC]))
        cells[regime] = {
            "p_build": p_b,
            "p_serve": p_s,
            "priced_oracle": {
                "materialized": sorted(oracle_set),
                "priced_realized": oracle_best,
            },
            "arms": arm_cells,
            "s2_priced_budget_violation_allocator":
                p_b * alloc_build > frozen.BUDGET,
        }
    return {
        "case_id": case["case_id"],
        "structure_q": {st["sid"]: len(st["queries"])
                        for st in structures},
        "declared_costs": declared,
        "selections": {arm: sorted(v) for arm, v in selections.items()},
        "verify_ops": verify_ops,
        "ground_truth": truth,
        "arm_outputs": arm_outputs,
        "regimes": cells,
        "outputs_exact_all_arms_all_regimes": exact_all,
    }


def flat_direct_accounting_check(domain, case_reports):
    """RG1-adjacent internal consistency: decomposed FLAT accounting equals
    the frozen V1 direct serve_case/build_cost path for every arm."""
    for case in case_reports:
        cid = case["case_id"]
        structures = [st for st in case["structures"]]
        frozen.prime_caches(domain, structures)
        for arm in ARMS:
            sel = set(case["selections"][arm])
            direct = (frozen.build_cost(structures, sel)
                      + frozen.serve_case(structures, sel, domain)[0])
            decomposed = case["regimes"]["FLAT"]["arms"][arm][
                "build_charge"] + case["regimes"]["FLAT"]["arms"][arm][
                "serve_charge"]
            if direct != decomposed:
                return False, f"{domain}:{cid}:{arm} direct={direct} " \
                              f"decomposed={decomposed}"
    return True, ""


def evaluate_set(cases, tag):
    domains = []
    v1_flat_zero_regret = True
    for dom in cases["domains"]:
        domain = dom["domain"]
        case_reports = []
        for case in dom["cases"]:
            rep = evaluate_case(domain, case)
            case_reports.append(rep)
            if tag == "V1_9" and rep["regimes"]["FLAT"]["arms"][ALLOC][
                    "priced_regret"] != 0:
                v1_flat_zero_regret = False
        ok, msg = flat_direct_accounting_check(domain, [
            {"case_id": r["case_id"],
             "structures": c["structures"],
             "selections": r["selections"]}
            for r, c in zip(case_reports, dom["cases"])])
        domains.append({
            "domain": domain,
            "charged_unit": dom["charged_unit"],
            "cases": case_reports,
            "flat_direct_accounting_consistent": ok,
            "flat_direct_accounting_violation": msg,
        })
    return {
        "set": tag,
        "case_count": sum(len(d["cases"]) for d in domains),
        "v1_flat_zero_regret_replicated":
            v1_flat_zero_regret if tag == "V1_9" else None,
        "domains": domains,
    }


def b1_mix_aggregates(expanded_report):
    """Case-level mixes: aggregate per-case S1 outcomes (pre-registered)."""
    per_case = {}
    for d in expanded_report["domains"]:
        for c in d["cases"]:
            per_case[(d["domain"], c["case_id"])] = c
    ordered = {}
    for d in expanded_report["domains"]:
        ordered[d["domain"]] = [c["case_id"] for c in d["cases"]]
    out = []
    for mix, counts in B1_MIXES:
        cells = {}
        for regime, _, _ in REGIMES:
            alloc_total = 0
            reason_pos = 0
            state_pos = 0
            pos_cases = []
            for domain in DOMAIN_ORDER:
                for cid in ordered[domain][:counts[domain]]:
                    cell = per_case[(domain, cid)]["regimes"][regime]
                    r = cell["arms"][ALLOC]["priced_regret"]
                    alloc_total += r
                    if r > 0:
                        pos_cases.append(f"{domain}:{cid}")
                    if cell["arms"]["REASON_ONLY"]["priced_regret"] > 0:
                        reason_pos += 1
                    if cell["arms"]["STATE_ALWAYS"]["priced_regret"] > 0:
                        state_pos += 1
            cells[regime] = {
                "allocator_total_priced_regret": alloc_total,
                "positive_regret_cases": pos_cases,
                "reason_only_positive_cells": reason_pos,
                "state_always_positive_cells": state_pos,
            }
        out.append({"mix": mix, "composition": counts, "regimes": cells})
    return out


def joint_mix_evaluation(expanded_cases):
    """B2: one shared nominal budget across domains; unchanged rule on the
    union structure list (frozen case-file order: SAT, PATH, KNAP)."""
    reports = []
    for mix, counts in B2_MIXES:
        union = []       # (domain, structure) in frozen order
        for domain in DOMAIN_ORDER:
            dom = next(d for d in expanded_cases["domains"]
                       if d["domain"] == domain)
            for case in dom["cases"][:counts[domain]]:
                for st in case["structures"]:
                    union.append((domain, st))
        sids = [st["sid"] for _, st in union]
        assert len(set(sids)) == len(sids), "sid collision in union"

        by_domain = {}
        truth = {}
        for domain in DOMAIN_ORDER:
            structs = [st for d, st in union if d == domain]
            by_domain[domain] = structs
            t, vops = frozen.ground_truth(domain, structs)
            truth[domain] = t

        charges = {}   # sid -> (reason, state, reason_out, state_out)
        for domain in DOMAIN_ORDER:
            structs = by_domain[domain]
            reason, state, r_out, s_out = per_structure_charges(
                domain, structs)
            for st in structs:
                charges[st["sid"]] = (reason[st["sid"]], state[st["sid"]],
                                      r_out[st["sid"]], s_out[st["sid"]])

        def dom_truth_map(domain, structs):
            return {st["sid"]: truth[domain][i]
                    for i, st in enumerate(structs)}

        union_structs = [st for _, st in union]
        selections = {
            "REASON_ONLY": [],
            "STATE_ALWAYS": frozen.state_always_selection(union_structs),
            ALLOC: frozen.allocator_selection(union_structs),
        }

        n = len(union_structs)
        declared = {st["sid"]: st["declared_cost"] for st in union_structs}
        subsets = []
        for mask in range(1 << n):
            sset = frozenset(sids[i] for i in range(n) if mask & (1 << i))
            if sum(declared[s] for s in sset) > frozen.BUDGET:
                continue
            subsets.append(sset)

        def serve_of(sel):
            build = sum(declared[s] for s in sel)
            serve = sum(charges[s][1] if s in sel else charges[s][0]
                        for s in sids)
            return build, serve

        def exact_of(sel):
            for domain in DOMAIN_ORDER:
                tmap = dom_truth_map(domain, by_domain[domain])
                for st in by_domain[domain]:
                    got = charges[st["sid"]][3] if st["sid"] in sel \
                        else charges[st["sid"]][2]
                    if got != tmap[st["sid"]]:
                        return False
            return True

        truth_union = [dom_truth_map(domain, by_domain[domain])[st["sid"]]
                       for domain, st in union]
        arm_outputs = {}
        for arm in ARMS:
            sel = set(selections[arm])
            arm_outputs[arm] = [charges[st["sid"]][3] if st["sid"] in sel
                                else charges[st["sid"]][2]
                                for _, st in union]

        cells = {}
        exact_all = True
        for regime, p_b, p_s in REGIMES:
            oracle_best, oracle_set = None, None
            for sset in subsets:
                build, serve = serve_of(sset)
                val = priced(p_b, p_s, build, serve)
                if oracle_best is None or val < oracle_best:
                    oracle_best, oracle_set = val, sset
            arm_cells = {}
            for arm in ARMS:
                sel = set(selections[arm])
                build, serve = serve_of(sel)
                ex = exact_of(sel)
                exact_all = exact_all and ex
                val = priced(p_b, p_s, build, serve)
                arm_cells[arm] = {
                    "materialized": sorted(sel),
                    "build_charge": build,
                    "serve_charge": serve,
                    "priced_realized": val,
                    "priced_regret": val - oracle_best,
                    "outputs_exact": ex,
                }
            alloc_build = sum(declared[s] for s in set(selections[ALLOC]))
            cells[regime] = {
                "p_build": p_b, "p_serve": p_s,
                "priced_oracle": {"materialized": sorted(oracle_set),
                                  "priced_realized": oracle_best},
                "arms": arm_cells,
                "s2_priced_budget_violation_allocator":
                    p_b * alloc_build > frozen.BUDGET,
            }
        reports.append({
            "mix": mix,
            "composition": counts,
            "structure_count": n,
            "selections": {arm: sorted(v) for arm, v in selections.items()},
            "ground_truth": truth_union,
            "arm_outputs": arm_outputs,
            "regimes": cells,
            "outputs_exact_all_arms_all_regimes": exact_all,
        })
    return reports


def regime_zero_regret_cells(reports_list):
    """ regimes where the allocator has zero priced regret in every cell """
    green = []
    for regime, _, _ in REGIMES:
        ok = True
        for rep in reports_list:
            for d in rep["domains"]:
                for c in d["cases"]:
                    if c["regimes"][regime]["arms"][ALLOC][
                            "priced_regret"] != 0:
                        ok = False
        if ok:
            green.append(regime)
    return green


def main():
    v1_cases = load_cases("p12_transfer_cases_v1.json")
    expanded_cases = load_cases("p12_transfer_cases_expanded_v1.json")
    assert expanded_cases["schema"] == \
        "p12-transfer-allocation-cases-expanded-v1"
    assert sum(len(d["cases"]) for d in expanded_cases["domains"]) == 27

    v1_report = evaluate_set(v1_cases, "V1_9")
    exp_report = evaluate_set(expanded_cases, "EXPANDED_27")
    b1 = b1_mix_aggregates(exp_report)
    b2 = joint_mix_evaluation(expanded_cases)

    # ---------------- coverage (RG3)
    coverage = {
        "regimes": [r for r, _, _ in REGIMES],
        "v1_case_regime_cells": v1_report["case_count"] * len(REGIMES),
        "expanded_case_regime_cells": exp_report["case_count"] * len(REGIMES),
        "b1_mixes": len(b1),
        "b2_joint_mixes": len(b2),
    }
    rg3_ok = (coverage["v1_case_regime_cells"] == 45
              and coverage["expanded_case_regime_cells"] == 135
              and coverage["b1_mixes"] == 4
              and coverage["b2_joint_mixes"] == 3)

    rg1_ok = (all(c["outputs_exact_all_arms_all_regimes"]
                  for d in v1_report["domains"] for c in d["cases"])
              and all(c["outputs_exact_all_arms_all_regimes"]
                      for d in exp_report["domains"] for c in d["cases"])
              and all(m["outputs_exact_all_arms_all_regimes"] for m in b2)
              and all(d["flat_direct_accounting_consistent"]
                      for rep in (v1_report, exp_report)
                      for d in rep["domains"]))

    # ---------------- verdicts (data-bound, never forced)
    green_regimes = regime_zero_regret_cells([v1_report, exp_report])
    joint_green = [r for r, _, _ in REGIMES
                   if all(m["regimes"][r]["arms"][ALLOC]["priced_regret"] == 0
                          for m in b2)]
    price_green = [r for r in green_regimes if r in joint_green]
    if len(price_green) == len(REGIMES):
        price_verdict = "ROBUST"
    elif price_green:
        price_verdict = "REGIME_CONDITIONAL"
    else:
        price_verdict = "BROKEN"

    shift_cells_ok = all(
        m["regimes"][r]["allocator_total_priced_regret"] == 0
        for m in b1 for r, _, _ in REGIMES)
    shift_joint_ok = len(joint_green) == len(REGIMES)
    if shift_cells_ok and shift_joint_ok:
        shift_verdict = "ROBUST"
    elif shift_cells_ok or shift_joint_ok:
        shift_verdict = "REGIME_CONDITIONAL"
    else:
        shift_verdict = "BROKEN"

    gates = {
        "RG1_exact_outputs_all_arms_all_regimes": rg1_ok,
        "RG2_byte_replay": "asserted_by_ci_rerun_cmp",
        "RG3_coverage_complete": rg3_ok,
        "RG4_two_implementations": "asserted_by_independent_checker_step",
        "RG5_hidden_parameterization_audit":
            "asserted_by_separate_audit_step",
    }

    report = {
        "schema": "p12-robustness-stress-result-v1",
        "study": "P12_ROBUSTNESS_STRESS_V1",
        "protocol": "P12_ROBUSTNESS_PROTOCOL_V2",
        "allocator": {
            "name": ALLOC,
            "rule": "materialize-if-q>=tau;greedy-by-desc-q;"
                    "cumulative<=B;ties-by-case-order",
            "tau": frozen.TAU,
            "budget_B": frozen.BUDGET,
            "signals": ["q_pending_multiplicity", "c_declared_cost",
                        "B_budget"],
            "price_oblivious": True,
            "domain_oblivious": True,
        },
        "regimes": [{"regime": r, "p_build": pb, "p_serve": ps}
                    for r, pb, ps in REGIMES],
        "v1_set": v1_report,
        "expanded_set": exp_report,
        "b1_case_mixes": b1,
        "b2_joint_mixes": b2,
        "coverage": coverage,
        "verdicts": {
            "price_axis": price_verdict,
            "price_axis_zero_regret_regimes": price_green,
            "distribution_shift_axis": shift_verdict,
            "shift_case_mixes_zero_regret": shift_cells_ok,
            "shift_joint_mixes_zero_regret_regimes": joint_green,
            "hidden_parameterization_axis":
                "bound_by_separate_audit_artifact",
        },
        "gates": gates,
        "terminal": "P12_ROBUSTNESS_STRESS_V1_EXECUTED",
    }
    sys.stdout.write(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
