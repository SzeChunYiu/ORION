#!/usr/bin/env python3
"""Bind ORION-16--18 publication packages to a committed subject.

The V1 candidate bindings are frozen.  Their V2 successors own additive files,
so publication-ready package files may be added or deliberately rebound there
without re-hashing or otherwise rewriting any previously bound scientific file.
Every package rebind records its prior digest and subject commit. Run this only
after the package commit exists; the resulting manifest commit can then follow
in a second commit, leaving the subject pin reachable after a merge commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PAPERS = {
    "P6": "orion-16-formal-epistemic-structures-and-mechanics",
    "P7": "orion-17-epistemic-navigation-open-worlds",
    "P8": "orion-18-epistemic-authority-autonomous-science",
}
PACKAGE = Path("submission/publication-ready-20260831")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_bytes(commit: str, relative: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"subject commit lacks {relative}")
    return completed.stdout


def git_text(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def extend(candidate_id: str, slug: str, commit: str) -> None:
    paper = ROOT / "papers" / slug
    manifest_path = paper / "CONTENT_MANIFEST_V2.json"
    outer_sums = paper / "content_binding_v2" / "SHA256SUMS"
    package = paper / PACKAGE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "orion.candidate-content-binding.v2":
        raise RuntimeError(f"{candidate_id}: unexpected V2 schema")
    if manifest.get("candidate_id") != candidate_id:
        raise RuntimeError(f"{candidate_id}: manifest candidate mismatch")
    prior_subject_commit = manifest.get("subject_commit")
    rows = manifest.get("bound_files")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"{candidate_id}: no prior bound files")

    by_path: dict[str, dict[str, str]] = {}
    package_prefix = (paper / PACKAGE).relative_to(ROOT).as_posix() + "/"
    package_rebindings: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
            raise RuntimeError(f"{candidate_id}: malformed prior bound row")
        relative = str(row["path"])
        if relative in by_path:
            raise RuntimeError(f"{candidate_id}: duplicate prior row {relative}")
        local = ROOT / relative
        expected = str(row["sha256"])
        if not local.is_file():
            raise RuntimeError(f"{candidate_id}: prior bound file disappeared: {relative}")
        actual = sha256_file(local)
        committed = sha256_bytes(git_bytes(commit, relative))
        if actual != committed:
            raise RuntimeError(f"{candidate_id}: working tree disagrees with subject commit: {relative}")
        if actual != expected:
            if not relative.startswith(package_prefix):
                raise RuntimeError(f"{candidate_id}: refusing to conceal scientific drift in {relative}")
            package_rebindings.append(
                {"path": relative, "prior_sha256": expected, "new_sha256": actual}
            )
        by_path[relative] = {"path": relative, "sha256": actual}

    if not package.is_dir():
        raise RuntimeError(f"{candidate_id}: publication package is absent")
    for path in sorted(package.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        relative = path.relative_to(ROOT).as_posix()
        digest = sha256_file(path)
        prior = by_path.get(relative)
        if prior is not None and prior["sha256"] != digest:
            raise RuntimeError(f"{candidate_id}: existing publication row drifted: {relative}")
        if sha256_bytes(git_bytes(commit, relative)) != digest:
            raise RuntimeError(f"{candidate_id}: package bytes are not in subject commit: {relative}")
        by_path[relative] = {"path": relative, "sha256": digest}

    lock = manifest.get("environment_lock")
    if not isinstance(lock, dict) or sha256_file(ROOT / str(lock.get("path"))) != lock.get("sha256"):
        raise RuntimeError(f"{candidate_id}: environment lock drifted")
    manifest["bound_files"] = [by_path[path] for path in sorted(by_path)]
    manifest["subject_commit"] = commit
    manifest["subject_tree"] = git_text("rev-parse", f"{commit}^{{tree}}")
    manifest["subject_commit_status"] = "BOUND"
    manifest["subject_commit_blocker"] = None
    manifest["subject_commit_unbound_paths"] = []
    if package_rebindings:
        history = manifest.setdefault("publication_package_rebinding_history", [])
        if not isinstance(history, list):
            raise RuntimeError(f"{candidate_id}: malformed publication rebind history")
        history.append(
            {
                "prior_subject_commit": prior_subject_commit,
                "new_subject_commit": commit,
                "reason": "publication package updated after a newly landed integrity diagnosis; scientific authority unchanged",
                "scientific_authority_delta": "NONE",
                "files": package_rebindings,
            }
        )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    outer_sums.write_text(
        f"{sha256_file(manifest_path)}  {manifest_path.relative_to(ROOT).as_posix()}\n",
        encoding="utf-8",
    )
    print(f"{candidate_id}: bound {len(by_path)} files to {commit}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-commit", required=True)
    parser.add_argument(
        "--candidate",
        action="append",
        choices=sorted(PAPERS),
        help="candidate to bind; repeat as needed (default: all)",
    )
    args = parser.parse_args()
    commit = args.subject_commit
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SystemExit("--subject-commit must be a full lowercase Git object ID")
    git_text("cat-file", "-e", f"{commit}^{{commit}}")
    git_text("merge-base", "--is-ancestor", commit, "HEAD")
    selected = args.candidate
    for candidate_id in selected or PAPERS:
        slug = PAPERS[candidate_id]
        extend(candidate_id, slug, commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
