from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXT = ROOT / "research" / "extensions" / "p6-higher-order-epistemic-mechanics"
RUNNER = EXT / "run_t7_epistemic_control_v1.py"
PROTOCOL = EXT / "T7_COUNTERMODELS_V1.json"
SUMMARY = EXT / "T7_COUNTERMODEL_SUMMARY_V1.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_t7_epistemic_control_v1", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_t7_countermodel_summary_rederives_exactly() -> None:
    runner = _load_runner()
    derived = runner.derive_summary(PROTOCOL)
    frozen = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert derived == frozen
    assert derived["terminal"] == "T7_CONTROL_COMPOSITION_GREEN"
    assert derived["passed"] == derived["n_cases"] == 10
    assert derived["failed"] == 0


def test_t7_countermodel_terminal_is_non_authorizing() -> None:
    frozen = json.loads(SUMMARY.read_text(encoding="utf-8"))
    for result in frozen["results"]:
        assert result["grants_scientific_authority"] is False
        assert result["grants_revision_authority"] is False
        assert result["grants_adoption_authority"] is False
        assert result["grants_promotion_authority"] is False
        assert result["grants_merge_authority"] is False
        assert result["grants_global_task_stop_authority"] is False
