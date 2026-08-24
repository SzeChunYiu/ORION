from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DISPOSITION = ROOT / "papers" / "ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json"


def _payload() -> dict:
    return json.loads(DISPOSITION.read_text(encoding="utf-8"))


def test_all_issue_1086_portfolio_decisions_are_recorded_once() -> None:
    payload = _payload()
    decisions = payload["decisions"]
    assert [row["decision_id"] for row in decisions] == [f"D{i}" for i in range(1, 9)]
    assert len({row["decision_id"] for row in decisions}) == 8
    assert payload["schema_version"] == "orion.issue-1086.portfolio-disposition.v1"
    assert payload["issue"] == "https://github.com/SzeChunYiu/ORION/issues/1086"
    exact = {
        "D1": (["P1", "P2", "P3", "P4"], "ADOPTED", "SHARED_INTERNAL_SPECIFICATION_TEST_FAMILY"),
        "D2": (["P1", "P2", "P3", "P4"], "ADOPTED_CONDITIONAL", "SEPARATE_ONLY_AFTER_DISTINCT_EXTERNAL_EVIDENCE"),
        "D3": (["P6", "P7", "P8"], "ADOPTED_CONDITIONAL", "CONSOLIDATE_UNIFIED_CALCULUS"),
        "D4": (["P9"], "ADOPTED_CONDITIONAL", "STANDALONE_BLOCKED"),
        "D5": (["P10"], "ADOPTED", "EXECUTION_PROGRAMME"),
        "D6": (["P12"], "ADOPTED_CONDITIONAL", "STRICT_STOP_GO"),
        "D7": (["P13", "P14"], "ADOPTED", "CONSOLIDATE_LIFECYCLE_CONTRACT_SAFETY"),
        "D8": (["P15", "Q3"], "ADOPTED", "CONSOLIDATE_SOFTWARE_INSTRUMENT"),
    }
    assert {
        row["decision_id"]: (row["papers"], row["status"], row["disposition"])
        for row in decisions
    } == exact


def test_distinct_p1_p4_external_partitions_are_named() -> None:
    payload = _payload()
    decision = next(row for row in payload["decisions"] if row["decision_id"] == "D2")
    partitions = decision["required_external_partitions"]
    assert partitions == {
        "P1": "ScienceAgentBench",
        "P2": "TREC-COVID",
        "P3": "OAEI",
        "P4": "SciFact/Crossref",
    }
    assert len(set(partitions.values())) == 4


def test_editorial_disposition_cannot_launder_scientific_authority() -> None:
    payload = _payload()
    boundaries = " ".join(payload["non_bypass_boundaries"])
    assert payload["authority"] == "PORTFOLIO_EDITORIAL_DISPOSITION_ONLY__NO_NEW_SCIENTIFIC_AUTHORITY"
    assert payload["scientific_authority_delta"] == "NONE"
    assert "independent adjudication" in boundaries
    assert "protected confirmation" in boundaries
    assert "CANNOT_CHECK" in boundaries


def test_required_consolidations_and_stop_go_states_are_explicit() -> None:
    by_id = {row["decision_id"]: row for row in _payload()["decisions"]}
    assert by_id["D3"]["disposition"] == "CONSOLIDATE_UNIFIED_CALCULUS"
    assert by_id["D5"]["disposition"] == "EXECUTION_PROGRAMME"
    assert by_id["D6"]["disposition"] == "STRICT_STOP_GO"
    assert by_id["D7"]["disposition"] == "CONSOLIDATE_LIFECYCLE_CONTRACT_SAFETY"
    assert by_id["D8"]["disposition"] == "CONSOLIDATE_SOFTWARE_INSTRUMENT"
