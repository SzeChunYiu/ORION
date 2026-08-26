#!/usr/bin/env python3
"""Post-freeze runner for P10 generated OCME V1.

Selection functions receive only originating tasks and frozen candidate grammars.
Held-out tasks are evaluated only after a primitive has been selected.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "generated_ocme_cases_v1.json"
PROTOCOL_PATH = HERE / "P10_GENERATED_OCME_PROTOCOL_V1.md"

BOOL_INPUTS = list(product((0, 1), repeat=4))
BINARY_INPUTS = ((0, 0), (0, 1), (1, 0), (1, 1))


def bool_op(code: int, a: int, b: int) -> int:
    idx = BINARY_INPUTS.index((a, b))
    return (code >> idx) & 1


def majority3(x: tuple[int, ...], vars_: list[int]) -> int:
    return int(sum(x[i] for i in vars_) >= 2)


def bool_target(case: dict[str, Any]) -> tuple[int, ...]:
    kind = case["kind"]
    if kind == "majority3":
        return tuple(majority3(x, case["vars"]) for x in BOOL_INPUTS)
    if kind == "xor":
        i, j = case["vars"]
        return tuple(x[i] ^ x[j] for x in BOOL_INPUTS)
    if kind == "projection":
        i = case["var"]
        return tuple(x[i] for x in BOOL_INPUTS)
    if kind == "constant":
        return tuple(int(case["value"]) for _ in BOOL_INPUTS)
    raise ValueError(kind)


def affine_bool_tables_4() -> set[tuple[int, ...]]:
    out: set[tuple[int, ...]] = set()
    for coeffs in product((0, 1), repeat=5):
        c, *a = coeffs
        table = tuple(c ^ (sum(ai & xi for ai, xi in zip(a, x)) % 2) for x in BOOL_INPUTS)
        out.add(table)
    assert len(out) == 32
    return out


def affine_binary_codes() -> set[int]:
    codes: set[int] = set()
    for c, a, b in product((0, 1), repeat=3):
        code = 0
        for idx, (x, y) in enumerate(BINARY_INPUTS):
            code |= (c ^ (a & x) ^ (b & y)) << idx
        codes.add(code)
    assert len(codes) == 8
    return codes


def bool_template_table(code: int, vars_: list[int]) -> tuple[int, ...]:
    i, j, k = vars_
    return tuple(
        bool_op(code, x[i], x[j])
        ^ bool_op(code, x[i], x[k])
        ^ bool_op(code, x[j], x[k])
        for x in BOOL_INPUTS
    )


def select_boolean(origin: dict[str, Any], codes: list[int]) -> dict[str, Any]:
    """Selection receives no held-out tasks."""
    target = bool_target(origin)
    affine_binary = affine_binary_codes()
    evaluated = []
    survivors = []
    for code in codes:
        outside = code not in affine_binary
        exact = bool_template_table(code, origin["vars"]) == target
        weight = int(code).bit_count()
        evaluated.append({"code": code, "outside_affine": outside, "exact_origin": exact, "weight": weight})
        if outside and exact:
            survivors.append((weight, code))
    if not survivors:
        return {"selected_code": None, "evaluated": evaluated}
    _, selected = min(survivors)
    return {"selected_code": selected, "evaluated": evaluated}


def unary_value(semantic: str, x: int) -> int:
    if semantic == "ABS":
        return abs(x)
    if semantic == "SIGN":
        return -1 if x < 0 else (1 if x > 0 else 0)
    if semantic == "SQUARE":
        return x * x
    if semantic == "CUBE":
        return x * x * x
    if semantic == "FOURTH_POWER":
        return x * x * x * x
    raise ValueError(semantic)


def int_target(case: dict[str, Any], domain: list[int]) -> tuple[Fraction, ...]:
    if case["kind"] == "cubic_affine":
        a, b = Fraction(case["linear"]), Fraction(case["constant"])
        return tuple(Fraction(x**3) + a * x + b for x in domain)
    if case["kind"] == "affine":
        a, b = Fraction(case["linear"]), Fraction(case["constant"])
        return tuple(a * x + b for x in domain)
    raise ValueError(case["kind"])


def fit_affine(domain: list[int], values: tuple[Fraction, ...]) -> tuple[Fraction, Fraction] | None:
    x0, x1 = map(Fraction, domain[:2])
    y0, y1 = values[:2]
    a = (y1 - y0) / (x1 - x0)
    b = y0 - a * x0
    if all(a * Fraction(x) + b == y for x, y in zip(domain, values)):
        return a, b
    return None


def fit_primitive_wrapper(semantic: str, case: dict[str, Any], domain: list[int]) -> tuple[Fraction, Fraction] | None:
    target = int_target(case, domain)
    residual = tuple(y - Fraction(unary_value(semantic, x)) for x, y in zip(domain, target))
    return fit_affine(domain, residual)


def select_integer(origin: dict[str, Any], catalog: list[dict[str, Any]], domain: list[int]) -> dict[str, Any]:
    """Selection receives no held-out tasks."""
    evaluated = []
    survivors = []
    for row in catalog:
        semantic = row["semantic"]
        primitive_table = tuple(Fraction(unary_value(semantic, x)) for x in domain)
        outside = fit_affine(domain, primitive_table) is None
        wrapper = fit_primitive_wrapper(semantic, origin, domain)
        exact = wrapper is not None
        evaluated.append({
            "candidate_id": row["candidate_id"],
            "semantic": semantic,
            "complexity_rank": row["complexity_rank"],
            "outside_affine": outside,
            "exact_origin": exact,
            "wrapper": None if wrapper is None else [str(wrapper[0]), str(wrapper[1])],
        })
        if outside and exact:
            survivors.append((row["complexity_rank"], row["candidate_id"], semantic, wrapper))
    if not survivors:
        return {"selected": None, "evaluated": evaluated}
    rank, candidate_id, semantic, wrapper = min(survivors, key=lambda r: (r[0], r[1]))
    return {
        "selected": {
            "candidate_id": candidate_id,
            "semantic": semantic,
            "complexity_rank": rank,
            "origin_wrapper": [str(wrapper[0]), str(wrapper[1])],
        },
        "evaluated": evaluated,
    }


def main() -> int:
    spec = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    b = spec["boolean_majority"]
    b_affine = affine_bool_tables_4()
    b_origin = b["originating"]
    b_origin_target = bool_target(b_origin)
    assert b_origin_target not in b_affine
    b_selected = select_boolean(b_origin, list(b["candidate_binary_truth_table_codes"]))
    b_code = b_selected["selected_code"]
    assert b_code is not None
    b_transfer = []
    for case in b["held_out"]:  # opened only post-selection
        target = bool_target(case)
        assert target not in b_affine
        solved = bool_template_table(b_code, case["vars"]) == target
        b_transfer.append({"id": case["id"], "solved": solved})
    b_controls = []
    for case in b["known_method_controls"]:
        member = bool_target(case) in b_affine
        b_controls.append({"id": case["id"], "classification": "KNOWN_COMPOSITION" if member else "FALSE_EXPANSION"})
    b_false_expansion = sum(r["classification"] != "KNOWN_COMPOSITION" for r in b_controls)

    i = spec["integer_cubic"]
    domain = list(i["domain"])
    i_origin = i["originating"]
    assert fit_affine(domain, int_target(i_origin, domain)) is None
    i_selected = select_integer(i_origin, list(i["candidate_catalog"]), domain)
    assert i_selected["selected"] is not None
    semantic = i_selected["selected"]["semantic"]
    i_transfer = []
    for case in i["held_out"]:  # opened only post-selection
        assert fit_affine(domain, int_target(case, domain)) is None
        wrapper = fit_primitive_wrapper(semantic, case, domain)
        i_transfer.append({
            "id": case["id"],
            "solved": wrapper is not None,
            "wrapper": None if wrapper is None else [str(wrapper[0]), str(wrapper[1])],
        })
    i_controls = []
    for case in i["known_method_controls"]:
        member = fit_affine(domain, int_target(case, domain)) is not None
        i_controls.append({"id": case["id"], "classification": "KNOWN_COMPOSITION" if member else "FALSE_EXPANSION"})
    i_false_expansion = sum(r["classification"] != "KNOWN_COMPOSITION" for r in i_controls)

    positive = (
        all(r["solved"] for r in b_transfer)
        and all(r["solved"] for r in i_transfer)
        and b_false_expansion == 0
        and i_false_expansion == 0
    )

    receipt = {
        "schema": "P10.GeneratedOCMEResult.v1",
        "protocol_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(),
        "selection_contract": "ORIGIN_ONLY__HELD_OUT_OPENED_AFTER_SELECTION",
        "boolean": {
            "old_closure_size": len(b_affine),
            "origin_outside_old_closure": True,
            "selected_code": b_code,
            "selected_truth_table": [bool_op(b_code, a, c) for a, c in BINARY_INPUTS],
            "candidate_count": len(b_selected["evaluated"]),
            "held_out_transfer": b_transfer,
            "false_expansion_count": b_false_expansion,
            "controls": b_controls,
            "old_language_search_synthesis_evolution_closed": True,
        },
        "integer": {
            "domain": domain,
            "origin_outside_old_closure": True,
            "selected": i_selected["selected"],
            "candidate_count": len(i_selected["evaluated"]),
            "held_out_transfer": i_transfer,
            "false_expansion_count": i_false_expansion,
            "controls": i_controls,
            "old_language_search_synthesis_evolution_closed": True,
        },
        "generated_edit_count": 2,
        "held_out_transfer_count": sum(r["solved"] for r in b_transfer + i_transfer),
        "terminal": "P10_GENERATED_OCME_V1_SUPPORTED" if positive else "P10_GENERATED_OCME_V1_NOT_SUPPORTED",
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert positive, receipt
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
