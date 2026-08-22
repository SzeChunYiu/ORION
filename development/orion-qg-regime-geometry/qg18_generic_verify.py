#!/usr/bin/env python3
"""QG-18 generic verifier -- pure primitives, no analyzer imports.

Rebuilds, from the standard library alone:

  * the two-bit symplectic Pauli algebra on n qubits (multiplication, weight,
    symplectic form) with no reference to any repository module;
  * the donor-owned all-three-blocks common-factor rule F3;
  * the frozen R6M/TARE acceptance predicate and the frozen unit-cost support
    objective O0;
  * the COMPLETE support-<=1 configuration family at the witness's n, by naive
    enumeration of every weight-<=1 frame six-tuple, every Tag key, every
    central choice and every relative target permutation.

It then re-derives the QG-18 lower bound from scratch:

    an explicit FEASIBLE configuration whose frame Paulis all have global
    support <= 2 and whose exact O0 cost is strictly below the exact minimum
    of O0 over the whole support-<=1 family
        =>  support 1 is not a valid support bound  =>  kappa_TARE >= 2.

The matching upper bound kappa_TARE <= 2 is the committed R6S all-n theorem,
bound here by sha256 and by its recorded outcome/authority strings.

Emits exactly one decision line: QG18_GENERIC_VERIFY=ACCEPT or =REJECT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG18_TARE_KAPPA_PROTOCOL_V1.md"
TOKEN = "QG18_GENERIC_VERIFY="
MAX_BRUTEFORCE_N = 2


# ---------------------------------------------------------------- primitives


def popcount(v: int) -> int:
    return bin(v).count("1")


def wt(key) -> int:
    """Global Pauli weight: number of qubits carrying a non-identity letter."""
    return popcount(key[0] | key[1])


def mul(a, b):
    """Pauli product up to phase, in the (X-mask, Z-mask) representation."""
    return (a[0] ^ b[0], a[1] ^ b[1])


def symp(a, b) -> int:
    """Symplectic form: 0 iff the two Paulis commute."""
    return (popcount(a[0] & b[1]) + popcount(a[1] & b[0])) & 1


def bits(key, q: int):
    """The two bits of the local letter of `key` at qubit q."""
    return ((key[0] >> q) & 1, (key[1] >> q) & 1)


def local_wt(bit_pair) -> int:
    return 0 if bit_pair == (0, 0) else 1


def f3(a, b, c) -> int:
    """Donor-owned all-three common-factor rule on local letters."""
    if a == b == c and a != (0, 0):
        return 1
    return local_wt(a) + local_wt(b) + local_wt(c)


def acceptance(frames6, s):
    """Frozen R6M acceptance predicate -> (l0, l1) or None."""
    for j in range(3):
        if symp(frames6[2 * j], frames6[2 * j + 1]) != 1:
            return None
    l0 = symp(s, frames6[0])
    l1 = symp(s, frames6[1])
    for j in (1, 2):
        if symp(s, frames6[2 * j]) != l0 or symp(s, frames6[2 * j + 1]) != l1:
            return None
    if l0 == l1:
        return None
    return (l0, l1)


def objective(t6, frames6, s, centrals, n: int) -> int:
    """Frozen unit-cost support objective O0."""
    raw = 0
    for j in range(3):
        m0 = 2 if centrals[j] == 0 else 4
        m1 = 2 if centrals[j] == 1 else 4
        raw += m0 * wt(frames6[2 * j]) + m1 * wt(frames6[2 * j + 1])
    raw += 2 * wt(s)
    tt = [mul(t6[i], frames6[i]) for i in range(6)]
    total = 0
    for k in (0, 1):
        for q in range(n):
            total += f3(bits(tt[k], q), bits(tt[2 + k], q), bits(tt[4 + k], q))
    return raw - 18 + total


def permute_targets(target_pairs, perms):
    out = []
    for j in range(3):
        pair = target_pairs[j]
        out.extend(pair if perms[j] == 0 else (pair[1], pair[0]))
    return tuple(out)


# --------------------------------------------- complete support-<=1 sweep


def weight_le1_keys(n: int):
    keys = [(0, 0)]
    for q in range(n):
        keys.append((1 << q, 0))          # X_q
        keys.append((1 << q, 1 << q))     # Y_q
        keys.append((0, 1 << q))          # Z_q
    return keys


def all_keys(n: int):
    return [(x, z) for x in range(1 << n) for z in range(1 << n)]


def cap1_bruteforce(target_pairs, n: int):
    """Naive complete enumeration of the support-<=1 family. Returns (min, stats)."""
    wkeys = weight_le1_keys(n)
    tags = all_keys(n)
    centrals_all = list(itertools.product((0, 1), repeat=3))
    perms_all = [(0, pb, pc) for pb in (0, 1) for pc in (0, 1)]
    permuted = {p: permute_targets(target_pairs, p) for p in perms_all}
    best = None
    accepted = 0
    evaluated = 0
    frame_tuples = 0
    supports = set()
    for frames6 in itertools.product(wkeys, repeat=6):
        frame_tuples += 1
        if (
            symp(frames6[0], frames6[1]) != 1
            or symp(frames6[2], frames6[3]) != 1
            or symp(frames6[4], frames6[5]) != 1
        ):
            continue
        for s in tags:
            if acceptance(frames6, s) is None:
                continue
            accepted += 1
            for f in frames6:
                supports.add(wt(f))
            for centrals in centrals_all:
                for perms in perms_all:
                    evaluated += 1
                    val = objective(permuted[perms], frames6, s, centrals, n)
                    if best is None or val < best:
                        best = val
    stats = {
        "frame_six_tuples_enumerated": frame_tuples,
        "expected_frame_six_tuples": len(wkeys) ** 6,
        "tag_keys_enumerated": len(tags),
        "accepted_frame_tag_pairs": accepted,
        "objective_evaluations": evaluated,
        "frame_supports_seen": sorted(supports),
    }
    return best, stats


# ------------------------------------------------------------------ verify


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_key(pair):
    return (int(pair[0]), int(pair[1]))


def main() -> int:
    reasons = {}
    ok = True

    def fail(name, detail):
        nonlocal ok
        ok = False
        reasons[name] = detail

    if not RESULTS.is_file():
        print(TOKEN + "REJECT")
        print(json.dumps({"results_file_missing": str(RESULTS)}, sort_keys=True))
        return 1
    res = json.loads(RESULTS.read_text())

    # --- 1. protocol + receipt hashes ------------------------------------
    if not PROTOCOL.is_file():
        fail("protocol_missing", str(PROTOCOL))
    else:
        got = sha256_of(PROTOCOL)
        reasons["protocol_sha256"] = got
        if got != res.get("protocol_sha256"):
            fail("protocol_sha256_mismatch", [got, res.get("protocol_sha256")])

    rb = res.get("receipt_bindings", {})
    receipt_paths = {
        "r6s": "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json",
        "r6o": "research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json",
        "r6p": "research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json",
        "qg7": "research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json",
        "qg7b": "research/extensions/orion-qg/QG7B_HYBRID_FAMILY_RESULTS.json",
        "qg7c": "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json",
        "qg8": "research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json",
        "qg9v6": "research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json",
    }
    hash_report = {}
    for name, rel in receipt_paths.items():
        path = ROOT / rel
        if not path.is_file():
            fail("receipt_missing_" + name, rel)
            continue
        got = sha256_of(path)
        want = rb.get(name + "_sha256")
        hash_report[name] = got
        if got != want:
            fail("receipt_sha256_mismatch_" + name, [got, want])
    reasons["recomputed_receipt_sha256"] = hash_report

    # --- 2. upper bound kappa <= 2 comes from the committed R6S theorem ---
    r6s_path = ROOT / receipt_paths["r6s"]
    if r6s_path.is_file():
        r6s = json.loads(r6s_path.read_text())
        upper = {
            "outcome_theorem_machine_checked": r6s.get("outcome")
            == "THEOREM_MACHINE_CHECKED",
            "authority_support3_never_pays": "SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N"
            in str(r6s.get("authority")),
            "lemma_e_holds": bool(r6s.get("lemma_e", {}).get("holds")),
            "lemma_b_w3_to_w8_clean": bool(
                r6s.get("lemma_b", {}).get("w3_to_w8_all_admit_subset")
            ),
        }
        reasons["upper_bound_r6s"] = upper
        if not all(upper.values()):
            fail("r6s_upper_bound_semantics", upper)

    # --- 3. the witness ---------------------------------------------------
    wit = (res.get("q1_necessity_hunt") or {}).get("canonical_witness")
    if not wit:
        fail("no_canonical_witness", None)
        print(TOKEN + "REJECT")
        print(json.dumps(reasons, sort_keys=True, default=str))
        return 1

    n = int(wit["n"])
    reasons["witness_n"] = n
    if n > MAX_BRUTEFORCE_N:
        fail("witness_n_exceeds_complete_bruteforce_reach", n)
        print(TOKEN + "REJECT")
        print(json.dumps(reasons, sort_keys=True, default=str))
        return 1

    target_pairs = tuple(
        (as_key(pair[0]), as_key(pair[1])) for pair in wit["targets"]
    )
    claimed_dp = int(wit["C_DP"])
    claimed_dxx = int(wit["C_Dxx"])
    claimed_cap1 = int(wit["C_cap1"])

    # 3a. explicit support-2 configuration, rebuilt and re-costed.
    s2 = wit["support2_configuration"]
    frames2 = tuple(as_key(f) for f in s2["frames"])
    tag2 = as_key(s2["tag"])
    centrals2 = tuple(int(c) for c in s2["centrals"])
    perms2 = tuple(int(p) for p in s2["target_permutations"])
    lab2 = acceptance(frames2, tag2)
    supports2 = [wt(f) for f in frames2]
    cost2 = (
        objective(permute_targets(target_pairs, perms2), frames2, tag2, centrals2, n)
        if lab2 is not None
        else None
    )
    reasons["support2_configuration"] = {
        "acceptance_labels": list(lab2) if lab2 else None,
        "per_frame_support": supports2,
        "max_frame_support": max(supports2),
        "recomputed_cost": cost2,
    }
    if lab2 is None:
        fail("support2_configuration_infeasible", None)
    if max(supports2) > 2:
        fail("support2_configuration_exceeds_support_2", max(supports2))
    if cost2 != claimed_dp or cost2 != claimed_dxx:
        fail("support2_cost_mismatch", [cost2, claimed_dp, claimed_dxx])

    # 3b. explicit cap-1 configuration, rebuilt and re-costed.
    c1 = wit["cap1_optimal_configuration"]
    frames1 = tuple(as_key(f) for f in c1["frames"])
    tag1 = as_key(c1["tag"])
    desc = c1["descriptor"]
    perms1 = (0, int(desc["perm_b"]), int(desc["perm_c"]))
    lab1 = acceptance(frames1, tag1)
    supports1 = [wt(f) for f in frames1]
    cost1 = None
    if lab1 is not None:
        cost1 = min(
            objective(permute_targets(target_pairs, perms1), frames1, tag1, centrals, n)
            for centrals in itertools.product((0, 1), repeat=3)
        )
    reasons["cap1_configuration"] = {
        "acceptance_labels": list(lab1) if lab1 else None,
        "per_frame_support": supports1,
        "max_frame_support": max(supports1),
        "recomputed_cost": cost1,
    }
    if lab1 is None:
        fail("cap1_configuration_infeasible", None)
    if max(supports1) > 1:
        fail("cap1_configuration_exceeds_support_1", max(supports1))
    if cost1 != claimed_cap1:
        fail("cap1_configuration_cost_mismatch", [cost1, claimed_cap1])

    # 3c. the complete support-<=1 brute force, rebuilt from primitives.
    bf, stats = cap1_bruteforce(target_pairs, n)
    reasons["cap1_bruteforce"] = dict(stats, minimum=bf)
    if stats["frame_six_tuples_enumerated"] != stats["expected_frame_six_tuples"]:
        fail("cap1_bruteforce_incomplete", stats)
    if stats["frame_supports_seen"] != [1]:
        fail("cap1_bruteforce_support_leak", stats["frame_supports_seen"])
    if bf != claimed_cap1:
        fail("cap1_bruteforce_mismatch", [bf, claimed_cap1])

    # 3d. the lower-bound inequality itself.
    strict = cost2 is not None and bf is not None and cost2 < bf
    reasons["strict_gap"] = {
        "support2_cost": cost2,
        "exact_support1_optimum": bf,
        "gap": (bf - cost2) if strict else None,
        "strict": strict,
    }
    if not strict:
        fail("no_strict_gap", [cost2, bf])

    # --- 4. terminal consistency -----------------------------------------
    consistency = {
        "terminal": res.get("terminal") == "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS",
        "kappa_is_2": res.get("intrinsic_support_number") == 2,
        "kappa_interval": res.get("kappa_interval") == [2, 2],
        "authority_not_r6": "NOT_R6" in str(res.get("authority")),
        "no_novelty_credit": res.get("novelty_credit") is False,
        "no_r6_authority": res.get("r6_authority") is False,
        "no_chemistry": res.get("chemistry_sources_read") is False,
        "protected_not_read": res.get("protected_subject_read") is False,
        "all_gates_true": all(bool(v) for v in (res.get("gates") or {}).values()),
    }
    reasons["result_consistency"] = consistency
    if not all(consistency.values()):
        fail("result_consistency", consistency)

    reasons["conclusion"] = (
        "kappa_TARE >= 2 re-derived from primitives: an explicit feasible "
        "support-2 configuration costs {} while the complete support-<=1 "
        "family's exact optimum is {}. With the committed R6S all-n upper "
        "bound (support <= 2), kappa_TARE = 2 exactly.".format(cost2, bf)
        if ok
        else "verification failed; see the recorded reasons"
    )

    print(TOKEN + ("ACCEPT" if ok else "REJECT"))
    print(json.dumps(reasons, sort_keys=True, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
