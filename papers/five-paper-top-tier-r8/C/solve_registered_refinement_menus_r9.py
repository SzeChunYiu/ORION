#!/usr/bin/env python3
"""Solve exact and epsilon refinement menus on the registered FiberGuard domains.

This is a portfolio-side application of the collision-pair theorem. It reuses the
registered domain encodings and target evaluators, so it is not the independent
ILP/SAT replay requested from Codex.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import fiberguard_r8 as fg

SCHEMA = "ORION.FiberGuard.RegisteredRefinementMenusR9.Results.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple((key, stable(value[key])) for key in sorted(value))
    if isinstance(value, (list, tuple)):
        return tuple(stable(item) for item in value)
    return value


def graph_records() -> tuple[list[tuple[Any, int, tuple[Any, ...]]], tuple[str, ...]]:
    n = 6
    feature_names = ("connected_component_count", "four_cycle_count", "clique_number")
    records = []
    for mask in range(1 << (n * (n - 1) // 2)):
        instance = fg.graph_adjacency(n, mask)
        target = fg.chromatic_backtracking(instance)
        extras = fg.graph_extra_features(instance)
        records.append((stable(fg.graph_feature(instance)), target, tuple(stable(extras[name]) for name in feature_names)))
    return records, feature_names


def set_cover_records() -> tuple[list[tuple[Any, int, tuple[Any, ...]]], tuple[str, ...]]:
    universe_size = 5
    universe = (1 << universe_size) - 1
    feature_names = (
        "pairwise_union_multiset",
        "element_frequency_multiset",
        "triple_intersection_multiset",
    )
    records = []
    for family in itertools.combinations(range(1, universe + 1), 5):
        if functools.reduce(int.__or__, family, 0) != universe:
            continue
        target = fg.minimum_cover_mask_dp(family, universe)
        extras = fg.set_cover_extra_features(family, universe_size)
        records.append((stable(fg.set_cover_feature(family)), target, tuple(stable(extras[name]) for name in feature_names)))
    return records, feature_names


def sat_records() -> tuple[list[tuple[Any, int, tuple[Any, ...]]], tuple[str, ...]]:
    variable_count = 4
    clauses = fg.all_binary_clauses(variable_count)
    feature_names = (
        "global_clause_sign_type_counts",
        "variable_pair_signed_profile_multiset",
        "labeled_variable_pair_signed_profile",
    )
    records = []
    for indices in itertools.combinations(range(len(clauses)), 5):
        formula = tuple(clauses[index] for index in indices)
        target = fg.satisfying_count_bitset(formula, variable_count)
        extras = fg.sat_extra_features(formula, variable_count)
        records.append((stable(fg.sat_feature(formula, variable_count)), target, tuple(stable(extras[name]) for name in feature_names)))
    return records, feature_names


def inclusion_minimal_covering_menus(feature_count: int, critical_masks: Sequence[int]) -> list[int]:
    covering = []
    for selected in range(1 << feature_count):
        if all(mask & selected for mask in critical_masks):
            covering.append(selected)
    minimal = []
    for selected in covering:
        if not any(other != selected and (other & selected) == other for other in covering):
            minimal.append(selected)
    return sorted(minimal, key=lambda mask: (mask.bit_count(), mask))


def decode_menu(mask: int, feature_names: Sequence[str]) -> list[str]:
    return [name for index, name in enumerate(feature_names) if (mask >> index) & 1]


def analyze_domain(
    name: str,
    records: Sequence[tuple[Any, int, tuple[Any, ...]]],
    feature_names: Sequence[str],
    epsilons: Sequence[float],
) -> dict[str, Any]:
    fibres: dict[Any, dict[tuple[int, tuple[Any, ...]], int]] = defaultdict(lambda: defaultdict(int))
    for base, target, candidates in records:
        fibres[base][(target, candidates)] += 1

    gap_mask_counts: dict[tuple[int, int], int] = defaultdict(int)
    target_values = set()
    candidate_cell_count = 0
    for cells in fibres.values():
        rows = [(target, candidates, multiplicity) for (target, candidates), multiplicity in cells.items()]
        candidate_cell_count += len(rows)
        for target, _candidates, _multiplicity in rows:
            target_values.add(target)
        for left_index in range(len(rows)):
            left_target, left_values, left_count = rows[left_index]
            for right_index in range(left_index + 1, len(rows)):
                right_target, right_values, right_count = rows[right_index]
                gap = abs(left_target - right_target)
                if gap == 0:
                    continue
                separation_mask = 0
                for index, (left, right) in enumerate(zip(left_values, right_values, strict=True)):
                    if left != right:
                        separation_mask |= 1 << index
                gap_mask_counts[(gap, separation_mask)] += left_count * right_count

    epsilon_rows = []
    for epsilon in epsilons:
        mask_counts: dict[int, int] = defaultdict(int)
        for (gap, mask), count in gap_mask_counts.items():
            if gap > 2.0 * epsilon:
                mask_counts[mask] += count
        critical_pairs = sum(mask_counts.values())
        unseparated = mask_counts.get(0, 0)
        nonzero_masks = sorted(mask for mask, count in mask_counts.items() if mask != 0 and count > 0)
        if unseparated:
            terminal = "INFEASIBLE_MENU"
            minimal_masks: list[int] = []
            unit_optimum = None
        else:
            minimal_masks = inclusion_minimal_covering_menus(len(feature_names), nonzero_masks)
            terminal = "EXACT_MENU_FOUND" if epsilon == 0 else "EPSILON_MENU_FOUND"
            unit_optimum = min((mask.bit_count() for mask in minimal_masks), default=0)
        epsilon_rows.append({
            "epsilon": epsilon,
            "critical_pair_count": critical_pairs,
            "unseparated_critical_pair_count": unseparated,
            "critical_separation_mask_histogram": {
                format(mask, f"0{len(feature_names)}b"): count
                for mask, count in sorted(mask_counts.items())
            },
            "inclusion_minimal_menus": [decode_menu(mask, feature_names) for mask in minimal_masks],
            "minimum_unit_cost_feature_count": unit_optimum,
            "terminal": terminal,
        })

    return {
        "domain": name,
        "instance_count": len(records),
        "base_fibre_count": len(fibres),
        "target_values": sorted(target_values),
        "candidate_feature_names": list(feature_names),
        "candidate_cell_count": candidate_cell_count,
        "gap_separation_histogram": {
            f"gap={gap};mask={format(mask, f'0{len(feature_names)}b')}": count
            for (gap, mask), count in sorted(gap_mask_counts.items())
        },
        "epsilon_results": epsilon_rows,
        "cost_authority": {
            "unit_cost_menu_is_combinatorial_only": True,
            "production_feature_costs_measured": False,
            "inclusion_minimal_menus_support_posthoc_frozen_cost_evaluation": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).with_name("REGISTERED_REFINEMENT_MENUS_R9_RESULTS.json")))
    args = parser.parse_args()
    domains = []
    for name, builder in (
        ("GRAPH_COLOURING_N6", graph_records),
        ("SET_COVER_U5_M5", set_cover_records),
        ("TWO_CNF_N4_M5", sat_records),
    ):
        records, feature_names = builder()
        domains.append(analyze_domain(name, records, feature_names, (0.0, 0.5, 1.0, 2.0)))
    result = {
        "schema": SCHEMA,
        "source": {
            "registered_domain_module": "fiberguard_r8.py",
            "registered_domain_module_sha256": hashlib.sha256(Path(fg.__file__).read_bytes()).hexdigest(),
            "portfolio_side_reuses_registered_encodings": True,
            "structurally_independent_replay": False,
        },
        "theorem_application": {
            "exact": "selected menu must hit every same-base target-disagreeing pair",
            "epsilon": "selected menu must hit every same-base pair with target gap greater than 2*epsilon",
            "candidate_costs": "unit costs only; all inclusion-minimal menus are retained for later frozen production costs",
        },
        "domains": domains,
        "authority": {
            "finite_exact_on_registered_domains": True,
            "independent_target_replay": False,
            "production_feature_costs_validated": False,
            "unseen_domain_generalization": False,
            "grants_journal_authority": False,
        },
        "terminal": "C_REGISTERED_REFINEMENT_MENUS__FINITE_EXACT_PORTFOLIO_SIDE_APPLICATION_COMPLETE",
    }
    output = Path(args.output)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
