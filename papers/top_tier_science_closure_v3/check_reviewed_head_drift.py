#!/usr/bin/env python3
"""Fail closed when main contains unaudited science-relevant commits.

The register records the newest main commit whose scientific implications were
interpreted paper by paper. Later commits are acceptable without re-audit only when
they modify this closure package or its dedicated workflow. Any other path means the
claim audit may be stale and CI fails with the exact commits and paths to review.

Passing this check does not confer scientific authority or publication readiness.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_REGISTER = HERE / "science_gap_register_v3.json"
DEFAULT_REF = "origin/main"
ALLOWED_EXACT_PATHS = {
    ".github/workflows/top-tier-science-gap-register.yml",
}
ALLOWED_PREFIXES = (
    "papers/top_tier_science_closure_v3/",
)


@dataclass(frozen=True)
class CommitDelta:
    commit: str
    date: str
    subject: str
    paths: tuple[str, ...]
    disallowed_paths: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "commit": self.commit,
            "date": self.date,
            "subject": self.subject,
            "paths": list(self.paths),
            "disallowed_paths": list(self.disallowed_paths),
        }


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc


def resolve_commit(ref: str) -> str:
    return run_git("rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip()


def path_is_allowed(path: str) -> bool:
    return path in ALLOWED_EXACT_PATHS or any(
        path.startswith(prefix) for prefix in ALLOWED_PREFIXES
    )


def commit_metadata(commit: str) -> tuple[str, str]:
    line = run_git("show", "-s", "--format=%cs%x09%s", commit).stdout.rstrip("\n")
    date, _, subject = line.partition("\t")
    return date, subject


def commit_paths(commit: str) -> tuple[str, ...]:
    # --first-parent makes a merge commit's change set correspond to what landed on
    # main, while ordinary commits still yield their complete tree delta.
    output = run_git(
        "diff-tree",
        "--first-parent",
        "--no-commit-id",
        "--name-only",
        "-r",
        "--root",
        commit,
    ).stdout
    return tuple(sorted({line.strip() for line in output.splitlines() if line.strip()}))


def evaluate(register_path: Path, ref: str) -> tuple[dict[str, Any], int]:
    payload = json.loads(register_path.read_text(encoding="utf-8"))
    audited = str(payload.get("latest_fully_interpreted_main_head", "")).strip()
    if not audited:
        return (
            {
                "status": "CANNOT_CHECK",
                "reason": "REGISTER_HAS_NO_LATEST_FULLY_INTERPRETED_MAIN_HEAD",
                "science_authority_delta": "NONE",
            },
            2,
        )

    try:
        audited_resolved = resolve_commit(audited)
        current = resolve_commit(ref)
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        return (
            {
                "status": "CANNOT_CHECK",
                "reason": "COMMIT_RESOLUTION_FAILED",
                "detail": str(exc),
                "audited_head": audited,
                "ref": ref,
                "science_authority_delta": "NONE",
            },
            2,
        )

    if audited_resolved == current:
        return (
            {
                "status": "GREEN",
                "reason": "REF_EQUALS_LATEST_FULLY_INTERPRETED_MAIN_HEAD",
                "audited_head": audited_resolved,
                "current_ref_head": current,
                "unreviewed_commit_count": 0,
                "science_authority_delta": "NONE",
            },
            0,
        )

    ancestor = run_git(
        "merge-base", "--is-ancestor", audited_resolved, current, check=False
    )
    if ancestor.returncode != 0:
        return (
            {
                "status": "RED",
                "reason": "AUDITED_HEAD_IS_NOT_ANCESTOR_OF_CURRENT_REF",
                "audited_head": audited_resolved,
                "current_ref_head": current,
                "ref": ref,
                "science_authority_delta": "NONE",
            },
            1,
        )

    commits = [
        line.strip()
        for line in run_git("rev-list", "--reverse", f"{audited_resolved}..{current}").stdout.splitlines()
        if line.strip()
    ]
    deltas: list[CommitDelta] = []
    for commit in commits:
        date, subject = commit_metadata(commit)
        paths = commit_paths(commit)
        disallowed = tuple(path for path in paths if not path_is_allowed(path))
        deltas.append(
            CommitDelta(
                commit=commit,
                date=date,
                subject=subject,
                paths=paths,
                disallowed_paths=disallowed,
            )
        )

    science_relevant = [delta for delta in deltas if delta.disallowed_paths]
    if science_relevant:
        return (
            {
                "status": "RED",
                "reason": "UNREVIEWED_SCIENCE_RELEVANT_COMMITS_AFTER_AUDITED_HEAD",
                "audited_head": audited_resolved,
                "current_ref_head": current,
                "ref": ref,
                "unreviewed_commit_count": len(deltas),
                "science_relevant_commit_count": len(science_relevant),
                "science_relevant_commits": [delta.as_dict() for delta in science_relevant],
                "all_commits_after_audited_head": [delta.as_dict() for delta in deltas],
                "science_authority_delta": "NONE",
            },
            1,
        )

    return (
        {
            "status": "GREEN",
            "reason": "ONLY_CLOSURE_PACKAGE_COMMITS_AFTER_AUDITED_HEAD",
            "audited_head": audited_resolved,
            "current_ref_head": current,
            "ref": ref,
            "unreviewed_commit_count": len(deltas),
            "commits_after_audited_head": [delta.as_dict() for delta in deltas],
            "science_authority_delta": "NONE",
        },
        0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result, code = evaluate(args.register.resolve(), args.ref)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"REVIEWED-HEAD DRIFT: {result['status']} — {result['reason']}")
        for delta in result.get("science_relevant_commits", []):
            print(f"- {delta['commit']} {delta['date']} {delta['subject']}")
            for path in delta["disallowed_paths"]:
                print(f"    {path}")
    return code


if __name__ == "__main__":
    sys.exit(main())
