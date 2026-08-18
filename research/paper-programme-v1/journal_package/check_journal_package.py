#!/usr/bin/env python3
"""Validate ORION journal packages for P1–P5.

This checker owns Gate 7–9 *inventory*: required files exist, hashes match,
missing submission artifacts stay CANNOT_CHECK, and claims without artifacts
stay OPEN. It does not mint ScientificResultVerification.v1 (issue #283).
Compiled PDFs are admitted only for packages that declare ``SUBMISSION_READY``
and bind the PDF as a required, checksummed file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "orion.journal-package.v1"
PAPER_DIRS = {
    "P1": Path("papers/paper-01-recursive-epistemic-reconstruction"),
    "P2": Path("papers/paper-02-open-world-scientific-discovery"),
    "P3": Path("papers/paper-03-global-knowledge-portrait"),
    "P4": Path("papers/paper-04-verified-scientific-discovery"),
    "P5": Path("papers/paper-05-self-orion"),
}
PACKAGE_DOCS = (
    "MANIFEST.json",
    "COMPILE.md",
    "LICENSE.md",
    "CLAIM_PDF_AUDIT.md",
    "README.md",
)
ALLOWED_CLAIM_STATUS = {
    "SUPPORTED",
    "NOT_SUPPORTED",
    "BOUNDED",
    "CANNOT_CHECK",
    "OPEN",
}
VERIFICATION_SCHEMA_MARKERS = (
    "ScientificResultVerification.v1",
    "orion.scientific-result-verification.v1",
)
VERIFICATION_RECORDS_DIR = Path("research/verification/records")
HEX = set("0123456789abcdef")
P2_CLAIM_BOUNDARY = "NARROWED_METHODS_AND_CRITICAL_SYSTEM_DESIGN__NO_EXTERNAL_ORION_SUPERIORITY"
P2_UNRESOLVED_CLAIMS = {"P2.H1"}


class PackageReport:
    def __init__(self, paper_id: str, paper_root: Path) -> None:
        self.paper_id = paper_id
        self.paper_root = paper_root
        self.errors: list[str] = []
        self.notes: list[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha(value: str, length: int) -> bool:
    return len(value) == length and all(ch in HEX for ch in value.lower())


def load_manifest(package_dir: Path) -> dict[str, Any]:
    path = package_dir / "MANIFEST.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return payload


def parse_sha256sums(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, rest = line.partition("  ")
        if not rest or not _is_sha(digest, 64):
            raise ValueError(f"malformed SHA256SUMS line: {raw!r}")
        mapping[rest] = digest.lower()
    return mapping


def write_sha256sums(paper_root: Path, relative_paths: list[str]) -> str:
    lines: list[str] = []
    for relative in relative_paths:
        target = paper_root / relative
        lines.append(f"{sha256_file(target)}  {relative}")
    text = "\n".join(lines) + "\n"
    (paper_root / "journal_package" / "SHA256SUMS").write_text(text, encoding="utf-8")
    return text


def hashed_paths(manifest: dict[str, Any]) -> list[str]:
    paths = [f"journal_package/{name}" for name in PACKAGE_DOCS]
    for entry in manifest.get("required_files", []):
        path = entry.get("path")
        if isinstance(path, str) and path not in paths:
            paths.append(path)
    return paths


def _verification_schema(payload: dict[str, Any]) -> str:
    return str(payload.get("schema_version") or payload.get("schema") or "")


def consume_verification_records(
    paper_id: str, paper_root: Path, repo_root: Path | None
) -> list[str]:
    """Consume issue #283 records; do not fork their schema."""
    found: list[str] = []
    evidence = paper_root / "evidence"
    if evidence.is_dir():
        for path in sorted(evidence.rglob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict) and _verification_schema(payload) in VERIFICATION_SCHEMA_MARKERS:
                found.append(str(path.relative_to(paper_root)))
    if repo_root is not None:
        records_dir = repo_root / VERIFICATION_RECORDS_DIR
        if records_dir.is_dir():
            for path in sorted(records_dir.glob("*.json")):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if not isinstance(payload, dict):
                    continue
                if _verification_schema(payload) not in VERIFICATION_SCHEMA_MARKERS:
                    continue
                if payload.get("paper_id") != paper_id:
                    continue
                found.append(str(path.relative_to(repo_root)))
    return found


