#!/usr/bin/env python3
"""Validate the additive, body-free protected prompt-fit successor V2 lane."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

LANE = Path(__file__).resolve().parent
REPO = LANE.parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DYNAMIC_CANNOT_CHECK = "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED"
STATIC_FIT = "FIT_FROM_BOUND_TOKEN_LEDGER"

EXPECTED_FILES = {
    "BODY_FREE_EXPORT_MANIFEST_V1.json",
    "CLEANUP_V1.json",
    "DEVELOPMENT_PACKET.md",
    "FINALIZATION_RECEIPT_V1.json",
    "HANDOFF_V2.md",
    "INPUT_GATE_RECEIPT_V1.json",
    "PROTECTED_PROMPT_FIT_RECEIPT_V1.json",
    "SACCT_V1.txt",
    "SCHEDULER_RUNTIME_RECEIPT_V2.json",
    "SHA256SUMS",
    "SUCCESSOR_INPUT_BINDINGS_V1.json",
    "SUCCESSOR_JOB_RECEIPT_V1.json",
    "SUCCESSOR_RESULT_V2.json",
    "TERMINAL_V1.txt",
    "TOKENIZATION_RECEIPT_V1.json",
    "TOKEN_LEDGER_AUDIT_AGGREGATE_V2.json",
    "validate_protected_prompt_fit_successor_v2.py",
}

IMPORTED = {
    "INPUT_GATE_RECEIPT_V1.json": {
        "bytes": 2751,
        "sha256": "c9d82fe81dcb468174ee1951cf3622b88d107aa52f7528e6e2997f3498a74534",
    },
    "SUCCESSOR_INPUT_BINDINGS_V1.json": {
        "bytes": 4252,
        "sha256": "14e6964c2894b5c500614da6c305d54429b6a5a70a5ce850833015cee4bebe23",
    },
    "FINALIZATION_RECEIPT_V1.json": {
        "bytes": 2084,
        "sha256": "0a5267edc41ff4b73c2807bf34e74f42d14f82f3f458f41c7bac790cbdf28ba5",
    },
    "TOKENIZATION_RECEIPT_V1.json": {
        "bytes": 1006,
        "sha256": "4330c210cd47bc36496da367e62fa849fcf74890c03b80edb20d2284b0b6af09",
    },
    "CLEANUP_V1.json": {
        "bytes": 343,
        "sha256": "7433906796d11e8f9d0d6431ce57fd55c881800145e99364745b4f8a69512270",
    },
    "PROTECTED_PROMPT_FIT_RECEIPT_V1.json": {
        "bytes": 539479,
        "sha256": "4ff1163b7e405b5881a7d2d4aea10bb634aaf49ada7bfc0c02159a1b5e18fa83",
    },
    "SUCCESSOR_JOB_RECEIPT_V1.json": {
        "bytes": 1884,
        "sha256": "b760fa128fd12174f179c52025c1b84e431719f69edb1f9b8b433cbacc993a11",
    },
    "BODY_FREE_EXPORT_MANIFEST_V1.json": {
        "bytes": 1577,
        "sha256": "ea2de55a77b0d8131a7f0e1814791363c50bfc54d9043ecb380ac3c0726cbb07",
    },
    "SACCT_V1.txt": {
        "bytes": 156,
        "sha256": "5eeb5ae5e933cdea0e9214e8d2c69e0ec65c561c607779635341668a95d6c0b1",
    },
    "TERMINAL_V1.txt": {
        "bytes": 351,
        "sha256": "6a8e694528f0b72369f2b80f759b5362407eec5124664fb19b702fd2c7a4e39f",
    },
}

PUBLIC_UPSTREAMS = {
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json": {
        "bytes": 9665,
        "sha256": "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
    },
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json": {
        "bytes": 5959,
        "sha256": "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
    },
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py": {
        "bytes": 49039,
        "sha256": "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
    },
    "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json": {
        "bytes": 161005,
        "sha256": "442d9793024a91c752d34b9ad3185af612d1db3759458e91a61911b385cbe758",
    },
    "development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/PROTECTED_PROMPT_FIT_CONTRACT_V1.json": {
        "bytes": 8840,
        "sha256": "a2c1dd159f662f019697a3f3a12d7cd06a3d6533258f73d24ed6390a236e51d1",
    },
    "development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/protected_prompt_fit_preflight_v1.py": {
        "bytes": 77033,
        "sha256": "4b605096e3421acd9f826e20864d96eda793f6a9b97879a264d4d8be2acac136",
    },
}

TOKENIZER_AUDIT_UPSTREAMS = {
    "development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/JOB_RECEIPT_V1.json": {
        "bytes": 1324,
        "sha256": "8644d0b02e125e4cdf75ca0ed913a2fbf0e818ebf358a9ace15d7be7fcabfbc4",
    },
    "development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/TOKENIZER_PROBE_V1.json": {
        "bytes": 6844,
        "sha256": "700aabce43e6b834bae4335855149d3b9de7d4b0861cf07e0a49ce9d113020e1",
    },
}

PRIVATE_LEDGER = {
    "bytes": 196220,
    "sha256": "340a51d96f9e39a53c5317fb3999ad28e5918d17af7a6d93381e4a4e7ae7c82d",
}
PRIVATE_TOKEN_ID_AUDIT = {
    "bytes": 4664053,
    "sha256": "04e33ef543e9ba602ed11eaa99145ecd765be883b0efd427c36b30e3d865b5fc",
}
CANONICAL_LEDGER_SHA256 = "93f42c0bdad394a558f61880896e8f68402dd87da00cfa28d4d0c7cfff96aa67"

SACCT = (
    "JobIDRaw|JobName|State|Elapsed|ExitCode|AllocTRES\n"
    "3537617|p1_sab_pf_succ_v1|COMPLETED|00:02:03|0:0|"
    "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1\n"
)
TERMINAL = (
    "P1_SAB_PROTECTED_PROMPT_FIT_SUCCESSOR_V1_COMPLETE job=3537617 "
    "job_receipt_sha256=b760fa128fd12174f179c52025c1b84e431719f69edb1f9b8b433cbacc993a11 "
    "export_manifest_sha256=ea2de55a77b0d8131a7f0e1814791363c50bfc54d9043ecb380ac3c0726cbb07 "
    "generation=0 tasks_executed=0 outcomes_opened=0 dynamic_rr_phase1=CANNOT_CHECK "
    "production_admissibility=CANNOT_CHECK\n"
)

checks = 0


def require(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1
    print(f"P1_SAB_PROTECTED_PROMPT_FIT_SUCCESSOR_V2_PASS: {label}")


def reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def reject_nonfinite(value: str) -> Any:
    raise ValueError(f"non-finite JSON number: {value}")


def load_json(name: str) -> dict[str, Any]:
    value = json.loads(
        (LANE / name).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_members,
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain one JSON object")
    assert_json_finite(value)
    return value


def binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def assert_json_finite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise AssertionError("non-finite JSON value")
    if isinstance(value, dict):
        for item in value.values():
            assert_json_finite(item)
    elif isinstance(value, list):
        for item in value:
            assert_json_finite(item)


def keys_are(value: dict[str, Any], expected: set[str]) -> bool:
    return set(value) == expected


def all_hex64(values: list[Any]) -> bool:
    return all(isinstance(value, str) and HEX64.fullmatch(value) for value in values)


def manifest_checks(path: Path, expected_manifest_sha: str) -> bool:
    if binding(path)["sha256"] != expected_manifest_sha:
        return False
    directory = path.parent
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if match is None:
            return False
        digest, name = match.groups()
        if name in names or not (directory / name).is_file():
            return False
        if binding(directory / name)["sha256"] != digest:
            return False
        names.add(name)
    actual = {item.name for item in directory.iterdir() if item.is_file() and item.name != path.name}
    return names == actual


# Exact lane shape, imported evidence, and merged public dependencies.
actual_files = {item.name for item in LANE.iterdir() if item.is_file()}
require(actual_files == EXPECTED_FILES, "exact additive successor artifact set")
require(all(binding(LANE / name) == expected for name, expected in IMPORTED.items()), "exact imported protected-job artifacts")
require(all(binding(REPO / name) == expected for name, expected in PUBLIC_UPSTREAMS.items()), "exact repaired merged public inputs")
require(all(binding(REPO / name) == expected for name, expected in TOKENIZER_AUDIT_UPSTREAMS.items()), "exact merged tokenizer-capability audit artifacts")

# Preserve all adverse predecessor artifacts, not only its summary JSON.
adverse = REPO / "development/p1-scienceagentbench-protected-prompt-fit-result-v1-2026-08-24"
require(
    manifest_checks(adverse / "SHA256SUMS", "37de79e648b0d2a8a5a84c5811f4cdff950c7c6bd4bc4f893ed17a768edc64f5"),
    "PR 1190 adverse lane remains byte-for-byte unchanged",
)
require(
    binding(adverse / "PROTECTED_PROMPT_FIT_RESULT_V1.json")["sha256"]
    == "2eccca3862e07e2a73e6efd1abf7988e2885a3269f11bd97f6d728f5f5fc1d1c",
    "exact adverse predecessor result retained",
)

# Input and runtime finalization receipts.
gate = load_json("INPUT_GATE_RECEIPT_V1.json")
bindings = load_json("SUCCESSOR_INPUT_BINDINGS_V1.json")
finalization = load_json("FINALIZATION_RECEIPT_V1.json")
require(
    gate.get("status") == "PASS_REPAIR_MERGED_INPUTS_AND_AUDIT_3537594_BOUND"
    and gate.get("counts") == {"authorized_rows": 102, "static_prompts_required": 1224, "tokenize_requests_required": 3672}
    and gate.get("public_files") == PUBLIC_UPSTREAMS,
    "input gate exact repaired inputs and planned counts",
)
require(
    gate.get("repair_merge")
    == {
        "merge_commit": "ee66ee2b6489f7c754ffff219e2ab183c03d6368",
        "origin_main_commit": "3c7dcbce8ae60865c3a79f480efe9858d33ffcc9",
        "pull_request": 1192,
    }
    and gate.get("known_private_inputs", {}).get("tokenizer_audit_job_3537594_receipt")
    == TOKENIZER_AUDIT_UPSTREAMS[next(name for name in TOKENIZER_AUDIT_UPSTREAMS if name.endswith("JOB_RECEIPT_V1.json"))]
    and gate.get("known_private_inputs", {}).get("tokenizer_audit_job_3537594_probe")
    == TOKENIZER_AUDIT_UPSTREAMS[next(name for name in TOKENIZER_AUDIT_UPSTREAMS if name.endswith("TOKENIZER_PROBE_V1.json"))],
    "repair merge and tokenizer-audit hashes bound",
)
require(
    bindings.get("status") == "READY_REPAIR_MERGED_CLEAN_CHECKOUT_BOUND"
    and bindings.get("submission_guard")
    == {
        "clean_checkout": True,
        "merged_validator_tests": 28,
        "owner_released": True,
        "repair_head_merged": True,
        "repair_merge_is_ancestor_of_origin_main": True,
        "slurm_job_submitted": False,
    }
    and bindings.get("planned_counts")
    == {
        "authorized_rows": 102,
        "dynamic_rr_phase1_records": 306,
        "official_outcomes_opened": 0,
        "static_prompts": 1224,
        "tasks_executed": 0,
        "tokenize_requests": 3672,
    },
    "clean-checkout final input bindings",
)
tokenizer_runtime = bindings.get("tokenizer_runtime", {})
require(
    tokenizer_runtime
    == {
        "add_special": True,
        "audit_capability_job_id": "3537594",
        "cuda_backend_sha256": "fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb",
        "host": "127.0.0.1",
        "integer_token_ids_and_count": True,
        "llama_cpp_commit": "7e4c0a96880dae4fc4268ad441f8a6446bd5460a",
        "llama_cpp_version": "b10434",
        "llama_server_sha256": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
        "parse_special": True,
        "prompt_request_response_hashes": True,
        "repeat_count": 3,
        "route": "POST /tokenize",
    },
    "exact llama.cpp tokenizer runtime and true/true three-repeat semantics",
)
require(
    bindings.get("live_model")
    == {
        "bytes": 18556689568,
        "filename": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
        "mode": "0400",
        "sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
    }
    and bindings.get("resource_bound")
    == {"cpus": 8, "gpus": "a40:1", "jobs": 1, "memory": "64G", "nodes": 1, "partition": "gpua40i", "tasks": 1, "walltime": "00:45:00"},
    "exact staged model and one-job resource bound",
)
require(
    finalization.get("status") == "READY_NOT_SUBMITTED"
    and finalization.get("ready_bindings") == IMPORTED["SUCCESSOR_INPUT_BINDINGS_V1.json"]
    and finalization.get("merged_validator", {}).get("tests") == 28
    and finalization.get("public_files") == PUBLIC_UPSTREAMS,
    "pre-submission finalization receipt and 28-test merged validator",
)

# Exact tokenization receipt and private-only artifact bindings.
tokenization = load_json("TOKENIZATION_RECEIPT_V1.json")
require(
    tokenization.get("status") == "PASS_COMPLETE_1224_PROMPT_EXACT_GGUF_LEDGER"
    and tokenization.get("ledger") == {**PRIVATE_LEDGER, "records": 1224}
    and tokenization.get("tokenize_requests") == 3672,
    "exact 1224-record private ledger and 3672 tokenize requests",
)
require(
    tokenization.get("request_semantics")
    == {"add_special": True, "canonical_request_json": True, "parse_special": True, "repeat_count": 3}
    and tokenization.get("prompt_request_response_hashes_retained") is True
    and tokenization.get("integer_token_ids_and_counts_retained_privately") is True,
    "canonical true/true three-repeat tokenization evidence",
)
require(
    tokenization.get("private_token_id_audit")
    == {**PRIVATE_TOKEN_ID_AUDIT, "records": 1224, "retention": "PRIVATE_NON_REPOSITORY_REMOTE_ROOT_ONLY"},
    "exact private 4.6 MB token-ID audit binding",
)

# Production prompt-fit receipt: enforce body-free schemas and recompute every aggregate.
receipt = load_json("PROTECTED_PROMPT_FIT_RECEIPT_V1.json")
require(
    receipt.get("schema_version") == "orion.p1.scienceagentbench.protected-prompt-fit-receipt.v1"
    and receipt.get("authority")
    == "HASH_BYTE_COUNT_AND_TYPED_PREFLIGHT_STATUS_ONLY__NO_BODY_EXECUTION_EVALUATION_OR_SCIENTIFIC_AUTHORITY"
    and receipt.get("mode") == "PROTECTED_OWNER_AUTHORIZED_PREFLIGHT",
    "protected receipt schema and bounded authority",
)
require(
    receipt.get("counts")
    == {
        "authorized_protected_tasks_opened_for_preflight": 102,
        "dynamic_rr_phase1_records": 306,
        "official_outcomes_opened": 0,
        "packet_bodies_retained": 0,
        "prompt_bodies_retained": 0,
        "state_independent_prompt_records": 1224,
        "tasks": 102,
        "tasks_executed": 0,
    },
    "protected receipt exact counts and zero body/task/outcome fields",
)
require(
    receipt.get("tokenizer_measurement")
    == {
        "all_state_independent_prompts_fit": True,
        "dynamic_rr_phase1_status": DYNAMIC_CANNOT_CHECK,
        "ledger_sha256": CANONICAL_LEDGER_SHA256,
        "records": 1224,
        "status": "CHECKED_FROM_BOUND_OWNER_SUPPLIED_EXACT_GGUF_LEDGER",
        "token_counts_independently_remeasured_here": False,
    },
    "canonical ledger hash and typed tokenizer measurement",
)

tasks = receipt.get("task_receipts")
require(isinstance(tasks, list) and len(tasks) == 102, "exactly 102 body-free task receipts")
task_keys = {
    "dynamic_rr_phase1_prompts",
    "instance_id",
    "manifest_binding_sha256",
    "masked_packet_binding",
    "overall_prompt_fit_status",
    "recovered_packet_binding",
    "state_independent_prompts",
    "static_prompt_fit_status",
}
prompt_keys = {
    "arm_id",
    "attempt",
    "context_window_tokens",
    "fit_status",
    "packet_kind",
    "phase_id",
    "phase_output_cap",
    "prompt_bytes",
    "prompt_sha256",
    "prompt_tokens",
    "seed",
}
require(all(isinstance(task, dict) and keys_are(task, task_keys) for task in tasks), "task receipts contain only body-free binding/status members")
require(len({task["instance_id"] for task in tasks}) == 102, "102 unique protected task identifiers")
require(
    all(
        isinstance(task["instance_id"], str)
        and task["instance_id"].isdigit()
        and HEX64.fullmatch(task["manifest_binding_sha256"])
        and keys_are(task["masked_packet_binding"], {"canonical_json_bytes", "canonical_json_sha256"})
        and keys_are(task["recovered_packet_binding"], {"canonical_json_bytes", "canonical_json_sha256"})
        and isinstance(task["masked_packet_binding"]["canonical_json_bytes"], int)
        and isinstance(task["recovered_packet_binding"]["canonical_json_bytes"], int)
        and HEX64.fullmatch(task["masked_packet_binding"]["canonical_json_sha256"])
        and HEX64.fullmatch(task["recovered_packet_binding"]["canonical_json_sha256"])
        for task in tasks
    ),
    "task and packet bodies represented only by byte/hash bindings",
)
require(
    all(
        task["static_prompt_fit_status"] == STATIC_FIT
        and task["overall_prompt_fit_status"] == DYNAMIC_CANNOT_CHECK
        and len(task["state_independent_prompts"]) == 12
        and len(task["dynamic_rr_phase1_prompts"]) == 3
        for task in tasks
    ),
    "all 102 tasks have 12 static FIT records and three dynamic CANNOT_CHECK records",
)

static_rows = [row for task in tasks for row in task["state_independent_prompts"]]
dynamic_rows = [row for task in tasks for row in task["dynamic_rr_phase1_prompts"]]
require(
    all(isinstance(row, dict) and keys_are(row, prompt_keys) for row in static_rows + dynamic_rows),
    "prompt records contain only geometry, hash, and typed-status members",
)
require(
    all(
        row["context_window_tokens"] == 32768
        and isinstance(row["prompt_bytes"], int)
        and row["prompt_bytes"] > 0
        and isinstance(row["prompt_tokens"], int)
        and row["prompt_tokens"] > 0
        and HEX64.fullmatch(row["prompt_sha256"])
        for row in static_rows
    ),
    "all static prompt bodies absent and replaced by positive geometry plus SHA-256",
)
require(
    all(
        row["context_window_tokens"] == 32768
        and row["phase_output_cap"] == 7168
        and row["packet_kind"] == "RECOVERED_PACKET_PLUS_DYNAMIC_RR_PHASE0_STATE"
        and row["prompt_bytes"] is None
        and row["prompt_tokens"] is None
        and row["prompt_sha256"] is None
        for row in dynamic_rows
    ),
    "all dynamic RR prompt geometry remains null pending RR phase-0 state",
)
require(len(static_rows) == 1224 and Counter(row["fit_status"] for row in static_rows) == Counter({STATIC_FIT: 1224}), "1224/1224 state-independent prompts FIT")
require(
    len(dynamic_rows) == 306
    and Counter(row["phase_id"] for row in dynamic_rows) == Counter({"RR_PHASE1": 306})
    and Counter(row["fit_status"] for row in dynamic_rows) == Counter({DYNAMIC_CANNOT_CHECK: 306}),
    "306/306 dynamic RR phase-1 records remain CANNOT_CHECK",
)

expected_phase = {
    "RR_PHASE0": {"records": 306, "minimum": 213, "maximum": 468, "cap": 1024, "packet_kind": "MASKED_PACKET"},
    "OS_PHASE1": {"records": 306, "minimum": 203, "maximum": 21022, "cap": 8192, "packet_kind": "RECOVERED_PACKET"},
    "NR_PHASE0": {"records": 306, "minimum": 213, "maximum": 468, "cap": 1024, "packet_kind": "MASKED_PACKET"},
    "NR_PHASE1": {"records": 306, "minimum": 218, "maximum": 21037, "cap": 7168, "packet_kind": "RECOVERED_PACKET"},
}
phase_ok = True
for phase, expected in expected_phase.items():
    rows = [row for row in static_rows if row["phase_id"] == phase]
    phase_ok &= (
        len(rows) == expected["records"]
        and min(row["prompt_tokens"] for row in rows) == expected["minimum"]
        and max(row["prompt_tokens"] for row in rows) == expected["maximum"]
        and {row["phase_output_cap"] for row in rows} == {expected["cap"]}
        and Counter(row["packet_kind"] for row in rows) == Counter({expected["packet_kind"]: 306})
    )
require(phase_ok, "exact four-phase counts, token ranges, output caps, and packet balance")
occupied = [row["prompt_tokens"] + row["phase_output_cap"] for row in static_rows]
margins = [row["context_window_tokens"] - row["prompt_tokens"] - row["phase_output_cap"] for row in static_rows]
require(max(occupied) == 29214 and min(margins) == 3554, "worst occupied context 29214 and minimum margin 3554")

# Body-free audit aggregate must equal the recomputation above.
aggregate = load_json("TOKEN_LEDGER_AUDIT_AGGREGATE_V2.json")
require(
    aggregate.get("status") == "PASS_ALL_1224_STATE_INDEPENDENT_PROMPTS_FIT"
    and aggregate.get("source_receipt") == {"path": "PROTECTED_PROMPT_FIT_RECEIPT_V1.json", **IMPORTED["PROTECTED_PROMPT_FIT_RECEIPT_V1.json"]},
    "aggregate binds the exact production prompt-fit receipt",
)
measurement = aggregate.get("measurement", {})
require(
    measurement.get("tasks") == 102
    and measurement.get("state_independent_prompt_records") == 1224
    and measurement.get("static_fit_records") == 1224
    and measurement.get("static_not_fit_records") == 0
    and measurement.get("all_state_independent_prompts_fit") is True
    and measurement.get("worst_occupied_context_tokens") == max(occupied)
    and measurement.get("minimum_remaining_context_margin_tokens") == min(margins),
    "aggregate exact static fit and global context geometry",
)
aggregate_phase_ok = True
for phase, expected in expected_phase.items():
    rows = [row for row in static_rows if row["phase_id"] == phase]
    got = measurement.get("phase_summary", {}).get(phase, {})
    aggregate_phase_ok &= got == {
        "fit_records": 306,
        "not_fit_records": 0,
        "occupied_context_tokens": {
            "maximum": max(row["prompt_tokens"] + row["phase_output_cap"] for row in rows),
            "minimum": min(row["prompt_tokens"] + row["phase_output_cap"] for row in rows),
        },
        "phase_output_cap": expected["cap"],
        "prompt_tokens": {"maximum": expected["maximum"], "minimum": expected["minimum"]},
        "records": 306,
        "remaining_context_margin_tokens": {
            "maximum": max(row["context_window_tokens"] - row["prompt_tokens"] - row["phase_output_cap"] for row in rows),
            "minimum": min(row["context_window_tokens"] - row["prompt_tokens"] - row["phase_output_cap"] for row in rows),
        },
    }
require(aggregate_phase_ok, "aggregate phase summaries exactly recomputed")
require(
    aggregate.get("private_ledger_bindings")
    == {
        "canonical_token_ledger_content_sha256": CANONICAL_LEDGER_SHA256,
        "private_token_id_audit": {**PRIVATE_TOKEN_ID_AUDIT, "records": 1224, "retention": "PRIVATE_NON_REPOSITORY_REMOTE_ROOT_ONLY"},
        "raw_exact_gguf_token_ledger_file": {**PRIVATE_LEDGER, "retention": "PRIVATE_NON_REPOSITORY_REMOTE_ROOT_ONLY"},
        "raw_ledger_or_token_id_audit_in_repository": False,
    }
    and aggregate.get("dynamic_rr_phase1")
    == {"all_records_cannot_check": True, "records": 306, "status": DYNAMIC_CANNOT_CHECK, "tasks": 102},
    "aggregate private-artifact bindings and dynamic CANNOT_CHECK boundary",
)
require(
    aggregate.get("tokenizer_semantics")
    == {
        "add_special": True,
        "canonical_request_json": True,
        "host": "127.0.0.1",
        "integer_token_ids_retained_privately": True,
        "parse_special": True,
        "prompt_request_response_hashes_retained": True,
        "repeat_count": 3,
        "repeat_identity": "THREE_BYTE_AND_INTEGER_TOKEN_ID_IDENTICAL_RESPONSES_PER_PROMPT",
        "route": "POST /tokenize",
        "runtime": "llama-server b10434 loopback endpoint",
        "tokenize_requests": 3672,
    },
    "aggregate enforces 3672 true/true byte-and-token-ID-identical repeat tokenizations",
)

# Scheduler evidence and cleanup are exact and singular.
require((LANE / "SACCT_V1.txt").read_text(encoding="utf-8") == SACCT, "exact one-row SACCT evidence")
require((LANE / "TERMINAL_V1.txt").read_text(encoding="utf-8") == TERMINAL, "exact one-line bounded terminal evidence")
job = load_json("SUCCESSOR_JOB_RECEIPT_V1.json")
require(
    job.get("slurm_job_id") == "3537617"
    and job.get("status") == "COMPLETE_BODY_FREE_LEDGER_AND_REPAIRED_PREFLIGHT_RECEIPT_EMITTED"
    and job.get("started_at_utc") == "2026-08-24T18:16:51Z"
    and job.get("finished_at_utc") == "2026-08-24T18:18:35Z",
    "exact protected successor job identity and bounded timestamps",
)
require(
    job.get("counts")
    == {
        "dynamic_rr_phase1": 306,
        "official_outcomes_opened": 0,
        "static_fit": 1224,
        "static_not_fit": 0,
        "static_prompts": 1224,
        "task_prompt_packet_bodies_retained": 0,
        "tasks": 102,
        "tasks_executed": 0,
        "tokenize_requests": 3672,
    }
    and job.get("execution_boundary")
    == {
        "credentials_used": False,
        "evaluator_or_outcome_opened": False,
        "external_api_invoked": False,
        "generation_invoked": False,
        "pytest_or_ci_invoked": False,
    },
    "job exact counts and zero execution/evaluator/API/credential fields",
)
cleanup = load_json("CLEANUP_V1.json")
require(cleanup.get("process_group_absent") is True and cleanup.get("loopback_listener_absent") is True, "process group and loopback listener absent")
runtime = load_json("SCHEDULER_RUNTIME_RECEIPT_V2.json")
require(
    runtime.get("status") == "PASS_EXACTLY_ONE_BOUNDED_A40_JOB_COMPLETED_EXIT_ZERO_AND_CLEANED"
    and runtime.get("job")
    == {
        "alloc_tres": "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1",
        "elapsed": "00:02:03",
        "exit_code": "0:0",
        "finished_at_utc": "2026-08-24T18:18:35Z",
        "job_name": "p1_sab_pf_succ_v1",
        "jobs_in_successor_execution_lane": 1,
        "resources": {"cpus": 8, "gpus": "a40:1", "memory": "64G", "nodes": 1, "partition": "gpua40i", "tasks": 1},
        "slurm_job_id": "3537617",
        "started_at_utc": "2026-08-24T18:16:51Z",
        "state": "COMPLETED",
    },
    "runtime receipt exact one completed A40 job",
)
require(
    runtime.get("public_evidence")
    == {
        "cleanup_receipt": {"path": "CLEANUP_V1.json", **IMPORTED["CLEANUP_V1.json"]},
        "job_receipt": {"path": "SUCCESSOR_JOB_RECEIPT_V1.json", **IMPORTED["SUCCESSOR_JOB_RECEIPT_V1.json"]},
        "sacct": {"path": "SACCT_V1.txt", **IMPORTED["SACCT_V1.txt"], "rows": 1},
        "terminal": {"path": "TERMINAL_V1.txt", **IMPORTED["TERMINAL_V1.txt"], "completion_lines": 1},
    }
    and runtime.get("private_evidence", {}).get("scheduler_stderr")
    == {
        "retention": "PRIVATE_NON_REPOSITORY_REMOTE_ROOT_ONLY",
        "bytes": 112,
        "sha256": "ea3bc2ddcd2e62b4f8b64836ca5650558f11b324858bf8bdeeff35de39a92a00",
    },
    "runtime exact public and private stream bindings",
)

# Export manifest must name private payloads only by binding; neither large payload is in the lane.
export = load_json("BODY_FREE_EXPORT_MANIFEST_V1.json")
require(
    export.get("status") == "PASS_EXPORT_SET_BODY_FREE"
    and export.get("task_prompt_packet_bodies_in_export_set") == 0
    and export.get("integer_token_ids_in_export_set") == 0
    and export.get("official_outcomes_opened") == 0,
    "body-free export manifest zero payload/outcome counts",
)
require(
    export.get("exportable_body_free_artifacts", {}).get("EXACT_GGUF_TOKEN_LEDGER_V1.json") == PRIVATE_LEDGER
    and export.get("private_nonexportable_artifacts", {}).get("PRIVATE_TOKENIZATION_AUDIT_V1.json") == PRIVATE_TOKEN_ID_AUDIT,
    "export manifest distinguishes raw ledger binding from private token-ID audit binding",
)

# Final bounded result and recursive receipt bindings.
result = load_json("SUCCESSOR_RESULT_V2.json")
require(
    result.get("status") == "STATIC_STATE_INDEPENDENT_PROMPT_FIT_ESTABLISHED_DYNAMIC_RR_AND_PRODUCTION_ADMISSIBILITY_CANNOT_CHECK"
    and result.get("predecessor_adverse_result", {}).get("preservation") == "UNCHANGED_ADVERSE_RESULT_RETAINED_NOT_REINTERPRETED"
    and result.get("repair", {}).get("pull_request") == 1192
    and result.get("repair", {}).get("merge_commit") == "ee66ee2b6489f7c754ffff219e2ab183c03d6368",
    "successor result preserves adverse predecessor and binds separate repair",
)
typed = result.get("typed_result", {})
require(
    typed.get("tasks") == 102
    and typed.get("static_state_independent_prompts") == 1224
    and typed.get("static_fit") == 1224
    and typed.get("static_not_fit") == 0
    and typed.get("all_state_independent_prompts_fit") is True
    and typed.get("worst_occupied_context_tokens") == 29214
    and typed.get("minimum_remaining_context_margin_tokens") == 3554
    and typed.get("dynamic_rr_phase1_records") == 306
    and typed.get("dynamic_rr_phase1") == DYNAMIC_CANNOT_CHECK
    and typed.get("production_admissibility") == "CANNOT_CHECK"
    and typed.get("billed_cost_usd") is None
    and typed.get("billed_cost_status") == "CANNOT_CHECK"
    and typed.get("scientific_authority_delta") == "NONE",
    "final typed result exact static success and dynamic/production/cost boundaries",
)
require(
    result.get("phase_token_ranges")
    == {
        phase: {
            "maximum_prompt_tokens": expected["maximum"],
            "minimum_prompt_tokens": expected["minimum"],
            "records": expected["records"],
        }
        for phase, expected in expected_phase.items()
    },
    "final result exact phase token ranges",
)
receipt_bindings = result.get("receipt_bindings", {})
expected_result_bindings = {
    "body_free_export_manifest": IMPORTED["BODY_FREE_EXPORT_MANIFEST_V1.json"],
    "cleanup_receipt": IMPORTED["CLEANUP_V1.json"],
    "finalization_receipt": IMPORTED["FINALIZATION_RECEIPT_V1.json"],
    "input_gate_receipt": IMPORTED["INPUT_GATE_RECEIPT_V1.json"],
    "protected_prompt_fit_receipt": IMPORTED["PROTECTED_PROMPT_FIT_RECEIPT_V1.json"],
    "sacct": IMPORTED["SACCT_V1.txt"],
    "scheduler_runtime_receipt": binding(LANE / "SCHEDULER_RUNTIME_RECEIPT_V2.json"),
    "successor_input_bindings": IMPORTED["SUCCESSOR_INPUT_BINDINGS_V1.json"],
    "successor_job_receipt": IMPORTED["SUCCESSOR_JOB_RECEIPT_V1.json"],
    "terminal": IMPORTED["TERMINAL_V1.txt"],
    "token_ledger_audit_aggregate": binding(LANE / "TOKEN_LEDGER_AUDIT_AGGREGATE_V2.json"),
    "tokenization_receipt": IMPORTED["TOKENIZATION_RECEIPT_V1.json"],
}
require(receipt_bindings == expected_result_bindings, "final result exact recursive receipt bindings")

# Global no-payload and no-authority boundary. Exact schemas above make this stronger than a filename scan.
forbidden_names = {
    "EXACT_GGUF_TOKEN_LEDGER_V1.json",
    "PRIVATE_TOKENIZATION_AUDIT_V1.json",
    "authorized_rows.json",
    "verified.parquet",
}
forbidden_suffixes = {".parquet", ".gguf"}
require(
    not (actual_files & forbidden_names)
    and not any(Path(name).suffix.lower() in forbidden_suffixes for name in actual_files),
    "no raw ledger, token-ID audit, protected rows, Parquet, or GGUF file",
)
for value in [gate, bindings, finalization, tokenization, receipt, aggregate, job, cleanup, runtime, export, result]:
    assert_json_finite(value)
require(
    gate.get("generation_invoked") is False
    and gate.get("evaluator_or_outcome_opened") is False
    and gate.get("external_api_invoked") is False
    and gate.get("credentials_used") is False
    and tokenization.get("generation_invoked") is False
    and tokenization.get("tasks_executed") == 0
    and tokenization.get("evaluator_or_outcome_opened") is False
    and tokenization.get("external_api_invoked") is False
    and tokenization.get("credentials_used") is False
    and cleanup.get("generation_invoked") is False
    and cleanup.get("external_api_invoked") is False,
    "all source receipts retain zero generation/task/evaluator/API/credential authority",
)
result_boundary = result.get("claim_boundary", {})
require(
    result_boundary
    == {
        "credentials_used": False,
        "evaluator_or_outcome_opened": False,
        "external_api_invoked": False,
        "generation_invoked": False,
        "gguf_in_repository": 0,
        "integer_token_id_audit_in_repository": 0,
        "manuscript_or_pdf_changed": False,
        "official_outcomes_opened": 0,
        "production_admissibility": "CANNOT_CHECK",
        "pytest_or_ci_invoked": False,
        "raw_protected_rows_in_repository": 0,
        "raw_token_ledger_in_repository": 0,
        "scientific_authority_delta": "NONE",
        "task_prompt_packet_bodies_in_repository": 0,
        "tasks_executed": 0,
    },
    "final zero-payload/generation/execution/outcome/evaluator/API/credential boundary",
)

print(f"P1_SAB_PROTECTED_PROMPT_FIT_SUCCESSOR_V2_OK checks={checks}")
