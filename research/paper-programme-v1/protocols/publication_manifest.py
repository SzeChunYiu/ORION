#!/usr/bin/env python3
"""Validate and content-address ORION publication protocols/run manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


PROTOCOL_SCHEMA_VERSION = "orion.publication-protocol.v1"
RUN_SCHEMA_VERSION = "orion.publication-run-manifest.v1"
HEX = set("0123456789abcdef")


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _iter_unbound(value: Any, path: str = "$") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _iter_unbound(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_unbound(child, f"{path}[{index}]")
    elif isinstance(value, str) and "UNBOUND" in value.upper():
        yield path


def unbound_paths(payload: Any) -> list[str]:
    return sorted(_iter_unbound(payload))


def _is_hex(value: str, length: int) -> bool:
    return len(value) == length and all(ch in HEX for ch in value)


def validate_protocol(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != PROTOCOL_SCHEMA_VERSION:
        errors.append("wrong protocol schema_version")
    status = payload.get("protocol_status")
    outcome_accessed = payload.get("outcome_accessed")
    if status not in {"DESIGN_FROZEN", "EXECUTION_FROZEN", "OUTCOME_ACCESSED", "INVALIDATED"}:
        errors.append(f"invalid protocol_status: {status!r}")
    if status in {"DESIGN_FROZEN", "EXECUTION_FROZEN"} and outcome_accessed is not False:
        errors.append(f"{status} requires outcome_accessed=false")
    if status == "OUTCOME_ACCESSED" and outcome_accessed is not True:
        errors.append("OUTCOME_ACCESSED requires outcome_accessed=true")

    for field in ("paper_id", "protocol_id", "primary_hypothesis", "task_families", "baselines", "ablations", "metrics", "statistics", "access_policy", "plots", "tables", "execution_bindings"):
        if field not in payload:
            errors.append(f"missing protocol field: {field}")

    bindings = payload.get("execution_bindings", {})
    if status in {"EXECUTION_FROZEN", "OUTCOME_ACCESSED"}:
        remaining = unbound_paths(bindings)
        if remaining:
            errors.append("execution-frozen protocol still contains UNBOUND fields: " + ", ".join(remaining))
        subject = bindings.get("subject_revision") if isinstance(bindings, dict) else None
        if not isinstance(subject, str) or not _is_hex(subject, 40):
            errors.append("execution-frozen subject_revision must be a full 40-character lowercase git SHA")
    return errors


def validate_run_manifest(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append("wrong run manifest schema_version")
    if payload.get("created_before_outcome_access") is not True:
        errors.append("run manifest must be created_before_outcome_access=true")
    subject = payload.get("subject_revision")
    if not isinstance(subject, str) or not _is_hex(subject, 40):
        errors.append("subject_revision must be a full 40-character lowercase git SHA")
    protocol_digest = payload.get("protocol_digest")
    if not isinstance(protocol_digest, str) or not _is_hex(protocol_digest, 64):
        errors.append("protocol_digest must be a lowercase SHA-256 hex digest")
    for field in ("paper_id", "protocol_id", "data_artifacts", "model_provider_revisions", "baseline_config_hashes", "evaluator_hash", "split_hashes", "evaluation_epoch", "seeds", "resource_limits", "environment", "access_policy_hash", "artifact_root"):
        if field not in payload:
            errors.append(f"missing run manifest field: {field}")
    remaining = unbound_paths(payload)
    if remaining:
        errors.append("run manifest contains UNBOUND fields: " + ", ".join(remaining))
    return errors


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return payload


def validate_file(path: Path, kind: str) -> dict[str, Any]:
    payload = load_json(path)
    if kind == "protocol":
        errors = validate_protocol(payload)
    elif kind == "run":
        errors = validate_run_manifest(payload)
    else:
        raise ValueError(kind)
    return {
        "path": str(path),
        "kind": kind,
        "valid": not errors,
        "digest_sha256": sha256_digest(payload),
        "unbound_paths": unbound_paths(payload),
        "errors": errors,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("protocol", "run"))
    parser.add_argument("files", nargs="+", type=Path)
    return parser


def main() -> None:
    args = _parser().parse_args()
    reports = [validate_file(path, args.kind) for path in args.files]
    print(json.dumps(reports, indent=2, sort_keys=True))
    if any(not report["valid"] for report in reports):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
