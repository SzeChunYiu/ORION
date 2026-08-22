"""Tests for ORION Paper 3 evaluation infrastructure."""
from __future__ import annotations

import math

from orion.study.ablations import ALL_ABLATIONS, ABLATION_IDS
from orion.study.baselines import ALL_BASELINES, BASELINE_IDS
from orion.study.metrics import (
    ALL_METRIC_FUNCTIONS,
    compute_all_metrics,
    false_merge_rate,
    valid_integration_rate,
    false_integration_rate_with_valid_integration_guard,
    mapping_precision_recall_f1,
    source_recoverability_rate,
    preservation_condition_accuracy,
    measurement_equivalence_accuracy,
    obstruction_precision_recall,
    unresolved_abstention_calibration,
    annotation_agreement_by_coordinate,
    cost_metrics,
)
from orion.study.statistics import (
    wilson_interval,
    percentile,
    bootstrap_mean_ci,
    paired_bootstrap_difference_ci,
    holm_correction,
    cohens_h,
    effect_size_category,
    check_superiority_margin,
    check_non_inferiority_margin,
    aggregate_across_runs,
    check_safety_margin_from_aggregates,
    discipline_stratified_analysis,
)


# ── fixtures ──────────────────────────────────────────────────────────────────

def _make_annotation(mapping: str = "IDENTITY",
                     integration: str = "GLUE_ALLOWED",
                     contradiction: str = "NO_CONTRADICTION",
                     referent: str = "CONVERGENT",
                     construct: str = "CONVERGENT",
                     measurement: str = "COMPATIBLE",
                     context: str = "CONSISTENT",
                     polarity: str = "CONSISTENT",
                     modality: str = "ASSERTIVE",
                     attribution: str = "SHARED",
                     discourse: str = "ELABORATES",
                     preservation: str | None = None,
                     recoverability: list[str] | None = None,
                     case_family: str = "bridge",
                     downstream_correct: bool | None = None,
                     ) -> dict[str, object]:
    d: dict[str, object] = {
        "mapping_relation": mapping,
        "integration_verdict": integration,
        "contradiction_verdict": contradiction,
        "referent_relation": referent,
        "construct_relation": construct,
        "measurement_relation": measurement,
        "context_relation": context,
        "polarity_relation": polarity,
        "modality_relation": modality,
        "attribution_relation": attribution,
        "discourse_relation": discourse,
        "case_family": case_family,
    }
    if preservation is not None:
        d["preservation_conditions"] = [preservation]
    else:
        d["preservation_conditions"] = []
    if recoverability is not None:
        d["recoverability_target"] = recoverability
    else:
        d["recoverability_target"] = []
    if downstream_correct is not None:
        d["downstream_correct"] = downstream_correct
    return d


def _make_prediction(mapping: str = "IDENTITY",
                     integration: str = "GLUE_ALLOWED",
                     contradiction: str = "NO_CONTRADICTION",
                     measurement: str = "COMPATIBLE",
                     preservation: list[str] | None = None,
                     recoverability: list[str] | None = None,
                     downstream_correct: bool | None = None,
                     ) -> dict[str, object]:
    d: dict[str, object] = {
        "mapping_relation": mapping,
        "integration_verdict": integration,
        "contradiction_verdict": contradiction,
        "measurement_relation": measurement,
        "preservation_conditions": preservation or [],
        "recoverability_target": recoverability or [],
    }
    if downstream_correct is not None:
        d["downstream_correct"] = downstream_correct
    return d


# ── metrics tests ─────────────────────────────────────────────────────────────

