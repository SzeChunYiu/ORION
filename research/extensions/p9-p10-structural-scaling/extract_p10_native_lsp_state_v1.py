from __future__ import annotations

import argparse
import hashlib
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# The legacy extractor imports the publication framework from a historical
# candidate path that contains tests but not the package.  The clean CI shards
# do not inherit the separate P9/P10 workflow's PYTHONPATH, so bind the canonical
# framework before importing the shared feature helpers.
ROOT = Path(__file__).resolve().parents[3]
FRAMEWORK = ROOT / "papers" / "orion-learning-machine" / "framework"
sys.path.insert(0, str(FRAMEWORK))

from extract_p10_native_trace_state_v1 import (  # noqa: E402
    BULLET,
    EXTRACTOR_SCHEMA,
    LEAN_TOOLCHAIN,
    MANIFEST,
    MATHLIB_COMMIT,
    sha_bytes,
    sha_file,
    source_events,
    state_features,
)

ACCESS_MODE = "LEAN_LSP_PLAIN_GOAL_DIRECT_V1"
MIN_ELIGIBLE = 9_474
CALIBRATION_TEXT = """example : α → α := by
  intro a
  exact a
"""
CALIBRATION_FILE = "OrionP10LspCalibration.lean"


class LspFailure(RuntimeError):
    pass


class LspTimeout(LspFailure):
    pass


class LspProtocolError(LspFailure):
    pass


class LeanLspClient:
    def __init__(self, checkout: Path, timeout: float):
        self.checkout = checkout
        self.timeout = timeout
        self.next_id = 1
        self.buffer = bytearray()
        self.proc = subprocess.Popen(
            ["lake", "env", "lean", "--server"],
            cwd=checkout,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )
        if self.proc.stdin is None or self.proc.stdout is None:
            raise LspProtocolError("failed to open Lean LSP pipes")
        self.stdout_fd = self.proc.stdout.fileno()

    def _send(self, payload: dict[str, Any]) -> None:
        if self.proc.poll() is not None:
            raise LspProtocolError(f"Lean server exited with {self.proc.returncode}")
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        frame = f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii") + raw
        assert self.proc.stdin is not None
        try:
            self.proc.stdin.write(frame)
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise LspProtocolError(f"Lean server write failed: {exc}") from exc

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._send(payload)

    def request(self, method: str, params: dict[str, Any] | None = None) -> tuple[int, Any]:
        request_id = self.next_id
        self.next_id += 1
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._send(payload)
        deadline = time.monotonic() + self.timeout
        while True:
            message = self._read_message(deadline)
            if message.get("id") != request_id:
                # Server notifications and stale responses are not state receipts.
                continue
            if "error" in message:
                raise LspProtocolError(
                    f"{method} JSON-RPC error: {json.dumps(message['error'], sort_keys=True)}"
                )
            return request_id, message.get("result")

    def _fill(self, deadline: float) -> None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise LspTimeout("Lean LSP response timeout")
        ready, _, _ = select.select([self.stdout_fd], [], [], remaining)
        if not ready:
            raise LspTimeout("Lean LSP response timeout")
        chunk = os.read(self.stdout_fd, 65536)
        if not chunk:
            code = self.proc.poll()
            raise LspProtocolError(f"Lean server stdout closed (exit={code})")
        self.buffer.extend(chunk)

    def _read_message(self, deadline: float) -> dict[str, Any]:
        marker = b"\r\n\r\n"
        while marker not in self.buffer:
            self._fill(deadline)
        header_end = self.buffer.index(marker)
        header = bytes(self.buffer[:header_end]).decode("ascii", errors="strict")
        content_length: int | None = None
        for line in header.split("\r\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            if key.strip().lower() == "content-length":
                content_length = int(value.strip())
        if content_length is None or content_length < 0:
            raise LspProtocolError("LSP frame missing valid Content-Length")
        payload_start = header_end + len(marker)
        payload_end = payload_start + content_length
        while len(self.buffer) < payload_end:
            self._fill(deadline)
        raw = bytes(self.buffer[payload_start:payload_end])
        del self.buffer[:payload_end]
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise LspProtocolError(f"invalid LSP JSON payload: {exc}") from exc
        if not isinstance(value, dict):
            raise LspProtocolError("LSP payload is not a JSON object")
        return value

    def initialize(self) -> None:
        _, result = self.request(
            "initialize",
            {
                "processId": None,
                "rootUri": self.checkout.as_uri(),
                "capabilities": {},
            },
        )
        if not isinstance(result, dict):
            raise LspProtocolError("Lean initialize returned non-object result")
        self.notify("initialized", {})

    def close(self) -> None:
        if self.proc.poll() is not None:
            return
        try:
            self.request("shutdown", None)
        except Exception:
            pass
        try:
            self.notify("exit", None)
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)


