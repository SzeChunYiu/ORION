#!/usr/bin/env python3
"""QG-24 generic verifier — from primitives, no analyzer import, no numpy.

Re-derives, rather than re-reads, everything QG-24 claims:

1. every digest (protocol, QG-21 receipt, staged predictions, result digest);
2. the donor-search gate, re-implemented here from ``donor_search``'s stated
   rules, plus the stronger check that every verbatim passage actually occurs in
   the committed query log;
3. Lemma L1, by an independent implementation of the merge search over the
   COMPLETE n=1 configuration space of the frozen grammar -- including the
   claim that the only position pairs the relation ever admits are the two block
   seams;
4. the n=1 rotation-count distribution, by complete re-enumeration;
5. the domain-size identity at every declared n, from an independent nine-bit
   dynamic program that shares no code with the analyzer's transform-based count;
6. every panel row: the decidable predicate, and the serialized seven-rotation
   witness -- re-checked against the grammar constraints, re-counted under the
   merge relation, and its theta_FT cost recomputed from scratch;
7. the terminal, the gate block and the forecast tally, for consistency with the
   re-derived numbers.

What this verifier establishes is every UPPER bound (a seven-rotation
compilation of the stated cost exists), every complete-enumeration count it
recomputes, and every arithmetic and digest claim. The LOWER bound -- that no
cheaper seven-rotation member exists -- is the exact DP's claim and is reported
as such, not silently absorbed.

Usage: qg24_generic_verify.py [results.json]
Exit 0 on ACCEPT, 1 on REJECT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_RESULTS = REPO / "research/extensions/orion-qg/QG24_ROTATION_REGIME_RESULTS.json"
QG21_RESULTS = REPO / "research/extensions/orion-qg/QG21_FT_CHEMISTRY_RESULTS.json"
DONOR_LOG = REPO / "development/orion-qg-regime-geometry/QG24_DONOR_SEARCH.md"

# ---- binary symplectic Pauli primitives, written out ------------------------
CODE_BITS = ((0, 0), (1, 0), (1, 1), (0, 1))
BITS_CODE = {b: i for i, b in enumerate(CODE_BITS)}


def lsymp(a, b):
    xa, za = CODE_BITS[a]
    xb, zb = CODE_BITS[b]
    return (xa & zb) ^ (za & xb)


def lmul(a, b):
    xa, za = CODE_BITS[a]
    xb, zb = CODE_BITS[b]
    return BITS_CODE[(xa ^ xb, za ^ zb)]


def pmul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def pwt(a):
    return bin(a[0] | a[1]).count("1")


def psymp(a, b):
    return (bin(a[0] & b[1]).count("1") + bin(a[1] & b[0]).count("1")) & 1


def pcode(a, q):
    return BITS_CODE[(((a[0] >> q) & 1), ((a[1] >> q) & 1))]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---- independent merge search ----------------------------------------------
# Uanti for m=2 is exp(i.t/2 R_nc).exp(i.p R_c).exp(i.t/2 R_nc); three blocks in
# sequence give nine rotations. Slot order (aA,bA,aB,bB,aC,bC).
POS = (0, 1, 0, 2, 3, 2, 4, 5, 4)
SEAM = {2: 0, 5: 1}  # Clifford intervener after this position; 0 = block A, 1 = B


def merge_search(eq, sp, comm, in_place):
    """comm[b][s] = 1 iff both Restore branch letters of block b commute with s."""
    edges = []
    for i in range(9):
        for j in range(i + 1, 9):
            si = POS[i]
            if not eq[si][POS[j]]:
                continue
            if any(sp[POS[k]][si] for k in range(i + 1, j)):
                continue
            if in_place and any(not comm[b][si] for p, b in SEAM.items() if i <= p < j):
                continue
            edges.append((i, j))
    best = [0]

    def rec(used, idx, cnt):
        if cnt > best[0]:
            best[0] = cnt
        for t in range(idx, len(edges)):
            i, j = edges[t]
            if (used >> i) & 1 or (used >> j) & 1:
                continue
            rec(used | (1 << i) | (1 << j), t + 1, cnt + 1)

    rec(0, 0, 0)
    return 9 - best[0], edges


def slot_data(frames, centrals, restores):
    slots = []
    for j in range(3):
        r0, r1 = frames[j]
        a, c = (r0, r1) if centrals[j] == 1 else (r1, r0)
        slots.extend([a, c])
    eq = [[1 if slots[i] == slots[j] else 0 for j in range(6)] for i in range(6)]
    sp = [[psymp(slots[i], slots[j]) for j in range(6)] for i in range(6)]
    comm = [[1 if all(psymp(t, slots[k]) == 0 for t in restores[b]) else 0
             for k in range(6)] for b in range(3)]
    return slots, eq, sp, comm


# ---- complete n=1 re-enumeration -------------------------------------------
ACCEPT9 = (0b010000111, 0b100000111)


def _state9(r, s):
    rA0, rA1, rB0, rB1, rC0, rC1 = r
    sA0, sB0, sC0 = lsymp(s, rA0), lsymp(s, rB0), lsymp(s, rC0)
    sA1, sB1, sC1 = lsymp(s, rA1), lsymp(s, rB1), lsymp(s, rC1)
    return (lsymp(rA0, rA1)
            | (lsymp(rB0, rB1) << 1)
            | (lsymp(rC0, rC1) << 2)
            | ((sA0 ^ sB0) << 3)
            | ((sA0 ^ sC0) << 4)
            | ((sA1 ^ sB1) << 5)
            | ((sA1 ^ sC1) << 6)
            | (sA0 << 7)
            | (sA1 << 8))


def enumerate_n1():
    """Complete n=1 enumeration: distribution per model and the pair support."""
    dist = {"R6L_RESTORE_IN_PLACE": {7: 0, 8: 0, 9: 0},
            "R6M_RESTORE_FACTORED": {7: 0, 8: 0, 9: 0}}
    pair_support, total = set(), 0
    for centrals in itertools.product((0, 1), repeat=3):
        for r in itertools.product(range(4), repeat=6):
            for s in range(4):
                if _state9(r, s) not in ACCEPT9:
                    continue
                frames = [(r[0], r[1]), (r[2], r[3]), (r[4], r[5])]
                slots = []
                for j in range(3):
                    r0, r1 = frames[j]
                    a, c = (r0, r1) if centrals[j] == 1 else (r1, r0)
                    slots.extend([a, c])
                eq = [[1 if slots[i] == slots[j] else 0 for j in range(6)]
                      for i in range(6)]
                sp = [[lsymp(slots[i], slots[j]) for j in range(6)]
                      for i in range(6)]
                for tA0, tA1, tB0, tB1 in itertools.product(range(4), repeat=4):
                    comm = [
                        [1 if (lsymp(tA0, slots[k]) == 0 and lsymp(tA1, slots[k]) == 0)
                         else 0 for k in range(6)],
                        [1 if (lsymp(tB0, slots[k]) == 0 and lsymp(tB1, slots[k]) == 0)
                         else 0 for k in range(6)],
                        [1] * 6,
                    ]
                    total += 1
                    for model in dist:
                        rc, edges = merge_search(
                            eq, sp, comm, model == "R6L_RESTORE_IN_PLACE")
                        dist[model][rc] += 1
                        pair_support.update(edges)
    return dist, sorted([i + 1, j + 1] for i, j in pair_support), total


def admissible_frame_tag_counts(n_values):
    """Independent nine-bit DP counting admissible (frames, Tag) assignments."""
    local = [0] * 512
    for r in itertools.product(range(4), repeat=6):
        for s in range(4):
            local[_state9(r, s)] += 1
    nz = [(d, c) for d, c in enumerate(local) if c]
    dp = [0] * 512
    dp[0] = 1
    out = {}
    for q in range(1, max(n_values) + 1):
        nxt = [0] * 512
        for t, cur in enumerate(dp):
            if cur:
                for d, c in nz:
                    nxt[t ^ d] += cur * c
        dp = nxt
        if q in n_values:
            out[q] = dp[ACCEPT9[0]] + dp[ACCEPT9[1]]
    return out


# ---- panel witness re-derivation -------------------------------------------

def theta_ft_cost(a, bs, S, targets, centrals, n):
    """theta_FT Clifford cost (4,2,2,1) of a seven-rotation compilation."""
    frames = [((a, bs[j]) if centrals[j] == 1 else (bs[j], a)) for j in range(3)]
    cost = 0
    for j in range(3):
        nc, c = (1 - centrals[j]), centrals[j]
        cost += 4 * (pwt(frames[j][nc]) - 1) + 2 * (pwt(frames[j][c]) - 1)
    cost += 2 * pwt(S)
    restores = [(pmul(targets[j][0], frames[j][0]),
                 pmul(targets[j][1], frames[j][1])) for j in range(3)]
    for k in range(2):
        ta, tb, tc = (restores[0][k], restores[1][k], restores[2][k])
        for q in range(n):
            la, lb, lc = pcode(ta, q), pcode(tb, q), pcode(tc, q)
            if la == lb == lc and la != 0:
                cost += 1
            else:
                cost += (la != 0) + (lb != 0) + (lc != 0)
    return cost, frames, restores


# ---- donor-search gate, re-implemented -------------------------------------
VERDICTS = {"SUBSUMED", "SUBSUMED_IN_SPECIAL_CASE", "INSTANCE_OF_KNOWN_GENERAL",
            "NEAREST_MISS", "NO_PRIOR_ART_FOUND", "CANNOT_ASSESS"}
NEEDS_PASSAGE = {"SUBSUMED", "SUBSUMED_IN_SPECIAL_CASE",
                 "INSTANCE_OF_KNOWN_GENERAL", "NEAREST_MISS"}
FAMILIES = ("OWN_VOCABULARY", "DONOR_FIELD_TRANSLATION", "INVERTED_OR_SURVEY")


def check_donor(records, log_text):
    bad = []
    for rec in records:
        cid = rec.get("claim_id")
        if rec.get("verdict") not in VERDICTS:
            bad.append([cid, "verdict-not-admissible"])
            continue
        fams = rec.get("query_families") or []
        if any(f not in fams for f in FAMILIES):
            bad.append([cid, "missing-query-family"])
        if rec.get("asserts_novelty"):
            if rec["verdict"] == "CANNOT_ASSESS":
                bad.append([cid, "cannot-assess-on-novelty-claim"])
            if not rec.get("query_log_ref"):
                bad.append([cid, "missing-query-log-ref"])
        if rec["verdict"] in NEEDS_PASSAGE and not str(
                rec.get("verbatim_passage", "")).strip():
            bad.append([cid, "missing-verbatim-passage"])
        passage = " ".join(str(rec.get("verbatim_passage", "")).split())
        if passage:
            # Markdown blockquote markers only. lstrip("> ") would treat its
            # argument as a CHARACTER SET and eat any run of '>' and spaces,
            # which in a fail-closed check could splice non-adjacent text into
            # something that looks like one contiguous quote. Strip the literal
            # "> " / ">" prefix instead, repeatedly, for nested blockquotes.
            def _unquote(line):
                while True:
                    if line.startswith("> "):
                        line = line[2:]
                    elif line.startswith(">"):
                        line = line[1:]
                    else:
                        return line
            flat = " ".join(_unquote(line).strip()
                            for line in log_text.splitlines())
            flat = " ".join(flat.split())
            if passage not in flat:
                bad.append([cid, "passage-not-in-committed-query-log"])
    return bad


def main(argv):
    res_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_RESULTS
    res = json.loads(res_path.read_text())
    checks, failures = {}, []

    def record(name, ok, detail=None):
        checks[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            failures.append(name)

    # 1. digests ------------------------------------------------------------
    record("protocol_sha256_recomputes",
           sha_file(REPO / res["protocol"]) == res["protocol_sha256"])
    record("qg21_receipt_unedited_sha256",
           sha_file(QG21_RESULTS) == res["qg21_binding"]["results_sha256"],
           {"recomputed": sha_file(QG21_RESULTS)})
    record("result_digest_recomputes",
           sha_text(canonical({k: v for k, v in res.items()
                               if k != "result_digest"})) == res["result_digest"])
    record("stage1_digest_recomputes",
           sha_text(canonical(res["stage1"]["embedded"])) == res["stage1"]["digest"])

    # 2. donor search -------------------------------------------------------
    bad = check_donor(res["donor_search"]["records"], DONOR_LOG.read_text())
    record("donor_search_gate_reimplemented", not bad, {"bad": bad})
    record("no_novelty_granted",
           res["novelty_credit"] is False and res["novelty_authority"] is False
           and res["donor_novelty_credit"] is False)
    record("document_level_verification_declared_false",
           res["donor_search"]["document_level_verification"] is False)

    # 3. Lemma L1 + 4. complete n=1 re-enumeration --------------------------
    dist, pairs, total = enumerate_n1()
    record("lemma_L1_pair_support_is_the_two_block_seams",
           pairs == [[3, 4], [6, 7]], {"recomputed": pairs})
    n1 = res["q1_distribution"]["1"]
    ok = True
    for model, block in n1["per_model"].items():
        for r in ("7", "8", "9"):
            if int(block["distribution_reduced"][r]) != dist[model][int(r)]:
                ok = False
    record("n1_distribution_recomputed_from_primitives", ok,
           {"recomputed": {m: {str(k): v for k, v in d.items()}
                           for m, d in dist.items()}})
    record("n1_domain_size_recomputed",
           total == int(n1["enumerated_domain_size_reduced"]),
           {"recomputed": total})

    # 5. domain-size identity at every declared n ---------------------------
    ns = sorted(int(k) for k in res["q1_distribution"])
    adm = admissible_frame_tag_counts(ns)
    bad_n = []
    for n in ns:
        block = res["q1_distribution"][str(n)]
        expect = 8 * adm[n] * (4 ** (4 * n))
        if int(block["enumerated_domain_size_reduced"]) != expect:
            bad_n.append([n, "domain-size"])
        if int(block["independent_admissible_frame_tag_count"]) != adm[n]:
            bad_n.append([n, "frame-tag-count"])
        for model, mb in block["per_model"].items():
            tot = sum(int(v) for v in mb["distribution_reduced"].values())
            if tot != expect:
                bad_n.append([n, model, "sum"])
            for k, v in mb["distribution_reduced"].items():
                if int(v) < 0:
                    bad_n.append([n, model, "negative"])
                if int(mb["distribution_full"][k]) != int(v) * (4 ** (2 * n)):
                    bad_n.append([n, model, "full-scale"])
    record("domain_size_identity_at_every_declared_n", not bad_n, {"bad": bad_n[:8]})

    # 6. Q1 verdict consistency ---------------------------------------------
    below9 = any(int(res["q1_distribution"][str(n)]["per_model"][m]
                     ["distribution_reduced"][r]) > 0
                 for n in ns for m in res["q1_distribution"][str(n)]["per_model"]
                 for r in ("7", "8"))
    record("ceiling_verdict_consistent_with_distribution",
           (res["q1_ceiling_verdict"] == "FAMILY_ARTIFACT") == below9
           and res["q1_rotation_count_is_invariant_in_the_grammar"] == (not below9),
           {"configurations_below_nine_exist": below9})
    record("terminal_consistent",
           res["terminal"] == ("QG24_PARTIAL__VARIATION_FOUND_BUT_NO_CLEAN_REGIME"
                               if below9 else
                               "QG24_CEILING_IS_STRUCTURAL__ROTATION_COUNT_"
                               "INVARIANT_IN_THE_GRAMMAR"))

    # 7. panel: predicate + seven-rotation witness ---------------------------
    bad_rows, checked_rows = [], 0
    qg21 = json.loads(QG21_RESULTS.read_text())
    base = {(r["subject"], canonical(r["matching"]), int(r["n_qubits"])):
            (r["target_pairs"], int(r["referee"]["theta_FT"]["C_DP"]))
            for r in qg21["rows"]}
    for row in res["panel"]:
        key = (row["subject"], canonical(row["matching"]), int(row["n_qubits"]))
        if key not in base:
            bad_rows.append([row["subject"], "row-not-in-qg21-receipt"])
            continue
        tp, cdp = base[key]
        n = int(row["n_qubits"])
        if cdp != int(row["r6m_theta_FT_optimum_clifford"]):
            bad_rows.append([row["subject"], "baseline-mismatch"])
        qa = pmul(tuple(tp[0][0]), tuple(tp[0][1]))
        qb = pmul(tuple(tp[1][0]), tuple(tp[1][1]))
        pred = row["predicate"]
        if bool(pred["seven_reachable_in_place"]) != (qa != (0, 0) and qb != (0, 0)):
            bad_rows.append([row["subject"], "predicate-in-place"])
        if pred["seven_reachable_factored"] is not True:
            bad_rows.append([row["subject"], "predicate-factored"])
        for model_key, wit_key in (("factored", "witness_factored"),
                                   ("in_place", "witness_in_place")):
            wit = row.get(wit_key)
            claimed = row[f"seven_rotation_min_clifford_{model_key}"]
            if wit is None:
                if claimed is not None:
                    bad_rows.append([row["subject"], model_key, "witness-missing"])
                continue
            a = tuple(wit["a"])
            bs = [tuple(b) for b in wit["b"]]
            S = tuple(wit["S"])
            centrals = [int(c) for c in wit["centrals"]]
            pairs_t = [(tuple(p[0]), tuple(p[1])) for p in tp]
            order = [pairs_t[0],
                     pairs_t[1] if int(wit["perm_b"]) == 0
                     else (pairs_t[1][1], pairs_t[1][0]),
                     pairs_t[2] if int(wit["perm_c"]) == 0
                     else (pairs_t[2][1], pairs_t[2][0])]
            cost, frames, restores = theta_ft_cost(a, bs, S, order, centrals, n)
            if cost != int(claimed):
                bad_rows.append([row["subject"], model_key, "cost", cost, claimed])
            grammar = (all(psymp(*frames[j]) == 1 for j in range(3))
                       and len({psymp(S, frames[j][0]) for j in range(3)}) == 1
                       and len({psymp(S, frames[j][1]) for j in range(3)}) == 1
                       and psymp(S, frames[0][0]) != psymp(S, frames[0][1]))
            if not grammar:
                bad_rows.append([row["subject"], model_key, "grammar"])
            _, eq, sp, comm = slot_data(frames, centrals, restores)
            rc, _ = merge_search(eq, sp, comm, model_key == "in_place")
            if rc != 7:
                bad_rows.append([row["subject"], model_key, "rotations", rc])
            price = row[f"clifford_price_{model_key}"]
            if price is not None and int(price) != int(claimed) - cdp:
                bad_rows.append([row["subject"], model_key, "price"])
        checked_rows += 1
    record("panel_witnesses_reverified_from_primitives", not bad_rows,
           {"rows": checked_rows, "bad": bad_rows[:8]})

    # 8. forecast tally ------------------------------------------------------
    panel_by = {(p["subject"], canonical(p["matching"]), int(p["n_qubits"])): p
                for p in res["panel"]}
    hits = 0
    for s in res["stage1"]["embedded"]["predictions"]:
        p = panel_by[(s["subject"], canonical(s["matching"]), int(s["n_qubits"]))]
        if (s["predicted_min_rotations_factored"] == p["min_rotations_factored"]
                and s["predicted_min_rotations_in_place"]
                == p["min_rotations_in_place"]):
            hits += 1
    fc = res["q2_regime"]["prospective_forecast"]
    record("forecast_tally_recomputes",
           hits == int(fc["hits"])
           and len(res["stage1"]["embedded"]["predictions"]) == int(fc["rows"]))
    record("G4_referee_never_called_in_stage1",
           int(fc["referee_calls_during_stage1"]) == 0)

    # 9. Q3 arithmetic -------------------------------------------------------
    q3 = res["q3_magnitude"]
    record("q3_rotation_fraction_recomputes",
           abs(q3["fraction_of_rotation_count_removed"] - 2 / 9) < 1e-12
           and int(q3["rotations_removed"])
           == int(q3["rotations_per_compilation_family_menu"])
           - int(q3["rotations_per_compilation_grammar_floor"]))
    record("authority_ceiling_not_r6",
           res["r6_authority"] is False
           and res["physical_quantum_advantage_claim"] is False
           and res["reserved_stretched_n2_accessed"] is False)

    verdict = "ACCEPT" if not failures else "REJECT"
    out = {
        "verifier": "qg24_generic_verify",
        "independent_of": ["qg24_rotation_regime", "max_r6* analyzers",
                           "orion_research_harness", "numpy"],
        "results_file": str(res_path),
        "results_sha256": sha_file(res_path),
        "terminal_under_review": res["terminal"],
        "n1_configurations_reenumerated": total,
        "declared_sizes": ns,
        "panel_rows_reverified": checked_rows,
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failures,
        "lower_bound_note": ("this verifier establishes that a seven-rotation "
                             "compilation of the stated theta_FT cost EXISTS for "
                             "every panel row, that the complete n=1 enumeration "
                             "and the domain-size identity hold, and that every "
                             "digest and arithmetic claim recomputes. That no "
                             "CHEAPER seven-rotation member exists is the exact "
                             "DP's claim and is not re-derived here."),
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QG24_GENERIC_VERIFY={verdict}")
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
