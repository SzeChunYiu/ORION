#!/usr/bin/env python3
"""Exhaustive finite correspondence census for Epistemic Decision Geometry V1."""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Iterable

from orion.discovery.decision_geometry import (
    bayes_decision,
    minimax_regret_decision,
    partition_bayes_regret,
    two_world_hedge_report,
    zero_regret_supported,
)

LOSS_VALUES = (0, 1, 2, 3)
SCOPES = ((2, 2), (2, 3), (2, 4), (3, 2), (4, 2))
RESULT_PATH = Path(__file__).with_name("EDG_FINITE_CENSUS_V1.json")


def _rows(values: tuple[int, ...], n_states: int, n_actions: int) -> dict[int, dict[int, float]]:
    return {
        state: {
            action: float(values[state * n_actions + action])
            for action in range(n_actions)
        }
        for state in range(n_states)
    }


def _direct_regrets(losses: dict[int, dict[int, float]]) -> dict[int, dict[int, float]]:
    result: dict[int, dict[int, float]] = {}
    for state, row in losses.items():
        minimum = min(row.values())
        result[state] = {action: value - minimum for action, value in row.items()}
    return result


def _direct_common_optimum(losses: dict[int, dict[int, float]]) -> bool:
    common: set[int] | None = None
    for row in losses.values():
        minimum = min(row.values())
        optima = {action for action, value in row.items() if value == minimum}
        common = optima if common is None else common & optima
    return bool(common)


def _direct_minimax_regret(losses: dict[int, dict[int, float]]) -> float:
    regrets = _direct_regrets(losses)
    actions = tuple(next(iter(losses.values())))
    return min(max(regrets[state][action] for state in losses) for action in actions)


def _direct_uniform_bayes_regret(losses: dict[int, dict[int, float]]) -> float:
    regrets = _direct_regrets(losses)
    actions = tuple(next(iter(losses.values())))
    n_states = len(losses)
    return min(
        sum(regrets[state][action] for state in losses) / n_states
        for action in actions
    )


def _set_partitions(n: int) -> tuple[tuple[int, ...], ...]:
    rows: list[tuple[int, ...]] = []

    def visit(index: int, blocks: list[list[int]]) -> None:
        if index == n:
            labels = [0] * n
            for block_id, block in enumerate(blocks):
                for state in block:
                    labels[state] = block_id
            rows.append(tuple(labels))
            return
        for block in blocks:
            block.append(index)
            visit(index + 1, blocks)
            block.pop()
        blocks.append([index])
        visit(index + 1, blocks)
        blocks.pop()

    visit(0, [])
    return tuple(rows)


def _refines(finer: tuple[int, ...], coarser: tuple[int, ...]) -> bool:
    induced: dict[int, int] = {}
    for fine, coarse in zip(finer, coarser, strict=True):
        previous = induced.setdefault(fine, coarse)
        if previous != coarse:
            return False
    return True


def _partition_map(labels: tuple[int, ...]) -> dict[int, int]:
    return {state: label for state, label in enumerate(labels)}


def _scope_census(n_states: int, n_actions: int) -> dict[str, object]:
    total = 0
    common_optimum = 0
    zero_minimax = 0
    unique_distinct_optima = 0
    hedge_present = 0
    no_hedge = 0
    hedge_gain_histogram: dict[str, int] = {}
    bayes_correspondence_violations = 0
    common_minimax_violations = 0
    hedge_identity_violations = 0
    first_hedge_witness: dict[str, object] | None = None

    for values in product(LOSS_VALUES, repeat=n_states * n_actions):
        losses = _rows(values, n_states, n_actions)
        total += 1

        direct_common = _direct_common_optimum(losses)
        reference_common = zero_regret_supported(losses)
        direct_minimax = _direct_minimax_regret(losses)
        reference_minimax = minimax_regret_decision(losses).worst_regret
        direct_bayes = _direct_uniform_bayes_regret(losses)
        reference_bayes = bayes_decision(losses).expected_regret

        if direct_common:
            common_optimum += 1
        if reference_minimax == 0:
            zero_minimax += 1
        if direct_common != reference_common or (direct_minimax == 0) != direct_common:
            common_minimax_violations += 1
        if reference_minimax != direct_minimax:
            common_minimax_violations += 1
        if reference_bayes != direct_bayes:
            bayes_correspondence_violations += 1

        if n_states != 2:
            continue
        report = two_world_hedge_report(losses, 0, 1)
        if (
            len(report.left_optima) == 1
            and len(report.right_optima) == 1
            and report.left_optima != report.right_optima
        ):
            unique_distinct_optima += 1
            direct_regrets = _direct_regrets(losses)
            best_sum = min(
                direct_regrets[0][action] + direct_regrets[1][action]
                for action in range(n_actions)
            )
            if report.exact_equal_prior_regret != best_sum / 2.0:
                hedge_identity_violations += 1
            gain = report.hedge_gain
            assert gain is not None
            key = str(int(gain) if gain.is_integer() else gain)
            hedge_gain_histogram[key] = hedge_gain_histogram.get(key, 0) + 1
            if report.hedge_present:
                hedge_present += 1
                if first_hedge_witness is None:
                    first_hedge_witness = {
                        "losses": [
                            [int(losses[state][action]) for action in range(n_actions)]
                            for state in range(n_states)
                        ],
                        "best_action": report.best_action,
                        "cross_action_gap": report.cross_action_gap,
                        "half_gap_value": report.half_gap_value,
                        "exact_equal_prior_regret": report.exact_equal_prior_regret,
                        "hedge_gain": report.hedge_gain,
                    }
            else:
                no_hedge += 1

    return {
        "n_states": n_states,
        "n_actions": n_actions,
        "loss_values": list(LOSS_VALUES),
        "tables": total,
        "common_optimum_tables": common_optimum,
        "zero_minimax_regret_tables": zero_minimax,
        "unique_distinct_optima_tables": unique_distinct_optima,
        "hedge_present_tables": hedge_present,
        "no_hedge_tables": no_hedge,
        "hedge_gain_histogram": hedge_gain_histogram,
        "first_hedge_witness": first_hedge_witness,
        "common_minimax_correspondence_violations": common_minimax_violations,
        "uniform_bayes_correspondence_violations": bayes_correspondence_violations,
        "hedge_identity_violations": hedge_identity_violations,
    }


