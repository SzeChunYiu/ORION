#!/usr/bin/env python3
"""Regenerate the frozen P6 V2 countermodel JSONL from its source register."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from papers.candidates.reproducibility_generators_v3 import regenerate_jsonl  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "assumption_countermodels_v2.source.json"
SCHEMA = HERE / "assumption_countermodels_v2.schema.json"
OUTPUT = HERE / "assumption_countermodels_v2.jsonl"


def records() -> list[dict[str, object]]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "orion.p6.assumption-countermodel-source.v2":
        raise ValueError("unexpected P6 source schema")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not all(isinstance(case, dict) for case in cases):
        raise ValueError("P6 source cases must be a non-empty object array")
    typed = list(cases)
    kinds = Counter(str(case.get("kind")) for case in typed)
    verdicts = Counter(str(case.get("expected_verdict")) for case in typed)
    if len(typed) != 12 or set(kinds.values()) != {2}:
        raise ValueError("P6 requires two controls for each of six hostile kinds")
    if verdicts != {"DETECTED": 6, "NOT_DETECTED": 6}:
        raise ValueError("P6 requires balanced detected/not-detected controls")
    return typed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    regenerate_jsonl(
        source=SOURCE,
        schema_path=SCHEMA,
        target=OUTPUT,
        records=records(),
        check=args.check,
    )
    print("P6 V2 GENERATOR: MATCH" if args.check else "P6 V2 GENERATOR: WROTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
