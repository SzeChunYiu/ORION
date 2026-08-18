"""ScientificResultVerification.v1 writer and fail-closed validator.

This module is the programme verifier contract for issue #283. It does not
import paper scoring internals. A record reports evidence; it cannot authorize
the claim it describes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "orion.scientific-result-verification.v1"
SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "SCIENTIFIC_RESULT_VERIFICATION_V1.json"
HEX64 = set("0123456789abcdef")
HEX40 = HEX64
PAPER_IDS = {"P1", "P2", "P3", "P4", "P5"}
STATES = {"VERIFIED", "BOUNDED_VERIFIED", "INVALIDATED", "CANNOT_CHECK"}
LAYER_STATUSES = {"PASS", "FAIL", "CANNOT_CHECK", "NOT_RUN"}
LAYER_NAMES = (
    "raw_artifact_replay",
    "independent_scorer",
    "leakage_shortcut",
    "denominator_statistics",
    "baseline_pressure",
    "holdout_cross_host",
)
ARTIFACT_ROLES = {
    "raw_record",
    "gold",
    "aggregate",
    "manifest",
    "telemetry",
    "protocol",
    "published_table",
    "missing_required",
}


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(ch in HEX64 for ch in value)


def missing_artifact_record(
    *,
    path: str,
    role: str = "missing_required",
) -> dict[str, Any]:
    return {
        "path": path,
        "role": role,
        "present": False,
        "sha256": "CANNOT_CHECK",
    }


def present_artifact(path: Path, role: str, *, root: Path | None = None) -> dict[str, Any]:
    relative = str(path) if root is None else str(path.relative_to(root))
    if not path.is_file():
        return missing_artifact_record(path=relative, role="missing_required")
    return {
        "path": relative,
        "role": role,
        "present": True,
        "sha256": sha256_file(path),
    }


def layer_result(status: str, summary: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    if status not in LAYER_STATUSES:
        raise ValueError(f"invalid layer status: {status!r}")
    payload: dict[str, Any] = {"status": status, "summary": summary}
    if details is not None:
        payload["details"] = details
    return payload


def decide_verification_state(
    *,
    layers: dict[str, Any],
    discrepancies: list[dict[str, Any]],
    required_artifacts_missing: bool,
    numbers_replayed: bool,
    independent_agrees: bool,
) -> tuple[str, str | None]:
    """Fail closed. Missing required artifacts can never yield VERIFIED."""
    high = [d for d in discrepancies if d.get("severity") == "high"]
    layer_fail = any(layers[name]["status"] == "FAIL" for name in LAYER_NAMES if name in layers)
    if required_artifacts_missing and not numbers_replayed:
        if layer_fail or high:
            return "INVALIDATED", "required raw artifacts missing and a layer or integrity check failed"
        return "CANNOT_CHECK", None
    if layer_fail and not numbers_replayed:
        return "INVALIDATED", "a verification layer failed and headline numbers did not replay"
    if high and not numbers_replayed:
        return "INVALIDATED", "; ".join(str(item.get("text", item)) for item in high)
    holdout = layers.get("holdout_cross_host", {}).get("status")
    leakage = layers.get("leakage_shortcut", {}).get("status")
    replay = layers.get("raw_artifact_replay", {}).get("status")
    scorer = layers.get("independent_scorer", {}).get("status")
    denom = layers.get("denominator_statistics", {}).get("status")
    core_pass = replay == "PASS" and scorer == "PASS" and denom == "PASS" and independent_agrees and numbers_replayed
    if core_pass and holdout == "PASS" and leakage == "PASS" and not high and not required_artifacts_missing:
        return "VERIFIED", None
    if numbers_replayed and independent_agrees and not layer_fail:
        return "BOUNDED_VERIFIED", None
    if required_artifacts_missing:
        return "CANNOT_CHECK", None
    return "BOUNDED_VERIFIED", None


def validate_record(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("wrong schema_version")
    if payload.get("self_authorizing") is not False:
        errors.append("self_authorizing must be false")
    if payload.get("paper_id") not in PAPER_IDS:
        errors.append(f"invalid paper_id: {payload.get('paper_id')!r}")
    for field in (
        "record_id",
        "claim_id",
        "atomic_claim_text",
        "bounded_claim_text",
        "subject",
        "protocol",
        "raw_artifacts",
        "scorers",
        "denominator",
        "layers",
        "verification_state",
        "discrepancies",
        "high_severity_integrity",
    ):
        if field not in payload:
            errors.append(f"missing field: {field}")
    state = payload.get("verification_state")
    if state not in STATES:
        errors.append(f"invalid verification_state: {state!r}")
    if state == "INVALIDATED" and not payload.get("invalidation_reason"):
        errors.append("INVALIDATED requires invalidation_reason")
    if state != "INVALIDATED" and payload.get("invalidation_reason") not in {None, "", False}:
        # allow omitted or explicit null only
        if "invalidation_reason" in payload and payload.get("invalidation_reason") not in {None}:
            errors.append("invalidation_reason is only allowed when verification_state is INVALIDATED")

    subject = payload.get("subject")
    if isinstance(subject, dict):
        if not _is_hex(subject.get("commit"), 40):
            errors.append("subject.commit must be a 40-character lowercase git SHA")
        if subject.get("evaluated_system_mutated") is not False:
            errors.append("subject.evaluated_system_mutated must be false")
        tree = subject.get("tree")
        if tree is not None and not _is_hex(tree, 40):
            errors.append("subject.tree must be a 40-character lowercase git SHA or null")
    else:
        errors.append("subject must be an object")

    protocol = payload.get("protocol")
    if isinstance(protocol, dict):
        if not protocol.get("id"):
            errors.append("protocol.id missing")
        digest = protocol.get("hash_sha256")
        if digest != "CANNOT_CHECK" and not _is_hex(digest, 64):
            errors.append("protocol.hash_sha256 must be SHA-256 hex or CANNOT_CHECK")
    else:
        errors.append("protocol must be an object")

    artifacts = payload.get("raw_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("raw_artifacts must be a non-empty array")
    else:
        missing_required = False
        for index, item in enumerate(artifacts):
            if not isinstance(item, dict):
                errors.append(f"raw_artifacts[{index}] must be an object")
                continue
            if item.get("role") not in ARTIFACT_ROLES:
                errors.append(f"raw_artifacts[{index}].role invalid")
            if not item.get("path"):
                errors.append(f"raw_artifacts[{index}].path missing")
            if "present" not in item:
                errors.append(f"raw_artifacts[{index}].present missing")
            digest = item.get("sha256")
            if item.get("present") is True and not _is_hex(digest, 64):
                errors.append(f"raw_artifacts[{index}] present artifact must have SHA-256 hex")
            if item.get("present") is False:
                if digest != "CANNOT_CHECK":
                    errors.append(f"raw_artifacts[{index}] missing artifact sha256 must be CANNOT_CHECK")
                if item.get("role") == "missing_required":
                    missing_required = True
        if state == "VERIFIED" and missing_required:
            errors.append("VERIFIED is forbidden when a required artifact is missing")

    scorers = payload.get("scorers")
    if isinstance(scorers, dict):
        if scorers.get("independent_from_written_spec") is not True and state == "VERIFIED":
            errors.append("VERIFIED requires independent_from_written_spec=true")
        if scorers.get("agreement") not in {"EXACT", "DISAGREE", "CANNOT_CHECK"}:
            errors.append("scorers.agreement invalid")
        if not isinstance(scorers.get("adjudication"), list):
            errors.append("scorers.adjudication must be an array")
        for key in ("original_hash_sha256", "independent_hash_sha256"):
            value = scorers.get(key)
            if value != "CANNOT_CHECK" and not _is_hex(value, 64):
                errors.append(f"scorers.{key} must be SHA-256 hex or CANNOT_CHECK")
    else:
        errors.append("scorers must be an object")

    denom = payload.get("denominator")
    if isinstance(denom, dict):
        for field in (
            "eligible_n",
            "unit",
            "repeats_nested_not_inflating_n",
            "cannot_check_or_invalid_handling",
            "post_outcome_exclusions",
        ):
            if field not in denom:
                errors.append(f"denominator.{field} missing")
        if denom.get("repeats_nested_not_inflating_n") is not True and state == "VERIFIED":
            errors.append("VERIFIED requires repeats_nested_not_inflating_n=true")
    else:
        errors.append("denominator must be an object")

    layers = payload.get("layers")
    if isinstance(layers, dict):
        for name in LAYER_NAMES:
            layer = layers.get(name)
            if not isinstance(layer, dict):
                errors.append(f"layers.{name} missing")
                continue
            if layer.get("status") not in LAYER_STATUSES:
                errors.append(f"layers.{name}.status invalid")
            if not layer.get("summary"):
                errors.append(f"layers.{name}.summary missing")
        if state == "VERIFIED":
            for name in ("raw_artifact_replay", "independent_scorer", "denominator_statistics"):
                if layers.get(name, {}).get("status") != "PASS":
                    errors.append(f"VERIFIED requires layers.{name}.status=PASS")
            if layers.get("holdout_cross_host", {}).get("status") == "CANNOT_CHECK":
                errors.append("VERIFIED forbids holdout_cross_host CANNOT_CHECK; use BOUNDED_VERIFIED")
    else:
        errors.append("layers must be an object")

    discrepancies = payload.get("discrepancies")
    if not isinstance(discrepancies, list):
        errors.append("discrepancies must be an array")
    else:
        for index, item in enumerate(discrepancies):
            if not isinstance(item, dict) or not item.get("id") or not item.get("text"):
                errors.append(f"discrepancies[{index}] invalid")
            elif item.get("severity") not in {"low", "medium", "high"}:
                errors.append(f"discrepancies[{index}].severity invalid")

    high = payload.get("high_severity_integrity")
    if not isinstance(high, list):
        errors.append("high_severity_integrity must be an array")
    elif state == "VERIFIED" and high:
        errors.append("VERIFIED forbids unresolved high_severity_integrity entries")

    digest = payload.get("record_sha256")
    if digest is not None:
        if not _is_hex(digest, 64):
            errors.append("record_sha256 must be SHA-256 hex")
        else:
            body = {key: value for key, value in payload.items() if key != "record_sha256"}
            if sha256_digest(body) != digest:
                errors.append("record_sha256 does not match canonical payload")
    return errors


def write_record(payload: dict[str, Any]) -> dict[str, Any]:
    errors = validate_record({key: value for key, value in payload.items() if key != "record_sha256"})
    if errors:
        raise ValueError("invalid ScientificResultVerification.v1: " + "; ".join(errors))
    body = dict(payload)
    body.pop("record_sha256", None)
    body["record_sha256"] = sha256_digest(body)
    return body


def dump_record(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    record = write_record(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def load_and_validate(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain one JSON object")
    errors = validate_record(payload)
    if errors:
        raise ValueError(f"{path} invalid: " + "; ".join(errors))
    return payload
