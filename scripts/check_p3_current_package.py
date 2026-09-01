#!/usr/bin/env python3
"""Verify the superseded ORION-13 render and current dual-route package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/orion-13-global-knowledge-portrait"
LEGACY = PAPER / "journal_package"
CURRENT = PAPER / "submission/publication-ready-20260831"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_legacy(errors: list[str]) -> None:
    manifest = json.loads((LEGACY / "MANIFEST.json").read_text(encoding="utf-8"))
    state = json.loads(
        (LEGACY / "RENDER_CLOSURE_STATE.json").read_text(encoding="utf-8")
    )
    expected = (
        (manifest, "package_status", "SUPERSEDED"),
        (manifest, "scientific_authority_delta", "NONE"),
        (manifest.get("package_authority") or {}, "current_submission_authorized", False),
        (manifest.get("render_binding") or {}, "current_revision_binding", False),
        (manifest.get("render_binding") or {}, "binding_status", "HISTORICAL_SUPERSEDED"),
        (state, "state", "SUPERSEDED"),
    )
    for record, key, value in expected:
        if record.get(key) != value:
            errors.append(
                f"legacy {key}: expected {value!r}, got {record.get(key)!r}"
            )


def check_current(errors: list[str]) -> None:
    manifest_path = CURRENT / "PACKAGE_MANIFEST.json"
    sums_path = CURRENT / "SHA256SUMS"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = (
        ("schema", "ORION.dual-submission-package.v1"),
        ("paper", "ORION-13"),
        ("status", "PACKAGE_COMPLETE__PORTAL_INPUTS_PENDING"),
        (
            "terminal",
            "P3_C5_C9_REPLICATED_MAPPING__P3_C10_C11_EXACT_IDENTITY_AUTHORITY",
        ),
        ("scientific_authority_delta", "NONE"),
    )
    for key, value in expected:
        if manifest.get(key) != value:
            errors.append(f"current {key}: expected {value!r}, got {manifest.get(key)!r}")

    authority = ROOT / str(manifest.get("active_authority"))
    if not authority.is_file() or sha256(authority) != manifest.get(
        "active_authority_sha256"
    ):
        errors.append("current active-authority binding mismatch")

    actual_payload = {
        path.relative_to(CURRENT).as_posix()
        for path in CURRENT.rglob("*")
        if path.is_file() and path.name not in {"PACKAGE_MANIFEST.json", "SHA256SUMS"}
    }
    declared_payload = set(manifest.get("payload") or {})
    if actual_payload != declared_payload:
        errors.append("current manifest payload coverage mismatch")
    for relative, record in (manifest.get("payload") or {}).items():
        path = CURRENT / relative
        if (
            not path.is_file()
            or sha256(path) != record.get("sha256")
            or path.stat().st_size != record.get("bytes")
        ):
            errors.append(f"current manifest payload mismatch: {relative}")

    sums: dict[str, str] = {}
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        sums[relative] = digest
    expected_sums = actual_payload | {"PACKAGE_MANIFEST.json"}
    if set(sums) != expected_sums:
        errors.append("current SHA256SUMS coverage mismatch")
    for relative, digest in sums.items():
        if not (CURRENT / relative).is_file() or sha256(CURRENT / relative) != digest:
            errors.append(f"current SHA256SUMS mismatch: {relative}")

    inventory = json.loads(
        (CURRENT / "ATOMIC_CLAIM_INVENTORY.json").read_text(encoding="utf-8")
    )
    retention = (CURRENT / "RESULT_RETENTION.md").read_text(encoding="utf-8")
    negatives = inventory.get("retained_negative_null_open_cannot_check") or []
    if not negatives or any(item not in retention for item in negatives):
        errors.append("current negative/null result retention mismatch")
    if manifest.get("identity") != {
        "source": "papers/AUTHOR_IDENTITY_V1.json",
        "name": "Sze Chun Yiu",
        "affiliation": "Stockholm University",
        "email": "sze-chun.yiu@fysik.su.se",
    }:
        errors.append("current canonical identity mismatch")
    if manifest.get("arxiv", {}).get("pages") != 9 or manifest.get("journal", {}).get(
        "pages"
    ) != 9:
        errors.append("current route page-count binding mismatch")


def main() -> int:
    errors: list[str] = []
    check_legacy(errors)
    check_current(errors)
    if errors:
        for error in errors:
            print(f"P3_CURRENT_PACKAGE_ERROR: {error}")
        return 1
    print("P3_HISTORICAL_RENDER_SUPERSEDED__CURRENT_DUAL_ROUTE_PACKAGE_BOUND")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
