"""The frozen label vocabulary must match the labels the source actually uses.

V1 declared SUPPORT/REFUTE. REFUTE is not a SciFact token: the pinned
revision's doc/data.md declares 'SUPPORT' | 'CONTRADICT', and the release
carries 832 SUPPORT and 463 CONTRADICT evidence rows with zero REFUTE. A
matcher honouring V1 would never fire contradiction_dominates, so every
contradicted claim would compose to the wrong verdict while the run looked
healthy.
"""

from __future__ import annotations

import json
from pathlib import Path

BASE = (
    Path(__file__).resolve().parents[3]
    / "papers/orion-14-verified-scientific-discovery/protocol"
)
V2 = BASE / "SCIFACT_LABEL_STATE_MAP_V2.json"


def _map() -> dict:
    return json.loads(V2.read_text())


def test_evidence_labels_are_the_ones_scifact_uses() -> None:
    vocab = _map()["scifact_label_vocabulary"]
    assert vocab["evidence_document_labels"] == ["SUPPORT", "CONTRADICT"]


def test_refute_appears_in_no_field_a_matcher_reads() -> None:
    """The token that made the contradiction path unreachable.

    It is still allowed -- required, in fact -- in the supersession reason,
    which has to name the defect it corrects. What must not survive is any
    occurrence a scorer would match against.
    """
    m = _map()
    vocab = m["scifact_label_vocabulary"]
    # the three places a scorer compares a label against
    assert "REFUTE" not in vocab["evidence_document_labels"]
    assert "REFUTE" not in vocab["claim_verdict_labels"]
    assert "REFUTE" not in {r["scifact_label"] for r in m["frozen_mapping"]}
    assert "REFUTE" not in json.dumps(m["claim_verdict_composition"])
    # and the mapping prose must not instruct a reader to match it either
    assert "REFUTE" not in json.dumps([r.get("rule_text", "") for r in m["frozen_mapping"]])
    # the observed-count record deliberately keeps REFUTE: 0 as evidence of absence
    assert vocab["observed_counts_train_plus_dev"]["REFUTE"] == 0


def test_mapping_covers_every_composed_verdict() -> None:
    m = _map()
    rows = {r["scifact_label"] for r in m["frozen_mapping"]}
    assert rows == set(m["scifact_label_vocabulary"]["claim_verdict_labels"])


def test_contradiction_dominates_names_the_real_token() -> None:
    rules = _map()["claim_verdict_composition"]["rules"]
    assert "CONTRADICT" in rules["contradiction_dominates"]


def test_v2_supersedes_v1_with_its_hash_and_reason() -> None:
    sup = _map()["supersedes"]
    assert sup["artifact"] == "SCIFACT_LABEL_STATE_MAP_V1.json"
    assert len(sup["sha256"]) == 64
    assert sup["corrected_before_any_scoring"] is True
    assert "REFUTE" in sup["reason"]  # the reason must name the defect


def test_v2_still_predates_scoring() -> None:
    m = _map()
    assert m["outcome_accessed"] is False
    assert m["scifact_outcome_artifacts_present_at_freeze"] == 0


def test_v1_is_retained_not_deleted() -> None:
    assert (BASE / "SCIFACT_LABEL_STATE_MAP_V1.json").is_file()
