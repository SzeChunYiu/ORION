#!/usr/bin/env python3
"""Synthetic hostile validation for the protected RR1 one-tuple finalizer.

All fixtures are invented metadata.  The suite never submits a job, invokes a
model/evaluator/API, or reads protected packet, prompt, completion, token-ID, or
official-outcome bodies.
"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest import mock


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
MODULE_PATH = ROOT / "protected_rr1_one_tuple_finalizer_v1.py"
CONTRACT_PATH = ROOT / "FINALIZER_CONTRACT_V1.json"
SCHEMA_PATH = ROOT / "FINALIZER_OUTPUT_SCHEMA_V1.json"
SYNTHETIC_RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"
BODY_FREE_MANIFEST_PATH = ROOT / "BODY_FREE_EXPORT_MANIFEST_V1.json"
SHA256SUMS_PATH = ROOT / "SHA256SUMS"
DONOR_PLAN_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24/RUN_PLAN_V1.json"
)

JOB_ID = "4000001"
CLUSTER = "cosmos"
NODE = "aurora01"
PARTITION = "gpua40i"
ACCOUNT = "lu2026-2-51"
GPU_UUID = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
START = "2026-08-24T11:00:00"
END = "2026-08-24T11:15:00"
TUPLE = {"task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101}

SACCT_FIELDS = (
    "JobIDRaw",
    "Partition",
    "State",
    "ExitCode",
    "DerivedExitCode",
    "Submit",
    "Eligible",
    "Start",
    "End",
    "TimelimitRaw",
    "Elapsed",
    "NodeList",
    "NNodes",
    "NCPUS",
    "NTasks",
    "ReqCPUS",
    "ReqMem",
    "ReqTRES",
    "AllocTRES",
    "Account",
    "QOS",
    "Constraints",
    "Reservation",
    "Reason",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value) + b"\n")
    path.chmod(0o600)


def write_private(path: Path, payload: bytes) -> None:
    path.write_bytes(payload)
    path.chmod(0o600)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise AssertionError(f"fixture JSON is not an object: {path}")
    return value


def sacct_row(
    *,
    job_id: str = JOB_ID,
    state: str = "COMPLETED",
    exit_code: str = "0:0",
    start: str = START,
    end: str = END,
    node: str = NODE,
    alloc_tres: str = "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1",
) -> bytes:
    values = {
        "JobIDRaw": job_id,
        "Partition": PARTITION,
        "State": state,
        "ExitCode": exit_code,
        "DerivedExitCode": "0:0",
        "Submit": "2026-08-24T10:59:00",
        "Eligible": "2026-08-24T10:59:01",
        "Start": start,
        "End": end,
        "TimelimitRaw": "60",
        "Elapsed": "00:15:00",
        "NodeList": node,
        "NNodes": "1",
        "NCPUS": "8",
        "NTasks": "1",
        "ReqCPUS": "8",
        "ReqMem": "64Gn",
        "ReqTRES": "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1",
        "AllocTRES": alloc_tres,
        "Account": ACCOUNT,
        "QOS": "normal",
        "Constraints": "",
        "Reservation": "",
        "Reason": "None",
    }
    return ("|".join(values[field] for field in SACCT_FIELDS) + "|\n").encode()


def scontrol_snapshot(*, state: str, end: str, exit_code: str = "0:0") -> bytes:
    return (
        f"JobId={JOB_ID} JobName=synthetic-rr1\n"
        f"   JobState={state} Reason=None Dependency=(null) ExitCode={exit_code}\n"
        f"   SubmitTime=2026-08-24T10:59:00 EligibleTime=2026-08-24T10:59:01\n"
        f"   StartTime={START} EndTime={end} Partition={PARTITION} Account={ACCOUNT}\n"
        f"   NodeList={NODE} NumNodes=1 NumCPUs=8 NumTasks=1\n"
        "   ReqTRES=billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1\n"
        "   AllocTRES=billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1\n"
        "   TresPerNode=gres:gpu:a40:1 GresDetail=gpu:a40:1(IDX:0)\n"
    ).encode()


def materialized_argv() -> dict[str, list[str]]:
    fields = ",".join(SACCT_FIELDS)
    return {
        "terminal_sacct": [
            "sacct", "-a", "-X", "-D", "-j", JOB_ID,
            "--parsable2", "--noheader", f"--format={fields}",
        ],
        "post_job_scontrol": ["scontrol", "show", "job", "-dd", JOB_ID],
        "scheduler_config": ["scontrol", "show", "config"],
        "scheduler_partition": ["scontrol", "show", "partition", PARTITION, "-o"],
        "scheduler_node": ["scontrol", "show", "node", "-dd", "-o", NODE],
        "nonoverlap_sacct": [
            "sacct", "-a", "-X", "-D", "-S", START, "-E", END,
            "-N", NODE, "--parsable2", "--noheader", f"--format={fields}",
        ],
    }


ROOT_INPUTS = (
    "POST_JOB_SACCT_V1.txt",
    "POST_JOB_SACCT_NONOVERLAP_V1.txt",
    "POST_JOB_SCONTROL_V1.txt",
    "SCHEDULER_CONFIG_V1.txt",
    "SCHEDULER_PARTITION_V1.txt",
    "SCHEDULER_NODE_V1.txt",
    "GPU_ALLOCATION_IDENTITY_V1.json",
    "SERVER_CLEANUP_V1.json",
    "STAGED_RUNTIME_INPUT_V1.json",
    "PROCESS_ATTESTATION_V1.json",
    "SCHEDULER_CAPTURE_PROVENANCE_V1.json",
)
ATTEMPT_INPUTS = (
    "SCONTROL_IN_JOB_V1.txt",
    "SLURM_IDENTITY_AND_SNAPSHOT_V1.json",
    "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json",
    "DIRECT_ROUTE_BRIDGE_BINDING_V1.json",
    "ATTEMPT_CAPTURE_V1.json",
)


class SyntheticFixture:
    def create(self, root: Path) -> None:
        root.chmod(0o700)
        attempt = root / "attempt"
        attempt.mkdir(parents=True, mode=0o700)
        runtime_inputs = root / "runtime-inputs"
        runtime_inputs.mkdir(mode=0o700)
        plan_bytes = DONOR_PLAN_PATH.read_bytes()
        write_private(runtime_inputs / "RUN_PLAN.json", plan_bytes)
        write_private(runtime_inputs / "MASKED_PACKET.json", b'{"trap":"must-not-open"}\n')
        write_private(runtime_inputs / "RECOVERED_PACKET.json", b'{"trap":"must-not-open"}\n')
        in_job = scontrol_snapshot(state="RUNNING", end="Unknown")
        terminal = sacct_row()
        post_scontrol = scontrol_snapshot(state="COMPLETED", end=END)
        write_private(root / "POST_JOB_SACCT_V1.txt", terminal)
        write_private(root / "POST_JOB_SACCT_NONOVERLAP_V1.txt", terminal)
        write_private(root / "POST_JOB_SCONTROL_V1.txt", post_scontrol)
        write_private(root / "SCHEDULER_CONFIG_V1.txt",
            b"SlurmctldVersion = 23.11.3\n"
            b"ClusterName = cosmos\n"
            b"MinJobAge = 300 sec\n"
            b"SelectType = select/cons_tres\n"
            b"SelectTypeParameters = CR_Core_Memory\n"
            b"GresTypes = gpu\n"
            b"TaskPlugin = task/cgroup\n"
            b"ProctrackType = proctrack/cgroup\n"
            b"AccountingStorageType = accounting_storage/slurmdbd\n"
            b"AccountingStorageEnforce = associations,limits,qos,safe\n"
            b"AccountingStorageTRES = gres/gpu\n"
            b"JobAcctGatherType = jobacct_gather/cgroup\n"
            b"PrivateData = none\n"
        )
        write_private(root / "SCHEDULER_PARTITION_V1.txt",
            f"PartitionName={PARTITION} AllowAccounts={ACCOUNT} Nodes=aurora[01-04] OverSubscribe=NO State=UP\n".encode()
        )
        write_private(root / "SCHEDULER_NODE_V1.txt",
            b"NodeName=aurora01 State=ALLOCATED Gres=gpu:a40:4(S:0-1) "
            b"CfgTRES=cpu=64,mem=500G,billing=64,gres/gpu=4,gres/gpu:a40=4\n"
        )
        write_private(attempt / "SCONTROL_IN_JOB_V1.txt", in_job)
        identity = {
            "slurm_job_identity": {
                "cluster": CLUSTER,
                "job_id": JOB_ID,
                "array_job_id": None,
                "array_task_id": None,
            },
            "slurm_in_job_snapshot_sha256": sha256_bytes(in_job),
            "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
            "environment_only_exclusivity_claimed": False,
        }
        write_json(attempt / "SLURM_IDENTITY_AND_SNAPSHOT_V1.json", identity)
        gpu = {
            "schema_version": "orion.p1.scienceagentbench.one-a40-allocation-identity.v1",
            "authority": "IN_JOB_VISIBLE_GPU_IDENTITY_METADATA_ONLY",
            "status": "PASS_EXACTLY_ONE_VISIBLE_NVIDIA_A40",
            "slurm_job_id": JOB_ID,
            "cuda_visible_devices": "0",
            "slurm_job_gpus": "0",
            "slurm_step_gpus": "0",
            "gpu": {"visible_index": "0", "gpu_uuid": GPU_UUID, "name": "NVIDIA A40"},
            "nvidia_smi_stdout_sha256": "1" * 64,
            "scheduler_exclusivity_status": "CANNOT_CHECK_PENDING_POST_JOB_SCHEDULER_FINALIZATION",
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        write_json(root / "GPU_ALLOCATION_IDENTITY_V1.json", gpu)
        extension = {
            "run_plan_sha256": "66d54431f6d8ac479b2009759a4cd7b6d5f7d489f4b8f4b6a99d0f591616cc81",
            "direct_driver_sha256": "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
            "direct_contract_sha256": "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
            "direct_prompt_bundle_sha256": "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
            "adapter_sha256": "e46434fd37872a4ca7abce35375043bca2035fce52e3f36d611b1a03b98aefb9",
            "upstream_wrapper_sha256": "1d4655350c1a037cd4e51ee11e15e21491c5bfd7cea125948beb2e152c73b582",
            "upstream_wrapper_execution_allowed": False,
            "upstream_wrapper_binding_role": "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED",
            "preflight_bridge_sha256": "7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91",
            "prompt_binding_mode": "PROSPECTIVE_STATIC_HASH_OR_DYNAMIC_SEALED_RR_STATE_RULE",
            "merged_slurm_bridge_donor_sha256": "93ee3abec947a2b6fe6b9a4d1fb7871bbee56c1e190430c4193431a640c93006",
            "dynamic_rr1_pretokenize": {
                "route": "POST /tokenize", "add_special": True, "parse_special": True,
                "repeat_count": 3, "phase_output_cap": 7168,
                "context_window_tokens": 32768,
                "completion_prompt_n_equality_required": True,
            },
            "tuple_freeze_sha256": "eb06634717a6e7ae5aa69d817fc61c285b961b5d72d128405b891c8dcf0c3a47",
        }
        source_sha = {
            "plan": "66d54431f6d8ac479b2009759a4cd7b6d5f7d489f4b8f4b6a99d0f591616cc81",
            "owner": "a94fba71c1d51a0b60f4ee2ab44da85ca139373070efc3d13c41e2c63c0e3dce",
            "runtime": "2bf1150adf32239cd7603c3bb92ea0c728e1a9f28388b6d7c89aeb22b2db5019",
            "masked": "405f5836a21192d0a6d21e4b85143865fec8a2fb7cd9a4eb62100862b9d1a3df",
            "recovered": "3fce9e45e3012845d7dec2e343c224b43a4d79dea0c1192e5bf1972652733722",
            "model": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
            "server": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
            "backend": "fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb",
            "launcher": "a540954aaa4ce638190162f39268bf660d7baac7d4e8841d4f56ba5441300219",
        }
        stage = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-direct-route-runtime-stage.v1",
            "authority": "ONE_TUPLE_RUNTIME_PREFLIGHT_METADATA_ONLY__NO_SUBMISSION_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
            "status": "HASHED_RUNTIME_INPUT_STAGED__PROCESS_ATTESTATION_PENDING",
            "tuple_identity": {"task_id": "1", "arm_id": "RR", "attempt": 1},
            "tuple_seed": 101,
            "source_paths": {name: f"/private/synthetic/{name}" for name in source_sha},
            "source_sha256": source_sha,
            "runtime_observed_sha256": {
                "model": source_sha["model"], "llama_server": source_sha["server"],
                "cuda_backend": source_sha["backend"], "launcher": source_sha["launcher"],
                "preflight_bridge": "7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91",
            },
            "run_plan_binding_extension": extension,
            "run_plan_binding_extension_sha256": canonical_hash(extension),
            "server_argv": [
                "/private/synthetic/server", "--model", "/private/synthetic/model",
                "--host", "127.0.0.1", "--port", "8080", "--ctx-size", "32768",
                "--parallel", "1", "--no-cont-batching", "--threads", "8",
                "--threads-batch", "8", "--batch-size", "512", "--ubatch-size", "512",
                "--cache-type-k", "f16", "--cache-type-v", "f16", "--flash-attn", "on",
                "--n-gpu-layers", "all", "--no-context-shift", "--metrics", "--slots",
            ],
            "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
            "prompt_commitments_by_phase": {
                "RR_PHASE0": {"status": "PROSPECTIVE_EXACT", "rendered_prompt_sha256": "a" * 64},
                "RR_PHASE1": {
                    "status": "DYNAMIC_SEALED_RR_STATE_RULE",
                    "template_text_sha256": "b" * 64,
                    "recovered_packet_canonical_sha256": source_sha["recovered"],
                    "state_source": "RR_PHASE0_STRICT_PARSED_CANONICAL_STATE_AND_SHA256",
                },
            },
            "protected_body_retention": False,
        }
        write_json(root / "STAGED_RUNTIME_INPUT_V1.json", stage)
        stage_file_sha = sha256_bytes((root / "STAGED_RUNTIME_INPUT_V1.json").read_bytes())
        attestation = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-process-attestation.v1",
            "authority": "LIVE_RUNTIME_IDENTITY_METADATA_ONLY__NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
            "status": "EXACT_ONE_TUPLE_LOOPBACK_PROCESS_ATTESTED",
            "runtime_stage_sha256": stage_file_sha,
            "process_identity": {
                "pid": 12345,
                "executable_path": stage["source_paths"]["server"],
                "executable_sha256": source_sha["server"],
                "executable_device": "123",
                "executable_inode": "456",
                "argv": copy.deepcopy(stage["server_argv"]),
                "cmdline_sha256": "9" * 64,
                "ggml_backend_path": stage["source_paths"]["backend"],
                "cuda_backend_mapped_path": stage["source_paths"]["backend"],
                "cuda_backend_sha256": source_sha["backend"],
                "model_mapped_path": stage["source_paths"]["model"],
                "model_sha256": source_sha["model"],
                "proxy_environment_empty": True,
            },
            "listener": {
                "listen_host": "127.0.0.1", "listen_port": 8080,
                "socket_inode": "789",
            },
            "readiness": {
                "health_sha256": "a" * 64, "slots_sha256": "b" * 64,
                "slot_count": 1,
            },
            "model_sha256": source_sha["model"],
            "llama_server_sha256": source_sha["server"],
            "cuda_backend_sha256": source_sha["backend"],
            "launcher_sha256": source_sha["launcher"],
            "successor_bridge_sha256": "7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91",
            "server_stdout_stderr_retained": False,
            "protected_bodies_retained": False,
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        write_json(root / "PROCESS_ATTESTATION_V1.json", attestation)
        dynamic_core = {
            "phase_id": "RR_PHASE1",
            "rendered_prompt_sha256": "2" * 64,
            "tokenize_request_sha256": "3" * 64,
            "tokenize_repeat_count": 3,
            "tokenize_raw_response_sha256": "4" * 64,
            "token_array_sha256": "5" * 64,
            "prompt_tokens": 20000,
            "phase_output_cap": 7168,
            "context_window_tokens": 32768,
            "remaining_context_margin_tokens": 5600,
            "completion_prompt_n_equal": True,
            "status": "PASS_DYNAMIC_RR1_PRETOKENIZE_FIT",
        }
        dynamic = {
            "schema_version": "orion.p1.scienceagentbench.dynamic-rr1-pretokenize-binding.v1",
            "authority": "DYNAMIC_PROMPT_FIT_METADATA_ONLY__NO_BODY_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
            "tuple_identity": copy.deepcopy(TUPLE),
            **copy.deepcopy(dynamic_core),
            "protected_bodies_retained": False,
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        write_json(attempt / "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json", dynamic)
        base_record = {
            "task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101,
            "input_tokens": 24000, "output_tokens": 1200, "tool_calls": 0,
            "wall_time_seconds": "900.000000000", "local_execution_wall_time_seconds": None,
            "billed_cost_usd": None, "failure": None,
            "raw_output_sha256": "6" * 64, "candidate_program_sha256": "7" * 64,
        }
        capture = {
            "schema_version": "orion.p1.scienceagentbench.lunarc-generation-attempt-capture.v1",
            "authority": "GENERATION_TIMING_METADATA_ONLY__ALLOCATION_AND_OUTCOMES_UNFINALIZED",
            "status": "TIMING_CAPTURED__ALLOCATION_FINALIZATION_PENDING",
            "run_plan_sha256": "66d54431f6d8ac479b2009759a4cd7b6d5f7d489f4b8f4b6a99d0f591616cc81",
            "task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101,
            "phase_sequence": ["RR_PHASE0", "RR_PHASE1"],
            "base_candidate_record": base_record,
            "base_candidate_record_canonical_sha256": canonical_hash(base_record),
            "cost_measurement_binding_sha256": "779204ac91ba4b11a4982d2b89d09f3e0788dfa035236f6fa1324a7b4bef3411",
            "exclusive_gpu_count": "1",
            "clock_id": "CLOCK_MONOTONIC_RAW", "clock_api": "clock_gettime_ns",
            "monotonic_start_ns": "1000000000", "monotonic_end_ns": "2000000000",
            "monotonic_elapsed_ns": "1000000000",
            "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
            "slurm_job_identity": copy.deepcopy(identity["slurm_job_identity"]),
            "slurm_in_job_snapshot_sha256": identity["slurm_in_job_snapshot_sha256"],
            "candidate_bodies_opened": False,
            "official_evaluator_invoked": False,
            "official_outcomes_opened": False,
            "scientific_authority_delta": "NONE",
        }
        write_json(attempt / "ATTEMPT_CAPTURE_V1.json", capture)
        bridge = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-direct-route-bridge-binding.v1",
            "authority": "ONE_TUPLE_ATTEMPT_BINDING_METADATA_ONLY__ALLOCATION_OUTCOMES_AND_918_LEDGER_UNFINALIZED",
            "status": "BOUND_ONE_TUPLE_CAPTURE__POST_JOB_FINALIZATION_PENDING",
            "tuple_identity": copy.deepcopy(TUPLE),
            "run_plan_binding_extension": extension,
            "run_plan_binding_extension_sha256": canonical_hash(extension),
            "runtime_stage_sha256": stage_file_sha,
            "process_attestation_sha256": sha256_bytes(
                (root / "PROCESS_ATTESTATION_V1.json").read_bytes()
            ),
            "attempt_capture_canonical_sha256": canonical_hash(capture),
            "request_bindings": [
                {
                    "phase_id": "RR_PHASE0", "rendered_prompt_sha256": "a" * 64,
                    "canonical_request_sha256": "b" * 64, "cache_prompt": False,
                    "completion_raw_response_sha256": "c" * 64,
                    "transport_status": "SENT_RESPONSE_ACCEPTED",
                },
                {
                    "phase_id": "RR_PHASE1", "rendered_prompt_sha256": "d" * 64,
                    "canonical_request_sha256": "e" * 64, "cache_prompt": False,
                    "completion_raw_response_sha256": "f" * 64,
                    "transport_status": "SENT_RESPONSE_ACCEPTED",
                },
            ],
            "dynamic_rr1_pretokenize_binding": copy.deepcopy(dynamic_core),
            "dynamic_rr1_pretokenize_binding_canonical_sha256": canonical_hash(dynamic_core),
            "protected_bodies_retained": False,
            "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
            "allocation_status": "CANNOT_CHECK_PENDING_ONE_TUPLE_SCHEDULER_FINALIZATION",
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        bridge["dynamic_rr1_pretokenize_file_sha256"] = sha256_bytes(
            (attempt / "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json").read_bytes()
        )
        write_json(attempt / "DIRECT_ROUTE_BRIDGE_BINDING_V1.json", bridge)
        cleanup = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-server-cleanup.v1",
            "authority": "PROCESS_CLEANUP_METADATA_ONLY",
            "status": "PASS_OWNED_PROCESS_GROUPS_ABSENT",
            "preflight_succeeded": True,
            "managed_processes": [
                {
                    "label": "unchanged-wrapper", "status": "NONINVOKED",
                    "binding_role": "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED",
                    "process_started": False, "process_group_id": None,
                    "termination_signal": None, "process_group_absent_after_cleanup": True,
                    "process_absent_after_cleanup": True,
                },
                {
                    "label": "llama-server", "process_started": True,
                    "process_group_id": 12345, "termination_signal": "SIGTERM",
                    "return_code": 0, "process_group_absent_after_cleanup": True,
                    "process_absent_after_cleanup": True,
                },
            ],
            "protected_bodies_retained": False,
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        write_json(root / "SERVER_CLEANUP_V1.json", cleanup)
        raw_names = (
            "POST_JOB_SACCT_V1.txt", "POST_JOB_SACCT_NONOVERLAP_V1.txt",
            "POST_JOB_SCONTROL_V1.txt", "SCHEDULER_CONFIG_V1.txt",
            "SCHEDULER_PARTITION_V1.txt", "SCHEDULER_NODE_V1.txt",
        )
        provenance = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-scheduler-capture-provenance.v1",
            "authority": "EXACT_SCHEDULER_CAPTURE_COMMAND_AND_RAW_BYTE_BINDING_ONLY",
            "status": "PASS_EXACT_POST_JOB_SCHEDULER_CAPTURE",
            "slurm_job_id": JOB_ID,
            "partition": PARTITION,
            "node_name": NODE,
            "allocation_started_at": START,
            "allocation_ended_at": END,
            "capture_argv": materialized_argv(),
            "raw_file_sha256": {
                name: sha256_bytes((root / name).read_bytes()) for name in raw_names
            },
            "credential_environment_read": False,
            "stderr_retained": False,
            "job_submitted": False,
            "scientific_authority_delta": "NONE",
        }
        write_json(root / "SCHEDULER_CAPTURE_PROVENANCE_V1.json", provenance)
        self.refresh_export(root)
        for directory in (root, attempt, runtime_inputs):
            directory.chmod(0o700)
        for path in root.rglob("*"):
            if path.is_file():
                path.chmod(0o600)
        (runtime_inputs / "MASKED_PACKET.json").chmod(0)
        (runtime_inputs / "RECOVERED_PACKET.json").chmod(0)

    def refresh_export(self, root: Path) -> None:
        attempt = root / "attempt"
        source_paths = [root / name for name in ROOT_INPUTS]
        source_paths.append(root / "runtime-inputs/RUN_PLAN.json")
        source_paths.extend(attempt / name for name in ATTEMPT_INPUTS[:2])
        if (attempt / "ATTEMPT_CAPTURE_V1.json").exists():
            source_paths.extend(
                attempt / name
                for name in (
                    "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json",
                    "DIRECT_ROUTE_BRIDGE_BINDING_V1.json",
                    "ATTEMPT_CAPTURE_V1.json",
                )
            )
        else:
            source_paths.extend(
                attempt / name
                for name in (
                    "DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json",
                    "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json",
                )
            )
        source_hashes = {
            str(path.relative_to(root)): sha256_bytes(path.read_bytes()) for path in source_paths
        }
        identity = read_json(attempt / "SLURM_IDENTITY_AND_SNAPSHOT_V1.json")
        export = {
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-one-tuple-scheduler-export.v1",
            "authority": "CANONICAL_SCHEDULER_AND_IN_JOB_METADATA_BINDING_ONLY",
            "status": "SCHEDULER_CONFIRMED_ONE_TUPLE_TERMINAL_EXCLUSIVE_GRES",
            "tuple_identity": copy.deepcopy(TUPLE),
            "slurm_job_identity": copy.deepcopy(identity["slurm_job_identity"]),
            "capture_argv": materialized_argv(),
            "source_sha256": source_hashes,
            "in_job_snapshot_sha256": identity["slurm_in_job_snapshot_sha256"],
            "scheduler_record_source": "TERMINAL_SACCT__POST_JOB_SCONTROL_DD__CONFIG_PARTITION_NODE__NONOVERLAP_SACCT__IN_JOB_GPU_IDENTITY",
            "scheduler_job_state": "COMPLETED",
            "scheduler_exit_code": "0:0",
            "allocation_started_at": START,
            "allocation_ended_at": END,
            "node_name": NODE,
            "partition": PARTITION,
            "account": ACCOUNT,
            "allocated_cpu_count": "8",
            "allocated_memory": "64G",
            "timelimit_raw_minutes": "60",
            "constraints": "",
            "allocated_gpu_count": "1",
            "gpu_allocations": [{
                "node_name": NODE, "gres_name": "gpu", "gres_type": "a40",
                "gres_index": "0", "gpu_uuid": GPU_UUID,
            }],
            "exclusive_gres_status": "SCHEDULER_CONFIRMED_CONSUMABLE_EXCLUSIVE_GRES",
            "attempt_scope_status": "ONE_TASK_ARM_ATTEMPT_ONLY_CONFIRMED",
            "nonoverlap_query_status": "NODE_WIDE_BOUNDED_A40_GRES_QUERY_NO_OVERLAP_CONFIRMED",
            "nonoverlap_conflict_count": 0,
            "whole_node_exclusivity_claimed": False,
            "protected_bodies_retained": False,
            "official_evaluator_invoked": False,
            "official_outcomes_opened": False,
            "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
            "production_admissibility": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
        }
        write_private(root / "SCHEDULER_EXPORT_V1.jsonl", canonical_bytes(export) + b"\n")

    def refresh_capture_provenance(self, root: Path) -> None:
        path = root / "SCHEDULER_CAPTURE_PROVENANCE_V1.json"
        provenance = read_json(path)
        provenance["raw_file_sha256"] = {
            name: sha256_bytes((root / name).read_bytes())
            for name in (
                "POST_JOB_SACCT_V1.txt",
                "POST_JOB_SACCT_NONOVERLAP_V1.txt",
                "POST_JOB_SCONTROL_V1.txt",
                "SCHEDULER_CONFIG_V1.txt",
                "SCHEDULER_PARTITION_V1.txt",
                "SCHEDULER_NODE_V1.txt",
            )
        }
        write_json(path, provenance)

    def refresh_export_source_hashes(self, root: Path) -> None:
        path = root / "SCHEDULER_EXPORT_V1.jsonl"
        export = read_json(path)
        attempt = root / "attempt"
        sources = [root / name for name in ROOT_INPUTS]
        sources.append(root / "runtime-inputs/RUN_PLAN.json")
        sources.extend(attempt / name for name in ATTEMPT_INPUTS[:2])
        if (attempt / "ATTEMPT_CAPTURE_V1.json").exists():
            sources.extend(attempt / name for name in ATTEMPT_INPUTS[2:])
        else:
            sources.extend(
                attempt / name
                for name in (
                    "DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json",
                    "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json",
                )
            )
        export["source_sha256"] = {
            str(source.relative_to(root)): sha256_bytes(source.read_bytes())
            for source in sources
        }
        write_private(path, canonical_bytes(export) + b"\n")


def load_module() -> ModuleType | None:
    if not MODULE_PATH.is_file():
        return None
    spec = importlib.util.spec_from_file_location("protected_rr1_one_tuple_finalizer_v1", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load finalizer module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    return module


class ProtectedRR1OneTupleFinalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.fixture = SyntheticFixture()

    def require_module(self) -> ModuleType:
        if self.module is None:
            self.skipTest("implementation intentionally absent for TDD RED")
        return self.module

    def run_fixture(self, mutate: Any = None, *, refresh: bool = True) -> tuple[int, dict[str, Any], Path]:
        module = self.require_module()
        holder = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(holder.cleanup)
        base = Path(holder.name)
        evidence = base / "evidence"
        output = base / "finalized"
        evidence.mkdir()
        self.fixture.create(evidence)
        if mutate is not None:
            mutate(evidence)
            if refresh:
                self.fixture.refresh_capture_provenance(evidence)
                self.fixture.refresh_export(evidence)
        code, receipt = module.finalize(evidence.resolve(), output.resolve())
        return code, receipt, output

    def assert_cannot_check(self, result: tuple[int, dict[str, Any], Path]) -> dict[str, Any]:
        code, receipt, output = result
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "CANNOT_CHECK_ONE_TUPLE_FINALIZATION")
        self.assertRegex(receipt["failure_detail_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("failure_detail", receipt)
        self.assertTrue((output / "ONE_TUPLE_FINALIZATION_CANNOT_CHECK_V1.json").is_file())
        self.assertFalse((output / "ONE_TUPLE_FINALIZATION_RECEIPT_V1.json").exists())
        return receipt

    def test_01_required_implementation_artifacts_exist(self) -> None:
        self.assertTrue(MODULE_PATH.is_file(), "TDD RED: finalizer module is absent")
        self.assertTrue(CONTRACT_PATH.is_file())
        self.assertTrue(SCHEMA_PATH.is_file())

    def test_02_contract_freezes_live_scheduler_argv_and_authority(self) -> None:
        contract = read_json(CONTRACT_PATH)
        self.assertEqual(contract["base_commit"], "eba4a67e8607cdef96a2bb038d685a9a5d548599")
        self.assertEqual(contract["scheduler_audit_binding"]["slurm_version"], "23.11.3")
        self.assertEqual(contract["scheduler_audit_binding"]["min_job_age_seconds"], 300)
        argv = contract["capture_command_argv_templates"]
        self.assertEqual(argv["terminal_sacct"][:6], ["sacct", "-a", "-X", "-D", "-j", "<SLURM_JOB_ID>"])
        self.assertIn("JobIDRaw,Partition,State,ExitCode,DerivedExitCode", argv["terminal_sacct"][-1])
        self.assertEqual(argv["post_job_scontrol"], ["scontrol", "show", "job", "-dd", "<SLURM_JOB_ID>"])
        self.assertEqual(
            argv["scheduler_partition"],
            ["scontrol", "show", "partition", "<PARTITION>", "-o"],
        )
        self.assertEqual(argv["scheduler_node"], ["scontrol", "show", "node", "-dd", "-o", "<NODE>"])
        self.assertEqual(argv["nonoverlap_sacct"][:5], ["sacct", "-a", "-X", "-D", "-S"])
        self.assertEqual(contract["production_admissibility"], "CANNOT_CHECK")
        self.assertEqual(contract["scientific_authority_delta"], "NONE")

    def test_03_cli_argv_is_exact_and_absolute(self) -> None:
        module = self.require_module()
        with self.assertRaises(module.FinalizationError):
            module.parse_cli(["finalize", "--evidence-root", "relative", "--output-root", "/tmp/x"])
        with self.assertRaises(module.FinalizationError):
            module.parse_cli(["finalize", "--evidence-root", "/tmp/e", "--output-root", "/tmp/o", "extra"])
        args = module.parse_cli(["finalize", "--evidence-root", "/tmp/e", "--output-root", "/tmp/o"])
        self.assertEqual(args.evidence_root, Path("/tmp/e"))

    def test_04_valid_synthetic_evidence_emits_bounded_pass(self) -> None:
        code, receipt, output = self.run_fixture()
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "PASS_ONE_TUPLE_POST_JOB_METADATA_FINALIZATION")
        self.assertEqual(receipt["terminal_job_state"], "COMPLETED")
        self.assertEqual(receipt["terminal_exit_code"], "0:0")
        self.assertEqual(receipt["allocation"]["gpu_allocations"][0]["gpu_uuid"], GPU_UUID)
        self.assertEqual(receipt["exclusive_gres_status"], "SCHEDULER_CONFIRMED_CONSUMABLE_EXCLUSIVE_GRES")
        self.assertEqual(
            receipt["nonoverlap_status"],
            "NODE_WIDE_BOUNDED_A40_GRES_QUERY_NO_OVERLAP_CONFIRMED",
        )
        self.assertFalse(receipt["allocation"]["whole_node_exclusivity_claimed"])
        self.assertEqual(receipt["runner_v2_population_ledger_status"], "NOT_FINALIZED_918_TUPLES")
        self.assertEqual(receipt["production_admissibility"], "CANNOT_CHECK")
        self.assertEqual(receipt["scientific_authority_delta"], "NONE")
        self.assertEqual(receipt["post_job_sacct_sha256"], receipt["input_artifact_sha256"]["POST_JOB_SACCT_V1.txt"])
        self.assertEqual(receipt["post_job_scontrol_sha256"], receipt["input_artifact_sha256"]["POST_JOB_SCONTROL_V1.txt"])
        self.assertNotEqual(receipt["attempt_capture_file_sha256"], receipt["attempt_capture_canonical_sha256"])
        self.assertFalse(receipt["runner_v2_population_finalizer_invoked"])
        self.assertTrue((output / "ONE_TUPLE_FINALIZATION_RECEIPT_V1.json").is_file())
        self.assertFalse((output / "ONE_TUPLE_FINALIZATION_CANNOT_CHECK_V1.json").exists())

    def test_05_sacct_parser_rejects_crlf_extra_rows_and_wrong_field_count(self) -> None:
        module = self.require_module()
        with self.assertRaises(module.FinalizationError):
            module.parse_sacct_snapshot(sacct_row().replace(b"\n", b"\r\n"), allow_multiple=False)
        with self.assertRaises(module.FinalizationError):
            module.parse_sacct_snapshot(sacct_row() + sacct_row(job_id="4000002"), allow_multiple=False)
        with self.assertRaises(module.FinalizationError):
            module.parse_sacct_snapshot(b"too|short|\n", allow_multiple=False)

    def test_06_scontrol_duplicate_required_key_fails_closed(self) -> None:
        for label, suffix in (
            ("exact", b"JobState=COMPLETED\n"),
            ("case-alias", b"jobstate=COMPLETED\n"),
        ):
            with self.subTest(label=label):
                def mutate(root: Path, payload: bytes = suffix) -> None:
                    path = root / "POST_JOB_SCONTROL_V1.txt"
                    path.write_bytes(path.read_bytes() + payload)
                self.assert_cannot_check(self.run_fixture(mutate))

    def test_07_config_partition_and_node_proofs_are_all_required(self) -> None:
        def mutate(root: Path) -> None:
            (root / "SCHEDULER_PARTITION_V1.txt").write_bytes(
                b"PartitionName=gpu Nodes=aurora[01-04] OverSubscribe=YES State=UP\n"
            )
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_08_scheduler_export_requires_canonical_single_lf_json_record(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            self.fixture.create(root)
            payload = (root / "SCHEDULER_EXPORT_V1.jsonl").read_bytes()
            with self.assertRaises(module.FinalizationError):
                module.parse_scheduler_export(payload.replace(b"\n", b"\r\n"))
            value = json.loads(payload)
            noncanonical = json.dumps(value, indent=2).encode() + b"\n"
            with self.assertRaises(module.FinalizationError):
                module.parse_scheduler_export(noncanonical)
            with self.assertRaises(module.FinalizationError):
                module.parse_scheduler_export(payload + payload)

    def test_09_source_hash_mismatch_fails_closed(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "POST_JOB_SACCT_V1.txt"
            path.write_bytes(path.read_bytes().replace(b"normal", b"urgent"))
        self.assert_cannot_check(self.run_fixture(mutate, refresh=False))

    def test_10_terminal_state_or_exit_code_not_successful_is_typed_cannot_check(self) -> None:
        def mutate(root: Path) -> None:
            (root / "POST_JOB_SACCT_V1.txt").write_bytes(sacct_row(state="FAILED", exit_code="1:0"))
            (root / "POST_JOB_SCONTROL_V1.txt").write_bytes(scontrol_snapshot(state="FAILED", end=END, exit_code="1:0"))
            export = json.loads((root / "SCHEDULER_EXPORT_V1.jsonl").read_text())
            export["scheduler_job_state"] = "FAILED"
            export["scheduler_exit_code"] = "1:0"
            (root / "SCHEDULER_EXPORT_V1.jsonl").write_bytes(canonical_bytes(export) + b"\n")
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_11_job_identity_mismatch_across_sacct_scontrol_and_in_job_fails(self) -> None:
        def mutate(root: Path) -> None:
            (root / "POST_JOB_SACCT_V1.txt").write_bytes(sacct_row(job_id="4000002"))
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_12_exact_one_a40_uuid_is_required(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "GPU_ALLOCATION_IDENTITY_V1.json"
            value = read_json(path)
            value["gpu"]["name"] = "NVIDIA H100"
            write_json(path, value)
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_13_gres_count_type_and_index_must_cross_bind(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "POST_JOB_SCONTROL_V1.txt"
            path.write_bytes(path.read_bytes().replace(b"gpu:a40:1(IDX:0)", b"gpu:a40:1(IDX:1)"))
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_14_nonoverlap_query_rejects_other_overlapping_a40_allocation(self) -> None:
        def mutate(root: Path) -> None:
            other = sacct_row(job_id="4000002", start="2026-08-24T11:05:00", end="2026-08-24T11:10:00")
            path = root / "POST_JOB_SACCT_NONOVERLAP_V1.txt"
            path.write_bytes(path.read_bytes() + other)
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_15_nonoverlap_query_allows_cpu_only_or_half_open_adjacent_jobs(self) -> None:
        def mutate(root: Path) -> None:
            cpu = sacct_row(
                job_id="4000002",
                start="2026-08-24T11:05:00",
                end="2026-08-24T11:10:00",
                alloc_tres="billing=4,cpu=4,mem=16G,node=1",
            )
            adjacent = sacct_row(job_id="4000003", start=END, end="2026-08-24T11:20:00")
            path = root / "POST_JOB_SACCT_NONOVERLAP_V1.txt"
            path.write_bytes(path.read_bytes() + cpu + adjacent)
        code, receipt, _ = self.run_fixture(mutate)
        self.assertEqual(code, 0)
        self.assertEqual(receipt["overlap_conflict_count"], 0)

    def test_16_environment_only_or_whole_node_exclusivity_claim_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            export = json.loads((root / "SCHEDULER_EXPORT_V1.jsonl").read_text())
            export["whole_node_exclusivity_claimed"] = True
            (root / "SCHEDULER_EXPORT_V1.jsonl").write_bytes(canonical_bytes(export) + b"\n")
        self.assert_cannot_check(self.run_fixture(mutate, refresh=False))

    def test_16a_full_102_task_plan_then_exact_tuple_seed_are_required(self) -> None:
        def mutate(root: Path) -> None:
            plan_path = root / "runtime-inputs/RUN_PLAN.json"
            plan = read_json(plan_path)
            plan["task_ids"] = ["1"]
            write_json(plan_path, plan)
            stage_path = root / "STAGED_RUNTIME_INPUT_V1.json"
            stage = read_json(stage_path)
            stage["source_sha256"]["plan"] = sha256_bytes(plan_path.read_bytes())
            write_json(stage_path, stage)
            attestation_path = root / "PROCESS_ATTESTATION_V1.json"
            attestation = read_json(attestation_path)
            attestation["runtime_stage_sha256"] = sha256_bytes(stage_path.read_bytes())
            write_json(attestation_path, attestation)
            bridge_path = root / "attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
            bridge = read_json(bridge_path)
            bridge["runtime_stage_sha256"] = sha256_bytes(stage_path.read_bytes())
            bridge["process_attestation_sha256"] = sha256_bytes(attestation_path.read_bytes())
            write_json(bridge_path, bridge)
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_16b_stage_process_bridge_and_dynamic_file_hash_chain_is_required(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "PROCESS_ATTESTATION_V1.json"
            value = read_json(path)
            value["runtime_stage_sha256"] = "f" * 64
            write_json(path, value)
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_17_attempt_capture_hash_and_pending_allocation_must_bind(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "attempt/ATTEMPT_CAPTURE_V1.json"
            value = read_json(path)
            value["allocation_status"] = "EXCLUSIVE_NO_OVERLAP_CONFIRMED"
            write_json(path, value)
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_18_attempt_cannot_check_sidecar_forces_typed_finalizer_cannot_check(self) -> None:
        def mutate(root: Path) -> None:
            attempt = root / "attempt"
            capture = read_json(attempt / "ATTEMPT_CAPTURE_V1.json")
            (attempt / "ATTEMPT_CAPTURE_V1.json").unlink()
            (attempt / "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json").unlink()
            (attempt / "DIRECT_ROUTE_BRIDGE_BINDING_V1.json").unlink()
            sidecar = {
                "schema_version": "orion.p1.scienceagentbench.lunarc-generation-attempt-cannot-check.v1",
                "authority": "GENERATION_CAPTURE_FAILURE_METADATA_ONLY",
                "status": "CANNOT_CHECK",
                "run_plan_sha256": "66d54431f6d8ac479b2009759a4cd7b6d5f7d489f4b8f4b6a99d0f591616cc81",
                "task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101,
                "expected_phase_sequence": ["RR_PHASE0", "RR_PHASE1"],
                "attempted_phase_sequence": ["RR_PHASE0"],
                "monotonic_start_ns": "1000000000",
                "monotonic_end_ns": "1500000000",
                "failure_code": "DIRECT_ROUTE_EXECUTION_FAILED",
                "failure_detail_sha256": "e" * 64,
                "captured_exception_detail_sha256": "d" * 64,
                "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
                "slurm_job_identity": capture["slurm_job_identity"],
                "slurm_in_job_snapshot_sha256": capture["slurm_in_job_snapshot_sha256"],
                "runner_v2_record_emitted": False,
                "official_evaluator_invoked": False,
                "official_outcomes_opened": False,
                "scientific_authority_delta": "NONE",
            }
            write_json(attempt / "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json", sidecar)
            failure_bridge = {
                "schema_version": "orion.p1.scienceagentbench.protected-rr1-direct-route-failure-binding.v1",
                "authority": "ONE_TUPLE_FAILURE_BINDING_METADATA_ONLY",
                "status": "CANNOT_CHECK",
                "tuple_identity": copy.deepcopy(TUPLE),
                "runtime_stage_sha256": sha256_bytes((root / "STAGED_RUNTIME_INPUT_V1.json").read_bytes()),
                "process_attestation_sha256": sha256_bytes((root / "PROCESS_ATTESTATION_V1.json").read_bytes()),
                "adapter_cannot_check_file_sha256": sha256_bytes((attempt / "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json").read_bytes()),
                "request_bindings": [],
                "dynamic_rr1_pretokenize_bindings": [],
                "protected_bodies_retained": False,
                "runner_v2_population_ledger_status": "NOT_FINALIZED_918_TUPLES",
                "production_admissibility": "CANNOT_CHECK",
                "scientific_authority_delta": "NONE",
            }
            write_json(attempt / "DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json", failure_bridge)
        receipt = self.assert_cannot_check(self.run_fixture(mutate))
        self.assertEqual(receipt["failure_code"], "ATTEMPT_CAPTURE_CANNOT_CHECK")

    def test_19_dynamic_tokenize_fit_and_bridge_hashes_are_required(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "attempt/DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json"
            value = read_json(path)
            value["completion_prompt_n_equal"] = False
            value["status"] = "PRETOKENIZE_FIT__COMPLETION_COUNT_PENDING"
            write_json(path, value)
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_20_cleanup_requires_every_owned_process_and_group_absent(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "SERVER_CLEANUP_V1.json"
            value = read_json(path)
            value["managed_processes"][1]["process_group_absent_after_cleanup"] = False
            write_json(path, value)
        receipt = self.assert_cannot_check(self.run_fixture(mutate))
        self.assertEqual(receipt["failure_code"], "CLEANUP_CANNOT_CHECK")

    def test_21_forbidden_body_or_token_id_fields_fail_before_success(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
            value = read_json(path)
            value["prompt_body"] = "synthetic but forbidden"
            write_json(path, value)
        self.assert_cannot_check(self.run_fixture(mutate))

    def test_22_symlinked_evidence_file_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "POST_JOB_SACCT_V1.txt"
            held = root / "held.txt"
            held.write_bytes(path.read_bytes())
            path.unlink()
            path.symlink_to(held)
        self.assert_cannot_check(self.run_fixture(mutate, refresh=False))

    def test_23_preexisting_output_root_is_rejected_without_overwrite(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            output = base / "output"
            evidence.mkdir()
            output.mkdir()
            sentinel = output / "sentinel"
            sentinel.write_text("keep")
            with self.assertRaises(module.FinalizationError):
                module.finalize(evidence.resolve(), output.resolve())
            self.assertEqual(sentinel.read_text(), "keep")

    def test_24_cli_terminal_is_body_free_and_exit_codes_are_exact(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            output = base / "output"
            evidence.mkdir()
            self.fixture.create(evidence)
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = module.main([
                    "finalize", "--evidence-root", str(evidence.resolve()),
                    "--output-root", str(output.resolve()),
                ])
            self.assertEqual(code, 0)
            self.assertEqual(stream.getvalue().strip(), "P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS")

    def test_25_output_schema_fields_are_exact(self) -> None:
        _, receipt, _ = self.run_fixture()
        schema = read_json(SCHEMA_PATH)
        self.assertEqual(set(receipt), set(schema["success"]["required_fields"]))
        self.assertFalse(receipt["protected_bodies_opened_by_finalizer"])
        self.assertFalse(receipt["protected_bodies_retained"])
        self.assertFalse(receipt["generation_invoked_by_finalizer"])
        self.assertFalse(receipt["network_invoked_by_finalizer"])
        self.assertFalse(receipt["external_api_invoked_by_finalizer"])
        self.assertFalse(receipt["credential_environment_read_by_finalizer"])
        self.assertTrue(receipt["one_tuple_generation_observed"])
        self.assertEqual(receipt["model_completion_calls"], 2)
        self.assertFalse(receipt["task_execution_invoked"])
        self.assertFalse(receipt["official_evaluator_invoked"])
        self.assertFalse(receipt["official_outcomes_opened"])
        self.assertFalse(receipt["runner_v2_population_finalizer_invoked"])

    def test_26_module_never_executes_scheduler_submission_or_opens_outcomes(self) -> None:
        self.require_module()
        source = MODULE_PATH.read_text()
        self.assertNotIn("sbatch", source)
        self.assertNotIn("finalize_v2_candidate_ledger(", source)
        self.assertNotIn("official_outcome", source.lower().replace("official_outcomes_opened", ""))
        self.assertIn("subprocess.run", source)
        self.assertNotIn("urlopen", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("http.client", source)
        self.assertNotIn("os.environ", source)

    def test_27_capture_helper_uses_exact_argv_order_and_fixed_environment(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            evidence.mkdir()
            self.fixture.create(evidence)
            output = base / "capture"
            argv = materialized_argv()
            response_by_argv = {
                tuple(argv["terminal_sacct"]): (evidence / "POST_JOB_SACCT_V1.txt").read_bytes(),
                tuple(argv["post_job_scontrol"]): (evidence / "POST_JOB_SCONTROL_V1.txt").read_bytes(),
                tuple(argv["scheduler_config"]): (evidence / "SCHEDULER_CONFIG_V1.txt").read_bytes(),
                tuple(argv["scheduler_partition"]): (evidence / "SCHEDULER_PARTITION_V1.txt").read_bytes(),
                tuple(argv["scheduler_node"]): (evidence / "SCHEDULER_NODE_V1.txt").read_bytes(),
                tuple(argv["nonoverlap_sacct"]): (evidence / "POST_JOB_SACCT_NONOVERLAP_V1.txt").read_bytes(),
            }
            calls: list[list[str]] = []

            def fake_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                calls.append(list(actual))
                self.assertEqual(
                    set(kwargs), {"stdout", "stderr", "env", "check"}
                )
                self.assertIs(kwargs["stdout"], module.subprocess.PIPE)
                self.assertIs(kwargs["stderr"], module.subprocess.PIPE)
                self.assertEqual(kwargs["env"], module.CAPTURE_ENVIRONMENT)
                self.assertFalse(kwargs["check"])
                return SimpleNamespace(
                    returncode=0, stdout=response_by_argv[tuple(actual)], stderr=b""
                )

            provenance = module.capture_scheduler(
                JOB_ID, PARTITION, NODE, output.resolve(), runner=fake_runner
            )
            expected_order = [
                argv["terminal_sacct"], argv["post_job_scontrol"],
                argv["scheduler_config"], argv["scheduler_partition"],
                argv["scheduler_node"], argv["nonoverlap_sacct"],
            ]
            self.assertEqual(calls, expected_order)
            self.assertEqual(provenance["capture_argv"], argv)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
            for path in output.iterdir():
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_28_capture_failure_rolls_back_only_the_new_private_root(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory) / "capture"
            calls = 0

            def fake_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                nonlocal calls
                calls += 1
                if calls == 1:
                    return SimpleNamespace(returncode=0, stdout=sacct_row(), stderr=b"")
                return SimpleNamespace(returncode=1, stdout=b"", stderr=b"synthetic")

            with self.assertRaises(module.FinalizationError):
                module.capture_scheduler(
                    JOB_ID, PARTITION, NODE, output.resolve(), runner=fake_runner
                )
            self.assertFalse(output.exists())

    def test_29_nonoverlap_target_row_must_be_present_once(self) -> None:
        def absent(root: Path) -> None:
            (root / "POST_JOB_SACCT_NONOVERLAP_V1.txt").write_bytes(
                sacct_row(
                    job_id="4000002",
                    alloc_tres="billing=4,cpu=4,mem=16G,node=1",
                )
            )

        def duplicate(root: Path) -> None:
            path = root / "POST_JOB_SACCT_NONOVERLAP_V1.txt"
            path.write_bytes(path.read_bytes() + sacct_row())

        for label, mutate in (("absent", absent), ("duplicate", duplicate)):
            with self.subTest(label=label):
                receipt = self.assert_cannot_check(self.run_fixture(mutate))
                self.assertIn(
                    receipt["failure_code"],
                    {"NONOVERLAP_CANNOT_CHECK", "EVIDENCE_PARSE_INVALID"},
                )

    def test_30_nonoverlap_generic_unknown_gpu_or_unknown_end_fails_closed(self) -> None:
        rows = {
            "generic": sacct_row(
                job_id="4000002", start="2026-08-24T11:05:00",
                end="2026-08-24T11:10:00",
                alloc_tres="billing=8,cpu=8,gres/gpu=1,mem=64G,node=1",
            ),
            "unknown_type": sacct_row(
                job_id="4000002", start="2026-08-24T11:05:00",
                end="2026-08-24T11:10:00",
                alloc_tres="billing=8,cpu=8,gres/gpu:unknown=1,gres/gpu=1,mem=64G,node=1",
            ),
            "unknown_end": sacct_row(
                job_id="4000002", start="2026-08-24T11:05:00", end="Unknown"
            ),
        }
        for label, row in rows.items():
            with self.subTest(label=label):
                def mutate(root: Path, payload: bytes = row) -> None:
                    path = root / "POST_JOB_SACCT_NONOVERLAP_V1.txt"
                    path.write_bytes(path.read_bytes() + payload)
                receipt = self.assert_cannot_check(self.run_fixture(mutate))
                self.assertEqual(receipt["failure_code"], "NONOVERLAP_CANNOT_CHECK")

    def test_31_capture_argv_tamper_fails_even_when_hash_maps_are_refreshed(self) -> None:
        def mutate(root: Path) -> None:
            provenance_path = root / "SCHEDULER_CAPTURE_PROVENANCE_V1.json"
            provenance = read_json(provenance_path)
            provenance["capture_argv"]["terminal_sacct"].append("--synthetic-tamper")
            write_json(provenance_path, provenance)
            export_path = root / "SCHEDULER_EXPORT_V1.jsonl"
            export = read_json(export_path)
            export["capture_argv"] = copy.deepcopy(provenance["capture_argv"])
            write_private(export_path, canonical_bytes(export) + b"\n")
            self.fixture.refresh_export_source_hashes(root)

        receipt = self.assert_cannot_check(self.run_fixture(mutate, refresh=False))
        self.assertIn(receipt["failure_code"], {"SCHEDULER_CAPTURE_FAILED", "ARGV_INVALID"})

    def test_32_source_hash_map_rejects_extra_and_missing_entries(self) -> None:
        def extra(root: Path) -> None:
            path = root / "SCHEDULER_EXPORT_V1.jsonl"
            export = read_json(path)
            export["source_sha256"]["synthetic-extra"] = "f" * 64
            write_private(path, canonical_bytes(export) + b"\n")

        def missing(root: Path) -> None:
            path = root / "SCHEDULER_EXPORT_V1.jsonl"
            export = read_json(path)
            export["source_sha256"].pop("POST_JOB_SACCT_V1.txt")
            write_private(path, canonical_bytes(export) + b"\n")

        for label, mutate in (("extra", extra), ("missing", missing)):
            with self.subTest(label=label):
                receipt = self.assert_cannot_check(
                    self.run_fixture(mutate, refresh=False)
                )
                self.assertEqual(receipt["failure_code"], "CROSS_BINDING_MISMATCH")

    def test_33_hardlinks_and_nonprivate_evidence_are_rejected(self) -> None:
        def hardlink(root: Path) -> None:
            os.link(root / "POST_JOB_SACCT_V1.txt", root / "synthetic-hardlink")

        def readable_file(root: Path) -> None:
            (root / "POST_JOB_SACCT_V1.txt").chmod(0o640)

        def readable_directory(root: Path) -> None:
            (root / "attempt").chmod(0o750)

        for label, mutate in (
            ("hardlink", hardlink),
            ("readable-file", readable_file),
            ("readable-directory", readable_directory),
        ):
            with self.subTest(label=label):
                receipt = self.assert_cannot_check(self.run_fixture(mutate))
                self.assertEqual(receipt["failure_code"], "INPUT_SET_INVALID")

    def test_34_symlinked_output_parent_is_rejected(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            evidence.mkdir()
            self.fixture.create(evidence)
            real_parent = base / "real-parent"
            real_parent.mkdir(mode=0o700)
            alias = base / "alias"
            alias.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaises(module.FinalizationError):
                module.finalize(evidence.resolve(), alias / "output")
            self.assertFalse((real_parent / "output").exists())

    def test_35_post_read_path_swap_is_detected_by_named_inode_recheck(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            path = root / "held.txt"
            write_private(path, b"original\n")
            parent_fd = os.open(root, os.O_RDONLY)
            real_read = module.os.read
            swapped = False

            def swapping_read(fd: int, count: int) -> bytes:
                nonlocal swapped
                payload = real_read(fd, count)
                if not swapped:
                    swapped = True
                    path.rename(root / "detached.txt")
                    write_private(path, b"replacement\n")
                return payload

            try:
                with mock.patch.object(module.os, "read", side_effect=swapping_read):
                    with self.assertRaises(module.FinalizationError):
                        module._read_held(parent_fd, "held.txt", "swap fixture")
            finally:
                os.close(parent_fd)

    def test_36_success_output_directory_and_file_modes_are_exact(self) -> None:
        code, _, output = self.run_fixture()
        self.assertEqual(code, 0)
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
        receipt = output / "ONE_TUPLE_FINALIZATION_RECEIPT_V1.json"
        self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
        self.assertEqual(receipt.stat().st_nlink, 1)

    def test_37_nested_body_and_token_id_key_aliases_are_rejected(self) -> None:
        aliases = ("token_ids", "Token-IDs", "completion_body", "PromptBody")
        for alias in aliases:
            with self.subTest(alias=alias):
                def mutate(root: Path, key: str = alias) -> None:
                    path = root / "attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
                    bridge = read_json(path)
                    bridge["synthetic_nested"] = [{"deeper": {key: "forbidden"}}]
                    write_json(path, bridge)
                receipt = self.assert_cannot_check(self.run_fixture(mutate))
                self.assertEqual(receipt["failure_code"], "FORBIDDEN_BODY_FIELD")

    def test_38_private_packet_traps_are_never_opened(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            output = base / "output"
            evidence.mkdir()
            self.fixture.create(evidence)
            real_open = module.os.open
            opened: list[str] = []

            def recording_open(path: Any, *args: Any, **kwargs: Any) -> int:
                try:
                    opened.append(os.fspath(path))
                except TypeError:
                    pass
                return real_open(path, *args, **kwargs)

            with mock.patch.object(module.os, "open", side_effect=recording_open):
                code, _ = module.finalize(evidence.resolve(), output.resolve())
            self.assertEqual(code, 0)
            basenames = {Path(name).name for name in opened}
            self.assertNotIn("MASKED_PACKET.json", basenames)
            self.assertNotIn("RECOVERED_PACKET.json", basenames)

    def test_39_finalize_has_no_scheduler_network_api_or_environment_route(self) -> None:
        import socket

        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            output = base / "output"
            evidence.mkdir()
            self.fixture.create(evidence)
            forbidden = AssertionError("forbidden finalize side effect")
            with (
                mock.patch.object(module.subprocess, "run", side_effect=forbidden),
                mock.patch.object(module.os, "getenv", side_effect=forbidden),
                mock.patch.object(socket, "socket", side_effect=forbidden),
                mock.patch.object(socket, "create_connection", side_effect=forbidden),
            ):
                code, receipt = module.finalize(evidence.resolve(), output.resolve())
            self.assertEqual(code, 0)
            self.assertFalse(receipt["network_invoked_by_finalizer"])
            self.assertFalse(receipt["external_api_invoked_by_finalizer"])
            self.assertFalse(receipt["credential_environment_read_by_finalizer"])

    def test_40_contract_schema_and_normalized_module_self_binding_is_exact(self) -> None:
        module = self.require_module()
        contract_bytes = CONTRACT_PATH.read_bytes()
        schema_bytes = SCHEMA_PATH.read_bytes()
        module_bytes = MODULE_PATH.read_bytes()
        contract = read_json(CONTRACT_PATH)
        binding = contract["self_binding"]
        self.assertEqual(sha256_bytes(contract_bytes), module.CONTRACT_SHA256)
        self.assertEqual(sha256_bytes(schema_bytes), module.SCHEMA_SHA256)
        self.assertEqual(binding["output_schema_sha256"], module.SCHEMA_SHA256)
        self.assertEqual(
            sha256_bytes(module.normalized_module_bytes(module_bytes)),
            module.NORMALIZED_MODULE_SHA256,
        )
        self.assertEqual(
            binding["normalized_module_sha256"], module.NORMALIZED_MODULE_SHA256
        )

    def test_41_body_free_manifest_and_checksum_set_bind_every_export(self) -> None:
        manifest = read_json(BODY_FREE_MANIFEST_PATH)
        exported = manifest["exported_files"]
        expected = {
            "DEVELOPMENT_PACKET.md", "FINALIZER_CONTRACT_V1.json",
            "FINALIZER_OUTPUT_SCHEMA_V1.json", "HANDOFF_V1.md",
            "SYNTHETIC_VALIDATION_RECEIPT_V1.json",
            "protected_rr1_one_tuple_finalizer_v1.py",
            "validate_protected_rr1_one_tuple_finalizer_v1.py",
        }
        self.assertEqual(set(exported), expected)
        for name, binding in exported.items():
            path = ROOT / name
            self.assertEqual(set(binding), {"bytes", "sha256"})
            self.assertEqual(binding["bytes"], path.stat().st_size)
            self.assertEqual(binding["sha256"], sha256_bytes(path.read_bytes()))
        self.assertFalse(manifest["protected_packet_bodies_in_export_set"])
        self.assertFalse(manifest["prompt_or_completion_bodies_in_export_set"])
        self.assertFalse(manifest["token_ids_in_export_set"])
        self.assertFalse(manifest["live_outputs_in_export_set"])
        self.assertEqual(manifest["production_admissibility"], "CANNOT_CHECK")
        checksum_lines = SHA256SUMS_PATH.read_text().splitlines()
        checksums = {
            name: digest
            for digest, name in (line.split("  ", 1) for line in checksum_lines)
        }
        self.assertEqual(set(checksums), expected | {BODY_FREE_MANIFEST_PATH.name})
        for name, digest in checksums.items():
            self.assertEqual(digest, sha256_bytes((ROOT / name).read_bytes()))

    def test_42_synthetic_receipt_binds_core_artifacts_and_nonclaims(self) -> None:
        receipt = read_json(SYNTHETIC_RECEIPT_PATH)
        self.assertEqual(receipt["status"], "PASS_SYNTHETIC_HOSTILE_VALIDATION")
        self.assertEqual(receipt["tests_run"], 44)
        self.assertEqual(receipt["tests_passed"], 44)
        self.assertEqual(receipt["tests_failed"], 0)
        expected_core = {
            "FINALIZER_CONTRACT_V1.json", "FINALIZER_OUTPUT_SCHEMA_V1.json",
            "protected_rr1_one_tuple_finalizer_v1.py",
            "validate_protected_rr1_one_tuple_finalizer_v1.py",
        }
        self.assertEqual(set(receipt["artifact_sha256"]), expected_core)
        for name, digest in receipt["artifact_sha256"].items():
            self.assertEqual(digest, sha256_bytes((ROOT / name).read_bytes()))
        self.assertEqual(receipt["live_scheduler_commands_executed"], 0)
        self.assertFalse(receipt["job_submitted"])
        self.assertFalse(receipt["generation_invoked"])
        self.assertFalse(receipt["official_evaluator_invoked"])
        self.assertEqual(receipt["official_outcomes_opened"], 0)
        self.assertEqual(receipt["protected_packet_bodies_opened"], 0)
        self.assertEqual(receipt["runner_v2_population_ledger_status"], "NOT_FINALIZED_918_TUPLES")
        self.assertEqual(receipt["production_admissibility"], "CANNOT_CHECK")
        self.assertEqual(receipt["scientific_authority_delta"], "NONE")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProtectedRR1OneTupleFinalizerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_PROTECTED_RR1_ONE_TUPLE_FINALIZER_V1_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} protected_bodies=0 generation=0 jobs=0 outcomes=0 "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