def _partition_refinement_census() -> dict[str, object]:
    n_states, n_actions = 3, 2
    partitions = _set_partitions(n_states)
    refinement_pairs = tuple(
        (finer, coarser)
        for finer in partitions
        for coarser in partitions
        if _refines(finer, coarser)
    )
    comparisons = strict = equal = violations = 0
    for values in product(LOSS_VALUES, repeat=n_states * n_actions):
        losses = _rows(values, n_states, n_actions)
        for finer, coarser in refinement_pairs:
            fine_regret = partition_bayes_regret(losses, _partition_map(finer))
            coarse_regret = partition_bayes_regret(losses, _partition_map(coarser))
            comparisons += 1
            if fine_regret > coarse_regret:
                violations += 1
            elif fine_regret < coarse_regret:
                strict += 1
            else:
                equal += 1
    return {
        "n_states": n_states,
        "n_actions": n_actions,
        "partition_count": len(partitions),
        "refinement_pair_count": len(refinement_pairs),
        "loss_tables": len(LOSS_VALUES) ** (n_states * n_actions),
        "comparisons": comparisons,
        "strict_improvements": strict,
        "equalities": equal,
        "violations": violations,
    }


def build_result() -> dict[str, object]:
    scopes = [_scope_census(*scope) for scope in SCOPES]
    total_tables = sum(int(row["tables"]) for row in scopes)
    total_common = sum(int(row["common_optimum_tables"]) for row in scopes)
    total_unique_distinct = sum(
        int(row["unique_distinct_optima_tables"]) for row in scopes
    )
    total_hedge = sum(int(row["hedge_present_tables"]) for row in scopes)
    total_no_hedge = sum(int(row["no_hedge_tables"]) for row in scopes)
    violations = sum(
        int(row["common_minimax_correspondence_violations"])
        + int(row["uniform_bayes_correspondence_violations"])
        + int(row["hedge_identity_violations"])
        for row in scopes
    )
    partition = _partition_refinement_census()
    violations += int(partition["violations"])
    terminal = (
        "EDG_FINITE_CORRESPONDENCE_GREEN"
        if violations == 0
        else "EDG_COUNTEREXAMPLE_FOUND"
    )
    return {
        "schema": "orion.discovery.edg-finite-census.v1",
        "theory_identity": "EPISTEMIC_DECISION_GEOMETRY_V1",
        "terminal": terminal,
        "scope": {
            "loss_values": list(LOSS_VALUES),
            "state_action_scopes": [list(scope) for scope in SCOPES],
            "probability": "uniform for Bayes correspondence",
            "partition_refinement_scope": [3, 2],
        },
        "totals": {
            "loss_tables": total_tables,
            "common_optimum_tables": total_common,
            "unique_distinct_optima_tables": total_unique_distinct,
            "hedge_present_tables": total_hedge,
            "no_hedge_tables": total_no_hedge,
            "all_correspondence_violations": violations,
        },
        "scope_results": scopes,
        "partition_refinement": partition,
        "interpretation": [
            "zero deterministic minimax regret iff a common fibre optimum exists",
            "uniform Bayes regret equals the exact fibrewise envelope",
            "two-action tables admit no third-action hedge",
            "hedge actions are rare but real once the action set has at least three actions",
            "information refinement never increased optimal Bayes regret in the complete registered scope",
        ],
        "authority": {
            "finite_exact_only": True,
            "external_proof_review": "CANNOT_CHECK",
            "naturalistic_transfer": "CANNOT_CHECK",
            "paper_claim_delta": "NONE",
        },
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = build_result()
    if args.write:
        RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        expected = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        if canonical_json(expected) != canonical_json(result):
            raise SystemExit("EDG_FINITE_CENSUS_MISMATCH")
    print(json.dumps(result["totals"], sort_keys=True))
    print(result["terminal"])
    return 0 if result["terminal"] == "EDG_FINITE_CORRESPONDENCE_GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
