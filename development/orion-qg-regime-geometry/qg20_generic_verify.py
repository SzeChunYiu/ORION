#!/usr/bin/env python3
"""QG-20 generic verifier -- pure primitives, no analyzer imports, no NumPy.

Rebuilds, from the standard library alone and with deliberately different
internals from the checker:

  * the single-qubit Pauli algebra, from the (x, z) bit-pair representation
    I=(0,0) X=(1,0) Y=(1,1) Z=(0,1), with multiplication as componentwise XOR,
    the symplectic form as x_a z_b XOR x_b z_a, and weight as (x OR z);
  * the documented R6M and R6I DP acceptance-parity state words, assembled from
    an explicit list of bit predicates rather than a hard-coded shift expression,
    and NOT read from any production `_DELTA` array;
  * the conserved-syndrome quotient ranks under all three rewrites (R6M slotwise,
    R6M block-level, R6I block-level) by a list-based row-reduction over GF(2)
    that shares no code with the checker's dict-pivot elimination;
  * both complete local deletion domains and their exchange margins mu, by naive
    nested enumeration of every row.

It then re-derives QG-20's arithmetic from scratch:

    slack = rank - kappa for each measured family, with kappa read verbatim from
    its own committed receipt field, and compares slack against the independently
    recomputed mu -- both on the QG-6 certified ranks and on the margin-aligned
    block rewrite.

It also re-checks the honesty constraint mechanically: the receipt's authority
string and claim boundary must deny law/theorem status.

Emits exactly one decision line: QG20_GENERIC_VERIFY=ACCEPT or =REJECT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG20_RANK_KAPPA_SLACK_PROTOCOL_V1.md"
QG6 = ROOT / "research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json"
QG9V6 = ROOT / "research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"
QG18 = ROOT / "research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json"
QG15 = ROOT / "research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json"
TOKEN = "QG20_GENERIC_VERIFY="


# ------------------------------------------------------- primitives, rebuilt

XZ = ((0, 0), (1, 0), (1, 1), (0, 1))  # I, X, Y, Z as (x-bit, z-bit)
INDEX = {pair: i for i, pair in enumerate(XZ)}


def mul(a: int, b: int) -> int:
    return INDEX[(XZ[a][0] ^ XZ[b][0], XZ[a][1] ^ XZ[b][1])]


def sy(a: int, b: int) -> int:
    return (XZ[a][0] & XZ[b][1]) ^ (XZ[b][0] & XZ[a][1])


def wt(a: int) -> int:
    return 1 if (XZ[a][0] | XZ[a][1]) else 0


def f3(a: int, b: int, c: int) -> int:
    """Donor-owned all-three-blocks common-factor rule."""
    if a == b == c and a != 0:
        return 1
    return wt(a) + wt(b) + wt(c)


def gf2_rank(vectors) -> int:
    """List-based row reduction; deliberately unlike the checker's dict pivoting."""
    rows = [v for v in vectors if v]
    reduced: list[int] = []
    for v in rows:
        cur = v
        for r in reduced:
            cur = min(cur, cur ^ r)
        if cur:
            reduced.append(cur)
            reduced.sort(reverse=True)
    return len(reduced)


# ------------------------------------ documented DP state words (no _DELTA use)


def r6m_word(a0, a1, b0, b1, c0, c1, s) -> int:
    bits = [
        sy(a0, a1),
        sy(b0, b1),
        sy(c0, c1),
        sy(s, a0) ^ sy(s, b0),
        sy(s, a0) ^ sy(s, c0),
        sy(s, a1) ^ sy(s, b1),
        sy(s, a1) ^ sy(s, c1),
        sy(s, a0),
        sy(s, a1),
    ]
    word = 0
    for i, bit in enumerate(bits):
        word |= (bit & 1) << i
    return word


def r6i_word(a0, a1, b0, b1, s0, s1) -> int:
    bits = [
        sy(a0, a1),
        sy(b0, b1),
        sy(s0, a0) ^ sy(s0, b0),
        sy(s1, a0) ^ sy(s1, b0),
        sy(s0, a1) ^ sy(s0, b1),
        sy(s1, a1) ^ sy(s1, b1),
        sy(s0, a0),
        sy(s1, a0),
        sy(s0, a1),
        sy(s1, a1),
    ]
    word = 0
    for i, bit in enumerate(bits):
        word |= (bit & 1) << i
    return word


