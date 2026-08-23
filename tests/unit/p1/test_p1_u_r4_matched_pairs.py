from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVALUATOR_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r4" / "evaluate.py"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("p1_u_r4_evaluator", EVALUATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def probes_for(e, gold: str):
    if gold == "UNRESOLVED":
        return {p: "INCONCLUSIVE" for p in e.REQUIRED_PROBES}
    if gold == e.CONTROL:
        return {p: "REFUTE" for p in e.REQUIRED_PROBES}
    return {
        p: ("SUPPORT" if cls == gold else "REFUTE")
        for p, cls in e.POLICY.PROBE_TO_CLASS.items()
    }


def make_pair(e, q, i: int):
    cls = q["class"]
    return {
        "pair_id": f"pair-{i}",
        "query_id": q["id"],
        "adverse_class": cls,
        "actual_domain": f"domain-{i % 6}",
        "source_id": f"source-pair-{i}",
        "source_url": f"https://example.invalid/pair/{i}",
        "source_year": 2020,
        "source_rank": 1,
        "adverse": {
            "id": f"pair-{i}-adverse",
            "dossier": "Matched study condition with a source-grounded scientific failure before correction.",
            "probes": probes_for(e, cls),
            "gold_class": cls,
        },
        "control": {
            "id": f"pair-{i}-control",
            "dossier": "Matched study condition where the existing scientific objective and boundary remain adequate.",
            "probes": probes_for(e, e.CONTROL),
            "gold_class": e.CONTROL,
        },
        "pair_evidence": {"note": "synthetic evaluator test only"},
    }


def make_unresolved(e, q, i: int):
    return {
        "id": f"unresolved-{i}",
        "query_id": q["id"],
        "actual_domain": f"unresolved-domain-{i}",
        "source_id": f"source-unresolved-{i}",
        "source_url": f"https://example.invalid/unresolved/{i}",
        "source_year": 2020,
        "source_rank": 1,
        "dossier": "The available observations leave multiple mechanisms observationally indistinguishable.",
        "probes": probes_for(e, "UNRESOLVED"),
        "gold_class": "UNRESOLVED",
        "admission_evidence": {"note": "synthetic evaluator test only"},
    }


def make_complete(e):
    pairs = []
    unresolved = []
    for i, q in enumerate(e.PLAN["queries"]):
        if q["class"] == "UNRESOLVED":
            unresolved.append(make_unresolved(e, q, i))
        else:
            pairs.append(make_pair(e, q, i))
    source_by_qid = {r["query_id"]: r for r in pairs}
    source_by_qid.update({r["query_id"]: r for r in unresolved})
    dispositions = []
    for q in e.PLAN["queries"]:
        row = source_by_qid[q["id"]]
        dispositions.append({
            "query_id": q["id"],
            "status": "ADMITTED",
            "results_returned": 10,
            "results_scanned": 1,
            "skipped": [],
            "selected_source_id": row["source_id"],
            "selected_rank": row["source_rank"],
        })
    return pairs, unresolved, dispositions


def test_r4_complete_matched_universe_passes_acquisition_gate():
    e = load_evaluator()
    pairs, unresolved, dispositions = make_complete(e)
    result = e.validate_acquisition(pairs, unresolved, dispositions)
    assert result["complete"] is True
    assert result["n_pairs"] == 24
    assert result["n_unresolved"] == 4
    assert result["n_sources"] == 28
    assert result["n_episodes"] == 52
    assert all(v == 4 for v in result["pair_class_counts"].values())


def test_r4_any_missing_required_source_fails_before_policy_execution():
    e = load_evaluator()
    pairs, unresolved, dispositions = make_complete(e)
    removed = pairs.pop()
    for i, row in enumerate(dispositions):
        if row["query_id"] == removed["query_id"]:
            dispositions[i] = {
                "query_id": row["query_id"],
                "status": "NO_QUALIFYING_SOURCE",
                "results_returned": 50,
                "results_scanned": 50,
                "skipped": [{"rank": 1, "reason": "no matched adverse/control source"}],
            }
            break
    result = e.evaluate(pairs, unresolved, dispositions)
    assert result["terminal"] == "P1_R4_CANNOT_CHECK_MATCHED_SOURCE_UNIVERSE"
    assert result["policy_outcomes_generated"] is False
    assert result["acquisition"]["checks"]["all_queries_admitted"] is False


def test_r4_rejects_wrong_year_duplicate_source_and_control_relabeling():
    e = load_evaluator()
    pairs, unresolved, dispositions = make_complete(e)
    pairs[0]["source_year"] = 2021
    with pytest.raises(ValueError, match="wrong source year"):
        e.validate_acquisition(pairs, unresolved, dispositions)

    pairs, unresolved, dispositions = make_complete(e)
    pairs[1]["source_id"] = pairs[0]["source_id"]
    with pytest.raises(ValueError, match="source identities"):
        e.validate_acquisition(pairs, unresolved, dispositions)

    pairs, unresolved, dispositions = make_complete(e)
    pairs[0]["control"]["gold_class"] = pairs[0]["adverse_class"]
    with pytest.raises(ValueError, match="gold mismatch"):
        e.validate_acquisition(pairs, unresolved, dispositions)


def test_r4_rejects_pair_query_class_and_disposition_mismatch():
    e = load_evaluator()
    pairs, unresolved, dispositions = make_complete(e)
    pairs[0]["adverse_class"] = "PROBLEM_BOUNDARY"
    with pytest.raises(ValueError, match="adverse class/query mismatch"):
        e.validate_acquisition(pairs, unresolved, dispositions)

    pairs, unresolved, dispositions = make_complete(e)
    dispositions[0]["selected_source_id"] = "wrong-source"
    result = e.validate_acquisition(pairs, unresolved, dispositions)
    assert result["complete"] is False
    assert result["checks"]["disposition_source_linkage"] is False


def test_r4_policy_visibility_excludes_pair_source_and_gold_metadata():
    e = load_evaluator()
    pair = make_pair(e, next(iter(e.PAIR_QUERIES.values())), 0)
    visible, _ = e._visible_episode(pair["adverse"])
    assert set(visible) == {"dossier", "probes"}
    assert "gold_class" not in visible
    assert "source_id" not in visible
    assert "pair_id" not in visible
