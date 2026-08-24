#!/usr/bin/env python3
"""Outcome-blind terminal parser for a pinned DGM patch-capture envelope.

The released Darwin Godel Machine does not expose a stable result schema before
benchmark evaluation.  The V4 adapter therefore freezes a small capture
envelope at the source-native boundary: initialization, diagnosis, self-edit,
and patch capture.  Evaluation scores, archive admission, protected labels,
and scorer feedback are forbidden.  A captured patch is only an arm-native
completion; it never licenses a P5 responsibility class.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ARM_ID = "C3_ARCHIVE_BASED_SELF_EDIT__DGM"
INPUT_SCHEMA_VERSION = "orion.p5.c3.dgm-patch-capture.v4"
OUTPUT_SCHEMA_VERSION = "orion.p5.c3.dgm-native-terminal.v4"
MAX_CAPTURE_BYTES = 1024 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

NATIVE_CODES = frozenset(
    {
        "INITIALIZED",
        "DIAGNOSIS_READY",
        "SELF_EDIT_STARTED",
        "PATCH_CAPTURED",
        "NO_ENTRY",
        "NO_PROBLEM_STATEMENT",
        "MISSING_PATCH",
        "EMPTY_PATCH",
        "ARGPARSE_INTEGRITY_ERROR",
        "PROVIDER_ERROR",
        "RUNTIME_ERROR",
        "TIMEOUT",
    }
)

STAGES = frozenset({"initialize", "diagnose", "self_edit", "capture_patch"})

PROHIBITED_KEYS = frozenset(
    {
        "accuracy_score",
        "archive_admitted",
        "benchmark_outcome",
        "evaluation_score",
        "external_protected_scorer",
        "gold_label",
        "gold_patch",
        "heldout_outcome",
        "improvement_diagnosis",
        "overall_performance",
        "protected_label",
        "protected_outcome",
        "protected_panel",
        "protected_score",
        "resolved_ids",
        "scorer_feedback",
        "test_output",
        "unresolved_ids",
    }
)

PROHIBITED_PREFIXES = ("gold_", "heldout_", "protected_", "scorer_")

ALLOWED_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "arm_id",
        "run_id",
        "parent_commit",
        "native_code",
        "stage",
        "exit_code",
        "patch_sha256",
        "patch_bytes",
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
            child_path = f"{path}.{key}"
            key_text = str(key)
            if key_text in PROHIBITED_KEYS or key_text.startswith(PROHIBITED_PREFIXES):
                hits.append(child_path)
            hits.extend(_find_prohibited_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_find_prohibited_keys(child, f"{path}[{index}]"))
    return hits


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NativeParseError(f"{field} must be a nonempty string")
    return value


def _optional_exit_code(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise NativeParseError("exit_code must be an integer or null")
    if value < 0 or value > 255:
        raise NativeParseError("exit_code must be in [0,255]")
    return value


def _map_status(native_code: str, patch_sha256: str | None, patch_bytes: int, exit_code: int | None) -> str:
    if native_code == "PATCH_CAPTURED":
        if patch_sha256 is None or patch_bytes <= 0 or exit_code != 0:
            return "INVALID"
        return "COMPLETE_SUCCESS"
    if native_code in {"INITIALIZED", "DIAGNOSIS_READY", "SELF_EDIT_STARTED", "NO_PROBLEM_STATEMENT"}:
        return "PARTIAL"
    if native_code in {"NO_ENTRY", "MISSING_PATCH", "EMPTY_PATCH"}:
        return "EMPTY"
    if native_code == "TIMEOUT":
        return "TIMEOUT"
    if native_code in {"ARGPARSE_INTEGRITY_ERROR", "PROVIDER_ERROR", "RUNTIME_ERROR"}:
        return "ERROR"
    return "INVALID"


def parse_capture_bytes(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_CAPTURE_BYTES:
        raise NativeParseError(f"capture exceeds {MAX_CAPTURE_BYTES} bytes")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NativeParseError("capture is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise NativeParseError("capture root must be an object")

    prohibited = _find_prohibited_keys(value)
    if prohibited:
        raise NativeParseError(
            "benchmark/protected/gold fields are forbidden: " + ", ".join(sorted(prohibited))
        )
    if value.get("schema_version") != INPUT_SCHEMA_VERSION:
        raise NativeParseError("only the pinned V4 capture schema is accepted")
    if value.get("arm_id") != ARM_ID:
        raise NativeParseError("capture has the wrong arm_id")
    unknown = sorted(set(value) - ALLOWED_ROOT_KEYS)
    if unknown:
        raise NativeParseError("capture contains keys outside the closed schema: " + ", ".join(unknown))

    native_code = value.get("native_code")
    if native_code not in NATIVE_CODES:
        raise NativeParseError("native_code is outside the pinned closed set")
    stage = value.get("stage")
    if stage not in STAGES:
        raise NativeParseError("stage is outside the outcome-blind pre-evaluation set")
    run_id = _required_string(value.get("run_id"), "run_id")
    parent_commit = _required_string(value.get("parent_commit"), "parent_commit")
    exit_code = _optional_exit_code(value.get("exit_code"))

    patch_sha256 = value.get("patch_sha256")
    if patch_sha256 is not None and (
        not isinstance(patch_sha256, str) or SHA256_RE.fullmatch(patch_sha256) is None
    ):
        raise NativeParseError("patch_sha256 must be a lowercase SHA-256 hex digest or null")
    patch_bytes = value.get("patch_bytes", 0)
    if isinstance(patch_bytes, bool) or not isinstance(patch_bytes, int) or patch_bytes < 0:
        raise NativeParseError("patch_bytes must be a nonnegative integer")
    if (patch_sha256 is None) != (patch_bytes == 0):
        raise NativeParseError("patch_sha256 and positive patch_bytes must occur together")
    if native_code == "PATCH_CAPTURED" and stage != "capture_patch":
        raise NativeParseError("PATCH_CAPTURED requires stage=capture_patch")
    if native_code != "PATCH_CAPTURED" and (patch_sha256 is not None or patch_bytes != 0):
        raise NativeParseError("only PATCH_CAPTURED may carry patch identity")

    status = _map_status(str(native_code), patch_sha256, patch_bytes, exit_code)
    terminal_vector = {
        "native_code": native_code,
        "stage": stage,
        "exit_code": exit_code,
        "patch_sha256": patch_sha256,
        "patch_bytes": patch_bytes,
    }
    terminal_bytes = json.dumps(
        terminal_vector, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "source": {
            "format": "ADAPTER_AUTHORED_DGM_PRE_EVALUATION_PATCH_CAPTURE_V4",
            "capture_sha256": sha256_bytes(raw),
            "capture_bytes": len(raw),
            "released_upstream_result_schema": False,
            "benchmark_or_archive_values_used_for_mapping": False,
        },
        "native_terminal": {
            "arm_id": ARM_ID,
            "status": status,
            "native_code": native_code,
            "payload_sha256": sha256_bytes(terminal_bytes),
        },
        "native_retention": {
            "stage_exact": stage,
            "exit_code_exact": exit_code,
            "run_id_sha256": sha256_bytes(run_id.encode("utf-8")),
            "parent_commit_sha256": sha256_bytes(parent_commit.encode("utf-8")),
            "patch_sha256": patch_sha256,
            "patch_bytes": patch_bytes,
        },
        "adapter_disposition": {
            "output": "UNRESOLVED",
            "reason": "ARM_NATIVE_TERMINAL_ONLY__NO_P5_CLASS_INFERENCE",
            "raw_native_singleton_licensed": False,
        },
        "outcome_boundary": {
            "benchmark_protected_or_gold_keys_seen": False,
            "external_protected_score_accessed": False,
            "archive_admission_inferred": False,
            "comparator_performance_inferred": False,
        },
    }


def parse_path(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise NativeParseError("capture path is not a regular file")
    return parse_capture_bytes(path.read_bytes())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = parse_path(args.capture)
    except NativeParseError as exc:
        print(f"P5_C3_NATIVE_PARSE_REFUSED: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