def tactic_token_column(line: str) -> int:
    bullet = BULLET.match(line)
    if bullet:
        column = bullet.start(3)
        while column < len(line) and line[column].isspace():
            column += 1
        return column
    return len(line) - len(line.lstrip())


def goal_state(result: Any) -> str | None:
    if not isinstance(result, dict):
        return None
    goals = result.get("goals")
    if not isinstance(goals, list) or not goals:
        return None
    if not all(isinstance(goal, str) and goal.strip() for goal in goals):
        return None
    return "\n\n".join(goal.strip() for goal in goals)


def calibration(client: LeanLspClient, checkout: Path) -> dict[str, Any]:
    path = checkout / CALIBRATION_FILE
    uri = path.resolve().as_uri()
    client.notify(
        "textDocument/didOpen",
        {
            "textDocument": {
                "uri": uri,
                "languageId": "lean4",
                "version": 1,
                "text": CALIBRATION_TEXT,
            }
        },
    )
    try:
        client.request("textDocument/waitForDiagnostics", {"uri": uri, "version": 1})
        first_id, first_result = client.request(
            "$/lean/plainGoal",
            {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 2}},
        )
        second_id, second_result = client.request(
            "$/lean/plainGoal",
            {"textDocument": {"uri": uri}, "position": {"line": 2, "character": 2}},
        )
    finally:
        client.notify("textDocument/didClose", {"textDocument": {"uri": uri}})

    first_state = goal_state(first_result)
    second_state = goal_state(second_result)
    if first_state is None or second_state is None:
        raise LspProtocolError("synthetic plainGoal calibration returned no usable goal")
    first_features, _, first_norm = state_features(first_state)
    second_features, _, second_norm = state_features(second_state)
    checks = {
        "intro_goal_is_implication": first_features["goal_shape"] == "implication_function",
        "intro_context_empty": int(first_features["context_cardinality"]) == 0,
        "exact_context_nonempty": int(second_features["context_cardinality"]) >= 1,
        "exact_goal_count_positive": int(second_features["num_goals"]) >= 1,
    }
    if not all(checks.values()):
        raise LspProtocolError(f"synthetic cursor calibration failed: {checks}")
    return {
        "terminal": "P10_NATIVE_LSP_CURSOR_CALIBRATION_GREEN",
        "checks": checks,
        "request_ids": [first_id, second_id],
        "normalized_state_sha256": [first_norm, second_norm],
    }


def runtime_identity(checkout: Path) -> dict[str, str]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=checkout,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    toolchain = (checkout / "lean-toolchain").read_text(encoding="utf-8").strip()
    if commit != MATHLIB_COMMIT:
        raise SystemExit(f"Mathlib checkout mismatch: {commit}")
    if toolchain != LEAN_TOOLCHAIN:
        raise SystemExit(f"Lean toolchain mismatch: {toolchain}")
    return {"mathlib_commit": commit, "lean_toolchain": toolchain}


def access_receipt(
    transition_id: str,
    request_id: int,
    line: int,
    character: int,
    state_sha256: str,
) -> str:
    material = {
        "access_mode": ACCESS_MODE,
        "transition_id": transition_id,
        "jsonrpc_request_id": request_id,
        "position": {"line": line, "character": character},
        "state_sha256": state_sha256,
    }
    return sha_bytes(json.dumps(material, sort_keys=True, separators=(",", ":")).encode())


