#!/usr/bin/env python3
"""Focused fail-closed validation for the adverse open-weight smoke packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Union


ROOT = Path(__file__).resolve().parent
MODEL_SHA = "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad"
RUNTIME_SHA = "d0758d38ac5882a2c68fd930d0c1220af1952469fa9f30c268746d4021709bf4"


def load(path: Union[Path, str]) -> dict:
    path = ROOT / path if isinstance(path, str) else path
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(directory: Path, name: str) -> None:
    for line in (directory / name).read_text().splitlines():
        expected, rel = line.split("  ", 1)
        assert digest(directory / rel) == expected, f"{directory.name}/{rel}"


def main() -> int:
    fixture = load("SYNTHETIC_FIXTURE_V1.json")
    pin = load("PINNED_ROUTE_V1.json")
    receipt = load("OPENWEIGHT_GPU_SMOKE_RECEIPT_V1.json")
    cleanup = load("REMOTE_CLEANUP_RECEIPT_V1.json")
    failed_job = ROOT / "remote-job-3533950"
    smoke_job = ROOT / "remote-job-3533966"
    smoke = load(smoke_job / "raw/SMOKE_RECEIPT_V1.json")
    fail_1 = load(failed_job / "JOB_FAILURE_V1.json")
    fail_2 = load(smoke_job / "JOB_FAILURE_V1.json")
    energy_1 = load(failed_job / "GPU_ENERGY_RECEIPT_V1.json")
    energy_2 = load(smoke_job / "GPU_ENERGY_RECEIPT_V1.json")

    assert fixture["official_task_content"] is False
    assert fixture["outcomes_opened"] is False
    assert set(fixture["arm_seeds"].values()) == {101, 202, 303}
    assert pin["model"]["expected_sha256"] == MODEL_SHA
    assert pin["runtime"]["client_version"] == "0.32.14"
    assert pin["runtime"]["executable_sha256"] == RUNTIME_SHA
    assert pin["network"]["listen_scope"] == "LOOPBACK_ONLY"
    assert pin["cost_contract"]["billed_usd"] is None

    assert smoke["status"] == "FAIL"
    assert smoke["totals"] == {
        "generated_tokens": 1374,
        "ollama_total_duration_ns": 36817204485,
        "prompt_tokens": 28974,
        "requests": 11,
    }
    calls = {call["call_id"]: call for call in smoke["calls"]}
    assert calls["rr_phase1"]["done_reason"] == "length"
    assert calls["rr_phase1"]["eval_count"] == 512
    replay = smoke["checks"]["same_seed_replay"]
    assert replay["status"] == "FAIL"
    assert len(set(replay["request_sha256s"])) == 1
    assert len(set(replay["response_text_sha256s"])) == 2
    sensitivity = smoke["checks"]["different_seed_sensitivity"]
    assert sensitivity["status"] == "PASS"
    assert sensitivity["distinct_response_count"] == 3
    context = smoke["checks"]["long_context_no_silent_truncation_witness"]
    assert context["status"] == "PASS"
    assert context["reported_prompt_tokens"] == 27764
    assert context["markers_all_reproduced"] is True
    assert context["markers_in_order"] is True
    assert context["reported_prompt_tokens"] < context["requested_num_ctx"] == 32768
    assert smoke["forbidden_inputs"] == {
        "protected_archive_opened": False,
        "benchmark_task_opened": False,
        "outcome_opened": False,
        "evaluator_opened": False,
        "credential_opened": False,
    }

    assert fail_1["slurm_job_id"] == "3533950" and fail_1["exit_code"] == 1
    assert fail_2["slurm_job_id"] == "3533966" and fail_2["exit_code"] == 2
    assert "zip() takes no keyword arguments" in (failed_job / "harness.stderr").read_text()
    assert "\"status\": \"FAIL\"" in (smoke_job / "harness.stdout").read_text()
    assert "3533950|p1_sab_ow_v1|gpua40i|lu2026-2-51|FAILED|1:0|363" in (failed_job / "SACCT_V1.txt").read_text()
    assert "3533966|p1_sab_ow_v1|gpua40i|lu2026-2-51|FAILED|2:0|288" in (smoke_job / "SACCT_V1.txt").read_text()
    assert MODEL_SHA in (smoke_job / "OLLAMA_STORE_SHA256SUMS").read_text()
    assert "127.0.0.1:11471" in (smoke_job / "SOCKETS_BEFORE_GENERATION.txt").read_text()

    for energy in (energy_1, energy_2):
        assert energy["status"] == "PASS_SAMPLED_TELEMETRY"
        assert energy["sample_count"] >= 2
        assert energy["gpu_seconds_sampled"] > 0
        assert energy["energy_wh_estimate"] > 0
        assert energy["max_memory_used_mib"] > 22000
        assert energy["billed_usd"] is None

    assert receipt["status"] == "ADVERSE_RR_LENGTH_AND_SAME_SEED_REPLAY_MISMATCH"
    assert receipt["model"]["observed_sha256"] == MODEL_SHA
    assert receipt["model"]["observed_bytes"] == 18556689568
    assert receipt["runtime"]["observed_sha256"] == RUNTIME_SHA
    assert receipt["slurm"]["allocated_gpu_seconds_total"] == 651
    assert receipt["probes"]["same_seed_replay"]["status"] == "FAIL"
    assert receipt["probes"]["different_seed_sensitivity"]["status"] == "PASS"
    assert receipt["probes"]["long_context_no_silent_truncation_witness"]["status"] == "PASS"
    assert receipt["cost"]["billed_usd"] is None
    assert receipt["cost"]["status"] == "CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE"
    assert receipt["cost"]["gpu_seconds_recorded_separately"] is True
    assert receipt["cost"]["sampled_energy_recorded_separately"] is True
    assert receipt["forbidden_inputs"] == {
        "protected_archive_opened": False,
        "benchmark_task_opened": False,
        "outcome_opened": False,
        "gold_program_opened": False,
        "evaluator_opened": False,
        "rubric_opened": False,
        "credential_opened": False,
    }
    assert receipt["scientific_authority_delta"] == "NONE"

    assert cleanup["status"] == "PASS_REMOTE_ROOT_REMOVED"
    assert cleanup["root_exists_after_cleanup"] is False
    assert cleanup["bytes_removed"] == 18565097014
    assert receipt["cleanup"] == cleanup
    assert "owner_authoritative_currency_conversion=NOT_EXPOSED" in (ROOT / "COST_AUTHORITY_PROBE_V1.txt").read_text()

    verify_manifest(failed_job, "REMOTE_RUN_SHA256SUMS")
    verify_manifest(smoke_job, "REMOTE_RUN_SHA256SUMS")

    manifest = (ROOT / "SHA256SUMS").read_text().splitlines()
    entries = {}
    for line in manifest:
        expected, rel = line.split("  ", 1)
        entries[rel] = expected
    required = {
        "DEVELOPMENT_PACKET.md", "HANDOFF_V1.md", "PINNED_ROUTE_V1.json",
        "SYNTHETIC_FIXTURE_V1.json", "TOKENIZER_PRECHECK_RECEIPT_V1.json",
        "OPENWEIGHT_GPU_SMOKE_RECEIPT_V1.json", "REMOTE_CLEANUP_RECEIPT_V1.json",
        "COST_AUTHORITY_PROBE_V1.txt", "SCHEDULER_REPAIR_RECEIPT_V1.txt",
        "FAILURE_AND_REPAIR_LOG.md", "run_lunarc_openweight_smoke_v1.sh",
        "openweight_synthetic_smoke_v1.py", "summarize_gpu_telemetry_v1.py",
        "validate_openweight_packet_v1.py",
    }
    assert required <= set(entries)
    for rel, expected in entries.items():
        assert rel != "SHA256SUMS"
        assert digest(ROOT / rel) == expected, rel

    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
