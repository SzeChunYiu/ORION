#!/usr/bin/env python3
"""Enumerate surviving references to the pre-R0 paper namespace.

Wave R0 (commit 3a1a83178, PR #1474) executed the operator's naming-unification
directive: 2734 git renames onto one flat ``ORION-NN`` series, with a separate
content-rebind pass over 11162 text files.  The rebind pass reached manuscript
prose but missed harness registries, test expectations and several manifests,
which is why ``fast (all but p2)`` has been red on main ever since.

This script drives those repairs from data instead of one-off greps.  It reads
the machine-readable alias registry that R0 itself shipped
(``papers/PAPER_ALIASES.md``) and reports every file that still names a
pre-R0 identifier or directory.

Measured scope, main @ b1e65d444
--------------------------------
178 files still name the pre-R0 namespace.  Cross-checked against the 61 test
files failing in ``fast (all but p2)``, the two sets overlap in **4** files.
Surviving old names are therefore a real but *minor* contributor to the red
suite; the dominant failure shapes are digest and content bindings against
artifacts that R0 rewrote without re-pinning.  Do not read a clean run of this
script as a green suite -- it checks naming only.

Exit codes
----------
0  no residual references (or --report)
1  residual references found
2  the alias registry could not be read -- CANNOT_CHECK, distinct from "clean"
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "papers" / "PAPER_ALIASES.md"

# Files that are *supposed* to name the old namespace: the registry and receipt
# themselves, and everything under the pre-unification archive.
EXCLUDED_PREFIXES = (
    "papers/archive/",
    "development/",
)
EXCLUDED_FILES = {
    "papers/PAPER_ALIASES.md",
    "papers/PAPER_RENAME_RECEIPT_V1.json",
    "papers/PAPER_PORTFOLIO_REFACTOR_PLAN_V1.md",
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".cfg", ".toml"}


def load_registry() -> dict:
    if not REGISTRY.is_file():
        raise FileNotFoundError(REGISTRY)
    block = re.search(r"```yaml\n(.*?)```", REGISTRY.read_text(encoding="utf-8"), re.S)
    if block is None:
        raise ValueError("no yaml block in alias registry")
    import yaml  # imported late so --help works without the dependency

    return yaml.safe_load(block.group(1))


def build_patterns(registry: dict) -> dict[str, re.Pattern[str]]:
    """One compiled pattern per retired name, keyed by ``old -> new``."""
    patterns: dict[str, re.Pattern[str]] = {}
    retained = set(registry.get("retained_outside_series") or ())

    for entry in registry.get("dir_aliases") or ():
        old, new = entry["old_dir"], entry["new_dir"]
        if old in retained:
            continue
        patterns[f"{old} -> {new}"] = re.compile(re.escape(old))

    # Bare ids (``P1``, ``Q1``, ``NQ``) are NOT scanned.  They collide with study
    # lane names, probability symbols and workflow filenames: a bare-id sweep
    # flags 2099 files, of which a sampled check found the overwhelming majority
    # to be unrelated.  Only the double-prefix artefact ``ORION-<old-id>`` is
    # unambiguous -- it can only have been produced by prefixing the new series
    # onto a name that still carried the retired id.
    for entry in registry.get("id_aliases") or ():
        old, new_id = entry["old"], entry["new"]
        if not re.fullmatch(r"(P|Q|QG)\d+", old):
            continue
        patterns[f"ORION-{old} -> {new_id}"] = re.compile(
            rf"ORION-{re.escape(old)}(?![\w-])"
        )

    return patterns


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line]


def scan(patterns: dict[str, re.Pattern[str]]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for rel in tracked_files():
        if rel in EXCLUDED_FILES or rel.startswith(EXCLUDED_PREFIXES):
            continue
        if Path(rel).suffix not in TEXT_SUFFIXES:
            continue
        path = ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hits = [label for label, pattern in patterns.items() if pattern.search(text)]
        if hits:
            findings[rel] = sorted(hits)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument(
        "--report", action="store_true", help="always exit 0 (inventory mode)"
    )
    args = parser.parse_args()

    try:
        registry = load_registry()
    except Exception as exc:  # noqa: BLE001 - CANNOT_CHECK must stay distinct
        print(f"CANNOT_CHECK: alias registry unreadable: {exc}", file=sys.stderr)
        return 2

    findings = scan(build_patterns(registry))

    if args.json:
        print(json.dumps(findings, indent=2, sort_keys=True))
    else:
        print(f"files still naming the pre-R0 namespace: {len(findings)}")
        by_alias: dict[str, int] = {}
        for hits in findings.values():
            for hit in hits:
                by_alias[hit] = by_alias.get(hit, 0) + 1
        for alias, count in sorted(by_alias.items(), key=lambda kv: -kv[1]):
            print(f"  {count:4d}  {alias}")

    if args.report:
        return 0
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