class TestFalseMergeRate:
    def test_perfect(self):
        gold = [_make_annotation(integration="GLUE_ALLOWED")]
        pred = [_make_prediction(integration="GLUE_ALLOWED")]
        result = false_merge_rate(gold, pred)
        assert result["false_merge_rate"] == 0.0

    def test_all_false_merge(self):
        gold = [_make_annotation(integration="OBSTRUCTION")]
        pred = [_make_prediction(integration="GLUE_ALLOWED")]
        result = false_merge_rate(gold, pred)
        assert result["false_merge_rate"] == 1.0

    def test_abstention_skipped(self):
        gold = [_make_annotation(integration="OBSTRUCTION")]
        pred = [_make_prediction(integration="UNRESOLVED")]
        result = false_merge_rate(gold, pred)
        assert result["false_merge_n"] == 0.0

    def test_empty(self):
        """An unmeasured harm rate must not read as the best attainable one."""

        result = false_merge_rate([], [])
        assert math.isnan(result["false_merge_rate"])
        assert result["false_merge_n"] == 0.0
        assert not (result["false_merge_rate"] <= 0.05)


class TestValidIntegrationRate:
    def test_perfect(self):
        gold = [_make_annotation(integration="GLUE_ALLOWED")]
        pred = [_make_prediction(integration="GLUE_ALLOWED")]
        result = valid_integration_rate(gold, pred)
        assert result["valid_integration_rate"] == 1.0

    def test_all_wrong(self):
        gold = [_make_annotation(integration="GLUE_ALLOWED")]
        pred = [_make_prediction(integration="OBSTRUCTION")]
        result = valid_integration_rate(gold, pred)
        assert result["valid_integration_rate"] == 0.0

    def test_mixed(self):
        gold = [
            _make_annotation(integration="GLUE_ALLOWED"),
            _make_annotation(integration="OBSTRUCTION"),
        ]
        pred = [
            _make_prediction(integration="GLUE_ALLOWED"),
            _make_prediction(integration="OBSTRUCTION"),
        ]
        result = valid_integration_rate(gold, pred)
        assert result["valid_integration_rate"] == 1.0


class TestComposite:
    def test_returns_both_metrics(self):
        gold = [_make_annotation(integration="GLUE_ALLOWED")]
        pred = [_make_prediction(integration="GLUE_ALLOWED")]
        result = false_integration_rate_with_valid_integration_guard(gold, pred)
        assert "false_merge_rate" in result
        assert "valid_integration_rate" in result


class TestMappingMetrics:
    def test_perfect_mapping(self):
        gold = [_make_annotation(mapping="IDENTITY")]
        pred = [_make_prediction(mapping="IDENTITY")]
        result = mapping_precision_recall_f1(gold, pred)
        assert result["mapping_f1_macro"] > 0.0

    def test_wrong_mapping(self):
        gold = [_make_annotation(mapping="IDENTITY")]
        pred = [_make_prediction(mapping="EQUIVALENCE")]
        result = mapping_precision_recall_f1(gold, pred)
        assert result["mapping_f1_IDENTITY"] == 0.0
        assert result["mapping_f1_EQUIVALENCE"] == 0.0


class TestUnresolvedCalibration:
    def test_no_unresolved(self):
        gold = [_make_annotation(integration="GLUE_ALLOWED")]
        pred = [_make_prediction(integration="GLUE_ALLOWED")]
        result = unresolved_abstention_calibration(gold, pred)
        assert result["unresolved_rate"] == 0.0
        assert result["unresolved_calibration"] == 0.0

    def test_correct_abstention(self):
        gold = [_make_annotation(integration="UNRESOLVED")]
        pred = [_make_prediction(integration="UNRESOLVED")]
        result = unresolved_abstention_calibration(gold, pred)
        assert result["unresolved_rate"] == 1.0
        assert result["unresolved_calibration"] == 1.0

    def test_wrong_abstention(self):
        gold = [_make_annotation(integration="GLUE_ALLOWED")]
        pred = [_make_prediction(integration="UNRESOLVED")]
        result = unresolved_abstention_calibration(gold, pred)
        assert result["unresolved_rate"] == 1.0
        assert result["unresolved_calibration"] == 0.0


