#!/usr/bin/env python3
"""P12 price-aware successor runner V1 (NR-13 revival, implementation A).

Executes the pre-registered P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1
battery over the SAME frozen pools, regimes, budget semantics and mixes as
the original P12_ROBUSTNESS_STRESS_V1 run, adding the successor arm
P12_PRICE_AWARE_ALLOCATOR_V1 (exact budgeted argmin of the charged
objective on the published charge-ledger certificates + price vector).

Everything frozen is imported UNMODIFIED:
  run_transfer_allocation_v1 (frozen V1 engines + original allocator)
  run_p12_robustness_v1      (charging path: per_structure_charges/priced,
                              regimes, mixes, verdict logic shape)
  p12_price_aware_allocator_v1 (the successor selector; its own module so
                              the surface audit can analyze it in isolation)

New in this runner only: the successor arm, the ORACLE_LOCATION diagnostic
arm, the BEFORE column (frozen allocator evaluated side-by-side), the tie
census, and the SC1-SC6 success-criteria evaluation. Stdlib only.

Budget semantics (unchanged, pre-registered):
  S1 (gates):  nominal budget on unpriced declared construction cost (<=500)
  S2 (report): priced-budget violation flags, characterization only
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_transfer_allocation_v1 as frozen  # noqa: E402
import run_p12_robustness_v1 as stress  # noqa: E402
from p12_price_aware_allocator_v1 import price_aware_selection  # noqa: E402

ORIG = frozen.ALLOCATOR_NAME
SUCCESSOR = "P12_PRICE_AWARE_ALLOCATOR_V1"
ARMS = ["REASON_ONLY", "STATE_ALWAYS", ORIG, SUCCESSOR,
        "ORACLE_LOCATION"]

REGIMES = stress.REGIMES
B1_MIXES = stress.B1_MIXES
B2_MIXES = stress.B2_MIXES
DOMAIN_ORDER = stress.DOMAIN_ORDER

BUDGET = frozen.BUDGET


def sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ledger_of(structures, reason, state):
    """The charging environment publishes the per-structure ledger the
    selector may read (prereg readable surface, nothing else)."""
    return [{"sid": st["sid"],
             "declared_cost": st["declared_cost"],
             "reason_serve_certificate": reason[st["sid"]],
             "state_serve_certificate": state[st["sid"]]}
            for st in structures]


def successor_selection(ledger, p_b, p_s):
    return price_aware_selection(ledger, (p_b, p_s), BUDGET)


def oracle_and_ties(sids, declared, reason, state, p_b, p_s):
    """Exhaustive priced optimum + tie census (count of budget-feasible
    subsets attaining the optimum), first-mask selection (matches the
    original runner's enumeration order)."""
    n = len(sids)
    best, best_set, ties = None, None, 0
    for mask in range(1 << n):
        sset = frozenset(sids[i] for i in range(n) if mask & (1 << i))
        if sum(declared[s] for s in sset) > BUDGET:
            continue
        build = sum(declared[s] for s in sset)
        serve = sum(state[s] if s in sset else reason[s] for s in sids)
        val = stress.priced(p_b, p_s, build, serve)
        if best is None or val < best:
            best, best_set = val, sset
    for mask in range(1 << n):
        sset = frozenset(sids[i] for i in range(n) if mask & (1 << i))
        if sum(declared[s] for s in sset) > BUDGET:
            continue
        build = sum(declared[s] for s in sset)
        serve = sum(state[s] if s in sset else reason[s] for s in sids)
        if stress.priced(p_b, p_s, build, serve) == best:
            ties += 1
    return best_set, best, ties


def evaluate_case(domain, case):
    """All arms (incl. successor and oracle-location) + priced oracle for
    one case, all regimes. Successor selection is regime-dependent."""
    structures = case["structures"]
    sids = [st["sid"] for st in structures]
    declared = {st["sid"]: st["declared_cost"] for st in structures}
    frozen.prime_caches(domain, structures)
    truth, verify_ops = frozen.ground_truth(domain, structures)
    reason, state, reason_out, state_out = stress.per_structure_charges(
        domain, structures)

    certificates = {st["sid"]: {
        "declared_cost": declared[st["sid"]],
        "reason_serve_certificate": reason[st["sid"]],
        "state_serve_certificate": state[st["sid"]],
    } for st in structures}
    ledger = ledger_of(structures, reason, state)

    static_selections = {
        "REASON_ONLY": [],
        "STATE_ALWAYS": frozen.state_always_selection(structures),
        ORIG: frozen.allocator_selection(structures),
    }

    cells = {}
    successor_selections = {}
    exact_all = True
    for regime, p_b, p_s in REGIMES:
        succ_sel = successor_selection(ledger, p_b, p_s)
        successor_selections[regime] = succ_sel
        oracle_set, oracle_best, ties = oracle_and_ties(
            sids, declared, reason, state, p_b, p_s)
        regime_selections = dict(static_selections)
        regime_selections[SUCCESSOR] = succ_sel
        regime_selections["ORACLE_LOCATION"] = sorted(oracle_set)
        arm_cells = {}
        for arm in ARMS:
            sel = set(regime_selections[arm])
            build = sum(declared[s] for s in sel)
            serve = sum(state[s] if s in sel else reason[s] for s in sids)
            outputs = [state_out[s] if s in sel else reason_out[s]
                       for s in sids]
            exact = outputs == truth
            exact_all = exact_all and exact
            val = stress.priced(p_b, p_s, build, serve)
            arm_cells[arm] = {
                "materialized": sorted(sel),
                "build_charge": build,
                "serve_charge": serve,
                "priced_realized": val,
                "priced_regret": val - oracle_best,
                "outputs_exact": exact,
                "outputs": outputs,
            }
        succ_build = sum(declared[s] for s in set(succ_sel))
        cells[regime] = {
            "p_build": p_b,
            "p_serve": p_s,
            "priced_oracle": {
                "materialized": sorted(oracle_set),
                "priced_realized": oracle_best,
                "optimal_subset_count": ties,
            },
            "arms": arm_cells,
            "s2_priced_budget_violation_successor":
                p_b * succ_build > BUDGET,
        }
    return {
        "case_id": case["case_id"],
        "structure_q": {st["sid"]: len(st["queries"])
                        for st in structures},
        "declared_costs": declared,
        "certificates": certificates,
        "selections": {arm: sorted(v) for arm, v in
                       static_selections.items()},
        "successor_selections": successor_selections,
        "verify_ops": verify_ops,
        "ground_truth": truth,
        "regimes": cells,
        "outputs_exact_all_arms_all_regimes": exact_all,
    }


def flat_direct_accounting_check(domain, case_reports, cases):
    """Decomposed FLAT accounting equals the frozen V1 direct
    build_cost + serve_case path for every non-oracle arm."""
    for rep, case in zip(case_reports, cases):
        cid = case["case_id"]
        structures = case["structures"]
        frozen.prime_caches(domain, structures)
        for arm in ("STATE_ALWAYS", ORIG, SUCCESSOR):
            if arm == SUCCESSOR:
                sel = set(rep["successor_selections"]["FLAT"])
            else:
                sel = set(rep["selections"][arm])
            direct = (frozen.build_cost(structures, sel)
                      + frozen.serve_case(structures, sel, domain)[0])
            decomposed = (rep["regimes"]["FLAT"]["arms"][arm][
                "build_charge"]
                + rep["regimes"]["FLAT"]["arms"][arm]["serve_charge"])
            if direct != decomposed:
                return False, f"{domain}:{cid}:{arm} direct={direct} " \
                              f"decomposed={decomposed}"
    return True, ""


def evaluate_set(cases, tag):
    domains = []
    for dom in cases["domains"]:
        domain = dom["domain"]
        case_reports = [evaluate_case(domain, case)
                        for case in dom["cases"]]
        ok, msg = flat_direct_accounting_check(
            domain, case_reports, dom["cases"])
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
        "domains": domains,
    }


