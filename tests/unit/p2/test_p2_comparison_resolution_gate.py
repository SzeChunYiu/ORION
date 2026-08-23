from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "papers" / "paper-02-open-world-scientific-discovery" / "scripts" / "comparison_resolution_gate.py"
AUDIT = ROOT / "papers" / "paper-02-open-world-scientific-discovery" / "evidence" / "audit" / "P2_COMPARISON_RESOLUTION_2026-08-22.json"


def _load():
    spec = importlib.util.spec_from_file_location("p2_comparison_resolution_gate", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_both_committed_wide_campaigns_are_refused_and_control_passes():
    module = _load()
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    for name, summary in payload["campaigns"].items():
        result = module.assess(summary)
        assert not result["passed"], name
        assert result["terminal"] == module.FAIL_TERMINAL
    assert module.assess(payload["control"])["passed"]


def test_distinct_candidates_do_not_rescue_identical_evaluator_outputs():
    module = _load()
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    v3 = payload["campaigns"]["P2_WIDE_OPENAIRE_MATCHED_RESULT_V3.json"]
    result = module.assess(v3)
    assert "DISTINCT_CANDIDATE_ARTIFACTS" not in result["failed_checks"]
    assert "DISTINCT_EVALUATOR_OUTPUTS" in result["failed_checks"]


def test_all_ties_zero_width_is_not_equivalence_at_any_n():
    module = _load()
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    summary = dict(payload["control"])
    summary["paired"] = {
        "n": 1_000_000,
        "wins": 0,
        "losses": 0,
        "ties": 1_000_000,
        "ci95_low": 0.0,
        "ci95_high": 0.0,
    }
    result = module.assess(summary)
    assert "PAIRED_SPLIT_HAS_DISCORDANCE" in result["failed_checks"]
    assert "NO_ALL_TIES_ZERO_WIDTH_EQUIVALENCE" in result["failed_checks"]


def test_measurement_floor_makes_registered_margin_unreachable():
    module = _load()
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    summary = dict(payload["control"])
    summary["floor"] = {
        "checked": True,
        "best_arm_avg_iou": 0.004,
        "required_avg_iou_delta": 0.03,
    }
    assert "ABSOLUTE_SCORE_SCALE_REACHES_EFFECT_MARGIN" in module.assess(summary)["failed_checks"]


def test_failed_resolution_blocks_every_requested_scientific_terminal():
    module = _load()
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    failed = payload["campaigns"]["P2_WIDE_OPENAIRE_MATCHED_RESULT_V3.json"]
    for requested in ("SUPPORTED", "NON_INFERIOR", "EQUIVALENT", "NOT_SUPPORTED"):
        result = module.authorize_scientific_terminal(failed, requested)
        assert not result["authorized"]
        assert result["terminal"] == module.FAIL_TERMINAL


def test_resolution_pass_is_only_an_instrument_precondition():
    module = _load()
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    result = module.assess(payload["control"])
    assert result["passed"]
    assert result["scientific_authority"] == "NONE"

