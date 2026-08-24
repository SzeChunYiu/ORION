#!/usr/bin/env python3
"""Fail-closed C2 gate and whole-run watchdog.

This V4 packet is intentionally not execution-ready.  ``--preflight`` reports
the exact registry blockers.  ``--execute`` remains impossible until every
required field is BOUND, an exact runtime launcher is present in the registry,
and a literal one-shot authorization token is supplied.  The watchdog applies
the frozen wallclock to one process group; it does not claim to isolate MOSS's
Docker daemon or dynamic trial containers.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any


ARM_ID = "C2_DIRECT_SELF_EDIT__MOSS"
AUTHORIZATION_TOKEN = "AUTHORIZE_P5_C2_ONE_SHOT_EXECUTION"
PROTECTED_ENV_PREFIXES = ("P5_PROTECTED_", "P5_GOLD_", "P5_SCORER_")


class ExecutionRefusal(ValueError):
    """Typed fail-closed execution refusal."""


def load_registry(path: Path) -> dict[str, Any]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExecutionRefusal("field registry is unreadable or invalid") from exc
    if registry.get("arm_id") != ARM_ID:
        raise ExecutionRefusal("field registry has the wrong arm_id")
    if not isinstance(registry.get("fields"), dict):
        raise ExecutionRefusal("field registry has no fields object")
    return registry


def blockers(registry: dict[str, Any]) -> list[str]:
    fields = registry["fields"]
    required = registry.get("required_field_paths", sorted(fields))
    return [field for field in required if fields.get(field, {}).get("state") != "BOUND"]


def runtime_launcher(registry: dict[str, Any]) -> list[str]:
    envelope = registry.get("bound_execution_envelope")
    if not isinstance(envelope, dict):
        raise ExecutionRefusal("bound_execution_envelope is absent")
    launcher = envelope.get("runtime_launcher")
    if not isinstance(launcher, list) or not launcher or not all(
        isinstance(item, str) and item for item in launcher
    ):
        raise ExecutionRefusal("exact runtime launcher is not bound")
    return launcher


def execute_with_watchdog(registry: dict[str, Any]) -> int:
    envelope = registry["bound_execution_envelope"]
    wallclock = envelope.get("wallclock_seconds", {})
    try:
        limit = int(wallclock["whole_c2_run"])
        grace = int(wallclock["termination_grace"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ExecutionRefusal("wallclock envelope is invalid") from exc
    if limit <= 0 or grace <= 0:
        raise ExecutionRefusal("wallclock and grace must be positive")

    protected_env = sorted(
        key for key in os.environ if key.startswith(PROTECTED_ENV_PREFIXES)
    )
    if protected_env:
        raise ExecutionRefusal(
            "protected/gold/scorer environment must not enter candidate custody: "
            + ", ".join(protected_env)
        )

    proc = subprocess.Popen(runtime_launcher(registry), start_new_session=True)
    try:
        return proc.wait(timeout=limit)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        return 124


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization-token", default="")
    args = parser.parse_args(argv)

    try:
        registry = load_registry(args.registry)
        remaining = blockers(registry)
        if args.preflight:
            print(
                json.dumps(
                    {
                        "arm_id": ARM_ID,
                        "execution_ready": not remaining,
                        "blocking_field_count": len(remaining),
                        "blocking_fields": remaining,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0 if not remaining else 3
        if remaining:
            raise ExecutionRefusal("required fields are not BOUND: " + ", ".join(remaining))
        if args.authorization_token != AUTHORIZATION_TOKEN:
            raise ExecutionRefusal("literal one-shot authorization token absent")
        return execute_with_watchdog(registry)
    except ExecutionRefusal as exc:
        print(f"P5_C2_EXECUTION_REFUSED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
