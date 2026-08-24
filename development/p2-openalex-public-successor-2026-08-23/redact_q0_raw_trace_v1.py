#!/usr/bin/env python3
"""Quarantine Q0_RAW plaintext and leave hash-only redistributed traces.

This is a rights-preserving archival transform, not a scientific rerun. It
does not change provider responses, candidate identities, scores or terminals.
The historical result continues to bind the quarantined original trace hash;
the redistributed trace receives a distinct redacted hash recorded in a new
receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def redact_trace(path: Path, quarantine_dir: Path) -> dict[str, Any]:
    original = path.read_bytes()
    original_sha = sha256_bytes(original)
    quarantine_name = f"{path.name}.{original_sha}.plaintext-quarantine.json"
    quarantine_path = quarantine_dir / quarantine_name
    if quarantine_path.exists():
        if sha256_bytes(quarantine_path.read_bytes()) != original_sha:
            raise ValueError(f"existing quarantine hash mismatch: {quarantine_path}")
    else:
        quarantine_path.write_bytes(original)
    os.chmod(quarantine_path, 0o600)

    trace = json.loads(original.decode("utf-8"))
    redacted: list[dict[str, str]] = []
    for task in trace.get("tasks", []):
        for call in task.get("calls", []):
            if call.get("query_id") != "Q0_RAW":
                continue
            query = call.pop("query", None)
            if not isinstance(query, str) or not query:
                raise ValueError(f"missing Q0_RAW plaintext in {path}:{task.get('task_id')}")
            query_sha = sha256_bytes(query.encode("utf-8"))
            call["query_sha256"] = query_sha
            call["query_redaction"] = "UPSTREAM_DECRYPTED_TEXT_QUARANTINED_HASH_ONLY"
            redacted.append({"task_id": str(task.get("task_id")), "query_sha256": query_sha})

    if len(redacted) != 24:
        raise ValueError(f"expected 24 Q0_RAW queries in {path}, got {len(redacted)}")
    for task in trace.get("tasks", []):
        for call in task.get("calls", []):
            if call.get("query_id") == "Q0_RAW" and "query" in call:
                raise ValueError("Q0_RAW plaintext survived redaction")

    redacted_body = (json.dumps(trace, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.write_bytes(redacted_body)
    return {
        "redistributed_file": path.name,
        "historical_plaintext_trace_sha256": original_sha,
        "redacted_trace_sha256": sha256_bytes(redacted_body),
        "q0_raw_queries_redacted": len(redacted),
        "hash_only_query_provenance": redacted,
        "quarantine_copy_sha256": original_sha,
        "quarantine_mode": "0600",
        "quarantine_location": "OUTSIDE_REDISTRIBUTED_WORKTREE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quarantine-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("traces", nargs="+", type=Path)
    args = parser.parse_args()
    args.quarantine_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(args.quarantine_dir, 0o700)
    files = [redact_trace(path, args.quarantine_dir) for path in args.traces]
    receipt = {
        "schema_version": "orion.p2.q0-raw-rights-redaction.v1",
        "date": "2026-08-23",
        "terminal": "P2_Q0_RAW_DECRYPTED_TEXT_QUARANTINED_HASH_ONLY_PROVENANCE",
        "operation": "ARCHIVAL_RIGHTS_REDACTION_NOT_SCIENTIFIC_RERUN",
        "files": files,
        "plaintext_redistribution_authority": "CANNOT_CHECK_UPSTREAM_PERMISSION",
        "redistribution_rule": "Q0_RAW decrypted text is absent; only SHA-256 provenance is retained in redistributed traces.",
        "scientific_identity_rule": "Historical V1 result and terminal retain the original quarantined trace hash; the redacted traces have successor archival hashes and do not rewrite the outcome.",
        "submission_guard": "Do not circulate plaintext even if locally recoverable; an authoritative upstream permission disposition is required before any future plaintext redistribution.",
    }
    args.receipt.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
