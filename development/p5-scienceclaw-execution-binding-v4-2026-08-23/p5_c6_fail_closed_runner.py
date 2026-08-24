#!/usr/bin/env python3
"""Fail-closed outer watchdog for a future fully bound ScienceClaw C6 run."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

COMMIT = "38b2f681e87272cd505c9b2671760fc3729756c2"
WHOLE_RUN_SECONDS = 21600
TERMINATION_GRACE_SECONDS = 120


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def emit(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, type=Path)
    ap.add_argument("--terminal-output", required=True, type=Path)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--upstream", type=Path)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--agent")
    ap.add_argument("--topic")
    ap.add_argument("--community")
    ap.add_argument("--skills")
    args = ap.parse_args()

    registry = load(args.registry)
    fields = registry.get("fields", {})
    blockers = sorted(key for key, value in fields.items() if value.get("status") != "BOUND")
    if blockers:
        emit(args.terminal_output, {
            "terminal": "EXECUTION_REFUSED_NONBOUND_FIELDS",
            "blocking_field_count": len(blockers),
            "blocking_fields": blockers,
            "native_execution": False,
        })
        return 3

    if args.preflight_only:
        emit(args.terminal_output, {"terminal": "PREFLIGHT_BOUND_NO_EXECUTION_REQUESTED", "native_execution": False})
        return 0

    if not all((args.upstream, args.agent, args.topic, args.community, args.skills)):
        emit(args.terminal_output, {"terminal": "EXECUTION_REFUSED_MISSING_LAUNCH_BINDING", "native_execution": False})
        return 4
    head = subprocess.check_output(["git", "-C", str(args.upstream), "rev-parse", "HEAD"], text=True).strip()
    if head != COMMIT:
        emit(args.terminal_output, {"terminal": "EXECUTION_REFUSED_SOURCE_IDENTITY", "native_execution": False, "observed_commit": head})
        return 4

    fallback_binding = fields["model_provider.fallbacks"].get("binding")
    if not isinstance(fallback_binding, dict) or not fallback_binding.get("native_fail_fast_enforced"):
        emit(args.terminal_output, {"terminal": "EXECUTION_REFUSED_NATIVE_FALLBACKS_OPEN", "native_execution": False})
        return 4

    # A future all-BOUND registry must also supply an isolated HOME and a
    # deny-by-default network/async-service policy.  These bindings are absent
    # in V4, so this branch is not reachable in this packet.
    scratch_home = fields["adapter.isolated_write_surface"]["binding"].get("scratch_home")
    if not scratch_home:
        emit(args.terminal_output, {"terminal": "EXECUTION_REFUSED_MISSING_ISOLATED_HOME", "native_execution": False})
        return 4
    env = dict(os.environ)
    env["HOME"] = str(scratch_home)
    cmd = [
        args.python,
        str(args.upstream / "bin" / "scienceclaw-post"),
        "--agent", args.agent,
        "--topic", args.topic,
        "--community", args.community,
        "--skills", args.skills,
        "--dry-run",
    ]
    proc = subprocess.Popen(cmd, env=env, start_new_session=True)
    try:
        code = proc.wait(timeout=WHOLE_RUN_SECONDS)
        emit(args.terminal_output, {"terminal": "NATIVE_PROCESS_EXIT", "exit_code": code, "native_execution": True})
        return code
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=TERMINATION_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        emit(args.terminal_output, {"terminal": "TIMEOUT", "exit_code": 124, "native_execution": True})
        return 124


if __name__ == "__main__":
    raise SystemExit(main())
