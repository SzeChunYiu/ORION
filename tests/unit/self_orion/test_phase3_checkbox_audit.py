"""Issue #209 checkbox audit: tick only verified-on-main, never fabricate empirical PASS."""

from __future__ import annotations

import json
from pathlib import Path

from orion.self_orion.phase3_checkbox_audit import (
    AUDIT_SCHEMA,
    ISSUE_209_CHECKBOXES,
    CheckboxKind,
    CheckboxVerdict,
    audit_issue_209_checkboxes,
    issue_209_checkbox_audit_to_dict,
)
from orion.self_orion.phase3_promotion import (
    MISSING_LONGITUDINAL_TRIAL_ID,
    MISSING_PROMOTION_TRIAL_ID,
    PHASE3_TERMINAL_CLAIM,
)

CANONICAL_AUDIT_PATH = (
    Path(__file__).resolve().parents[3]
    / "development"
    / "phase3"
    / "ISSUE_209_CHECKBOX_AUDIT_v1.json"
)


def test_audit_covers_every_issue_209_checkbox_exactly_once() -> None:
    audit = audit_issue_209_checkboxes()
    ids = [item.checkbox_id for item in audit.items]
    assert len(ids) == len(set(ids)) == len(ISSUE_209_CHECKBOXES) == 49
    assert audit.issue_number == 209
    assert audit.schema == AUDIT_SCHEMA
    assert not audit.closes_issue_209
    assert not audit.emits_terminal_claim
    assert not audit.grants_governed_self_orion


def test_github_ticks_are_exactly_the_verified_on_main_boxes() -> None:
    audit = audit_issue_209_checkboxes()
    ticked = tuple(item.checkbox_id for item in audit.items if item.github_tick)
    assert ticked == audit.verified_on_main_ids
    for item in audit.items:
        if item.verdict is CheckboxVerdict.VERIFIED_ON_MAIN:
            assert item.github_tick is True
            assert item.kind is CheckboxKind.PROTOCOL_FREEZE
        else:
            assert item.github_tick is False


def test_empirical_boxes_are_cannot_check_and_name_the_missing_trial() -> None:
    audit = audit_issue_209_checkboxes()
    empirical = [item for item in audit.items if item.kind is CheckboxKind.EMPIRICAL_TRIAL]
    assert empirical
    for item in empirical:
        assert item.verdict is CheckboxVerdict.CANNOT_CHECK
        assert item.github_tick is False
        assert item.missing_trial_id in {
            MISSING_PROMOTION_TRIAL_ID,
            MISSING_LONGITUDINAL_TRIAL_ID,
        }
    step4 = [item for item in empirical if item.checkbox_id.startswith("step4.")]
    assert len(step4) == 9
    assert {item.missing_trial_id for item in step4} == {MISSING_PROMOTION_TRIAL_ID}
    step6 = [item for item in empirical if item.checkbox_id.startswith("step6.")]
    assert len(step6) == 5
    assert {item.missing_trial_id for item in step6} == {MISSING_LONGITUDINAL_TRIAL_ID}


def test_unbound_identities_are_cannot_check_not_verified() -> None:
    audit = audit_issue_209_checkboxes()
    by_id = {item.checkbox_id: item for item in audit.items}
    for checkbox_id in (
        "prefreeze.phase2_terminal_bound",
        "prefreeze.external_host_bound",
        "prefreeze.protected_custody_independent",
        "step1.sampling_epoch_pool",
    ):
        item = by_id[checkbox_id]
        assert item.verdict is CheckboxVerdict.CANNOT_CHECK
        assert item.github_tick is False
        assert item.missing_trial_id == MISSING_PROMOTION_TRIAL_ID


def test_protocol_freeze_boxes_are_verified_on_main_after_pr_269() -> None:
    audit = audit_issue_209_checkboxes()
    by_id = {item.checkbox_id: item for item in audit.items}
    for checkbox_id in (
        "prefreeze.no_grant_code_path",
        "prefreeze.escalation_frozen",
        "step1.define_task_class",
        "step1.inclusion_exclusion",
        "step1.include_ordinary_kinds",
        "step1.exclude_protected",
        "step1.preserve_unresolved",
        "step3.freeze_baseline",
        "step5.fail_closed_host_control",
        "step7.versioned_protocol",
        "step7.hostile_known_answer_tests",
    ):
        item = by_id[checkbox_id]
        assert item.verdict is CheckboxVerdict.VERIFIED_ON_MAIN
        assert item.github_tick is True


def test_shadow_namespace_requirement_is_unmet_not_laundered() -> None:
    audit = audit_issue_209_checkboxes()
    item = {entry.checkbox_id: entry for entry in audit.items}["step7.shadow_pr_integration"]
    assert item.verdict is CheckboxVerdict.UNMET
    assert item.github_tick is False
    assert "merge_was_not_through_shadow_namespace" in item.blockers


def test_exact_final_head_ci_is_cannot_check_because_the_audit_does_not_poll_github() -> None:
    audit = audit_issue_209_checkboxes()
    item = {entry.checkbox_id: entry for entry in audit.items}["step7.exact_final_head_ci"]
    assert item.verdict is CheckboxVerdict.CANNOT_CHECK
    assert item.github_tick is False
    assert "exact_final_head_ci_not_attested_in_repository" in item.blockers


def test_audit_payload_cannot_carry_the_terminal_claim() -> None:
    payload = issue_209_checkbox_audit_to_dict(audit_issue_209_checkboxes())
    dumped = json.dumps(payload)
    assert PHASE3_TERMINAL_CLAIM not in dumped
    assert payload["terminal_claim"] is None
    assert payload["phase_3_governed_self_orion_closed"] is False
    assert payload["closes_issue_209"] is False
    assert payload["primary_missing_trial_id"] == MISSING_PROMOTION_TRIAL_ID
    assert payload["forbidden"]["terminal_claim_emitted"] is False


def test_committed_audit_json_matches_the_code_owned_audit() -> None:
    committed = json.loads(CANONICAL_AUDIT_PATH.read_text(encoding="utf-8"))
    derived = issue_209_checkbox_audit_to_dict(audit_issue_209_checkboxes())
    assert committed == derived
    assert committed["counts"]["total"] == 49
    assert committed["counts"]["verified_on_main"] == len(committed["verified_on_main_ids"])
    assert committed["counts"]["cannot_check"] == len(committed["cannot_check_ids"])
    assert committed["counts"]["unmet"] == len(committed["unmet_ids"])
