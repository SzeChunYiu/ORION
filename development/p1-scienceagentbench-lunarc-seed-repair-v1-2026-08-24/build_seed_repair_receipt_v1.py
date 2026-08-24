#!/usr/bin/env python3
"""Build the bounded top-level receipt from retained local artifacts."""

import argparse
import hashlib
import json
from pathlib import Path


def load(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = args.packet_dir
    source = load(packet / "SOURCE_CANONICALIZATION_V1.json")
    failed_energy = load(packet / "remote-job-3534108/GPU_ENERGY_RECEIPT_POSTHOC_V1.json")
    result_job = load(packet / "remote-job-3534123/JOB_RECEIPT_V1.json")
    primary = load(packet / "remote-job-3534123/primary_cache_off/CONDITION_RECEIPT_V1.json")
    negative = load(packet / "remote-job-3534123/negative_control_cache_on/CONDITION_RECEIPT_V1.json")
    cleanup = load(packet / "REMOTE_CLEANUP_RECEIPT_V1.json")
    terminal = (packet / "remote-job-3534123/TERMINAL.txt").read_text().strip()

    receipt = {
        "schema": "orion.p1.scienceagentbench.lunarc-direct-seed-repair.v1",
        "status": "PASS_BOUNDED_DIRECT_COMPLETION_CACHE_OFF_SEED_REPAIR",
        "terminal": terminal,
        "source_adverse_evidence": {
            "source_pr": 1130,
            "source_commit": "8c1f5c88bda5da7dc192c40dc92698c19fbb57ba",
            "canonicalization_status": source["status"],
            "request_raw_bytes_identical": source["comparison"]["request_raw_bytes_identical"],
            "response_text_identical": source["comparison"]["response_text_identical"],
            "derived_prompt_token_prefixes_identical": source["comparison"]["derived_prompt_token_prefixes_identical"],
            "derived_generated_token_arrays_identical": source["comparison"]["derived_generated_token_arrays_identical"],
            "first_generated_token_difference_index": source["comparison"]["first_generated_token_difference_index"],
        },
        "runtime": result_job["runtime"],
        "model": {
            "repository": "unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF",
            "revision": "b17cb02dd882d5b6ab62fc777ad2995f19668350",
            "filename": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
            "bytes": 18556689568,
            "sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
        },
        "jobs": {
            "3534108": {
                "state": "CANCELLED by 6350",
                "allocation_elapsed_seconds": 149,
                "batch_exit_code": "0:9",
                "disposition": "NOT_RESULT_BEARING_CPU_FALLBACK_CANCELLED_AFTER_MISSING_GGML_BACKEND_PATH",
                "exact_warning": "warning: no usable GPU found, --gpu-layers option will be ignored",
                "partial_primary_receipt_retained": True,
                "partial_negative_control_requests_completed": 1,
                "posthoc_sampled_telemetry": failed_energy,
            },
            "3534123": {
                "state": "COMPLETED",
                "allocation_elapsed_seconds": 63,
                "exit_code": "0:0",
                "disposition": "RESULT_BEARING_EXACT_CUDA_BACKEND_BOUND",
                "job_receipt_sha256": digest(packet / "remote-job-3534123/JOB_RECEIPT_V1.json"),
            },
        },
        "primary_cache_off": {
            "status": primary["status"],
            "request_order": primary["request_order"],
            "temperature": 0.2,
            "within_seed_token_array_identity": primary["gates"]["within_seed_token_array_identity"],
            "within_seed_content_identity": primary["gates"]["within_seed_content_identity"],
            "between_seed_token_array_sensitivity": primary["gates"]["between_seed_token_array_sensitivity"],
            "cache_n_values": primary["gates"]["cache_n_values"],
            "prompt_n_values": primary["gates"]["prompt_n_values"],
            "seed_101_token_array_sha256": primary["records"][0]["token_array_sha256"],
            "seed_202_token_array_sha256": primary["records"][1]["token_array_sha256"],
            "condition_receipt_sha256": digest(packet / "remote-job-3534123/primary_cache_off/CONDITION_RECEIPT_V1.json"),
        },
        "negative_control_cache_on": {
            "status": negative["status"],
            "cache_n_values": negative["gates"]["cache_n_values"],
            "prompt_n_values": negative["gates"]["prompt_n_values"],
            "within_seed_token_array_identity": negative["gates"]["within_seed_token_array_identity"],
            "condition_receipt_sha256": digest(packet / "remote-job-3534123/negative_control_cache_on/CONDITION_RECEIPT_V1.json"),
        },
        "diagnostics": {
            "cublas_workspace_config": "NOT_RUN_PRIMARY_CACHE_OFF_PASSED",
            "flash_attention_off": "NOT_RUN_PRIMARY_CACHE_OFF_PASSED",
            "greedy_substitution": "FORBIDDEN_AND_NOT_RUN",
        },
        "resources": {
            "slurm_top_level_gpu_allocation_elapsed_seconds_total": 212,
            "slurm_batch_elapsed_seconds_total": 243,
            "sampled_allocation_gpu_seconds_total": failed_energy["gpu_seconds_sampled"] + result_job["gpu_telemetry"]["gpu_seconds_sampled"],
            "sample_integrated_energy_wh_total": failed_energy["energy_wh_estimate"] + result_job["gpu_telemetry"]["energy_wh_estimate"],
            "maximum_vram_mib_result_job": result_job["gpu_telemetry"]["max_memory_used_mib"],
            "result_job_gpu": result_job["gpu_telemetry"]["gpu_name"],
            "result_job_gpu_uuid": result_job["gpu_telemetry"]["gpu_uuid"],
            "slurm_consumed_energy_raw_both_jobs": 0,
        },
        "cost": {
            "billed_usd": None,
            "status": "CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE",
            "gpu_seconds_and_sampled_energy_are_not_currency": True,
        },
        "cleanup": cleanup,
        "artifacts": {
            "source_canonicalization_sha256": digest(packet / "SOURCE_CANONICALIZATION_V1.json"),
            "remote_job_3534108_manifest_sha256": digest(packet / "remote-job-3534108/REMOTE_PARTIAL_SHA256SUMS"),
            "remote_job_3534123_manifest_sha256": digest(packet / "remote-job-3534123/REMOTE_RUN_SHA256SUMS"),
            "cleanup_receipt_sha256": digest(packet / "REMOTE_CLEANUP_RECEIPT_V1.json"),
        },
        "forbidden_inputs": result_job["forbidden_inputs"],
        "limitations": [
            "Synthetic nonbenchmark infrastructure witness only; no protected task, outcome, gold program, evaluator, rubric, or credential was opened.",
            "The pass discriminates one direct llama-server cache-off route on one A40 and one fixture; it does not erase or rewrite PR #1130's adverse Ollama-route evidence.",
            "Cache-on negative control showed replay failure for seed 101 after cache reuse; cache-enabled direct inference is not promoted.",
            "No official ScienceAgentBench execution, task-quality, superiority, manuscript, or publication claim follows from this receipt.",
        ],
        "scientific_authority_delta": "NONE",
    }
    args.output.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n")
    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
