from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "orion01_r11_pyzx_round1.py"
SPEC = importlib.util.spec_from_file_location("orion01_r11_pyzx_round1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
SPEC.loader.exec_module(study)


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
