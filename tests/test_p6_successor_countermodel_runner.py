import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "research" / "extensions" / "p6-higher-order-epistemic-mechanics"


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "p6_higher_order_countermodels",
        EXT / "run_countermodels_v1.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_countermodel_summary_is_exactly_rederived():
    runner = _load_runner()
    panel = json.loads((EXT / "COUNTERMODELS_V1.json").read_text())
    expected = json.loads((EXT / "COUNTERMODEL_SUMMARY_V1.json").read_text())
    assert runner.run(panel) == expected


def test_countermodel_terminal_is_non_authorizing():
    summary = json.loads((EXT / "COUNTERMODEL_SUMMARY_V1.json").read_text())
    assert summary["terminal"] == "TRANCHE1_FORMAL_COUNTERMODELS_GREEN"
    assert summary["claim_ceiling"] == (
        "FORMAL_NON_AUTHORIZING_MINIMAL_REVISION_SUBSTRATE_ONLY"
    )
    assert summary["grants_scientific_authority"] is False
    assert summary["grants_self_orion_adoption"] is False