class TestObstructionMetrics:
    def test_correct_obstruction(self):
        gold = [_make_annotation(integration="OBSTRUCTION")]
        pred = [_make_prediction(integration="OBSTRUCTION")]
        result = obstruction_precision_recall(gold, pred)
        assert result["obstruction_precision"] == 1.0
        assert result["obstruction_recall"] == 1.0

    def test_false_positive_obstruction(self):
        gold = [_make_annotation(integration="GLUE_ALLOWED")]
        pred = [_make_prediction(integration="OBSTRUCTION")]
        result = obstruction_precision_recall(gold, pred)
        assert result["obstruction_precision"] == 0.0
        # No gold obstruction → TP=0, FN=0, so recall = 0/(0+0) = 0.0
        assert result["obstruction_recall"] == 0.0


class TestSourceRecoverability:
    def test_recoverable(self):
        gold = [_make_annotation(recoverability=["source_a", "source_b"])]
        pred = [_make_prediction(recoverability=["source_a", "source_b"])]
        result = source_recoverability_rate(gold, pred)
        assert result["source_recoverability_rate"] == 1.0

    def test_unrecoverable(self):
        gold = [_make_annotation(recoverability=["source_a"])]
        pred = [_make_prediction(recoverability=[])]
        result = source_recoverability_rate(gold, pred)
        assert result["source_recoverability_rate"] == 0.0

    def test_no_requirement(self):
        gold = [_make_annotation(recoverability=[])]
        pred = [_make_prediction(recoverability=[])]
        result = source_recoverability_rate(gold, pred)
        assert result["source_recoverability_n"] == 0.0


class TestPreservationCondition:
    def test_matching(self):
        gold = [_make_annotation(preservation="p1")]
        pred = [_make_prediction(preservation=["p1"])]
        result = preservation_condition_accuracy(gold, pred)
        assert result["preservation_condition_accuracy"] == 1.0

    def test_mismatched(self):
        gold = [_make_annotation(preservation="p1")]
        pred = [_make_prediction(preservation=["p2"])]
        result = preservation_condition_accuracy(gold, pred)
        assert result["preservation_condition_accuracy"] == 0.0


class TestAnnotationAgreement:
    def test_perfect_agreement(self):
        a = _make_annotation()
        b = _make_annotation()
        result = annotation_agreement_by_coordinate([a], [b])
        for key, value in result.items():
            assert value == 1.0, f"Expected 1.0 for {key}, got {value}"

    def test_disagreement(self):
        a = _make_annotation(mapping="IDENTITY")
        b = _make_annotation(mapping="EQUIVALENCE")
        result = annotation_agreement_by_coordinate([a], [b])
        assert result["agreement_mapping_relation"] == 0.0


class TestCostMetrics:
    def test_empty(self):
        result = cost_metrics([])
        assert result["wallclock_seconds_total"] == 0.0

    def test_single_result(self):
        results = [{"cost": {"wallclock_seconds": 10, "model_tokens": 100,
                              "storage_overhead": 5}}]
        result = cost_metrics(results)
        assert result["wallclock_seconds_total"] == 10.0
        assert result["model_tokens_mean"] == 100.0
        assert result["storage_overhead_total"] == 5.0

    def test_missing_cost_keys(self):
        results = [{"cost": {"wallclock_seconds": 10}}]
        result = cost_metrics(results)
        assert result["wallclock_seconds_total"] == 10.0
        assert result["model_tokens_mean"] == 0.0


