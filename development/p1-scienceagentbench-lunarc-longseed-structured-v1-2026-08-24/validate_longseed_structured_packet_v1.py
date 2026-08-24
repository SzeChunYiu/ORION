#!/usr/bin/env python3
"""Fail-closed focused validator for the long-seed structured packet."""

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JOB = ROOT / "remote-job-3534486"
TERMINAL = (
    "P1_SAB_LONGSEED_STRUCTURED_PASS__STRICT_RAW_JSON_EXACT_SCHEMA__"
    "WITHIN_SEED_TOKEN_CONTENT_IDENTITY__BETWEEN_SEED_SENSITIVITY__"
    "CACHE_N_ZERO__PROMPT_N_27855__NO_TRUNCATION__NONCOMPOSABLE__"
    "JOB_3534486__PRODUCTION_BLOCKED__COST_CANNOT_CHECK"
)
MARKERS = [
    "MK0_7b91c2",
    "MK1_a46fd8",
    "MK2_19e3ab",
    "MK3_c58071",
    "MK4_ef268d",
    "MK5_34da90",
]
ALLOWED = {"amber", "cobalt", "delta", "ember", "fjord", "glyph", "harbor", "iris"}


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


def verify_packet_manifest():
    manifest = ROOT / "SHA256SUMS"
    observed = {}
    for line in manifest.read_text().splitlines():
        expected, relative = line.split(None, 1)
        require(relative not in observed, "duplicate packet manifest path")
        observed[relative] = expected
    expected_paths = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name != "SHA256SUMS"
        and "__pycache__" not in path.parts
    }
    require(set(observed) == expected_paths, "packet manifest coverage")
    for relative, expected in observed.items():
        require(digest_path(ROOT / relative) == expected, "packet manifest hash: " + relative)


def verify_manifest():
    paths = set()
    for line in (JOB / "REMOTE_RUN_SHA256SUMS").read_text().splitlines():
        expected, relative = line.split(None, 1)
        relative = relative.strip().removeprefix("./")
        paths.add(relative)
        path = JOB / relative
        require(path.is_file(), "manifest file absent: " + str(path))
        require(digest_path(path) == expected, "manifest hash: " + str(path))
    return paths


