"""Unit tests for the Self-ORION V4 successor subject and panel builders.

Covers the mechanism the V3 confirmatory execution left unexercised: the
revision-gate blocking branch driven by candidate-visible preservation
obligations projected into forbidden writes.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from orion.study.p5.revision_level_v3_freeze import (
    derive_candidate_packet,
    validate_protected_suite,
)
from orion.study.p5.revision_level_v3_policies import (
    FeedbackMode,
    ProtectedFeedbackOracle,
    RevisionPolicyDecision,
)
from orion.study.p5.revision_level_v4_policies import (
    SUBJECT_POLICY_ID,
    run_revision_policy_v4,
)

ROOT = Path(__file__).resolve().parents[3]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_builder = _load(
    "v4_suite_builder", "research/self-orion-v4/confirmatory/build_confirmatory_suite_v2.py"
)
_splitter = _load(
    "v4_split_builder", "research/self-orion-v4/confirmatory/build_final_split_v2.py"
)


def _suite_packet_cases():
    suite = _builder.build_suite()
    validate_protected_suite(suite)
    packet = derive_candidate_packet(suite)
    suite_cases = {str(c["case_id"]): c for c in suite["cases"]}
    packet_cases = {str(c["case_id"]): c for c in packet["cases"]}
    assert set(suite_cases) == set(packet_cases)
    return suite, suite_cases, packet_cases


def _oracle_for(suite_case) -> ProtectedFeedbackOracle:
    return ProtectedFeedbackOracle(
        case_id=str(suite_case["case_id"]),
        outcome_by_action=dict(suite_case["protected_diagnostic_outcomes"]),
        mode=FeedbackMode.NORMAL,
    )


def _run(policy: str, packet_case, suite_case) -> RevisionPolicyDecision:
    decision = run_revision_policy_v4(policy, packet_case, _oracle_for(suite_case))
    decision.verify()
    return decision


@pytest.fixture(scope="module")
def panel():
    return _suite_packet_cases()


def test_panel_size_strata_and_gold_coverage(panel):
    _suite, suite_cases, _packet = panel
    assert len(suite_cases) == 180
    identifiable = [cid for cid in suite_cases if not cid.endswith(("-7", "-8"))]
    ambiguous = [cid for cid in suite_cases if cid.endswith("-7")]
    preservation = [cid for cid in suite_cases if cid.endswith("-8")]
    assert (len(identifiable), len(ambiguous), len(preservation)) == (140, 20, 20)
    gold_counts: dict[str, int] = {}
    for case in suite_cases.values():
        gold_counts[str(case["protected_gold_revision_class"])] = (
            gold_counts.get(str(case["protected_gold_revision_class"]), 0) + 1
        )
    for repair in _builder.REPAIRS:
        assert gold_counts[repair] == 20
    assert gold_counts["UNRESOLVED"] == 40
    for cid in preservation:
        state = suite_cases[cid]["protected_evaluator_state"]
        assert state["preservation_conflict"] is True
        forbidden = state["preservation_forbidden_write"]
        assert forbidden in suite_cases[cid]["protected_surface"]
        assert f"preserve:{forbidden}" in suite_cases[cid]["preservation_obligations"]
    cannot_check = sum(
        1 for c in suite_cases.values() if c["protected_evaluator_state"]["cannot_check"]
    )
    assert cannot_check == 10


def test_candidate_packet_never_contains_protected_fields(panel):
    _suite, _suite_cases, _packet_cases = panel
    packet = derive_candidate_packet(_suite)
    for key in packet:
        assert not str(key).startswith("protected_")
    for case in packet["cases"]:
        assert not str(case["case_id"]).startswith("protected_")
        for key in case:
            assert not str(key).startswith("protected_")
        assert case["revision_invasiveness"] == packet["revision_invasiveness"]


def test_v4_subject_promotes_on_identifiable_cases(panel):
    _suite, suite_cases, packet_cases = panel
    for cid, packet_case in packet_cases.items():
        if cid.endswith(("-7", "-8")):
            continue
        decision = _run(SUBJECT_POLICY_ID, packet_case, suite_cases[cid])
        assert decision.selected_revision_class == str(
            suite_cases[cid]["protected_gold_revision_class"]
        ), cid
        assert "PRESERVATION_BLOCKED" not in ",".join(decision.trace)


def test_v4_subject_refuses_ambiguous_cases(panel):
    _suite, suite_cases, packet_cases = panel
    for cid, packet_case in packet_cases.items():
        if not cid.endswith("-7"):
            continue
        decision = _run(SUBJECT_POLICY_ID, packet_case, suite_cases[cid])
        assert decision.selected_revision_class == "UNRESOLVED", cid
        assert not any(t.startswith("PRESERVATION_BLOCKED:") for t in decision.trace)


def test_v4_subject_refuses_preservation_conflicts_through_blocked_gate(panel):
    _suite, suite_cases, packet_cases = panel
    for cid, packet_case in packet_cases.items():
        if not cid.endswith("-8"):
            continue
        decision = _run(SUBJECT_POLICY_ID, packet_case, suite_cases[cid])
        assert decision.selected_revision_class == "UNRESOLVED", cid
        blocked = [t for t in decision.trace if t.startswith("PRESERVATION_BLOCKED:")]
        assert blocked, cid
        forbidden = suite_cases[cid]["protected_evaluator_state"]["preservation_forbidden_write"]
        assert forbidden in blocked[0]
        assert any(t.startswith("REVISION_GATE:") for t in decision.trace)


def test_v3_parent_still_promotes_on_preservation_conflicts(panel):
    """The parent's measurable defect: diagnosis licenses a preserved write."""
    _suite, suite_cases, packet_cases = panel
    for cid, packet_case in packet_cases.items():
        if not cid.endswith("-8"):
            continue
        parent = _run("FULL_T7", packet_case, suite_cases[cid])
        subject = _run(SUBJECT_POLICY_ID, packet_case, suite_cases[cid])
        assert parent.selected_revision_class != "UNRESOLVED", cid
        assert subject.selected_revision_class == "UNRESOLVED", cid


