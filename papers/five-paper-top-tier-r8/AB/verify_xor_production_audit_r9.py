#!/usr/bin/env python3
"""Independent production-realization and interaction audit for the F_2^5 XOR grammar."""
from __future__ import annotations

import collections
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "ORION.AB.XORProductionAuditR9.Results.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def xor_sum(values: Iterable[int]) -> int:
    total = 0
    for value in values:
        total ^= value
    return total


def canonical(word: Iterable[int]) -> tuple[int, ...]:
    return tuple(sorted(word))


def zero_deletion_moves(word: Sequence[int]) -> list[dict[str, Any]]:
    n = len(word)
    moves: list[dict[str, Any]] = []
    seen: set[tuple[int, ...]] = set()
    for mask in range(1, (1 << n) - 1):
        deleted = tuple(word[index] for index in range(n) if (mask >> index) & 1)
        if xor_sum(deleted) != 0:
            continue
        successor = canonical(word[index] for index in range(n) if not ((mask >> index) & 1))
        if successor in seen:
            continue
        seen.add(successor)
        moves.append(
            {
                "schema": "DELETE_ZERO",
                "operands": list(deleted),
                "successor": list(successor),
            }
        )
    return moves


def fusion_moves(word: Sequence[int]) -> list[dict[str, Any]]:
    moves: list[dict[str, Any]] = []
    seen: set[tuple[int, ...]] = set()
    for left in range(len(word)):
        for right in range(left + 1, len(word)):
            a, b = word[left], word[right]
            if a == b:
                continue
            fused = a ^ b
            assert fused != 0
            successor = canonical(
                [word[index] for index in range(len(word)) if index not in (left, right)] + [fused]
            )
            if successor in seen:
                continue
            seen.add(successor)
            moves.append(
                {
                    "schema": "FUSE_DISTINCT_PAIR",
                    "operands": [a, b],
                    "result": fused,
                    "successor": list(successor),
                }
            )
    return moves


def strong_moves(word: Sequence[int]) -> list[dict[str, Any]]:
    return zero_deletion_moves(word) + fusion_moves(word)


def reduce_to_unique_normal_form(word: Sequence[int]) -> tuple[int, ...]:
    current = list(word)
    assert current and xor_sum(current) != 0
    while len(current) > 1:
        pair = next(
            (
                (left, right)
                for left in range(len(current))
                for right in range(left + 1, len(current))
                if current[left] == current[right]
            ),
            None,
        )
        if pair is not None:
            left, right = pair
            current = [value for index, value in enumerate(current) if index not in (left, right)]
            assert current
            continue
        a = current.pop()
        b = current.pop()
        current.append(a ^ b)
        current.sort()
    assert current[0] == xor_sum(word)
    return (current[0],)


def weak_terminal(word: Sequence[int]) -> bool:
    return xor_sum(word) != 0 and not zero_deletion_moves(word)


def check_move_invariants(word: Sequence[int], move: dict[str, Any]) -> None:
    successor = tuple(move["successor"])
    assert successor
    assert all(value > 0 for value in successor)
    assert xor_sum(successor) == xor_sum(word)
    assert len(successor) < len(word)


def exhaustive_dimension(dimension: int) -> dict[str, Any]:
    alphabet = tuple(range(1, 1 << dimension))
    maximum_length = dimension + 1
    states = 0
    moves = 0
    local_peaks = 0
    local_peak_mismatches = 0
    weak_maximum = 0
    weak_witness: tuple[int, ...] | None = None
    strong_terminal_maximum = 0
    schema_counts: collections.Counter[str] = collections.Counter()
    interaction_counts: collections.Counter[str] = collections.Counter()

    for length in range(1, maximum_length + 1):
        for word in itertools.combinations_with_replacement(alphabet, length):
            if xor_sum(word) == 0:
                continue
            states += 1
            if weak_terminal(word) and length > weak_maximum:
                weak_maximum = length
                weak_witness = word
            successors = strong_moves(word)
            if not successors:
                strong_terminal_maximum = max(strong_terminal_maximum, length)
            for move in successors:
                check_move_invariants(word, move)
                moves += 1
                schema_counts[move["schema"]] += 1
            for first_index in range(len(successors)):
                for second_index in range(first_index + 1, len(successors)):
                    first = successors[first_index]
                    second = successors[second_index]
                    local_peaks += 1
                    interaction_counts["--".join(sorted((first["schema"], second["schema"])))] += 1
                    normal_first = reduce_to_unique_normal_form(first["successor"])
                    normal_second = reduce_to_unique_normal_form(second["successor"])
                    if normal_first != normal_second:
                        local_peak_mismatches += 1
    basis = tuple(1 << index for index in range(dimension))
    assert weak_terminal(basis)
    assert weak_maximum == dimension
    assert strong_terminal_maximum == 1
    assert local_peak_mismatches == 0
    return {
        "dimension": dimension,
        "alphabet_size": len(alphabet),
        "maximum_state_length": maximum_length,
        "states_checked": states,
        "moves_checked": moves,
        "move_schema_counts": dict(sorted(schema_counts.items())),
        "local_peaks_checked": local_peaks,
        "interaction_class_counts": dict(sorted(interaction_counts.items())),
        "local_peak_mismatches": local_peak_mismatches,
        "weak_terminal_budget": weak_maximum,
        "weak_witness": list(weak_witness or ()),
        "strong_terminal_budget": strong_terminal_maximum,
        "status": "FINITE_EXACT",
    }


