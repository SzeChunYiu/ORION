#!/usr/bin/env python3
"""QG-21 generic verifier — from primitives, no analyzer import.

Independently re-derives, from the serialized QG-21 artifacts alone:

1. the staging digest (sha256 of the canonical staged predictions) and its
   agreement with the digest recorded in the receipt;
2. the donor cost C_R6L of every real row under every frozen objective, by a
   self-contained re-implementation of the weight-one TARE-M2 shared-Tag donor
   grammar and the all-three Restore factor rule;
3. every claimed strict improvement: the serialized frame / Tag / Restore
   assignment is re-checked against the grammar's constraints (per-block frame
   anticommutation, one shared Tag with a single distinct label pattern across
   all three blocks, Restore = target x frame) and its cost is recomputed from
   scratch under the row's objective weights, then compared with the claimed
   referee optimum and the claimed improvement delta;
4. the internal consistency of every donor-exact claim (referee optimum equals
   the independently recomputed donor cost).

Deliberately imports NO QG-21 / QG-2 / R6 analyzer code and no numpy: all Pauli
algebra below is written from the binary symplectic definitions. What this
verifier can establish from primitives is every UPPER bound (a compilation of
cost c exists) and every arithmetic claim; the LOWER bound (that no cheaper
member of the grammar exists) is the exact DP referee's claim and is reported
as such, not silently absorbed.

Usage: qg21_generic_verify.py [results.json] [stage1.json]
Exit code 0 on ACCEPT, 1 on REJECT.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_RESULTS = REPO / "research/extensions/orion-qg/QG21_FT_CHEMISTRY_RESULTS.json"
DEFAULT_STAGE1 = REPO / "research/extensions/orion-qg/QG21_STAGE1_PREDICTIONS.json"

# ---- binary symplectic Pauli primitives (self-contained) -------------------
# A Pauli is (x, z), two n-bit masks; letter at qubit q is (x>>q & 1, z>>q & 1)
# with I=(0,0), X=(1,0), Y=(1,1), Z=(0,1).


def pmul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def wt(a):
    return bin(a[0] | a[1]).count("1")


def symp(a, b):
    return (bin(a[0] & b[1]).count("1") + bin(a[1] & b[0]).count("1")) & 1


def letter_key(letter, q):
    # letter 1=X, 2=Y, 3=Z
    bx, bz = {1: (1, 0), 2: (1, 1), 3: (0, 1)}[letter]
    return (bx << q, bz << q)


def local(a, q):
    return ((a[0] >> q) & 1, (a[1] >> q) & 1)


def f3_support(ta, tb, tc, n):
    """All-three common-factor rule: identical non-identity letters cost 1."""
    total = 0
    for q in range(n):
        la, lb, lc = local(ta, q), local(tb, q), local(tc, q)
        if la != (0, 0) and la == lb == lc:
            total += 1
        else:
            total += sum(1 for x in (la, lb, lc) if x != (0, 0))
    return total


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


# ---- independent donor family (weight-one M2, one shared Tag) --------------

def donor_min_restore_units(target_pairs, n):
    """s* = min factored-Restore support over the weight-one donor grammar.

    Frames are weight one at a single qubit q: R0 = v0@q, R1 = v1@q with
    v0 != v1 (they anticommute).  The minimum-weight Tag S solving
    <S,R0> = l0, <S,R1> = l1 for a distinct one-bit label pair is the weight-one
    letter v0@q (labels (0,1)) or v1@q (labels (1,0)).  Three blocks may share a
    Tag iff they agree on (S, labels).  Restore words are T_k = P_sigma(k) * R_k.
    """
    per_block = []
    for pair in target_pairs:
        options = {}
        for q in range(n):
            for v0 in (1, 2, 3):
                for v1 in (1, 2, 3):
                    if v0 == v1:
                        continue
                    r0, r1 = letter_key(v0, q), letter_key(v1, q)
                    for labels in ((0, 1), (1, 0)):
                        s = r0 if labels == (0, 1) else r1
                        if symp(s, r0) != labels[0] or symp(s, r1) != labels[1]:
                            raise AssertionError("tag solve failed")
                        for sigma in (0, 1):
                            t0 = pmul(pair[sigma], r0)
                            t1 = pmul(pair[1 - sigma], r1)
                            options.setdefault((s, labels), []).append((t0, t1))
        per_block.append(options)
    common = set(per_block[0]) & set(per_block[1]) & set(per_block[2])
    if not common:
        raise AssertionError("donor family empty")
    best = None
    for key in sorted(common):
        for t_a in per_block[0][key]:
            for t_b in per_block[1][key]:
                for t_c in per_block[2][key]:
                    units = (f3_support(t_a[0], t_b[0], t_c[0], n)
                             + f3_support(t_a[1], t_b[1], t_c[1], n))
                    if best is None or units < best:
                        best = units
    return int(best), 1  # (s*, tag weight)


def permute6(t6, perm_b, perm_c):
    a0, a1, b0, b1, c0, c1 = t6
    if perm_b:
        b0, b1 = b1, b0
    if perm_c:
        c0, c1 = c1, c0
    return (a0, a1, b0, b1, c0, c1)


def check_witness(row_targets, n, wit, weights):
    """Re-derive a serialized compilation's validity and cost from primitives."""
    problems = []
    flat = tuple(tuple(t) for pair in row_targets for t in pair)
    t6 = permute6(flat, int(wit["relative_permutation_B"]),
                  int(wit["relative_permutation_C"]))
    frames = [[tuple(v) for v in wit["R"][k]] for k in ("A", "B", "C")]
    s = tuple(wit["S"])
    centrals = [int(c) for c in wit["centrals"]]
    labels = None
    for j, (r0, r1) in enumerate(frames):
        if symp(r0, r1) != 1:
            problems.append(f"block {j}: frame branches do not anticommute")
        lab = (symp(s, r0), symp(s, r1))
        if lab[0] == lab[1]:
            problems.append(f"block {j}: Tag does not separate the two branches")
        if labels is None:
            labels = lab
        elif lab != labels:
            problems.append(f"block {j}: label pattern differs from block 0 "
                            "(the Tag is not shared)")
    restores = [[pmul(t6[2 * j + k], frames[j][k]) for j in range(3)]
                for k in (0, 1)]
    units = sum(f3_support(restores[k][0], restores[k][1], restores[k][2], n)
                for k in (0, 1))
    uanti = 0
    for j, (r0, r1) in enumerate(frames):
        w = (wt(r0), wt(r1))
        c = centrals[j]
        uanti += weights["t_nc"] * (w[1 - c] - 1) + weights["t_c"] * (w[c] - 1)
    cost = uanti + weights["t_tag"] * wt(s) + weights["t_r"] * units
    return cost, units, problems


