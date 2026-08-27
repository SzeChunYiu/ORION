#!/usr/bin/env python3
"""Replay the ORION-01 R11 adverse core without the disputed AST audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / "orion01_r11_pyzx_round1.py"
RESULT_PATH = HERE / "ORION01_R11_PYZX_RESULTS.json"
BEFORE_PATH = HERE / "ORION01_R11_PYZX_COUNTEREXAMPLE_BEFORE.json"
AFTER_PATH = HERE / "ORION01_R11_PYZX_COUNTEREXAMPLE_AFTER.json"

SPEC = importlib.util.spec_from_file_location("orion01_r11_pyzx_round1", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot load frozen Round-1 runner")
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
SPEC.loader.exec_module(study)


def verify_adverse_core() -> dict[str, Any]:
    registry = study.load_registry()
    source_binding = study.verify_installed_source(registry)
    committed = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    if committed["terminal"] != study.FAIL_TERMINAL:
        raise study.StudyFailure("committed terminal drift")

    word = ("H0", "H0", "H0")
    if list(study.all_gate_words(4)).index(word) != 73:
        raise study.StudyFailure("counterexample chronology drift")
    start = study.start_state_from_word(word)
    current = start
    operations = study.operation_map()
    for symbol in ("pivot_boundary_simp", "copy_simp", "to_gh"):
        successor = study.apply_operation(current, operations[symbol])
        if successor is None:
            raise study.StudyFailure(f"prefix guard rejected: {symbol}")
        if not study.matrices_equal(study.dense_matrix(current), study.dense_matrix(successor)):
            raise study.StudyFailure(f"prefix changed semantics: {symbol}")
        current = successor

    if current != BEFORE_PATH.read_text(encoding="utf-8"):
        raise study.StudyFailure("predecessor graph bytes drift")
    if study.sha256_text(current) != committed["counterexample"]["before"]["sha256"]:
        raise study.StudyFailure("predecessor graph digest drift")

    successor = study.apply_operation(current, operations["pivot_boundary_simp"])
    if successor is None:
        raise study.StudyFailure("adverse callable guard rejected")
    if successor != AFTER_PATH.read_text(encoding="utf-8"):
        raise study.StudyFailure("successor graph bytes drift")
    if study.sha256_text(successor) != committed["counterexample"]["after"]["sha256"]:
        raise study.StudyFailure("successor graph digest drift")

    before_matrix = study.dense_matrix(current)
    after_matrix = study.dense_matrix(successor)
    equal_exact = study.matrices_equal(before_matrix, after_matrix)
    equal_up_to_scalar = bool(
        study.pyzx.tensor.compare_tensors(before_matrix, after_matrix, preserve_scalar=False)
    )
    if equal_exact or equal_up_to_scalar:
        raise study.StudyFailure("adverse transition no longer changes semantics")
    residual = before_matrix - after_matrix
    max_residual = round(float(np.max(np.abs(residual))), 12)
    frobenius_residual = round(float(np.linalg.norm(residual)), 12)
    if max_residual != committed["counterexample"]["max_absolute_matrix_residual"]:
        raise study.StudyFailure("maximum residual drift")
    if frobenius_residual != committed["counterexample"]["frobenius_matrix_residual"]:
        raise study.StudyFailure("Frobenius residual drift")

    production = study.graph_from_state(start)
    study.pyzx.simplify.full_reduce(production)
    production_state = study.source_graph_state(production)
    production_semantics = study.matrices_equal(
        study.dense_matrix(start), study.dense_matrix(production_state)
    )
    if not production_semantics:
        raise study.StudyFailure("scheduled full_reduce changed witness semantics")

    return {
        "terminal": committed["terminal"],
        "source_binding": source_binding,
        "word": list(word),
        "predecessor_sha256": study.sha256_text(current),
        "successor_sha256": study.sha256_text(successor),
        "equal_including_scalar": equal_exact,
        "equal_up_to_nonzero_scalar": equal_up_to_scalar,
        "max_absolute_matrix_residual": max_residual,
        "frobenius_matrix_residual": frobenius_residual,
        "scheduled_full_reduce_semantics_preserved": production_semantics,
        "disputed_ast_or_omission_audit_used": False,
    }


def main() -> int:
    receipt = verify_adverse_core()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