def transition_row(
    *,
    item: dict[str, Any],
    event: dict[str, Any],
    state: str,
    request_id: int,
    line: int,
    character: int,
) -> dict[str, Any]:
    transition_id = str(event["transition_id"])
    state_vector, dependency_vector, normalized_digest = state_features(state)
    state_digest = sha_bytes(state.encode())
    receipt_material = {
        "transition_id": transition_id,
        "source_path": item["path"],
        "source_sha256": item["sha256"],
        "theorem_name": event["theorem_name"],
        "action_index": event["action_index"],
        "previous_family": event["previous_family"],
        "true_action": event["family"],
        "state_sha256": state_digest,
        "mathlib_commit": MATHLIB_COMMIT,
        "lean_toolchain": LEAN_TOOLCHAIN,
    }
    receipt_sha = sha_bytes(
        json.dumps(receipt_material, sort_keys=True, separators=(",", ":")).encode()
    )
    return {
        **receipt_material,
        "top_module": item["top_module"],
        "normalized_state_sha256": normalized_digest,
        "state_features": state_vector,
        "dependency_features": dependency_vector,
        "receipt_sha256": receipt_sha,
        "access_receipt_sha256": access_receipt(
            transition_id, request_id, line, character, state_digest
        ),
        "lsp_request_id": request_id,
        "query_position": {"line": line, "character": character},
    }


