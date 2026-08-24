#!/usr/bin/env python3
"""Fail-closed C5 preflight and isolated Docker command constructor.

This packet is not execution-ready.  The wrapper will not construct or execute
the Double Ratchet command until all 21 registry fields are BOUND.  Validation
uses ``--preflight`` only; it never starts a model, dataset, metric loop, task,
or protected scorer.
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


ARM_ID = "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY"
AUTHORIZATION_TOKEN = "AUTHORIZE_P5_C5_ONE_SHOT_DEVELOPMENT_EVOLUTION"


class IsolationRefusal(ValueError):
    """Fail-closed construction or execution refusal."""


def load_registry(path: Path) -> dict[str, Any]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IsolationRefusal("field registry unreadable or invalid") from exc
    if registry.get("arm_id") != ARM_ID:
        raise IsolationRefusal("wrong arm_id")
    if not isinstance(registry.get("fields"), dict):
        raise IsolationRefusal("missing fields object")
    return registry


def blockers(registry: dict[str, Any]) -> list[str]:
    fields = registry["fields"]
    required = registry.get("required_field_paths", sorted(fields))
    return [field for field in required if fields.get(field, {}).get("state") != "BOUND"]


def _existing_dir(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_dir():
        raise IsolationRefusal(f"{label} must be an existing directory")
    return resolved


def _existing_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise IsolationRefusal(f"{label} must be an existing regular file")
    return resolved


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def construct_command(
    *,
    registry: dict[str, Any],
    source_dir: Path,
    task_packet_dir: Path,
    output_dir: Path,
    aws_credentials_file: Path,
) -> list[str]:
    remaining = blockers(registry)
    if remaining:
        raise IsolationRefusal("required fields are not BOUND: " + ", ".join(remaining))

    source = _existing_dir(source_dir, "source_dir")
    task_packet = _existing_dir(task_packet_dir, "task_packet_dir")
    output = _existing_dir(output_dir, "output_dir")
    credentials = _existing_file(aws_credentials_file, "aws_credentials_file")
    if any(_overlaps(output, p) for p in (source, task_packet)):
        raise IsolationRefusal("output_dir must be disjoint from all read-only inputs")
    if any(output.iterdir()):
        raise IsolationRefusal("output_dir must be empty for a one-attempt fresh store")
    if not (task_packet / "datasets").is_dir():
        raise IsolationRefusal("task packet must contain a datasets/ directory")

    envelope = registry.get("bound_execution_envelope")
    if not isinstance(envelope, dict):
        raise IsolationRefusal("bound_execution_envelope missing")
    image = envelope.get("runtime_image")
    network = envelope.get("egress_network")
    native_command = envelope.get("native_command")
    compute = envelope.get("compute")
    wallclock = envelope.get("wallclock_seconds")
    if not isinstance(image, str) or "@sha256:" not in image:
        raise IsolationRefusal("runtime image is not content addressed")
    if not isinstance(network, str) or not network:
        raise IsolationRefusal("deny-by-default provider egress network is not bound")
    if not isinstance(native_command, list) or not all(
        isinstance(part, str) and part for part in native_command
    ):
        raise IsolationRefusal("native command is not bound")
    joined = " ".join(native_command)
    if "scripts/run_metric_evo.py" not in joined:
        raise IsolationRefusal("command is not the metric-only entrypoint")
    if any(forbidden in native_command for forbidden in ("--naive", "--golden-diff-selectable")):
        raise IsolationRefusal("unsafe metric ablation is forbidden")
    if "run_co_evo" in joined or "run_skill_evo" in joined:
        raise IsolationRefusal("joint or skill evolution is forbidden for C5")
    if not isinstance(compute, dict) or not isinstance(wallclock, dict):
        raise IsolationRefusal("compute or wallclock envelope is missing")

    # Exact source is mounted read-only.  The independently frozen candidate
    # packet overlays only datasets/, also read-only.  Native writes can reach
    # the host only through the empty results/ mount.  /tmp and provider caches
    # are disposable tmpfs mounts.  The named network must be independently
    # attested as deny-by-default with only the bound Bedrock endpoint allowed.
    inner = (
        "set -euo pipefail; "
        "cd /input/source; "
        f"timeout --signal=TERM --kill-after={int(wallclock['termination_grace'])}s "
        f"{int(wallclock['whole_c5_run'])}s "
        + shlex.join(native_command)
    )
    return [
        "docker",
        "run",
        "--rm",
        "--read-only",
        "--network",
        network,
        "--cpus",
        str(compute["vcpus"]),
        "--memory",
        f"{compute['ram_gib']}g",
        "--pids-limit",
        str(compute["pids_limit"]),
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,nodev,size=8g",
        "--tmpfs",
        "/run/cache:rw,noexec,nosuid,nodev,size=16g",
        "--mount",
        f"type=bind,src={source},dst=/input/source,readonly",
        "--mount",
        f"type=bind,src={task_packet / 'datasets'},dst=/input/source/datasets,readonly",
        "--mount",
        f"type=bind,src={task_packet},dst=/input/task,readonly",
        "--mount",
        f"type=bind,src={output},dst=/input/source/results",
        "--mount",
        f"type=bind,src={credentials},dst=/run/secrets/aws-credentials,readonly",
        "--security-opt",
        "no-new-privileges",
        "--cap-drop",
        "ALL",
        "--env",
        "AWS_SHARED_CREDENTIALS_FILE=/run/secrets/aws-credentials",
        "--env",
        "HF_HOME=/input/task/hf",
        "--env",
        "HF_DATASETS_OFFLINE=1",
        "--env",
        "HF_HUB_OFFLINE=1",
        "--env",
        "PYTHONDONTWRITEBYTECODE=1",
        image,
        "/bin/bash",
        "-lc",
        inner,
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--source-dir", type=Path)
    ap.add_argument("--task-packet-dir", type=Path)
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--aws-credentials-file", type=Path)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--emit-command", action="store_true")
    mode.add_argument("--execute", action="store_true")
    ap.add_argument("--authorization-token", default="")
    args = ap.parse_args(argv)

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
                        "protected_outcome_accessed": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0 if not remaining else 3

        needed = (
            args.source_dir,
            args.task_packet_dir,
            args.output_dir,
            args.aws_credentials_file,
        )
        if any(value is None for value in needed):
            raise IsolationRefusal("source, task packet, output and credential paths are required")
        command = construct_command(
            registry=registry,
            source_dir=args.source_dir,
            task_packet_dir=args.task_packet_dir,
            output_dir=args.output_dir,
            aws_credentials_file=args.aws_credentials_file,
        )
        if args.emit_command:
            print(shlex.join(command))
            return 0
        if args.authorization_token != AUTHORIZATION_TOKEN:
            raise IsolationRefusal("literal one-shot development authorization token absent")
        forbidden_env = (
            "P5_PROTECTED_SCORE_PATH",
            "P5_PROTECTED_PANEL_PATH",
            "P5_FINAL_OUTCOME_PATH",
        )
        if any(os.environ.get(name) for name in forbidden_env):
            raise IsolationRefusal("protected panel/outcome path entered evolution custody")
        return subprocess.run(command, check=False).returncode
    except IsolationRefusal as exc:
        print(f"P5_C5_ISOLATION_REFUSED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
