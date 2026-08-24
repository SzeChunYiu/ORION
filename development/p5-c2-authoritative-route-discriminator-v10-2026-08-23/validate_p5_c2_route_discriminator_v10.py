#!/usr/bin/env python3
"""Self-contained validation for the P5 C2 V10 packet (no test framework)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    json_paths = sorted(ROOT.glob("*.json"))
    docs = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in json_paths}
    assert len(json_paths) >= 6

    protocol = docs["P5_C2_V10_AUDIT_PROTOCOL.json"]
    upstream = docs["P5_C2_V10_UPSTREAM_PUBLICATION_RECEIPT.json"]
    route = docs["P5_C2_V10_PINNED_SOURCE_ROUTE_RECEIPT.json"]
    contract = docs["P5_C2_V10_SUCCESSOR_BYTE_CONTRACT.json"]
    result = docs["P5_C2_V10_RESULT.json"]
    ledger = docs["P5_C2_V10_NEGATIVE_LEDGER.json"]

    assert protocol["protocol_id"] == result["protocol_id"]
    assert result["arm_or_model_executed"] is False
    assert result["field_instances_closed"] == 0 and result["status"] == "BLOCKING"
    assert result["preserved"]["c2_v4_bound_fields"] == 7
    assert result["preserved"]["c2_v4_blocking_fields"] == 14
    assert result["preserved"]["panel_confirmatory_ready"] == "0/6"

    assert upstream["moss_public_refs"]["branches"] == [
        {"name": "main", "sha": "5453f1feebad44c199f5887f852fc5bc7fb7d4da"}
    ]
    assert upstream["moss_public_refs"]["tags"] == [
        {"name": "v0.1.0", "sha": "9f1b2929a6a1b6d405e0ce378d52cc8c8293618c"}
    ]
    assert upstream["moss_public_refs"]["releases"] == 0
    assert upstream["arxiv_v2_source"]["archive_member_count"] == 12
    assert upstream["arxiv_v2_source"]["exact_required_runner_mentions"] == 0
    assert upstream["arxiv_v2_source"]["supplement_or_companion_archive_members"] == []
    assert upstream["moss_main"]["benchmark_prefix_members"] == 0
    assert upstream["moss_v0_1_0"]["benchmark_prefix_members"] == 0
    assert upstream["claw_eval_pinned_companion_candidate"]["exact_required_runner_matches"] == 0
    assert upstream["claw_eval_pinned_companion_candidate"]["license_path_matches"] == 0

    assert route["demo_route"]["state"] == "BLOCKING"
    assert route["user_mode_route"]["state"] == "BLOCKING_FOR_V7_LANG1_NATIVE_TASK_ENVIRONMENT"
    assert route["user_mode_route"]["only_task_fields_forwarded"] == ["task_id", "user_prompt"]
    assert route["user_mode_route"]["trial_worker_volume_mounts"] == ["iter_dir:/iter_dir"]
    assert len(route["excerpts"]) == 7
    for e in route["excerpts"]:
        assert hashlib.sha256(e["text"].encode()).hexdigest() == e["text_sha256"]

    ids = [x["id"] for x in contract["required_byte_classes"]]
    assert ids == [
        "session", "source_mount", "pre_action_certificate",
        "public_evaluator", "write_reset_policy", "route_adapter",
    ]
    assert len(ledger["entries"]) == 3

    manifest = docs.get("ARTIFACT_MANIFEST_V10.json")
    if manifest is not None:
        for item in manifest["artifacts"]:
            p = ROOT / item["path"]
            assert p.is_file()
            assert p.stat().st_size == item["size_bytes"]
            assert sha256(p) == item["sha256"]

    print(json.dumps({
        "json_files_parsed": len(json_paths),
        "route_excerpts_verified": len(route["excerpts"]),
        "negative_entries_verified": len(ledger["entries"]),
        "required_successor_byte_classes": len(ids),
        "status": "PASS",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
