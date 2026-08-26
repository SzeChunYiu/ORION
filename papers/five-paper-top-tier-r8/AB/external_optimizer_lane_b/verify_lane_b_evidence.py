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
EXPECTED_REVIEW_COMMIT = "82e94b19b9b79733bd5353cb433e48fe338e4423"
EXPECTED_REVIEW_TREE = "a81360e61b5c4bfed9a45009f419b77f01735a18"
EXPECTED_CROSS_AUDIT_TERMINAL = (
    "AB_THEOREM_REPAIR_PARTIAL_PASS__T10_CONVENTION_REQUIRED"
)
EXPECTED_PATCH_SHA256 = (
    "0ebe9192f94839585a6d36661ffd0d9ce764a8b5490deb0faf88bfdd4a42d137"
)
EXPECTED_DONOR_SOURCES = {
    "10.1007/s00145-012-9124-7": (
        "d71379d217872301f6b085b3cc2383bc98b14e4413f4fde8c1dcdf1c88cc6d2c",
        380528,
    ),
    "10.1016/j.tcs.2014.10.014": (
        "f551ed1e386663b70ee0fe544c20b9d0fb0db83a031fa9fe777c7dbc1847247a",
        247527,
    ),
}
EXPECTED_MANIFEST_PATHS = {
    "AUDIT_REPORT.md",
    "MINIMAL_SAFE_INTEGRATION_PATCH.diff",
    "QMAP_AB_MAPPING_RESULT.json",
    "SOURCE_BINDINGS.json",
    "THEOREM_REPAIR_CROSS_AUDIT.json",
    "THEOREM_REPAIR_CROSS_AUDIT.md",
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


def verify_bundle(
    root: Path,
    external_source_root: Path | None = None,
    donor_source_root: Path | None = None,
) -> list[str]:
    """Return all bundle errors; an empty list is a pass."""

    root = root.resolve()
    errors: list[str] = []
    required = {
        "AUDIT_REPORT.md",
        "EVIDENCE_MANIFEST.json",
        "MINIMAL_SAFE_INTEGRATION_PATCH.diff",
        "QMAP_AB_MAPPING_RESULT.json",
        "SOURCE_BINDINGS.json",
        "THEOREM_REPAIR_CROSS_AUDIT.json",
        "THEOREM_REPAIR_CROSS_AUDIT.md",
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
        cross_audit = load_json(root / "THEOREM_REPAIR_CROSS_AUDIT.json")
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

    if bindings.get("schema") != "orion.ab.external_optimizer_source_bindings.v2":
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

    review = bindings.get("reviewed_hostile_audit", {})
    if review.get("commit") != EXPECTED_REVIEW_COMMIT:
        errors.append("hostile-review commit binding drift")
    if review.get("tree") != EXPECTED_REVIEW_TREE:
        errors.append("hostile-review tree binding drift")
    if review.get("cross_audit_terminal") != EXPECTED_CROSS_AUDIT_TERMINAL:
        errors.append("hostile-review cross-audit terminal drift")

    if cross_audit.get("reviewed_commit") != EXPECTED_REVIEW_COMMIT:
        errors.append("cross-audit reviewed commit drift")
    if cross_audit.get("reviewed_tree") != EXPECTED_REVIEW_TREE:
        errors.append("cross-audit reviewed tree drift")
    if cross_audit.get("terminal") != EXPECTED_CROSS_AUDIT_TERMINAL:
        errors.append("cross-audit terminal drift")
    theorem_verdicts = {
        row.get("id"): row.get("verdict") for row in cross_audit.get("objects", [])
    }
    if theorem_verdicts.get("AB-T10") != "REPAIR_INCOMPLETE":
        errors.append("Theorem 10 adverse cross-audit verdict drift")
    if theorem_verdicts.get("AB-T13") != "PASS_INTERNAL_CALIBRATION_ONLY":
        errors.append("Theorem 13 calibration-only ceiling drift")
    if cross_audit.get("donor_absorption", {}).get("broad_claim") != "DONOR_ABSORBED":
        errors.append("broad XOR donor-absorption status drift")
    if (
        cross_audit.get("claim_ceiling", {}).get("external_significance")
        != "CANNOT_CHECK"
    ):
        errors.append("AB-specific external-significance ceiling drift")

    donors = {
        entry.get("doi"): entry for entry in bindings.get("donor_primary_sources", [])
    }
    if set(donors) != set(EXPECTED_DONOR_SOURCES):
        errors.append("donor primary-source set drift")
    for doi, (expected_hash, expected_bytes) in EXPECTED_DONOR_SOURCES.items():
        entry = donors.get(doi, {})
        if entry.get("sha256") != expected_hash:
            errors.append(f"donor primary-source hash drift: {doi}")
        if entry.get("bytes") != expected_bytes:
            errors.append(f"donor primary-source byte-count drift: {doi}")

    harness_notes = bindings.get("harness_notes_non_authoritative", {})
    if harness_notes.get("authority") != (
        "PROVENANCE_ONLY__NOT_PRIMARY_SOURCE_OR_NOVELTY_MATHEMATICAL_"
        "VENUE_JOURNAL_AUTHORITY"
    ):
        errors.append("harness-note non-authority boundary drift")

    patch_binding = bindings.get("integration_patch_binding", {})
    if patch_binding.get("target_commit") != EXPECTED_REVIEW_COMMIT:
        errors.append("integration-patch target commit drift")
    if patch_binding.get("target_tree") != EXPECTED_REVIEW_TREE:
        errors.append("integration-patch target tree drift")
    if patch_binding.get("sha256") != EXPECTED_PATCH_SHA256:
        errors.append("integration-patch hash binding drift")
    _check_hash(
        root / "MINIMAL_SAFE_INTEGRATION_PATCH.diff",
        EXPECTED_PATCH_SHA256,
        errors,
        "minimal safe integration patch",
    )
    patch_bytes = (root / "MINIMAL_SAFE_INTEGRATION_PATCH.diff").stat().st_size
    if patch_bytes != patch_binding.get("bytes"):
        errors.append(
            "integration-patch byte-count mismatch: "
            f"expected {patch_binding.get('bytes')}, got {patch_bytes}"
        )
    if cross_audit.get("integration_patch", {}).get("sha256") != EXPECTED_PATCH_SHA256:
        errors.append("cross-audit integration-patch hash drift")

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

    theorem_report = (root / "THEOREM_REPAIR_CROSS_AUDIT.md").read_text(
        encoding="utf-8"
    )
    required_theorem_report_terms = (
        EXPECTED_CROSS_AUDIT_TERMINAL,
        "T10 | `REPAIR_INCOMPLETE`",
        "T13 | `PASS_INTERNAL_CALIBRATION_ONLY`",
        "10.1007/s00145-012-9124-7",
        "10.1016/j.tcs.2014.10.014",
        "AB-specific external significance and novelty remain `CANNOT_CHECK`",
    )
    for term in required_theorem_report_terms:
        if term not in theorem_report:
            errors.append(f"theorem cross-audit report is missing frozen term: {term}")

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

    if donor_source_root is not None:
        donor_source_root = donor_source_root.resolve()
        for entry in bindings.get("donor_primary_sources", []):
            path = donor_source_root / entry["cache_path"]
            _check_hash(path, entry["sha256"], errors, f"donor source {entry['doi']}")
            if path.is_file() and path.stat().st_size != entry["bytes"]:
                errors.append(
                    f"donor source byte-count mismatch for {entry['doi']}: "
                    f"expected {entry['bytes']}, got {path.stat().st_size}"
                )
        for entry in harness_notes.get("files", []):
            path = donor_source_root / entry["cache_path"]
            _check_hash(path, entry["sha256"], errors, "non-authoritative harness note")
            if path.is_file() and path.stat().st_size != entry["bytes"]:
                errors.append(
                    "non-authoritative harness-note byte-count mismatch: "
                    f"expected {entry['bytes']}, got {path.stat().st_size}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--external-source-root", type=Path)
    parser.add_argument("--donor-source-root", type=Path)
    args = parser.parse_args()
    errors = verify_bundle(
        args.root,
        external_source_root=args.external_source_root,
        donor_source_root=args.donor_source_root,
    )
    receipt = {
        "schema": "orion.ab.external_optimizer_verification_receipt.v1",
        "status": "PASS" if not errors else "FAIL",
        "terminal": "CANNOT_CHECK",
        "external_source_bytes_checked": args.external_source_root is not None,
        "donor_and_harness_note_bytes_checked": args.donor_source_root is not None,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
