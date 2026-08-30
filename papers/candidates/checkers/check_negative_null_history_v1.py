#!/usr/bin/env python3
"""Validate P6--P8 append-only negative/null history source bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

PAPERS = {
    "P6": Path("papers/orion-16-formal-epistemic-structures-and-mechanics"),
    "P7": Path("papers/orion-17-epistemic-navigation-open-worlds"),
    "P8": Path("papers/orion-18-epistemic-authority-autonomous-science"),
}
ALLOWED_TERMINALS = {"NEGATIVE_EQUIVALENCE_THEOREM", "MATCH_IS_NOT_NECESSARY"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical_source_is_bound(root: Path, source: str, digest: str) -> bool:
    """Return whether ``source`` has the recorded bytes now or in git history.

    A negative-history row is append-only, while its versioned claim ledger can
    legitimately gain later, narrower claims.  Requiring the moving worktree
    file to retain the old digest made an honest ledger extension invalidate the
    immutable adverse record.  The path plus SHA-256 already identifies the old
    bytes; git history supplies the missing temporal coordinate without rewriting
    the history row.
    """

    source_path = root / source
    if source_path.is_file() and sha256_file(source_path) == digest:
        return True
    if _digest_at_path(root, source, digest):
        return True
    # git log -- <path> stops at a rename and --follow does not survive a
    # restructuring that moves thousands of files at once. R0 moved these ledgers
    # twice, so a walk anchored to the current path cannot reach bytes recorded
    # under either earlier one. Fall back to every historical file sharing this
    # basename, which is strictly narrower than accepting any blob anywhere.
    return _digest_under_any_historical_path_with_same_name(root, source, digest)


def _git(root: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True, capture_output=True, text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _digest_at_path(root: Path, path: str, digest: str) -> bool:
    out = _git(root, "log", "--format=%H", "--", path)
    if out is None:
        return False
    for commit in out.splitlines():
        try:
            content = subprocess.run(
                ["git", "-C", str(root), "show", f"{commit}:{path}"],
                check=True, capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError):
            continue
        if hashlib.sha256(content).hexdigest() == digest:
            return True
    return False


def _digest_under_any_historical_path_with_same_name(
    root: Path, source: str, digest: str
) -> bool:
    name = PurePosixPath(source).name
    seen: set[str] = set()
    out = _git(root, "log", "--all", "--name-only", "--format=", "--diff-filter=AMR")
    if out is None:
        return False
    for line in out.splitlines():
        line = line.strip()
        if line and line != source and PurePosixPath(line).name == name:
            seen.add(line)
    for path in sorted(seen):
        if _digest_at_path(root, path, digest):
            return True
    return False


def validate_history(root: Path, paper_id: str) -> list[dict[str, object]]:
    path = PAPERS[paper_id] / "evidence/history/NEGATIVE_NULL_HISTORY_V1.jsonl"
    full = root / path
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(full.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        row = json.loads(raw)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: object required")
        required = {
            "schema_version",
            "record_id",
            "paper_id",
            "claim_id",
            "terminal",
            "disposition",
            "immutable",
            "positive_authority_granted",
            "source",
            "source_sha256",
        }
        missing = required - set(row)
        if missing:
            raise ValueError(f"{path}:{line_number}: missing {sorted(missing)}")
        record_id = row["record_id"]
        if not isinstance(record_id, str) or not record_id or record_id in seen:
            raise ValueError(f"{path}:{line_number}: duplicate/invalid record_id")
        seen.add(record_id)
        if row["schema_version"] != "orion.paper-negative-null-history.v1":
            raise ValueError(f"{path}:{line_number}: wrong schema")
        if row["paper_id"] != paper_id:
            raise ValueError(f"{path}:{line_number}: wrong paper")
        if row["terminal"] not in ALLOWED_TERMINALS:
            raise ValueError(f"{path}:{line_number}: nonhistorical terminal")
        if row["immutable"] is not True or row["positive_authority_granted"] is not False:
            raise ValueError(f"{path}:{line_number}: history cannot authorize or mutate")
        digest = row["source_sha256"]
        source = row["source"]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"{path}:{line_number}: invalid digest")
        if not isinstance(source, str):
            raise ValueError(f"{path}:{line_number}: invalid source")
        source_path = (root / source).resolve()
        try:
            source_path.relative_to(root.resolve())
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: source escapes repository") from exc
        if not historical_source_is_bound(root, source, digest):
            raise ValueError(f"{path}:{line_number}: stale or missing source binding")
        rows.append(row)
    if not rows:
        raise ValueError(f"{path}: empty history is not evidence")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--paper", choices=sorted(PAPERS), action="append")
    args = parser.parse_args()
    for paper_id in args.paper or sorted(PAPERS):
        rows = validate_history(args.root.resolve(), paper_id)
        print(f"{paper_id} NEGATIVE/NULL HISTORY: BOUND ({len(rows)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
