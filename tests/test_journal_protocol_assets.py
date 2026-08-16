from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ROOT = ROOT / "research" / "paper-programme-v1" / "protocols"
STATS_MODULE = PROTOCOL_ROOT / "publication_stats.py"


def _load_stats():
    spec = importlib.util.spec_from_file_location("publication_stats", STATS_MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_common_protocol_schemas_are_json():
    for name in ("PUBLICATION_PROTOCOL_SCHEMA_V1.json", "RESULT_RECORD_SCHEMA_V1.json"):
        payload = json.loads((PROTOCOL_ROOT / name).read_text(encoding="utf-8"))
        assert payload["type"] == "object"
        assert payload["$schema"].endswith("2020-12/schema")


def test_publication_stats_wilson_and_precision():
    module = _load_stats()
    lo, hi = module.wilson_interval(50, 100)
    assert lo < 0.5 < hi
    assert module.required_n_for_proportion_half_width(0.05, 0.5) >= 384


def test_publication_stats_paired_bootstrap_is_deterministic():
    module = _load_stats()
    candidate = [1, 1, 0, 1, 1, 0]
    baseline = [0, 1, 0, 0, 1, 0]
    first = module.paired_bootstrap_difference_ci(candidate, baseline, resamples=1000, seed=7)
    second = module.paired_bootstrap_difference_ci(candidate, baseline, resamples=1000, seed=7)
    assert first == second
    assert first[0] > 0
