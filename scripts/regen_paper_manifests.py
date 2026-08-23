#!/usr/bin/env python3
"""Regenerate CONTENT_MANIFEST_V1.json + SHA256SUMS for papers/paper-NN-*.

Repairs the 2026-08 seam corruption (two concatenated JSON writes) by
rebuilding each manifest as a single valid object, preserves all curated
metadata verbatim (candidate_id, claim_scope, closes_gate, digest_file,
grants_authority, issue, reproducibility_targets, schema_version and the
per-file roles of already-bound paths), appends newly tracked in-directory
files with role null, and re-derives the subject_commit quartet from the
current git state (HEAD commit + which bound paths differ from HEAD).

Stdlib only. Read-only with --dry-run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

QUARTET = (
    "subject_commit",
    "subject_commit_blocker",
    "subject_commit_status",
    "subject_commit_unbound_paths",
)
DEFAULT_BLOCKER = (
    "bound files differ from the recorded commit; the commit does not "
    "describe these bytes"
)
CLAIM_SCOPE_DEFAULT = (
    "Binds the bytes of one candidate package and names the commit they "
    "were read at. Not a readiness verdict, not novelty or claim authority, "
    "and not permission to deposit a permanent archive."
)
EXCLUDE_NAMES = {"CONTENT_MANIFEST_V1.json", "SHA256SUMS"}
EXCLUDE_PARTS = {"__pycache__"}
EXCLUDE_SUFFIXES = {".pyc"}

SUBJECT_RE = re.compile(r'^\s*"subject_commit":')


def run_git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


def parse_tolerant(raw: str) -> tuple[dict, dict] | None:
    """Return (first_object, latest_quartet) from a possibly seam-corrupted manifest.

    The corruption pattern is one complete-minus-closing-brace object followed
    by a fragment repeating the subject_commit* keys with newer values. We keep
    the first object as the curated metadata source and read the quartet state
    from the LAST occurrence of each key.
    """
    lines = raw.splitlines()
    seams = [i for i, ln in enumerate(lines) if SUBJECT_RE.match(ln)]
    try:
        if len(seams) <= 1:
            first = json.loads(raw)
        else:
            head = "\n".join(lines[: seams[1]]).rstrip().rstrip(",")
            first = json.loads(head + "\n}")
    except json.JSONDecodeError:
        return None
    latest: dict = {}
    for key in QUARTET:
        pat = re.compile(r'^\s*"' + re.escape(key) + r'":\s*(.*?),?\s*$')
        for ln in lines:
            m = pat.match(ln)
            if m:
                try:
                    latest[key] = json.loads(m.group(1))
                except json.JSONDecodeError:
                    pass
    return first, latest


def paper_dirs(repo: Path, only: set[str] | None) -> list[Path]:
    dirs = []
    for d in sorted((repo / "papers").iterdir()):
        if not d.is_dir() or not re.fullmatch(r"paper-\d\d-.*", d.name):
            continue
        if only and d.name[:8] not in only and d.name.split("-")[0][5:] not in only:
            continue
        dirs.append(d)
    return dirs


def collect_files(repo: Path, paper: Path, bound_paths: list[str]) -> tuple[list[str], list[str]]:
    """Final binding set: surviving bound paths (original order) + newly
    discovered in-directory files (sorted, appended). Returns (paths, dropped)."""
    tracked = [
        p for p in run_git(repo, "ls-files", "--", str(paper)).splitlines() if p
    ]
    untracked_clean = [
        p
        for p in run_git(
            repo, "ls-files", "--others", "--exclude-standard", "--", str(paper)
        ).splitlines()
        if p
    ]
    existing = set(tracked) | set(untracked_clean)

    keep, dropped = [], []
    self_manifest = f"{paper.relative_to(repo)}/CONTENT_MANIFEST_V1.json"
    for p in bound_paths:
        # Bound paths may live outside the paper directory (shared candidate
        # packages, tests); keep any that still exist on disk. The manifest
        # itself is dropped: a digest of its own bytes cannot converge across
        # rewrites (the historical manifests carried such a stale self-entry).
        if p == self_manifest:
            continue
        on_disk = (repo / p).exists()
        (keep if on_disk else dropped).append(p)

    def bindable(p: str) -> bool:
        rel = Path(p)
        return (
            rel.name not in EXCLUDE_NAMES
            and rel.suffix not in EXCLUDE_SUFFIXES
            and not (EXCLUDE_PARTS & set(rel.parts))
        )

    fresh = sorted(p for p in existing if bindable(p) and p not in set(keep))
    return keep + fresh, dropped


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dirty_paths(repo: Path, paths: list[str]) -> set[str]:
    """Paths that are untracked or modified relative to HEAD."""
    out = run_git(repo, "status", "--porcelain", "--", *paths)
    flagged: set[str] = set()
    for ln in out.splitlines():
        code, _, p = ln[:2], ln[2], ln[3:]
        p = p.strip('"')
        if code.strip() and code != "D " and code != " D":
            flagged.add(p)
        if "R" in code and " -> " in p:
            flagged.add(p.split(" -> ", 1)[1])
    return flagged


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".", help="git repository root")
    ap.add_argument(
        "--papers",
        default="",
        help="comma-separated filter, e.g. paper-06,paper-08 (default: all)",
    )
    ap.add_argument(
        "--include-new",
        action="store_true",
        help="create manifests for papers that have none yet (default: skip them)",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    if not (repo / ".git").exists():
        print(f"error: {repo} is not a git repository", file=sys.stderr)
        return 2
    only = {s.strip() for s in args.papers.split(",") if s.strip()} or None

    head = run_git(repo, "rev-parse", "HEAD").strip()
    rc = 0
    for paper in paper_dirs(repo, only):
        name = paper.name
        manifest = paper / "CONTENT_MANIFEST_V1.json"
        sums = paper / "SHA256SUMS"
        if not manifest.exists() and not args.include_new:
            print(f"{name}: no existing manifest; skipped (use --include-new)")
            continue

        meta: dict = {}
        roles: dict[str, str | None] = {}
        bound_paths: list[str] = []
        prev_status = None
        prev_blocker = None
        if manifest.exists():
            parsed = parse_tolerant(manifest.read_text())
            if parsed is None:
                print(f"{name}: FAILED to parse existing manifest; skipped")
                rc = 1
                continue
            first, latest = parsed
            meta = {
                k: v
                for k, v in first.items()
                if k != "bound_files" and k not in QUARTET
            }
            bound_paths = [b["path"] for b in first["bound_files"]]
            roles = {b["path"]: b.get("role") for b in first["bound_files"]}
            prev_status = latest.get("subject_commit_status")
            prev_blocker = latest.get("subject_commit_blocker")

        paths, dropped = collect_files(repo, paper, bound_paths)
        for p in dropped:
            print(f"  {name}: dropping bound path absent from disk/git: {p}")
        entries = [{"path": p, "role": roles.get(p)} for p in paths]

        flagged = dirty_paths(repo, paths)
        unbound = sorted(flagged & set(paths))
        status = "BOUND" if not unbound else "CANNOT_CHECK"
        if not unbound:
            blocker = None
        else:
            blocker = (
                prev_blocker
                if isinstance(prev_blocker, str) and prev_blocker
                else DEFAULT_BLOCKER
            )

        obj = {
            **meta,
            "bound_files": entries,
            "subject_commit": head,
            "subject_commit_blocker": blocker,
            "subject_commit_status": status,
            "subject_commit_unbound_paths": unbound,
        }
        if "digest_file" not in obj:
            obj["digest_file"] = str(sums.relative_to(repo))
        if "grants_authority" not in obj:
            obj["grants_authority"] = "NONE"
        if "schema_version" not in obj:
            obj["schema_version"] = "orion.candidate-content-binding.v1"
        if "candidate_id" not in obj:
            obj["candidate_id"] = "P" + str(int(paper.name.split("-")[1]))
        if "claim_scope" not in obj:
            obj["claim_scope"] = CLAIM_SCOPE_DEFAULT
        obj.setdefault("closes_gate", None)
        obj.setdefault("issue", None)
        obj.setdefault("reproducibility_targets", {})

        manifest_text = json.dumps(obj, sort_keys=True, indent=2) + "\n"
        sums_lines = sorted(
            f"{sha256_file(repo / p)}  {p}\n" for p in paths
        )
        sums_text = "".join(sums_lines)

        if args.dry_run:
            print(
                f"{name}: {len(entries)} files, status={status} "
                f"(was {prev_status}), unbound={len(unbound)}, dropped={len(dropped)}"
            )
            continue

        manifest.write_text(manifest_text)
        sums.write_text(sums_text)
        # post-write self-check
        reloaded = json.loads(manifest.read_text())
        assert len(reloaded["bound_files"]) == len(entries)
        assert len(sums.read_text().splitlines()) == len(entries)
        print(
            f"{name}: wrote {len(entries)} bound files, {len(sums_lines)} sums, "
            f"status={status} (was {prev_status}), unbound={len(unbound)}, "
            f"dropped={len(dropped)}"
        )
    return rc


if __name__ == "__main__":
    sys.exit(main())
