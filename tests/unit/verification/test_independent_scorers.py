from __future__ import annotations

import json
from pathlib import Path

import pytest

from independent_scorers import (
    p3_flat_relation,
    p3_orion_relation,
    score_p1_h1,
    score_p2_aggregates,
    score_p3_mapping,
    score_p4_from_counts,
    score_p5_attribution,
)
from leakage import planted_label_leakage_hits

ROOT = Path(__file__).resolve().parents[3]


def test_p4_count_scorer_h1_h2():
    scored = score_p4_from_counts(
        orion_false_promotions=0,
        comparator_false_promotions=180,
        hostile_n=360,
        orion_clean=60,
        comparator_clean=60,
        clean_n=60,
    )
    assert scored["H1"]["status"] == "PASS"
    assert scored["H1"]["point"] == -0.5
    assert scored["H2"]["status"] == "PASS"
    assert scored["H2"]["point"] == 0.0


def test_p4_planted_denominator_mutation_fails_h1():
    mutated = score_p4_from_counts(
        orion_false_promotions=0,
        comparator_false_promotions=180,
        hostile_n=180,  # planted half-n
        orion_clean=60,
        comparator_clean=60,
        clean_n=60,
    )
    honest = score_p4_from_counts(
        orion_false_promotions=0,
        comparator_false_promotions=180,
        hostile_n=360,
        orion_clean=60,
        comparator_clean=60,
        clean_n=60,
    )
    assert mutated["orion_fp_rate"] == 0.0
    assert mutated["comparator_fp_rate"] == 1.0
    assert mutated["comparator_fp_rate"] != honest["comparator_fp_rate"]


def test_p3_independent_mapping_on_confirmatory_gold():
    gold = ROOT / (
        "papers/orion-13-global-knowledge-portrait/gold/adjudicated/"
        "public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl"
    )
    cases = [json.loads(line) for line in gold.read_text().splitlines() if line.strip()]
    report = score_p3_mapping(cases)
    assert report["n"] == 32
    assert report["systems"]["orion"]["false_merge_rate"] == 0.0
    assert report["systems"]["flat_predicate_canonicalization"]["false_merge_rate"] == 0.1875
    assert report["primary"]["confirmatory_primary_pass"] is True
    contra = next(case for case in cases if case["expected"]["meaning_relation"] == "CONTRADICTORY")
    assert p3_orion_relation(contra) == "CONTRADICTORY"
    assert p3_flat_relation(contra) == "COMPATIBLE"


def test_p5_independent_rescore_21_of_24():
    suite = json.loads(
        (ROOT / "papers/orion-15-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json").read_text()
    )
    rows = [
        json.loads(line)
        for line in (
            ROOT / "papers/orion-15-self-orion/evidence/glm-5.2-attribution/results.jsonl"
        ).read_text().splitlines()
        if line.strip()
    ]
    gold = {case["case_id"]: case["protected_root_cause"] for case in suite["cases"]}
    scored = score_p5_attribution(rows, gold)
    assert scored["correct"] == 21
    assert scored["n"] == 24
    assert scored["macro_f1"] == pytest.approx(0.8726190476190476)
    assert scored["macro_f1"] != pytest.approx(0.875)
    assert not planted_label_leakage_hits(
        [{"case_id": c["case_id"], "visible": c["visible_symptom"], "gold": c["protected_root_cause"]} for c in suite["cases"]]
    )


def test_p2_aggregate_arithmetic_and_record_count():
    summary = json.loads(
        (
            ROOT / "papers/orion-12-open-world-scientific-discovery/evidence/offline_results/RESULTS_SUMMARY_V1.json"
        ).read_text()
    )
    scored = score_p2_aggregates(summary)
    assert scored["n_tasks"] == 390
    assert scored["record_count_consistent"]
    assert scored["orion_recall"] == 0.979487
    assert scored["strongest_baseline_recall"] == 0.666667
    assert scored["primary_promoted"] is False


def test_p1_h1_remains_not_supported():
    path = ROOT / "papers/orion-11-recursive-epistemic-reconstruction/results/raw/test_scored.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    scored = score_p1_h1(rows)
    assert scored["orion_successes"] == 1
    assert scored["orion_n"] == 48
    assert scored["h1_status"] == "NOT_SUPPORTED"
    assert scored["n_records"] == 2880
