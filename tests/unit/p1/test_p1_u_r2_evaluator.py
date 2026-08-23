from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVAL_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r2" / "evaluate.py"
PROTOCOL = json.loads((EVAL_PATH.parent / "PROTOCOL_V1.json").read_text())


def load_eval():
    spec = importlib.util.spec_from_file_location("p1_u_r2_eval", EVAL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clear_case(case_id: str = "dev", query_id: str = "CBIO-1", source_id: str = "dev-source"):
    probes = {p: "REFUTE" for p in PROTOCOL["probes"]}
    probes["P_ENVIRONMENT_REPLAY"] = "SUPPORT"
    return {
        "id": case_id,
        "domain": "computational_biology",
        "query_id": query_id,
        "source_id": source_id,
        "source_url": "https://example.invalid/dev",
        "dossier": "A reproducible analysis pipeline changes after a software dependency and environment version update.",
        "probes": probes,
        "gold_class": "IMPLEMENTATION_OR_ENVIRONMENT",
    }


def test_probe_gate_does_not_allow_enumeration():
    e = load_eval()
    gate = e.ProbeGate({p: "REFUTE" for p in PROTOCOL["probes"]})
    with pytest.raises(RuntimeError):
        list(gate)


def test_primary_evaluator_runs_without_exposing_gold_to_policy():
    e = load_eval()
    c = clear_case()
    result = e.evaluate([c])
    assert result["terminal"] == "P1_R2_PRIMARY_CANNOT_CHECK_INCOMPLETE_CORPUS"
    row = result["rows"][0]
    assert row["gold_class"] == "IMPLEMENTATION_OR_ENVIRONMENT"
    assert row["outcomes"]["ORION_R2"]["choice"] in set(PROTOCOL["classes"]) | {"UNRESOLVED"}


def test_duplicate_source_identity_fails_closed():
    e = load_eval()
    with pytest.raises(ValueError, match="source identities"):
        e.evaluate([clear_case("a", "CBIO-1", "same"), clear_case("b", "CBIO-2", "same")])


def test_overlong_dossier_fails_closed():
    e = load_eval()
    c = clear_case()
    c["dossier"] = "word " * 91
    with pytest.raises(ValueError, match="90-word"):
        e.evaluate([c])
