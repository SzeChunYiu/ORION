#!/usr/bin/env python3
"""Find exactly two outcome-blind WorkflowHub replacement families.

This successor is allowed to use only public source metadata and normalized
RO-Crate content binding. It excludes every workflow family from the original
128-frame, scans the remaining public TRS universe in deterministic ID order,
and accepts the first two candidates that pass every frozen source/content
rule. It never reads change-stratum adjudication, REUSE/REOPEN gold, ORION
predictions, baseline predictions, or study outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable

from bind_workflowhub_rocrate_content_v1 import bind_pair, load_snapshot
from census_workflowhub_versioned_sources_v1 import (
    fetch_all_tools,
    fetch_license,
    integer_versions,
    tool_sort_key,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE / "workflowhub-normalized-content-binding-v2"
TARGET_N = 2
EXPECTED_BASE_SELECTED_ROWS_SHA256 = "2f36f8d5900c904d939e87f7c582281e27445f4045d520754b7b11dcbbc3b882"
EXPECTED_FAILURE_IDS = ["402", "444"]


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_normalized_base() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = json.loads((BASE / "SNAPSHOT_V2.json").read_text())
    if manifest.get("schema") != "ORION.A3.WorkflowHubNormalizedContentBindingDurableSnapshot.v2":
        raise ValueError("wrong durable normalized snapshot schema")
    if manifest.get("selected_rows_sha256") != EXPECTED_BASE_SELECTED_ROWS_SHA256:
        raise ValueError("normalized snapshot selected-row binding mismatch")
    if manifest.get("candidate_n") != 128 or manifest.get("cannot_check_workflow_ids") != EXPECTED_FAILURE_IDS:
        raise ValueError("normalized snapshot base counts/failures changed")
    rows: list[dict[str, Any]] = []
    for chunk in manifest["chunks"]:
        path = ROOT / chunk["path"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != chunk["sha256"]:
            raise ValueError(f"normalized snapshot chunk hash mismatch: {chunk['path']}")
        payload = json.loads(raw)
        if payload.get("schema") != "ORION.A3.WorkflowHubNormalizedContentBindingSnapshotChunk.v2":
            raise ValueError("normalized snapshot chunk schema mismatch")
        if len(payload.get("rows", [])) != chunk["rows"]:
            raise ValueError("normalized snapshot chunk row-count mismatch")
        rows.extend(payload["rows"])
    if len(rows) != 128 or len({r["workflow_id"] for r in rows}) != 128:
        raise ValueError("normalized base must contain 128 unique workflow families")
    if canonical_sha(rows) != manifest["selected_rows_sha256"]:
        raise ValueError("normalized base selected-row digest mismatch")
    retained = [r for r in rows if r["status"] == "NORMALIZED_CONTENT_BOUND_DIFFERENT"]
    failed = [r for r in rows if r["status"] == "CANNOT_CHECK_NORMALIZED_CONTENT_BINDING"]
    if len(retained) != 126 or [r["workflow_id"] for r in failed] != EXPECTED_FAILURE_IDS:
        raise ValueError("normalized base status partition mismatch")
    return manifest, rows


def replacement_projection(binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_id": binding["workflow_id"],
        "version_before": binding["version_before"],
        "version_after": binding["version_after"],
        "license_before": binding["license_before"],
        "license_after": binding["license_after"],
        "metadata_sha256_before": binding["metadata_sha256_before"],
        "metadata_sha256_after": binding["metadata_sha256_after"],
        "before_normalized_sha256": binding["before"]["normalized_content_manifest_sha256"],
        "after_normalized_sha256": binding["after"]["normalized_content_manifest_sha256"],
        "before_member_count": binding["before"]["normalized_member_count"],
        "after_member_count": binding["after"]["normalized_member_count"],
        "status": binding["status"],
    }


def deterministic_select(
    tools: list[dict[str, Any]],
    original_ids: set[str],
    target_n: int,
    qualify: Callable[[dict[str, Any]], dict[str, Any] | None],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for tool in sorted(tools, key=tool_sort_key):
        tool_id = str(tool.get("id"))
        if tool_id in original_ids:
            continue
        if len(integer_versions(tool)) < 2:
            continue
        candidate = qualify(tool)
        if candidate is None:
            continue
        selected.append(candidate)
        if len(selected) == target_n:
            break
    return selected


def live_replacements(polite_delay: float = 0.03) -> dict[str, Any]:
    base_manifest, base_rows = load_normalized_base()
    _source_manifest, source_rows = load_snapshot()
    original_ids = {r["workflow_id"] for r in source_rows}
    if len(original_ids) != 128 or original_ids != {r["workflow_id"] for r in base_rows}:
        raise ValueError("original source census and normalized snapshot family sets disagree")

    tools = fetch_all_tools()
    ids = [str(t.get("id")) for t in tools]
    if len(ids) != len(set(ids)):
        raise RuntimeError("TRS /tools returned duplicate workflow ids")

    attempts: list[dict[str, Any]] = []

    def qualify(tool: dict[str, Any]) -> dict[str, Any] | None:
        tool_id = str(tool.get("id"))
        versions = integer_versions(tool)
        before, after = versions[-2], versions[-1]
        attempt: dict[str, Any] = {
            "workflow_id": tool_id,
            "version_before": before,
            "version_after": after,
            "stage": "metadata",
        }
        try:
            lic_before, meta_before = fetch_license(tool_id, before)
            time.sleep(polite_delay)
            lic_after, meta_after = fetch_license(tool_id, after)
            time.sleep(polite_delay)
        except Exception as exc:
            attempt.update({"status": "REJECTED_PUBLIC_METADATA", "reason": str(exc)[:300]})
            attempts.append(attempt)
            return None
        row = {
            "workflow_id": tool_id,
            "version_before": before,
            "version_after": after,
            "license_before": lic_before,
            "license_after": lic_after,
            "metadata_sha256_before": meta_before,
            "metadata_sha256_after": meta_after,
        }
        attempt["stage"] = "normalized_content"
        binding = bind_pair(row)
        if binding["status"] != "NORMALIZED_CONTENT_BOUND_DIFFERENT":
            attempt.update({"status": binding["status"], "reason": binding.get("reason")})
            attempts.append(attempt)
            return None
        projected = replacement_projection(binding)
        attempt.update({
            "status": "SELECTED_REPLACEMENT",
            "before_normalized_sha256": projected["before_normalized_sha256"],
            "after_normalized_sha256": projected["after_normalized_sha256"],
        })
        attempts.append(attempt)
        return projected

    selected = deterministic_select(tools, original_ids, TARGET_N, qualify)
    retained_ids = [r["workflow_id"] for r in base_rows if r["status"] == "NORMALIZED_CONTENT_BOUND_DIFFERENT"]
    final_ids = retained_ids + [r["workflow_id"] for r in selected]
    success = len(selected) == TARGET_N and len(final_ids) == 128 and len(set(final_ids)) == 128
    successor_identity = {
        "base_selected_rows_sha256": base_manifest["selected_rows_sha256"],
        "excluded_transport_failure_workflow_ids": EXPECTED_FAILURE_IDS,
        "replacements": selected,
    }
    return {
        "schema": "ORION.A3.WorkflowHubTwoReplacementSuccessorResult.v1",
        "terminal": (
            "WORKFLOWHUB_TWO_REPLACEMENT_SUCCESSOR_CONTENT_BOUND"
            if success else "CANNOT_CHECK_WORKFLOWHUB_TWO_REPLACEMENT_SUCCESSOR_CAPACITY"
        ),
        "trs_tools_seen": len(tools),
        "original_frame_n": 128,
        "retained_original_n": 126,
        "excluded_original_workflow_ids": EXPECTED_FAILURE_IDS,
        "replacement_target_n": TARGET_N,
        "replacement_n": len(selected),
        "replacements": selected,
        "attempts_before_stop": attempts,
        "final_source_family_n": len(final_ids) if success else 126 + len(selected),
        "final_unique_source_family_n": len(set(final_ids)),
        "successor_frame_sha256": canonical_sha(successor_identity),
        "selection_rule": "first two passing non-original families in deterministic WorkflowHub id order",
        "all_original_128_workflow_ids_excluded_from_replacement_search": True,
        "change_stratum_adjudicated": False,
        "external_gold_accessed": False,
        "protected_orion_predictions_accessed": False,
        "primary_replication_assignment_performed": False,
        "scientific_authority_delta": "NONE__OUTCOME_BLIND_SOURCE_FRAME_REPAIR_ONLY",
    }


def self_test() -> dict[str, Any]:
    tools = [
        {"id": "5", "versions": [{"id": "1"}, {"id": "2"}]},
        {"id": "2", "versions": [{"id": "1"}, {"id": "2"}]},
        {"id": "4", "versions": [{"id": "1"}]},
        {"id": "3", "versions": [{"id": "1"}, {"id": "2"}]},
        {"id": "1", "versions": [{"id": "1"}, {"id": "2"}]},
    ]
    original = {"1"}
    decisions = {"2": None, "3": {"workflow_id": "3"}, "5": {"workflow_id": "5"}}
    selected = deterministic_select(tools, original, 2, lambda t: decisions.get(str(t["id"])))
    assert [r["workflow_id"] for r in selected] == ["3", "5"]
    reverse = deterministic_select(list(reversed(tools)), original, 2, lambda t: decisions.get(str(t["id"])))
    assert reverse == selected
    base, rows = load_normalized_base()
    assert base["cannot_check_workflow_ids"] == EXPECTED_FAILURE_IDS
    assert sum(r["status"] == "NORMALIZED_CONTENT_BOUND_DIFFERENT" for r in rows) == 126
    return {
        "decision": "GREEN",
        "network_accessed": False,
        "deterministic_under_input_reversal": True,
        "base_snapshot_n": 128,
        "base_retained_n": 126,
        "frozen_failure_ids": EXPECTED_FAILURE_IDS,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = self_test() if args.self_test else live_replacements()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    if not args.self_test and result["terminal"].startswith("CANNOT_CHECK"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
