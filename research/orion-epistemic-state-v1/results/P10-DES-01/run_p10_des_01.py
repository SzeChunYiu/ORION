#!/usr/bin/env python3
"""Fail-closed executor for P10-DES-01.

The frozen wide P10 study requires native verifier-backed tasks, exact donor
executables, blinded obstruction gold, independent OCME witnesses, protected
replication, and external scoring custody.  Existing toy OCME receipts,
internal runners, public source metadata, or a timed-out donor are not lawful
substitutes.  Missing inputs therefore produce a denominator-complete
acquisition-blocker packet without opening outcomes or consuming GPU time.
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
    "protected_task_manifest": "P10_PROTECTED_TASK_MANIFEST_V1.json",
    "native_verifier_runners": "P10_NATIVE_VERIFIER_RUNNERS_V1.json",
    "strongest_donor_executables": "P10_STRONGEST_DONOR_EXECUTABLES_V1.json",
    "blinded_obstruction_custody": "P10_BLINDED_OBSTRUCTION_CUSTODY_V1.json",
    "independent_ocme_witness": "P10_INDEPENDENT_OCME_WITNESS_V1.json",
    "protected_replication_split": "P10_PROTECTED_REPLICATION_SPLIT_V1.json",
    "independent_scorer_review": "P10_INDEPENDENT_SCORER_REVIEW_CUSTODY_V1.json",
    "power_attainability": "P10_POWER_ATTAINABILITY_RECEIPT_V1.json",
}

EXPECTED_OUTPUTS = (
    "RAW_MANIFEST_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
    "P10_OBSTRUCTION_AND_FALSE_INVENTION_RESULT_V1.json",
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
    for domain in freeze["study"]["domains"]:
        domain_id = domain["domain_id"]
        slug = domain["slug"]
        rows.extend(
            {
                "case_id": f"p10-protected:{slug}:task:{index:03d}",
                "domain": domain_id,
                "cohort": f"{slug}_tasks",
                "case_identity_state": "FROZEN_SLOT_EXACT_PROVIDER_ID_NOT_TRANSFERRED",
                "status": "CANNOT_CHECK",
                "reason": "PROTECTED_TASK_AND_NATIVE_EVALUATOR_NOT_TRANSFERRED",
                "eligible_for_hypothesis_testing": False,
                "outcome": None,
            }
            for index in range(1, 101)
        )
        rows.extend(
            {
                "case_id": f"p10-protected:{slug}:known-method-control:{index:03d}",
                "domain": domain_id,
                "cohort": f"{slug}_known_method_controls",
                "case_identity_state": "FROZEN_SLOT_EXACT_PROVIDER_ID_NOT_TRANSFERRED",
                "status": "CANNOT_CHECK",
                "reason": "BLINDED_KNOWN_METHOD_CONTROL_GOLD_NOT_TRANSFERRED",
                "eligible_for_hypothesis_testing": False,
                "outcome": None,
            }
            for index in range(1, 21)
        )
    if len(rows) != 480 or len({row["case_id"] for row in rows}) != 480:
        raise ValueError("planned P10 case denominator or identity drift")
    return rows


def case_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    labels = (
        "lean_tasks",
        "lean_known_method_controls",
        "sygus_tasks",
        "sygus_known_method_controls",
        "ipc_tasks",
        "ipc_known_method_controls",
        "code_tasks",
        "code_known_method_controls",
    )
    return {label: sum(row["cohort"] == label for row in rows) for label in labels}


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
    if freeze["job_id"] != "P10-DES-01":
        raise ValueError("wrong job freeze")
    if freeze["subject_revision"] != "3c97b87f4f4c8c0365226019236c83d3c4c7bb37":
        raise ValueError("wrong frozen subject")
    if freeze["study"]["case_denominator"] != 480:
        raise ValueError("case denominator drift")
    if freeze["study"]["protected_task_denominator"] != 400:
        raise ValueError("protected task denominator drift")
    if freeze["study"]["known_method_control_denominator"] != 80:
        raise ValueError("known-method control denominator drift")
    if len(freeze["study"]["arms"]) != 9:
        raise ValueError("arm denominator drift")
    if freeze["study"]["seeds"] != [1010, 1011, 1012]:
        raise ValueError("seed drift")
    if freeze["study"]["planned_run_cell_denominator"] != 480 * 9 * 3:
        raise ValueError("run-cell denominator drift")
    if freeze["terminals"]["cannot_check"] != (
        "P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT"
    ):
        raise ValueError("acquisition blocker terminal drift")


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
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", freeze_commit, execution_head],
        cwd=REPO_ROOT,
    ).returncode != 0:
        raise RuntimeError(f"freeze commit {freeze_commit} is not an ancestor of {execution_head}")

    transfers = transfer_state(transfer_dir)
    all_transfers = all(item["present"] for item in transfers.values())
    if all_transfers:
        raise RuntimeError(
            "all P10 protected transfers present: freeze a transfer-digest-bound executor before access"
        )
    remote = load_json(remote_probe) if remote_probe and remote_probe.is_file() else {
        "state": "NOT_PROBED",
        "reason": "no LUNARC preflight supplied",
        "protected_outcome_accessed": False,
    }
    cases = planned_case_rows()
    domain_counts = case_counts(cases)
    counts = {
        "case_denominator": len(cases),
        "protected_task_denominator": sum(v for k, v in domain_counts.items() if k.endswith("_tasks")),
        "known_method_control_denominator": sum(
            v for k, v in domain_counts.items() if k.endswith("known_method_controls")
        ),
        "domain_denominator": len(freeze["study"]["domains"]),
        "arm_denominator": len(freeze["study"]["arms"]),
        "seed_denominator": len(freeze["study"]["seeds"]),
        "planned_run_cell_denominator": freeze["study"]["planned_run_cell_denominator"],
        "cases_executed": 0,
        "cases_cannot_check": len(cases),
        "run_cells_executed": 0,
        **domain_counts,
    }
    terminal = freeze["terminals"]["cannot_check"]

    raw = {
        "schema": "orion.p10-des.raw-manifest.v1",
        "job_id": "P10-DES-01",
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

    hypotheses = {name: "PROSPECTIVE_NOT_EXECUTED" for name in freeze["study"]["hypotheses"]}
    primary = {
        "schema": "orion.p10-des.primary-result.v1",
        "job_id": "P10-DES-01",
        "exact_terminal": terminal,
        "counts": counts,
        "hypotheses": hypotheses,
        "endpoint_results": {
            endpoint: {
                "state": "NOT_EVALUATED_INPUTS_ABSENT",
                "estimate": None,
                "reason": terminal,
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
        "job_id": "P10-DES-01",
        "strongest_donor": freeze["study"]["strongest_donor"],
        "registered_donor_arms": freeze["study"]["donor_arms"],
        "state": "NOT_RUN",
        "reason": "full native donor executables, adapters, evaluators, and matched task inputs absent",
        "weak_proxy_substituted": False,
        "resource_matching_evaluable": False,
        "donor_absorption_state": "CANNOT_CHECK",
    }
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", donor)

    controls = {
        "schema": "orion.p10-des.negative-controls.v1",
        "job_id": "P10-DES-01",
        "internal_fixture_substitution": False,
        "public_source_metadata_substituted": False,
        "generated_exact_setting_ocme_substituted": False,
        "native_lean_cannot_check_substituted": False,
        "timeout_treated_as_obstruction": False,
        "no_jump_control": {"planned_denominator": 480, "evaluated": 0, "state": "CANNOT_CHECK"},
        "known_method_controls": {
            "planned_denominator": 80,
            "evaluated": 0,
            "false_expansions": None,
            "state": "CANNOT_CHECK",
        },
        "proposal_origin_probe": "NOT_RUN_NO_CANDIDATE_OR_EXTERNAL_TRACE",
        "hidden_access_widening_probe": "NOT_RUN_NO_PROTECTED_EVALUATOR",
        "cross_arm_cache_probe": "NOT_RUN_NO_MATCHED_EXECUTION",
        "rows_dropped": 0,
    }
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", controls)

    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": "P10-DES-01",
        "frozen_per_case_per_arm_seed": freeze["resources"]["per_case_per_arm_seed"],
        "planned_run_cells": counts["planned_run_cell_denominator"],
        "executed_run_cells": 0,
        "model_calls": 0,
        "verifier_calls": 0,
        "tool_calls": 0,
        "gpu_hours": 0,
        "cpu_hours": 0,
        "scientific_outcome_access": False,
        "slurm_job_submitted": False,
        "slurm_job_not_submitted_reason": terminal,
        "censoring": {
            "resource_cap_hit": False,
            "timeout_hit": False,
            "missing_transfer_is_cannot_check_not_censoring": True,
            "future_cap_hits_retained_as_censored": True,
            "timeout_never_proves_outside_closure": True,
        },
        "remote_probe": remote,
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)

    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": "P10-DES-01",
        "state": "CANNOT_CHECK",
        "reason": terminal,
        "eligible_cases": 0,
        "held_out_transfer_evaluable": False,
        "authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)

    custom = {
        "schema": "orion.p10-des.obstruction-false-invention-result.v1",
        "job_id": "P10-DES-01",
        "exact_terminal": terminal,
        "candidate_edits_scored": 0,
        "verifier_accepted_edits": 0,
        "outside_closure_certificates": 0,
        "minimality_certificates": 0,
        "held_out_transfer_successes": 0,
        "false_inventions": None,
        "false_invention_denominator": 0,
        "known_method_control_planned_denominator": 80,
        "timeout_certificates": 0,
        "proposal_origin_traces": 0,
        "state": "CANNOT_CHECK",
    }
    write_json(HERE / "P10_OBSTRUCTION_AND_FALSE_INVENTION_RESULT_V1.json", custom)

    component_names = (
        "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json",
        "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json",
        "TRANSFER_RESULT_V1.json",
        "P10_OBSTRUCTION_AND_FALSE_INVENTION_RESULT_V1.json",
    )
    components = {name: sha256_file(HERE / name) for name in component_names}
    missing = [name for name, state in transfers.items() if not state["present"]]
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": "P10-DES-01",
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "freeze_commit": freeze_commit,
        "execution_head": execution_head,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "raw_manifest_sha256": raw_digest,
        "component_sha256": components,
        "case_outcomes": cases,
        "denominators": counts,
        "hypotheses": hypotheses,
        "hard_preconditions": {
            name: state["present"] for name, state in transfers.items()
        }
        | {"all_attained": all_transfers, "missing": missing},
        "leakage": {
            "generated_exact_setting_ocme_excluded": True,
            "native_lean_adverse_lineage_preserved": True,
            "remote_internal_execution_outcomes_unopened": True,
            "executor_saw_protected_outcomes": False,
            "weak_proxy_substituted": False,
            "timeout_treated_as_obstruction": False,
            "post_outcome_retuning": False,
        },
        "censoring": resources["censoring"],
        "strongest_donor": donor,
        "resource_vector": resources,
        "transfer": transfer,
        "obstruction_and_false_invention": custom,
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
    print(run(transfer_dir=args.transfer_dir, remote_probe=args.remote_probe))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
