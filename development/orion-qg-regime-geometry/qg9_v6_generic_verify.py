#!/usr/bin/env python3
"""Independent generic-ORION verifier for QG-9 V6 support-1 theorem.

No production R6I/P10 algebra is imported.  Phase-free Paulis are rebuilt as
F_2^2 vectors and every finite lemma domain is recomputed independently.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "artifacts/orion-qg-qg9-v6-support1-normalization.json"
PARENT = ROOT / "development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG9_V6_SUPPORT1_NORMALIZATION_PROTOCOL_V1.md"
OUT = ROOT / "artifacts/orion-qg-qg9-v6-generic-verification.json"
TOKEN = "ORIONQG_QG9_V6_GENERIC="

VEC = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
INV = {v: k for k, v in VEC.items()}
BASES = tuple((a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b)


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def mul(a: int, b: int) -> int:
    av, bv = VEC[a], VEC[b]
    return INV[(av[0] ^ bv[0], av[1] ^ bv[1])]


def symp(a: int, b: int) -> int:
    av, bv = VEC[a], VEC[b]
    return (av[0] * bv[1] + av[1] * bv[0]) & 1


def wt(a: int) -> int:
    return int(a != 0)


def frame(a: int, b: int):
    return a, b, mul(a, b)


def raw_frame(a: int, b: int, central: int) -> int:
    r = frame(a, b)
    m = [4, 4, 4]
    m[central] = 2
    return sum(m[k] * wt(r[k]) for k in range(3))


def restore(p, a: int, b: int) -> int:
    r = frame(a, b)
    return sum(wt(mul(p[k], r[k])) for k in range(3))


def deletion_domain():
    mx = {"commuting": -999, "anticommuting": -999}
    n = 0
    for a, b in itertools.product(range(4), repeat=2):
        if a == b == 0:
            continue
        cls = "anticommuting" if symp(a, b) else "commuting"
        for p in itertools.product(range(4), repeat=3):
            for c in range(3):
                d = restore(p, 0, 0) - (raw_frame(a, b, c) + restore(p, a, b))
                mx[cls] = max(mx[cls], d)
                n += 1
    return n, mx


def alignment_domain():
    n = 0
    mx = -999
    frame_ok = True
    for a in BASES:
        for b in BASES:
            for p in itertools.product(range(4), repeat=3):
                for c in range(3):
                    frame_ok &= raw_frame(*a, c) == 10 and raw_frame(*b, c) == 10
                    mx = max(mx, restore(p, *b) - restore(p, *a))
                    n += 1
    return n, mx, frame_ok


def labels(s0: int, s1: int, basis):
    return 2 * symp(s0, basis[0]) + symp(s1, basis[0]), 2 * symp(s0, basis[1]) + symp(s1, basis[1])


def tag_domains():
    dual_ok = True
    dual_count = 0
    for b in BASES:
        rows = [(s0, s1) for s0, s1 in itertools.product(range(4), repeat=2) if labels(s0, s1, b) == (1, 2)]
        dual_ok &= len(rows) == 1 and rows[0][0] != 0 and rows[0][1] != 0
        dual_count += len(rows)

    rig_n = 0
    rig_bad = 0
    for A in BASES:
        for B in BASES:
            for s0, s1 in itertools.product(range(4), repeat=2):
                rig_n += 1
                la, lb = labels(s0, s1, A), labels(s0, s1, B)
                if la == lb and la[0] in (1, 2, 3) and la[1] in (1, 2, 3) and la[0] != la[1] and A != B:
                    rig_bad += 1

    twoq = tuple(itertools.product(range(4), repeat=2))
    dist_n = 0
    minima = []
    for A in BASES:
        for B in BASES:
            best = 999
            for s0 in twoq:
                for s1 in twoq:
                    dist_n += 1
                    la = labels(s0[0], s1[0], A)
                    lb = labels(s0[1], s1[1], B)
                    if la != lb or la[0] not in (1, 2, 3) or la[1] not in (1, 2, 3) or la[0] == la[1]:
                        continue
                    best = min(best, 2 * (sum(x != 0 for x in s0) + sum(x != 0 for x in s1)))
            minima.append(best)

    label_nonzero = True
    label_count = 0
    for c0 in (1, 2, 3):
        for c1 in (1, 2, 3):
            if c0 == c1:
                continue
            label_count += 1
            u = ((c0 >> 1) & 1, (c1 >> 1) & 1)
            v = (c0 & 1, c1 & 1)
            label_nonzero &= u != (0, 0) and v != (0, 0)
    return {
        "dual_ok": dual_ok and dual_count == 6,
        "rigidity_domain": rig_n,
        "rigidity_bad": rig_bad,
        "distinct_domain": dist_n,
        "distinct_minima": sorted(set(minima)),
        "label_count": label_count,
        "label_rows_nonzero": label_nonzero,
    }


def main() -> int:
    a = json.loads(RESULT.read_text())
    u = dict(a)
    observed = u.pop("result_digest", None)
    digest_ok = observed == hashlib.sha256(canonical(u).encode()).hexdigest()
    dn, dm = deletion_domain()
    an, am, af = alignment_domain()
    tags = tag_domains()
    comp = a.get("composition_audit", {})
    checks = {
        "schema": a.get("schema") == "ORION.QG.QG9.V6.Support1Normalization.v1",
        "result_digest": digest_ok,
        "protocol_hash": a.get("protocol_sha256") == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "parent_support2": json.loads(PARENT.read_text()).get("terminal") == "QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED",
        "deletion_domain_2880": dn == 2880 and a["deletion_lemma"]["domain_size"] == dn,
        "deletion_maxima": dm == {"commuting": -4, "anticommuting": -7} and a["deletion_lemma"]["max_delta"] == dm,
        "alignment_domain_6912": an == 6912 and a["core_alignment_lemma"]["domain_size"] == an,
        "alignment_max3": am == 3 and af and a["core_alignment_lemma"]["max_restore_objective_increase"] == 3,
        "dual_tag": tags["dual_ok"] and a["tag_lemmas"]["canonical_dual_all_nonzero"] is True,
        "same_core_rigidity": tags["rigidity_domain"] == 576 and tags["rigidity_bad"] == 0 and a["tag_lemmas"]["same_qubit_rigidity"]["holds"] is True,
        "distinct_tag_min8": tags["distinct_domain"] == 9216 and tags["distinct_minima"] == [8] and a["tag_lemmas"]["distinct_qubit_tag"]["all_minima_8"] is True,
        "old_tag_floor4": tags["label_count"] == 6 and tags["label_rows_nonzero"] and a["tag_lemmas"]["feasible_label_rows"]["original_tag_cost_floor"] == 4,
        "composition_credit_vs_alignment": comp.get("extra_credit_floor") == 4 and comp.get("alignment_ceiling") == 3 and comp.get("credit_strictly_exceeds_alignment") is True,
        "composition_distinct": comp.get("distinct_non_support_case_closes") is True and comp.get("distinct_both_support1_case_closes") is True,
        "composition_same": comp.get("same_core_tag_nonincrease") is True and comp.get("same_core_alignment_paid") is True and comp.get("same_core_support1_rigidity") is True,
        "support0_infeasible": comp.get("support0_infeasible") is True,
        "stress_no_counterexample": a.get("stress", {}).get("all_pass") is True,
        "authority_ceiling": a.get("new_theorem_authority") is False and a.get("novelty_authority") is False and a.get("physical_quantum_advantage_claim") is False,
    }
    positive = a.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED"
    decision = "ACCEPT_SUPPORT1_THEOREM" if positive and all(checks.values()) else "REJECT"
    out = {
        "schema": "ORION.QG.QG9.V6.GenericVerification.v1",
        "issue": "SzeChunYiu/ORION#807",
        "decision": decision,
        "checks": checks,
        "all_checks": all(checks.values()),
        "independent_domains": {
            "deletion": dn,
            "alignment": an,
            "same_core_tag": tags["rigidity_domain"],
            "distinct_core_tag": tags["distinct_domain"],
        },
        "terminal": a.get("terminal"),
        "support1_authority": False,
        "novelty_authority": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
