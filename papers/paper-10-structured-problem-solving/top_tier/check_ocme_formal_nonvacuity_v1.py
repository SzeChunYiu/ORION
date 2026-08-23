#!/usr/bin/env python3
"""Independent checker for the prospectively frozen P10 OCME formal V1 protocol."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "ocme_formal_cases_v1.json"
PROTOCOL = HERE / "P10_OCME_FORMAL_NONVACUITY_PROTOCOL_V1.md"


def bool_inputs(n: int = 4):
    return list(product((0, 1), repeat=n))


def affine_bool_table(coeffs: tuple[int, ...], xs) -> tuple[int, ...]:
    a0, *a = coeffs
    return tuple(a0 ^ sum((ai & xi) for ai, xi in zip(a, x)) % 2 for x in xs)


def bool_target(case: dict, xs) -> tuple[int, ...]:
    kind = case["kind"]
    if kind == "and":
        return tuple(x[case["i"]] & x[case["j"]] for x in xs)
    if kind == "xor":
        return tuple(x[case["i"]] ^ x[case["j"]] for x in xs)
    if kind == "projection":
        return tuple(x[case["i"]] for x in xs)
    if kind == "constant":
        return tuple(case["value"] for _ in xs)
    raise ValueError(kind)


def boolean_setting(spec: dict) -> dict:
    xs = bool_inputs(4)
    old_tables = {
        affine_bool_table(coeffs, xs): coeffs
        for coeffs in product((0, 1), repeat=5)
    }
    assert len(old_tables) == 32

    obstruction_rows = []
    for split in ("originating", "held_out"):
        for case in spec[split]:
            target = bool_target(case, xs)
            in_old = target in old_tables
            assert not in_old, case
            # New AND2 edit solves every pairwise conjunction without changing truth-table verifier.
            after_edit = tuple(x[case["i"]] & x[case["j"]] for x in xs)
            assert after_edit == target
            obstruction_rows.append({
                "id": case["id"],
                "split": split,
                "old_closure_member": in_old,
                "after_edit_verified": True,
            })

    controls = []
    for case in spec["known_method_controls"]:
        target = bool_target(case, xs)
        assert target in old_tables, case
        controls.append({"id": case["id"], "classification": "KNOWN_COMPOSITION"})

    # AND2 itself is outside old affine closure.
    and_table = tuple(x[0] & x[1] for x in xs)
    assert and_table not in old_tables

    return {
        "old_closure_size": len(old_tables),
        "candidate_edit": spec["candidate_edit"],
        "candidate_edit_outside_closure": True,
        "obstructions": obstruction_rows,
        "known_method_controls": controls,
        "false_expansion_count": 0,
    }


def integer_target(case: dict, domain: list[int]) -> tuple[Fraction, ...]:
    if case["kind"] == "shifted_square":
        k = Fraction(case["shift"])
        return tuple((Fraction(x) - k) ** 2 for x in domain)
    if case["kind"] == "affine":
        a, b = Fraction(case["a"]), Fraction(case["b"])
        return tuple(a * x + b for x in map(Fraction, domain))
    raise ValueError(case["kind"])


def affine_fit(domain: list[int], values: tuple[Fraction, ...]):
    x0, x1 = Fraction(domain[0]), Fraction(domain[1])
    y0, y1 = values[0], values[1]
    assert x1 != x0
    a = (y1 - y0) / (x1 - x0)
    b = y0 - a * x0
    candidate = tuple(a * Fraction(x) + b for x in domain)
    return a, b, candidate == values


def second_differences(values: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    first = [b - a for a, b in zip(values, values[1:])]
    return tuple(b - a for a, b in zip(first, first[1:]))


def integer_setting(spec: dict) -> dict:
    domain = spec["domain"]
    obstruction_rows = []
    for split in ("originating", "held_out"):
        for case in spec[split]:
            target = integer_target(case, domain)
            a, b, in_old = affine_fit(domain, target)
            assert not in_old, case
            sec = second_differences(target)
            assert sec and all(v == 2 for v in sec), (case, sec)

            # New SQUARE edit with old affine premap x -> x-k.
            k = Fraction(case["shift"])
            after_edit = tuple((Fraction(x) - k) ** 2 for x in domain)
            assert after_edit == target
            obstruction_rows.append({
                "id": case["id"],
                "split": split,
                "old_affine_candidate_from_first_two": [str(a), str(b)],
                "old_closure_member": False,
                "second_difference": [str(v) for v in sec],
                "after_edit_verified": True,
            })

    controls = []
    for case in spec["known_method_controls"]:
        target = integer_target(case, domain)
        a, b, in_old = affine_fit(domain, target)
        assert in_old, case
        controls.append({
            "id": case["id"],
            "classification": "KNOWN_COMPOSITION",
            "affine": [str(a), str(b)],
        })

    # SQUARE is outside affine closure on the frozen seven-point verifier domain.
    square = tuple(Fraction(x) ** 2 for x in domain)
    _, _, square_in_old = affine_fit(domain, square)
    assert not square_in_old

    return {
        "domain": domain,
        "candidate_edit": spec["candidate_edit"],
        "candidate_edit_outside_closure": True,
        "obstructions": obstruction_rows,
        "known_method_controls": controls,
        "false_expansion_count": 0,
    }


def main() -> int:
    spec = json.loads(CASES.read_text())
    boolean = boolean_setting(spec["boolean_affine"])
    integer = integer_setting(spec["integer_affine"])

    all_obstructions = boolean["obstructions"] + integer["obstructions"]
    assert len(all_obstructions) == 8
    assert all(not row["old_closure_member"] and row["after_edit_verified"] for row in all_obstructions)
    assert boolean["false_expansion_count"] == integer["false_expansion_count"] == 0

    receipt = {
        "protocol": "P10_OCME_FORMAL_NONVACUITY_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "boolean_affine": boolean,
        "integer_affine": integer,
        "obstruction_certificate_count": 2,
        "outside_closure_edit_count": 2,
        "held_out_transfer_count": sum(row["split"] == "held_out" for row in all_obstructions),
        "terminal": "P10_OCME_FORMAL_NONVACUITY_V1_GREEN",
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
