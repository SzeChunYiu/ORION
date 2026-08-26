from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.self_orion.live_packet import DEEP_TASK_ID, WIDE_TASK_ID
from orion.self_orion.phase2_preflight import DEEP_TARGET_TASK, WIDE_LITERATURE_TASK
from orion.study.p5.fresh_transfer_campaign import (
    ATTRIBUTION_REPORT_PATH,
    ATTRIBUTION_RESULTS_PATH,
    FROZEN_ISSUE8_DEEP_TASK_ID,
    FROZEN_ISSUE8_WIDE_TASK_ID,
    IMMUTABLE_ATTRIBUTION_ERRORS,
    REQUIRED_CREDENTIAL_ENV_VARS,
    AttributionArchive,
    AttributionError,
    FreshTransferCampaignBinding,
    FreshTransferCampaignStatus,
    UnboundFreshTransferCampaign,
    assess_fresh_transfer_campaign_preflight,
    audit_issue_159_checkboxes,
    default_repo_root,
    inspect_phase2_preflight_fail_closed,
    inspect_repository_campaign_binding,
    load_attribution_archive,
    main,
    refuse_unbound_execution,
)


REPO = default_repo_root()
SECRET = "super-secret-credential-value-do-not-emit"


def _valid_archive() -> AttributionArchive:
    return AttributionArchive(
        model="glm-5.2",
        total_cases=24,
        correct=21,
        incorrect=3,
        errors=tuple(
            AttributionError(case_id, gold, attributed)
            for case_id, gold, attributed in IMMUTABLE_ATTRIBUTION_ERRORS
        ),
        results_path=ATTRIBUTION_RESULTS_PATH,
        report_path=ATTRIBUTION_REPORT_PATH,
    )


def _bound_binding(**overrides: object) -> FreshTransferCampaignBinding:
    values: dict[str, object] = dict(
        phase2_preflight_fail_closed=True,
        in_source_wide_task_id=FROZEN_ISSUE8_WIDE_TASK_ID,
        in_source_deep_task_id=FROZEN_ISSUE8_DEEP_TASK_ID,
        frozen_wide_task_id=FROZEN_ISSUE8_WIDE_TASK_ID,
        frozen_deep_task_id=FROZEN_ISSUE8_DEEP_TASK_ID,
        present_credential_env_vars=REQUIRED_CREDENTIAL_ENV_VARS,
        missing_credential_env_vars=(),
        attribution=_valid_archive(),
    )
    values.update(overrides)
    return FreshTransferCampaignBinding(**values)  # type: ignore[arg-type]


def test_merged_attribution_archive_is_21_of_24_with_three_immutable_errors() -> None:
    archive = load_attribution_archive(REPO)
    assert archive.model == "glm-5.2"
    assert archive.total_cases == 24
    assert archive.correct == 21
    assert archive.incorrect == 3
    assert tuple(error.as_tuple() for error in archive.errors) == IMMUTABLE_ATTRIBUTION_ERRORS


def test_laundering_24_of_24_is_rejected(tmp_path: Path) -> None:
    src_results = REPO / ATTRIBUTION_RESULTS_PATH
    src_report = REPO / ATTRIBUTION_REPORT_PATH
    dest = tmp_path / "papers/orion-15-self-orion/evidence/glm-5.2-attribution"
    dest.mkdir(parents=True)
    rewritten = []
    for line in src_results.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        record["attributed_root_cause"] = record["gold_root_cause"]
        record["correct"] = True
        rewritten.append(json.dumps(record))
    (dest / "results.jsonl").write_text("\n".join(rewritten) + "\n", encoding="utf-8")
    report = json.loads(src_report.read_text(encoding="utf-8"))
    report["metrics"]["correct_attributions"] = 24
    report["metrics"]["incorrect_attributions"] = 0
    (dest / "report.json").write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(ValueError, match="21/24"):
        load_attribution_archive(tmp_path)


