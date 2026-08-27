#!/usr/bin/env python3
"""Reproduce the adverse contextual-guard counterexample from ORION-01 R11."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / "orion01_r11_pyzx_round1.py"
RESULT_PATH = HERE / "ORION01_R11_PYZX_RESULTS.json"
BEFORE_PATH = HERE / "ORION01_R11_PYZX_COUNTEREXAMPLE_BEFORE.json"
AFTER_PATH = HERE / "ORION01_R11_PYZX_COUNTEREXAMPLE_AFTER.json"
FAILURE_01 = HERE / "ORION01_R11_EXECUTION_FAILURE_01.json"
FAILURE_02 = HERE / "ORION01_R11_EXECUTION_FAILURE_02.json"

SPEC = importlib.util.spec_from_file_location("orion01_r11_pyzx_round1", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot load frozen Round-1 runner")
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
SPEC.loader.exec_module(study)


def rounded_matrix(matrix: np.ndarray[Any, Any]) -> list[list[list[float]]]:
    return [
        [
            [round(float(value.real), 12), round(float(value.imag), 12)]
            for value in row
        ]
        for row in matrix
    ]


def file_binding(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(study.REPO_ROOT).as_posix(),
        "sha256": study.sha256_bytes(data),
        "bytes": len(data),
    }


def verify_counterexample() -> dict[str, Any]:
    registry = study.load_registry()
    source_binding = study.verify_installed_source(registry)
    registry_audit = study.derive_source_registry(registry)
    freeze = study.protocol_freeze_binding()
    authority_controls = study.hostile_authority_controls()

    word = ("H0", "H0", "H0")
    all_words = list(study.all_gate_words(4))
    word_index = all_words.index(word)
    if word_index != 73:
        raise study.StudyFailure(f"counterexample word index drift: {word_index}")

    start = study.start_state_from_word(word)
    current = start
    path = ("pivot_boundary_simp", "copy_simp", "to_gh")
    path_checks: list[dict[str, Any]] = []
    operations = study.operation_map()
    for symbol in path:
        successor = study.apply_operation(current, operations[symbol])
        if successor is None:
            raise study.StudyFailure(f"counterexample prefix operation not applicable: {symbol}")
        before_matrix = study.dense_matrix(current)
        after_matrix = study.dense_matrix(successor)
        exact = study.matrices_equal(before_matrix, after_matrix)
        if not exact:
            raise study.StudyFailure(f"counterexample prefix changed semantics: {symbol}")
        path_checks.append(
            {
                "symbol": symbol,
                "before_sha256": study.sha256_text(current),
                "after_sha256": study.sha256_text(successor),
                "dense_semantics_including_scalar": exact,
            }
        )
        current = successor

    committed_before = BEFORE_PATH.read_text(encoding="utf-8")
    if current != committed_before:
        raise study.StudyFailure("committed predecessor graph differs from fresh replay")
    if study.sha256_text(current) != "fc217397673f7daf78672942239dfbb0c4596e5e07a3ff892b9003a0d60353c0":
        raise study.StudyFailure("predecessor graph digest drift")

    after = study.apply_operation(current, operations["pivot_boundary_simp"])
    if after is None:
        raise study.StudyFailure("adverse pivot_boundary_simp guard no longer accepts witness")
    committed_after = AFTER_PATH.read_text(encoding="utf-8")
    if after != committed_after:
        raise study.StudyFailure("committed successor graph differs from fresh replay")
    if study.sha256_text(after) != "102babf6392e6d16136d262f967d49990a4075db36c39823b148de124ace038d":
        raise study.StudyFailure("successor graph digest drift")

    before_matrix = study.dense_matrix(current)
    after_matrix = study.dense_matrix(after)
    equal_including_scalar = study.matrices_equal(before_matrix, after_matrix)
    equal_up_to_scalar = bool(
        study.pyzx.tensor.compare_tensors(before_matrix, after_matrix, preserve_scalar=False)
    )
    if equal_including_scalar or equal_up_to_scalar:
        raise study.StudyFailure("registered adverse transition no longer changes semantics")

    production_graph = study.graph_from_state(start)
    study.pyzx.simplify.full_reduce(production_graph)
    production_state = study.source_graph_state(production_graph)
    production_semantics = study.matrices_equal(
        study.dense_matrix(start), study.dense_matrix(production_state)
    )
    if not production_semantics:
        raise study.StudyFailure("production full_reduce changed witness semantics")

    residual = before_matrix - after_matrix
    result = {
        "schema": "ORION.ORION01.R11.PyZXFullReduceRound1AdverseResults.v1",
        "date": "2026-08-27",
        "paper_id": "ORION-01",
        "round": 1,
        "terminal": study.FAIL_TERMINAL,
        "disposition": "FREE_REORDERING_CONTEXTUAL_GUARD_UNSOUND__PRODUCTION_ENTRYPOINT_NOT_REFUTED",
        "protocol_freeze": freeze,
        "source_binding": source_binding,
        "registry_audit": registry_audit,
        "input_domain": {
            **registry["input_domain"],
            "executed_before_fail_closed_terminal": word_index + 1,
            "first_failing_word_zero_based_index": word_index,
            "first_failing_word_one_based_ordinal": word_index + 1,
            "complete_domain_executed": False,
        },
        "counterexample": {
            "source_word": list(word),
            "source_word_label": "H0,H0,H0",
            "start_state_sha256": study.sha256_text(start),
            "semantics_preserving_prefix": path_checks,
            "adverse_operation": "pivot_boundary_simp",
            "adverse_operation_registered_id": "PYZX.FR.07",
            "adverse_guard_accepted": True,
            "before": file_binding(BEFORE_PATH),
            "after": file_binding(AFTER_PATH),
            "before_resource": list(study.resource(study.graph_from_state(current))),
            "after_resource": list(study.resource(study.graph_from_state(after))),
            "before_structural_measure": list(
                study.structural_measure(study.graph_from_state(current))
            ),
            "after_structural_measure": list(
                study.structural_measure(study.graph_from_state(after))
            ),
            "dense_semantics_equal_including_scalar": equal_including_scalar,
            "dense_semantics_equal_up_to_nonzero_scalar": equal_up_to_scalar,
            "before_matrix_real_imag": rounded_matrix(before_matrix),
            "after_matrix_real_imag": rounded_matrix(after_matrix),
            "max_absolute_matrix_residual": round(float(np.max(np.abs(residual))), 12),
            "frobenius_matrix_residual": round(float(np.linalg.norm(residual)), 12),
            "production_full_reduce_on_same_source_word": {
                "semantics_equal_including_scalar": production_semantics,
                "output_state_sha256": study.sha256_text(production_state),
                "output_resource": list(study.resource(production_graph)),
            },
        },
        "hostile_authority_controls": authority_controls,
        "execution_failure_custody": [file_binding(FAILURE_01), file_binding(FAILURE_02)],
        "gates": {
            "exact_public_source_identity": True,
            "complete_ast_symbol_inventory": True,
            "all_single_registry_omissions_rejected": True,
            "semantics_preserving_prefix_replayed": True,
            "registered_guard_accepts_adverse_transition": True,
            "adverse_transition_changes_dense_semantics_including_scalar": True,
            "adverse_transition_changes_dense_semantics_even_up_to_scalar": True,
            "production_entrypoint_semantics_preserved_on_witness": True,
            "free_reordering_semantics_gate": False,
            "complete_frozen_domain_search": False,
            "strict_gap_or_bounded_null_authorized": False,
        },
        "round_accounting": {
            "consumed": 1,
            "maximum": 3,
            "round_disposition": "ADVERSE_CANNOT_CHECK",
            "science_status_after_this_round": "OPEN",
            "next_round_required": True,
            "same_incomplete_macro_language_may_not_be_relabeled_as_round_2": True,
        },
        "next_gate": (
            "Round 2 must use a scientifically distinct subject with source-complete "
            "contextual scheduler guards, or another public finite grammar; it may not "
            "delete the counterexample or silently restrict PYZX.FR.07 after outcome access."
        ),
        "claim_boundary": {
            "established": (
                "A deterministic bounded counterexample shows that freely reordering the "
                "twelve automatic full_reduce macro operations under only their callable "
                "guards is not a sound semantics-preserving production language."
            ),
            "not_established": [
                "PyZX full_reduce is unsound in its source scheduler",
                "all PyZX pivot-boundary uses are unsound",
                "a complete contextual PyZX production registry",
                "a realized certificate gap",
                "the complete-domain bounded null",
                "all-PyZX or all-ZX-calculus completeness",
                "generic compiler optimality or speedup",
                "physical or hardware advantage",
                "external novelty or journal authority",
                "submission readiness or authorization",
            ],
        },
        "authority": {
            "bounded_counterexample_established": True,
            "production_full_reduce_refuted": False,
            "complete_contextual_registry_established": False,
            "realized_certificate_gap_established": False,
            "bounded_null_established": False,
            "all_pyzx_completeness": False,
            "all_zx_calculus_completeness": False,
            "generic_compiler_optimality": False,
            "physical_or_hardware_advantage": False,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
            "submission_authorized": False,
            "protected_task3_or_p9": False,
        },
    }
    return result


def render(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rendered = render(verify_counterexample())
    if args.write:
        RESULT_PATH.write_text(rendered, encoding="utf-8")
    elif not RESULT_PATH.is_file() or RESULT_PATH.read_text(encoding="utf-8") != rendered:
        print("committed adverse result differs from fresh replay", file=sys.stderr)
        return 1
    print(study.FAIL_TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
