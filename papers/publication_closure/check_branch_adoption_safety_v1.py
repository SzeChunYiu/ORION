#!/usr/bin/env python3
"""Would adopting this branch delete evidence that `main` currently holds?

Issue #1701 lists a number of branches as ADOPT FIRST. Two of them, checked by hand,
turned out to carry real contributions *and* silent regressions in the same diff. This
generalises that check so it is cheap and consistent to run on the rest.

The core move is a three-way blob comparison. "Differs from the merge-base" is not "is
newer": a file can differ because the branch advanced it, because `main` advanced it, or
because both did. Only the first is safe to take wholesale.

For every file the branch touches, each blob is classified:

  SAME_AS_MAIN    branch content already equals main
  ONLY_ON_BRANCH  main does not have the file at all -> a candidate contribution
  BRANCH_AHEAD    main is still at the merge-base -> branch advanced it alone
  MAIN_AHEAD      branch is still at the merge-base -> branch is stale here
  BOTH_DIVERGED   both moved -> needs reconciliation, never a wholesale take

and then, for anything main also has, the branch is checked for *evidence loss*: does
main carry negative-evidence lines (CANNOT_CHECK, adverse, falsified, quarantined,
refuted, NOT_SUPPORTED) or JSONL records that the branch does not?

Exit codes
  0  SAFE          - nothing main holds would be lost
  1  WOULD_DELETE  - adopting wholesale would drop evidence main has
  3  CANNOT_CHECK  - ref unresolvable or no merge-base
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

EXIT_SAFE, EXIT_WOULD_DELETE, EXIT_CANNOT_CHECK = 0, 1, 3

NEG = re.compile(
    r"CANNOT_CHECK|adverse|falsif|quarantin|refut|NOT_SUPPORTED|null result|retract",
    re.IGNORECASE,
)


def git(*args: str) -> str:
    r = subprocess.run(["/usr/bin/git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def blob(ref: str, path: str) -> str | None:
    r = subprocess.run(
        ["/usr/bin/git", "rev-parse", f"{ref}:{path}"], capture_output=True, text=True
    )
    return r.stdout.strip() if r.returncode == 0 else None


def content(ref: str, path: str) -> str:
    return git("show", f"{ref}:{path}")


def jsonl_keys(text: str) -> list[str]:
    """Record identity for a .jsonl ledger, so 'fewer lines' becomes 'which records'."""
    keys = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            keys.append(line[:80])
            continue
        for f in ("attempt_id", "id", "record_id", "case_id", "round"):
            if f in r:
                keys.append(str(r[f]))
                break
        else:
            keys.append(json.dumps(r, sort_keys=True)[:80])
    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("branch")
    ap.add_argument("--main", default="origin/main")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()

    if not git("rev-parse", "--verify", f"{args.branch}^{{commit}}").strip():
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "BRANCH_UNRESOLVABLE"}))
        return EXIT_CANNOT_CHECK
    mb = git("merge-base", args.branch, args.main).strip()
    if not mb:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "NO_MERGE_BASE"}))
        return EXIT_CANNOT_CHECK

    files = [f for f in git("diff", "--name-only", mb, args.branch).splitlines() if f]
    buckets: dict[str, list[str]] = {}
    losses = []

    for f in files:
        b, m, base = blob(args.branch, f), blob(args.main, f), blob(mb, f)
        if b is None and m is None:
            # Present only at the merge-base; both sides removed it. Not a
            # contribution (there is nothing to contribute) and not a loss.
            cls = "DELETED_BY_BOTH"
        elif b is None and m is not None:
            # The branch deletes a file main still has. This is never a contribution,
            # and it is invisible to a line-count comparison, so it is called out here.
            cls = "DELETED_BY_BRANCH"
        elif m is None:
            cls = "ONLY_ON_BRANCH"
        elif b == m:
            cls = "SAME_AS_MAIN"
        elif m == base:
            cls = "BRANCH_AHEAD"
        elif b == base:
            cls = "MAIN_AHEAD"
        else:
            cls = "BOTH_DIVERGED"
        buckets.setdefault(cls, []).append(f)

        if cls == "DELETED_BY_BRANCH":
            losses.append({
                "path": f,
                "classification": cls,
                "deleted_by_branch": True,
                "main_bytes": len(content(args.main, f)),
            })
            continue
        if m is None or b == m:
            continue
        mt, bt = content(args.main, f), content(args.branch, f)
        entry = {"path": f, "classification": cls}
        hit = False
        if f.endswith(".jsonl"):
            mk, bk = jsonl_keys(mt), jsonl_keys(bt)
            lost = [k for k in mk if k not in bk]
            if lost:
                entry["lost_records"] = sorted(set(lost))
                entry["record_counts"] = {"main": len(mk), "branch": len(bk)}
                hit = True
        mn = sum(1 for l in mt.splitlines() if NEG.search(l))
        bn = sum(1 for l in bt.splitlines() if NEG.search(l))
        if mn > bn:
            entry["negative_lines"] = {"main": mn, "branch": bn, "delta": mn - bn}
            hit = True
        ml, bl = len(mt.splitlines()), len(bt.splitlines())
        if ml > bl:
            entry["line_counts"] = {"main": ml, "branch": bl, "delta": ml - bl}
            hit = True
        # Line counts read 0 for a single-line file with no trailing newline, which
        # hid a real shrink during validation. Bytes do not have that blind spot.
        if len(mt) > len(bt):
            entry["byte_counts"] = {"main": len(mt), "branch": len(bt),
                                    "delta": len(mt) - len(bt)}
            hit = True
        if hit:
            losses.append(entry)

    out = {
        "branch": args.branch,
        "main": args.main,
        "merge_base": mb[:9],
        "files_touched": len(files),
        "classification": {k: len(v) for k, v in sorted(buckets.items())},
        "contributions": sorted(
            buckets.get("ONLY_ON_BRANCH", []) + buckets.get("BRANCH_AHEAD", [])
        ),
        "deleted_by_branch": sorted(buckets.get("DELETED_BY_BRANCH", [])),
        "evidence_losses": losses,
        "status": "WOULD_DELETE_EVIDENCE" if losses else "SAFE_TO_ADOPT",
    }
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return EXIT_WOULD_DELETE if losses else EXIT_SAFE


if __name__ == "__main__":
    sys.exit(main())
