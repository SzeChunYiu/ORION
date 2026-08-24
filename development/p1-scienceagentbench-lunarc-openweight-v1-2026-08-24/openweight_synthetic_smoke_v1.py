#!/usr/bin/env python3
"""Frozen synthetic-only Ollama generation smoke for the P1 open-weight route."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


SCHEMA = "orion.p1.scienceagentbench.lunarc-openweight-smoke-receipt.v1"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def post_json(url: str, payload: dict[str, Any], timeout: float = 1800.0) -> tuple[dict[str, Any], float]:
    body = canonical_bytes(payload)
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read())
    return result, time.monotonic() - started


def request_options(fixture: dict[str, Any], seed: int, num_predict: int) -> dict[str, Any]:
    decoding = fixture["decoding"]
    return {
        "seed": seed,
        "num_ctx": decoding["num_ctx"],
        "num_predict": num_predict,
        "temperature": decoding["temperature"],
        "top_p": decoding["top_p"],
        "top_k": decoding["top_k"],
        "min_p": decoding["min_p"],
        "repeat_penalty": decoding["repeat_penalty"],
    }


def generate(
    *,
    call_id: str,
    base_url: str,
    model: str,
    fixture: dict[str, Any],
    prompt: str,
    seed: int,
    num_predict: int,
    output_dir: Path,
    json_format: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "keep_alive": "30m",
        "options": request_options(fixture, seed, num_predict),
    }
    if json_format:
        payload["format"] = "json"
    request_path = output_dir / f"{call_id}.request.json"
    response_path = output_dir / f"{call_id}.response.json"
    write_json(request_path, payload)
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        response, client_wall_seconds = post_json(f"{base_url}/api/generate", payload)
    except Exception as exc:
        write_json(
            output_dir / f"{call_id}.failure.json",
            {
                "call_id": call_id,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "request_sha256": sha256_file(request_path),
                "started_utc": started_utc,
            },
        )
        raise
    write_json(response_path, response)
    text = response.get("response", "")
    require(isinstance(text, str) and text != "", f"{call_id}: empty response text")
    eval_count = response.get("eval_count")
    eval_duration = response.get("eval_duration")
    prompt_eval_count = response.get("prompt_eval_count")
    require(isinstance(eval_count, int) and eval_count > 0, f"{call_id}: invalid eval_count")
    require(isinstance(prompt_eval_count, int) and prompt_eval_count > 0, f"{call_id}: invalid prompt_eval_count")
    require(isinstance(eval_duration, int) and eval_duration > 0, f"{call_id}: invalid eval_duration")
    return {
        "call_id": call_id,
        "seed": seed,
        "options": payload["options"],
        "request_sha256": sha256_file(request_path),
        "request_bytes": request_path.stat().st_size,
        "response_envelope_sha256": sha256_file(response_path),
        "response_envelope_bytes": response_path.stat().st_size,
        "response_text_sha256": sha256_bytes(text.encode()),
        "response_text_bytes": len(text.encode()),
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "load_duration_ns": response.get("load_duration"),
        "prompt_eval_duration_ns": response.get("prompt_eval_duration"),
        "eval_duration_ns": eval_duration,
        "total_duration_ns": response.get("total_duration"),
        "client_wall_seconds": client_wall_seconds,
        "generation_tokens_per_second": eval_count / (eval_duration / 1e9),
        "done": response.get("done"),
        "done_reason": response.get("done_reason"),
        "created_at": response.get("created_at"),
        "model_returned": response.get("model"),
    }


def arm_prompts(fixture: dict[str, Any]) -> dict[str, str]:
    masked = json.dumps(fixture["masked_packet"], sort_keys=True, separators=(",", ":"))
    recovered = json.dumps(fixture["recovered_packet"], sort_keys=True, separators=(",", ":"))
    return {
        "RR_PHASE0": (
            "This is a synthetic nonbenchmark fixture. From the masked packet below, emit only a compact JSON "
            "typed state with keys assumptions, unresolved_inputs, intended_analysis, invariants, output_contract. "
            f"MASKED_PACKET={masked}"
        ),
        "RR_PHASE1_PREFIX": (
            "This is the recovery phase of a synthetic nonbenchmark fixture. Compare RECOVERED_PACKET against the "
            "persisted typed state, revise only affected entries, and emit exactly one self-contained Python program "
            "that writes the required JSON output. Do not use markdown. "
            f"RECOVERED_PACKET={recovered} PERSISTED_TYPED_STATE="
        ),
        "OS_PHASE1": (
            "This is a synthetic nonbenchmark one-shot fixture. Emit exactly one self-contained Python program that "
            "uses the recovered inline values and writes the required JSON output. Do not use markdown. "
            f"RECOVERED_PACKET={recovered}"
        ),
        "NR_PHASE0": (
            "This is a synthetic nonbenchmark masked fixture. Emit only a generic bounded analysis plan that does not "
            "guess masked values and does not contain a final program. "
            f"MASKED_PACKET={masked}"
        ),
        "NR_PHASE1": (
            "This is a fresh, stateless synthetic nonbenchmark request. Ignore any prior plan. Emit exactly one "
            "self-contained Python program from scratch that uses the recovered inline values and writes the required "
            f"JSON output. Do not use markdown. RECOVERED_PACKET={recovered}"
        ),
    }


def long_context_prompt(fixture: dict[str, Any]) -> tuple[str, list[str]]:
    spec = fixture["long_context"]
    require(len(spec["marker_positions"]) == len(spec["marker_values"]), "long-context marker binding length mismatch")
    positions = dict(zip(spec["marker_positions"], spec["marker_values"]))
    lines = [
        "Synthetic long-context retention probe. Read every line. Six unique marker values appear once each. "
        "At the end, return a compact JSON object with key markers whose value is the six marker values in encounter "
        "order. Copy exact bytes; do not infer or guess absent values."
    ]
    for index in range(spec["filler_line_count"]):
        if index in positions:
            lines.append(f"RETENTION_MARKER={positions[index]}")
        lines.append(spec["filler_template"].format(index=index))
    lines.append(
        "End of synthetic probe. Return only the compact JSON object requested at the beginning, copying all six "
        "marker values in encounter order."
    )
    return "\n".join(lines), spec["marker_values"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:11471")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fixture = json.loads(args.fixture.read_text())
    require(fixture["official_task_content"] is False, "fixture must be nonbenchmark")
    require(fixture["protected_archive_access_permitted"] is False, "protected access must be forbidden")
    require(fixture["outcomes_opened"] is False, "outcomes must remain unopened")
    require(fixture["evaluator_access_permitted"] is False, "evaluator access must be forbidden")
    require(fixture["credential_access_permitted"] is False, "credential access must be forbidden")
    require(args.base_url == "http://127.0.0.1:11471", "endpoint must be the frozen loopback URL")

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_started = time.monotonic()
    calls: list[dict[str, Any]] = []
    prompts = arm_prompts(fixture)
    seeds = fixture["arm_seeds"]

    rr0 = generate(
        call_id="rr_phase0", base_url=args.base_url, model=args.model, fixture=fixture,
        prompt=prompts["RR_PHASE0"], seed=seeds["RR"], num_predict=320,
        output_dir=args.output_dir, json_format=True,
    )
    calls.append(rr0)
    rr0_text = json.loads((args.output_dir / "rr_phase0.response.json").read_text())["response"]
    calls.append(generate(
        call_id="rr_phase1", base_url=args.base_url, model=args.model, fixture=fixture,
        prompt=prompts["RR_PHASE1_PREFIX"] + rr0_text, seed=seeds["RR"], num_predict=512,
        output_dir=args.output_dir,
    ))
    calls.append(generate(
        call_id="os_phase1", base_url=args.base_url, model=args.model, fixture=fixture,
        prompt=prompts["OS_PHASE1"], seed=seeds["OS"], num_predict=512,
        output_dir=args.output_dir,
    ))
    calls.append(generate(
        call_id="nr_phase0", base_url=args.base_url, model=args.model, fixture=fixture,
        prompt=prompts["NR_PHASE0"], seed=seeds["NR"], num_predict=320,
        output_dir=args.output_dir,
    ))
    calls.append(generate(
        call_id="nr_phase1", base_url=args.base_url, model=args.model, fixture=fixture,
        prompt=prompts["NR_PHASE1"], seed=seeds["NR"], num_predict=512,
        output_dir=args.output_dir,
    ))

    replay = fixture["replay_probe"]
    for ordinal in (1, 2):
        calls.append(generate(
            call_id=f"replay_seed101_{ordinal}", base_url=args.base_url, model=args.model, fixture=fixture,
            prompt=replay["prompt"], seed=replay["seed"], num_predict=replay["maximum_output_tokens"],
            output_dir=args.output_dir, json_format=True,
        ))

    sensitivity = fixture["sensitivity_probe"]
    for seed in sensitivity["seeds"]:
        calls.append(generate(
            call_id=f"sensitivity_seed{seed}", base_url=args.base_url, model=args.model, fixture=fixture,
            prompt=sensitivity["prompt"], seed=seed, num_predict=sensitivity["maximum_output_tokens"],
            output_dir=args.output_dir, json_format=True,
        ))

    long_prompt, markers = long_context_prompt(fixture)
    calls.append(generate(
        call_id="long_context_seed101", base_url=args.base_url, model=args.model, fixture=fixture,
        prompt=long_prompt, seed=101, num_predict=fixture["long_context"]["maximum_output_tokens"],
        output_dir=args.output_dir, json_format=True,
    ))

    by_id = {call["call_id"]: call for call in calls}
    replay_hashes = [by_id[f"replay_seed101_{i}"]["response_text_sha256"] for i in (1, 2)]
    replay_request_hashes = [by_id[f"replay_seed101_{i}"]["request_sha256"] for i in (1, 2)]
    sensitivity_hashes = [by_id[f"sensitivity_seed{s}"]["response_text_sha256"] for s in sensitivity["seeds"]]
    long_text = json.loads((args.output_dir / "long_context_seed101.response.json").read_text())["response"]
    long_call = by_id["long_context_seed101"]
    long_status = (
        all(marker in long_text for marker in markers)
        and markers == sorted(markers, key=long_text.index)
        and long_call["prompt_eval_count"] >= fixture["long_context"]["minimum_reported_prompt_tokens"]
        and long_call["prompt_eval_count"] < fixture["decoding"]["num_ctx"]
        and long_call["done"] is True
        and long_call["done_reason"] == "stop"
    )
    call_status = all(call["done"] is True and call["done_reason"] == "stop" for call in calls)
    receipt = {
        "schema": SCHEMA,
        "status": "PASS" if call_status and len(set(replay_hashes)) == 1 and len(set(replay_request_hashes)) == 1 and len(set(sensitivity_hashes)) >= 2 and long_status else "FAIL",
        "authority": "SYNTHETIC_NONBENCHMARK_INFRASTRUCTURE_ONLY",
        "started_utc": started_utc,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "client_wall_seconds": time.monotonic() - run_started,
        "host": socket.gethostname(),
        "python": sys.version,
        "platform": platform.platform(),
        "slurm": {key: os.environ.get(key) for key in ("SLURM_JOB_ID", "SLURM_JOB_NAME", "SLURM_JOB_PARTITION", "SLURMD_NODENAME")},
        "endpoint": args.base_url,
        "model": args.model,
        "fixture_path": str(args.fixture),
        "fixture_sha256": sha256_file(args.fixture),
        "seeds": seeds,
        "calls": calls,
        "checks": {
            "all_calls_done_reason_stop": call_status,
            "rr_two_phase_same_seed_and_state_included": True,
            "os_one_phase_only": True,
            "nr_phase1_stateless_phase0_output_not_included": True,
            "same_seed_replay": {
                "status": "PASS" if len(set(replay_hashes)) == 1 and len(set(replay_request_hashes)) == 1 else "FAIL",
                "request_sha256s": replay_request_hashes,
                "response_text_sha256s": replay_hashes,
            },
            "different_seed_sensitivity": {
                "status": "PASS" if len(set(sensitivity_hashes)) >= 2 else "FAIL",
                "seeds": sensitivity["seeds"],
                "distinct_response_count": len(set(sensitivity_hashes)),
                "response_text_sha256s": sensitivity_hashes,
            },
            "long_context_no_silent_truncation_witness": {
                "status": "PASS" if long_status else "FAIL",
                "scope": "THIS_FROZEN_SYNTHETIC_PROMPT_ONLY",
                "markers_expected": markers,
                "markers_all_reproduced": all(marker in long_text for marker in markers),
                "markers_in_order": all(marker in long_text for marker in markers) and markers == sorted(markers, key=long_text.index),
                "reported_prompt_tokens": long_call["prompt_eval_count"],
                "minimum_reported_prompt_tokens": fixture["long_context"]["minimum_reported_prompt_tokens"],
                "requested_num_ctx": fixture["decoding"]["num_ctx"],
                "done_reason": long_call["done_reason"],
            },
        },
        "totals": {
            "requests": len(calls),
            "prompt_tokens": sum(call["prompt_eval_count"] for call in calls),
            "generated_tokens": sum(call["eval_count"] for call in calls),
            "ollama_total_duration_ns": sum(call["total_duration_ns"] for call in calls if isinstance(call["total_duration_ns"], int)),
        },
        "cost": {
            "billed_usd": None,
            "status": "CANNOT_CHECK_PENDING_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION",
            "gpu_seconds_and_energy_recorded_separately": True,
        },
        "forbidden_inputs": {
            "protected_archive_opened": False,
            "benchmark_task_opened": False,
            "outcome_opened": False,
            "evaluator_opened": False,
            "credential_opened": False,
        },
        "scientific_authority_delta": "NONE",
    }
    write_json(args.output_dir / "SMOKE_RECEIPT_V1.json", receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(args.output_dir / "SMOKE_RECEIPT_V1.json")}, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
