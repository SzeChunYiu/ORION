#!/usr/bin/env python3
"""Re-pin digests that drifted because Wave R0 renamed paths inside an artifact.

Wave R0 (``3a1a83178``, PR #1474) executed the operator's naming-unification
directive.  It regenerated digest pins for ``orion-16..25`` but not for the many
receipts, protocols and corpora elsewhere in the tree that record the SHA-256 of
files R0 rewrote.  Those bindings now report drift, and the drift masks the
assertions the surrounding tests actually make.

Re-pinning a digest is only safe when the underlying file changed by *renaming
alone*.  This script proves that before it writes anything:

1. Locate the file's pre-R0 blob, following R0's own renames.
2. Apply the alias registry (``papers/PAPER_ALIASES.md``) to the pre-R0 bytes.
3. Require that every differing line is accounted for by a rename.

Any file with a surviving non-rename difference is **REFUSED**, never re-pinned.
A refusal means the content changed scientifically and a human must look at it.
Renaming a path never changes a result; silently re-pinning a changed result
would launder one.

Exit codes
----------
0  nothing to do, or --apply completed with no refusals
1  drifted bindings remain (report mode), or a refusal blocked --apply
2  the alias registry could not be read -- CANNOT_CHECK, distinct from clean
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R0 = "3a1a83178"
REGISTRY = ROOT / "papers" / "PAPER_ALIASES.md"
HEX64 = re.compile(r"\A[0-9a-f]{64}\Z")
DIGEST_KEYS = ("sha256", "digest", "hash", "sha_256")
PATH_KEYS = ("path", "artifact", "file", "protocol_doc", "checker")


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=ROOT, capture_output=True)


def load_alias_pairs() -> list[tuple[str, str]]:
    block = re.search(r"```yaml\n(.*?)```", REGISTRY.read_text(encoding="utf-8"), re.S)
    if block is None:
        raise ValueError("no yaml block in alias registry")
    import yaml

    registry = yaml.safe_load(block.group(1))
    pairs: list[tuple[str, str]] = []
    for entry in registry.get("dir_aliases") or ():
        pairs.append((entry["old_dir"], entry["new_dir"]))
    for entry in registry.get("file_aliases") or ():
        pairs.append((entry["old"], entry["new"]))
    # Longest first: 'paper-06-formal-...' must win over any shorter prefix.
    pairs.sort(key=lambda kv: -len(kv[0]))
    return pairs


_RENAME_MAP: dict[str, str] | None = None


def r0_rename_map() -> dict[str, str]:
    """R0's own new-path -> old-path map, computed once.

    Asking git for a single path's rename does not work here: filtering the
    diff by the *new* path hides the old one, so the rename is never reported
    and every renamed artifact would be refused as if its content had changed.
    """
    global _RENAME_MAP
    if _RENAME_MAP is None:
        proc = run(["git", "diff", "--find-renames", "--name-status", f"{R0}^", R0])
        mapping: dict[str, str] = {}
        for line in proc.stdout.decode("utf-8", "replace").splitlines():
            parts = line.split("\t")
            if parts and parts[0].startswith("R") and len(parts) == 3:
                mapping[parts[2]] = parts[1]
        _RENAME_MAP = mapping
    return _RENAME_MAP


def pre_r0_bytes(rel: str) -> bytes | None:
    """The file's content immediately before R0, following R0's renames."""
    proc = run(["git", "show", f"{R0}^:{rel}"])
    if proc.returncode == 0:
        return proc.stdout
    source = r0_rename_map().get(rel)
    if source is None:
        return None
    proc = run(["git", "show", f"{R0}^:{source}"])
    return proc.stdout if proc.returncode == 0 else None


def rename_only(old: bytes, new: bytes, pairs: list[tuple[str, str]]) -> bool:
    """True when `new` is reachable from `old` by alias renames alone."""
    try:
        old_text = old.decode("utf-8")
        new_text = new.decode("utf-8")
    except UnicodeDecodeError:
        return False
    if old_text == new_text:
        return True

    def _collapse(text: str) -> str:
        for old_name, new_name in pairs:
            text = text.replace(old_name, new_name)
        return re.sub(r"(?:ORION-)+(ORION-\d+)", r"\1", text)

    # Fast path: whole-file rename equality. Only fall back to the line-by-line
    # comparison when this fails -- difflib over every R0-touched file is minutes.
    if _collapse(old_text) == _collapse(new_text):
        return True

    import difflib

    changed_old: list[str] = []
    changed_new: list[str] = []
    for line in difflib.unified_diff(
        old_text.splitlines(), new_text.splitlines(), lineterm="", n=0
    ):
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("-"):
            changed_old.append(line[1:])
        elif line.startswith("+"):
            changed_new.append(line[1:])
    if len(changed_old) != len(changed_new):
        return False
    # The whole-file fast path above already accepts anything a rename explains.
    # Reaching here with a large diff means the collapse did not reconcile it,
    # and comparing thousands of lines through 70 replacements each is slow for
    # an answer that is almost certainly "refuse". Refusing is the safe
    # direction, so cap it rather than grind.
    if len(changed_old) > 200:
        return False

    def collapse(text: str) -> str:
        for old_name, new_name in pairs:
            text = text.replace(old_name, new_name)
        # R0's own rebind produced no ORION-ORION-NN; normalise so the double
        # prefix a naive replace can create never counts as a difference.
        return re.sub(r"(?:ORION-)+(ORION-\d+)", r"\1", text)

    return all(collapse(a) == collapse(b) for a, b in zip(changed_old, changed_new))


def iter_bindings(node, out: list):
    """Yield (container, digest_key, path) for every path-to-digest binding."""
    if isinstance(node, dict):
        path_value = next(
            (node[k] for k in PATH_KEYS if isinstance(node.get(k), str)), None
        )
        for key, value in node.items():
            if isinstance(value, str) and HEX64.match(value):
                if key in DIGEST_KEYS and path_value:
                    out.append((node, key, path_value))
                elif "/" in key:
                    out.append((node, key, key))
        for value in node.values():
            iter_bindings(value, out)
    elif isinstance(node, list):
        for item in node:
            iter_bindings(item, out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the re-pins")
    parser.add_argument("paths", nargs="*", help="JSON files to check (default: all tracked)")
    args = parser.parse_args()

    try:
        pairs = load_alias_pairs()
    except Exception as exc:  # noqa: BLE001 - CANNOT_CHECK must stay distinct
        print(f"CANNOT_CHECK: alias registry unreadable: {exc}", file=sys.stderr)
        return 2

    if args.paths:
        targets = args.paths
    else:
        listed = run(["git", "ls-files", "*.json"]).stdout.decode()
        targets = [line for line in listed.splitlines() if line]

    import hashlib

    repinned = refused = 0
    for rel in targets:
        source = ROOT / rel
        try:
            document = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        bindings: list = []
        iter_bindings(document, bindings)
        dirty = False
        for container, digest_key, bound_path in bindings:
            target = ROOT / bound_path
            if not target.is_file():
                continue
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual == container[digest_key]:
                continue
            old = pre_r0_bytes(bound_path)
            if old is None or not rename_only(old, target.read_bytes(), pairs):
                refused += 1
                print(f"REFUSED  {rel}\n         -> {bound_path} (not a pure rename)")
                continue
            print(f"REPIN    {rel}\n         -> {bound_path}")
            repinned += 1
            if args.apply:
                stale = container[digest_key]
                text = source.read_text(encoding="utf-8")
                # Surgical: swap the digest string in place.  Rewriting the
                # document with json.dumps would reflow formatting across the
                # whole file, changing bytes nothing asked to change -- and
                # these files are themselves digest-bound elsewhere.
                if text.count(stale) != 1:
                    print(f"         SKIP: digest appears {text.count(stale)}x, not 1")
                    continue
                source.write_text(text.replace(stale, actual), encoding="utf-8")
                dirty = True
        _ = dirty

    print(f"\nrepinned={repinned} refused={refused} apply={args.apply}")
    if refused:
        return 1
    return 0 if args.apply or not repinned else 1


if __name__ == "__main__":
    raise SystemExit(main())
