from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.study.p10.a0_runtime import run_a0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cases-per-family", type=int, default=128)
    parser.add_argument("--seed", default="p10-a0-responsibility-control-v1")
    args = parser.parse_args()
    result = run_a0(seed=args.seed, cases_per_family=args.cases_per_family)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"terminal": result["terminal"], "arms": result["arms"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
