#!/usr/bin/env python3
"""Run the frozen non-composable long-context structured-output condition."""

import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path


ORDER = [101, 202, 101, 202, 101, 202]


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def write_json(path, value):
    path.write_bytes(canonical(value) + b"\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def build_completion_body(sampling, prompt, seed, schema):
    """Return the frozen completion body with only json_schema added."""
    body = dict(sampling)
    body.update(
        {
            "prompt": prompt,
            "seed": seed,
            "cache_prompt": False,
            "json_schema": schema,
        }
    )
    return body


def validate_structured_content(content, markers, allowed):
    """Apply the prospective strict raw-JSON and exact-schema gates once."""
    try:
        parsed = json.loads(content)
        raw_parse = True
    except (json.JSONDecodeError, TypeError):
        parsed = None
        raw_parse = False
    exact_keys = isinstance(parsed, dict) and set(parsed) == {
        "markers",
        "sampling_choice",
    }
    marker_order_exact = exact_keys and parsed["markers"] == markers
    choice = parsed["sampling_choice"] if exact_keys else None
    sampling_choice_allowed = exact_keys and choice in allowed
    exact_schema = (
        raw_parse
        and exact_keys
        and marker_order_exact
        and sampling_choice_allowed
    )
    return {
        "parsed": parsed,
        "raw_content_strict_json_parse": raw_parse,
        "exact_keys": exact_keys,
        "marker_order_exact": marker_order_exact,
        "sampling_choice": choice,
        "sampling_choice_allowed": sampling_choice_allowed,
        "exact_schema_no_extra_text_or_keys": exact_schema,
    }


def post_json(url, body, timeout=1800):
    request_raw = canonical(body)
    request = urllib.request.Request(
        url,
        data=request_raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response_raw = response.read()
    return request_raw, response_raw, time.monotonic() - started


def contains_fragment(value, fragment):
    if isinstance(value, str):
        return fragment in value
    if isinstance(value, list):
        return any(contains_fragment(item, fragment) for item in value)
    if isinstance(value, dict):
        return any(
            contains_fragment(key, fragment) or contains_fragment(item, fragment)
            for key, item in value.items()
        )
    return False


def tokenize(base_url, prompt, add_special):
    body = {
        "content": prompt,
        "add_special": add_special,
        "parse_special": True,
        "with_pieces": False,
    }
    request_raw, response_raw, wall = post_json(
        base_url.rstrip("/") + "/tokenize", body
    )
    response = json.loads(response_raw)
    tokens = response.get("tokens")
    require(
        isinstance(tokens, list) and all(isinstance(token, int) for token in tokens),
        "tokenize endpoint did not return integer IDs",
    )
    return {
        "request_sha256": digest(request_raw),
        "response_sha256": digest(response_raw),
        "token_ids": tokens,
        "token_array_sha256": digest(canonical(tokens)),
        "token_count": len(tokens),
        "client_wall_seconds": wall,
    }


def run(protocol, prompt_path, schema_path, base_url, output_dir):
    prompt_raw = prompt_path.read_bytes()
    prompt = prompt_raw.decode("utf-8")
    prompt_spec = protocol["prompt"]
    require(len(prompt_raw) == prompt_spec["combined_bytes"], "combined prompt bytes")
    require(digest(prompt_raw) == prompt_spec["combined_sha256"], "combined prompt hash")
    require(protocol["request_order"] == ORDER, "frozen request order")
    prefix = prompt_raw[: prompt_spec["prefix_bytes"]]
    suffix = prompt_raw[prompt_spec["prefix_bytes"] :]
    require(digest(prefix) == prompt_spec["prefix_sha256"], "prefix hash")
    require(digest(suffix) == prompt_spec["suffix_sha256"], "suffix hash")

    schema_raw = schema_path.read_bytes()
    schema_spec = protocol["output_schema"]
    require(len(schema_raw) == schema_spec["bytes"], "output schema bytes")
    require(digest(schema_raw) == schema_spec["sha256"], "output schema hash")
    require(schema_spec["request_field"] == "json_schema", "schema request field")
    schema = json.loads(schema_raw)
    require(isinstance(schema, dict), "output schema must be an object")

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_tokens = tokenize(base_url, prompt, False)
    effective_tokens = tokenize(base_url, prompt, True)
    token_receipt = {
        "schema": "orion.p1.scienceagentbench.longseed-prompt-token-ids.v1",
        "status": "PASS_DIRECT_TOKEN_IDS_RETAINED",
        "prefix_sha256": prompt_spec["prefix_sha256"],
        "prefix_bytes": prompt_spec["prefix_bytes"],
        "suffix_sha256": prompt_spec["suffix_sha256"],
        "suffix_bytes": prompt_spec["suffix_bytes"],
        "combined_sha256": prompt_spec["combined_sha256"],
        "combined_bytes": prompt_spec["combined_bytes"],
        "prompt_bodies_retained": False,
        "raw_without_special": raw_tokens,
        "effective_with_special": effective_tokens,
        "scientific_authority_delta": "NONE",
    }
    write_json(output_dir / "PROMPT_TOKEN_ID_RECEIPT_V1.json", token_receipt)

    sampling = protocol["sampling"]
    markers = protocol["required_markers"]
    allowed = set(protocol["allowed_sampling_choices"])
    records = []
    tokens_by_seed = {101: [], 202: []}
    contents_by_seed = {101: [], 202: []}
    for index, seed in enumerate(ORDER, 1):
        body = build_completion_body(sampling, prompt, seed, schema)
        request_raw, response_raw, wall = post_json(
            base_url.rstrip("/") + "/completion", body
        )
        response = json.loads(response_raw)
        require(not response.get("error"), "server error")
        echoed = response.pop("prompt", None)
        require(isinstance(echoed, str), "missing echoed prompt")
        echoed_raw = echoed.encode("utf-8")
        require(len(echoed_raw) == len(prompt_raw), "echoed prompt bytes")
        require(digest(echoed_raw) == digest(prompt_raw), "echoed prompt hash")
        response["prompt_receipt"] = {
            "sha256": prompt_spec["combined_sha256"],
            "bytes": prompt_spec["combined_bytes"],
            "body_retained": False,
        }
        require(not contains_fragment(response, prompt[:64]), "prompt fragment remains")
        tokens = response.get("tokens")
        content = response.get("content")
        timings = response.get("timings")
        require(
            isinstance(tokens, list) and all(isinstance(token, int) for token in tokens),
            "missing generated token IDs",
        )
        require(isinstance(content, str), "missing response content")
        require(isinstance(timings, dict), "missing timings")
        sanitized = canonical(response) + b"\n"
        path = output_dir / ("response_%02d_seed_%d.json" % (index, seed))
        path.write_bytes(sanitized)
        structured = validate_structured_content(content, markers, allowed)
        tokens_by_seed[seed].append(tokens)
        contents_by_seed[seed].append(content)
        records.append(
            {
                "index": index,
                "seed": seed,
                "prompt_sha256": prompt_spec["combined_sha256"],
                "prompt_bytes": prompt_spec["combined_bytes"],
                "prompt_body_retained": False,
                "request_sha256": digest(request_raw),
                "request_bytes": len(request_raw),
                "unretained_raw_response_sha256": digest(response_raw),
                "retained_sanitized_response_sha256": digest(sanitized),
                "content_sha256": digest(content.encode("utf-8")),
                "content_bytes": len(content.encode("utf-8")),
                "generated_token_ids": tokens,
                "generated_token_array_sha256": digest(canonical(tokens)),
                "generated_token_count": len(tokens),
                "cache_n": timings.get("cache_n"),
                "prompt_n": timings.get("prompt_n"),
                "predicted_n": timings.get("predicted_n"),
                "truncated": response.get("truncated"),
                "raw_content_strict_json_parse": structured[
                    "raw_content_strict_json_parse"
                ],
                "exact_keys": structured["exact_keys"],
                "marker_order_exact": structured["marker_order_exact"],
                "sampling_choice": structured["sampling_choice"],
                "sampling_choice_allowed": structured[
                    "sampling_choice_allowed"
                ],
                "exact_schema_no_extra_text_or_keys": structured[
                    "exact_schema_no_extra_text_or_keys"
                ],
                "client_wall_seconds": wall,
            }
        )

    within_tokens = {
        str(seed): all(item == values[0] for item in values[1:])
        for seed, values in tokens_by_seed.items()
    }
    within_contents = {
        str(seed): all(item == values[0] for item in values[1:])
        for seed, values in contents_by_seed.items()
    }
    cache_values = [record["cache_n"] for record in records]
    prompt_values = [record["prompt_n"] for record in records]
    truncated_values = [record["truncated"] for record in records]
    target_prompt_n = protocol["gates"][
        "prompt_n_matches_unconstrained_job_3534250"
    ]
    gates = {
        "within_seed_generated_token_identity": within_tokens,
        "within_seed_content_identity": within_contents,
        "between_seed_generated_token_sensitivity": tokens_by_seed[101][0] != tokens_by_seed[202][0],
        "between_seed_content_sensitivity": contents_by_seed[101][0] != contents_by_seed[202][0],
        "cache_n_all_zero": all(value == 0 for value in cache_values),
        "cache_n_values": cache_values,
        "prompt_n_constant": len(set(prompt_values)) == 1,
        "prompt_n_values": prompt_values,
        "prompt_n_matches_unconstrained_job_3534250": all(
            value == target_prompt_n for value in prompt_values
        ),
        "prompt_n_unconstrained_job_3534250_target": target_prompt_n,
        "truncated_all_false": all(value is False for value in truncated_values),
        "truncated_values": truncated_values,
        "raw_content_strict_json_parse_all_requests": all(
            record["raw_content_strict_json_parse"] for record in records
        ),
        "raw_content_strict_json_parse_checks": [
            record["raw_content_strict_json_parse"] for record in records
        ],
        "exact_keys_all_requests": all(record["exact_keys"] for record in records),
        "exact_keys_checks": [record["exact_keys"] for record in records],
        "marker_order_exact_all_requests": all(
            record["marker_order_exact"] for record in records
        ),
        "marker_order_exact_checks": [
            record["marker_order_exact"] for record in records
        ],
        "sampling_choice_allowed_all_requests": all(
            record["sampling_choice_allowed"] for record in records
        ),
        "sampling_choices": [record["sampling_choice"] for record in records],
        "exact_schema_no_extra_text_or_keys_all_requests": all(
            record["exact_schema_no_extra_text_or_keys"] for record in records
        ),
        "exact_schema_checks": [
            record["exact_schema_no_extra_text_or_keys"] for record in records
        ],
    }
    passed = (
        all(within_tokens.values())
        and all(within_contents.values())
        and gates["between_seed_generated_token_sensitivity"]
        and gates["between_seed_content_sensitivity"]
        and gates["cache_n_all_zero"]
        and gates["prompt_n_constant"]
        and gates["prompt_n_matches_unconstrained_job_3534250"]
        and gates["truncated_all_false"]
        and gates["raw_content_strict_json_parse_all_requests"]
        and gates["exact_keys_all_requests"]
        and gates["marker_order_exact_all_requests"]
        and gates["sampling_choice_allowed_all_requests"]
        and gates["exact_schema_no_extra_text_or_keys_all_requests"]
    )
    receipt = {
        "schema": "orion.p1.scienceagentbench.longseed-structured-condition.v1",
        "status": (
            "PASS_BOUNDED_LONGSEED_STRUCTURED_GATES"
            if passed
            else "ADVERSE_BOUNDED_LONGSEED_STRUCTURED_GATE_FAILURE"
        ),
        "request_order": ORDER,
        "sampling": sampling,
        "cache_prompt": False,
        "output_schema": {
            "sha256": schema_spec["sha256"],
            "bytes": schema_spec["bytes"],
            "request_field": schema_spec["request_field"],
        },
        "prompt": {
            "prefix_sha256": prompt_spec["prefix_sha256"],
            "prefix_bytes": prompt_spec["prefix_bytes"],
            "suffix_sha256": prompt_spec["suffix_sha256"],
            "suffix_bytes": prompt_spec["suffix_bytes"],
            "combined_sha256": prompt_spec["combined_sha256"],
            "combined_bytes": prompt_spec["combined_bytes"],
            "body_retained": False,
            "raw_prompt_token_count": raw_tokens["token_count"],
            "effective_prompt_token_count": effective_tokens["token_count"],
        },
        "records": records,
        "gates": gates,
        "non_composability": protocol["non_composability"],
        "production_replay_status": "BLOCKED",
        "forbidden_inputs_opened": False,
        "scientific_authority_delta": "NONE",
    }
    write_json(output_dir / "CONDITION_RECEIPT_V1.json", receipt)
    print(receipt["status"])
    return 0 if passed else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    require(all(protocol["forbidden_inputs"].values()), "protected inputs must be forbidden")
    try:
        return run(
            protocol,
            args.prompt,
            args.schema,
            args.base_url,
            args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure = {
            "schema": "orion.p1.scienceagentbench.longseed-structured-infrastructure-failure.v1",
            "status": "NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "prompt_sha256": protocol["prompt"]["combined_sha256"],
            "prompt_bytes": protocol["prompt"]["combined_bytes"],
            "prompt_body_retained": False,
            "output_schema_sha256": protocol["output_schema"]["sha256"],
            "output_schema_bytes": protocol["output_schema"]["bytes"],
            "scientific_authority_delta": "NONE",
        }
        write_json(args.output_dir / "CONDITION_FAILURE_V1.json", failure)
        print(failure["status"])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