def test_delegation_identity_on_non_preservation_cases(panel):
    _suite, suite_cases, packet_cases = panel
    for cid, packet_case in packet_cases.items():
        if cid.endswith("-8"):
            continue
        parent = _run("FULL_T7", packet_case, suite_cases[cid])
        subject = _run(SUBJECT_POLICY_ID, packet_case, suite_cases[cid])
        assert parent.selected_revision_class == subject.selected_revision_class, cid
        assert list(parent.diagnostic_actions) == list(subject.diagnostic_actions), cid


def test_baseline_arms_delegate_verbatim(panel):
    _suite, suite_cases, packet_cases = panel
    sample = sorted(packet_cases)[::37]
    for policy in (
        "NO_REVISION",
        "DIRECT_SELF_EDIT",
        "M_OPEN_ONLY",
        "ALWAYS_UNRESOLVED",
        "RANDOM_DIAGNOSTIC",
    ):
        for cid in sample:
            decision = _run(policy, packet_cases[cid], suite_cases[cid])
            assert decision.policy_id == policy
            decision.verify()


def test_subject_respects_diagnostic_budget(panel):
    _suite, suite_cases, packet_cases = panel
    for cid, packet_case in packet_cases.items():
        decision = _run(SUBJECT_POLICY_ID, packet_case, suite_cases[cid])
        costs = {
            str(a["action_id"]): float(a["cost"]) for a in packet_case["allowed_diagnostics"]
        }
        spent = sum(costs[a] for a in decision.diagnostic_actions)
        assert spent <= float(packet_case["diagnostic_budget"]) + 1e-12, cid


def test_final_split_is_even_and_deterministic(panel):
    suite, _suite_cases, _packet_cases = panel
    split = _splitter.build_split(suite)
    assignment = split["assignment"]
    assert len(assignment) == 180
    counts = {arm: sum(1 for v in assignment.values() if v == arm) for arm in ("PRIMARY_A", "REPLICATION_B")}
    assert counts == {"PRIMARY_A": 90, "REPLICATION_B": 90}
    for gold, stats in split["stratification"].items():
        assert abs(stats["PRIMARY_A"] - stats["REPLICATION_B"]) <= 1, gold
    again = _splitter.build_split(suite)
    assert again == split
