#!/usr/bin/env python3
"""Validate only the retained body-free job-3537915 CANNOT_CHECK certificate.

The validator reads the six body-free result evidence files beside it and the
merged V5 freeze packet.  It never contacts Slurm, opens a protected body, or
issues tokenize, completion, generation, evaluator, or outcome operations.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
V5_ROOT = ROOT.parent / "p1-scienceagentbench-backend-canonical-map-discriminator-v5-2026-08-25"
CERTIFICATE = ROOT / "JOB_3537915_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V2.json"
LIVE_RECEIPT = ROOT / "JOB_3537915_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json"
OPERATOR_EVIDENCE = ROOT / "JOB_3537915_OPERATOR_EVIDENCE.txt"
DEPLOYMENT_EVIDENCE = ROOT / "DEPLOYMENT_PRE_SUBMIT_EVIDENCE.txt"
SUBMISSION_EVIDENCE = ROOT / "SUBMISSION_EVIDENCE.txt"
SLURM_STDOUT = ROOT / "slurm-3537915.out"
SLURM_STDERR = ROOT / "slurm-3537915.err"

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_STAGES = [
    "CONTRACT_BOUND",
    "RUNTIME_FILES_BOUND",
    "SERVER_STARTED",
    "SERVER_READY_BODY_FREE",
    "CANONICAL_MAP_ATTESTATION_1",
    "SERVER_CLEANUP_PASS",
]
EXPECTED_TERMINAL = (
    "P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK "
    "failure_code=GPU_IDENTITY_INVALID "
    "detail_sha256=37a3b93da155ad4641b63864fd78781f9144c3813a2b02fae9ba0924a98025a2"
)
EXPECTED_SOURCES = {
    "DEPLOYMENT_PRE_SUBMIT_EVIDENCE.txt": (
        11384,
        "050f129a9a24c5de59c61c583b7aff5d61a3ebeb36ea8efbdc698384b97adf13",
    ),
    "JOB_3537915_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json": (
        1883,
        "2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3",
    ),
    "JOB_3537915_OPERATOR_EVIDENCE.txt": (
        6332,
        "9db089f05026ed0417c22d3d9daebb3b8143930cb9bcc28547f9999ab7f925a7",
    ),
    "SUBMISSION_EVIDENCE.txt": (
        2059,
        "8c3309253a4447aa275b8ce95ba8272d8f6664d39a382ec907af10015fa15848",
    ),
    "slurm-3537915.err": (
        172,
        "c80d3ab5044472895eace3c7faa096eaa1f7441108696d98b51c50a10f53870e",
    ),
    "slurm-3537915.out": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
}
EXPECTED_V5_SOURCES = {
    "BACKEND_CANONICAL_MAP_DISCRIMINATOR_CONTRACT_V2.json": (
        8543,
        "1eaf4c9ac3f289ad3ced81e6ae50a861e59469b4b1206ed529fb2c4983de41dd",
    ),
    "BACKEND_CANONICAL_MAP_DISCRIMINATOR_OUTPUT_SCHEMA_V2.json": (
        7482,
        "de5add5dff997c9f345afaf20933262ff57f1d2d5b491fb31086587f6d36408f",
    ),
    "BODY_FREE_EXPORT_MANIFEST_V2.json": (
        3101,
        "7645576c89907e6c23be8814c24d778733eee925981d5f745eb830dac9c964bf",
    ),
    "DEVELOPMENT_PACKET.md": (
        8992,
        "5e62e930d5137bae374c22fcd1935633034bc976ec7ba297e99837def523da75",
    ),
    "HANDOFF_V1.md": (
        7356,
        "89dd0cf8f806a4fdc196e37d5e6cec49690113407c850fe104471da616a42750",
    ),
    "JOB_3537910_PREDECESSOR_BINDING_V1.json": (
        4162,
        "31b9ea69c996a20d09bf06306c833c00c866591729195a21ddfe484dec6a9b1e",
    ),
    "SHA256SUMS": (
        1057,
        "701484eb856a553d75c7e7e6ff97946e1bdf1281e1f200efedf2153700a31165",
    ),
    "SYNTHETIC_VALIDATION_RECEIPT_V2.json": (
        4710,
        "271030043e29ab732a0ad45794967f9c07fba586e4e3ed47478c033bd3a1f088",
    ),
    "backend_canonical_map_discriminator_v2.py": (
        63962,
        "a9b2d77aa98eaaf02d334da2b444cb8f4e788bafb13b951e8369fd2c77fab285",
    ),
    "run_backend_canonical_map_discriminator_v2.sh": (
        14164,
        "62ef2f3b631006458855a9e07a9cd961dcf043deed4a3dafd20ac7e58374b0ff",
    ),
    "validate_backend_canonical_map_discriminator_v2.py": (
        52989,
        "6e7988e78004fa3ce6f5c814223e91cda2b222530d4bd9629e2ad3664c656f64",
    ),
}
EXPECTED_GPU_CAPTURE = {
    "argv": [
        "/usr/bin/nvidia-smi",
        "--query-gpu=index,uuid,name",
        "--format=csv,noheader,nounits",
    ],
    "return_code": 6,
    "status": "COMPLETED",
    "stderr": {
        "bytes": 76,
        "sha256": "0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a",
    },
    "stdout": {
        "bytes": 22,
        "sha256": "cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd",
    },
    "stdout_parse_attempted": False,
}
EXPECTED_CLEANUP = {
    "pid": 137741,
    "process_absent_after_cleanup": True,
    "process_group_absent_after_cleanup": True,
    "process_group_id": 137741,
    "process_started": True,
    "return_code": 0,
    "termination_signal": "SIGTERM",
}
EXPECTED_LOG_BINDINGS = {
    "core_server_streams": {
        "stderr": {
            "bytes": 1641,
            "sha256": "0d40487d172f90e5fb1f83ad7e6fac342486ae9450dfdc9a94239268a3b2e153",
        },
        "stdout": {
            "bytes": 0,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
    },
    "slurm_streams": {
        "stderr": {
            "bytes": 172,
            "sha256": "c80d3ab5044472895eace3c7faa096eaa1f7441108696d98b51c50a10f53870e",
        },
        "stdout": {
            "bytes": 0,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
    },
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


def require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{label} field set differs: {sorted(set(value) ^ expected)}")


def exact_binding(path: Path, expected_bytes: int, expected_sha: str) -> dict[str, Any]:
    raw = path.read_bytes()
    if len(raw) != expected_bytes or sha256_bytes(raw) != expected_sha:
        raise ValueError(f"retained source differs: {path.name}")
    return {"bytes": expected_bytes, "sha256": expected_sha}


def validate_source_bindings(certificate: dict[str, Any]) -> None:
    bindings = certificate["source_bindings"]
    if set(bindings) != set(EXPECTED_SOURCES):
        raise ValueError("certificate source binding set differs")
    for name, (expected_bytes, expected_sha) in EXPECTED_SOURCES.items():
        expected = exact_binding(ROOT / name, expected_bytes, expected_sha)
        if bindings[name] != expected:
            raise ValueError(f"certificate source binding differs: {name}")


def validate_merged_v5_sources(certificate: dict[str, Any]) -> None:
    bindings = certificate["executed_packet"]["merged_v5_source_bindings"]
    if set(bindings) != set(EXPECTED_V5_SOURCES):
        raise ValueError("merged V5 source binding set differs")
    for name, (expected_bytes, expected_sha) in EXPECTED_V5_SOURCES.items():
        expected = exact_binding(V5_ROOT / name, expected_bytes, expected_sha)
        if bindings[name] != expected:
            raise ValueError(f"certificate merged V5 binding differs: {name}")

    sums = (V5_ROOT / "SHA256SUMS").read_bytes()
    if not sums.endswith(b"\n") or sums.endswith(b"\n\n"):
        raise ValueError("merged V5 SHA256SUMS framing differs")
    lines = sums.decode("ascii").splitlines()
    expected_names = sorted(set(EXPECTED_V5_SOURCES) - {"SHA256SUMS"})
    parsed: list[tuple[str, str]] = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if match is None:
            raise ValueError("merged V5 SHA256SUMS grammar differs")
        parsed.append((match.group(1), match.group(2)))
    if [name for _, name in parsed] != expected_names:
        raise ValueError("merged V5 SHA256SUMS name/order set differs")
    for digest, name in parsed:
        if digest != EXPECTED_V5_SOURCES[name][1]:
            raise ValueError(f"merged V5 SHA256SUMS digest differs: {name}")

    _, contract = strict_json(V5_ROOT / "BACKEND_CANONICAL_MAP_DISCRIMINATOR_CONTRACT_V2.json")
    if contract["base_commit"] != "cf002879df0aac27d269d6fa1477818ab507d15a":
        raise ValueError("merged V5 contract base differs")
    if contract["status"] != "FROZEN_NOT_EXECUTED" or contract["submission_authority"] is not False:
        raise ValueError("merged V5 contract authority boundary differs")
    gate = contract["gpu_identity_gate"]
    if gate["failure_code"] != "GPU_IDENTITY_INVALID":
        raise ValueError("merged V5 GPU failure code differs")
    if "NVIDIA_SMI_NONZERO_RETURN" not in gate["completed_call_failure_subcodes"]:
        raise ValueError("merged V5 GPU nonzero-return subcode is absent")
    if gate["parse_policy"]["stdout_parse_attempted_for_nonzero_return"] is not False:
        raise ValueError("merged V5 nonzero-return parse policy differs")

    _, schema = strict_json(
        V5_ROOT / "BACKEND_CANONICAL_MAP_DISCRIMINATOR_OUTPUT_SCHEMA_V2.json"
    )
    condition = schema["cannot_check"]["gpu_failure_variants"]["completed_call"][
        "subcode_conditions"
    ]["NVIDIA_SMI_NONZERO_RETURN"]
    if condition != {
        "return_code": "NONZERO",
        "stderr.bytes": "ANY_NONNEGATIVE_INTEGER",
        "stdout_parse_attempted": False,
    }:
        raise ValueError("merged V5 output schema nonzero-return condition differs")


def validate_live_receipt(certificate: dict[str, Any]) -> bytes:
    raw, receipt = strict_json(LIVE_RECEIPT)
    require_exact_keys(
        receipt,
        {
            "schema_version",
            "authority",
            "status",
            "base_commit",
            "contract_sha256",
            "completed_stages",
            "server_log_bindings",
            "cleanup",
            "body_free_http_request_types_allowed",
            "protected_packet_bodies_opened",
            "protected_prompt_bodies_opened",
            "tokenize_requests",
            "completion_requests",
            "generation_invocations",
            "official_evaluator_invoked",
            "official_outcomes_opened",
            "production_admissibility",
            "scientific_authority_delta",
            "failure_code",
            "failure_detail_sha256",
            "failure_subcode",
            "gpu_capture",
        },
        "live receipt",
    )
    if receipt["schema_version"] != (
        "orion.p1.scienceagentbench.backend-canonical-map-discriminator-cannot-check.v2"
    ):
        raise ValueError("live receipt schema differs")
    if receipt["authority"] != (
        "BODY_FREE_CANONICAL_MAP_DISCRIMINATOR_FAILURE_ONLY__NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY"
    ):
        raise ValueError("live receipt authority differs")
    if receipt["status"] != "CANNOT_CHECK_BACKEND_CANONICAL_MAP_DISCRIMINATOR":
        raise ValueError("live receipt status differs")
    if receipt["base_commit"] != "cf002879df0aac27d269d6fa1477818ab507d15a":
        raise ValueError("live receipt base differs")
    if receipt["contract_sha256"] != EXPECTED_V5_SOURCES[
        "BACKEND_CANONICAL_MAP_DISCRIMINATOR_CONTRACT_V2.json"
    ][1]:
        raise ValueError("live receipt contract binding differs")
    if receipt["completed_stages"] != EXPECTED_STAGES:
        raise ValueError("live receipt completed stages differ")
    if receipt["failure_code"] != "GPU_IDENTITY_INVALID":
        raise ValueError("live receipt failure code differs")
    if receipt["failure_detail_sha256"] != certificate["failure"]["failure_detail_sha256"]:
        raise ValueError("live receipt failure-detail binding differs")
    if receipt["failure_subcode"] != "NVIDIA_SMI_NONZERO_RETURN":
        raise ValueError("live receipt failure subcode differs")
    if receipt["gpu_capture"] != EXPECTED_GPU_CAPTURE:
        raise ValueError("live receipt completed GPU capture differs")
    if receipt["cleanup"] != EXPECTED_CLEANUP:
        raise ValueError("live receipt cleanup differs")
    if receipt["server_log_bindings"] != EXPECTED_LOG_BINDINGS["core_server_streams"]:
        raise ValueError("live receipt core stream bindings differ")
    if receipt["body_free_http_request_types_allowed"] != ["GET /health", "GET /slots"]:
        raise ValueError("live receipt body-free request allowlist differs")
    for key in (
        "protected_packet_bodies_opened",
        "protected_prompt_bodies_opened",
        "tokenize_requests",
        "completion_requests",
        "generation_invocations",
        "official_outcomes_opened",
    ):
        if receipt[key] != 0 or isinstance(receipt[key], bool):
            raise ValueError(f"live receipt nonzero or mistyped counter: {key}")
    if receipt["official_evaluator_invoked"] is not False:
        raise ValueError("live receipt evaluator boundary differs")
    if receipt["production_admissibility"] != "CANNOT_CHECK":
        raise ValueError("live receipt production boundary differs")
    if receipt["scientific_authority_delta"] != "NONE":
        raise ValueError("live receipt scientific boundary differs")
    return raw


def validate_operator_evidence(receipt_raw: bytes) -> None:
    evidence = OPERATOR_EVIDENCE.read_bytes()
    required = [
        b"3537915                p1_sab_backend_map_v2           FAILED   00:01:24      1:0            cg14",
        b"JobId=3537915 JobName=p1_sab_backend_map_v2",
        b"JobState=FAILED Reason=NonZeroExitCode",
        b"ExitCode=1:0 RunTime=00:01:24",
        b"NodeList=cg14 BatchHost=cg14",
        b"AllocTRES=cpu=8,mem=64G,node=1,billing=8,gres/gpu=1,gres/gpu:a40=1",
        b"600 172 scyiu hep 1 ",
        b"c80d3ab5044472895eace3c7faa096eaa1f7441108696d98b51c50a10f53870e",
        b"600 0 scyiu hep 1 ",
        b"500 scyiu hep 2 ",
        b"400 1883 scyiu hep 1 ",
        b"2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3",
        EXPECTED_TERMINAL.encode("utf-8"),
        receipt_raw.rstrip(b"\n"),
    ]
    if any(item not in evidence for item in required):
        raise ValueError("operator evidence lacks an exact job/log/receipt/custody binding")


def validate_deployment_and_submission_evidence() -> None:
    deployment = DEPLOYMENT_EVIDENCE.read_text(encoding="utf-8")
    required_deployment = [
        "DEPLOYMENT_PASS merge=e47ffa7689e48667d167fe0658b37753ebb67a4c",
        "archive_bytes=215040",
        "archive_sha256=5fcf011c3e6a477eb219449f056c676a90e1472b3868cd2a726ba0ee9426e915",
        "run=ABSENT output=ABSENT log=ABSENT upload=ABSENT",
        "1eaf4c9ac3f289ad3ced81e6ae50a861e59469b4b1206ed529fb2c4983de41dd",
        "de5add5dff997c9f345afaf20933262ff57f1d2d5b491fb31086587f6d36408f",
        "701484eb856a553d75c7e7e6ff97946e1bdf1281e1f200efedf2153700a31165",
        "a9b2d77aa98eaaf02d334da2b444cb8f4e788bafb13b951e8369fd2c77fab285",
        "62ef2f3b631006458855a9e07a9cd961dcf043deed4a3dafd20ac7e58374b0ff",
    ]
    if any(item not in deployment for item in required_deployment):
        raise ValueError("deployment evidence lacks an exact merged V5 binding")

    submission = SUBMISSION_EVIDENCE.read_text(encoding="utf-8")
    required_submission = [
        "SUBMITTED raw_job_id=3537915 job_id=3537915",
        "run_pre_submit=ABSENT output_pre_submit=ABSENT",
        "merge=e47ffa7689e48667d167fe0658b37753ebb67a4c",
        "JobId=3537915 JobName=p1_sab_backend_map_v2",
        "JobState=PENDING Reason=Priority",
        "gres/gpu:a40=1",
    ]
    if any(item not in submission for item in required_submission):
        raise ValueError("submission evidence lacks an exact job/fresh-root binding")


def validate_certificate(certificate: dict[str, Any]) -> None:
    require_exact_keys(
        certificate,
        {
            "schema_version",
            "authority",
            "status",
            "job",
            "executed_packet",
            "receipt_binding",
            "failure",
            "gpu_capture",
            "completed_stages",
            "positive_first_attestation_scope",
            "cannot_check_boundary",
            "cleanup",
            "retained_log_bindings",
            "truthful_scope",
            "no_promotion",
            "accounting",
            "source_bindings",
        },
        "certificate",
    )
    if certificate["schema_version"] != (
        "orion.p1.scienceagentbench.backend-canonical-map-discriminator-job-result-certificate.v2"
    ):
        raise ValueError("certificate schema differs")
    if certificate["authority"] != (
        "BODY_FREE_JOB_RESULT_GPU_CAPTURE_AND_FIRST_ATTESTATION_STAGE_CERTIFICATE_ONLY__"
        "NO_FULL_DISCRIMINATOR_PASS_PROTECTED_EXECUTION_OUTCOME_PRODUCTION_OR_SCIENTIFIC_AUTHORITY"
    ):
        raise ValueError("certificate authority differs")
    if certificate["status"] != "PASS_CERTIFIED_BODY_FREE_JOB_3537915_CANNOT_CHECK":
        raise ValueError("certificate status differs")
    if certificate["job"] != {
        "allocated_gpu_count": 1,
        "allocated_gpu_scope": (
            "SCHEDULER_A40_GRES_ONLY__GPU_CAPTURE_COMPLETED__GPU_IDENTITY_CANNOT_CHECK"
        ),
        "elapsed_seconds": 84,
        "exit_code": "1:0",
        "job_id": "3537915",
        "node": "cg14",
        "scheduler_gpu_allocation_seconds": 84,
        "state": "FAILED",
    }:
        raise ValueError("certificate job record differs")
    executed = certificate["executed_packet"]
    if {key: value for key, value in executed.items() if key != "merged_v5_source_bindings"} != {
        "base_commit": "cf002879df0aac27d269d6fa1477818ab507d15a",
        "contract_sha256": "1eaf4c9ac3f289ad3ced81e6ae50a861e59469b4b1206ed529fb2c4983de41dd",
        "deployed_commit": "e47ffa7689e48667d167fe0658b37753ebb67a4c",
        "deployment_archive": {
            "bytes": 215040,
            "sha256": "5fcf011c3e6a477eb219449f056c676a90e1472b3868cd2a726ba0ee9426e915",
        },
    }:
        raise ValueError("certificate executed packet binding differs")
    expected_receipt = {
        "bytes": 1883,
        "file": LIVE_RECEIPT.name,
        "sha256": "2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3",
    }
    if certificate["receipt_binding"] != expected_receipt:
        raise ValueError("certificate receipt binding differs")
    if certificate["completed_stages"] != EXPECTED_STAGES:
        raise ValueError("certificate completed stages differ")
    if certificate["failure"] != {
        "failure_code": "GPU_IDENTITY_INVALID",
        "failure_detail_sha256": "37a3b93da155ad4641b63864fd78781f9144c3813a2b02fae9ba0924a98025a2",
        "failure_subcode": "NVIDIA_SMI_NONZERO_RETURN",
        "terminal": EXPECTED_TERMINAL,
    }:
        raise ValueError("certificate failure binding differs")
    if not SHA_RE.fullmatch(certificate["failure"]["failure_detail_sha256"]):
        raise ValueError("certificate failure detail is not SHA-256")
    if certificate["gpu_capture"] != EXPECTED_GPU_CAPTURE:
        raise ValueError("certificate GPU capture differs")
    if certificate["cleanup"] != EXPECTED_CLEANUP:
        raise ValueError("certificate cleanup differs")
    if certificate["retained_log_bindings"] != EXPECTED_LOG_BINDINGS:
        raise ValueError("certificate retained log bindings differ")
    positive = certificate["positive_first_attestation_scope"]
    if positive != {
        "claim": (
            "FRESH_BODY_FREE_FIRST_ATTESTATION_ONLY__EXACT_SERVER_PROCESS_ARGV_ENVIRONMENT_AND_"
            "LOOPBACK_LISTENER_PASSED__FROZEN_SERVER_BACKEND_MODEL_IDENTITIES_PRESENT_UNDER_ONLY_"
            "ALLOWED_LOGICAL_OR_CANONICAL_PATHS_WITH_MATCHING_DEVICE_INODE"
        ),
        "first_attestation_details_retained": False,
        "first_attestation_passed": True,
        "observed_mapping_paths_or_segments_retained": False,
        "semantic_basis": "EXECUTED_V5_MODULE_SHA256_AND_ORDERED_COMPLETED_STAGE",
    }:
        raise ValueError("certificate first-attestation scope differs")
    if certificate["cannot_check_boundary"] != {
        "discriminator_pass": False,
        "final_listener_rebind_completed": False,
        "final_runtime_file_rebind_completed": False,
        "gpu_capture_completed": True,
        "gpu_identity_bound": False,
        "mapping_reattestation_byte_identical": False,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
        "second_mapping_attestation_completed": False,
    }:
        raise ValueError("certificate CANNOT_CHECK boundary differs")
    if certificate["no_promotion"] != {
        "job_3537893_promoted": False,
        "job_3537910_promoted": False,
        "protected_retry_authorized": False,
        "relation_to_prior_jobs": (
            "POST_OUTCOME_BODY_FREE_DIAGNOSIS_ONLY__NO_CAUSAL_REPAIR_REINTERPRETATION_OR_PROMOTION"
        ),
    }:
        raise ValueError("certificate no-promotion boundary differs")
    if certificate["truthful_scope"] != {
        "completion_requests": 0,
        "generation_invocations": 0,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "production_admissibility": "CANNOT_CHECK",
        "protected_execution_invoked": False,
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scientific_authority_delta": "NONE",
        "task_bearing_requests": 0,
        "tokenize_requests": 0,
    }:
        raise ValueError("certificate truthful scope differs")
    accounting = certificate["accounting"]
    if accounting != {
        "body_free_discriminator_scheduler_gpu_seconds": 170,
        "body_free_discriminator_submissions_completed": 2,
        "combined_scheduler_gpu_seconds": 260,
        "generation_attempts_consumed": 0,
        "hidden_second_sample": False,
        "job_3537915_body_free_scheduler_gpu_seconds": 84,
        "job_3537915_counts_as_protected_generation_attempt": False,
        "job_3537915_counts_as_protected_infrastructure_submission": False,
        "next_protected_generation_ordinal_if_separately_authorized": 1,
        "next_protected_infrastructure_submission_ordinal_if_separately_authorized": 4,
        "prior_body_free_discriminator_scheduler_gpu_seconds": 86,
        "prior_combined_scheduler_gpu_seconds": 176,
        "prior_protected_scheduler_gpu_seconds": 90,
        "protected_generation_attempts_consumed": 0,
        "protected_infrastructure_submissions_completed": 3,
        "protected_scheduler_gpu_seconds": 90,
    }:
        raise ValueError("certificate accounting differs")
    if accounting["prior_combined_scheduler_gpu_seconds"] + accounting[
        "job_3537915_body_free_scheduler_gpu_seconds"
    ] != accounting["combined_scheduler_gpu_seconds"]:
        raise ValueError("total scheduler cost arithmetic differs")
    if accounting["prior_body_free_discriminator_scheduler_gpu_seconds"] + accounting[
        "job_3537915_body_free_scheduler_gpu_seconds"
    ] != accounting["body_free_discriminator_scheduler_gpu_seconds"]:
        raise ValueError("body-free scheduler cost arithmetic differs")
    if accounting["protected_scheduler_gpu_seconds"] != accounting[
        "prior_protected_scheduler_gpu_seconds"
    ]:
        raise ValueError("protected scheduler cost changed")


def main() -> int:
    _, certificate = strict_json(CERTIFICATE)
    validate_source_bindings(certificate)
    validate_merged_v5_sources(certificate)
    receipt_raw = validate_live_receipt(certificate)
    validate_operator_evidence(receipt_raw)
    validate_deployment_and_submission_evidence()
    validate_certificate(certificate)
    if SLURM_STDOUT.read_bytes() != b"":
        raise ValueError("Slurm stdout is not exactly empty")
    if SLURM_STDERR.read_bytes() != (EXPECTED_TERMINAL + "\n").encode("utf-8"):
        raise ValueError("Slurm stderr terminal differs")
    print(
        "P1_SAB_JOB_3537915_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V2_VALIDATION_PASS "
        "job_state=FAILED mapping_attestation_1=PASS gpu_capture=COMPLETED "
        "gpu_identity=CANNOT_CHECK failure_subcode=NVIDIA_SMI_NONZERO_RETURN rc=6 "
        "protected_bodies=0 task_requests=0 generation=0 evaluator=0 outcomes=0 "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
