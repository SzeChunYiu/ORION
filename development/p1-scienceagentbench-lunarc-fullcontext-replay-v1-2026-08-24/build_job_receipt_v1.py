#!/usr/bin/env python3
"""Build a robust job receipt even when the harness receipt is absent."""

import argparse
import json
from pathlib import Path


def load_or_none(path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--harness-rc", type=int, required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--started-utc", required=True)
    parser.add_argument("--finished-utc", required=True)
    parser.add_argument("--wall-seconds", type=int, required=True)
    args = parser.parse_args()

    harness_path = args.run_dir / "results/HARNESS_RECEIPT_V1.json"
    harness = load_or_none(harness_path)
    postprocessing_failures = []
    if harness is None:
        postprocessing_failures.append("HARNESS_RECEIPT_MISSING_OR_INVALID")
        harness = {
            "schema": "orion.p1.scienceagentbench.fullcontext-replay-harness.v1",
            "status": "NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE",
            "condition_statuses": {},
            "infrastructure_failures": {
                "postprocessing": {
                    "status": "NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE",
                    "error": "HARNESS_RECEIPT_MISSING_OR_INVALID",
                }
            },
            "composition_status": "NOT_COMPOSED__NO_COMPOSITE_SCIENTIFIC_WITNESS",
            "prompt_bodies_retained": False,
            "forbidden_inputs_opened": False,
            "scientific_authority_delta": "NONE",
        }
    energy = load_or_none(args.run_dir / "GPU_ENERGY_RECEIPT_V1.json")
    if energy is None:
        postprocessing_failures.append("GPU_ENERGY_RECEIPT_MISSING_OR_INVALID")
        energy = {
            "schema": "orion.p1.scienceagentbench.fullcontext-replay-gpu-energy.v1",
            "status": "CANNOT_CHECK_MISSING_OR_INVALID_TELEMETRY_RECEIPT",
            "billed_usd": None,
            "scientific_authority_delta": "NONE",
        }

    status = harness["status"]
    if status == "COMPLETE_TWO_SEPARATE_CONDITIONS" and args.harness_rc == 0:
        terminal = (
            "P1_SAB_FULLCONTEXT_REPLAY_COMPLETE__TWO_SEPARATE_CONDITIONS_RETAINED__"
            "SHORT_PASS__LONG_PASS__NO_COMPOSITE_SCIENTIFIC_WITNESS__JOB_"
            + args.job_id
            + "__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"
        )
    elif status == "COMPLETE_WITH_ONE_OR_MORE_ADVERSE_CONDITIONS":
        terminal = (
            "P1_SAB_FULLCONTEXT_REPLAY_COMPLETE__TWO_SEPARATE_CONDITIONS_RETAINED__"
            "ONE_OR_MORE_SCIENTIFICALLY_ADVERSE__NO_COMPOSITE_SCIENTIFIC_WITNESS__JOB_"
            + args.job_id
            + "__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"
        )
    else:
        status = "NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE"
        terminal = (
            "P1_SAB_FULLCONTEXT_REPLAY_NOT_RESULT_BEARING__INFRASTRUCTURE_FAILURE__"
            "NO_COMPOSITE_SCIENTIFIC_WITNESS__JOB_"
            + args.job_id
            + "__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"
        )

    receipt = {
        "schema": "orion.p1.scienceagentbench.fullcontext-replay-job.v1",
        "status": status,
        "terminal": terminal,
        "slurm_job_id": args.job_id,
        "started_utc": args.started_utc,
        "finished_utc": args.finished_utc,
        "runtime_wall_seconds": args.wall_seconds,
        "harness_exit_code": args.harness_rc,
        "harness": harness,
        "postprocessing_failures": postprocessing_failures,
        "gpu_telemetry": energy,
        "runtime": {
            "ollama_module": "ollama/0.32.14",
            "ollama_no_cloud": "1",
            "llama_cpp_version": "b10434",
            "llama_cpp_commit": "7e4c0a96880dae4fc4268ad441f8a6446bd5460a",
            "model_sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
            "llama_server_sha256": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
            "cuda_backend_sha256": "fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb",
        },
        "cost": {
            "billed_usd": None,
            "status": "CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE",
            "allocated_seconds_recorded_posthoc": True,
            "gpu_seconds_and_sampled_energy_recorded_separately": True,
        },
        "forbidden_inputs": {
            "protected_archive_opened": False,
            "benchmark_task_opened": False,
            "outcome_opened": False,
            "gold_program_opened": False,
            "evaluator_opened": False,
            "rubric_opened": False,
            "credential_opened": False,
        },
        "scientific_authority_delta": "NONE",
    }
    (args.run_dir / "JOB_RECEIPT_V1.json").write_text(canonical(receipt))
    (args.run_dir / "TERMINAL.txt").write_text(terminal + "\n")
    print(terminal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
