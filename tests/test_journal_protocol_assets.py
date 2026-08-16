from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ROOT = ROOT / "research" / "paper-programme-v1" / "protocols"
STATS_MODULE = PROTOCOL_ROOT / "publication_stats.py"
SVG_MODULE = PROTOCOL_ROOT / "publication_svg.py"
PAPER_PROTOCOLS = {
    "P1": ROOT / "papers" / "paper-01-recursive-epistemic-reconstruction" / "protocol" / "PROTOCOL_V1.json",
    "P2": ROOT / "papers" / "paper-02-open-world-scientific-discovery" / "protocol" / "PROTOCOL_V1.json",
    "P3": ROOT / "papers" / "paper-03-global-knowledge-portrait" / "protocol" / "PROTOCOL_V1.json",
    "P4": ROOT / "papers" / "paper-04-verified-scientific-discovery" / "protocol" / "PROTOCOL_V1.json",
    "P5": ROOT / "papers" / "paper-05-self-orion" / "protocol" / "PROTOCOL_V1.json",
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_common_protocol_schemas_are_json():
    for name in ("PUBLICATION_PROTOCOL_SCHEMA_V1.json", "RESULT_RECORD_SCHEMA_V1.json"):
        payload = json.loads((PROTOCOL_ROOT / name).read_text(encoding="utf-8"))
        assert payload["type"] == "object"
        assert payload["$schema"].endswith("2020-12/schema")


def test_all_five_protocols_are_outcome_blind_design_freezes():
    seen = set()
    for paper_id, path in PAPER_PROTOCOLS.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "orion.publication-protocol.v1"
        assert payload["paper_id"] == paper_id
        assert payload["protocol_status"] == "DESIGN_FROZEN"
        assert payload["outcome_accessed"] is False
        assert payload["primary_hypothesis"]["id"].startswith(f"{paper_id}.")
        assert payload["task_families"]
        assert payload["baselines"]
        assert payload["ablations"]
        assert payload["plots"]
        assert payload["tables"]
        assert payload["execution_bindings"]["subject_revision"] == "UNBOUND"
        seen.add(payload["protocol_id"])
    assert len(seen) == 5


def test_p3_annotation_and_p4_p5_protected_schemas_parse():
    paths = [
        ROOT / "papers" / "paper-03-global-knowledge-portrait" / "protocol" / "ANNOTATION_SCHEMA_V1.json",
        ROOT / "papers" / "paper-04-verified-scientific-discovery" / "protocol" / "ATTACK_CASE_SCHEMA_V1.json",
        ROOT / "papers" / "paper-05-self-orion" / "protocol" / "HIDDEN_CAUSE_CASE_SCHEMA_V1.json",
    ]
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["type"] == "object"
        assert payload["required"]


def test_publication_stats_wilson_and_precision():
    module = _load_module("publication_stats", STATS_MODULE)
    lo, hi = module.wilson_interval(50, 100)
    assert lo < 0.5 < hi
    assert module.required_n_for_proportion_half_width(0.05, 0.5) >= 384


def test_publication_stats_paired_bootstrap_is_deterministic():
    module = _load_module("publication_stats", STATS_MODULE)
    candidate = [1, 1, 0, 1, 1, 0]
    baseline = [0, 1, 0, 0, 1, 0]
    first = module.paired_bootstrap_difference_ci(candidate, baseline, resamples=1000, seed=7)
    second = module.paired_bootstrap_difference_ci(candidate, baseline, resamples=1000, seed=7)
    assert first == second
    assert first[0] > 0


def test_dependency_free_svg_builders_emit_real_svg():
    module = _load_module("publication_svg", SVG_MODULE)
    bars = module.bar_chart(
        [{"system": "baseline", "value": 0.4}, {"system": "orion", "value": 0.6}],
        label_key="system",
        value_key="value",
        title="Smoke",
        y_label="score",
    )
    assert bars.startswith("<svg")
    assert "baseline" in bars and "orion" in bars
    heatmap = module.heatmap(
        [
            {"truth": "A", "pred": "A", "value": 3},
            {"truth": "A", "pred": "B", "value": 1},
            {"truth": "B", "pred": "A", "value": 0},
            {"truth": "B", "pred": "B", "value": 4},
        ],
        row_key="truth",
        col_key="pred",
        value_key="value",
        title="Matrix",
    )
    assert heatmap.startswith("<svg")
    assert "Matrix" in heatmap
