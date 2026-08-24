from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from extract_p10_native_lsp_state_v1 import (
    ACCESS_MODE,
    MIN_ELIGIBLE,
    access_receipt,
    tactic_token_column,
)
from extract_p10_native_trace_state_v1 import (
    EXTRACTOR_SCHEMA,
    LEAN_TOOLCHAIN,
    MANIFEST,
    MATHLIB_COMMIT,
    P10,
    sha_bytes,
    sha_file,
    source_events,
)

CORPUS = P10 / "benchmark" / "corpus" / "mathlib4_e72c1e277f31"
DENOMINATOR = 11_842
EXPECTED_SHARDS = 8
ALLOWED_GOAL_SHAPES = {
    "equality", "iff", "conjunction", "disjunction", "implication_function",
    "forall", "exists", "order_comparison", "arithmetic_algebraic", "prop_type_sort", "other",
}
ALLOWED_CONTEXT_SHAPES = ALLOWED_GOAL_SHAPES
ALLOWED_TOKEN_BUCKETS = {"0-31", "32-63", "64-127", "128-255", "256-511", "512+"}
ALLOWED_DEPTH_BUCKETS = {"0-2", "3-5", "6-9", "10+"}


def receipt_material(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key]
        for key in (
            "transition_id", "source_path", "source_sha256", "theorem_name", "action_index",
            "previous_family", "true_action", "state_sha256", "mathlib_commit", "lean_toolchain",
        )
    }


def verify_parent_receipt(row: dict[str, Any]) -> bool:
    expected = sha_bytes(
        json.dumps(receipt_material(row), sort_keys=True, separators=(",", ":")).encode()
    )
    return expected == row.get("receipt_sha256")


def verify_access_receipt(row: dict[str, Any]) -> bool:
    pos = row.get("query_position")
    if not isinstance(pos, dict):
        return False
    expected = access_receipt(
        str(row["transition_id"]),
        int(row["lsp_request_id"]),
        int(pos["line"]),
        int(pos["character"]),
        str(row["state_sha256"]),
    )
    return expected == row.get("access_receipt_sha256")


def build_expected() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    manifest = json.loads(MANIFEST.read_text())
    file_map: dict[str, dict[str, Any]] = {}
    expected: dict[str, dict[str, Any]] = {}
    total = 0
    for item in manifest["files"]:
        path = CORPUS / item["path"]
        if not path.is_file() or sha_file(path) != item["sha256"]:
            raise SystemExit(f"bound corpus identity mismatch: {item['path']}")
        text = path.read_text(encoding="utf-8")
        events, transition_count = source_events(text, item["path"])
        total += transition_count
        lines = text.splitlines()
        file_map[item["path"]] = {**item, "lines": lines, "transition_count": transition_count}
        for event in events:
            if not event["is_transition"]:
                continue
            tid = str(event["transition_id"])
            if tid in expected:
                raise SystemExit(f"duplicate expected transition id {tid}")
            line = int(event["line_zero_index"])
            expected[tid] = {
                "source_path": item["path"],
                "source_sha256": item["sha256"],
                "top_module": item["top_module"],
                "theorem_name": event["theorem_name"],
                "action_index": event["action_index"],
                "previous_family": event["previous_family"],
                "true_action": event["family"],
                "query_position": {
                    "line": line,
                    "character": tactic_token_column(lines[line]),
                },
            }
    if total != DENOMINATOR or len(expected) != DENOMINATOR:
        raise SystemExit(f"expected denominator mismatch: total={total}, ids={len(expected)}")
    return expected, file_map


