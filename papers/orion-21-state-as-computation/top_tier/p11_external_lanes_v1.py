#!/usr/bin/env python3
"""P11 external campaign — model lane adapters (P12 invocation-contract pattern).

Lanes (exact identities frozen in P11_EXTERNAL_MODEL_IDENTITY_FREEZE_V1.json):
  gpt-5.5-codexcli     codex exec --skip-git-repo-check <prompt>   (single turn)
  claude-fable-5-cli   claude -p --model claude-fable-5 --output-format json
  llama3.1-8b-ollama   POST /api/generate (local ollama serve)

Each call returns a record: output text, rc, seconds, input_tokens, output_tokens,
token_accounting_method. Token split rule (frozen): claude/ollama report the split
natively; codex reports a combined "tokens used" total, from which
output_tokens = ceil(len(stdout_text)/4) is subtracted (declared estimate).
Retry: 3 attempts, exponential backoff 30s*2^n on rc!=0 or empty output.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

CODEX_BIN = os.environ.get("P11_CODEX_BIN", "codex")
CLAUDE_BIN = os.environ.get("P11_CLAUDE_BIN", "claude")
OLLAMA_URL = os.environ.get("P11_OLLAMA_URL", "http://127.0.0.1:11434")
CODEX_TIMEOUT = int(os.environ.get("P11_CODEX_TIMEOUT", "1800"))
CLAUDE_TIMEOUT = int(os.environ.get("P11_CLAUDE_TIMEOUT", "1800"))
OLLAMA_TIMEOUT = int(os.environ.get("P11_OLLAMA_TIMEOUT", "3600"))


def _est_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def _codex_call(prompt: str, timeout: int) -> dict:
    t0 = time.time()
    proc = subprocess.run([CODEX_BIN, "exec", "--skip-git-repo-check", prompt],
                          capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL, check=False)
    out = proc.stdout or ""
    m = re.search(r"tokens used:\s*(\d+)", out)
    total = int(m.group(1)) if m else None
    # codex streams banners around the message; the agent reply is the last
    # non-meta block. Heuristic (frozen): strip lines that are metadata.
    lines = [l for l in out.splitlines() if l.strip()]
    body = []
    for l in lines:
        if l.startswith(("tokens used", "[", "user", "codex", "OpenAI", "model:", "thinking", "metadata")):
            continue
        body.append(l)
    text = "\n".join(body).strip()
    if total is None:
        in_t, out_t = _est_tokens(prompt), _est_tokens(text)
        method = "chars4_estimate"
    else:
        out_t = min(_est_tokens(text) + 64, total)
        in_t, method = total - out_t, "codex_total_minus_chars4_output"
    return {"output": text, "rc": proc.returncode, "seconds": round(time.time() - t0, 3),
            "input_tokens": max(0, in_t), "output_tokens": max(0, out_t),
            "token_accounting_method": method, "stderr_tail": (proc.stderr or "")[-400:]}


def _claude_call(prompt: str, timeout: int) -> dict:
    t0 = time.time()
    proc = subprocess.run([CLAUDE_BIN, "-p", prompt, "--model", "claude-fable-5",
                           "--output-format", "json", "--verbose"],
                          capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL, check=False)
    out = proc.stdout or ""
    try:
        payload = json.loads(out)
        usage = payload.get("usage") or payload.get("message", {}).get("usage") or {}
        in_t = int(usage.get("input_tokens", 0)) or _est_tokens(prompt)
        out_t = int(usage.get("output_tokens", 0)) or _est_tokens(payload.get("result", ""))
        text = payload.get("result") or ""
        method = "cli_json_usage"
    except (json.JSONDecodeError, ValueError):
        text, in_t, out_t, method = out.strip(), _est_tokens(prompt), _est_tokens(out), "chars4_estimate"
    return {"output": text, "rc": proc.returncode, "seconds": round(time.time() - t0, 3),
            "input_tokens": in_t, "output_tokens": out_t,
            "token_accounting_method": method, "stderr_tail": (proc.stderr or "")[-400:]}


def _ollama_call(prompt: str, timeout: int) -> dict:
    t0 = time.time()
    req = urllib.request.Request(
        OLLAMA_URL.rstrip("/") + "/api/generate",
        data=json.dumps({"model": "llama3.1:8b", "prompt": prompt, "stream": False,
                         "options": {"num_ctx": 131072, "temperature": 0.6,
                                     "top_p": 0.9, "seed": 42}}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode())
    return {"output": payload.get("response", "").strip(), "rc": 0,
            "seconds": round(time.time() - t0, 3),
            "input_tokens": int(payload.get("prompt_eval_count", 0)) or _est_tokens(prompt),
            "output_tokens": int(payload.get("eval_count", 0)),
            "token_accounting_method": "ollama_native", "stderr_tail": ""}


def _ollama_embed(inputs: list[str]) -> dict:
    t0 = time.time()
    req = urllib.request.Request(
        OLLAMA_URL.rstrip("/") + "/api/embed",
        data=json.dumps({"model": "bge-m3", "input": inputs}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        payload = json.loads(resp.read().decode())
    vecs = payload.get("embeddings") or []
    return {"vectors": vecs, "seconds": round(time.time() - t0, 3),
            "embedded_tokens": sum(_est_tokens(x) for x in inputs),
            "embedding_calls": 1, "rc": 0}


_CALLERS = {"gpt-5.5-codexcli": _codex_call, "claude-fable-5-cli": _claude_call,
            "llama3.1-8b-ollama": _ollama_call}
_TIMEOUTS = {"gpt-5.5-codexcli": CODEX_TIMEOUT, "claude-fable-5-cli": CLAUDE_TIMEOUT,
             "llama3.1-8b-ollama": OLLAMA_TIMEOUT}


def call(lane_id: str, prompt: str) -> dict:
    caller = _CALLERS[lane_id]
    last: dict | None = None
    for attempt in range(3):
        try:
            rec = caller(prompt, _TIMEOUTS[lane_id])
            if rec["rc"] == 0 and rec["output"].strip():
                rec["attempts"] = attempt + 1
                return rec
            last = rec
        except (subprocess.TimeoutExpired, urllib.error.URLError, OSError) as exc:
            last = {"output": "", "rc": -1, "seconds": 0.0, "input_tokens": 0,
                    "output_tokens": 0, "token_accounting_method": "failed",
                    "stderr_tail": str(exc)[-400:]}
        time.sleep(30 * (2 ** attempt))
    last["attempts"] = 3
    return last


def embed(inputs: list[str]) -> dict:
    for attempt in range(3):
        try:
            rec = _ollama_embed(inputs)
            if rec["rc"] == 0 and rec["vectors"]:
                return rec
        except (urllib.error.URLError, OSError) as exc:
            time.sleep(30 * (2 ** attempt))
            last_err = exc
    raise RuntimeError(f"embedding failed after retries: {last_err}")


LANES = ("gpt-5.5-codexcli", "claude-fable-5-cli", "llama3.1-8b-ollama")