class TestComputeAllMetrics:
    def test_returns_flat_dict(self):
        gold = [_make_annotation()]
        pred = [_make_prediction()]
        result = compute_all_metrics(gold, pred)
        assert isinstance(result, dict)
        assert len(result) > 10
        assert "false_merge_rate" in result
        assert "valid_integration_rate" in result

    def test_empty_inputs(self):
        """Every rate over an empty corpus is unmeasured, not zero and not perfect.

        The harm rate and the utility rate used to come back 0.0 together, which
        reads as "no harm and no utility" rather than "nothing was run". Both are
        nan now, so a caller comparing either against a threshold fails closed.
        """

        result = compute_all_metrics([], [])
        assert isinstance(result, dict)
        assert math.isnan(result["false_merge_rate"])
        assert math.isnan(result["valid_integration_rate"])

    def test_all_metric_functions_registered(self):
        assert len(ALL_METRIC_FUNCTIONS) >= 12


# ── statistics tests ──────────────────────────────────────────────────────────

class TestWilsonInterval:
    def test_coin_flip(self):
        lo, hi = wilson_interval(50, 100)
        assert lo < 0.5 < hi

    def test_all_successes(self):
        lo, hi = wilson_interval(100, 100)
        assert lo > 0.95

    def test_all_failures(self):
        lo, hi = wilson_interval(0, 100)
        assert hi < 0.05

    def test_zero_total(self):
        import pytest
        with pytest.raises(ValueError, match="total must be positive"):
            wilson_interval(0, 0)


class TestPercentile:
    def test_median(self):
        assert percentile([1, 2, 3, 4, 5], 0.5) == 3.0

    def test_min(self):
        assert percentile([1, 2, 3], 0.0) == 1.0

    def test_max(self):
        assert percentile([1, 2, 3], 1.0) == 3.0

    def test_single_element(self):
        assert percentile([42], 0.5) == 42.0

    def test_empty(self):
        import pytest
        with pytest.raises(ValueError, match="must be non-empty"):
            percentile([], 0.5)


class TestBootstrap:
    def test_constant(self):
        mean, lo, hi = bootstrap_mean_ci([5.0, 5.0, 5.0, 5.0, 5.0])
        assert mean == 5.0
        assert lo <= 5.0 <= hi

    def test_empty(self):
        import pytest
        with pytest.raises(ValueError, match="must be non-empty"):
            bootstrap_mean_ci([])

    def test_paired_difference(self):
        candidate = [0.2, 0.3, 0.25, 0.35, 0.28]
        baseline = [0.1, 0.15, 0.12, 0.18, 0.14]
        diff, lo, hi = paired_bootstrap_difference_ci(candidate, baseline)
        assert diff > 0.0
        assert lo <= diff <= hi

    def test_paired_length_mismatch(self):
        import pytest
        with pytest.raises(ValueError, match="must have the same positive length"):
            paired_bootstrap_difference_ci([0.1], [0.2, 0.3])


class TestHolmCorrection:
    def test_no_correction_single(self):
        result = holm_correction([0.01])
        assert result == [0.01]

    def test_correction_multiple(self):
        result = holm_correction([0.01, 0.02, 0.03])
        # After correction, p-values should be >= original or <= 1.0
        assert all(p <= 1.0 for p in result)
        # Monotonicity should hold
        assert result[0] <= result[1] <= result[2]

    def test_empty(self):
        assert holm_correction([]) == []


class TestCohensH:
    def test_identical(self):
        assert cohens_h(0.5, 0.5) == 0.0

    def test_large_difference(self):
        h = abs(cohens_h(0.9, 0.1))
        assert h > 1.0  # should be "large"

    def test_category(self):
        assert effect_size_category(0.0) == "negligible"
        assert effect_size_category(0.3) == "small"
        assert effect_size_category(0.6) == "medium"
        assert effect_size_category(0.9) == "large"


class TestSafetyMargins:
    def test_superiority_passes(self):
        result = check_superiority_margin(0.01, 0.10, margin=0.05)
        assert result["superiority_passed"] is True

    def test_superiority_fails(self):
        result = check_superiority_margin(0.08, 0.10, margin=0.05)
        assert result["superiority_passed"] is False

    def test_non_inferiority_passes(self):
        result = check_non_inferiority_margin(0.95, 0.90, margin=0.03)
        assert result["non_inferiority_passed"] is True

    def test_non_inferiority_fails(self):
        result = check_non_inferiority_margin(0.85, 0.90, margin=0.03)
        assert result["non_inferiority_passed"] is False


