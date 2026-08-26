#!/usr/bin/env python3
"""Finite proof-carrying checker for the AB production-realization gate.

The checker verifies a *declared finite registry*. It cannot establish that the
registry contains every move of an external production implementation; that
completeness claim remains separately owned by the supplied registry digest and
review evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

INPUT_SCHEMA = "ORION.AB.FiniteProductionRealizationInstanceR9.v1"
RESULT_SCHEMA = "ORION.AB.FiniteProductionRealizationResultR9.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def rank_tuple(value: Any) -> tuple[float, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("objective_rank must be a nonempty numeric list")
    result = []
    for item in value:
        if not isinstance(item, (int, float)) or isinstance(item, bool):
            raise ValueError("objective_rank entries must be numeric")
        result.append(float(item))
    return tuple(result)


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def descendants(start: str, adjacency: dict[str, tuple[str, ...]]) -> frozenset[str]:
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in adjacency.get(current, ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return frozenset(seen)


def terminal_set(start: str, adjacency: dict[str, tuple[str, ...]]) -> frozenset[str]:
    return frozenset(node for node in descendants(start, adjacency) if not adjacency.get(node, ()))


def check_instance(data: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if data.get("schema") != INPUT_SCHEMA:
        issues.append({"type": "INVALID_SCHEMA", "observed": data.get("schema")})

    claimed_bound = data.get("claimed_weak_terminal_bound")
    if not isinstance(claimed_bound, int) or claimed_bound < 0:
        issues.append({"type": "INVALID_CLAIMED_BOUND", "observed": claimed_bound})
        claimed_bound = 0

    state_rows = data.get("states")
    if not isinstance(state_rows, list) or not state_rows:
        issues.append({"type": "MISSING_STATES"})
        state_rows = []

    states: dict[str, dict[str, Any]] = {}
    for row in state_rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            issues.append({"type": "INVALID_STATE_ROW", "row": row})
            continue
        state_id = row["id"]
        if state_id in states:
            issues.append({"type": "DUPLICATE_STATE_ID", "state": state_id})
            continue
        try:
            support = row["support"]
            abstract_support = row["abstract_support"]
            if not isinstance(support, int) or support < 0:
                raise ValueError("support must be a nonnegative integer")
            if not isinstance(abstract_support, int) or abstract_support < 0:
                raise ValueError("abstract_support must be a nonnegative integer")
            objective_rank = rank_tuple(row["objective_rank"])
            if row.get("feasible") is not True:
                raise ValueError("all registered states must be feasible")
        except (KeyError, ValueError) as error:
            issues.append({"type": "INVALID_STATE", "state": state_id, "error": str(error)})
            continue
        normalized = dict(row)
        normalized["support"] = support
        normalized["abstract_support"] = abstract_support
        normalized["objective_rank_tuple"] = objective_rank
        normalized["semantics_token"] = canonical_json(row.get("semantics"))
        normalized["abstraction_token"] = canonical_json(row.get("abstraction"))
        states[state_id] = normalized
        if support != abstract_support:
            issues.append({
                "type": "SUPPORT_NOT_PRESERVED_BY_REPRESENTATION",
                "state": state_id,
                "production_support": support,
                "abstract_support": abstract_support,
            })

    def parse_moves(kind: str) -> tuple[list[dict[str, Any]], dict[str, tuple[str, ...]]]:
        rows = data.get(kind)
        if not isinstance(rows, list):
            issues.append({"type": "MISSING_MOVE_LIST", "move_kind": kind})
            rows = []
        parsed: list[dict[str, Any]] = []
        adjacency_sets: dict[str, set[str]] = defaultdict(set)
        seen = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                issues.append({"type": "INVALID_MOVE_ROW", "move_kind": kind, "index": index})
                continue
            source, target = row.get("source"), row.get("target")
            rule = row.get("rule_id")
            key = (source, target, rule)
            if key in seen:
                issues.append({"type": "DUPLICATE_MOVE", "move_kind": kind, "move": key})
                continue
            seen.add(key)
            if source not in states or target not in states or not isinstance(rule, str) or not rule:
                issues.append({"type": "INVALID_MOVE_ENDPOINT_OR_RULE", "move_kind": kind, "index": index, "row": row})
                continue
            source_state, target_state = states[source], states[target]
            if target_state["support"] >= source_state["support"]:
                issues.append({
                    "type": "MOVE_DOES_NOT_STRICTLY_REDUCE_SUPPORT",
                    "move_kind": kind,
                    "source": source,
                    "target": target,
                })
            if target_state["semantics_token"] != source_state["semantics_token"]:
                issues.append({
                    "type": "MOVE_CHANGES_DECLARED_SEMANTICS",
                    "move_kind": kind,
                    "source": source,
                    "target": target,
                })
            if target_state["objective_rank_tuple"] > source_state["objective_rank_tuple"]:
                issues.append({
                    "type": "MOVE_INCREASES_OBJECTIVE",
                    "move_kind": kind,
                    "source": source,
                    "target": target,
                    "source_rank": list(source_state["objective_rank_tuple"]),
                    "target_rank": list(target_state["objective_rank_tuple"]),
                })
            parsed.append(dict(row))
            adjacency_sets[source].add(target)
        adjacency = {source: tuple(sorted(targets)) for source, targets in adjacency_sets.items()}
        return parsed, adjacency

    weak_moves, weak_adjacency = parse_moves("weak_moves")
    production_moves, production_adjacency = parse_moves("production_moves")

    weak_reachability = {state_id: descendants(state_id, weak_adjacency) for state_id in states}
    production_reachability = {state_id: descendants(state_id, production_adjacency) for state_id in states}

    # Sound lifting: every declared weak move must be realizable as a finite path
    # in the complete production registry between the exact registered states.
    for move in weak_moves:
        if move["target"] not in production_reachability.get(move["source"], frozenset()):
            issues.append({
                "type": "WEAK_MOVE_NOT_LIFTED_BY_PRODUCTION_REGISTRY",
                "source": move["source"],
                "target": move["target"],
                "rule_id": move["rule_id"],
            })

    weak_terminals = sorted(state_id for state_id in states if not weak_adjacency.get(state_id, ()))
    production_terminals = sorted(state_id for state_id in states if not production_adjacency.get(state_id, ()))
    if not weak_terminals:
        issues.append({"type": "NO_WEAK_TERMINALS"})
    if not production_terminals:
        issues.append({"type": "NO_PRODUCTION_TERMINALS"})

    ceiling_failures = []
    weak_terminal_sets: dict[str, frozenset[str]] = {}
    production_terminal_sets: dict[str, frozenset[str]] = {}
    for state_id in states:
        weak_terminal_sets[state_id] = terminal_set(state_id, weak_adjacency)
        production_terminal_sets[state_id] = terminal_set(state_id, production_adjacency)
        if not weak_terminal_sets[state_id]:
            ceiling_failures.append({"state": state_id, "reason": "no reachable weak terminal"})
            continue
        minimum = min(states[terminal]["support"] for terminal in weak_terminal_sets[state_id])
        if minimum > claimed_bound:
            ceiling_failures.append({"state": state_id, "minimum_reachable_weak_terminal_support": minimum})
    if ceiling_failures:
        issues.append({"type": "WEAK_NORMALIZATION_CEILING_FAIL", "failures": ceiling_failures})

    computed_weak_terminal_complexity = max((states[state]["support"] for state in weak_terminals), default=None)
    if computed_weak_terminal_complexity != claimed_bound:
        issues.append({
            "type": "CLAIMED_WEAK_BOUND_NOT_EXACT_TERMINAL_COMPLEXITY",
            "claimed": claimed_bound,
            "computed": computed_weak_terminal_complexity,
        })

    witnesses = data.get("weak_terminal_witnesses")
    if not isinstance(witnesses, list) or not witnesses:
        issues.append({"type": "MISSING_WEAK_TERMINAL_WITNESS"})
        witnesses = []
    witness_rows = []
    for witness in witnesses:
        valid_state = witness in states
        weak_terminal = witness in weak_terminals
        matching_support = valid_state and states[witness]["support"] == claimed_bound
        production_terminal = witness in production_terminals
        witness_rows.append({
            "state": witness,
            "registered": valid_state,
            "weak_terminal": weak_terminal,
            "support_matches_claim": matching_support,
            "production_terminal": production_terminal,
            "production_successors": list(production_adjacency.get(witness, ())),
        })
    realizing_witnesses = [row for row in witness_rows if row["registered"] and row["weak_terminal"] and row["support_matches_claim"]]
    if not realizing_witnesses:
        issues.append({"type": "NO_REALIZING_MAXIMUM_WEAK_TERMINAL"})

    registry = data.get("production_registry")
    registry_complete = False
    if not isinstance(registry, dict):
        issues.append({"type": "MISSING_PRODUCTION_REGISTRY_RECEIPT"})
        registry = {}
    else:
        registry_complete = registry.get("declared_complete") is True
        if not registry_complete:
            issues.append({"type": "PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE"})
        if not valid_sha256(registry.get("source_manifest_sha256")):
            issues.append({"type": "INVALID_PRODUCTION_REGISTRY_SOURCE_DIGEST"})
        argument = registry.get("completeness_argument")
        if not isinstance(argument, str) or len(argument.strip()) < 30:
            issues.append({"type": "MISSING_PRODUCTION_REGISTRY_COMPLETENESS_ARGUMENT"})

    complete_move_irreducible_witnesses = [row for row in realizing_witnesses if row["production_terminal"]]

    production_min_terminal_support: dict[str, int | None] = {}
    for state_id, terminals in production_terminal_sets.items():
        production_min_terminal_support[state_id] = (
            min(states[terminal]["support"] for terminal in terminals) if terminals else None
        )
    computed_production_intrinsic_support = max(
        (value for value in production_min_terminal_support.values() if value is not None),
        default=None,
    )

    # Interaction audit: pair every one-step production peak and require a
    # common descendant only when the certificate requests confluence.
    local_peak_count = 0
    unjoinable_peaks = []
    for source, successors in production_adjacency.items():
        for left, right in itertools.combinations(successors, 2):
            local_peak_count += 1
            common = production_reachability[left] & production_reachability[right]
            if not common:
                unjoinable_peaks.append({"source": source, "left": left, "right": right})
    require_confluence = data.get("require_production_confluence") is True
    if require_confluence and unjoinable_peaks:
        issues.append({"type": "PRODUCTION_LOCAL_CONFLUENCE_FAIL", "peaks": unjoinable_peaks})

    terminal_signatures: dict[str, list[dict[str, Any]]] = {}
    for state_id, terminals in production_terminal_sets.items():
        terminal_signatures[state_id] = [
            {
                "state": terminal,
                "support": states[terminal]["support"],
                "semantics": states[terminal]["semantics"],
                "objective_rank": list(states[terminal]["objective_rank_tuple"]),
                "abstraction": states[terminal]["abstraction"],
            }
            for terminal in sorted(terminals)
        ]
    unique_terminal_state_for_every_source = all(len(terminals) == 1 for terminals in production_terminal_sets.values())

    hard_issue_types = {row["type"] for row in issues}
    registry_or_soundness_block = any(
        issue_type.startswith("INVALID_")
        or issue_type in {
            "MISSING_STATES",
            "DUPLICATE_STATE_ID",
            "INVALID_STATE_ROW",
            "INVALID_STATE",
            "MISSING_MOVE_LIST",
            "INVALID_MOVE_ROW",
            "DUPLICATE_MOVE",
            "INVALID_MOVE_ENDPOINT_OR_RULE",
            "MOVE_DOES_NOT_STRICTLY_REDUCE_SUPPORT",
            "MOVE_CHANGES_DECLARED_SEMANTICS",
            "MOVE_INCREASES_OBJECTIVE",
            "WEAK_MOVE_NOT_LIFTED_BY_PRODUCTION_REGISTRY",
            "NO_WEAK_TERMINALS",
            "NO_PRODUCTION_TERMINALS",
            "PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE",
            "MISSING_PRODUCTION_REGISTRY_RECEIPT",
            "MISSING_PRODUCTION_REGISTRY_COMPLETENESS_ARGUMENT",
            "PRODUCTION_LOCAL_CONFLUENCE_FAIL",
        }
        for issue_type in hard_issue_types
    )

    if registry_or_soundness_block:
        terminal = "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED"
    elif ceiling_failures or computed_weak_terminal_complexity != claimed_bound or not realizing_witnesses:
        terminal = "WEAK_CERTIFICATE_CLAIM_REJECTED"
    elif complete_move_irreducible_witnesses and computed_production_intrinsic_support == claimed_bound:
        terminal = "PRODUCTION_EXACT_TRANSFER_PASS"
    elif computed_production_intrinsic_support is not None and computed_production_intrinsic_support < claimed_bound:
        terminal = "PROOF_LANGUAGE_WASTE_CERTIFIED"
    else:
        terminal = "PRODUCTION_LOWER_TRANSFER_NOT_ESTABLISHED"

    if not registry_complete:
        warnings.append({
            "type": "DECLARED_FINITE_REGISTRY_ONLY",
            "message": "The checker cannot discover moves omitted from an external production implementation.",
        })

    result = {
        "schema": RESULT_SCHEMA,
        "instance_id": data.get("instance_id"),
        "input_sha256": sha256_json(data),
        "counts": {
            "states": len(states),
            "weak_moves": len(weak_moves),
            "production_moves": len(production_moves),
            "weak_terminals": len(weak_terminals),
            "production_terminals": len(production_terminals),
            "local_production_peaks": local_peak_count,
            "unjoinable_local_production_peaks": len(unjoinable_peaks),
        },
        "claims": {
            "claimed_weak_terminal_bound": claimed_bound,
            "computed_weak_terminal_complexity": computed_weak_terminal_complexity,
            "computed_production_intrinsic_support": computed_production_intrinsic_support,
            "certificate_waste": (
                claimed_bound - computed_production_intrinsic_support
                if computed_production_intrinsic_support is not None
                else None
            ),
        },
        "realization_gate": {
            "support_preserving_representation": not any(row["type"] == "SUPPORT_NOT_PRESERVED_BY_REPRESENTATION" for row in issues),
            "weak_moves_soundly_lifted": not any(row["type"] == "WEAK_MOVE_NOT_LIFTED_BY_PRODUCTION_REGISTRY" for row in issues),
            "realizing_maximum_weak_terminal": bool(realizing_witnesses),
            "complete_move_irreducible_witness": bool(complete_move_irreducible_witnesses),
            "production_registry_declared_complete": registry_complete,
            "witnesses": witness_rows,
        },
        "interaction_audit": {
            "confluence_required": require_confluence,
            "unjoinable_local_peaks": unjoinable_peaks,
            "unique_terminal_state_for_every_source": unique_terminal_state_for_every_source,
            "terminal_signatures": terminal_signatures,
        },
        "production_minimum_terminal_support_by_state": production_min_terminal_support,
        "issues": issues,
        "warnings": warnings,
        "terminal": terminal,
        "authority": {
            "finite_declared_registry_checked": True,
            "external_registry_completeness_proved_by_checker": False,
            "production_application_authority": terminal == "PRODUCTION_EXACT_TRANSFER_PASS",
            "journal_authority": False,
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="finite production-realization certificate JSON")
    parser.add_argument("--output", help="result JSON path")
    args = parser.parse_args()
    input_path = Path(args.input)
    data = json.loads(input_path.read_text(encoding="utf-8"))
    result = check_instance(data)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