def test_fail_closed_discriminator_agrees_with_the_p0_probe() -> None:
    from orion.self_orion.phase2_preflight import (
        Phase2ClosurePreflight,
        Phase2PreflightStatus,
        assess_phase2_preflight,
    )

    probe = assess_phase2_preflight(
        Phase2ClosurePreflight(
            protocol_id="phase2-shadow-closure-v1",
            subject_revision_hash="a" * 64,
            provider_manifest_hash="b" * 64,
            evaluator_artifact_hash="c" * 64,
            evaluation_epoch_id="phase2:epoch:frozen-before-outcomes",
            baseline_id="simple-llm-retrieval-baseline-v1",
            resource_budget_units=100.0,
        )
    )
    p0_fail_closed = probe.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
    assert inspect_phase2_preflight_fail_closed() is p0_fail_closed


def test_published_issue8_packet_is_not_the_in_source_execution_registry() -> None:
    assert WIDE_TASK_ID == FROZEN_ISSUE8_WIDE_TASK_ID
    assert DEEP_TASK_ID == FROZEN_ISSUE8_DEEP_TASK_ID
    assert WIDE_LITERATURE_TASK.task_id != FROZEN_ISSUE8_WIDE_TASK_ID
    assert DEEP_TARGET_TASK.task_id != FROZEN_ISSUE8_DEEP_TASK_ID


def test_inspected_repository_binding_refuses_unbound_execution() -> None:
    binding = inspect_repository_campaign_binding(repo_root=REPO, environ={})
    report = assess_fresh_transfer_campaign_preflight(binding)
    assert report.status is not FreshTransferCampaignStatus.READY_TO_EXECUTE
    assert report.issue8_packet_bound is False
    assert any(item.startswith("issue8_packet_unbound:") for item in report.blockers)
    assert any(item.startswith("credentials_absent:") for item in report.blockers)
    if not binding.phase2_preflight_fail_closed:
        assert "phase2_preflight_fail_open" in report.blockers
        assert report.status is FreshTransferCampaignStatus.BIND_FAIL_CLOSED_PREFLIGHT
    assert report.attribution_verified is True
    assert report.empirical_authority == "CANNOT_CHECK"
    assert report.campaign_execution == "REFUSED_UNBOUND"
    assert report.recommends_host_promotion is False
    assert report.grants_phase2_closure is False
    assert report.grants_p5_peer_review_ready is False
    with pytest.raises(UnboundFreshTransferCampaign, match="refusing unbound"):
        refuse_unbound_execution(binding)


def test_three_arbitrary_hashes_do_not_authorize_this_campaign() -> None:
    binding = inspect_repository_campaign_binding(repo_root=REPO, environ={})
    report = assess_fresh_transfer_campaign_preflight(binding)
    assert report.status is not FreshTransferCampaignStatus.READY_TO_EXECUTE
    assert report.recommends_host_promotion is False


def test_task_id_divergence_blocks_and_names_both_registries() -> None:
    report = assess_fresh_transfer_campaign_preflight(
        _bound_binding(
            in_source_wide_task_id=WIDE_LITERATURE_TASK.task_id,
            in_source_deep_task_id=DEEP_TARGET_TASK.task_id,
        )
    )
    assert report.status is FreshTransferCampaignStatus.BIND_ISSUE8_PACKET
    blocker = next(item for item in report.blockers if item.startswith("issue8_packet_unbound:"))
    assert WIDE_LITERATURE_TASK.task_id in blocker
    assert FROZEN_ISSUE8_WIDE_TASK_ID in blocker
    assert DEEP_TARGET_TASK.task_id in blocker
    assert FROZEN_ISSUE8_DEEP_TASK_ID in blocker


def test_missing_credentials_are_named_without_values() -> None:
    missing = REQUIRED_CREDENTIAL_ENV_VARS
    report = assess_fresh_transfer_campaign_preflight(
        _bound_binding(
            present_credential_env_vars=(),
            missing_credential_env_vars=missing,
        )
    )
    assert report.status is FreshTransferCampaignStatus.BIND_CREDENTIALS
    encoded = json.dumps(report.to_json_dict())
    assert SECRET not in encoded
    for name in REQUIRED_CREDENTIAL_ENV_VARS:
        assert name in encoded


