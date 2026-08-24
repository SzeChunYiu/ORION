"""Frozen final split for the Self-ORION V3 confirmatory execution.

Deterministic, stratified by protected gold revision class: within each of the
eight classes the 12 cases are sorted by case_id and alternately assigned to
PRIMARY_A / REPLICATION_B (6 + 6 per class, 48 + 48 overall).  Both halves are
scored; the frozen decision rules require directional agreement between halves
for the positive terminal.  Written before any policy execution.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SPLIT_ID = "P5V3-CONFIRMATORY-FINAL-SPLIT-2026-08-24"


def build_split(suite: dict[str, object]) -> dict[str, object]:
    cases = suite["cases"]
    by_class: dict[str, list[str]] = {}
    for case in cases:
        by_class.setdefault(str(case["protected_gold_revision_class"]), []).append(str(case["case_id"]))
    assignment: dict[str, str] = {}
    stratification: dict[str, dict[str, int]] = {}
    for gold in sorted(by_class):
        ids = sorted(by_class[gold])
        for index, case_id in enumerate(ids):
            assignment[case_id] = "PRIMARY_A" if index % 2 == 0 else "REPLICATION_B"
        stratification[gold] = {
            "PRIMARY_A": sum(1 for cid in ids if assignment[cid] == "PRIMARY_A"),
            "REPLICATION_B": sum(1 for cid in ids if assignment[cid] == "REPLICATION_B"),
        }
    return {
        "schema_version": "orion.p5.revision-level-v3.final-split.v1",
        "split_id": SPLIT_ID,
        "created_before_outcome_access": True,
        "assignment": assignment,
        "stratification": stratification,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    suite = json.loads(
        (root / "research" / "self-orion-v3" / "confirmatory" / "PROTECTED_CONFIRMATORY_SUITE_V1.json").read_text(
            encoding="utf-8"
        )
    )
    split = build_split(suite)
    path = root / "research" / "self-orion-v3" / "confirmatory" / "CONFIRMATORY_FINAL_SPLIT_V1.json"
    path.write_text(json.dumps(split, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    counts = {arm: sum(1 for v in split["assignment"].values() if v == arm) for arm in ("PRIMARY_A", "REPLICATION_B")}
    print(json.dumps({"split_id": SPLIT_ID, "counts": counts, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
