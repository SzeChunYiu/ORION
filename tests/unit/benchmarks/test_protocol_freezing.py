"""Tests for P4 protocol freezing — metrics, statistics, and freeze manifest."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

PAPER_ROOT = ROOT / "papers" / "orion-14-verified-scientific-discovery"
PROTOCOL_DIR = PAPER_ROOT / "protocol"
MANUSCRIPT_DIR = PAPER_ROOT / "manuscript"
PROTOCOLS_DIR = ROOT / "research" / "paper-programme-v1" / "protocols"
STATS_MODULE = PROTOCOLS_DIR / "publication_stats.py"


def _load_module(name: str, path: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_statistical_analysis_plan_exists():
    path = PROTOCOL_DIR / "STATISTICAL_ANALYSIS_PLAN_V1.md"
    assert path.exists(), "STATISTICAL_ANALYSIS_PLAN_V1.md must exist"
    text = path.read_text(encoding="utf-8")
    assert "H1" in text and "H2" in text and "H3" in text
    assert "bootstrap" in text
    assert "wilson" in text.lower()
    assert "practical" in text and "margin" in text
    assert "seed" in text and "20260816" in text


def test_metrics_registry_exists_and_valid():
    path = PROTOCOL_DIR / "METRICS_REGISTRY_V1.json"
    assert path.exists(), "METRICS_REGISTRY_V1.json must exist"
    registry = json.loads(path.read_text(encoding="utf-8"))
    assert registry["schema_version"] == "orion.publication-metrics-registry.v1"
    assert registry["paper_id"] == "P4"
    assert registry["protocol_id"] == "P4.protected-authority.v1"
    assert len(registry["primary_metrics"]) == 2
    assert len(registry["secondary_metrics"]) >= 14
    primary_ids = {m["id"] for m in registry["primary_metrics"]}
    assert "false_authority_promotion_rate" in primary_ids
    assert "clean_authority_coverage" in primary_ids


def test_freeze_manifest_exists():
    path = PROTOCOL_DIR / "FREEZE_MANIFEST_V1.md"
    assert path.exists(), "FREEZE_MANIFEST_V1.md must exist"
    text = path.read_text(encoding="utf-8")
    assert "DESIGN_FROZEN" in text
    assert "UNBOUND" in text
    assert "EXECUTION_FROZEN" in text
    assert "promotion" in text.lower()


def test_plot_spec_exists():
    path = PROTOCOL_DIR / "PLOT_SPEC_V1.md"
    assert path.exists(), "PLOT_SPEC_V1.md must exist"
    text = path.read_text(encoding="utf-8")
    for fig in ("ORION-14-1", "ORION-14-2", "ORION-14-3", "ORION-14-4", "ORION-14-5", "ORION-14-6"):
        assert fig in text, f"Figure {fig} must be specified in PLOT_SPEC_V1.md"
    for tbl in ("Table ORION-14-1", "Table ORION-14-2", "Table ORION-14-3"):
        assert tbl in text, f"Table {tbl} must be specified in PLOT_SPEC_V1.md"


def test_plot_spec_uses_publication_svg_builder():
    text = PROTOCOL_DIR.joinpath("PLOT_SPEC_V1.md").read_text(encoding="utf-8")
    assert "bar_chart" in text or "heatmap" in text
    assert "publication_svg" in text


def test_protocol_execution_bindings_are_fully_bound_when_execution_frozen():
    protocol = json.loads(
        (PROTOCOL_DIR / "PROTOCOL_V1.json").read_text(encoding="utf-8")
    )
    assert protocol["protocol_status"] == "EXECUTION_FROZEN"
    assert protocol["outcome_accessed"] is False
    bindings = protocol["execution_bindings"]
    assert bindings["subject_revision"] == "46977ea104162c4cf64da8138a4c4759065fe6d4"
    assert (
        bindings["dataset_revisions"]["protected_attack_set"]
        == "23c7732118bf750b4f5b927aab271cf1e7ee1068d8dc1838ca5119d7e436b102"
    )
    assert (
        bindings["baseline_config_hashes"]
        == "efa50d3f4e1d76589f80a813e52805b01940409cf353c4826713935a87d8ca84"
    )
    assert (
        bindings["evaluator_hash"]
        == "14a4c01442bd5f1d17eb4c7c443d94cbcf198e4e910a62d4126e6f35f27ad0c7"
    )
    assert (
        bindings["split_hashes"]
        == "747213c60d7a6087a6f6fda5e25546acae5ee70ec1b5b9b7db3868f208213959"
    )
    assert bindings["evaluation_epoch"] == "2026-08-16T19:22:06Z"

    def assert_bound(value: object, path: str = "execution_bindings") -> None:
        if isinstance(value, dict):
            assert value, f"{path} must not be empty"
            for key, item in value.items():
                assert_bound(item, f"{path}.{key}")
            return
        assert value != "UNBOUND", f"{path} must be bound"
        assert value not in (None, "", [], {}), f"{path} must be concrete"

    assert_bound(bindings)


def test_publication_stats_wilson_interval():
    module = _load_module("publication_stats", STATS_MODULE)
    lo, hi = module.wilson_interval(50, 100)
    assert lo < 0.5 < hi
    assert 0.40 <= lo <= 0.50
    assert 0.50 <= hi <= 0.60

    lo0, hi0 = module.wilson_interval(0, 100)
    assert lo0 < 1e-10, f"lower bound for 0/100 should be near 0, got {lo0}"
    assert hi0 > 0.0

    lo1, hi1 = module.wilson_interval(100, 100)
    assert hi1 == 1.0
    assert lo1 < 1.0


def test_publication_stats_required_n():
    module = _load_module("publication_stats", STATS_MODULE)
    n = module.required_n_for_proportion_half_width(0.05, 0.5)
    assert n >= 384, f"required n for half-width 0.05 should be >= 384, got {n}"

    n2 = module.required_n_for_proportion_half_width(0.01, 0.5)
    assert n2 > n, "tighter margin should require more samples"


def test_publication_stats_bootstrap_deterministic():
    module = _load_module("publication_stats", STATS_MODULE)
    a = [0.1, 0.2, 0.3, 0.4, 0.5]
    b = [0.15, 0.25, 0.1, 0.35, 0.45]
    first = module.paired_bootstrap_difference_ci(a, b, resamples=1000, seed=42)
    second = module.paired_bootstrap_difference_ci(a, b, resamples=1000, seed=42)
    assert first == second


def test_stats_uses_fixed_seed_20260816():
    module = _load_module("publication_stats", STATS_MODULE)
    a = [0.1, 0.2, 0.3, 0.4, 0.5]
    b = [0.15, 0.25, 0.1, 0.35, 0.45]
    result = module.paired_bootstrap_difference_ci(a, b, resamples=10000, seed=20260816)
    mean, lo, hi = result
    assert lo <= mean <= hi
    assert mean > -0.1


def test_publication_stats_summarize_jsonl():
    """Test that summarize_result_jsonl can parse a minimal JSONL file."""
    import tempfile
    module = _load_module("publication_stats", STATS_MODULE)
    lines = [
        json.dumps({"system_id": "orion", "metrics": {"false_authority_promotion_rate": 0.05}}),
        json.dumps({"system_id": "orion", "metrics": {"false_authority_promotion_rate": 0.03}}),
        json.dumps({"system_id": "baseline", "metrics": {"false_authority_promotion_rate": 0.15}}),
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(lines))
        tmp = f.name
    try:
        result = module.summarize_result_jsonl(Path(tmp), "false_authority_promotion_rate")
        assert "orion" in result
        assert "baseline" in result
        assert result["orion"]["n"] == 2
        assert result["orion"]["mean"] < result["baseline"]["mean"]
    finally:
        Path(tmp).unlink()


def test_hypotheses_mapped_in_metrics_registry():
    registry = json.loads(
        (PROTOCOL_DIR / "METRICS_REGISTRY_V1.json").read_text(encoding="utf-8")
    )
    primary_hypotheses = {m["hypothesis"] for m in registry["primary_metrics"]}
    assert "P4.H1" in primary_hypotheses
    assert "P4.H2" in primary_hypotheses

    secondary_hypotheses = {m["hypothesis"] for m in registry["secondary_metrics"]}
    assert "P4.H3" in secondary_hypotheses


def test_statistical_plan_matches_protocol():
    protocol = json.loads(
        (PROTOCOL_DIR / "PROTOCOL_V1.json").read_text(encoding="utf-8")
    )
    stats_text = (PROTOCOL_DIR / "STATISTICAL_ANALYSIS_PLAN_V1.md").read_text(encoding="utf-8")

    # Check that the plan matches each protocol statistics field
    protocol_stats = protocol["statistics"]
    assert "Wilson" in stats_text
    assert "bootstrap" in stats_text
    assert int(protocol_stats.get("stochastic_repeats", 0)) == 5
    assert "Holm" in stats_text


def test_protocol_matches_metrics_registry():
    protocol = json.loads(
        (PROTOCOL_DIR / "PROTOCOL_V1.json").read_text(encoding="utf-8")
    )
    registry = json.loads(
        (PROTOCOL_DIR / "METRICS_REGISTRY_V1.json").read_text(encoding="utf-8")
    )
    protocol_primary = set(protocol["metrics"]["primary"])
    registry_primary = {m["id"] for m in registry["primary_metrics"]}
    assert protocol_primary == registry_primary, (
        f"Protocol primary metrics {protocol_primary} != registry {registry_primary}"
    )
