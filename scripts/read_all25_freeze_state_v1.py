#!/usr/bin/env python3
"""Read the all-25 bounded-science freeze at any HEAD, not only at the freeze commit.

`papers/check_all25_bounded_science_freeze_v3.py` validates a property of
**HEAD**::

    head   = git.resolve_commit("HEAD")
    parent = git.resolve_commit(f"{head}^")
    require(parent == content_base, "freeze commit parent is not the declared content base")

so it can only pass while HEAD *is* the freeze commit (or a merge whose first
parent is the content base). The next commit on main turns it into
``FREEZE_INVALID``, and nothing distinguishes "this freeze was never
well-formed" from "three unrelated PRs have landed since". That is how the V2
freeze became valid only at ``fe5da5332``: not wrong, just unreadable.

The scientific content of a freeze is a fact about the **freeze commit** — that
each paper's tree there matched its recorded ``final_tree_oid`` — and that fact
is permanently checkable. Whether papers have moved *since* is separate, and it
is information rather than a malformed freeze.

This reader separates them. It locates the freeze commit by identity (the commit
that added the manifest) instead of assuming HEAD, re-checks the attestation
there, and reports post-freeze drift as its own outcome.

It does not replace the frozen checker and does not modify it. The frozen
checker's verdict at the freeze commit remains authoritative; this reader must
agree with it there, which its test asserts.

Exit codes follow the programme convention:

    0  the freeze is well formed and its attestation holds (drift, if any, is reported)
    2  a finding: the freeze is malformed, or its attestation fails at its own commit
    3  could not check -- inputs absent, ambiguous history, or not a git repository
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

MANIFEST_REL = "papers/ALL_25_BOUNDED_SCIENCE_FREEZE_V3.json"
CHECKER_REL = "papers/check_all25_bounded_science_freeze_v3.py"


class CannotCheck(Exception):
    """Input absent or history ambiguous -- distinct from a finding."""


class Finding(Exception):
    """The freeze itself does not hold."""


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["/usr/bin/git", *args], cwd=repo, capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise CannotCheck(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _tree_oid(repo: Path, commit: str, path: str) -> str | None:
    proc = subprocess.run(
        ["/usr/bin/git", "rev-parse", "--verify", f"{commit}:{path}"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def locate_freeze_commit(repo: Path, head: str) -> str:
    """The commit that ADDED the manifest, among HEAD's ancestors.

    Identity, not position. `--diff-filter=A` is what makes this the freeze
    commit rather than any later commit that merely touched the file.
    """
    out = _git(
        repo,
        "log",
        head,
        "--diff-filter=A",
        "--format=%H",
        "--",
        MANIFEST_REL,
    )
    commits = [line for line in out.splitlines() if line]
    if not commits:
        raise CannotCheck(
            f"no commit in {head}'s ancestry adds {MANIFEST_REL}; the freeze has "
            "not been taken on this branch"
        )
    if len(commits) > 1:
        raise CannotCheck(
            "ambiguous history: more than one commit adds the manifest "
            f"({', '.join(c[:12] for c in commits)}); cannot identify the freeze"
        )
    return commits[0]


def validate_freeze_shape(repo: Path, freeze: str, content_base: str) -> None:
    parent = _git(repo, "rev-parse", "--verify", f"{freeze}^{{commit}}")
    first_parent = _git(repo, "rev-parse", "--verify", f"{freeze}^")
    if first_parent != content_base:
        raise Finding(
            f"freeze commit {parent[:12]} has first parent {first_parent[:12]}, "
            f"not the declared content base {content_base[:12]}"
        )
    rows = []
    for line in _git(repo, "diff", "--name-status", content_base, freeze, "--").splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            raise CannotCheck(f"malformed diff row: {line}")
        rows.append((parts[0], parts[1]))
    expected = sorted([("A", MANIFEST_REL), ("A", CHECKER_REL)])
    if sorted(rows) != expected:
        raise Finding(
            "the freeze commit must add exactly the manifest and the checker; "
            f"it changes {sorted(rows)}"
        )


def read_manifest(repo: Path, freeze: str) -> dict:
    proc = subprocess.run(
        ["/usr/bin/git", "show", f"{freeze}:{MANIFEST_REL}"],
        cwd=repo,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise CannotCheck(f"cannot read the manifest at {freeze[:12]}")
    try:
        return json.loads(proc.stdout.decode("utf-8"))
    except ValueError as exc:
        raise CannotCheck(f"manifest at {freeze[:12]} is malformed: {exc}") from exc


def check_attestation(repo: Path, freeze: str, manifest: dict) -> list[str]:
    """The permanent fact: every paper's tree AT THE FREEZE matched its pin."""
    broken = []
    for paper in manifest["papers"]:
        got = _tree_oid(repo, freeze, paper["canonical_directory"])
        if got != paper["final_tree_oid"]:
            broken.append(
                f"{paper['paper_id']}: tree at the freeze commit is "
                f"{(got or 'ABSENT')[:12]}, recorded {paper['final_tree_oid'][:12]}"
            )
    return broken


def measure_drift(repo: Path, head: str, manifest: dict) -> list[dict]:
    """Papers whose tree has moved since the freeze. Information, not a fault."""
    drift = []
    for paper in manifest["papers"]:
        directory = paper["canonical_directory"]
        got = _tree_oid(repo, head, directory)
        if got != paper["final_tree_oid"]:
            drift.append(
                {
                    "paper_id": paper["paper_id"],
                    "canonical_directory": directory,
                    "frozen_tree_oid": paper["final_tree_oid"],
                    "head_tree_oid": got,
                    "state": "ABSENT_AT_HEAD" if got is None else "MOVED",
                }
            )
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--rev", default="HEAD")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument(
        "--require-no-drift",
        action="store_true",
        help="also fail when any paper has moved since the freeze; use at the "
        "moment of taking a freeze, not in routine CI",
    )
    args = parser.parse_args(argv)

    try:
        repo = Path(_git(args.repo, "rev-parse", "--show-toplevel"))
        head = _git(repo, "rev-parse", "--verify", f"{args.rev}^{{commit}}")
        freeze = locate_freeze_commit(repo, head)
        manifest = read_manifest(repo, freeze)
        content_base = manifest["content_base_commit"]
        validate_freeze_shape(repo, freeze, content_base)
        broken = check_attestation(repo, freeze, manifest)
        drift = measure_drift(repo, head, manifest)
    except CannotCheck as exc:
        print(f"CANNOT_CHECK: {exc}", file=sys.stderr)
        return 3
    except Finding as exc:
        print(f"FREEZE_MALFORMED: {exc}", file=sys.stderr)
        return 2

    if broken:
        for row in broken:
            print(f"ATTESTATION_BROKEN: {row}", file=sys.stderr)
        return 2

    terminal = "BOUNDED_FREEZE_ATTESTATION_HOLDS"
    if drift:
        terminal += "__POST_FREEZE_DRIFT"

    report = {
        "schema": "orion.all25-freeze-state.v1",
        "scientific_authority_delta": "NONE",
        "rev": head,
        "freeze_commit": freeze,
        "content_base_commit": content_base,
        "papers": len(manifest["papers"]),
        "drifted": drift,
        "terminal": terminal,
    }
    if args.json_out:
        args.json_out.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    print(
        f"{terminal} freeze_commit={freeze} content_base={content_base} "
        f"papers={len(manifest['papers'])} drifted={len(drift)}"
    )
    for row in drift:
        print(f"  DRIFTED {row['paper_id']}: {row['state']}")

    if drift and args.require_no_drift:
        print(
            "--require-no-drift was set and papers have moved since the freeze",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
