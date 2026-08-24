#!/usr/bin/env python3
"""Fail-closed V9 adapter gate for outcome-free DGM initialization.

This module never imports or executes DGM. It opens only the exact
candidate-safe DGM_outer.py member, proves whether the released initialization
contract admits a nondegenerate outcome-free parent, and stops if not.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any

EXPECTED_SEED_SHA256 = "8d7197f581cad11695ae4c867ad8f941d86f7eeec8d0e8e4e7b79895d72b8f2d"
EXPECTED_DGM_OUTER_SHA256 = "239bc76f0e1b78210b8f7b3757b1082f6ca07db3537d6af50a45bf97709795ed"
EXPECTED_PREREGISTRATION_SHA256 = "18946ca0493bb73a3c52f51a0cef5910b11f19e0e89c6da34f272c761076718c"
DGM_MEMBER = "candidate/dgm/DGM_outer.py"
TERMINAL = (
    "P5_C3_V9_OUTCOME_FREE_INITIALIZATION_ADAPTER_STOPPED__"
    "UNCHANGED_NATIVE_PARENT_SELECTION_REQUIRES_PRIOR_OUTCOME_METADATA__"
    "NO_LAWFUL_SEMANTICS_PRESERVING_ADAPTER__RUNTIME_TASK_ENVIRONMENT_REMAINS_BLOCKING"
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def constants(node: ast.AST) -> set[str]:
    return {child.value for child in ast.walk(node) if isinstance(child, ast.Constant) and isinstance(child.value, str)}


def function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise RuntimeError(f"missing native function: {name}")


def call_names(node: ast.AST) -> list[str]:
    names = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        target = child.func
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, ast.Attribute):
            base = target.value.id if isinstance(target.value, ast.Name) else ""
            names.append(f"{base}.{target.attr}" if base else target.attr)
    return names


def line_window(source: str, start: int, end: int) -> str:
    rows = source.splitlines()
    return "\n".join(f"{number}: {rows[number - 1]}" for number in range(start, end + 1)) + "\n"


def analyze(seed: Path, preregistration: Path) -> dict[str, Any]:
    seed_sha = file_digest(seed)
    prereg_sha = file_digest(preregistration)
    if seed_sha != EXPECTED_SEED_SHA256:
        raise RuntimeError(f"V8 seed identity mismatch: {seed_sha}")
    if prereg_sha != EXPECTED_PREREGISTRATION_SHA256:
        raise RuntimeError(f"preregistration identity mismatch: {prereg_sha}")

    with tarfile.open(seed, "r:gz") as archive:
        member = archive.getmember(DGM_MEMBER)
        handle = archive.extractfile(member)
        if handle is None:
            raise RuntimeError("DGM_outer member unreadable")
        raw = handle.read()
    if digest(raw) != EXPECTED_DGM_OUTER_SHA256:
        raise RuntimeError("DGM_outer identity mismatch")

    source = raw.decode("utf-8")
    tree = ast.parse(source, filename=DGM_MEMBER)
    initialize = function(tree, "initialize_run")
    choose = function(tree, "choose_selfimproves")
    main = function(tree, "main")
    init_constants = constants(initialize)
    choose_constants = constants(choose)
    main_constants = constants(main)
    choose_calls = call_names(choose)

    required_prior_fields = sorted(
        {
            "overall_performance",
            "accuracy_score",
            "total_unresolved_ids",
            "total_emptypatch_ids",
            "total_resolved_ids",
        }
        & choose_constants
    )
    gates = {
        "fresh_archive_is_nonempty_initial": "initial" in init_constants,
        "fresh_initial_directory_required": "Error: Need to properly configure evaluation results for the initial version." in init_constants,
        "native_parent_eligibility_reads_overall_performance": "overall_performance" in choose_constants,
        "native_parent_eligibility_reads_all_four_prior_fields": required_prior_fields == [
            "accuracy_score",
            "overall_performance",
            "total_emptypatch_ids",
            "total_resolved_ids",
            "total_unresolved_ids",
        ],
        "missing_parent_metadata_is_caught_and_skipped": any(isinstance(node, ast.Continue) for node in ast.walk(choose)) and any(isinstance(node, ast.ExceptHandler) for node in ast.walk(choose)),
        "nondegenerate_random_route_requires_candidates": "random.choices" in choose_calls,
        "no_released_outcome_free_initialization_argument": not any("outcome_free" in value for value in main_constants),
    }
    if not all(gates.values()):
        raise RuntimeError(f"exact-source microgate shape drift: {gates}")

    strategy_adjudication = [
        {
            "strategy": "RESTORE_NATIVE_INITIAL_METADATA",
            "admissible": False,
            "reason": "Requires excluded initial/ prior-result payloads.",
        },
        {
            "strategy": "SYNTHESIZE_NEUTRAL_OR_ZERO_OVERALL_PERFORMANCE",
            "admissible": False,
            "reason": "Fabricates prior performance and identifier partitions that native selection consumes.",
        },
        {
            "strategy": "EMPTY_ARCHIVE_OR_ZERO_SELFIMPROVE_OR_ZERO_GENERATIONS",
            "admissible": False,
            "reason": "Avoids rather than preserves a nondegenerate C3 parent-selection and self-edit route.",
        },
        {
            "strategy": "REPLACE_NATIVE_PARENT_SELECTION_WITH_INPUT_CERTIFICATE_ONLY",
            "admissible": False,
            "reason": "Materially replaces the released score/count-dependent parent-eligibility semantics.",
        },
    ]
    return {
        "schema_version": "orion.p5.c3.outcome-free-initializer-adapter-result.v9",
        "adapter_id": "DGM_OUTCOME_FREE_INITIALIZATION_ADAPTER_V9",
        "authority": "STATIC_EXACT_BYTE_AND_AST_MICROGATE_ONLY",
        "predecessor_seed_sha256": seed_sha,
        "preregistration_sha256": prereg_sha,
        "source_member": DGM_MEMBER,
        "source_member_sha256": digest(raw),
        "source_lines_examined": [[15, 35], [50, 68], [215, 320]],
        "source_excerpt_sha256": digest((line_window(source, 15, 35) + line_window(source, 50, 68)).encode("utf-8")),
        "gates": gates,
        "required_prior_fields": required_prior_fields,
        "strategy_adjudication": strategy_adjudication,
        "native_semantics_preservable": False,
        "adapter_materialized": False,
        "initial_directory_materialized": False,
        "prior_performance_fields_created": False,
        "dgm_source_mutated": False,
        "lang1_core_mutated": False,
        "executions": {"dgm": 0, "model": 0, "benchmark": 0, "scorer": 0, "outcomes": 0, "tests": 0},
        "field": "runtime.task_environment",
        "field_status": "BLOCKING",
        "field_instances_closed": 0,
        "residual": "NATIVE_C3_INITIAL_PARENT_ELIGIBILITY_REQUIRES_REAL_PRIOR_OUTCOME_METADATA",
        "next_discriminator": "An upstream DGM release must define an outcome-free initial parent and selection semantics natively; otherwise a changed parent selector is a new comparator, not a semantics-preserving C3 adapter.",
        "claims": {"execution_readiness": "NOT_ESTABLISHED", "performance": "CANNOT_CHECK", "superiority": "CANNOT_CHECK"},
        "terminal": TERMINAL,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True, type=Path)
    parser.add_argument("--preregistration", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.seed, args.preregistration)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["terminal"])
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
