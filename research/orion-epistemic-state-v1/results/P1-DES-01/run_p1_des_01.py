#!/usr/bin/env python3
"""Fail-closed executor for the frozen P1-DES-01 protected study.

The public ScienceAgentBench annotation sheet and earlier constructed P1
worlds are not substitutes for the protected benchmark/evaluator or a fresh,
prospectively sequestered counterfactual cohort.  This executor therefore
performs only precondition and custody checks unless all frozen transfers are
present.  Missing transfers become denominator-complete CANNOT_CHECK rows;
they are never converted to zero scores or dropped.
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
    "scienceagentbench": "SCIENCEAGENTBENCH_TRANSFER_V1.json",
    "fresh_counterfactual": "FRESH_COUNTERFACTUAL_TRANSFER_V1.json",
    "arms": "ARM_IMPLEMENTATION_TRANSFER_V1.json",
    "protected_adoption": "PROTECTED_ADOPTION_TRANSFER_V1.json",
}

EXPECTED_OUTPUTS = (
    "RAW_MANIFEST_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
    "RESULT_BINDING_PACKET_V1.json",
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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


def sab_case_ids() -> list[str]:
    masking = load_json(
        REPO_ROOT
        / "papers/paper-01-recursive-epistemic-reconstruction/masking/P1_MASKING_FREEZE_V1.json"
    )
    ids = [str(row["instance_id"]) for row in masking["entries"]]
    if len(ids) != 102 or len(set(ids)) != 102:
        raise ValueError("frozen ScienceAgentBench metadata denominator is not 102 unique rows")
    return [f"sab:{item}" for item in ids]


def planned_case_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "case_id": case_id,
            "cohort": "scienceagentbench_official_102",
            "status": "CANNOT_CHECK",
            "reason": "PROTECTED_ARCHIVE_OR_OFFICIAL_EVALUATOR_NOT_TRANSFERRED",
            "eligible_for_primary": False,
            "outcome": None,
        }
        for case_id in sab_case_ids()
    ]
    rows.extend(
        {
            "case_id": f"counterfactual-remint:{index:03d}",
            "cohort": "fresh_counterfactual_hidden_formulation_48",
            "status": "CANNOT_CHECK",
            "reason": "FRESH_PROSPECTIVE_CUSTODY_NOT_TRANSFERRED",
            "eligible_for_primary": False,
            "outcome": None,
        }
        for index in range(1, 49)
    )
    assert len(rows) == 150
    return rows


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
    if freeze["job_id"] != "P1-DES-01":
        raise ValueError("wrong job freeze")
    if freeze["subject_revision"] != "3c97b87f4f4c8c0365226019236c83d3c4c7bb37":
        raise ValueError("wrong frozen subject")
    if freeze["study"]["case_denominator"] != 150:
        raise ValueError("case denominator drift")
    if len(freeze["study"]["arms"]) != 5:
        raise ValueError("arm denominator drift")
    if freeze["study"]["stochastic_repeats"] != 5:
        raise ValueError("repeat denominator drift")


def run(*, transfer_dir: Path | None, remote_probe: Path | None) -> str:
    freeze = load_json(FREEZE_PATH)
    validate_freeze(freeze)
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
        # The transferred artifacts may contain protected outcomes.  A separate
        # executor whose bytes are frozen against those exact manifests must be
        # committed before reading them.  This preflight deliberately refuses
        # to improvise that executor after seeing a transfer.
        raise RuntimeError("all transfers present: freeze a transfer-bound execution binary first")

    remote = load_json(remote_probe) if remote_probe and remote_probe.is_file() else {
        "state": "NOT_PROBED",
        "reason": "no remote probe supplied",
    }
    cases = planned_case_rows()
    counts = {
        "case_denominator": len(cases),
        "scienceagentbench_cases": sum(row["cohort"].startswith("scienceagentbench") for row in cases),
        "counterfactual_cases": sum(row["cohort"].startswith("fresh_counterfactual") for row in cases),
        "cases_executed": 0,
        "cases_cannot_check": len(cases),
        "arm_denominator": len(freeze["study"]["arms"]),
        "stochastic_repeats": freeze["study"]["stochastic_repeats"],
        "planned_run_cell_denominator": (
            len(cases)
            * len(freeze["study"]["arms"])
            * freeze["study"]["stochastic_repeats"]
        ),
        "run_cells_executed": 0,
    }
    terminal = freeze["terminals"]["cannot_check"]

    raw = {
        "schema": "orion.p1-des.raw-manifest.v1",
        "job_id": "P1-DES-01",
        "subject_revision": freeze["subject_revision"],
        "execution_head": execution_head,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "transfers": transfers,
        "remote_probe": remote,
        "case_outcomes": cases,
        "counts": counts,
        "rows_dropped": 0,
    }
    write_json(HERE / "RAW_MANIFEST_V1.json", raw)
    raw_digest = sha256_file(HERE / "RAW_MANIFEST_V1.json")

    primary = {
        "schema": "orion.p1-des.primary-result.v1",
        "job_id": "P1-DES-01",
        "exact_terminal": terminal,
        "counts": counts,
        "endpoint_results": {
            endpoint: {
                "state": "CANNOT_CHECK",
                "estimate": None,
                "reason": "zero eligible protected run cells",
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
        "claim_ceiling": freeze["claim_ceiling"],
    }
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)

    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": "P1-DES-01",
        "strongest_donor": freeze["study"]["strongest_donor"],
        "state": "NOT_RUN",
        "reason": "matched protected substrates and transfer-bound donor implementation unavailable",
        "weak_proxy_substituted": False,
        "resource_matching_evaluable": False,
        "donor_absorption_state": "CANNOT_CHECK",
    }
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", donor)

    controls = {
        "schema": "orion.p1-des.negative-controls.v1",
        "job_id": "P1-DES-01",
        "generator_label_probe": "NOT_RUN_NO_FRESH_COUNTERFACTUAL_TRANSFER",
        "filename_probe": "NOT_RUN_NO_FRESH_COUNTERFACTUAL_TRANSFER",
        "prompt_template_probe": "PREVIOUS_66_CASE_LINEAGE_KNOWN_TO_LEAK_AND_EXCLUDED_FROM_PRIMARY",
        "contamination_probe": "CANNOT_CHECK_PROTECTED_ARCHIVE_UNAVAILABLE",
        "harmful_reopening": {"denominator": 0, "count": None, "state": "CANNOT_CHECK"},
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
        "job_id": "P1-DES-01",
        "frozen_per_case_per_arm": freeze["resources"]["per_case_per_arm"],
        "planned_run_cells": counts["planned_run_cell_denominator"],
        "executed_run_cells": 0,
        "model_calls": 0,
        "tool_calls": 0,
        "search_calls": 0,
        "gpu_hours": 0,
        "scientific_outcome_access": False,
        "censoring": {
            "resource_cap_hit": False,
            "timeout_hit": False,
            "missing_transfer_is_cannot_check_not_censoring": True,
        },
        "remote_probe": remote,
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)

    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": "P1-DES-01",
        "state": "CANNOT_CHECK",
        "reason": terminal,
        "eligible_cases": 0,
        "authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)

    component_digests = {
        name: sha256_file(HERE / name)
        for name in (
            "PRIMARY_RESULT_V1.json",
            "IDEAL_DONOR_RESULT_V1.json",
            "NEGATIVE_CONTROLS_V1.json",
            "RESOURCE_LEDGER_V1.json",
            "TRANSFER_RESULT_V1.json",
        )
    }
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": "P1-DES-01",
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
            "official_benchmark_cleartext": transfers["scienceagentbench"]["present"],
            "official_evaluator": transfers["scienceagentbench"]["present"],
            "fresh_counterfactual_custody": transfers["fresh_counterfactual"]["present"],
            "exact_five_arm_implementations": transfers["arms"]["present"],
            "protected_adoption_custody": transfers["protected_adoption"]["present"],
            "all_attained": all_transfers,
        },
        "leakage": {
            "previous_66_case_lineage_excluded": True,
            "executor_saw_protected_outcomes": False,
            "weak_proxy_substituted": False,
            "post_outcome_retuning": False,
        },
        "censoring": resources["censoring"],
        "strongest_donor": donor,
        "resource_vector": resources,
        "transfer": transfer,
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
