from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVAL_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r5" / "evaluate.py"


def load_eval():
    spec = importlib.util.spec_from_file_location("p1_u_r5_eval", EVAL_PATH)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def probes_for(e, gold):
    if gold == e.UNRESOLVED: return {p:"INCONCLUSIVE" for p in e.PROBES}
    if gold == e.CONTROL: return {p:"REFUTE" for p in e.PROBES}
    return {p:("SUPPORT" if cls == gold else "REFUTE") for p,cls in e.POLICY.PROBE_TO_CLASS.items()}


def make_data(e):
    pairs=[]
    for i,s in enumerate(e.FIXED["pair_sources"]):
        c=s["class"]
        pairs.append({
            "pair_id":f"pair-{i}","query_id":s["query_id"],"adverse_class":c,"actual_domain":f"domain-{i%6}",
            "source_id":s["source_id"],"source_url":f"https://example.invalid/{i}","source_year":2020,
            "adverse":{"id":f"a-{i}","dossier":"A source-grounded adverse condition before correction.","probes":probes_for(e,c),"gold_class":c},
            "control":{"id":f"c-{i}","dossier":"A matched source condition where the current scientific objective remains adequate.","probes":probes_for(e,e.CONTROL),"gold_class":e.CONTROL},
            "pair_evidence":{"note":"synthetic validation only"}
        })
    unresolved=[]
    for i,s in enumerate(e.FIXED["unresolved_sources"]):
        unresolved.append({"id":f"u-{i}","query_id":s["query_id"],"actual_domain":f"u-domain-{i}","source_id":s["source_id"],"source_url":f"https://example.invalid/u/{i}","source_year":2020,"dossier":"Available evidence leaves multiple explanations indistinguishable.","probes":probes_for(e,e.UNRESOLVED),"gold_class":e.UNRESOLVED,"admission_evidence":{"note":"synthetic validation only"}})
    return pairs, unresolved


def test_r5_exact_fixed_source_set_passes_validation():
    e=load_eval(); pairs,unresolved=make_data(e); r=e.validate_fixed_data(pairs,unresolved)
    assert r["complete"] is True
    assert r["checks"]["exact_pair_source_set"] is True
    assert r["checks"]["exact_unresolved_source_set"] is True
    assert all(v >= 3 for v in r["class_counts"].values())


def test_r5_missing_or_extra_source_fails_before_policy_outcomes():
    e=load_eval(); pairs,unresolved=make_data(e); pairs.pop(); r=e.evaluate(pairs,unresolved)
    assert r["terminal"] == "P1_R5_CANNOT_CHECK_FIXED_DATA"
    assert r["policy_outcomes_generated"] is False

    pairs,unresolved=make_data(e); pairs[0]["source_id"]="doi:invented-extra"; r=e.evaluate(pairs,unresolved)
    assert r["terminal"] == "P1_R5_CANNOT_CHECK_FIXED_DATA"
    assert r["policy_outcomes_generated"] is False


def test_r5_rejects_fixed_class_wrong_year_duplicate_source_and_control_relabel():
    e=load_eval(); pairs,unresolved=make_data(e); pairs[0]["adverse_class"]="PROBLEM_BOUNDARY"; r=e.validate_fixed_data(pairs,unresolved)
    assert r["complete"] is False
    assert any("query/class mismatch" in x for x in r["errors"])

    pairs,unresolved=make_data(e); pairs[0]["source_year"]=2021; r=e.validate_fixed_data(pairs,unresolved)
    assert r["complete"] is False
    assert any("wrong source year" in x for x in r["errors"])

    pairs,unresolved=make_data(e); pairs[1]["source_id"]=pairs[0]["source_id"]; r=e.validate_fixed_data(pairs,unresolved)
    assert r["complete"] is False

    pairs,unresolved=make_data(e); pairs[0]["control"]["gold_class"]=pairs[0]["adverse_class"]; r=e.validate_fixed_data(pairs,unresolved)
    assert r["complete"] is False
    assert any("gold mismatch" in x for x in r["errors"])


def test_r5_policy_visible_episode_has_only_dossier_and_gate():
    e=load_eval(); pairs,_=make_data(e); ep=pairs[0]["adverse"]; gate=e.ProbeGate(ep["probes"]); visible={"dossier":ep["dossier"],"probes":gate}
    assert set(visible)=={"dossier","probes"}
    assert "source_id" not in visible and "gold_class" not in visible and "query_id" not in visible
