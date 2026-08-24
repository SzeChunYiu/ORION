from __future__ import annotations

import json
from pathlib import Path

from orion.study.p5_attribution_publication import PRESERVED_ERRORS, generate

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "papers" / "paper-05-self-orion" / "evidence" / "glm-5.2-attribution" / "results.jsonl"


def _rows() -> list[dict[str, object]]:
    return [json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_generate_writes_p5_2_through_p5_7_from_archived_rows(tmp_path: Path) -> None:
    generate(_rows(), tmp_path)
    for name in (
        "TABLE_P5_2_REPLAY_VS_FRESH.json",
        "TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json",
        "TABLE_P5_4_LONGITUDINAL.json",
        "TABLE_P5_5_IMPROVEMENT_INTEGRITY_FRONTIER.json",
        "TABLE_P5_6_FAILURE_RECURRENCE.json",
        "TABLE_P5_7_ATTRIBUTION_COST.json",
        "P5_ATTRIBUTION_TABLES_V1.md",
        "README.md",
    ):
        assert (tmp_path / name).is_file(), name

    p2 = json.loads((tmp_path / "TABLE_P5_2_REPLAY_VS_FRESH.json").read_text())
    p3 = json.loads((tmp_path / "TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json").read_text())
    p4 = json.loads((tmp_path / "TABLE_P5_4_LONGITUDINAL.json").read_text())
    p5 = json.loads((tmp_path / "TABLE_P5_5_IMPROVEMENT_INTEGRITY_FRONTIER.json").read_text())
    p6 = json.loads((tmp_path / "TABLE_P5_6_FAILURE_RECURRENCE.json").read_text())
    p7 = json.loads((tmp_path / "TABLE_P5_7_ATTRIBUTION_COST.json").read_text())

    assert p2["status"] == p4["status"] == p5["status"] == p6["status"] == "CANNOT_CHECK"
    assert p2["rows"] == p4["rows"] == p5["rows"] == []
    assert p3["summary_metrics"]["correct_attributions"] == 21
    assert p3["summary_metrics"]["incorrect_attributions"] == 3
    assert p3["summary_metrics"]["macro_f1"] == 0.8726190476190476
    assert p3["per_family_metrics"]["IMPLEMENTATION_BUG"]["precision"] == 0.75
    assert p3["per_family_metrics"]["IMPLEMENTATION_BUG"]["f1"] == 0.8571428571428571
    got = {
        (row["case_id"], row["gold"], row["attributed"])
        for row in p3["incorrect_cases"]
    }
    assert got == set(PRESERVED_ERRORS)
    assert p3["confusion_matrix"]["RETRIEVAL_MISS"]["attributed_REPRESENTATION_GAP"] == 1
    assert p7["total_tokens"] == 14190
    assert p7["status"] == "ARCHIVED_ATTRIBUTION_ONLY"
    md = (tmp_path / "P5_ATTRIBUTION_TABLES_V1.md").read_text()
    assert "P5-HC-002" in md
    assert "macro-F1 0.8726" in md
    assert "CANNOT_CHECK" in md
