#!/usr/bin/env python3
"""Mechanism-matched revival attempts for four unfinished ORION-06 negatives.

R4C and R5B receive new resource-objective computations on already-open
subjects. R6I and R6K receive explicitly retrospective exact replays of the
already-public R6K and R6L mechanisms. Nothing in this runner grants novelty,
external independence, R6, submission, or final-freeze authority.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import sys
import urllib.request
from typing import Any, Iterable, Iterator, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROTOCOL_PATH = HERE / "ORION06_NEGATIVE_REVIVAL_R1_PROTOCOL.json"
TARGET_PARITY = 0b101
CODE_BITS = ((0, 0), (1, 0), (1, 1), (0, 1))  # I, X, Y, Z
BITS_CODE = {bits: code for code, bits in enumerate(CODE_BITS)}
POINT_COORDS = (
    "Lambda_joint",
    "parity_CNOT",
    "controlled_Rz",
    "controlled_H",
    "controlled_Pauli_support",
    "AND2_compute_uncompute_pairs",
    "max_extra_conjunction_scratch",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def perfect_matchings(items: tuple[int, ...]) -> Iterator[tuple[tuple[int, int], ...]]:
    """Yield every perfect matching once in recursive lexicographic order."""
    if not items:
        yield tuple()
        return
    first = items[0]
    for position in range(1, len(items)):
        second = items[position]
        rest = items[1:position] + items[position + 1 :]
        for tail in perfect_matchings(rest):
            yield ((first, second),) + tail


def weight(key: tuple[int, int]) -> int:
    return (key[0] | key[1]).bit_count()


def multiply(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] ^ right[0], left[1] ^ right[1]


def symplectic(left: tuple[int, int], right: tuple[int, int]) -> int:
    return (
        (left[0] & right[1]).bit_count() + (left[1] & right[0]).bit_count()
    ) & 1


def local_multiply(left: int, right: int) -> int:
    lx, lz = CODE_BITS[left]
    rx, rz = CODE_BITS[right]
    return BITS_CODE[(lx ^ rx, lz ^ rz)]


def local_symplectic(left: int, right: int) -> int:
    lx, lz = CODE_BITS[left]
    rx, rz = CODE_BITS[right]
    return (lx * rz ^ lz * rx) & 1


def local_codes(key: tuple[int, int], n: int) -> tuple[int, ...]:
    x, z = key
    return tuple(BITS_CODE[((x >> q) & 1, (z >> q) & 1)] for q in range(n))


def mask_from_codes(codes: Sequence[int]) -> tuple[int, int]:
    x = z = 0
    for q, code in enumerate(codes):
        bx, bz = CODE_BITS[int(code)]
        x |= bx << q
        z |= bz << q
    return x, z


def pauli_word_key(word: str) -> tuple[int, int]:
    codes = {"I": 0, "X": 1, "Y": 2, "Z": 3}
    if not word or any(letter not in codes for letter in word):
        raise ValueError(word)
    return mask_from_codes([codes[letter] for letter in word])


def _local_delta(r0: int, r1: int, s: int) -> int:
    return (
        local_symplectic(r0, r1)
        | (local_symplectic(s, r0) << 1)
        | (local_symplectic(s, r1) << 2)
    )


@lru_cache(maxsize=None)
def _scalar_local_options(p0: int, p1: int) -> tuple[tuple[int, tuple[int, int, int]], ...]:
    rows: list[list[tuple[int, tuple[int, int, int]]]] = [[] for _ in range(8)]
    for r0, r1, s in itertools.product(range(4), repeat=3):
        t0 = local_multiply(p0, r0)
        t1 = local_multiply(p1, r1)
        cost = (
            4 * int(r0 != 0)
            + 2 * int(r1 != 0)
            + 2 * int(s != 0)
            + int(t0 != 0)
            + int(t1 != 0)
        )
        rows[_local_delta(r0, r1, s)].append((cost, (r0, r1, s)))
    return tuple(min(row, key=lambda item: (item[0], item[1])) for row in rows)


def _canonical_orientation(
    p0_key: tuple[int, int], p1_key: tuple[int, int], n: int
) -> tuple[int, tuple[tuple[int, int, int], ...]]:
    states: dict[int, tuple[int, tuple[tuple[int, int, int], ...]]] = {0: (0, tuple())}
    for p0, p1 in zip(local_codes(p0_key, n), local_codes(p1_key, n), strict=True):
        local = _scalar_local_options(p0, p1)
        nxt: dict[int, tuple[int, tuple[tuple[int, int, int], ...]]] = {}
        for previous, (cost, sequence) in states.items():
            for delta, (local_cost, triple) in enumerate(local):
                parity = previous ^ delta
                candidate = cost + local_cost, sequence + (triple,)
                if parity not in nxt or candidate < nxt[parity]:
                    nxt[parity] = candidate
        states = nxt
    raw_cost, sequence = states[TARGET_PARITY]
    return raw_cost - 6, sequence


def _tare_row_from_sequence(
    ordered_targets: tuple[tuple[int, int], tuple[int, int]],
    sequence: tuple[tuple[int, int, int], ...],
    orientation: int,
    expected_internal_cost: int | None = None,
) -> dict[str, Any]:
    a, b = ordered_targets
    r0 = mask_from_codes([triple[0] for triple in sequence])
    r1 = mask_from_codes([triple[1] for triple in sequence])
    s = mask_from_codes([triple[2] for triple in sequence])
    t0 = multiply(a, r0)
    t1 = multiply(b, r1)
    t01 = multiply(t0, t1)
    parity = 4 * (weight(r0) - 1) + 2 * (weight(r1) - 1)
    controlled_support = 2 * weight(s) + min(weight(t0), weight(t1)) + weight(t01)
    internal = parity + 2 * weight(s) + weight(t0) + weight(t1)
    checks = {
        "R0_anticommutes_R1": symplectic(r0, r1) == 1,
        "S_commutes_R0": symplectic(s, r0) == 0,
        "S_anticommutes_R1": symplectic(s, r1) == 1,
        "T0R0_equals_P0_bits": multiply(t0, r0) == a,
        "T1R1_equals_P1_bits": multiply(t1, r1) == b,
        "controlled_support_recomputed": controlled_support
        == 2 * weight(s) + min(weight(t0), weight(t1)) + weight(multiply(t0, t1)),
        "internal_cost_recomputed": expected_internal_cost is None
        or internal == expected_internal_cost,
    }
    if not all(checks.values()):
        raise AssertionError({"tare_witness_failure": checks})
    return {
        "type": "TARE_M2",
        "orientation": orientation,
        "ordered_targets": [list(a), list(b)],
        "R0": list(r0),
        "R1": list(r1),
        "S": list(s),
        "T0": list(t0),
        "T1": list(t1),
        "G_internal_2q": internal,
        "parity_CNOT": parity,
        "controlled_Rz": 3,
        "controlled_H": 3,
        "controlled_Pauli_support": controlled_support,
        "AND2_compute_uncompute_pairs": 2,
        "max_extra_conjunction_scratch": 1,
        "checks": checks,
    }


@lru_cache(maxsize=200000)
def canonical_pair_witness(
    first: tuple[int, int], second: tuple[int, int], n: int
) -> dict[str, Any]:
    if symplectic(first, second) == 1:
        candidates = []
        for orientation, (a, b) in enumerate(((first, second), (second, first))):
            parity = 4 * (weight(a) - 1) + 2 * (weight(b) - 1)
            candidates.append((parity, orientation, a, b))
        parity, orientation, a, b = min(candidates)
        return {
            "type": "DIRECT_ANTI_UNITARY",
            "orientation": orientation,
            "ordered_targets": [list(a), list(b)],
            "G_internal_2q": parity,
            "parity_CNOT": parity,
            "controlled_Rz": 3,
            "controlled_H": 0,
            "controlled_Pauli_support": 0,
            "AND2_compute_uncompute_pairs": 0,
            "max_extra_conjunction_scratch": 0,
            "checks": {"targets_anticommute": symplectic(a, b) == 1},
        }
    choices = []
    for orientation, (a, b) in enumerate(((first, second), (second, first))):
        internal, sequence = _canonical_orientation(a, b, n)
        choices.append((internal, orientation, sequence, a, b))
    internal, orientation, sequence, a, b = min(
        choices, key=lambda row: (row[0], row[1], row[2])
    )
    return _tare_row_from_sequence((a, b), sequence, orientation, internal)


def _dominates_tuple(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return all(a <= b for a, b in zip(left, right, strict=True)) and left != right


def _prune_vector_map(
    rows: dict[tuple[int, ...], tuple[tuple[int, int, int], ...]]
) -> dict[tuple[int, ...], tuple[tuple[int, int, int], ...]]:
    ordered = sorted(rows.items(), key=lambda item: (sum(item[0]), item[0], item[1]))
    kept: list[tuple[tuple[int, ...], tuple[tuple[int, int, int], ...]]] = []
    for vector, sequence in ordered:
        if any(_dominates_tuple(previous, vector) for previous, _ in kept):
            continue
        kept = [row for row in kept if not _dominates_tuple(vector, row[0])]
        kept.append((vector, sequence))
    return dict(kept)


@lru_cache(maxsize=None)
def _pareto_local_options(
    p0: int, p1: int
) -> tuple[tuple[tuple[int, ...], tuple[int, int, int]], ...]:
    by_delta: list[dict[tuple[int, ...], tuple[int, int, int]]] = [dict() for _ in range(8)]
    for r0, r1, s in itertools.product(range(4), repeat=3):
        t0 = local_multiply(p0, r0)
        t1 = local_multiply(p1, r1)
        t01 = local_multiply(t0, t1)
        vector = (
            4 * int(r0 != 0) + 2 * int(r1 != 0),
            2 * int(s != 0),
            int(t0 != 0),
            int(t1 != 0),
            int(t01 != 0),
        )
        delta = _local_delta(r0, r1, s)
        triple = (r0, r1, s)
        old = by_delta[delta].get(vector)
        if old is None or triple < old:
            by_delta[delta][vector] = triple
    rows = []
    for delta, mapping in enumerate(by_delta):
        pruned = _prune_vector_map({vector: (triple,) for vector, triple in mapping.items()})
        for vector, sequence in pruned.items():
            rows.append((delta, vector, sequence[0]))
    return tuple(rows)


def _controlled_orientation_frontier(
    first: tuple[int, int], second: tuple[int, int], n: int, orientation: int
) -> list[dict[str, Any]]:
    states: dict[int, dict[tuple[int, ...], tuple[tuple[int, int, int], ...]]] = {
        0: {(0, 0, 0, 0, 0): tuple()}
    }
    for p0, p1 in zip(local_codes(first, n), local_codes(second, n), strict=True):
        local = _pareto_local_options(p0, p1)
        nxt: dict[int, dict[tuple[int, ...], tuple[tuple[int, int, int], ...]]] = {
            parity: {} for parity in range(8)
        }
        for previous, mapping in states.items():
            for vector, sequence in mapping.items():
                for delta, local_vector, triple in local:
                    parity = previous ^ delta
                    candidate_vector = tuple(
                        a + b for a, b in zip(vector, local_vector, strict=True)
                    )
                    candidate_sequence = sequence + (triple,)
                    old = nxt[parity].get(candidate_vector)
                    if old is None or candidate_sequence < old:
                        nxt[parity][candidate_vector] = candidate_sequence
        states = {
            parity: _prune_vector_map(mapping)
            for parity, mapping in nxt.items()
            if mapping
        }
    collapsed: dict[tuple[int, int], tuple[tuple[int, ...], tuple[tuple[int, int, int], ...]]] = {}
    for additive, sequence in states[TARGET_PARITY].items():
        u_raw, twice_s, t0_support, t1_support, t01_support = additive
        outer = u_raw - 6, twice_s + min(t0_support, t1_support) + t01_support
        old = collapsed.get(outer)
        candidate = additive, sequence
        if old is None or candidate < old:
            collapsed[outer] = candidate
    points = []
    for outer, (_, sequence) in collapsed.items():
        row = _tare_row_from_sequence((first, second), sequence, orientation)
        if (row["parity_CNOT"], row["controlled_Pauli_support"]) != outer:
            raise AssertionError("controlled frontier backtrack mismatch")
        points.append(row)
    return points


@lru_cache(maxsize=200000)
def controlled_pair_frontier(
    first: tuple[int, int], second: tuple[int, int], n: int
) -> tuple[dict[str, Any], ...]:
    if symplectic(first, second) == 1:
        return (canonical_pair_witness(first, second, n),)
    rows = _controlled_orientation_frontier(first, second, n, 0)
    rows += _controlled_orientation_frontier(second, first, n, 1)
    best: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        vector = row["parity_CNOT"], row["controlled_Pauli_support"]
        old = best.get(vector)
        if old is None or canonical_json(row) < canonical_json(old):
            best[vector] = row
    kept = []
    for vector, row in sorted(best.items()):
        if any(_dominates_tuple(other, vector) for other in best if other != vector):
            continue
        kept.append(row)
    return tuple(kept)


def _pair_lambda(a: float, b: float, direct: bool) -> float:
    base = math.hypot(abs(a), abs(b))
    return base if direct else math.sqrt(2.0) * base


def _legacy_pair_lambda(a: float, b: float) -> float:
    return math.sqrt(2.0) * math.hypot(abs(a), abs(b))


def _sum_witness_vectors(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    summed = {
        key: sum(int(row[key]) for row in rows)
        for key in (
            "parity_CNOT",
            "controlled_Rz",
            "controlled_H",
            "controlled_Pauli_support",
            "AND2_compute_uncompute_pairs",
        )
    }
    summed["max_extra_conjunction_scratch"] = max(
        (int(row["max_extra_conjunction_scratch"]) for row in rows), default=0
    )
    return summed


def _point_dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    values_left = tuple(left[key] for key in POINT_COORDS)
    values_right = tuple(right[key] for key in POINT_COORDS)
    return all(a <= b for a, b in zip(values_left, values_right, strict=True)) and values_left != values_right


def _point_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(left[key] == right[key] for key in POINT_COORDS)


def _pareto_points(points: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for point in points:
        key = tuple(point[name] for name in POINT_COORDS)
        old = unique.get(key)
        if old is None or canonical_json(point) < canonical_json(old):
            unique[key] = point
    ordered = sorted(unique.values(), key=lambda row: tuple(row[name] for name in POINT_COORDS))
    kept: list[dict[str, Any]] = []
    for point in ordered:
        if any(_point_dominates(other, point) for other in ordered if other is not point):
            continue
        kept.append(point)
    return kept


def _protocol() -> dict[str, Any]:
    protocol = json.loads(PROTOCOL_PATH.read_text())
    if protocol["status"] != "FROZEN_BEFORE_NEW_RESOURCE_OUTCOMES":
        raise AssertionError("revival protocol is not frozen")
    return protocol


def _attempt(protocol: dict[str, Any], negative_id: str) -> dict[str, Any]:
    return next(row for row in protocol["attempts"] if row["source_negative_id"] == negative_id)


def _r4c_terms(protocol: dict[str, Any]) -> list[tuple[tuple[int, int], float, int]]:
    attempt = _attempt(protocol, "R4C_H2_REGIME_LIMITED")
    return [
        (pauli_word_key(row["pauli"]), float(row["coefficient"]), int(row["source_index"]))
        for row in attempt["subject"]["terms"]
    ]


def _verify_r4c_notebook(protocol: dict[str, Any]) -> dict[str, Any]:
    attempt = _attempt(protocol, "R4C_H2_REGIME_LIMITED")
    subject = attempt["subject"]
    url = (
        "https://raw.githubusercontent.com/SNIPRS/hamiltonian/"
        f"{subject['commit']}/{subject['path']}"
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read()
    observed = hashlib.sha256(raw).hexdigest()
    if observed != subject["notebook_sha256"]:
        raise AssertionError({"R4C_notebook_sha256": [observed, subject["notebook_sha256"]]})
    notebook = json.loads(raw)
    cell = notebook["cells"][int(subject["output_cell_index"])]
    text = "\n".join("".join(row.get("text", [])) for row in cell.get("outputs", []))
    pattern = re.compile(r"^\s*(\d+) \[([+\-0-9.eE]+) '(-?)([IXYZ]+)'\]\s*$")
    extracted = []
    for line in text.splitlines():
        match = pattern.match(line)
        if not match or int(match.group(1)) == 0:
            continue
        coefficient = float(match.group(2)) * (-1 if match.group(3) else 1)
        extracted.append(
            {
                "source_index": int(match.group(1)),
                "coefficient": coefficient,
                "pauli": match.group(4),
            }
        )
    if extracted != subject["terms"]:
        raise AssertionError({"R4C_notebook_term_drift": [extracted, subject["terms"]]})
    return {"url": url, "sha256": observed, "terms_exact": True}


def run_r4c(protocol: dict[str, Any]) -> dict[str, Any]:
    source_check = _verify_r4c_notebook(protocol)
    terms = _r4c_terms(protocol)
    n = len(_attempt(protocol, "R4C_H2_REGIME_LIMITED")["subject"]["terms"][0]["pauli"])
    edge_rows: dict[tuple[int, int], dict[str, Any]] = {}
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            witness = canonical_pair_witness(terms[i][0], terms[j][0], n)
            if not all(witness["checks"].values()):
                raise AssertionError({"R4C_pair_witness": [i, j]})
            direct = witness["type"] == "DIRECT_ANTI_UNITARY"
            edge_rows[(i, j)] = {
                "witness": witness,
                "legacy_lambda": _legacy_pair_lambda(terms[i][1], terms[j][1]),
                "actual_lambda": _pair_lambda(terms[i][1], terms[j][1], direct),
                "direct": direct,
            }

    matching_count = 0
    legacy_best: dict[int, dict[str, Any]] = {}
    all_points: list[dict[str, Any]] = []
    legacy_parent: dict[str, Any] | None = None
    for matching in perfect_matchings(tuple(range(len(terms)))):
        matching_count += 1
        edges = [edge_rows[tuple(sorted(pair))] for pair in matching]
        witnesses = [edge["witness"] for edge in edges]
        direct = sum(edge["direct"] for edge in edges)
        legacy_lambda = sum(edge["legacy_lambda"] for edge in edges)
        actual_lambda = sum(edge["actual_lambda"] for edge in edges)
        vector = _sum_witness_vectors(witnesses)
        serialized_matching = [
            [terms[i][2], terms[j][2]] for i, j in matching
        ]
        point = {
            "matching": serialized_matching,
            "matching_sha256": sha256_value(serialized_matching),
            "legacy_Lambda": legacy_lambda,
            "Lambda_joint": actual_lambda,
            "direct_unitary_blocks": direct,
            "all_witness_checks_pass": True,
            "canonical_witness_sha256": sha256_value(witnesses),
            **vector,
        }
        all_points.append(point)
        if legacy_parent is None or (legacy_lambda, serialized_matching) < (
            legacy_parent["legacy_Lambda"],
            legacy_parent["matching"],
        ):
            legacy_parent = point
        for required in range(direct + 1):
            old = legacy_best.get(required)
            if old is None or (legacy_lambda, serialized_matching) < (
                old["legacy_Lambda"],
                old["matching"],
            ):
                legacy_best[required] = point

    expected = json.loads(
        (ROOT / "research/extensions/orion-q/MAX_R4C_FRESH_H2_HETEROGENEOUS_PAIR_RESULTS.json").read_text()
    )["frontier"]
    frontier_binding = []
    for row in expected:
        required = int(row["required_direct_pairs"])
        observed = legacy_best.get(required)
        if row.get("infeasible"):
            passed = observed is None
            observed_lambda = None
        else:
            observed_lambda = observed["legacy_Lambda"] if observed else None
            passed = observed is not None and abs(observed_lambda - float(row["lambda"])) <= 1e-12
        frontier_binding.append(
            {
                "required_direct_pairs": required,
                "expected_lambda": row.get("lambda"),
                "observed_lambda": observed_lambda,
                "pass": passed,
            }
        )
    if matching_count != 135135 or not all(row["pass"] for row in frontier_binding):
        raise AssertionError({"R4C_frontier_binding": frontier_binding, "matching_count": matching_count})
    assert legacy_parent is not None
    pareto = _pareto_points(all_points)
    one_percent = [
        point for point in pareto if point["Lambda_joint"] <= 1.01 * legacy_parent["Lambda_joint"] + 1e-12
    ]
    improvements = [point for point in one_percent if _point_dominates(point, legacy_parent)]
    tradeoffs = [point for point in pareto if not _point_equal(point, legacy_parent)]
    if improvements:
        outcome = "IMPROVED"
        terminal = "ORION06_R4C_ACTUAL_RESOURCE_PARENT_DOMINATED__OPEN_SUBJECT_ONLY"
    elif tradeoffs:
        outcome = "PARETO_TRADEOFF_ONLY"
        terminal = "ORION06_R4C_BINARY_GATE_REPLACED_BY_ACTUAL_RESOURCE_TRADEOFF__NO_SUPERIORITY"
    else:
        outcome = "RETAINED_NEGATIVE"
        terminal = "ORION06_R4C_ACTUAL_RESOURCE_PARENT_REMAINS_UNIQUE_FRONTIER"
    return {
        "source_negative_id": "R4C_H2_REGIME_LIMITED",
        "mechanism_stage": "EVALUATION_OBJECTIVE",
        "lever": "R4C_ACTUAL_RESTORE_OUTER_SELECT_PARETO_REPLAY",
        "revival_outcome": outcome,
        "terminal": terminal,
        "source_check": source_check,
        "matching_count": matching_count,
        "pair_edge_count": len(edge_rows),
        "legacy_frontier_binding": frontier_binding,
        "strongest_parent": legacy_parent,
        "pareto_point_count": len(pareto),
        "one_percent_pareto_point_count": len(one_percent),
        "strict_parent_dominating_points": improvements,
        "pareto_frontier": pareto,
        "original_negative_preserved": True,
        "scientific_authority_delta": "NONE",
        "authority": {
            "prospective_confirmation": False,
            "end_to_end_qsvt_superiority": False,
            "hardware_independence": False,
            "novelty": False,
            "final_freeze": False,
        },
    }


def _load_h4_batch() -> tuple[list[tuple[tuple[int, int], float]], tuple[int, ...], dict[str, Any]]:
    qdir = ROOT / "research/extensions/orion-q"
    sys.path.insert(0, str(qdir))
    import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # type: ignore

    cfg = r6f.p10.base.SUBJECTS["H4"]
    terms, indices, _, max_imag, observed_blob = r6f._frozen_batch(cfg)
    return terms, indices, {
        "commit": cfg["commit"],
        "path": cfg["path"],
        "expected_blob": cfg["blob"],
        "observed_blob": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"],
        "max_imag": max_imag,
    }


def _aggregate_matching(
    matching: tuple[tuple[int, int], ...],
    selected_terms: Sequence[tuple[tuple[int, int], float, int]],
    witnesses: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    lam = 0.0
    for (i, j), witness in zip(matching, witnesses, strict=True):
        lam += _pair_lambda(
            selected_terms[i][1],
            selected_terms[j][1],
            witness["type"] == "DIRECT_ANTI_UNITARY",
        )
    vector = _sum_witness_vectors(witnesses)
    serialized = [[selected_terms[i][2], selected_terms[j][2]] for i, j in matching]
    return {
        "matching": serialized,
        "matching_sha256": sha256_value(serialized),
        "Lambda_joint": lam,
        "direct_unitary_blocks": sum(
            witness["type"] == "DIRECT_ANTI_UNITARY" for witness in witnesses
        ),
        "all_witness_checks_pass": all(all(row["checks"].values()) for row in witnesses),
        "canonical_witness_sha256": sha256_value(witnesses),
        **vector,
    }


def run_r5b(protocol: dict[str, Any]) -> dict[str, Any]:
    terms, source_indices, source = _load_h4_batch()
    expected = tuple(
        _attempt(protocol, "R5B_PROOF_OUTER_REPLAY")["subject"]["frozen_source_indices"]
    )
    if source_indices != expected or not source["source_blob_verified"]:
        raise AssertionError({"R5B_H4_batch_binding": [source_indices, expected, source]})
    selected = [(terms[index][0], float(terms[index][1]), int(index)) for index in source_indices]
    n = 8
    parent_edges: dict[tuple[int, int], dict[str, Any]] = {}
    candidate_edges: dict[tuple[int, int], tuple[dict[str, Any], ...]] = {}
    for i in range(6):
        for j in range(i + 1, 6):
            parent_edges[(i, j)] = canonical_pair_witness(selected[i][0], selected[j][0], n)
            candidate_edges[(i, j)] = controlled_pair_frontier(selected[i][0], selected[j][0], n)

    parent_points = []
    candidate_points = []
    matchings = list(perfect_matchings(tuple(range(6))))
    if len(matchings) != 15:
        raise AssertionError("R5B matching count drift")
    for matching in matchings:
        parent_witnesses = [parent_edges[tuple(sorted(pair))] for pair in matching]
        parent_points.append(_aggregate_matching(matching, selected, parent_witnesses))
        frontiers = [candidate_edges[tuple(sorted(pair))] for pair in matching]
        for witnesses in itertools.product(*frontiers):
            candidate_points.append(_aggregate_matching(matching, selected, witnesses))

    if not all(point["all_witness_checks_pass"] for point in parent_points + candidate_points):
        raise AssertionError("R5B witness verification failure")
    parent_pareto = _pareto_points(parent_points)
    candidate_pareto = _pareto_points(candidate_points)
    minimum_lambda = min(point["Lambda_joint"] for point in parent_points)
    budget = 1.01 * minimum_lambda
    candidates_in_budget = [point for point in candidate_pareto if point["Lambda_joint"] <= budget + 1e-12]
    strict = []
    expansions = []
    for candidate in candidates_in_budget:
        dominated_by_parent = any(_point_dominates(parent, candidate) for parent in parent_pareto)
        equal_parent = any(_point_equal(parent, candidate) for parent in parent_pareto)
        dominates_parent = any(_point_dominates(candidate, parent) for parent in parent_pareto)
        if not dominated_by_parent and dominates_parent:
            strict.append(candidate)
        if not dominated_by_parent and not equal_parent:
            expansions.append(candidate)
    if strict:
        outcome = "IMPROVED"
        terminal = "ORION06_R5B_CONTROLLED_AWARE_PARENT_POINT_DOMINATED__OPEN_H4_ONLY"
    elif expansions:
        outcome = "PARETO_TRADEOFF_ONLY"
        terminal = "ORION06_R5B_CONTROLLED_AWARE_FRONTIER_EXPANDED__NO_STRICT_SUPERIORITY"
    else:
        outcome = "RETAINED_NEGATIVE"
        terminal = "ORION06_R5B_CONTROLLED_AWARE_PARENT_ENVELOPE_RETAINED"
    return {
        "source_negative_id": "R5B_PROOF_OUTER_REPLAY",
        "mechanism_stage": "RESOURCE_PROJECTION",
        "lever": "CONTROLLED_SELECT_AWARE_EXACT_REPRESENTATION_AND_REMATCHING",
        "revival_outcome": outcome,
        "terminal": terminal,
        "source": source,
        "frozen_source_indices": list(source_indices),
        "matching_count": len(matchings),
        "parent_pair_representation_count": len(parent_edges),
        "candidate_pair_frontier_sizes": {
            f"{selected[i][2]}-{selected[j][2]}": len(candidate_edges[(i, j)])
            for i in range(6)
            for j in range(i + 1, 6)
        },
        "parent_point_count": len(parent_points),
        "candidate_point_count": len(candidate_points),
        "minimum_Lambda": minimum_lambda,
        "one_percent_Lambda_budget": budget,
        "parent_pareto": parent_pareto,
        "candidate_pareto": candidate_pareto,
        "strict_parent_dominating_points": strict,
        "frontier_expansion_points": expansions,
        "original_negative_preserved": True,
        "residual": "H4 was already open; protected new-subject confirmation remains unearned",
        "scientific_authority_delta": "NONE",
        "authority": {
            "prospective_confirmation": False,
            "new_subject_generalization": False,
            "end_to_end_qsvt_superiority": False,
            "hardware_independence": False,
            "novelty": False,
            "final_freeze": False,
        },
    }


def _without_runtime(value: dict[str, Any]) -> dict[str, Any]:
    return {key: row for key, row in value.items() if key != "runtime_seconds"}


def adjudicate_known_replays(
    r6k_result_path: Path, r6l_result_path: Path, root: Path = ROOT
) -> dict[str, Any]:
    root = Path(root).resolve()
    protocol = _protocol()
    for negative_id in ("R6I_EXACT_RANK2", "R6K_EXACT_RESTORE_FACTOR"):
        attempt = _attempt(protocol, negative_id)
        for key, expected in attempt["bound_replay"].items():
            if not key.endswith("_sha256"):
                continue
            path_key = key.removesuffix("_sha256") + "_path"
            if path_key not in attempt["bound_replay"]:
                # protocol_sha256 -> protocol_path, runner_sha256 -> runner_path, etc.
                path_key = key.replace("_sha256", "_path")
            relative = attempt["bound_replay"].get(path_key)
            if relative is None and key == "known_receipt_sha256":
                relative = attempt["bound_replay"]["known_receipt_path"]
            if relative is None:
                raise AssertionError({"unbound_replay_hash": [negative_id, key]})
            observed = sha256_file(root / relative)
            if observed != expected:
                raise AssertionError({"replay_source_hash_drift": [negative_id, relative, expected, observed]})

    r6k = json.loads(Path(r6k_result_path).read_text())
    r6l = json.loads(Path(r6l_result_path).read_text())
    known_r6k = json.loads(
        (root / "research/extensions/orion-q/MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_RESULTS.json").read_text()
    )
    known_r6l = json.loads(
        (root / "research/extensions/orion-q/MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json").read_text()
    )
    if _without_runtime(r6k) != _without_runtime(known_r6k):
        raise AssertionError("fresh R6K replay differs scientifically from the bound public receipt")
    if _without_runtime(r6l) != _without_runtime(known_r6l):
        raise AssertionError("fresh R6L replay differs scientifically from the bound public receipt")
    r6k_strict = {
        subject: bool(r6k["subjects"][subject]["strict_budget_matched_improvement_exists"])
        for subject in ("H4", "N2")
    }
    r6l_strict = {
        subject: bool(r6l["subjects"][subject]["strict_budget_matched_improvement_exists"])
        for subject in ("H4", "N2")
    }
    if all(r6k_strict.values()):
        r6i_outcome = "IMPROVED"
    elif any(r6k_strict.values()):
        r6i_outcome = "PARTIAL"
    else:
        r6i_outcome = "RETAINED_NEGATIVE"
    if all(r6l_strict.values()):
        r6k_outcome = "CORRECT_SUBTRACTION"
    elif any(r6l_strict.values()):
        r6k_outcome = "PARTIAL"
    else:
        r6k_outcome = "RETAINED_NEGATIVE"
    common_authority = {
        "prospective_confirmation": False,
        "novelty": False,
        "r6": False,
        "final_freeze": False,
    }
    return {
        "schema": "ORION.ORION06.MethodLanguageReplayAdjudication.v1",
        "R6I_EXACT_RANK2": {
            "mechanism_stage": "METHOD_LANGUAGE",
            "lever": "R6K_JOINT_RESTORE_FACTOR_EXACT_REPLAY",
            "revival_outcome": r6i_outcome,
            "strict_by_subject": r6k_strict,
            "replay_scientifically_equal_to_known_receipt": True,
            "original_negative_preserved": True,
            "authority": common_authority,
        },
        "R6K_EXACT_RESTORE_FACTOR": {
            "mechanism_stage": "METHOD_LANGUAGE",
            "lever": "R6L_THREE_TARE2_ARITY_SWAP_DONOR_REPLAY",
            "revival_outcome": r6k_outcome,
            "strict_by_subject": r6l_strict,
            "classification": "donor absorption, not candidate novelty",
            "replay_scientifically_equal_to_known_receipt": True,
            "original_negative_preserved": True,
            "authority": {**common_authority, "donor_novelty_credit": False},
        },
        "scientific_authority_delta": "NONE",
        "unsolvable": [],
    }


def run_new_resources() -> dict[str, Any]:
    protocol = _protocol()
    return {
        "schema": "ORION.ORION06.NewResourceRevivalResult.v1",
        "date": "2026-08-28",
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "source_commit": os.environ.get("ORION06_REVIVAL_SOURCE_COMMIT"),
        "slurm": {
            key: os.environ.get(key)
            for key in (
                "SLURM_JOB_ID",
                "SLURM_JOB_NAME",
                "SLURM_JOB_PARTITION",
                "SLURM_CPUS_PER_TASK",
                "SLURM_MEM_PER_NODE",
                "SLURMD_NODENAME",
            )
        },
        "attempts": {
            "R4C_H2_REGIME_LIMITED": run_r4c(protocol),
            "R5B_PROOF_OUTER_REPLAY": run_r5b(protocol),
        },
        "scientific_authority_delta": "NONE",
        "unsolvable": [],
        "authority": {
            "prospective_confirmation": False,
            "external_independence": False,
            "novelty": False,
            "journal_or_submission": False,
            "final_freeze": False,
        },
    }


def _write_new(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-new-resources", action="store_true")
    group.add_argument("--adjudicate-known-replays", action="store_true")
    parser.add_argument("--r6k-result", type=Path)
    parser.add_argument("--r6l-result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.run_new_resources:
        result = run_new_resources()
        prefix = "ORION06_NEW_RESOURCE_REVIVAL="
    else:
        if args.r6k_result is None or args.r6l_result is None:
            parser.error("replay adjudication requires --r6k-result and --r6l-result")
        result = adjudicate_known_replays(args.r6k_result, args.r6l_result)
        prefix = "ORION06_METHOD_LANGUAGE_REPLAYS="
    _write_new(args.output, result)
    print(prefix + canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
