from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research/extensions/p6-higher-order-epistemic-mechanics"
RUNNER = RESEARCH / "run_t2_t3_countermodels_v1.py"
PANEL = RESEARCH / "T2_T3_COUNTERMODELS_V1.json"
SUMMARY = RESEARCH / "T2_T3_COUNTERMODEL_SUMMARY_V1.json"


def _load_runner():
    spec = spec_from_file_location("p6_t2_t3_countermodels", RUNNER)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_t2_t3_countermodels_rederive_frozen_summary_exactly() -> None:
    runner = _load_runner()
    panel = json.loads(PANEL.read_text())
    expected = json.loads(SUMMARY.read_text())

    actual = runner.run(panel)

    assert actual == expected
    assert actual["n_cases"] == 9
    assert actual["n_pass"] == 9
    assert actual["accuracy"] == 1.0
    assert actual["terminal"] == "T2_T3_FORMAL_COUNTERMODELS_GREEN"
    assert actual["grants_scientific_authority"] is False
    assert actual["grants_self_orion_adoption"] is False
