#!/usr/bin/env python3
"""QG-7b generic verifier — independent primitive re-derivation.

Rebuilds everything it checks from primitive operations on symplectic Pauli
keys: NO import of the analyzer, of the committed orion-q machinery, or of
any of their tables. Reads only the two receipt JSON files (data, not code)
and the frozen protocol file (for its hash).

Checks:
  V1  protocol hash binding (RESULTS.protocol_sha256 == sha256 of the frozen
      protocol file) and schema/terminal/authority vocabulary.
  V2  Panel W: all 64 rows bound bit-exactly to the committed QG-7 receipt's
      fourth-regime witnesses; for every row the serialized B'' witness is
      re-verified from primitives (frozen shape predicate, grammar labels,
      pairwise anticommutation, primitive cost recomputation with the
      first-principles F3 table) and must equal C_DP == C_Dxx == f_Bsecond,
      with the fourth-regime gap C_Dxx < min(C_Dplus, f_Bprime) intact.
  V3  count consistency: panel sums, coverage accounting, exact/pinched
      partition, expected panel sizes (64 / 740 / 9261 / 240 / Panel X sum).
  V4  fifth candidates / contradictions / hard failures: primitive numeric
      re-checks of every serialized entry (and emptiness when the closes
      terminal is claimed).
  V5  terminal + authority re-derivation from the frozen selection rules.
  V6  result digest recomputation (canonical JSON minus timing and digest).
  V7  verification_sample sandwich checks.

Prints ACCEPT or REJECT (with reasons) and exits 0/1.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = REPO / "research/extensions/orion-qg/QG7B_HYBRID_FAMILY_RESULTS.json"
QG7_RESULTS = (
    REPO / "research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json")
PROTOCOL = HERE / "QG7B_HYBRID_FAMILY_PROTOCOL_V1.md"

CLOSES_TERMINAL = "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS"
FIFTH_TERMINAL = "QG7B_FIFTH_CONFIGURATION_FOUND"
CANNOT_TERMINAL = "QG7B_CANNOT_CHECK"
AUTH = {
    CLOSES_TERMINAL: (
        "ORIONQG_QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS__"
        "WEIGHT2_TAG_PHANTOM_BORROW_BSECOND__NOT_R6"),
    FIFTH_TERMINAL: (
        "ORIONQG_QG7B_FIFTH_CONFIGURATION_FOUND__"
        "HOSTILE_SEARCH_WITNESS_REFEREE_CONFIRMED__NOT_R6"),
    CANNOT_TERMINAL: (
        "ORIONQG_QG7B_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6"),
}

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


# ---- primitive symplectic Pauli algebra (built from scratch) -----------------

def popcount(v: int) -> int:
    return bin(v).count("1")


def wt(key) -> int:
    return popcount(key[0] | key[1])


def symp(a, b) -> int:
    return (popcount(a[0] & b[1]) + popcount(a[1] & b[0])) % 2


def mul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def letter(key, q: int) -> int:
    xb = (key[0] >> q) & 1
    zb = (key[1] >> q) & 1
    return {(0, 0): 0, (1, 0): 1, (1, 1): 2, (0, 1): 3}[(xb, zb)]


def letter_key(v: int, q: int):
    xb, zb = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}[v]
    return (xb << q, zb << q)


def f3(a: int, b: int, c: int) -> int:
    if a == b == c != 0:
        return 1
    return (a != 0) + (b != 0) + (c != 0)


def config_cost_primitive(t6, frames6, s, n: int) -> int:
    """Frozen-grammar configuration cost with centrals (1,1,1), rebuilt from
    first principles: raw = sum_j 4*wt(f0)+2*wt(f1) + 2*wt(s) - 18 + branch
    F3 sums of the frame-multiplied targets."""
    raw = 0
    for j in range(3):
        raw += 4 * wt(frames6[2 * j]) + 2 * wt(frames6[2 * j + 1])
    raw += 2 * wt(s)
    tt = [mul(t6[i], frames6[i]) for i in range(6)]
    f3sum = 0
    for k in (0, 1):
        for q in range(n):
            f3sum += f3(letter(tt[k], q), letter(tt[2 + k], q),
                        letter(tt[4 + k], q))
    return raw - 18 + f3sum


def check_bsecond_witness(target_pairs, n: int, wit) -> str | None:
    """Primitive re-derivation of the frozen B'' witness predicate.
    Returns None on success, else a reason string."""
    qa, qb = int(wit["q_ta"]), int(wit["q_tb"])
    va, vb = int(wit["v_a"]), int(wit["v_b"])
    if qa == qb or not (0 <= qa < n and 0 <= qb < n):
        return "tag qubits not distinct/in range"
    if va not in (1, 2, 3) or vb not in (1, 2, 3):
        return "tag letters out of range"
    s = mul(letter_key(va, qa), letter_key(vb, qb))
    if wt(s) != 2:
        return "tag weight != 2"
    tag_letters = {qa: va, qb: vb}
    frames6, t6 = [], []
    any_phantom = False
    tp = [(tuple(a), tuple(b)) for a, b in target_pairs]
    for j, blk in enumerate(wit["blocks"]):
        fc = tuple(blk["frame_comm"])
        fa = tuple(blk["frame_anti"])
        sigma = int(blk["sigma"])
        frames6.extend([fc, fa])
        t6.extend([tp[j][sigma], tp[j][1 - sigma]])
        mc = fc[0] | fc[1]
        ma = fa[0] | fa[1]
        if blk["kind"] == "anchored":
            if wt(fc) != 1 or wt(fa) != 1 or mc != ma:
                return "anchored shape broken"
            q = mc.bit_length() - 1
            if q not in tag_letters or fc != letter_key(tag_letters[q], q):
                return "anchored comm frame is not the tag letter"
            if int(blk["extra"]) != 0:
                return "anchored extra != 0"
        elif blk["kind"] == "phantom":
            any_phantom = True
            if wt(fc) != 1 or wt(fa) != 2:
                return "phantom support shape broken"
            if ((mc >> qa) & 1) or ((mc >> qb) & 1):
                return "phantom home on tag support"
            if not (((ma >> qa) & 1) or ((ma >> qb) & 1)):
                return "phantom anti frame does not borrow at a tag qubit"
            if int(blk["extra"]) != 2:
                return "phantom extra != 2"
        else:
            return "unknown block kind"
    if not any_phantom:
        return "all-anchored corner (not a B'' member)"
    # grammar acceptance: pairwise anticommutation + common distinct labels
    for j in range(3):
        if symp(frames6[2 * j], frames6[2 * j + 1]) != 1:
            return "frame pair does not anticommute"
    for j in range(3):
        if symp(s, frames6[2 * j]) != 0:
            return "comm frame label != 0"
        if symp(s, frames6[2 * j + 1]) != 1:
            return "anti frame label != 1"
    if any(f == (0, 0) for f in frames6):
        return "identity frame"
    cost = config_cost_primitive(t6, frames6, s, n)
    if cost != int(wit["value"]):
        return f"primitive cost {cost} != witness value {wit['value']}"
    return None


# ---- load ---------------------------------------------------------------------

def main() -> int:
    res = json.loads(RESULTS.read_text())
    qg7 = json.loads(QG7_RESULTS.read_text())

    # V1: protocol binding + vocabulary
    proto_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if res.get("protocol_sha256") != proto_sha:
        fail("V1: protocol_sha256 does not match the frozen protocol file")
    if res.get("schema") != "ORIONQG.QG7B.HybridFamily.v1":
        fail("V1: unexpected schema")
    terminal = res.get("terminal")
    if terminal not in AUTH:
        fail(f"V1: unknown terminal {terminal}")
    elif res.get("authority") != AUTH[terminal]:
        fail("V1: authority string does not match the terminal")
    if "NOT_R6" not in str(res.get("authority")):
        fail("V1: authority ceiling violated")
    for flag in ("novelty_credit", "donor_novelty_credit", "r6_authority",
                 "reserved_stretched_n2_accessed", "chemistry_data_read"):
        if res.get(flag) is not False:
            fail(f"V1: flag {flag} is not False")

    q2 = res["q2"]
    w = q2["panel_w_witnesses"]
    h = q2["panel_h_qg7_reevaluated"]
    s_p = q2["panel_s_structured_n2"]
    f_p = q2["panel_f_fresh_seeded"]
    x_p = q2["panel_x_adversarial"]

    # V2: Panel W primitive re-verification + QG-7 receipt binding
    rec_wits = qg7["arm1_hostile_search"]["fourth_regime_candidates_verbatim"]
    if len(rec_wits) != 64 or len(w["rows"]) != 64:
        fail("V2: witness count != 64")
    for row, rec in zip(w["rows"], rec_wits):
        i = row["index"]
        if (row["panel"] != rec["panel"]
                or row["local_index"] != rec["local_index"]
                or row["target_pairs"] != rec["target_pairs"]
                or row["C_DP"] != rec["C_DP"]
                or row["C_Dxx"] != rec["C_Dxx"]
                or row["C_Dplus"] != rec["C_Dplus"]
                or row["f_Bprime"] != rec["f_Bprime"]):
            fail(f"V2: row {i} not bound to the QG-7 receipt")
            continue
        n = int(row["panel"].rsplit("_n", 1)[1])
        if row["C_DP"] != row["C_Dxx"]:
            fail(f"V2: row {i} violates C_DP == C_Dxx")
        if not (row["C_Dxx"] < min(row["C_Dplus"], row["f_Bprime"])):
            fail(f"V2: row {i} is not fourth-regime")
        if row["covered_by_bsecond"]:
            if row["f_Bsecond"] != row["C_DP"]:
                fail(f"V2: row {i} covered flag but f_Bsecond != C_DP")
            reason = check_bsecond_witness(
                row["target_pairs"], n, row["bsecond_witness_verbatim"])
            if reason is not None:
                fail(f"V2: row {i} B'' witness rejected: {reason}")
            elif int(row["bsecond_witness_verbatim"]["value"]) != row["C_DP"]:
                fail(f"V2: row {i} witness value != C_DP")

    # V3: count consistency
    if w["witnesses_bound"] != 64:
        fail("V3: panel W bound count != 64")
    h_sum = sum(p["evaluated"] for p in h["panels"].values())
    if h_sum != h["instances_evaluated_total"] or h_sum != 740:
        fail("V3: panel H totals inconsistent or != 740")
    x_sum = sum(p["evaluated"] for p in x_p["panels"].values())
    if x_sum != x_p["instances_evaluated_total"]:
        fail("V3: panel X totals inconsistent")
    if s_p["instances"] != 9261:
        fail("V3: panel S != 9261")
    if f_p["instances"] != 240:
        fail("V3: panel F != 240")
    expected_total = 64 + h_sum + s_p["instances"] + f_p["instances"] + x_sum
    if q2["instances_total"] != expected_total:
        fail("V3: instances_total != sum of panels")
    if (q2["covered_without_bsecond"] + q2["covered_by_bsecond"]
            + q2["uncovered_total"] != q2["instances_total"]):
        fail("V3: coverage partition does not sum")
    if (q2["bsecond_exact_rows"] + q2["bsecond_pinched_rows"]
            != q2["instances_total"]):
        fail("V3: exact/pinched partition does not sum")
    for pkey, p in list(h["panels"].items()) + list(x_p["panels"].items()):
        if p["raw_scanned"] != (p["evaluated"] + p["zero_target_skipped"]
                                + p["duplicate_skipped"]):
            fail(f"V3: {pkey} raw != evaluated + skips")
        if sum(p["regime_census"].values()) != p["evaluated"]:
            fail(f"V3: {pkey} census does not sum to evaluated")

    # V4: serialized findings
    fifths = q2["fifth_candidates_verbatim"]
    if q2["fifth_configuration_confirmed_total"] > len(fifths):
        fail("V4: confirmed fifths exceed serialized fifths")
    for k, fc in enumerate(fifths):
        vals = [v for v in (fc["C_Dplus"], fc["f_Bprime"],
                            fc["f_Bsecond"]) if v is not None]
        base = fc["C_Dxx"] if fc["C_Dxx"] is not None else fc["C_DP"]
        # a fifth configuration claim requires base < min of the family values
        if not vals or base >= min(vals):
            fail(f"V4: fifth candidate {k} numeric claim inconsistent")
    if terminal == CLOSES_TERMINAL:
        if fifths or q2["uncovered_total"] != 0:
            fail("V4: closes terminal with fifths/uncovered present")
        if q2["r6s_contradictions_verbatim"] or \
                q2["hard_assertion_failures_verbatim"]:
            fail("V4: closes terminal with serialized failures")
        if not w["all_covered"]:
            fail("V4: closes terminal but panel W not all covered")
        for key, p in (("S", s_p), ("F", f_p)):
            if p["covered_count"] != p["instances"]:
                fail(f"V4: closes terminal but panel {key} not all covered")
        if h["covered_total"] != h_sum or x_p["covered_total"] != x_sum:
            fail("V4: closes terminal but H/X not all covered")

    # V5: terminal re-derivation from the frozen rules
    gates_ok = all(bool(v) for v in res["gates"].values())
    all_covered = (
        q2["uncovered_total"] == 0 and w["all_covered"]
        and s_p["covered_count"] == s_p["instances"]
        and f_p["covered_count"] == f_p["instances"]
        and h["covered_total"] == h_sum
        and x_p["covered_total"] == x_sum)
    confirmed = q2["fifth_configuration_confirmed_total"]
    total_f = q2["fifth_configuration_candidates_total"]
    if confirmed > 0 and gates_ok:
        expected_terminal = FIFTH_TERMINAL
    elif total_f > 0 or q2["r6s_contradictions_verbatim"] or not gates_ok \
            or not all_covered:
        expected_terminal = CANNOT_TERMINAL
    else:
        expected_terminal = CLOSES_TERMINAL
    if terminal != expected_terminal:
        fail(f"V5: terminal {terminal} != re-derived {expected_terminal}")

    # V6: digest recomputation
    body = {k: v for k, v in res.items()
            if k not in ("timing", "result_digest")}
    digest = hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()
    if digest != res.get("result_digest"):
        fail("V6: result_digest does not recompute")

    # V7: verification-sample sandwiches
    for row in res["verification_sample"]:
        c_dp = row["C_DP"]
        if row.get("C_Dxx") is not None:
            if not (c_dp <= row["C_Dxx"] <= row["C_Dplus"]):
                fail(f"V7: sample sandwich broken at {row['panel']}"
                     f"/{row['local_index']}")
        if row.get("f_Bsecond") is not None and row["f_Bsecond"] < c_dp:
            fail(f"V7: sample B'' soundness broken at {row['panel']}"
                 f"/{row['local_index']}")
        if row.get("f_Bprime") is not None and row["f_Bprime"] < c_dp:
            fail(f"V7: sample B' soundness broken at {row['panel']}"
                 f"/{row['local_index']}")

    if failures:
        print("REJECT")
        for msg in failures:
            print("  -", msg)
        return 1
    print("ACCEPT")
    print(f"  terminal={terminal}")
    print(f"  panel_w_covered={w['covered_count']}/64  "
          f"instances_total={q2['instances_total']}  "
          f"uncovered={q2['uncovered_total']}  "
          f"fifths={total_f} (confirmed {confirmed})")
    print(f"  digest={res['result_digest']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
