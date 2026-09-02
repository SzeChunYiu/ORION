#!/usr/bin/env python3
"""Receipt-level checker for the ORION-10 envelope-composition step (v1).

Scope.  The supplement states the all-size envelope
    C_DP = min{C_<=1, f_B', f_B''}
as a twelve-link reduction chain whose last open sector is discharged by a
per-geometry domination lemma (378 geometries x 2^24 states) plus an induction
on the number of commuting-support-two blocks.  This checker re-derives that
statement's committed arithmetic from the pinned receipt artifacts: geometry
completeness and closure, census dispatch, chain shape and terminal flag,
gate truth, downstream-link domains, the two dead alternative routes, and the
QG-5/QG-5b input/event count accounting.  It does NOT re-execute the
6,341,787,648-state enumeration; that enumeration is the scientific run bound
by the QG-7e receipt, and machine-checkability of the composition step is
bounded by what the per-geometry audits record.

Exit codes: 0 = PASS, 1 = FAIL (any check failed), 2 = CANNOT_CHECK
(an artifact is missing or unreadable, so the pinned bindings cannot be
opened at all; this is distinct from FAIL).

Usage: python3 check_envelope_composition_v1.py
Expects a checkout containing research/extensions/orion-qg/ (found by walking
up from this script's directory, or via $ORION10_REPO_ROOT).
Writes CHECK_ENVELOPE_COMPOSITION_RECEIPT_V1.json next to this script.
"""

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone

SCHEMA = "ORION10_CHECK_ENVELOPE_COMPOSITION_V1"
VERSION = "1.0"

ARTIFACT_DIR = os.path.join("research", "extensions", "orion-qg")
PINNED = {
    "QG7E_TWELVE_STATES_RESULTS.json":
        "b452ac0ae11f610099f0a1813786f6a806847c76752dd065edc559707dcb7fd8",
    "QG7E_V2_PP_SINGLE_PINNER_RESULTS.json":
        "c5368796d0ccf6267e252ec06614bfeed73af80815859106b64ab7dbd7ab08d8",
    "QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json":
        "1caf27ed2c5782c3d276cf811bbdf28cf7467c03fcf2f12925829e859ea5fa99",
    "QG5_CERTIFIED_FORECAST_RESULTS.json":
        "f5ef5c7599cb4331d18d4edb95b434961efa55c2f9ac18263bdbfb017df5fc3e",
    "QG5B_EXACT_FORECASTER_RESULTS.json":
        "7701d4fb708a0a235493a0e4da72076d5d8b77a3e19fa9997ab6a5de51997f16",
}

checks = []


def record(cid, ok, detail):
    checks.append({"id": cid, "status": "pass" if ok else "FAIL", "detail": detail})
    return ok


def find_repo_root():
    env = os.environ.get("ORION10_REPO_ROOT")
    if env and os.path.isdir(os.path.join(env, ARTIFACT_DIR)):
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(here, ARTIFACT_DIR)):
            return here
        here = os.path.dirname(here)
    return None


