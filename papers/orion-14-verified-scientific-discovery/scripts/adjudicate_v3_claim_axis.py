#!/usr/bin/env python3
"""Adjudicate P4 V3 H3 on its exact identifiability axis."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
DEFAULT_REGISTER = P4 / "evidence" / "protected_v3" / "IDENTIFIABILITY_V3.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--construction", default="v3")
    parser.add_argument("--terminal", default="CANNOT_CHECK")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT / "src"))
    from orion.study.p4 import assess_claim_axis

    raw = args.register.read_bytes()
    register = json.loads(raw)
    assessment = assess_claim_axis(
        register, construction=args.construction, terminal=args.terminal
    )
    payload = {
        **assessment.as_json(),
        "claim_id": "P4.H3",
        "register_path": str(args.register.relative_to(ROOT)),
        "register_sha256": hashlib.sha256(raw).hexdigest(),
        "interpretation": (
            "Authority is exact-axis only. Off-axis residuals remain disclosed and "
            "do not imply whole-register clearance."
        ),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if assessment.authorized else 3


if __name__ == "__main__":
    raise SystemExit(main())