def feature_surface_green(row: dict[str, Any]) -> bool:
    s = row.get("state_features")
    d = row.get("dependency_features")
    if not isinstance(s, dict) or not isinstance(d, dict):
        return False
    expected_s = {
        "num_goals", "context_cardinality", "goal_shape", "context_shape_histogram",
        "has_equality", "has_conjunction_disjunction", "has_implication_function",
        "has_quantification", "has_arithmetic_algebraic", "has_prop_type_sort",
        "state_token_bucket", "visible_depth_bucket",
    }
    expected_d = {
        "context_reference_edges", "goal_context_references",
        "max_context_reference_indegree", "referencing_declaration_fraction",
    }
    if set(s) != expected_s or set(d) != expected_d:
        return False
    if s["goal_shape"] not in ALLOWED_GOAL_SHAPES:
        return False
    hist = s["context_shape_histogram"]
    if not isinstance(hist, dict) or set(hist) != ALLOWED_CONTEXT_SHAPES:
        return False
    if s["state_token_bucket"] not in ALLOWED_TOKEN_BUCKETS:
        return False
    if s["visible_depth_bucket"] not in ALLOWED_DEPTH_BUCKETS:
        return False
    payload = json.dumps({"s": s, "d": d}, sort_keys=True)
    forbidden = [
        str(row.get("source_path", "")), str(row.get("theorem_name", "")),
        str(row.get("top_module", "")), str(row.get("transition_id", "")),
        str(row.get("state_sha256", "")),
    ]
    return not any(value and value in payload for value in forbidden)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    expected, _ = build_expected()
    shards = [json.loads(Path(path).read_text()) for path in args.shards]
    shard_ids = sorted((int(s["shard_index"]), int(s["shard_count"])) for s in shards)
    if shard_ids != [(i, EXPECTED_SHARDS) for i in range(EXPECTED_SHARDS)]:
        raise SystemExit(f"incomplete/duplicate shard set: {shard_ids}")

    calibration_green = True
    denominator = eligible_reported = 0
    selected_files = 0
    rows: list[dict[str, Any]] = []
    file_status: dict[str, int] = {}
    for shard in shards:
        if shard.get("schema") != EXTRACTOR_SCHEMA:
            raise SystemExit("shard schema mismatch")
        if shard.get("successor_study") != "P10_NATIVE_LSP_ACCESS_SUCCESSOR_V1":
            raise SystemExit("successor study mismatch")
        if shard.get("extractor_receipt_mode") != ACCESS_MODE:
            raise SystemExit("access mode mismatch")
        if shard.get("mathlib_commit") != MATHLIB_COMMIT or shard.get("lean_toolchain") != LEAN_TOOLCHAIN:
            raise SystemExit("runtime identity mismatch")
        denominator += int(shard["transition_denominator"])
        eligible_reported += int(shard["eligible_transitions"])
        selected_files += int(shard["selected_files"])
        rows.extend(shard["rows"])
        for cal in shard.get("calibrations", []):
            calibration_green = calibration_green and (
                cal.get("terminal") == "P10_NATIVE_LSP_CURSOR_CALIBRATION_GREEN"
            )
        if shard.get("terminal") == "CANNOT_CHECK_LSP_CURSOR_SEMANTICS":
            calibration_green = False
        for f in shard["files"]:
            status = str(f["status"])
            file_status[status] = file_status.get(status, 0) + 1

    if denominator != DENOMINATOR:
        raise SystemExit(f"aggregate denominator mismatch: {denominator}")
    if selected_files != 457:
        raise SystemExit(f"selected file count mismatch: {selected_files}")
    if eligible_reported != len(rows):
        raise SystemExit("reported eligible count != row count")

    seen: set[str] = set()
    parent_receipts_green = access_receipts_green = positions_green = features_green = True
    metadata_green = True
    for row in rows:
        tid = str(row["transition_id"])
        if tid in seen:
            raise SystemExit(f"duplicate observed transition id: {tid}")
        seen.add(tid)
        exp = expected.get(tid)
        if exp is None:
            raise SystemExit(f"observed transition outside frozen denominator: {tid}")
        for key in (
            "source_path", "source_sha256", "top_module", "theorem_name", "action_index",
            "previous_family", "true_action",
        ):
            metadata_green = metadata_green and row.get(key) == exp[key]
        positions_green = positions_green and row.get("query_position") == exp["query_position"]
        parent_receipts_green = parent_receipts_green and verify_parent_receipt(row)
        access_receipts_green = access_receipts_green and verify_access_receipt(row)
        features_green = features_green and feature_surface_green(row)

    mutation_checks = {
        "parent_source_mutation_rejected": False,
        "parent_transition_mutation_rejected": False,
        "access_position_mutation_rejected": False,
        "access_state_mutation_rejected": False,
    }
    if rows:
        base = rows[0]
        a = copy.deepcopy(base)
        a["source_sha256"] = "0" * 64
        mutation_checks["parent_source_mutation_rejected"] = not verify_parent_receipt(a)
        b = copy.deepcopy(base)
        b["transition_id"] = "0" * 32
        mutation_checks["parent_transition_mutation_rejected"] = not verify_parent_receipt(b)
        c = copy.deepcopy(base)
        c["query_position"]["character"] = int(c["query_position"]["character"]) + 1
        mutation_checks["access_position_mutation_rejected"] = not verify_access_receipt(c)
        d = copy.deepcopy(base)
        d["state_sha256"] = "f" * 64
        mutation_checks["access_state_mutation_rejected"] = not verify_access_receipt(d)

    integrity_green = all([
        metadata_green, parent_receipts_green, access_receipts_green,
        positions_green, features_green,
        all(mutation_checks.values()) if rows else True,
    ])
    if not integrity_green:
        raise SystemExit(json.dumps({
            "metadata_green": metadata_green,
            "parent_receipts_green": parent_receipts_green,
            "access_receipts_green": access_receipts_green,
            "positions_green": positions_green,
            "features_green": features_green,
            "mutation_checks": mutation_checks,
        }, sort_keys=True))

    coverage = len(rows) / DENOMINATOR
    if not calibration_green:
        terminal = "CANNOT_CHECK_LSP_CURSOR_SEMANTICS"
    elif len(rows) >= MIN_ELIGIBLE:
        terminal = "P10_NATIVE_LSP_STATE_COVERAGE_SUPPORTED"
    else:
        terminal = "CANNOT_CHECK_NATIVE_STATE_COVERAGE"

    report = {
        "schema": "P10.NativeLspAccessAggregate.v1",
        "terminal": terminal,
        "mathlib_commit": MATHLIB_COMMIT,
        "lean_toolchain": LEAN_TOOLCHAIN,
        "selected_files": selected_files,
        "transition_denominator": DENOMINATOR,
        "eligible_transitions": len(rows),
        "minimum_eligible": MIN_ELIGIBLE,
        "eligibility_coverage": coverage,
        "calibration_green": calibration_green,
        "integrity_green": integrity_green,
        "parent_receipts_green": parent_receipts_green,
        "access_receipts_green": access_receipts_green,
        "frozen_positions_green": positions_green,
        "feature_surface_green": features_green,
        "mutation_checks": mutation_checks,
        "file_status": dict(sorted(file_status.items())),
        "missing_transition_count": DENOMINATOR - len(rows),
    }
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
