#!/usr/bin/env python3
"""Fail-closed focused validator for the full-context replay packet."""

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULT_TERMINAL = (
    "P1_SAB_FULLCONTEXT_REPLAY_COMPLETE__TWO_SEPARATE_CONDITIONS_RETAINED__"
    "ONE_OR_MORE_SCIENTIFICALLY_ADVERSE__NO_COMPOSITE_SCIENTIFIC_WITNESS__"
    "JOB_3534213__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load(path):
    return json.loads(path.read_text())


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def digest_path(path):
    return digest(path.read_bytes())


def verify_manifest(directory):
    manifest = directory / "REMOTE_RUN_SHA256SUMS"
    require(manifest.is_file(), "missing remote manifest")
    for line in manifest.read_text().splitlines():
        expected, relative = line.split(None, 1)
        relative = relative.strip().removeprefix("./")
        path = directory / relative
        require(path.is_file(), "manifest file absent: " + str(path))
        require(digest_path(path) == expected, "manifest hash: " + str(path))


def verify_prompt_token_receipt(directory, expected_count, source_fields):
    receipt = load(directory / "PROMPT_TOKEN_ID_RECEIPT_V1.json")
    require(receipt["prompt_body_retained"] is False, "prompt body retained")
    require(receipt["direct_tokenizer_equality_to_source_is_a_gate"] is False, "route equality gate")
    require(receipt["source_route_token_identities"] == source_fields, "source token identities")
    for name in ("raw_without_special", "effective_with_special"):
        section = receipt[name]
        tokens = section["token_ids"]
        require(len(tokens) == expected_count, name + " token count")
        require(all(isinstance(token, int) for token in tokens), name + " integer tokens")
        require(section["token_count"] == len(tokens), name + " count receipt")
        require(section["token_array_sha256"] == digest(canonical(tokens)), name + " token hash")
    return receipt


def verify_condition(job, name, expect_sensitivity, prompt_count, prompt_sha, prompt_bytes, source_fields):
    directory = job / "results" / name
    receipt = load(directory / "CONDITION_RECEIPT_V1.json")
    verify_prompt_token_receipt(directory, prompt_count, source_fields)
    require(receipt["request_order"] == [101, 202, 101, 202, 101, 202], name + " order")
    require(receipt["cache_prompt"] is False, name + " cache flag")
    require(receipt["prompt"]["sha256"] == prompt_sha, name + " prompt hash")
    require(receipt["prompt"]["bytes"] == prompt_bytes, name + " prompt bytes")
    require(receipt["prompt"]["body_retained"] is False, name + " prompt body")
    require(receipt["prompt"]["direct_tokenizer_equality_to_source_is_a_gate"] is False, name + " route equality")
    require(receipt["prompt_echo_sanitization"]["status"] == "PASS_PROMPT_BODIES_REMOVED_BEFORE_PACKET_RETENTION", name + " sanitization")
    require(receipt["sampling"]["temperature"] == (0.8 if name.startswith("short") else 0.2), name + " temperature")
    require(receipt["sampling"]["n_predict"] == (96 if name.startswith("short") else 128), name + " cap")
    tokens = {101: [], 202: []}
    contents = {101: [], 202: []}
    request_hashes = {101: set(), 202: set()}
    for record in receipt["records"]:
        seed = record["seed"]
        path = directory / ("response_%02d_seed_%d.json" % (record["index"], seed))
        response = load(path)
        require("prompt" not in response, name + " raw prompt echo retained")
        require(response["prompt_receipt"] == {"body_retained": False, "bytes": prompt_bytes, "sha256": prompt_sha}, name + " prompt receipt")
        require(record["retained_sanitized_response_sha256"] == digest_path(path), name + " sanitized hash")
        require(record["prompt_echo_removed"] is True, name + " echo flag")
        generated = response["tokens"]
        content = response["content"]
        require(generated == record["generated_token_ids"], name + " generated IDs")
        require(record["generated_token_array_sha256"] == digest(canonical(generated)), name + " token hash")
        require(record["content_sha256"] == digest(content.encode()), name + " content hash")
        require(response["timings"]["cache_n"] == record["cache_n"], name + " cache_n")
        require(response["timings"]["prompt_n"] == record["prompt_n"], name + " prompt_n")
        require(response["truncated"] is record["truncated"] is False, name + " truncation")
        tokens[seed].append(generated)
        contents[seed].append(content)
        request_hashes[seed].add(record["request_sha256"])
    require(all(len(values) == 1 for values in request_hashes.values()), name + " within-seed request hashes")
    within_tokens = {str(seed): all(x == values[0] for x in values[1:]) for seed, values in tokens.items()}
    within_contents = {str(seed): all(x == values[0] for x in values[1:]) for seed, values in contents.items()}
    between_tokens = tokens[101][0] != tokens[202][0]
    between_contents = contents[101][0] != contents[202][0]
    gates = receipt["gates"]
    require(within_tokens == gates["within_seed_generated_token_identity"] == {"101": True, "202": True}, name + " within tokens")
    require(within_contents == gates["within_seed_content_identity"] == {"101": True, "202": True}, name + " within content")
    require(between_tokens is gates["between_seed_generated_token_sensitivity"] is expect_sensitivity, name + " token sensitivity")
    require(between_contents is gates["between_seed_content_sensitivity"] is expect_sensitivity, name + " content sensitivity")
    require(gates["cache_n_values"] == [0] * 6 and gates["cache_n_all_zero"] is True, name + " cache gate")
    require(gates["prompt_n_values"] == [prompt_count] * 6 and gates["prompt_n_constant"] is True, name + " prompt gate")
    require(gates["truncated_values"] == [False] * 6 and gates["truncated_all_false"] is True, name + " truncation gate")
    require(gates["markers_complete_and_ordered_all_requests"] is True, name + " marker gate")
    return receipt


def main():
    protocol = load(ROOT / "FROZEN_FULLCONTEXT_REPLAY_PROTOCOL_V1.json")
    development = (ROOT / "DEVELOPMENT_PACKET.md").read_text()
    require("does not isolate prompt length,\nprompt content, context, sampling, or cap effects relative to PR #1139" in development, "non-causal comparison boundary")
    require("It isolates prompt" not in development, "causal isolation overclaim")
    require(protocol["request_order"] == [101, 202, 101, 202, 101, 202], "protocol order")
    require(protocol["conditions"]["short_pr1130_replay"]["prompt_sha256"] == "afb432d64085e79f36da380ce0dbc79aa8b5efe221921da06d511480947b4a3b", "short protocol hash")
    require(protocol["conditions"]["long_pr1130_six_marker"]["prompt_sha256"] == "6c52c9055c03367832e9e61c31f49489194cecd94e732fbc7ca59caeb40cf918", "long protocol hash")
    require(protocol["conditions"]["short_pr1130_replay"]["temperature"] == 0.8, "short protocol temp")
    require(protocol["conditions"]["long_pr1130_six_marker"]["temperature"] == 0.2, "long protocol temp")
    require(protocol["server"]["ctx_size"] == 32768 and protocol["server"]["cache_prompt"] is False, "server protocol")
    require(all(protocol["forbidden_inputs"].values()), "protocol forbidden inputs")

    provenance = load(ROOT / "SOURCE_PROMPT_PROVENANCE_V1.json")
    require(provenance["status"] == "PASS_EXACT_PROMPT_BYTES_EXTRACTED_FROM_FIXED_GIT_OBJECTS", "source provenance")
    require(provenance["source_commit"] == "92f078040c9e5248af44ae2e7ec8930124d41ca5", "source commit")
    require(provenance["prompt_bodies_retained_in_this_packet"] is False, "source body boundary")

    failed = ROOT / "remote-job-3534209"
    result = ROOT / "remote-job-3534213"
    verify_manifest(failed)
    verify_manifest(result)
    require("3534209|p1_sab_fullctx_v1|gpua40|lu2026-2-51|normal|cg01|FAILED|00:00:55" in (failed / "SACCT_V1.txt").read_text(), "3534209 sacct")
    require("RuntimeError: short_pr1130_replay: raw prompt-token count" in (failed / "harness.stderr").read_text(), "3534209 precheck")
    failure = load(failed / "JOB_FAILURE_V1.json")
    require(failure["status"] == "FAIL_UNPLANNED_COMMAND", "3534209 postprocess status")
    require("HARNESS_RECEIPT_V1.json" in failure["failed_command"], "3534209 postprocess command")
    require(not any((failed / "results").rglob("*")), "3534209 completion outputs")
    require((failed / "TERMINAL.txt").read_text().strip().endswith("JOB_3534209__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"), "3534209 terminal")

    require("3534213|p1_sab_fullctx_v1|gpua40|lu2026-2-51|normal|cg04|FAILED|00:02:06" in (result / "SACCT_V1.txt").read_text(), "3534213 sacct")
    require((result / "TERMINAL.txt").read_text().strip() == RESULT_TERMINAL, "result terminal")
    job_receipt = load(result / "JOB_RECEIPT_V1.json")
    require(job_receipt["status"] == "COMPLETE_WITH_ONE_OR_MORE_ADVERSE_CONDITIONS", "job status")
    generic_trap = load(result / "JOB_FAILURE_V1.json")
    require(generic_trap["exit_code"] == 2 and "direct_fullcontext_replay_v1.py" in generic_trap["failed_command"], "result generic trap provenance")
    require(job_receipt["harness"]["composition_status"] == "NOT_COMPOSED__NO_COMPOSITE_SCIENTIFIC_WITNESS", "job composition")
    require(job_receipt["runtime"]["model_sha256"] == protocol["model"]["sha256"], "job model")
    require(job_receipt["runtime"]["cuda_backend_sha256"] == protocol["runtime"]["site_cuda_v13_backend_sha256"], "job backend")
    require(all(value is False for value in job_receipt["forbidden_inputs"].values()), "job forbidden inputs")

    short = verify_condition(result, "short_pr1130_replay", True, 35, "afb432d64085e79f36da380ce0dbc79aa8b5efe221921da06d511480947b4a3b", 186, {"source_ollama_context_prefix_token_count": 42, "source_ollama_prompt_eval_count": 43})
    long = verify_condition(result, "long_pr1130_six_marker", False, 27756, "6c52c9055c03367832e9e61c31f49489194cecd94e732fbc7ca59caeb40cf918", 90575, {"source_ollama_prompt_eval_count": 27764})
    require(short["status"] == "PASS_FROZEN_FULLCONTEXT_REPLAY_GATES", "short status")
    require(long["status"] == "ADVERSE_FROZEN_FULLCONTEXT_REPLAY_GATE_FAILURE", "long status")
    require({r["generated_token_array_sha256"] for r in long["records"]} == {"dcbc46bd932fe88f58d183d29a8506dbb51526bceb1458b5335acfeeacdc4cb7"}, "long identical token hash")

    sanitization = load(result / "PROMPT_ECHO_SANITIZATION_V1.json")
    require(sanitization["status"] == "PASS_PROMPT_BODIES_REMOVED_BEFORE_PACKET_RETENTION", "sanitization status")
    require(sanitization["record_count"] == 12 and sanitization["prompt_bodies_retained"] is False, "sanitization count")
    require(sanitization["sanitizer_script_sha256"] == digest_path(ROOT / "sanitize_prompt_echoes_v1.py"), "sanitizer source")

    energy0 = load(failed / "GPU_ENERGY_RECEIPT_V1.json")
    energy1 = load(result / "GPU_ENERGY_RECEIPT_V1.json")
    require(math.isclose(energy0["gpu_seconds_sampled"] + energy1["gpu_seconds_sampled"], 80.87, abs_tol=1e-12), "sampled GPU seconds")
    require(math.isclose(energy0["energy_wh_estimate"] + energy1["energy_wh_estimate"], 5.874718534722224, abs_tol=1e-15), "sampled energy")

    cleanup = load(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json")
    require(cleanup["status"] == "PASS_REMOTE_ROOT_REMOVED" and cleanup["root_exists_after_cleanup"] is False, "cleanup")
    require(cleanup["du_bytes_before_cleanup"] == 18557303002, "cleanup bytes")

    top = load(ROOT / "FULLCONTEXT_REPLAY_RECEIPT_V1.json")
    require(top["status"] == "COMPLETE_MIXED_SHORT_PASS_LONG_ADVERSE", "top status")
    require(top["terminal"] == RESULT_TERMINAL, "top terminal")
    require(top["production_replay_status"] == "BLOCKED", "production block")
    require(top["cleanup_assurance"] == {
        "root_absence_status": "PASS_RETAINED_CLEANUP_RECEIPT",
        "job_absence_status": "CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT",
        "process_absence_status": "CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT",
    }, "cleanup assurance boundary")
    require(top["resources"]["slurm_top_level_gpu_allocation_elapsed_seconds_total"] == 181, "allocated seconds")
    require(top["cost"]["billed_usd"] is None, "billed USD")
    require(all(value is False for value in top["forbidden_inputs"].values()), "top forbidden inputs")
    require(top["prompt_bodies_retained"] is False, "top prompt boundary")
    require(top["artifacts"]["protocol_sha256"] == digest_path(ROOT / "FROZEN_FULLCONTEXT_REPLAY_PROTOCOL_V1.json"), "top protocol hash")
    require(top["artifacts"]["remote_job_3534213_manifest_sha256"] == digest_path(result / "REMOTE_RUN_SHA256SUMS"), "top manifest hash")
    require(top["artifacts"]["cleanup_receipt_sha256"] == digest_path(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json"), "top cleanup hash")

    short_fragment = b"Synthetic replay " + b"probe. Return exactly one compact"
    long_fragment = b"FILLER_0000 " + b"amber cobalt"
    for path in ROOT.rglob("*"):
        if path.is_file():
            raw = path.read_bytes()
            require(short_fragment not in raw, "short prompt body retained: " + str(path))
            require(long_fragment not in raw, "long prompt body retained: " + str(path))
            require(path.stat().st_size < 10_000_000, "large model/prompt artifact retained")
    print(RESULT_TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
