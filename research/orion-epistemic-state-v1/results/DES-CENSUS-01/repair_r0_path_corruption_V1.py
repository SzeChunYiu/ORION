#!/usr/bin/env python3
"""R0 frozen-manifest path-corruption repair (DES-CENSUS-01 family), 2026-08-27.

Defect: R0 (papers rename wave, receipt `papers/PAPER_RENAME_RECEIPT_V1.json`) blanket-
rewrote path STRINGS inside five frozen DES-CENSUS-01 artifacts while their
`subject_commit`/`subject_tree`/blob oids stayed pinned at the pre-R0 world
(commit 3c97b87f, tree ec9455cc). Result: the frozen records name paths that do
not exist in the tree they claim to have censused.

Repair policy (no re-census, no authority decision):
  * restore each corrupted path string to its pre-R0 form, evidenced by
    (a) inverse of the R0 rewrite (dir renames + archive-root moves), then
    (b) bijection against unclaimed subject-tree paths, each step verified by
    blob-oid equality wherever the record carries an oid;
  * string-exact replacement on the raw JSON text so every other byte is
    preserved;
  * `subject_commit`, `subject_tree`, oids, `freeze_sha256` are NOT touched
    (freeze_sha256 hashes FREEZE_V1.json, which is path-free and unmodified).

Run from the repository root. Writes a repair receipt JSON next to the
artifacts and prints verification counts. Exits non-zero if any invariant
fails. Unrepaired sites (if any) are reported explicitly, never guessed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
FAMILY = REPO / "research/orion-epistemic-state-v1/results"
TARGETS = [
    "DES-CENSUS-01/RAW_MANIFEST_V1.json",
    "DES-CENSUS-01/LABEL_CENSUS_V1.json",
    "DES-CENSUS-01/RESULT_BINDING_PACKET_V1.json",
    "DES-CENSUS-01/UNCLASSIFIED_BLOCKER_ATLAS_V1.json",
    "DES-CENSUS-01/RESOURCE_LEDGER_V1.json",
]
SUBJECT_TREE = "ec9455ccfdded0c2a27c97b425ad001b228151de"
ARCHIVE_ROOTS = ("papers/archive/2026-08-pre-unification/", "archive/2026-08-pre-unification/")


def load_tree(tree: str) -> dict[str, str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-tree", "-r", tree],
        capture_output=True, text=True, check=True,
    ).stdout
    return {line.split("\t", 1)[1]: line.split("\t", 1)[0].split()[2] for line in out.splitlines()}


def reverse_candidates(path: str, rev_dirs: dict[str, str]) -> list[str]:
    """Inverse of the R0 rewrite: archive-root strip and dir un-renames."""
    cands: list[str] = []
    for root in ARCHIVE_ROOTS:
        if path.startswith(root):
            inner = path[len(root):]
            cands += [inner, "papers/" + inner]
    for new, old in rev_dirs.items():
        prefix = f"papers/{new}/"
        if path.startswith(prefix):
            tail = path[len(prefix):]
            cands += [f"papers/{old}/{tail}", f"papers/archive/2026-08-pre-unification/papers/{old}/{tail}"]
    return cands


def main() -> int:
    tree = load_tree(SUBJECT_TREE)
    oid2paths: dict[str, list[str]] = defaultdict(list)
    for p, o in tree.items():
        oid2paths[o].append(p)

    receipt_data = json.loads((REPO / "papers/PAPER_RENAME_RECEIPT_V1.json").read_text())
    rev_dirs = {v: k for k, v in receipt_data["moves"]["simple_renames"].items()}
    for old in receipt_data["moves"]["merged_into_orion_01"]:
        rev_dirs.setdefault("orion-01-certificate-realization", old)

    failures: list[str] = []

    # ---- Phase 1: authoritative mapping from RAW_MANIFEST file_rows (oid-anchored, bijection-closed)
    raw_path = FAMILY / TARGETS[0]
    raw = json.loads(raw_path.read_text())
    rows = raw["file_rows"]
    present = {r["path"] for r in rows if r["path"] in tree}
    missing = [r for r in rows if r["path"] not in tree]
    unclaimed = {p for p in tree if p not in present}

    mapping: dict[str, str] = {}
    stats = {"transform": 0, "bijection": 0}
    for r in missing:
        cands = [c for c in reverse_candidates(r["path"], rev_dirs) if tree.get(c) == r["oid"]]
        if len(cands) == 1:
            mapping[r["path"]] = cands[0]
            stats["transform"] += 1
            continue
        free = sorted(p for p in unclaimed if tree[p] == r["oid"] and p not in mapping.values())
        if len(free) == 1:
            mapping[r["path"]] = free[0]
            stats["bijection"] += 1
        else:
            failures.append(f"RAW unresolved: {r['path']} oid={r['oid']} free={free}")
    leftover = unclaimed - set(mapping.values())
    if leftover:
        failures.append(f"bijection incomplete, {len(leftover)} tree paths unassigned: {sorted(leftover)[:5]}")
    print(f"[RAW] missing={len(missing)} transform={stats['transform']} bijection={stats['bijection']} unresolved={len(missing)-len(mapping)}")

    # ---- Phase 2: apply string-exact repairs across all five files
    report = {}
    for rel in TARGETS:
        fp = FAMILY / rel
        text = fp.read_text()
        data = json.loads(text)

        # collect corrupted path strings in this file (papers/-rooted, absent from subject tree)
        corrupt: set[str] = set()
        def scan(o):
            if isinstance(o, dict):
                for v in o.values(): scan(v)
            elif isinstance(o, list):
                for v in o: scan(v)
            elif isinstance(o, str) and o.startswith("papers/") and o not in tree:
                corrupt.add(o)
        scan(data)

        local_map: dict[str, str] = {}
        unresolved_local: list[str] = []
        for c in sorted(corrupt):
            if c in mapping:
                local_map[c] = mapping[c]
                continue
            cands = [x for x in reverse_candidates(c, rev_dirs) if x in tree]
            if len(cands) == 1:
                local_map[c] = cands[0]
            else:
                unresolved_local.append(c)
        new_text = text
        sites = 0
        for old, new in sorted(local_map.items()):
            tok_old, tok_new = json.dumps(old), json.dumps(new)
            n = new_text.count(tok_old)
            if n == 0:
                failures.append(f"{rel}: token absent after prior edits: {old}")
                continue
            new_text = new_text.replace(tok_old, tok_new)
            sites += n

        # verify: parses, deep-equal modulo mapped paths, no other bytes differ
        new_data = json.loads(new_text)
        diffs = []

        def diff(a, b, p="$"):
            if isinstance(a, dict) and isinstance(b, dict):
                if set(a) != set(b): diffs.append(f"{p}: keyset")
                for k in a:
                    if k in b: diff(a[k], b[k], f"{p}.{k}")
            elif isinstance(a, list) and isinstance(b, list):
                if len(a) != len(b): diffs.append(f"{p}: len")
                for i, (x, y) in enumerate(zip(a, b)): diff(x, y, f"{p}[{i}]")
            elif a != b:
                if not (isinstance(a, str) and a in local_map and local_map[a] == b):
                    diffs.append(f"{p}: {a!r} -> {b!r}")

        diff(data, new_data)
        if diffs:
            failures.append(f"{rel}: unexpected structural diffs: {diffs[:3]}")

        # post-repair: no papers/ string outside the subject tree remains (except unresolved)
        residue = []

        def rescan(o):
            if isinstance(o, dict):
                for v in o.values(): rescan(v)
            elif isinstance(o, list):
                for v in o: rescan(v)
            elif isinstance(o, str) and o.startswith("papers/") and o not in tree:
                residue.append(o)
        rescan(new_data)
        residue = sorted(set(residue) - set(unresolved_local))
        if residue:
            failures.append(f"{rel}: post-repair residue {residue[:3]}")

        if sites:
            fp.write_text(new_text)
        report[rel] = {
            "unique_corrupted_strings": len(corrupt),
            "repaired_strings": len(local_map),
            "replacement_sites": sites,
            "unresolved_strings": unresolved_local,
        }
        print(f"[{rel}] corrupt={len(corrupt)} repaired={len(local_map)} sites={sites} unresolved={len(unresolved_local)}")
        for u in unresolved_local[:5]:
            print(f"    UNRESOLVED: {u}")

    # ---- RAW-specific final invariants
    raw2 = json.loads(raw_path.read_text())
    bad_path = [r["path"] for r in raw2["file_rows"] if r["path"] not in tree]
    bad_oid = [r["path"] for r in raw2["file_rows"] if tree.get(r["path"]) != r["oid"]]
    fr = raw2["occurrence_rows"]["file_refs"]
    rowmap = {r["oid"]: r["path"] for r in raw2["file_rows"]}
    fr_bad = [(p, o) for p, o in fr if rowmap.get(o) != p]
    print(f"[RAW invariants] paths-not-in-tree={len(bad_path)} oid-mismatch={len(bad_oid)} file_ref-mismatch={len(fr_bad)}")
    if bad_path: failures.append(f"RAW: {len(bad_path)} paths still outside subject tree")
    if bad_oid: failures.append(f"RAW: {len(bad_oid)} oid mismatches after repair")
    if fr_bad: failures.append(f"RAW: {len(fr_bad)} file_refs disagree with file_rows")

    # ---- receipt
    receipt = {
        "schema": "orion.dynamic-epistemic-state.des-census.r0-path-repair-receipt.v1",
        "date": "2026-08-27",
        "defect": "R0 rename wave rewrote path strings inside five frozen DES-CENSUS-01 artifacts whose subject_commit/subject_tree/oids remained pre-R0",
        "subject_commit": raw["subject_commit"],
        "subject_tree": SUBJECT_TREE,
        "policy": [
            "no re-census; paths restored from the entries' own evidence only",
            "inverse-R0 transform verified by blob-oid where the record carries one",
            "bijection fallback: each census row maps to exactly one subject-tree path",
            "string-exact raw-text replacement; all non-path bytes preserved",
            "subject_commit, subject_tree, oids, freeze_sha256 untouched",
        ],
        "resolution_counts": {"transform": stats["transform"], "bijection": stats["bijection"]},
        "files": report,
        "mapping": {k: v for k, v in sorted(mapping.items())},
        "failures": failures,
    }
    out = FAMILY / "DES-CENSUS-01/R0_PATH_REPAIR_RECEIPT_V1.json"
    out.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print(f"\nreceipt -> {out.relative_to(REPO)}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:10]:
            print("  -", f)
        return 1
    print("ALL INVARIANTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
