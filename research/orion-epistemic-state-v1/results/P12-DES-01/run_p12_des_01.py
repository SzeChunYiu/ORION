#!/usr/bin/env python3
"""Fail-closed P12-DES-01 packet generator.

The frozen execution needs the protected ScienceAgentBench payload and a
separately frozen non-FLAT successor.  Public annotations and model-file
presence cannot replace protected task outcomes.  When either hard
precondition is absent, this runner preserves every clean-license case as an
explicit CANNOT_CHECK row and consumes no cluster allocation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
FREEZE_PATH = HERE / "FREEZE_V1.json"
PREFLIGHT_PATH = HERE / "LUNARC_PREFLIGHT_V1.json"
PLAN_PATH = REPO_ROOT / "papers/paper-12-adaptive-state-reasoning/runtime/P12_CAMPAIGN_PLAN_V1.json"

TERMINAL = "CANNOT_CHECK_PROTECTED_SUBSTRATE_AND_NONFLAT_SUCCESSOR_NOT_RUN"
NONFLAT_TERMINAL = "CANNOT_CHECK_NONFLAT_SUCCESSOR_NOT_FRESHLY_FROZEN"
ENDPOINTS = (
    "task_gain",
    "regret",
    "cost",
    "domain_stability",
    "censoring",
    "action_diversity",
    "signal_contribution",
)
COMPONENTS = (
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
)
EXPECTED_OUTPUTS = (
    "RAW_MANIFEST_V1.json",
    *COMPONENTS,
    "RESULT_BINDING_PACKET_V1.json",
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def committed_freeze_revision() -> str:
    relative = FREEZE_PATH.relative_to(REPO_ROOT)
    revision = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", str(relative)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    if not revision:
        raise RuntimeError("FREEZE_V1.json is not committed")
    return revision


def validate_freeze(freeze: dict[str, Any]) -> None:
    if freeze["job_id"] != "P12-DES-01":
        raise ValueError("wrong job freeze")
    if freeze["git"]["subject_sha"] != "3c97b87f4f4c8c0365226019236c83d3c4c7bb37":
        raise ValueError("wrong frozen subject")
    flat = freeze["current_flat_stopgo"]
    if flat["clean_license_case_denominator"] != 96:
        raise ValueError("clean-license denominator drift")
    if flat["task_family_denominator"] != 24 or flat["domain_denominator"] != 4:
        raise ValueError("family/domain denominator drift")
    if flat["run_cell_denominator"] != "CANNOT_CHECK_NOT_INFERRED_FROM_AVAILABLE_MODEL_FAMILIES":
        raise ValueError("run-cell state drift")
    if freeze["nonflat_successor"]["terminal"] != NONFLAT_TERMINAL:
        raise ValueError("non-FLAT terminal drift")
    if freeze["terminal_precedence"][0] != TERMINAL:
        raise ValueError("terminal precedence drift")


def validate_source_bindings(freeze: dict[str, Any]) -> None:
    for binding in freeze["source_bindings"]:
        path = REPO_ROOT / binding["path"]
        if not path.is_file() or sha256_file(path) != binding["sha256"]:
            raise RuntimeError(f"source binding drift: {binding['path']}")


def validate_preflight(preflight: dict[str, Any]) -> None:
    sab = preflight["scienceagentbench"]
    archive = sab["official_archive"]
    expected = {
        "bytes": 1_769_478_786,
        "sha256": "46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610",
        "state": "ENCRYPTED_PROTECTED_ARCHIVE",
        "all_entries_encrypted": True,
    }
    for key, value in expected.items():
        if archive.get(key) != value:
            raise ValueError(f"preflight archive {key} drift")
    if sab["official_evaluation_runnable"] is not False:
        raise ValueError("protected evaluation unexpectedly runnable")
    if preflight["protected_outcome_accessed"] is not False:
        raise ValueError("preflight accessed protected outcome")
    if preflight["slurm_job_submitted"] is not False:
        raise ValueError("preflight claims a submitted job")
    if any(sab["archive_password_environment_presence"].values()):
        raise ValueError("password custody changed; freeze a password-bound executor before access")
    for component in sab["cleartext_components"].values():
        if component["files"] != 0 or component["bytes"] != 0:
            raise ValueError("cleartext protected component changed; freeze a new executor before access")


def planned_case_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in plan["plan"]:
        rows.append(
            {
                "instance_id": str(item["instance_id"]),
                "domain": item["domain"],
                "task_family": item["family"],
                "planned_signals": item["signals"],
                "planned_actions": item["actions"],
                "status": "CANNOT_CHECK",
                "reason": "PROTECTED_DATASETS_EVALUATORS_GOLD_AND_SCORERS_UNAVAILABLE",
                "eligible_for_stopgo_inference": False,
                "task_outcome": None,
                "task_gain": None,
                "regret": None,
                "cost": None,
                "censored": None,
            }
        )
    if len(rows) != 96 or len({row["instance_id"] for row in rows}) != 96:
        raise ValueError("case denominator or identity drift")
    if {row["instance_id"] for row in rows} & {"3", "32", "46", "53", "54", "84"}:
        raise ValueError("license-excluded instance entered clean denominator")
    if len({row["task_family"] for row in rows}) != 24:
        raise ValueError("task-family denominator drift")
    return rows


def counts(rows: list[dict[str, Any]], freeze: dict[str, Any]) -> dict[str, Any]:
    domains = freeze["current_flat_stopgo"]["domain_case_counts"]
    actual_domains = {domain: sum(row["domain"] == domain for row in rows) for domain in domains}
    if actual_domains != domains:
        raise ValueError("domain case-count drift")
    return {
        "official_instances": 102,
        "license_excluded_cases": 6,
        "clean_license_cases_planned": 96,
        "clean_license_cases_executed": 0,
        "clean_license_cases_cannot_check": 96,
        "task_families": 24,
        "domains": 4,
        "domain_case_counts": actual_domains,
        "frozen_flat_arms": 3,
        "available_model_artifacts_observed": 4,
        "exact_model_execution_denominator": "CANNOT_CHECK_NOT_FROZEN",
        "stochastic_repeat_denominator": "CANNOT_CHECK_NOT_FROZEN",
        "planned_run_cell_denominator": "CANNOT_CHECK_NOT_FROZEN",
        "run_cells_executed": 0,
        "task_outcomes_observed": 0,
        "rows_dropped": 0,
        "slurm_jobs_submitted": 0,
    }


def hard_preconditions(preflight: dict[str, Any]) -> dict[str, Any]:
    archive = preflight["scienceagentbench"]["official_archive"]
    return {
        "HP1_OFFICIAL_ARCHIVE_CLEAR_AND_HASH_BOUND": {
            "attained": False,
            "detail": "archive hash and bytes bound, but all 845 entries remain encrypted",
            "archive_sha256": archive["sha256"],
        },
        "HP2_DATASETS_EVALUATORS_GOLD_AND_SCORERS_RUNNABLE": {"attained": False},
        "HP3_96_CASES_RETAIN_PROTECTED_OUTCOME_CUSTODY": {"attained": False},
        "HP4_EXACT_MODEL_AND_RUN_CELL_MANIFEST_FROZEN": {"attained": False},
        "HP5_ALL_SUCCESSOR_COMPARATORS_FROZEN_AND_RUNNABLE": {"attained": False},
        "HP6_MATCHED_ACTION_SIGNAL_INFORMATION_AND_VECTOR_RESOURCES": {"attained": False},
        "HP7_POSITIVE_AND_VIOLATING_STRATA_FOR_EVERY_HARD_CONDITION": {"attained": False},
        "HP8_LABEL_FILENAME_TEMPLATE_MODEL_AND_CROSS_ARM_LEAKAGE_PROBES_PASS": {"attained": False},
        "HP9_FRESH_NONFLAT_MULTI_MODEL_DOMAIN_SUCCESSOR_FROZEN": {"attained": False},
        "HP10_NONFLAT_PRICE_AND_SHIFT_TRANSFER_EXECUTED_WITHOUT_CENSORING": {"attained": False},
        "all_attained": False,
    }


def run() -> str:
    freeze = load_json(FREEZE_PATH)
    preflight = load_json(PREFLIGHT_PATH)
    plan = load_json(PLAN_PATH)
    validate_freeze(freeze)
    validate_source_bindings(freeze)
    validate_preflight(preflight)

    execution_head = git_head()
    freeze_commit = committed_freeze_revision()
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", freeze_commit, execution_head],
        cwd=REPO_ROOT,
    ).returncode:
        raise RuntimeError("freeze commit is not an ancestor of execution head")

    rows = planned_case_rows(plan)
    denominators = counts(rows, freeze)
    preconditions = hard_preconditions(preflight)
    endpoint_results = {
        endpoint: {
            "state": "CANNOT_CHECK",
            "estimate": None,
            "reason": TERMINAL,
        }
        for endpoint in ENDPOINTS
    }

    raw = {
        "schema": "orion.p12-des-01.raw-manifest.v1",
        "job_id": "P12-DES-01",
        "subject_revision": freeze["git"]["subject_sha"],
        "execution_head": execution_head,
        "freeze_commit": freeze_commit,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "lunarc_preflight_sha256": sha256_file(PREFLIGHT_PATH),
        "campaign_plan_sha256": sha256_file(PLAN_PATH),
        "case_outcomes": rows,
        "denominators": denominators,
        "protected_outcome_accessed": False,
        "public_metadata_used_for_task_outcomes": False,
        "slurm_job_submitted": False,
        "slurm_job_not_submitted_reason": "protected evaluation is not runnable; placeholder jobs are forbidden",
    }
    write_json(HERE / "RAW_MANIFEST_V1.json", raw)

    primary = {
        "schema": "orion.p12-des-01.primary-result.v1",
        "job_id": "P12-DES-01",
        "exact_terminal": TERMINAL,
        "flat_stopgo_terminal": "CANNOT_CHECK_PROTECTED_SUBSTRATE_NOT_RUN",
        "nonflat_successor_terminal": NONFLAT_TERMINAL,
        "denominators": denominators,
        "endpoint_results": endpoint_results,
        "stopgo_gate_evaluable": False,
        "stopgo_gate_passed": False,
        "positive_terminal_attained": False,
        "negative_or_harmful_rows": 0,
        "null_rows": 0,
        "crashed_rows": 0,
        "censored_rows": 0,
        "cannot_check_rows": 96,
        "rows_dropped": 0,
        "claim_ceiling": freeze["authority_ceiling"],
    }
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)

    donor = {
        "schema": "orion.p12-des-01.ideal-donor-result.v1",
        "job_id": "P12-DES-01",
        "strongest_one_signal_arm": {
            "state": "CANNOT_CHECK_FROZEN_TUNING_SPLIT_OUTCOME_UNAVAILABLE",
            "selected_arm": None,
        },
        "required_successor_comparators": {
            name: {"frozen_for_p12_des_01": False, "executed": False, "result": None}
            for name in ("FIXED_BALANCED", "BEST_FIXED", "ORACLE", "IDEAL_VALUE_OF_INFORMATION_PRODUCT")
        },
        "ideal_donor_state": "NOT_RUN",
        "weak_proxy_substituted": False,
        "historical_price_aware_successor_reused": False,
        "historical_exclusion_reason": freeze["nonflat_successor"]["historical_protocol_not_reused"],
        "resource_matching_evaluable": False,
    }
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", donor)

    controls = {
        "schema": "orion.p12-des-01.negative-controls.v1",
        "job_id": "P12-DES-01",
        "license_excluded_instance_ids": [3, 32, 46, 53, 54, 84],
        "license_exclusions_respected": True,
        "all_clean_license_cases_retained": True,
        "metadata_parseability_substituted_for_task_outcomes": False,
        "model_file_presence_substituted_for_model_execution": False,
        "historical_nonflat_result_substituted": False,
        "post_outcome_retuning": False,
        "leakage_probes": {
            "label": "NOT_RUN_PROTECTED_INPUTS_UNAVAILABLE",
            "filename": "NOT_RUN_PROTECTED_INPUTS_UNAVAILABLE",
            "template": "NOT_RUN_PROTECTED_INPUTS_UNAVAILABLE",
            "model": "NOT_RUN_PROTECTED_INPUTS_UNAVAILABLE",
            "cross_arm": "NOT_RUN_PROTECTED_INPUTS_UNAVAILABLE",
        },
        "resource_cap_hit": False,
        "missing_custody_treated_as_censoring": False,
        "rows_dropped": 0,
    }
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", controls)

    resources = {
        "schema": "orion.p12-des-01.resource-ledger.v1",
        "job_id": "P12-DES-01",
        "planned_run_cell_denominator": "CANNOT_CHECK_NOT_FROZEN",
        "run_cells_executed": 0,
        "model_calls": 0,
        "scorer_calls": 0,
        "tool_calls": 0,
        "gpu_hours": 0,
        "cpu_hours": 0,
        "slurm_jobs_submitted": 0,
        "slurm_job_not_submitted_reason": "protected evaluation is not runnable; placeholder jobs are forbidden",
        "model_artifact_inventory": preflight["model_artifact_inventory"],
        "protected_outcome_access": False,
        "censoring": {
            "resource_cap_hit": False,
            "timeout_hit": False,
            "missing_password_or_custody_is_cannot_check_not_censoring": True,
            "future_cap_hits_must_be_retained_as_censored": True,
        },
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)

    transfer = {
        "schema": "orion.p12-des-01.transfer-result.v1",
        "job_id": "P12-DES-01",
        "current_flat_stopgo": {"state": "CANNOT_CHECK", "executed_cases": 0},
        "nonflat_multi_model_domain_successor": {
            "state": "CANNOT_CHECK",
            "terminal": NONFLAT_TERMINAL,
            "fresh_identity_frozen": False,
            "price_regimes_executed": 0,
            "distribution_shifts_executed": 0,
        },
        "cross_model_generalization_evaluable": False,
        "domain_shift_robustness_evaluable": False,
        "authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)

    components = {name: sha256_file(HERE / name) for name in COMPONENTS}
    binding = {
        "schema": "orion.p12-des-01.result-binding-packet.v1",
        "job_id": "P12-DES-01",
        "base_main": freeze["git"]["fresh_origin_main_sha"],
        "subject_revision": freeze["git"]["subject_sha"],
        "freeze_commit": freeze_commit,
        "execution_head": execution_head,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "lunarc_preflight_sha256": sha256_file(PREFLIGHT_PATH),
        "raw_manifest_sha256": sha256_file(HERE / "RAW_MANIFEST_V1.json"),
        "component_sha256": components,
        "case_outcomes": rows,
        "denominators": denominators,
        "endpoint_results": endpoint_results,
        "hard_preconditions": preconditions,
        "leakage_and_proxy_boundary": controls,
        "censoring": resources["censoring"],
        "exact_terminal": TERMINAL,
        "nonflat_successor_terminal": NONFLAT_TERMINAL,
        "positive_terminal_attained": False,
        "external_authority_state": "CANNOT_CHECK",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "computation_session_paper_authority_delta": "NONE",
    }
    write_json(HERE / "RESULT_BINDING_PACKET_V1.json", binding)
    return TERMINAL


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    print(run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
