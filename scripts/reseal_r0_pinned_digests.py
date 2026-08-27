#!/usr/bin/env python3
"""Update pins that name the pre-R0 digest of a file R0 renamed into.

Wave R0 (``3a1a83178``, PR #1474) rewrote paths inside 3658 files under the
operator's naming-unification directive, and regenerated digest pins only for
``orion-16..25``.  Everywhere else -- test constants, checker constants,
receipts -- a hard-coded SHA-256 still names the *pre-R0* bytes.  Those pins
fail closed, and because many of them guard a whole module's fixtures, one
stale constant can account for every failure in a file.

This replaces a hex literal only when both hold:

* it is **exactly** the SHA-256 of some file's pre-R0 bytes, so it is a pin for
  that file and not an unrelated hash that happens to be 64 hex characters; and
* applying the alias registry to those pre-R0 bytes reproduces the file's
  committed bytes exactly, so R0 changed names and nothing else.

A file whose content genuinely changed is never re-pinned: renaming a path
cannot change a result, but re-pinning a changed result would launder one.

Exit codes
----------
0  clean, or --apply completed
1  stale pins remain (report mode)
2  the alias registry could not be read -- CANNOT_CHECK, distinct from clean
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R0 = "3a1a83178"
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
TEXT = {".py", ".md", ".json", ".yml", ".yaml", ".txt", ".cfg", ".toml"}

sys.path.insert(0, str(ROOT / "scripts"))
from repin_r0_renamed_digests import load_alias_pairs, r0_rename_map, rename_only, run  # noqa: E402


def batch_blobs(revspecs: list[str]) -> dict[str, bytes]:
    """Read many blobs in one git process; a per-file git show is far too slow."""
    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert proc.stdin and proc.stdout
    out: dict[str, bytes] = {}
    # Write and read in lockstep. Writing every spec up front fills the pipe
    # buffer while git is blocked writing output nobody is reading yet, and the
    # whole thing deadlocks a few thousand specs in.
    for spec in revspecs:
        proc.stdin.write(f"{spec}\n".encode())
        proc.stdin.flush()
        header = proc.stdout.readline().decode().strip()
        if " blob " not in header:
            continue
        size = int(header.split()[-1])
        out[spec] = proc.stdout.read(size)
        proc.stdout.read(1)
    proc.stdin.close()
    proc.wait()
    return out


def build_index(pairs) -> dict[str, tuple[str, str]]:
    """pre-R0 digest -> (path, current digest) for rename-only files."""
    renamed = r0_rename_map()
    touched = [
        line
        for line in run(["git", "show", "--name-only", "--format=", R0]).stdout.decode().splitlines()
        if line
    ]
    paths = sorted(set(touched) | set(renamed))
    olds = batch_blobs([f"{R0}^:{renamed.get(p, p)}" for p in paths])
    news = batch_blobs([f"origin/main:{p}" for p in paths])
    index: dict[str, tuple[str, str]] = {}
    refused = 0
    for rel in paths:
        old = olds.get(f"{R0}^:{renamed.get(rel, rel)}")
        new = news.get(f"origin/main:{rel}")
        if old is None or new is None or old == new:
            continue
        if not rename_only(old, new, pairs):
            refused += 1
            continue
        index[hashlib.sha256(old).hexdigest()] = (rel, hashlib.sha256(new).hexdigest())
    print(f"index: {len(index)} rename-only files ({refused} refused as content changes)")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        pairs = load_alias_pairs()
    except Exception as exc:  # noqa: BLE001
        print(f"CANNOT_CHECK: alias registry unreadable: {exc}", file=sys.stderr)
        return 2

    index = build_index(pairs)
    total = 0
    for rel in run(["git", "ls-files"]).stdout.decode().splitlines():
        path = ROOT / rel
        if not rel or path.suffix not in TEXT or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # Never rewrite a file's own digest recorded inside itself.
        hits = {h for h in HEX64.findall(text) if h in index and index[h][0] != rel}
        if not hits:
            continue
        for stale in hits:
            text = text.replace(stale, index[stale][1])
        print(f"  {rel}: {len(hits)} pin(s) -> {', '.join(sorted(index[h][0].split('/')[-1] for h in hits))}")
        total += len(hits)
        if args.apply:
            path.write_text(text, encoding="utf-8")
    print(f"\npins={total} apply={args.apply}")
    return 0 if args.apply or total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
