#!/usr/bin/env python3
"""Additive hostile-review audit for the frozen ORION-01 R11 registry.

The prospectively frozen runner and raw result remain byte-identical.  This
checker addresses two post-outcome review findings without retroactively
editing them: the original in-function omission loop was non-identifying, and
the original AST comparison filtered calls through a known-symbol whitelist.
"""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / "orion01_r11_pyzx_round1.py"
REGISTRY_PATH = HERE / "ORION01_R11_PYZX_SOURCE_REGISTRY.json"
RESULT_PATH = HERE / "ORION01_R11_PYZX_RESULTS.json"
RECEIPT_PATH = HERE / "ORION01_R11_POST_REVIEW_REGISTRY_AUDIT.json"

SPEC = importlib.util.spec_from_file_location("orion01_r11_pyzx_round1", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot load frozen Round-1 runner")
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
SPEC.loader.exec_module(study)


EXPECTED_ALL_CALLS = {
    "clifford_simp": ["interior_clifford_simp", "pivot_boundary_simp"],
    "full_reduce": [
        "ValueError",
        "any",
        "copy_simp",
        "g.remove_isolated_vertices",
        "g.types",
        "g.vertices",
        "gadget_simp",
        "interior_clifford_simp",
        "pivot_gadget_simp",
        "supplementarity_simp",
        "clifford_simp",
    ],
    "interior_clifford_simp": [
        "id_simp",
        "lcomp_simp",
        "pivot_simp",
        "spider_simp",
        "to_gh",
    ],
    "spider_simp": ["fuse_simp", "remove_self_loop_simp"],
}
EXPECTED_ALL_CALLS = {key: sorted(value) for key, value in EXPECTED_ALL_CALLS.items()}
BENIGN_NONMUTATING_CALLS = {
    "clifford_simp": [],
    "full_reduce": ["ValueError", "any", "g.types", "g.vertices"],
    "interior_clifford_simp": [],
    "spider_simp": [],
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_name(node: ast.Call) -> str:
    value = node.func
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Attribute):
        parts = []
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
            return ".".join(reversed(parts))
    raise study.StudyFailure(f"unclassified call expression: {ast.dump(node.func)}")


def expected_call_inventory(registry: Mapping[str, Any]) -> dict[str, list[str]]:
    expected: dict[str, list[str]] = {}
    for parent, children in registry["control_call_graph"].items():
        normalized = [
            "g.remove_isolated_vertices"
            if child == "BaseGraph.remove_isolated_vertices"
            else child
            for child in children
        ]
        expected[parent] = sorted(normalized + BENIGN_NONMUTATING_CALLS[parent])
    return expected


def full_call_inventory(registry: Mapping[str, Any]) -> dict[str, list[str]]:
    study.verify_installed_source(registry)
    source = study.pyzx_source_root() / "pyzx/simplify.py"
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    observed = {
        name: sorted({call_name(node) for node in ast.walk(functions[name]) if isinstance(node, ast.Call)})
        for name in EXPECTED_ALL_CALLS
    }
    expected = expected_call_inventory(registry)
    if expected != EXPECTED_ALL_CALLS and registry == study.load_registry():
        raise study.StudyFailure(
            f"frozen registry/full-call expectation mismatch: expected={expected} "
            f"frozen={EXPECTED_ALL_CALLS}"
        )
    if observed != expected:
        extra = {
            parent: sorted(set(observed[parent]) - set(expected[parent]))
            for parent in observed
            if set(observed[parent]) - set(expected[parent])
        }
        missing = {
            parent: sorted(set(expected[parent]) - set(observed[parent]))
            for parent in observed
            if set(expected[parent]) - set(observed[parent])
        }
        kind = "unregistered pinned source call" if extra else "missing pinned source call"
        raise study.StudyFailure(
            f"{kind}: extra={extra} missing={missing} observed={observed} expected={expected}"
        )
    return observed


def mutation_replay(registry: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = []
    for symbol in registry["registered_symbol_order"]:
        mutated = deepcopy(registry)
        mutated["registered_symbol_order"] = [
            item for item in mutated["registered_symbol_order"] if item != symbol
        ]
        mutated["registered_schemas"] = [
            item for item in mutated["registered_schemas"] if item["symbol"] != symbol
        ]
        removed_from_graph = 0
        for parent, children in mutated["control_call_graph"].items():
            retained = []
            for child in children:
                normalized = (
                    "remove_isolated_vertices"
                    if child == "BaseGraph.remove_isolated_vertices"
                    else child
                )
                if normalized == symbol:
                    removed_from_graph += 1
                else:
                    retained.append(child)
            mutated["control_call_graph"][parent] = retained
        if removed_from_graph != 1:
            raise study.StudyFailure(
                f"registry symbol does not have one control-graph surface: {symbol}"
            )
        try:
            full_call_inventory(mutated)
        except study.StudyFailure as error:
            if "unregistered pinned source call" not in str(error):
                raise
            rows.append(
                {
                    "omitted": symbol,
                    "disposition": "REJECTED",
                    "reason": str(error),
                    "registry_surface_removed": True,
                    "rejection_kind": "UNREGISTERED_PINNED_SOURCE_CALL",
                }
            )
        else:  # pragma: no cover - enforced by the hostile mutation replay
            raise study.StudyFailure(f"mutated registry omission was accepted: {symbol}")
    return rows


def build_receipt() -> dict[str, Any]:
    registry = study.load_registry()
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    inventory = full_call_inventory(registry)
    mutations = mutation_replay(registry)
    if result["terminal"] != study.FAIL_TERMINAL:
        raise study.StudyFailure("raw adverse terminal drift")
    if len(mutations) != 12 or any(row["disposition"] != "REJECTED" for row in mutations):
        raise study.StudyFailure("post-review omission replay incomplete")
    return {
        "schema": "ORION.ORION01.R11.PostReviewRegistryAudit.v1",
        "date": "2026-08-27",
        "paper_id": "ORION-01",
        "round": 1,
        "terminal": "ORION01_R11_POST_REVIEW_REGISTRY_AUDIT_PASS__ADVERSE_TERMINAL_UNCHANGED",
        "raw_science_terminal": study.FAIL_TERMINAL,
        "bindings": {
            "raw_result_sha256": sha256_file(RESULT_PATH),
            "frozen_registry_sha256": sha256_file(REGISTRY_PATH),
            "frozen_runner_sha256": sha256_file(RUNNER_PATH),
            "pyzx_commit": study.EXPECTED_COMMIT,
        },
        "review_findings": {
            "original_inline_omission_loop": {
                "disposition": "NON_IDENTIFYING_TAUTOLOGICAL_COMPARISON__NOT_AUTHORITY",
                "raw_bytes_rewritten": False,
                "repair": "ACTUAL_MUTATED_REGISTRY_REPLAY",
            },
            "original_whitelist_filtered_ast_comparison": {
                "disposition": "INSUFFICIENT_ALONE_TO_EXCLUDE_UNKNOWN_CALLS",
                "raw_bytes_rewritten": False,
                "repair": "FULL_PINNED_CONTROL_CALL_INVENTORY_WITH_EXPLICIT_BENIGN_CLASSIFICATION",
            },
            "first_post_review_mutation_replay": {
                "disposition": "INTERNAL_FIELD_MISMATCH__NOT_INDEPENDENT_SOURCE_OMISSION_AUTHORITY",
                "raw_bytes_rewritten": False,
                "repair": "REMOVE_EACH_SYMBOL_FROM_ALL_REGISTRY_SURFACES_AND_RERUN_UNFILTERED_SOURCE_CALL_AUDIT",
            },
        },
        "full_pinned_control_call_inventory": inventory,
        "explicit_benign_nonmutating_calls": BENIGN_NONMUTATING_CALLS,
        "mutated_registry_omissions": mutations,
        "mutated_registry_omissions_rejected": len(mutations),
        "scientific_disposition": {
            "bounded_counterexample_unchanged": True,
            "round_1_consumed_as_adverse_cannot_check": True,
            "production_full_reduce_refuted": False,
            "complete_contextual_registry_established": False,
            "realized_certificate_gap_established": False,
            "bounded_null_established": False,
        },
        "authority": {
            "post_review_structural_corroboration": "SAME_OWNER_LOCAL_REPLAY_ONLY",
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
            "submission_authorized": False,
            "protected_task3_or_p9": False,
        },
    }


def render(receipt: Mapping[str, Any]) -> str:
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rendered = render(build_receipt())
    if args.write:
        RECEIPT_PATH.write_text(rendered, encoding="utf-8")
    elif not RECEIPT_PATH.is_file() or RECEIPT_PATH.read_text(encoding="utf-8") != rendered:
        print("committed post-review receipt differs from fresh audit", file=sys.stderr)
        return 1
    print("ORION01_R11_POST_REVIEW_REGISTRY_AUDIT_PASS__ADVERSE_TERMINAL_UNCHANGED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
