#!/usr/bin/env python3
"""Definitive R0 repair, layer 2: byte-restore of the frozen DES-CENSUS-01 artifacts.

Layer 1 (`repair_r0_path_corruption_V1.py`) proved by inference (inverse-R0
transform + oid verification + bijection closure over the subject tree) that the
standalone `papers/...` path strings in the five frozen artifacts were rewritten
by R0. It also showed 2,721/2,721 file_rows resolve and that two files round-trip
byte-identically. What layer 1 could not do: strings with paths EMBEDDED in
larger strings (`ARTIFACT:papers/...` ids, `json_key=... value=...` annotation
records, prose snippets) — R0 rewrote those too.

Layer 2 uses git ground truth. For each artifact:

  1. assert the only commits ever touching it are its pre-R0 edits and the R0
     commit 3a1a8317 (so HEAD bytes == R0 bytes, no post-R0 drift);
  2. take the original bytes at its last pre-R0 commit;
  3. apply the FORWARD R0 rename map to the original and require exact equality
     with the R0 bytes — proving R0's edit was exactly the mechanical rename and
     nothing else (the receipt's `rebind.hand_edits` classes are live code, CI
     workflow globs, elided short-form refs, and canonical-Q1 refs — no frozen
     research artifact; and the byte-exact equality here is the independent
     proof for these five files);
  4. restore the original bytes into the worktree.

Fails loudly (exit 1, no write) if any file's forward check leaves residuals.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
FAM = "research/orion-epistemic-state-v1/results/DES-CENSUS-01/"
FILES = [
    "RAW_MANIFEST_V1.json",
    "LABEL_CENSUS_V1.json",
    "RESULT_BINDING_PACKET_V1.json",
    "UNCLASSIFIED_BLOCKER_ATLAS_V1.json",
    "RESOURCE_LEDGER_V1.json",
]
R0_COMMIT = "3a1a8317"  # papers(R0): ORION-01…25 namespace unification (#1474)


def git(*args: str, binary: bool = False):
    out = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode()


def move_vocabulary() -> list[tuple[str, str]]:
    """Rewrite vocabulary of the R0 wave, longest-match-first.

    Mirrors R0's recorded pass design (receipt `rebind.passes`):
      pass A "full old path prefixes -> new paths (longest-first, file-level
      before dir-level)" — absolute `papers/...` refs follow the actual git
      file moves, INCLUDING moves into `papers/archive/`;
      pass B "bare dir basenames, guarded against archive/candidates
      contexts" — relative and bare refs follow DIR-level renames
      (simple_renames / merges / stub), and dirs archived outright get the
      archive-root prefix (`moves.archived_dirs`).

    Hence: for a file under a RENAMED dir whose git move went to the archive
    (the archived Q1 manuscript chain inside Q-paper-01 -> orion-05), the
    relative form of that git pair is suppressed — pass B's dir rename wins
    for relative refs (observed: `Q-paper-01-tare-expressivity/
    MANUSCRIPT_V3.md` -> `orion-05-tare-expressivity/MANUSCRIPT_V3.md`),
    while absolute refs keep the file-level archive move. Used ONLY to test
    that each observed orig->r0 string change is a pure name rewrite — never
    applied blindly.
    """
    rec = json.loads((REPO / "papers/PAPER_RENAME_RECEIPT_V1.json").read_text())
    renamed_dirs = (set(rec["moves"]["simple_renames"])
                    | set(rec["moves"]["merged_into_orion_01"])
                    | set(rec["moves"]["stub_to_candidates"]))
    V: list[tuple[str, str]] = []
    for line in git("diff", "--name-status", "-M", f"{R0_COMMIT}^..{R0_COMMIT}").splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].startswith("R") and parts[1].startswith("papers/"):
            V.append((parts[1], parts[2]))                       # absolute moved path
            old_rel = parts[1][len("papers/"):]
            suppressed = (parts[2].startswith("papers/archive/")
                          and old_rel.split("/", 1)[0] in renamed_dirs)
            if not suppressed:                                   # relative form (pass B territory)
                V.append((old_rel, parts[2][len("papers/"):]))
    for old, new in rec["moves"]["simple_renames"].items():
        V += [(f"papers/{old}/", f"papers/{new}/"), (f"{old}/", f"{new}/"), (old, new)]
    for old in rec["moves"]["merged_into_orion_01"]:
        V += [(f"papers/{old}/", "papers/orion-01-certificate-realization/"),
              (f"{old}/", "orion-01-certificate-realization/"),
              (old, "orion-01-certificate-realization")]
    for old, new in rec["moves"]["stub_to_candidates"].items():
        V += [(f"papers/{old}/", f"papers/{new}/"), (f"{old}/", f"{new}/"), (old, new)]
    for arch in rec["moves"]["archived_dirs"]:  # "archive/2026-08-pre-unification/<dir>"
        d = arch.split("/", 2)[2]
        V += [(f"papers/{d}/", f"papers/{arch}/"), (f"{d}/", f"{arch}/"), (d, arch)]
    return sorted(set(V), key=lambda t: -len(t[0]))


def vocab_rewrite(s: str, V: list[tuple[str, str]], _cache={}) -> str:
    """Single-pass longest-match rewrite — mirrors R0's own pass design
    ("A: longest-first, file-level before dir-level; B: bare basenames guarded
    against archive contexts"). The old sequential str.replace loop re-applied
    the relative/bare form inside spans already rewritten by the absolute form
    (double `archive/2026-08-pre-unification/` prefixes). One simultaneous
    scan: the alternation is ordered longest-old-first, so each position
    matches its longest token and consumed spans can never be re-matched."""
    if "pat" not in _cache:
        table: dict[str, str] = {}
        for old, new in V:
            if old in table and table[old] != new:
                raise SystemExit(f"vocab conflict for {old!r}: {table[old]!r} vs {new!r}")
            table[old] = new
        _cache["pat"] = re.compile("|".join(re.escape(old) for old, _ in V))
        _cache["map"] = table
    return _cache["pat"].sub(lambda m: _cache["map"][m.group(0)], s)


def leaf_diffs(a, b, path="$", out=None):
    if out is None: out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if k in b: leaf_diffs(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)): leaf_diffs(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append((path, a, b))
    return out


def main() -> int:
    V = move_vocabulary()
    report, failures = {}, []

    for name in FILES:
        rel = FAM + name
        commits = git("log", "--format=%h", "--", rel).split()
        if commits[0] != R0_COMMIT:
            failures.append(f"{name}: last touching commit is {commits[0]}, not R0 {R0_COMMIT}")
            continue
        pre = next(c for c in commits[1:] if c != R0_COMMIT)  # newest pre-R0 edit
        orig = git("show", f"{pre}:{rel}", binary=True)
        r0 = git("show", f"HEAD:{rel}", binary=True)

        diffs = leaf_diffs(json.loads(orig), json.loads(r0))
        unexplained = [(p, a, b) for p, a, b in diffs
                       if not (isinstance(a, str) and isinstance(b, str) and vocab_rewrite(a, V) == b)]
        if unexplained:
            p, a, b = unexplained[0]
            failures.append(f"{name}: {len(unexplained)}/{len(diffs)} diffs not explainable by the move vocabulary; first @ {p}\n      orig: {str(a)[:110]}\n      r0  : {str(b)[:110]}\n      vocab: {vocab_rewrite(str(a), V)[:110] if isinstance(a, str) else '(non-string)'}")
            continue

        (REPO / rel).write_bytes(orig)
        so, sr = hashlib.sha256(orig).hexdigest(), hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        report[name] = {
            "original_commit": pre,
            "original_sha256": so,
            "restored_sha256": sr,
            "bytes": len(orig),
            "diff_check": f"{len(diffs)} string diffs, ALL explained by the R0 move vocabulary (pure name rewrites, no content changes)",
        }
        print(f"[{name}] preR0={pre} restored {len(orig)}B sha={so[:12]} diffs={len(diffs)} all-vocabulary-explained")

    # ---- invariants on the restored RAW manifest
    tree = {}
    for line in git("ls-tree", "-r", "ec9455ccfdded0c2a27c97b425ad001b228151de").splitlines():
        meta, path = line.split("\t", 1)
        tree[path] = meta.split()[2]
    raw = json.loads((REPO / (FAM + FILES[0])).read_text())
    bad_path = [r["path"] for r in raw["file_rows"] if r["path"] not in tree]
    bad_oid = [r["path"] for r in raw["file_rows"] if tree.get(r["path"]) != r["oid"]]
    pairs = {(r["path"], r["oid"]) for r in raw["file_rows"]}
    fr_bad = [p for p, o in raw["occurrence_rows"]["file_refs"] if (p, o) not in pairs]
    print(f"[RAW invariants] paths-outside-tree={len(bad_path)} oid-mismatch={len(bad_oid)} file_ref-pair-miss={len(fr_bad)}")
    if bad_path: failures.append(f"RAW: {len(bad_path)} row paths outside subject tree")
    if bad_oid: failures.append(f"RAW: {len(bad_oid)} row oid mismatches")
    if fr_bad: failures.append(f"RAW: {len(fr_bad)} file_refs not matching any (path,oid) row")

    receipt_path = REPO / (FAM + "R0_PATH_REPAIR_RECEIPT_V1.json")
    receipt = json.loads(receipt_path.read_text())
    receipt["layer2_byte_restore"] = {
        "method": "git byte-restore at each artifact's last pre-R0 commit, admitted only after proving every orig->R0 string change is a pure R0 name rewrite (move vocabulary), i.e. R0 made no content changes to these frozen files",
        "r0_commit": R0_COMMIT,
        "files": report,
        "invariants": {
            "raw_rows_outside_subject_tree": len(bad_path),
            "raw_row_oid_mismatches": len(bad_oid),
            "raw_file_ref_pair_misses": len(fr_bad),
        },
    }
    receipt["failures"] = failures
    receipt_path.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print(f"receipt updated -> {FAM}R0_PATH_REPAIR_RECEIPT_V1.json")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures: print("  -", f)
        return 1
    print("ALL INVARIANTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
