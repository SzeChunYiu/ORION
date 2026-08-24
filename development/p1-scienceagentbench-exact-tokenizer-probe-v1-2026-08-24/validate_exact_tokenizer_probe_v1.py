#!/usr/bin/env python3
"""Fail-closed validation for the body-safe exact GGUF tokenizer result lane."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path
from typing import Any


LANE = Path(__file__).resolve().parent
HEX64 = re.compile(r"^[0-9a-f]{64}$")
JOB_ID = "3537594"
TERMINAL = (
    "P1_SAB_EXACT_GGUF_TOKENIZER_PROBE_PASS__JOB_3537594__"
    "NO_GENERATION__NO_PROTECTED_INPUTS__COST_CANNOT_CHECK"
)

EXPECTED_FILES = {
    "CLEANUP_V1.json",
    "DEVELOPMENT_PACKET.md",
    "EXACT_TOKENIZER_RESULT_V1.json",
    "FROZEN_JOB_SCRIPT_V1.slurm",
    "FROZEN_RUNTIME_HASHES.txt",
    "FROZEN_TOKENIZER_GEOMETRY.json",
    "HANDOFF_V1.md",
    "JOB_RECEIPT_V1.json",
    "REMOTE_ARTIFACT_SHA256SUMS",
    "SACCT_V1.txt",
    "SHA256SUMS",
    "SLOTS.json",
    "TERMINAL.txt",
    "TOKENIZER_PROBE_V1.json",
    "validate_exact_tokenizer_probe_v1.py",
}

REMOTE_TO_LOCAL = {
    "job.slurm": "FROZEN_JOB_SCRIPT_V1.slurm",
    "slurm-3537594.out": "TERMINAL.txt",
    "job-3537594/JOB_RECEIPT_V1.json": "JOB_RECEIPT_V1.json",
    "job-3537594/TOKENIZER_PROBE_V1.json": "TOKENIZER_PROBE_V1.json",
    "job-3537594/CLEANUP_V1.json": "CLEANUP_V1.json",
    "job-3537594/FROZEN_RUNTIME_HASHES.txt": "FROZEN_RUNTIME_HASHES.txt",
    "job-3537594/FROZEN_TOKENIZER_GEOMETRY.json": "FROZEN_TOKENIZER_GEOMETRY.json",
    "job-3537594/SLOTS.json": "SLOTS.json",
}

EXPECTED_REMOTE_HASHES = {
    "job.slurm": "cbcfa367b167f5b4f7d6577c0145979fd1bc6b9167e6526772fcc0044fef2f18",
    "slurm-3537594.out": "d0c99330dc84d0f2faa1d7032abb9e12da63d9bd8af38d807ab2f229a935c247",
    "job-3537594/JOB_RECEIPT_V1.json": "8644d0b02e125e4cdf75ca0ed913a2fbf0e818ebf358a9ace15d7be7fcabfbc4",
    "job-3537594/TOKENIZER_PROBE_V1.json": "700aabce43e6b834bae4335855149d3b9de7d4b0861cf07e0a49ce9d113020e1",
    "job-3537594/CLEANUP_V1.json": "2d8843e4849ea16bf729d1872246f4f45458aceb00b0643e050cc0334c812f04",
    "job-3537594/FROZEN_RUNTIME_HASHES.txt": "b3f40f484e08da8999891dbd325bc2c5711b4030d0087e874583e55fd154a87e",
    "job-3537594/FROZEN_TOKENIZER_GEOMETRY.json": "7fd9e36d30b40b5b39a37a8693dfdbfd0a017266b40f6421a8cf375cffe2f549",
    "job-3537594/SLOTS.json": "39cf5a5b0639296f3a75ebe7c2e162bc51b6e239886c5f41430c1869b68d4e6d",
}

EXPECTED_LOCAL_HASHES = {
    local: EXPECTED_REMOTE_HASHES[remote]
    for remote, local in REMOTE_TO_LOCAL.items()
}
EXPECTED_LOCAL_HASHES.update(
    {
        "REMOTE_ARTIFACT_SHA256SUMS": "586e7cb737b82cfcd460cb0adbc4e4f846912e7f4df4685488b009ebdabe48f6",
        "SACCT_V1.txt": "465d9c198439c0b91eb3cd15ea27f8346be74c7c7f566ec6af7c447f857c1099",
    }
)

EXPECTED_PROMPTS = {
    "ascii": "INVENTED_TOKENIZER_PROBE_ALPHA_7f91\n",
    "unicode": "Invented café Δ 中文🙂 line\nsecond invented line.\n",
    "json_like": (
        "ORION invented prompt only. Attempt ordinal: 1. Canonical invented packet JSON follows:\n"
        '{"dataset_preview":null,"domain":"synthetic","instance_id":"SYNTHETIC-1",'
        '"task_inst":"invented"}\n'
    ),
    "literal_special_marker": (
        "Invented literal marker <|im_start|> remains synthetic and opens no task.\n"
    ),
}

EXPECTED_COUNTS = {
    ("ascii", "completion_equivalent"): 14,
    ("ascii", "plain_no_special"): 14,
    ("unicode", "completion_equivalent"): 13,
    ("unicode", "plain_no_special"): 13,
    ("json_like", "completion_equivalent"): 46,
    ("json_like", "plain_no_special"): 46,
    ("literal_special_marker", "completion_equivalent"): 13,
    ("literal_special_marker", "plain_no_special"): 16,
}

RUNTIME = {
    "model_sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
    "llama_server_sha256": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
    "cuda_backend_sha256": "fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb",
    "llama_cpp_version": "b10434",
    "llama_cpp_commit": "7e4c0a96880dae4fc4268ad441f8a6446bd5460a",
}

checks = 0


def require(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1
    print(f"P1_SAB_EXACT_TOKENIZER_RESULT_V1_PASS: {label}")


def reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def reject_nonfinite(value: str) -> Any:
    raise ValueError(f"non-finite JSON number: {value}")


def assert_json_finite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise AssertionError("non-finite JSON value")
    if isinstance(value, dict):
        for item in value.values():
            assert_json_finite(item)
    elif isinstance(value, list):
        for item in value:
            assert_json_finite(item)


def load_json(name: str) -> Any:
    value = json.loads(
        (LANE / name).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_members,
        parse_constant=reject_nonfinite,
    )
    assert_json_finite(value)
    return value


def binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def parse_sha_manifest(name: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in (LANE / name).read_text(encoding="utf-8").splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise AssertionError(f"malformed SHA line in {name}: {line!r}")
        digest, path = parts
        if not HEX64.fullmatch(digest) or not path or path in parsed:
            raise AssertionError(f"invalid or duplicate SHA line in {name}: {line!r}")
        parsed[path] = digest
    return parsed


# Exact additive lane and remote-to-repository integrity bridge.
actual_files = {path.name for path in LANE.iterdir() if path.is_file()}
require(actual_files == EXPECTED_FILES, "exact additive lane artifact set")

for name, digest in EXPECTED_LOCAL_HASHES.items():
    require(binding(LANE / name)["sha256"] == digest, f"exact imported hash: {name}")

remote_hashes = parse_sha_manifest("REMOTE_ARTIFACT_SHA256SUMS")
require(remote_hashes == EXPECTED_REMOTE_HASHES, "exact remote artifact hash manifest")
require(
    all(
        binding(LANE / local)["sha256"] == remote_hashes[remote]
        for remote, local in REMOTE_TO_LOCAL.items()
    ),
    "all remote artifacts map byte-exactly to repository copies",
)

# Exact terminal and completed allocation evidence.
require(
    (LANE / "TERMINAL.txt").read_text(encoding="utf-8") == TERMINAL + "\n",
    "exact one-line SLURM stdout terminal",
)

sacct_text = (LANE / "SACCT_V1.txt").read_text(encoding="utf-8")
sacct_rows = list(csv.DictReader(io.StringIO(sacct_text), delimiter="|"))
require(len(sacct_rows) == 3, "sacct allocation plus batch and extern rows only")
allocation = sacct_rows[0]
require(
    allocation
    == {
        "JobIDRaw": "3537594",
        "JobName": "p1_sab_tok_v1",
        "Account": "lu2026-2-51",
        "Partition": "gpua40i",
        "State": "COMPLETED",
        "ExitCode": "0:0",
        "Elapsed": "00:01:00",
        "Timelimit": "00:20:00",
        "Start": "2026-08-24T19:56:25",
        "End": "2026-08-24T19:57:25",
        "NodeList": "cg14",
        "NNodes": "1",
        "NCPUS": "8",
        "ReqMem": "64G",
        "AllocTRES": "billing=8,cpu=8,gres/gpu:a40=1,gres/gpu=1,mem=64G,node=1",
    },
    "exact completed A40 allocation row",
)
require(
    [row["JobIDRaw"] for row in sacct_rows[1:]] == ["3537594.batch", "3537594.extern"]
    and all(row["State"] == "COMPLETED" and row["ExitCode"] == "0:0" for row in sacct_rows[1:]),
    "completed batch and extern steps",
)

# Frozen job receipt and runtime identity.
job = load_json("JOB_RECEIPT_V1.json")
require(isinstance(job, dict), "job receipt is one JSON object")
require(
    job.get("schema") == "orion.p1.scienceagentbench.exact-gguf-tokenizer-job.v1"
    and job.get("status") == "PASS_EXACT_GGUF_TOKENIZER_CAPABILITY"
    and job.get("slurm_job_id") == JOB_ID,
    "exact job receipt schema, status, and identity",
)
require(
    job.get("safe_tokenize_mode")
    == {
        "add_special": True,
        "parse_special": True,
        "repeatability_check_required": True,
        "route": "POST /tokenize",
    },
    "completion-equivalent tokenizer mode is explicit true,true",
)
require(job.get("runtime") == RUNTIME, "exact frozen runtime bindings in job receipt")
require(
    job.get("tokenizer_probe_sha256") == EXPECTED_LOCAL_HASHES["TOKENIZER_PROBE_V1.json"]
    and job.get("cleanup_sha256") == EXPECTED_LOCAL_HASHES["CLEANUP_V1.json"],
    "job receipt binds exact probe and cleanup receipts",
)
require(
    job.get("production_prompt_token_ledger_capability")
    == "SUPPORTED_WITH_EXACT_FROZEN_GGUF_AND_EXPLICIT_POST_TOKENIZE_MODE"
    and job.get("production_admissibility") == "CANNOT_CHECK"
    and job.get("scientific_authority_delta") == "NONE",
    "capability is bounded from production and scientific authority",
)
require(
    job.get("protected_inputs_opened") is False
    and job.get("generation_invoked") is False
    and job.get("official_outcomes_opened") is False
    and job.get("external_api_invoked") is False
    and job.get("credentials_used") is False,
    "job receipt excludes protected input, generation, outcomes, APIs, and credentials",
)
require(
    job.get("cost")
    == {
        "billed_usd": None,
        "status": "CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE",
    },
    "billed cost remains owner-authoritative CANNOT_CHECK",
)

runtime_text = (LANE / "FROZEN_RUNTIME_HASHES.txt").read_text(encoding="utf-8")
expected_runtime_text = (
    "model_bytes=18556689568\n"
    f"model_sha256={RUNTIME['model_sha256']}\n"
    f"llama_server_sha256={RUNTIME['llama_server_sha256']}\n"
    f"cuda_backend_sha256={RUNTIME['cuda_backend_sha256']}\n"
    f"llama_cpp_version={RUNTIME['llama_cpp_version']}\n"
    f"llama_cpp_commit={RUNTIME['llama_cpp_commit']}\n"
    "llama_server_version=version: 0.1.0-dev (build 1, commit 7e4c0a968)\n"
    "built with GNU 13.3.1 for Linux x86_64\n"
)
require(runtime_text == expected_runtime_text, "exact frozen runtime hash text")

# Probe route, geometry, invented prompts, modes, token arrays, and repeats.
probe = load_json("TOKENIZER_PROBE_V1.json")
require(isinstance(probe, dict), "tokenizer probe is one JSON object")
require(
    probe.get("schema") == "orion.p1.scienceagentbench.exact-gguf-tokenizer-probe.v1"
    and probe.get("status") == "PASS_EXACT_GGUF_TOKENIZE_ROUTE_REPEATABLE",
    "exact tokenizer probe schema and repeatability status",
)
require(
    probe.get("route")
    == {
        "external_api_invoked": False,
        "generation_invoked": False,
        "host": "127.0.0.1",
        "method": "POST",
        "path": "/tokenize",
        "port": 11479,
    },
    "loopback POST tokenize route only",
)
expected_probe_geometry = {
    "cache_prompt": "NOT_APPLICABLE_TOKENIZE_ENDPOINT",
    "context_shift": False,
    "context_tokens": 32768,
    "continuous_batching": False,
    "parallel_slots": 1,
    "server_prompt_cache_used": False,
    "slot_count": 1,
}
require(probe.get("geometry") == expected_probe_geometry, "exact tokenizer geometry")
require(
    probe.get("model_tokenizer_metadata")
    == {"add_bos_token": False, "add_eos_token": False},
    "exact BOS and EOS tokenizer metadata",
)
require(
    probe.get("prompt_bodies_retained") is False
    and probe.get("protected_inputs_opened") is False
    and probe.get("official_tasks_opened") == 0
    and probe.get("generation_invoked") is False
    and probe.get("official_outcomes_opened") == 0
    and probe.get("credentials_used") is False
    and probe.get("production_admissibility") == "CANNOT_CHECK"
    and probe.get("scientific_authority_delta") == "NONE",
    "probe is body-free and has no protected, production, or outcome authority",
)

records = probe.get("records")
require(isinstance(records, list) and len(records) == 12, "eight token records and four mode comparisons")
token_records = [record for record in records if isinstance(record, dict) and "token_ids" in record]
comparison_records = [record for record in records if isinstance(record, dict) and "mode_comparison" in record]
require(len(token_records) == 8 and len(comparison_records) == 4, "exact probe record partition")

by_key: dict[tuple[str, str], dict[str, Any]] = {}
for record in token_records:
    key = (record.get("prompt_label"), record.get("mode"))
    require(key in EXPECTED_COUNTS and key not in by_key, f"recognized unique token record: {key}")
    by_key[key] = record

    text = EXPECTED_PROMPTS[key[0]]
    prompt_bytes = text.encode("utf-8")
    require(
        record.get("prompt_bytes") == len(prompt_bytes)
        and record.get("prompt_sha256") == hashlib.sha256(prompt_bytes).hexdigest(),
        f"invented prompt byte and SHA binding: {key}",
    )

    expected_flags = (
        {"add_special": True, "parse_special": True}
        if key[1] == "completion_equivalent"
        else {"add_special": False, "parse_special": False}
    )
    require(
        record.get("add_special") is expected_flags["add_special"]
        and record.get("parse_special") is expected_flags["parse_special"],
        f"explicit tokenizer flags: {key}",
    )
    request = {
        "content": text,
        "add_special": expected_flags["add_special"],
        "parse_special": expected_flags["parse_special"],
    }
    request_bytes = json.dumps(
        request,
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    require(
        record.get("request_sha256") == hashlib.sha256(request_bytes).hexdigest(),
        f"canonical request SHA binding: {key}",
    )

    token_ids = record.get("token_ids")
    require(
        isinstance(token_ids, list)
        and all(isinstance(item, int) and not isinstance(item, bool) for item in token_ids)
        and record.get("token_count") == len(token_ids) == EXPECTED_COUNTS[key],
        f"integer token IDs and exact count: {key}",
    )
    response_hashes = record.get("response_raw_sha256s")
    require(
        record.get("repeat_count") == 3
        and record.get("repeatable_token_ids") is True
        and isinstance(response_hashes, list)
        and len(response_hashes) == 3
        and len(set(response_hashes)) == 1
        and all(isinstance(item, str) and HEX64.fullmatch(item) for item in response_hashes),
        f"three identical response hashes and repeatability: {key}",
    )

require(set(by_key) == set(EXPECTED_COUNTS), "all expected invented prompt and mode records present")

expected_comparisons = {
    "ascii": True,
    "unicode": True,
    "json_like": True,
    "literal_special_marker": False,
}
actual_comparisons: dict[str, bool] = {}
for record in comparison_records:
    label = record.get("prompt_label")
    require(
        label in expected_comparisons
        and label not in actual_comparisons
        and record.get("mode_comparison") == "completion_equivalent_vs_plain_no_special"
        and record.get("token_arrays_identical") is expected_comparisons[label],
        f"exact mode comparison: {label}",
    )
    actual_comparisons[label] = record["token_arrays_identical"]
require(actual_comparisons == expected_comparisons, "literal special marker is the exact mode discriminator")
require(
    151644 in by_key[("literal_special_marker", "completion_equivalent")]["token_ids"]
    and 151644 not in by_key[("literal_special_marker", "plain_no_special")]["token_ids"],
    "special token ID 151644 appears only in true,true marker probe",
)

geometry = load_json("FROZEN_TOKENIZER_GEOMETRY.json")
require(
    geometry
    == {
        "cache_prompt": "NOT_APPLICABLE_TOKENIZE_ENDPOINT",
        "context_shift": False,
        "context_tokens": 32768,
        "continuous_batching": False,
        "host": "127.0.0.1",
        "parallel_slots": 1,
        "port": 11479,
        "route": "POST /tokenize",
        "server_prompt_cache_used": False,
    },
    "exact frozen tokenizer geometry file",
)
slots = load_json("SLOTS.json")
require(
    slots == [{"id": 0, "n_ctx": 32768, "speculative": False, "is_processing": False}],
    "one idle non-speculative 32768-token slot",
)

# Cleanup and exact frozen job script boundaries.
cleanup = load_json("CLEANUP_V1.json")
require(
    cleanup
    == {
        "loopback_listener_absent": True,
        "process_group_absent": True,
        "production_admissibility": "CANNOT_CHECK",
        "schema": "orion.p1.scienceagentbench.exact-gguf-tokenizer-cleanup.v1",
        "scientific_authority_delta": "NONE",
        "status": "PASS_PROCESS_GROUP_AND_LISTENER_ABSENT",
    },
    "exact process-group and listener cleanup receipt",
)

job_script = (LANE / "FROZEN_JOB_SCRIPT_V1.slurm").read_text(encoding="utf-8")
require(
    "#SBATCH --account=lu2026-2-51" in job_script
    and "#SBATCH --partition=gpua40i" in job_script
    and "#SBATCH --gres=gpu:a40:1" in job_script
    and "#SBATCH --time=00:20:00" in job_script,
    "bounded A40 job directives",
)
require(
    'request("POST","/tokenize",request_obj)' in job_script
    and 'HTTPConnection(host,port' in job_script
    and "HOST=127.0.0.1" in job_script
    and '"generation_invoked":False' in job_script,
    "frozen script invokes loopback tokenize and records no generation",
)
require(
    "/completion" not in job_script
    and "/v1/chat/completions" not in job_script
    and "/v1/completions" not in job_script,
    "frozen script contains no generation endpoint",
)
require(
    all(text.replace("\n", "\\n")[:18] in job_script or text.splitlines()[0] in job_script for text in EXPECTED_PROMPTS.values())
    and "protected_inputs_opened\":False" in job_script
    and "official_tasks_opened\":0" in job_script,
    "frozen script contains only the bound invented probes and zero protected tasks",
)
require(
    "setsid env -i" in job_script
    and "unset HF_TOKEN" in job_script
    and "external_api_invoked\":False" in job_script
    and (
        "P1_SAB_EXACT_GGUF_TOKENIZER_PROBE_PASS__JOB_${SLURM_JOB_ID}__"
        "NO_GENERATION__NO_PROTECTED_INPUTS__COST_CANNOT_CHECK"
    )
    in job_script,
    "scrubbed environment, no external API, and terminal template in frozen script",
)

# Derived typed result must narrow the remote capability rather than promote it.
result = load_json("EXACT_TOKENIZER_RESULT_V1.json")
require(isinstance(result, dict), "derived result is one JSON object")
require(
    result.get("schema") == "orion.p1.scienceagentbench.exact-gguf-tokenizer-result.v1"
    and result.get("status")
    == "PASS_EXACT_FROZEN_GGUF_TOKENIZER_ROUTE_REPEATABILITY_ON_INVENTED_PROMPTS",
    "derived result is route-repeatability PASS only",
)
require(
    result.get("required_completion_equivalent_mode") == job["safe_tokenize_mode"],
    "derived result preserves mandatory true,true mode",
)
require(
    result.get("claim_boundary")
    == {
        "benchmark_or_outcome_claim": "NONE",
        "established": "POST_TOKENIZE_RETURNS_REPEATABLE_EXACT_TOKEN_IDS_FOR_FOUR_INVENTED_PROMPTS_UNDER_FROZEN_RUNTIME_AND_EXPLICIT_MODE",
        "generation_correctness": "CANNOT_CHECK_NOT_INVOKED",
        "production_admissibility": "CANNOT_CHECK",
        "protected_prompt_fit": "CANNOT_CHECK_NO_PROTECTED_PROMPT_OPENED_OR_TOKENIZED",
        "scientific_authority_delta": "NONE",
    },
    "derived result explicitly denies protected-fit and production promotion",
)
require(
    result.get("probe_counts")
    == {
        "credentials_used": 0,
        "explicit_modes": 2,
        "external_api_invocations": 0,
        "generation_invocations": 0,
        "invented_prompts": 4,
        "official_outcomes_opened": 0,
        "official_tasks_opened": 0,
        "protected_inputs_opened": 0,
        "repeatable_records": 8,
        "repeats_per_record": 3,
        "token_records": 8,
    },
    "derived result exact zero-authority and repeatability counts",
)
require(
    result.get("mode_discriminator")
    == {
        "completion_equivalent_token_count": 13,
        "plain_no_special_token_count": 16,
        "prompt_label": "literal_special_marker",
        "special_token_id_observed_in_completion_equivalent_mode": 151644,
        "token_arrays_identical": False,
    },
    "derived result exact literal-marker discriminator",
)
expected_job_summary = {
    "account": "lu2026-2-51",
    "bounded_slurm_jobs_used": 1,
    "elapsed": "00:01:00",
    "exact_terminal": TERMINAL,
    "exit_code": "0:0",
    "gpu": "a40:1",
    "partition": "gpua40i",
    "slurm_job_id": JOB_ID,
    "state": "COMPLETED",
    "time_limit": "00:20:00",
}
require(result.get("job") == expected_job_summary, "derived result exact job and terminal binding")

bound_names = {
    "CLEANUP_V1.json",
    "FROZEN_JOB_SCRIPT_V1.slurm",
    "FROZEN_RUNTIME_HASHES.txt",
    "FROZEN_TOKENIZER_GEOMETRY.json",
    "JOB_RECEIPT_V1.json",
    "REMOTE_ARTIFACT_SHA256SUMS",
    "SACCT_V1.txt",
    "SLOTS.json",
    "TERMINAL.txt",
    "TOKENIZER_PROBE_V1.json",
}
require(
    result.get("artifact_bindings") == {name: binding(LANE / name) for name in sorted(bound_names)},
    "derived result byte and SHA bindings for all evidence",
)
require(
    result.get("retention")
    == {
        "credentials": "ABSENT",
        "generated_completions": "ABSENT",
        "invented_prompt_bodies": "FROZEN_JOB_SCRIPT_ONLY",
        "model_or_runtime_binary": "ABSENT_HASH_BINDINGS_ONLY",
        "protected_prompt_or_task_bodies": "ABSENT",
        "server_log": "EXCLUDED_AS_UNNECESSARY_FOR_PASS_VERIFICATION",
    },
    "body-safe retention and explicit server-log exclusion",
)
require(result.get("cost") == job["cost"], "derived result preserves cost CANNOT_CHECK")

# Lane SHA manifest is complete and self-excluding.
manifest = parse_sha_manifest("SHA256SUMS")
require(set(manifest) == EXPECTED_FILES - {"SHA256SUMS"}, "SHA manifest covers every non-manifest lane file")
for name, expected in manifest.items():
    require(binding(LANE / name)["sha256"] == expected, f"SHA manifest entry: {name}")

print(
    "P1_SAB_EXACT_TOKENIZER_RESULT_V1_VALIDATION_PASS__"
    f"CHECKS_{checks}__JOB_3537594__TRUE_TRUE_MODE_REQUIRED__"
    "INVENTED_ONLY__PROTECTED_FIT_AND_PRODUCTION_CANNOT_CHECK"
)
