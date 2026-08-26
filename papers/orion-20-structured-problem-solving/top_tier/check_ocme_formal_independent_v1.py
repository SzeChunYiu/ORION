#!/usr/bin/env python3
"""Second independent verifier for the frozen P10 OCME formal V1 object.

This checker deliberately uses different membership tests from
``check_ocme_formal_nonvacuity_v1.py``:

* Boolean-affine closure is recognized by algebraic-normal-form degree, not by
  enumerating all affine truth tables.
* Integer-affine closure is recognized by exact three-point collinearity over all
  triples, not by fitting the first two points or inspecting second differences.

It reads only the prospectively frozen protocol/cases and never imports or invokes
the primary checker.  Authority is limited to the finite OCME V1 object.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CASES = HERE / "ocme_formal_cases_v1.json"
PROTOCOL = HERE / "P10_OCME_FORMAL_NONVACUITY_PROTOCOL_V1.md"


def bool_value(case: dict[str, Any], x: tuple[int, ...]) -> int:
    kind = case["kind"]
    if kind == "and":
        return x[case["i"]] & x[case["j"]]
    if kind == "xor":
        return x[case["i"]] ^ x[case["j"]]
    if kind == "projection":
        return x[case["i"]]
    if kind == "constant":
        return int(case["value"])
    raise ValueError(kind)


def anf_coefficients(case: dict[str, Any], n: int = 4) -> list[int]:
    """Return GF(2) algebraic-normal-form coefficients by Möbius transform."""

    values = []
    for mask in range(1 << n):
        x = tuple((mask >> bit) & 1 for bit in range(n))
        values.append(bool_value(case, x))
    coeffs = values[:]
    for bit in range(n):
        for mask in range(1 << n):
            if mask & (1 << bit):
                coeffs[mask] ^= coeffs[mask ^ (1 << bit)]
    return coeffs


def anf_degree(case: dict[str, Any], n: int = 4) -> int:
    coeffs = anf_coefficients(case, n)
    active = [mask.bit_count() for mask, coefficient in enumerate(coeffs) if coefficient]
    return max(active, default=0)


def bool_affine_member(case: dict[str, Any]) -> bool:
    return anf_degree(case) <= 1


def boolean_setting(spec: dict[str, Any]) -> dict[str, Any]:
    obstruction_rows = []
    for split in ("originating", "held_out"):
        for case in spec[split]:
            degree = anf_degree(case)
            if degree <= 1:
                raise SystemExit(f"Boolean obstruction unexpectedly affine: {case['id']}")
            # The registered AND2 primitive must reproduce the frozen target exactly.
            for mask in range(16):
                x = tuple((mask >> bit) & 1 for bit in range(4))
                expected = bool_value(case, x)
                after_edit = x[case["i"]] & x[case["j"]]
                if expected != after_edit:
                    raise SystemExit(f"AND2 transfer failure: {case['id']}")
            obstruction_rows.append(
                {
                    "id": case["id"],
                    "split": split,
                    "anf_degree": degree,
                    "old_closure_member": False,
                    "after_edit_verified": True,
                }
            )

    controls = []
    for case in spec["known_method_controls"]:
        degree = anf_degree(case)
        if degree > 1:
            raise SystemExit(f"Boolean known-method control outside affine closure: {case['id']}")
        controls.append(
            {
                "id": case["id"],
                "classification": "KNOWN_COMPOSITION",
                "anf_degree": degree,
            }
        )

    and2_case = {"kind": "and", "i": 0, "j": 1}
    if bool_affine_member(and2_case):
        raise SystemExit("registered AND2 primitive is not outside Boolean-affine closure")

    return {
        "candidate_edit": spec["candidate_edit"],
        "candidate_edit_outside_closure": True,
        "membership_test": "GF2_ALGEBRAIC_NORMAL_FORM_DEGREE_LE_1",
        "obstructions": obstruction_rows,
        "known_method_controls": controls,
        "false_expansion_count": 0,
    }


def integer_values(case: dict[str, Any], domain: list[int]) -> list[Fraction]:
    kind = case["kind"]
    if kind == "shifted_square":
        shift = Fraction(case["shift"])
        return [(Fraction(x) - shift) ** 2 for x in domain]
    if kind == "affine":
        a, b = Fraction(case["a"]), Fraction(case["b"])
        return [a * Fraction(x) + b for x in domain]
    raise ValueError(kind)


def violating_collinearity_triple(
    domain: list[int], values: list[Fraction]
) -> tuple[int, int, int] | None:
    """Return the first non-collinear triple, or None iff all points are affine."""

    for i, j, k in combinations(range(len(domain)), 3):
        xi, xj, xk = map(Fraction, (domain[i], domain[j], domain[k]))
        yi, yj, yk = values[i], values[j], values[k]
        left = (yj - yi) * (xk - xi)
        right = (yk - yi) * (xj - xi)
        if left != right:
            return i, j, k
    return None


def integer_affine_member(case: dict[str, Any], domain: list[int]) -> bool:
    return violating_collinearity_triple(domain, integer_values(case, domain)) is None


def integer_setting(spec: dict[str, Any]) -> dict[str, Any]:
    domain = list(spec["domain"])
    obstruction_rows = []
    for split in ("originating", "held_out"):
        for case in spec[split]:
            values = integer_values(case, domain)
            witness = violating_collinearity_triple(domain, values)
            if witness is None:
                raise SystemExit(f"integer obstruction unexpectedly affine: {case['id']}")

            shift = Fraction(case["shift"])
            after_edit = [(Fraction(x) - shift) ** 2 for x in domain]
            if after_edit != values:
                raise SystemExit(f"SQUARE transfer failure: {case['id']}")
            obstruction_rows.append(
                {
                    "id": case["id"],
                    "split": split,
                    "old_closure_member": False,
                    "first_noncollinear_index_triple": list(witness),
                    "after_edit_verified": True,
                }
            )

    controls = []
    for case in spec["known_method_controls"]:
        if not integer_affine_member(case, domain):
            raise SystemExit(f"integer known-method control outside affine closure: {case['id']}")
        controls.append({"id": case["id"], "classification": "KNOWN_COMPOSITION"})

    square_case = {"kind": "shifted_square", "shift": 0}
    if integer_affine_member(square_case, domain):
        raise SystemExit("registered SQUARE primitive is not outside integer-affine closure")

    return {
        "domain": domain,
        "candidate_edit": spec["candidate_edit"],
        "candidate_edit_outside_closure": True,
        "membership_test": "EXACT_ALL_TRIPLES_COLLINEARITY",
        "obstructions": obstruction_rows,
        "known_method_controls": controls,
        "false_expansion_count": 0,
    }


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    spec = json.loads(CASES.read_text(encoding="utf-8"))
    boolean = boolean_setting(spec["boolean_affine"])
    integer = integer_setting(spec["integer_affine"])

    all_obstructions = boolean["obstructions"] + integer["obstructions"]
    if len(all_obstructions) != 8:
        raise SystemExit(f"expected 8 frozen obstruction instances, found {len(all_obstructions)}")
    held_out = sum(row["split"] == "held_out" for row in all_obstructions)
    if held_out != 6:
        raise SystemExit(f"expected 6 held-out transfer instances, found {held_out}")
    if boolean["false_expansion_count"] or integer["false_expansion_count"]:
        raise SystemExit("known-method control falsely classified as expansion")

    receipt: dict[str, Any] = {
        "schema": "P10.OCMEFormalIndependentVerification.v1",
        "protocol": "P10_OCME_FORMAL_NONVACUITY_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "boolean_affine": boolean,
        "integer_affine": integer,
        "obstruction_certificate_count": 2,
        "outside_closure_edit_count": 2,
        "held_out_transfer_count": held_out,
        "implementation_independence": (
            "NO_PRIMARY_CHECKER_IMPORT__ANF_AND_COLLINEARITY_MEMBERSHIP_TESTS"
        ),
        "claim_authority": "FROZEN_P10_OCME_FORMAL_V1_VERIFICATION_ONLY",
        "terminal": "P10_OCME_FORMAL_SECOND_INDEPENDENT_CHECKER_GREEN",
    }
    receipt["receipt_sha256"] = canonical_digest(receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
