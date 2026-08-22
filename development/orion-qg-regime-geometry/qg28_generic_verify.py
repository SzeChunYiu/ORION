#!/usr/bin/env python3
"""Independent from-primitives verifier for QG-28 (residual W9).

Re-derives, rather than reads: the support-capped frame-pair counts, both
cell-count models and the crossover they imply, the minimum-weight Tag by two
independent routes, and -- for a declared sample -- C_D++ itself by a brute
force written straight against the frozen family definition, through
``r6m.factor_restore_triple`` rather than through any cost formula this
programme's search code happens to use.

Usage:  qg28_generic_verify.py [results.json]

The input path is an argument and the output path follows it. QG-10's verifier
hardcoded both, which made it untestable and made it destroy its own record the
first time anyone tried; that is not repeated here.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import sys
from typing import Any, Mapping

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/extensions/orion-q"))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6b_tare_transformation_reuse_donor as reuse  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402

h = p10.h
wt, symp, mul = p10.wt, p10.symp, p10.mul
LABELS = ((0, 1), (1, 0))

RESULTS = ROOT / "research/extensions/orion-qg/QG28_SUPPORT_CAPPED_REALIZATION_RESULTS.json"
OUT = ROOT / "development/orion-qg-regime-geometry/QG28_GENERIC_VERIFICATION.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG28_SUPPORT_CAPPED_REALIZATION_PROTOCOL_V1.md"

#: How many n=1 instances the definitional brute force re-derives. Declared,
#: because it is a sample and must not read as an enumeration.
BRUTE_N1_INSTANCES = 12
BRUTE_STRIDE = 337
#: How many of the DP-driven search's n=1 rows are recomputed definitionally.
DP_ROWS_RECHECKED = 6


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ---- primitives re-derived, not imported from the lane ---------------------


def small_paulis(n: int) -> list[tuple[int, int]]:
    out = []
    for q in range(n):
        for bx, bz in ((1, 0), (0, 1), (1, 1)):
            out.append((bx << q, bz << q))
    for q1 in range(n):
        for q2 in range(q1 + 1, n):
            for b1 in ((1, 0), (0, 1), (1, 1)):
                for b2 in ((1, 0), (0, 1), (1, 1)):
                    out.append(((b1[0] << q1) | (b2[0] << q2),
                                (b1[1] << q1) | (b2[1] << q2)))
    return out


def pair_count(n: int) -> int:
    s = small_paulis(n)
    return sum(1 for a in s for b in s if symp(a, b) == 1)


def cells_dxx(n: int) -> int:
    return 2 * (4 ** n - 1) * (3 * (2 * n + 1) * 4 ** (2 * n) + 4 ** (2 * n))


def cells_capped(p: int) -> int:
    return 54 * p ** 3


def cells_capped_dp(n: int, p: int) -> int:
    return p ** 3 * (512 * n + 48)


def tag_min_by_dp(six, l0: int, l1: int, n: int) -> int:
    INF = 10 ** 9
    target = sum(1 << i for i in range(6) if (l1 if i % 2 else l0))
    dp = [INF] * 64
    dp[0] = 0
    for q in range(n):
        nd = [INF] * 64
        for sx in (0, 1):
            for sz in (0, 1):
                cost = 0 if (sx or sz) == 0 else 1
                v = 0
                for i, r in enumerate(six):
                    if (sx & ((r[1] >> q) & 1)) ^ (sz & ((r[0] >> q) & 1)):
                        v |= 1 << i
                for st in range(64):
                    if dp[st] + cost < nd[st ^ v]:
                        nd[st ^ v] = dp[st] + cost
        dp = nd
    return dp[target]


def tag_min_by_sweep(six, l0: int, l1: int, n: int) -> int:
    best = 10 ** 9
    for x in range(2 ** n):
        for z in range(2 ** n):
            s = (x, z)
            if all(symp(s, r) == (l1 if i % 2 else l0) for i, r in enumerate(six)):
                best = min(best, wt(s))
    return best


def brute_c_dxx(target_pairs, n: int) -> int:
    """C_D++ from the frozen family definition, by exhaustive enumeration.

    Deliberately slow and deliberately literal: every frame-pair triple, every
    Tag, every target permutation, every per-block central, and the Restore
    support taken from ``r6m.factor_restore_triple`` -- the frozen factoring
    function -- rather than from any closed-form agreement count. If the lane's
    cost identity were wrong, this is what would catch it.
    """
    s = small_paulis(n)
    pairs = [(a, b) for a in s for b in s if symp(a, b) == 1]
    keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n) if (x, z) != (0, 0)]
    best = None
    for perms in itertools.product((0, 1), repeat=3):
        ordered = [
            target_pairs[j] if perms[j] == 0
            else (target_pairs[j][1], target_pairs[j][0])
            for j in range(3)
        ]
        for skey in keys:
            for triple in itertools.product(pairs, repeat=3):
                labels = (symp(skey, triple[0][0]), symp(skey, triple[0][1]))
                if labels[0] == labels[1]:
                    continue
                if any(
                    (symp(skey, f[0]), symp(skey, f[1])) != labels for f in triple[1:]
                ):
                    continue
                uanti = sum(
                    min(r6m._uanti_m2(triple[j], c) for c in (0, 1)) for j in range(3)
                )
                signed = []
                for j in range(3):
                    row = []
                    for k in range(2):
                        t = mul(ordered[j][k], triple[j][k])
                        row.append(
                            (int(reuse.correction_phase(
                                ordered[j][k], triple[j][k], t, n)), t)
                        )
                    signed.append(row)
                factored = sum(
                    r6m.factor_restore_triple(
                        signed[0][k], signed[1][k], signed[2][k], n)["support"]
                    for k in range(2)
                )
                cost = uanti + 2 * wt(skey) + factored
                if best is None or cost < best:
                    best = cost
    if best is None:
        raise AssertionError("brute force found no feasible D++ point")
    return int(best)


def letter_key(letter: int, q: int):
    bx, bz = h.CODE_BITS[letter]
    return (bx << q, bz << q)


# ---- the verifier ----------------------------------------------------------


def verify(path: pathlib.Path) -> dict[str, Any]:
    rec = json.loads(path.read_text())
    checks: dict[str, bool] = {}
    notes: dict[str, Any] = {}

    # 1. digest custody -- necessary, never sufficient (RECEIPT_CHURN_HAZARD).
    body = {k: v for k, v in rec.items()
            if k not in ("content_digest", "timings_excluded_from_digest",
                         "total_seconds")}
    checks["content_digest_recomputes"] = (
        rec.get("content_digest") == sha(canonical(body))
    )
    checks["protocol_digest_matches_committed_protocol"] = (
        rec.get("protocol_digest") == sha(PROTOCOL.read_text())
    )

    # 2. the honesty disclosure the protocol's section 0 requires.
    ps = rec.get("prospective_status") or {}
    checks["q1_and_q2_declared_not_prospective"] = (
        ps.get("q1_build_the_capped_search") is False
        and ps.get("q2_agreement_on_declared_domains") is False
    )
    checks["q3_declared_prospective"] = ps.get("q3_cell_model_and_crossover") is True
    checks["scouting_disclosure_present"] = bool(
        str(ps.get("disclosure", "")).strip()
    ) and "prototype" in str(ps.get("disclosure", "")).lower()
    checks["protocol_carries_the_same_disclosure"] = (
        "Scouting disclosure" in PROTOCOL.read_text()
    )

    # 3. frame-pair counts re-derived from the Pauli algebra.
    fp = rec.get("frame_pair_counts") or {}
    rederived = {str(n): pair_count(n) for n in (1, 2, 3)}
    checks["frame_pair_counts_rederived"] = (
        {k: int(v) for k, v in fp.items()} == rederived
    )
    notes["frame_pair_counts_rederived"] = rederived

    # 4. both cell models and the crossover, recomputed from the frozen formulas.
    q3 = rec.get("q3_cell_model") or {}
    ladder = q3.get("ladder") or []
    ok_rows = bool(ladder)
    for row in ladder:
        n = int(row["n"])
        p = pair_count(n)
        if (int(row["P"]) != p or int(row["N_cap"]) != cells_capped(p)
                or int(row["N_dxx"]) != cells_dxx(n)
                or int(row["N_cap_dp"]) != cells_capped_dp(n, p)
                or bool(row["capped_cheaper"]) != (cells_capped(p) < cells_dxx(n))
                or bool(row["capped_dp_cheaper"]) != (
                    cells_capped_dp(n, p) < cells_dxx(n))):
            ok_rows = False
    checks["cell_model_rows_rederived"] = ok_rows
    own_cross = next(
        (n for n in range(1, 15) if cells_capped(pair_count(n)) < cells_dxx(n)), None
    )
    checks["crossover_rederived"] = q3.get("crossover_n") == own_cross
    own_cross_dp = next(
        (n for n in range(1, 15)
         if cells_capped_dp(n, pair_count(n)) < cells_dxx(n)), None
    )
    checks["dp_variant_crossover_rederived"] = (
        q3.get("crossover_n_dp_variant") == own_cross_dp
    )
    notes["crossover_rederived"] = own_cross
    notes["crossover_dp_variant_rederived"] = own_cross_dp

    # The amendment is only admissible if it discloses itself. A second counting
    # rule added after a first run is exactly the churn `criterion_binding` gates,
    # and the mitigating fact -- that the terminal does not move -- has to be
    # stated in the record rather than left for a reader to work out.
    amend = q3.get("counting_rule_amendment") or {}
    checks["counting_rule_amendment_discloses_itself"] = (
        amend.get("added_after_the_protocol_was_frozen") is True
        and amend.get("added_before_any_full_run_completed") is True
        and bool(str(amend.get("description", "")).strip())
        and bool(str(amend.get("rationale", "")).strip())
        and bool(str(amend.get("effect_on_the_terminal", "")).strip())
        and bool(str(amend.get("when_and_why_it_was_noticed", "")).strip())
    )

    # 5. the Tag claim, by the verifier's own DP against its own sweep.
    tag_ok = True
    tag_rows = 0
    for n in (1, 2, 3):
        s = small_paulis(n)
        pairs = [(a, b) for a in s for b in s if symp(a, b) == 1]
        step = max(1, len(pairs) // 7)
        for i in range(0, len(pairs), step):
            for j in range(0, len(pairs), step):
                k = (i + j) % len(pairs)
                six = (pairs[i][0], pairs[i][1], pairs[j][0], pairs[j][1],
                       pairs[k][0], pairs[k][1])
                for l0, l1 in LABELS:
                    tag_rows += 1
                    if tag_min_by_dp(six, l0, l1, n) != tag_min_by_sweep(
                            six, l0, l1, n):
                        tag_ok = False
    checks["tag_dp_equals_tag_sweep_under_this_verifier"] = tag_ok
    notes["tag_rows_checked_by_verifier"] = tag_rows
    tdv = rec.get("tag_dp_vs_sweep") or {}
    checks["tag_dp_claims_are_internally_consistent"] = bool(tdv) and all(
        bool(v.get("dp_reproduces_sweep")) == (int(v.get("disagreement_count", -1)) == 0)
        for v in tdv.values()
    )

    # 6. C_D++ itself, re-derived definitionally on a declared n=1 sample.
    brute_rows = []
    brute_ok = True
    idx = 0
    for _ in range(BRUTE_N1_INSTANCES):
        p6 = tuple((idx >> (2 * (5 - t))) & 3 for t in range(6))
        tps = tuple((letter_key(p6[2 * j], 0), letter_key(p6[2 * j + 1], 0))
                    for j in range(3))
        mine = brute_c_dxx(tps, 1)
        theirs = int(r6p.dxx_search(tps, 1, max_weight=2)["C_Dxx"])
        brute_rows.append({"instance_index": idx, "brute": mine, "dxx": theirs,
                           "agree": mine == theirs})
        if mine != theirs:
            brute_ok = False
        idx = (idx + BRUTE_STRIDE) % 4096
    checks["definitional_brute_force_agrees_on_declared_n1_sample"] = brute_ok
    notes["definitional_brute_force_rows"] = brute_rows

    # 6b. the DP-driven search block: the thing that licenses "the 4^n Tag sweep
    #     is removable". Its rows are recomputed by the verifier's own
    #     definitional brute force, so the claim rests on a re-derivation.
    dps = rec.get("dp_driven_search") or {}
    rows = dps.get("rows") or []
    checks["dp_driven_search_flag_matches_its_rows"] = bool(rows) and (
        bool(dps.get("all_agree")) == all(bool(r.get("agree")) for r in rows)
        and int(dps.get("agree", -1)) == sum(1 for r in rows if r.get("agree"))
        and int(dps.get("instances", -1)) == len(rows)
    )
    checks["dp_driven_search_is_not_n1_only"] = any(
        int(r.get("n", 1)) >= 2 for r in rows
    )
    checks["dp_driven_search_declares_its_scope"] = bool(
        str(dps.get("declared_scope_and_obstacle", "")).strip()
    )
    dp_rows_ok = bool(rows)
    checked = 0
    for row in rows:
        if int(row.get("n", 0)) != 1 or checked >= DP_ROWS_RECHECKED:
            continue
        idx = int(row["instance_index"])
        p6 = tuple((idx >> (2 * (5 - t))) & 3 for t in range(6))
        tps = tuple((letter_key(p6[2 * j], 0), letter_key(p6[2 * j + 1], 0))
                    for j in range(3))
        mine = brute_c_dxx(tps, 1)
        if (int(row.get("C_dp_driven", -1)) != mine
                or int(row.get("C_table_driven", -2)) != mine
                or int(row.get("C_Dxx", -3)) != mine):
            dp_rows_ok = False
        checked += 1
    checks["dp_driven_search_rows_recomputed"] = dp_rows_ok and checked > 0
    notes["dp_driven_rows_recomputed"] = checked

    # The n>=2 rows were previously read, not recomputed, so a fabricated one
    # cleared the gate while the "the Tag table is removable" claim looked
    # evidenced. Reported by Cursor Bugbot on 5da6b4de. The definitional brute
    # force is not affordable at n=2, so the committed dxx_search is used as the
    # independent value and the row's three numbers must all equal it.
    w1 = [letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    n2_ok, n2_checked = True, 0
    for row in rows:
        if int(row.get("n", 0)) != 2:
            continue
        idxs = row.get("target_indices")
        if not isinstance(idxs, list) or len(idxs) != 6:
            n2_ok = False
            continue
        tps = tuple((w1[idxs[2 * j]], w1[idxs[2 * j + 1]]) for j in range(3))
        want = int(r6p.dxx_search(tps, 2, max_weight=2)["C_Dxx"])
        if any(int(row.get(k, -1)) != want
               for k in ("C_dp_driven", "C_table_driven", "C_Dxx")):
            n2_ok = False
        n2_checked += 1
    checks["dp_driven_n2_rows_recomputed"] = n2_ok and n2_checked > 0
    notes["dp_driven_n2_rows_recomputed"] = n2_checked

    # A DP sample that did NOT agree is a legitimate outcome and this verifier
    # must accept a receipt that reports it honestly. What it may not accept is
    # a receipt that reports a disagreement and still announces the win.
    dp_agrees = bool(dps.get("all_agree"))
    checks["dp_disagreement_would_move_the_terminal"] = dp_agrees or (
        rec.get("terminal") == "QG28_REALIZATION_DISAGREES__SOMETHING_IS_WRONG"
    )

    lic = (rec.get("deviation_from_protocol_section_3_3") or {}).get(
        "what_licenses_the_claim_anyway"
    )
    checks["licensing_record_matches_the_dp_rows"] = isinstance(lic, Mapping) and (
        int(lic.get("instances_run", -1)) == len(rows)
        and int(lic.get("instances_agreeing", -1)) == sum(
            1 for r in rows if r.get("agree"))
        and bool(lic.get("licenses_the_claim")) == (
            bool(rows) and all(bool(r.get("agree")) for r in rows))
    )

    dev = rec.get("deviation_from_protocol_section_3_3") or {}
    checks["section_3_3_deviation_disclosed"] = bool(dev) and all(
        bool(str(dev.get(k, "")).strip())
        for k in ("section_says", "what_the_bulk_domains_actually_run", "why",
                  "found_by")
    ) and bool(str((dev.get("what_licenses_the_claim_anyway") or {}).get(
        "text", "")).strip())

    # 7. the hostile panels, recomputed row by row rather than read.
    panels = next(
        (d for d in rec.get("domains", []) if str(d.get("domain", "")).startswith("C")),
        None,
    )
    panel_ok = panels is not None
    if panels is not None:
        want = {}
        inst = [
            (name, 1, tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b])
                            for a, b in pr))
            for name, pr in sorted(r6m._HOSTILE_N1_PANELS.items())
        ] + [
            (name, 2, tuple((tuple(a), tuple(b)) for a, b in pr))
            for name, pr in sorted(r6m._HOSTILE_N2_PANELS.items())
        ]
        for name, n, tps in inst:
            want[name] = int(r6p.dxx_search(tps, n, max_weight=2)["C_Dxx"])
        for row in panels.get("rows", []):
            nm = row.get("panel")
            if nm not in want:
                panel_ok = False
                continue
            if int(row.get("C_Dxx", -1)) != want[nm]:
                panel_ok = False
            if int(row.get("C_capped", -2)) != want[nm]:
                panel_ok = False
            if bool(row.get("agree")) != (
                    int(row.get("C_capped", -2)) == int(row.get("C_Dxx", -1))):
                panel_ok = False
        if sorted(r.get("panel") for r in panels.get("rows", [])) != sorted(want):
            panel_ok = False
    checks["hostile_panel_rows_recomputed"] = panel_ok

    # 8. domain bookkeeping. A claim of completeness is checked against the size
    #    the domain would have if it were complete, not against its own word.
    doms = {str(d.get("domain", ""))[0]: d for d in rec.get("domains", [])}
    checks["domain_a_is_the_complete_4096"] = (
        "A" in doms and doms["A"].get("instances") == 4096
        and doms["A"].get("complete_enumeration") is True
    )
    checks["domain_b_is_the_complete_9261"] = (
        "B" in doms and doms["B"].get("instances") == 21 ** 3
        and doms["B"].get("complete_enumeration") is True
    )
    checks["domain_d_is_declared_a_sample_not_an_enumeration"] = (
        "D" in doms and doms["D"].get("complete_enumeration") is False
        and bool(str(doms["D"].get("obstacle_named", "")).strip())
    )
    checks["every_domain_agree_flag_matches_its_own_counts"] = bool(doms) and all(
        bool(d.get("all_agree")) == (
            int(d.get("agree", -1)) == int(d.get("instances", -2))
        )
        for d in rec.get("domains", [])
    )
    checks["no_domain_claims_agreement_while_carrying_mismatches"] = all(
        not (bool(d.get("all_agree")) and int(d.get("mismatch_count", 0)) > 0)
        for d in rec.get("domains", [])
    )
    checks["all_domains_agree_matches_the_domains"] = (
        bool(rec.get("all_domains_agree"))
        == all(bool(d.get("all_agree")) for d in rec.get("domains", []))
    )
    checks["total_instances_is_the_sum_of_the_domains"] = (
        int(rec.get("total_instances_compared", -1))
        == sum(int(d.get("instances", 0)) for d in rec.get("domains", []))
    )

    # 9. the terminal must follow from what was measured, not be chosen.
    agree = bool(rec.get("all_domains_agree")) and dp_agrees
    cross = own_cross is not None
    if agree and cross:
        want_terminal = "QG28_COROLLARY_REALIZED__PROJECTED_WIN_CONFIRMED_WITH_ITS_CROSSOVER"
    elif agree:
        want_terminal = "QG28_COROLLARY_REALIZED__NO_WIN_AT_ANY_N"
    else:
        want_terminal = "QG28_REALIZATION_DISAGREES__SOMETHING_IS_WRONG"
    checks["terminal_follows_from_the_measurements"] = (
        rec.get("terminal") == want_terminal
    )
    notes["terminal_rederived"] = want_terminal

    # 10. authority ceiling.
    checks["not_r6_and_no_novelty_asserted"] = (
        rec.get("r6_authority") is False
        and rec.get("novelty_authority") is False
        and rec.get("novelty_credit") is False
        and rec.get("donor_novelty_credit") is False
        and rec.get("physical_quantum_advantage_claim") is False
        and rec.get("protected_subject_read") is False
        and rec.get("reserved_stretched_n2_accessed") is False
    )
    checks["donor_records_assert_no_novelty"] = bool(
        rec.get("donor_search_records")
    ) and all(
        r.get("asserts_novelty") is False for r in rec.get("donor_search_records", [])
    )
    gates = rec.get("gates") or {}
    checks["gate_g3_wall_clock_carries_no_argument"] = (
        gates.get("G3_no_complexity_inference_from_wall_clock") is True
        and bool(str(q3.get("wall_clock_status", "")).strip())
    )
    checks["gate_g5_matches_the_domains_as_recorded"] = (
        gates.get("G5_complete_on_A_B_C__D_declared_sample")
        == (
            bool(doms.get("A", {}).get("complete_enumeration"))
            and bool(doms.get("B", {}).get("complete_enumeration"))
            and bool(doms.get("C", {}).get("complete_enumeration"))
            and not bool(doms.get("D", {}).get("complete_enumeration"))
        )
    )

    verdict = "ACCEPT" if all(checks.values()) else "REJECT"
    return {
        "schema": "ORIONQG.QG28.GenericVerification.v1",
        "input": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "checks": checks,
        "failed_checks": sorted(k for k, v in checks.items() if not v),
        "notes": notes,
        "verdict": verdict,
    }


def main(argv: list[str]) -> int:
    path = pathlib.Path(argv[1]).resolve() if len(argv) > 1 else RESULTS
    out = verify(path)
    dest = OUT if path == RESULTS else path.with_name(path.stem + ".verification.json")
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": out["verdict"],
                      "failed": out["failed_checks"]}, indent=1))
    print("wrote", dest)
    return 0 if out["verdict"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
