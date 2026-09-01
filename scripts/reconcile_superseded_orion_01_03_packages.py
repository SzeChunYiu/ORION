#!/usr/bin/env python3
"""Reconcile retained ORION-01--03 package snapshots as superseded history.

The unified publication-ready packages are the only current submission
objects.  Earlier split/detailed package directories remain valuable provenance,
but their live checksum inventories must describe the retained bytes.  This
script preserves the pre-reconciliation manifest and checksum files verbatim,
denies current submission authority, and writes a complete current inventory.
It never edits a manuscript, PDF, source archive, result, or claim ledger.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    (
        ROOT / "papers/orion-01-certificate-realization/journal_package_A_final",
        "papers/orion-01-certificate-realization/submission/publication-ready-20260831",
        "legacy theory-A component of unified ORION-01",
    ),
    (
        ROOT / "papers/orion-01-certificate-realization/journal_package_B_final",
        "papers/orion-01-certificate-realization/submission/publication-ready-20260831",
        "legacy theory-B component of unified ORION-01",
    ),
    (
        ROOT / "papers/orion-02-fiberguard-finite-fibre/journal_package_final",
        "papers/orion-02-fiberguard-finite-fibre/submission/publication-ready-20260831",
        "retained predecessor to the unified ORION-02 filing package",
    ),
    (
        ROOT / "papers/orion-03-typed-merge-falsification/journal_package_final",
        "papers/orion-03-typed-merge-falsification/submission/publication-ready-20260831",
        "retained predecessor to the unified ORION-03 filing package",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_files(package: Path) -> list[Path]:
    return [
        path
        for path in sorted(package.rglob("*"))
        if path.is_file()
        and path.name != "SHA256SUMS"
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]


def reconcile(package: Path, successor: str, role: str) -> None:
    manifest_path = package / "PACKAGE_MANIFEST.json"
    sums_path = package / "SHA256SUMS"
    if not manifest_path.is_file() or not sums_path.is_file():
        raise RuntimeError(f"binding artifacts missing: {package}")
    history = package / "history" / "pre-unified-reconciliation-20260901"
    historical_manifest = history / "PACKAGE_MANIFEST.json"
    historical_sums = history / "SHA256SUMS.pre-reconciliation.txt"
    if history.exists():
        before_manifest = historical_manifest.read_bytes()
        before_sums = historical_sums.read_bytes()
    else:
        before_manifest = manifest_path.read_bytes()
        before_sums = sums_path.read_bytes()
        history.mkdir(parents=True)
        historical_manifest.write_bytes(before_manifest)
        historical_sums.write_bytes(before_sums)

    marker = package / "HISTORICAL_COMPONENT_ONLY.md"
    marker.write_text(
        "# Superseded publication package\n\n"
        f"This directory is a {role}. It is retained for provenance and is not a "
        "current submission object.\n\n"
        f"The current arXiv/journal package is `{successor}/`. No manuscript, result, "
        "negative finding, PDF, or source archive was changed by this reconciliation.\n",
        encoding="utf-8",
    )
    receipt = {
        "schema": "ORION.PublicationClosure.SupersededPackageReconciliation.v1",
        "date": "2026-09-01",
        "package": package.relative_to(ROOT).as_posix(),
        "pre_reconciliation_manifest_sha256": hashlib.sha256(before_manifest).hexdigest(),
        "pre_reconciliation_sha256sums_sha256": hashlib.sha256(before_sums).hexdigest(),
        "successor": successor,
        "current_submission_authorized": False,
        "scientific_authority_delta": "NONE",
        "retained_payload_edited": False,
        "terminal": "SUPERSEDED_PACKAGE_BYTES_RECONCILED_WITH_HISTORY_RETAINED",
    }
    receipt_path = package / "SUPERSEDED_RECONCILIATION_V1.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    manifest = json.loads(before_manifest)
    manifest["package_status"] = "HISTORICAL_SUPERSEDED"
    manifest["current_submission_authorized"] = False
    manifest["superseded_by"] = successor
    manifest["reconciliation"] = {
        "date": "2026-09-01",
        "receipt": receipt_path.relative_to(package).as_posix(),
        "pre_reconciliation_history": history.relative_to(package).as_posix(),
        "retained_payload_edited": False,
        "scientific_authority_delta": "NONE",
    }
    candidates = [
        path
        for path in package_files(package)
        if path != manifest_path
    ]
    manifest["files"] = {
        path.relative_to(package).as_posix(): sha256(path) for path in candidates
    }
    if "publication_surface_sha256" in manifest and (package / "MANUSCRIPT.md").is_file():
        manifest["publication_surface_sha256"] = sha256(package / "MANUSCRIPT.md")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sums_path.write_text(
        "".join(
            f"{sha256(path)}  {path.relative_to(package).as_posix()}\n"
            for path in package_files(package)
        ),
        encoding="utf-8",
    )

    for line in sums_path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        if sha256(package / relative) != digest:
            raise RuntimeError(f"post-write checksum mismatch: {package / relative}")
    current = json.loads(manifest_path.read_text(encoding="utf-8"))
    for relative, digest in current["files"].items():
        if sha256(package / relative) != digest:
            raise RuntimeError(f"post-write manifest mismatch: {package / relative}")
    print(f"RECONCILED {package.relative_to(ROOT)}")


def main() -> int:
    for package, successor, role in PACKAGES:
        reconcile(package, successor, role)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
