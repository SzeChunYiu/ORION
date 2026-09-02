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


def build(content_base: str, allow_unreachable: bool = False) -> tuple[dict, str]:
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
    args = parser.parse_args(argv)
    if args.date is None:
        import datetime
        args.date = datetime.date.today().isoformat()

    constants, template = build(args.content_base, args.disposition_unreachable)
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
