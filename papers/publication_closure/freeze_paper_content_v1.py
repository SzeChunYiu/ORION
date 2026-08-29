#!/usr/bin/env python3
"""Freeze one paper directory's tracked bytes into a manifest and a digest file.

ORION-16..25 each carry a ``CONTENT_MANIFEST_V1.json`` naming the files bound
into the package and a ``SHA256SUMS`` holding their digests. ORION-01..15
carried neither, so nothing could say whether a byte under those directories
had moved: ``orion.programme.content_binding_coverage`` reported them
``UNBOUND``, and an unbound paper answers "how many files drifted?" with the
same ``0`` a clean bound one does.

This tool writes that pair for one paper directory. It binds bytes and names
the commit they were read at. It is **not** a readiness verdict, not novelty or
claim authority, and not permission to deposit a permanent archive --
``grants_authority`` is ``NONE`` and this tool never writes anything else there.

The inclusion rule is not invented here; it is read off the seven packages that
already carry a V1 binding. At their subject commits ORION-19..25 bind every
tracked file in their own directory except exactly two: the manifest (which
cannot hash itself) and the paper-root ``SHA256SUMS`` (which cannot contain its
own digest). ORION-20 at ``81473e5e`` is the clearest case -- 52 tracked, 50
bound, those two excluded. Files under ``audit/``, and files whose names carry
``_AUDIT_`` or ``_STATUS_``, are unbound in the *current* tree only because
they were added after the freeze; they are not a category the convention
excludes, and treating them as one would silently drop scientific content on a
filename coincidence.

Build artifacts are excluded through
:func:`orion.programme.content_binding_coverage.is_build_artifact` rather than
through a second copy of the rule. That module's own docstring records what
happened when the rule was written out twice: the copies drifted once LaTeX
trees appeared, and one side reported files current that nobody was watching.
Excluding them also keeps this tool's numerator aligned with that module's
denominator, which drops the same files from ``files_on_disk``.

Nested digest files -- ``experiments/.../SHA256SUMS`` and friends -- are bound.
They are content produced by an experiment, not this package's own binding.
ORION-19 binds its nested ``ut3-checkpoint-custody-v1/SHA256SUMS``, and the
coverage survey drops any path named ``SHA256SUMS`` from ``covered`` anyway, so
including them matches convention without inflating coverage.

Symlinks and submodule entries are not bound, because they carry no bytes to
hash: ``shasum -a 256`` on ``papers/orion-02-fiberguard-finite-fibre/rounds/r19``
fails with "Is a directory". Their omission is printed on every run rather than
left silent -- an absence that prints nothing is indistinguishable from a clean
result. No content is lost by it: the symlink's target is a separately tracked
directory whose files are bound in their own right, and ``Path.rglob`` does not
descend a symlinked directory, so the coverage survey never counted it either.

``subject_commit_unbound_paths`` keeps the meaning
``papers/candidates/checkers/check_content_binding_v1.py`` gives it -- bound
files whose worktree bytes disagree with the recorded commit -- because four
checkers under ``papers/`` assert that field is ``[]``. A skipped symlink is not
drift and must never be reported there.

Exit codes: ``0`` clean, ``1`` drift, ``3`` CANNOT_CHECK.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from orion.programme.content_binding_coverage import is_build_artifact

SCHEMA_VERSION = "orion.candidate-content-binding.v1"
MANIFEST_NAME = "CONTENT_MANIFEST_V1.json"
SUMS_NAME = "SHA256SUMS"

#: Copied verbatim from the packages that already carry a V1 binding. The
#: wording is the boundary: restating it loosely here would let a byte binding
#: read as the readiness work it is only a prerequisite for.
CLAIM_SCOPE = (
    "Binds the bytes of one candidate package and names the commit they were "
    "read at. Not a readiness verdict, not novelty or claim authority, and not "
    "permission to deposit a permanent archive."
)

#: ORION-11..15 are P1..P5 -- each directory carries `P<n>_`-prefixed artifacts
#: naming itself, and ORION-16..25 continue the run as P6..P15. ORION-01..10
#: predate that series and carry no `P<n>` identity anywhere in the tree, so
#: they are named by their ORION id. Deriving `P(n-10)` for them would mint
#: candidate numbers the programme never assigned.
def candidate_id_for(paper_dir_name: str) -> str:
    prefix = "orion-"
    if not paper_dir_name.startswith(prefix):
        return paper_dir_name
    head = paper_dir_name[len(prefix) :].split("-", 1)[0]
    if not head.isdigit():
        return paper_dir_name
    number = int(head)
    if 11 <= number <= 25:
        return f"P{number - 10}"
    return f"ORION-{number:02d}"


class CannotCheck(RuntimeError):
    """The freeze could not be evaluated at all, as distinct from failing."""


def _git(repo_root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ["/usr/bin/git", "-C", str(repo_root), *arguments],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise CannotCheck(f"git {' '.join(arguments)} failed: {error}") from error
    return completed.stdout


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_entries(repo_root: Path, relative_dir: str) -> tuple[list[str], list[str]]:
    """Tracked paths under the directory, split into regular blobs and the rest.

    ``-z`` is not optional. Without it git C-quotes any path holding a space or
    a backslash, and a quoted path silently stops matching the file on disk.
    """

    raw = _git(repo_root, "ls-tree", "-r", "-z", "HEAD", "--", relative_dir)
    regular: list[str] = []
    skipped: list[str] = []
    for record in raw.split("\0"):
        if not record:
            continue
        meta, _, path = record.partition("\t")
        mode = meta.split(" ", 1)[0]
        # 100644/100755 are regular blobs. 120000 is a symlink and 160000 a
        # submodule gitlink; neither holds bytes this manifest can bind.
        if mode in {"100644", "100755"}:
            regular.append(path)
        else:
            skipped.append(f"{path} (mode {mode})")
    return sorted(regular), sorted(skipped)


def bind_set(repo_root: Path, paper_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """Return (bound paths, skipped non-blob entries, excluded build artifacts)."""

    relative_dir = paper_dir.relative_to(repo_root).as_posix()
    regular, skipped = _tree_entries(repo_root, relative_dir)
    own_artifacts = {f"{relative_dir}/{MANIFEST_NAME}", f"{relative_dir}/{SUMS_NAME}"}

    bound: list[str] = []
    build: list[str] = []
    for path in regular:
        if path in own_artifacts:
            continue
        # The absolute path matters: is_build_artifact's sidecar rule asks
        # whether a `.tex` neighbour exists on disk, which answers False for a
        # relative path resolved against the wrong cwd.
        if is_build_artifact(repo_root / path):
            build.append(path)
            continue
        bound.append(path)
    return bound, skipped, build


def _worktree_disagreement(repo_root: Path, paper_dir: Path, bound: list[str]) -> list[str]:
    """Bound paths whose worktree bytes differ from HEAD.

    Mirrors ``check_content_binding_v1.commit_disagreement``: a commit that does
    not describe the bytes on disk is not a subject, and recording it as one
    would be the fabrication this tool exists to prevent.
    """

    relative_dir = paper_dir.relative_to(repo_root).as_posix()
    changed = set(
        _git(repo_root, "diff", "--name-only", "-z", "HEAD", "--", relative_dir).split("\0")
    )
    return sorted(set(bound) & changed)


def build_manifest(repo_root: Path, paper_dir: Path) -> tuple[dict[str, object], list[str], dict]:
    bound, skipped, build = bind_set(repo_root, paper_dir)
    if not bound:
        raise CannotCheck(f"{paper_dir} has no tracked file to bind")

    head = _git(repo_root, "rev-parse", "HEAD").strip()
    missing = [path for path in bound if not (repo_root / path).is_file()]
    if missing:
        raise CannotCheck(f"tracked at HEAD but absent from the worktree: {missing[:5]}")

    disagreeing = _worktree_disagreement(repo_root, paper_dir, bound)
    if disagreeing:
        status, blocker = "CANNOT_CHECK", (
            "bound files differ from the recorded commit; the commit does not "
            "describe these bytes"
        )
    else:
        status, blocker = "BOUND", None

    relative_dir = paper_dir.relative_to(repo_root).as_posix()
    manifest = {
        "bound_files": [{"path": path, "role": None} for path in bound],
        "candidate_id": candidate_id_for(paper_dir.name),
        "claim_scope": CLAIM_SCOPE,
        "closes_gate": None,
        "digest_file": f"{relative_dir}/{SUMS_NAME}",
        "grants_authority": "NONE",
        "issue": None,
        "reproducibility_targets": {},
        "schema_version": SCHEMA_VERSION,
        "subject_commit": head,
        "subject_commit_blocker": blocker,
        "subject_commit_status": status,
        "subject_commit_unbound_paths": disagreeing,
    }
    return manifest, bound, {"skipped": skipped, "build": build}


def render_sums(repo_root: Path, bound: list[str]) -> str:
    """`shasum -a 256` output order: ascending digest, two spaces, repo-relative path."""

    rows = sorted((_sha256(repo_root / path), path) for path in bound)
    return "".join(f"{digest}  {path}\n" for digest, path in rows)


def parse_sums(text: str) -> dict[str, str]:
    recorded: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        digest, separator, path = line.partition("  ")
        if not separator or len(digest) != 64:
            raise CannotCheck(f"{SUMS_NAME} line {number} is not a sha256 record: {line!r}")
        recorded[path] = digest
    return recorded


def check(repo_root: Path, paper_dir: Path) -> tuple[int, dict[str, object]]:
    """Verify the recorded digests against disk.

    Deliberately *not* a re-derivation of the bind set. A freeze names the bytes
    it was taken over; files added since are a coverage question, reported here
    as `unmanifested_tracked_files`, not drift. Failing on them would turn every
    still-valid freeze red the moment its paper grew a file.
    """

    manifest_path = paper_dir / MANIFEST_NAME
    sums_path = paper_dir / SUMS_NAME
    for required in (manifest_path, sums_path):
        if not required.is_file():
            return 3, {"outcome": "CANNOT_CHECK", "reason": f"missing {required}"}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        recorded = parse_sums(sums_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, CannotCheck) as error:
        return 3, {"outcome": "CANNOT_CHECK", "reason": str(error)}

    declared = [entry["path"] for entry in manifest.get("bound_files", [])]
    drifted: list[str] = []
    missing: list[str] = []
    for path, digest in sorted(recorded.items()):
        target = repo_root / path
        if not target.is_file():
            missing.append(path)
        elif _sha256(target) != digest:
            drifted.append(path)

    undigested = sorted(set(declared) - set(recorded))
    unmanifested_digests = sorted(set(recorded) - set(declared))
    # Coverage is informational, so its absence must not decide the verdict.
    # Drift is a question about bytes on disk; making it depend on git metadata
    # would report "cannot check" for a tree that plainly had drifted.
    try:
        tracked_now, _, _ = bind_set(repo_root, paper_dir)
        coverage_delta: list[str] | None = sorted(set(tracked_now) - set(declared))
    except CannotCheck:
        coverage_delta = None

    report = {
        "paper": paper_dir.relative_to(repo_root).as_posix(),
        "subject_commit": manifest.get("subject_commit"),
        "subject_commit_status": manifest.get("subject_commit_status"),
        "bound_files": len(declared),
        "digest_records": len(recorded),
        "drifted": drifted,
        "missing": missing,
        "manifest_entries_without_a_digest": undigested,
        "digest_records_not_in_manifest": unmanifested_digests,
        "unmanifested_tracked_files": coverage_delta,
    }

    if manifest.get("subject_commit_status") == "CANNOT_CHECK":
        report["outcome"] = "CANNOT_CHECK"
        return 3, report
    if drifted or missing or undigested or unmanifested_digests:
        report["outcome"] = "DRIFT"
        return 1, report
    report["outcome"] = "OK"
    return 0, report


def write(repo_root: Path, paper_dir: Path) -> tuple[int, dict[str, object]]:
    manifest, bound, extra = build_manifest(repo_root, paper_dir)
    (paper_dir / SUMS_NAME).write_text(render_sums(repo_root, bound), encoding="utf-8")
    (paper_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report = {
        "paper": paper_dir.relative_to(repo_root).as_posix(),
        "candidate_id": manifest["candidate_id"],
        "subject_commit": manifest["subject_commit"],
        "subject_commit_status": manifest["subject_commit_status"],
        "bound_files": len(bound),
        "subject_commit_unbound_paths": manifest["subject_commit_unbound_paths"],
        "skipped_non_blob_entries": extra["skipped"],
        "excluded_build_artifacts": extra["build"],
        "outcome": "WROTE",
    }
    return (0 if manifest["subject_commit_status"] == "BOUND" else 3), report


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_dir", type=Path, help="paper directory to freeze")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify, write nothing")
    mode.add_argument("--write", action="store_true", help="regenerate manifest and digests")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)

    repo_root = arguments.repo_root.resolve()
    paper_dir = arguments.paper_dir.resolve()
    if not paper_dir.is_dir():
        print(f"CANNOT_CHECK: no such directory: {paper_dir}", file=sys.stderr)
        return 3
    try:
        paper_dir.relative_to(repo_root)
    except ValueError:
        print(f"CANNOT_CHECK: {paper_dir} is outside {repo_root}", file=sys.stderr)
        return 3

    try:
        code, report = check(repo_root, paper_dir) if arguments.check else write(repo_root, paper_dir)
    except CannotCheck as error:
        print(f"CANNOT_CHECK: {error}", file=sys.stderr)
        return 3

    if arguments.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['paper']}: {report['outcome']} ({report['bound_files']} bound files)")
        for key in (
            "drifted",
            "missing",
            "manifest_entries_without_a_digest",
            "digest_records_not_in_manifest",
            "subject_commit_unbound_paths",
            "skipped_non_blob_entries",
            "excluded_build_artifacts",
            "unmanifested_tracked_files",
        ):
            values = report.get(key) or []
            # Printed even when the run is clean: an omission that prints
            # nothing cannot be told apart from an omission that did not happen.
            if values:
                print(f"  {key}: {len(values)}")
                for value in values[:10]:
                    print(f"    {value}")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
