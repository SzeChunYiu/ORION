#!/usr/bin/env python3
"""Execute ordinary Python notebook cells offline without a Jupyter dependency."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NETWORK_PATTERN = re.compile(r"\b(requests|urllib|httpx|aiohttp|socket)\b|https?://")


def execute(path: Path, visualization_root: Path) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__notebook__"}
    previous = Path.cwd()
    try:
        os.environ["MPLBACKEND"] = "Agg"
        os.chdir(visualization_root)
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell.get("source", []))
            if NETWORK_PATTERN.search(source):
                raise RuntimeError(f"network-capable source in {path.name} cell {index}")
            compiled = compile(source, f"{path.name}:cell-{index}", "exec")
            exec(compiled, namespace, namespace)
            try:
                import matplotlib
                import matplotlib.pyplot as plt

                matplotlib.use("Agg", force=True)
                plt.show = lambda *args, **kwargs: None
                plt.close("all")
            except ImportError:
                pass
    finally:
        os.chdir(previous)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--visualization-root", type=Path, default=ROOT / "visualization")
    parser.add_argument("notebooks", nargs="*", type=Path)
    args = parser.parse_args()
    vis_root = args.visualization_root.resolve()
    paths = args.notebooks or sorted((vis_root / "notebooks").glob("*.ipynb"))
    sys.path.insert(0, str(vis_root / "src"))
    for path in paths:
        execute(path.resolve(), vis_root)
        print(f"PASS {path}")
    print("NETWORK=DENIED_BY_SOURCE_AUDIT")
    print("SCIENTIFIC_AUTHORITY=UNCHANGED_BY_NOTEBOOK_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
