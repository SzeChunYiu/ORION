#!/usr/bin/env python3
"""Fail-closed executor for the frozen P9-DES-01 programme.

P9-DES-01 needs a content-bound six-checkpoint open-weight ladder, runnable
representations/tasks/verifiers, donor implementations, and a separately bound
numerical build/provider/architecture matrix.  A filename that resembles a
checkpoint, package version strings, or historical build outcomes are not those
inputs.  Until every transfer exists, this executor emits denominator-complete
CANNOT_CHECK rows and submits no GPU job.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
FREEZE_PATH = HERE / "FREEZE_V1.json"

EXPECTED_OUTPUTS = (
    "RAW_MANIFEST_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
    "RESULT_BINDING_PACKET_V1.json",
)
CUSTOM_OUTPUTS = ("ACQUISITION_PREFLIGHT_V1.json", "PLANNED_CELL_LEDGER_V1.json")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def committed_freeze_revision() -> str:
    relative = FREEZE_PATH.relative_to(REPO_ROOT)
    revision = git("log", "-1", "--format=%H", "--", str(relative))
    if not revision:
        raise RuntimeError("FREEZE_V1.json is not committed")
    return revision


def validate_freeze(freeze: dict[str, Any]) -> None:
    if freeze["job_id"] != "P9-DES-01":
        raise ValueError("wrong job freeze")
    if freeze["subject_revision"] != "3c97b87f4f4c8c0365226019236c83d3c4c7bb37":
        raise ValueError("wrong subject revision")
    if freeze["base_main"] != "f049e30391a09213240f6325ee319f9fa811189a":
        raise ValueError("wrong main-base revision")
    if freeze["study"]["model_cell_denominator"] != 1344:
        raise ValueError("model-cell denominator drift")
    if freeze["study"]["numerical_cell_denominator"] != 12:
        raise ValueError("numerical-cell denominator drift")
    if freeze["study"]["planned_cell_denominator"] != 1356:
        raise ValueError("total denominator drift")
    if freeze["decision_rule"]["scalarization"] != "FORBIDDEN":
        raise ValueError("scalarization not forbidden")


def validate_source_bindings(freeze: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for name, binding in sorted(freeze["source_bindings"].items()):
        path = REPO_ROOT / binding["path"]
        actual = sha256_file(path) if path.is_file() else None
        rows.append(
            {
                "name": name,
                "path": binding["path"],
                "expected_sha256": binding["sha256"],
                "actual_sha256": actual,
                "matched": actual == binding["sha256"],
            }
        )
    return {"all_matched": all(row["matched"] for row in rows), "rows": rows}


def model_cell_ids(freeze: dict[str, Any]) -> list[str]:
    axes = freeze["study"]["model_axes"]
    ids = []
    for k in axes["k_relational_complexity"]:
        for representation in axes["representations"]:
            for family in sorted(axes["scale_ladders"]):
                for scale in axes["scale_ladders"][family]:
                    for budget in axes["inference_budgets"]:
                        for block in axes["domain_blocks"]:
                            ids.append(
                                f"k{k}|{representation}|{family}|{scale}|C{budget}|{block}"
                            )
    return ids


def numerical_cell_ids(freeze: dict[str, Any]) -> list[str]:
    axes = freeze["study"]["numerical_axes"]
    return [
        f"{provider}|{architecture}|{build_profile}"
        for provider in axes["providers"]
        for architecture in axes["architectures"]
        for build_profile in axes["build_profiles"]
    ]


def transfer_state(freeze: dict[str, Any], transfer_dir: Path | None) -> dict[str, Any]:
    state = {}
    for key, filename in freeze["required_transfer_files"].items():
        path = transfer_dir / filename if transfer_dir else None
        present = bool(path and path.is_file())
        state[key] = {
            "required_file": filename,
            "present": present,
            "sha256": sha256_file(path) if present and path else None,
        }
    return state


def local_checkpoint_probe() -> dict[str, Any]:
    suffixes = {".safetensors", ".gguf", ".onnx"}
    names = {"pytorch_model.bin", "consolidated.00.pth"}
    found = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix in suffixes or path.name in names:
            found.append(
                {
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
            if len(found) >= 16:
                break
    runtimes = [
        name for name in ("torch", "transformers", "llama_cpp", "onnxruntime")
        if importlib.util.find_spec(name) is not None
    ]
    return {
        "scope": "subject repository only",
        "checkpoint_like_files": found,
        "checkpoint_like_file_count_capped": len(found),
        "loading_runtimes_present": runtimes,
        "does_not_establish_declared_ladder": True,
    }


def current_build_probe() -> dict[str, Any]:
    versions = {}
    for name in ("numpy", "scipy", "sklearn"):
        try:
            module = __import__(name)
            versions[name] = getattr(module, "__version__", "UNKNOWN")
        except Exception as exc:  # retained as preflight state, not a crash row
            versions[name] = f"UNAVAILABLE:{type(exc).__name__}"
    executable = Path(sys.executable)
    return {
        "provider": "LOCAL",
        "system": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "executable": str(executable),
        "executable_sha256": sha256_file(executable) if executable.is_file() else None,
        "package_versions": versions,
        "complete_binary_build_identity": False,
        "missing": [
            "content-bound wheel or conda-package archives",
            "BLAS/LAPACK shared-library digests and build flags",
            "container or immutable environment image digest",
            "all other provider/architecture build cells",
        ],
    }


def planned_rows(freeze: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    model_reason = "CONTENT_BOUND_CHECKPOINT_LADDER_AND_CELL_EXECUTOR_NOT_TRANSFERRED"
    numerical_reason = "CONTENT_BOUND_NUMERICAL_BUILD_MATRIX_NOT_TRANSFERRED"
    model = [
        {
            "case_id": case_id,
            "matrix": "open_weight_factorial",
            "status": "CANNOT_CHECK",
            "cell_status": "NOT_RUN",
            "reason": model_reason,
            "outcome": None,
            "eligible_for_primary": False,
        }
        for case_id in model_cell_ids(freeze)
    ]
    numerical = [
        {
            "case_id": case_id,
            "matrix": "numerical_build_provider_architecture",
            "status": "CANNOT_CHECK",
            "cell_status": "NOT_RUN",
            "reason": numerical_reason,
            "outcome": None,
            "eligible_for_primary": False,
        }
        for case_id in numerical_cell_ids(freeze)
    ]
    return model, numerical


def run(*, transfer_dir: Path | None, remote_probe: Path | None) -> str:
    freeze = load_json(FREEZE_PATH)
    validate_freeze(freeze)
    bindings = validate_source_bindings(freeze)
    if not bindings["all_matched"]:
        raise RuntimeError("frozen source binding drift")
    execution_head = git("rev-parse", "HEAD")
    freeze_commit = committed_freeze_revision()
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", freeze_commit, execution_head], cwd=REPO_ROOT
    ).returncode != 0:
        raise RuntimeError("freeze commit is not an ancestor of execution head")

    transfers = transfer_state(freeze, transfer_dir)
    if all(value["present"] for value in transfers.values()):
        raise RuntimeError(
            "all protected transfers present: freeze a transfer-bound model/build executor before access"
        )
    local_probe = local_checkpoint_probe()
    build_probe = current_build_probe()
    remote = (
        load_json(remote_probe)
        if remote_probe and remote_probe.is_file()
        else {"state": "NOT_PROBED", "scientific_execution_authority": False}
    )
    model_rows, numerical_rows = planned_rows(freeze)
    all_rows = model_rows + numerical_rows
    counts = {
        "model_cell_denominator": len(model_rows),
        "model_cells_executed": 0,
        "model_cells_cannot_check": len(model_rows),
        "numerical_cell_denominator": len(numerical_rows),
        "numerical_cells_executed": 0,
        "numerical_cells_cannot_check": len(numerical_rows),
        "planned_cell_denominator": len(all_rows),
        "cells_executed": 0,
        "cells_cannot_check": len(all_rows),
        "slurm_jobs_submitted": 0,
        "gpu_jobs_submitted": 0,
        "rows_dropped": 0,
    }
    hard = {
        "six_exact_checkpoint_revisions_and_weight_digests_transferred": False,
        "seven_representations_with_round_trip_and_leakage_checks_transferred": False,
        "two_domain_task_generators_and_verifiers_transferred": False,
        "1344_cell_execution_binary_transferred": False,
        "strongest_donor_complete_implementations_transferred": False,
        "twelve_content_bound_numerical_build_cells_transferred": False,
        "independent_terminal_gold_and_scorer_transferred": False,
        "matched_model_and_donor_resources_evaluable": False,
    }
    terminal = freeze["terminals"]["cannot_check"]

    preflight = {
        "schema": "orion.p9-des.acquisition-preflight.v1",
        "job_id": "P9-DES-01",
        "exact_terminal": terminal,
        "transfers": transfers,
        "local_checkpoint_probe": local_probe,
        "local_build_probe": build_probe,
        "lunarc_probe": remote,
        "hard_preconditions": hard,
        "gpu_execution_permitted": False,
        "gpu_execution_prohibition": (
            "Checkpoint revisions/weight digests, cell executor, and numerical build identities "
            "are not content-bound. GPU execution would create uninterpretable cells."
        ),
        "weak_proxy_substituted": False,
    }
    write_json(HERE / "ACQUISITION_PREFLIGHT_V1.json", preflight)
    ledger = {
        "schema": "orion.p9-des.planned-cell-ledger.v1",
        "job_id": "P9-DES-01",
        "model_cells": model_rows,
        "numerical_cells": numerical_rows,
        "counts": counts,
    }
    write_json(HERE / "PLANNED_CELL_LEDGER_V1.json", ledger)

    raw = {
        "schema": "orion.p9-des.raw-manifest.v1",
        "job_id": "P9-DES-01",
        "subject_revision": freeze["subject_revision"],
        "execution_head": execution_head,
        "freeze_commit": freeze_commit,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "source_binding_audit": bindings,
        "transfers": transfers,
        "case_outcomes": all_rows,
        "counts": counts,
    }
    write_json(HERE / "RAW_MANIFEST_V1.json", raw)

    primary = {
        "schema": "orion.p9-des.primary-result.v1",
        "job_id": "P9-DES-01",
        "exact_terminal": terminal,
        "positive_gate_evaluable": False,
        "positive_gate_passed": False,
        "endpoint_results": {
            endpoint: {"state": "CANNOT_CHECK", "estimate": None, "denominator": 0}
            for endpoint in freeze["study"]["primary_endpoints"]
        },
        "hard_preconditions": hard,
        "counts": counts,
        "claim_ceiling": freeze["claim_ceiling"],
    }
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)

    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": "P9-DES-01",
        "strongest_donors": freeze["comparators"]["strongest_donors"],
        "ideal_donor_product": freeze["comparators"]["ideal_product"],
        "state": "NOT_RUN",
        "reason": "matched content-bound model/build substrates and donor implementations unavailable",
        "weak_proxy_substituted": False,
        "donor_absorption_state": "CANNOT_CHECK",
        "resource_matching_evaluable": False,
    }
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", donor)

    controls = {
        "schema": "orion.p9-des.negative-controls.v1",
        "job_id": "P9-DES-01",
        "retained_historical_boundaries": freeze["retained_historical_boundaries"],
        "classical_capacity_ladder_substituted_for_open_weights": False,
        "metadata_or_filename_treated_as_checkpoint_identity": False,
        "package_version_manifest_treated_as_binary_identity": False,
        "historical_build_toggle_treated_as_prospective_held_out_matrix": False,
        "null_adverse_cannot_check_erased": False,
        "rows_dropped": 0,
        "external_independence": "CANNOT_CHECK",
    }
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", controls)

    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": "P9-DES-01",
        "frozen_resource_vector": freeze["resources"],
        "model_cells_executed": 0,
        "numerical_cells_executed": 0,
        "model_calls": 0,
        "decode_calls": 0,
        "network_calls": 0,
        "slurm_jobs_submitted": 0,
        "gpu_jobs_submitted": 0,
        "gpu_hours": 0,
        "censoring": {
            "resource_cap_hit": False,
            "timeout_hit": False,
            "missing_transfer_is_cannot_check_not_censoring": True,
        },
        "rows_dropped": 0,
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)

    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": "P9-DES-01",
        "state": "CANNOT_CHECK",
        "exact_terminal": terminal,
        "case_rows_transferred": len(all_rows),
        "unlocked_placeholders": [
            "P9 acquisition/precondition result",
            "P9 denominator-complete CANNOT_CHECK matrix",
        ],
        "external_authority_state": "CANNOT_CHECK",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "paper_authority_delta": "NONE",
    }
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)

    names = (
        "RAW_MANIFEST_V1.json",
        "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json",
        "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json",
        "TRANSFER_RESULT_V1.json",
        *CUSTOM_OUTPUTS,
    )
    digests = {name: sha256_file(HERE / name) for name in names}
    packet = {
        "schema": "orion.p9-des.result-binding-packet.v1",
        "job_id": "P9-DES-01",
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": execution_head,
        "freeze_commit": freeze_commit,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "raw_manifest_sha256": digests["RAW_MANIFEST_V1.json"],
        "component_sha256": digests,
        "case_outcomes": all_rows,
        "denominators": counts,
        "hard_precondition_attainment": hard,
        "leakage_and_censoring": {
            "weak_proxy_substituted": False,
            "censored_rows": 0,
            "crashed_rows": 0,
            "cannot_check_rows": len(all_rows),
            "rows_dropped": 0,
        },
        "strongest_donor": freeze["comparators"]["strongest_donors"],
        "ideal_donor": freeze["comparators"]["ideal_product"],
        "resource_vector": freeze["resources"],
        "transfer_state": "CANNOT_CHECK",
        "exact_terminal": terminal,
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "CANNOT_CHECK",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "paper_authority_delta": "NONE",
    }
    write_json(HERE / "RESULT_BINDING_PACKET_V1.json", packet)
    print(terminal)
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transfer-dir", type=Path)
    parser.add_argument("--remote-probe", type=Path)
    args = parser.parse_args()
    run(transfer_dir=args.transfer_dir, remote_probe=args.remote_probe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
