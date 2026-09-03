#!/usr/bin/env python3
"""Build QG48_R2_PARTS_MANIFEST_V1.json — one digest row per R2 sweep part.

Mirrors the QG47 precedent (#2189: aggregates land, raw run-site parts stay at
the run site). Usage:

    python3 qg48_r2_parts_manifest_builder.py --r2-parts-dir QG48_R2_PARTS \
        --outfile QG48_R2_PARTS_MANIFEST_V1.json

Hard-fails (exit 2) unless exactly 1350 parts with unique task_ids 0..1349,
uniform seed 20260903, and uniform letters_sha256 are present, so the manifest
can only be emitted for a complete campaign.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "ORION.QG.QG48.R2PartsManifest.v1"
N_TASKS = 1350
R2_SEED = 20260903


def canon(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--r2-parts-dir", type=Path, required=True)
    ap.add_argument("--outfile", type=Path, required=True)
    args = ap.parse_args()

    files = sorted(args.r2_parts_dir.glob("r2_part_*.json"))
    problems: list[str] = []
    if len(files) != N_TASKS:
        problems.append(f"expected {N_TASKS} parts, found {len(files)}")

    rows: list[dict] = []
    seeds, letters = set(), set()
    for f in files:
        part = json.loads(f.read_text(encoding="utf-8"))
        seeds.add(part.get("seed"))
        letters.add(part.get("letters_sha256"))
        rows.append({
            "file": f"QG48_R2_PARTS/{f.name}",
            "file_sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            "task_id": part["task_id"],
            "arm": part["arm"],
            "objective": part["objective"],
            "ob_idx": part["ob_idx"],
            "n_bits": part["n_bits"],
            "instances": part["instances"],
            "witness_count": part["witness_count"],
            "min_gap": part["min_gap"],
            "part_digest": part["part_digest"],
            "letters_sha256": part["letters_sha256"],
        })

    task_ids = sorted(r["task_id"] for r in rows)
    if task_ids != list(range(N_TASKS)):
        missing = sorted(set(range(N_TASKS)) - set(task_ids))
        dups = len(task_ids) != len(set(task_ids))
        problems.append(f"task_id coverage broken: {len(missing)} missing e.g. {missing[:5]}"
                        + (" + duplicates" if dups else ""))
    if seeds != {R2_SEED}:
        problems.append(f"seed drift: {sorted(seeds)!r}")
    if len(letters) != 1:
        problems.append(f"letters_sha256 not uniform: {len(letters)} values")

    if problems:
        for p in problems:
            print(f"MANIFEST=FAILED {p}")
        return 2

    rows.sort(key=lambda r: r["task_id"])
    manifest = {
        "schema": SCHEMA,
        "generated": "2026-09-03",
        "r2_seed": R2_SEED,
        "letters_sha256_uniform": letters.pop(),
        "manifest_sha256_of_rows": hashlib.sha256(
            canon(rows).encode()).hexdigest(),
        "part_count": len(rows),
        "total_instances": sum(r["instances"] for r in rows),
        "total_witnesses": sum(r["witness_count"] for r in rows),
        "parts": rows,
    }
    args.outfile.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print(f"MANIFEST=WRITTEN {args.outfile} parts={len(rows)} "
          f"witnesses={manifest['total_witnesses']} "
          f"rows_sha={manifest['manifest_sha256_of_rows'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
