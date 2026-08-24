#!/usr/bin/env python3
"""Outcome-blind terminal parser for pinned MOSS manifest schema v6.

The parser deliberately ignores all development score values and never reads
an external/protected scorer.  It retains MOSS's exact manifest terminal and
the latest native iteration verdict, while hashing the candidate identifiers.
No MOSS terminal is promoted to a P5 responsibility class: that remains the
separate V3 certificate/action/fibre operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ARM_ID = "C2_DIRECT_SELF_EDIT__MOSS"
SCHEMA_VERSION = "orion.p5.c2.moss-native-terminal.v4"
MAX_MANIFEST_BYTES = 16 * 1024 * 1024

MANIFEST_STATUSES = frozenset(
    {
        "initialized",
        "in_progress",
        "swap_pending",
        "converged",
        "rolled_back",
        "failed",
        "aborted_max_iter",
        "aborted_streak",
    }
)

VERDICTS = frozenset(
    {
        "converged",
        "need_more_work",
        "fundamental_limit_model",
        "fundamental_limit_arch",
        "build_failed",
        "build_smoke_failed",
        "implementer_failed",
        "architect_output_malformed",
        "architect_violated_readonly",
        "reviewer_rejected_max_rounds",
        "reviewer_violated_readonly",
        "plan_rejected_max_rounds",
        "code_rejected_max_rounds",
        "implementer_blocked",
        "partial_progress",
    }
)

# Pinned MOSS development manifests contain native development scores.  They
# are allowed to exist but are neither emitted nor used in terminal mapping.
# External/protected/gold fields, by contrast, are forbidden anywhere.
PROHIBITED_KEYS = frozenset(
    {
        "external_protected_scorer",
        "gold_label",
        "gold_patch",
        "heldout_outcome",
        "protected_label",
        "protected_outcome",
        "protected_panel",
        "protected_score",
        "scorer_feedback",
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
            if str(key) in PROHIBITED_KEYS:
                hits.append(child_path)
            hits.extend(_find_prohibited_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_find_prohibited_keys(child, f"{path}[{index}]"))
    return hits


def _nonempty_optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise NativeParseError(f"{field} must be a nonempty string or null")
    return value


def _native_status(
    manifest_status: str,
    latest_verdict: str | None,
    commit_hash: str | None,
    image_tag: str | None,
) -> str:
    if manifest_status == "converged":
        if latest_verdict == "converged" and commit_hash and image_tag:
            return "COMPLETE_SUCCESS"
        return "INVALID"
    if manifest_status in {"initialized", "in_progress", "swap_pending"}:
        return "PARTIAL"
    if manifest_status in {"aborted_max_iter", "aborted_streak"}:
        return "ABSTAIN"
    if manifest_status in {"failed", "rolled_back"}:
        return "ERROR"
    return "INVALID"


def parse_manifest_bytes(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_MANIFEST_BYTES:
        raise NativeParseError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NativeParseError("manifest is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise NativeParseError("manifest root must be an object")

    prohibited = _find_prohibited_keys(value)
    if prohibited:
        raise NativeParseError(
            "external protected/gold keys are forbidden: " + ", ".join(sorted(prohibited))
        )
    if value.get("schemaVersion") != 6:
        raise NativeParseError("only pinned native manifest schemaVersion 6 is accepted")

    manifest_status = value.get("status")
    if manifest_status not in MANIFEST_STATUSES:
        raise NativeParseError("manifest.status is absent or outside the pinned closed set")
    trigger_id = _nonempty_optional_string(value.get("triggerId"), "manifest.triggerId")
    if trigger_id is None:
        raise NativeParseError("manifest.triggerId is required")
    flag_batch_id = _nonempty_optional_string(value.get("flagBatchId"), "manifest.flagBatchId")

    current_iteration = value.get("currentIteration")
    if isinstance(current_iteration, bool) or not isinstance(current_iteration, int) or current_iteration < 0:
        raise NativeParseError("manifest.currentIteration must be a nonnegative integer")
    current_stage = value.get("currentStage")
    if not isinstance(current_stage, str):
        raise NativeParseError("manifest.currentStage must be a string")

    iterations = value.get("iterations")
    if not isinstance(iterations, list):
        raise NativeParseError("manifest.iterations must be an array")
    latest_verdict: str | None = None
    commit_hash: str | None = None
    image_tag: str | None = None
    if iterations:
        latest = iterations[-1]
        if not isinstance(latest, dict):
            raise NativeParseError("latest manifest iteration must be an object")
        latest_verdict_value = latest.get("verdict")
        if latest_verdict_value not in VERDICTS:
            raise NativeParseError("latest iteration verdict is outside the pinned closed set")
        latest_verdict = str(latest_verdict_value)
        commit_hash = _nonempty_optional_string(latest.get("commitHash"), "latest.commitHash")
        image_tag = _nonempty_optional_string(latest.get("imageTag"), "latest.imageTag")

    status = _native_status(manifest_status, latest_verdict, commit_hash, image_tag)
    terminal_vector = {
        "manifest_status": manifest_status,
        "latest_verdict": latest_verdict,
        "commit_hash": commit_hash,
        "image_tag": image_tag,
    }
    terminal_bytes = json.dumps(
        terminal_vector, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "source": {
            "format": "MOSS_EVOLUTION_MANIFEST_V6_JSON",
            "manifest_sha256": sha256_bytes(raw),
            "manifest_bytes": len(raw),
            "development_scores_used_for_mapping": False,
            "development_scores_reproduced": False,
        },
        "native_terminal": {
            "arm_id": ARM_ID,
            "status": status,
            "native_code": manifest_status,
            "payload_sha256": sha256_bytes(terminal_bytes),
        },
        "native_retention": {
            "manifest_status_exact": manifest_status,
            "latest_verdict_exact": latest_verdict,
            "current_iteration": current_iteration,
            "current_stage": current_stage,
            "iteration_records": len(iterations),
            "trigger_id_sha256": sha256_bytes(trigger_id.encode("utf-8")),
            "flag_batch_id_sha256": (
                sha256_bytes(flag_batch_id.encode("utf-8")) if flag_batch_id else None
            ),
            "candidate_commit_sha256": (
                sha256_bytes(commit_hash.encode("utf-8")) if commit_hash else None
            ),
            "candidate_image_tag_sha256": (
                sha256_bytes(image_tag.encode("utf-8")) if image_tag else None
            ),
        },
        "adapter_disposition": {
            "output": "UNRESOLVED",
            "reason": "ARM_NATIVE_TERMINAL_ONLY__NO_CLASS_INFERENCE",
            "raw_native_singleton_licensed": False,
        },
        "outcome_boundary": {
            "external_protected_or_gold_keys_seen": False,
            "external_protected_score_accessed": False,
            "comparator_performance_inferred": False,
        },
    }


def parse_path(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise NativeParseError("manifest path is not a regular file")
    return parse_manifest_bytes(path.read_bytes())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = parse_path(args.manifest)
    except NativeParseError as exc:
        print(f"P5_C2_NATIVE_PARSE_REFUSED: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