def b1_mix_aggregates(expanded_report):
    """Case-level mixes on the successor (AFTER) and the frozen allocator
    (BEFORE), from the same expanded-set report."""
    per_case = {}
    for d in expanded_report["domains"]:
        for c in d["cases"]:
            per_case[(d["domain"], c["case_id"])] = c
    ordered = {d["domain"]: [c["case_id"] for c in d["cases"]]
               for d in expanded_report["domains"]}
    out = []
    for mix, counts in B1_MIXES:
        cells = {}
        for regime, _, _ in REGIMES:
            succ_total = 0
            orig_total = 0
            pos_cases = []
            for domain in DOMAIN_ORDER:
                for cid in ordered[domain][:counts[domain]]:
                    cell = per_case[(domain, cid)]["regimes"][regime]
                    s = cell["arms"][SUCCESSOR]["priced_regret"]
                    o = cell["arms"][ORIG]["priced_regret"]
                    succ_total += s
                    orig_total += o
                    if s > 0:
                        pos_cases.append(f"{domain}:{cid}")
            cells[regime] = {
                "successor_total_priced_regret": succ_total,
                "original_allocator_total_priced_regret": orig_total,
                "successor_positive_regret_cases": pos_cases,
            }
        out.append({"mix": mix, "composition": counts, "regimes": cells})
    return out


