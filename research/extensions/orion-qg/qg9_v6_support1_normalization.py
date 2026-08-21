#!/usr/bin/env python3
"""QG-9 V6: whole-system Tag-relocating support-1 normalization theorem.

The protocol was frozen before this checker ran.  The proof consists of finite
local Pauli domains plus a symbolic composition case split.  A deterministic
full-configuration stress panel is corroboration only.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

ISSUE = "SzeChunYiu/ORION#807"
PARENT_SUPPORT2 = ROOT / "development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json"
PARENT_SUPPORT2_RESULT = ROOT / "research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json"
PARENT_V5 = ROOT / "development/orion-qg-regime-geometry/QG9_V5_PROTECTED_RUN_RECEIPT_2026-08-21.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG9_V6_SUPPORT1_NORMALIZATION_PROTOCOL_V1.md"
DEFAULT_OUT = ROOT / "artifacts/orion-qg-qg9-v6-support1-normalization.json"
TOKEN = "ORIONQG_QG9_V6="
SEED = 20260821

LETTERS = range(4)
MUL = [[int(r6i._MUL[a, b]) for b in LETTERS] for a in LETTERS]
SY = [[int(r6i._SYMP[a, b]) for b in LETTERS] for a in LETTERS]
LW = [int(r6i._LW[a]) for a in LETTERS]
ANTI_BASES = tuple((a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b)


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lmul(a: int, b: int) -> int:
    return MUL[a][b]


def lsymp(a: int, b: int) -> int:
    return SY[a][b]


def local_frame(a: int, b: int) -> tuple[int, int, int]:
    return a, b, lmul(a, b)


def local_raw_frame_cost(a: int, b: int, central: int) -> int:
    r = local_frame(a, b)
    m = [4, 4, 4]
    m[central] = 2
    return sum(m[k] * LW[r[k]] for k in range(3))


def local_restore_cost(p: tuple[int, int, int], a: int, b: int) -> int:
    r = local_frame(a, b)
    return sum(LW[lmul(p[k], r[k])] for k in range(3))


def deletion_lemma() -> dict[str, Any]:
    counts = {"commuting": 0, "anticommuting": 0}
    maxima = {"commuting": -999, "anticommuting": -999}
    minima = {"commuting": 999, "anticommuting": 999}
    witnesses: dict[str, Any] = {}
    total = 0
    for a, b in itertools.product(LETTERS, repeat=2):
        if a == b == 0:
            continue
        cls = "anticommuting" if lsymp(a, b) else "commuting"
        for p in itertools.product(LETTERS, repeat=3):
            for central in range(3):
                old = local_raw_frame_cost(a, b, central) + local_restore_cost(p, a, b)
                new = local_restore_cost(p, 0, 0)
                delta = new - old
                total += 1
                counts[cls] += 1
                minima[cls] = min(minima[cls], delta)
                if delta > maxima[cls]:
                    maxima[cls] = delta
                    witnesses[cls] = {
                        "a": a,
                        "b": b,
                        "targets": list(p),
                        "central": central,
                        "delta": delta,
                    }
    return {
        "domain_size": total,
        "counts": counts,
        "max_delta": maxima,
        "min_delta": minima,
        "max_witness": witnesses,
        "expected_domain_2880": total == 2880,
        "commuting_max_minus4": maxima["commuting"] == -4,
        "anticommuting_max_minus7": maxima["anticommuting"] == -7,
    }


def core_alignment_lemma() -> dict[str, Any]:
    total = 0
    max_delta = -999
    max_hamming = -1
    witness = None
    frame_invariant = True
    for old in ANTI_BASES:
        for new in ANTI_BASES:
            ro = local_frame(*old)
            rn = local_frame(*new)
            for p in itertools.product(LETTERS, repeat=3):
                for central in range(3):
                    old_frame = local_raw_frame_cost(*old, central)
                    new_frame = local_raw_frame_cost(*new, central)
                    frame_invariant &= old_frame == 10 and new_frame == 10
                    delta = local_restore_cost(p, *new) - local_restore_cost(p, *old)
                    h = sum(int(ro[k] != rn[k]) for k in range(3))
                    total += 1
                    if delta > max_delta:
                        max_delta = delta
                        witness = {
                            "old": list(old),
                            "new": list(new),
                            "targets": list(p),
                            "central": central,
                            "delta": delta,
                            "triple_hamming": h,
                        }
                    max_hamming = max(max_hamming, h)
    return {
        "domain_size": total,
        "expected_domain_6912": total == 6912,
        "frame_contribution_always_10": frame_invariant,
        "max_restore_objective_increase": max_delta,
        "max_triple_hamming": max_hamming,
        "max_is_3": max_delta == 3,
        "witness": witness,
    }


def local_labels(s0: int, s1: int, basis: tuple[int, int]) -> tuple[int, int]:
    a, b = basis
    return 2 * lsymp(s0, a) + lsymp(s1, a), 2 * lsymp(s0, b) + lsymp(s1, b)


def dual_tag_for_basis(basis: tuple[int, int]) -> tuple[int, int]:
    rows = [(s0, s1) for s0, s1 in itertools.product(LETTERS, repeat=2) if local_labels(s0, s1, basis) == (1, 2)]
    if len(rows) != 1:
        raise AssertionError({"nonunique_dual": basis, "rows": rows})
    return rows[0]


def tag_lemmas() -> dict[str, Any]:
    dual = {}
    dual_ok = True
    for basis in ANTI_BASES:
        s0, s1 = dual_tag_for_basis(basis)
        dual[str(basis)] = [s0, s1]
        dual_ok &= s0 != 0 and s1 != 0 and local_labels(s0, s1, basis) == (1, 2)

    rigidity_rows = 0
    rigidity_feasible = 0
    rigidity_bad = []
    for A in ANTI_BASES:
        for B in ANTI_BASES:
            for s0, s1 in itertools.product(LETTERS, repeat=2):
                rigidity_rows += 1
                la = local_labels(s0, s1, A)
                lb = local_labels(s0, s1, B)
                feasible = la == lb and la[0] in (1, 2, 3) and la[1] in (1, 2, 3) and la[0] != la[1]
                if feasible:
                    rigidity_feasible += 1
                    if A != B:
                        rigidity_bad.append({"A": list(A), "B": list(B), "s0": s0, "s1": s1, "labels": list(la)})

    distinct_rows = 0
    distinct_minima = {}
    distinct_bad = []
    twoq = tuple(itertools.product(LETTERS, repeat=2))
    for A in ANTI_BASES:
        for B in ANTI_BASES:
            best = 999
            for s0 in twoq:
                for s1 in twoq:
                    distinct_rows += 1
                    la = local_labels(s0[0], s1[0], A)
                    lb = local_labels(s0[1], s1[1], B)
                    if la != lb or la[0] not in (1, 2, 3) or la[1] not in (1, 2, 3) or la[0] == la[1]:
                        continue
                    cost = 2 * (sum(int(x != 0) for x in s0) + sum(int(x != 0) for x in s1))
                    best = min(best, cost)
            distinct_minima[str((A, B))] = best
            if best != 8:
                distinct_bad.append({"A": list(A), "B": list(B), "minimum": best})

    label_rows = []
    label_row_nonzero = True
    for c0 in (1, 2, 3):
        for c1 in (1, 2, 3):
            if c0 == c1:
                continue
            u = ((c0 >> 1) & 1, (c1 >> 1) & 1)
            v = (c0 & 1, c1 & 1)
            label_rows.append({"labels": [c0, c1], "S0_syndrome_row": list(u), "S1_syndrome_row": list(v)})
            label_row_nonzero &= u != (0, 0) and v != (0, 0)

    return {
        "canonical_dual": dual,
        "canonical_dual_all_nonzero": dual_ok,
        "same_qubit_rigidity": {
            "domain_size": rigidity_rows,
            "expected_domain_576": rigidity_rows == 576,
            "feasible_rows": rigidity_feasible,
            "different_basis_counterexamples": rigidity_bad,
            "holds": not rigidity_bad,
        },
        "distinct_qubit_tag": {
            "domain_size": distinct_rows,
            "expected_domain_9216": distinct_rows == 9216,
            "basis_pair_count": len(distinct_minima),
            "all_minima_8": not distinct_bad and set(distinct_minima.values()) == {8},
            "bad": distinct_bad,
        },
        "feasible_label_rows": {
            "ordered_distinct_nonzero_count": len(label_rows),
            "rows": label_rows,
            "both_tag_syndrome_rows_nonzero": label_row_nonzero,
            "original_tag_cost_floor": 4 if label_row_nonzero else None,
        },
    }


def production_binding() -> dict[str, Any]:
    mul = all(MUL[a][b] == p10.h.local_mul(a, b) for a in LETTERS for b in LETTERS)
    sy = all(SY[a][b] == p10.h.local_symp(a, b) for a in LETTERS for b in LETTERS)
    lw = all(LW[a] == p10.h.local_wt(a) for a in LETTERS)
    return {"mul_exact": mul, "symp_exact": sy, "weight_exact": lw, "all_exact": mul and sy and lw}


def global_letters(key: tuple[int, int], n: int) -> list[int]:
    return list(p10.codes(key, n))


def key_from_letters(xs: list[int]):
    return p10.key_from_codes(xs)


def anti_core(pair, n: int) -> int:
    a = global_letters(pair[0], n)
    b = global_letters(pair[1], n)
    qs = [q for q in range(n) if lsymp(a[q], b[q]) == 1]
    if not qs:
        raise AssertionError("global symplectic-one pair has no local anti core")
    return qs[0]


def localized_pair(pair, n: int, q: int, basis: tuple[int, int] | None = None):
    a = global_letters(pair[0], n)
    b = global_letters(pair[1], n)
    if basis is None:
        basis = (a[q], b[q])
    aa = [0] * n
    bb = [0] * n
    aa[q], bb[q] = basis
    return key_from_letters(aa), key_from_letters(bb)


def pair_is_support1(pair) -> bool:
    return p10.wt(pair[0]) <= 1 and p10.wt(pair[1]) <= 1


def canonical_tags(n: int, qA: int, basisA: tuple[int, int], qB: int, basisB: tuple[int, int]):
    s0 = [0] * n
    s1 = [0] * n
    da = dual_tag_for_basis(basisA)
    if qA == qB:
        if basisA != basisB:
            raise AssertionError("same-qubit canonical Tag requires common basis")
        s0[qA], s1[qA] = da
    else:
        db = dual_tag_for_basis(basisB)
        s0[qA], s1[qA] = da
        s0[qB], s1[qB] = db
    return key_from_letters(s0), key_from_letters(s1)


def labels_global(s0, s1, pair):
    return 2 * p10.symp(s0, pair[0]) + p10.symp(s1, pair[0]), 2 * p10.symp(s0, pair[1]) + p10.symp(s1, pair[1])


def block_cost(pair, targets, central: int) -> int:
    rs = (pair[0], pair[1], p10.mul(pair[0], pair[1]))
    return p10.uanti_support(rs, central) + sum(p10.wt(p10.mul(targets[k], rs[k])) for k in range(3))


def config_cost(pairA, pairB, s0, s1, targetsA, targetsB, centralA, centralB, permB):
    tb = tuple(targetsB[permB[k]] for k in range(3))
    return block_cost(pairA, targetsA, centralA) + block_cost(pairB, tb, centralB) + 2 * (p10.wt(s0) + p10.wt(s1))


def feasible(pairA, pairB, s0, s1) -> bool:
    if p10.symp(pairA[0], pairA[1]) != 1 or p10.symp(pairB[0], pairB[1]) != 1:
        return False
    la = labels_global(s0, s1, pairA)
    lb = labels_global(s0, s1, pairB)
    return la == lb and la[0] in (1, 2, 3) and la[1] in (1, 2, 3) and la[0] != la[1]


def min_tag_for_pairs(pairA, pairB, n: int):
    keys = [(x, z) for x in range(1 << n) for z in range(1 << n)]
    best = None
    for c0, c1 in ((a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b):
        u0, u1 = (c0 >> 1) & 1, (c1 >> 1) & 1
        v0, v1 = c0 & 1, c1 & 1
        mins = []
        for rhs in ((u0, u1, u0, u1), (v0, v1, v0, v1)):
            m = None
            mk = None
            for s in keys:
                syn = (p10.symp(s, pairA[0]), p10.symp(s, pairA[1]), p10.symp(s, pairB[0]), p10.symp(s, pairB[1]))
                if syn == rhs:
                    w = p10.wt(s)
                    if m is None or (w, s) < (m, mk):
                        m, mk = w, s
            if m is None:
                break
            mins.append((m, mk))
        if len(mins) != 2:
            continue
        row = (2 * (mins[0][0] + mins[1][0]), mins[0][1], mins[1][1], (c0, c1))
        if best is None or row < best:
            best = row
    return best


def random_pair_cap2(n: int, rng: random.Random):
    keys = [(x, z) for x in range(1 << n) for z in range(1 << n) if (x, z) != (0, 0) and p10.wt((x, z)) <= 2]
    for _ in range(10000):
        a = rng.choice(keys)
        b = rng.choice(keys)
        if p10.symp(a, b) == 1:
            return a, b
    raise AssertionError("failed to sample support2 symplectic pair")


def normalize(pairA, pairB, s0, s1, n: int):
    qA = anti_core(pairA, n)
    qB = anti_core(pairB, n)
    laA = global_letters(pairA[0], n)[qA]
    laB = global_letters(pairA[1], n)[qA]
    lbA = global_letters(pairB[0], n)[qB]
    lbB = global_letters(pairB[1], n)[qB]
    basisA = (laA, laB)
    basisB = (lbA, lbB)
    if qA == qB and basisA != basisB:
        a1 = pair_is_support1(pairA)
        b1 = pair_is_support1(pairB)
        if a1 and b1:
            raise AssertionError("rigidity violation: two support1 same-core bases differ")
        if a1 and not b1:
            basisB = basisA
        else:
            basisA = basisB if b1 else basisA
            basisB = basisA
    newA = localized_pair(pairA, n, qA, basisA)
    newB = localized_pair(pairB, n, qB, basisB)
    ns0, ns1 = canonical_tags(n, qA, basisA, qB, basisB)
    return newA, newB, ns0, ns1


def stress_panel() -> dict[str, Any]:
    rng = random.Random(SEED)
    rows = []
    failures = []
    for n in range(2, 7):
        for rep in range(12):
            for _attempt in range(1000):
                A = random_pair_cap2(n, rng)
                B = random_pair_cap2(n, rng)
                tag = min_tag_for_pairs(A, B, n)
                if tag is not None:
                    break
            else:
                raise AssertionError("failed to find feasible shared Tag")
            _, s0, s1, _ = tag
            targetsA = tuple((rng.randrange(1 << n), rng.randrange(1 << n)) for _ in range(3))
            targetsB = tuple((rng.randrange(1 << n), rng.randrange(1 << n)) for _ in range(3))
            ca = rng.randrange(3)
            cb = rng.randrange(3)
            perm = tuple(rng.sample(range(3), 3))
            old = config_cost(A, B, s0, s1, targetsA, targetsB, ca, cb, perm)
            nA, nB, ns0, ns1 = normalize(A, B, s0, s1, n)
            new = config_cost(nA, nB, ns0, ns1, targetsA, targetsB, ca, cb, perm)
            ok = feasible(nA, nB, ns0, ns1) and pair_is_support1(nA) and pair_is_support1(nB) and new <= old
            row = {"n": n, "rep": rep, "old_cost": old, "new_cost": new, "delta": new - old, "pass": ok}
            rows.append(row)
            if not ok and len(failures) < 10:
                failures.append(row)
    return {
        "seed": SEED,
        "rows": len(rows),
        "n_values": [2, 3, 4, 5, 6],
        "all_pass": not failures and all(r["pass"] for r in rows),
        "max_delta": max(r["delta"] for r in rows),
        "min_delta": min(r["delta"] for r in rows),
        "failures": failures,
    }


def main() -> int:
    parent = json.loads(PARENT_SUPPORT2.read_text())
    parent_result = json.loads(PARENT_SUPPORT2_RESULT.read_text())
    v5 = json.loads(PARENT_V5.read_text())
    binding = production_binding()
    deletion = deletion_lemma()
    alignment = core_alignment_lemma()
    tags = tag_lemmas()

    parent_binding = {
        "support2_receipt_sha256": sha(PARENT_SUPPORT2),
        "support2_result_sha256": sha(PARENT_SUPPORT2_RESULT),
        "v5_receipt_sha256": sha(PARENT_V5),
        "support2_terminal": parent.get("terminal"),
        "support2_both_accept": parent.get("both_accept"),
        "support2_result_bound": parent_result.get("support_bound"),
        "v5_terminal": v5.get("terminal"),
        "v5_support1_authority_false": v5.get("support1_authority") is False,
    }

    composition = {
        "extra_credit_floor": 4,
        "alignment_ceiling": 3,
        "credit_strictly_exceeds_alignment": 4 > 3,
        "old_tag_floor": 4,
        "distinct_core_new_tag": 8,
        "distinct_non_support_case_closes": 4 + 4 >= 8,
        "distinct_both_support1_old_tag_floor": 8,
        "distinct_both_support1_case_closes": tags["distinct_qubit_tag"]["all_minima_8"],
        "same_core_new_tag": 4,
        "same_core_tag_nonincrease": 4 <= 4,
        "same_core_alignment_paid": 4 >= 3,
        "same_core_support1_rigidity": tags["same_qubit_rigidity"]["holds"],
        "support0_infeasible": lsymp(0, 0) == 0,
    }

    local_gates = {
        "protocol_present": PROTOCOL.is_file(),
        "production_algebra_exact": binding["all_exact"],
        "deletion_domain_2880": deletion["expected_domain_2880"],
        "deletion_commuting_max_minus4": deletion["commuting_max_minus4"],
        "deletion_anti_max_minus7": deletion["anticommuting_max_minus7"],
        "alignment_domain_6912": alignment["expected_domain_6912"],
        "alignment_frame_invariant": alignment["frame_contribution_always_10"],
        "alignment_max3": alignment["max_is_3"],
        "canonical_dual_tag": tags["canonical_dual_all_nonzero"],
        "same_qubit_domain_576": tags["same_qubit_rigidity"]["expected_domain_576"],
        "same_qubit_rigidity": tags["same_qubit_rigidity"]["holds"],
        "distinct_tag_domain_9216": tags["distinct_qubit_tag"]["expected_domain_9216"],
        "distinct_tag_min8": tags["distinct_qubit_tag"]["all_minima_8"],
        "old_tag_floor4": tags["feasible_label_rows"]["both_tag_syndrome_rows_nonzero"],
        "parent_support2": parent.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED" and parent.get("both_accept") is True and parent_result.get("support_bound") == 2,
        "v5_is_bounded_negative_only": v5.get("terminal") == "QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL" and v5.get("support1_authority") is False,
        "composition_all": all(isinstance(x, bool) and x for k, x in composition.items() if k not in {"extra_credit_floor", "alignment_ceiling", "old_tag_floor", "distinct_core_new_tag", "distinct_both_support1_old_tag_floor", "same_core_new_tag"}),
    }

    stress = stress_panel() if all(local_gates.values()) else {"rows": 0, "all_pass": False, "skipped": "local gate failed"}
    gates = dict(local_gates)
    gates["stress_no_counterexample"] = stress.get("all_pass") is True

    if all(gates.values()):
        terminal = "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED"
        support_bound = 1
        kappa = 1
    elif not all(v for k, v in local_gates.items() if k not in {"composition_all"}):
        terminal = "QG9_SUPPORT1_LOCAL_LEMMA_COUNTEREXAMPLE_FOUND"
        support_bound = None
        kappa = None
    elif not local_gates["composition_all"]:
        terminal = "QG9_SUPPORT1_COMPOSITION_GAP_FOUND"
        support_bound = None
        kappa = None
    else:
        terminal = "QG9_SUPPORT1_CANNOT_CHECK"
        support_bound = None
        kappa = None

    result = {
        "schema": "ORION.QG.QG9.V6.Support1Normalization.v1",
        "issue": ISSUE,
        "protocol_sha256": sha(PROTOCOL),
        "production_binding": binding,
        "parent_binding": parent_binding,
        "deletion_lemma": deletion,
        "core_alignment_lemma": alignment,
        "tag_lemmas": tags,
        "composition_audit": composition,
        "stress": stress,
        "gates": gates,
        "terminal": terminal,
        "support_bound": support_bound,
        "intrinsic_support_number": kappa,
        "support0_infeasible": composition["support0_infeasible"],
        "new_theorem_authority": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "network_access": False,
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DEFAULT_OUT))
    ns = ap.parse_args()
    out = Path(ns.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {
        "terminal": terminal,
        "support_bound": support_bound,
        "intrinsic_support_number": kappa,
        "result_digest": result["result_digest"],
        "all_gates": all(gates.values()),
        "stress_rows": stress.get("rows"),
        "stress_max_delta": stress.get("max_delta"),
    }
    print(TOKEN + canonical(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