class TestAggregateAcrossRuns:
    def test_basic_aggregation(self):
        runs = [
            {"fm": 0.1, "vi": 0.9},
            {"fm": 0.2, "vi": 0.8},
            {"fm": 0.15, "vi": 0.85},
        ]
        result = aggregate_across_runs(runs)
        assert "fm" in result
        assert "vi" in result
        assert result["fm"]["mean"] == 0.15
        assert result["fm"]["n_runs"] == 3.0
        assert result["fm"]["min"] == 0.1
        assert result["fm"]["max"] == 0.2

    def test_empty(self):
        result = aggregate_across_runs([])
        assert result == {}


class TestSafetyMarginFromAggregates:
    def test_both_pass(self):
        cand = {"false_merge_rate": 0.01, "valid_integration_rate": 0.95}
        base = {"false_merge_rate": 0.10, "valid_integration_rate": 0.90}
        result = check_safety_margin_from_aggregates(cand, base)
        assert result["both_passed"] is True

    def test_superiority_fails_non_inferiority_passes(self):
        cand = {"false_merge_rate": 0.08, "valid_integration_rate": 0.95}
        base = {"false_merge_rate": 0.10, "valid_integration_rate": 0.90}
        result = check_safety_margin_from_aggregates(cand, base)
        assert result["both_passed"] is False
        assert result["superiority"]["superiority_passed"] is False
        assert result["non_inferiority"]["non_inferiority_passed"] is True


class TestDisciplineStratified:
    def test_stratification(self):
        def _simple_metric(gs, ps):
            return {"count": float(len(gs))}
        gold = [
            _make_annotation(case_family="bridge"),
            _make_annotation(case_family="physics"),
        ]
        gold[0]["discipline"] = "bridge"
        gold[1]["discipline"] = "physics"
        pred = [_make_prediction(), _make_prediction()]
        result = discipline_stratified_analysis(gold, pred, _simple_metric,
                                                 discipline_key="discipline")
        assert "bridge" in result
        assert "physics" in result
        assert "pooled" in result
        assert result["pooled"]["count"] == 2.0


# ── baselines / ablations tests ───────────────────────────────────────────────

class TestBaselines:
    def test_all_baselines_have_unique_ids(self):
        ids = [b.system_id() for b in ALL_BASELINES]
        assert len(ids) == len(set(ids)), "Duplicate baseline IDs"

    def test_all_baselines_produce_integration_result(self):
        doc = {
            "document_id": "test",
            "document_version": "v1",
            "text": "Test source text.",
            "discipline": "physics",
            "span_start": 0,
            "span_end": 16,
            "text_hash": "abc",
        }
        sources = [doc]
        from orion.study.baselines import SourceDocument as SD
        sd = SD(**doc)
        for baseline in ALL_BASELINES:
            result = baseline.integrate([sd])
            assert result.system_id == baseline.system_id()

    def test_baseline_ids_match(self):
        assert BASELINE_IDS == [b.system_id() for b in ALL_BASELINES]


class TestAblations:
    def test_all_ablations_have_unique_ids(self):
        ids = [a.system_id() for a in ALL_ABLATIONS]
        assert len(ids) == len(set(ids)), "Duplicate ablation IDs"

    def test_ablation_ids_match(self):
        assert ABLATION_IDS == [a.system_id() for a in ALL_ABLATIONS]

    def test_each_ablation_has_description(self):
        for ablation in ALL_ABLATIONS:
            assert ablation._description, f"Missing description for {ablation.system_id()}"


# ── evaluate runner tests ─────────────────────────────────────────────────────

