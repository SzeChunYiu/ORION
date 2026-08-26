"""Verify the frozen JOB-AB-R8-2 source and evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import qmap_ab_faithfulness as audit

EXPECTED_CANDIDATE = "MQT_QMAP_CLIFFORD_SYNTHESIS"
EXPECTED_COMMIT = "6a0d8a2ff411a0e2c9604c71aff80ba633c0d660"
EXPECTED_TREE = "9a5ad960beb63a0cc23f78b289e629da58b99941"
EXPECTED_PAPER_SHA256 = (
    "bea4eea2fc32f6d35b0df4fc68501c93b032083d42a66f90fcab219b0c03c082"
)
EXPECTED_MANIFEST_PATHS = {
    "AUDIT_REPORT.md",
    "QMAP_AB_MAPPING_RESULT.json",
    "SOURCE_BINDINGS.json",
    "qmap_ab_faithfulness.py",
    "tests/test_qmap_ab_faithfulness.py",
    "tests/test_verify_lane_b_evidence.py",
    "verify_lane_b_evidence.py",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError("could not locate repository root")


def _check_hash(path: Path, expected: str, errors: list[str], label: str) -> None:
    if not path.is_file():
        errors.append(f"missing {label}: {path}")
        return
    actual = sha256_file(path)
    if actual != expected:
        errors.append(f"hash mismatch for {label}: expected {expected}, got {actual}")


def verify_bundle(root: Path, external_source_root: Path | None = None) -> list[str]:
    """Return all bundle errors; an empty list is a pass."""

    root = root.resolve()
    errors: list[str] = []
    required = {
        "AUDIT_REPORT.md",
        "EVIDENCE_MANIFEST.json",
        "QMAP_AB_MAPPING_RESULT.json",
        "SOURCE_BINDINGS.json",
        "qmap_ab_faithfulness.py",
        "verify_lane_b_evidence.py",
    }
    for relative in sorted(required):
        if not (root / relative).is_file():
            errors.append(f"missing required artifact: {relative}")
    if errors:
        return errors

    try:
        result = load_json(root / "QMAP_AB_MAPPING_RESULT.json")
        bindings = load_json(root / "SOURCE_BINDINGS.json")
        manifest = load_json(root / "EVIDENCE_MANIFEST.json")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"could not load frozen JSON: {exc}"]

    expected_result = audit.assess_faithfulness()
    if result != expected_result:
        errors.append(
            "QMAP_AB_MAPPING_RESULT.json does not match executable assessment"
        )
    if result.get("terminal") != "CANNOT_CHECK":
        errors.append("terminal drifted from CANNOT_CHECK")
    if result.get("faithful_external_realization") is not False:
        errors.append("faithful_external_realization must remain false")

    if bindings.get("schema") != "orion.ab.external_optimizer_source_bindings.v1":
        errors.append("unexpected source-binding schema")
    if bindings.get("candidate") != EXPECTED_CANDIDATE:
        errors.append("candidate binding drift")
    paper = bindings.get("primary_paper", {})
    if paper.get("sha256") != EXPECTED_PAPER_SHA256:
        errors.append("primary paper hash binding drift")
    code = bindings.get("open_code", {})
    if code.get("commit") != EXPECTED_COMMIT:
        errors.append("QMAP commit binding drift")
    if code.get("tree") != EXPECTED_TREE:
        errors.append("QMAP tree binding drift")
    if code.get("license") != "MIT":
        errors.append("QMAP license binding drift")

    try:
        repo_root = find_repo_root(root)
    except FileNotFoundError as exc:
        errors.append(str(exc))
    else:
        for entry in bindings.get("local_ab_contract", {}).get("files", []):
            _check_hash(
                repo_root / entry["path"],
                entry["sha256"],
                errors,
                f"local AB source {entry['path']}",
            )

    entries = manifest.get("files", [])
    manifest_paths = {entry.get("path") for entry in entries}
    if manifest.get("schema") != "orion.ab.external_optimizer_evidence_manifest.v1":
        errors.append("unexpected evidence-manifest schema")
    if manifest_paths != EXPECTED_MANIFEST_PATHS:
        errors.append(
            "evidence manifest path set drift: "
            f"expected {sorted(EXPECTED_MANIFEST_PATHS)}, got {sorted(manifest_paths)}"
        )
    for entry in entries:
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            errors.append("malformed evidence-manifest entry")
            continue
        _check_hash(root / relative, expected_hash, errors, f"evidence {relative}")

    report = (root / "AUDIT_REPORT.md").read_text(encoding="utf-8")
    required_report_terms = (
        "Terminal: `CANNOT_CHECK`",
        "EXTERNAL_MOVE_DECREASES_LIVE_FRAGMENT_CARDINALITY_WITHOUT_GARBAGE_QUOTIENT",
        EXPECTED_COMMIT,
        EXPECTED_PAPER_SHA256,
    )
    for term in required_report_terms:
        if term not in report:
            errors.append(f"audit report is missing frozen term: {term}")

    if external_source_root is not None:
        external_source_root = external_source_root.resolve()
        _check_hash(
            external_source_root / paper["cache_path"],
            paper["sha256"],
            errors,
            "primary paper cache",
        )
        if (external_source_root / paper["cache_path"]).is_file():
            actual_bytes = (external_source_root / paper["cache_path"]).stat().st_size
            if actual_bytes != paper["bytes"]:
                errors.append(
                    "primary paper byte-count mismatch: "
                    f"expected {paper['bytes']}, got {actual_bytes}"
                )
        _check_hash(
            external_source_root / "qmap/LICENSE.md",
            code["license_file_sha256"],
            errors,
            "QMAP license cache",
        )
        for entry in code.get("files", []):
            _check_hash(
                external_source_root / entry["cache_path"],
                entry["sha256"],
                errors,
                f"QMAP source cache {entry['path']}",
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--external-source-root", type=Path)
    args = parser.parse_args()
    errors = verify_bundle(args.root, args.external_source_root)
    receipt = {
        "schema": "orion.ab.external_optimizer_verification_receipt.v1",
        "status": "PASS" if not errors else "FAIL",
        "terminal": "CANNOT_CHECK",
        "external_source_bytes_checked": args.external_source_root is not None,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