def test_erasing_immutable_errors_blocks_the_campaign() -> None:
    damaged = AttributionArchive(
        model="glm-5.2",
        total_cases=24,
        correct=24,
        incorrect=0,
        errors=(),
        results_path=ATTRIBUTION_RESULTS_PATH,
        report_path=ATTRIBUTION_REPORT_PATH,
    )
    report = assess_fresh_transfer_campaign_preflight(_bound_binding(attribution=damaged))
    assert report.status is FreshTransferCampaignStatus.BIND_ATTRIBUTION_ARCHIVE
    assert "immutable_attribution_errors_not_preserved" in report.blockers
    assert "attribution_archive_not_21_correct" in report.blockers


def test_no_alarm_a_genuinely_bound_preflight_reaches_ready_without_promoting() -> None:
    report = assess_fresh_transfer_campaign_preflight(_bound_binding())
    assert report.status is FreshTransferCampaignStatus.READY_TO_EXECUTE
    assert report.blockers == ()
    assert report.campaign_execution == "HOST_RUNBOOK_ONLY"
    assert report.empirical_authority == "CANNOT_CHECK"
    assert report.recommends_host_promotion is False
    handed = refuse_unbound_execution(_bound_binding())
    assert handed.status is FreshTransferCampaignStatus.READY_TO_EXECUTE
    assert handed.recommends_host_promotion is False


def test_checkbox_audit_ticks_only_verified_items_and_preserves_cannot_check() -> None:
    audit = audit_issue_159_checkboxes(repo_root=REPO, environ={})
    ticked = [item for item in audit["checkboxes"] if item["ticked"]]
    assert ticked
    assert all(item["verified_on_main"] for item in ticked)
    ids = {item["id"]: item for item in audit["checkboxes"]}
    assert ids["evidence.glm52_attribution_21_of_24"]["ticked"] is True
    assert ids["evidence.result_bearing_fresh_transfer_campaign"]["ticked"] is False
    assert ids["execution.issue8_live_trial"]["ticked"] is False
    assert ids["execution.issue76_development_cycle"]["ticked"] is False
    assert ids["authority.host_promotion_recommendation"]["ticked"] is False
    assert audit["empirical_authority"] == "CANNOT_CHECK"
    assert audit["recommends_host_promotion"] is False
    assert audit["dependencies"]["8"]["status"] == "CANNOT_CHECK"
    assert audit["dependencies"]["8"]["packet_bound"] is False
    assert audit["dependencies"]["76"]["status"] == "CANNOT_CHECK"
    assert audit["dependencies"]["277"]["fail_closed_on_main"] is (
        inspect_phase2_preflight_fail_closed()
    )
    assert audit["attribution"]["correct"] == 21
    assert audit["attribution"]["total"] == 24


def test_committed_checkbox_audit_matches_the_live_auditor() -> None:
    audit_path = REPO / "papers/orion-15-self-orion/evidence/ISSUE_159_CHECKBOX_AUDIT_V1.json"
    committed = json.loads(audit_path.read_text(encoding="utf-8"))
    live = audit_issue_159_checkboxes(repo_root=REPO, environ={})
    assert committed["schema_version"] == live["schema_version"]
    assert committed["attribution"]["correct"] == 21
    assert committed["attribution"]["total"] == 24
    assert committed["campaign"]["campaign_execution"] == "REFUSED_UNBOUND"
    assert committed["recommends_host_promotion"] is False
    assert committed["checkboxes"] == live["checkboxes"]


def test_cli_refuses_unbound_repository_and_does_not_print_secrets(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in REQUIRED_CREDENTIAL_ENV_VARS:
        monkeypatch.setenv(name, SECRET)
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert SECRET not in captured.out
    assert SECRET not in captured.err
    payload = json.loads(captured.out)
    assert payload["preflight"]["status"] != "READY_TO_EXECUTE"
    assert payload["preflight"]["recommends_host_promotion"] is False
    assert payload["audit"]["attribution"]["errors"][0]["case_id"] == "P5-HC-002"
