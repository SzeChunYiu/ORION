#!/usr/bin/env python3
"""P12 price-aware successor — independent second checker V1 (impl B).

Different algorithm classes from the successor runner (impl A) at every
stage where independence is claimed:
  charging : the INDEPENDENT checker engines of
             check_p12_robustness_independent_v1 (full-rescan fixpoint UP
             + occurrence-cost model; bidirectional-BFS completion
             distances + forward-BFS expansion counting; exhaustive 2^n
             knapsack truth + closed-form charges), imported unmodified;
  argmin   : exhaustive budget-feasible subset enumeration with first-mask
             tie-break (the runner uses 0/1-knapsack DP with
             prefer-not-take ties) — a different exact algorithm class.

Independently re-derives from the case files alone:
  - every per-structure charge certificate (declared, reason, state);
  - the priced oracle (value + first-mask location) for every case-regime
    cell and every B2 joint mix;
  - the successor selection under exhaustive enumeration and its priced
    realized value / regret in all 180 case-regime + 15 joint cells;
  - both restrictions and the frozen allocator (own implementations);
  - output exactness vs own truth for every arm in every regime;
  - the B1 aggregates, the verdicts, and SC1/SC2/SC3/SC6;
then cross-checks all of it against the runner's emitted JSON (default
./p12_price_aware_successor_v1.json, falling back to this directory).

Selection comparison rule (pre-registered): selections must be identical
whenever the budgeted optimum is unique; when optima tie, the two sets may
differ only with identical priced value (each such divergence is listed,
not counted as a discrepancy).

Terminal: P12_PRICE_AWARE_SUCCESSOR_SECOND_CHECKER_GREEN (zero
discrepancies).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_p12_robustness_independent_v1 as indep  # noqa: E402

BUDGET = indep.BUDGET
REGIMES = indep.REGIMES
DOMAIN_ORDER = indep.DOMAIN_ORDER
B1_MIXES = indep.B1_MIXES
B2_MIXES = indep.B2_MIXES
SUCCESSOR = "P12_PRICE_AWARE_ALLOCATOR_V1"
ORIG = indep.ALLOC
ARMS = ["REASON_ONLY", "STATE_ALWAYS", ORIG, SUCCESSOR,
        "ORACLE_LOCATION"]
V1_TAG = "V1_9"
EXPANDED_TAG = "EXPANDED_27"

D = []          # discrepancy records
TIE_DIVERGED = []  # allowed: non-unique optimum, equal value


def disc(cat, detail):
    D.append({"category": cat, "detail": detail})


def load_runner_json():
    for cand in ("p12_price_aware_successor_v1.json",
                 os.path.join(HERE,
                              "p12_price_aware_successor_v1.json")):
        if os.path.exists(cand):
            with open(cand) as f:
                return json.load(f), cand
    sys.exit("runner JSON not found (run the runner first)")


def my_successor_pick(sids, declared, reason, state, p_b, p_s):
    """Exhaustive budget-feasible argmin of sum d[s] (d = p_b*decl -
    p_s*(reason-state)); first-mask tie-break. Returns (sorted sids,
    sum d, full priced realized served on the WHOLE sid list)."""
    n = len(sids)
    best, best_set, ties = None, None, 0
    const = p_s * sum(reason[s] for s in sids)
    for mask in range(1 << n):
        sset = frozenset(sids[i] for i in range(n) if mask & (1 << i))
        if sum(declared[s] for s in sset) > BUDGET:
            continue
        val = sum(p_b * declared[s] - p_s * (reason[s] - state[s])
                  for s in sset)
        if best is None or val < best:
            best, best_set = val, sset
    for mask in range(1 << n):
        sset = frozenset(sids[i] for i in range(n) if mask & (1 << i))
        if sum(declared[s] for s in sset) > BUDGET:
            continue
        val = sum(p_b * declared[s] - p_s * (reason[s] - state[s])
                  for s in sset)
        if val == best:
            ties += 1
    realized = const + best
    return sorted(best_set), best, realized, ties


def own_certificate_map(domain, structures):
    declared, reason, state, truth = {}, {}, {}, {}
    for st in structures:
        d_, r_, s_, t_ = indep.charges(domain, st)
        declared[st["sid"]] = d_
        reason[st["sid"]] = r_
        state[st["sid"]] = s_
        truth[st["sid"]] = t_
    return declared, reason, state, truth


def check_cell(regime, p_b, p_s, cell, my_ctx, where, my_regret):
    """Cross-check one (case|joint)-regime cell. my_ctx carries sids,
    declared, reason, state, truth (dict by sid) for the locus."""
    sids, declared, reason, state, truth = my_ctx
    # 1. oracle value + location (first-mask on both sides here)
    o_set, o_val = indep.priced_oracle(sids, declared, reason, state,
                                       p_b, p_s)
    r_oval = cell["priced_oracle"]["priced_realized"]
    if r_oval != o_val:
        disc("oracle_value",
             f"{where}:{regime} runner={r_oval} mine={o_val}")
    r_oloc = cell["priced_oracle"]["materialized"]
    if r_oloc != sorted(o_set):
        disc("oracle_location",
             f"{where}:{regime} runner={r_oloc} mine={sorted(o_set)}")
    # 2. successor: exhaustive argmin vs runner DP
    m_sel, m_sumd, m_realized, m_ties = my_successor_pick(
        sids, declared, reason, state, p_b, p_s)
    r_ties = cell["priced_oracle"]["optimal_subset_count"]
    if m_ties != r_ties:
        disc("tie_count",
             f"{where}:{regime} runner={r_ties} mine={m_ties}")
    r_sel = cell["arms"][SUCCESSOR]["materialized"]
    if r_sel != m_sel:
        if m_ties == 1:
            disc("successor_selection_unique_optimum",
                 f"{where}:{regime} runner={r_sel} mine={m_sel}")
        else:
            r_val = cell["arms"][SUCCESSOR]["priced_realized"]
            if r_val != m_realized:
                disc("successor_tie_value_mismatch",
                     f"{where}:{regime} runner_val={r_val} "
                     f"mine_val={m_realized}")
            else:
                TIE_DIVERGED.append(
                    {"where": f"{where}:{regime}",
                     "runner_selection": r_sel,
                     "checker_selection": m_sel,
                     "optimal_subset_count": m_ties,
                     "priced_value": m_realized})
    r_sval = cell["arms"][SUCCESSOR]["priced_realized"]
    if r_sval != m_realized:
        disc("successor_realized",
             f"{where}:{regime} runner={r_sval} mine={m_realized}")
    r_sreg = cell["arms"][SUCCESSOR]["priced_regret"]
    if r_sreg != m_realized - o_val:
        disc("successor_regret",
             f"{where}:{regime} runner={r_sreg} "
             f"mine={m_realized - o_val}")
    if sum(declared[s] for s in r_sel) > BUDGET:
        disc("successor_budget_violation", f"{where}:{regime}")
    # 3. every arm's realized/regret from runner's materialized set
    for arm in ARMS:
        acell = cell["arms"][arm]
        sel = set(acell["materialized"])
        build = sum(declared[s] for s in sel)
        serve = sum(state[s] if s in sel else reason[s] for s in sids)
        val = p_b * build + p_s * serve
        if acell["build_charge"] != build or acell["serve_charge"] != serve:
            disc("arm_charges",
                 f"{where}:{regime}:{arm} runner=({acell['build_charge']},"
                 f"{acell['serve_charge']}) mine=({build},{serve})")
        if acell["priced_realized"] != val:
            disc("arm_realized",
                 f"{where}:{regime}:{arm} runner={acell['priced_realized']}"
                 f" mine={val}")
        if acell["priced_regret"] != val - o_val:
            disc("arm_regret",
                 f"{where}:{regime}:{arm} runner={acell['priced_regret']}"
                 f" mine={val - o_val}")
        if sum(declared[s] for s in sel) > BUDGET:
            disc("arm_budget_violation", f"{where}:{regime}:{arm}")
        # 4. output exactness vs own truth
        if acell["outputs"] != [truth[s] for s in sids]:
            disc("outputs_inexact", f"{where}:{regime}:{arm}")
        if acell["outputs_exact"] is not True:
            disc("runner_flagged_inexact", f"{where}:{regime}:{arm}")
    return m_realized - o_val


def main():
    rep, path = load_runner_json()
    if rep.get("schema") != "p12-price-aware-successor-result-v1":
        disc("schema", str(rep.get("schema")))
    if rep.get("study") != "P12_PRICE_AWARE_SUCCESSOR_V1":
        disc("study", str(rep.get("study")))

    v1_cases = json.load(open(os.path.join(
        HERE, "p12_transfer_cases_v1.json")))
    exp_cases = json.load(open(os.path.join(
        HERE, "p12_transfer_cases_expanded_v1.json")))

    # ---------------- per-case cross-checks (both sets)
    my_case_regret = {}   # (tag, domain, case_id, regime) -> dict
    my_succ_variant_cells = []
    for cases, rep_key, tag in ((v1_cases, "v1_set", V1_TAG),
                                (exp_cases, "expanded_set", EXPANDED_TAG)):
        rep_set = rep[rep_key]
        doms = {d["domain"]: d["cases"] for d in cases["domains"]}
        rep_doms = {d["domain"]: d["cases"] for d in rep_set["domains"]}
        if set(doms) != set(rep_doms):
            disc("domains", f"{tag} {set(doms)} vs {set(rep_doms)}")
        if rep_set["case_count"] != sum(len(v) for v in doms.values()):
            disc("case_count", f"{tag} {rep_set['case_count']}")
        for domain in DOMAIN_ORDER:
            if len(doms[domain]) != len(rep_doms[domain]):
                disc("domain_case_count",
                     f"{tag}:{domain} {len(doms[domain])} vs "
                     f"{len(rep_doms[domain])}")
                continue
            for case, rc in zip(doms[domain], rep_doms[domain]):
                structures = case["structures"]
                if rc["case_id"] != case["case_id"]:
                    disc("case_id", f"{tag}:{domain}")
                    continue
                where = f"{tag}:{domain}:{case['case_id']}"
                sids = [st["sid"] for st in structures]
                if list(rc["certificates"]) != sids:
                    disc("certificate_order", where)
                declared, reason, state, truth = \
                    own_certificate_map(domain, structures)
                for s in sids:
                    c = rc["certificates"][s]
                    if c["declared_cost"] != declared[s]:
                        disc("cert_declared", f"{where}:{s}")
                    if c["reason_serve_certificate"] != reason[s]:
                        disc("cert_reason", f"{where}:{s}")
                    if c["state_serve_certificate"] != state[s]:
                        disc("cert_state", f"{where}:{s}")
                if rc["ground_truth"] != [truth[s] for s in sids]:
                    disc("ground_truth", where)
                # static selections (own implementations)
                if rc["selections"]["REASON_ONLY"] != []:
                    disc("reason_only_selection", where)
                if set(rc["selections"]["STATE_ALWAYS"]) != \
                        set(indep.own_state_always(structures)):
                    disc("state_always_selection", where)
                if set(rc["selections"][ORIG]) != \
                        set(indep.own_allocator_pick(structures)):
                    disc("original_allocator_selection", where)
                ctx = (sids, declared, reason, state, truth)
                variants = set()
                for regime, p_b, p_s in REGIMES:
                    if regime not in rc["regimes"]:
                        disc("missing_regime", f"{where}:{regime}")
                        continue
                    cr = (p_b, p_s)
                    if (rc["regimes"][regime]["p_build"],
                            rc["regimes"][regime]["p_serve"]) != cr:
                        disc("regime_prices", f"{where}:{regime}")
                    sreg = check_cell(regime, p_b, p_s,
                                      rc["regimes"][regime], ctx,
                                      where, None)
                    o_sel = set(rc["regimes"][regime]["arms"][ORIG][
                        "materialized"])
                    o_build = sum(declared[s] for s in o_sel)
                    o_serve = sum(state[s] if s in o_sel else reason[s]
                                  for s in sids)
                    o_val = p_b * o_build + p_s * o_serve
                    o_set, o_best = indep.priced_oracle(
                        sids, declared, reason, state, p_b, p_s)
                    my_case_regret[(tag, domain, case["case_id"],
                                    regime)] = {
                        "successor": sreg,
                        "orig": o_val - o_best,
                        "successor_realized":
                            rc["regimes"][regime]["arms"][SUCCESSOR][
                                "priced_realized"],
                        "orig_realized": o_val,
                    }
                    variants.add(tuple(rc["regimes"][regime]["arms"][
                        SUCCESSOR]["materialized"]))
                if len(variants) > 1:
                    my_succ_variant_cells.append(where)

    # ---------------- B2 joints (own union charges)
    my_joint = {}
    for mix, counts in B2_MIXES:
        union = []
        for domain in DOMAIN_ORDER:
            dom = next(d for d in exp_cases["domains"]
                       if d["domain"] == domain)
            for case in dom["cases"][:counts[domain]]:
                for st in case["structures"]:
                    union.append((domain, st))
        sids = [st["sid"] for _, st in union]
        declared, reason, state = {}, {}, {}
        truth = {}
        for domain in DOMAIN_ORDER:
            structs = [st for d, st in union if d == domain]
            d_, r_, s_, t_ = own_certificate_map(domain, structs)
            declared.update(d_)
            reason.update(r_)
            state.update(s_)
            truth.update(t_)
        ctx = (sids, declared, reason, state, truth)
        rj = next(m for m in rep["b2_joint_mixes"]
                  if m["mix"] == mix)
        if rj["structure_count"] != len(union):
            disc("joint_structure_count", mix)
        for s in sids:
            c = rj["certificates"][s]
            if (c["declared_cost"] != declared[s]
                    or c["reason_serve_certificate"] != reason[s]
                    or c["state_serve_certificate"] != state[s]):
                disc("joint_cert", f"{mix}:{s}")
        if rj["ground_truth"] != [truth[s] for s in sids]:
            disc("joint_ground_truth", mix)
        if set(rj["selections"][ORIG]) != set(
                indep.own_allocator_pick([st for _, st in union])):
            disc("joint_original_allocator_selection", mix)
        if set(rj["selections"]["STATE_ALWAYS"]) != set(
                indep.own_state_always([st for _, st in union])):
            disc("joint_state_always_selection", mix)
        for regime, p_b, p_s in REGIMES:
            sreg = check_cell(regime, p_b, p_s, rj["regimes"][regime],
                              ctx, f"B2:{mix}", None)
            o_sel = set(rj["regimes"][regime]["arms"][ORIG][
                "materialized"])
            o_build = sum(declared[s] for s in o_sel)
            o_serve = sum(state[s] if s in o_sel else reason[s]
                          for s in sids)
            o_val = p_b * o_build + p_s * o_serve
            o_set, o_best = indep.priced_oracle(
                sids, declared, reason, state, p_b, p_s)
            my_joint[(mix, regime)] = {"successor": sreg,
                                       "orig": o_val - o_best}

    # ---------------- B1 aggregates (own numbers)
    for mix, counts in B1_MIXES:
        rb = next(m for m in rep["b1_case_mixes"] if m["mix"] == mix)
        for regime, _, _ in REGIMES:
            s_tot = sum(
                my_case_regret[(EXPANDED_TAG, domain, cid, regime)][
                    "successor"]
                for domain in DOMAIN_ORDER
                for cid in [c["case_id"] for d in exp_cases["domains"]
                            if d["domain"] == domain
                            for c in d["cases"]][:counts[domain]])
            o_tot = sum(
                my_case_regret[(EXPANDED_TAG, domain, cid, regime)][
                    "orig"]
                for domain in DOMAIN_ORDER
                for cid in [c["case_id"] for d in exp_cases["domains"]
                            if d["domain"] == domain
                            for c in d["cases"]][:counts[domain]])
            cells = rb["regimes"][regime]
            if cells["successor_total_priced_regret"] != s_tot:
                disc("b1_successor_total",
                     f"{mix}:{regime} runner="
                     f"{cells['successor_total_priced_regret']} "
                     f"mine={s_tot}")
            if cells["original_allocator_total_priced_regret"] != o_tot:
                disc("b1_original_total",
                     f"{mix}:{regime} runner="
                     f"{cells['original_allocator_total_priced_regret']}"
                     f" mine={o_tot}")

    # ---------------- SC + verdict recomputation (own numbers)
    sc1_ok = all(
        my_case_regret[(V1_TAG, d, c["case_id"], "FLAT")]["successor"]
        == 0
        for d in DOMAIN_ORDER
        for dom in [next(x for x in v1_cases["domains"]
                         if x["domain"] == d)] for c in dom["cases"])
    sc1_cost = all(
        my_case_regret[(V1_TAG, d, c["case_id"], "FLAT")][
            "successor_realized"]
        == my_case_regret[(V1_TAG, d, c["case_id"], "FLAT")][
            "orig_realized"]
        for d in DOMAIN_ORDER
        for dom in [next(x for x in v1_cases["domains"]
                         if x["domain"] == d)] for c in dom["cases"])
    sc2_ok = (all(v["successor"] == 0
                  for k, v in my_case_regret.items())
              and all(v["successor"] == 0 for v in my_joint.values()))
    sc3_ok = all(v["successor"] == 0 for v in my_joint.values())
    sc6_ok = bool(my_succ_variant_cells)
    sc = rep.get("success_criteria", {})
    for key, mine in (("SC1_FLAT_replication_constraint",
                       sc1_ok and sc1_cost),
                      ("SC2_price_axis", sc2_ok),
                      ("SC3_shift_axis", sc3_ok),
                      ("SC6_price_responsiveness_liveness", sc6_ok)):
        if sc.get(key, {}).get("ok") != mine:
            disc("sc_flag", f"{key} runner={sc.get(key, {}).get('ok')} "
                            f"mine={mine}")
    # B1 zero totals feed SC3 as well
    b1_all_zero = all(
        my_case_regret[(EXPANDED_TAG, domain, cid, regime)][
            "successor"] == 0
        for domain in DOMAIN_ORDER
        for cid in [c["case_id"] for d in exp_cases["domains"]
                    if d["domain"] == domain for c in d["cases"]]
        for regime, _, _ in REGIMES)
    if sc3_ok and not b1_all_zero:
        disc("sc3_internal", "joint green but case cells not")

    def own_verdicts(key):
        green = [r for r, _, _ in REGIMES if all(
            my_case_regret[(t, d, c, r)][key] == 0
            for t in (V1_TAG, EXPANDED_TAG)
            for d in DOMAIN_ORDER
            for c in [cc["case_id"]
                      for dd in (v1_cases["domains"]
                                 if t == V1_TAG
                                 else exp_cases["domains"])
                      if dd["domain"] == d
                      for cc in dd["cases"]])]
        joint_green = [r for r, _, _ in REGIMES if all(
            my_joint[(m, r)][key] == 0 for m, _ in B2_MIXES)]
        price_green = [r for r in green if r in joint_green]
        if len(price_green) == len(REGIMES):
            v = "ROBUST"
        elif price_green:
            v = "REGIME_CONDITIONAL"
        else:
            v = "BROKEN"
        return v, price_green

    s_price, s_green = own_verdicts("successor")
    o_price, o_green = own_verdicts("orig")
    v = rep.get("verdicts", {})
    checks = [("successor_price_axis", s_price),
              ("successor_price_axis_zero_regret_regimes", s_green),
              ("original_allocator_price_axis", o_price),
              ("original_allocator_price_axis_zero_regret_regimes",
               o_green)]
    for key, mine in checks:
        if v.get(key) != mine:
            disc("verdict", f"{key} runner={v.get(key)} mine={mine}")

    coverage = {"case_regime_cells": len(my_case_regret),
                "joint_mix_regime_cells": len(my_joint)}
    if coverage["case_regime_cells"] != 180:
        disc("coverage_cells", str(coverage["case_regime_cells"]))
    if coverage["joint_mix_regime_cells"] != 15:
        disc("coverage_joint", str(coverage["joint_mix_regime_cells"]))

    out = {
        "schema": "p12-price-aware-successor-second-checker-v1",
        "study": "P12_PRICE_AWARE_SUCCESSOR_V1",
        "runner_json": path,
        "implementation": {
            "charging": "independent engines imported from "
                        "check_p12_robustness_independent_v1 "
                        "(full-rescan UP / bidirectional BFS / "
                        "exhaustive knapsack truth)",
            "argmin": "exhaustive budget-feasible subset enumeration, "
                      "first-mask tie-break (vs runner DP "
                      "prefer-not-take)",
        },
        "cells_cross_checked": coverage,
        "own_recomputation": {
            "SC1_FLAT": {"regret_zero": sc1_ok,
                         "realized_equals_original": sc1_cost},
            "SC2_price_axis": sc2_ok,
            "SC3_shift_axis": sc3_ok,
            "SC6_price_responsiveness": sc6_ok,
            "successor_price_axis": s_price,
            "successor_zero_regret_regimes": s_green,
            "original_allocator_price_axis": o_price,
            "original_allocator_zero_regret_regimes": o_green,
        },
        "tie_divergences_allowed": TIE_DIVERGED,
        "discrepancy_count": len(D),
        "discrepancies": D,
        "terminal": ("P12_PRICE_AWARE_SUCCESSOR_SECOND_CHECKER_GREEN"
                     if not D else
                     "P12_PRICE_AWARE_SUCCESSOR_SECOND_CHECKER_FAILED"),
    }
    sys.stdout.write(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