def main():
    root = find_repo_root()
    if root is None:
        print("CANNOT_CHECK: repository root with %s not found" % ARTIFACT_DIR)
        return 2

    docs = {}
    observed = {}
    for name, pin in sorted(PINNED.items()):
        path = os.path.join(root, ARTIFACT_DIR, name)
        if not os.path.isfile(path):
            print("CANNOT_CHECK: missing artifact %s" % path)
            return 2
        raw = open(path, "rb").read()
        digest = hashlib.sha256(raw).hexdigest()
        observed[name] = {"sha256": digest, "bytes": len(raw),
                          "path": os.path.relpath(path, root)}
        docs[name] = json.loads(raw)
        record("digest." + name, digest == pin,
               "pinned %s, observed %s" % (pin, digest))

    q7e = docs["QG7E_TWELVE_STATES_RESULTS.json"]
    v2 = docs["QG7E_V2_PP_SINGLE_PINNER_RESULTS.json"]
    q7f = docs["QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json"]
    q5 = docs["QG5_CERTIFIED_FORECAST_RESULTS.json"]
    q5b = docs["QG5B_EXACT_FORECASTER_RESULTS.json"]

    counts = {}

    # ---- B. per-geometry domination lemma: completeness and closure -------
    p1 = q7e["p1e_domination_lemma"]
    roles = p1["roles"]
    rows = p1["per_geometry"]
    expected_pairs = set()
    for i, a in enumerate(roles):
        for b in roles[i:]:
            expected_pairs.add(tuple(sorted((a, b))))
    seen = set()
    bad_rows = []
    for r in rows:
        geom = tuple(sorted(r["geometry"]))
        if (geom in seen or geom not in expected_pairs
                or r.get("closed") is not True or r.get("residue") != 0
                or r.get("state_domain") != 2 ** 24
                or r.get("permutations_admitted") != 8):
            bad_rows.append(r.get("geometry"))
        seen.add(geom)
    record("p1e.geometry_set",
           len(roles) == p1["role_count"] == 27
           and len(set(roles)) == 27
           and len(expected_pairs) == 27 * 28 // 2 == 378
           and seen == expected_pairs
           and not bad_rows,
           "roles=%d distinct=%d; expected unordered pairs=%d; seen=%d; "
           "bad rows=%d" % (len(roles), len(set(roles)), len(expected_pairs),
                            len(seen), len(bad_rows)))
    record("p1e.closure",
           p1["geometry_count"] == 378 and p1["geometries_closed"] == 378
           and p1["residue_total"] == 0
           and p1["residue_total"] == sum(r["residue"] for r in rows)
           and p1["holds"] is True,
           "geometry_count=%s geometries_closed=%s residue_total=%s holds=%s"
           % (p1["geometry_count"], p1["geometries_closed"],
              p1["residue_total"], p1["holds"]))
    total_states = p1["total_states"]
    record("p1e.state_arithmetic",
           total_states == sum(r["state_domain"] for r in rows)
           == 378 * 2 ** 24 == 6341787648,
           "total_states=%s == 378*2^24=%d" % (total_states, 378 * 2 ** 24))
    counts["p1e_total_states"] = total_states
    counts["p1e_geometries"] = p1["geometry_count"]

    # ---- C. census dispatch ------------------------------------------------
    p2 = q7e["p2_census_dispatch"]
    census_sum = sum(p2["committed_census"].values())
    record("p2.census_dispatch",
           p2["patterns_dispatched_closed"] == 135604
           and p2["patterns_open"] == 0
           and p2["failures_total"] == 135604
           and p2["dispatch_sums_to_census"] is True
           and p2["census_reproduced_verbatim"] is True
           and p2["committed_census"] == p2["observed_census"]
           and census_sum == 135604
           and p2["domain_size"] == 2 ** 29,
           "dispatched_closed=%s open=%s census_sum=%s domain=2^%d"
           % (p2["patterns_dispatched_closed"], p2["patterns_open"],
              census_sum, p2["domain_size"].bit_length() - 1))
    counts["census_patterns"] = p2["patterns_dispatched_closed"]

    # ---- D. twelve-link chain and terminal theorem -------------------------
    pa = q7e["proof_audit"]
    chain = pa["chain"]
    steps = [l["step"] for l in chain]
    expected_steps = [1, 2, 3, 4, 5, 6, "6b", 7, 8, 9, 10, 11]
    record("chain.shape",
           len(chain) == 12 and steps == expected_steps,
           "steps=%s" % steps)
    record("chain.terminal",
           pa["theorem_terminal_reached"] is True
           and pa["statement"]
           == "C_DP == min(C_D+, f_B', f_B'') for all n, unit-cost TARE",
           "terminal=%s statement=%r"
           % (pa["theorem_terminal_reached"], pa["statement"]))
    link7 = chain[7]
    link8 = chain[8]
    record("chain.composition_links",
           "dominated" in link7["claim"] and "strictly fewer comm-s2" in link7["claim"]
           and "removes exactly one comm-s2 block per application and never creates one"
           in link8["carried_by"]
           and "the measure decreases strictly" in link8["carried_by"],
           "step7 claim admits domination with strictly fewer comm-s2 blocks; "
           "step8 measure strictly decreases")
    ao = pa["attack_outcomes"]
    record("chain.attack_outcomes",
           ao.get("E1_composition_fixpoint") == "CANNOT CLOSE (exact, serialized)"
           and ao.get("E2_geometry_class_enlargement") == "CLOSES"
           and ao.get("E3_direct_exhaustive_settlement") == "SETTLES 12/12",
           "E1=%r E2=%r E3=%r" % (ao.get("E1_composition_fixpoint"),
                                  ao.get("E2_geometry_class_enlargement"),
                                  ao.get("E3_direct_exhaustive_settlement")))

    # ---- E. gates -----------------------------------------------------------
    gates = q7e["gates"]
    record("gates.all_true",
           len(gates) == 12 and all(v is True for v in gates.values())
           and gates.get("G8_permutation_binding") is True
           and gates.get("G9_p1e_complete_domains") is True
           and gates.get("G10_census_dispatch") is True,
           "n_gates=%d all_true=%s" % (len(gates),
                                       all(v is True for v in gates.values())))

    # ---- F. downstream-link domains ----------------------------------------
    g2 = q7e["g2_mirror_identity"]
    g3 = q7e["g3_gauge_permutations"]
    gp = q7e["gp_permutation_binding"]
    t4b = q7e["inherited_lemmas"]["t4b_pinned_summary"]
    per_n_rows = sum(v["rows"] for v in gp["per_n"].values())
    per_n_mism = sum(v["mismatches"] for v in gp["per_n"].values())
    record("links.domains",
           g2["domain_size"] == 2 ** 24 and g2["holds"] is True
           and g2.get("f3_exchange_failures") == 0
           and g3["domain_size"] == 6 * 2 ** 24 and g3["holds"] is True
           and g3.get("failures") == 0
           and gp["domain_rows"] == gp["expected_domain_rows"] == 5340816
           and gp["mismatches"] == 0 and gp["holds"] is True
           and per_n_rows == 5340816 and per_n_mism == 0
           and t4b["domain_size"] == 2 ** 29
           and sum(t4b["failing_census"].values()) == 135604,
           "mirror 2^24 holds=%s; gauges 6*2^24 holds=%s; GP rows=%d "
           "mismatches=%d; t4b 2^29 census=%d"
           % (g2["holds"], g3["holds"], gp["domain_rows"], gp["mismatches"],
              sum(t4b["failing_census"].values())))
    counts["gp_domain_rows"] = gp["domain_rows"]

    # ---- G. dead route 1: single-pinner normalization ----------------------
    record("deadroute.v2_single_pinner",
           v2["PP_SINGLE_PINNER_ALL_N"] is True
           and v2["product_domain"] == 133349376 == 32556 * 4096
           and v2["CHAIN_ALL_N"] is False
           and v2["GLOBAL_BDOUBLEPRIME_COMPLETENESS"] is False
           and v2["both_accept"] is True
           and v2["deterministic_replay_byte_identical"] is True,
           "PP_ALL_N=%s product_domain=%d CHAIN_ALL_N=%s "
           "GLOBAL_B''_COMPLETENESS=%s"
           % (v2["PP_SINGLE_PINNER_ALL_N"], v2["product_domain"],
              v2["CHAIN_ALL_N"], v2["GLOBAL_BDOUBLEPRIME_COMPLETENESS"]))
    counts["v2_product_domain"] = v2["product_domain"]

    # ---- H. dead route 2: two-coordinate chain representation --------------
    fc = q7f["frozen_candidate"]
    record("deadroute.qg7f_representation",
           q7f["representation_premise_refuted"] is True
           and q7f["CHAIN_REPRESENTATION_COMPLETE"] is False
           and q7f["CHAIN_ALL_N"] is False
           and q7f["GLOBAL_BDOUBLEPRIME_COMPLETENESS"] is False
           and fc["tag"] == [1, 1, 1] and fc["tag_weight"] == 3
           and q7f["B_M1_comm_s2_irreducible"] is True
           and q7f["C_M1_comm_s2_irreducible"] is True
           and q7f["class00_reducible_coordinates_B"] == []
           and q7f["class00_reducible_coordinates_C"] == [],
           "tag=%s wt=%d; blocks B,C M1-comm-s2-irreducible; class-(0,0) "
           "reducible coordinates empty in both" % (fc["tag"], fc["tag_weight"]))

    # ---- I. input/event count accounting -----------------------------------
    bm = q5["benchmark"]
    structured = bm["structured_n2_exhaustive"]["instances"]
    fresh = bm["fresh_seeded_panel"]["instances"]
    seed = bm["fresh_seeded_panel"]["seed"]
    fresh_err = bm["fresh_seeded_panel"]["nonzero_errors_verbatim"][0]
    chem_listing = {k: len(v) for k, v in bm["receipted_chemistry_rows"].items()}
    chem_listing_errors = {k: bm["receipted_chemistry"][k]["nonzero_error_count"]
                           for k in bm["receipted_chemistry"]}
    record("counts.qg5_benchmark",
           bm["dp_compared_instances_total"] == 9546
           and structured == 9261 and fresh == 240 and seed == 20260826
           and bm["nonzero_forecast_errors_total"] == 1
           and bm["structured_n2_exhaustive"]["nonzero_error_count"] == 0
           and bm["fresh_seeded_panel"]["nonzero_error_count"] == 1
           and fresh_err["index"] == 7 and fresh_err["n"] == 3
           and fresh_err["C_DP"] == 10 and fresh_err["predicted_C_DP"] == 11
           and fresh_err["error"] == 1,
           "total=%d = structured %d + fresh %d + chemistry %d; errors=%d "
           "(fresh idx 7, n=3, C_DP 10 vs predicted 11)"
           % (bm["dp_compared_instances_total"], structured, fresh,
              bm["dp_compared_instances_total"] - structured - fresh,
              bm["nonzero_forecast_errors_total"]))

    q1 = q5b["q1"]
    panels = q5b["panels"]
    pd = panels["panel_d_chemistry"]
    pa_row = panels["panel_a_refuting_instance"]
    chem_total = pd["rows_total"]
    record("counts.qg5b_events",
           q1["dp_compared_instances_total"] == 9547
           == 1 + 9261 + 240 + chem_total
           and panels["panel_b_structured_n2"]["instances"] == 9261
           and panels["panel_b_structured_n2"]["q1_nonzero_error_count"] == 0
           and panels["panel_c_fresh_seeded"]["instances"] == 240
           and panels["panel_c_fresh_seeded"]["q1_nonzero_error_count"] == 0
           and panels["panel_c_fresh_seeded"]["qg5_receipt_bound"] is True
           and chem_total == 45 and pd["pinched_exact_total"] == 45
           and pa_row["index_in_fresh_panel"] == 7 and pa_row["n"] == 3
           and pa_row["C_DP"] == 10 and pa_row["F2_C_Dxx"] == 10
           and pa_row["q1_error"] == 0
           and q1["nonzero_error_total"] == 0
           and q1["outcome"] == "Q1_ZERO_ERROR"
           and q5b["gates"]["no_dp_call_in_forecast_path"] is True,
           "9,547 events = 1 refuting re-audit + 9,261 structured + 240 fresh "
           "+ 45 chemistry; nonzero_error_total=%d; "
           "no_dp_call_in_forecast_path=%s"
           % (q1["nonzero_error_total"],
              q5b["gates"]["no_dp_call_in_forecast_path"]))
    counts["distinct_inputs"] = bm["dp_compared_instances_total"]
    counts["comparison_events"] = q1["dp_compared_instances_total"]
    counts["chemistry_rows_total"] = chem_total
    counts["qg5_chemistry_verbatim_listing"] = chem_listing
    counts["qg5_chemistry_listing_nonzero_errors"] = chem_listing_errors

    # ---- verdict -------------------------------------------------------------
    failed = [c for c in checks if c["status"] != "pass"]
    verdict = "PASS" if not failed else "FAIL"
    exit_code = 0 if not failed else 1

    receipt = {
        "schema": SCHEMA,
        "version": VERSION,
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": platform.node(),
        "python": platform.python_version(),
        "checker_sha256": hashlib.sha256(
            open(os.path.abspath(__file__), "rb").read()).hexdigest(),
        "repo_root_relative_artifacts": ARTIFACT_DIR,
        "artifacts": observed,
        "checks": checks,
        "counts": counts,
        "scope_note": ("Receipt-level re-derivation of the committed "
                       "composition arithmetic; the 6,341,787,648-state "
                       "enumeration itself is the scientific run bound by "
                       "the QG-7e receipt and is not re-executed."),
        "verdict": verdict,
        "exit_code": exit_code,
    }
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "CHECK_ENVELOPE_COMPOSITION_RECEIPT_V1.json")
    with open(out_path, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")

    for c in checks:
        print("[%s] %s -- %s" % (c["status"].upper(), c["id"], c["detail"]))
    print("VERDICT: %s (%d/%d checks pass)" % (verdict,
                                               len(checks) - len(failed),
                                               len(checks)))
    print("receipt: %s" % out_path)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
