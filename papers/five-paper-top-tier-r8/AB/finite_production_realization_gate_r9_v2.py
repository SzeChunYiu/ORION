#!/usr/bin/env python3
"""Authoritative V2 terminal policy for the finite AB realization checker."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from finite_production_realization_gate_r9 import check_instance as check_v1

HARD_REALIZATION_ISSUES = {
    "SUPPORT_NOT_PRESERVED_BY_REPRESENTATION",
    "INVALID_SCHEMA",
    "INVALID_CLAIMED_BOUND",
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
    "MISSING_PRODUCTION_REGISTRY_RECEIPT",
    "PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE",
    "INVALID_PRODUCTION_REGISTRY_SOURCE_DIGEST",
    "MISSING_PRODUCTION_REGISTRY_COMPLETENESS_ARGUMENT",
    "PRODUCTION_LOCAL_CONFLUENCE_FAIL",
}
WEAK_CLAIM_ISSUES = {
    "WEAK_NORMALIZATION_CEILING_FAIL",
    "CLAIMED_WEAK_BOUND_NOT_EXACT_TERMINAL_COMPLEXITY",
    "MISSING_WEAK_TERMINAL_WITNESS",
    "NO_REALIZING_MAXIMUM_WEAK_TERMINAL",
}


def check_instance(data: dict[str, Any]) -> dict[str, Any]:
    result = check_v1(data)
    issue_types = {row["type"] for row in result["issues"]}
    if issue_types & HARD_REALIZATION_ISSUES:
        terminal = "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED"
    elif issue_types & WEAK_CLAIM_ISSUES:
        terminal = "WEAK_CERTIFICATE_CLAIM_REJECTED"
    elif (
        result["realization_gate"]["complete_move_irreducible_witness"]
        and result["claims"]["computed_production_intrinsic_support"]
        == result["claims"]["claimed_weak_terminal_bound"]
    ):
        terminal = "PRODUCTION_EXACT_TRANSFER_PASS"
    elif (
        result["claims"]["computed_production_intrinsic_support"] is not None
        and result["claims"]["computed_production_intrinsic_support"]
        < result["claims"]["claimed_weak_terminal_bound"]
    ):
        terminal = "PROOF_LANGUAGE_WASTE_CERTIFIED"
    else:
        terminal = "PRODUCTION_LOWER_TRANSFER_NOT_ESTABLISHED"
    result["schema"] = "ORION.AB.FiniteProductionRealizationResultR9.v2"
    result["terminal_policy"] = {
        "version": 2,
        "support_preservation_is_hard_gate": True,
        "hard_realization_issue_types": sorted(HARD_REALIZATION_ISSUES),
        "weak_claim_issue_types": sorted(WEAK_CLAIM_ISSUES),
    }
    result["terminal"] = terminal
    result["authority"]["production_application_authority"] = terminal == "PRODUCTION_EXACT_TRANSFER_PASS"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = check_instance(data)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
