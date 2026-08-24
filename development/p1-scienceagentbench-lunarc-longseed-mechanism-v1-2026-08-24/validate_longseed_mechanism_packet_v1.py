#!/usr/bin/env python3
"""Fail-closed focused validator for the long-seed mechanism packet."""

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JOB = ROOT / "remote-job-3534250"
TERMINAL = (
    "P1_SAB_LONGSEED_MECHANISM_ADVERSE__ONE_OR_MORE_FROZEN_GATES_FAILED__"
    "NONCOMPOSABLE__JOB_3534250__PRODUCTION_BLOCKED__COST_CANNOT_CHECK"
)
MARKERS = [
    "MK0_7b91c2",
    "MK1_a46fd8",
    "MK2_19e3ab",
    "MK3_c58071",
    "MK4_ef268d",
    "MK5_34da90",
]


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


def verify_manifest():
    for line in (JOB / "REMOTE_RUN_SHA256SUMS").read_text().splitlines():
        expected, relative = line.split(None, 1)
        path = JOB / relative.strip().removeprefix("./")
        require(path.is_file(), "manifest file absent: " + str(path))
        require(digest_path(path) == expected, "manifest hash: " + str(path))


def main():
    verify_manifest()
    protocol = load(ROOT / "FROZEN_LONGSEED_MECHANISM_PROTOCOL_V1.json")
    require(protocol["request_order"] == [101, 202, 101, 202, 101, 202], "order")
    require(protocol["sampling"]["temperature"] == 0.8, "temperature")
    require(protocol["sampling"]["n_predict"] == 128, "cap")
    require(protocol["server"]["ctx_size"] == 32768, "context")
    require(protocol["server"]["cache_prompt"] is False, "cache flag")
    require(all(protocol["forbidden_inputs"].values()), "forbidden inputs")
    require(protocol["production_replay_status_regardless_of_result"] == "BLOCKED", "production")

    provenance = load(ROOT / "PROMPT_PROVENANCE_V1.json")
    require(provenance["status"] == "PASS_PREFIX_SUFFIX_COMBINED_BYTES_FROZEN_BEFORE_EXECUTION", "provenance")
    require(provenance["combined"]["bytes"] == 91026, "prompt bytes")
    require(provenance["combined"]["sha256"] == "b55831c8657f3a1f5556833204b5aff79fe84e58f170edaa228909401e222f72", "prompt hash")
    require(provenance["prompt_bodies_retained_in_this_packet"] is False, "prompt retention")

    require("3534250|p1_sab_longseed_v1|gpua40|lu2026-2-51|normal|cg04|FAILED|00:01:59" in (JOB / "SACCT_V1.txt").read_text(), "sacct")
    require((JOB / "TERMINAL.txt").read_text().strip() == TERMINAL, "terminal")
    job = load(JOB / "JOB_RECEIPT_V1.json")
    condition = load(JOB / "results/CONDITION_RECEIPT_V1.json")
    require(job["status"] == "ADVERSE_BOUNDED_LONGSEED_MECHANISM_GATE_FAILURE", "job status")
    require(job["terminal"] == TERMINAL and job["condition"] == condition, "job condition")
    require(job["harness_exit_code"] == 2 and job["runtime_wall_seconds"] == 118, "job runtime")
    require(job["non_composability"]["production_replay_status"] == "BLOCKED", "production block")

    prompt_tokens = load(JOB / "results/PROMPT_TOKEN_ID_RECEIPT_V1.json")
    require(prompt_tokens["prompt_bodies_retained"] is False, "token prompt retention")
    for name in ("raw_without_special", "effective_with_special"):
        section = prompt_tokens[name]
        require(section["token_count"] == len(section["token_ids"]) == 27855, name + " count")
        require(section["token_array_sha256"] == digest(canonical(section["token_ids"])), name + " hash")

    tokens = {101: [], 202: []}
    contents = {101: [], 202: []}
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
        require(record["content_sha256"] == digest(content.encode()), "content hash")
        try:
            json.loads(content)
        except json.JSONDecodeError:
            pass
        else:
            raise AssertionError("raw content unexpectedly parsed")
        require(all(marker in content for marker in MARKERS), "markers complete")
        require(MARKERS == sorted(MARKERS, key=content.index), "markers ordered")
        require(record["sampling_choice"] is None and record["sampling_choice_allowed"] is False, "strict choice gate")
        require(response["timings"]["cache_n"] == record["cache_n"] == 0, "cache_n")
        require(response["timings"]["prompt_n"] == record["prompt_n"] == 27855, "prompt_n")
        require(response["truncated"] is record["truncated"] is False, "truncation")
        tokens[seed].append(response["tokens"])
        contents[seed].append(content)
        request_hashes[seed].add(record["request_sha256"])

    within_tokens = {str(seed): all(x == values[0] for x in values[1:]) for seed, values in tokens.items()}
    within_contents = {str(seed): all(x == values[0] for x in values[1:]) for seed, values in contents.items()}
    gates = condition["gates"]
    require(all(len(values) == 1 for values in request_hashes.values()), "request hashes")
    require(within_tokens == gates["within_seed_generated_token_identity"] == {"101": True, "202": True}, "within tokens")
    require(within_contents == gates["within_seed_content_identity"] == {"101": True, "202": True}, "within contents")
    require(tokens[101][0] != tokens[202][0] and gates["between_seed_generated_token_sensitivity"] is True, "token sensitivity")
    require(contents[101][0] != contents[202][0] and gates["between_seed_content_sensitivity"] is True, "content sensitivity")
    require(gates["sampling_choices"] == [None] * 6 and gates["sampling_choice_allowed_all_requests"] is False, "adverse choice")
    require(gates["cache_n_values"] == [0] * 6 and gates["prompt_n_values"] == [27855] * 6, "timing gates")
    require({r["generated_token_array_sha256"] for r in condition["records"] if r["seed"] == 101} == {"4a6e4f09f2e9a04f5355429f7b36daed6cafd2281c91625a05111188ee21e06d"}, "seed 101 hash")
    require({r["generated_token_array_sha256"] for r in condition["records"] if r["seed"] == 202} == {"a345d234e8786268d9b703c0cb0666fd18b35e0fbb646979322f00b395e3d578"}, "seed 202 hash")

    energy = load(JOB / "GPU_ENERGY_RECEIPT_V1.json")
    require(math.isclose(energy["gpu_seconds_sampled"], 72.379, abs_tol=1e-12), "GPU seconds")
    require(math.isclose(energy["energy_wh_estimate"], 5.518933734722219, abs_tol=1e-15), "energy")

    cleanup = load(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json")
    require(cleanup["status"] == "PASS_REMOTE_ROOT_REMOVED" and cleanup["root_exists_after_cleanup"] is False, "cleanup")
    require(cleanup["files_removed"] == 66 and cleanup["file_bytes_removed"] == 18557665195, "cleanup inventory")
    top = load(ROOT / "LONGSEED_MECHANISM_RECEIPT_V1.json")
    require(top["status"] == "COMPLETE_ADVERSE_STRICT_RAW_CONTENT_PARSE_GATE", "top status")
    require(top["terminal"] == TERMINAL and top["non_composability"]["production_replay_status"] == "BLOCKED", "top boundary")
    require(top["result"]["embedded_json_reparsed"] is False, "reparse boundary")
    require(top["cleanup_assurance"] == {"root_absence_status": "PASS_RETAINED_CLEANUP_RECEIPT", "job_absence_status": "CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT", "process_absence_status": "CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT"}, "cleanup scope")
    require(top["artifacts"]["protocol_sha256"] == digest_path(ROOT / "FROZEN_LONGSEED_MECHANISM_PROTOCOL_V1.json"), "top protocol hash")
    require(top["artifacts"]["remote_job_manifest_sha256"] == digest_path(JOB / "REMOTE_RUN_SHA256SUMS"), "top manifest hash")
    require(top["artifacts"]["cleanup_receipt_sha256"] == digest_path(ROOT / "REMOTE_CLEANUP_RECEIPT_V1.json"), "top cleanup hash")

    require("not extract or reparse" in (ROOT / "FAILURE_AND_REPAIR_LOG.md").read_text(), "documented strict boundary")
    for path in ROOT.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            prompt_fragment = b"FILLER_" + b"0000"
            require(prompt_fragment not in path.read_bytes(), "prompt body retained: " + str(path))
            require(path.stat().st_size < 10_000_000, "large artifact retained")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