def direct_enumerator_volume(n: int, q: int, cap: int) -> int:
    return sum(__import__("math").comb(n, support) * (q**support) for support in range(cap + 1))


def main() -> None:
    dimension = 5
    basis = tuple(1 << index for index in range(dimension))
    total = xor_sum(basis)
    assert total == 31
    assert weak_terminal(basis)
    strong_normal = reduce_to_unique_normal_form(basis)
    assert strong_normal == (31,)

    finite_controls = [exhaustive_dimension(dimension) for dimension in (2, 3, 4)]
    q = (1 << dimension) - 1
    scaling = []
    for n in (10, 20, 50, 100, 200):
        weak_volume = direct_enumerator_volume(n, q, 5)
        strong_volume = direct_enumerator_volume(n, q, 1)
        scaling.append(
            {
                "coordinate_count": n,
                "local_nonidentity_labels": q,
                "weak_cap_5_candidates": weak_volume,
                "strong_cap_1_candidates": strong_volume,
                "exact_candidate_ratio": weak_volume / strong_volume,
            }
        )

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "grammar": {
            "dimension": dimension,
            "state": "finite multiset of nonzero F_2^5 vectors with nonzero XOR total",
            "objective": "multiset cardinality",
            "weak_proof_language": ["DELETE_ZERO"],
            "complete_production_move_registry": ["DELETE_ZERO", "FUSE_DISTINCT_PAIR"],
            "completeness_basis": "the production grammar is defined to admit exactly these two universally quantified schemas",
        },
        "realization": {
            "map": "identity multiset representation",
            "support_preserved": True,
            "weak_terminal_word": list(basis),
            "weak_terminal_support": len(basis),
            "production_preimage": list(basis),
            "weak_irreducible": True,
            "strong_normal_form": list(strong_normal),
            "intrinsic_support": 1,
            "support_zero_infeasible": True,
            "certificate_waste": 4,
        },
        "symbolic_audit": {
            "termination_measure": "support strictly decreases under every move",
            "semantic_invariant": "total XOR",
            "unique_normal_form": "singleton containing the nonzero total XOR",
            "confluence_reason": "all successors preserve total XOR and reduce to the same singleton",
            "critical_interaction_classes": [
                "DELETE_ZERO--DELETE_ZERO",
                "DELETE_ZERO--FUSE_DISTINCT_PAIR",
                "FUSE_DISTINCT_PAIR--FUSE_DISTINCT_PAIR",
            ],
            "all_interactions_join_by_unique_normal_form": True,
        },
        "finite_controls": finite_controls,
        "direct_enumerator_scaling": scaling,
        "authority": {
            "realized_weak_certificate_budget_5": True,
            "complete_defined_production_intrinsic_support_1": True,
            "production_certificate_gap_5_to_1": True,
            "equivalent_to_full_TARE_or_hardware_compiler": False,
            "algorithm_independent_runtime_lower_bound": False,
            "external_significance_review": False,
            "grants_journal_authority": False,
        },
        "terminal": "AB_REALIZED_CERTIFICATE_GAP_WITH_COMPLETE_MOVE_AUDIT__EXPLICIT_XOR_GRAMMAR",
    }
    result["content_sha256"] = digest(result)
    output = Path(__file__).with_name("PRODUCTION_AUDIT_R9_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