def joint_mix_evaluation(expanded_cases):
    """B2: one shared nominal budget across domains; the SAME successor
    rule on the union ledger (frozen order SAT, PATH, KNAP)."""
    reports = []
    for mix, counts in B2_MIXES:
        union = []
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
            frozen.prime_caches(domain, structs)
            t, _ = frozen.ground_truth(domain, structs)
            truth[domain] = t

        charges = {}
        for domain in DOMAIN_ORDER:
            structs = by_domain[domain]
            reason, state, r_out, s_out = stress.per_structure_charges(
                domain, structs)
            for st in structs:
                charges[st["sid"]] = (reason[st["sid"]], state[st["sid"]],
                                      r_out[st["sid"]], s_out[st["sid"]])

        def dom_truth_map(domain, structs):
            return {st["sid"]: truth[domain][i]
                    for i, st in enumerate(structs)}

        union_structs = [st for _, st in union]
        declared = {st["sid"]: st["declared_cost"] for st in union_structs}
        reason = {s: charges[s][0] for s in sids}
        state = {s: charges[s][1] for s in sids}
        ledger = [{"sid": st["sid"],
                   "declared_cost": st["declared_cost"],
                   "reason_serve_certificate": charges[st["sid"]][0],
                   "state_serve_certificate": charges[st["sid"]][1]}
                  for _, st in union]

        static_selections = {
            "REASON_ONLY": [],
            "STATE_ALWAYS": frozen.state_always_selection(union_structs),
            ORIG: frozen.allocator_selection(union_structs),
        }

        def outputs_of(sel):
            return [charges[st["sid"]][3] if st["sid"] in sel
                    else charges[st["sid"]][2] for _, st in union]

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

        cells = {}
        successor_selections = {}
        exact_all = True
        for regime, p_b, p_s in REGIMES:
            succ_sel = successor_selection(ledger, p_b, p_s)
            successor_selections[regime] = succ_sel
            oracle_set, oracle_best, ties = oracle_and_ties(
                sids, declared, reason, state, p_b, p_s)
            regime_selections = dict(static_selections)
            regime_selections[SUCCESSOR] = succ_sel
            regime_selections["ORACLE_LOCATION"] = sorted(oracle_set)
            arm_cells = {}
            for arm in ARMS:
                sel = set(regime_selections[arm])
                build = sum(declared[s] for s in sel)
                serve = sum(state[s] if s in sel else reason[s]
                            for s in sids)
                ex = exact_of(sel)
                exact_all = exact_all and ex
                val = stress.priced(p_b, p_s, build, serve)
                arm_cells[arm] = {
                    "materialized": sorted(sel),
                    "build_charge": build,
                    "serve_charge": serve,
                    "priced_realized": val,
                    "priced_regret": val - oracle_best,
                    "outputs_exact": ex,
                    "outputs": outputs_of(sel),
                }
            succ_build = sum(declared[s] for s in set(succ_sel))
            cells[regime] = {
                "p_build": p_b, "p_serve": p_s,
                "priced_oracle": {"materialized": sorted(oracle_set),
                                  "priced_realized": oracle_best,
                                  "optimal_subset_count": ties},
                "arms": arm_cells,
                "s2_priced_budget_violation_successor":
                    p_b * succ_build > BUDGET,
            }
        reports.append({
            "mix": mix,
            "composition": counts,
            "structure_count": len(union_structs),
            "certificates": {st["sid"]: {
                "declared_cost": st["declared_cost"],
                "reason_serve_certificate": charges[st["sid"]][0],
                "state_serve_certificate": charges[st["sid"]][1],
            } for _, st in union},
            "selections": {arm: sorted(v) for arm, v in
                           static_selections.items()},
            "successor_selections": successor_selections,
            "ground_truth": truth_union,
            "regimes": cells,
            "outputs_exact_all_arms_all_regimes": exact_all,
        })
    return reports


