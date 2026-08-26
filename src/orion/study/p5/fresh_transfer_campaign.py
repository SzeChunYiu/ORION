"""Fail-closed preflight for the P5 hidden-cause fresh-transfer campaign.

This module never launches providers, never prints credential values, and never
recommends host promotion.  A READY status means a host may follow the frozen
runbook; it is not empirical credit and is not a Self-ORION terminal.

Live execution is refused unless all of the following hold on the inspected
tree:

* Phase-2 preflight is fail-closed (the #277 P0 probe must not reach READY);
* the published #8 packet task identities are the ones the in-source registry
  would execute;
* required credential *names* are present in the environment (values are never
  copied into reports);
* the merged GLM-5.2 attribution archive is 21/24 with the three immutable
  errors preserved.

On current ``origin/main`` those bindings are absent, so the only admissible
campaign status is ``CANNOT_CHECK``.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "orion.p5.fresh-transfer-campaign-preflight.v1"
RUNBOOK_PATH = (
    "papers/orion-15-self-orion/protocol/FRESH_TRANSFER_CAMPAIGN_RUNBOOK_V1.md"
)
ATTRIBUTION_RESULTS_PATH = (
    "papers/orion-15-self-orion/evidence/glm-5.2-attribution/results.jsonl"
)
ATTRIBUTION_REPORT_PATH = (
    "papers/orion-15-self-orion/evidence/glm-5.2-attribution/report.json"
)
PUBLISHED_PACKET_PATH = "papers/orion-15-self-orion/protocol/LIVE_TRIAL_PACKET_V1.json"
CHECKBOX_AUDIT_PATH = (
    "papers/orion-15-self-orion/evidence/ISSUE_159_CHECKBOX_AUDIT_V1.json"
)

FROZEN_ISSUE8_WIDE_TASK_ID = "P5.LIVE.WIDE.stopping-rule-source-families"
FROZEN_ISSUE8_DEEP_TASK_ID = "P5.LIVE.DEEP.flat-round-without-lineage"
FROZEN_ATTRIBUTION_MODEL = "glm-5.2"
FROZEN_ATTRIBUTION_TOTAL = 24
FROZEN_ATTRIBUTION_CORRECT = 21

REQUIRED_CREDENTIAL_ENV_VARS = (
    "OPENAI_API_KEY",
    "ORION_PROTECTED_VERIFIER_URL",
    "ORION_PROTECTED_VERIFIER_TOKEN",
    "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
    "ORION_PHASE2_EVALUATION_EPOCH_ID",
)

IMMUTABLE_ATTRIBUTION_ERRORS: tuple[tuple[str, str, str], ...] = (
    ("P5-HC-002", "RETRIEVAL_MISS", "REPRESENTATION_GAP"),
    ("P5-HC-012", "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE", "IMPLEMENTATION_BUG"),
    ("P5-HC-018", "REPRESENTATION_GAP", "METHOD_BASIS_GAP"),
)

EIGHT_HIDDEN_CAUSE_FAMILIES = frozenset(
    {
        "RETRIEVAL_MISS",
        "ROUTING_PLANNING_MISS",
        "IMPLEMENTATION_BUG",
        "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
        "EVALUATOR_METRIC_BUG",
        "REPRESENTATION_GAP",
        "MEASUREMENT_SPECIFICATION_GAP",
        "METHOD_BASIS_GAP",
    }
)

_P0_SUBJECT = "a" * 64
_P0_PROVIDER = "b" * 64
_P0_EVALUATOR = "c" * 64


class FreshTransferCampaignStatus(str, Enum):
    BIND_FAIL_CLOSED_PREFLIGHT = "BIND_FAIL_CLOSED_PREFLIGHT"
    BIND_ISSUE8_PACKET = "BIND_ISSUE8_PACKET"
    BIND_CREDENTIALS = "BIND_CREDENTIALS"
    BIND_ATTRIBUTION_ARCHIVE = "BIND_ATTRIBUTION_ARCHIVE"
    READY_TO_EXECUTE = "READY_TO_EXECUTE"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class AttributionError:
    case_id: str
    gold: str
    attributed: str

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.case_id, self.gold, self.attributed)


@dataclass(frozen=True)
class AttributionArchive:
    model: str
    total_cases: int
    correct: int
    incorrect: int
    errors: tuple[AttributionError, ...]
    results_path: str
    report_path: str

    @property
    def accuracy(self) -> float:
        return self.correct / self.total_cases if self.total_cases else 0.0


@dataclass(frozen=True)
class FreshTransferCampaignBinding:
    """Declared facts the gate compares. Credential *values* are never stored."""

    phase2_preflight_fail_closed: bool
    in_source_wide_task_id: str
    in_source_deep_task_id: str
    frozen_wide_task_id: str
    frozen_deep_task_id: str
    present_credential_env_vars: tuple[str, ...]
    attribution: AttributionArchive | None
    missing_credential_env_vars: tuple[str, ...] = ()


@dataclass(frozen=True)
class FreshTransferCampaignReport:
    schema_version: str
    status: FreshTransferCampaignStatus
    blockers: tuple[str, ...]
    empirical_authority: str
    campaign_execution: str
    issue8_packet_bound: bool
    phase2_preflight_fail_closed: bool
    attribution_verified: bool
    missing_credential_env_vars: tuple[str, ...]
    runbook: str

    @property
    def recommends_host_promotion(self) -> bool:
        return False

    @property
    def grants_phase2_closure(self) -> bool:
        return False

    @property
    def grants_p5_peer_review_ready(self) -> bool:
        return False

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status.value,
            "blockers": list(self.blockers),
            "empirical_authority": self.empirical_authority,
            "campaign_execution": self.campaign_execution,
            "issue8_packet_bound": self.issue8_packet_bound,
            "phase2_preflight_fail_closed": self.phase2_preflight_fail_closed,
            "attribution_verified": self.attribution_verified,
            "missing_credential_env_vars": list(self.missing_credential_env_vars),
            "runbook": self.runbook,
            "recommends_host_promotion": self.recommends_host_promotion,
            "grants_phase2_closure": self.grants_phase2_closure,
            "grants_p5_peer_review_ready": self.grants_p5_peer_review_ready,
        }


class UnboundFreshTransferCampaign(RuntimeError):
    """Raised when a campaign launch is attempted without a bound preflight."""

    def __init__(self, report: FreshTransferCampaignReport) -> None:
        self.report = report
        super().__init__(
            "refusing unbound fresh-transfer campaign: " + ",".join(report.blockers)
        )


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_attribution_archive(repo_root: Path | None = None) -> AttributionArchive:
    """Recompute 21/24 from raw records and require the three immutable errors."""

    root = repo_root or default_repo_root()
    results_path = root / ATTRIBUTION_RESULTS_PATH
    report_path = root / ATTRIBUTION_REPORT_PATH
    if not results_path.is_file() or not report_path.is_file():
        raise FileNotFoundError("glm-5.2 attribution archive is missing")

    records: list[dict[str, Any]] = []
    for line in results_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        if not isinstance(raw, dict):
            raise ValueError("attribution results.jsonl records must be objects")
        records.append(raw)

    errors: list[AttributionError] = []
    correct = 0
    for record in records:
        case_id = str(record["case_id"])
        gold = str(record["gold_root_cause"])
        attributed = str(record["attributed_root_cause"])
        is_correct = gold == attributed
        if bool(record.get("correct")) is not is_correct:
            raise ValueError(f"{case_id} correct flag disagrees with gold/attributed")
        if record.get("error") not in (None, "", False):
            raise ValueError(f"{case_id} must remain a non-error attribution record")
        if is_correct:
            correct += 1
        else:
            errors.append(AttributionError(case_id, gold, attributed))

    report = _load_json(report_path)
    if not isinstance(report, dict):
        raise ValueError("attribution report.json must be an object")
    metrics = report.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("attribution report.json metrics must be an object")

    archive = AttributionArchive(
        model=str(report.get("model", "")),
        total_cases=len(records),
        correct=correct,
        incorrect=len(errors),
        errors=tuple(errors),
        results_path=ATTRIBUTION_RESULTS_PATH,
        report_path=ATTRIBUTION_REPORT_PATH,
    )
    if archive.model != FROZEN_ATTRIBUTION_MODEL:
        raise ValueError("attribution archive model must remain glm-5.2")
    if archive.total_cases != FROZEN_ATTRIBUTION_TOTAL:
        raise ValueError("attribution archive must contain exactly 24 cases")
    if archive.correct != FROZEN_ATTRIBUTION_CORRECT:
        raise ValueError("attribution archive must remain 21/24; do not launder 24/24")
    if int(metrics.get("correct_attributions", -1)) != FROZEN_ATTRIBUTION_CORRECT:
        raise ValueError("report.json correct_attributions disagrees with raw records")
    if int(metrics.get("incorrect_attributions", -1)) != 3:
        raise ValueError("report.json incorrect_attributions disagrees with raw records")
    observed = tuple(error.as_tuple() for error in archive.errors)
    if observed != IMMUTABLE_ATTRIBUTION_ERRORS:
        raise ValueError("immutable attribution errors were not preserved")
    return archive


def inspect_phase2_preflight_fail_closed() -> bool:
    """True only if the #277 P0 probe no longer certifies READY.

    Three well-formed hex strings with no frozen packet must not reach
    ``READY_TO_EXECUTE_SHADOW_TRIAL``.  Shape-only hashing is fail-open.
    """

    from orion.self_orion.phase2_preflight import (
        Phase2ClosurePreflight,
        Phase2PreflightStatus,
        assess_phase2_preflight,
    )

    parameters = inspect.signature(Phase2ClosurePreflight).parameters
    kwargs: dict[str, Any] = {
        "protocol_id": "phase2-shadow-closure-v1",
        "subject_revision_hash": _P0_SUBJECT,
        "provider_manifest_hash": _P0_PROVIDER,
        "evaluator_artifact_hash": _P0_EVALUATOR,
        "evaluation_epoch_id": "phase2:epoch:frozen-before-outcomes",
        "baseline_id": "simple-llm-retrieval-baseline-v1",
        "resource_budget_units": 100.0,
    }
    filtered = {key: value for key, value in kwargs.items() if key in parameters}
    report = assess_phase2_preflight(Phase2ClosurePreflight(**filtered))
    return report.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL


def inspect_issue8_packet_identities(
    repo_root: Path | None = None,
) -> tuple[str, str, str, str]:
    """Return (in-source wide, in-source deep, frozen wide, frozen deep)."""

    from orion.self_orion.live_packet import DEEP_TASK_ID, WIDE_TASK_ID
    from orion.self_orion.phase2_preflight import DEEP_TARGET_TASK, WIDE_LITERATURE_TASK

    root = repo_root or default_repo_root()
    document = _load_json(root / PUBLISHED_PACKET_PATH)
    if not isinstance(document, dict):
        raise ValueError("published #8 packet must be an object")
    published_tasks = document.get("tasks")
    if not isinstance(published_tasks, list):
        raise ValueError("published #8 packet tasks must be an array")
    published_ids = [
        str(task["task_id"])
        for task in published_tasks
        if isinstance(task, dict) and "task_id" in task
    ]
    if WIDE_TASK_ID not in published_ids or DEEP_TASK_ID not in published_ids:
        raise ValueError("published #8 packet does not contain the frozen live tasks")
    if WIDE_TASK_ID != FROZEN_ISSUE8_WIDE_TASK_ID or DEEP_TASK_ID != FROZEN_ISSUE8_DEEP_TASK_ID:
        raise ValueError("live_packet task ids drifted from the frozen #8 identities")
    return (
        WIDE_LITERATURE_TASK.task_id,
        DEEP_TARGET_TASK.task_id,
        FROZEN_ISSUE8_WIDE_TASK_ID,
        FROZEN_ISSUE8_DEEP_TASK_ID,
    )


def inspect_present_credential_env_vars(
    environ: Mapping[str, str] | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (present names, missing names). Values are never returned."""

    source = os.environ if environ is None else environ
    present: list[str] = []
    missing: list[str] = []
    for name in REQUIRED_CREDENTIAL_ENV_VARS:
        value = source.get(name)
        if isinstance(value, str) and value.strip():
            present.append(name)
        else:
            missing.append(name)
    return tuple(present), tuple(missing)


