#!/usr/bin/env python3
"""Positive and hostile controls for the finite AB production-realization gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from finite_production_realization_gate_r9_v2 import check_instance

DIGEST = "0" * 64


def state(
    identifier: str,
    support: int,
    semantics: str = "sigma",
    objective: int = 0,
    abstraction: str | None = None,
    abstract_support: int | None = None,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "feasible": True,
        "support": support,
        "abstract_support": support if abstract_support is None else abstract_support,
        "semantics": semantics,
        "objective_rank": [objective],
        "abstraction": identifier if abstraction is None else abstraction,
    }


def move(source: str, target: str, rule: str) -> dict[str, str]:
    return {"source": source, "target": target, "rule_id": rule}


def certificate(
    identifier: str,
    states: list[dict[str, Any]],
    weak_moves: list[dict[str, str]],
    production_moves: list[dict[str, str]],
    bound: int,
    witnesses: list[str],
    complete: bool = True,
    require_confluence: bool = False,
) -> dict[str, Any]:
    return {
        "schema": "ORION.AB.FiniteProductionRealizationInstanceR9.v1",
        "instance_id": identifier,
        "claimed_weak_terminal_bound": bound,
        "states": states,
        "weak_moves": weak_moves,
        "production_moves": production_moves,
        "weak_terminal_witnesses": witnesses,
        "production_registry": {
            "declared_complete": complete,
            "source_manifest_sha256": DIGEST,
            "completeness_argument": (
                "This finite hostile control explicitly enumerates every admitted production shortening edge."
            ),
        },
        "require_production_confluence": require_confluence,
        "authority": {
            "finite_control_only": True,
            "external_registry_completeness": False,
            "journal_authority": False,
        },
    }


def main() -> None:
    controls: list[tuple[str, dict[str, Any], str, set[str]]] = []

    controls.append((
        "exact_transfer",
        certificate(
            "exact-transfer",
            [state("a", 2), state("b", 1, abstraction="total")],
            [move("a", "b", "weak-delete")],
            [move("a", "b", "production-delete")],
            1,
            ["b"],
            require_confluence=True,
        ),
        "PRODUCTION_EXACT_TRANSFER_PASS",
        set(),
    ))

    controls.append((
        "certificate_waste",
        certificate(
            "certificate-waste",
            [state("weak-terminal", 3, abstraction="zero-sum-free-word"), state("singleton", 1, abstraction="total")],
            [],
            [move("weak-terminal", "singleton", "complete-fusion")],
            3,
            ["weak-terminal"],
            require_confluence=True,
        ),
        "PROOF_LANGUAGE_WASTE_CERTIFIED",
        set(),
    ))

    controls.append((
        "semantic_unsoundness",
        certificate(
            "semantic-unsoundness",
            [state("a", 2, semantics="left"), state("b", 1, semantics="right")],
            [move("a", "b", "weak")],
            [move("a", "b", "production")],
            1,
            ["b"],
        ),
        "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED",
        {"MOVE_CHANGES_DECLARED_SEMANTICS"},
    ))

    controls.append((
        "objective_increase",
        certificate(
            "objective-increase",
            [state("a", 2, objective=0), state("b", 1, objective=1)],
            [move("a", "b", "weak")],
            [move("a", "b", "production")],
            1,
            ["b"],
        ),
        "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED",
        {"MOVE_INCREASES_OBJECTIVE"},
    ))

    controls.append((
        "support_map_mismatch",
        certificate(
            "support-map-mismatch",
            [state("a", 2), state("b", 1, abstract_support=2)],
            [move("a", "b", "weak")],
            [move("a", "b", "production")],
            2,
            ["b"],
        ),
        "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED",
        {"SUPPORT_NOT_PRESERVED_BY_REPRESENTATION"},
    ))

    controls.append((
        "unlifted_weak_move",
        certificate(
            "unlifted-weak-move",
            [state("a", 2), state("b", 1, abstraction="weak-target"), state("c", 1, abstraction="production-target")],
            [move("a", "b", "weak")],
            [move("a", "c", "production")],
            1,
            ["b"],
        ),
        "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED",
        {"WEAK_MOVE_NOT_LIFTED_BY_PRODUCTION_REGISTRY"},
    ))

    controls.append((
        "incomplete_registry",
        certificate(
            "incomplete-registry",
            [state("a", 2), state("b", 1)],
            [move("a", "b", "weak")],
            [move("a", "b", "production")],
            1,
            ["b"],
            complete=False,
        ),
        "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED",
        {"PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE"},
    ))

    controls.append((
        "nonconfluent_interaction",
        certificate(
            "nonconfluent-interaction",
            [state("a", 2), state("b", 1, abstraction="left-normal"), state("c", 1, abstraction="right-normal")],
            [move("a", "b", "weak")],
            [move("a", "b", "left"), move("a", "c", "right")],
            1,
            ["b"],
            require_confluence=True,
        ),
        "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED",
        {"PRODUCTION_LOCAL_CONFLUENCE_FAIL"},
    ))

    rows = []
    for name, instance, expected_terminal, required_issues in controls:
        result = check_instance(instance)
        observed_issues = {row["type"] for row in result["issues"]}
        assert result["terminal"] == expected_terminal, (name, result["terminal"], expected_terminal)
        assert required_issues <= observed_issues, (name, required_issues, observed_issues)
        rows.append({
            "control": name,
            "expected_terminal": expected_terminal,
            "observed_terminal": result["terminal"],
            "required_issue_types": sorted(required_issues),
            "observed_issue_types": sorted(observed_issues),
            "input_sha256": hashlib.sha256(json.dumps(instance, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "status": "PASS",
        })

    output = {
        "schema": "ORION.AB.FiniteProductionRealizationGateControlsR9.v1",
        "checker": "finite_production_realization_gate_r9_v2.py",
        "controls": rows,
        "summary": {
            "control_count": len(rows),
            "passes": len(rows),
            "failures": 0,
            "status": "PASS",
        },
        "authority": {
            "finite_checker_controls": True,
            "external_registry_completeness": False,
            "pauli_or_TARE_application_validated": False,
            "grants_journal_authority": False,
        },
        "terminal": "AB_FINITE_PRODUCTION_REALIZATION_GATE__POSITIVE_AND_HOSTILE_CONTROLS_PASS",
    }
    path = Path(__file__).with_name("FINITE_PRODUCTION_REALIZATION_GATE_CONTROLS_R9_RESULTS.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
