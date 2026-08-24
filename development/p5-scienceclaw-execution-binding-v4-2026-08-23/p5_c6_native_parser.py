#!/usr/bin/env python3
"""Outcome-blind structural parser for one native ScienceClaw dry-run draft.

The parser is deliberately not a P5 selector.  It refuses protected-key
families before JSON decoding, retains no scientific payload values, and maps
every admissible native draft to UNRESOLVED.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ARM_ID = "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW"
SCHEMA = "orion.p5.c6.scienceclaw-native-terminal.v4"
EXPECTED_TOP_LEVEL = {
    "agent",
    "topic",
    "community",
    "title",
    "hypothesis",
    "method",
    "findings",
    "content",
    "investigation_results",
}
PROHIBITED_KEY_RE = re.compile(
    rb"[\\\"](?:protected(?:_[a-z0-9_]+)?|gold(?:_[a-z0-9_]+)?|hidden(?:_[a-z0-9_]+)?|"
    rb"holdout(?:_[a-z0-9_]+)?|private_score|reference_answer|scorer_output|"
    rb"final_test(?:_[a-z0-9_]+)?)[\\\"]\s*:",
    re.IGNORECASE,
)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def refuse(message: str) -> int:
    print(json.dumps({"terminal": "INPUT_REFUSED", "reason": message}, sort_keys=True))
    return 2


def structural_list_count(value: Any) -> int | None:
    return len(value) if isinstance(value, list) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        raw = args.draft.read_bytes()
    except OSError as exc:
        return refuse(f"draft unreadable: {exc}")

    # Refuse by raw key name before decoding, so protected values are neither
    # parsed nor copied into an adapter artifact.
    match = PROHIBITED_KEY_RE.search(raw)
    if match:
        return refuse("protected/gold/hidden/holdout/final-test key refused before JSON decoding")

    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return refuse(f"invalid JSON: {exc}")
    if not isinstance(value, dict):
        return refuse("draft root must be an object")
    if set(value) != EXPECTED_TOP_LEVEL:
        return refuse(f"top-level key mismatch: {sorted(set(value) ^ EXPECTED_TOP_LEVEL)}")

    required_strings = ("agent", "topic", "community", "title", "hypothesis", "method", "findings", "content")
    if any(not isinstance(value[key], str) or not value[key].strip() for key in required_strings):
        return refuse("required candidate-visible draft strings must be nonempty")
    investigation = value["investigation_results"]
    if not isinstance(investigation, dict):
        return refuse("investigation_results must be an object")

    # Only shape/count metadata is retained.  No paper, claim, measurement,
    # score, model output, or artifact payload is emitted.
    counts = {
        key: structural_list_count(investigation.get(key))
        for key in ("papers", "proteins", "compounds", "productive_tools", "insights", "artifacts")
        if key in investigation
    }
    output = {
        "schema_version": SCHEMA,
        "arm_id": ARM_ID,
        "adapter_terminal": "UNRESOLVED",
        "native_terminal": "NATIVE_DRY_RUN_DRAFT_RECORDED",
        "draft_sha256": sha256_bytes(raw),
        "draft_size_bytes": len(raw),
        "top_level_keys": sorted(value),
        "investigation_result_key_count": len(investigation),
        "structural_list_counts": counts,
        "scientific_payload_values_retained": False,
        "native_exit_status_is_sufficient": False,
        "raw_native_singleton_licences": 0,
        "performance_inference": "FORBIDDEN",
        "source_native_caveat": "ScienceClaw draft/artifact status is provenance and representation evidence, not a P5 responsibility selector.",
    }
    encoded = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
