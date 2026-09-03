#!/usr/bin/env python3
"""ORION A4 job-local OpenAI-compatible bridge for the codex / claude CLI lanes.

Implements the frozen lane wiring of A4_MODEL_IDENTITY_FREEZE_V1.json /
A4_INTERVENTION_PREREG_V1.json execution_pattern.model_lane_config:

- the shipped SciAgentGYM third-party proxy base URL is NEVER contacted;
- each study family is served through its frozen lane via an OpenAI-compatible
  bridge local to the sbatch job;
- gpt-5.5        -> codex exec --model gpt-5.5 (codex-cli 0.129.0-alpha.15,
                    operator-pinned; frozen host config enforced per call:
                    model_reasoning_effort=high, service_tier=fast);
- claude-fable-5 -> claude -p --model claude-fable-5 (claude CLI 2.1.258).

The gym's OpenAI SDK client posts /v1/chat/completions here; the bridge
flattens the message list into a single unit prompt for the single-turn CLI
lane and renders the reply as a chat.completion object.

Charge accounting: the codex lane's "tokens used" stdout line is surfaced as
usage.prompt_tokens = total (completion_tokens = 0, total_tokens = total) so
any prompt+completion sum reproduces the lane-reported figure.  The claude
lane reports no machine-readable usage in plain -p mode; usage stays 0 and the
task is CANNOT_CHECK_COST per the prereg charge rule.

Subprocess transport: prompts <= A4_ARG_MAX_BYTES (default 100000) are passed
as the sole CLI argument (frozen invocation contract); larger prompts fall
back to stdin ("-"), a transport-only change logged per call.

Harness-only file: no substrate bytes are read or modified.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("A4_BRIDGE_PORT", "8765"))
FAMILY = os.environ.get("A4_BRIDGE_FAMILY", "codex")  # codex | claude
CALL_TIMEOUT = int(os.environ.get("A4_BRIDGE_CALL_TIMEOUT", "570"))
ARG_MAX_BYTES = int(os.environ.get("A4_ARG_MAX_BYTES", "100000"))
CODEX_BIN = os.environ.get("A4_CODEX_BIN", "codex")
CLAUDE_BIN = os.environ.get("A4_CLAUDE_BIN", "claude")
WORKDIR = os.environ.get("A4_BRIDGE_CWD") or tempfile.mkdtemp(prefix="a4-bridge-")

CODEX_MODEL = os.environ.get("A4_CODEX_MODEL", "gpt-5.5")
CLAUDE_MODEL = os.environ.get("A4_CLAUDE_MODEL", "claude-fable-5")

HEADER = (
    "You are executing exactly one assistant turn of an automated agent "
    "conversation. Below is the conversation transcript so far. Output ONLY "
    "the content of the next assistant message: no preamble, no commentary, "
    "no quotation marks, no explanation of your role."
)

_lock = threading.Lock()


def _content_to_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                chunks.append(str(part.get("text", "")))
            elif isinstance(part, str):
                chunks.append(part)
        return "\n".join(c for c in chunks if c)
    return str(content)


def _render_action_block(name: str, arguments_json) -> str:
    """Render a native tool_call in the Action text format the gym's ReAct
    system prompt teaches (and _parse_glm_text_tool_calls parses back)."""
    try:
        args = json.loads(arguments_json or "{}")
    except Exception:
        args = {"raw": str(arguments_json)}
    lines = [f"Action: {name}"]
    for k, v in args.items():
        lines.append(f"<arg_key>{k}</arg_key>")
        lines.append(f"<arg_value>{v}</arg_value>")
    return "\n".join(lines)


def flatten_messages(messages) -> str:
    blocks = []
    for m in messages:
        if not isinstance(m, dict):
            blocks.append(str(m))
            continue
        role = m.get("role", "user")
        text = _content_to_text(m.get("content"))
        if role == "system":
            blocks.append("[SYSTEM INSTRUCTIONS]\n" + text)
        elif role == "user":
            blocks.append("[USER]\n" + text)
        elif role == "assistant":
            body = text
            for tc in m.get("tool_calls") or []:
                try:
                    fn = tc.get("function", {})
                    body = (body + "\n" if body else "") + _render_action_block(
                        fn.get("name", "tool"), fn.get("arguments", "{}")
                    )
                except Exception:
                    pass
            blocks.append("[ASSISTANT]\n" + body)
        elif role == "tool":
            blocks.append(
                "[TOOL RESULT (call %s)]\n%s" % (m.get("tool_call_id", "?"), text)
            )
        else:
            blocks.append("[%s]\n%s" % (role.upper(), text))
    return HEADER + "\n\n" + "\n\n".join(blocks) + "\n\n[ASSISTANT]\n"


def _parse_codex_output(stdout: str):
    """codex exec (0.129.0-alpha.15) prints a banner, the echoed prompt,
    cosmetic ERROR lines, then:
        codex
        <answer text>
        tokens used
        <N>
    Return (answer_text, tokens_total_or_None)."""
    lines = stdout.splitlines()
    tokens = None
    tokens_line = None
    for i, ln in enumerate(lines):
        if ln.strip().lower() == "tokens used":
            tokens_line = i
            if i + 1 < len(lines):
                m = re.search(r"[\d,]+", lines[i + 1])
                if m:
                    try:
                        tokens = int(m.group(0).replace(",", ""))
                    except ValueError:
                        pass
    # bracket: FIRST standalone "codex" header .. FIRST "tokens used" after it.
    # Forward-first wins when the answer text itself contains a "codex" line.
    start = None
    end = None
    for i, ln in enumerate(lines):
        if start is None:
            if ln.strip() == "codex":
                start = i + 1
        elif ln.strip().lower() == "tokens used":
            end = i
            break
    if start is None:
        start = 0
    answer_lines = lines[start:end] if end is not None else lines[start:]
    answer = "\n".join(answer_lines).strip()
    if not answer:
        answer = stdout.strip()[-4000:]
    return answer, tokens


def run_codex(prompt: str):
    cmd = [
        CODEX_BIN, "exec", "--model", CODEX_MODEL, "--skip-git-repo-check",
        "-c", "model_reasoning_effort=high",
        "-c", "service_tier=fast",
    ]
    stdin_data = None
    if len(prompt.encode("utf-8")) <= ARG_MAX_BYTES:
        cmd.append(prompt)
        transport = "argv"
    else:
        cmd.append("-")
        stdin_data = prompt  # text=True subprocess: pass str, not bytes
        transport = "stdin-dash"
    t0 = time.time()
    proc = subprocess.run(
        cmd, input=stdin_data, capture_output=True, text=True,
        timeout=CALL_TIMEOUT, cwd=WORKDIR,
    )
    elapsed = time.time() - t0
    if proc.returncode != 0:
        raise RuntimeError(
            "codex exec rc=%d transport=%s stderr_tail=%r"
            % (proc.returncode, transport, proc.stderr[-800:])
        )
    answer, tokens = _parse_codex_output(proc.stdout)
    return answer, tokens, elapsed, transport


def run_claude(prompt: str):
    cmd = [CLAUDE_BIN, "-p", "--model", CLAUDE_MODEL]
    t0 = time.time()
    proc = subprocess.run(
        cmd, input=prompt.encode("utf-8"), capture_output=True,
        timeout=CALL_TIMEOUT, cwd=WORKDIR,
    )
    elapsed = time.time() - t0
    stdout_text = proc.stdout.decode("utf-8", "replace")
    if proc.returncode != 0:
        # rc!=0 is a hard lane failure (a wall banner must NOT be fed to the
        # study as an assistant turn); surface both tails for diagnosis.
        raise RuntimeError(
            "claude -p rc=%d stdout_tail=%r stderr_tail=%r"
            % (proc.returncode, stdout_text[-400:], proc.stderr[-400:])
        )
    answer = stdout_text.strip()
    return answer, None, elapsed, "stdin"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # quiet default access log
        pass

    def _send(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, {"service": "a4-cli-bridge", "family": FAMILY, "port": PORT})

    def do_POST(self):
        if self.path.rstrip("/") not in ("/v1/chat/completions",):
            self._send(404, {"error": {"message": "unknown path %s" % self.path}})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception as exc:
            self._send(400, {"error": {"message": "bad request body: %s" % exc}})
            return
        messages = body.get("messages") or []
        prompt = flatten_messages(messages)
        model = body.get("model", CODEX_MODEL if FAMILY == "codex" else CLAUDE_MODEL)
        t0 = time.time()
        try:
            with _lock:  # serialise lane calls; the study loop is sequential
                if FAMILY == "codex":
                    answer, tokens, elapsed, transport = run_codex(prompt)
                elif FAMILY == "claude":
                    answer, tokens, elapsed, transport = run_claude(prompt)
                else:
                    raise RuntimeError("unknown A4_BRIDGE_FAMILY %r" % FAMILY)
        except Exception as exc:
            sys.stderr.write(
                "[a4-bridge] %s model=%s prompt_bytes=%d FAIL %.1fs %s\n"
                % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), model,
                   len(prompt.encode("utf-8")), time.time() - t0, exc)
            )
            sys.stderr.flush()
            self._send(500, {"error": {"message": str(exc), "type": "a4_bridge_error"}})
            return
        usage = {
            "prompt_tokens": tokens or 0,
            "completion_tokens": 0,
            "total_tokens": tokens or 0,
        }
        sys.stderr.write(
            "[a4-bridge] %s model=%s prompt_bytes=%d transport=%s rc=ok "
            "tokens=%s elapsed=%.1fs answer_chars=%d\n"
            % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), model,
               len(prompt.encode("utf-8")), transport, tokens, elapsed, len(answer))
        )
        sys.stderr.flush()
        self._send(200, {
            "id": "a4bridge-%s" % uuid.uuid4().hex[:12],
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": answer, "tool_calls": None},
                "finish_reason": "stop",
            }],
            "usage": usage,
        })


def main():
    sys.stderr.write(
        "[a4-bridge] starting family=%s port=%d codex_bin=%s claude_bin=%s cwd=%s\n"
        % (FAMILY, PORT, CODEX_BIN, CLAUDE_BIN, WORKDIR)
    )
    sys.stderr.flush()
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
