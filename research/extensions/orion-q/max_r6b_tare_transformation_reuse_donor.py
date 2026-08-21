#!/usr/bin/env python3
"""MAX-R6B: exhaustive donor-owned TARE transformation reuse on open subjects.

Frozen by MAX_R6B_TARE_TRANSFORMATION_REUSE_DONOR_ABSORPTION_PROTOCOL.md.
This lane gives the TARE donor first right of refusal after the exact single-block
joint-frame candidate collapsed to the exact frame-only comparator. A positive is
absorbed donor capability only; it grants no R6 or novelty authority.
"""
from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from typing import Any

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6_p10_candidate_blind_frame_optimizer as p10

WINDOW = p10.WINDOW


# Hermitian one-qubit Pauli code convention (x,z): I=00, X=10, Y=11, Z=01.
# Product phase exponents e are defined by A B = i^e C.
_LOCAL_PHASE = {
    (0, 0): 0,
    (0, 1): 0,
    (0, 2): 0,
    (0, 3): 0,
    (1, 0): 0,
    (1, 1): 0,
    (1, 2): 1,
    (1, 3): 3,
    (2, 0): 0,
    (2, 1): 3,
    (2, 2): 0,
    (2, 3): 1,
    (3, 0): 0,
    (3, 1): 1,
    (3, 2): 3,
    (3, 3): 0,
}


def _local_letter(x: int, z: int) -> int:
    if x == 0 and z == 0:
        return 0
    if x == 1 and z == 0:
        return 1
    if x == 1 and z == 1:
        return 2
    return 3


def mul_phase(a: tuple[int, int], b: tuple[int, int], n: int) -> tuple[tuple[int, int], int]:
    """Return Hermitian Pauli binary product and i-phase exponent."""
    exponent = 0
    for q in range(n):
        aa = _local_letter((a[0] >> q) & 1, (a[1] >> q) & 1)
        bb = _local_letter((b[0] >> q) & 1, (b[1] >> q) & 1)
        exponent = (exponent + _LOCAL_PHASE[(aa, bb)]) % 4
    return p10.mul(a, b), exponent


def correction_phase(
    target: tuple[int, int],
    frame: tuple[int, int],
    correction: tuple[int, int],
    n: int,
) -> int:
    """g such that i^g T R = P under the Hermitian Pauli convention."""
    got, exponent = mul_phase(correction, frame, n)
    if got != target:
        raise AssertionError({"correction_binary_identity_failed": [target, frame, correction, got]})
    return (-exponent) % 4


def _labels(s0, s1, rs) -> tuple[int, int, int]:
    return tuple(2 * p10.symp(s0, r) + p10.symp(s1, r) for r in rs)


def _target_key(rec: dict[str, Any]):
    return (-float(rec["fraction"]), -int(rec["delta"]), tuple(rec["term_indices"]))


def window_champions(cfg) -> tuple[list[tuple[tuple[int, int], float]], list[dict[str, Any]], float]:
    """Replay P10 and retain exactly one best improving triple per 12-term window."""
    terms, max_imag = p10.load_terms(cfg)
    champions: list[dict[str, Any]] = []
    n = int(cfg["n_qubits"])
    for start in range(0, len(terms), WINDOW):
        end = min(start + WINDOW, len(terms))
        best = None
        for comb in itertools.combinations(range(start, end), 3):
            targets = tuple(terms[i][0] for i in comb)
            if p10.is_direct_triple(targets):
                continue
            canonical = p10.canonical_best(targets, n)
            generated = p10.rank2_best(targets, n)
            delta = int(canonical["cost"] - generated["cost"])
            if delta <= 0:
                continue
            fraction = float(delta / canonical["cost"] if canonical["cost"] else 0.0)
            lam = math.sqrt(3.0) * math.sqrt(sum(float(terms[i][1]) ** 2 for i in comb))
            rec = {
                "window_start": int(start),
                "term_indices": list(comb),
                "delta": delta,
                "fraction": fraction,
                "Lambda_TARE3": float(lam),
                "p10_generated": generated,
                "p10_canonical": canonical,
            }
            if best is None or _target_key(rec) < _target_key(best):
                best = rec
        if best is not None:
            champions.append(best)
    champions.sort(key=_target_key)
    return terms, champions, max_imag


