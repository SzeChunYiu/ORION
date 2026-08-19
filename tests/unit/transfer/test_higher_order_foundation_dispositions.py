from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "p6-higher-order-epistemic-mechanics"
DISPOSITIONS = RESEARCH / "FOUNDATION_ISSUE_DISPOSITIONS_V1.json"
PARENTS = RESEARCH / "FORMAL_PARENT_MAP_V1.json"


def test_foundation_dispositions_are_complete_and_parent_bound() -> None:
    dispositions = json.loads(DISPOSITIONS.read_text(encoding="utf-8"))
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))

    parent_ids = {row["component_id"] for row in parents["components"]}
    rows = {row["issue"]: row for row in dispositions["issues"]}

    assert set(rows) == {452, 458, 459, 462, 463}
    assert rows[452]["terminal"] == "FOUNDATION_NARROWED_TO_EXISTING_THEORY"
    assert rows[458]["terminal"] == "NO_INCREMENTAL_VALUE"
    assert rows[459]["terminal"] == "EXISTING_DIAGNOSTICS_SUFFICIENT"
    assert rows[462]["terminal"] == "EXISTING_SOCIAL_THEORY_SUFFICIENT"
    assert rows[463]["terminal"] == "FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS"

    for row in rows.values():
        assert row["basis"]
        assert set(row["basis"]) <= parent_ids
        assert row["kept_orion_object"]
        assert row["struck_claim"]

    assert parents["new_unified_primitive_count"] == 0
    assert parents["unified_calculus_novelty"] == "STRUCK"


def test_foundation_dispositions_do_not_self_authorize_closure() -> None:
    dispositions = json.loads(DISPOSITIONS.read_text(encoding="utf-8"))

    assert dispositions["authority"] == "ISSUE_DISPOSITION_ONLY_AFTER_EXACT_HEAD_CI_AND_MERGE"
    assert any("No issue is closed" in item for item in dispositions["nonclaims"])