def ranks_r6m_slotwise() -> dict:
    acc = [set() for _ in range(6)]
    rows = 0
    for v in itertools.product(range(4), repeat=7):
        rows += 1
        base = r6m_word(*v)
        for slot in range(6):
            w = list(v)
            w[slot] = 0
            acc[slot].add(base ^ r6m_word(*w))
    names = ("A0", "A1", "B0", "B1", "C0", "C1")
    return {
        "rows": rows,
        "per_slot": {names[i]: gf2_rank(acc[i]) for i in range(6)},
    }


def ranks_r6m_blockwise() -> dict:
    pairs = {"A": (0, 1), "B": (2, 3), "C": (4, 5)}
    acc = {k: set() for k in pairs}
    rows = 0
    for v in itertools.product(range(4), repeat=7):
        rows += 1
        base = r6m_word(*v)
        for name, (i, j) in pairs.items():
            w = list(v)
            w[i] = 0
            w[j] = 0
            acc[name].add(base ^ r6m_word(*w))
    return {"rows": rows, "per_block": {k: gf2_rank(v) for k, v in acc.items()}}


def ranks_r6i_blockwise() -> dict:
    acc = {"A": set(), "B": set()}
    rows = 0
    for v in itertools.product(range(4), repeat=6):
        rows += 1
        base = r6i_word(*v)
        acc["A"].add(base ^ r6i_word(0, 0, v[2], v[3], v[4], v[5]))
        acc["B"].add(base ^ r6i_word(v[0], v[1], 0, 0, v[4], v[5]))
    return {"rows": rows, "per_block": {k: gf2_rank(v) for k, v in acc.items()}}


# ------------------------------------------------------------ margins, rebuilt


def mu_r6i() -> dict:
    """R6I: block frame is the rank-2 dependent triple (a, b, ab)."""
    worst = {0: None, 1: None}  # keyed by symplectic class
    rows = {0: 0, 1: 0}
    for a in range(4):
        for b in range(4):
            if a == 0 and b == 0:
                continue
            cls = sy(a, b)
            triple = (a, b, mul(a, b))
            for central in range(3):
                mult = [4, 4, 4]
                mult[central] = 2
                refund = sum(mult[k] * wt(triple[k]) for k in range(3))
                for p in itertools.product(range(4), repeat=3):
                    before = sum(wt(mul(p[k], triple[k])) for k in range(3))
                    after = sum(wt(p[k]) for k in range(3))
                    delta = (after - before) - refund
                    rows[cls] += 1
                    if worst[cls] is None or delta > worst[cls]:
                        worst[cls] = delta
    return {
        "rows_commuting": rows[0],
        "rows_anticommuting": rows[1],
        "rows_total": rows[0] + rows[1],
        "credit_commuting": -worst[0],
        "credit_anticommuting": -worst[1],
        "mu": min(-worst[0], -worst[1]),
    }


def mu_tare() -> dict:
    """R6M/TARE: two frame letters per block, Restore change scored through F3."""
    worst = {0: None, 1: None}
    rows = {0: 0, 1: 0}
    for f0 in range(4):
        for f1 in range(4):
            if f0 == 0 and f1 == 0:
                continue
            cls = sy(f0, f1)
            for slot in range(3):
                for central in (0, 1):
                    m0 = 2 if central == 0 else 4
                    m1 = 2 if central == 1 else 4
                    refund = m0 * wt(f0) + m1 * wt(f1)
                    for p0, p1, u0, v0, u1, v1 in itertools.product(range(4), repeat=6):
                        o0 = mul(p0, f0)
                        o1 = mul(p1, f1)
                        if slot == 0:
                            pen = (f3(p0, u0, v0) - f3(o0, u0, v0)) + (
                                f3(p1, u1, v1) - f3(o1, u1, v1)
                            )
                        elif slot == 1:
                            pen = (f3(u0, p0, v0) - f3(u0, o0, v0)) + (
                                f3(u1, p1, v1) - f3(u1, o1, v1)
                            )
                        else:
                            pen = (f3(u0, v0, p0) - f3(u0, v0, o0)) + (
                                f3(u1, v1, p1) - f3(u1, v1, o1)
                            )
                        delta = pen - refund
                        rows[cls] += 1
                        if worst[cls] is None or delta > worst[cls]:
                            worst[cls] = delta
    return {
        "rows_commuting": rows[0],
        "rows_anticommuting": rows[1],
        "rows_total": rows[0] + rows[1],
        "credit_commuting": -worst[0],
        "credit_anticommuting": -worst[1],
        "mu": min(-worst[0], -worst[1]),
    }


