#!/usr/bin/env python3
"""Build data, notebooks, figures, dashboard, and deterministic output manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "visualization/scripts"
AUTHORITY_BOUNDARY = "REPOSITORY_RECEIPTS_ONLY__NO_EXTERNAL_AUTHORITY_DELTA"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def run(*args: str) -> None:
    environment = os.environ.copy()
    source = str(ROOT / "visualization/src")
    environment["PYTHONPATH"] = source + os.pathsep + environment.get("PYTHONPATH", "")
    subprocess.run([sys.executable, *args], cwd=ROOT, env=environment, check=True)


def build(output_root: Path) -> Path:
    atlas = output_root / "data/derived/atlas.json"
    source_manifest = output_root / "data/manifests/source_manifest.json"
    notebooks = output_root / "notebooks"
    dashboard = output_root / "figures/interactive/evidence_atlas.html"
    run(
        str(SCRIPTS / "build_data.py"),
        "--root",
        str(ROOT),
        "--atlas",
        str(atlas),
        "--manifest",
        str(source_manifest),
    )
    run(str(SCRIPTS / "make_notebooks.py"), "--output-dir", str(notebooks))
    run(str(SCRIPTS / "render_all.py"), "--atlas", str(atlas), "--output-root", str(output_root))
    run(str(SCRIPTS / "build_dashboard.py"), "--atlas", str(atlas), "--output", str(dashboard))

    manifest_path = output_root / "generated/manifests/output_manifest.json"
    candidates = [
        *sorted((output_root / "data").rglob("*.json")),
        *sorted((output_root / "figures").rglob("*")),
        *sorted(notebooks.glob("*.ipynb")),
    ]
    files = [path for path in candidates if path.is_file() and path != manifest_path]
    manifest = {
        "schema": "orion.visualization.output-manifest.v1",
        "authority_boundary": AUTHORITY_BOUNDARY,
        "file_count": len(files),
        "files": [
            {
                "path": path.relative_to(output_root).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in sorted(files)
        ],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT / "visualization")
    args = parser.parse_args()
    manifest = build(args.output_root.resolve())
    print(manifest)
    print(f"SCIENTIFIC_AUTHORITY={AUTHORITY_BOUNDARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
