#!/usr/bin/env python3
"""Validate only the canonical body-free job-3537910 result certificate."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CERTIFICATE = ROOT / "JOB_3537910_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V1.json"
LIVE_RECEIPT = ROOT / "JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json"
OPERATOR_EVIDENCE = ROOT / "JOB_3537910_OPERATOR_EVIDENCE.txt"
DEPLOYMENT_EVIDENCE = ROOT / "DEPLOYMENT_PRE_SUBMIT_EVIDENCE.txt"
SUBMISSION_EVIDENCE = ROOT / "SUBMISSION_EVIDENCE.txt"
SLURM_STDOUT = ROOT / "slurm-3537910.out"
SLURM_STDERR = ROOT / "slurm-3537910.err"
RESULT_MANIFEST = ROOT / "RESULT_EXPORT_MANIFEST_V1.json"
SHA256SUMS = ROOT / "SHA256SUMS"
FROZEN_V4_CORE = (
    ROOT.parent
    / "p1-scienceagentbench-backend-canonical-map-discriminator-v4-2026-08-25"
    / "backend_canonical_map_discriminator_v1.py"
)

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
    "P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK "
    "failure_code=GPU_IDENTITY_INVALID "
    "detail_sha256=a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4"
)
EXPECTED_SOURCES = {
    "DEPLOYMENT_PRE_SUBMIT_EVIDENCE.txt": (8242, "2d1ecdde1bd78d4d677d756cff4805681b2fffb52d94473fc1693d8ec4a3dbed"),
    "JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json": (1464, "cf62273ddb03288e23a7933332367794f0712e14103c4fe7fdb99579d112448a"),
    "JOB_3537910_OPERATOR_EVIDENCE.txt": (7855, "ba59039b58c57c73d8645c45d990bdbbf6b1a39187f83c824fd3627dcfe562b1"),
    "SUBMISSION_EVIDENCE.txt": (830, "0638abdd309aa122549e5268de269be9dbd1f1d822e671ac6fff7a2e8ddc4cc1"),
    "slurm-3537910.err": (169, "27c5fda40d52f578c90f18d155ae90d3a89fe06049a652b1150a609fe6380dfc"),
    "slurm-3537910.out": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
}
EXPECTED_PAYLOAD_NAMES = {
    "DEPLOYMENT_PRE_SUBMIT_EVIDENCE.txt",
    "DEVELOPMENT_PACKET.md",
    "HANDOFF_V1.md",
    "JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json",
    "JOB_3537910_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V1.json",
    "JOB_3537910_OPERATOR_EVIDENCE.txt",
    "OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json",
    "SUBMISSION_EVIDENCE.txt",
    "classify_gpu_identity_failure_v1.py",
    "slurm-3537910.err",
    "slurm-3537910.out",
    "validate_gpu_identity_failure_classification_v1.py",
    "validate_job_3537910_body_free_cannot_check_certificate_v1.py",
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


def validate_source_bindings(certificate: dict[str, Any]) -> None:
    bindings = certificate["source_bindings"]
    if set(bindings) != set(EXPECTED_SOURCES):
        raise ValueError("certificate source binding set differs")
    for name, (expected_bytes, expected_sha) in EXPECTED_SOURCES.items():
        raw = (ROOT / name).read_bytes()
        if len(raw) != expected_bytes or sha256_bytes(raw) != expected_sha:
            raise ValueError(f"retained source differs: {name}")
        if bindings[name] != {"bytes": expected_bytes, "sha256": expected_sha}:
            raise ValueError(f"certificate binding differs: {name}")


def validate_result_manifest() -> None:
    _, manifest = strict_json(RESULT_MANIFEST)
    require_exact_keys(
        manifest,
        {
            "schema_version",
            "authority",
            "status",
            "lane",
            "total_exported_file_count",
            "manifested_payload_file_count",
            "manifested_payload_exclusions",
            "manifested_payload_files",
            "external_dependencies",
            "sha256sums_scope",
            "truthful_scope",
        },
        "result manifest",
    )
    if manifest["schema_version"] != "orion.p1.scienceagentbench.backend-canonical-map-job-result-export-manifest.v1":
        raise ValueError("result manifest schema differs")
    if manifest["authority"] != "BODY_FREE_JOB_RESULT_EXPORT_INTEGRITY_ONLY__NO_FULL_DISCRIMINATOR_PASS_PROTECTED_EXECUTION_OUTCOME_PRODUCTION_OR_SCIENTIFIC_AUTHORITY":
        raise ValueError("result manifest authority differs")
    if manifest["status"] != "PASS_BODY_FREE_JOB_RESULT_EXPORT_INTEGRITY":
        raise ValueError("result manifest status differs")
    if manifest["lane"] != "development/p1-scienceagentbench-backend-canonical-map-discriminator-v4-job-3537910-result-2026-08-25":
        raise ValueError("result manifest lane differs")
    if manifest["total_exported_file_count"] != 15:
        raise ValueError("result manifest total file count differs")
    if manifest["manifested_payload_file_count"] != 13:
        raise ValueError("result manifest payload count differs")
    if manifest["manifested_payload_exclusions"] != [
        "RESULT_EXPORT_MANIFEST_V1.json",
        "SHA256SUMS",
    ]:
        raise ValueError("result manifest exclusions differ")
    payloads = manifest["manifested_payload_files"]
    if not isinstance(payloads, dict) or set(payloads) != EXPECTED_PAYLOAD_NAMES:
        raise ValueError("result manifest payload set differs")
    for name in sorted(EXPECTED_PAYLOAD_NAMES):
        path = ROOT / name
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o644:
            raise ValueError(f"result payload mode/type differs: {name}")
        raw = path.read_bytes()
        expected = {
            "bytes": len(raw),
            "mode": "0644",
            "sha256": sha256_bytes(raw),
        }
        if payloads[name] != expected:
            raise ValueError(f"result payload binding differs: {name}")
    dependency = manifest["external_dependencies"]
    core_raw = FROZEN_V4_CORE.read_bytes()
    if dependency != {
        "frozen_v4_core": {
            "bytes": 59609,
            "executed_commit": "8e84ae99af5122ce6f8e641955e196c27aed07c8",
            "path": "../p1-scienceagentbench-backend-canonical-map-discriminator-v4-2026-08-25/backend_canonical_map_discriminator_v1.py",
            "sha256": "59780ecb75ffc47f8f6c15eae239a5570d7bebb66cfbaf573368affaab1f8219",
        }
    }:
        raise ValueError("result manifest external dependency differs")
    if len(core_raw) != 59609 or sha256_bytes(core_raw) != dependency["frozen_v4_core"]["sha256"]:
        raise ValueError("frozen V4 core dependency differs")
    if manifest["sha256sums_scope"] != {
        "covered_file_count": 14,
        "covers_manifested_payload_files": True,
        "excluded_self": "SHA256SUMS",
        "includes_manifest": True,
    }:
        raise ValueError("SHA256SUMS scope differs")
    if manifest["truthful_scope"] != {
        "completion_requests": 0,
        "generation_invocations": 0,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "production_admissibility": "CANNOT_CHECK",
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scientific_authority_delta": "NONE",
        "tokenize_requests": 0,
    }:
        raise ValueError("result manifest truthful scope differs")

    sums_raw = SHA256SUMS.read_bytes()
    if not sums_raw.endswith(b"\n") or sums_raw.endswith(b"\n\n"):
        raise ValueError("SHA256SUMS final-LF framing differs")
    try:
        lines = sums_raw.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("SHA256SUMS is not ASCII") from exc
    expected_sum_names = sorted(EXPECTED_PAYLOAD_NAMES | {RESULT_MANIFEST.name})
    parsed: list[tuple[str, str]] = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if match is None:
            raise ValueError("SHA256SUMS line grammar differs")
        parsed.append((match.group(1), match.group(2)))
    if [name for _, name in parsed] != expected_sum_names:
        raise ValueError("SHA256SUMS name/order set differs")
    for digest, name in parsed:
        if sha256_bytes((ROOT / name).read_bytes()) != digest:
            raise ValueError(f"SHA256SUMS digest differs: {name}")


def validate_live_receipt(certificate: dict[str, Any]) -> dict[str, Any]:
    raw, receipt = strict_json(LIVE_RECEIPT)
    if len(raw) != 1464 or sha256_bytes(raw) != EXPECTED_SOURCES[LIVE_RECEIPT.name][1]:
        raise ValueError("live receipt byte binding differs")
    if receipt["schema_version"] != "orion.p1.scienceagentbench.backend-canonical-map-discriminator-cannot-check.v1":
        raise ValueError("live receipt schema differs")
    if receipt["authority"] != "BODY_FREE_CANONICAL_MAP_DISCRIMINATOR_FAILURE_ONLY__NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY":
        raise ValueError("live receipt authority differs")
    if receipt["status"] != "CANNOT_CHECK_BACKEND_CANONICAL_MAP_DISCRIMINATOR":
        raise ValueError("live receipt status differs")
    if receipt["completed_stages"] != EXPECTED_STAGES:
        raise ValueError("live receipt completed stages differ")
    if receipt["failure_code"] != "GPU_IDENTITY_INVALID" or receipt["failure_detail_sha256"] != certificate["failure"]["failure_detail_sha256"]:
        raise ValueError("live receipt failure binding differs")
    if receipt["contract_sha256"] != certificate["executed_packet"]["contract_sha256"]:
        raise ValueError("live receipt contract binding differs")
    for key in (
        "protected_packet_bodies_opened",
        "protected_prompt_bodies_opened",
        "tokenize_requests",
        "completion_requests",
        "generation_invocations",
        "official_outcomes_opened",
    ):
        if receipt[key] != 0:
            raise ValueError(f"live receipt nonzero counter: {key}")
    if receipt["official_evaluator_invoked"] is not False:
        raise ValueError("live receipt evaluator boundary differs")
    if receipt["production_admissibility"] != "CANNOT_CHECK" or receipt["scientific_authority_delta"] != "NONE":
        raise ValueError("live receipt authority boundary differs")
    if receipt["body_free_http_request_types_allowed"] != ["GET /health", "GET /slots"]:
        raise ValueError("request-type allowlist differs")
    if "body_free_http_requests" in receipt:
        raise ValueError("receipt must not imply HTTP request counts")
    if receipt["server_log_bindings"] != certificate["retained_log_bindings"]["core_server_streams"]:
        raise ValueError("core server stream bindings differ")
    if receipt["cleanup"] != certificate["cleanup"]:
        raise ValueError("cleanup binding differs")
    return receipt


def validate_operator_evidence(receipt_raw: bytes) -> None:
    evidence = OPERATOR_EVIDENCE.read_bytes()
    required = [
        b"3537910|p1_sab_backend_map_v1|FAILED|00:01:26|1:0|",
        b"gres/gpu:a40=1",
        b"NodeList=cg14",
        b"mode=500 bytes=78 uid=6350 gid=6300 nlink=2",
        b"f 400 1464 scyiu hep 1 ",
        b"cf62273ddb03288e23a7933332367794f0712e14103c4fe7fdb99579d112448a",
        receipt_raw.rstrip(b"\n"),
    ]
    if any(item not in evidence for item in required):
        raise ValueError("operator evidence lacks an exact job/receipt/custody binding")


def validate_deployment_and_submission_evidence() -> None:
    deployment = DEPLOYMENT_EVIDENCE.read_text(encoding="utf-8")
    for item in (
        "DEPLOYMENT_ARCHIVE merge=8e84ae99af5122ce6f8e641955e196c27aed07c8 bytes=174080 sha256=821a41be9d157d9b8220ac1adc7c01f2e2a93cee0dc870d038195ef38741942b",
        "8101ce3deacb650ef5607b78a1cfc378f5827fe49f954d5eff7dd87c75ee995c",
        "7e28ebad44ca2292e9d4edeb54642c90ec13761ac27808ff56fcab841fa4209f",
        "59780ecb75ffc47f8f6c15eae239a5570d7bebb66cfbaf573368affaab1f8219",
        "6d9278f9cffb2dffbe06287d6b4a10253d371448687e3330ea62afe7669e3bb4",
        "DEPLOYMENT_PASS",
    ):
        if item not in deployment:
            raise ValueError("deployment evidence lacks an executed-packet binding")
    submission = SUBMISSION_EVIDENCE.read_text(encoding="utf-8")
    if "SUBMITTED raw_job_id=3537910 job_id=3537910" not in submission:
        raise ValueError("submission evidence lacks the exact job ID")
    if "run_pre_submit=ABSENT output_pre_submit=ABSENT" not in submission:
        raise ValueError("submission evidence lacks fresh-root preconditions")


def validate_certificate(certificate: dict[str, Any]) -> None:
    require_exact_keys(
        certificate,
        {
            "schema_version",
            "authority",
            "status",
            "job",
            "executed_packet",
            "failure",
            "completed_stages",
            "positive_first_attestation_scope",
            "cannot_check_boundary",
            "cleanup",
            "retained_log_bindings",
            "truthful_scope",
            "accounting",
            "source_bindings",
        },
        "certificate",
    )
    if certificate["schema_version"] != "orion.p1.scienceagentbench.backend-canonical-map-discriminator-job-result-certificate.v1":
        raise ValueError("certificate schema differs")
    if certificate["authority"] != "BODY_FREE_JOB_RESULT_AND_FIRST_ATTESTATION_STAGE_CERTIFICATE_ONLY__NO_FULL_DISCRIMINATOR_PASS_PROTECTED_EXECUTION_OUTCOME_PRODUCTION_OR_SCIENTIFIC_AUTHORITY":
        raise ValueError("certificate authority differs")
    if certificate["status"] != "PASS_CERTIFIED_BODY_FREE_JOB_3537910_CANNOT_CHECK":
        raise ValueError("certificate status differs")
    if certificate["executed_packet"] != {
        "contract_sha256": "8101ce3deacb650ef5607b78a1cfc378f5827fe49f954d5eff7dd87c75ee995c",
        "deployment_archive": {
            "bytes": 174080,
            "sha256": "821a41be9d157d9b8220ac1adc7c01f2e2a93cee0dc870d038195ef38741942b",
        },
        "executed_commit": "8e84ae99af5122ce6f8e641955e196c27aed07c8",
        "module_sha256": "59780ecb75ffc47f8f6c15eae239a5570d7bebb66cfbaf573368affaab1f8219",
    }:
        raise ValueError("certificate executed-packet binding differs")
    if certificate["job"] != {
        "allocated_gpu_count": 1,
        "allocated_gpu_scope": "SCHEDULER_A40_GRES_ONLY__LIVE_GPU_IDENTITY_CANNOT_CHECK",
        "elapsed_seconds": 86,
        "exit_code": "1:0",
        "job_id": "3537910",
        "node": "cg14",
        "scheduler_gpu_allocation_seconds": 86,
        "state": "FAILED",
    }:
        raise ValueError("certificate job record differs")
    if certificate["completed_stages"] != EXPECTED_STAGES:
        raise ValueError("certificate completed stages differ")
    positive = certificate["positive_first_attestation_scope"]
    if positive != {
        "claim": "FRESH_BODY_FREE_FIRST_ATTESTATION_ONLY__EXACT_SERVER_PROCESS_ARGV_ENVIRONMENT_AND_LOOPBACK_LISTENER_PASSED__FROZEN_SERVER_BACKEND_MODEL_IDENTITIES_PRESENT_UNDER_ONLY_ALLOWED_LOGICAL_OR_CANONICAL_PATHS_WITH_MATCHING_DEVICE_INODE",
        "first_attestation_details_retained": False,
        "first_attestation_passed": True,
        "observed_mapping_paths_or_segments_retained": False,
        "relation_to_job_3537893": "POST_OUTCOME_DIAGNOSIS_ONLY__NO_CAUSAL_REPAIR_REINTERPRETATION_OR_PROMOTION",
        "semantic_basis": "EXECUTED_MODULE_SHA256_AND_ORDERED_COMPLETED_STAGE",
    }:
        raise ValueError("positive first-attestation scope differs")
    boundary = certificate["cannot_check_boundary"]
    if boundary != {
        "discriminator_pass": False,
        "final_listener_rebind_completed": False,
        "final_runtime_file_rebind_completed": False,
        "gpu_identity_bound": False,
        "gpu_identity_detail_plaintext_retained": False,
        "mapping_reattestation_byte_identical": False,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
        "second_mapping_attestation_completed": False,
    }:
        raise ValueError("CANNOT_CHECK boundary differs")
    scope = certificate["truthful_scope"]
    expected_zero = {
        "completion_requests": 0,
        "generation_invocations": 0,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scientific_authority_delta": "NONE",
        "tokenize_requests": 0,
    }
    if scope != expected_zero:
        raise ValueError("certificate truthful scope differs")
    accounting = certificate["accounting"]
    if accounting != {
        "body_free_discriminator_scheduler_gpu_seconds": 86,
        "body_free_discriminator_submissions_completed": 1,
        "combined_scheduler_gpu_seconds": 176,
        "generation_attempts_consumed": 0,
        "hidden_second_sample": False,
        "job_3537910_counts_as_protected_generation_attempt": False,
        "job_3537910_counts_as_protected_infrastructure_submission": False,
        "next_protected_generation_ordinal_if_separately_authorized": 1,
        "next_protected_infrastructure_submission_ordinal_if_separately_authorized": 4,
        "prior_protected_scheduler_gpu_seconds": 90,
        "protected_infrastructure_submissions_completed": 3,
    }:
        raise ValueError("certificate accounting differs")
    if accounting["combined_scheduler_gpu_seconds"] != accounting["prior_protected_scheduler_gpu_seconds"] + accounting["body_free_discriminator_scheduler_gpu_seconds"]:
        raise ValueError("combined scheduler cost arithmetic differs")
    if certificate["failure"] != {
        "failure_code": "GPU_IDENTITY_INVALID",
        "failure_detail_sha256": "a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4",
        "terminal": EXPECTED_TERMINAL,
    }:
        raise ValueError("certificate failure binding differs")
    if not SHA_RE.fullmatch(certificate["failure"]["failure_detail_sha256"]):
        raise ValueError("certificate failure detail is not SHA-256")
    if certificate["cleanup"] != {
        "pid": 130837,
        "process_absent_after_cleanup": True,
        "process_group_absent_after_cleanup": True,
        "process_group_id": 130837,
        "process_started": True,
        "return_code": 0,
        "termination_signal": "SIGTERM",
    }:
        raise ValueError("certificate cleanup binding differs")
    if certificate["retained_log_bindings"] != {
        "core_server_streams": {
            "stderr": {
                "bytes": 1641,
                "sha256": "7d63416db0da43ec4813235bb7ce6d383cc497577714a3c8051b73820826a764",
            },
            "stdout": {
                "bytes": 0,
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
        },
        "slurm_streams": {
            "stderr": {
                "bytes": 169,
                "sha256": "27c5fda40d52f578c90f18d155ae90d3a89fe06049a652b1150a609fe6380dfc",
            },
            "stdout": {
                "bytes": 0,
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
        },
    }:
        raise ValueError("certificate retained-log binding differs")


def main() -> int:
    validate_result_manifest()
    _, certificate = strict_json(CERTIFICATE)
    validate_source_bindings(certificate)
    receipt_raw, _ = strict_json(LIVE_RECEIPT)
    validate_live_receipt(certificate)
    validate_operator_evidence(receipt_raw)
    validate_deployment_and_submission_evidence()
    validate_certificate(certificate)
    if SLURM_STDOUT.read_bytes() != b"":
        raise ValueError("Slurm stdout is not exactly empty")
    if SLURM_STDERR.read_bytes() != (EXPECTED_TERMINAL + "\n").encode("utf-8"):
        raise ValueError("Slurm stderr terminal differs")
    print(
        "P1_SAB_JOB_3537910_BODY_FREE_CANNOT_CHECK_CERTIFICATE_VALIDATION_PASS "
        "job_state=FAILED mapping_attestation_1=PASS gpu_identity=CANNOT_CHECK "
        "protected_bodies=0 generation=0 production_admissibility=CANNOT_CHECK "
        "scientific_authority=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
