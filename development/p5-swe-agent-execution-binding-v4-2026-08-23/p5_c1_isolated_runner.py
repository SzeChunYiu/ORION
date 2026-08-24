#!/usr/bin/env python3
"""Fail-closed C1 execution wrapper and Docker command constructor.

The V4 packet is intentionally not execution-ready.  ``--preflight`` checks
the frozen field registry and reports blockers.  ``--emit-command`` constructs
the exact command only after every required field is BOUND.  ``--execute`` is
additionally gated by a literal authorization token.  No comparator is run by
this file during packet validation.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


AUTHORIZATION_TOKEN = "AUTHORIZE_P5_C1_ONE_SHOT_EXECUTION"
ARM_ID = "C1_FIXED_AGENT__SWE_AGENT"


class IsolationRefusal(ValueError):
    """Fail-closed execution refusal."""


def load_registry(path: Path) -> dict[str, Any]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IsolationRefusal("field registry is unreadable or invalid") from exc
    if registry.get("arm_id") != ARM_ID:
        raise IsolationRefusal("field registry has the wrong arm_id")
    fields = registry.get("fields")
    if not isinstance(fields, dict):
        raise IsolationRefusal("field registry has no fields object")
    return registry


def blockers(registry: dict[str, Any]) -> list[str]:
    fields = registry["fields"]
    required = registry.get("required_field_paths", sorted(fields))
    return [field for field in required if fields.get(field, {}).get("state") != "BOUND"]


def _regular_dir(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_dir():
        raise IsolationRefusal(f"{label} must be an existing directory")
    return resolved


def construct_command(
    *,
    registry: dict[str, Any],
    source_dir: Path,
    task_seed_dir: Path,
    output_dir: Path,
) -> list[str]:
    remaining = blockers(registry)
    if remaining:
        raise IsolationRefusal("required fields are not BOUND: " + ", ".join(remaining))

    source = _regular_dir(source_dir, "source_dir")
    task_seed = _regular_dir(task_seed_dir, "task_seed_dir")
    output = _regular_dir(output_dir, "output_dir")
    if source == output or task_seed == output or output in source.parents or output in task_seed.parents:
        raise IsolationRefusal("output_dir must be disjoint from read-only inputs")

    envelope = registry["bound_execution_envelope"]
    image = envelope["runtime_image"]
    compute = envelope["compute"]
    wallclock = envelope["wallclock_seconds"]

    # Root is read-only; only /run/p5-output is host-writable.  The task seed and
    # SWE-agent source are mounted read-only and copied into ephemeral /work.
    inner = (
        "set -euo pipefail; "
        "cp -a /input/task/. /work/task/; "
        "cd /work/task; "
        "timeout --signal=TERM --kill-after=30s "
        f"{int(wallclock['per_case'])}s "
        "env PYTHONPATH=/input/source python -m sweagent.run.run run "
        "--config /work/task/run_config.yaml --output_dir /work/native-output; "
        "cp -a /work/native-output/. /run/p5-output/"
    )
    return [
        "docker",
        "run",
        "--rm",
        "--read-only",
        "--network",
        "none",
        "--cpus",
        str(compute["vcpus"]),
        "--memory",
        f"{compute['ram_gib']}g",
        "--pids-limit",
        str(compute["pids_limit"]),
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,nodev,size=1g",
        "--tmpfs",
        "/work:rw,nosuid,nodev,size=8g",
        "--mount",
        f"type=bind,src={source},dst=/input/source,readonly",
        "--mount",
        f"type=bind,src={task_seed},dst=/input/task,readonly",
        "--mount",
        f"type=bind,src={output},dst=/run/p5-output",
        "--security-opt",
        "no-new-privileges",
        "--cap-drop",
        "ALL",
        image,
        "/bin/bash",
        "-lc",
        inner,
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--task-seed-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--emit-command", action="store_true")
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

        if args.source_dir is None or args.task_seed_dir is None or args.output_dir is None:
            raise IsolationRefusal("source, task-seed and output directories are required")
        command = construct_command(
            registry=registry,
            source_dir=args.source_dir,
            task_seed_dir=args.task_seed_dir,
            output_dir=args.output_dir,
        )
        if args.emit_command:
            print(shlex.join(command))
            return 0
        if args.authorization_token != AUTHORIZATION_TOKEN:
            raise IsolationRefusal("literal one-shot authorization token absent")
        if os.environ.get("P5_PROTECTED_SCORE_PATH"):
            raise IsolationRefusal("protected score path must not enter candidate execution custody")
        return subprocess.run(command, check=False).returncode
    except IsolationRefusal as exc:
        print(f"P5_C1_ISOLATION_REFUSED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
