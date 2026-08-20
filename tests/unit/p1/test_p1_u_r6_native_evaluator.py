from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVAL_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r6" / "evaluate_native.py"


def load_eval():
    spec = importlib.util.spec_from_file_location("p1_u_r6_native_eval", EVAL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_r6_fixed_corpus_is_exact_r4_outcome_free_source_set():
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.validate_fixed_corpus(pairs, unresolved)
    assert result["complete"] is True
    assert len(pairs) == 22
    assert len(unresolved) == 4
    assert sum(result["class_counts"].values()) == 22
    assert all(value >= 3 for value in result["class_counts"].values())


def test_r6_fixed_corpus_fails_closed_on_source_or_class_mutation():
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    mutated = [dict(row) for row in pairs]
    mutated[0] = dict(mutated[0])
    mutated[0]["source_id"] = "doi:mutated-source"
    result = e.validate_fixed_corpus(mutated, unresolved)
    assert result["complete"] is False
    assert result["checks"]["exact_pair_sources"] is False

    pairs, unresolved = e.fixed_corpus()
    mutated = [dict(row) for row in pairs]
    mutated[0] = dict(mutated[0])
    mutated[0]["adverse_class"] = "PROBLEM_BOUNDARY"
    result = e.validate_fixed_corpus(mutated, unresolved)
    assert result["complete"] is False
    assert any("class mismatch" in error for error in result["errors"])


def test_candidate_visible_dossiers_have_no_literal_evaluator_metadata_leakage():
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    literal_classes = set(e.SUBSTANTIVE) | {e.CONTROL, e.UNRESOLVED}
    for pair in pairs:
        for member in ("adverse", "control"):
            dossier = str(pair[member]["dossier"])
            assert str(pair["query_id"]) not in dossier
            assert str(pair["source_id"]) not in dossier
            assert "pair_role" not in dossier.lower()
            assert not any(label in dossier for label in literal_classes)
    for ep in unresolved:
        dossier = str(ep["dossier"])
        assert str(ep["query_id"]) not in dossier
        assert str(ep["source_id"]) not in dossier
        assert not any(label in dossier for label in literal_classes)


def test_b3_comparator_is_budget_gated_and_cannot_enumerate_hidden_probes():
    e = load_eval()
    pairs, _ = e.fixed_corpus()
    result = e._b3(pairs[0]["adverse"])
    assert result["cost"] <= int(e.PROTOCOL["budget"])
    assert len(result["probe_accesses"]) == result["cost"]

    gate = e.B3ProbeGate(pairs[0]["adverse"]["probes"])
    with pytest.raises(RuntimeError, match="may not enumerate"):
        list(gate)


def test_native_lineage_verifier_rejects_tampering_and_accepts_real_runtime_result():
    e = load_eval()
    pairs, _ = e.fixed_corpus()
    ep = pairs[0]["adverse"]
    result = e.NATIVE.run_native_ard(ep, evidence_note="synthetic evaluator-lineage smoke")
    e._verify_native_lineage(result)

    bad = dict(result)
    bad["grants_merge_authority"] = True
    with pytest.raises(AssertionError, match="merge authority"):
        e._verify_native_lineage(bad)

    bad = dict(result)
    bad["root"] = dict(result["root"])
    bad["root"]["operator_ids"] = []
    with pytest.raises(AssertionError, match="root runtime lineage"):
        e._verify_native_lineage(bad)


def test_native_candidate_and_b3_share_same_two_probe_ceiling():
    e = load_eval()
    pairs, _ = e.fixed_corpus()
    ep = pairs[1]["adverse"]
    native = e.NATIVE.run_native_ard(ep, evidence_note="synthetic budget equality")
    b3 = e._b3(ep)
    assert len(native["probe_accesses"]) <= int(e.PROTOCOL["budget"])
    assert b3["cost"] <= int(e.PROTOCOL["budget"])
