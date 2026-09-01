#!/usr/bin/env python3
"""Supersede two legacy filing bindings without deleting their history."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPECS = (
    {
        "directory": ROOT / "papers/orion-12-open-world-scientific-discovery/submission",
        "manifest": "SUBMISSION_MANIFEST_V1.json",
        "successor": "papers/orion-12-open-world-scientific-discovery/submission/publication-ready-20260831",
        "paper": "ORION-12",
    },
    {
        "directory": ROOT / "papers/orion-13-global-knowledge-portrait/journal_package/wave1_current",
        "manifest": "SUBMISSION_MANIFEST.json",
        "successor": "papers/orion-13-global-knowledge-portrait/submission/publication-ready-20260831",
        "paper": "ORION-13",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile(spec: dict[str, object]) -> None:
    directory = Path(spec["directory"])
    manifest_path = directory / str(spec["manifest"])
    sums_path = directory / "SHA256SUMS"
    history = directory / "history/pre-unified-reconciliation-20260901"
    historical_manifest = history / manifest_path.name
    historical_sums = history / "SHA256SUMS.pre-reconciliation.txt"
    if history.exists():
        original_manifest = historical_manifest.read_bytes()
    else:
        original_manifest = manifest_path.read_bytes()
        original_sums = sums_path.read_bytes()
        history.mkdir(parents=True)
        historical_manifest.write_bytes(original_manifest)
        historical_sums.write_bytes(original_sums)

    manifest = json.loads(original_manifest)
    manifest["package_status"] = "HISTORICAL_SUPERSEDED"
    manifest["current_submission_authorized"] = False
    manifest["superseded_by"] = spec["successor"]
    manifest["scientific_authority_delta"] = "NONE"
    if spec["paper"] == "ORION-12":
        manifest.setdefault("author", {})["affiliation"] = "Independent Researcher"
    else:
        manifest["historical_unavailable_artifacts"] = ["manuscript.pdf"]
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    receipt = directory / "SUPERSEDED_RECONCILIATION_V1.json"
    receipt.write_text(
        json.dumps(
            {
                "schema": "ORION.PublicationClosure.LegacyFilingReconciliation.v1",
                "date": "2026-09-01",
                "paper": spec["paper"],
                "directory": directory.relative_to(ROOT).as_posix(),
                "successor": spec["successor"],
                "current_submission_authorized": False,
                "scientific_authority_delta": "NONE",
                "historical_binding_retained": history.relative_to(directory).as_posix(),
                "terminal": "LEGACY_FILING_SUPERSEDED_AND_HISTORY_RETAINED",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    files = [path for path in sorted(directory.iterdir()) if path.is_file() and path != sums_path]
    files.extend(path for path in sorted(history.rglob("*")) if path.is_file())
    sums_path.write_text(
        "".join(
            f"{sha256(path)}  {path.relative_to(directory).as_posix()}\n" for path in files
        ),
        encoding="utf-8",
    )
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        if sha256(directory / relative) != digest:
            raise RuntimeError(f"checksum mismatch after reconciliation: {relative}")
    print(f"RECONCILED {spec['paper']} legacy filing")


def main() -> int:
    for spec in SPECS:
        reconcile(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