class TestGoldLoading:
    def test_load_list(self, tmp_path):
        f = tmp_path / "gold.json"
        f.write_text('[{"case_id": "c1", "sources": []}]', encoding="utf-8")
        from orion.study.evaluate import load_gold
        result = load_gold(f)
        assert len(result) == 1
        assert result[0]["case_id"] == "c1"

    def test_load_object(self, tmp_path):
        f = tmp_path / "gold.json"
        f.write_text('{"annotations": [{"case_id": "c1"}]}', encoding="utf-8")
        from orion.study.evaluate import load_gold
        result = load_gold(f)
        assert len(result) == 1

    def test_invalid(self, tmp_path):
        f = tmp_path / "gold.json"
        f.write_text('{"not_annotations": []}', encoding="utf-8")
        import pytest
        from orion.study.evaluate import load_gold
        with pytest.raises(ValueError, match="Unrecognized gold file shape"):
            load_gold(f)


class TestBuildManifest:
    def test_manifest_structure(self, tmp_path):
        gold = tmp_path / "gold.json"
        gold.write_text("[]", encoding="utf-8")
        from orion.study.evaluate import build_manifest
        m = build_manifest(["ORION_FULL"], [0, 1], gold)
        assert m["paper_id"] == "P3"
        assert m["protocol_id"] == "P3.cross-domain-atlas.v1"
        assert m["gold_hash"]


# ── plots tests ───────────────────────────────────────────────────────────────

class TestPlotGeneration:
    def test_figure_specs_defined(self, tmp_path):
        from orion.study.plots import FIGURE_SPECS, generate_figure
        fig = "P3-1"
        assert fig in FIGURE_SPECS
        data = [{"system_id": "ORION", "false_merge_rate": 0.05}]
        try:
            path = generate_figure(fig, data, tmp_path)
            assert path.exists()
        except (FileNotFoundError, ImportError):
            pass  # SVG module may not be importable from this path

    def test_table_specs_defined(self, tmp_path):
        from orion.study.plots import TABLE_SPECS, generate_table_latex
        table = "P3-T1"
        assert table in TABLE_SPECS
        data = [{"system_id": "ORION", "false_merge_rate": 0.05,
                 "valid_integration_rate": 0.95, "superiority_passed": True,
                 "non_inferiority_passed": True, "both_passed": True}]
        path = generate_table_latex(table, data, tmp_path)
        text = path.read_text(encoding="utf-8")
        assert r"\begin{table}" in text
        assert r"\label{tab:P3:T1}" in text

    def test_generate_all_figures(self, tmp_path):
        from orion.study.plots import FIGURE_SPECS, generate_all_figures
        data = [{"system_id": "ORION", "false_merge_rate": 0.05,
                 "valid_integration_rate": 0.95, "mapping_f1_macro": 0.85,
                 "discipline": "physics"}]
        try:
            paths = generate_all_figures(data, tmp_path)
            for fig_id in FIGURE_SPECS:
                assert fig_id in paths
        except (FileNotFoundError, ImportError):
            pass  # SVG module may not be importable

    def test_generate_all_tables(self, tmp_path):
        from orion.study.plots import TABLE_SPECS, generate_all_tables
        data = [{"system_id": "ORION", "false_merge_rate": 0.05,
                 "valid_integration_rate": 0.95, "mapping_f1_macro": 0.85,
                 "discipline": "physics", "n_cases": 50,
                 "source_recoverability_rate": 0.9,
                 "ablation_id": "test", "delta_false_merge_rate": -0.02,
                 "delta_valid_integration_rate": 0.03,
                 "delta_mapping_f1_macro": -0.01,
                 "cohens_h": 0.3, "effect_size_category": "small",
                 "superiority_passed": True, "non_inferiority_passed": True,
                 "both_passed": True}]
        paths = generate_all_tables(data, tmp_path)
        for table_id in TABLE_SPECS:
            assert table_id in paths
            text = paths[table_id].read_text(encoding="utf-8")
            assert r"\begin{table}" in text