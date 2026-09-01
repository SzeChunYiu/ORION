#!/usr/bin/env python3
"""Verify the sole current ORION-13 Brief Report package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/orion-13-global-knowledge-portrait"
LEGACY = PAPER / "journal_package"
CURRENT = PAPER / "submission/publication-final-20260901"
FORBIDDEN = re.compile(r"(?i)tier[ _-]?b|peer_review_ready|package_complete|reclassify_as_note")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_legacy(errors: list[str]) -> None:
    manifest = json.loads((LEGACY / "MANIFEST.json").read_text(encoding="utf-8"))
    state = json.loads(
        (LEGACY / "RENDER_CLOSURE_STATE.json").read_text(encoding="utf-8")
    )
    expected = (
        (manifest, "package_status", "SUPERSEDED"),
        (manifest.get("package_authority") or {}, "current_submission_authorized", False),
        (manifest.get("render_binding") or {}, "current_revision_binding", False),
        (state, "state", "SUPERSEDED"),
        (
            state,
            "superseded_by",
            "papers/orion-13-global-knowledge-portrait/submission/publication-final-20260901/PACKAGE_MANIFEST.json",
        ),
    )
    for record, key, value in expected:
        if record.get(key) != value:
            errors.append(f"legacy {key}: expected {value!r}, got {record.get(key)!r}")


def pdf_text(path: Path, errors: list[str]) -> str:
    info = subprocess.run(
        ["pdfinfo", str(path)], text=True, capture_output=True, check=False
    )
    if info.returncode:
        errors.append(f"pdfinfo failed: {path.relative_to(CURRENT)}")
        return ""
    pages = re.search(r"^Pages:\s+(\d+)", info.stdout, flags=re.M)
    if not pages or int(pages.group(1)) != 7:
        errors.append(f"route is not seven pages: {path.relative_to(CURRENT)}")
    extracted = subprocess.run(
        ["pdftotext", str(path), "-"], text=True, capture_output=True, check=False
    )
    if extracted.returncode or not extracted.stdout.strip():
        errors.append(f"PDF text extraction failed: {path.relative_to(CURRENT)}")
        return ""
    return re.sub(r"\s+", " ", extracted.stdout)


def check_current(errors: list[str]) -> None:
    manifest_path = CURRENT / "PACKAGE_MANIFEST.json"
    sums_path = CURRENT / "SHA256SUMS"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = (
        ("schema", "orion.publication-package.v1"),
        ("paper", "ORION-13"),
        ("publication_route", "F1000Research Brief Report and attributed arXiv preprint"),
    )
    for key, value in expected:
        if manifest.get(key) != value:
            errors.append(f"current {key}: expected {value!r}, got {manifest.get(key)!r}")

    for key, digest_key in (
        ("active_authority", "active_authority_sha256"),
        ("canonical_science_source", "canonical_science_source_sha256"),
    ):
        path = ROOT / str(manifest.get(key, ""))
        if not path.is_file() or sha256(path) != manifest.get(digest_key):
            errors.append(f"current {key} binding mismatch")
    for relative, digest in (manifest.get("canonical_sources") or {}).items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"current canonical-source binding mismatch: {relative}")

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
        if relative in sums:
            errors.append(f"duplicate checksum entry: {relative}")
        sums[relative] = digest
    if set(sums) != actual_payload | {"PACKAGE_MANIFEST.json"}:
        errors.append("current SHA256SUMS coverage mismatch")
    for relative, digest in sums.items():
        path = CURRENT / relative
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"current SHA256SUMS mismatch: {relative}")

    required = ("32-case holdout", "six of 32", "400/400", "250/400", "50/400", "eight unique")
    for route in ("arxiv", "journal"):
        record = manifest.get(route) or {}
        pdf = CURRENT / str(record.get("pdf", ""))
        source = CURRENT / str(record.get("source", ""))
        if not pdf.is_file() or sha256(pdf) != record.get("pdf_sha256"):
            errors.append(f"{route} PDF binding mismatch")
            continue
        if not source.is_file() or sha256(source) != record.get("source_sha256"):
            errors.append(f"{route} source binding mismatch")
        else:
            try:
                with zipfile.ZipFile(source) as archive:
                    if archive.testzip() is not None or archive.namelist() != sorted(archive.namelist()):
                        errors.append(f"{route} source archive is corrupt or non-canonical")
            except zipfile.BadZipFile:
                errors.append(f"{route} source archive is unreadable")
        text = pdf_text(pdf, errors)
        lower = text.lower()
        for token in required:
            if token.lower() not in lower:
                errors.append(f"{route} PDF missing bounded result: {token}")
        if FORBIDDEN.search(text):
            errors.append(f"{route} PDF leaks an internal publication token")
        if record.get("pages") != 7:
            errors.append(f"{route} manifest page binding mismatch")

    if manifest.get("journal", {}).get("venue") != "F1000Research" or manifest.get(
        "journal", {}
    ).get("article_type") != "Brief Report":
        errors.append("journal route is not the resolved Brief Report")
    if "DOI" not in (CURRENT / "HUMAN_INPUTS_REQUIRED.md").read_text(encoding="utf-8"):
        errors.append("human filing blockers do not retain the archive DOI requirement")


def main() -> int:
    errors: list[str] = []
    check_legacy(errors)
    check_current(errors)
    if errors:
        for error in errors:
            print(f"P3_CURRENT_PACKAGE_ERROR: {error}")
        return 1
    print("P3_BRIEF_REPORT_PACKAGE_BOUND__HUMAN_FILING_INPUTS_PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
