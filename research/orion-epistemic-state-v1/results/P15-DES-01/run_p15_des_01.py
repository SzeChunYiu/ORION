#!/usr/bin/env python3
"""Fail-closed executor for P15-DES-01.

The frozen production study requires public production workloads, a balanced
fault corpus, three locked runtime images, production and independent-site
custody, executable comparators, external gold, and publication-race capture.
Existing bounded SEI/provenance/attestation receipts and unbound same-programme
LUNARC rehearsals are not lawful substitutes.  Missing inputs therefore emit a
denominator-complete CANNOT_CHECK packet without opening outcomes or consuming
SLURM resources.
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
    "workload_fault_manifest": "P15_WORKLOAD_FAULT_MANIFEST_V1.json",
    "runtime_image_locks_and_sboms": "P15_RUNTIME_IMAGE_LOCKS_AND_SBOMS_V1.json",
    "production_harness_and_fault_injectors": (
        "P15_PRODUCTION_HARNESS_AND_FAULT_INJECTORS_V1.json"
    ),
    "comparator_implementations": "P15_COMPARATOR_IMPLEMENTATIONS_V1.json",
    "key_custody_attestation": "P15_KEY_CUSTODY_ATTESTATION_V1.json",
    "primary_site_custody": "P15_PRIMARY_SITE_CUSTODY_V1.json",
    "independent_cross_site_replay": "P15_INDEPENDENT_CROSS_SITE_REPLAY_V1.json",
    "external_gold_and_scorer": "P15_EXTERNAL_GOLD_AND_SCORER_V1.json",
    "publication_race_event_capture": "P15_PUBLICATION_RACE_EVENT_CAPTURE_V1.json",
}

EXPECTED_OUTPUTS = (
    "RAW_MANIFEST_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
    "P15_PRODUCTION_NONINTERFERENCE_RESULT_V1.json",
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
    rows: list[dict[str, Any]] = [
        {
            "case_id": f"p15-production:workload-slot:{index:03d}",
            "cohort": "production_workloads",
            "fault_family": None,
            "case_identity_state": "FROZEN_SLOT_EXACT_PROVIDER_ID_NOT_TRANSFERRED",
            "status": "CANNOT_CHECK",
            "reason": "PRODUCTION_WORKLOAD_ID_GOLD_AND_CUSTODY_NOT_TRANSFERRED",
            "eligible_for_hypothesis_testing": False,
            "outcome": None,
        }
        for index in range(1, 31)
    ]
    fault_families = (
        ("host-resource", "host_resource_faults"),
        (
            "process-lifecycle-publication-race",
            "process_lifecycle_publication_race_faults",
        ),
        ("key-attestation-custody", "key_attestation_custody_faults"),
        ("evaluator-site-custody", "evaluator_site_custody_faults"),
    )
    for slug, cohort in fault_families:
        rows.extend(
            {
                "case_id": f"p15-production:fault:{slug}:{index:02d}",
                "cohort": cohort,
                "fault_family": slug,
                "case_identity_state": "FROZEN_SLOT_EXACT_FAULT_PAYLOAD_NOT_TRANSFERRED",
                "status": "CANNOT_CHECK",
                "reason": "FAULT_PAYLOAD_GOLD_AND_CUSTODY_NOT_TRANSFERRED",
                "eligible_for_hypothesis_testing": False,
                "outcome": None,
            }
            for index in range(1, 6)
        )
    if len(rows) != 50 or len({row["case_id"] for row in rows}) != 50:
        raise ValueError("planned P15 case denominator or identity drift")
    return rows


def case_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    cohorts = (
        "production_workloads",
        "host_resource_faults",
        "process_lifecycle_publication_race_faults",
        "key_attestation_custody_faults",
        "evaluator_site_custody_faults",
    )
    return {cohort: sum(row["cohort"] == cohort for row in rows) for cohort in cohorts}


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
    if freeze["job_id"] != "P15-DES-01":
        raise ValueError("wrong job freeze")
    if freeze["subject_revision"] != "3c97b87f4f4c8c0365226019236c83d3c4c7bb37":
        raise ValueError("wrong frozen subject")
    study = freeze["study"]
    if study["case_denominator"] != 50:
        raise ValueError("case denominator drift")
    if study["production_workload_denominator"] != 30:
        raise ValueError("production workload denominator drift")
    if study["fault_denominator"] != 20:
        raise ValueError("fault denominator drift")
    if len(study["runtime_images"]) != 3:
        raise ValueError("runtime-image denominator drift")
    if len(study["sites"]) != 2:
        raise ValueError("site denominator drift")
    if len(study["arms"]) != 7:
        raise ValueError("arm denominator drift")
    if study["seeds"] != [1515, 1516, 1517]:
        raise ValueError("seed drift")
    if study["planned_run_cell_denominator"] != 50 * 3 * 2 * 7 * 3:
        raise ValueError("run-cell denominator drift")
    if freeze["terminals"]["cannot_check"] != (
        "P15_PRODUCTION_HOST_PROCESS_KEY_CUSTODY_AND_CROSS_SITE_REPLAY_CANNOT_CHECK"
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
            "all P15 production transfers present: freeze a transfer-digest-bound executor before access"
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
        "production_workload_denominator": cohort_counts["production_workloads"],
        "fault_denominator": sum(value for key, value in cohort_counts.items() if key != "production_workloads"),
        "runtime_image_denominator": len(freeze["study"]["runtime_images"]),
        "site_denominator": len(freeze["study"]["sites"]),
        "arm_denominator": len(freeze["study"]["arms"]),
        "seed_denominator": len(freeze["study"]["seeds"]),
        "planned_run_cell_denominator": freeze["study"]["planned_run_cell_denominator"],
        "cases_executed": 0,
        "cases_cannot_check": len(cases),
        "run_cells_executed": 0,
        **cohort_counts,
    }
    terminal = freeze["terminals"]["cannot_check"]

    raw = {
        "schema": "orion.p15-des.raw-manifest.v1",
        "job_id": "P15-DES-01",
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
        "schema": "orion.p15-des.primary-result.v1",
        "job_id": "P15-DES-01",
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
        "job_id": "P15-DES-01",
        "strongest_donor": freeze["study"]["strongest_donor"],
        "registered_donor_arms": freeze["study"]["donor_arms"],
        "state": "NOT_RUN",
        "reason": "production inputs, locked images, comparator executables, and independent custody absent",
        "weak_proxy_substituted": False,
        "resource_matching_evaluable": False,
        "donor_absorption_state": "CANNOT_CHECK",
    }
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", donor)

    controls = {
        "schema": "orion.p15-des.negative-controls.v1",
        "job_id": "P15-DES-01",
        "internal_fixture_substitution": False,
        "existing_bounded_receipts_substituted": False,
        "same_site_replay_treated_as_independent": False,
        "unbound_lunarc_lineage_substituted": False,
        "attestation_treated_as_scientific_truth": False,
        "existing_bounded_receipts": freeze["retained_bounded_evidence"],
        "host_fault_controls": {"planned_denominator": 5, "evaluated": 0, "state": "CANNOT_CHECK"},
        "process_and_race_controls": {"planned_denominator": 5, "evaluated": 0, "state": "CANNOT_CHECK"},
        "key_custody_controls": {"planned_denominator": 5, "evaluated": 0, "state": "CANNOT_CHECK"},
        "site_custody_controls": {"planned_denominator": 5, "evaluated": 0, "state": "CANNOT_CHECK"},
        "outcome_label_leakage_probe": "NOT_RUN_NO_EXTERNAL_GOLD_OR_SCORER",
        "cross_arm_cache_probe": "NOT_RUN_NO_MATCHED_EXECUTION",
        "publication_race_probe": "NOT_RUN_EVENT_CAPTURE_NOT_TRANSFERRED",
        "rows_dropped": 0,
    }
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", controls)

    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": "P15-DES-01",
        "frozen_per_case_image_site_arm_seed": freeze["resources"]["per_case_image_site_arm_seed"],
        "planned_run_cells": counts["planned_run_cell_denominator"],
        "executed_run_cells": 0,
        "model_calls": 0,
        "harness_runs": 0,
        "fault_injections": 0,
        "replay_calls": 0,
        "attestation_calls": 0,
        "gold_scorer_calls": 0,
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
            "timeout_never_proves_noninterference": True,
        },
        "remote_probe": remote,
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)

    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": "P15-DES-01",
        "state": "CANNOT_CHECK",
        "reason": terminal,
        "eligible_cases": 0,
        "cross_site_replay_evaluable": False,
        "independent_site_authority": False,
        "authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)

    custom = {
        "schema": "orion.p15-des.production-noninterference-result.v1",
        "job_id": "P15-DES-01",
        "exact_terminal": terminal,
        "production_cases_planned": 50,
        "production_cases_scored": 0,
        "fault_cases_planned": 20,
        "fault_injections_completed": 0,
        "runtime_images_planned": 3,
        "runtime_images_executed": 0,
        "sites_planned": 2,
        "cross_site_replays_completed": 0,
        "publication_races_captured": 0,
        "attribution_estimate": None,
        "fault_coverage_estimate": None,
        "false_rejection_estimate": None,
        "overhead_estimate": None,
        "production_noninterference_estimate": None,
        "state": "CANNOT_CHECK",
    }
    write_json(HERE / "P15_PRODUCTION_NONINTERFERENCE_RESULT_V1.json", custom)

    component_names = (
        "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json",
        "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json",
        "TRANSFER_RESULT_V1.json",
        "P15_PRODUCTION_NONINTERFERENCE_RESULT_V1.json",
    )
    components = {name: sha256_file(HERE / name) for name in component_names}
    missing = [name for name, state in transfers.items() if not state["present"]]
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": "P15-DES-01",
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
            "exact_external_case_identities_unavailable_not_invented": True,
            "existing_bounded_receipts_preserved_not_substituted": True,
            "unbound_remote_execution_outcomes_unopened": True,
            "same_site_replay_not_called_independent": True,
            "executor_saw_protected_outcomes": False,
            "weak_proxy_substituted": False,
            "timeout_treated_as_noninterference": False,
            "post_outcome_retuning": False,
        },
        "censoring": resources["censoring"],
        "strongest_donor": donor,
        "resource_vector": resources,
        "transfer": transfer,
        "production_noninterference": custom,
        "retained_bounded_evidence": freeze["retained_bounded_evidence"],
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
