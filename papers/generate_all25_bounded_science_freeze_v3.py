#!/usr/bin/env python3
"""Generate the V3 all-25 bounded-science freeze at a given content base.

The V2 freeze is valid only at commit fe5da5332, on a branch 639 commits behind
main that was never merged, and it is substantively stale: 0 of 25 papers still
match their recorded ``final_tree_oid``. Re-anchoring V2 would bind a programme
state that exists nowhere, so the freeze is re-taken rather than repaired.

What carries over unchanged, because it is a judgement rather than a derived
value: every paper's boundary, bounded_terminal, donors, forbidden_promotions,
retained adverse/null/CANNOT_CHECK records, integration_state, source result
commits, and the authority ceiling. What is re-derived: the content anchor and
each paper's final tree.

The audited base is deliberately NOT moved. Its 23 immutable V1 receipts and the
identity registry were verified byte-identical on main, so the original audit
still holds and ``baseline_tree_oid`` stays as audited.

The checker is a template plus embedded constants: validate_checker_template_binding
hashes the source with the constants block replaced by a placeholder, so swapping
constants preserves the template hash by construction.

Usage:
    generate_all25_bounded_science_freeze_v3.py --content-base <commit> [--out-dir papers]

The caller must then commit the two emitted files -- and only those two -- onto
the declared content base, because validate_exact_freeze_commit requires the
freeze commit to add exactly the manifest and the checker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2_CHECKER = ROOT / "papers/check_all25_bounded_science_freeze_v2.py"
CONSTANTS_RE = re.compile(r"(?ms)^CONSTANTS = json\.loads\(r'''(.*?)'''\)\nOID_RE =")
PLACEHOLDER = "@@" + "FREEZE_CONSTANTS_JSON" + "@@"

V3_MANIFEST_REL = "papers/ALL_25_BOUNDED_SCIENCE_FREEZE_V3.json"
V3_CHECKER_REL = "papers/check_all25_bounded_science_freeze_v3.py"


def git(*args: str) -> str:
    out = subprocess.run(["/usr/bin/git", *args], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


def load_v2() -> tuple[str, dict]:
    source = V2_CHECKER.read_text(encoding="utf-8")
    match = CONSTANTS_RE.search(source)
    if not match:
        raise SystemExit("cannot locate embedded constants in the V2 checker")
    return source, json.loads(match.group(1))


def template_of(source: str) -> str:
    normalized, count = CONSTANTS_RE.subn(
        f"CONSTANTS = json.loads(r'''{PLACEHOLDER}''')\nOID_RE =", source, count=1
    )
    if count != 1:
        raise SystemExit("cannot normalize the checker template")
    return normalized


# The V2 checker validates a property of HEAD, not of the freeze:
#
#     head   = git.resolve_commit("HEAD")
#     parent = git.resolve_commit(f"{head}^")
#     require(parent == content_base, ...)
#
# so it passes only while HEAD *is* the freeze commit, and the next commit on
# main turns it into FREEZE_INVALID with no way to tell "never well formed" from
# "unrelated PRs have landed". That is how the V2 freeze became valid only at
# fe5da5332, and it happened again to V3 within hours of taking it.
#
# The patches below move every attestation check onto the freeze commit, which is
# located by identity rather than assumed to be HEAD, and turn post-freeze paper
# movement into a reported outcome instead of an invalidation. `scripts/
# read_all25_freeze_state_v1.py` implements the same separation for freezes whose
# checker predates this change.
#
# Each patch asserts its own replacement count, so a drifted upstream checker
# fails loudly here rather than silently emitting a half-patched validator.
READABLE_PATCHES: tuple[tuple[str, str, int], ...] = (
    (
        "def validate_exact_freeze_commit(git: GitRepo, head: str) -> None:\n"
        '    content_base = CONSTANTS["content_base_commit"]\n'
        '    parent = git.resolve_commit(f"{head}^")\n',
        "def locate_freeze_commit(git: GitRepo, rev: str) -> str:\n"
        '    """The single commit in rev\'s ancestry that ADDS the manifest.\n\n'
        "    Identity, not position. --diff-filter=A is what makes this the freeze\n"
        "    commit rather than any later commit that merely touched the file.\n"
        '    """\n'
        "    out = git.text(\n"
        '        "log", rev, "--diff-filter=A", "--format=%H", "--",\n'
        '        CONSTANTS["manifest_relative"],\n'
        "    ).split()\n"
        "    if not out:\n"
        "        raise CannotCheck(\n"
        '            f"no commit in {rev}\'s ancestry adds "\n'
        '            f"{CONSTANTS[\'manifest_relative\']}"\n'
        "        )\n"
        "    if len(out) > 1:\n"
        "        raise CannotCheck(\n"
        '            "ambiguous history: more than one commit adds the manifest: "\n'
        '            + ", ".join(oid[:12] for oid in out)\n'
        "        )\n"
        "    return out[0]\n"
        "\n"
        "\n"
        "def measure_post_freeze_drift(\n"
        "    git: GitRepo, manifest: dict[str, Any], rev: str\n"
        ") -> list[dict[str, Any]]:\n"
        '    """Papers whose tree has moved since the freeze. Information, not a fault."""\n'
        "    drift = []\n"
        '    for paper in manifest["papers"]:\n'
        '        directory = paper["canonical_directory"]\n'
        "        try:\n"
        "            current = git.tree_oid(rev, directory)\n"
        "        except ValidationError:\n"
        "            current = None\n"
        '        if current != paper["final_tree_oid"]:\n'
        "            drift.append(\n"
        "                {\n"
        '                    "paper_id": paper["paper_id"],\n'
        '                    "canonical_directory": directory,\n'
        '                    "frozen_tree_oid": paper["final_tree_oid"],\n'
        '                    "current_tree_oid": current,\n'
        '                    "state": "ABSENT" if current is None else "MOVED",\n'
        "                }\n"
        "            )\n"
        "    return drift\n"
        "\n"
        "\n"
        "def validate_exact_freeze_commit(git: GitRepo, freeze: str) -> None:\n"
        '    content_base = CONSTANTS["content_base_commit"]\n'
        '    parent = git.resolve_commit(f"{freeze}^")\n',
        1,
    ),
    (
        '    for line in git.text("diff", "--name-status", content_base, head, "--").splitlines():',
        '    for line in git.text("diff", "--name-status", content_base, freeze, "--").splitlines():',
        1,
    ),
    (
        "def validate_git_bindings(git: GitRepo, manifest: dict[str, Any], head: str) -> None:",
        "def validate_git_bindings(git: GitRepo, manifest: dict[str, Any], freeze: str) -> None:",
        1,
    ),
    (
        '    require(git.is_ancestor(content_base, head), "content base is not an ancestor of HEAD")',
        '    require(\n'
        '        git.is_ancestor(content_base, freeze),\n'
        '        "content base is not an ancestor of the freeze commit",\n'
        "    )",
        1,
    ),
    (
        "        for commit in (audited, content_base, head):",
        "        for commit in (audited, content_base, freeze):",
        1,
    ),
    (
        '        require(git.tree_oid(head, path) == paper["final_tree_oid"], f"{paper_id}: post-freeze paper-tree drift")',
        '        require(\n'
        '            git.tree_oid(freeze, path) == paper["final_tree_oid"],\n'
        '            f"{paper_id}: paper tree at the freeze commit does not match its pin",\n'
        "        )",
        1,
    ),
    (
        "class ValidationError(RuntimeError):\n    pass",
        "class ValidationError(RuntimeError):\n"
        '    """The freeze does not hold."""\n'
        "\n"
        "\n"
        "class CannotCheck(RuntimeError):\n"
        '    """Inputs absent or history ambiguous. Distinct from a failure."""',
        1,
    ),
    (
        '    require(status == "", f"worktree is dirty or untracked:\\n{status}")',
        "    if status:\n"
        '        raise CannotCheck(f"worktree is dirty or untracked:\\n{status}")',
        1,
    ),
    (
        '    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="ORION repository root")\n'
        "    return parser.parse_args(argv)",
        '    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="ORION repository root")\n'
        '    parser.add_argument("--rev", default="HEAD", help="revision to read the freeze from")\n'
        "    parser.add_argument(\n"
        '        "--require-no-drift",\n'
        '        action="store_true",\n'
        '        help="also fail when a paper has moved since the freeze, and require a "\n'
        '        "clean worktree; use when TAKING a freeze, not in routine reading",\n'
        "    )\n"
        "    return parser.parse_args(argv)",
        1,
    ),
    (
        "    git = GitRepo(args.repo)\n"
        '    head = git.resolve_commit("HEAD")\n'
        "    validate_exact_freeze_commit(git, head)\n"
        '    manifest_path = git.root / CONSTANTS["manifest_relative"]\n'
        "    try:\n"
        '        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))\n'
        "    except (OSError, json.JSONDecodeError) as exc:\n"
        '        raise ValidationError(f"cannot read committed V2 manifest: {exc}") from exc\n'
        "    validate_manifest_shape(manifest)\n"
        "    validate_git_bindings(git, manifest, head)\n"
        "    validate_clean_worktree(git)\n"
        "    print(\n"
        '        "BOUNDED_FREEZE_VALID "\n'
        "        f\"content_base={CONSTANTS['content_base_commit']} \"\n"
        "        f\"head={head} papers={len(CONSTANTS['papers'])} \"\n"
        '        "authority=submission:false,top-tier:false,external:false,production:false"\n'
        "    )\n"
        "    return 0",
        "    git = GitRepo(args.repo)\n"
        "    rev = git.resolve_commit(args.rev)\n"
        "    freeze = locate_freeze_commit(git, rev)\n"
        "    validate_exact_freeze_commit(git, freeze)\n"
        "    try:\n"
        "        manifest = json.loads(\n"
        '            git.blob_bytes(freeze, CONSTANTS["manifest_relative"]).decode("utf-8")\n'
        "        )\n"
        "    except (ValidationError, UnicodeDecodeError, json.JSONDecodeError) as exc:\n"
        "        raise CannotCheck(\n"
        '            f"cannot read the manifest at the freeze commit: {exc}"\n'
        "        ) from exc\n"
        "    validate_manifest_shape(manifest)\n"
        "    validate_git_bindings(git, manifest, freeze)\n"
        "    drift = measure_post_freeze_drift(git, manifest, rev)\n"
        "    if args.require_no_drift:\n"
        "        validate_clean_worktree(git)\n"
        "    terminal = (\n"
        '        "BOUNDED_FREEZE_ATTESTATION_HOLDS__POST_FREEZE_DRIFT"\n'
        "        if drift\n"
        '        else "BOUNDED_FREEZE_VALID"\n'
        "    )\n"
        "    print(\n"
        '        f"{terminal} "\n'
        "        f\"content_base={CONSTANTS['content_base_commit']} \"\n"
        '        f"freeze_commit={freeze} rev={rev} "\n'
        "        f\"papers={len(CONSTANTS['papers'])} drifted={len(drift)} \"\n"
        '        "authority=submission:false,top-tier:false,external:false,production:false"\n'
        "    )\n"
        "    for row in drift:\n"
        "        print(f\"  DRIFTED {row['paper_id']}: {row['state']}\")\n"
        "    if drift and args.require_no_drift:\n"
        "        raise ValidationError(\n"
        '            "--require-no-drift was set and papers have moved since the freeze"\n'
        "        )\n"
        "    return 0",
        1,
    ),
    (
        "if __name__ == \"__main__\":\n"
        "    try:\n"
        "        raise SystemExit(main())\n"
        "    except ValidationError as exc:\n"
        '        print(f"FREEZE_INVALID: {exc}", file=sys.stderr)\n'
        "        raise SystemExit(1)",
        "if __name__ == \"__main__\":\n"
        "    try:\n"
        "        raise SystemExit(main())\n"
        "    except CannotCheck as exc:\n"
        '        print(f"FREEZE_CANNOT_CHECK: {exc}", file=sys.stderr)\n'
        "        raise SystemExit(3)\n"
        "    except ValidationError as exc:\n"
        '        print(f"FREEZE_INVALID: {exc}", file=sys.stderr)\n'
        "        raise SystemExit(1)",
        1,
    ),
)


