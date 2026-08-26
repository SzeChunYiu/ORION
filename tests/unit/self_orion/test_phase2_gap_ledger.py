"""Invariants for the #76 Phase-2 gap ledger and live-packet CANNOT_CHECK.

These records are inventory, not gate evidence. The tests pin the claims that
would be most damaging if they drifted: that Phase 2 is not closed, that no
empirical #76 checkbox is marked tickable, and that the CANNOT_CHECK verdict
still names the unpublished corpus binding on the frozen packet.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LEDGER_PATH = REPO_ROOT / "research/phase2/PHASE2_CLOSURE_GAP_LEDGER_V1.json"
CANNOT_CHECK_PATH = (
    REPO_ROOT / "research/phase2/PHASE2_LIVE_PACKET_EXECUTION_CANNOT_CHECK_V1.json"
)
PACKET_PATH = REPO_ROOT / "papers/orion-15-self-orion/protocol/LIVE_TRIAL_PACKET_V1.json"
BINDING_DOC = REPO_ROOT / "research/phase2/PHASE2_SUBJECT_ANCHOR_BINDING_V1.md"

EMPIRICAL_SECTIONS = {"dependency", "A", "B", "C", "D", "E", "F"}
EMPIRICAL_IDS_THAT_MAY_BE_TICKABLE = {"DEP1"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_gap_ledger_does_not_close_phase2_or_grant_authority():
    ledger = _load(LEDGER_PATH)
    assert ledger["schema"] == "Phase2ClosureGapLedger.v1"
    assert ledger["grants_authority"] == "NONE"
    assert ledger["closes_gate"] is None
    assert ledger["phase2_terminal_issued"] is False
    assert ledger["terminal_string_not_issued"] == "PHASE_2_SHADOW_SELF_ORION_CLOSED"
    assert ledger["summary"]["merged_evidence"] == 0
    assert ledger["summary"]["newly_ticked_by_this_audit"] == 0


def test_only_verified_architecture_and_dep1_are_tickable():
    ledger = _load(LEDGER_PATH)
    items = ledger["items"]
    assert len(items) == ledger["summary"]["total_checkboxes"] == 58

    tickable = [item for item in items if item["tickable_on_main"]]
    untickable = [item for item in items if not item["tickable_on_main"]]
    assert len(tickable) == ledger["summary"]["already_ticked_and_verified_on_main"] == 14
    assert len(untickable) == ledger["summary"]["unticked_and_not_tickable_on_main"] == 44

    for item in tickable:
        assert item["issue_checkbox"] == "checked"
        assert item["action"] == "KEEP_TICKED"
        assert item["class"] == "VERIFIED_ON_MAIN"

    for item in items:
        if item["id"] in EMPIRICAL_IDS_THAT_MAY_BE_TICKABLE:
            continue
        if item["section"] in EMPIRICAL_SECTIONS:
            assert item["tickable_on_main"] is False
            assert item["issue_checkbox"] == "unchecked"
            assert item["action"] == "LEAVE_UNTICKED"
            assert item["class"] != "MERGED_EVIDENCE"
            assert item["class"] != "VERIFIED_ON_MAIN"


def test_live_packet_execution_is_cannot_check_and_matches_published_packet():
    record = _load(CANNOT_CHECK_PATH)
    packet = _load(PACKET_PATH)

    assert record["schema"] == "Phase2LivePacketExecutionCannotCheck.v1"
    assert record["verdict"] == "CANNOT_CHECK"
    assert record["grants_authority"] == "NONE"
    assert record["closes_gate"] is None
    assert record["phase2_terminal_issued"] is False
    assert record["audited_subject"]["is_phase2_closure_subject"] is False

    frozen = record["frozen_packet"]
    assert frozen["corpus_revision"] == "UNBOUND"
    assert frozen["outcome_accessed"] is False
    assert packet["corpus_revision"] == "UNBOUND"
    assert packet["outcome_accessed"] is False
    assert frozen["packet_fingerprint"] == packet["packet_fingerprint"]
    assert frozen["trial_fingerprint"] == packet["trial_fingerprint"]
    assert frozen["packet_id"] == packet["packet_id"]


def test_binding_doc_refuses_the_phase2_terminal():
    text = BINDING_DOC.read_text(encoding="utf-8")
    assert "PHASE_2_SHADOW_SELF_ORION_CLOSED" in text
    assert "not issued" in text.lower()
    assert "7983401847ea2b33706aacbf6e45b6bc63a60d0d" in text
    assert 'corpus_revision: "UNBOUND"' in text
