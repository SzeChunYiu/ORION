"""The attribution checker must reject mutants, not merely pass on real data.

A checker validated only against the data it was written for proves nothing: it
may be asserting a tautology. Each test below breaks exactly one property the
checker claims to detect and requires the matching non-zero exit.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "_attribute_advantage_v1", HERE / "attribute_advantage_v1.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load_module()


@pytest.fixture(scope="module")
def real(mod):
    source = json.loads(mod.SOURCE.read_text(encoding="utf-8"))
    costed = json.loads(mod.COSTED.read_text(encoding="utf-8"))
    return source, costed


def _run(mod, tmp_path, source, costed):
    """Point the module at mutated inputs and run its real main()."""
    src = tmp_path / "RESULTS_V1.json"
    cst = tmp_path / "RESULT_V1.json"
    src.write_text(json.dumps(source), encoding="utf-8")
    cst.write_text(json.dumps(costed), encoding="utf-8")
    original = (mod.SOURCE, mod.COSTED)
    mod.SOURCE, mod.COSTED = src, cst
    try:
        return mod.main([])
    finally:
        mod.SOURCE, mod.COSTED = original


def test_real_data_passes(mod, tmp_path, real):
    source, costed = real
    assert _run(mod, tmp_path, source, costed) == 0


def test_safety_matched_arm_whose_views_disagree_is_a_finding(mod, tmp_path, real):
    """A zero-forbidden arm must give identical counts under both views."""
    source, costed = copy.deepcopy(real[0]), real[1]
    for comparison in source["comparisons"]:
        if comparison["comparator"] == "random_safe_ablation":
            comparison["outcomes"]["raw_success"]["orion_better"] += 1
            break
    else:  # pragma: no cover
        pytest.fail("random_safe_ablation absent from the source table")
    assert _run(mod, tmp_path, source, costed) == 2


def test_unsafe_arm_favouring_orion_on_raw_success_is_a_finding(mod, tmp_path, real):
    """The separation breaks if ORION wins on raw success without the conjunct."""
    source, costed = copy.deepcopy(real[0]), real[1]
    for comparison in source["comparisons"]:
        if comparison["comparator"] == "exact_dp_oracle":
            comparison["outcomes"]["raw_success"]["favours"] = "ORION"
            break
    else:  # pragma: no cover
        pytest.fail("exact_dp_oracle absent from the source table")
    assert _run(mod, tmp_path, source, costed) == 2


def test_primary_criterion_no_longer_favouring_orion_is_a_finding(mod, tmp_path, real):
    source, costed = copy.deepcopy(real[0]), real[1]
    source["comparisons"][0]["outcomes"]["frozen_primary"]["favours"] = "COMPARATOR"
    assert _run(mod, tmp_path, source, costed) == 2


def test_drifted_published_rate_is_cannot_check_not_a_finding(mod, tmp_path, real):
    """If the source table moved, we are not measuring what the note described."""
    source, costed = real[0], copy.deepcopy(real[1])
    costed["per_arm"]["orion_level_monotone"]["joint_clear_rate"] = 0.5
    assert _run(mod, tmp_path, source, costed) == 3


def test_missing_outcome_view_is_cannot_check(mod, tmp_path, real):
    source, costed = copy.deepcopy(real[0]), real[1]
    del source["comparisons"][0]["outcomes"]["raw_success"]
    assert _run(mod, tmp_path, source, costed) == 3


def test_absent_input_is_cannot_check(mod, tmp_path, real):
    source, costed = real
    src = tmp_path / "gone.json"
    cst = tmp_path / "RESULT_V1.json"
    cst.write_text(json.dumps(costed), encoding="utf-8")
    original = (mod.SOURCE, mod.COSTED)
    mod.SOURCE, mod.COSTED = src, cst
    try:
        assert mod.main([]) == 3
    finally:
        mod.SOURCE, mod.COSTED = original


def test_committed_result_matches_a_fresh_run(mod, tmp_path, real):
    """The committed RESULTS_V1.json must be what the checker produces now."""
    committed = HERE / "RESULTS_V1.json"
    if not committed.is_file():  # pragma: no cover
        pytest.skip("no committed result to compare against")
    out = tmp_path / "fresh.json"
    source, costed = real
    src = tmp_path / "RESULTS_V1.json"
    cst = tmp_path / "RESULT_V1.json"
    src.write_text(json.dumps(source), encoding="utf-8")
    cst.write_text(json.dumps(costed), encoding="utf-8")
    original = (mod.SOURCE, mod.COSTED)
    mod.SOURCE, mod.COSTED = src, cst
    try:
        assert mod.main(["--json-out", str(out)]) == 0
    finally:
        mod.SOURCE, mod.COSTED = original
    fresh = json.loads(out.read_text(encoding="utf-8"))
    stored = json.loads(committed.read_text(encoding="utf-8"))
    # `reads` records the real input paths; the fresh run used temp copies.
    fresh.pop("reads", None)
    stored.pop("reads", None)
    assert fresh == stored
