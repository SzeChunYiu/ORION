#!/usr/bin/env python3
"""Re-derive the ORION V1 freeze receipt counts and manifest digests from disk.

The freeze terminal must be a derived checker result. Receipt counts and
manifest digests are therefore never hand-edited: they are recomputed from
the ledgers and the on-disk bytes, then verified by check_orion_v1_freeze.py.

This tool recomputes only identity and counts. It never assigns a
disposition, never sets coverage.complete, and never alters a terminal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PKG = Path("research/orion-v1-freeze")
MANIFEST = "V1_FREEZE_MANIFEST_V1.json"
RECEIPT = "V1_BOOTSTRAP_RECEIPT_V1.json"
# Imported, never duplicated: a second copy of this set would silently drift
# from the checker's and the manifest would then bind the wrong file list.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_orion_v1_freeze import FIXED  # noqa: E402


def load(root: Path, name: str) -> dict[str, Any]:
    return json.loads((root / PKG / name).read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def counts(root: Path) -> dict[str, int]:
    comp = load(root, "V1_COMPONENT_GRAPH_V1.json")
    thm = load(root, "V1_THEOREM_AUTHORITY_LEDGER_V1.json")
    iss = load(root, "V1_ISSUE_DISPOSITION_LEDGER_V1.json")
    job = load(root, "V1_EXECUTION_JOB_LEDGER_V1.json")
    gap = load(root, "V1_EXECUTION_GAP_LEDGER_V1.json")
    pap = load(root, "V1_PAPER_CANDIDATE_GATE_V1.json")
    entries = iss["entries"]
    gaps = gap["gaps"]
    return {
        "components": len(comp["nodes"]),
        "theorem_authority_rows": len(thm["entries"]),
        "issues": len(entries),
        "pending_issue_audits": sum(r["disposition"] == "PENDING_ATOMIC_AUDIT" for r in entries),
        "jobs": len(job["jobs"]),
        "gaps": len(gaps),
        "open_internal_gaps": sum(
            g["status"] == "OPEN" and g["class"] == "INTERNAL_LOCAL" for g in gaps
        ),
        "external_blockers": sum(g["class"] != "INTERNAL_LOCAL" for g in gaps),
        "paper_candidates": len(pap["candidates"]),
        "manifest_files": 0,
    }


def manifest(root: Path) -> list[dict[str, Any]]:
    package = {
        p.relative_to(root).as_posix()
        for p in (root / PKG).iterdir()
        if p.is_file() and p.name != MANIFEST
    }
    rows = []
    for rel in sorted(package | FIXED):
        raw = (root / rel).read_bytes()
        rows.append({"bytes": len(raw), "path": rel, "sha256": hashlib.sha256(raw).hexdigest()})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args()
    root = args.root.resolve()

    receipt = load(root, RECEIPT)
    c = counts(root)
    # Manifest is written first so its own digest set is stable, then the
    # receipt count is reconciled against the rows actually written.
    rows = manifest(root)
    c["manifest_files"] = len(rows)
    receipt["counts"] = c
    dump(root / PKG / RECEIPT, receipt)

    rows = manifest(root)  # receipt bytes just changed; re-digest
    man = load(root, MANIFEST)
    man["files"] = rows
    dump(root / PKG / MANIFEST, man)

    print(json.dumps({"counts": c, "manifest_files": len(rows)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
