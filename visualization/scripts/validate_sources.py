#!/usr/bin/env python3
"""Read-only validation of visualization source bindings.

Exit 0 = CHECKED, 2 = DRIFT, 3 = CANNOT_CHECK (registered source absent).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def validate(root: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = []
    overall = "CHECKED"
    for source in manifest["sources"]:
        path = root / source["path"]
        if not path.is_file():
            state = "CANNOT_CHECK"
            actual = None
            overall = "CANNOT_CHECK"
        else:
            actual = sha256(path)
            state = "CHECKED" if actual == source["sha256"] else "DRIFT"
            if state == "DRIFT" and overall != "CANNOT_CHECK":
                overall = "DRIFT"
        rows.append(
            {
                "id": source["id"],
                "path": source["path"],
                "state": state,
                "expected_sha256": source["sha256"],
                "actual_sha256": actual,
            }
        )
    catalog = root / "visualization/source_catalog.json"
    catalog_actual = sha256(catalog) if catalog.is_file() else None
    if catalog_actual is None:
        catalog_state = "CANNOT_CHECK"
        overall = "CANNOT_CHECK"
    elif catalog_actual != manifest["source_catalog_sha256"]:
        catalog_state = "DRIFT"
        if overall != "CANNOT_CHECK":
            overall = "DRIFT"
    else:
        catalog_state = "CHECKED"
    return {
        "schema": "orion.visualization.source-validation.v1",
        "overall": overall,
        "source_catalog": {
            "state": catalog_state,
            "actual_sha256": catalog_actual,
            "expected_sha256": manifest["source_catalog_sha256"],
        },
        "sources": rows,
        "authority_delta": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "visualization/data/manifests/source_manifest.json"
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(args.root.resolve(), args.manifest.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["overall"])
        for row in result["sources"]:
            if row["state"] != "CHECKED":
                print(f"{row['state']} {row['path']}")
        print("SCIENTIFIC_AUTHORITY=UNCHANGED_BY_SOURCE_VALIDATION")
    return {"CHECKED": 0, "DRIFT": 2, "CANNOT_CHECK": 3}[result["overall"]]


if __name__ == "__main__":
    raise SystemExit(main())