def collect_sc(v1_report, exp_report, b1, b2):
    """SC1-SC6 from this run's own numbers (never forced)."""
    # SC1: FLAT replication constraint on the V1 9-case set
    sc1_regrets = []
    sc1_costs = []
    for d in v1_report["domains"]:
        for c in d["cases"]:
            cell = c["regimes"]["FLAT"]
            sc1_regrets.append(cell["arms"][SUCCESSOR]["priced_regret"])
            sc1_costs.append(
                cell["arms"][SUCCESSOR]["priced_realized"]
                - cell["arms"][ORIG]["priced_realized"])
    sc1 = all(r == 0 for r in sc1_regrets) and all(
        d == 0 for d in sc1_costs)

    # SC2: zero successor regret in every case cell of both sets + joints
    sc2 = all(
        c["regimes"][r]["arms"][SUCCESSOR]["priced_regret"] == 0
        for rep in (v1_report, exp_report)
        for d in rep["domains"] for c in d["cases"]
        for r, _, _ in REGIMES) and all(
        m["regimes"][r]["arms"][SUCCESSOR]["priced_regret"] == 0
        for m in b2 for r, _, _ in REGIMES)

    # SC3: shift axis (B1 aggregates + joints) on successor numbers
    sc3 = all(
        m["regimes"][r]["successor_total_priced_regret"] == 0
        for m in b1 for r, _, _ in REGIMES) and all(
        m["regimes"][r]["arms"][SUCCESSOR]["priced_regret"] == 0
        for m in b2 for r, _, _ in REGIMES)

    # SC6: successor selections respond to the price vector somewhere
    sc6_evidence = []
    for rep, tag in ((v1_report, "V1_9"), (exp_report, "EXPANDED_27")):
        for d in rep["domains"]:
            for c in d["cases"]:
                variants = {tuple(v) for v in
                            c["successor_selections"].values()}
                if len(variants) > 1:
                    sc6_evidence.append(
                        f"{tag}:{d['domain']}:{c['case_id']}")
    for m in b2:
        variants = {tuple(v) for v in m["successor_selections"].values()}
        if len(variants) > 1:
            sc6_evidence.append(f"B2:{m['mix']}")
    sc6 = bool(sc6_evidence)

    # tie census: cells whose budgeted optimum is not unique
    tie_cells = []
    for rep, tag in ((v1_report, "V1_9"), (exp_report, "EXPANDED_27")):
        for d in rep["domains"]:
            for c in d["cases"]:
                for r, _, _ in REGIMES:
                    n = c["regimes"][r]["priced_oracle"][
                        "optimal_subset_count"]
                    if n > 1:
                        tie_cells.append(f"{tag}:{d['domain']}:"
                                         f"{c['case_id']}:{r}(n={n})")
    for m in b2:
        for r, _, _ in REGIMES:
            n = m["regimes"][r]["priced_oracle"]["optimal_subset_count"]
            if n > 1:
                tie_cells.append(f"B2:{m['mix']}:{r}(n={n})")

    return {
        "SC1_FLAT_replication_constraint": {
            "ok": sc1,
            "successor_flat_regrets_v1_9": sc1_regrets,
            "successor_minus_original_flat_realized_v1_9": sc1_costs,
        },
        "SC2_price_axis": {"ok": sc2},
        "SC3_shift_axis": {"ok": sc3},
        "SC6_price_responsiveness_liveness": {
            "ok": sc6,
            "variant_cells": sc6_evidence,
        },
        "tie_census": {"tie_cell_count": len(tie_cells),
                       "tie_cells": tie_cells},
    }


