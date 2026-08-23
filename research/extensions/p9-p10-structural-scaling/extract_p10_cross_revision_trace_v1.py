from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from extract_p10_native_trace_state_v1 import (
    MANIFEST,
    instrument,
    parse_messages,
    run_lean,
    sha_bytes,
    sha_file,
    source_events,
    state_features,
    states_from_messages,
)

TARGET_COMMIT = "d77ef0741c6da1ff12df68fb4145ea0ae0850c54"
TARGET_TOOLCHAIN = "leanprover/lean4:v4.34.0-rc1"
SCHEMA = "P10.CrossRevisionNativeTraceShard.v1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mathlib-checkout", required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--file-timeout", type=int, default=240)
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard index")

    checkout = Path(args.mathlib_checkout).resolve()
    actual_commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_commit != TARGET_COMMIT:
        raise SystemExit(f"target commit mismatch: {actual_commit}")
    toolchain = (checkout / "lean-toolchain").read_text().strip()
    if toolchain != TARGET_TOOLCHAIN:
        raise SystemExit(f"target toolchain mismatch: {toolchain}")

    source_manifest = json.loads(MANIFEST.read_text())
    selected = [
        item for item in source_manifest["files"]
        if int(hashlib.sha256(item["path"].encode()).hexdigest(), 16) % args.shard_count
        == args.shard_index
    ]

    rows: list[dict] = []
    files: list[dict] = []
    target_denominator = 0
    eligible = 0
    existing_paths = 0

    for source_item in selected:
        relative = source_item["path"]
        path = checkout / relative
        if not path.is_file():
            files.append({
                "path": relative,
                "top_module": source_item["top_module"],
                "status": "TARGET_PATH_MISSING",
                "transitions": 0,
                "eligible_transitions": 0,
            })
            continue
        existing_paths += 1
        target_sha = sha_file(path)
        original = path.read_text(encoding="utf-8")
        events, transition_count = source_events(original, relative)
        target_denominator += transition_count
        instrumented, line_receipts = instrument(original, events)
        proc = None
        failure_reason = None
        try:
            path.write_text(instrumented, encoding="utf-8")
            proc = run_lean(checkout, path, args.file_timeout)
        except subprocess.TimeoutExpired:
            failure_reason = "INSTRUMENTED_TIMEOUT"
        finally:
            path.write_text(original, encoding="utf-8")
            if sha_file(path) != target_sha:
                raise SystemExit(f"failed to restore target source: {relative}")

        if proc is None or proc.returncode != 0:
            if failure_reason is None:
                failure_reason = "INSTRUMENTATION_UNSUPPORTED"
            try:
                original_proc = run_lean(checkout, path, args.file_timeout)
                original_green = original_proc.returncode == 0
            except subprocess.TimeoutExpired:
                original_green = False
                failure_reason = "ORIGINAL_TIMEOUT_AFTER_INSTRUMENTATION_FAILURE"
            files.append({
                "path": relative,
                "top_module": source_item["top_module"],
                "target_source_sha256": target_sha,
                "status": failure_reason,
                "original_green_after_restore": original_green,
                "transitions": transition_count,
                "eligible_transitions": 0,
                "instrumented_returncode": proc.returncode if proc else None,
                "stderr_tail": proc.stderr[-2000:] if proc else None,
            })
            continue

        combined = proc.stdout + "\n" + proc.stderr
        states = states_from_messages(parse_messages(combined), line_receipts)
        event_by_id = {event["transition_id"]: event for event in events}
        file_eligible = 0
        for transition_id, state in states.items():
            event = event_by_id.get(transition_id)
            if event is None or not event["is_transition"]:
                continue
            state_vector, dependency_vector, normalized_digest = state_features(state)
            state_digest = sha_bytes(state.encode())
            receipt_material = {
                "transition_id": transition_id,
                "source_path": relative,
                "source_sha256": target_sha,
                "theorem_name": event["theorem_name"],
                "action_index": event["action_index"],
                "previous_family": event["previous_family"],
                "true_action": event["family"],
                "state_sha256": state_digest,
                "mathlib_commit": TARGET_COMMIT,
                "lean_toolchain": TARGET_TOOLCHAIN,
            }
            receipt_sha = sha_bytes(
                json.dumps(receipt_material, sort_keys=True, separators=(",", ":")).encode()
            )
            rows.append({
                **receipt_material,
                "top_module": source_item["top_module"],
                "normalized_state_sha256": normalized_digest,
                "state_features": state_vector,
                "dependency_features": dependency_vector,
                "receipt_sha256": receipt_sha,
            })
            file_eligible += 1
        eligible += file_eligible
        files.append({
            "path": relative,
            "top_module": source_item["top_module"],
            "target_source_sha256": target_sha,
            "status": "TRACE_GREEN" if file_eligible == transition_count else "PARTIAL_TRACE",
            "transitions": transition_count,
            "eligible_transitions": file_eligible,
            "native_trace_count": len(states),
            "instrumented_returncode": proc.returncode,
        })

    output = {
        "schema": SCHEMA,
        "target_commit": TARGET_COMMIT,
        "target_toolchain": TARGET_TOOLCHAIN,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "source_manifest_paths_in_shard": len(selected),
        "existing_target_paths": existing_paths,
        "target_transition_denominator": target_denominator,
        "eligible_target_transitions": eligible,
        "rows": rows,
        "files": files,
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k not in {"rows", "files"}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