def start_calibrated(checkout: Path, timeout: float) -> tuple[LeanLspClient, dict[str, Any]]:
    client = LeanLspClient(checkout, timeout)
    try:
        client.initialize()
        cal = calibration(client, checkout)
    except Exception:
        client.close()
        raise
    return client, cal


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mathlib-checkout", required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--request-timeout", type=float, default=240.0)
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard index")

    checkout = Path(args.mathlib_checkout).resolve()
    runtime = runtime_identity(checkout)
    manifest = json.loads(MANIFEST.read_text())
    if manifest["source"]["commit"] != MATHLIB_COMMIT:
        raise SystemExit("manifest Mathlib commit mismatch")
    if manifest["source"]["lean_toolchain"] != LEAN_TOOLCHAIN:
        raise SystemExit("manifest Lean toolchain mismatch")

    selected = [
        item
        for item in manifest["files"]
        if int(hashlib.sha256(item["path"].encode()).hexdigest(), 16) % args.shard_count
        == args.shard_index
    ]
    rows: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    denominator = 0
    eligible = 0
    seen_transition_ids: set[str] = set()
    calibrations: list[dict[str, Any]] = []
    server: LeanLspClient | None = None
    server_generation = 0
    fatal_calibration = False

    def restart_server() -> bool:
        nonlocal server, server_generation, fatal_calibration
        if server is not None:
            server.close()
        server = None
        try:
            client, cal = start_calibrated(checkout, args.request_timeout)
        except Exception as exc:
            calibrations.append(
                {
                    "server_generation": server_generation + 1,
                    "terminal": "CANNOT_CHECK_LSP_CURSOR_SEMANTICS",
                    "error": str(exc),
                }
            )
            fatal_calibration = True
            return False
        server_generation += 1
        cal = {**cal, "server_generation": server_generation}
        calibrations.append(cal)
        server = client
        return True

    restart_server()

    for item in selected:
        path = checkout / item["path"]
        if not path.is_file() or sha_file(path) != item["sha256"]:
            raise SystemExit(f"source identity mismatch: {item['path']}")
        original = path.read_text(encoding="utf-8")
        events, transition_count = source_events(original, item["path"])
        denominator += transition_count
        transition_events = [event for event in events if event["is_transition"]]

        if fatal_calibration or server is None:
            files.append(
                {
                    "path": item["path"],
                    "top_module": item["top_module"],
                    "transitions": transition_count,
                    "eligible_transitions": 0,
                    "status": "CANNOT_CHECK_LSP_CURSOR_SEMANTICS",
                }
            )
            continue

        uri = path.resolve().as_uri()
        file_rows: list[dict[str, Any]] = []
        request_failures: list[dict[str, Any]] = []
        server_failed = False
        try:
            server.notify(
                "textDocument/didOpen",
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "lean4",
                        "version": 1,
                        "text": original,
                    }
                },
            )
            server.request("textDocument/waitForDiagnostics", {"uri": uri, "version": 1})

            source_lines = original.splitlines()
            for event in transition_events:
                transition_id = str(event["transition_id"])
                if transition_id in seen_transition_ids:
                    raise SystemExit(f"duplicate transition id: {transition_id}")
                seen_transition_ids.add(transition_id)
                line = int(event["line_zero_index"])
                if not 0 <= line < len(source_lines):
                    request_failures.append(
                        {"transition_id": transition_id, "reason": "SOURCE_LINE_OUT_OF_RANGE"}
                    )
                    continue
                character = tactic_token_column(source_lines[line])
                try:
                    request_id, result = server.request(
                        "$/lean/plainGoal",
                        {
                            "textDocument": {"uri": uri},
                            "position": {"line": line, "character": character},
                        },
                    )
                except (LspTimeout, LspProtocolError) as exc:
                    request_failures.append(
                        {
                            "transition_id": transition_id,
                            "reason": "LSP_REQUEST_FAILURE",
                            "error": str(exc),
                        }
                    )
                    server_failed = True
                    break
                state = goal_state(result)
                if state is None:
                    request_failures.append(
                        {"transition_id": transition_id, "reason": "LSP_NULL_OR_EMPTY_GOAL"}
                    )
                    continue
                file_rows.append(
                    transition_row(
                        item=item,
                        event=event,
                        state=state,
                        request_id=request_id,
                        line=line,
                        character=character,
                    )
                )
        except (LspTimeout, LspProtocolError) as exc:
            request_failures.append(
                {"transition_id": None, "reason": "LSP_FILE_FAILURE", "error": str(exc)}
            )
            server_failed = True
        finally:
            if server is not None and not server_failed:
                try:
                    server.notify("textDocument/didClose", {"textDocument": {"uri": uri}})
                except Exception:
                    server_failed = True
            if sha_file(path) != item["sha256"]:
                raise SystemExit(f"source bytes changed during LSP access: {item['path']}")

        # A failed file is never retried. Rows returned before a failure remain
        # valid; missing transitions remain explicitly ineligible.
        rows.extend(file_rows)
        eligible += len(file_rows)
        files.append(
            {
                "path": item["path"],
                "top_module": item["top_module"],
                "transitions": transition_count,
                "eligible_transitions": len(file_rows),
                "status": (
                    "LSP_GOAL_GREEN"
                    if len(file_rows) == transition_count
                    else "PARTIAL_LSP_GOAL"
                    if file_rows
                    else "LSP_GOAL_UNAVAILABLE"
                ),
                "request_failures": request_failures,
                "server_generation": server_generation,
            }
        )
        if server_failed:
            restart_server()

    if server is not None:
        server.close()

    terminal = (
        "P10_NATIVE_LSP_SHARD_COMPLETE"
        if not fatal_calibration
        else "CANNOT_CHECK_LSP_CURSOR_SEMANTICS"
    )
    output = {
        "schema": EXTRACTOR_SCHEMA,
        "successor_study": "P10_NATIVE_LSP_ACCESS_SUCCESSOR_V1",
        "extractor_receipt_mode": ACCESS_MODE,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "mathlib_commit": runtime["mathlib_commit"],
        "lean_toolchain": runtime["lean_toolchain"],
        "selected_files": len(selected),
        "transition_denominator": denominator,
        "eligible_transitions": eligible,
        "eligibility_fraction": eligible / denominator if denominator else 1.0,
        "global_minimum_eligible": MIN_ELIGIBLE,
        "calibrations": calibrations,
        "rows": rows,
        "files": files,
        "terminal": terminal,
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: output[key]
                for key in (
                    "schema",
                    "successor_study",
                    "extractor_receipt_mode",
                    "shard_index",
                    "shard_count",
                    "selected_files",
                    "transition_denominator",
                    "eligible_transitions",
                    "eligibility_fraction",
                    "global_minimum_eligible",
                    "terminal",
                )
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
