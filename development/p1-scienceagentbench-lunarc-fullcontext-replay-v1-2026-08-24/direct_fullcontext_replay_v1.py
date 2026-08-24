#!/usr/bin/env python3
"""Run the two frozen cache-off direct llama-server replay conditions."""

import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path


EXPECTED_ORDER = [101, 202, 101, 202, 101, 202]


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_bytes(canonical_bytes(value) + b"\n")


def post_json(url, body, timeout=1800):
    request_raw = canonical_bytes(body)
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


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


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
        "tokenize endpoint did not return integer token IDs",
    )
    return {
        "request_sha256": digest(request_raw),
        "response_sha256": digest(response_raw),
        "token_ids": tokens,
        "token_array_sha256": digest(canonical_bytes(tokens)),
        "token_count": len(tokens),
        "client_wall_seconds": wall,
    }


def run_condition(name, spec, prompt_path, protocol, base_url, output_root):
    prompt_raw = prompt_path.read_bytes()
    prompt = prompt_raw.decode("utf-8")
    require(len(prompt_raw) == spec["prompt_bytes"], name + ": prompt byte count")
    require(digest(prompt_raw) == spec["prompt_sha256"], name + ": prompt hash")

    raw_tokens = tokenize(base_url, prompt, False)
    effective_tokens = tokenize(base_url, prompt, True)

    directory = output_root / name
    directory.mkdir(parents=True, exist_ok=True)
    token_receipt = {
        "schema": "orion.p1.scienceagentbench.fullcontext-prompt-token-ids.v1",
        "condition": name,
        "prompt_sha256": spec["prompt_sha256"],
        "prompt_bytes": spec["prompt_bytes"],
        "prompt_body_retained": False,
        "source_route_token_identities": {
            key: value for key, value in spec.items() if key.startswith("source_ollama_")
        },
        "direct_tokenizer_equality_to_source_is_a_gate": False,
        "raw_without_special": raw_tokens,
        "effective_with_special": effective_tokens,
        "scientific_authority_delta": "NONE",
    }
    write_json(directory / "PROMPT_TOKEN_ID_RECEIPT_V1.json", token_receipt)

    records = []
    tokens_by_seed = {101: [], 202: []}
    contents_by_seed = {101: [], 202: []}
    marker_checks = []
    request_order = protocol["request_order"]
    require(request_order == EXPECTED_ORDER, name + ": frozen request order")
    for index, seed in enumerate(request_order, 1):
        body = {
            "prompt": prompt,
            "seed": seed,
            "cache_prompt": False,
            "temperature": spec["temperature"],
            "top_k": spec["top_k"],
            "top_p": spec["top_p"],
            "min_p": spec["min_p"],
            "repeat_penalty": spec["repeat_penalty"],
            "n_predict": spec["n_predict"],
            "stream": False,
            "return_tokens": True,
        }
        request_raw, response_raw, wall = post_json(
            base_url.rstrip("/") + "/completion", body
        )
        response = json.loads(response_raw)
        require(not response.get("error"), name + ": server error")
        tokens = response.get("tokens")
        content = response.get("content")
        timings = response.get("timings")
        require(
            isinstance(tokens, list)
            and all(isinstance(token, int) for token in tokens),
            name + ": missing generated token IDs",
        )
        require(isinstance(content, str), name + ": missing response content")
        require(isinstance(timings, dict), name + ": missing timings")
        require(
            isinstance(timings.get("cache_n"), int)
            and isinstance(timings.get("prompt_n"), int),
            name + ": missing cache_n or prompt_n",
        )
        response_path = directory / (
            "response_%02d_seed_%d.json" % (index, seed)
        )
        response_bytes = response_raw + (
            b"" if response_raw.endswith(b"\n") else b"\n"
        )
        response_path.write_bytes(response_bytes)
        markers = spec["required_markers"]
        markers_complete = all(marker in content for marker in markers)
        markers_ordered = (
            markers_complete
            and markers == sorted(markers, key=content.index)
        )
        marker_checks.append(markers_complete and markers_ordered)
        tokens_by_seed[seed].append(tokens)
        contents_by_seed[seed].append(content)
        records.append(
            {
                "index": index,
                "seed": seed,
                "prompt_sha256": spec["prompt_sha256"],
                "prompt_bytes": spec["prompt_bytes"],
                "prompt_body_retained": False,
                "request_sha256": digest(request_raw),
                "request_bytes": len(request_raw),
                "response_sha256": digest(response_bytes),
                "content_sha256": digest(content.encode("utf-8")),
                "content_bytes": len(content.encode("utf-8")),
                "generated_token_ids": tokens,
                "generated_token_array_sha256": digest(canonical_bytes(tokens)),
                "generated_token_count": len(tokens),
                "cache_n": timings["cache_n"],
                "prompt_n": timings["prompt_n"],
                "predicted_n": timings.get("predicted_n"),
                "truncated": response.get("truncated"),
                "stop": response.get("stop"),
                "stopped_eos": response.get("stopped_eos"),
                "stopped_limit": response.get("stopped_limit"),
                "markers_complete": markers_complete,
                "markers_ordered": markers_ordered,
                "client_wall_seconds": wall,
            }
        )

    within_token = {
        str(seed): all(value == arrays[0] for value in arrays[1:])
        for seed, arrays in tokens_by_seed.items()
    }
    within_content = {
        str(seed): all(value == values[0] for value in values[1:])
        for seed, values in contents_by_seed.items()
    }
    between_token = tokens_by_seed[101][0] != tokens_by_seed[202][0]
    between_content = contents_by_seed[101][0] != contents_by_seed[202][0]
    cache_values = [record["cache_n"] for record in records]
    prompt_values = [record["prompt_n"] for record in records]
    truncated_values = [record["truncated"] for record in records]
    gates = {
        "within_seed_generated_token_identity": within_token,
        "within_seed_content_identity": within_content,
        "between_seed_generated_token_sensitivity": between_token,
        "between_seed_content_sensitivity": between_content,
        "cache_n_all_zero": all(value == 0 for value in cache_values),
        "cache_n_values": cache_values,
        "prompt_n_constant": len(set(prompt_values)) == 1,
        "prompt_n_values": prompt_values,
        "truncated_all_false": all(value is False for value in truncated_values),
        "truncated_values": truncated_values,
        "markers_complete_and_ordered_all_requests": all(marker_checks),
        "marker_checks": marker_checks,
    }
    status_pass = (
        all(within_token.values())
        and all(within_content.values())
        and between_token
        and between_content
        and gates["cache_n_all_zero"]
        and gates["prompt_n_constant"]
        and gates["truncated_all_false"]
        and gates["markers_complete_and_ordered_all_requests"]
    )
    receipt = {
        "schema": "orion.p1.scienceagentbench.fullcontext-replay-condition.v1",
        "condition": name,
        "status": (
            "PASS_FROZEN_FULLCONTEXT_REPLAY_GATES"
            if status_pass
            else "ADVERSE_FROZEN_FULLCONTEXT_REPLAY_GATE_FAILURE"
        ),
        "cache_prompt": False,
        "request_order": request_order,
        "sampling": {
            key: spec[key]
            for key in (
                "temperature",
                "top_k",
                "top_p",
                "min_p",
                "repeat_penalty",
                "n_predict",
            )
        },
        "prompt": {
            "sha256": spec["prompt_sha256"],
            "bytes": spec["prompt_bytes"],
            "body_retained": False,
            "raw_prompt_token_count": raw_tokens["token_count"],
            "effective_prompt_token_count_with_special": effective_tokens["token_count"],
            "source_route_token_identities": {
                key: value for key, value in spec.items() if key.startswith("source_ollama_")
            },
            "direct_tokenizer_equality_to_source_is_a_gate": False,
            "token_id_receipt_sha256": digest(
                (directory / "PROMPT_TOKEN_ID_RECEIPT_V1.json").read_bytes()
            ),
        },
        "records": records,
        "gates": gates,
        "forbidden_inputs_opened": False,
        "scientific_authority_delta": "NONE",
    }
    write_json(directory / "CONDITION_RECEIPT_V1.json", receipt)
    return receipt, status_pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--short-prompt", type=Path, required=True)
    parser.add_argument("--long-prompt", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text())
    require(protocol["request_order"] == EXPECTED_ORDER, "protocol request order")
    require(
        all(protocol["forbidden_inputs"].values()),
        "protocol must forbid every protected input class",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    conditions = {}
    infrastructure_failures = {}
    all_pass = True
    for name, prompt_path in (
        ("short_pr1130_replay", args.short_prompt),
        ("long_pr1130_six_marker", args.long_prompt),
    ):
        try:
            receipt, passed = run_condition(
                name,
                protocol["conditions"][name],
                prompt_path,
                protocol,
                args.base_url,
                args.output_dir,
            )
            conditions[name] = receipt["status"]
            all_pass = all_pass and passed
        except Exception as exc:
            all_pass = False
            failure = {
                "schema": "orion.p1.scienceagentbench.fullcontext-condition-infrastructure-failure.v1",
                "status": "NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE",
                "condition": name,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "prompt_sha256": protocol["conditions"][name]["prompt_sha256"],
                "prompt_bytes": protocol["conditions"][name]["prompt_bytes"],
                "prompt_body_retained": False,
                "scientific_authority_delta": "NONE",
            }
            condition_dir = args.output_dir / name
            condition_dir.mkdir(parents=True, exist_ok=True)
            write_json(condition_dir / "CONDITION_FAILURE_V1.json", failure)
            conditions[name] = failure["status"]
            infrastructure_failures[name] = failure
    has_infrastructure_failure = bool(infrastructure_failures)
    summary = {
        "schema": "orion.p1.scienceagentbench.fullcontext-replay-harness.v1",
        "status": (
            "NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE"
            if has_infrastructure_failure
            else (
                "COMPLETE_TWO_SEPARATE_CONDITIONS"
                if all_pass
                else "COMPLETE_WITH_ONE_OR_MORE_ADVERSE_CONDITIONS"
            )
        ),
        "condition_statuses": conditions,
        "infrastructure_failures": infrastructure_failures,
        "composition_status": "NOT_COMPOSED__NO_COMPOSITE_SCIENTIFIC_WITNESS",
        "prompt_bodies_retained": False,
        "forbidden_inputs_opened": False,
        "scientific_authority_delta": "NONE",
    }
    write_json(args.output_dir / "HARNESS_RECEIPT_V1.json", summary)
    print(summary["status"])
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
