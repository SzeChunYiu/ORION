"""Non-outcome unit controls for the ORION-01 Round-2 atomic checker registry.

These tests run in CI against the pinned production system; they check the
frozen inputs, the registry/runner agreement, the audit layer, and two
bounded words end-to-end (including determinism).  They never assert any
protected scientific outcome of the study.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import pytest

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "orion01_round2_atomic_registry.py"
SPEC = importlib.util.spec_from_file_location("orion01_round2_atomic_registry", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
try:
    SPEC.loader.exec_module(study)
except ImportError as exc:  # pinned production system absent on this machine
    pytest.skip(f"pinned PyZX not installed: {exc}", allow_module_level=True)


def _no_floats(node: Any) -> bool:
    if isinstance(node, bool) or node is None or isinstance(node, (str, int)):
        return True
    if isinstance(node, float):
        return False
    if isinstance(node, dict):
        return all(_no_floats(key) and _no_floats(value) for key, value in node.items())
    if isinstance(node, (list, tuple)):
        return all(_no_floats(item) for item in node)
    raise AssertionError(f"unexpected receipt value type: {type(node)}")


def test_frozen_registry_shape_and_authority_boundary() -> None:
    registry = study.load_registry()
    assert registry["schema"] == "ORION.ORION01.Round2.PyZXAtomicCheckerSourceRegistry.v1"
    assert registry["paper_id"] == "ORION-01"
    assert registry["round"] == 2
    assert registry["frozen_before_scientific_outcome_access"] is True
    assert registry["source"]["commit"] == study.EXPECTED_COMMIT
    assert registry["source"]["version"] == "0.10.5"
    assert len(registry["source"]["source_files"]) == 16
    assert len(registry["registered_schemas"]) == 12
    assert [row["id"] for row in registry["registered_schemas"]] == registry["registered_symbol_order"]
    assert registry["input_domain"]["primary_word_count"] == 585
    assert registry["input_domain"]["max_primary_word_length"] == 3
    assert registry["input_domain"]["boundary_probe_length6_word_count"] == 16
    assert registry["max_states_per_input_fail_closed"] == 20000
    assert registry["generic_search_baseline"]["restarts"] == study.GENERIC_RESTARTS
    boundaries = registry["authority_boundaries"]
    for key in (
        "all_pyzx_completeness",
        "all_zx_completeness",
        "generic_compiler_optimality",
        "physical_or_hardware_advantage",
        "external_novelty",
        "journal_authority",
        "submission_authorized",
        "round1_macro_language_relabeling",
    ):
        assert boundaries[key] is False, key


def test_protocol_freeze_and_terminals_declared() -> None:
    text = study.PROTOCOL_PATH.read_text(encoding="utf-8")
    assert "frozen before scientific outcome access" in text.lower()
    assert "Round 2 of at most 3" in text
    registry = study.load_registry()
    for terminal in registry["allowed_terminals"]:
        assert terminal in study.PROTOCOL_PATH.read_text(encoding="utf-8"), terminal
    assert study.POSITIVE_TERMINAL in registry["allowed_terminals"]
    assert study.NULL_TERMINAL in registry["allowed_terminals"]
    assert study.GENERIC_TERMINAL in registry["allowed_terminals"]
    assert study.CROSS_TERMINAL in registry["allowed_terminals"]
    assert study.FAIL_TERMINAL in registry["allowed_terminals"]
    assert "AB_R2_ATOMIC_GUARD_UNSOUND" in registry["allowed_terminals"]
    # Round-1 preservation is declared, not relabeled.
    assert registry["round1_preservation"]["macro_language_terminal"] == study.FAIL_TERMINAL


def test_frozen_domain_enumeration() -> None:
    words = study.primary_words()
    assert len(words) == 585
    assert words[0] == ()
    assert words[1] == ("H0",)
    assert words[72] == ("CX10", "CX10")
    assert words[73] == ("H0", "H0", "H0")
    assert words[-1] == ("CX10", "CX10", "CX10")
    probes = study.probe_words()
    assert len(probes) == 16
    # itertools.product follows the frozen GATE_ALPHABET order, whose
    # first two tokens are H0 and H1.  These assertions bind the actual
    # pre-outcome enumeration used by the committed receipt.
    assert probes[0] == ("H0",) * 6
    assert probes[1] == ("H0",) * 5 + ("H1",)
    registry = study.load_registry()
    payloads = study.word_payloads("pilot", registry)
    assert len(payloads) == 73
    assert [payload[2] for payload in payloads] == list(range(73))
    execute = study.word_payloads("execute", registry)
    assert len(execute) == 585 + 16
    assert execute[585][3] == "probe"
    assert execute[585][2] == 585
    assert execute[-1][2] == 600


def test_move_table_matches_registry_order() -> None:
    registry = study.load_registry()
    table = study.atomic_move_table()
    assert sorted(table) == registry["registered_symbol_order"]
    hostile = study.hostile_extension_map()
    assert sorted(hostile) == sorted(registry["hostile_extension_symbols"])
    for symbol in hostile.values():
        assert callable(symbol)


def test_installed_source_binding() -> None:
    registry = study.load_registry()
    verification = study.verify_installed_source(registry)
    assert verification["commit"] == study.EXPECTED_COMMIT
    assert verification["source_files_checked"] == 16


def test_static_ast_audits_pass() -> None:
    registry = study.load_registry()
    audits = study.derive_source_audits(registry)
    assert audits["primitive_closure_exact"] is True
    assert len(audits["derived_official_primitives"]) == 12
    assert audits["hostile_omissions_rejected"] == 12
    assert audits["mutator_method_surface_covered"] is True
    assert audits["mutator_method_surface_uncovered"] == []
    assert audits["guard_purity_all_pure"] is True
    assert len(audits["runtime_binding"]) >= 1
    matchers = audits["runtime_binding"]["mutating_batch_matchers_reachable_from_full_reduce"]
    assert "match_pivot_boundary" in matchers
    assert "match_pivot_gadget" in matchers
    assert "match_phase_gadgets" in matchers


def test_bounded_words_execute_deterministically() -> None:
    registry = study.load_registry()
    cap = int(registry["max_states_per_input_fail_closed"])
    for word in (("H0",), ("T0", "T1")):
        task = study.WordTask(word=word, word_index=study.primary_words().index(word), mode="execute", domain="primary", cap=cap)
        first = study.analyze_word(task)
        second = study.analyze_word(task)
        assert study.canonical_json(first) == study.canonical_json(second)
        assert first["cap_hit"] is False
        assert first["witness_replay_ok"] is True
        assert first["native_state_represented"] is True
        assert first["reachable_states"] >= 1
        assert first["witness_length"] >= 0
        assert first["optimum_resource"] <= first["native_resource"]
        assert first["generic_resource"] >= first["optimum_resource"]
        assert first["interaction_census"]["pair_count"] == 144
        assert len(first["witness"]) == first["witness_length"]
        assert _no_floats({key: value for key, value in first.items() if key != "interaction_census"})


def test_generic_seed_rule_frozen() -> None:
    registry = study.load_registry()
    assert study.GENERIC_SEED_MULTIPLIER == 1000003
    assert study.GENERIC_SEED_OFFSET == 7
    assert registry["generic_search_baseline"]["rng"] == (
        "NUMPY_PCG64_SEED_1000003_TIMES_WORD_INDEX_PLUS_7"
    )
    assert registry["generic_search_baseline"]["epsilon_random_move_probability"] == 0.25


def test_committed_receipts_if_present() -> None:
    results = study.RESULTS_PATH
    subset = study.SUBSET_RESULTS_PATH
    if not results.is_file() and not subset.is_file():
        pytest.skip("outcome receipts not committed yet")
    for path in (results, subset):
        if not path.is_file():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert _no_floats(raw)
        assert raw["paper_id"] == "ORION-01"
        assert raw["round"] == 2
        assert raw["outcome"]["terminal"] in study.load_registry()["allowed_terminals"]
        indexes = [row["word_index"] for row in raw["rows"]]
        assert indexes == sorted(indexes)
