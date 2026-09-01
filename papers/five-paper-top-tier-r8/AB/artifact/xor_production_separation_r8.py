#!/usr/bin/env python3
"""Exact finite controls for a complete XOR-aggregation production separation.

Weak proof language: delete a nonempty proper zero-XOR submultiset.
Strong production language: weak deletions plus pair fusion u,v -> u xor v
for distinct nonzero u,v. Equal pairs are already weakly deletable.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "ORION.XORProductionSeparationR8.Results.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def xor_sum(values: Iterable[int]) -> int:
    total = 0
    for value in values:
        total ^= value
    return total


def has_proper_zero_submultiset(word: Sequence[int]) -> bool:
    n = len(word)
    for mask in range(1, (1 << n) - 1):
        total = 0
        for i, value in enumerate(word):
            if (mask >> i) & 1:
                total ^= value
        if total == 0:
            return True
    return False


def weak_terminal(word: Sequence[int]) -> bool:
    return xor_sum(word) != 0 and not has_proper_zero_submultiset(word)


def strong_terminal(word: Sequence[int]) -> bool:
    if xor_sum(word) == 0:
        return False
    if has_proper_zero_submultiset(word):
        return False
    if len(word) <= 1:
        return True
    # If a pair is equal it is a zero-XOR deletion. Otherwise any distinct pair
    # can be fused to its nonzero XOR, strictly reducing fragment count.
    return False


def reduce_strong(word: Sequence[int]) -> tuple[int, list[dict[str, Any]]]:
    current = list(word)
    trace: list[dict[str, Any]] = []
    while len(current) > 1:
        found_equal = False
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                if current[i] == current[j]:
                    a = current[i]
                    current = [v for k, v in enumerate(current) if k not in (i, j)]
                    trace.append({"move": "DELETE_EQUAL_PAIR", "operands": [a, a], "state": current[:]})
                    found_equal = True
                    break
            if found_equal:
                break
        if found_equal:
            if not current:
                raise AssertionError("nonzero-total word cannot reduce to empty")
            continue
        a = current.pop()
        b = current.pop()
        fused = a ^ b
        assert fused != 0
        current.append(fused)
        current.sort()
        trace.append({"move": "FUSE", "operands": [a, b], "result": fused, "state": current[:]})
    assert current[0] == xor_sum(word)
    return current[0], trace


def enumerate_dimension(dimension: int) -> dict[str, Any]:
    alphabet = tuple(range(1, 1 << dimension))
    max_length = dimension + 1
    weak_max = 0
    strong_max = 0
    weak_witness: list[int] | None = None
    strong_witness: list[int] | None = None
    tested = 0
    weak_terminal_count = 0
    strong_terminal_count = 0
    for length in range(1, max_length + 1):
        for word in itertools.combinations_with_replacement(alphabet, length):
            if xor_sum(word) == 0:
                continue
            tested += 1
            if weak_terminal(word):
                weak_terminal_count += 1
                if length > weak_max:
                    weak_max = length
                    weak_witness = list(word)
            if strong_terminal(word):
                strong_terminal_count += 1
                if length > strong_max:
                    strong_max = length
                    strong_witness = list(word)
            terminal, _ = reduce_strong(word)
            assert terminal == xor_sum(word)
    basis = [1 << i for i in range(dimension)]
    assert weak_terminal(basis)
    assert weak_max == dimension
    assert strong_max == 1
    return {
        "dimension": dimension,
        "alphabet_size": len(alphabet),
        "maximum_tested_length": max_length,
        "nonzero_total_multisets_tested": tested,
        "weak_terminal_count": weak_terminal_count,
        "strong_terminal_count": strong_terminal_count,
        "weak_terminal_budget": weak_max,
        "strong_terminal_budget": strong_max,
        "certificate_waste": weak_max - strong_max,
        "weak_maximum_witness": weak_witness,
        "strong_maximum_witness": strong_witness,
        "basis_production_witness": basis,
        "basis_strong_reduction": reduce_strong(basis)[1],
        "status": "FINITE_EXACT",
    }


def main() -> None:
    dimensions = [enumerate_dimension(d) for d in (2, 3, 4)]
    result = {
        "schema": SCHEMA,
        "model": {
            "state": "nonzero-total multiset of nonzero F_2^d parity fragments",
            "weak_moves": "proper zero-XOR deletion",
            "strong_moves": "weak moves plus fusion of two distinct fragments into their XOR",
            "objective": "number of live parity fragments",
        },
        "theorem_claim": {
            "weak_terminal_budget": "d",
            "strong_terminal_budget": "1",
            "production_gap": "d-1",
            "basis_word_is_realized_weak_terminal": True,
        },
        "finite_controls": dimensions,
        "authority": {
            "symbolic_proof_required_for_all_d": True,
            "finite_controls_pass": True,
            "production_system_is_complete_by_definition": True,
            "hardware_or_runtime_benefit": False,
            "grants_scientific_authority": False,
        },
    }
    result["content_sha256"] = sha256(result)
    output = Path(__file__).with_name("XOR_PRODUCTION_SEPARATION_R8_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