def readable_template(template: str) -> str:
    """Move the checker's attestation from HEAD onto the freeze commit."""
    patched = template
    for old, new, expected in READABLE_PATCHES:
        count = patched.count(old)
        if count == expected:
            patched = patched.replace(old, new)
        else:
            raise SystemExit(
                "cannot patch the checker template for readability: expected "
                f"{expected} occurrence(s) of a fragment, found {count}. The "
                "upstream checker has drifted; reconcile it rather than emitting "
                "a half-patched validator."
            )
    if "head" in patched[patched.find("OID_RE ="):]:
        raise SystemExit(
            "patched template still refers to `head`; the attestation would "
            "remain tied to the reading position"
        )
    return patched


def verify_immutable(constants: dict, ref: str) -> None:
    """Refuse to re-freeze if the audited evidence base moved."""
    bad = []
    for entry in constants["immutable_v1_receipts"]:
        try:
            current = git("rev-parse", f"{ref}:{entry['path']}")
        except SystemExit:
            bad.append((entry["path"], "MISSING"))
            continue
        if current != entry["blob_oid"]:
            bad.append((entry["path"], current))
    registry = constants.get("identity_registry", {})
    if registry:
        current = git("rev-parse", f"{ref}:{registry['path']}")
        if current != registry["git_blob_oid"]:
            bad.append((registry["path"], current))
    if bad:
        for path, got in bad:
            print(f"IMMUTABLE DRIFT: {path} -> {got}", file=sys.stderr)
        raise SystemExit(
            "refusing to re-freeze: the audited immutable evidence base has changed, "
            "which is a finding about immutability, not a re-anchoring problem"
        )


