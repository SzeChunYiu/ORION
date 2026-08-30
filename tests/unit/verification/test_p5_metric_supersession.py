from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from independent_scorers import score_p5_attribution


ROOT = Path(__file__).resolve().parents[3]
P5 = ROOT / "papers/orion-15-self-orion"
RESULTS = P5 / "evidence/glm-5.2-attribution/results.jsonl"
REPORT = P5 / "evidence/glm-5.2-attribution/report.json"
RECEIPT = P5 / "evidence/glm-5.2-attribution/REPRODUCTION_RECEIPT.json"
TABLE = P5 / "evidence/TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json"
DISCREPANCY = P5 / "evidence/DISCREPANCY_P5_D1_MACRO_F1_V1.json"
SUITE = P5 / "evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json"
# Pre-R0 identity of the same artifact, retained so the rename stays auditable.
PRE_R0_REPORT_SHA256 = "13ac651d00513b737023c309eab3ed3bde7adcc5f9612d146705d1d4a0877eca"
# Current identity: R0 (commit 3a1a83178) renamed the paper directory and rewrote
# this file's results_path/suite_path with it. Metrics are byte-identical across
# the rename; see DISCREPANCY_P5_D1_MACRO_F1_V1.json -> original_artifact.identity_migration.
HISTORICAL_REPORT_SHA256 = "676c1d78e9570f450b1b734ce17990131f3eb6ea5c94afb8ae7baa113c980abe"


def _independent_score() -> dict[str, object]:
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    gold = {case["case_id"]: case["protected_root_cause"] for case in suite["cases"]}
    return score_p5_attribution(rows, gold)


def test_corrected_current_metrics_match_independent_scorer() -> None:
    """D1 closes only if the current publication-derived artifacts equal #283's scorer."""

    scored = _independent_score()
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    table = json.loads(TABLE.read_text(encoding="utf-8"))

    assert scored["n"] == 24
    assert scored["correct"] == 21
    assert scored["accuracy"] == 0.875
    assert scored["macro_f1"] == pytest.approx(0.8726190476190476)
    assert receipt["metrics"]["accuracy"] == scored["accuracy"]
    assert receipt["metrics"]["macro_f1"] == pytest.approx(scored["macro_f1"])
    assert table["summary_metrics"]["accuracy"] == scored["accuracy"]
    assert table["summary_metrics"]["macro_f1"] == pytest.approx(scored["macro_f1"])


def test_historical_metric_disagreement_remains_visible_after_supersession() -> None:
    """A corrected derived artifact must not erase the report that caused D1."""

    historical = json.loads(REPORT.read_text(encoding="utf-8"))
    discrepancy = json.loads(DISCREPANCY.read_text(encoding="utf-8"))
    scored = _independent_score()

    assert hashlib.sha256(REPORT.read_bytes()).hexdigest() == HISTORICAL_REPORT_SHA256
    assert historical["metrics"]["macro_f1"] == 0.875
    assert historical["metrics"]["macro_f1"] != pytest.approx(scored["macro_f1"])
    assert discrepancy["original_artifact"]["sha256"] == HISTORICAL_REPORT_SHA256
    assert discrepancy["original_artifact"]["preserved_unchanged"] is True
    assert discrepancy["differing_fields"]["independent_standard_macro_f1"] == pytest.approx(scored["macro_f1"])
    assert discrepancy["authority"]["empirical_authority"] == "ATTRIBUTION_DIAGNOSIS_ONLY"
    assert discrepancy["authority"]["self_authorizing"] is False
