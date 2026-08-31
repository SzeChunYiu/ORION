#!/usr/bin/env python3
"""Regenerate CONTENT_MANIFEST_V1.json + SHA256SUMS for papers/orion-NN-*.

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


def parse_tolerant(raw: str) -> tuple[dict, dict, list[str]] | None:
    """Return (first_object, latest_quartet, recovered_paths) from a seam-corrupted manifest.

    The corruption pattern is one complete-minus-closing-brace object followed
    by a fragment repeating the subject_commit* keys with newer values. We keep
    the first object as the curated metadata source and read the quartet state
    from the LAST occurrence of each key. A second corruption mode is a
    duplicated ``"path"`` key inside one bound_files entry (the seam rewrite
    emitted the replacement path without deleting the original): json.loads
    silently keeps only the last value, so we record every collided path, in
    order of appearance, as ``recovered_paths`` for the caller to re-bind.
    """
    recovered: list[str] = []

    def _pair_hook(pairs: list[tuple[str, object]]) -> dict:
        paths = [v for k, v in pairs if k == "path"]
        if len(paths) > 1:
            recovered.extend(str(p) for p in paths)
        obj: dict = {}
        for k, v in pairs:
            obj[k] = v
        return obj

    lines = raw.splitlines()
    seams = [i for i, ln in enumerate(lines) if SUBJECT_RE.match(ln)]
    try:
        if len(seams) <= 1:
            first = json.loads(raw, object_pairs_hook=_pair_hook)
        else:
            head = "\n".join(lines[: seams[1]]).rstrip().rstrip(",")
            first = json.loads(head + "\n}", object_pairs_hook=_pair_hook)
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
    return first, latest, recovered


def paper_dirs(repo: Path, only: set[str] | None) -> list[Path]:
    dirs = []
    for d in sorted((repo / "papers").iterdir()):
        if not d.is_dir() or not re.fullmatch(r"orion-\d\d-.*", d.name):
            continue
        if only and d.name[:9] not in only and d.name.split("-")[1] not in only:
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


#: P6-P8 are ALSO validated by papers/candidates/checkers/check_content_binding_v1.py,
#: which derives its own authoritative path set. That checker excludes
#: SUCCESSOR_V2_PATHS from V1's identity and deliberately INCLUDES the manifest
#: itself (written first, hashed second, the way P1-P5 do it).
#:
#: This script previously derived a rival set: it knew nothing about the V2
#: successor paths and dropped the manifest. The two could never agree, so
#: regenerating a candidate manifest produced a file the checker rejected --
#: 26 test failures that no amount of re-running either tool could clear.
#:
#: Rather than duplicate the rules (the checker's own comment warns that a
#: second hand-maintained list is free to disagree with the normative one),
#: this defers to the checker when one applies.
_CANDIDATE_CHECKER = Path("papers/candidates/checkers/check_content_binding_v1.py")


def candidate_bound_paths(repo: Path, paper: Path) -> list[str] | None:
    """Authoritative path set from the candidate checker, or None if it does
    not govern this paper."""
    checker_path = repo / _CANDIDATE_CHECKER
    if not checker_path.is_file():
        return None
    import importlib.util

    spec = importlib.util.spec_from_file_location("_ccb_v1", checker_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    rel = paper.relative_to(repo)
    for cid, directory in getattr(mod, "CANDIDATE_DIRS", {}).items():
        if Path(directory).name == rel.name:
            try:
                return list(mod.bound_paths(repo, cid))
            except Exception:
                return None
    return None


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
        help="comma-separated filter, e.g. orion-16,orion-18 (default: all)",
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

    # A pin must name a commit that still exists after this branch merges. This
    # repository squash-merges, so a commit that lives only on a feature branch is
    # destroyed on merge and every bound file then fails to resolve via
    # `git show <subject_commit>:<path>`, silently degrading to PARTIAL. Warn at
    # write time rather than letting it surface as unexplained CI failures on main.
    try:
        upstream = run_git(repo, "rev-parse", "--verify", "-q", "origin/main").strip()
    except Exception:
        upstream = ""
    if upstream:
        merge_base = ""
        try:
            merge_base = run_git(repo, "merge-base", head, upstream).strip()
        except Exception:
            pass
        if merge_base != head:
            print(
                f"warning: subject_commit {head[:12]} is not reachable from origin/main.\n"
                "         This repo squash-merges, so that commit will not survive the merge and\n"
                "         every pin written now will dangle on main. Re-pin after merging, or pin\n"
                "         to a commit already on origin/main that contains the bound bytes.",
                file=sys.stderr,
            )
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
            first, latest, recovered = parsed
            meta = {
                k: v
                for k, v in first.items()
                if k != "bound_files" and k not in QUARTET
            }
            bound_paths = [b["path"] for b in first["bound_files"]]
            for p in recovered:
                if p not in bound_paths:
                    bound_paths.append(p)
                    print(f"  recovered collided bound path: {p}")
            roles = {b["path"]: b.get("role") for b in first["bound_files"]}
            prev_status = latest.get("subject_commit_status")
            prev_blocker = latest.get("subject_commit_blocker")

        governed = candidate_bound_paths(repo, paper)
        if governed is not None:
            paths, dropped = governed, [p for p in bound_paths if p not in set(governed)]
            print(f"  {name}: using candidate checker's authoritative path set "
                  f"({len(paths)} files)")
        else:
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

        # The manifest may be one of its own bound paths (the candidate checker
        # requires this: the digest file binds the manifest's bytes). Hashing
        # the copy still on disk would record the digest of the PREVIOUS
        # manifest, so the sums file would be stale the instant it was written.
        # Hash the text about to be written instead of what is currently there.
        manifest_rel = str(manifest.relative_to(repo))

        def _digest(rel: str) -> str:
            if rel == manifest_rel:
                return hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()
            return sha256_file(repo / rel)

        sums_lines = sorted(f"{_digest(p)}  {p}\n" for p in paths)
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