def _block_payload(terms, champion: dict[str, Any], n: int) -> dict[str, Any]:
    indices = tuple(int(i) for i in champion["term_indices"])
    targets = tuple(terms[i][0] for i in indices)
    coefficients = tuple(float(terms[i][1]) for i in indices)
    frame_only = exact.frame_only_strong(targets, n)
    return {
        "window_start": int(champion["window_start"]),
        "term_indices": list(indices),
        "targets": [list(x) for x in targets],
        "coefficients": list(coefficients),
        "Lambda_TARE3": float(
            math.sqrt(3.0) * math.sqrt(sum(value * value for value in coefficients))
        ),
        "p10_delta": int(champion["delta"]),
        "p10_fraction": float(champion["fraction"]),
        "frame_only": frame_only,
    }


@dataclass(frozen=True)
class ReuseSignature:
    s0: tuple[int, int]
    s1: tuple[int, int]
    labels: tuple[int, int, int]
    corrections: tuple[tuple[int, tuple[int, int]], ...]
    provenance: tuple[Any, ...]

    def key(self):
        return (self.s0, self.s1, self.labels, self.corrections)


def complete_source_signatures(block: dict[str, Any], n: int) -> dict[tuple[Any, ...], ReuseSignature]:
    targets = tuple(tuple(x) for x in block["targets"])
    signatures: dict[tuple[Any, ...], ReuseSignature] = {}
    for q in range(n):
        xyz = ((1 << q, 0), (1 << q, 1 << q), (0, 1 << q))
        for rs in itertools.permutations(xyz, 3):
            rs = tuple(rs)
            if not p10.is_pairwise_anti(rs):
                raise AssertionError("weight-one donor frame is not pairwise anti")
            for labels in exact.DEPENDENT_LABEL_TRIPLES:
                hi_syn = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
                lo_syn = sum(((labels[k] & 1) << k) for k in range(3))
                _wh, s0 = p10.tag_min_weight(rs, hi_syn, n)
                _wl, s1 = p10.tag_min_weight(rs, lo_syn, n)
                if _labels(s0, s1, rs) != tuple(labels):
                    raise AssertionError("source signature label reconstruction failed")
                for permutation in itertools.permutations(range(3)):
                    permuted = tuple(targets[permutation[k]] for k in range(3))
                    corrections = tuple(p10.mul(permuted[k], rs[k]) for k in range(3))
                    signed = tuple(
                        (correction_phase(permuted[k], rs[k], corrections[k], n), corrections[k])
                        for k in range(3)
                    )
                    signature = ReuseSignature(
                        s0=tuple(s0),
                        s1=tuple(s1),
                        labels=tuple(int(x) for x in labels),
                        corrections=signed,
                        provenance=(q, tuple(rs), tuple(permutation)),
                    )
                    key = signature.key()
                    old = signatures.get(key)
                    if old is None or signature.provenance < old.provenance:
                        signatures[key] = signature
    return signatures


def apply_signature(signature: ReuseSignature, block: dict[str, Any], n: int):
    targets = tuple(tuple(x) for x in block["targets"])
    ts = tuple(item[1] for item in signature.corrections)
    expected_phases = tuple(int(item[0]) for item in signature.corrections)
    best = None
    for permutation in itertools.permutations(range(3)):
        permuted = tuple(targets[permutation[k]] for k in range(3))
        rs = tuple(p10.mul(permuted[k], ts[k]) for k in range(3))
        if not p10.is_pairwise_anti(rs):
            continue
        if _labels(signature.s0, signature.s1, rs) != signature.labels:
            continue
        phases = tuple(correction_phase(permuted[k], rs[k], ts[k], n) for k in range(3))
        if phases != expected_phases:
            continue
        central_costs = tuple(p10.uanti_support(rs, central) for central in range(3))
        central = min(range(3), key=lambda c: (central_costs[c], c))
        rec = {
            "target_permutation": list(permutation),
            "R": [list(x) for x in rs],
            "S": [list(signature.s0), list(signature.s1)],
            "labels": list(signature.labels),
            "signed_T": [
                {"phase_exponent": expected_phases[k], "T": list(ts[k])}
                for k in range(3)
            ],
            "central": int(central),
            "uanti_support": int(central_costs[central]),
        }
        key = (
            rec["uanti_support"],
            tuple(permutation),
            central,
            tuple(rs),
        )
        if best is None or key < best[0]:
            best = (key, rec)
    return None if best is None else best[1]


