#!/usr/bin/env python3
"""Fail-closed byte and commit verification for ORION-17's additive V2 binding.

The generic P6--P8 checker owns the historical V1 manifests.  This checker owns
P7's additive V2 layer: every listed byte, the outer manifest checksum, and the
recorded commit/tree identity must all be independently recoverable.  It grants
no scientific or submission authority.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PAPER_REL = Path("papers/orion-17-epistemic-navigation-open-worlds")
MANIFEST_REL = PAPER_REL / "CONTENT_MANIFEST_V2.json"
SUMS_REL = PAPER_REL / "content_binding_v2" / "SHA256SUMS"
SCHEMA = "orion.candidate-content-binding.v2"
CANDIDATE = "P7"
ARCHIVE_BRANCH = "shadow/orion17-p7-v2-subject-20260829"
ARCHIVE_REF = f"refs/remotes/origin/{ARCHIVE_BRANCH}"
HEX = frozenset("0123456789abcdef")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def is_sha(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in HEX for character in value.lower())
    )


def audit() -> dict[str, Any]:
    errors: list[str] = []
    cannot_check: list[str] = []
    manifest_path = ROOT / MANIFEST_REL
    sums_path = ROOT / SUMS_REL

    if not manifest_path.is_file():
        errors.append(f"manifest missing: {MANIFEST_REL.as_posix()}")
        payload: dict[str, Any] = {}
    else:
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"manifest unreadable: {exc}")
            loaded = {}
        if not isinstance(loaded, dict):
            errors.append("manifest must contain one JSON object")
            payload = {}
        else:
            payload = loaded

    require(payload.get("schema_version") == SCHEMA, "unexpected schema_version", errors)
    require(payload.get("candidate_id") == CANDIDATE, "unexpected candidate_id", errors)
    require(payload.get("subject_commit_status") == "BOUND", "V2 status is not BOUND", errors)
    require(payload.get("subject_commit_blocker") is None, "BOUND manifest carries a blocker", errors)
    require(
        payload.get("subject_commit_unbound_paths") == [],
        "BOUND manifest carries unbound paths",
        errors,
    )

    raw_rows = payload.get("bound_files")
    if not isinstance(raw_rows, list) or not raw_rows:
        errors.append("bound_files must be a non-empty list")
        raw_rows = []

    rows: dict[str, str] = {}
    duplicates: set[str] = set()
    for index, row in enumerate(raw_rows):
        if not isinstance(row, dict):
            errors.append(f"bound_files[{index}] is not an object")
            continue
        path = row.get("path")
        digest = row.get("sha256")
        if not isinstance(path, str) or not path:
            errors.append(f"bound_files[{index}] has no valid path")
            continue
        candidate_path = Path(path)
        if candidate_path.is_absolute() or ".." in candidate_path.parts:
            errors.append(f"unsafe bound path: {path}")
            continue
        if path in rows:
            duplicates.add(path)
        if not is_sha(digest, 64):
            errors.append(f"invalid sha256 for {path}")
            continue
        rows[path] = str(digest).lower()

    if duplicates:
        errors.append("duplicate bound paths: " + ", ".join(sorted(duplicates)))
    for forbidden in (MANIFEST_REL.as_posix(), SUMS_REL.as_posix()):
        if forbidden in rows:
            errors.append(f"self-referential binding path is forbidden: {forbidden}")

    digest_mismatches: list[dict[str, str | None]] = []
    for relative, expected in sorted(rows.items()):
        target = ROOT / relative
        if not target.is_file():
            digest_mismatches.append(
                {"path": relative, "expected": expected, "observed": None}
            )
            continue
        observed = sha256(target)
        if observed != expected:
            digest_mismatches.append(
                {"path": relative, "expected": expected, "observed": observed}
            )
    if digest_mismatches:
        errors.append("bound-file digest drift: " + json.dumps(digest_mismatches, sort_keys=True))

    if not sums_path.is_file():
        errors.append(f"outer checksum missing: {SUMS_REL.as_posix()}")
    elif manifest_path.is_file():
        expected_line = f"{sha256(manifest_path)}  {MANIFEST_REL.as_posix()}"
        observed_lines = [
            line.strip()
            for line in sums_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if observed_lines != [expected_line]:
            errors.append("outer checksum does not exactly bind CONTENT_MANIFEST_V2.json")

    subject_commit = payload.get("subject_commit")
    subject_tree = payload.get("subject_tree")
    if not is_sha(subject_commit, 40):
        errors.append("subject_commit must be a 40-character git SHA")
    elif not is_sha(subject_tree, 40):
        errors.append("subject_tree must be a 40-character git SHA")
    else:
        try:
            git("cat-file", "-e", f"{subject_commit}^{{commit}}")
            observed_tree = git("rev-parse", f"{subject_commit}^{{tree}}").stdout.strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            # A BOUND claim is fail-closed: absence of the named commit is an error,
            # not a green CANNOT_CHECK outcome.
            errors.append(f"BOUND subject_commit is not recoverable: {exc}")
        else:
            if observed_tree != subject_tree:
                errors.append(
                    f"subject_tree mismatch: manifest={subject_tree}, observed={observed_tree}"
                )
            ancestor = git(
                "merge-base", "--is-ancestor", str(subject_commit), "HEAD", check=False
            )
            archive = git("rev-parse", "--verify", ARCHIVE_REF, check=False)
            archive_commit = archive.stdout.strip() if archive.returncode == 0 else None
            if ancestor.returncode == 0:
                provenance_mode = "ANCESTOR"
            elif archive_commit == subject_commit:
                provenance_mode = "DURABLE_ARCHIVE_REF"
            else:
                provenance_mode = "UNRECOVERABLE_PROVENANCE"
                errors.append(
                    "subject_commit is neither an ancestor nor the commit named by "
                    f"{ARCHIVE_REF}"
                )

            listed = set(
                git("ls-tree", "-r", "--name-only", str(subject_commit)).stdout.splitlines()
            )
            absent_from_subject = sorted(set(rows) - listed)
            if absent_from_subject:
                errors.append(
                    "bound paths absent from subject_commit: " + ", ".join(absent_from_subject)
                )
            if rows:
                disagreement = git(
                    "diff",
                    "--name-only",
                    str(subject_commit),
                    "--",
                    *sorted(rows),
                ).stdout.splitlines()
                if disagreement:
                    errors.append(
                        "current bound bytes differ from subject_commit: "
                        + ", ".join(sorted(disagreement))
                    )

    return {
        "schema_version": "orion.p7-content-binding-v2-audit.v1",
        "candidate_id": CANDIDATE,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "cannot_check": cannot_check,
        "bound_file_count": len(rows),
        "subject_commit": subject_commit,
        "subject_tree": subject_tree,
        "provenance_archive_branch": ARCHIVE_BRANCH,
        "provenance_mode": locals().get("provenance_mode"),
        "manifest_sha256": sha256(manifest_path) if manifest_path.is_file() else None,
        "scientific_authority_delta": "NONE",
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"P7_CONTENT_BINDING_V2=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
