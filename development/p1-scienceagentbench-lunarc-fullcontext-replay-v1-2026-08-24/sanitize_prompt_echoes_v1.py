#!/usr/bin/env python3
"""Replace llama-server prompt echoes with hash/byte receipts before retention."""

import argparse
import hashlib
import json
import time
from pathlib import Path


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def contains_prompt_fragment(value, fragment):
    if isinstance(value, str):
        return fragment in value
    if isinstance(value, list):
        return any(contains_prompt_fragment(item, fragment) for item in value)
    if isinstance(value, dict):
        return any(
            contains_prompt_fragment(key, fragment)
            or contains_prompt_fragment(item, fragment)
            for key, item in value.items()
        )
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    script_sha256 = digest(Path(__file__).read_bytes())
    records = []
    for condition, spec in protocol["conditions"].items():
        directory = args.job_dir / "results" / condition
        receipt_path = directory / "CONDITION_RECEIPT_V1.json"
        receipt = json.loads(receipt_path.read_text())
        for record in receipt["records"]:
            path = directory / (
                "response_%02d_seed_%d.json" % (record["index"], record["seed"])
            )
            raw = path.read_bytes()
            if digest(raw) != record["response_sha256"]:
                raise SystemExit("original response hash mismatch: " + str(path))
            response = json.loads(raw)
            prompt = response.pop("prompt", None)
            if not isinstance(prompt, str):
                raise SystemExit("missing echoed prompt: " + str(path))
            prompt_raw = prompt.encode("utf-8")
            if len(prompt_raw) != spec["prompt_bytes"]:
                raise SystemExit("echoed prompt byte mismatch: " + str(path))
            if digest(prompt_raw) != spec["prompt_sha256"]:
                raise SystemExit("echoed prompt hash mismatch: " + str(path))
            response["prompt_receipt"] = {
                "sha256": spec["prompt_sha256"],
                "bytes": spec["prompt_bytes"],
                "body_retained": False,
            }
            fragment = prompt[:64]
            if contains_prompt_fragment(response, fragment):
                raise SystemExit("prompt fragment remains after sanitization: " + str(path))
            sanitized = canonical(response)
            path.write_bytes(sanitized)
            original_sha256 = record.pop("response_sha256")
            record["unretained_raw_response_sha256"] = original_sha256
            record["retained_sanitized_response_sha256"] = digest(sanitized)
            record["prompt_echo_removed"] = True
            records.append(
                {
                    "condition": condition,
                    "index": record["index"],
                    "seed": record["seed"],
                    "prompt_sha256": spec["prompt_sha256"],
                    "prompt_bytes": spec["prompt_bytes"],
                    "unretained_raw_response_sha256": original_sha256,
                    "retained_sanitized_response_sha256": digest(sanitized),
                    "retained_sanitized_response_bytes": len(sanitized),
                }
            )
        receipt["prompt_echo_sanitization"] = {
            "status": "PASS_PROMPT_BODIES_REMOVED_BEFORE_PACKET_RETENTION",
            "sanitizer_script_sha256": script_sha256,
            "raw_response_bodies_retained": False,
        }
        receipt_path.write_bytes(canonical(receipt))
    output = {
        "schema": "orion.p1.scienceagentbench.fullcontext-prompt-echo-sanitization.v1",
        "status": "PASS_PROMPT_BODIES_REMOVED_BEFORE_PACKET_RETENTION",
        "job_id": args.job_dir.name.removeprefix("job-"),
        "records": records,
        "record_count": len(records),
        "sanitizer_script_sha256": script_sha256,
        "prompt_bodies_retained": False,
        "sanitized_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scientific_results_changed": False,
        "scientific_authority_delta": "NONE",
    }
    (args.job_dir / "PROMPT_ECHO_SANITIZATION_V1.json").write_bytes(canonical(output))
    print(output["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