def verdicts_for(arm, v1_report, exp_report, b2, shift_cells_ok):
    """The original battery's verdict logic, recomputed on the given
    arm's numbers (successor) or the BEFORE column (frozen allocator).
    shift_cells_ok is the B1 case-mix flag, computed by the caller (the
    two arms live under different B1 aggregate keys)."""
    green_regimes = []
    for regime, _, _ in REGIMES:
        ok = all(
            c["regimes"][regime]["arms"][arm]["priced_regret"] == 0
            for rep in (v1_report, exp_report)
            for d in rep["domains"] for c in d["cases"])
        if ok:
            green_regimes.append(regime)
    joint_green = [r for r, _, _ in REGIMES
                   if all(m["regimes"][r]["arms"][arm][
                       "priced_regret"] == 0 for m in b2)]
    price_green = [r for r in green_regimes if r in joint_green]
    if len(price_green) == len(REGIMES):
        price_verdict = "ROBUST"
    elif price_green:
        price_verdict = "REGIME_CONDITIONAL"
    else:
        price_verdict = "BROKEN"
    shift_joint_ok = len(joint_green) == len(REGIMES)
    if shift_cells_ok and shift_joint_ok:
        shift_verdict = "ROBUST"
    elif shift_cells_ok or shift_joint_ok:
        shift_verdict = "REGIME_CONDITIONAL"
    else:
        shift_verdict = "BROKEN"
    return {
        "price_axis": price_verdict,
        "price_axis_zero_regret_regimes": price_green,
        "distribution_shift_axis": shift_verdict,
        "shift_case_mixes_zero_regret": shift_cells_ok,
        "shift_joint_mixes_zero_regret_regimes": joint_green,
    }


