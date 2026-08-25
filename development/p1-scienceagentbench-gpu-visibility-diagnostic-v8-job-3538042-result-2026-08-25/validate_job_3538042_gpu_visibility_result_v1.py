#!/usr/bin/env python3
"""Validate the body-free job-3538042 positive GPU-visibility result packet."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import stat
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "JOB_3538042_GPU_VISIBILITY_RESULT_V1.json"
RECEIPT = ROOT / "GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json"
MANIFEST = ROOT / "RESULT_EXPORT_MANIFEST_V1.json"
SHA256SUMS = ROOT / "SHA256SUMS"

BASE = (
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824"
)
DEPLOYMENT_ROOT = f"{BASE}/repo-gpu-visibility-v8-20260825"
RUN_ROOT = f"{BASE}/live-gpu-visibility-v8-20260825"
OUTPUT_ROOT = f"{RUN_ROOT}/evidence"
LOG_ROOT = f"{BASE}/live-gpu-visibility-v8-20260825-submit-logs"
BASE_MERGE = "123a75b5663a77290741ae7f5c24490954118f4d"
RECEIPT_SHA256 = "dfb40dd1565cd73533d320aa325bf28386b6478a129d01f2fa7fb1826a09daee"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
STDOUT_TERMINAL = (
    "P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_PASS "
    "decision=VISIBLE_A40_IDENTITY_BOUND"
)
LATENCY_INTERPRETATION = (
    "OBSERVED_FILESYSTEM_VISIBILITY_LATENCY_ONLY__NOT_JOB_RUNTIME_CORE_RUNTIME_"
    "CAUSAL_OR_FAILURE_EVIDENCE"
)
IDENTITY = {
    "gpu_uuid": "GPU-06bb5356-4a6f-8c40-d27d-a0de37505a16",
    "index": "0",
    "name": "NVIDIA A40",
}
LIST_STDOUT = (
    b"GPU 0: NVIDIA A40 (UUID: GPU-06bb5356-4a6f-8c40-d27d-a0de37505a16)\n"
)
IDENTITY_STDOUT = (
    b"0, GPU-06bb5356-4a6f-8c40-d27d-a0de37505a16, NVIDIA A40\n"
)
SACCT = (
    "JobIDRaw|JobName|State|ExitCode|ElapsedRaw|NodeList|AllocTRES|Start|End\n"
    "3538042|p1_sab_gpu_visibility_v1|COMPLETED|0:0|3|cg15|"
    "billing=1,cpu=1,gres/gpu:a40=1,gres/gpu=1,mem=4G,node=1|"
    "2026-08-25T08:10:43|2026-08-25T08:10:46\n"
    "3538042.batch|batch|COMPLETED|0:0|3|cg15|"
    "cpu=1,gres/gpu:a40=1,gres/gpu=1,mem=4G,node=1|"
    "2026-08-25T08:10:43|2026-08-25T08:10:46\n"
    "3538042.extern|extern|COMPLETED|0:0|3|cg15|"
    "billing=1,cpu=1,gres/gpu:a40=1,gres/gpu=1,mem=4G,node=1|"
    "2026-08-25T08:10:43|2026-08-25T08:10:46\n"
)
EXPECTED_SUBMISSION = (
    "P1_V8_SUBMISSION_PASS job=3538042 line=Submitted batch job 3538042 "
    f"zero_argv=true submit_cwd={DEPLOYMENT_ROOT} run_absent=true "
    "output_absent=true\n"
    "     JOBID                     NAME     STATE       TIME  NODES         "
    "NODELIST(REASON)      QOS\n"
    "   3538042 p1_sab_gpu_visibility_v1   PENDING       0:00      1"
    "                   (None)   normal\n"
)

EXPECTED_SOURCES = {
    "GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json": (
        9896,
        RECEIPT_SHA256,
    ),
    "JOB_3538042_FIRST_CUSTODY.txt": (
        2428,
        "cf1e99b4fde053f3214ca3bc67844ba8b396d3c235efc370269e1caa8f6ed16f",
    ),
    "JOB_3538042_RECEIPT_CUSTODY.txt": (
        12255,
        "3854f60f01430fccd2ba38d28cda2e947595415c3c7a46690f6d1bfb43966784",
    ),
    "REMOTE_DEPLOYMENT_SCRIPT_V1.sh": (
        6278,
        "14e20f92ac277d97c9d0330e0a90c7dcb501fbcb9eafab31a0ed27e6fc3c7726",
    ),
    "REMOTE_SUBMIT_SCRIPT_V1.sh": (
        1572,
        "7da57df1652933e9a2c8d88de8ea500100f1176d0ad475fa286f1e18bb41c381",
    ),
    "SUBMISSION_EVIDENCE.txt": (
        441,
        "16e2c057195bb50a4d20778d2f426fef1b0d001a3b2571febdbe51862c7c56fa",
    ),
    "slurm-3538042.err": (0, EMPTY_SHA256),
    "slurm-3538042.out": (
        77,
        "8230b7d0b95aa98e354f3e2c527fc2eb773dff4f18a99bfb05ae232f37524796",
    ),
}
EXPECTED_EXTERNAL_LANE = {
    "lane": "../p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25",
    "result_commit": BASE_MERGE,
    "files": {
        "BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json": (
            4163,
            "577599ad7f2b988f525ae110cf7a01e8056eb12f76c02c3f12a0a6e2482258e2",
        ),
        "GPU_VISIBILITY_DIAGNOSTIC_CONTRACT_V1.json": (
            6402,
            "4065d3271a002624bddd539e25293d41c0dab74aa7444a145a5aa058533e4e31",
        ),
        "SHA256SUMS": (
            1246,
            "3163f6a03db373f1301cfb6db1b56838170099f1610180ab87bbb7c1c1d6ebf1",
        ),
        "SYNTHETIC_VALIDATION_RECEIPT_V1.json": (
            7150,
            "16cff9e15a90c0808095ac808eb61876a3bdbe08dca2a4e56b0155ffb15a1207",
        ),
        "run_gpu_visibility_diagnostic_v1.sh": (
            14103,
            "15142f2246d1697acc6e05ae9d08a365a0f59ce9475889fb7860273d13308e66",
        ),
    },
}
EXPECTED_PAYLOAD_NAMES = {
    "DEVELOPMENT_PACKET.md",
    "GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json",
    "JOB_3538042_FIRST_CUSTODY.txt",
    "JOB_3538042_GPU_VISIBILITY_RESULT_V1.json",
    "JOB_3538042_RECEIPT_CUSTODY.txt",
    "REMOTE_DEPLOYMENT_SCRIPT_V1.sh",
    "REMOTE_SUBMIT_SCRIPT_V1.sh",
    "SUBMISSION_EVIDENCE.txt",
    "slurm-3538042.err",
    "slurm-3538042.out",
    "validate_job_3538042_gpu_visibility_result_v1.py",
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


def between_once(raw: bytes, begin: bytes, end: bytes, label: str) -> bytes:
    if raw.count(begin) != 1 or raw.count(end) != 1:
        raise ValueError(f"{label} marker count differs")
    before, remainder = raw.split(begin, 1)
    payload, after = remainder.split(end, 1)
    if not before or not after:
        raise ValueError(f"{label} framing differs")
    return payload


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

    if (ROOT / "slurm-3538042.out").read_bytes() != (
        STDOUT_TERMINAL.encode("ascii") + b"\n"
    ):
        raise ValueError("raw Slurm stdout differs")
    if (ROOT / "slurm-3538042.err").read_bytes() != b"":
        raise ValueError("raw Slurm stderr is not exact empty bytes")


def validate_evidence_text(receipt_raw: bytes) -> None:
    submission = (ROOT / "SUBMISSION_EVIDENCE.txt").read_text("utf-8")
    if submission != EXPECTED_SUBMISSION:
        raise ValueError("submission evidence body differs")

    first_raw = (ROOT / "JOB_3538042_FIRST_CUSTODY.txt").read_bytes()
    first = first_raw.decode("utf-8")
    for required in (
        "P1_V8_CUSTODY_ROOTS\n",
        f"label=ROOT type=directory mode=500 owner=scyiu group=hep links=3 bytes=33 path={DEPLOYMENT_ROOT}",
        f"label=RUN state=ABSENT path={RUN_ROOT}",
        f"label=OUTPUT state=ABSENT path={OUTPUT_ROOT}",
        f"label=LOG type=directory mode=700 owner=scyiu group=hep links=2 bytes=10 path={LOG_ROOT}",
        "FILE state=PRESENT bytes=77 sha256=8230b7d0b95aa98e354f3e2c527fc2eb773dff4f18a99bfb05ae232f37524796",
        f"FILE state=PRESENT bytes=0 sha256={EMPTY_SHA256}",
        f"FILE state=ABSENT path={OUTPUT_ROOT}/GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json",
        f"FILE state=ABSENT path={OUTPUT_ROOT}/GPU_VISIBILITY_DIAGNOSTIC_CANNOT_CHECK_V1.json",
        f"--- STDOUT BEGIN ---\n{STDOUT_TERMINAL}\n--- STDOUT END ---",
        "--- STDERR BEGIN ---\n--- STDERR END ---",
        "--- RECEIPT BEGIN ---\n--- RECEIPT END ---",
        "--- SACCT ---\n" + SACCT,
    ):
        if required not in first:
            raise ValueError(f"first custody missing exact evidence: {required}")
    if first.count(SACCT) != 1:
        raise ValueError("first-custody sacct count differs")
    if between_once(
        first_raw,
        b"--- RECEIPT BEGIN ---\n",
        b"--- RECEIPT END ---\n",
        "first-custody receipt",
    ) != b"":
        raise ValueError("first-custody receipt observation is not empty")

    second_raw = (ROOT / "JOB_3538042_RECEIPT_CUSTODY.txt").read_bytes()
    second = second_raw.decode("utf-8")
    for required in (
        "P1_V8_RECEIPT_CUSTODY_ROOTS\n",
        f"label=ROOT type=directory mode=500 owner=scyiu group=hep links=3 bytes=33 mtime=1787638196 path={DEPLOYMENT_ROOT}",
        f"label=RUN type=directory mode=700 owner=scyiu group=hep links=3 bytes=30 mtime=1787638245 path={RUN_ROOT}",
        f"label=OUTPUT type=directory mode=500 owner=scyiu group=hep links=2 bytes=62 mtime=1787638245 path={OUTPUT_ROOT}",
        f"label=LOG type=directory mode=700 owner=scyiu group=hep links=2 bytes=68 mtime=1787638244 path={LOG_ROOT}",
        f"RECEIPT state=PRESENT bytes=9896 sha256={RECEIPT_SHA256} stat=55:616335787075:9896:400:scyiu:1:1787638245 path={OUTPUT_ROOT}/GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json",
        "--- STREAMS ---\n",
        "STREAM bytes=77 sha256=8230b7d0b95aa98e354f3e2c527fc2eb773dff4f18a99bfb05ae232f37524796 stat=55:612042605605:77:600:scyiu:1:1787638246",
        f"STREAM bytes=0 sha256={EMPTY_SHA256} stat=55:612042605627:0:600:scyiu:1:1787638244",
        "--- SACCT ---\n" + SACCT,
    ):
        if required not in second:
            raise ValueError(f"receipt custody missing exact evidence: {required}")
    embedded = between_once(
        second_raw,
        b"--- RECEIPT BEGIN ---\n",
        b"--- RECEIPT END ---\n",
        "receipt-custody embedded receipt",
    )
    if embedded != receipt_raw:
        raise ValueError("receipt-custody embedded receipt is not byte exact")
    if second.count(SACCT) != 1:
        raise ValueError("receipt-custody sacct count differs")

    deployment = (ROOT / "REMOTE_DEPLOYMENT_SCRIPT_V1.sh").read_text("utf-8")
    for required in (
        f"MERGE={BASE_MERGE}",
        "ARCHIVE_BYTES=450560",
        "ARCHIVE_SHA256=ef795324bda3293e74c19b4999c08bd5d250770be2f08983fa56d79a653691a2",
        "[[ \"$member_count\" == 55 && \"$regular_count\" == 50 ]]",
        "P1_V8_DEPLOYMENT_MODE_SEAL_PASS regular=0400 entry=0500 directories=0500",
        "P1_V8_DEPLOYMENT_POST_VALIDATION_INTEGRITY_PASS",
        "P1_V8_DEPLOYMENT_READY",
    ):
        if required not in deployment:
            raise ValueError(f"deployment script missing exact binding: {required}")
    if deployment.count("run_validator ") != 4:
        raise ValueError("deployment validator call count differs")

    submit_script = (ROOT / "REMOTE_SUBMIT_SCRIPT_V1.sh").read_text("utf-8")
    for required in (
        'cd -- "$ROOT"',
        '[[ "${PWD-}" == "$ROOT" ]]',
        '[[ "$(pwd -P)" == "$ROOT" ]]',
        'submit_line=$(/usr/bin/sbatch --export=NIL \\\n',
        '--chdir="$ROOT"',
        '"$ENTRY")',
        "zero_argv=true submit_cwd=%s run_absent=true output_absent=true",
    ):
        if required not in submit_script:
            raise ValueError(f"submission script missing exact binding: {required}")


def validate_raw_capture(
    capture: dict[str, Any], expected: bytes, expected_sha256: str
) -> None:
    if capture != {
        "base64": base64.b64encode(expected).decode("ascii"),
        "bytes": len(expected),
        "complete": True,
        "encoding": "base64",
        "sha256": expected_sha256,
    }:
        raise ValueError("receipt raw command capture differs")
    if base64.b64decode(capture["base64"], validate=True) != expected:
        raise ValueError("receipt raw command base64 does not decode exactly")
    if sha256_bytes(expected) != expected_sha256:
        raise ValueError("validator command-capture constant differs")


def validate_receipt(receipt: dict[str, Any]) -> None:
    if receipt["schema_version"] != (
        "orion.p1.scienceagentbench.gpu-visibility-diagnostic-result.v1"
    ):
        raise ValueError("receipt schema differs")
    if receipt["status"] != "PASS_GPU_VISIBILITY_DIAGNOSTIC":
        raise ValueError("receipt status differs")
    if receipt["decision"] != "VISIBLE_A40_IDENTITY_BOUND":
        raise ValueError("receipt decision differs")
    if receipt["authority"] != (
        "BODY_FREE_GPU_VISIBILITY_DIAGNOSTIC_RESULT_ONLY__NO_CAUSAL_PROOF_"
        "PROTECTED_EXECUTION_TASK_OUTCOME_PRODUCTION_OR_SCIENTIFIC_AUTHORITY"
    ):
        raise ValueError("receipt authority differs")
    if receipt["contract_sha256"] != (
        "4065d3271a002624bddd539e25293d41c0dab74aa7444a145a5aa058533e4e31"
    ):
        raise ValueError("receipt contract binding differs")
    if receipt["predecessor_binding"] != {
        "bytes": 3473,
        "file": "JOB_3537915_PREDECESSOR_BINDING_V1.json",
        "job_id": "3537915",
        "result_commit": "9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67",
        "sha256": "639e96639c33d78f592241d138ba98e0381c8b71d5d2cecc5ebb953430439729",
        "status": "PASS_BOUND_JOB_3537915_ADVERSE_PREDECESSOR",
    }:
        raise ValueError("receipt scientific predecessor binding differs")
    if receipt["pre_run_failure_binding"] != {
        "bytes": 4091,
        "file": "V7_JOB_3537988_PRE_RUN_FAILURE_BINDING_V1.json",
        "job_id": "3537988",
        "result_commit": "c9741a30f4d1634cbacdf79b454ae56c6eb89da5",
        "sha256": "deaab63454227b28dd55a8a0fabf32cf8faf252781dfdc3ec8f4e7762268386e",
        "status": "PASS_BOUND_V7_JOB_3537988_PRE_RUN_FAILURE",
    }:
        raise ValueError("receipt V7 pre-run-failure binding differs")
    if receipt["prior_accounting"] != {
        "body_free_discriminator_scheduler_gpu_seconds": 170,
        "body_free_discriminator_submissions_completed": 3,
        "combined_scheduler_gpu_seconds": 260,
        "protected_generation_attempts_consumed": 0,
        "protected_infrastructure_scheduler_gpu_seconds": 90,
        "protected_infrastructure_submissions_completed": 3,
    }:
        raise ValueError("receipt prior accounting differs")

    commands = receipt["commands"]
    expected_commands = {
        "nvidia_smi_list": (
            ["/usr/bin/nvidia-smi", "-L"],
            LIST_STDOUT,
            "68362ead8006fec11a6aadd27bce4ca3f7b8055951a60929af377afccb8f5b0f",
        ),
        "unscoped_identity": (
            [
                "/usr/bin/nvidia-smi",
                "--query-gpu=index,uuid,name",
                "--format=csv,noheader,nounits",
            ],
            IDENTITY_STDOUT,
            "cc5322d6b5896f8ac36c0cd313c9670861c2a2a66ad5ad6a4a30bc6537dc18e9",
        ),
        "scoped_identity": (
            [
                "/usr/bin/nvidia-smi",
                "--id=0",
                "--query-gpu=index,uuid,name",
                "--format=csv,noheader,nounits",
            ],
            IDENTITY_STDOUT,
            "cc5322d6b5896f8ac36c0cd313c9670861c2a2a66ad5ad6a4a30bc6537dc18e9",
        ),
    }
    if set(commands) != set(expected_commands):
        raise ValueError("receipt command set differs")
    for label, (argv, stdout, stdout_sha256) in expected_commands.items():
        command = commands[label]
        if command["argv"] != argv:
            raise ValueError(f"receipt command argv differs: {label}")
        if command["return_code"] != 0 or command["status"] != "COMPLETED":
            raise ValueError(f"receipt command outcome differs: {label}")
        if command["stdout_parse_attempted"] is not True:
            raise ValueError(f"receipt parse-attempt binding differs: {label}")
        validate_raw_capture(command["stdout"], stdout, stdout_sha256)
        validate_raw_capture(command["stderr"], b"", EMPTY_SHA256)

    parsed = receipt["parsed_outputs"]
    if parsed["nvidia_smi_list"] != {
        "identity": IDENTITY,
        "status": "PARSED_ONE_A40",
    }:
        raise ValueError("receipt list identity parse differs")
    if parsed["unscoped_identity"] != {
        "identity": IDENTITY,
        "status": "PARSED_ONE_A40",
    }:
        raise ValueError("receipt unscoped identity parse differs")
    if parsed["scoped_identity"] != {
        "identity": IDENTITY,
        "scope_token": "0",
        "scope_token_matches_identity": True,
        "status": "PARSED_ONE_A40",
    }:
        raise ValueError("receipt scoped identity parse differs")

    environment = receipt["environment"]
    if environment["cuda_visible_devices_token"] != "0":
        raise ValueError("receipt CUDA scope token differs")
    if environment["scheduler_node"] != "cg15":
        raise ValueError("receipt scheduler node differs")
    for name, utf8 in {
        "CUDA_VISIBLE_DEVICES": "0",
        "SLURMD_NODENAME": "cg15",
        "SLURM_JOB_GPUS": "0",
        "SLURM_JOB_ID": "3538042",
    }.items():
        variable = environment["variables"][name]
        if variable["present"] is not True or variable["utf8"] != utf8:
            raise ValueError(f"receipt environment binding differs: {name}")
    if receipt["node_change_diagnostic"] != {
        "different_from_predecessor_node": True,
        "excluded_predecessor_node": "cg14",
        "interpretation": "NODE_CHANGE_DIAGNOSTIC_ONLY__NO_CAUSAL_PROOF",
        "observed_scheduler_node": "cg15",
    }:
        raise ValueError("receipt node-change boundary differs")
    if receipt["no_promotion"] != {
        "job_3537893_promoted": False,
        "job_3537910_promoted": False,
        "job_3537915_promoted": False,
        "job_3537988_promoted": False,
        "node_change_is_causal_proof": False,
        "protected_retry_authorized": False,
    }:
        raise ValueError("receipt no-promotion boundary differs")
    for key, expected in {
        "completion_requests": 0,
        "generation_invocations": 0,
        "model_started": False,
        "network_accessed": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "production_admissibility": "CANNOT_CHECK",
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scientific_authority_delta": "NONE",
        "task_bearing_requests": 0,
        "tokenize_requests": 0,
    }.items():
        if receipt[key] != expected:
            raise ValueError(f"receipt claim boundary differs: {key}")


def validate_external_lane(result: dict[str, Any]) -> None:
    observed_lanes = result["external_lane_bindings"]
    if set(observed_lanes) != {"v8_freeze"}:
        raise ValueError("external lane binding set differs")
    observed = observed_lanes["v8_freeze"]
    if observed["lane"] != EXPECTED_EXTERNAL_LANE["lane"]:
        raise ValueError("external V8 lane path differs")
    if observed["result_commit"] != EXPECTED_EXTERNAL_LANE["result_commit"]:
        raise ValueError("external V8 lane commit differs")
    expected_files = EXPECTED_EXTERNAL_LANE["files"]
    if set(observed["files"]) != set(expected_files):
        raise ValueError("external V8 file set differs")
    lane_root = ROOT / str(EXPECTED_EXTERNAL_LANE["lane"])
    for name, (expected_bytes, expected_sha256) in expected_files.items():
        raw = (lane_root / name).read_bytes()
        if (len(raw), sha256_bytes(raw)) != (expected_bytes, expected_sha256):
            raise ValueError(f"external V8 lane bytes differ: {name}")
        if observed["files"][name] != {
            "bytes": expected_bytes,
            "sha256": expected_sha256,
        }:
            raise ValueError(f"result external V8 binding differs: {name}")


def validate_result(result: dict[str, Any]) -> None:
    expected_top_level = {
        "accounting_after_job_3538042",
        "authority",
        "base_merge_commit",
        "claim_boundary",
        "created_utc",
        "custody",
        "custody_observations",
        "decision",
        "deployment",
        "external_lane_bindings",
        "gpu_identity",
        "job",
        "no_promotion",
        "production_admissibility",
        "receipt",
        "schema_version",
        "source_bindings",
        "status",
        "submission",
        "truthful_scope",
    }
    if set(result) != expected_top_level:
        raise ValueError("result top-level member set differs")
    if result["schema_version"] != (
        "orion.p1.scienceagentbench.gpu-visibility-diagnostic-job-3538042-"
        "result.v1"
    ):
        raise ValueError("result schema differs")
    if result["status"] != "PASS_BOUND_JOB_3538042_GPU_VISIBILITY_DIAGNOSTIC":
        raise ValueError("result status differs")
    if result["decision"] != "VISIBLE_A40_IDENTITY_BOUND":
        raise ValueError("result decision differs")
    if result["base_merge_commit"] != BASE_MERGE:
        raise ValueError("result base merge differs")
    if result["created_utc"] != "2026-08-25T06:22:28Z":
        raise ValueError("result creation timestamp differs")
    if result["authority"] != (
        "BODY_FREE_V8_JOB_3538042_POSITIVE_GPU_VISIBILITY_DIAGNOSTIC_RESULT_"
        "ONLY__NO_MODEL_EXECUTION_TASK_SUCCESS_PRODUCTION_CAUSAL_SUPERIORITY_"
        "PROTECTED_EXECUTION_OR_SCIENTIFIC_AUTHORITY"
    ):
        raise ValueError("result authority differs")
    if result["job"] != {
        "allocated_gpu_count": 1,
        "allocated_gpu_scope": (
            "SCHEDULER_A40_GRES_AND_PROCESS_VISIBLE_A40_IDENTITY_BOUND"
        ),
        "elapsed_seconds": 3,
        "end": "2026-08-25T08:10:46",
        "exit_code": "0:0",
        "job_id": "3538042",
        "node": "cg15",
        "scheduler_gpu_allocation_seconds": 3,
        "start": "2026-08-25T08:10:43",
        "state": "COMPLETED",
    }:
        raise ValueError("result job binding differs")
    if result["gpu_identity"] != {
        "exact_visible_gpu_count": 1,
        "identity": IDENTITY,
        "list_identity_matches": True,
        "scope_token": "0",
        "scope_token_matches_identity": True,
        "scoped_identity_matches": True,
        "unscoped_identity_matches": True,
    }:
        raise ValueError("result GPU identity binding differs")
    if result["receipt"] != {
        "authority": (
            "BODY_FREE_GPU_VISIBILITY_DIAGNOSTIC_RESULT_ONLY__NO_CAUSAL_PROOF_"
            "PROTECTED_EXECUTION_TASK_OUTCOME_PRODUCTION_OR_SCIENTIFIC_AUTHORITY"
        ),
        "bytes": 9896,
        "contract_sha256": (
            "4065d3271a002624bddd539e25293d41c0dab74aa7444a145a5aa058533e4e31"
        ),
        "decision": "VISIBLE_A40_IDENTITY_BOUND",
        "file": "GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json",
        "schema_version": (
            "orion.p1.scienceagentbench.gpu-visibility-diagnostic-result.v1"
        ),
        "sha256": RECEIPT_SHA256,
        "status": "PASS_GPU_VISIBILITY_DIAGNOSTIC",
    }:
        raise ValueError("result receipt binding differs")
    if result["custody"] != {
        "log": {"mode": "0700", "state": "PRESENT"},
        "output": {"mode": "0500", "state": "PRESENT_SEALED"},
        "receipt": {
            "bytes": 9896,
            "mode": "0400",
            "sha256": RECEIPT_SHA256,
            "state": "PRESENT",
        },
        "receipt_cannot_check": "ABSENT",
        "root": {"mode": "0500", "state": "SEALED_PRESERVED"},
        "run": {"mode": "0700", "state": "PRESENT"},
        "stderr": {"bytes": 0, "mode": "0600", "sha256": EMPTY_SHA256},
        "stdout": {
            "bytes": 77,
            "mode": "0600",
            "sha256": "8230b7d0b95aa98e354f3e2c527fc2eb773dff4f18a99bfb05ae232f37524796",
        },
    }:
        raise ValueError("result custody binding differs")

    observations = result["custody_observations"]
    if observations != {
        "first": {
            "job_state": "COMPLETED",
            "output": "ABSENT",
            "receipt_cannot_check": "ABSENT",
            "receipt_success": "ABSENT",
            "record": {
                "bytes": 2428,
                "file": "JOB_3538042_FIRST_CUSTODY.txt",
                "mtime_local": "2026-08-25T08:11:19+0200",
                "sha256": "cf1e99b4fde053f3214ca3bc67844ba8b396d3c235efc370269e1caa8f6ed16f",
            },
            "run": "ABSENT",
        },
        "interpretation": LATENCY_INTERPRETATION,
        "observed_record_interval_seconds": 75,
        "second": {
            "job_state": "COMPLETED",
            "output": "PRESENT_SEALED",
            "receipt_success": "PRESENT_BOUND",
            "record": {
                "bytes": 12255,
                "file": "JOB_3538042_RECEIPT_CUSTODY.txt",
                "mtime_local": "2026-08-25T08:12:34+0200",
                "sha256": "3854f60f01430fccd2ba38d28cda2e947595415c3c7a46690f6d1bfb43966784",
            },
            "run": "PRESENT",
        },
    }:
        raise ValueError("result custody observations differ")
    first_mtime = datetime.strptime(
        observations["first"]["record"]["mtime_local"], "%Y-%m-%dT%H:%M:%S%z"
    )
    second_mtime = datetime.strptime(
        observations["second"]["record"]["mtime_local"], "%Y-%m-%dT%H:%M:%S%z"
    )
    if int((second_mtime - first_mtime).total_seconds()) != 75:
        raise ValueError("custody-record mtime interval is not exactly 75 seconds")
    if result["submission"] != {
        "record": {
            "bytes": 441,
            "file": "SUBMISSION_EVIDENCE.txt",
            "mtime_local": "2026-08-25T08:10:43+0200",
            "sha256": "16e2c057195bb50a4d20778d2f426fef1b0d001a3b2571febdbe51862c7c56fa",
        },
        "submit_cwd": DEPLOYMENT_ROOT,
        "trampoline_argv_count": 0,
    }:
        raise ValueError("result submission/mtime binding differs")

    accounting = result["accounting_after_job_3538042"]
    if accounting != {
        "body_free_discriminator_scheduler_gpu_seconds": 173,
        "body_free_discriminator_submissions_completed": 4,
        "combined_scheduler_gpu_seconds": 263,
        "job_3538042_scheduler_gpu_seconds": 3,
        "prior_body_free_discriminator_scheduler_gpu_seconds": 170,
        "prior_body_free_discriminator_submissions_completed": 3,
        "prior_combined_scheduler_gpu_seconds": 260,
        "protected_generation_attempts_consumed": 0,
        "protected_infrastructure_scheduler_gpu_seconds": 90,
        "protected_infrastructure_submissions_completed": 3,
        "v8_body_free_submissions_added": 1,
    }:
        raise ValueError("result accounting differs")
    if (
        accounting["prior_combined_scheduler_gpu_seconds"]
        + accounting["job_3538042_scheduler_gpu_seconds"]
        != accounting["combined_scheduler_gpu_seconds"]
        or accounting["prior_body_free_discriminator_scheduler_gpu_seconds"]
        + accounting["job_3538042_scheduler_gpu_seconds"]
        != accounting["body_free_discriminator_scheduler_gpu_seconds"]
    ):
        raise ValueError("result accounting arithmetic differs")
    if result["deployment"] != {
        "archive": {
            "bytes": 450560,
            "directory_entries": 5,
            "members": 55,
            "regular_files": 50,
            "sha256": "ef795324bda3293e74c19b4999c08bd5d250770be2f08983fa56d79a653691a2",
        },
        "deployment_root": DEPLOYMENT_ROOT,
        "merge_commit": BASE_MERGE,
        "preserved_without_remote_mutation_during_result_export": True,
    }:
        raise ValueError("result deployment binding differs")
    if result["claim_boundary"] != {
        "causal_explanation_established": False,
        "gpu_visibility_diagnostic_positive_for_job_3538042_only": True,
        "job_3537915_reinterpreted_or_repaired": False,
        "model_execution_evidence": False,
        "orion_superiority_evidence": False,
        "production_evidence": False,
        "protected_execution_evidence": False,
        "task_success_evidence": False,
    }:
        raise ValueError("result claim boundary differs")
    if result["no_promotion"] != {
        "job_3537915_promoted": False,
        "job_3537988_promoted": False,
        "job_3538042_causes_prior_failures": False,
        "job_3538042_model_or_task_evidence": False,
        "job_3538042_production_or_superiority_evidence": False,
        "protected_retry_authorized": False,
    }:
        raise ValueError("result no-promotion boundary differs")
    if result["truthful_scope"] != {
        "completion_requests": 0,
        "diagnostic_network_accessed": False,
        "generation_invocations": 0,
        "model_started": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scientific_authority_delta": "NONE",
        "task_bearing_requests": 0,
        "task_successes_observed": 0,
        "tokenize_requests": 0,
    }:
        raise ValueError("result truthful-scope boundary differs")
    if result["production_admissibility"] != "CANNOT_CHECK":
        raise ValueError("result production admissibility differs")


def validate_manifest() -> None:
    _, manifest = strict_json(MANIFEST)
    if manifest["schema_version"] != (
        "orion.p1.scienceagentbench.gpu-visibility-diagnostic-job-result-"
        "export-manifest.v1"
    ):
        raise ValueError("manifest schema differs")
    if manifest["status"] != "PASS_JOB_3538042_GPU_VISIBILITY_RESULT_EXPORT_INTEGRITY":
        raise ValueError("manifest status differs")
    if manifest["authority"] != (
        "BODY_FREE_V8_JOB_3538042_POSITIVE_GPU_VISIBILITY_RESULT_EXPORT_"
        "INTEGRITY_ONLY__NO_MODEL_EXECUTION_TASK_SUCCESS_PROTECTED_EXECUTION_"
        "PRODUCTION_CAUSAL_SUPERIORITY_OR_SCIENTIFIC_AUTHORITY"
    ):
        raise ValueError("manifest authority differs")
    if manifest["base_merge_commit"] != BASE_MERGE:
        raise ValueError("manifest base merge differs")
    if manifest["external_lane_bindings_in_result"] is not True:
        raise ValueError("manifest external-lane declaration differs")
    if manifest["lane"] != (
        "development/p1-scienceagentbench-gpu-visibility-diagnostic-v8-"
        "job-3538042-result-2026-08-25"
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
        "gpu_visibility_diagnostic_positive_for_job_3538042_only": True,
        "jobs_recorded": 1,
        "model_executions_observed": 0,
        "production_admissibility": "CANNOT_CHECK",
        "protected_generation_attempts_consumed": 0,
        "scheduler_gpu_seconds_added": 3,
        "scientific_authority_delta": "NONE",
        "task_successes_observed": 0,
    }:
        raise ValueError("manifest truthful scope differs")

    sums_raw = SHA256SUMS.read_bytes()
    if not sums_raw.endswith(b"\n") or sums_raw.endswith(b"\n\n"):
        raise ValueError("SHA256SUMS final-LF framing differs")
    lines = sums_raw.decode("ascii").splitlines()
    expected_names = sorted(EXPECTED_PAYLOAD_NAMES | {MANIFEST.name})
    parsed: list[tuple[str, str]] = []
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
    result_raw, result = strict_json(RESULT)
    receipt_raw, receipt = strict_json(RECEIPT)
    if len(result_raw) != 7110 or sha256_bytes(result_raw) != (
        "01f7a30f57fa6a3313c78f7c3566e36cc48ab88a73762d460e125636e24dab3a"
    ):
        raise ValueError("canonical lane result bytes/hash differ")
    if len(receipt_raw) != 9896 or sha256_bytes(receipt_raw) != RECEIPT_SHA256:
        raise ValueError("canonical receipt bytes/hash differ")
    validate_sources(result)
    validate_evidence_text(receipt_raw)
    validate_receipt(receipt)
    validate_result(result)
    validate_external_lane(result)
    validate_manifest()
    print(
        "P1_SAB_GPU_VISIBILITY_JOB_3538042_RESULT_VALIDATION_PASS "
        "sources=8 payloads=11 scheduler_gpu_seconds_added=3 "
        "body_free_submissions_added=1 decision=VISIBLE_A40_IDENTITY_BOUND "
        "model_execution=NONE task_success=NONE protected_execution=NONE "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
