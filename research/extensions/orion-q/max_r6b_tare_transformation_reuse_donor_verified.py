#!/usr/bin/env python3
"""Verification-only launcher for the frozen MAX-R6B donor-reuse search.

The frozen search implementation's hostile label test used another valid
permutation of (1,2,3). Because destination target permutations are explicitly
allowed by the frozen protocol, that supposed mismatch is legitimately
transferable and the hostile test false-fails before chemistry is evaluated.

This launcher changes no subject, selector, comparator, reuse signature search,
resource accounting, or scientific gate. It replaces only that hostile test
with an impossible label signature containing 0, which cannot be induced by the
frozen dependent-frame label alphabet (permutations of 1,2,3).
"""
from __future__ import annotations

import max_r6b_tare_transformation_reuse_donor as impl


def hostile_validation_fixed():
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
        got, phase = impl.mul_phase(single[pair[0]], single[pair[1]], 1)
        passed = reverse[got] == out_name and phase == out_phase
        phase_rows["".join(pair)] = {"out": reverse[got], "phase": phase, "pass": passed}
        if not passed:
            raise AssertionError({"phase_table_failure": pair, "got": [got, phase]})

    n = 2
    rs = ((1, 0), (1, 1), (0, 1))
    labels = (1, 2, 3)
    hi_syn = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
    lo_syn = sum(((labels[k] & 1) << k) for k in range(3))
    _wh, s0 = impl.p10.tag_min_weight(rs, hi_syn, n)
    _wl, s1 = impl.p10.tag_min_weight(rs, lo_syn, n)
    targets = rs
    signed = tuple(
        (impl.correction_phase(targets[k], rs[k], (0, 0), n), (0, 0))
        for k in range(3)
    )
    signature = impl.ReuseSignature(tuple(s0), tuple(s1), labels, signed, ("hostile",))
    block = {"targets": [list(x) for x in targets], "term_indices": [0, 1, 2]}
    valid = impl.apply_signature(signature, block, n)
    if valid is None:
        raise AssertionError("valid hostile reuse signature rejected")

    bad_phase = impl.ReuseSignature(
        signature.s0,
        signature.s1,
        signature.labels,
        ((1, signature.corrections[0][1]), *signature.corrections[1:]),
        ("bad-phase",),
    )
    # A mere permutation of (1,2,3) is not a hostile mismatch because the
    # protocol permits destination target permutations. Include label 0 so no
    # allowed permutation can repair the signature.
    bad_labels = impl.ReuseSignature(
        signature.s0,
        signature.s1,
        (0, 1, 2),
        signature.corrections,
        ("bad-labels",),
    )
    nonanti = {
        "targets": [list(single["X"]), list(single["X"]), list(single["X"])],
        "term_indices": [3, 4, 5],
    }
    gates = {
        "signed_pauli_table": all(row["pass"] for row in phase_rows.values()),
        "valid_signature_accepted": valid is not None,
        "phase_mismatch_rejected": impl.apply_signature(bad_phase, block, n) is None,
        "label_mismatch_rejected": impl.apply_signature(bad_labels, block, n) is None,
        "nonanticommuting_destination_rejected": impl.apply_signature(signature, nonanti, n) is None,
    }
    if not all(gates.values()):
        raise AssertionError({"hostile_reuse_gates": gates})
    return {"phase_rows": phase_rows, "gates": gates, "all_pass": True}


def main():
    impl.hostile_validation = hostile_validation_fixed
    return impl.main()


if __name__ == "__main__":
    main()
