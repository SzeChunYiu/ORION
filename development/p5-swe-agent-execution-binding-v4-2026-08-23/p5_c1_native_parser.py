#!/usr/bin/env python3
"""Outcome-blind parser for the pinned SWE-agent C1 native trajectory.

This parser never reads a scorer, protected test, gold patch, benchmark result,
or comparator outcome.  It retains SWE-agent's exact ``info.exit_status`` and
hashes (rather than reproduces) the candidate submission.  It deliberately
emits ``UNRESOLVED``: responsibility-class emission remains the separate V3
certificate/action/invariance operation and must stay outside this native
terminal parser.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ARM_ID = "C1_FIXED_AGENT__SWE_AGENT"
SCHEMA_VERSION = "orion.p5.c1.swe-agent-native-terminal.v4"
MAX_TRAJECTORY_BYTES = 50 * 1024 * 1024

# A candidate trajectory has no need for any of these evaluator-side fields.
# Fail closed rather than accidentally bridge protected custody into C1.
PROHIBITED_KEYS = frozenset(
    {
        "FAIL_TO_PASS",
        "PASS_TO_PASS",
        "evaluation_report",
        "gold_patch",
        "protected_outcome",
        "protected_score",
        "resolved",
        "reward",
        "score",
        "test_patch",
    }
)


class NativeParseError(ValueError):
    """Typed fail-closed parser error."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _find_prohibited_keys(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in PROHIBITED_KEYS:
                hits.append(child_path)
            hits.extend(_find_prohibited_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_find_prohibited_keys(child, f"{path}[{index}]"))
    return hits


def _native_status(exit_status: str | None, submission: str | None, steps: int) -> str:
    """Map native completion shape without treating an autosubmission as success."""
    if exit_status == "submitted" and bool(submission):
        return "COMPLETE_SUCCESS"
    if exit_status and exit_status.startswith("submitted ("):
        return "PARTIAL"
    if exit_status is None:
        return "EMPTY" if steps == 0 and not submission else "PARTIAL"
    if "timeout" in exit_status or "total_execution_time" in exit_status:
        return "TIMEOUT"
    if exit_status in {"exit_forfeit", "exit_cost", "exit_context", "exit_command"}:
        return "ABSTAIN"
    if exit_status.startswith("skipped"):
        return "INVALID"
    if exit_status in {
        "exit_api",
        "exit_environment_error",
        "exit_error",
        "exit_format",
    }:
        return "ERROR"
    return "INVALID"


def parse_trajectory_bytes(raw: bytes, *, expected_instance_id: str | None = None) -> dict[str, Any]:
    if len(raw) > MAX_TRAJECTORY_BYTES:
        raise NativeParseError(f"trajectory exceeds {MAX_TRAJECTORY_BYTES} bytes")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NativeParseError("trajectory is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise NativeParseError("trajectory root must be an object")

    prohibited = _find_prohibited_keys(value)
    if prohibited:
        raise NativeParseError("protected/evaluator-side keys are forbidden: " + ", ".join(sorted(prohibited)))

    info = value.get("info")
    trajectory = value.get("trajectory")
    if not isinstance(info, dict):
        raise NativeParseError("trajectory.info must be an object")
    if not isinstance(trajectory, list):
        raise NativeParseError("trajectory.trajectory must be an array")

    exit_status_value = info.get("exit_status")
    if exit_status_value is not None and not isinstance(exit_status_value, str):
        raise NativeParseError("info.exit_status must be a string or null")
    submission_value = info.get("submission")
    if submission_value is not None and not isinstance(submission_value, str):
        raise NativeParseError("info.submission must be a string or null")

    replay_config = value.get("replay_config")
    instance_id = expected_instance_id
    if expected_instance_id is not None and not expected_instance_id.strip():
        raise NativeParseError("expected instance id must be nonempty")

    model_stats = info.get("model_stats", {})
    if not isinstance(model_stats, dict):
        raise NativeParseError("info.model_stats must be an object when present")
    numeric_stats: dict[str, int | float] = {}
    for key in ("api_calls", "tokens_sent", "tokens_received", "instance_cost"):
        datum = model_stats.get(key, 0)
        if isinstance(datum, bool) or not isinstance(datum, (int, float)) or datum < 0:
            raise NativeParseError(f"info.model_stats.{key} must be a nonnegative number")
        numeric_stats[key] = datum

    patch_bytes = (submission_value or "").encode("utf-8")
    native_code = exit_status_value if exit_status_value is not None else "MISSING_EXIT_STATUS"
    status = _native_status(exit_status_value, submission_value, len(trajectory))

    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "instance_id": instance_id,
        "source": {
            "format": "SWE_AGENT_TRAJECTORY_JSON",
            "trajectory_sha256": sha256_bytes(raw),
            "replay_config_present": replay_config is not None,
        },
        "native_terminal": {
            "arm_id": ARM_ID,
            "status": status,
            "native_code": native_code,
            "payload_sha256": sha256_bytes(patch_bytes),
        },
        "native_retention": {
            "exit_status_exact": exit_status_value,
            "submission_bytes": len(patch_bytes),
            "trajectory_steps": len(trajectory),
            "model_stats": numeric_stats,
        },
        "adapter_disposition": {
            "output": "UNRESOLVED",
            "reason": "ARM_NATIVE_TERMINAL_ONLY__NO_CLASS_INFERENCE",
            "raw_native_singleton_licensed": False,
        },
        "outcome_boundary": {
            "protected_keys_seen": False,
            "protected_score_accessed": False,
            "comparator_outcome_accessed": False,
        },
    }


def parse_path(path: Path, *, expected_instance_id: str | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise NativeParseError("trajectory path is not a regular file")
    return parse_trajectory_bytes(path.read_bytes(), expected_instance_id=expected_instance_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trajectory", type=Path)
    parser.add_argument("--instance-id")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = parse_path(args.trajectory, expected_instance_id=args.instance_id)
    except NativeParseError as exc:
        print(f"P5_C1_NATIVE_PARSE_REFUSED: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
