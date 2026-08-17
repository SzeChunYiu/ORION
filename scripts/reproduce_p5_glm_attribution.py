#!/usr/bin/env python3
"""Replay archived GLM-5.2 attribution records into a hashed diagnosis-only receipt.

This does not call a live model and cannot authorize host promotion.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def main() -> int:
    from orion.study.p5.attribution_receipt import write_reproduction_artifacts

    repo_root = Path(__file__).resolve().parents[1]
    receipt = write_reproduction_artifacts(repo_root)
    json.dump(
        {
            "correct": f"{receipt['metrics']['correct_attributions']}/{receipt['metrics']['total_cases']}",
            "accuracy": receipt["metrics"]["accuracy"],
            "macro_f1": receipt["metrics"]["macro_f1"],
            "false_method_change_rate": receipt["metrics"]["false_method_change_rate"],
            "residual_errors": receipt["residual_errors"],
            "records_sha256": receipt["records_sha256"],
            "receipt_sha256": receipt["receipt_sha256"],
            "empirical_authority": receipt["empirical_authority"],
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