def signature_shared_cost(signature: ReuseSignature, a: dict[str, Any], b: dict[str, Any], n: int):
    wa = apply_signature(signature, a, n)
    wb = apply_signature(signature, b, n)
    if wa is None or wb is None:
        return None
    ts = tuple(item[1] for item in signature.corrections)
    tag = 2 * (p10.wt(signature.s0) + p10.wt(signature.s1))
    correction = sum(p10.wt(t) for t in ts)
    total = tag + correction + int(wa["uanti_support"]) + int(wb["uanti_support"])
    checks = {
        "same_S": wa["S"] == wb["S"],
        "same_labels": wa["labels"] == wb["labels"],
        "same_signed_T": wa["signed_T"] == wb["signed_T"],
        "blocks_disjoint": set(a["term_indices"]).isdisjoint(b["term_indices"]),
        "cost_recomputed": total
        == 2 * (p10.wt(signature.s0) + p10.wt(signature.s1))
        + sum(p10.wt(item[1]) for item in signature.corrections)
        + wa["uanti_support"]
        + wb["uanti_support"],
    }
    if not all(checks.values()):
        raise AssertionError({"reuse_witness_failed": checks})
    return {
        "C_reuse": int(total),
        "tag_support_twice_shared": int(tag),
        "correction_support_shared": int(correction),
        "source_signature_provenance": list(signature.provenance),
        "block_A": wa,
        "block_B": wb,
        "checks": checks,
    }


def best_reuse(a: dict[str, Any], b: dict[str, Any], n: int):
    signatures = complete_source_signatures(a, n)
    signatures.update(
        {
            key: value
            for key, value in complete_source_signatures(b, n).items()
            if key not in signatures
        }
    )
    best = None
    valid = 0
    for key in sorted(signatures):
        rec = signature_shared_cost(signatures[key], a, b, n)
        if rec is None:
            continue
        valid += 1
        rkey = (
            rec["C_reuse"],
            tuple(rec["source_signature_provenance"]),
            tuple(key),
        )
        if best is None or rkey < best[0]:
            best = (rkey, rec)
    return {
        "source_signature_count": len(signatures),
        "valid_reuse_signature_count": valid,
        "best": None if best is None else best[1],
    }


def hostile_validation() -> dict[str, Any]:
    single = {
        "I": (0, 0),
        "X": (1, 0),
        "Y": (1, 1),
        "Z": (0, 1),
    }
    expected = {
        ("X", "Y"): ("Z", 1),
        ("Y", "X"): ("Z", 3),
        ("Y", "Z"): ("X", 1),
        ("Z", "Y"): ("X", 3),
        ("Z", "X"): ("Y", 1),
        ("X", "Z"): ("Y", 3),
    }
    reverse = {value: name for name, value in single.items()}
    phase_rows = {}
    for pair, (out_name, out_phase) in expected.items():
        got, phase = mul_phase(single[pair[0]], single[pair[1]], 1)
        passed = reverse[got] == out_name and phase == out_phase
        phase_rows["".join(pair)] = {"out": reverse[got], "phase": phase, "pass": passed}
        if not passed:
            raise AssertionError({"phase_table_failure": pair, "got": [got, phase]})

    n = 2
    rs = ((1, 0), (1, 1), (0, 1))
    labels = (1, 2, 3)
    hi_syn = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
    lo_syn = sum(((labels[k] & 1) << k) for k in range(3))
    _wh, s0 = p10.tag_min_weight(rs, hi_syn, n)
    _wl, s1 = p10.tag_min_weight(rs, lo_syn, n)
    targets = rs
    signed = tuple((correction_phase(targets[k], rs[k], (0, 0), n), (0, 0)) for k in range(3))
    signature = ReuseSignature(tuple(s0), tuple(s1), labels, signed, ("hostile",))
    block = {"targets": [list(x) for x in targets], "term_indices": [0, 1, 2]}
    valid = apply_signature(signature, block, n)
    if valid is None:
        raise AssertionError("valid hostile reuse signature rejected")

    bad_phase = ReuseSignature(
        signature.s0,
        signature.s1,
        signature.labels,
        ((1, signature.corrections[0][1]), *signature.corrections[1:]),
        ("bad-phase",),
    )
    # A permutation of (1,2,3) can be made valid by an allowed target permutation.
    # Include label 0 so no permutation of this dependent-frame label set can match.
    bad_labels = ReuseSignature(
        signature.s0,
        signature.s1,
        (0, 1, 2),
        signature.corrections,
        ("bad-labels",),
    )
    nonanti = {"targets": [list(single["X"]), list(single["X"]), list(single["X"])], "term_indices": [3, 4, 5]}
    gates = {
        "signed_pauli_table": all(row["pass"] for row in phase_rows.values()),
        "valid_signature_accepted": valid is not None,
        "phase_mismatch_rejected": apply_signature(bad_phase, block, n) is None,
        "label_mismatch_rejected": apply_signature(bad_labels, block, n) is None,
        "nonanticommuting_destination_rejected": apply_signature(signature, nonanti, n) is None,
    }
    if not all(gates.values()):
        raise AssertionError({"hostile_reuse_gates": gates})
    return {"phase_rows": phase_rows, "gates": gates, "all_pass": True}


