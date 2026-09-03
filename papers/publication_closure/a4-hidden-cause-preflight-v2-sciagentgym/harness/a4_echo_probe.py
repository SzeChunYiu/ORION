#!/usr/bin/env python3
"""ORION A4 lane echo probe (harness-only).

Fires the frozen echo-token request plus gym-shaped requests at a lane
endpoint (the job-local bridge, or ollama directly) from INSIDE the sbatch
job and writes verbatim receipts (request + verbatim response + job meta)
under A4_ECHO_OUTDIR (fs9).

Tests:
  plain     - single user message, "reply with exactly this token"
  gymshape  - the gym's exact request shape: system + user + assistant with
              native tool_calls + tool result + assistant with Action-text
              (no tool_calls) + dangling tool result, tools array,
              tool_choice=auto, temperature 0. Validates the lane accepts
              the message list the substrate will actually send.
  bigprompt - a >100KB prompt (exercises the bridge's stdin transport for
              the codex lane; skipped for direct ollama).

Exit code 0 iff every requested test's response contains the echo token.
"""

from __future__ import annotations

import datetime
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = os.environ["A4_ECHO_ENDPOINT"]
OUTDIR = Path(os.environ.get("A4_ECHO_OUTDIR",
                             "/projects/hep/fs9/users/scyiu/orion-a4/receipts"))
MODEL = os.environ["A4_ECHO_MODEL"]
TOKEN = os.environ.get("A4_ECHO_TOKEN", "A4_LANE_ECHO_OK")
TESTS = [t for t in os.environ.get("A4_ECHO_TESTS", "plain,gymshape").split(",") if t]
PROBE_TIMEOUT = int(os.environ.get("A4_ECHO_TIMEOUT", "600"))


def post(payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    status, body = 0, ""
    try:
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as r:
            status, body = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        status, body = -1, "EXC: %r" % (exc,)
    return status, body, time.time() - t0


def receipt(name: str, request_obj, status: int, body: str, elapsed: float):
    rec = {
        "schema": "ORION.A4.LaneEchoReceipt.v1",
        "test": name,
        "endpoint": ENDPOINT,
        "model": MODEL,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "node": socket.gethostname(),
        "recorded_utc": datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_s": round(elapsed, 1),
        "http_status": status,
        "request": request_obj,
        "response_verbatim": body,
    }
    OUTDIR.mkdir(parents=True, exist_ok=True)
    p = OUTDIR / ("%s-%s.json" % (name, os.environ.get("SLURM_JOB_ID", "nojob")))
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[echo-probe] wrote %s status=%s elapsed=%.1fs" % (p, status, elapsed),
          flush=True)


GYM_TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_data",
        "description": "Fetch a dataset by name.",
        "parameters": {
            "type": "object",
            "properties": {"dataset": {"type": "string"}},
            "required": ["dataset"],
        },
    },
}]


def build(name: str):
    if name == "plain":
        return {
            "model": MODEL,
            "messages": [{"role": "user", "content":
                "Reply with exactly this token and nothing else: %s" % TOKEN}],
            "temperature": 0,
        }
    if name == "gymshape":
        return {
            "model": MODEL,
            "messages": [
                {"role": "system", "content":
                    "You are a science assistant. Use tools via the Action "
                    "format when needed."},
                {"role": "user", "content":
                    "What is 2+2? (calibration echo task; if no tool is "
                    "needed, reply with the token %s)" % TOKEN},
                {"role": "assistant", "content": "", "tool_calls": [{
                    "id": "call_probe_1", "type": "function",
                    "function": {"name": "get_data",
                                 "arguments": "{\"dataset\": \"probe\"}"},
                }]},
                {"role": "tool", "tool_call_id": "call_probe_1",
                 "content": "{\"result\": \"probe dataset: 2+2=4\"}"},
                {"role": "assistant", "content":
                    "Action: get_data\n<arg_key>dataset</arg_key>\n"
                    "<arg_value>probe</arg_value>"},
                {"role": "tool", "tool_call_id": "call_probe_2",
                 "content": "{\"result\": \"probe dataset: 2+2=4\"}"},
            ],
            "tools": GYM_TOOLS,
            "tool_choice": "auto",
            "temperature": 0,
        }
    if name == "bigprompt":
        filler = ("Calibration filler line for transport validation. " * 6400)
        return {
            "model": MODEL,
            "messages": [{"role": "user", "content":
                filler + "\nIgnore all filler above. Reply with exactly this "
                "token and nothing else: %s" % TOKEN}],
            "temperature": 0,
        }
    raise SystemExit("unknown test %r" % name)


def main() -> int:
    results = {}
    for name in TESTS:
        payload = build(name)
        status, body, elapsed = post(payload)
        receipt(name, payload, status, body, elapsed)
        ok = TOKEN in body
        results[name] = "PASS" if ok else "FAIL"
        print("[echo-probe] %s -> %s (%s)" % (name, results[name], body[:200]),
              flush=True)
    print("ECHO_PROBE_SUMMARY: " + " ".join(
        "%s=%s" % kv for kv in results.items()), flush=True)
    return 0 if all(v == "PASS" for v in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
