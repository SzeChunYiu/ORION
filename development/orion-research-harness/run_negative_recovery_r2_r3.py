#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion_research_harness.negative_recovery import evaluate_dual_recovery

OUT = Path("/tmp/orion-negative-recovery-r2-r3.json")
PREFIX = "ORION_NEGATIVE_RECOVERY_R2_R3="


def main() -> int:
    result = evaluate_dual_recovery()
    canonical = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(canonical, encoding="utf-8")
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    token = {
        "schema": result["schema"],
        "terminal": result["terminal"],
        "result_sha256": digest,
        "metrics": result["metrics"],
        "gates": result["gates"],
    }
    print(PREFIX + json.dumps(token, sort_keys=True))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