# ------------------------------------------------------------------- verify


def main() -> int:
    reasons: dict = {}
    failures: list = []

    def fail(tag, detail=None):
        failures.append({"check": tag, "detail": detail})

    if not RESULTS.exists():
        print(TOKEN + "REJECT")
        print(json.dumps({"failed": [{"check": "results_missing"}]}))
        return 1
    res = json.loads(RESULTS.read_text())

    # --- 1. protocol + source receipt binding ---------------------------
    psha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    reasons["protocol"] = {
        "path_exists": PROTOCOL.exists(),
        "sha256": psha,
        "claimed": res.get("protocol_sha256"),
        "match": psha == res.get("protocol_sha256"),
    }
    if not reasons["protocol"]["match"]:
        fail("protocol_sha256", reasons["protocol"])

    src = {
        "QG6_SYNDROME_DIMENSION_RESULTS.json": QG6,
        "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json": QG9V6,
        "QG18_TARE_KAPPA_RESULTS.json": QG18,
        "QG15_THIRD_FAMILY_RESULTS.json": QG15,
    }
    sha_check = {}
    for name, path in src.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        claimed = (res.get("receipt_sha256") or {}).get(name)
        sha_check[name] = {"actual": actual, "claimed": claimed, "match": actual == claimed}
        if actual != claimed:
            fail("receipt_sha256", {name: sha_check[name]})
    reasons["source_receipt_sha256"] = sha_check

    qg6 = json.loads(QG6.read_text())
    qg9 = json.loads(QG9V6.read_text())
    qg18 = json.loads(QG18.read_text())
    qg15 = json.loads(QG15.read_text())

    # --- 2. independently recomputed ranks ------------------------------
    rm = ranks_r6m_slotwise()
    rb = ranks_r6m_blockwise()
    ri = ranks_r6i_blockwise()
    reasons["ranks"] = {
        "r6m_slotwise": rm,
        "r6m_blockwise": rb,
        "r6i_blockwise": ri,
    }
    if rm["rows"] != 4 ** 7 or rb["rows"] != 4 ** 7 or ri["rows"] != 4 ** 6:
        fail("rank_domain_incomplete", reasons["ranks"])
    r6m_rank = set(rm["per_slot"].values())
    r6i_rank = set(ri["per_block"].values())
    r6m_block_rank = set(rb["per_block"].values())
    if len(r6m_rank) != 1 or len(r6i_rank) != 1 or len(r6m_block_rank) != 1:
        fail("rank_not_uniform", reasons["ranks"])
    r6m_rank = r6m_rank.pop()
    r6i_rank = r6i_rank.pop()
    r6m_block_rank = r6m_block_rank.pop()

    # These must equal the QG-6 committed certified ranks.
    if r6m_rank != qg6["r6m"]["auto_dimension"]:
        fail("r6m_rank_vs_qg6", [r6m_rank, qg6["r6m"]["auto_dimension"]])
    if r6i_rank != qg6["r6i"]["auto_dimension"]:
        fail("r6i_rank_vs_qg6", [r6i_rank, qg6["r6i"]["auto_dimension"]])

    # --- 3. independently recomputed margins ----------------------------
    m_i = mu_r6i()
    m_t = mu_tare()
    reasons["margins"] = {"R6I": m_i, "R6M_TARE": m_t}
    if m_i["rows_total"] != 2880:
        fail("r6i_margin_domain", m_i)
    if m_t["rows_commuting"] != 221184 or m_t["rows_anticommuting"] != 147456:
        fail("tare_margin_domain", m_t)

    qg9_mu = qg9["composition"]["extra_active_column_credit_floor"]
    qg18_mu = qg18["q2_tag_relocation_transfer"]["l1_deletion_credit"]["credit_floor"]
    if m_i["mu"] != qg9_mu:
        fail("r6i_mu_vs_qg9v6", [m_i["mu"], qg9_mu])
    if m_t["mu"] != qg18_mu:
        fail("tare_mu_vs_qg18", [m_t["mu"], qg18_mu])

    # --- 4. kappa, two-sided, verbatim ----------------------------------
    kappa = {
        "R6I": qg9["intrinsic_support_number"],
        "R6M_TARE": qg18["intrinsic_support_number"],
    }
    two_sided = {
        "R6I": qg9.get("support_bound") == 1 and qg9.get("support0_infeasible") is True,
        "R6M_TARE": qg18.get("kappa_interval") == [2, 2],
    }
    reasons["kappa"] = {"values": kappa, "two_sided": two_sided}
    if not all(two_sided.values()):
        fail("kappa_not_two_sided", two_sided)

    # --- 5. the slack arithmetic, both rewrites -------------------------
    certified_rank = {"R6I": r6i_rank, "R6M_TARE": r6m_rank}
    aligned_rank = {"R6I": r6i_rank, "R6M_TARE": r6m_block_rank}
    mu_val = {"R6I": m_i["mu"], "R6M_TARE": m_t["mu"]}

    def build(rank_map):
        out = {}
        for fam in ("R6I", "R6M_TARE"):
            slack = rank_map[fam] - kappa[fam]
            out[fam] = {
                "rank": rank_map[fam],
                "kappa": kappa[fam],
                "slack": slack,
                "mu": mu_val[fam],
                "slack_equals_mu": slack == mu_val[fam],
            }
        return out

    cert_table = build(certified_rank)
    aligned_table = build(aligned_rank)
    reasons["independent_slack_table_certified"] = cert_table
    reasons["independent_slack_table_margin_aligned"] = aligned_table
    cert_holds = all(v["slack_equals_mu"] for v in cert_table.values())
    aligned_holds = all(v["slack_equals_mu"] for v in aligned_table.values())

    # cross-check against the receipt's own Q1 table, row for row
    claimed_rows = {r["family"]: r for r in res.get("q1_slack_table", [])}
    row_match = {}
    for fam, mine in cert_table.items():
        c = claimed_rows.get(fam)
        row_match[fam] = bool(
            c
            and c["rank"] == mine["rank"]
            and c["kappa"] == mine["kappa"]
            and c["slack"] == mine["slack"]
            and c["mu"] == mine["mu"]
            and c["slack_equals_mu"] == mine["slack_equals_mu"]
        )
        if not row_match[fam]:
            fail("q1_row_mismatch", {fam: [c, mine]})
    reasons["q1_row_match"] = row_match

    if res.get("q2_relation", {}).get("relation_holds_on_measured_families") != cert_holds:
        fail("relation_flag_mismatch", cert_holds)
    aligned_claim = (
        res.get("q2_relation", {}).get("rewrite_dependence", {})
        .get("relation_holds_under_aligned_rewrite")
    )
    if aligned_claim != aligned_holds:
        fail("aligned_relation_flag_mismatch", [aligned_claim, aligned_holds])
    diag_claim = res.get("rewrite_alignment_diagnostic", {}).get(
        "block_level_auto_dimension"
    )
    if diag_claim != r6m_block_rank:
        fail("aligned_rank_mismatch", [diag_claim, r6m_block_rank])

    # --- 6. Q3: StabPrep really has no transition table / frame split ----
    q3 = res.get("q3_third_family", {})
    stab_ok = (
        q3.get("derivable_cheaply") is False
        and q3.get("first_failing_criterion") == "T1"
        and "Dijkstra" in str(qg15.get("family", {}).get("referee", ""))
        and set(qg15.get("gate_costs", {}).keys()) == {"H", "S", "SDG", "CNOT"}
    )
    reasons["q3"] = {
        "receipt_verdict": q3.get("verdict"),
        "first_failing_criterion": q3.get("first_failing_criterion"),
        "qg15_referee": qg15.get("family", {}).get("referee"),
        "qg15_gate_costs": qg15.get("gate_costs"),
        "consistent": stab_ok,
    }
    if not stab_ok:
        fail("q3_inconsistent", reasons["q3"])

    # --- 7. terminal selection rule, re-applied --------------------------
    expected_terminal = (
        "QG20_SLACK_MEASURED__NO_RELATION"
        if not cert_holds
        else (
            "QG20_SLACK_CHARACTERIZED__MARGIN_RELATION_HOLDS"
            if q3.get("derivable_cheaply")
            else "QG20_PARTIAL__THIRD_FAMILY_NOT_DERIVABLE"
        )
    )
    reasons["terminal"] = {
        "claimed": res.get("terminal"),
        "recomputed": expected_terminal,
        "match": res.get("terminal") == expected_terminal,
    }
    if not reasons["terminal"]["match"]:
        fail("terminal_mismatch", reasons["terminal"])

    # --- 8. honesty constraint, mechanically ------------------------------
    auth = str(res.get("authority", ""))
    cb = json.dumps(res.get("claim_boundary", {}))
    honesty = {
        "authority_says_candidate_relation": "CANDIDATE_RELATION" in auth,
        "authority_says_two_points": "TWO_POINTS" in auth,
        "authority_denies_law": "NOT_A_LAW" in auth,
        "authority_has_no_bare_theorem_claim": "THEOREM" not in auth,
        "authority_not_r6": "NOT_R6" in auth,
        "authority_discloses_rewrite_dependence": "MARGIN_ALIGNED" in auth
        or "REWRITE" in auth,
        "claim_boundary_says_coincidence": "COINCIDENCE" in cb.upper(),
        "claim_boundary_lists_alternatives": len(
            res.get("claim_boundary", {}).get(
                "alternative_accounts_not_excluded_by_the_data", []
            )
        )
        >= 2,
    }
    reasons["honesty_constraint"] = honesty
    if not all(honesty.values()):
        fail("honesty_constraint", honesty)

    # --- 9. ceilings and gates --------------------------------------------
    ceilings = {
        "novelty_credit_false": res.get("novelty_credit") is False,
        "donor_novelty_credit_false": res.get("donor_novelty_credit") is False,
        "r6_authority_false": res.get("r6_authority") is False,
        "no_physical_advantage_claim": res.get("physical_quantum_advantage_claim")
        is False,
        "no_chemistry_read": res.get("chemistry_sources_read") is False,
        "protected_not_read": res.get("protected_subject_read") is False,
        "no_network": res.get("network_access") is False,
        "all_gates_true": all(bool(v) for v in (res.get("gates") or {}).values()),
    }
    reasons["ceilings"] = ceilings
    if not all(ceilings.values()):
        fail("ceilings", ceilings)

    # --- 10. result digest reproducibility ---------------------------------
    body = {k: v for k, v in res.items() if k != "result_digest"}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    reasons["result_digest"] = {
        "claimed": res.get("result_digest"),
        "recomputed": digest,
        "match": digest == res.get("result_digest"),
    }
    if digest != res.get("result_digest"):
        fail("result_digest", reasons["result_digest"])

    ok = not failures
    reasons["failed"] = failures
    reasons["conclusion"] = (
        "Independently rebuilt from pure primitives: R6I rank {} kappa {} slack {} mu {}; "
        "R6M/TARE rank {} kappa {} slack {} mu {}. slack == mu on both under the QG-6 "
        "certified ranks; under the margin-aligned block rewrite the R6M/TARE rank is {} "
        "and the relation FAILS ({}). The two-point agreement is a coincidence, not a law."
    ).format(
        cert_table["R6I"]["rank"],
        cert_table["R6I"]["kappa"],
        cert_table["R6I"]["slack"],
        cert_table["R6I"]["mu"],
        cert_table["R6M_TARE"]["rank"],
        cert_table["R6M_TARE"]["kappa"],
        cert_table["R6M_TARE"]["slack"],
        cert_table["R6M_TARE"]["mu"],
        r6m_block_rank,
        aligned_holds,
    ) if ok else "verification failed; see the recorded reasons"

    print(TOKEN + ("ACCEPT" if ok else "REJECT"))
    print(json.dumps(reasons, sort_keys=True, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
