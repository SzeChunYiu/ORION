#!/usr/bin/env python3
"""Fail-closed executor for the frozen P5-DES-01 protected study.

SWE-bench Verified is public development material, not hidden transfer.  The
published 96-case P5 lineage and authored hidden-cause fixtures are also not
eligible protected inputs.  Unless the exact public-rights, fresh-issue,
comparator, evaluator, threshold, candidate-isolation, and external-adoption
transfers are present, this executor emits denominator-complete CANNOT_CHECK
rows and performs no model or GPU work.
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

REQUIRED_TRANSFER_FILES = {
    "swe_bench_verified": "SWE_BENCH_VERIFIED_TRANSFER_V1.json",
    "fresh_held_issues": "FRESH_HELD_ISSUES_TRANSFER_V1.json",
    "arm_implementations": "ARM_IMPLEMENTATIONS_TRANSFER_V1.json",
    "protected_evaluator": "PROTECTED_EVALUATOR_TRANSFER_V1.json",
    "threshold_freeze": "THRESHOLD_FREEZE_TRANSFER_V1.json",
    "external_adoption": "EXTERNAL_ADOPTION_CUSTODY_TRANSFER_V1.json",
    "candidate_isolation": "CANDIDATE_CUSTODY_ISOLATION_TRANSFER_V1.json",
    "rights_and_eligibility": "RIGHTS_AND_ELIGIBILITY_TRANSFER_V1.json",
}

EXPECTED_OUTPUTS = (
    "RAW_MANIFEST_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
    "P5_PROTECTED_ADOPTION_RESULT_V1.json",
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


def planned_case_rows() -> list[dict[str, Any]]:
    freeze = load_json(FREEZE_PATH)
    rows: list[dict[str, Any]] = []
    rows.extend(
        {
            "case_id": f"swebench-verified:row-{index:06d}",
            "cohort": "swe_bench_verified_public_500",
            "status": "CANNOT_CHECK",
            "reason": "SWE_BENCH_RIGHTS_EVALUATOR_OR_PAYLOAD_NOT_TRANSFERRED",
            "eligible_for_primary": False,
            "outcome": None,
        }
        for index in range(1, 501)
    )
    for wave in ("primary", "replication"):
        for domain in freeze["study"]["fresh_design"]["domains"]:
            for revision_class in freeze["study"]["fresh_design"]["revision_classes"]:
                for index in range(1, 13):
                    rows.append(
                        {
                            "case_id": (
                                f"fresh-held:{wave}:{domain}:{revision_class}:{index:02d}"
                            ),
                            "cohort": f"fresh_powered_{wave}_768",
                            "status": "CANNOT_CHECK",
                            "reason": "PROTECTED_FRESH_ISSUE_CUSTODY_NOT_TRANSFERRED",
                            "eligible_for_primary": False,
                            "outcome": None,
                        }
                    )
        rows.extend(
            {
                "case_id": f"fresh-held:{wave}:no-revision-sentinel:{index:03d}",
                "cohort": f"fresh_sentinel_{wave}_96",
                "status": "CANNOT_CHECK",
                "reason": "PROTECTED_FRESH_SENTINEL_CUSTODY_NOT_TRANSFERRED",
                "eligible_for_primary": False,
                "outcome": None,
            }
            for index in range(1, 97)
        )
    if len(rows) != 2228 or len({row["case_id"] for row in rows}) != 2228:
        raise ValueError("planned P5 case denominator or identity drift")
    return rows


def case_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    cohorts = {
        "swe_bench_verified_public_cases": "swe_bench_verified_public_500",
        "fresh_powered_primary_cases": "fresh_powered_primary_768",
        "fresh_powered_replication_cases": "fresh_powered_replication_768",
        "fresh_sentinel_primary_cases": "fresh_sentinel_primary_96",
        "fresh_sentinel_replication_cases": "fresh_sentinel_replication_96",
    }
    return {
        label: sum(row["cohort"] == cohort for row in rows)
        for label, cohort in cohorts.items()
    }


def transfer_state(transfer_dir: Path | None) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for name, filename in REQUIRED_TRANSFER_FILES.items():
        path = transfer_dir / filename if transfer_dir else None
        present = bool(path and path.is_file())
        state[name] = {
            "required_file": filename,
            "present": present,
            "sha256": sha256_file(path) if present and path is not None else None,
        }
    return state


def validate_freeze(freeze: dict[str, Any]) -> None:
    if freeze["job_id"] != "P5-DES-01":
        raise ValueError("wrong job freeze")
    if freeze["subject_revision"] != "3c97b87f4f4c8c0365226019236c83d3c4c7bb37":
        raise ValueError("wrong frozen subject")
    if freeze["study"]["case_denominator"] != 2228:
        raise ValueError("case denominator drift")
    if len(freeze["study"]["arms"]) != 8:
        raise ValueError("arm denominator drift")
    if freeze["study"]["seeds"] != [5005, 5006, 5007]:
        raise ValueError("seed drift")
    expected_cells = 2228 * 8 * 3
    if freeze["study"]["planned_run_cell_denominator"] != expected_cells:
        raise ValueError("run-cell denominator drift")
    if freeze["decision_rule"]["scalarization"] != "FORBIDDEN":
        raise ValueError("compensatory scalarization is forbidden")
    if freeze["exclusions"]["existing_96_case_lineage"] != (
        "DIAGNOSTIC_ONLY_NO_TERMINAL_NOT_ELIGIBLE_FOR_P5_DES_01"
    ):
        raise ValueError("historical 96-case lineage must remain excluded")


def validate_frozen_files(freeze: dict[str, Any]) -> None:
    for binding in freeze["source_bindings"].values():
        path = REPO_ROOT / binding["path"]
        if not path.is_file() or sha256_file(path) != binding["sha256"]:
            raise RuntimeError(f"source binding drift: {binding['path']}")
    for key in ("runner", "test"):
        binding = freeze["implementation"][key]
        path = REPO_ROOT / binding["path"]
        if not path.is_file() or sha256_file(path) != binding["sha256"]:
            raise RuntimeError(f"implementation binding drift: {binding['path']}")


def run(*, transfer_dir: Path | None, remote_probe: Path | None) -> str:
    freeze = load_json(FREEZE_PATH)
    validate_freeze(freeze)
    validate_frozen_files(freeze)
    execution_head = git_head()
    freeze_commit = committed_freeze_revision()
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", freeze_commit, execution_head],
        cwd=REPO_ROOT,
    )
    if ancestry.returncode != 0:
        raise RuntimeError(f"freeze commit {freeze_commit} is not an ancestor of {execution_head}")

    transfers = transfer_state(transfer_dir)
    all_transfers = all(item["present"] for item in transfers.values())
    if all_transfers:
        raise RuntimeError(
            "all protected transfers present: freeze a transfer-digest-bound executor before access"
        )

    remote = load_json(remote_probe) if remote_probe and remote_probe.is_file() else {
        "state": "NOT_PROBED",
        "reason": "no LUNARC preflight supplied",
        "protected_outcome_accessed": False,
    }
    cases = planned_case_rows()
    cohort_counts = case_counts(cases)
    counts = {
        "case_denominator": len(cases),
        **cohort_counts,
        "fresh_powered_cases": (
            cohort_counts["fresh_powered_primary_cases"]
            + cohort_counts["fresh_powered_replication_cases"]
        ),
        "fresh_sentinel_cases": (
            cohort_counts["fresh_sentinel_primary_cases"]
            + cohort_counts["fresh_sentinel_replication_cases"]
        ),
        "cases_executed": 0,
        "cases_cannot_check": len(cases),
        "arm_denominator": len(freeze["study"]["arms"]),
        "seed_denominator": len(freeze["study"]["seeds"]),
        "planned_run_cell_denominator": freeze["study"]["planned_run_cell_denominator"],
        "run_cells_executed": 0,
    }
    terminal = freeze["terminals"]["cannot_check"]

    raw = {
        "schema": "orion.p5-des.raw-manifest.v1",
        "job_id": "P5-DES-01",
        "subject_revision": freeze["subject_revision"],
        "execution_head": execution_head,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "transfers": transfers,
        "remote_probe": remote,
        "case_outcomes": cases,
        "counts": counts,
        "rows_dropped": 0,
        "protected_outcome_accessed": False,
    }
    write_json(HERE / "RAW_MANIFEST_V1.json", raw)
    raw_digest = sha256_file(HERE / "RAW_MANIFEST_V1.json")

    primary = {
        "schema": "orion.p5-des.primary-result.v1",
        "job_id": "P5-DES-01",
        "exact_terminal": terminal,
        "counts": counts,
        "endpoint_results": {
            endpoint: {
                "state": "CANNOT_CHECK",
                "estimate": None,
                "reason": "zero eligible protected matched run cells",
            }
            for endpoint in freeze["study"]["primary_endpoints"]
        },
        "positive_gate_evaluable": False,
        "positive_gate_passed": False,
        "negative_or_harmful_rows": 0,
        "null_rows": 0,
        "crashed_rows": 0,
        "censored_rows": 0,
        "cannot_check_rows": len(cases),
        "rows_dropped": 0,
        "claim_ceiling": freeze["claim_ceiling"],
    }
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)

    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": "P5-DES-01",
        "strongest_donor": freeze["study"]["strongest_donor"],
        "registered_donor_arms": freeze["study"]["donor_arms"],
        "state": "NOT_RUN",
        "reason": "exact transfer-bound donor adapters and protected matched substrates unavailable",
        "weak_proxy_substituted": False,
        "resource_matching_evaluable": False,
        "donor_absorption_state": "CANNOT_CHECK",
    }
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", donor)

    controls = {
        "schema": "orion.p5-des.negative-controls.v1",
        "job_id": "P5-DES-01",
        "existing_96_case_lineage": "EXCLUDED_NOT_RESEALED_NOT_REUSED",
        "authored_fixture_substitution": False,
        "public_task_substituted_for_hidden_transfer": False,
        "weak_donor_proxy_substituted": False,
        "generator_label_probe": "NOT_RUN_NO_EXTERNAL_FRESH_CASE_MANIFEST",
        "filename_probe": "NOT_RUN_NO_EXTERNAL_FRESH_CASE_MANIFEST",
        "prompt_template_probe": "NOT_RUN_NO_EXTERNAL_FRESH_CASE_MANIFEST",
        "benchmark_solution_retrieval_probe": "NOT_RUN_NO_ELIGIBLE_PUBLIC_PAYLOAD",
        "cross_arm_cache_probe": "NOT_RUN_NO_MATCHED_ARM_EXECUTION",
        "evaluator_gaming_probe": "NOT_RUN_NO_PROTECTED_EVALUATOR",
        "pass_to_pass_regressions": {"denominator": 0, "count": None, "state": "CANNOT_CHECK"},
        "harmful_transfer": {"denominator": 0, "count": None, "state": "CANNOT_CHECK"},
        "protected_adoption_false_positives": {
            "denominator": 0,
            "count": None,
            "state": "CANNOT_CHECK",
        },
        "rows_dropped": 0,
    }
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", controls)

    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": "P5-DES-01",
        "frozen_per_case_per_arm_seed": freeze["resources"]["per_case_per_arm_seed"],
        "planned_run_cells": counts["planned_run_cell_denominator"],
        "executed_run_cells": 0,
        "model_calls": 0,
        "tool_calls": 0,
        "gpu_hours": 0,
        "cpu_hours": 0,
        "scientific_outcome_access": False,
        "gpu_job_submitted": False,
        "gpu_job_not_submitted_reason": "hard acquisition and custody preconditions absent",
        "censoring": {
            "resource_cap_hit": False,
            "timeout_hit": False,
            "missing_transfer_is_cannot_check_not_censoring": True,
            "future_cap_hits_retained_as_censored": True,
        },
        "remote_probe": remote,
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)

    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": "P5-DES-01",
        "state": "CANNOT_CHECK",
        "reason": terminal,
        "eligible_cases": 0,
        "held_out_transfer_evaluable": False,
        "authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)

    authority = {
        "schema": "orion.p5-des.protected-adoption-result.v1",
        "job_id": "P5-DES-01",
        "exact_terminal": terminal,
        "authority_separation": freeze["authority_separation"],
        "candidate_custody_attained": transfers["candidate_isolation"]["present"],
        "independent_evaluator_custody_attained": transfers["protected_evaluator"]["present"],
        "pre_outcome_threshold_custody_attained": transfers["threshold_freeze"]["present"],
        "external_adoption_custody_attained": transfers["external_adoption"]["present"],
        "self_promotion_authorized": False,
        "adoptions_scored": 0,
        "false_adoptions": None,
        "state": "CANNOT_CHECK",
    }
    write_json(HERE / "P5_PROTECTED_ADOPTION_RESULT_V1.json", authority)

    component_names = (
        "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json",
        "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json",
        "TRANSFER_RESULT_V1.json",
        "P5_PROTECTED_ADOPTION_RESULT_V1.json",
    )
    component_digests = {name: sha256_file(HERE / name) for name in component_names}
    missing_transfers = [name for name, state in transfers.items() if not state["present"]]
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": "P5-DES-01",
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "freeze_commit": freeze_commit,
        "execution_head": execution_head,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "raw_manifest_sha256": raw_digest,
        "component_sha256": component_digests,
        "case_outcomes": cases,
        "denominators": counts,
        "hard_preconditions": {
            "swe_bench_verified_transfer": transfers["swe_bench_verified"]["present"],
            "fresh_held_issue_transfer": transfers["fresh_held_issues"]["present"],
            "exact_eight_arm_implementations": transfers["arm_implementations"]["present"],
            "candidate_custody_isolated": transfers["candidate_isolation"]["present"],
            "independent_protected_evaluator": transfers["protected_evaluator"]["present"],
            "threshold_frozen_before_outcomes": transfers["threshold_freeze"]["present"],
            "external_adoption_custody": transfers["external_adoption"]["present"],
            "rights_and_eligibility": transfers["rights_and_eligibility"]["present"],
            "all_attained": all_transfers,
            "missing": missing_transfers,
        },
        "leakage": {
            "existing_96_case_lineage_excluded": True,
            "authored_fixture_excluded": True,
            "public_tasks_not_used_as_hidden_transfer": True,
            "executor_saw_protected_outcomes": False,
            "weak_proxy_substituted": False,
            "post_outcome_retuning": False,
        },
        "censoring": resources["censoring"],
        "strongest_donor": donor,
        "resource_vector": resources,
        "transfer": transfer,
        "protected_adoption": authority,
        "exact_terminal": terminal,
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "CANNOT_CHECK",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "paper_authority_delta": "NONE",
    }
    write_json(HERE / "RESULT_BINDING_PACKET_V1.json", binding)
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transfer-dir", type=Path)
    parser.add_argument("--remote-probe", type=Path)
    args = parser.parse_args()
    terminal = run(transfer_dir=args.transfer_dir, remote_probe=args.remote_probe)
    print(terminal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
