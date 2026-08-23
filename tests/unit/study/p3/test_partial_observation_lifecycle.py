from __future__ import annotations

import copy
import json
from pathlib import Path

from orion.study.p3.partial_observation_lifecycle import build_lifecycle, validate_lifecycle

ROOT = Path(__file__).resolve().parents[4]
ARTIFACT = ROOT / "papers/paper-03-global-knowledge-portrait/P3_PARTIAL_OBSERVATION_LIFECYCLE_V1.json"


def payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_committed_lifecycle_is_derived_and_has_one_active_leaf() -> None:
    actual = payload()
    assert actual == build_lifecycle()
    assert validate_lifecycle(actual) == []
    assert actual["active_leaf"] == "A004"
    assert [n["node_id"] for n in actual["nodes"] if n["authority_state"] == "ACTIVE_ADJUDICATIVE"] == ["A004"]
    assert all(n["overall_outcome"] == "FAIL" for n in actual["nodes"])


def test_filename_order_cannot_select_authority() -> None:
    changed = payload()
    changed["nodes"] = list(reversed(changed["nodes"]))
    assert validate_lifecycle(changed)


def test_duplicate_id_missing_predecessor_and_digest_substitution_fail() -> None:
    for mutate in (
        lambda p: p["nodes"].__setitem__(1, copy.deepcopy(p["nodes"][0])),
        lambda p: p["nodes"][4].__setitem__("predecessor", None),
        lambda p: p["nodes"][4].__setitem__("protocol_sha256", "0" * 64),
    ):
        changed = payload()
        mutate(changed)
        assert validate_lifecycle(changed)


def test_more_than_one_active_leaf_fails() -> None:
    changed = payload()
    changed["nodes"][3]["authority_state"] = "ACTIVE_ADJUDICATIVE"
    assert validate_lifecycle(changed)


def test_stale_gate_check_is_typed_as_history() -> None:
    states = {item["path"]: item["state"] for item in payload()["document_states"]}
    assert states["JOURNAL_GATE_CHECK.md"] == "HISTORICAL_PREPARATORY_SNAPSHOT"
    assert states["JOURNAL_READINESS.md"] == "CURRENT_SCOPED_READINESS"
