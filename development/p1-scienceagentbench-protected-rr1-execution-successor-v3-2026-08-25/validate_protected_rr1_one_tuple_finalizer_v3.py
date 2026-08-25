#!/usr/bin/env python3
"""Synthetic hostile validation for the protected RR1 one-tuple finalizer.

All fixtures are invented metadata.  The suite never submits a job, invokes a
model/evaluator/API, or reads protected packet, prompt, completion, token-ID, or
official-outcome bodies.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Mapping
from unittest import mock


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
MODULE_PATH = ROOT / "protected_rr1_one_tuple_finalizer_v3.py"
CONTRACT_PATH = ROOT / "FINALIZER_CONTRACT_V3.json"
SCHEMA_PATH = ROOT / "FINALIZER_OUTPUT_SCHEMA_V3.json"
SYNTHETIC_RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"
BODY_FREE_MANIFEST_PATH = ROOT / "BODY_FREE_EXPORT_MANIFEST_V1.json"
SHA256SUMS_PATH = ROOT / "SHA256SUMS"
TRAMPOLINE_PATH = ROOT / "run_protected_rr1_direct_execution_trampoline_v3.sh"
FROZEN_NORMALIZED_TRAMPOLINE_SHA256 = (
    "a04b00ec70f346bf770438d039b94c10cdba38fa158b2af2c209942072f9b82d"
)
FAILURE_CERTIFICATE_PATH = ROOT / "FAILED_JOB_3537828_NO_GENERATION_CERTIFICATE_V1.json"
FROZEN_SUCCESSOR_ROOT = Path(
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "repo-exec-successor-v3-20260825"
)
FROZEN_DONOR_ROOT = Path(
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "repo-51f13ba9/development/"
    "p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24"
)
FROZEN_RUN_ROOT = Path(
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "live-rr1-exec-successor-v3-20260825"
)
FROZEN_SBATCH_STDOUT_PATH = FROZEN_RUN_ROOT / "logs/SBATCH_STDOUT_V1.txt"
FROZEN_SBATCH_STDERR_PATH = FROZEN_RUN_ROOT / "logs/SBATCH_STDERR_V1.txt"
FROZEN_PARSE_STDOUT_PATH = FROZEN_RUN_ROOT / "logs/PARSE_SBATCH_JOB_ID_STDOUT_V1.txt"
FROZEN_PARSE_STDERR_PATH = FROZEN_RUN_ROOT / "logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt"
FROZEN_BASH_PATH = Path("/usr/bin/bash")
FROZEN_BASH_SHA256 = "ec6d007d48ef11bc47ad3f372b4b20ff2f0d4e63867e7e4cc0f1b17b19fa88b2"
FROZEN_SHA256SUM_PATH = Path("/usr/bin/sha256sum")
FROZEN_SHA256SUM_SHA256 = "1950eda10a1bb0c6c2a086ba009b847edec6f30d25eb311b9154ae08819041a9"
FROZEN_READLINK_PATH = Path("/usr/bin/readlink")
FROZEN_READLINK_SHA256 = "99dbafcdcba4adb285ea164c3a3bf27539719328a8ae5df9be6d84cdde1146dc"
FROZEN_CMP_PATH = Path("/usr/bin/cmp")
FROZEN_CMP_SHA256 = "16d8b82bf5ee1774585ce5c63691cb156aa350c48f0d0689b27d13aa4b0a62eb"
FROZEN_STAT_PATH = Path("/usr/bin/stat")
FROZEN_STAT_SHA256 = "f7ef3b1376596ce952779ea53a91ec97ce8b57389a3ffde75a499564b1c8f25f"
FROZEN_WC_PATH = Path("/usr/bin/wc")
FROZEN_WC_SHA256 = "9cfb241d8d95fe3805a6d9af22b5dfac4f8aa0ce2d2b966db8b45a71baf501c9"
FROZEN_PYTHON_PATH_ENTRY = Path(
    "/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin"
)
FROZEN_PYTHON_COMMAND = FROZEN_PYTHON_PATH_ENTRY / "python3"
FROZEN_PYTHON_REAL_TARGET = Path(
    "/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3.11"
)
FROZEN_PYTHON_SHA256 = "34f2f9f9561850d15d8060a2565c3a81046425faaba575687d3b75e1212d0f77"
FROZEN_RUNTIME_PATH = f"{FROZEN_PYTHON_PATH_ENTRY}:/usr/bin:/bin"
FROZEN_PYTHON_LIBRARY_LOGICAL_DIR = Path(
    "/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib"
)
FROZEN_PYTHON_LIBRARY_CANONICAL_DIR = Path(
    "/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib"
)
FROZEN_LIBPYTHON_LOGICAL_PATH = (
    FROZEN_PYTHON_LIBRARY_LOGICAL_DIR / "libpython3.11.so.1.0"
)
FROZEN_LIBPYTHON_CANONICAL_PATH = (
    FROZEN_PYTHON_LIBRARY_CANONICAL_DIR / "libpython3.11.so.1.0"
)
FROZEN_LIBPYTHON_SHA256 = "398cbf957b8584d4e06ce374b888555149d517ea1037f7ca44d62f855a5b83c5"
FROZEN_LIBPYTHON_SIZE = 22160208
FROZEN_LIBPYTHON_MODE = 0o755
FROZEN_LIBPYTHON_UID = 1400
FROZEN_LIBPYTHON_GID = 1400
FROZEN_PYTHON_LIBRARY_DIR_MODE = 0o755
FROZEN_PYTHON_LIBRARY_DIR_UID = 1400
FROZEN_PYTHON_LIBRARY_DIR_GID = 1400
FROZEN_PYTHON_LIBRARY_DIR_NLINK = 4
FROZEN_LIBPYTHON_ABI_PATH = FROZEN_PYTHON_LIBRARY_LOGICAL_DIR / "libpython3.so"
FROZEN_LIBPYTHON_ABI_SHA256 = (
    "9ce9dfd0670cd9e05cdee0478b0a82425b1fd45abe7bdef807a4e7ba2a331f93"
)
FROZEN_LIBPYTHON_ABI_SIZE = 15352
FROZEN_LIBPYTHON_ABI_MODE = 0o755
FROZEN_LIBPYTHON_ABI_UID = 1400
FROZEN_LIBPYTHON_ABI_GID = 1400
FROZEN_LIBPYTHON_ABI_NLINK = 1
FROZEN_EFFECTIVE_SERVER_LD_LIBRARY_PATH = (
    "/sw/pkg/ollama/0.32.14/lib/ollama:"
    "/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13:"
    f"{FROZEN_PYTHON_LIBRARY_LOGICAL_DIR}"
)
FROZEN_DIRECT_EXECUTION_ARGV = (
    "--masked-packet",
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "private-inputs/MASKED_PACKET.json",
    "--recovered-packet",
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "private-inputs/RECOVERED_PACKET.json",
    "--model",
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_exact_model_v1_20260824/model/"
    "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    "--llama-server",
    "/sw/pkg/ollama/0.32.14/lib/ollama/llama-server",
    "--cuda-backend",
    "/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so",
    "--output-root",
    str(FROZEN_RUN_ROOT / "runtime-parent/evidence"),
)
PREDECESSOR_DIRECT_ROOT = (
    REPO_ROOT
    / "development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24"
)
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
LIVE_CONFIG_HEADER = b"Configuration data as of 2026-08-24T22:23:08\n"
LIVE_NODE_LINE = (
    b"NodeName=cg14 Arch=x86_64 CoresPerSocket=16  CPUAlloc=0 CPUEfctv=32 "
    b"CPUTot=32 CPULoad=10.64 AvailableFeatures=icelake,mem512GB,rack_f1,gpua40 "
    b"ActiveFeatures=icelake,mem512GB,rack_f1,gpua40 Gres=gpu:a40:1 "
    b"GresDrain=N/A GresUsed=gpu:a40:0(IDX:N/A) NodeAddr=cg14 "
    b"NodeHostName=cg14 Version=23.11.3 OS=Linux 5.14.0-687.24.1.el9_8.x86_64 "
    b"#1 SMP PREEMPT_DYNAMIC Thu Jul 9 16:32:56 UTC 2026  RealMemory=512000 "
    b"AllocMem=0 FreeMem=465242 Sockets=2 Boards=1 State=IDLE ThreadsPerCore=1 "
    b"TmpDisk=0 Weight=10 Owner=N/A MCS_label=N/A Partitions=gpua40i,hpua40i  "
    b"BootTime=2026-07-13T10:15:51 SlurmdStartTime=2026-07-20T12:39:41 "
    b"LastBusyTime=2026-08-24T20:18:53 ResumeAfterTime=None "
    b"CfgTRES=cpu=32,mem=500G,billing=32,gres/gpu=1,gres/gpu:a40=1 "
    b"AllocTRES= CapWatts=n/a CurrentWatts=0 AveWatts=0 ExtSensorsJoules=n/a "
    b"ExtSensorsWatts=0 ExtSensorsTemp=n/a\n"
)


def normalized_trampoline_sha256(payload: bytes) -> str:
    pattern = re.compile(
        rb"(?m)^NORMALIZED_TRAMPOLINE_SHA256='([0-9a-f]{64})'$"
    )
    normalized, count = pattern.subn(
        b"NORMALIZED_TRAMPOLINE_SHA256='" + (b"0" * 64) + b"'", payload
    )
    if count != 1:
        raise AssertionError(
            f"trampoline normalized self-binding assignment count is {count}, not 1"
        )
    return sha256_bytes(normalized)

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
    n_tasks: str = "",
    req_mem: str = "64G",
    partition: str = PARTITION,
    overrides: Mapping[str, str] | None = None,
) -> bytes:
    values = {
        "JobIDRaw": job_id,
        "Partition": partition,
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
        "NTasks": n_tasks,
        "ReqCPUS": "8",
        "ReqMem": req_mem,
        "ReqTRES": "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1",
        "AllocTRES": alloc_tres,
        "Account": ACCOUNT,
        "QOS": "normal",
        "Constraints": "",
        "Reservation": "",
        "Reason": "None",
    }
    if overrides:
        unknown = set(overrides) - set(SACCT_FIELDS)
        if unknown:
            raise AssertionError(f"unknown synthetic sacct fields: {sorted(unknown)}")
        values.update(overrides)
    return ("|".join(values[field] for field in SACCT_FIELDS) + "\n").encode()


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


CAPTURE_INPUTS = (
    "POST_JOB_SACCT_V1.txt",
    "POST_JOB_SACCT_NONOVERLAP_V1.txt",
    "POST_JOB_SCONTROL_V1.txt",
    "SCHEDULER_CONFIG_V1.txt",
    "SCHEDULER_PARTITION_V1.txt",
    "SCHEDULER_NODE_V1.txt",
    "SCHEDULER_CAPTURE_PROVENANCE_V1.json",
)
ROOT_INPUTS = (
    *CAPTURE_INPUTS[:6],
    "GPU_ALLOCATION_IDENTITY_V1.json",
    "SERVER_CLEANUP_V1.json",
    "STAGED_RUNTIME_INPUT_V1.json",
    "PROCESS_ATTESTATION_V1.json",
    CAPTURE_INPUTS[6],
)
ATTEMPT_INPUTS = (
    "SCONTROL_IN_JOB_V1.txt",
    "SLURM_IDENTITY_AND_SNAPSHOT_V1.json",
    "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json",
    "DIRECT_ROUTE_BRIDGE_BINDING_V1.json",
    "ATTEMPT_CAPTURE_V1.json",
)


class SyntheticFixture:
    def split_capture(self, root: Path, capture_root: Path) -> None:
        capture_root.mkdir(mode=0o700)
        for name in CAPTURE_INPUTS:
            source = root / name
            target = capture_root / name
            source_info = source.lstat()
            if stat.S_ISLNK(source_info.st_mode):
                target.symlink_to(os.readlink(source))
                continue
            target.write_bytes(source.read_bytes())
            source_mode = stat.S_IMODE(source_info.st_mode)
            target.chmod(
                0o400
                if source_mode in {0o400, 0o600} and source_info.st_nlink == 1
                else source_mode
            )
            if source_info.st_nlink != 1:
                os.link(target, capture_root / f".{name}.synthetic-hardlink")

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
            LIVE_CONFIG_HEADER
            +
            b"SLURM_VERSION = 23.11.3\n"
            b"ClusterName = cosmos\n"
            b"MinJobAge = 300 sec\n"
            b"SelectType = select/cons_tres\n"
            b"SelectTypeParameters = CR_Core_Memory\n"
            b"GresTypes = gpu\n"
            b"TaskPlugin = task/cgroup,task/affinity\n"
            b"ProctrackType = proctrack/cgroup\n"
            b"AccountingStorageType = accounting_storage/slurmdbd\n"
            b"AccountingStorageEnforce = associations,limits,qos,safe\n"
            b"AccountingStorageTRES = gres/gpu\n"
            b"JobAcctGatherType = jobacct_gather/cgroup\n"
            b"PrivateData = none\n"
        )
        write_private(root / "SCHEDULER_PARTITION_V1.txt",
            f"PartitionName={PARTITION} AllowAccounts=ALL Nodes=aurora[01-04] OverSubscribe=NO State=UP\n".encode()
        )
        write_private(root / "SCHEDULER_NODE_V1.txt",
            b"NodeName=aurora01 Arch=x86_64 CoresPerSocket=16  CPUAlloc=8 "
            b"State=ALLOCATED Gres=gpu:a40:4(S:0-1) Version=23.11.3 "
            b"OS=Linux 5.14.0-687.24.1.el9_8.x86_64 #1 SMP PREEMPT_DYNAMIC "
            b"Thu Jul 9 16:32:56 UTC 2026  RealMemory=512000 "
            b"CfgTRES=cpu=64,mem=500G,billing=64,gres/gpu=4,gres/gpu:a40=4 "
            b"AllocTRES=cpu=8,mem=64G,gres/gpu=1,gres/gpu:a40=1\n"
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
                    "phase_id": "RR_PHASE1", "rendered_prompt_sha256": "2" * 64,
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
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-scheduler-capture-provenance.v3",
            "authority": "EXACT_SCHEDULER_CAPTURE_COMMAND_AND_RAW_BYTE_BINDING_ONLY",
            "status": "PASS_EXACT_POST_JOB_SCHEDULER_CAPTURE",
            "slurm_job_id": JOB_ID,
            "partition": PARTITION,
            "node_name": NODE,
            "allocation_started_at": START,
            "allocation_ended_at": END,
            "capture_argv": materialized_argv(),
            "capture_command_timeout_seconds": 20,
            "post_terminal_capture_deadline_seconds": 240,
            "post_job_scontrol_start_latency_limit_seconds": 2,
            "terminal_observed_at_utc": "2026-08-24T22:23:08.000000Z",
            "terminal_observed_monotonic_ns": "2000000000",
            "post_job_scontrol_started_at_utc": "2026-08-24T22:23:09.000000Z",
            "post_job_scontrol_start_seconds_after_terminal_observation": "1.000000000",
            "post_job_scontrol_completed_at_utc": "2026-08-24T22:23:10.000000Z",
            "post_job_scontrol_seconds_after_terminal_observation": "2.000000000",
            "capture_command_observations": [
                {
                    "key": key,
                    "argv": materialized_argv()[key],
                    "started_at_monotonic_ns": str(started),
                    "started_at_utc": f"2026-08-24T22:23:{started_second:02d}.000000Z",
                    "completed_at_monotonic_ns": str(completed),
                    "completed_at_utc": f"2026-08-24T22:23:{completed_second:02d}.000000Z",
                    "duration_seconds": "1.000000000",
                    "seconds_after_terminal_observation": f"{elapsed}.000000000",
                    "post_terminal_deadline_remaining_seconds": f"{240 - elapsed}.000000000",
                    "completed_before_post_terminal_deadline": True,
                }
                for key, started, completed, started_second, completed_second, elapsed in (
                    ("post_job_scontrol", 3_000_000_000, 4_000_000_000, 9, 10, 2),
                    ("scheduler_config", 5_000_000_000, 6_000_000_000, 11, 12, 4),
                    ("scheduler_partition", 7_000_000_000, 8_000_000_000, 13, 14, 6),
                    ("scheduler_node", 9_000_000_000, 10_000_000_000, 15, 16, 8),
                    ("nonoverlap_sacct", 11_000_000_000, 12_000_000_000, 17, 18, 10),
                )
            ],
            "terminal_poll_interval_seconds": 5,
            "terminal_poll_limit": 1440,
            "terminal_poll_count": 1,
            "terminal_poll_observations": [{
                "poll_index": 1,
                "observed_at_monotonic_ns": "1000000000",
                "argv": materialized_argv()["terminal_sacct"],
                "row_count": 1,
                "raw_sha256": sha256_bytes(sacct_row()),
                "state": "COMPLETED",
                "partition": PARTITION,
                "classification": "TERMINAL_COMPLETE_gpua40i",
                "terminal": True,
            }],
            "partition_source": "INTERNAL_FROZEN_gpua40i",
            "node_source": "DERIVED_FROM_UNIQUE_TERMINAL_SACCT_NODELIST",
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
            "schema_version": "orion.p1.scienceagentbench.protected-rr1-one-tuple-scheduler-export.v3",
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
    spec = importlib.util.spec_from_file_location("protected_rr1_one_tuple_finalizer_v3", MODULE_PATH)
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

    def run_fixture(
        self, mutate: Any = None, *, refresh: bool = True,
        capture_mutate: Any = None,
    ) -> tuple[int, dict[str, Any], Path]:
        module = self.require_module()
        holder = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(holder.cleanup)
        base = Path(holder.name)
        evidence = base / "evidence"
        capture_root = base / "capture"
        output = base / "finalized"
        evidence.mkdir()
        self.fixture.create(evidence)
        if mutate is not None:
            mutate(evidence)
            if refresh:
                self.fixture.refresh_capture_provenance(evidence)
                self.fixture.refresh_export(evidence)
        self.fixture.split_capture(evidence, capture_root)
        if capture_mutate is not None:
            capture_mutate(capture_root)
        code, receipt = module.finalize(
            evidence.resolve(), capture_root.resolve(), output.resolve()
        )
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
        module = self.require_module()
        contract = read_json(CONTRACT_PATH)
        self.assertEqual(module.FROZEN_SBATCH_STDOUT_PATH, FROZEN_SBATCH_STDOUT_PATH)
        self.assertEqual(
            contract["schema_version"],
            "orion.p1.scienceagentbench.protected-rr1-direct-execution-successor-finalizer-contract.v3",
        )
        self.assertEqual(contract["base_commit"], "bbc73f0860b1b76a2c4fe4449f7a30d0866cb247")
        self.assertEqual(contract["scheduler_audit_binding"]["slurm_version"], "23.11.3")
        self.assertEqual(contract["scheduler_audit_binding"]["min_job_age_seconds"], 300)
        self.assertEqual(contract["capture_execution"]["terminal_poll_interval_seconds"], 5)
        self.assertEqual(contract["capture_execution"]["terminal_poll_limit"], 1440)
        self.assertEqual(
            contract["capture_execution"]["post_terminal_timing"],
            {
                "capture_sequence_deadline_seconds": 240,
                "command_timeout_seconds": 20,
                "first_command": "scontrol show job -dd <SLURM_JOB_ID>",
                "first_command_max_start_latency_seconds": 2,
                "monotonic_arithmetic": "EXACT_INTEGER_NANOSECOND_START_COMPLETION_DURATION_ELAPSED_AND_REMAINING_DEADLINE",
                "terminal_persistence_order": "FIRST_COMMAND_SUBPROCESS_LAUNCHED_BEFORE_TERMINAL_SACCT_O_EXCL_FSYNC",
                "terminal_raw_retained_on_any_subsequent_failure": True,
                "utc_grammar": "YYYY-MM-DDTHH:MM:SS.ffffffZ_NONDECREASING",
            },
        )
        self.assertEqual(
            contract["scheduler_audit_binding"][
                "post_terminal_deadline_margin_before_min_job_age_seconds"
            ],
            60,
        )
        self.assertTrue(
            contract["filesystem_custody"][
                "evidence_capture_descriptor_identity_distinct_required"
            ]
        )
        self.assertTrue(
            contract["filesystem_custody"][
                "finalize_three_path_values_distinct_required"
            ]
        )
        self.assertFalse(
            contract["operator_assembly"]["manual_scheduler_export_authorship_required"]
        )
        frozen_module_path = (
            FROZEN_SUCCESSOR_ROOT / ROOT.relative_to(REPO_ROOT) / MODULE_PATH.name
        )
        python_entrypoint_prefix = [
            str(FROZEN_PYTHON_COMMAND), "-I", "-S", str(frozen_module_path)
        ]
        self.assertEqual(
            contract["entrypoint_argv"],
            [
                [
                    *python_entrypoint_prefix,
                    "parse-sbatch-job-id",
                    "--input-path",
                    str(FROZEN_SBATCH_STDOUT_PATH),
                ],
                [
                    *python_entrypoint_prefix,
                    "watch-capture",
                    "--job-id",
                    "<SLURM_JOB_ID>",
                    "--output-root",
                    str(FROZEN_RUN_ROOT / "capture-parent/capture"),
                ],
                [
                    *python_entrypoint_prefix,
                    "finalize",
                    "--evidence-root",
                    str(FROZEN_RUN_ROOT / "runtime-parent/evidence"),
                    "--capture-root",
                    str(FROZEN_RUN_ROOT / "capture-parent/capture"),
                    "--output-root",
                    str(FROZEN_RUN_ROOT / "final-parent/result"),
                ],
            ],
        )
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
        self.assertFalse(contract["submission_authority"])
        self.assertEqual(contract["status"], "FROZEN_REPAIRED_NOT_RESUBMITTED")

        repair = contract["direct_execution_repair"]
        successor_trampoline = FROZEN_SUCCESSOR_ROOT / ROOT.relative_to(REPO_ROOT) / TRAMPOLINE_PATH.name
        self.assertEqual(repair["submission_cwd"], str(FROZEN_SUCCESSOR_ROOT))
        self.assertEqual(repair["runtime_cwd"], str(FROZEN_SUCCESSOR_ROOT))
        self.assertEqual(repair["slurm_submit_dir"], str(FROZEN_SUCCESSOR_ROOT))
        self.assertEqual(repair["submitted_file"], str(successor_trampoline))
        self.assertEqual(repair["canonical_trampoline_sha256"], sha256_bytes(TRAMPOLINE_PATH.read_bytes()))
        self.assertEqual(
            repair["normalized_trampoline_sha256"],
            FROZEN_NORMALIZED_TRAMPOLINE_SHA256,
        )
        self.assertEqual(
            normalized_trampoline_sha256(TRAMPOLINE_PATH.read_bytes()),
            FROZEN_NORMALIZED_TRAMPOLINE_SHA256,
        )
        self.assertEqual(
            repair["spooled_source_binding"],
            "RAW_BYTES_AND_SHA256_EQUAL_CANONICAL_TRAMPOLINE_PLUS_NORMALIZED_SHA256_EQUAL_EXACT_FREEZE",
        )
        self.assertEqual(repair["direct_route_argv"], list(FROZEN_DIRECT_EXECUTION_ARGV))
        expected_directives = [
            line for line in (PREDECESSOR_DIRECT_ROOT / "run_protected_rr1_direct_route_v1.sh").read_text().splitlines()
            if line.startswith("#SBATCH ")
        ]
        self.assertEqual(repair["sbatch_directives"], expected_directives)
        self.assertEqual(
            repair["sbatch_argv"],
            [
                "sbatch",
                "--parsable",
                "--export=NIL",
                f"--output={FROZEN_RUN_ROOT}/logs/slurm-%j.out",
                f"--error={FROZEN_RUN_ROOT}/logs/slurm-%j.err",
                str(successor_trampoline),
                *FROZEN_DIRECT_EXECUTION_ARGV,
            ],
        )
        self.assertEqual(
            repair["sbatch_stdout_job_id"],
            {
                "accepted_raw_grammar": "CANONICAL_POSITIVE_DECIMAL_BYTES_WITH_EXACTLY_ONE_FINAL_LF",
                "bridge_argv": [
                    *contract["entrypoint_argv"][0],
                ],
                "input_file_mode": "0600_EXACT",
                "input_file_nlink": 1,
                "input_file_owner": "CURRENT_EFFECTIVE_UID",
                "input_path": str(FROZEN_SBATCH_STDOUT_PATH),
                "missing_final_lf_allowed": False,
                "semicolon_cluster_suffix_allowed": False,
                "whitespace_or_extra_lines_allowed": False,
                "watch_capture_start": "IMMEDIATE_WITH_EXACT_PARSED_JOB_ID",
            },
        )
        self.assertEqual(
            repair["runtime_toolchain"],
            {
                "bash": {"path": str(FROZEN_BASH_PATH), "sha256": FROZEN_BASH_SHA256},
                "sha256sum": {
                    "path": str(FROZEN_SHA256SUM_PATH),
                    "sha256": FROZEN_SHA256SUM_SHA256,
                },
                "readlink": {
                    "path": str(FROZEN_READLINK_PATH),
                    "sha256": FROZEN_READLINK_SHA256,
                },
                "cmp": {
                    "path": str(FROZEN_CMP_PATH),
                    "sha256": FROZEN_CMP_SHA256,
                },
                "stat": {
                    "path": str(FROZEN_STAT_PATH),
                    "sha256": FROZEN_STAT_SHA256,
                },
                "wc": {
                    "path": str(FROZEN_WC_PATH),
                    "sha256": FROZEN_WC_SHA256,
                },
                "python_path_entry": str(FROZEN_PYTHON_PATH_ENTRY),
                "python_command_path": str(FROZEN_PYTHON_COMMAND),
                "python_real_target": str(FROZEN_PYTHON_REAL_TARGET),
                "python_real_target_sha256": FROZEN_PYTHON_SHA256,
                "python_library_path": str(FROZEN_PYTHON_LIBRARY_LOGICAL_DIR),
                "runtime_path": FROZEN_RUNTIME_PATH,
            },
        )
        loader = repair["loader_repair"]
        self.assertEqual(
            loader["environment_assignment"],
            {"LD_LIBRARY_PATH": str(FROZEN_PYTHON_LIBRARY_LOGICAL_DIR)},
        )
        self.assertEqual(loader["elf_needed_soname"], "libpython3.11.so.1.0")
        self.assertEqual(
            loader["search_directory"],
            {
                "logical_path": str(FROZEN_PYTHON_LIBRARY_LOGICAL_DIR),
                "canonical_path": str(FROZEN_PYTHON_LIBRARY_CANONICAL_DIR),
                "mode": "0755",
                "uid": FROZEN_PYTHON_LIBRARY_DIR_UID,
                "gid": FROZEN_PYTHON_LIBRARY_DIR_GID,
                "nlink": FROZEN_PYTHON_LIBRARY_DIR_NLINK,
                "top_level_entry_count": 5,
                "top_level_entries": {
                    "libpython3.11.so": {
                        "type": "SYMLINK",
                        "target": "libpython3.11.so.1.0",
                    },
                    "libpython3.11.so.1.0": {"type": "REGULAR_NON_SYMLINK"},
                    "libpython3.so": {"type": "REGULAR_NON_SYMLINK"},
                    "pkgconfig": {
                        "type": "DIRECTORY_NON_SYMLINK",
                        "mode": "0755",
                        "uid": FROZEN_PYTHON_LIBRARY_DIR_UID,
                        "gid": FROZEN_PYTHON_LIBRARY_DIR_GID,
                    },
                    "python3.11": {
                        "type": "DIRECTORY_NON_SYMLINK",
                        "mode": "0755",
                        "uid": FROZEN_PYTHON_LIBRARY_DIR_UID,
                        "gid": FROZEN_PYTHON_LIBRARY_DIR_GID,
                    },
                },
            },
        )
        self.assertEqual(loader["library"], {
            "logical_path": str(FROZEN_LIBPYTHON_LOGICAL_PATH),
            "canonical_path": str(FROZEN_LIBPYTHON_CANONICAL_PATH),
            "size_bytes": FROZEN_LIBPYTHON_SIZE,
            "mode": "0755",
            "uid": FROZEN_LIBPYTHON_UID,
            "gid": FROZEN_LIBPYTHON_GID,
            "nlink": 1,
            "sha256": FROZEN_LIBPYTHON_SHA256,
            "leaf_type": "REGULAR_NON_SYMLINK",
        })
        self.assertEqual(
            loader["abi_library"],
            {
                "logical_path": str(FROZEN_LIBPYTHON_ABI_PATH),
                "size_bytes": FROZEN_LIBPYTHON_ABI_SIZE,
                "mode": "0755",
                "uid": FROZEN_LIBPYTHON_ABI_UID,
                "gid": FROZEN_LIBPYTHON_ABI_GID,
                "nlink": FROZEN_LIBPYTHON_ABI_NLINK,
                "sha256": FROZEN_LIBPYTHON_ABI_SHA256,
                "leaf_type": "REGULAR_NON_SYMLINK",
            },
        )
        self.assertEqual(
            loader["python_runtime_probe"],
            {
                "argv": [
                    str(FROZEN_PYTHON_COMMAND),
                    "-B",
                    "-I",
                    "-S",
                    "-c",
                    "import ctypes,tarfile,zlib",
                ],
                "body_access": False,
                "generation": False,
                "network": False,
                "output_capture": "STDOUT_AND_STDERR_MERGED_BEFORE_HASH_BOUND_WC_C",
                "required_combined_output_bytes": 0,
                "required_exit_code": 0,
            },
        )
        self.assertEqual(
            loader["effective_server_ld_library_path"],
            FROZEN_EFFECTIVE_SERVER_LD_LIBRARY_PATH,
        )
        self.assertEqual(loader["cuda_visible_devices_source"], "SLURM_INJECTED_UNCHANGED")
        self.assertEqual(repair["trampoline_entry_environment"], {
            "ld_library_path_on_entry": "ABSENT_INCLUDING_DEFINED_EMPTY",
            "ld_preload_on_entry": "ABSENT_INCLUDING_DEFINED_EMPTY",
            "source": "SBATCH_EXPORT_NIL_ONLY_SLURM_AND_SPANK_VARIABLES",
        })
        direct_module_path = PREDECESSOR_DIRECT_ROOT / "protected_rr1_direct_route_v1.py"
        direct_spec = importlib.util.spec_from_file_location(
            "protected_rr1_direct_route_v1_server_environment_test",
            direct_module_path,
        )
        self.assertIsNotNone(direct_spec)
        self.assertIsNotNone(direct_spec.loader if direct_spec is not None else None)
        if direct_spec is None or direct_spec.loader is None:
            self.fail("exact direct-route module loader is unavailable")
        direct_module = importlib.util.module_from_spec(direct_spec)
        direct_spec.loader.exec_module(direct_module)
        backend = Path(
            "/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so"
        )
        server_env = direct_module.build_credential_free_server_environment(
            backend,
            {
                "PATH": FROZEN_RUNTIME_PATH,
                "LD_LIBRARY_PATH": str(FROZEN_PYTHON_LIBRARY_LOGICAL_DIR),
                "CUDA_VISIBLE_DEVICES": "0",
                "SYNTHETIC_CREDENTIAL_TRAP": "must-not-survive",
            },
        )
        self.assertEqual(
            server_env["LD_LIBRARY_PATH"], FROZEN_EFFECTIVE_SERVER_LD_LIBRARY_PATH
        )
        self.assertEqual(server_env["CUDA_VISIBLE_DEVICES"], "0")
        self.assertNotIn("SYNTHETIC_CREDENTIAL_TRAP", server_env)
        self.assertEqual(
            repair["submission_capture"],
            {
                "environment_unset_before_submission": [
                    "BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP",
                    "LD_PRELOAD",
                ],
                "operator_python_ld_library_path": str(FROZEN_PYTHON_LIBRARY_LOGICAL_DIR),
                "sbatch_export": "NIL",
                "shell_options": ["errexit", "nounset", "pipefail", "noclobber"],
                "umask": "077",
                "stdout_path": str(FROZEN_SBATCH_STDOUT_PATH),
                "stderr_path": str(FROZEN_SBATCH_STDERR_PATH),
                "parse_stdout_path": str(FROZEN_PARSE_STDOUT_PATH),
                "parse_stderr_path": str(FROZEN_PARSE_STDERR_PATH),
                "stdout_mode": "0600_EXACT",
                "stderr_mode": "0600_EXACT",
                "parse_stdout_mode": "0600_EXACT",
                "parse_stderr_mode": "0600_EXACT",
                "sbatch_exit_zero_required_before_parse": True,
                "sbatch_stderr_required_empty": True,
                "parse_exit_zero_required_before_read": True,
                "parse_stderr_required_empty": True,
                "parse_stdout_exact_grammar": "CANONICAL_POSITIVE_DECIMAL_BYTES_WITH_EXACTLY_ONE_FINAL_LF",
                "bridge_file_mode_check_argv_template": [
                    "/usr/bin/stat", "-c", "%a", "--", "<PATH>",
                ],
            },
        )
        sequence = repair["operator_sequence"]
        self.assertEqual([step["step"] for step in sequence], [
            "CREATE_PRIVATE_LOG_FILES_AND_SUBMIT",
            "REQUIRE_EMPTY_SBATCH_STDERR",
            "PARSE_EXACT_SBATCH_STDOUT_TO_PRIVATE_FILES",
            "REQUIRE_EMPTY_PARSE_STDERR_AND_READ_EXACT_JOB_ID",
            "WATCH_CAPTURE_IMMEDIATELY",
            "FINALIZE_AFTER_JOB_AND_CAPTURE_SUCCESS",
        ])
        self.assertEqual(sequence[0]["stdout_path"], str(FROZEN_SBATCH_STDOUT_PATH))
        self.assertEqual(sequence[0]["stderr_path"], str(FROZEN_SBATCH_STDERR_PATH))
        self.assertEqual(sequence[0]["argv"], repair["sbatch_argv"])
        self.assertEqual(sequence[1]["required_empty_path"], str(FROZEN_SBATCH_STDERR_PATH))
        self.assertTrue(sequence[1]["required_regular_non_symlink"])
        self.assertEqual(sequence[1]["required_mode"], "0600")
        self.assertEqual(sequence[2]["argv"], contract["entrypoint_argv"][0])
        self.assertEqual(sequence[2]["stdout_path"], str(FROZEN_PARSE_STDOUT_PATH))
        self.assertEqual(sequence[2]["stderr_path"], str(FROZEN_PARSE_STDERR_PATH))
        self.assertEqual(sequence[3]["required_empty_path"], str(FROZEN_PARSE_STDERR_PATH))
        self.assertTrue(sequence[3]["required_regular_non_symlink"])
        self.assertEqual(sequence[3]["required_mode"], "0600")
        self.assertEqual(sequence[3]["stdout_input_path"], str(FROZEN_PARSE_STDOUT_PATH))
        self.assertEqual(sequence[3]["shell_assignment"], "JOBID")
        self.assertEqual(sequence[4]["argv"], contract["entrypoint_argv"][1])
        self.assertEqual(sequence[5]["argv"], contract["entrypoint_argv"][2])
        shell_sequence = repair["operator_sequence_shell"]
        self.assertIn(
            "unset BASH_ENV ENV PYTHONPATH PYTHONHOME PYTHONSTARTUP",
            shell_sequence,
        )
        self.assertIn("unset LD_PRELOAD", shell_sequence)
        self.assertIn(
            f"export LD_LIBRARY_PATH={FROZEN_PYTHON_LIBRARY_LOGICAL_DIR}",
            shell_sequence,
        )
        self.assertTrue(any("sbatch --parsable --export=NIL" in line for line in shell_sequence))
        self.assertTrue(any("python3 -I -S" in line for line in shell_sequence))
        self.assertTrue(any("PARSE_SBATCH_JOB_ID_STDOUT_V1.txt" in line for line in shell_sequence))
        self.assertTrue(any("PARSE_SBATCH_JOB_ID_STDERR_V1.txt" in line for line in shell_sequence))
        self.assertFalse(any("RAW=$(sbatch" in line for line in shell_sequence))
        python_shell_lines = [
            line for line in shell_sequence
            if line.startswith(str(FROZEN_PYTHON_COMMAND) + " ")
        ]
        self.assertEqual(len(python_shell_lines), 3)
        self.assertTrue(all(" -I -S " in line for line in python_shell_lines))
        stderr_mode_lines = [
            line for line in shell_sequence
            if "/usr/bin/stat -c %a --" in line
        ]
        self.assertEqual(len(stderr_mode_lines), 2)
        self.assertTrue(any(str(FROZEN_SBATCH_STDERR_PATH) in line for line in stderr_mode_lines))
        self.assertTrue(any(str(FROZEN_PARSE_STDERR_PATH) in line for line in stderr_mode_lines))
        self.assertEqual(
            contract["operator_success_gates"],
            {
                "job_terminal": "P1_SAB_PROTECTED_RR1_ONE_TUPLE_CAPTURED__SCHEDULER_FINALIZATION_PENDING",
                "watcher_terminal": "P1_SAB_PROTECTED_RR1_POST_JOB_SCHEDULER_CAPTURE_PASS",
                "finalizer_terminal": "P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS",
                "watcher_starts": "IMMEDIATELY_AFTER_VALIDATED_SBATCH_PARSABLE_JOB_ID",
                "root_reuse_allowed": False,
                "hard_stop_on": [
                    "MISSING_OR_WRONG_EXACT_SUCCESS_TERMINAL",
                    "NONZERO_EXIT",
                    "TYPED_WATCHER_CANNOT_CHECK",
                    "TYPED_FINALIZER_CANNOT_CHECK",
                    "CLEANUP_DRIFT",
                    "EVIDENCE_DRIFT",
                    "PATH_DRIFT",
                    "HASH_DRIFT",
                    "OUTPUT_ROOT_REUSE",
                ],
            },
        )
        self.assertEqual(
            repair["private_root_topology"],
            {
                "run_root": str(FROZEN_RUN_ROOT),
                "runtime_parent": str(FROZEN_RUN_ROOT / "runtime-parent"),
                "runtime_evidence_root": str(FROZEN_RUN_ROOT / "runtime-parent/evidence"),
                "capture_parent": str(FROZEN_RUN_ROOT / "capture-parent"),
                "capture_root": str(FROZEN_RUN_ROOT / "capture-parent/capture"),
                "final_parent": str(FROZEN_RUN_ROOT / "final-parent"),
                "finalization_root": str(FROZEN_RUN_ROOT / "final-parent/result"),
                "logs_root": str(FROZEN_RUN_ROOT / "logs"),
                "parent_mode": "0700",
                "three_output_roots_absent_before_submission": True,
            },
        )
        self.assertEqual(
            repair["immutable_donor"],
            {
                "root": str(FROZEN_DONOR_ROOT),
                "launcher": {
                    "path": str(FROZEN_DONOR_ROOT / "run_protected_rr1_direct_route_v1.sh"),
                    "sha256": "a540954aaa4ce638190162f39268bf660d7baac7d4e8841d4f56ba5441300219",
                },
                "module": {
                    "path": str(FROZEN_DONOR_ROOT / "protected_rr1_direct_route_v1.py"),
                    "sha256": "7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91",
                },
                "contract": {
                    "path": str(FROZEN_DONOR_ROOT / "PROTECTED_RR1_DIRECT_ROUTE_CONTRACT_V1.json"),
                    "sha256": "a091bf0617d657ee7f8c2bcab08acda96d16246407d791d6a90704efffedc398",
                },
            },
        )

        readiness = contract["terminal_poll_readiness"]
        self.assertEqual(readiness["no_row"], "RETRY")
        self.assertEqual(readiness["preterminal_partition_values"], ["", "gpua40i"])
        self.assertEqual(
            readiness["terminal_incomplete_allowed_sentinels"],
            {
                field: ([""] if field == "Partition" else ["", "Unknown"])
                for field in module.TERMINAL_ACCOUNTING_INCOMPLETE_NORMALIZATION
            },
        )
        self.assertEqual(
            readiness["retry_classifications"],
            [
                "NO_ROW",
                "PRETERMINAL_EMPTY_PARTITION",
                "PRETERMINAL_PARTITION_READY",
                "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL",
            ],
        )
        self.assertEqual(readiness["complete_classification"], "TERMINAL_COMPLETE_gpua40i")
        self.assertTrue(readiness["wrong_nonblank_partition_fails_immediately"])
        self.assertTrue(readiness["malformed_or_contradictory_rows_fail_immediately"])

        certificate = read_json(FAILURE_CERTIFICATE_PATH)
        failed = contract["failed_job_3537828"]
        self.assertEqual(
            failed["certificate"],
            {
                "path": FAILURE_CERTIFICATE_PATH.name,
                "bytes": FAILURE_CERTIFICATE_PATH.stat().st_size,
                "sha256": sha256_bytes(FAILURE_CERTIFICATE_PATH.read_bytes()),
            },
        )
        self.assertEqual(failed["prior_job"], certificate["prior_job"])
        self.assertEqual(failed["logs"], certificate["logs"])
        self.assertEqual(failed["pre_generation_execution"], certificate["pre_generation_execution"])
        self.assertEqual(failed["retry_semantics"], certificate["retry_semantics"])
        predecessor = contract["predecessor_successor_v2_bindings"]
        self.assertEqual(predecessor["mutation"], "NONE")
        for binding in (
            predecessor["contract"], predecessor["failure_certificate"],
            predecessor["finalizer"], predecessor["trampoline"],
            predecessor["sha256s"],
        ):
            path = REPO_ROOT / binding["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(binding["sha256"], sha256_bytes(path.read_bytes()))

    def test_03_cli_argv_is_exact_and_absolute(self) -> None:
        module = self.require_module()
        with self.assertRaises(module.FinalizationError):
            module.parse_cli([
                "finalize", "--evidence-root", "relative",
                "--capture-root", "/tmp/c", "--output-root", "/tmp/x",
            ])
        with self.assertRaises(module.FinalizationError):
            module.parse_cli([
                "finalize", "--evidence-root", "/tmp/e",
                "--capture-root", "/tmp/c", "--output-root", "/tmp/o", "extra",
            ])
        args = module.parse_cli([
            "finalize", "--evidence-root", "/tmp/e",
            "--capture-root", "/tmp/c", "--output-root", "/tmp/o",
        ])
        self.assertEqual(args.evidence_root, Path("/tmp/e"))
        self.assertEqual(args.capture_root, Path("/tmp/c"))
        capture = module.parse_capture_cli([
            "watch-capture", "--job-id", JOB_ID,
            "--output-root", "/tmp/new-capture",
        ])
        self.assertEqual(capture.job_id, JOB_ID)
        with self.assertRaises(module.FinalizationError):
            module.parse_capture_cli([
                "watch-capture", "--job-id", JOB_ID,
                "--partition", PARTITION, "--output-root", "/tmp/new-capture",
            ])
        synthetic_frozen_path = Path("/tmp/SBATCH_STDOUT_V1.txt")
        with mock.patch.object(
            module, "FROZEN_SBATCH_STDOUT_PATH", synthetic_frozen_path
        ):
            parsed_job_id = module.parse_sbatch_job_id_cli([
                "parse-sbatch-job-id", "--input-path", str(synthetic_frozen_path),
            ])
        self.assertEqual(parsed_job_id.input_path, synthetic_frozen_path)
        for argv in (
            ["parse-sbatch-job-id", "--input-path", "relative"],
            ["parse-sbatch-job-id", "--raw", JOB_ID],
            ["parse-sbatch-job-id", "--input-path", "/tmp/out", "extra"],
            ["parse-sbatch-job-id", "--input-path", "/tmp/other-absolute.txt"],
        ):
            with self.subTest(parse_job_id_argv=argv):
                with self.assertRaises(module.FinalizationError):
                    module.parse_sbatch_job_id_cli(argv)

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

        def omit_optional_export(root: Path) -> None:
            (root / "SCHEDULER_EXPORT_V1.jsonl").unlink()

        generated_code, generated_receipt, generated_output = self.run_fixture(
            omit_optional_export, refresh=False
        )
        self.assertEqual(generated_code, 0)
        generated_export = generated_output / "SCHEDULER_EXPORT_V1.jsonl"
        self.assertTrue(generated_export.is_file())
        self.assertEqual(
            sha256_bytes(generated_export.read_bytes()),
            generated_receipt["scheduler_export_raw_record_sha256"],
        )

        module = self.require_module()
        live_row = module.parse_sacct_snapshot(sacct_row(), allow_multiple=False)[0]
        self.assertEqual(live_row["NTasks"], "")
        self.assertEqual(live_row["ReqMem"], "64G")

        def explicit_one_task(root: Path) -> None:
            row = sacct_row(n_tasks="1")
            (root / "POST_JOB_SACCT_V1.txt").write_bytes(row)
            (root / "POST_JOB_SACCT_NONOVERLAP_V1.txt").write_bytes(row)

        explicit_code, _, _ = self.run_fixture(explicit_one_task)
        self.assertEqual(explicit_code, 0)

        for label, row in (
            ("two-tasks", sacct_row(n_tasks="2")),
            ("node-suffixed-reqmem", sacct_row(req_mem="64Gn")),
        ):
            with self.subTest(label=label):
                def mutate(root: Path, payload: bytes = row) -> None:
                    (root / "POST_JOB_SACCT_V1.txt").write_bytes(payload)
                    (root / "POST_JOB_SACCT_NONOVERLAP_V1.txt").write_bytes(payload)
                receipt = self.assert_cannot_check(self.run_fixture(mutate))
                self.assertIn(
                    receipt["failure_code"],
                    {"EXCLUSIVITY_CANNOT_CHECK", "EVIDENCE_PARSE_INVALID"},
                )

    def test_05_sacct_parser_rejects_crlf_extra_rows_and_wrong_field_count(self) -> None:
        module = self.require_module()
        self.assertEqual(sacct_row().count(b"|"), len(SACCT_FIELDS) - 1)
        self.assertFalse(sacct_row().endswith(b"|\n"))
        with self.assertRaises(module.FinalizationError):
            module.parse_sacct_snapshot(sacct_row().replace(b"\n", b"\r\n"), allow_multiple=False)
        with self.assertRaises(module.FinalizationError):
            module.parse_sacct_snapshot(sacct_row() + sacct_row(job_id="4000002"), allow_multiple=False)
        with self.assertRaises(module.FinalizationError):
            module.parse_sacct_snapshot(b"too|short|\n", allow_multiple=False)
        with self.assertRaises(module.FinalizationError):
            module.parse_sacct_snapshot(sacct_row()[:-1] + b"|\n", allow_multiple=False)

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

    def test_07_live_config_partition_formats_and_negative_proofs(self) -> None:
        module = self.require_module()
        live = module.parse_config_snapshots(
            LIVE_CONFIG_HEADER
            + b"BOOT_TIME = 2026-07-31T10:17:20\n"
            + b"SlurmctldHost[0] = cosmos-slurm1\n"
            + b"\nCgroup Support Configuration:\n"
            + b"SLURM_VERSION = 23.11.3\n"
            + b"ClusterName = cosmos\n"
            + b"MinJobAge = 300 sec\n"
            + b"SelectType = select/cons_tres\n"
            + b"GresTypes = gpu\n"
            + b"TaskPlugin = task/cgroup,task/affinity\n"
            + b"ProctrackType = proctrack/cgroup\n"
            + b"AccountingStorageType = accounting_storage/slurmdbd\n"
            + b"AccountingStorageEnforce = associations,limits,qos,safe\n"
            + b"AccountingStorageTRES = gres/gpu\n"
            + b"JobAcctGatherType = jobacct_gather/cgroup\n"
            + b"PrivateData = none\n"
            + b"\nSlurmctld(primary) at cosmos-slurm1 is UP\n",
            b"PartitionName=gpua40i AllowAccounts=ALL Nodes=cg14 OverSubscribe=NO State=UP\n",
            LIVE_NODE_LINE,
        )
        self.assertEqual(set(live["config"]), module.SCHEDULER_CONFIG_REQUIRED_FIELDS)
        self.assertIn("PREEMPT_DYNAMIC", live["node"]["OS"])
        self.assertEqual(live["node"]["AllocTRES"], "")

        def explicit_account_list(root: Path) -> None:
            (root / "SCHEDULER_PARTITION_V1.txt").write_bytes(
                f"PartitionName={PARTITION} AllowAccounts=other,{ACCOUNT} "
                "Nodes=aurora[01-04] OverSubscribe=NO State=UP\n".encode()
            )

        code, _, _ = self.run_fixture(explicit_account_list)
        self.assertEqual(code, 0)

        def account_missing(root: Path) -> None:
            (root / "SCHEDULER_PARTITION_V1.txt").write_bytes(
                f"PartitionName={PARTITION} AllowAccounts=other "
                "Nodes=aurora[01-04] OverSubscribe=NO State=UP\n".encode()
            )

        def affinity_missing(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(
                path.read_bytes().replace(
                    b"TaskPlugin = task/cgroup,task/affinity\n",
                    b"TaskPlugin = task/cgroup\n",
                )
            )

        def cgroup_missing(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(
                path.read_bytes().replace(
                    b"TaskPlugin = task/cgroup,task/affinity\n",
                    b"TaskPlugin = task/affinity\n",
                )
            )

        def header_missing(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(path.read_bytes().removeprefix(LIVE_CONFIG_HEADER))

        def header_malformed(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(path.read_bytes().replace(
                LIVE_CONFIG_HEADER,
                b"Configuration data as of 2026-08-24T22:23\n",
            ))

        def header_misplaced(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            lines = path.read_bytes().splitlines(keepends=True)
            path.write_bytes(lines[1] + lines[0] + b"".join(lines[2:]))

        def required_duplicate(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(path.read_bytes() + b"TaskPlugin = task/cgroup,task/affinity\n")

        def required_case_alias(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(path.read_bytes().replace(
                b"TaskPlugin = task/cgroup,task/affinity\n",
                b"taskplugin = task/cgroup,task/affinity\n",
            ))

        def required_missing(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(path.read_bytes().replace(
                b"TaskPlugin = task/cgroup,task/affinity\n", b""
            ))

        def required_empty_duplicate(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(path.read_bytes() + b"TaskPlugin =\n")

        def required_empty_case_alias(root: Path) -> None:
            path = root / "SCHEDULER_CONFIG_V1.txt"
            path.write_bytes(path.read_bytes() + b"taskplugin =\n")

        for label, mutate in (
            ("account-missing", account_missing),
            ("affinity-missing", affinity_missing),
            ("cgroup-missing", cgroup_missing),
            ("header-missing", header_missing),
            ("header-malformed", header_malformed),
            ("header-misplaced", header_misplaced),
            ("required-duplicate", required_duplicate),
            ("required-case-alias", required_case_alias),
            ("required-missing", required_missing),
            ("required-empty-duplicate", required_empty_duplicate),
            ("required-empty-case-alias", required_empty_case_alias),
        ):
            with self.subTest(label=label):
                receipt = self.assert_cannot_check(self.run_fixture(mutate))
                self.assertIn(
                    receipt["failure_code"],
                    {"EXCLUSIVITY_CANNOT_CHECK", "EVIDENCE_PARSE_INVALID"},
                )

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
        def mutation(field: str, value: Any) -> Any:
            def mutate(root: Path) -> None:
                path = root / "attempt/ATTEMPT_CAPTURE_V1.json"
                capture = read_json(path)
                if field == "base_tuple":
                    capture["base_candidate_record"]["task_id"] = value
                    capture["base_candidate_record_canonical_sha256"] = canonical_hash(
                        capture["base_candidate_record"]
                    )
                elif field == "base_seed":
                    capture["base_candidate_record"]["seed"] = value
                    capture["base_candidate_record_canonical_sha256"] = canonical_hash(
                        capture["base_candidate_record"]
                    )
                else:
                    capture[field] = value
                write_json(path, capture)
                bridge_path = root / "attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
                bridge = read_json(bridge_path)
                bridge["attempt_capture_canonical_sha256"] = canonical_hash(capture)
                write_json(bridge_path, bridge)
            return mutate

        for label, mutate in (
            ("allocation", mutation("allocation_status", "EXCLUSIVE_NO_OVERLAP_CONFIRMED")),
            ("clock-id", mutation("clock_id", "CLOCK_MONOTONIC")),
            ("clock-api", mutation("clock_api", "time_ns")),
            ("base-tuple", mutation("base_tuple", "2")),
            ("base-seed", mutation("base_seed", 202)),
        ):
            with self.subTest(label=label):
                receipt = self.assert_cannot_check(self.run_fixture(mutate))
                self.assertIn(
                    receipt["failure_code"],
                    {"CAPTURE_CANNOT_CHECK", "CROSS_BINDING_MISMATCH"},
                )

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
        def fit_incomplete(root: Path) -> None:
            path = root / "attempt/DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json"
            value = read_json(path)
            value["completion_prompt_n_equal"] = False
            value["status"] = "PRETOKENIZE_FIT__COMPLETION_COUNT_PENDING"
            write_json(path, value)

        def request_hash_unbound(root: Path) -> None:
            path = root / "attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
            value = read_json(path)
            value["request_bindings"][0]["rendered_prompt_sha256"] = "9" * 64
            write_json(path, value)

        def authority_drift(root: Path) -> None:
            path = root / "attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
            value = read_json(path)
            value["authority"] = "SYNTHETIC_AUTHORITY_DRIFT"
            write_json(path, value)

        def capture_authority_drift(root: Path) -> None:
            attempt = root / "attempt"
            path = attempt / "ATTEMPT_CAPTURE_V1.json"
            value = read_json(path)
            value["authority"] = "SYNTHETIC_AUTHORITY_DRIFT"
            write_json(path, value)
            bridge_path = attempt / "DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
            bridge = read_json(bridge_path)
            bridge["attempt_capture_canonical_sha256"] = canonical_hash(value)
            write_json(bridge_path, bridge)

        def dynamic_authority_drift(root: Path) -> None:
            attempt = root / "attempt"
            path = attempt / "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json"
            value = read_json(path)
            value["authority"] = "SYNTHETIC_AUTHORITY_DRIFT"
            write_json(path, value)
            bridge_path = attempt / "DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
            bridge = read_json(bridge_path)
            bridge["dynamic_rr1_pretokenize_file_sha256"] = sha256_bytes(
                path.read_bytes()
            )
            write_json(bridge_path, bridge)

        def gpu_authority_drift(root: Path) -> None:
            path = root / "GPU_ALLOCATION_IDENTITY_V1.json"
            value = read_json(path)
            value["authority"] = "SYNTHETIC_AUTHORITY_DRIFT"
            write_json(path, value)

        def stage_authority_drift(root: Path) -> None:
            stage_path = root / "STAGED_RUNTIME_INPUT_V1.json"
            stage = read_json(stage_path)
            stage["authority"] = "SYNTHETIC_AUTHORITY_DRIFT"
            write_json(stage_path, stage)
            process_path = root / "PROCESS_ATTESTATION_V1.json"
            process = read_json(process_path)
            process["runtime_stage_sha256"] = sha256_bytes(stage_path.read_bytes())
            write_json(process_path, process)
            bridge_path = root / "attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json"
            bridge = read_json(bridge_path)
            bridge["runtime_stage_sha256"] = sha256_bytes(stage_path.read_bytes())
            bridge["process_attestation_sha256"] = sha256_bytes(process_path.read_bytes())
            write_json(bridge_path, bridge)

        def gpu_extra_top_level(root: Path) -> None:
            path = root / "GPU_ALLOCATION_IDENTITY_V1.json"
            value = read_json(path)
            value["extra"] = "must-fail"
            write_json(path, value)

        for label, mutate in (
            ("fit-incomplete", fit_incomplete),
            ("request-hash-unbound", request_hash_unbound),
            ("bridge-authority-drift", authority_drift),
            ("capture-authority-drift", capture_authority_drift),
            ("dynamic-authority-drift", dynamic_authority_drift),
            ("gpu-authority-drift", gpu_authority_drift),
            ("stage-authority-drift", stage_authority_drift),
            ("gpu-extra-top-level", gpu_extra_top_level),
        ):
            with self.subTest(label=label):
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
                module.finalize(
                    evidence.resolve(), (base / "capture").resolve(), output.resolve()
                )
            self.assertEqual(sentinel.read_text(), "keep")

            self.fixture.create(evidence)
            same_root_output = base / "same-root-output"
            with self.assertRaises(module.FinalizationError):
                module.finalize(
                    evidence.resolve(), evidence.resolve(), same_root_output.resolve()
                )
            self.assertFalse(same_root_output.exists())

            capture_root = base / "capture"
            self.fixture.split_capture(evidence, capture_root)
            atomic_output = base / "atomic-output"
            real_write_json = module._write_new_json

            def fail_success_receipt(
                output_fd: int, name: str, value: Any
            ) -> tuple[str, tuple[int, int]]:
                if name == module.SUCCESS_NAME:
                    raise module.FinalizationError(
                        "OUTPUT_INVALID", "synthetic second-write failure"
                    )
                return real_write_json(output_fd, name, value)

            with (
                mock.patch.object(module, "_write_new_json", side_effect=fail_success_receipt),
                self.assertRaises(module.FinalizationError),
            ):
                module.finalize(
                    evidence.resolve(), capture_root.resolve(), atomic_output.resolve()
                )
            self.assertFalse(atomic_output.exists())

    def test_24_cli_terminal_is_body_free_and_exit_codes_are_exact(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            sbatch_stdout = base / "SBATCH_STDOUT_V1.txt"
            write_private(sbatch_stdout, f"{JOB_ID}\n".encode())
            parser_stdout = io.StringIO()
            parser_stderr = io.StringIO()
            with (
                mock.patch.object(
                    module, "FROZEN_SBATCH_STDOUT_PATH", sbatch_stdout.resolve()
                ),
                contextlib.redirect_stdout(parser_stdout),
                contextlib.redirect_stderr(parser_stderr),
            ):
                parser_code = module.main([
                    "parse-sbatch-job-id",
                    "--input-path",
                    str(sbatch_stdout.resolve()),
                ])
            self.assertEqual(parser_code, 0)
            self.assertEqual(parser_stdout.getvalue(), f"{JOB_ID}\n")
            self.assertEqual(parser_stderr.getvalue(), "")

            rendered_module = base / MODULE_PATH.name
            rendered_module.write_text(
                MODULE_PATH.read_text().replace(
                    '\nif __name__ == "__main__":',
                    "\nFROZEN_SBATCH_STDOUT_PATH = Path("
                    f"{str(sbatch_stdout.resolve())!r})\n\n"
                    'if __name__ == "__main__":',
                )
            )
            rendered_module.chmod(0o700)
            hostile_python = base / "hostile-python"
            hostile_python.mkdir(mode=0o700)
            import_marker = base / "PYTHONPATH_WAS_IMPORTED"
            (hostile_python / "hashlib.py").write_text(
                f"from pathlib import Path\nPath({str(import_marker)!r}).write_text('bad')\n"
                "raise RuntimeError('hostile PYTHONPATH imported')\n"
            )
            startup = base / "hostile-startup.py"
            startup.write_text("raise RuntimeError('hostile PYTHONSTARTUP executed')\n")
            parser_env = dict(os.environ)
            parser_env.update({
                "PYTHONPATH": str(hostile_python),
                "PYTHONHOME": str(base / "invalid-python-home"),
                "PYTHONSTARTUP": str(startup),
            })
            parser_process = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-S",
                    str(rendered_module),
                    "parse-sbatch-job-id",
                    "--input-path",
                    str(sbatch_stdout.resolve()),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=parser_env,
                check=False,
                timeout=10,
            )
            self.assertEqual(parser_process.returncode, 0)
            self.assertEqual(parser_process.stdout, f"{JOB_ID}\n".encode())
            self.assertEqual(parser_process.stderr, b"")
            self.assertFalse(import_marker.exists())

            invalid_payloads = (
                b"",
                JOB_ID.encode(),
                b"0\n",
                f"0{JOB_ID}\n".encode(),
                f"{JOB_ID};cosmos\n".encode(),
                f" {JOB_ID}\n".encode(),
                f"{JOB_ID} \n".encode(),
                f"{JOB_ID}\n\n".encode(),
                f"Submitted batch job {JOB_ID}\n".encode(),
                f"{JOB_ID}\r\n".encode(),
                b"\xff\n",
            )
            for index, payload in enumerate(invalid_payloads):
                with self.subTest(sbatch_stdout=payload):
                    invalid = base / f"invalid-{index}.txt"
                    write_private(invalid, payload)
                    out = io.StringIO()
                    err = io.StringIO()
                    with (
                        mock.patch.object(
                            module, "FROZEN_SBATCH_STDOUT_PATH", invalid.resolve()
                        ),
                        contextlib.redirect_stdout(out),
                        contextlib.redirect_stderr(err),
                    ):
                        invalid_code = module.main([
                            "parse-sbatch-job-id",
                            "--input-path",
                            str(invalid.resolve()),
                        ])
                    self.assertEqual(invalid_code, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertRegex(
                        err.getvalue().strip(),
                        r"^P1_SAB_PROTECTED_RR1_SBATCH_JOB_ID_CANNOT_CHECK "
                        r"failure_code=(?:SBATCH_JOB_ID_INVALID|INPUT_SET_INVALID) "
                        r"detail_sha256=[0-9a-f]{64}$",
                    )

            wrong_mode = base / "wrong-mode.txt"
            write_private(wrong_mode, f"{JOB_ID}\n".encode())
            wrong_mode.chmod(0o400)
            hardlink_source = base / "hardlink-source.txt"
            write_private(hardlink_source, f"{JOB_ID}\n".encode())
            hardlink = base / "hardlink.txt"
            os.link(hardlink_source, hardlink)
            symlink = base / "symlink.txt"
            symlink.symlink_to(sbatch_stdout)
            for label, hostile_path in (
                ("wrong-mode", wrong_mode),
                ("hardlink", hardlink),
                ("symlink", symlink),
            ):
                with self.subTest(label=label):
                    out = io.StringIO()
                    err = io.StringIO()
                    with (
                        mock.patch.object(
                            module,
                            "FROZEN_SBATCH_STDOUT_PATH",
                            hostile_path.absolute(),
                        ),
                        contextlib.redirect_stdout(out),
                        contextlib.redirect_stderr(err),
                    ):
                        hostile_code = module.main([
                            "parse-sbatch-job-id",
                            "--input-path",
                            str(hostile_path.absolute()),
                        ])
                    self.assertEqual(hostile_code, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("failure_code=INPUT_SET_INVALID", err.getvalue())

            evidence = base / "evidence"
            capture_root = base / "capture-input"
            output = base / "output"
            evidence.mkdir()
            self.fixture.create(evidence)
            self.fixture.split_capture(evidence, capture_root)
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = module.main([
                    "finalize", "--evidence-root", str(evidence.resolve()),
                    "--capture-root", str(capture_root.resolve()),
                    "--output-root", str(output.resolve()),
                ])
            self.assertEqual(code, 0)
            self.assertEqual(stream.getvalue().strip(), "P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS")
            self.assertTrue((output / "SCHEDULER_EXPORT_V1.jsonl").is_file())

            for label, bad_output in (
                ("preexisting", output.resolve()),
                ("missing-parent", (base / "missing" / "output").resolve()),
            ):
                with self.subTest(label=label):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        bad_code = module.main([
                            "finalize", "--evidence-root", str(evidence.resolve()),
                            "--capture-root", str(capture_root.resolve()),
                            "--output-root", str(bad_output),
                        ])
                    terminal = stderr.getvalue().strip()
                    self.assertEqual(bad_code, 2)
                    self.assertRegex(
                        terminal,
                        r"^P1_SAB_PROTECTED_RR1_ONE_TUPLE_FINALIZER_ARGV_CANNOT_CHECK "
                        r"failure_code=(?:OUTPUT_INVALID|INPUT_SET_INVALID) "
                        r"detail_sha256=[0-9a-f]{64}$",
                    )
                    self.assertNotIn("Traceback", terminal)

            nonprivate = base / "nonprivate"
            nonprivate.mkdir(mode=0o755)
            symlink_parent = base / "parent-link"
            symlink_parent.symlink_to(nonprivate)
            for label, bad_output in (
                ("non-0700-parent", nonprivate / "out"),
                ("symlink-parent", symlink_parent / "out"),
            ):
                with self.subTest(label=label):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        bad_code = module.main([
                            "finalize", "--evidence-root", str(evidence.resolve()),
                            "--capture-root", str(capture_root.resolve()),
                            "--output-root", str(bad_output.absolute()),
                        ])
                    self.assertEqual(bad_code, 2)
                    self.assertNotIn("Traceback", stderr.getvalue())

            unexpected_stderr = io.StringIO()
            with (
                mock.patch.object(
                    module, "finalize", side_effect=RuntimeError("synthetic trap")
                ),
                contextlib.redirect_stderr(unexpected_stderr),
            ):
                unexpected_code = module.main([
                    "finalize", "--evidence-root", str(evidence.resolve()),
                    "--capture-root", str(capture_root.resolve()),
                    "--output-root", str((base / "unexpected-output").resolve()),
                ])
            self.assertEqual(unexpected_code, 2)
            self.assertRegex(
                unexpected_stderr.getvalue().strip(),
                r"failure_code=FINALIZER_RUNTIME_FAILED detail_sha256=[0-9a-f]{64}$",
            )
            self.assertNotIn("Traceback", unexpected_stderr.getvalue())

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

        module = self.require_module()
        with mock.patch.object(
            module, "_validate_evidence", side_effect=RuntimeError("synthetic trap")
        ):
            runtime_receipt = self.assert_cannot_check(self.run_fixture())
        self.assertEqual(runtime_receipt["failure_code"], "FINALIZER_RUNTIME_FAILED")

    def test_26_module_never_executes_scheduler_submission_or_opens_outcomes(self) -> None:
        module = self.require_module()
        source = MODULE_PATH.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            called = node.func
            is_subprocess_call = (
                isinstance(called, ast.Attribute)
                and isinstance(called.value, ast.Name)
                and called.value.id == "subprocess"
            )
            if is_subprocess_call:
                self.assertFalse(
                    any(
                        isinstance(child, ast.Constant) and child.value == "sbatch"
                        for child in ast.walk(node)
                    ),
                    "finalizer must not contain a subprocess call route to sbatch",
                )
        self.assertNotIn("subprocess", module.parse_sbatch_parsable_job_id.__code__.co_names)
        self.assertNotIn("os", module.parse_sbatch_parsable_job_id.__code__.co_names)
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
            persistence_order: list[str] = []

            def fake_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                calls.append(list(actual))
                if actual == argv["post_job_scontrol"]:
                    persistence_order.append("post-job-scontrol-launched")
                self.assertEqual(
                    set(kwargs), {"stdout", "stderr", "env", "check", "timeout"}
                )
                self.assertIs(kwargs["stdout"], module.subprocess.PIPE)
                self.assertIs(kwargs["stderr"], module.subprocess.PIPE)
                self.assertEqual(kwargs["env"], module.CAPTURE_ENVIRONMENT)
                self.assertFalse(kwargs["check"])
                self.assertEqual(kwargs["timeout"], 20)
                return SimpleNamespace(
                    returncode=0, stdout=response_by_argv[tuple(actual)], stderr=b""
                )

            real_write_new_bytes = module._write_new_bytes

            def recording_write_new_bytes(
                output_fd: int, name: str, payload: bytes
            ) -> tuple[str, tuple[int, int]]:
                if name == "POST_JOB_SACCT_V1.txt":
                    persistence_order.append("terminal-sacct-persistence-started")
                return real_write_new_bytes(output_fd, name, payload)

            ticks = iter(range(1_000_000_000, 30_000_000_000, 1_000_000_000))
            with mock.patch.object(
                module, "_write_new_bytes", side_effect=recording_write_new_bytes
            ):
                provenance = module.watch_capture_scheduler(
                    JOB_ID, output.resolve(), runner=fake_runner,
                    sleeper=lambda _: self.fail("terminal fixture must not sleep"),
                    monotonic_ns=lambda: next(ticks),
                )
            expected_order = [
                argv["terminal_sacct"], argv["post_job_scontrol"],
                argv["scheduler_config"], argv["scheduler_partition"],
                argv["scheduler_node"], argv["nonoverlap_sacct"],
            ]
            self.assertEqual(calls, expected_order)
            self.assertEqual(
                persistence_order[:2],
                [
                    "post-job-scontrol-launched",
                    "terminal-sacct-persistence-started",
                ],
            )
            self.assertEqual(provenance["capture_argv"], argv)
            self.assertEqual(provenance["node_name"], NODE)
            self.assertEqual(provenance["terminal_poll_count"], 1)
            self.assertEqual(provenance["capture_command_timeout_seconds"], 20)
            self.assertEqual(provenance["post_terminal_capture_deadline_seconds"], 240)
            self.assertEqual(
                provenance["post_job_scontrol_start_latency_limit_seconds"], 2
            )
            self.assertEqual(
                provenance[
                    "post_job_scontrol_start_seconds_after_terminal_observation"
                ],
                "1.000000000",
            )
            self.assertEqual(
                [item["key"] for item in provenance["capture_command_observations"]],
                [
                    "post_job_scontrol", "scheduler_config",
                    "scheduler_partition", "scheduler_node",
                    "nonoverlap_sacct",
                ],
            )
            self.assertTrue(
                all(
                    item["completed_before_post_terminal_deadline"]
                    for item in provenance["capture_command_observations"]
                )
            )
            self.assertTrue(
                all(
                    item["duration_seconds"] == "1.000000000"
                    for item in provenance["capture_command_observations"]
                )
            )
            self.assertEqual(
                provenance["terminal_poll_observations"][0]["argv"],
                argv["terminal_sacct"],
            )
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
            for path in output.iterdir():
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o400)

            sequence_output = base / "capture-sequence"
            poll_payloads = iter([
                b"",
                sacct_row(state="PENDING", start="", end="", node=""),
                sacct_row(state="RUNNING", end="Unknown"),
                sacct_row(),
            ])
            terminal_calls = 0
            sleeps: list[int] = []

            def sequence_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                nonlocal terminal_calls
                if actual == argv["terminal_sacct"] and terminal_calls < 4:
                    terminal_calls += 1
                    return SimpleNamespace(
                        returncode=0, stdout=next(poll_payloads), stderr=b""
                    )
                return SimpleNamespace(
                    returncode=0, stdout=response_by_argv[tuple(actual)], stderr=b""
                )

            sequence_ticks = iter([
                0, 5_000_000_000, 10_000_000_000, 15_000_000_000,
                *range(16_000_000_000, 40_000_000_000, 1_000_000_000),
            ])
            sequence = module.watch_capture_scheduler(
                JOB_ID, sequence_output.resolve(), runner=sequence_runner,
                sleeper=sleeps.append, monotonic_ns=lambda: next(sequence_ticks),
            )
            self.assertEqual(sequence["terminal_poll_count"], 4)
            self.assertEqual(sleeps, [5, 5, 5])
            self.assertEqual(
                [item["row_count"] for item in sequence["terminal_poll_observations"]],
                [0, 1, 1, 1],
            )
            self.assertEqual(
                [item["terminal"] for item in sequence["terminal_poll_observations"]],
                [False, False, False, True],
            )

    def test_28_watch_capture_failures_retain_only_body_free_private_evidence(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            output = base / "capture"
            calls = 0

            def fake_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                nonlocal calls
                calls += 1
                if calls == 1:
                    return SimpleNamespace(returncode=0, stdout=sacct_row(), stderr=b"")
                return SimpleNamespace(returncode=1, stdout=b"", stderr=b"synthetic")

            with self.assertRaises(module.FinalizationError):
                module.watch_capture_scheduler(
                    JOB_ID, output.resolve(), runner=fake_runner,
                    sleeper=lambda _: None, monotonic_ns=lambda: 1_000_000_000,
                )
            self.assertTrue(output.is_dir())
            self.assertTrue((output / "POST_JOB_SACCT_V1.txt").is_file())
            self.assertTrue((output / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json").is_file())
            cannot = read_json(output / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json")
            self.assertEqual(cannot["failure_code"], "SCHEDULER_CAPTURE_FAILED")
            self.assertNotIn("failure_detail", cannot)
            for path in output.iterdir():
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o400)

            def run_terminal_failure(label: str, payloads: list[bytes]) -> None:
                target = base / label
                iterator = iter(payloads)
                ticks = iter(range(0, 100_000_000_000, 5_000_000_000))

                def terminal_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                    return SimpleNamespace(returncode=0, stdout=next(iterator), stderr=b"")

                with self.assertRaises(module.FinalizationError):
                    module.watch_capture_scheduler(
                        JOB_ID, target.resolve(), runner=terminal_runner,
                        sleeper=lambda _: None, monotonic_ns=lambda: next(ticks),
                    )
                receipt = read_json(target / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json")
                self.assertRegex(receipt["failure_detail_sha256"], r"^[0-9a-f]{64}$")

            run_terminal_failure("multiple", [sacct_row() + sacct_row(job_id="4000002")])
            run_terminal_failure("step", [sacct_row(job_id="4000001.batch")])
            run_terminal_failure("ambiguous-node", [sacct_row(node="aurora[01-02]")])
            with mock.patch.object(module, "TERMINAL_POLL_LIMIT", 2):
                run_terminal_failure("retry-exhausted", [b"", b""])

            hung_output = base / "hung-scontrol"
            hung_calls = 0

            def hung_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                nonlocal hung_calls
                hung_calls += 1
                if hung_calls == 1:
                    return SimpleNamespace(returncode=0, stdout=sacct_row(), stderr=b"")
                raise module.subprocess.TimeoutExpired(
                    cmd=actual, timeout=kwargs["timeout"]
                )

            hung_ticks = iter(range(0, 100_000_000_000, 1_000_000_000))
            with self.assertRaises(module.FinalizationError):
                module.watch_capture_scheduler(
                    JOB_ID, hung_output.resolve(), runner=hung_runner,
                    sleeper=lambda _: None, monotonic_ns=lambda: next(hung_ticks),
                )
            hung = read_json(hung_output / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json")
            self.assertEqual(hung["failure_code"], "SCHEDULER_CAPTURE_TIMEOUT")
            self.assertTrue((hung_output / "POST_JOB_SACCT_V1.txt").is_file())

            unexpected_output = base / "unexpected-runner"
            unexpected_calls = 0

            def unexpected_runner(
                actual: list[str], **kwargs: Any
            ) -> SimpleNamespace:
                nonlocal unexpected_calls
                unexpected_calls += 1
                if unexpected_calls == 1:
                    return SimpleNamespace(returncode=0, stdout=sacct_row(), stderr=b"")
                raise RuntimeError("synthetic runner trap")

            with self.assertRaises(module.FinalizationError) as unexpected_context:
                module.watch_capture_scheduler(
                    JOB_ID, unexpected_output.resolve(), runner=unexpected_runner,
                    sleeper=lambda _: None,
                    monotonic_ns=lambda: 1_000_000_000,
                )
            self.assertEqual(
                unexpected_context.exception.code,
                "SCHEDULER_CAPTURE_RUNTIME_FAILED",
            )
            unexpected = read_json(
                unexpected_output / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json"
            )
            self.assertEqual(
                unexpected["failure_code"], "SCHEDULER_CAPTURE_RUNTIME_FAILED"
            )
            self.assertTrue(
                (unexpected_output / "POST_JOB_SACCT_V1.txt").is_file()
            )

            latency_output = base / "late-first-scontrol"
            latency_calls = 0

            def latency_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                nonlocal latency_calls
                latency_calls += 1
                if latency_calls == 1:
                    return SimpleNamespace(returncode=0, stdout=sacct_row(), stderr=b"")
                return SimpleNamespace(
                    returncode=0,
                    stdout=scontrol_snapshot(state="COMPLETED", end=END),
                    stderr=b"",
                )

            latency_ticks = iter([0, 1_000_000_000, 3_000_000_001])
            with self.assertRaises(module.FinalizationError):
                module.watch_capture_scheduler(
                    JOB_ID, latency_output.resolve(), runner=latency_runner,
                    sleeper=lambda _: None,
                    monotonic_ns=lambda: next(latency_ticks),
                )
            latency = read_json(
                latency_output / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json"
            )
            self.assertEqual(
                latency["failure_code"],
                "SCHEDULER_CAPTURE_START_LATENCY_EXCEEDED",
            )
            self.assertEqual(latency_calls, 1)
            self.assertTrue((latency_output / "POST_JOB_SACCT_V1.txt").is_file())
            self.assertFalse((latency_output / "POST_JOB_SCONTROL_V1.txt").exists())

            duration_output = base / "over-duration-scontrol"
            duration_calls = 0

            def duration_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                nonlocal duration_calls
                duration_calls += 1
                if duration_calls == 1:
                    return SimpleNamespace(returncode=0, stdout=sacct_row(), stderr=b"")
                return SimpleNamespace(
                    returncode=0,
                    stdout=scontrol_snapshot(state="COMPLETED", end=END),
                    stderr=b"",
                )

            duration_ticks = iter([0, 1_000_000_000, 2_000_000_000, 22_000_000_001])
            with self.assertRaises(module.FinalizationError):
                module.watch_capture_scheduler(
                    JOB_ID, duration_output.resolve(), runner=duration_runner,
                    sleeper=lambda _: None,
                    monotonic_ns=lambda: next(duration_ticks),
                )
            duration = read_json(
                duration_output / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json"
            )
            self.assertEqual(duration["failure_code"], "SCHEDULER_CAPTURE_TIMEOUT")
            self.assertTrue((duration_output / "POST_JOB_SACCT_V1.txt").is_file())
            self.assertFalse((duration_output / "POST_JOB_SCONTROL_V1.txt").exists())

            deadline_output = base / "deadline"
            deadline_calls = 0

            def deadline_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                nonlocal deadline_calls
                deadline_calls += 1
                if deadline_calls == 1:
                    return SimpleNamespace(returncode=0, stdout=sacct_row(), stderr=b"")
                return SimpleNamespace(
                    returncode=0,
                    stdout=scontrol_snapshot(state="COMPLETED", end=END),
                    stderr=b"",
                )

            deadline_ticks = iter([
                0, 1_000_000_000, 2_000_000_000,
                3_000_000_000, 242_000_000_000,
            ])
            with self.assertRaises(module.FinalizationError):
                module.watch_capture_scheduler(
                    JOB_ID, deadline_output.resolve(), runner=deadline_runner,
                    sleeper=lambda _: None,
                    monotonic_ns=lambda: next(deadline_ticks),
                )
            deadline = read_json(
                deadline_output / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json"
            )
            self.assertEqual(
                deadline["failure_code"], "SCHEDULER_CAPTURE_DEADLINE_EXCEEDED"
            )
            self.assertTrue((deadline_output / "POST_JOB_SCONTROL_V1.txt").is_file())

            preexisting = base / "preexisting"
            preexisting.mkdir(mode=0o700)
            sentinel = preexisting / "sentinel"
            sentinel.write_text("keep")
            with self.assertRaises(module.FinalizationError):
                module.watch_capture_scheduler(
                    JOB_ID, preexisting.resolve(), runner=fake_runner,
                    sleeper=lambda _: None, monotonic_ns=lambda: 3_000_000_000,
                )
            self.assertEqual(sentinel.read_text(), "keep")

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

        def wrong_start_latency(provenance: dict[str, Any]) -> None:
            provenance[
                "post_job_scontrol_start_seconds_after_terminal_observation"
            ] = "2.000000001"

        def wrong_duration(provenance: dict[str, Any]) -> None:
            provenance["capture_command_observations"][0][
                "duration_seconds"
            ] = "0.999999999"

        def utc_regression(provenance: dict[str, Any]) -> None:
            provenance["capture_command_observations"][1][
                "started_at_utc"
            ] = "2026-08-24T22:23:09.000000Z"

        for label, timing_mutator in (
            ("start-latency-arithmetic", wrong_start_latency),
            ("command-duration-arithmetic", wrong_duration),
            ("utc-order", utc_regression),
        ):
            with self.subTest(label=label):
                def capture_mutate(
                    capture_root: Path, mutator: Any = timing_mutator
                ) -> None:
                    path = capture_root / "SCHEDULER_CAPTURE_PROVENANCE_V1.json"
                    path.chmod(0o600)
                    provenance = read_json(path)
                    mutator(provenance)
                    write_json(path, provenance)
                    path.chmod(0o400)

                timing_receipt = self.assert_cannot_check(
                    self.run_fixture(capture_mutate=capture_mutate)
                )
                self.assertEqual(
                    timing_receipt["failure_code"], "SCHEDULER_CAPTURE_FAILED"
                )

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

        def capture_mode_drift(capture_root: Path) -> None:
            (capture_root / "SCHEDULER_CAPTURE_PROVENANCE_V1.json").chmod(0o600)

        receipt = self.assert_cannot_check(
            self.run_fixture(capture_mutate=capture_mode_drift)
        )
        self.assertEqual(receipt["failure_code"], "INPUT_SET_INVALID")

        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            output = base / "alias-output"
            evidence.mkdir()
            self.fixture.create(evidence)
            alias = evidence / ".." / "evidence"
            code, alias_receipt = module.finalize(
                evidence.resolve(), alias.absolute(), output.resolve()
            )
            self.assertEqual(code, 1)
            self.assertEqual(alias_receipt["failure_code"], "INPUT_SET_INVALID")

    def test_34_symlinked_output_parent_is_rejected(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            evidence.mkdir()
            self.fixture.create(evidence)
            capture_root = base / "capture"
            self.fixture.split_capture(evidence, capture_root)
            real_parent = base / "real-parent"
            real_parent.mkdir(mode=0o700)
            alias = base / "alias"
            alias.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaises(module.FinalizationError):
                module.finalize(evidence.resolve(), capture_root.resolve(), alias / "output")
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

            for label, drift in (
                ("mode", lambda target: target.chmod(0o644)),
                ("link-count", lambda target: os.link(target, root / "held-link.txt")),
            ):
                with self.subTest(label=label):
                    target = root / f"held-{label}.txt"
                    write_private(target, b"original\n")
                    fd = os.open(root, os.O_RDONLY)
                    changed = False

                    def drifting_read(file_fd: int, count: int) -> bytes:
                        nonlocal changed
                        payload = real_read(file_fd, count)
                        if not changed:
                            changed = True
                            drift(target)
                        return payload

                    try:
                        with mock.patch.object(module.os, "read", side_effect=drifting_read):
                            with self.assertRaises(module.FinalizationError):
                                module._read_held(fd, target.name, f"{label} fixture")
                    finally:
                        os.close(fd)

    def test_36_success_output_directory_and_file_modes_are_exact(self) -> None:
        code, _, output = self.run_fixture()
        self.assertEqual(code, 0)
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
        receipt = output / "ONE_TUPLE_FINALIZATION_RECEIPT_V1.json"
        self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
        self.assertEqual(receipt.stat().st_nlink, 1)
        export = output / "SCHEDULER_EXPORT_V1.jsonl"
        self.assertEqual(stat.S_IMODE(export.stat().st_mode), 0o600)
        self.assertEqual(export.stat().st_nlink, 1)

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
            capture_root = base / "capture"
            self.fixture.split_capture(evidence, capture_root)
            real_open = module.os.open
            opened: list[str] = []

            def recording_open(path: Any, *args: Any, **kwargs: Any) -> int:
                try:
                    opened.append(os.fspath(path))
                except TypeError:
                    pass
                return real_open(path, *args, **kwargs)

            with mock.patch.object(module.os, "open", side_effect=recording_open):
                code, _ = module.finalize(
                    evidence.resolve(), capture_root.resolve(), output.resolve()
                )
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
            capture_root = base / "capture"
            self.fixture.split_capture(evidence, capture_root)
            forbidden = AssertionError("forbidden finalize side effect")
            with (
                mock.patch.object(module.subprocess, "run", side_effect=forbidden),
                mock.patch.object(module.os, "getenv", side_effect=forbidden),
                mock.patch.object(socket, "socket", side_effect=forbidden),
                mock.patch.object(socket, "create_connection", side_effect=forbidden),
            ):
                code, receipt = module.finalize(
                    evidence.resolve(), capture_root.resolve(), output.resolve()
                )
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

    def test_41_spooled_trampoline_executes_original_hash_bound_launcher(self) -> None:
        module = self.require_module()
        self.assertTrue(TRAMPOLINE_PATH.is_file(), "TDD RED: spool-safe trampoline absent")
        self.assertTrue(FAILURE_CERTIFICATE_PATH.is_file())
        trampoline = TRAMPOLINE_PATH.read_text()
        donor_launcher = PREDECESSOR_DIRECT_ROOT / "run_protected_rr1_direct_route_v1.sh"
        donor_module = PREDECESSOR_DIRECT_ROOT / "protected_rr1_direct_route_v1.py"
        expected_directives = [
            line for line in donor_launcher.read_text().splitlines()
            if line.startswith("#SBATCH ")
        ]
        actual_directives = [
            line for line in trampoline.splitlines() if line.startswith("#SBATCH ")
        ]
        self.assertEqual(len(expected_directives), 10)
        self.assertEqual(actual_directives, expected_directives)
        self.assertIn(f"SUCCESSOR_ROOT='{FROZEN_SUCCESSOR_ROOT}'", trampoline)
        self.assertIn(f"ORIGINAL_ROOT='{FROZEN_DONOR_ROOT}'", trampoline)
        self.assertIn("SLURM_SUBMIT_DIR", trampoline)
        self.assertIn('[[ "${PWD-}" == "$SUCCESSOR_ROOT" ]]', trampoline)
        self.assertEqual(trampoline.splitlines()[0], "#!/usr/bin/bash")
        self.assertIn(f"BASH_PATH='{FROZEN_BASH_PATH}'", trampoline)
        self.assertIn(f"BASH_SHA256='{FROZEN_BASH_SHA256}'", trampoline)
        self.assertIn(f"SHA256SUM_PATH='{FROZEN_SHA256SUM_PATH}'", trampoline)
        self.assertIn(f"SHA256SUM_SHA256='{FROZEN_SHA256SUM_SHA256}'", trampoline)
        self.assertIn(f"PYTHON_PATH_ENTRY='{FROZEN_PYTHON_PATH_ENTRY}'", trampoline)
        self.assertIn(f"PYTHON_COMMAND='{FROZEN_PYTHON_COMMAND}'", trampoline)
        self.assertIn(f"PYTHON_REAL_TARGET='{FROZEN_PYTHON_REAL_TARGET}'", trampoline)
        self.assertIn(f"PYTHON_REAL_TARGET_SHA256='{FROZEN_PYTHON_SHA256}'", trampoline)
        self.assertIn(f"RUNTIME_PATH='{FROZEN_RUNTIME_PATH}'", trampoline)
        self.assertIn(f"READLINK_SHA256='{FROZEN_READLINK_SHA256}'", trampoline)
        self.assertIn(f"CMP_SHA256='{FROZEN_CMP_SHA256}'", trampoline)
        self.assertIn(f"STAT_SHA256='{FROZEN_STAT_SHA256}'", trampoline)
        self.assertIn(f"WC_PATH='{FROZEN_WC_PATH}'", trampoline)
        self.assertIn(f"WC_SHA256='{FROZEN_WC_SHA256}'", trampoline)
        self.assertIn(
            f"NORMALIZED_TRAMPOLINE_SHA256='{FROZEN_NORMALIZED_TRAMPOLINE_SHA256}'",
            trampoline,
        )
        self.assertEqual(
            normalized_trampoline_sha256(TRAMPOLINE_PATH.read_bytes()),
            FROZEN_NORMALIZED_TRAMPOLINE_SHA256,
        )
        self.assertIn(
            f"PYTHON_LIBRARY_LOGICAL_DIR='{FROZEN_PYTHON_LIBRARY_LOGICAL_DIR}'",
            trampoline,
        )
        self.assertIn(
            f"PYTHON_LIBRARY_CANONICAL_DIR='{FROZEN_PYTHON_LIBRARY_CANONICAL_DIR}'",
            trampoline,
        )
        self.assertIn(f"LIBPYTHON_SHA256='{FROZEN_LIBPYTHON_SHA256}'", trampoline)
        self.assertIn(f"LIBPYTHON_SIZE='{FROZEN_LIBPYTHON_SIZE}'", trampoline)
        self.assertIn(
            f"PYTHON_LIBRARY_DIR_NLINK='{FROZEN_PYTHON_LIBRARY_DIR_NLINK}'",
            trampoline,
        )
        self.assertIn(
            f"LIBPYTHON_ABI_SHA256='{FROZEN_LIBPYTHON_ABI_SHA256}'", trampoline
        )
        self.assertIn(
            f"LIBPYTHON_ABI_SIZE='{FROZEN_LIBPYTHON_ABI_SIZE}'", trampoline
        )
        self.assertIn("[[ ${LD_LIBRARY_PATH+x} != x ]]", trampoline)
        self.assertIn("[[ ${LD_PRELOAD+x} != x ]]", trampoline)
        self.assertIn('export LD_LIBRARY_PATH="$PYTHON_LIBRARY_LOGICAL_DIR"', trampoline)
        self.assertIn("-B -I -S -c 'import ctypes,tarfile,zlib'", trampoline)
        self.assertIn('export PATH="$RUNTIME_PATH"', trampoline)
        self.assertIn('[[ "$(command -v python3)" == "$PYTHON_COMMAND" ]]', trampoline)
        self.assertIn('"$CMP_PATH" -s -- "$0" "$CANONICAL_TRAMPOLINE"', trampoline)
        self.assertNotRegex(
            trampoline, r"(?m)^\s*(?:sha256sum|cut|readlink|cmp|wc)\b"
        )
        self.assertNotIn("BASH_SOURCE", trampoline)
        self.assertNotIn("--wrap", trampoline)
        self.assertIn(sha256_bytes(donor_launcher.read_bytes()), trampoline)
        self.assertIn(sha256_bytes(donor_module.read_bytes()), trampoline)
        self.assertIn(
            sha256_bytes(
                (PREDECESSOR_DIRECT_ROOT / "PROTECTED_RR1_DIRECT_ROUTE_CONTRACT_V1.json").read_bytes()
            ),
            trampoline,
        )
        self.assertIn('exec /usr/bin/bash "$ORIGINAL_LAUNCHER" "$@"', trampoline)
        self.assertNotIn('exec bash "$ORIGINAL_LAUNCHER" "$@"', trampoline)
        for value in FROZEN_DIRECT_EXECUTION_ARGV:
            self.assertIn(value, trampoline)

        self.assertEqual(module.parse_sbatch_parsable_job_id(b"3538000\n"), "3538000")
        for payload in (
            b"", b"3538000", b"0\n", b"03538000\n", b"3538000;cosmos\n",
            b" 3538000\n", b"3538000 \n", b"3538000\n\n",
            b"Submitted batch job 3538000\n", b"3538000\r\n", b"\xff\n",
        ):
            with self.subTest(sbatch_stdout=payload):
                with self.assertRaises(module.FinalizationError):
                    module.parse_sbatch_parsable_job_id(payload)

        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            successor_root = base / "successor-snapshot"
            canonical_trampoline = (
                successor_root
                / ROOT.relative_to(REPO_ROOT)
                / TRAMPOLINE_PATH.name
            )
            canonical_trampoline.parent.mkdir(parents=True)
            tool_root = base / "toolchain"
            tool_root.mkdir(mode=0o700)
            local_bash = Path(shutil.which("bash") or "/bin/bash").resolve()
            local_sha256sum = Path(shutil.which("sha256sum") or "")
            local_readlink = Path(shutil.which("readlink") or "")
            local_cmp = Path(shutil.which("cmp") or "")
            local_wc = Path(shutil.which("wc") or "")
            self.assertTrue(local_sha256sum.is_file())
            self.assertTrue(local_readlink.is_file())
            self.assertTrue(local_cmp.is_file())
            self.assertTrue(local_wc.is_file())
            fake_stat = tool_root / "stat"
            fake_stat.write_text(
                f"#!{sys.executable}\n"
                "import os,stat,sys\n"
                "value=os.stat(sys.argv[-1], follow_symlinks=True)\n"
                "fmt=next((arg for arg in sys.argv[1:] if '%' in arg), '')\n"
                "fields={'%s':value.st_size,'%a':f'{stat.S_IMODE(value.st_mode):o}',"
                "'%u':value.st_uid,'%g':value.st_gid,'%h':value.st_nlink}\n"
                "if fmt not in ('%a %u %g %h','%a %u %g','%s %a %u %g %h'):\n"
                "    raise SystemExit(64)\n"
                "print(' '.join(str(fields[token]) for token in fmt.split()))\n"
            )
            fake_stat.chmod(0o700)
            fake_bin = base / "fake-bin"
            fake_bin.mkdir(mode=0o700)
            fake_library_dir = base / "fake-python-lib"
            fake_library_dir.mkdir(mode=0o755)
            fake_library = fake_library_dir / "libpython3.11.so.1.0"
            fake_library_bytes = b"synthetic-libpython-v3-fixture"
            fake_abi_library = fake_library_dir / "libpython3.so"
            fake_abi_library_bytes = b"synthetic-libpython-abi-v3-fixture"

            def reset_library_namespace() -> None:
                fake_library_dir.chmod(0o755)
                for entry in tuple(fake_library_dir.iterdir()):
                    if entry.is_dir() and not entry.is_symlink():
                        shutil.rmtree(entry)
                    else:
                        entry.unlink()
                fake_library.write_bytes(fake_library_bytes)
                fake_library.chmod(0o755)
                fake_abi_library.write_bytes(fake_abi_library_bytes)
                fake_abi_library.chmod(0o755)
                (fake_library_dir / "libpython3.11.so").symlink_to(
                    "libpython3.11.so.1.0"
                )
                (fake_library_dir / "pkgconfig").mkdir(mode=0o755)
                (fake_library_dir / "python3.11").mkdir(mode=0o755)

            reset_library_namespace()
            fake_python_target = tool_root / "python3.11"
            fake_python_target.write_text(
                f"#!{local_bash}\n"
                "if [[ \"${1-}\" == '-B' ]]; then\n"
                "  [[ -z \"${SYNTHETIC_PROBE_STDOUT-}\" ]] || printf '%s' \"$SYNTHETIC_PROBE_STDOUT\"\n"
                "  [[ -z \"${SYNTHETIC_PROBE_STDERR-}\" ]] || printf '%s' \"$SYNTHETIC_PROBE_STDERR\" >&2\n"
                "  exit \"${SYNTHETIC_PROBE_EXIT_CODE-0}\"\n"
                "fi\n"
                "printf 'PATH=%s\\n' \"$PATH\"\n"
                "printf 'LD_LIBRARY_PATH=%s\\n' \"$LD_LIBRARY_PATH\"\n"
                "printf 'PYARGV:%s\\n' \"$@\"\n"
            )
            fake_python_target.chmod(0o700)
            fake_python = fake_bin / "python3"
            fake_python.symlink_to(fake_python_target)
            local_runtime_path = f"{fake_bin}:/usr/bin:/bin"
            replacements = {
                str(FROZEN_SUCCESSOR_ROOT): str(successor_root),
                str(FROZEN_DONOR_ROOT): str(PREDECESSOR_DIRECT_ROOT.resolve()),
                str(FROZEN_BASH_PATH): str(local_bash),
                FROZEN_BASH_SHA256: sha256_bytes(local_bash.read_bytes()),
                str(FROZEN_SHA256SUM_PATH): str(local_sha256sum),
                FROZEN_SHA256SUM_SHA256: sha256_bytes(local_sha256sum.read_bytes()),
                FROZEN_READLINK_SHA256: sha256_bytes(local_readlink.read_bytes()),
                FROZEN_CMP_SHA256: sha256_bytes(local_cmp.read_bytes()),
                str(FROZEN_WC_PATH): str(local_wc),
                FROZEN_WC_SHA256: sha256_bytes(local_wc.read_bytes()),
                str(FROZEN_STAT_PATH): str(fake_stat),
                FROZEN_STAT_SHA256: sha256_bytes(fake_stat.read_bytes()),
                str(FROZEN_PYTHON_REAL_TARGET): str(fake_python_target),
                FROZEN_PYTHON_SHA256: sha256_bytes(fake_python_target.read_bytes()),
                str(FROZEN_PYTHON_PATH_ENTRY): str(fake_bin),
                str(FROZEN_READLINK_PATH): str(local_readlink),
                str(FROZEN_CMP_PATH): str(local_cmp),
                str(FROZEN_PYTHON_LIBRARY_CANONICAL_DIR): str(fake_library_dir),
                str(FROZEN_PYTHON_LIBRARY_LOGICAL_DIR): str(fake_library_dir),
                FROZEN_LIBPYTHON_SHA256: sha256_bytes(fake_library_bytes),
                str(FROZEN_LIBPYTHON_SIZE): str(len(fake_library_bytes)),
                f"LIBPYTHON_UID='{FROZEN_LIBPYTHON_UID}'": f"LIBPYTHON_UID='{os.getuid()}'",
                f"LIBPYTHON_GID='{FROZEN_LIBPYTHON_GID}'": f"LIBPYTHON_GID='{os.getgid()}'",
                f"PYTHON_LIBRARY_DIR_UID='{FROZEN_PYTHON_LIBRARY_DIR_UID}'": (
                    f"PYTHON_LIBRARY_DIR_UID='{os.getuid()}'"
                ),
                f"PYTHON_LIBRARY_DIR_GID='{FROZEN_PYTHON_LIBRARY_DIR_GID}'": (
                    f"PYTHON_LIBRARY_DIR_GID='{os.getgid()}'"
                ),
                f"PYTHON_LIBRARY_DIR_NLINK='{FROZEN_PYTHON_LIBRARY_DIR_NLINK}'": (
                    f"PYTHON_LIBRARY_DIR_NLINK='{fake_library_dir.stat().st_nlink}'"
                ),
                FROZEN_LIBPYTHON_ABI_SHA256: sha256_bytes(fake_abi_library_bytes),
                str(FROZEN_LIBPYTHON_ABI_SIZE): str(len(fake_abi_library_bytes)),
                f"LIBPYTHON_ABI_UID='{FROZEN_LIBPYTHON_ABI_UID}'": (
                    f"LIBPYTHON_ABI_UID='{os.getuid()}'"
                ),
                f"LIBPYTHON_ABI_GID='{FROZEN_LIBPYTHON_ABI_GID}'": (
                    f"LIBPYTHON_ABI_GID='{os.getgid()}'"
                ),
            }
            rendered = trampoline
            for frozen, local in replacements.items():
                rendered = rendered.replace(frozen, local)
            rendered = rendered.replace(
                f"RUNTIME_PATH='{fake_bin}:/usr/bin:/bin'",
                f"RUNTIME_PATH='{local_runtime_path}'",
            )
            rendered_normalized_sha256 = normalized_trampoline_sha256(
                rendered.encode()
            )
            rendered, rendered_binding_count = re.subn(
                r"(?m)^NORMALIZED_TRAMPOLINE_SHA256='[0-9a-f]{64}'$",
                f"NORMALIZED_TRAMPOLINE_SHA256='{rendered_normalized_sha256}'",
                rendered,
            )
            self.assertEqual(rendered_binding_count, 1)
            canonical_trampoline.write_text(rendered)
            canonical_trampoline.chmod(0o700)
            spooled = base / "slurm_script"
            spooled.write_text(rendered)
            spooled.chmod(0o700)
            env = dict(os.environ)
            env.pop("LD_LIBRARY_PATH", None)
            env.pop("LD_PRELOAD", None)
            env["SLURM_SUBMIT_DIR"] = str(successor_root)
            env["PWD"] = str(successor_root)
            env["PATH"] = "/hostile/path"
            completed = subprocess.run(
                [str(local_bash), str(spooled), *FROZEN_DIRECT_EXECUTION_ARGV],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                cwd=successor_root, check=False, timeout=10,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr.decode())
            lines = completed.stdout.decode().splitlines()
            self.assertEqual(
                lines,
                [
                    f"PATH={local_runtime_path}",
                    f"LD_LIBRARY_PATH={fake_library_dir}",
                    f"PYARGV:{donor_module.resolve()}",
                    "PYARGV:supervise",
                    *(f"PYARGV:{value}" for value in FROZEN_DIRECT_EXECUTION_ARGV),
                ],
            )

            for variable, value in (
                ("LD_LIBRARY_PATH", ""),
                ("LD_LIBRARY_PATH", str(fake_library_dir)),
                ("LD_LIBRARY_PATH", "/hostile/library"),
                ("LD_PRELOAD", ""),
                ("LD_PRELOAD", "/hostile/preload.so"),
            ):
                with self.subTest(inherited_variable=variable, inherited_value=value):
                    hostile_env = dict(env)
                    hostile_env[variable] = value
                    hostile = subprocess.run(
                        [str(local_bash), str(spooled), *FROZEN_DIRECT_EXECUTION_ARGV],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env=hostile_env, cwd=successor_root, check=False, timeout=10,
                    )
                    self.assertEqual(hostile.returncode, 2)
                    self.assertEqual(hostile.stdout, b"")
                    self.assertRegex(
                        hostile.stderr.decode(),
                        r"^P1_SAB_PROTECTED_RR1_DIRECT_EXECUTION_TRAMPOLINE_V3_CANNOT_CHECK "
                        r"failure_code=ENVIRONMENT_INVALID detail_sha256=[0-9a-f]{64}\n$",
                    )

            for label, mutate_library in (
                ("missing", lambda: fake_library.unlink()),
                ("wrong-bytes", lambda: fake_library.write_bytes(b"wrong")),
                ("wrong-mode", lambda: fake_library.chmod(0o700)),
                (
                    "hardlink",
                    lambda: os.link(
                        fake_library, fake_library_dir / ".synthetic-hardlink"
                    ),
                ),
                (
                    "unexpected-dso",
                    lambda: (fake_library_dir / "libsynthetic-hostile.so").write_bytes(
                        b"hostile"
                    ),
                ),
                ("directory-custody", lambda: fake_library_dir.chmod(0o700)),
                (
                    "child-directory-custody",
                    lambda: (fake_library_dir / "pkgconfig").chmod(0o700),
                ),
                ("abi-missing", lambda: fake_abi_library.unlink()),
                ("abi-wrong-bytes", lambda: fake_abi_library.write_bytes(b"wrong")),
                ("abi-wrong-mode", lambda: fake_abi_library.chmod(0o700)),
            ):
                with self.subTest(libpython=label):
                    reset_library_namespace()
                    mutate_library()
                    hostile = subprocess.run(
                        [str(local_bash), str(spooled), *FROZEN_DIRECT_EXECUTION_ARGV],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env=env, cwd=successor_root, check=False, timeout=10,
                    )
                    self.assertEqual(hostile.returncode, 2)
                    self.assertEqual(hostile.stdout, b"")
                    self.assertIn(b"failure_code=LIBPYTHON_DRIFT", hostile.stderr)
                    self.assertNotIn(b"Traceback", hostile.stderr)
            reset_library_namespace()

            for label, variable in (
                ("stdout", "SYNTHETIC_PROBE_STDOUT"),
                ("stderr", "SYNTHETIC_PROBE_STDERR"),
            ):
                with self.subTest(python_runtime_probe_output=label):
                    hostile_env = dict(env)
                    hostile_env[variable] = f"synthetic-{label}-must-not-pass"
                    hostile = subprocess.run(
                        [str(local_bash), str(spooled), *FROZEN_DIRECT_EXECUTION_ARGV],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=hostile_env,
                        cwd=successor_root,
                        check=False,
                        timeout=10,
                    )
                    self.assertEqual(hostile.returncode, 2)
                    self.assertEqual(hostile.stdout, b"")
                    self.assertRegex(
                        hostile.stderr.decode(),
                        r"^P1_SAB_PROTECTED_RR1_DIRECT_EXECUTION_TRAMPOLINE_V3_CANNOT_CHECK "
                        r"failure_code=PYTHON_RUNTIME_UNAVAILABLE detail_sha256=[0-9a-f]{64}\n$",
                    )
                    self.assertNotIn(b"PYARGV:supervise", hostile.stdout)

            for label, submit_dir, cwd, argv in (
                ("relative", ".", successor_root, FROZEN_DIRECT_EXECUTION_ARGV),
                ("missing", str(base / "missing"), successor_root, FROZEN_DIRECT_EXECUTION_ARGV),
                ("wrong-cwd", str(successor_root), base, FROZEN_DIRECT_EXECUTION_ARGV),
                ("arbitrary-argv", str(successor_root), successor_root, ("--synthetic-arg", "value")),
                ("reordered-argv", str(successor_root), successor_root, tuple(reversed(FROZEN_DIRECT_EXECUTION_ARGV))),
            ):
                with self.subTest(label=label):
                    hostile_env = dict(env)
                    hostile_env["SLURM_SUBMIT_DIR"] = submit_dir
                    hostile = subprocess.run(
                        [str(local_bash), str(spooled), *argv],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env=hostile_env, cwd=cwd, check=False, timeout=10,
                    )
                    self.assertNotEqual(hostile.returncode, 0)
                    self.assertNotIn(b"Traceback", hostile.stderr)

            alias = base / "repo-alias"
            alias.symlink_to(successor_root, target_is_directory=True)
            alias_env = dict(env)
            alias_env["SLURM_SUBMIT_DIR"] = str(alias)
            alias_result = subprocess.run(
                [str(local_bash), str(spooled), *FROZEN_DIRECT_EXECUTION_ARGV],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=alias_env,
                cwd=successor_root, check=False, timeout=10,
            )
            self.assertNotEqual(alias_result.returncode, 0)

            identically_stale = rendered.replace(
                "umask 077\n", "umask 077\n# synthetic identical stale bytes\n", 1
            )
            canonical_trampoline.write_text(identically_stale)
            spooled.write_text(identically_stale)
            self.assertEqual(
                canonical_trampoline.read_bytes(), spooled.read_bytes()
            )
            identically_stale_result = subprocess.run(
                [str(local_bash), str(spooled), *FROZEN_DIRECT_EXECUTION_ARGV],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=successor_root,
                check=False,
                timeout=10,
            )
            self.assertEqual(identically_stale_result.returncode, 2)
            self.assertEqual(identically_stale_result.stdout, b"")
            self.assertIn(b"failure_code=SOURCE_DRIFT", identically_stale_result.stderr)

            canonical_trampoline.write_text(rendered + "\n")
            spooled.write_text(rendered)
            source_drift = subprocess.run(
                [str(local_bash), str(spooled), *FROZEN_DIRECT_EXECUTION_ARGV],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                cwd=successor_root, check=False, timeout=10,
            )
            self.assertNotEqual(source_drift.returncode, 0)
            self.assertIn(b"SOURCE_DRIFT", source_drift.stderr)

        certificate = read_json(FAILURE_CERTIFICATE_PATH)
        self.assertEqual(certificate["prior_job"], {
            "job_id": "3537828", "state": "FAILED", "exit_code": "127:0",
            "elapsed_seconds": 1, "node": "cg14",
            "allocated_gpu_count": 1, "scheduler_gpu_allocation_seconds": 1,
        })
        logs = certificate["logs"]
        self.assertEqual(logs["stdout_bytes"], 0)
        self.assertEqual(logs["stdout_sha256"], "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(logs["stderr_bytes"], 127)
        self.assertEqual(logs["stderr_sha256"], "439ddcf58763e070b3c96ce803b56b4a9694761bfda8e14cd5cd2b7078f8ab10")
        self.assertEqual(logs["capture_cannot_check_bytes"], 6321)
        self.assertEqual(logs["capture_cannot_check_sha256"], "83a97ac2e2ff92c241f9824b476969b441aead00ef456820eddc3053bb81648c")
        self.assertEqual(logs["capture_failure_detail_sha256"], "1d733d9de0d4dc259545dc0992b1e1f495e9c82d057339fd58b4e90ab849857e")
        self.assertEqual(logs["capture_failure_relation"], "TRUTHFUL_DOWNSTREAM_CONSEQUENCE_OF_PRE_PYTHON_FAILURE__NOT_PRIMARY_FAILURE")
        execution = certificate["pre_generation_execution"]
        self.assertEqual(execution["python_exec_attempts"], 1)
        self.assertEqual(execution["python_interpreters_started"], 0)
        self.assertEqual(execution["python_invocations"], 0)
        self.assertEqual(execution["runtime_roots_created"], 0)
        self.assertEqual(execution["model_opens"], 0)
        self.assertEqual(execution["server_starts"], 0)
        self.assertEqual(execution["tokenize_requests"], 0)
        self.assertEqual(execution["completion_requests"], 0)
        self.assertEqual(execution["generation_invocations"], 0)
        self.assertEqual(execution["generation_attempts_consumed"], 0)
        self.assertEqual(execution["plan_allocated_accelerator_seconds"], 0)
        retry = certificate["retry_semantics"]
        self.assertEqual(retry["repaired_resubmission_generation_ordinal"], 1)
        self.assertEqual(retry["cumulative_scheduler_gpu_allocation_seconds"], 2)
        self.assertEqual(retry["next_infrastructure_submission_ordinal"], 3)
        self.assertFalse(retry["hidden_second_sample"])
        self.assertFalse(retry["scheduler_cost_erased"])

    def test_42_poll_transients_are_narrow_and_hash_classified(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            evidence = base / "evidence"
            evidence.mkdir()
            self.fixture.create(evidence)
            argv = materialized_argv()
            responses = {
                tuple(argv["post_job_scontrol"]): (evidence / "POST_JOB_SCONTROL_V1.txt").read_bytes(),
                tuple(argv["scheduler_config"]): (evidence / "SCHEDULER_CONFIG_V1.txt").read_bytes(),
                tuple(argv["scheduler_partition"]): (evidence / "SCHEDULER_PARTITION_V1.txt").read_bytes(),
                tuple(argv["scheduler_node"]): (evidence / "SCHEDULER_NODE_V1.txt").read_bytes(),
                tuple(argv["nonoverlap_sacct"]): (evidence / "POST_JOB_SACCT_NONOVERLAP_V1.txt").read_bytes(),
            }

            def run_success(label: str, poll_rows: list[bytes]) -> dict[str, Any]:
                iterator = iter(poll_rows)
                terminal_calls = 0
                poll_ticks = [index * 5_000_000_000 for index in range(len(poll_rows))]
                command_tick = poll_ticks[-1] + 1_000_000_000
                ticks = poll_ticks + [
                    command_tick + index * 1_000_000_000 for index in range(11)
                ]

                def runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                    nonlocal terminal_calls
                    if actual == argv["terminal_sacct"] and terminal_calls < len(poll_rows):
                        terminal_calls += 1
                        return SimpleNamespace(returncode=0, stdout=next(iterator), stderr=b"")
                    return SimpleNamespace(
                        returncode=0, stdout=responses[tuple(actual)], stderr=b""
                    )

                return module.watch_capture_scheduler(
                    JOB_ID, (base / label).resolve(), runner=runner,
                    sleeper=lambda _: None,
                    monotonic_ns=lambda: ticks.pop(0),
                )

            sequence_rows = [
                b"",
                sacct_row(state="PENDING", start="", end="", node="", partition=""),
                sacct_row(state="RUNNING", end="Unknown", partition=""),
                sacct_row(),
            ]
            sequence = run_success("empty-pending-sequence", sequence_rows)
            observations = sequence["terminal_poll_observations"]
            self.assertEqual(
                [item["classification"] for item in observations],
                [
                    "NO_ROW",
                    "PRETERMINAL_EMPTY_PARTITION",
                    "PRETERMINAL_EMPTY_PARTITION",
                    "TERMINAL_COMPLETE_gpua40i",
                ],
            )
            self.assertEqual(
                [item["partition"] for item in observations],
                [None, "", "", PARTITION],
            )
            self.assertEqual(
                [item["state"] for item in observations],
                [None, "PENDING", "RUNNING", "COMPLETED"],
            )
            self.assertEqual(
                [item["raw_sha256"] for item in observations],
                [sha256_bytes(row) for row in sequence_rows],
            )

            terminal_incomplete_rows = [
                sacct_row(partition=""),
                sacct_row(overrides={"End": "Unknown"}),
                sacct_row(
                    overrides={
                        "ExitCode": "",
                        "NodeList": "Unknown",
                        "ReqMem": "Unknown",
                        "Account": "",
                    }
                ),
                sacct_row(),
            ]
            terminal_incomplete = run_success("terminal-incomplete", terminal_incomplete_rows)
            self.assertEqual(
                [item["classification"] for item in terminal_incomplete["terminal_poll_observations"]],
                [
                    "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL",
                    "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL",
                    "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL",
                    "TERMINAL_COMPLETE_gpua40i",
                ],
            )
            self.assertEqual(
                [item["raw_sha256"] for item in terminal_incomplete["terminal_poll_observations"]],
                [sha256_bytes(row) for row in terminal_incomplete_rows],
            )

            expected_sentinel_fields = {
                "Partition", "ExitCode", "DerivedExitCode", "Submit", "Eligible",
                "Start", "End", "TimelimitRaw", "NodeList", "NNodes", "NCPUS",
                "ReqCPUS", "ReqMem", "ReqTRES", "AllocTRES", "Account",
            }
            self.assertEqual(
                set(module.TERMINAL_ACCOUNTING_INCOMPLETE_NORMALIZATION),
                expected_sentinel_fields,
            )
            for field in sorted(expected_sentinel_fields):
                sentinels = ("",) if field == "Partition" else ("", "Unknown")
                for sentinel in sentinels:
                    with self.subTest(field=field, sentinel=sentinel):
                        row = sacct_row(overrides={field: sentinel})
                        record = module.parse_sacct_poll_snapshot(row)
                        self.assertEqual(
                            module.classify_sacct_poll_snapshot(row, record),
                            "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL",
                        )

            for label, row in (
                ("wrong-nonblank", sacct_row(state="PENDING", start="", end="", node="", partition="cpu")),
                ("wrong-terminal-partition", sacct_row(partition="cpu")),
                ("malformed-terminal-nnodes", sacct_row(partition="", overrides={"NNodes": "bogus"})),
                ("terminal-unknown-ntasks", sacct_row(overrides={"NTasks": "Unknown"})),
                ("step-row", sacct_row(job_id=f"{JOB_ID}.batch")),
                ("multiple-rows", sacct_row() + sacct_row()),
                ("wrong-field-count", b"one|short|row\n"),
            ):
                with self.subTest(label=label):
                    target = base / label

                    def hostile_runner(
                        actual: list[str], payload: bytes = row, **kwargs: Any
                    ) -> SimpleNamespace:
                        return SimpleNamespace(returncode=0, stdout=payload, stderr=b"")

                    with self.assertRaises(module.FinalizationError):
                        module.watch_capture_scheduler(
                            JOB_ID, target.resolve(), runner=hostile_runner,
                            sleeper=lambda _: None, monotonic_ns=lambda: 0,
                        )
                    failure = read_json(target / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json")
                    self.assertEqual(
                        failure["failure_code"],
                        "SCHEDULER_CAPTURE_FAILED"
                        if label in {"wrong-nonblank", "wrong-terminal-partition"}
                        else "EVIDENCE_PARSE_INVALID",
                    )
                    rejected = failure["terminal_poll_observations"][-1]
                    self.assertEqual(
                        rejected["classification"],
                        "REJECTED_PARSE" if label in {"step-row", "multiple-rows", "wrong-field-count"}
                        else "REJECTED_PROFILE",
                    )
                    self.assertEqual(rejected["raw_sha256"], sha256_bytes(row))

            exhausted = base / "incomplete-terminal-exhausted"
            incomplete_terminal = sacct_row(overrides={"End": "Unknown"})

            def blank_terminal_runner(actual: list[str], **kwargs: Any) -> SimpleNamespace:
                return SimpleNamespace(returncode=0, stdout=incomplete_terminal, stderr=b"")

            exhausted_ticks = iter([0, 5_000_000_000])
            with (
                mock.patch.object(module, "TERMINAL_POLL_LIMIT", 2),
                self.assertRaises(module.FinalizationError),
            ):
                module.watch_capture_scheduler(
                    JOB_ID, exhausted.resolve(), runner=blank_terminal_runner,
                    sleeper=lambda _: None,
                    monotonic_ns=lambda: next(exhausted_ticks),
                )
            exhausted_receipt = read_json(
                exhausted / "SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json"
            )
            self.assertEqual(
                exhausted_receipt["failure_code"], "SCHEDULER_TERMINAL_TIMEOUT"
            )
            self.assertEqual(
                [item["classification"] for item in exhausted_receipt["terminal_poll_observations"]],
                [
                    "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL",
                    "TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL",
                ],
            )

    def test_43_body_free_manifest_and_checksum_set_bind_every_export(self) -> None:
        manifest = read_json(BODY_FREE_MANIFEST_PATH)
        exported = manifest["exported_files"]
        expected = {
            "DEVELOPMENT_PACKET.md", "FINALIZER_CONTRACT_V3.json",
            "FINALIZER_OUTPUT_SCHEMA_V3.json", "HANDOFF_V1.md",
            "FAILED_JOB_3537828_NO_GENERATION_CERTIFICATE_V1.json",
            "SYNTHETIC_VALIDATION_RECEIPT_V1.json",
            "protected_rr1_one_tuple_finalizer_v3.py",
            "run_protected_rr1_direct_execution_trampoline_v3.sh",
            "validate_protected_rr1_one_tuple_finalizer_v3.py",
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
        self.assertFalse(manifest["live_job_or_protected_outputs_in_export_set"])
        self.assertTrue(
            manifest["privacy_safe_read_only_scheduler_format_exemplars_in_export_set"]
        )
        self.assertEqual(manifest["production_admissibility"], "CANNOT_CHECK")
        checksum_lines = SHA256SUMS_PATH.read_text().splitlines()
        checksums = {
            name: digest
            for digest, name in (line.split("  ", 1) for line in checksum_lines)
        }
        self.assertEqual(set(checksums), expected | {BODY_FREE_MANIFEST_PATH.name})
        for name, digest in checksums.items():
            self.assertEqual(digest, sha256_bytes((ROOT / name).read_bytes()))

    def test_44_synthetic_receipt_binds_core_artifacts_and_nonclaims(self) -> None:
        receipt = read_json(SYNTHETIC_RECEIPT_PATH)
        self.assertEqual(receipt["status"], "PASS_SYNTHETIC_HOSTILE_VALIDATION")
        self.assertEqual(receipt["tests_run"], 46)
        self.assertEqual(receipt["tests_passed"], 46)
        self.assertEqual(receipt["tests_failed"], 0)
        expected_core = {
            "FINALIZER_CONTRACT_V3.json", "FINALIZER_OUTPUT_SCHEMA_V3.json",
            "FAILED_JOB_3537828_NO_GENERATION_CERTIFICATE_V1.json",
            "protected_rr1_one_tuple_finalizer_v3.py",
            "run_protected_rr1_direct_execution_trampoline_v3.sh",
            "validate_protected_rr1_one_tuple_finalizer_v3.py",
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
        self.assertEqual(
            receipt["scheduler_config_dialect_replay"],
            "PASS_REQUIRED_ALLOWLIST_WITH_MISSING_EMPTY_DUPLICATE_AND_CASE_ALIAS_REJECTED__UNRELATED_SLURM_23_11_LINES_TOLERATED",
        )
        self.assertEqual(receipt["failed_job_id"], "3537828")
        self.assertEqual(receipt["prior_scheduler_gpu_allocation_seconds"], 2)
        self.assertEqual(receipt["job_3537828_scheduler_gpu_allocation_seconds"], 1)
        self.assertEqual(receipt["cumulative_scheduler_gpu_allocation_seconds"], 2)
        self.assertEqual(receipt["prior_generation_attempts_consumed"], 0)
        self.assertEqual(receipt["repaired_resubmission_generation_ordinal"], 1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProtectedRR1OneTupleFinalizerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_PROTECTED_RR1_ONE_TUPLE_FINALIZER_V3_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} protected_bodies=0 generation=0 jobs=0 outcomes=0 "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
