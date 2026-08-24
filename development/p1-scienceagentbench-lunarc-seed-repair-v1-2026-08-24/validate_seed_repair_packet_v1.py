#!/usr/bin/env python3
"""Fail-closed focused validator for the bounded direct-seed repair packet."""

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TERMINAL = (
    "P1_SAB_DIRECT_SEED_REPAIR_PASS__CACHE_OFF_WITHIN_SEED_TOKEN_IDENTITY__"
    "BETWEEN_SEED_SENSITIVITY__CACHE_N_ZERO__PROMPT_N_CONSTANT__JOB_3534123__"
    "COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load(path):
    return json.loads(path.read_text())


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_path(path):
    return digest_bytes(path.read_bytes())


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def verify_remote_manifest(directory, manifest_name):
    manifest = directory / manifest_name
    require(manifest.is_file(), "missing " + str(manifest))
    for line in manifest.read_text().splitlines():
        expected, relative = line.split(None, 1)
        relative = relative.strip()
        if relative.startswith("./"):
            relative = relative[2:]
        path = directory / relative
        require(path.is_file(), "manifest file missing: " + str(path))
        require(digest_path(path) == expected, "manifest hash mismatch: " + str(path))


def verify_source_canonicalization():
    source_dir = ROOT / "source-pr1130"
    receipt = load(ROOT / "SOURCE_CANONICALIZATION_V1.json")
    require(receipt["status"] == "CONFIRMED_CONTENT_AND_GENERATED_TOKEN_ARRAY_DIVERGENCE", "source status")
    require(receipt["source_pr"] == 1130, "source PR")
    require(receipt["source_commit"] == "8c1f5c88bda5da7dc192c40dc92698c19fbb57ba", "source commit")
    requests = []
    responses = []
    volatile = set(receipt["comparison"]["canonical_response_fields_excluded"])
    require(volatile == {"created_at", "total_duration", "load_duration", "prompt_eval_duration", "eval_duration"}, "volatile field set")
    for record in receipt["records"]:
        name = record["name"]
        request_raw = (source_dir / (name + ".request.json")).read_bytes()
        response_raw = (source_dir / (name + ".response.json")).read_bytes()
        request = json.loads(request_raw)
        response = json.loads(response_raw)
        context = response["context"]
        generated = context[-response["eval_count"]:]
        prompt = context[:-response["eval_count"]]
        canonical = {key: value for key, value in response.items() if key not in volatile}
        require(digest_bytes(request_raw) == record["request_raw_sha256"], "source request hash")
        require(digest_bytes(response_raw) == record["response_raw_sha256"], "source response hash")
        require(digest_bytes(canonical_bytes(canonical)) == record["canonical_response_sha256"], "source canonical hash")
        require(digest_bytes(response["response"].encode()) == record["response_text_sha256"], "source content hash")
        require(digest_bytes(canonical_bytes(context)) == record["context_token_array_sha256"], "source context hash")
        require(digest_bytes(canonical_bytes(generated)) == record["generated_token_array_sha256"], "source generated hash")
        requests.append((request_raw, request))
        responses.append((response, prompt, generated))
    require(requests[0][0] == requests[1][0], "source request bytes must match")
    require(requests[0][1] == requests[1][1], "source request JSON must match")
    require(responses[0][0]["response"] != responses[1][0]["response"], "source content must differ")
    require(responses[0][1] == responses[1][1] and len(responses[0][1]) == 42, "source prompt prefix")
    require(responses[0][2] != responses[1][2], "source generated arrays must differ")
    first = next(i for i, pair in enumerate(zip(responses[0][2], responses[1][2])) if pair[0] != pair[1])
    require(first == 16, "source first generated-token difference")
    return receipt


def verify_condition(job_dir, name, cache_prompt, expected_cache, expected_prompt):
    directory = job_dir / name
    receipt = load(directory / "CONDITION_RECEIPT_V1.json")
    require(receipt["request_order"] == [101, 202, 101, 202, 101, 202], name + " order")
    require(receipt["cache_prompt"] is cache_prompt, name + " cache flag")
    tokens = {101: [], 202: []}
    contents = {101: [], 202: []}
    request_hashes = {101: set(), 202: set()}
    raw_response_hashes = {101: set(), 202: set()}
    observed_cache = []
    observed_prompt = []
    for index, seed in enumerate(receipt["request_order"], 1):
        request_path = directory / ("request_%02d_seed_%d.json" % (index, seed))
        response_path = directory / ("response_%02d_seed_%d.json" % (index, seed))
        request_raw = request_path.read_bytes()
        response_raw = response_path.read_bytes()
        request = json.loads(request_raw)
        response = json.loads(response_raw)
        record = receipt["records"][index - 1]
        require(request["seed"] == seed and request["cache_prompt"] is cache_prompt, name + " request identity")
        require(request["temperature"] == 0.2 and request["return_tokens"] is True, name + " sampling")
        require(request["stream"] is False and request["n_predict"] == 128, name + " response contract")
        require(record["request_sha256"] == digest_path(request_path), name + " request hash")
        require(record["response_raw_sha256"] == digest_path(response_path), name + " response hash")
        require(record["token_array_sha256"] == digest_bytes(canonical_bytes(response["tokens"])), name + " token hash")
        require(record["content_sha256"] == digest_bytes(response["content"].encode()), name + " content hash")
        require(response["timings"]["cache_n"] == record["cache_n"], name + " cache timing")
        require(response["timings"]["prompt_n"] == record["prompt_n"], name + " prompt timing")
        require(all(isinstance(token, int) for token in response["tokens"]), name + " raw token ids")
        tokens[seed].append(response["tokens"])
        contents[seed].append(response["content"])
        request_hashes[seed].add(digest_path(request_path))
        raw_response_hashes[seed].add(digest_path(response_path))
        observed_cache.append(record["cache_n"])
        observed_prompt.append(record["prompt_n"])
    require(observed_cache == expected_cache, name + " cache_n sequence")
    require(observed_prompt == expected_prompt, name + " prompt_n sequence")
    require(all(len(values) == 1 for values in request_hashes.values()), name + " requests within seed")
    require(all(len(values) > 1 for values in raw_response_hashes.values()), name + " raw responses retain volatile differences")
    require(receipt["gates"]["cache_n_values"] == expected_cache, name + " receipt cache_n")
    require(receipt["gates"]["prompt_n_values"] == expected_prompt, name + " receipt prompt_n")
    computed_token_identity = {
        str(seed): all(item == values[0] for item in values[1:])
        for seed, values in tokens.items()
    }
    computed_content_identity = {
        str(seed): all(item == values[0] for item in values[1:])
        for seed, values in contents.items()
    }
    require(computed_token_identity == receipt["gates"]["within_seed_token_array_identity"], name + " token identity")
    require(computed_content_identity == receipt["gates"]["within_seed_content_identity"], name + " content identity")
    require((tokens[101][0] != tokens[202][0]) == receipt["gates"]["between_seed_token_array_sensitivity"], name + " sensitivity")
    return receipt


def main():
    source = verify_source_canonicalization()
    require((ROOT / "OLLAMA_V0.32.14_LLAMA_CPP_VERSION.txt").read_text() == "b10434\n", "llama.cpp version file")
    runtime = load(ROOT / "RUNTIME_SOURCE_PIN_V1.json")
    require(runtime["ollama_github_tag_commit"] == "d67ad83426633195089509347ffd4fe795120198", "Ollama tag")
    require(runtime["llama_cpp_version"] == "b10434", "llama.cpp tag")
    require(runtime["llama_cpp_tag_commit"] == "7e4c0a96880dae4fc4268ad441f8a6446bd5460a", "llama.cpp commit")
    require(runtime["site_llama_server_executable_sha256"] == "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b", "server pin")
    require(runtime["site_cuda_v13_backend_sha256"] == "fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb", "CUDA backend pin")

    cancelled = ROOT / "remote-job-3534108"
    result = ROOT / "remote-job-3534123"
    verify_remote_manifest(cancelled, "REMOTE_PARTIAL_SHA256SUMS")
    verify_remote_manifest(result, "REMOTE_RUN_SHA256SUMS")
    require("3534108|p1_sab_seed_v1|gpua40i|cg15|CANCELLED by 6350|00:02:29|0:0|" in (cancelled / "SACCT_V1.txt").read_text(), "cancelled sacct")
    require("3534108.batch|batch||cg15|CANCELLED|00:03:00|0:9|" in (cancelled / "SACCT_V1.txt").read_text(), "cancelled batch sacct")
    require("warning: no usable GPU found, --gpu-layers option will be ignored" in (cancelled / "server-primary_cache_off.log").read_text(), "cancelled CPU fallback warning")
    require(load(cancelled / "primary_cache_off/CONDITION_RECEIPT_V1.json")["status"] == "PASS_CACHE_OFF_DETERMINISTIC_AND_SEED_SENSITIVE", "partial CPU receipt retained")
    cancelled_energy = load(cancelled / "GPU_ENERGY_RECEIPT_POSTHOC_V1.json")
    require(cancelled_energy["billed_usd"] is None and cancelled_energy["max_memory_used_mib"] == 1255.0, "cancelled telemetry")

    require("3534123|p1_sab_seed_v1|gpua40i|cg15|COMPLETED|00:01:03|0:0|" in (result / "SACCT_V1.txt").read_text(), "result sacct")
    job = load(result / "JOB_RECEIPT_V1.json")
    require(job["status"] == "PASS_PRIMARY_CACHE_OFF_DETERMINISTIC_AND_SEED_SENSITIVE", "result job status")
    require(job["slurm_job_id"] == "3534123", "result job id")
    require(job["runtime"]["llama_cpp_version"] == "b10434", "job runtime")
    require(job["runtime"]["cuda_backend_sha256"] == runtime["site_cuda_v13_backend_sha256"], "job CUDA binding")
    require(job["condition_order"] == ["primary_cache_off", "negative_control_cache_on"], "condition order")
    require(job["gpu_telemetry"]["gpu_name"] == "NVIDIA A40", "result GPU")
    require(job["gpu_telemetry"]["max_memory_used_mib"] == 19581.0, "result VRAM")
    require(job["gpu_telemetry"]["max_utilization_gpu_percent"] == 100.0, "result utilization")
    require(job["cost"]["billed_usd"] is None, "job billed cost")
    require(all(value is False for value in job["forbidden_inputs"].values()), "job forbidden inputs")

    primary = verify_condition(result, "primary_cache_off", False, [0, 0, 0, 0, 0, 0], [70, 70, 70, 70, 70, 70])
    require(primary["status"] == "PASS_CACHE_OFF_DETERMINISTIC_AND_SEED_SENSITIVE", "primary status")
    require(primary["gates"]["within_seed_token_array_identity"] == {"101": True, "202": True}, "primary replay")
    require(primary["gates"]["within_seed_content_identity"] == {"101": True, "202": True}, "primary content replay")
    require(primary["gates"]["between_seed_token_array_sensitivity"] is True, "primary sensitivity")
    require(primary["records"][0]["token_array_sha256"] == "35ea602a3d475ac1a522d066969b89c26532b5f2504e0409e805ad9153f75659", "seed 101 token hash")
    require(primary["records"][1]["token_array_sha256"] == "10fa4f4e19f20c3a957b25bd572f293a35227972f59901656701d6f901791e8f", "seed 202 token hash")

    negative = verify_condition(result, "negative_control_cache_on", True, [0, 69, 69, 69, 69, 69], [70, 1, 1, 1, 1, 1])
    require(negative["status"] == "OBSERVED_CACHE_ON_NEGATIVE_CONTROL", "negative status")
    require(negative["gates"]["within_seed_token_array_identity"] == {"101": False, "202": True}, "negative replay pattern")
    require(not (result / "diagnostic_cublas_workspace").exists(), "CUBLAS diagnostic must not run after primary pass")
    require(not (result / "diagnostic_flash_attn_off").exists(), "flash-off diagnostic must not run after primary pass")

    require((result / "TERMINAL.txt").read_text().strip() == TERMINAL, "terminal file")
    handoff = (ROOT / "HANDOFF_V1.md").read_text()
    require(TERMINAL in handoff, "handoff terminal")
    cleanup = load(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json")
    require(cleanup["status"] == "PASS_REMOTE_ROOT_REMOVED", "cleanup status")
    require(cleanup["root_exists_after_cleanup"] is False, "cleanup postcondition")
    require(cleanup["du_bytes_before_cleanup"] == 18556938228, "cleanup bytes")

    top = load(ROOT / "DIRECT_SEED_REPAIR_RECEIPT_V1.json")
    require(top["status"] == "PASS_BOUNDED_DIRECT_COMPLETION_CACHE_OFF_SEED_REPAIR", "top status")
    require(top["terminal"] == TERMINAL, "top terminal")
    require(top["source_adverse_evidence"]["canonicalization_status"] == source["status"], "top source")
    require(top["jobs"]["3534108"]["state"] == "CANCELLED by 6350", "top cancelled job")
    require(top["jobs"]["3534123"]["state"] == "COMPLETED", "top result job")
    require(top["primary_cache_off"]["cache_n_values"] == [0] * 6, "top primary cache")
    require(top["negative_control_cache_on"]["cache_n_values"] == [0, 69, 69, 69, 69, 69], "top negative cache")
    require(top["diagnostics"]["cublas_workspace_config"] == "NOT_RUN_PRIMARY_CACHE_OFF_PASSED", "top CUBLAS diagnostic")
    require(top["diagnostics"]["flash_attention_off"] == "NOT_RUN_PRIMARY_CACHE_OFF_PASSED", "top flash diagnostic")
    require(top["cost"]["billed_usd"] is None, "top billed USD")
    require(top["cost"]["status"] == "CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE", "top cost status")
    require(all(value is False for value in top["forbidden_inputs"].values()), "top forbidden inputs")
    require(top["scientific_authority_delta"] == "NONE", "top authority")
    require(top["resources"]["slurm_top_level_gpu_allocation_elapsed_seconds_total"] == 212, "top resource seconds")
    require(top["resources"]["slurm_batch_elapsed_seconds_total"] == 243, "batch seconds")
    require(math.isclose(top["resources"]["sample_integrated_energy_wh_total"], 1.2592378833333315, rel_tol=0, abs_tol=1e-15), "energy total")
    require(top["artifacts"]["source_canonicalization_sha256"] == digest_path(ROOT / "SOURCE_CANONICALIZATION_V1.json"), "top source hash")
    require(top["artifacts"]["remote_job_3534108_manifest_sha256"] == digest_path(cancelled / "REMOTE_PARTIAL_SHA256SUMS"), "top cancelled manifest")
    require(top["artifacts"]["remote_job_3534123_manifest_sha256"] == digest_path(result / "REMOTE_RUN_SHA256SUMS"), "top result manifest")
    require(top["artifacts"]["cleanup_receipt_sha256"] == digest_path(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json"), "top cleanup hash")
    require(max(path.stat().st_size for path in ROOT.rglob("*") if path.is_file()) < 10_000_000, "large model bytes must not be retained")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