def main():
    remote_manifest_paths = verify_manifest()
    require("SACCT_V1.txt" not in remote_manifest_paths, "structured runtime-stage manifest scope")
    attributes = (
        "remote-job-3534486/ENVIRONMENT.txt -whitespace\n"
        "remote-job-3534486/NVIDIA_SMI_AFTER.txt -whitespace\n"
    )
    require((ROOT / ".gitattributes").read_text() == attributes, "scoped raw receipt attributes")
    environment = JOB / "ENVIRONMENT.txt"
    nvidia_after = JOB / "NVIDIA_SMI_AFTER.txt"
    require(digest_path(environment) == "80d466c3f71fa4af917fca23f4fd42b30dc89c91b2fdec2063e1234666745d6e", "environment raw hash")
    require(environment.read_bytes().splitlines(keepends=True)[14] == b"Mon Aug 24 16:30:41 2026       \n", "environment raw whitespace")
    require(digest_path(nvidia_after) == "e27eab544d373be578785aeb8ab3ba4280fc2c32e391c753596847666ad3f41d", "nvidia raw hash")
    require(nvidia_after.read_bytes().splitlines(keepends=True)[0] == b"Mon Aug 24 16:32:06 2026       \n", "nvidia raw whitespace")
    verify_packet_manifest()
    protocol = load(ROOT / "FROZEN_LONGSEED_STRUCTURED_PROTOCOL_V1.json")
    require(protocol["prior_condition"]["job"] == "3534250", "prior job")
    require(protocol["prior_condition"]["status_changed_or_promoted"] is False, "prior promotion")
    require(protocol["prior_condition"]["only_changed_request_field_set"] == ["json_schema"], "only change")
    require(protocol["request_order"] == [101, 202, 101, 202, 101, 202], "order")
    require(protocol["sampling"]["temperature"] == 0.8 and protocol["sampling"]["n_predict"] == 128, "sampling")
    require(protocol["server"]["ctx_size"] == 32768 and protocol["server"]["cache_prompt"] is False, "server")
    require(all(protocol["forbidden_inputs"].values()), "forbidden inputs")

    schema_path = ROOT / "FROZEN_OUTPUT_SCHEMA_V1.json"
    schema = load(schema_path)
    require(schema_path.stat().st_size == 646, "schema bytes")
    require(digest_path(schema_path) == "7b9ffda6c9daa1f39a1350959590112c5c663c6373a81e1e3fbffa23f0649498", "schema hash")
    require(schema["required"] == ["markers", "sampling_choice"] and schema["additionalProperties"] is False, "schema keys")

    require("3534486|p1_sab_structured_v1|gpua40|lu2026-2-51|normal|cg04|COMPLETED|00:01:38" in (JOB / "SACCT_V1.txt").read_text(), "sacct")
    require((JOB / "TERMINAL.txt").read_text().strip() == TERMINAL, "terminal")
    job = load(JOB / "JOB_RECEIPT_V1.json")
    condition = load(JOB / "results/CONDITION_RECEIPT_V1.json")
    require(job["status"] == "PASS_BOUNDED_LONGSEED_STRUCTURED_GATES", "job status")
    require(job["terminal"] == TERMINAL and job["condition"] == condition, "job condition")
    require(job["harness_exit_code"] == 0 and job["runtime_wall_seconds"] == 98, "runtime")
    require(job["non_composability"]["job_3534250_adverse_changed_or_promoted"] is False, "3534250 boundary")

    prompt_tokens = load(JOB / "results/PROMPT_TOKEN_ID_RECEIPT_V1.json")
    require(prompt_tokens["prompt_bodies_retained"] is False, "token prompt retention")
    for name in ("raw_without_special", "effective_with_special"):
        section = prompt_tokens[name]
        require(section["token_count"] == len(section["token_ids"]) == 27855, name + " count")
        require(section["token_array_sha256"] == digest(canonical(section["token_ids"])), name + " hash")

    tokens = {101: [], 202: []}
    contents = {101: [], 202: []}
    parsed_by_seed = {101: [], 202: []}
    request_hashes = {101: set(), 202: set()}
    for record in condition["records"]:
        seed = record["seed"]
        path = JOB / "results" / ("response_%02d_seed_%d.json" % (record["index"], seed))
        response = load(path)
        require("prompt" not in response, "raw prompt echo retained")
        require(response["prompt_receipt"]["body_retained"] is False, "prompt receipt")
        require(record["retained_sanitized_response_sha256"] == digest_path(path), "response hash")
        require(response["tokens"] == record["generated_token_ids"], "generated tokens")
        require(record["generated_token_array_sha256"] == digest(canonical(response["tokens"])), "token hash")
        content = response["content"]
        parsed = json.loads(content)
        require(set(parsed) == {"markers", "sampling_choice"}, "exact keys")
        require(parsed["markers"] == MARKERS, "exact marker order")
        require(parsed["sampling_choice"] in ALLOWED, "allowed choice")
        require(record["content_sha256"] == digest(content.encode()), "content hash")
        require(record["raw_content_strict_json_parse"] is True, "raw parse receipt")
        require(record["exact_keys"] is True and record["exact_schema_no_extra_text_or_keys"] is True, "exact schema receipt")
        require(record["sampling_choice"] == parsed["sampling_choice"] and record["sampling_choice_allowed"] is True, "choice receipt")
        require(response["timings"]["cache_n"] == record["cache_n"] == 0, "cache_n")
        require(response["timings"]["prompt_n"] == record["prompt_n"] == 27855, "prompt_n")
        require(response["truncated"] is record["truncated"] is False, "truncation")
        tokens[seed].append(response["tokens"])
        contents[seed].append(content)
        parsed_by_seed[seed].append(parsed)
        request_hashes[seed].add(record["request_sha256"])

    gates = condition["gates"]
    require(all(len(values) == 1 for values in request_hashes.values()), "request hashes")
    require(gates["within_seed_generated_token_identity"] == {"101": True, "202": True}, "within tokens gate")
    require(gates["within_seed_content_identity"] == {"101": True, "202": True}, "within content gate")
    require(all(all(x == values[0] for x in values[1:]) for values in tokens.values()), "within tokens")
    require(all(all(x == values[0] for x in values[1:]) for values in contents.values()), "within contents")
    require(tokens[101][0] != tokens[202][0] and gates["between_seed_generated_token_sensitivity"] is True, "token sensitivity")
    require(contents[101][0] != contents[202][0] and gates["between_seed_content_sensitivity"] is True, "content sensitivity")
    require(parsed_by_seed[101][0] == parsed_by_seed[202][0], "parsed semantic identity")
    require(gates["sampling_choices"] == ["iris"] * 6, "identical choices")
    require(gates["raw_content_strict_json_parse_all_requests"] is True, "raw parse gate")
    require(gates["exact_schema_no_extra_text_or_keys_all_requests"] is True, "schema gate")
    require(gates["prompt_n_values"] == [27855] * 6 and gates["prompt_n_matches_unconstrained_job_3534250"] is True, "prompt gate")
    require({r["generated_token_array_sha256"] for r in condition["records"] if r["seed"] == 101} == {"d4b5a8d85f7abe290b93451b00f0e05c920800e87874922f651c174bf336c290"}, "seed 101 hash")
    require({r["generated_token_array_sha256"] for r in condition["records"] if r["seed"] == 202} == {"1de431e98133302a4b2c8417cad20679ec4334250fa9abf54e1e8d61196636d3"}, "seed 202 hash")

    energy = load(JOB / "GPU_ENERGY_RECEIPT_V1.json")
    require(energy["schema"] == "orion.p1.scienceagentbench.longseed-mechanism-gpu-energy.v1", "inherited telemetry schema")
    require(math.isclose(energy["gpu_seconds_sampled"], 72.336, abs_tol=1e-12), "GPU seconds")
    require(math.isclose(energy["energy_wh_estimate"], 5.545619033333338, abs_tol=1e-15), "energy")

    cleanup = load(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json")
    require(cleanup["status"] == "PASS_REMOTE_ROOT_REMOVED" and cleanup["root_exists_after_cleanup"] is False, "cleanup")
    require(cleanup["files_removed"] == 66 and cleanup["file_bytes_removed"] == 18557665195, "cleanup inventory")
    top = load(ROOT / "LONGSEED_STRUCTURED_RECEIPT_V1.json")
    require(top["status"] == "COMPLETE_PASS_BOUNDED_STRUCTURED_GATES", "top status")
    require(top["terminal"] == TERMINAL and top["non_composability"]["production_replay_status"] == "BLOCKED", "top boundary")
    require(top["result"]["semantic_choice_sensitivity"] == "NOT_ESTABLISHED", "semantic boundary")
    require(top["result"]["parsed_objects_identical_across_seeds"] is True, "parsed boundary")
    require(top["cleanup_assurance"] == {"root_absence_status": "PASS_RETAINED_CLEANUP_RECEIPT", "job_absence_status": "CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT", "process_absence_status": "CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT"}, "cleanup scope")
    require(top["artifacts"]["protocol_sha256"] == digest_path(ROOT / "FROZEN_LONGSEED_STRUCTURED_PROTOCOL_V1.json"), "top protocol hash")
    require(top["artifacts"]["remote_job_manifest_sha256"] == digest_path(JOB / "REMOTE_RUN_SHA256SUMS"), "top manifest hash")
    require(top["artifacts"]["sacct_v1_sha256"] == digest_path(JOB / "SACCT_V1.txt"), "top SACCT hash")
    require(top["post_job_accounting_binding"] == {
        "path": "remote-job-3534486/SACCT_V1.txt",
        "remote_run_manifest_coverage": "INTENTIONALLY_EXCLUDED_POST_JOB_LOCAL_RECEIPT",
        "sha256": digest_path(JOB / "SACCT_V1.txt"),
    }, "structured accounting binding")
    require(top["artifacts"]["cleanup_receipt_sha256"] == digest_path(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json"), "top cleanup hash")

    for name in ("DEVELOPMENT_PACKET.md", "FAILURE_AND_REPAIR_LOG.md", "HANDOFF_V1.md"):
        text = (ROOT / name).read_text()
        require("NOT_ESTABLISHED" in text and "iris" in text, name + " semantic caveat")
    for path in ROOT.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            prompt_fragment = b"FILLER_" + b"0000"
            require(prompt_fragment not in path.read_bytes(), "prompt body retained: " + str(path))
            require(path.stat().st_size < 10_000_000, "large artifact retained")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