def build(
    content_base: str,
    allow_unreachable: bool = False,
    legacy_checker: bool = False,
) -> tuple[dict, str]:
    source, constants = load_v2()
    verify_immutable(constants, content_base)

    new = json.loads(json.dumps(constants))
    new["content_base_commit"] = git("rev-parse", content_base)
    new["content_base_tree"] = git("rev-parse", f"{content_base}^{{tree}}")
    new["manifest_relative"] = V3_MANIFEST_REL
    new["checker_relative"] = V3_CHECKER_REL

    # Provenance that has become unreachable is dispositioned, not dropped and not
    # silently re-derived. The V2 record cites source result commits that were
    # reachable in August and are now absent locally and refused by the remote as
    # "not our ref"; nothing can re-derive them. Retaining the identifier under an
    # explicit CANNOT_CHECK disposition preserves the provenance claim and its
    # failure, while leaving `source_result_commits` to mean exactly what the
    # checker enforces: commits that resolve. Requires --disposition-unreachable
    # so that writing a freeze around unreachable provenance is a deliberate act.
    unreachable: list[tuple[str, str]] = []
    for pid, paper in new["papers"].items():
        keep, lost = [], []
        for commit in paper.get("source_result_commits") or []:
            probe = subprocess.run(
                ["/usr/bin/git", "cat-file", "-e", f"{commit}^{{commit}}"],
                cwd=ROOT, capture_output=True,
            )
            (keep if probe.returncode == 0 else lost).append(commit)
        if lost:
            unreachable.extend((pid, c) for c in lost)
            if not allow_unreachable:
                continue
            paper["source_result_commits"] = keep
            paper["unreachable_source_result_commits"] = [
                {
                    "commit": c,
                    "disposition": "UNREACHABLE_PROVENANCE__CANNOT_CHECK",
                    "note": (
                        "cited by the V2 freeze and reachable at that time; absent from this "
                        "repository and refused by the remote as 'not our ref'. Retained as a "
                        "provenance claim that can no longer be checked, not withdrawn."
                    ),
                }
                for c in lost
            ]
    if unreachable and not allow_unreachable:
        for pid, commit in unreachable:
            print(f"UNREACHABLE PROVENANCE: {pid} source_result_commit {commit}", file=sys.stderr)
        raise SystemExit(
            "refusing to re-freeze: the V2 record cites source result commits that no "
            "longer exist. Re-run with --disposition-unreachable to retain them under an "
            "explicit UNREACHABLE_PROVENANCE__CANNOT_CHECK disposition."
        )
    if unreachable:
        print(f"dispositioned {len(unreachable)} unreachable source result commit(s) "
              f"as UNREACHABLE_PROVENANCE__CANNOT_CHECK:")
        for pid, commit in unreachable:
            print(f"   {pid}  {commit}")

    moved = 0
    repinned: list[tuple[str, str, str, str]] = []
    for pid, paper in new["papers"].items():
        directory = paper["canonical_directory"]
        final = git("rev-parse", f"{content_base}:{directory}")
        if final != paper["final_tree_oid"]:
            moved += 1
        paper["final_tree_oid"] = final

        # Donor and retained adverse/null records are pinned by blob. Re-pin them
        # at the new content base, but report every one that moved: a freeze that
        # silently absorbs a changed negative is worse than no freeze. A record
        # that has disappeared is refused outright rather than dropped.
        for field in ("donors", "retained_adverse_null_cannot_check"):
            for entry in paper.get(field) or []:
                path = entry.get("path")
                if not path or "git_blob_oid" not in entry:
                    continue
                try:
                    current = git("rev-parse", f"{content_base}:{path}")
                except SystemExit:
                    raise SystemExit(
                        f"refusing to re-freeze: {pid} {field} record has disappeared "
                        f"from the content base: {path}"
                    )
                if current != entry["git_blob_oid"]:
                    # Re-pin the bytes only if the meaning survived. A retained
                    # negative that no longer states its own terminal has been
                    # weakened, and that is a finding, not something to re-pin.
                    blob = subprocess.run(
                        ["/usr/bin/git", "show", f"{content_base}:{path}"],
                        cwd=ROOT, capture_output=True,
                    ).stdout
                    text = blob.decode("utf-8", errors="replace")
                    for token in entry.get("required_terminal_tokens") or []:
                        if token not in text:
                            raise SystemExit(
                                f"refusing to re-freeze: {pid} {field} record no longer "
                                f"contains its required terminal token {token!r}: {path}"
                            )
                    repinned.append((pid, field, path, current))
                    entry["git_blob_oid"] = current
                    if "sha256" in entry:
                        entry["sha256"] = hashlib.sha256(blob).hexdigest()
    if repinned:
        print(f"\nre-pinned {len(repinned)} evidence record(s) that moved since the V2 freeze;")
        print("each must be reviewed as a change to retained evidence, not absorbed silently:")
        for pid, field, path, oid in repinned:
            print(f"   {pid}  {field}  -> {oid[:12]}  {path}")

    template = template_of(source)
    if not legacy_checker:
        template = readable_template(template)
    new["checker_template_binding"] = {
        "algorithm": "sha256",
        "normalization": constants["checker_template_binding"]["normalization"],
        "normalized_template_sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
    }
    print(f"papers whose final tree moved since the V2 freeze: {moved}/{len(new['papers'])}")
    return new, template


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-base", required=True)
    # Must default to the directory named by V3_MANIFEST_REL / V3_CHECKER_REL.
    # The manifest records those relative paths as its own identity, so writing
    # anywhere else produces a file that misdescribes where it lives.
    parser.add_argument("--out-dir", type=Path, default=ROOT / "papers")
    parser.add_argument("--date", default=None)
    parser.add_argument("--disposition-unreachable", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--legacy-checker",
        action="store_true",
        help="emit the unpatched V2-derived checker, which validates a property "
        "of HEAD and therefore reads as invalid from the next commit onward",
    )
    args = parser.parse_args(argv)
    if args.date is None:
        import datetime
        args.date = datetime.date.today().isoformat()

    constants, template = build(
        args.content_base, args.disposition_unreachable, args.legacy_checker
    )
    blob = json.dumps(constants, indent=2, sort_keys=True, ensure_ascii=False)
    checker = template.replace(PLACEHOLDER, blob)

    # The manifest is not the raw constants: `papers` is a list carrying paper_id,
    # the receipt set is restructured, and manifest-only keys (date, science_frozen)
    # are present while checker-only keys (protected_paths, *_relative) are not.
    manifest = {
        "audited_base_commit": constants["audited_base_commit"],
        "audited_base_tree": constants["audited_base_tree"],
        "authority_ceiling": constants["authority_ceiling"],
        "checker_template_binding": constants["checker_template_binding"],
        "content_base_commit": constants["content_base_commit"],
        "content_base_tree": constants["content_base_tree"],
        "date": args.date,
        "evidence_semantics": constants["evidence_semantics"],
        "identity_registry": constants["identity_registry"],
        "immutable_v1_receipt_set": {
            "audited_at_commit": constants["audited_base_commit"],
            "count": len(constants["immutable_v1_receipts"]),
            "entries": constants["immutable_v1_receipts"],
            "sorted_git_listing_sha256": constants["immutable_v1_listing_sha256"],
        },
        "noncontrolling_provenance": constants["noncontrolling_provenance"],
        "papers": [
            {"paper_id": pid, **body}
            for pid, body in sorted(constants["papers"].items())
        ],
        "schema": constants["schema"],
        "science_frozen": True,
        "terminal": constants["terminal"],
    }

    if args.dry_run:
        print(f"would write {V3_CHECKER_REL} ({len(checker)} bytes)")
        print(f"would write {V3_MANIFEST_REL} ({len(json.dumps(manifest, indent=2))} bytes)")
        print(f"content_base_commit = {constants['content_base_commit']}")
        return 0

    (args.out_dir / "check_all25_bounded_science_freeze_v3.py").write_text(checker, encoding="utf-8")
    (args.out_dir / "ALL_25_BOUNDED_SCIENCE_FREEZE_V3.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {V3_CHECKER_REL} and {V3_MANIFEST_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
