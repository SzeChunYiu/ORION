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
import re
import zipfile


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


def parse_sums(payload: bytes) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw in payload.decode("utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        digest, separator, relative = raw.partition("  ")
        if not separator or not re.fullmatch(r"[0-9a-f]{64}", digest) or not relative:
            raise RuntimeError(f"malformed historical checksum row: {raw!r}")
        rows[relative] = digest
    return rows


def historical_payload_drift(package: Path, before_sums: bytes) -> list[dict[str, object]]:
    """Compare retained payload to its old inventory without normalizing drift away."""

    rows: list[dict[str, object]] = []
    for relative, expected in parse_sums(before_sums).items():
        # Reconciliation necessarily rewrites the package authority manifest;
        # payload drift is everything else in the old inventory.
        if relative == "PACKAGE_MANIFEST.json":
            continue
        path = package / relative
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            rows.append(
                {
                    "path": relative,
                    "historical_sha256": expected,
                    "current_sha256": actual,
                    "status": "MISMATCH" if actual is not None else "MISSING",
                }
            )
    return rows


def _walk_path_hash_claims(node: object) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(node, dict):
        path = node.get("path")
        digest = node.get("sha256")
        if isinstance(path, str) and isinstance(digest, str):
            found.append((path, digest.removeprefix("sha256:")))
        for value in node.values():
            found.extend(_walk_path_hash_claims(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_walk_path_hash_claims(value))
    return found


def internal_binding_drift(package: Path) -> list[dict[str, object]]:
    """Audit retained receipts as historical claims; never rewrite their bytes."""

    rows: list[dict[str, object]] = []
    names = ("BUILD_RECEIPT.json", "PUBLICATION_RELEASE_MANIFEST.json")
    for name in names:
        record = package / name
        if not record.is_file():
            continue
        payload = json.loads(record.read_text(encoding="utf-8"))
        for relative, expected in _walk_path_hash_claims(payload):
            # Receipt paths use two conventions: package-relative paths for
            # packaged artifacts and repository-relative paths for canonical
            # source inputs. Treating both as package-relative creates false
            # MISSING findings for a source that is present and hash-correct.
            path = ROOT / relative if relative.startswith("papers/") else package / relative
            actual = sha256(path) if path.is_file() else None
            if actual != expected:
                rows.append(
                    {
                        "record": name,
                        "path": relative,
                        "claimed_sha256": expected,
                        "current_sha256": actual,
                        "status": "MISMATCH" if actual is not None else "MISSING",
                    }
                )
    return rows


def back_matter_counts(text: str) -> dict[str, int]:
    return {
        "data_and_code_availability": len(
            re.findall(r"(?im)^##?\s+Data and code availability\s*$", text)
        ),
        "references": len(re.findall(r"(?im)^##?\s+References\s*$", text)),
    }


def successor_back_matter(successor: Path) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for route in ("arxiv", "journal"):
        archive = successor / route / "source.zip"
        if not archive.is_file():
            continue
        with zipfile.ZipFile(archive) as zipped:
            main = zipped.read("main.tex").decode("utf-8")
        rows[route] = {
            "data_and_code_availability": len(
                re.findall(r"\\section\*?\{Data and code availability\}", main)
            ),
            "references": len(re.findall(r"\\section\*?\{References\}", main)),
        }
    return rows


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

    payload_drift = historical_payload_drift(package, before_sums)
    internal_drift = internal_binding_drift(package)
    manuscript = package / "MANUSCRIPT.md"
    legacy_back_matter = (
        back_matter_counts(manuscript.read_text(encoding="utf-8"))
        if manuscript.is_file()
        else {}
    )
    successor_path = ROOT / successor
    successor_counts = successor_back_matter(successor_path)

    drift_record = package / "HISTORICAL_BINDING_DRIFT_V1.json"
    drift_record.write_text(
        json.dumps(
            {
                "schema": "ORION.PublicationClosure.HistoricalBindingDrift.v1",
                "date": "2026-09-01",
                "package": package.relative_to(ROOT).as_posix(),
                "package_status": "HISTORICAL_SUPERSEDED",
                "current_submission_authorized": False,
                "successor": successor,
                "scientific_authority_delta": "NONE",
                "historical_checksum_payload_drift": payload_drift,
                "historical_internal_binding_claim_drift": internal_drift,
                "legacy_manuscript_back_matter_counts": legacy_back_matter,
                "successor_source_back_matter_counts": successor_counts,
                "disposition": (
                    "PRE_EXISTING_DRIFT_AND_LAYOUT_ANOMALIES_RETAINED_AS_HISTORY; "
                    "NOT_A_CURRENT_SUBMISSION_SURFACE"
                    if payload_drift or internal_drift or any(v > 1 for v in legacy_back_matter.values())
                    else "NO_PRE_EXISTING_PAYLOAD_DRIFT_DETECTED"
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    marker = package / "HISTORICAL_COMPONENT_ONLY.md"
    marker.write_text(
        "# Superseded publication package\n\n"
        f"This directory is a {role}. It is retained for provenance and is not a "
        "current submission object.\n\n"
        f"The current arXiv/journal package is `{successor}/`. This reconciliation did "
        "not edit a manuscript, result, negative finding, PDF, or source archive. Any "
        "pre-existing payload or internal-binding drift is retained verbatim and listed "
        "in `HISTORICAL_BINDING_DRIFT_V1.json`; it is not normalized into a claim that "
        "the old package remained current.\n",
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
        "payload_edited_by_this_reconciliation": False,
        "pre_existing_payload_binding_drift_detected": bool(payload_drift or internal_drift),
        "pre_existing_payload_binding_drift_count": len(payload_drift) + len(internal_drift),
        "historical_binding_drift_record": drift_record.name,
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
        "payload_edited_by_this_reconciliation": False,
        "pre_existing_payload_binding_drift_detected": bool(payload_drift or internal_drift),
        "pre_existing_payload_binding_drift_count": len(payload_drift) + len(internal_drift),
        "historical_binding_drift_record": drift_record.name,
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
