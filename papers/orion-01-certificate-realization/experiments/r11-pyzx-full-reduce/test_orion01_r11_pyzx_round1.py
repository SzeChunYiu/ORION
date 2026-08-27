from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "orion01_r11_pyzx_round1.py"
SPEC = importlib.util.spec_from_file_location("orion01_r11_pyzx_round1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
SPEC.loader.exec_module(study)

VERIFY_PATH = HERE / "verify_orion01_r11_pyzx_counterexample.py"
INTERPRETATION_PATH = HERE / "ORION01_R11_PYZX_ADVERSE_INTERPRETATION.md"
VERIFY_SPEC = importlib.util.spec_from_file_location(
    "verify_orion01_r11_pyzx_counterexample", VERIFY_PATH
)
assert VERIFY_SPEC is not None and VERIFY_SPEC.loader is not None
adverse = importlib.util.module_from_spec(VERIFY_SPEC)
sys.modules[VERIFY_SPEC.name] = adverse
VERIFY_SPEC.loader.exec_module(adverse)

POST_REVIEW_PATH = HERE / "verify_orion01_r11_post_review_registry.py"
POST_REVIEW_SPEC = importlib.util.spec_from_file_location(
    "verify_orion01_r11_post_review_registry", POST_REVIEW_PATH
)
assert POST_REVIEW_SPEC is not None and POST_REVIEW_SPEC.loader is not None
post_review = importlib.util.module_from_spec(POST_REVIEW_SPEC)
sys.modules[POST_REVIEW_SPEC.name] = post_review
POST_REVIEW_SPEC.loader.exec_module(post_review)

ADVERSE_CORE_PATH = HERE / "verify_orion01_r11_adverse_core.py"
ADVERSE_CORE_SPEC = importlib.util.spec_from_file_location(
    "verify_orion01_r11_adverse_core", ADVERSE_CORE_PATH
)
assert ADVERSE_CORE_SPEC is not None and ADVERSE_CORE_SPEC.loader is not None
adverse_core = importlib.util.module_from_spec(ADVERSE_CORE_SPEC)
sys.modules[ADVERSE_CORE_SPEC.name] = adverse_core
ADVERSE_CORE_SPEC.loader.exec_module(adverse_core)


def test_frozen_registry_shape_and_authority_boundary() -> None:
    row = study.load_registry()
    assert row["paper_id"] == "ORION-01"
    assert row["round"] == 1
    assert row["frozen_before_scientific_outcome_access"] is True
    assert row["source"]["commit"] == study.EXPECTED_COMMIT
    assert row["registered_symbol_order"] == list(study.operation_map())
    assert len(row["registered_schemas"]) == 12
    assert len(set(row["registered_symbol_order"])) == 12
    assert row["input_domain"]["complete_word_count"] == 4681
    assert row["authority_boundaries"]["all_pyzx_completeness"] is False
    assert row["authority_boundaries"]["all_zx_completeness"] is False
    assert row["authority_boundaries"]["protected_task3_or_p9"] is False


def test_installed_source_and_independent_ast_closure() -> None:
    row = study.load_registry()
    installed = study.verify_installed_source(row)
    audit = study.derive_source_registry(row)
    assert installed["commit"] == study.EXPECTED_COMMIT
    assert installed["source_files_checked"] == 16
    assert audit["manifest_exact"] is True
    assert audit["discovered_count"] == 12
    assert audit["hostile_omissions_rejected"] == 12
    assert all(item["rejected"] for item in audit["hostile_single_omissions"])


def test_post_review_registry_controls_are_genuine_and_additive() -> None:
    fresh = post_review.build_receipt()
    committed = json.loads(post_review.RECEIPT_PATH.read_text())
    assert post_review.render(fresh) == post_review.RECEIPT_PATH.read_text()
    assert fresh == committed
    assert committed["raw_science_terminal"] == study.FAIL_TERMINAL
    assert committed["mutated_registry_omissions_rejected"] == 12
    assert all(
        item["disposition"] == "REJECTED"
        for item in committed["mutated_registry_omissions"]
    )
    assert all(
        item["registry_surface_removed"] is True
        and item["rejection_kind"] == "UNREGISTERED_PINNED_SOURCE_CALL"
        for item in committed["mutated_registry_omissions"]
    )
    findings = committed["review_findings"]
    assert findings["original_inline_omission_loop"]["disposition"].startswith(
        "NON_IDENTIFYING_TAUTOLOGICAL_COMPARISON"
    )
    assert findings["original_whitelist_filtered_ast_comparison"]["disposition"] == (
        "INSUFFICIENT_ALONE_TO_EXCLUDE_UNKNOWN_CALLS"
    )
    assert committed["scientific_disposition"]["bounded_counterexample_unchanged"] is True
    assert committed["scientific_disposition"]["complete_contextual_registry_established"] is False


def test_adverse_core_replays_without_the_disputed_registry_audit() -> None:
    receipt = adverse_core.verify_adverse_core()
    assert receipt["terminal"] == study.FAIL_TERMINAL
    assert receipt["word"] == ["H0", "H0", "H0"]
    assert receipt["equal_including_scalar"] is False
    assert receipt["equal_up_to_nonzero_scalar"] is False
    assert receipt["scheduled_full_reduce_semantics_preserved"] is True
    assert receipt["disputed_ast_or_omission_audit_used"] is False


def test_complete_word_enumerator_without_outcome_access() -> None:
    words = list(study.all_gate_words(4))
    assert len(words) == 4681
    assert sum(len(study.GATE_ALPHABET) ** n for n in range(5)) == 4681
    assert words[0] == ()
    assert words[-1] == ("CX10", "CX10", "CX10", "CX10")


def test_lossless_state_and_scalar_semantics_helpers() -> None:
    circuit = study.Circuit(2)
    circuit.add_gate("HAD", 0)
    circuit.add_gate("T", 1)
    circuit.add_gate("CNOT", 0, 1)
    graph = circuit.to_graph()
    state = study.source_graph_state(graph)
    restored = study.graph_from_state(state)
    assert study.source_graph_state(restored) == state
    assert study.resource(graph) == study.resource(restored)
    assert study.structural_measure(graph) == study.structural_measure(restored)
    assert np.allclose(
        graph.to_matrix(preserve_scalar=True),
        restored.to_matrix(preserve_scalar=True),
        rtol=1e-9,
        atol=1e-9,
    )


def test_hostile_authority_controls_collapse_false_bounds() -> None:
    row = study.hostile_authority_controls()
    assert row["all_passed"] is True
    assert row["complete_registry_no_gap"]["minimum"] == 1
    assert row["trace_equivalent_omitted_global_move"]["gap_collapsed"] is True
    assert row["omitted_cross_component_merge"]["gap_collapsed"] is True


def test_protocol_and_registry_are_result_free_before_execution() -> None:
    registry = json.loads(study.REGISTRY_PATH.read_text())
    assert "terminal" not in registry
    assert registry["allowed_terminals"] == [
        "AB_R11_REALIZED_GAP_COMPLETE_REWRITE_REGISTRY",
        "AB_R11_COMPLETE_REGISTRY_NO_STRICT_GAP",
        "AB_R11_CROSS_MOVE_COLLAPSES_GAP",
        "AB_R11_DONOR_EQUIVALENT",
        "CANNOT_CHECK_MOVE_COMPLETENESS",
    ]


def test_adverse_counterexample_replays_byte_identically() -> None:
    fresh = adverse.verify_counterexample()
    committed = json.loads(adverse.RESULT_PATH.read_text())
    assert adverse.render(fresh) == adverse.RESULT_PATH.read_text()
    assert fresh == committed
    assert committed["terminal"] == study.FAIL_TERMINAL
    assert committed["input_domain"]["first_failing_word_zero_based_index"] == 73
    assert committed["input_domain"]["first_failing_word_one_based_ordinal"] == 74
    assert committed["input_domain"]["complete_domain_executed"] is False
    assert committed["counterexample"]["source_word"] == ["H0", "H0", "H0"]
    assert committed["counterexample"]["adverse_operation"] == "pivot_boundary_simp"
    assert committed["counterexample"]["dense_semantics_equal_including_scalar"] is False
    assert committed["counterexample"]["dense_semantics_equal_up_to_nonzero_scalar"] is False
    assert committed["counterexample"]["production_full_reduce_on_same_source_word"][
        "semantics_equal_including_scalar"
    ] is True


def test_adverse_interpretation_reports_exact_committed_residuals() -> None:
    result = json.loads(adverse.RESULT_PATH.read_text())
    interpretation = INTERPRETATION_PATH.read_text()
    counterexample = result["counterexample"]
    assert f"`{counterexample['max_absolute_matrix_residual']}`" in interpretation
    assert f"`{counterexample['frobenius_matrix_residual']}`" in interpretation


def test_round_consumption_and_authority_are_fail_closed() -> None:
    result = json.loads(adverse.RESULT_PATH.read_text())
    status = json.loads((HERE / "ORION01_R11_ROUND1_STATUS.json").read_text())
    failure_1 = json.loads((HERE / "ORION01_R11_EXECUTION_FAILURE_01.json").read_text())
    failure_2 = json.loads((HERE / "ORION01_R11_EXECUTION_FAILURE_02.json").read_text())

    assert status["terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"
    assert status["rounds"] == {
        "consumed": 1,
        "maximum": 3,
        "current": "ROUND_1_ADVERSE_CANNOT_CHECK_CONTEXTUAL_GUARD__ROUND_2_OPEN",
    }
    assert result["round_accounting"]["round_disposition"] == "ADVERSE_CANNOT_CHECK"
    assert result["round_accounting"]["same_incomplete_macro_language_may_not_be_relabeled_as_round_2"] is True
    assert failure_1["authority"]["science_result_established"] is False
    assert failure_2["authority"]["science_result_established"] is False
    assert failure_1["terminal"] == failure_2["terminal"] == result["terminal"]

    assert result["authority"]["bounded_counterexample_established"] is True
    assert result["authority"]["production_full_reduce_refuted"] is False
    assert result["authority"]["complete_contextual_registry_established"] is False
    assert result["authority"]["realized_certificate_gap_established"] is False
    assert result["authority"]["bounded_null_established"] is False
    assert result["authority"]["external_independence"] is False
    assert result["authority"]["novelty"] is False
    assert result["authority"]["journal_authority"] is False
    assert result["authority"]["submission_authorized"] is False
    assert result["authority"]["protected_task3_or_p9"] is False


def test_prospective_chronology_is_preserved_across_failure_receipts() -> None:
    result = json.loads(adverse.RESULT_PATH.read_text())
    freeze = result["protocol_freeze"]["freeze_commit"]
    failure_1_commit = subprocess.check_output(
        [
            "git",
            "-C",
            str(study.REPO_ROOT),
            "log",
            "--diff-filter=A",
            "--format=%H",
            "-1",
            "--",
            adverse.FAILURE_01.relative_to(study.REPO_ROOT).as_posix(),
        ],
        text=True,
    ).strip()
    failure_2_commit = subprocess.check_output(
        [
            "git",
            "-C",
            str(study.REPO_ROOT),
            "log",
            "--diff-filter=A",
            "--format=%H",
            "-1",
            "--",
            adverse.FAILURE_02.relative_to(study.REPO_ROOT).as_posix(),
        ],
        text=True,
    ).strip()
    assert freeze == "449b254a8b0265747e8dc70dd771d432dd296b83"
    assert failure_1_commit == "29bba3d89363d05ec98436d5f9a707aaa7368e41"
    assert failure_2_commit == result["protocol_freeze"]["runner_last_change_commit"]
    for earlier, later in ((freeze, failure_1_commit), (failure_1_commit, failure_2_commit)):
        subprocess.run(
            ["git", "-C", str(study.REPO_ROOT), "merge-base", "--is-ancestor", earlier, later],
            check=True,
        )