def main(argv):
    res_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_RESULTS
    st_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_STAGE1
    res = json.loads(res_path.read_text())
    stage1 = json.loads(st_path.read_text())
    checks = {}
    failures = []

    def record(name, ok, detail=None):
        checks[name] = {"ok": bool(ok)}
        if detail is not None:
            checks[name]["detail"] = detail
        if not ok:
            failures.append(name)

    # 1. staging digest ------------------------------------------------------
    recomputed = sha256_text(canonical(stage1))
    record("stage1_digest_recomputed", recomputed == res["stage1"]["digest"],
           {"recomputed": recomputed, "receipt": res["stage1"]["digest"]})
    record("stage1_artifact_sha256",
           sha256_text(st_path.read_text()) == res["stage1"]["artifact_sha256"])
    record("stage1_referee_calls_zero",
           int(res["stage1"]["referee_calls_during_stage1"]) == 0
           and bool(res["stage1"]["referee_stub_installed"]))

    # 2. staged predictions match the receipt rows ---------------------------
    staged = {canonical([r["subject"], r["matching"]]): r for r in stage1["rows"]}
    mismatched = 0
    for row in res["rows"]:
        key = canonical([row["subject"], row["matching"]])
        st = staged.get(key)
        if st is None or canonical(st["predictions"]) != canonical(row["predictions"]):
            mismatched += 1
    record("staged_predictions_match_receipt_rows", mismatched == 0,
           {"mismatched_rows": mismatched, "staged_rows": len(staged)})

    # 3. independent donor cost on every row and objective -------------------
    objectives = {name: {k: int(v[k]) for k in ("t_nc", "t_c", "t_tag", "t_r")}
                  for name, v in res["objectives"].items()}
    donor_bad = []
    s_star_bad = []
    for row in res["rows"]:
        n = int(row["n_qubits"])
        tp = tuple(tuple(tuple(t) for t in pair) for pair in row["target_pairs"])
        s_star, tag_w = donor_min_restore_units(tp, n)
        if s_star != int(row["primitives"]["s_star"]):
            s_star_bad.append([row["subject"], row["matching"], s_star,
                               row["primitives"]["s_star"]])
        for name, w in objectives.items():
            mine = w["t_tag"] * tag_w + w["t_r"] * s_star
            claimed = int(row["predictions"][name]["C_R6L"])
            if mine != claimed:
                donor_bad.append([row["subject"], row["matching"], name, mine,
                                  claimed])
    record("independent_s_star_matches", not s_star_bad,
           {"rows_checked": len(res["rows"]), "bad": s_star_bad[:5]})
    record("independent_donor_cost_matches_all_rows_all_objectives",
           not donor_bad,
           {"checks": len(res["rows"]) * len(objectives), "bad": donor_bad[:5]})

    # 4. every claimed improvement re-derived from primitives ----------------
    imp_bad = []
    for imp in res["improvements"]:
        n = int(imp["n_qubits"])
        w = {k: int(imp["objective_weights"][k])
             for k in ("t_nc", "t_c", "t_tag", "t_r")}
        cost, units, problems = check_witness(imp["target_pairs"], n,
                                              imp["improved_compilation"], w)
        why = list(problems)
        if cost != int(imp["referee_optimal_cost"]):
            why.append(f"recomputed cost {cost} != claimed referee optimum "
                       f"{imp['referee_optimal_cost']}")
        if units != int(imp["improved_compilation"]["restore_units_factored"]):
            why.append("restore units disagree")
        donor, _ = donor_min_restore_units(
            tuple(tuple(tuple(t) for t in pair) for pair in imp["target_pairs"]), n)
        donor_cost = w["t_tag"] * 1 + w["t_r"] * donor
        if donor_cost != int(imp["donor_cost_C_R6L"]):
            why.append(f"independent donor cost {donor_cost} != claimed "
                       f"{imp['donor_cost_C_R6L']}")
        if donor_cost - cost != int(imp["delta_vs_donor"]):
            why.append("delta arithmetic disagrees")
        if donor_cost - cost <= 0:
            why.append("claimed strict improvement is not strict")
        if why:
            imp_bad.append({"subject": imp["subject"], "matching": imp["matching"],
                            "objective": imp["objective"], "problems": why})
    record("every_claimed_improvement_rederived_from_primitives", not imp_bad,
           {"improvements_checked": len(res["improvements"]),
            "bad": imp_bad[:5]})

    # 5. donor-exact claims are internally consistent ------------------------
    de_bad = []
    for row in res["rows"]:
        for name in objectives:
            ref = row["referee"][name]
            if ref["truth_regime"] == "DONOR_EXACT":
                if int(ref["C_DP"]) != int(row["predictions"][name]["C_R6L"]):
                    de_bad.append([row["subject"], row["matching"], name])
                if int(ref["delta_vs_donor"]) != 0:
                    de_bad.append([row["subject"], row["matching"], name, "delta"])
    record("donor_exact_claims_consistent", not de_bad, {"bad": de_bad[:5]})

    # 6. objective set is the frozen one -------------------------------------
    frozen = {"theta_FT": (4, 2, 2, 1), "S1": (4, 2, 4, 2), "S2": (8, 4, 2, 1),
              "S3": (2, 2, 2, 1), "O1_control": (7, 1, 4, 3)}
    ok_obj = all(
        name in objectives and tuple(objectives[name][k] for k in
                                     ("t_nc", "t_c", "t_tag", "t_r")) == vals
        for name, vals in frozen.items()) and len(objectives) == len(frozen)
    record("frozen_objective_set_unchanged", ok_obj, objectives)

    # 7. counts add up --------------------------------------------------------
    counted = sum(1 for row in res["rows"] for name in objectives
                  if row["referee"][name]["strict_improvement"])
    record("improvement_count_matches_rows",
           counted == len(res["improvements"]) == int(res["improvement_count"]),
           {"counted_from_rows": counted,
            "improvements_listed": len(res["improvements"])})
    defensible = [n for n, v in res["per_objective_summary"].items()
                  if v["derivable_from_ft_accounting"]]
    dcount = sum(1 for row in res["rows"] for name in defensible
                 if row["referee"][name]["strict_improvement"])
    record("defensible_improvement_count_matches",
           dcount == int(res["q3_magnitude"]["defensible_objective_improved_rows"]))

    verdict = "ACCEPT" if not failures else "REJECT"
    out = {
        "verifier": "qg21_generic_verify",
        "independent_of": ["qg21_ft_chemistry", "qg2_objective_robustness",
                           "max_r6* analyzers", "numpy"],
        "results_file": str(res_path),
        "results_sha256": sha256_text(res_path.read_text()),
        "terminal_under_review": res["terminal"],
        "rows": len(res["rows"]),
        "improvements": len(res["improvements"]),
        "checks": checks,
        "failed_checks": failures,
        "lower_bound_note": ("Optimality of each compilation (that no cheaper "
                             "member of the grammar exists) is the exact DP "
                             "referee's claim; this verifier establishes the "
                             "existence and cost of every exhibited compilation, "
                             "every donor cost, and every arithmetic claim, from "
                             "primitives."),
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QG21_GENERIC_VERIFY={verdict}")
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
