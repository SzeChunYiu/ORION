#!/usr/bin/env python3
"""Validate the body-free job-3537988 submission-fixture failure packet."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "JOB_3537988_SUBMIT_ROOT_CANNOT_CHECK_V1.json"
MANIFEST = ROOT / "RESULT_EXPORT_MANIFEST_V1.json"
SHA256SUMS = ROOT / "SHA256SUMS"

EXPECTED_DETAIL = "SLURM_SUBMIT_DIR differs from the exact successor root"
EXPECTED_DETAIL_SHA256 = (
    "1e0b0ccad8cab36771b3dc63311de1f26ba7a08dc692d14a02fa47ce1780b759"
)
EXPECTED_TERMINAL = (
    "P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_TRAMPOLINE_V1_CANNOT_CHECK "
    "failure_code=SUBMIT_ROOT_INVALID "
    "detail_sha256=1e0b0ccad8cab36771b3dc63311de1f26ba7a08dc692d14a02fa47ce1780b759"
)
EXPECTED_SOURCES = {
    "JOB_3537988_FIRST_CUSTODY.txt": (
        2477,
        "83744dc918e5d7fdd5f620661cb64b47cbae70c1c43bfe18156d23e985da5aed",
    ),
    "REMOTE_DEPLOYMENT_EVIDENCE.txt": (
        5708,
        "afaedbc4cde0f1413a2040116be4b4fc073a59216d9c017b9c3e1cf93d349851",
    ),
    "REMOTE_SUBMIT_SCRIPT_V1.sh": (
        1396,
        "7f822f1c2fa78f882cf824e9efc2277bda462a31bd139a5c92a6e5ceebe5f5f3",
    ),
    "SUBMISSION_EVIDENCE.txt": (
        313,
        "834c02dbf7cf1d231ae86b1e8902907cbab481db4dcb585e98fc66060adff6a9",
    ),
    "slurm-3537988.err": (
        172,
        "aedf4ea5358a0d37bc6f1ddbc3b78b0e392adab3a1093b241665961c2bee495c",
    ),
    "slurm-3537988.out": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
}
EXPECTED_EXTERNAL_LANES = {
    "v7_freeze": {
        "lane": "../p1-scienceagentbench-gpu-visibility-diagnostic-v7-2026-08-25",
        "result_commit": "87a1f6f76dcefbc79d00c397a5aa9c7047a760b7",
        "files": {
            "BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json": (
                3849,
                "075eb092bc5a66e5a57fb30c2c7c40eba245839485534015d0c53eca1b4aaf9b",
            ),
            "SHA256SUMS": (
                1133,
                "5826bbddb9a93cf3f10f1e613a8c025fdfa636b4c8f83d8e25c275745d1fc023",
            ),
            "run_gpu_visibility_diagnostic_v1.sh": (
                14103,
                "f1fea01c96e212df8ed3c0220e693dccfdfbd9ae808eff11aaff19f2bde43414",
            ),
        },
    },
    "v6_deployment_validation_failure": {
        "lane": "../p1-scienceagentbench-gpu-visibility-diagnostic-v6-deployment-validation-result-2026-08-25",
        "result_commit": "598fa94273349094848659b7e3357a494e294b5a",
        "files": {
            "RESULT_EXPORT_MANIFEST_V1.json": (
                1743,
                "26e76cb210c998440ffc16c8dedbdc72a8b294e7ba8e8db8efe37641530cce88",
            ),
            "SHA256SUMS": (
                669,
                "5f70406596941090d200af627055fb6ba663b9b6c3f1869d130d7cc880071c42",
            ),
        },
    },
    "v5_job_3537915_scientific_predecessor": {
        "lane": "../p1-scienceagentbench-backend-canonical-map-discriminator-v5-job-3537915-result-2026-08-25",
        "result_commit": "9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67",
        "files": {
            "RESULT_EXPORT_MANIFEST_V2.json": (
                5322,
                "9ffdb5135cf4848863cb49d604a86af7747cbbaf7a241bba627c8f460d33decd",
            ),
            "SHA256SUMS": (
                1728,
                "c169ef799b79ec6c3537e32d61f66fbf9bb3628d82484762b3d2b60fe7841434",
            ),
        },
    },
}
EXPECTED_PAYLOAD_NAMES = {
    "DEVELOPMENT_PACKET.md",
    "JOB_3537988_FIRST_CUSTODY.txt",
    "JOB_3537988_SUBMIT_ROOT_CANNOT_CHECK_V1.json",
    "REMOTE_DEPLOYMENT_EVIDENCE.txt",
    "REMOTE_SUBMIT_SCRIPT_V1.sh",
    "SUBMISSION_EVIDENCE.txt",
    "slurm-3537988.err",
    "slurm-3537988.out",
    "validate_job_3537988_submit_root_failure_v1.py",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_json(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ValueError(f"{path.name} must have exactly one final LF")
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=reject_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"nonfinite JSON constant: {token}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain one JSON object")
    canonical = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"
    if raw != canonical:
        raise ValueError(f"{path.name} is not exact canonical JSON")
    return raw, value


def validate_sources(result: dict[str, Any]) -> None:
    if set(result["source_bindings"]) != set(EXPECTED_SOURCES):
        raise ValueError("result source binding set differs")
    for name, (expected_bytes, expected_sha256) in EXPECTED_SOURCES.items():
        raw = (ROOT / name).read_bytes()
        if (len(raw), sha256_bytes(raw)) != (expected_bytes, expected_sha256):
            raise ValueError(f"retained source differs: {name}")
        if result["source_bindings"][name] != {
            "bytes": expected_bytes,
            "sha256": expected_sha256,
        }:
            raise ValueError(f"result source binding differs: {name}")

    if (ROOT / "slurm-3537988.out").read_bytes() != b"":
        raise ValueError("raw Slurm stdout is not exact empty bytes")
    if (ROOT / "slurm-3537988.err").read_bytes() != (
        EXPECTED_TERMINAL.encode("ascii") + b"\n"
    ):
        raise ValueError("raw Slurm stderr differs")


def validate_external_lanes(result: dict[str, Any]) -> None:
    observed = result["external_lane_bindings"]
    if set(observed) != set(EXPECTED_EXTERNAL_LANES):
        raise ValueError("external lane binding set differs")
    for label, expected_lane in EXPECTED_EXTERNAL_LANES.items():
        lane = observed[label]
        if lane["lane"] != expected_lane["lane"]:
            raise ValueError(f"external lane path differs: {label}")
        if lane["result_commit"] != expected_lane["result_commit"]:
            raise ValueError(f"external lane commit differs: {label}")
        if set(lane["files"]) != set(expected_lane["files"]):
            raise ValueError(f"external lane file set differs: {label}")
        lane_root = ROOT / expected_lane["lane"]
        for name, (expected_bytes, expected_sha256) in expected_lane["files"].items():
            raw = (lane_root / name).read_bytes()
            if (len(raw), sha256_bytes(raw)) != (expected_bytes, expected_sha256):
                raise ValueError(f"external lane bytes differ: {label}/{name}")
            if lane["files"][name] != {
                "bytes": expected_bytes,
                "sha256": expected_sha256,
            }:
                raise ValueError(f"external lane result binding differs: {label}/{name}")


def validate_evidence_text() -> None:
    deployment = (ROOT / "REMOTE_DEPLOYMENT_EVIDENCE.txt").read_text("utf-8")
    for required in (
        "P1_V7_ARCHIVE_PASS merge=87a1f6f76dcefbc79d00c397a5aa9c7047a760b7 bytes=368640 sha256=88017af9faa0ed4d020c155af026a2edc597146c872b8b77550cc977bff2d6d8 members=42 regular_files=38",
        "P1_V7_DEPLOYMENT_MODE_SEAL_PASS regular=0400 entry=0500 directories=0500",
        "P1_V7_DEPLOYMENT_POST_VALIDATION_INTEGRITY_PASS",
        "P1_V7_POST_VALIDATION_ABSENT label=RUN",
        "P1_V7_POST_VALIDATION_ABSENT label=OUTPUT",
        "P1_V7_POST_VALIDATION_ABSENT label=LOG",
        "P1_V7_DEPLOYMENT_READY",
    ):
        if required not in deployment:
            raise ValueError(f"deployment evidence missing: {required}")
    if deployment.count("P1_V7_DEPLOYMENT_VALIDATION_PASS label=") != 4:
        raise ValueError("deployment validator mode count differs")

    submission = (ROOT / "SUBMISSION_EVIDENCE.txt").read_text("utf-8")
    if "P1_V7_SUBMISSION_PASS job=3537988" not in submission:
        raise ValueError("submission evidence job differs")
    if "3537988 p1_sab_gpu_visibility_v1   PENDING" not in submission:
        raise ValueError("submission evidence initial queue state differs")

    custody = (ROOT / "JOB_3537988_FIRST_CUSTODY.txt").read_text("utf-8")
    for required in (
        "label=RUN state=ABSENT",
        "label=OUTPUT state=ABSENT",
        "label=LOG type=directory mode=700",
        "FILE state=PRESENT bytes=0 sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "FILE state=PRESENT bytes=172 sha256=aedf4ea5358a0d37bc6f1ddbc3b78b0e392adab3a1093b241665961c2bee495c",
        "FILE state=ABSENT path=",
        EXPECTED_TERMINAL,
        "3537988|p1_sab_gpu_visibility_v1|FAILED|2:0|0|cg15|billing=1,cpu=1,gres/gpu:a40=1,gres/gpu=1,mem=4G,node=1",
    ):
        if required not in custody:
            raise ValueError(f"first-custody evidence missing: {required}")

    submit_script = (ROOT / "REMOTE_SUBMIT_SCRIPT_V1.sh").read_text("utf-8")
    if 'submit_line=$(/usr/bin/sbatch --export=NIL \\\n' not in submit_script:
        raise ValueError("submission script sbatch shape differs")
    if '--chdir="$ROOT"' not in submit_script:
        raise ValueError("submission script chdir binding differs")
    if '(cd "$ROOT"' in submit_script:
        raise ValueError("submission script unexpectedly invokes sbatch from ROOT")


def validate_result(result: dict[str, Any]) -> None:
    if result["schema_version"] != (
        "orion.p1.scienceagentbench.gpu-visibility-diagnostic-job-3537988-"
        "submit-root-failure.v1"
    ):
        raise ValueError("result schema differs")
    if result["status"] != "CANNOT_CHECK_V7_SUBMISSION_FIXTURE":
        raise ValueError("result status differs")
    if result["base_merge_commit"] != "87a1f6f76dcefbc79d00c397a5aa9c7047a760b7":
        raise ValueError("result base merge commit differs")
    if result["failure"] != {
        "code": "SUBMIT_ROOT_INVALID",
        "detail_plaintext": EXPECTED_DETAIL,
        "detail_sha256": EXPECTED_DETAIL_SHA256,
        "terminal": EXPECTED_TERMINAL,
    }:
        raise ValueError("result failure binding differs")
    if len(EXPECTED_DETAIL.encode("utf-8")) != 54:
        raise ValueError("exact failure detail byte count differs")
    if sha256_bytes(EXPECTED_DETAIL.encode("utf-8")) != EXPECTED_DETAIL_SHA256:
        raise ValueError("exact failure detail hash differs")
    if result["job"] != {
        "allocated_gpu_count": 1,
        "allocated_gpu_scope": "SCHEDULER_A40_GRES_ONLY__NO_GPU_VISIBILITY_EVIDENCE",
        "elapsed_seconds": 0,
        "exit_code": "2:0",
        "job_id": "3537988",
        "node": "cg15",
        "scheduler_gpu_allocation_seconds": 0,
        "state": "FAILED",
    }:
        raise ValueError("result job binding differs")
    if result["accounting_after_job_3537988"] != {
        "body_free_discriminator_scheduler_gpu_seconds": 170,
        "body_free_discriminator_submissions_completed": 3,
        "combined_scheduler_gpu_seconds": 260,
        "job_3537988_scheduler_gpu_seconds": 0,
        "prior_body_free_discriminator_scheduler_gpu_seconds": 170,
        "prior_body_free_discriminator_submissions_completed": 2,
        "prior_combined_scheduler_gpu_seconds": 260,
        "protected_generation_attempts_consumed": 0,
        "protected_infrastructure_scheduler_gpu_seconds": 90,
        "protected_infrastructure_submissions_completed": 3,
        "v7_body_free_submissions_added": 1,
    }:
        raise ValueError("result accounting differs")
    if result["custody"] != {
        "log": {"mode": "0700", "state": "PRESENT"},
        "output": "ABSENT",
        "receipt_cannot_check": "ABSENT",
        "receipt_success": "ABSENT",
        "root": {"mode": "0500", "state": "SEALED_PRESERVED"},
        "run": "ABSENT",
        "stderr": {
            "bytes": 172,
            "mode": "0600",
            "sha256": "aedf4ea5358a0d37bc6f1ddbc3b78b0e392adab3a1093b241665961c2bee495c",
        },
        "stdout": {
            "bytes": 0,
            "mode": "0600",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
    }:
        raise ValueError("result custody differs")
    if result["deployment"] != {
        "archive": {
            "bytes": 368640,
            "sha256": "88017af9faa0ed4d020c155af026a2edc597146c872b8b77550cc977bff2d6d8",
        },
        "clean_validation_passed": True,
        "deployment_root": (
            "/projects/hep/fs10/scratch/scyiu/"
            "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
            "repo-gpu-visibility-v7-20260825"
        ),
        "post_validation_integrity_passed": True,
        "post_validation_log_absent_before_creation": True,
        "post_validation_output_absent": True,
        "post_validation_run_absent": True,
    }:
        raise ValueError("result deployment binding differs")
    root_cause = result["root_cause"]
    if root_cause["classification"] != "OPERATOR_HANDOFF_SUBMISSION_FIXTURE_DEFECT":
        raise ValueError("root-cause classification differs")
    if root_cause["sbatch_invoked_outside_frozen_root"] is not True:
        raise ValueError("outside-ROOT invocation is not bound")
    if root_cause["slurm_chdir_sets_slurm_submit_dir"] is not False:
        raise ValueError("Slurm chdir semantic boundary differs")
    if root_cause["diagnostic_core_started"] is not False:
        raise ValueError("diagnostic core start boundary differs")
    if root_cause["nvidia_smi_commands_executed"] != 0:
        raise ValueError("nvidia-smi execution boundary differs")
    if result["truthful_scope"] != {
        "completion_requests": 0,
        "diagnostic_network_accessed": False,
        "generation_invocations": 0,
        "gpu_visibility_evidence_collected": False,
        "model_started": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scientific_authority_delta": "NONE",
        "task_bearing_requests": 0,
        "tokenize_requests": 0,
    }:
        raise ValueError("result truthful-scope boundary differs")
    if result["production_admissibility"] != "CANNOT_CHECK":
        raise ValueError("production admissibility differs")
    if any(result["no_promotion"].values()):
        raise ValueError("no-promotion boundary differs")


def validate_manifest() -> None:
    _, manifest = strict_json(MANIFEST)
    if manifest["schema_version"] != (
        "orion.p1.scienceagentbench.gpu-visibility-diagnostic-job-result-"
        "export-manifest.v1"
    ):
        raise ValueError("manifest schema differs")
    if manifest["status"] != "PASS_JOB_3537988_FAILURE_EXPORT_INTEGRITY":
        raise ValueError("manifest status differs")
    if manifest["authority"] != (
        "BODY_FREE_V7_JOB_3537988_SUBMISSION_FIXTURE_FAILURE_EXPORT_INTEGRITY_"
        "ONLY__NO_GPU_VISIBILITY_PROTECTED_EXECUTION_TASK_OUTCOME_PRODUCTION_"
        "CAUSAL_OR_SCIENTIFIC_AUTHORITY"
    ):
        raise ValueError("manifest authority differs")
    if manifest["base_merge_commit"] != "87a1f6f76dcefbc79d00c397a5aa9c7047a760b7":
        raise ValueError("manifest base merge commit differs")
    if manifest["external_lane_bindings_in_result"] is not True:
        raise ValueError("manifest external-lane binding declaration differs")
    if manifest["lane"] != (
        "development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-"
        "job-3537988-result-2026-08-25"
    ):
        raise ValueError("manifest lane differs")
    if manifest["manifested_payload_exclusions"] != [
        "RESULT_EXPORT_MANIFEST_V1.json",
        "SHA256SUMS",
    ]:
        raise ValueError("manifest exclusions differ")
    if manifest["manifested_payload_file_count"] != len(EXPECTED_PAYLOAD_NAMES):
        raise ValueError("manifest payload count differs")
    if manifest["total_exported_file_count"] != len(EXPECTED_PAYLOAD_NAMES) + 2:
        raise ValueError("manifest total file count differs")
    payloads = manifest["manifested_payload_files"]
    if set(payloads) != EXPECTED_PAYLOAD_NAMES:
        raise ValueError("manifest payload set differs")
    for name in EXPECTED_PAYLOAD_NAMES:
        path = ROOT / name
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o644:
            raise ValueError(f"payload mode/type differs: {name}")
        raw = path.read_bytes()
        if payloads[name] != {
            "bytes": len(raw),
            "mode": "0644",
            "sha256": sha256_bytes(raw),
        }:
            raise ValueError(f"manifest payload binding differs: {name}")
    if manifest["sha256sums_scope"] != {
        "covered_file_count": len(EXPECTED_PAYLOAD_NAMES) + 1,
        "covers_manifested_payload_files": True,
        "excluded_self": "SHA256SUMS",
        "includes_manifest": True,
    }:
        raise ValueError("manifest SHA256SUMS scope differs")
    if manifest["truthful_scope"] != {
        "body_free_submissions_added": 1,
        "gpu_visibility_evidence_collected": False,
        "jobs_recorded": 1,
        "production_admissibility": "CANNOT_CHECK",
        "protected_generation_attempts_consumed": 0,
        "scheduler_gpu_seconds_added": 0,
        "scientific_authority_delta": "NONE",
    }:
        raise ValueError("manifest truthful scope differs")

    sums_raw = SHA256SUMS.read_bytes()
    if not sums_raw.endswith(b"\n") or sums_raw.endswith(b"\n\n"):
        raise ValueError("SHA256SUMS final-LF framing differs")
    lines = sums_raw.decode("ascii").splitlines()
    expected_names = sorted(EXPECTED_PAYLOAD_NAMES | {MANIFEST.name})
    parsed = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if match is None:
            raise ValueError("SHA256SUMS line grammar differs")
        parsed.append((match.group(1), match.group(2)))
    if [name for _, name in parsed] != expected_names:
        raise ValueError("SHA256SUMS name/order set differs")
    for digest, name in parsed:
        if sha256_bytes((ROOT / name).read_bytes()) != digest:
            raise ValueError(f"SHA256SUMS digest differs: {name}")


def main() -> int:
    _, result = strict_json(RESULT)
    validate_sources(result)
    validate_external_lanes(result)
    validate_evidence_text()
    validate_result(result)
    validate_manifest()
    print(
        "P1_SAB_GPU_VISIBILITY_JOB_3537988_RESULT_VALIDATION_PASS "
        "sources=6 payloads=9 scheduler_gpu_seconds_added=0 "
        "body_free_submissions_added=1 gpu_evidence=NONE "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