def _p1_h1_verdict(paper_root: Path) -> str | None:
    table = paper_root / "results" / "P1-T2_baseline_ablation_results.json"
    if not table.is_file():
        return None
    payload = json.loads(table.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("system_id") != "orion_full":
            continue
        assessment = (row.get("difference_vs_comparator") or {}).get("assessment") or {}
        if assessment.get("hypothesis_id") == "P1.H1":
            verdict = assessment.get("verdict")
            return str(verdict) if verdict is not None else None
    return None


def check_package(paper_id: str, paper_root: Path, *, repo_root: Path | None = None) -> PackageReport:
    report = PackageReport(paper_id, paper_root)
    package_dir = paper_root / "journal_package"
    if not package_dir.is_dir():
        report.errors.append("journal_package/ directory is missing")
        return report

    for name in (*PACKAGE_DOCS, "SHA256SUMS"):
        if not (package_dir / name).is_file():
            report.errors.append(f"required package file missing: journal_package/{name}")
    if report.errors:
        return report

    try:
        manifest = load_manifest(package_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report.errors.append(f"MANIFEST.json unreadable: {exc}")
        return report

    if manifest.get("schema_version") != SCHEMA_VERSION:
        report.errors.append(f"wrong schema_version: {manifest.get('schema_version')!r}")
    if manifest.get("paper_id") != paper_id:
        report.errors.append(f"paper_id mismatch: {manifest.get('paper_id')!r} != {paper_id!r}")
    if manifest.get("package_status") not in {"SCAFFOLDING", "SUBMISSION_READY"}:
        report.errors.append(f"invalid package_status: {manifest.get('package_status')!r}")
    revision = manifest.get("audit_subject_revision")
    if not isinstance(revision, str) or not _is_sha(revision, 40):
        report.errors.append("audit_subject_revision must be a 40-character git SHA")

    required = manifest.get("required_files")
    if not isinstance(required, list) or not required:
        report.errors.append("required_files must be a non-empty array")
        required = []
    required_paths: set[str] = set()
    for entry in required:
        if not isinstance(entry, dict) or not entry.get("path") or not entry.get("role"):
            report.errors.append(f"malformed required_files entry: {entry!r}")
            continue
        path = str(entry["path"])
        required_paths.add(path)
        target = paper_root / path
        if not target.is_file():
            report.errors.append(f"required file missing: {entry['path']}")

    operations = manifest.get("submission_operations", [])
    if not isinstance(operations, list):
        report.errors.append("submission_operations must be an array")
        operations = []
    operation_paths: set[str] = set()
    for entry in operations:
        if not isinstance(entry, dict):
            report.errors.append(f"malformed submission_operations entry: {entry!r}")
            continue
        expected_keys = {"path", "role", "status", "reason"}
        if set(entry) != expected_keys:
            report.errors.append(
                f"submission_operations entry must contain exactly {sorted(expected_keys)}: {entry!r}"
            )
            continue
        path = entry.get("path")
        if not all(isinstance(entry.get(key), str) and entry.get(key) for key in ("path", "role", "reason")):
            report.errors.append(f"malformed submission_operations entry: {entry!r}")
            continue
        if entry.get("status") != "SUBMISSION_OPERATION":
            report.errors.append(
                f"submission operation {path!r} must be SUBMISSION_OPERATION, not {entry.get('status')!r}"
            )
        if path in operation_paths:
            report.errors.append(f"duplicate submission operation path: {path}")
        operation_paths.add(path)
        if path in required_paths:
            report.errors.append(f"submission operation is also a required file: {path}")

    readiness = manifest.get("readiness_scope")
    if readiness is not None:
        if paper_id != "P2":
            report.errors.append("readiness_scope is only allowed for P2")
        elif not isinstance(readiness, dict):
            report.errors.append("P2 readiness_scope must be an object")
        else:
            expected_keys = {
                "scope_id", "terminal", "claim_boundary", "attestation_path",
                "unresolved_claims", "external_superiority",
            }
            if set(readiness) != expected_keys:
                report.errors.append(
                    f"P2 readiness_scope must contain exactly {sorted(expected_keys)}"
                )
            if readiness.get("scope_id") != "P2_NARROWED":
                report.errors.append("P2 readiness_scope.scope_id must be P2_NARROWED")
            if readiness.get("terminal") != manifest.get("declared_paper_terminal"):
                report.errors.append(
                    "P2 readiness_scope.terminal must match declared_paper_terminal"
                )
            if readiness.get("terminal") != "PEER_REVIEW_READY":
                report.errors.append(
                    "P2 readiness_scope.terminal must be PEER_REVIEW_READY"
                )
            if readiness.get("claim_boundary") != manifest.get("claim_boundary"):
                report.errors.append(
                    "P2 readiness_scope.claim_boundary must match manifest claim_boundary"
                )
            if readiness.get("claim_boundary") != P2_CLAIM_BOUNDARY:
                report.errors.append("P2 readiness_scope.claim_boundary is not the approved boundary")
            attestation = readiness.get("attestation_path")
            if not isinstance(attestation, str) or not attestation:
                report.errors.append("P2 readiness_scope.attestation_path must be non-empty")
            else:
                if Path(attestation).is_absolute() or ".." in Path(attestation).parts:
                    report.errors.append("P2 readiness_scope.attestation_path must be package-relative")
                if not (paper_root / attestation).is_file():
                    report.errors.append(
                        f"P2 readiness_scope attestation missing: {attestation}"
                    )
                if attestation not in required_paths:
                    report.errors.append(
                        "P2 readiness_scope.attestation_path must be a required file"
                    )
            unresolved = readiness.get("unresolved_claims")
            if not isinstance(unresolved, list) or any(
                not isinstance(item, str) or not item for item in unresolved
            ):
                report.errors.append(
                    "P2 readiness_scope.unresolved_claims must be a non-empty string array"
                )
            elif set(unresolved) != P2_UNRESOLVED_CLAIMS:
                report.errors.append(
                    "P2 readiness_scope.unresolved_claims must be exactly P2.H1"
                )
            if readiness.get("external_superiority") != "CANNOT_CHECK":
                report.errors.append(
                    "P2 readiness_scope.external_superiority must be CANNOT_CHECK"
                )

    missing = manifest.get("missing_artifacts")
    if not isinstance(missing, list):
        report.errors.append("missing_artifacts must be an array")
        missing = []
    for entry in missing:
        if not isinstance(entry, dict):
            report.errors.append(f"malformed missing_artifacts entry: {entry!r}")
            continue
        if entry.get("status") != "CANNOT_CHECK":
            report.errors.append(
                f"missing artifact {entry.get('path')!r} must be CANNOT_CHECK, not {entry.get('status')!r}"
            )
        if not entry.get("reason"):
            report.errors.append(f"missing artifact {entry.get('path')!r} has empty reason")
        path = entry.get("path")
        if isinstance(path, str) and (paper_root / path).is_file():
            report.errors.append(f"missing artifact is actually present: {path}")
        if isinstance(path, str) and path.endswith(".pdf") and "unready" not in str(entry.get("reason", "")).lower():
            # Fabricating a PDF of an unready manuscript is forbidden; presence is already rejected.
            pass

    claims = manifest.get("claims")
    if not isinstance(claims, list) or not claims:
        report.errors.append("claims must be a non-empty array")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict):
            report.errors.append(f"malformed claim: {claim!r}")
            continue
        status = claim.get("status")
        artifacts = claim.get("artifacts")
        claim_id = claim.get("id")
        if status not in ALLOWED_CLAIM_STATUS:
            report.errors.append(f"claim {claim_id!r} has invalid status {status!r}")
            continue
        if not isinstance(artifacts, list):
            report.errors.append(f"claim {claim_id!r} artifacts must be an array")
            continue
        if status == "OPEN":
            if artifacts:
                report.errors.append(f"OPEN claim {claim_id!r} must not cite artifacts")
            continue
        if not artifacts:
            report.errors.append(f"claim {claim_id!r} has no artifacts; status must be OPEN")
            continue
        present = [(paper_root / path).is_file() for path in artifacts if isinstance(path, str)]
        if status in {"SUPPORTED", "NOT_SUPPORTED", "BOUNDED"} and not all(present):
            report.errors.append(f"claim {claim_id!r} status {status} but an artifact is missing")
        if status == "CANNOT_CHECK" and all(present) and present:
            report.notes.append(
                f"claim {claim_id!r} is CANNOT_CHECK while cited artifacts exist; keep if authority is still insufficient"
            )

    if manifest.get("package_status") == "SUBMISSION_READY":
        if missing:
            report.errors.append("SUBMISSION_READY package must not list missing_artifacts")
        open_claims = [
            claim.get("id")
            for claim in claims
            if isinstance(claim, dict) and claim.get("status") == "OPEN"
        ]
        if open_claims:
            report.errors.append(
                "SUBMISSION_READY package has OPEN claims: " + ", ".join(map(str, open_claims))
            )

    verification = manifest.get("scientific_result_verification")
    if not isinstance(verification, dict):
        report.errors.append("scientific_result_verification object missing")
    else:
        if verification.get("owner_issue") != 283:
            report.errors.append("scientific_result_verification.owner_issue must be 283")
        if verification.get("schema_name") != "ScientificResultVerification.v1":
            report.errors.append("must consume ScientificResultVerification.v1, not a forked schema")
        found = consume_verification_records(paper_id, paper_root, repo_root)
        recorded = verification.get("records_present")
        if not isinstance(recorded, list):
            report.errors.append("scientific_result_verification.records_present must be an array")
        elif sorted(found) != sorted(str(item) for item in recorded):
            report.errors.append(
                "scientific_result_verification.records_present does not match files found under evidence/"
            )

    pdfs = list(package_dir.glob("*.pdf"))
    required_paths = {
        str(entry.get("path")) for entry in required if isinstance(entry, dict)
    }
    if pdfs and manifest.get("package_status") != "SUBMISSION_READY":
        report.errors.append(
            "journal_package/ contains a PDF but the package is not SUBMISSION_READY: "
            + ", ".join(path.name for path in pdfs)
        )
    if manifest.get("package_status") == "SUBMISSION_READY":
        if not pdfs:
            report.errors.append("SUBMISSION_READY package has no compiled PDF")
        for pdf in pdfs:
            relative = f"journal_package/{pdf.name}"
            if relative not in required_paths:
                report.errors.append(f"compiled PDF is not a required file: {relative}")

    try:
        sums = parse_sha256sums(package_dir / "SHA256SUMS")
    except ValueError as exc:
        report.errors.append(str(exc))
        sums = {}
    expected = hashed_paths(manifest)
    for relative in expected:
        target = paper_root / relative
        if not target.is_file():
            continue
        digest = sums.get(relative)
        if digest is None:
            report.errors.append(f"SHA256SUMS missing {relative}")
            continue
        actual = sha256_file(target)
        if digest != actual:
            report.errors.append(f"hash mismatch for {relative}")
    extra = sorted(set(sums) - set(expected))
    if extra:
        report.errors.append("SHA256SUMS has unexpected paths: " + ", ".join(extra))

    if paper_id == "P1":
        verdict = _p1_h1_verdict(paper_root)
        h1_claims = [claim for claim in claims if isinstance(claim, dict) and claim.get("id") == "P1.H1"]
        if not h1_claims:
            report.errors.append("P1 package must include claim P1.H1")
        else:
            status = h1_claims[0].get("status")
            if status != "NOT_SUPPORTED":
                report.errors.append(f"P1.H1 must remain NOT_SUPPORTED, not {status!r}")
        if verdict is not None and verdict != "NOT_SUPPORTED":
            report.errors.append(f"P1-T2 H1 verdict drifted from NOT_SUPPORTED to {verdict!r}")
        if verdict is None:
            report.errors.append("P1-T2 H1 verdict could not be read from the archived table")

    audit = (package_dir / "CLAIM_PDF_AUDIT.md").read_text(encoding="utf-8")
    if paper_id == "P1" and "NOT_SUPPORTED" not in audit:
        report.errors.append("P1 CLAIM_PDF_AUDIT.md must retain H1 NOT_SUPPORTED in prose")
    if "OPEN" not in audit and any(
        isinstance(claim, dict) and claim.get("status") == "OPEN" for claim in claims
    ):
        report.errors.append("CLAIM_PDF_AUDIT.md must list OPEN claims")

    if repo_root is not None:
        pass
    return report


def check_repository(repo_root: Path) -> list[PackageReport]:
    reports: list[PackageReport] = []
    for paper_id, relative in PAPER_DIRS.items():
        reports.append(check_package(paper_id, repo_root / relative, repo_root=repo_root))
    return reports


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write-hashes", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    root = args.root.resolve()
    if args.write_hashes:
        for paper_id, relative in PAPER_DIRS.items():
            paper_root = root / relative
            manifest = load_manifest(paper_root / "journal_package")
            write_sha256sums(paper_root, hashed_paths(manifest))
            print(f"wrote {relative}/journal_package/SHA256SUMS")
    reports = check_repository(root)
    payload = [
        {
            "paper_id": report.paper_id,
            "ok": report.ok,
            "errors": report.errors,
            "notes": report.notes,
        }
        for report in reports
    ]
    print(json.dumps(payload, indent=2, sort_keys=True))
    if any(not report.ok for report in reports):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
