#!/usr/bin/env python3
"""Canonicalize the retained PR #1130 replay pair without timing fields."""

import argparse
import hashlib
import json
from pathlib import Path


VOLATILE_RESPONSE_FIELDS = {
    "created_at",
    "total_duration",
    "load_duration",
    "prompt_eval_duration",
    "eval_duration",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    names = ["replay_seed101_1", "replay_seed101_2"]
    requests = []
    responses = []
    records = []
    for name in names:
        request_path = args.source_dir / (name + ".request.json")
        response_path = args.source_dir / (name + ".response.json")
        request_raw = request_path.read_bytes()
        response_raw = response_path.read_bytes()
        request = json.loads(request_raw)
        response = json.loads(response_raw)
        context = response.get("context")
        eval_count = response.get("eval_count")
        if not isinstance(context, list) or not isinstance(eval_count, int):
            raise SystemExit("missing context token array or eval_count")
        if eval_count <= 0 or eval_count > len(context):
            raise SystemExit("invalid eval_count/context relationship")
        prompt_tokens = context[:-eval_count]
        generated_tokens = context[-eval_count:]
        canonical = {
            key: value
            for key, value in response.items()
            if key not in VOLATILE_RESPONSE_FIELDS
        }
        records.append(
            {
                "name": name,
                "request_raw_sha256": digest(request_raw),
                "response_raw_sha256": digest(response_raw),
                "canonical_response_sha256": digest(canonical_bytes(canonical)),
                "response_text_sha256": digest(response["response"].encode("utf-8")),
                "context_token_array_sha256": digest(canonical_bytes(context)),
                "generated_token_array_sha256": digest(canonical_bytes(generated_tokens)),
                "context_token_count": len(context),
                "prompt_token_prefix_count_derived": len(prompt_tokens),
                "generated_token_count_from_eval_count": len(generated_tokens),
            }
        )
        requests.append((request_raw, request))
        responses.append((response, prompt_tokens, generated_tokens))

    left, right = responses
    first_context_diff = next(
        (i for i, pair in enumerate(zip(left[0]["context"], right[0]["context"]))
         if pair[0] != pair[1]),
        None,
    )
    first_generated_diff = next(
        (i for i, pair in enumerate(zip(left[2], right[2])) if pair[0] != pair[1]),
        None,
    )
    comparison = {
        "request_raw_bytes_identical": requests[0][0] == requests[1][0],
        "request_json_identical": requests[0][1] == requests[1][1],
        "response_text_identical": left[0]["response"] == right[0]["response"],
        "context_token_arrays_identical": left[0]["context"] == right[0]["context"],
        "derived_prompt_token_prefixes_identical": left[1] == right[1],
        "derived_generated_token_arrays_identical": left[2] == right[2],
        "first_context_token_difference_index": first_context_diff,
        "first_generated_token_difference_index": first_generated_diff,
        "canonical_response_fields_excluded": sorted(VOLATILE_RESPONSE_FIELDS),
    }
    confirmed = (
        comparison["request_raw_bytes_identical"]
        and comparison["request_json_identical"]
        and not comparison["response_text_identical"]
        and not comparison["context_token_arrays_identical"]
        and comparison["derived_prompt_token_prefixes_identical"]
        and not comparison["derived_generated_token_arrays_identical"]
    )
    receipt = {
        "schema": "orion.p1.scienceagentbench.pr1130-replay-canonicalization.v1",
        "source_pr": 1130,
        "source_commit": "8c1f5c88bda5da7dc192c40dc92698c19fbb57ba",
        "status": (
            "CONFIRMED_CONTENT_AND_GENERATED_TOKEN_ARRAY_DIVERGENCE"
            if confirmed
            else "ADVERSE_CANONICALIZATION_DID_NOT_CONFIRM_EXPECTED_DIVERGENCE"
        ),
        "records": records,
        "comparison": comparison,
        "scientific_authority_delta": "NONE",
    }
    args.output.write_bytes(canonical_bytes(receipt) + b"\n")
    print(receipt["status"])
    return 0 if confirmed else 2


if __name__ == "__main__":
    raise SystemExit(main())

