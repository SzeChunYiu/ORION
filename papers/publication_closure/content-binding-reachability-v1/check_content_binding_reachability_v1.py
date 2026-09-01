#!/usr/bin/env python3
"""Audit every CONTENT_MANIFEST for a subject_commit that a reviewer can reach.

A content manifest claims that a set of files had exact bytes at a named commit.
Two independent things can go wrong with that claim, and they need different
verdicts:

FALSE BINDING -- the manifest says BOUND, and the bytes at its own subject_commit
disagree with what it records. The claim is untrue as written. This is the
condition the manifests' own blocker text describes: "bound files differ from the
recorded commit; the commit does not describe these bytes."

UNREACHABLE BINDING -- the bytes agree, so the claim is true, but the commit is
not an ancestor of the default branch. It usually lives on a side branch that a
squash merge replaced with a different commit. The claim remains checkable only
by whoever still has that branch, which is not a reviewer working from the
default branch, and stops being checkable at all once the branch is pruned.

These are graded separately on purpose. Collapsing them would either overstate an
unreachable-but-true binding as a falsehood, or understate a false one as a
filing problem.

Exit codes: 0 clean, 1 at least one FALSE binding, 2 unreachable only,
3 could not check (no manifests found, or git unavailable).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def git(*args: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["/usr/bin/git", "-C", str(root), *args], capture_output=True)


def commit_exists(sha: str, root: Path) -> bool:
    r = git("cat-file", "-t", sha, root=root)
    return r.returncode == 0 and r.stdout.decode().strip() == "commit"


def is_ancestor(sha: str, ref: str, root: Path) -> bool:
    return git("merge-base", "--is-ancestor", sha, ref, root=root).returncode == 0


def audit_manifest(path: Path, root: Path, ref: str) -> dict:
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"manifest": str(path), "verdict": "UNREADABLE", "detail": str(exc)}

    sha = m.get("subject_commit")
    status = m.get("subject_commit_status")
    if not sha:
        return {"manifest": str(path), "verdict": "NO_SUBJECT_COMMIT", "status": status}

    exists = commit_exists(sha, root)
    reachable = is_ancestor(sha, ref, root) if exists else False

    differ: list[str] = []
    absent: list[str] = []
    if exists:
        for entry in m.get("bound_files") or []:
            rel = entry.get("path")
            expected = entry.get("sha256") or entry.get("digest")
            if not rel or not expected:
                continue
            blob = git("show", f"{sha}:{rel}", root=root)
            if blob.returncode != 0:
                absent.append(rel)
            elif hashlib.sha256(blob.stdout).hexdigest() != expected:
                differ.append(rel)

    disagreeing = sorted(differ + absent)
    claims_bound = status == "BOUND"
    if not exists:
        verdict = "COMMIT_MISSING"
    elif disagreeing and claims_bound:
        verdict = "FALSE_BINDING"
    elif disagreeing:
        # It already says it cannot check, and it is right about that.
        verdict = "DISAGREES_AND_SAYS_SO"
    elif not reachable:
        verdict = "UNREACHABLE_BINDING"
    else:
        verdict = "OK"

    return {
        "manifest": str(path),
        "verdict": verdict,
        "status": status,
        "subject_commit": sha,
        "commit_exists": exists,
        "reachable_from_ref": reachable,
        "bound_files": len(m.get("bound_files") or []),
        "disagreeing": disagreeing,
        "declared_unbound_paths": m.get("subject_commit_unbound_paths") or [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--emit", default="")
    a = ap.parse_args()
    root = Path(a.root).resolve()

    if git("rev-parse", "--git-dir", root=root).returncode != 0:
        print("not a git repository; cannot check reachability", file=sys.stderr)
        return 3

    manifests = sorted(root.glob("papers/**/CONTENT_MANIFEST_V*.json"))
    if not manifests:
        print("no CONTENT_MANIFEST files found", file=sys.stderr)
        return 3

    rows = [audit_manifest(p.relative_to(root), root, a.ref) for p in manifests]
    false_bindings = [r for r in rows if r["verdict"] == "FALSE_BINDING"]
    unreachable = [r for r in rows if r["verdict"] == "UNREACHABLE_BINDING"]
    missing = [r for r in rows if r["verdict"] == "COMMIT_MISSING"]

    out = {
        "schema": "ORION.CONTENT_BINDING_REACHABILITY.v1",
        "ref": a.ref,
        "manifests_audited": len(rows),
        "false_bindings": len(false_bindings),
        "unreachable_bindings": len(unreachable),
        "commit_missing": len(missing),
        "rows": rows,
        "reading": (
            "A false binding is untrue as written and must be corrected to CANNOT_CHECK "
            "with its disagreeing paths listed. An unreachable binding is true but only "
            "checkable by someone holding the side branch it names, which a reviewer "
            "working from the default branch is not."
        ),
    }
    if a.emit:
        Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"manifests audited      : {len(rows)}")
    print(f"FALSE bindings         : {len(false_bindings)}")
    print(f"unreachable bindings   : {len(unreachable)}")
    print(f"subject commit missing : {len(missing)}")
    for r in false_bindings:
        print(f"  FALSE       {r['manifest']}  ({len(r['disagreeing'])} disagreeing)")
    for r in unreachable:
        print(f"  UNREACHABLE {r['manifest']}  {r['subject_commit'][:12]}")
    if false_bindings or missing:
        return 1
    return 2 if unreachable else 0


if __name__ == "__main__":
    raise SystemExit(main())