def main():
    v1_cases = stress.load_cases("p12_transfer_cases_v1.json")
    expanded_cases = stress.load_cases("p12_transfer_cases_expanded_v1.json")
    assert expanded_cases["schema"] == \
        "p12-transfer-allocation-cases-expanded-v1"
    assert sum(len(d["cases"]) for d in expanded_cases["domains"]) == 27

    v1_report = evaluate_set(v1_cases, "V1_9")
    exp_report = evaluate_set(expanded_cases, "EXPANDED_27")
    b1 = b1_mix_aggregates(exp_report)
    b2 = joint_mix_evaluation(expanded_cases)

    coverage = {
        "regimes": [r for r, _, _ in REGIMES],
        "v1_case_regime_cells": v1_report["case_count"] * len(REGIMES),
        "expanded_case_regime_cells": exp_report["case_count"]
        * len(REGIMES),
        "b1_mixes": len(b1),
        "b2_joint_mixes": len(b2),
    }

    sc = collect_sc(v1_report, exp_report, b1, b2)

    succ_b1_ok = all(
        m["regimes"][r]["successor_total_priced_regret"] == 0
        for m in b1 for r, _, _ in REGIMES)
    succ_verdicts = verdicts_for(SUCCESSOR, v1_report, exp_report,
                                 b2, succ_b1_ok)
    orig_b1_ok = all(
        m["regimes"][r]["original_allocator_total_priced_regret"] == 0
        for m in b1 for r, _, _ in REGIMES)
    orig_verdicts = verdicts_for(ORIG, v1_report, exp_report,
                                 b2, orig_b1_ok)

    rg1_ok = (all(c["outputs_exact_all_arms_all_regimes"]
                  for d in v1_report["domains"] for c in d["cases"])
              and all(c["outputs_exact_all_arms_all_regimes"]
                      for d in exp_report["domains"] for c in d["cases"])
              and all(m["outputs_exact_all_arms_all_regimes"] for m in b2)
              and all(d["flat_direct_accounting_consistent"]
                      for rep in (v1_report, exp_report)
                      for d in rep["domains"]))
    rg3_ok = (coverage["v1_case_regime_cells"] == 45
              and coverage["expanded_case_regime_cells"] == 135
              and coverage["b1_mixes"] == 4
              and coverage["b2_joint_mixes"] == 3)

    regret_mass = {"before": {}, "after": {}}
    for regime, _, _ in REGIMES:
        regret_mass["before"][regime] = sum(
            c["regimes"][regime]["arms"][ORIG]["priced_regret"]
            for rep in (v1_report, exp_report)
            for d in rep["domains"] for c in d["cases"])
        regret_mass["after"][regime] = sum(
            c["regimes"][regime]["arms"][SUCCESSOR]["priced_regret"]
            for rep in (v1_report, exp_report)
            for d in rep["domains"] for c in d["cases"])

    report = {
        "schema": "p12-price-aware-successor-result-v1",
        "study": "P12_PRICE_AWARE_SUCCESSOR_V1",
        "protocol": "P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1",
        "prereg_sha256": sha256_of(os.path.join(
            HERE, "P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1.json")),
        "allocator_before": {
            "name": ORIG,
            "rule": "materialize-if-q>=tau;greedy-by-desc-q;"
                    "cumulative<=B;ties-by-case-order",
            "tau": frozen.TAU,
            "budget_B": frozen.BUDGET,
            "price_oblivious": True,
        },
        "allocator_successor": {
            "name": SUCCESSOR,
            "rule": "exact 0/1-knapsack argmin of the charged objective on "
                    "the published charge-ledger certificates and price "
                    "vector; DP over integer declared weights; ties prefer "
                    "not-taking; eligibility = sign of priced marginal "
                    "delta (no multiplicity threshold)",
            "new_free_parameters": 0,
            "readable_surface": ["sid", "declared_cost",
                                 "reason_serve_certificate",
                                 "state_serve_certificate",
                                 "B_budget", "p_build", "p_serve"],
        },
        "regimes": [{"regime": r, "p_build": pb, "p_serve": ps}
                    for r, pb, ps in REGIMES],
        "v1_set": v1_report,
        "expanded_set": exp_report,
        "b1_case_mixes": b1,
        "b2_joint_mixes": b2,
        "coverage": coverage,
        "success_criteria": sc,
        "total_priced_regret_mass": regret_mass,
        "verdicts": {
            "successor_price_axis": succ_verdicts["price_axis"],
            "successor_price_axis_zero_regret_regimes":
                succ_verdicts["price_axis_zero_regret_regimes"],
            "successor_distribution_shift_axis":
                succ_verdicts["distribution_shift_axis"],
            "successor_shift_case_mixes_zero_regret":
                succ_verdicts["shift_case_mixes_zero_regret"],
            "successor_shift_joint_mixes_zero_regret_regimes":
                succ_verdicts["shift_joint_mixes_zero_regret_regimes"],
            "original_allocator_price_axis": orig_verdicts["price_axis"],
            "original_allocator_price_axis_zero_regret_regimes":
                orig_verdicts["price_axis_zero_regret_regimes"],
            "original_allocator_distribution_shift_axis":
                orig_verdicts["distribution_shift_axis"],
            "original_allocator_shift_case_mixes_zero_regret":
                orig_verdicts["shift_case_mixes_zero_regret"],
            "original_allocator_shift_joint_mixes_zero_regret_regimes":
                orig_verdicts["shift_joint_mixes_zero_regret_regimes"],
        },
        "gates": {
            "RG1_exact_outputs_all_arms_all_regimes": rg1_ok,
            "RG3_coverage_complete": rg3_ok,
            "RG4_two_implementations":
                "asserted_by_independent_checker_step",
            "SC5_successor_surface_audit":
                "asserted_by_separate_audit_step",
        },
        "terminal": "P12_PRICE_AWARE_SUCCESSOR_RUN_EXECUTED",
    }
    sys.stdout.write(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
