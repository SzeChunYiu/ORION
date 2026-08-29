#!/usr/bin/env python3
"""Re-seal SHA-256 bindings that Wave R0's renames invalidated.

Wave R0 (``3a1a83178``, PR #1474) executed the operator's naming-unification
directive across 3658 files.  Hundreds of receipts, manifests, checkers and
protocols record the SHA-256 of files R0 rewrote, and R0 regenerated pins only
for ``orion-16..25``.  Every other binding still names a pre-R0 digest, and
those stale bindings fail closed *before* the surrounding test reaches the
assertion it actually makes -- which is why one stale constant could account
for 22 failures in a single file.

Rather than guess which hex strings are pins, this works from proof:

1. Hash every file's **pre-R0** bytes.  A 64-hex string in the tree is treated
   as a stale pin only when it equals the pre-R0 digest of a file that exists.
2. Gate that file: applying the alias registry to its pre-R0 bytes must
   reproduce its committed bytes exactly.  Rename-only, or it is refused.
3. Replace the stale digest with the file's current digest.

Steps 1-3 repeat to a fixpoint, because re-sealing a file changes its own
digest and so invalidates pins that bind *it* -- these lanes nest several
layers deep.

A file that fails the gate is never re-sealed.  Renaming a path cannot change
a result; re-pinning a file whose content genuinely changed would launder one.

Exit codes
----------
0  clean, or --apply reached a fixpoint
1  stale bindings remain (report mode)
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
MAX_PASSES = 12
SKIP_SUFFIXES = {".png", ".pdf", ".jpg", ".jpeg", ".gz", ".zip", ".ico", ".woff", ".woff2"}

sys.path.insert(0, str(ROOT / "scripts"))
from repin_r0_renamed_digests import (  # noqa: E402
    load_alias_pairs,
    pre_r0_bytes,
    r0_rename_map,
    rename_only,
    run,
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tracked() -> list[str]:
    return [p for p in run(["git", "ls-files"]).stdout.decode().splitlines() if p]


def build_stale_index(pairs) -> dict[str, tuple[str, str]]:
    """pre-R0 digest -> (path, current digest), for rename-only files only."""
    index: dict[str, tuple[str, str]] = {}
    renamed_from = r0_rename_map()
    touched = {
        line
        for line in run(
            ["git", "show", "--name-only", "--format=", R0]
        ).stdout.decode().splitlines()
        if line
    }
    touched |= set(renamed_from)
    refused = 0
    for rel in sorted(touched):
        target = ROOT / rel
        if not target.is_file() or target.suffix in SKIP_SUFFIXES:
            continue
        old = pre_r0_bytes(rel)
        if old is None:
            continue
        committed = run(["git", "show", f"origin/main:{rel}"]).stdout
        if not committed:
            continue
        if not rename_only(old, committed, pairs):
            refused += 1
            continue
        old_digest = sha(old)
        new_digest = sha(target.read_bytes())
        if old_digest != new_digest:
            index[old_digest] = (rel, new_digest)
    print(f"index: {len(index)} rename-only files with drifted digests "
          f"({refused} refused as content changes)")
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

    files = [
        rel
        for rel in tracked()
        if Path(rel).suffix not in SKIP_SUFFIXES and (ROOT / rel).is_file()
    ]

    total = 0
    for attempt in range(1, MAX_PASSES + 1):
        index = build_stale_index(pairs)
        if not index:
            break
        changed = 0
        for rel in files:
            path = ROOT / rel
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            found = {h for h in HEX64.findall(text) if h in index}
            # Never rewrite a file's own recorded digest inside itself.
            found = {h for h in found if index[h][0] != rel}
            if not found:
                continue
            for stale in found:
                text = text.replace(stale, index[stale][1])
            changed += 1
            total += len(found)
            print(f"  pass {attempt}: {rel} ({len(found)} pin(s))")
            if args.apply:
                path.write_text(text, encoding="utf-8")
        if not args.apply or changed == 0:
            break
    print(f"\nbindings={total} apply={args.apply}")
    return 0 if args.apply or total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