def run_subject(name: str, cfg) -> dict[str, Any]:
    terms, champions, max_imag = window_champions(cfg)
    if len(champions) < 2:
        return {
            "subject": name,
            "source_blob": cfg["blob"],
            "n_qubits": cfg["n_qubits"],
            "max_imag": max_imag,
            "window_champion_count": len(champions),
            "batch_eligible": False,
            "selected_blocks": [],
            "C_separate": None,
            "reuse": None,
            "strict_improvement": False,
        }
    n = int(cfg["n_qubits"])
    selected = champions[:2]
    a = _block_payload(terms, selected[0], n)
    b = _block_payload(terms, selected[1], n)
    if a["window_start"] == b["window_start"] or not set(a["term_indices"]).isdisjoint(b["term_indices"]):
        raise AssertionError("frozen window-champion batch is not disjoint")
    separate = int(a["frame_only"]["C_joint"] + b["frame_only"]["C_joint"])
    reuse = best_reuse(a, b, n)
    best_cost = None if reuse["best"] is None else int(reuse["best"]["C_reuse"])
    return {
        "subject": name,
        "source_blob": cfg["blob"],
        "n_qubits": n,
        "max_imag": max_imag,
        "window_champion_count": len(champions),
        "batch_eligible": True,
        "selected_blocks": [a, b],
        "C_separate": separate,
        "reuse": reuse,
        "strict_improvement": best_cost is not None and best_cost < separate,
        "nonworse": best_cost is not None and best_cost <= separate,
        "delta": None if best_cost is None else int(separate - best_cost),
    }


def main() -> dict[str, Any]:
    hostile = hostile_validation()
    subjects = {
        name: run_subject(name, cfg)
        for name, cfg in p10.base.SUBJECTS.items()
    }
    gates = {
        "hostile_signed_reuse_exact": hostile["all_pass"],
        "both_subjects_batch_eligible": all(row["batch_eligible"] for row in subjects.values()),
        "reuse_witness_exists_both": all(
            row.get("reuse") is not None and row["reuse"]["best"] is not None
            for row in subjects.values()
        ),
        "reuse_nonworse_both": all(row.get("nonworse") is True for row in subjects.values()),
        "strict_reuse_improvement_at_least_one": any(
            row.get("strict_improvement") is True for row in subjects.values()
        ),
        "fresh_stretched_n2_unread": True,
    }
    supported = all(gates.values())
    result = {
        "schema": "ORIONQ.MAXR6B.TARETransformationReuseDonorAbsorption.v1",
        "authority": (
            "MAX_R6B_TARE_REUSE_DONOR_POSITIVE__ABSORB_NO_NOVELTY"
            if supported
            else "MAX_R6B_TARE_REUSE_DONOR_NEGATIVE__NO_NOVELTY"
        ),
        "scope": "OPEN_H4_EQ_N2_DONOR_ABSORPTION_ONLY__NOT_R6",
        "donor_credit": "TARE_U_TAG_U_CORRECT_REUSE_AND_GENERIC_COMMON_CLIFFORD_FACTORING",
        "novelty_credit": False,
        "hostile": hostile,
        "subjects": subjects,
        "gates": gates,
        "development_supported": supported,
        "reserved_stretched_n2_accessed": False,
        "r6_authority": False,
    }
    print("ORIONQ_MAX_R6B_TARE_REUSE=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
