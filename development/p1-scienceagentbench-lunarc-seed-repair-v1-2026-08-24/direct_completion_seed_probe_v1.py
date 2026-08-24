#!/usr/bin/env python3
"""Run one frozen six-request direct llama-server completion condition."""

import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def post_json(url, body):
    raw = canonical_bytes(body)
    request = urllib.request.Request(
        url,
        data=raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=300) as response:
        response_raw = response.read()
    return raw, response_raw, time.monotonic() - started


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--cache-prompt", choices=("true", "false"), required=True)
    args = parser.parse_args()

    fixture = json.loads(args.fixture.read_text())
    seeds = fixture["request_order"]
    if seeds != [101, 202, 101, 202, 101, 202]:
        raise SystemExit("frozen seed sequence mismatch")
    cache_prompt = args.cache_prompt == "true"
    args.output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    tokens_by_seed = {101: [], 202: []}
    contents_by_seed = {101: [], 202: []}
    for index, seed in enumerate(seeds, 1):
        body = dict(fixture["sampling"])
        body.update(
            {
                "prompt": fixture["prompt"],
                "seed": seed,
                "cache_prompt": cache_prompt,
            }
        )
        request_raw, response_raw, client_wall_seconds = post_json(
            args.base_url.rstrip("/") + "/completion", body
        )
        response = json.loads(response_raw)
        if response.get("error"):
            raise SystemExit("server error: " + str(response["error"]))
        tokens = response.get("tokens")
        content = response.get("content")
        timings = response.get("timings")
        if not isinstance(tokens, list):
            raise SystemExit("return_tokens=true did not yield a token array")
        if not isinstance(content, str) or not isinstance(timings, dict):
            raise SystemExit("missing content or timings")
        cache_n = timings.get("cache_n")
        prompt_n = timings.get("prompt_n")
        if not isinstance(cache_n, int) or not isinstance(prompt_n, int):
            raise SystemExit("missing integer timings.cache_n or timings.prompt_n")
        request_path = args.output_dir / ("request_%02d_seed_%d.json" % (index, seed))
        response_path = args.output_dir / ("response_%02d_seed_%d.json" % (index, seed))
        request_path.write_bytes(request_raw + b"\n")
        response_path.write_bytes(response_raw + (b"" if response_raw.endswith(b"\n") else b"\n"))
        tokens_by_seed[seed].append(tokens)
        contents_by_seed[seed].append(content)
        records.append(
            {
                "index": index,
                "seed": seed,
                "request_sha256": digest(request_raw + b"\n"),
                "response_raw_sha256": digest(
                    response_raw + (b"" if response_raw.endswith(b"\n") else b"\n")
                ),
                "content_sha256": digest(content.encode("utf-8")),
                "token_array_sha256": digest(canonical_bytes(tokens)),
                "token_count": len(tokens),
                "cache_n": cache_n,
                "prompt_n": prompt_n,
                "predicted_n": timings.get("predicted_n"),
                "client_wall_seconds": client_wall_seconds,
            }
        )

    within_seed_token_identity = {
        str(seed): all(item == arrays[0] for item in arrays[1:])
        for seed, arrays in tokens_by_seed.items()
    }
    within_seed_content_identity = {
        str(seed): all(item == values[0] for item in values[1:])
        for seed, values in contents_by_seed.items()
    }
    between_seed_token_sensitivity = tokens_by_seed[101][0] != tokens_by_seed[202][0]
    cache_n_values = [record["cache_n"] for record in records]
    prompt_n_values = [record["prompt_n"] for record in records]
    cache_n_all_zero = all(value == 0 for value in cache_n_values)
    prompt_n_constant = len(set(prompt_n_values)) == 1
    cache_off_gate_pass = (
        not cache_prompt
        and all(within_seed_token_identity.values())
        and between_seed_token_sensitivity
        and cache_n_all_zero
        and prompt_n_constant
    )
    receipt = {
        "schema": "orion.p1.scienceagentbench.direct-completion-seed-probe.v1",
        "condition": args.condition,
        "cache_prompt": cache_prompt,
        "request_order": seeds,
        "records": records,
        "gates": {
            "within_seed_token_array_identity": within_seed_token_identity,
            "within_seed_content_identity": within_seed_content_identity,
            "between_seed_token_array_sensitivity": between_seed_token_sensitivity,
            "cache_n_all_zero": cache_n_all_zero,
            "cache_n_values": cache_n_values,
            "prompt_n_constant": prompt_n_constant,
            "prompt_n_values": prompt_n_values,
        },
        "status": (
            "PASS_CACHE_OFF_DETERMINISTIC_AND_SEED_SENSITIVE"
            if cache_off_gate_pass
            else (
                "OBSERVED_CACHE_ON_NEGATIVE_CONTROL"
                if cache_prompt
                else "ADVERSE_CACHE_OFF_GATE_FAILURE"
            )
        ),
        "forbidden_inputs_opened": False,
        "scientific_authority_delta": "NONE",
    }
    receipt_path = args.output_dir / "CONDITION_RECEIPT_V1.json"
    receipt_path.write_bytes(canonical_bytes(receipt) + b"\n")
    print(receipt["status"])
    return 0 if (cache_prompt or cache_off_gate_pass) else 2


if __name__ == "__main__":
    raise SystemExit(main())

