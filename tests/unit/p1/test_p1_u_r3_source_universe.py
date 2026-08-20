from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVALUATOR_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r3" / "evaluate.py"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("p1_u_r3_evaluator", EVALUATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_case(e, query, i: int):
    gold = query["class"]
    probes = {p: "INCONCLUSIVE" for p in e.REQUIRED_PROBES}
    if gold in e.POLICY.PROBE_TO_CLASS.values():
        for p, cls in e.POLICY.PROBE_TO_CLASS.items():
            probes[p] = "SUPPORT" if cls == gold else "REFUTE"
    elif gold == "NO_HIGH_LEVEL_REFORMULATION":
        probes = {p: "REFUTE" for p in e.REQUIRED_PROBES}
    return {
        "id": f"case-{i}",
        "query_id": query["id"],
        "query_class": query["class"],
        "actual_domain": f"domain-{i % 5}",
        "source_id": f"source-{i}",
        "source_url": f"https://example.invalid/{i}",
        "source_year": 2022,
        "source_rank": 1,
        "dossier": "A source-grounded scientific episode with a visible pre-resolution tension.",
        "probes": probes,
        "gold_class": gold,
        "admission_evidence": {"note": "synthetic evaluator test only"},
    }


def make_complete(e):
    cases = [make_case(e, q, i) for i, q in enumerate(e.PLAN["queries"])]
    dispositions = [
        {
            "query_id": c["query_id"],
            "status": "ADMITTED",
            "results_returned": 10,
            "results_scanned": 1,
            "skipped": [],
            "selected_source_id": c["source_id"],
            "selected_rank": c["source_rank"],
        }
        for c in cases
    ]
    return cases, dispositions


def test_r3_acquisition_accepts_complete_universe_and_one_no_source_when_quotas_hold():
    e = load_evaluator()
    cases, dispositions = make_complete(e)
    result = e.validate_acquisition(cases, dispositions)
    assert result["complete"] is True
    assert result["n_cases"] == 40
    assert result["n_domains"] == 5
    assert all(v >= 5 for v in result["class_counts"].values())

    # A query may legitimately have no qualifying source if all frozen corpus quotas still hold.
    cases.pop()
    dispositions[-1] = {
        "query_id": dispositions[-1]["query_id"],
        "status": "NO_QUALIFYING_SOURCE",
        "results_returned": 8,
        "results_scanned": 8,
        "skipped": [{"rank": 1, "reason": "nonqualifying"}],
    }
    result = e.validate_acquisition(cases, dispositions)
    assert result["complete"] is True
    assert result["n_cases"] == 39


def test_r3_class_quota_failure_cannot_generate_policy_outcomes():
    e = load_evaluator()
    cases, dispositions = make_complete(e)

    # Remove two UNRESOLVED cases so that class falls from five to three, below the frozen minimum four.
    removed_qids = {e.PLAN["queries"][-1]["id"], e.PLAN["queries"][-2]["id"]}
    cases = [c for c in cases if c["query_id"] not in removed_qids]
    for i, row in enumerate(dispositions):
        if row["query_id"] in removed_qids:
            dispositions[i] = {
                "query_id": row["query_id"],
                "status": "NO_QUALIFYING_SOURCE",
                "results_returned": 8,
                "results_scanned": 8,
                "skipped": [{"rank": 1, "reason": "nonqualifying"}],
            }

    result = e.evaluate(cases, dispositions)
    assert result["terminal"] == "P1_R3_CANNOT_CHECK_SOURCE_UNIVERSE"
    assert result["policy_outcomes_generated"] is False
    assert result["acquisition"]["checks"]["minimum_per_gold_class"] is False


def test_r3_rejects_wrong_year_duplicate_sources_and_bad_linkage():
    e = load_evaluator()
    cases, dispositions = make_complete(e)
    cases[0]["source_year"] = 2023
    with pytest.raises(ValueError, match="source year"):
        e.validate_acquisition(cases, dispositions)

    cases, dispositions = make_complete(e)
    cases[1]["source_id"] = cases[0]["source_id"]
    with pytest.raises(ValueError, match="source identities"):
        e.validate_acquisition(cases, dispositions)

    cases, dispositions = make_complete(e)
    dispositions[0]["selected_source_id"] = "wrong-source"
    result = e.validate_acquisition(cases, dispositions)
    assert result["complete"] is False
    assert result["checks"]["disposition_case_linkage"] is False


def test_r3_policy_never_sees_source_or_gold_metadata():
    e = load_evaluator()
    query = e.PLAN["queries"][10]
    case = make_case(e, query, 10)
    visible, _ = e._visible_case(case)
    assert set(visible) == {"dossier", "probes"}
    assert "gold_class" not in visible
    assert "source_id" not in visible
    assert "query_id" not in visible
