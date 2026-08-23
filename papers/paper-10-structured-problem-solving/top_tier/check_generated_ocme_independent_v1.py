#!/usr/bin/env python3
"""Structurally independent verifier for P10 generated OCME V1.

Uses Boolean affine parallelogram identities and integer all-triples collinearity;
does not import the primary runner.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product, combinations
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "generated_ocme_cases_v1.json"
PROTOCOL_PATH = HERE / "P10_GENERATED_OCME_PROTOCOL_V1.md"
B4 = list(product((0, 1), repeat=4))
B2 = ((0, 0), (0, 1), (1, 0), (1, 1))


def op(code: int, a: int, b: int) -> int:
    idx = B2.index((a, b))
    return (code >> idx) & 1


def maj(x: tuple[int, ...], vs: list[int]) -> int:
    return int(sum(x[v] for v in vs) >= 2)


def table(case: dict[str, Any]) -> tuple[int, ...]:
    if case["kind"] == "majority3":
        return tuple(maj(x, case["vars"]) for x in B4)
    if case["kind"] == "xor":
        i, j = case["vars"]
        return tuple(x[i] ^ x[j] for x in B4)
    if case["kind"] == "projection":
        return tuple(x[case["var"]] for x in B4)
    if case["kind"] == "constant":
        return tuple(case["value"] for _ in B4)
    raise ValueError(case["kind"])


def bool_affine_by_second_derivatives(values: tuple[int, ...]) -> bool:
    lookup = {x: y for x, y in zip(B4, values)}
    for x in B4:
        for i, j in combinations(range(4), 2):
            xi = list(x); xi[i] ^= 1; xi = tuple(xi)
            xj = list(x); xj[j] ^= 1; xj = tuple(xj)
            xij = list(x); xij[i] ^= 1; xij[j] ^= 1; xij = tuple(xij)
            if lookup[x] ^ lookup[xi] ^ lookup[xj] ^ lookup[xij]:
                return False
    return True


def binary_affine(code: int) -> bool:
    vals = [op(code, a, b) for a, b in B2]
    return (vals[0] ^ vals[1] ^ vals[2] ^ vals[3]) == 0


def template(code: int, vs: list[int]) -> tuple[int, ...]:
    i, j, k = vs
    return tuple(op(code, x[i], x[j]) ^ op(code, x[i], x[k]) ^ op(code, x[j], x[k]) for x in B4)


def select_bool(origin: dict[str, Any], codes: list[int]) -> int | None:
    tgt = table(origin)
    candidates = []
    for code in codes:
        if not binary_affine(code) and template(code, origin["vars"]) == tgt:
            candidates.append((int(code).bit_count(), int(code)))
    return min(candidates)[1] if candidates else None


def unary(semantic: str, x: int) -> Fraction:
    if semantic == "ABS": return Fraction(abs(x))
    if semantic == "SIGN": return Fraction(-1 if x < 0 else (1 if x > 0 else 0))
    if semantic == "SQUARE": return Fraction(x*x)
    if semantic == "CUBE": return Fraction(x*x*x)
    if semantic == "FOURTH_POWER": return Fraction(x*x*x*x)
    raise ValueError(semantic)


def int_values(case: dict[str, Any], domain: list[int]) -> tuple[Fraction, ...]:
    if case["kind"] == "cubic_affine":
        return tuple(Fraction(x**3 + case["linear"]*x + case["constant"]) for x in domain)
    if case["kind"] == "affine":
        return tuple(Fraction(case["linear"]*x + case["constant"]) for x in domain)
    raise ValueError(case["kind"])


def collinear(domain: list[int], values: tuple[Fraction, ...]) -> bool:
    pts = [(Fraction(x), y) for x, y in zip(domain, values)]
    for (x1,y1),(x2,y2),(x3,y3) in combinations(pts, 3):
        if (y2-y1)*(x3-x1) != (y3-y1)*(x2-x1):
            return False
    return True


def wrapper_exact(semantic: str, case: dict[str, Any], domain: list[int]) -> bool:
    residual = tuple(y - unary(semantic, x) for x, y in zip(domain, int_values(case, domain)))
    return collinear(domain, residual)


def select_int(origin: dict[str, Any], catalog: list[dict[str, Any]], domain: list[int]) -> dict[str, Any] | None:
    candidates = []
    for row in catalog:
        primitive = tuple(unary(row["semantic"], x) for x in domain)
        outside = not collinear(domain, primitive)
        exact = wrapper_exact(row["semantic"], origin, domain)
        if outside and exact:
            candidates.append((row["complexity_rank"], row["candidate_id"], row["semantic"]))
    if not candidates:
        return None
    rank, candidate_id, semantic = min(candidates)
    return {"candidate_id": candidate_id, "semantic": semantic, "complexity_rank": rank}


def main() -> int:
    spec = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    b = spec["boolean_majority"]
    assert not bool_affine_by_second_derivatives(table(b["originating"]))
    b_code = select_bool(b["originating"], list(b["candidate_binary_truth_table_codes"]))
    assert b_code is not None
    b_transfer = [template(b_code, c["vars"]) == table(c) for c in b["held_out"]]
    b_controls = [bool_affine_by_second_derivatives(table(c)) for c in b["known_method_controls"]]

    i = spec["integer_cubic"]
    domain = list(i["domain"])
    assert not collinear(domain, int_values(i["originating"], domain))
    i_sel = select_int(i["originating"], list(i["candidate_catalog"]), domain)
    assert i_sel is not None
    i_transfer = [wrapper_exact(i_sel["semantic"], c, domain) for c in i["held_out"]]
    i_controls = [collinear(domain, int_values(c, domain)) for c in i["known_method_controls"]]

    assert all(b_transfer) and all(i_transfer)
    assert all(b_controls) and all(i_controls)
    payload = {
        "schema": "P10.GeneratedOCMEIndependentVerification.v1",
        "protocol_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(),
        "boolean_selected_code": b_code,
        "integer_selected": i_sel,
        "held_out_transfer_count": sum(b_transfer) + sum(i_transfer),
        "false_expansion_count": 0,
        "terminal": "P10_GENERATED_OCME_SECOND_INDEPENDENT_CHECKER_GREEN",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
