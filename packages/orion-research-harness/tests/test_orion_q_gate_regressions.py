from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_r4b_frozen_hostile_matrix_is_executed():
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "research/extensions/orion-q/max_r4b_tare_split_majorization.py"
    module = _load_module(script, "orion_q_r4b_gate_regression")

    checks = module.exhaustive_theorem_checks()
    assert checks["all_hostile_and_random_checks_pass"] is True
    assert checks["total_failures"] == 0
    assert checks["total_partition_evaluations"] > 0

    required = {
        "all_equal",
        "repeated_magnitudes",
        "zeros",
        "one_dominant",
        "identity_remint",
    }
    for config in checks["configs"].values():
        assert required <= set(config["hostile_cases"])
        assert all(item["pass"] for item in config["hostile_cases"].values())
        assert len(config["random_dynamic_ranges_log10"]) >= 2


def test_r4b_positive_terminal_is_impossible_after_hostile_failure(monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "research/extensions/orion-q/max_r4b_tare_split_majorization.py"
    module = _load_module(script, "orion_q_r4b_negative_gate_regression")

    monkeypatch.setattr(
        module,
        "exhaustive_theorem_checks",
        lambda: {
            "all_hostile_and_random_checks_pass": False,
            "total_failures": 1,
            "total_partition_evaluations": 1,
            "configs": {},
            "tolerance": module.TOL,
        },
    )
    monkeypatch.setattr(module, "lih_result", lambda: {})
    monkeypatch.setattr(module, "uniform_heisenberg_control", lambda: {})
    monkeypatch.setattr(module, "disordered_heisenberg_panel", lambda: {})

    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code == 1
    output = capsys.readouterr().out
    assert "R4B_TARE_SPLIT_MAJORISATION_HOSTILE_CHECK_FAILED__THEOREM_NOT_PROMOTED" in output
    assert "R4B_TARE_SPLIT_MAJORISATION_THEOREM_SUPPORTED__COEFFICIENT_COORDINATE_ONLY" not in output


def test_r4d_ci_requires_scientific_receipt_pass_bit():
    repo_root = Path(__file__).resolve().parents[3]
    workflow = repo_root / ".github/workflows/orion-q-max-r4d.yml"
    text = workflow.read_text()
    assert 'payload.get("r4d_protocol_pass") is not True' in text
    assert "frozen R4D scientific gate did not pass" in text