def inspect_repository_campaign_binding(
    *,
    repo_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> FreshTransferCampaignBinding:
    root = repo_root or default_repo_root()
    present, missing = inspect_present_credential_env_vars(environ)
    try:
        attribution = load_attribution_archive(root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        attribution = None
    wide, deep, frozen_wide, frozen_deep = inspect_issue8_packet_identities(root)
    return FreshTransferCampaignBinding(
        phase2_preflight_fail_closed=inspect_phase2_preflight_fail_closed(),
        in_source_wide_task_id=wide,
        in_source_deep_task_id=deep,
        frozen_wide_task_id=frozen_wide,
        frozen_deep_task_id=frozen_deep,
        present_credential_env_vars=present,
        missing_credential_env_vars=missing,
        attribution=attribution,
    )


def _attribution_blockers(archive: AttributionArchive | None) -> list[str]:
    if archive is None:
        return ["attribution_archive_absent_or_unverified"]
    blockers: list[str] = []
    if archive.model != FROZEN_ATTRIBUTION_MODEL:
        blockers.append("attribution_model_not_glm-5.2")
    if archive.total_cases != FROZEN_ATTRIBUTION_TOTAL:
        blockers.append("attribution_archive_not_24_cases")
    if archive.correct != FROZEN_ATTRIBUTION_CORRECT:
        blockers.append("attribution_archive_not_21_correct")
    observed = tuple(error.as_tuple() for error in archive.errors)
    if observed != IMMUTABLE_ATTRIBUTION_ERRORS:
        blockers.append("immutable_attribution_errors_not_preserved")
    return blockers


def assess_fresh_transfer_campaign_preflight(
    binding: FreshTransferCampaignBinding,
) -> FreshTransferCampaignReport:
    """Compare declared facts. Missing evidence is CANNOT_CHECK, not PASS."""

    blockers: list[str] = []
    packet_bound = (
        binding.in_source_wide_task_id == binding.frozen_wide_task_id
        and binding.in_source_deep_task_id == binding.frozen_deep_task_id
        and binding.frozen_wide_task_id == FROZEN_ISSUE8_WIDE_TASK_ID
        and binding.frozen_deep_task_id == FROZEN_ISSUE8_DEEP_TASK_ID
    )
    if not binding.phase2_preflight_fail_closed:
        blockers.append("phase2_preflight_fail_open")
    if not packet_bound:
        blockers.append(
            "issue8_packet_unbound:in_source="
            f"{binding.in_source_wide_task_id},{binding.in_source_deep_task_id}"
            ";frozen="
            f"{binding.frozen_wide_task_id},{binding.frozen_deep_task_id}"
        )
    missing = binding.missing_credential_env_vars
    if missing:
        blockers.append("credentials_absent:" + ",".join(missing))
    attribution_blockers = _attribution_blockers(binding.attribution)
    blockers.extend(attribution_blockers)
    attribution_verified = not attribution_blockers

    if not binding.phase2_preflight_fail_closed:
        status = FreshTransferCampaignStatus.BIND_FAIL_CLOSED_PREFLIGHT
    elif not packet_bound:
        status = FreshTransferCampaignStatus.BIND_ISSUE8_PACKET
    elif missing:
        status = FreshTransferCampaignStatus.BIND_CREDENTIALS
    elif attribution_blockers:
        status = FreshTransferCampaignStatus.BIND_ATTRIBUTION_ARCHIVE
    elif blockers:
        status = FreshTransferCampaignStatus.CANNOT_CHECK
    else:
        status = FreshTransferCampaignStatus.READY_TO_EXECUTE

    execution = (
        "HOST_RUNBOOK_ONLY"
        if status is FreshTransferCampaignStatus.READY_TO_EXECUTE
        else "REFUSED_UNBOUND"
    )
    return FreshTransferCampaignReport(
        schema_version=SCHEMA_VERSION,
        status=status,
        blockers=tuple(blockers),
        empirical_authority="CANNOT_CHECK",
        campaign_execution=execution,
        issue8_packet_bound=packet_bound,
        phase2_preflight_fail_closed=binding.phase2_preflight_fail_closed,
        attribution_verified=attribution_verified,
        missing_credential_env_vars=missing,
        runbook=RUNBOOK_PATH,
    )


def refuse_unbound_execution(
    binding: FreshTransferCampaignBinding | None = None,
    *,
    repo_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> FreshTransferCampaignReport:
    """Raise unless the campaign is fully bound. Never launches providers."""

    observed = binding or inspect_repository_campaign_binding(
        repo_root=repo_root, environ=environ
    )
    report = assess_fresh_transfer_campaign_preflight(observed)
    if report.status is not FreshTransferCampaignStatus.READY_TO_EXECUTE:
        raise UnboundFreshTransferCampaign(report)
    if report.recommends_host_promotion or report.empirical_authority != "CANNOT_CHECK":
        raise RuntimeError("fresh-transfer preflight must not self-certify promotion")
    return report


def _verified_structural_files(repo_root: Path) -> dict[str, bool]:
    required = {
        "table_p5_1": repo_root
        / "papers/orion-15-self-orion/evidence/TABLE_P5_1_NEAREST_WORK.json",
        "protocol_v2": repo_root / "papers/orion-15-self-orion/protocol/PROTOCOL_V2.json",
        "negative_history_chain": repo_root
        / "papers/orion-15-self-orion/protocol/P5_NEGATIVE_HISTORY_CHAIN_V1.json",
        "protected_suite_freeze": repo_root
        / "papers/orion-15-self-orion/protocol/PROTECTED_SUITE_FREEZE_V1.md",
        "published_packet": repo_root / PUBLISHED_PACKET_PATH,
        "attribution_results": repo_root / ATTRIBUTION_RESULTS_PATH,
        "attribution_report": repo_root / ATTRIBUTION_REPORT_PATH,
    }
    return {name: path.is_file() for name, path in required.items()}


def audit_issue_159_checkboxes(
    *,
    repo_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Tick only what is independently verified on the inspected tree."""

    root = repo_root or default_repo_root()
    binding = inspect_repository_campaign_binding(repo_root=root, environ=environ)
    report = assess_fresh_transfer_campaign_preflight(binding)
    files = _verified_structural_files(root)
    attribution_ok = False
    attribution_payload: dict[str, Any] | None = None
    try:
        archive = load_attribution_archive(root)
        attribution_ok = True
        attribution_payload = {
            "model": archive.model,
            "correct": archive.correct,
            "total": archive.total_cases,
            "accuracy": archive.accuracy,
            "errors": [
                {"case_id": error.case_id, "gold": error.gold, "attributed": error.attributed}
                for error in archive.errors
            ],
        }
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        attribution_payload = None

    checkboxes = [
        {
            "id": "precondition.nearest_work_substrate",
            "ticked": files["table_p5_1"],
            "verified_on_main": files["table_p5_1"],
            "evidence": "papers/orion-15-self-orion/evidence/TABLE_P5_1_NEAREST_WORK.json",
        },
        {
            "id": "precondition.staged_acceptance_v2",
            "ticked": files["protocol_v2"],
            "verified_on_main": files["protocol_v2"],
            "evidence": "papers/orion-15-self-orion/protocol/PROTOCOL_V2.json",
        },
        {
            "id": "precondition.v2_negative_history_chain",
            "ticked": files["negative_history_chain"],
            "verified_on_main": files["negative_history_chain"],
            "evidence": "papers/orion-15-self-orion/protocol/P5_NEGATIVE_HISTORY_CHAIN_V1.json",
        },
        {
            "id": "precondition.protected_suite_freeze_protocol",
            "ticked": files["protected_suite_freeze"],
            "verified_on_main": files["protected_suite_freeze"],
            "evidence": "papers/orion-15-self-orion/protocol/PROTECTED_SUITE_FREEZE_V1.md",
        },
        {
            "id": "precondition.final_campaign_identities_frozen",
            "ticked": False,
            "verified_on_main": False,
            "status": "CANNOT_CHECK",
            "reason": "exact final subject/provider/model/evaluator/split/epoch are not bound",
        },
        {
            "id": "evidence.glm52_attribution_21_of_24",
            "ticked": attribution_ok,
            "verified_on_main": attribution_ok,
            "evidence": ATTRIBUTION_REPORT_PATH,
            "note": "diagnosis archive only; not protected fresh-transfer evidence",
        },
        {
            "id": "evidence.result_bearing_fresh_transfer_campaign",
            "ticked": False,
            "verified_on_main": False,
            "status": "CANNOT_CHECK",
            "reason": report.campaign_execution,
        },
        {
            "id": "execution.issue8_live_trial",
            "ticked": False,
            "verified_on_main": False,
            "status": "CANNOT_CHECK",
            "reason": "issue #8 remains OPEN and the frozen packet is not bound",
        },
        {
            "id": "execution.issue76_development_cycle",
            "ticked": False,
            "verified_on_main": False,
            "status": "CANNOT_CHECK",
            "reason": "issue #76 remains OPEN and is blocked on #8",
        },
        {
            "id": "metrics.protected_fresh_transfer",
            "ticked": False,
            "verified_on_main": False,
            "status": "CANNOT_CHECK",
        },
        {
            "id": "figures.p5_2_through_p5_7",
            "ticked": False,
            "verified_on_main": False,
            "status": "CANNOT_CHECK",
        },
        {
            "id": "authority.host_promotion_recommendation",
            "ticked": False,
            "verified_on_main": False,
            "status": "CANNOT_CHECK",
            "reason": "preflight must not self-certify promotion",
        },
    ]
    illegally_ticked = [
        item["id"] for item in checkboxes if item["ticked"] and not item["verified_on_main"]
    ]
    if illegally_ticked:
        raise RuntimeError("checkbox audit attempted to tick unverified items")
    return {
        "schema_version": "orion.p5.issue-159-checkbox-audit.v1",
        "issue": 159,
        "empirical_authority": "CANNOT_CHECK",
        "recommends_host_promotion": False,
        "campaign": report.to_json_dict(),
        "attribution": attribution_payload,
        "dependencies": {
            "8": {
                "state": "OPEN",
                "packet_bound": report.issue8_packet_bound,
                "status": "CANNOT_CHECK",
            },
            "76": {
                "state": "OPEN",
                "status": "CANNOT_CHECK",
                "blocked_on": [8],
            },
            "277": {
                "state": "OPEN",
                "fail_closed_on_main": report.phase2_preflight_fail_closed,
                "fail_closed_pr": 289,
                "packet_still_unbound": not report.issue8_packet_bound,
                "status": "CANNOT_CHECK",
            },
        },
        "remaining_cannot_check": [
            item["id"] for item in checkboxes if item.get("status") == "CANNOT_CHECK"
        ],
        "checkboxes": checkboxes,
        "eight_hidden_cause_families": sorted(EIGHT_HIDDEN_CAUSE_FAMILIES),
        "runbook": RUNBOOK_PATH,
    }


def write_checkbox_audit(path: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    audit = audit_issue_159_checkboxes(repo_root=repo_root)
    path.write_text(_canonical_json(audit).decode("utf-8") + "\n", encoding="utf-8")
    return audit


def _scrub_secrets(text: str, environ: Mapping[str, str]) -> None:
    for name in REQUIRED_CREDENTIAL_ENV_VARS:
        value = environ.get(name, "")
        if value and value in text:
            raise RuntimeError(f"refusing to emit credential material from {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="P5 fresh-transfer campaign preflight (never launches providers)."
    )
    parser.add_argument("--repo", type=Path, default=None)
    parser.add_argument("--write-audit", type=Path, default=None)
    args = parser.parse_args(argv)
    repo_root = args.repo
    binding = inspect_repository_campaign_binding(repo_root=repo_root)
    report = assess_fresh_transfer_campaign_preflight(binding)
    payload: dict[str, Any] = {"preflight": report.to_json_dict()}
    if args.write_audit is not None:
        payload["audit"] = write_checkbox_audit(args.write_audit, repo_root=repo_root)
    else:
        payload["audit"] = audit_issue_159_checkboxes(repo_root=repo_root)
    encoded = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    _scrub_secrets(encoded, os.environ)
    sys.stdout.write(encoded)
    if report.status is FreshTransferCampaignStatus.READY_TO_EXECUTE:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
