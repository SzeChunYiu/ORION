from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from orion.discovery.recursive_atom_calculus_closure import (
    AtomStudyDisposition,
    RecursionStopReason,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGISTRY = HERE / "FRONTIER_ATOM_REGISTRY_V1.json"
DEFAULT_QUEUE = HERE / "FRONTIER_ATOM_QUEUE_V1.json"

RUNNABLE_STATUSES = {"OPEN", "DONOR_SUBTRACTION", "PROTOCOL_FROZEN"}
BLOCKED_STATUSES = {"RUNTIME_GATED", "BLOCKED"}
POSITIVE_STATUSES = {"CONTROLLED_POSITIVE"}


def fail(msg: str) -> None:
    raise SystemExit(f"FRONTIER_ATOM_REGISTRY_INVALID: {msg}")


def load() -> dict[str, Any]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if data.get("schema") != "ORION.FrontierAtomRegistry.v1":
        fail("schema")
    return data


def path_exists(relative: str | None) -> bool:
    return bool(relative) and (ROOT / str(relative)).is_file()


def validate(data: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    allowed_statuses = set(data["allowed_statuses"])
    allowed_dispositions = {v.value for v in AtomStudyDisposition}
    allowed_stops = {v.value for v in RecursionStopReason}

    if data.get("governance", {}).get("scientific_authority") is not False:
        fail("registry governance may not grant scientific authority")
    if data.get("governance", {}).get("novelty_authority") is not False:
        fail("registry governance may not grant novelty authority")
    if data.get("governance", {}).get("recursive_calculus_terminal") != "RECURSIVE_ATOM_STUDY_CALCULUS_FROZEN":
        fail("wrong recursive calculus terminal")
    if data.get("governance", {}).get("study_surface") != "BoundedEpistemicAtomStudy.v2":
        fail("frontier must use reviewed atom-study surface")

    rows = list(data.get("nodes", []))
    if len(rows) < 50:
        fail(f"frontier unexpectedly collapsed to {len(rows)} nodes")
    ids = [str(row.get("id", "")) for row in rows]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        fail("node ids must be non-empty and unique")
    by_id = {row["id"]: row for row in rows}
    roots = [row for row in rows if row["status"] == "ROOT"]
    if len(roots) != 1 or roots[0]["parent_id"] != "":
        fail("exactly one root with empty parent is required")

    children: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        node_id = row["id"]
        status = row["status"]
        if status not in allowed_statuses:
            fail(f"{node_id}: unregistered status {status}")
        disposition = row["candidate_disposition"]
        if disposition not in allowed_dispositions:
            fail(f"{node_id}: disposition not in frozen recursive calculus: {disposition}")
        if row.get("grants_scientific_authority") is not False or row.get("grants_novelty_authority") is not False:
            fail(f"{node_id}: node self-authorizes")
        if not row.get("question"):
            fail(f"{node_id}: missing question")
        if not row.get("resource_axes"):
            fail(f"{node_id}: missing resource axes")
        if not row.get("protected_discriminator"):
            fail(f"{node_id}: missing protected discriminator")
        if not row.get("donor_or_owner_ids"):
            fail(f"{node_id}: missing donor/owner pressure")
        if not row.get("evaluator_id") or not row.get("authority_owner_id"):
            fail(f"{node_id}: missing evaluator/authority identity")
        if row["evaluator_id"] == row["authority_owner_id"]:
            fail(f"{node_id}: evaluator equals authority owner")

        parent = row["parent_id"]
        if parent:
            if parent not in by_id:
                fail(f"{node_id}: unknown parent {parent}")
            children[parent].append(node_id)

        if status in POSITIVE_STATUSES:
            receipts = list(row.get("evidence_receipt_paths") or [])
            if not receipts:
                fail(f"{node_id}: positive node has no evidence receipt")
            missing = [p for p in receipts if not path_exists(p)]
            if missing:
                fail(f"{node_id}: missing positive receipt(s): {missing}")
        if status == "PROTOCOL_FROZEN":
            p = row.get("protocol_or_study_path")
            if not path_exists(p):
                fail(f"{node_id}: frozen protocol path missing: {p}")
        if status in BLOCKED_STATUSES and not row.get("runtime_blocker"):
            fail(f"{node_id}: blocked/runtime-gated node lacks blocker")
        if status == "STOPPED":
            stop = row.get("stop_reason")
            if stop not in allowed_stops:
                fail(f"{node_id}: stopped node lacks frozen recursion stop")
        elif row.get("stop_reason") is not None:
            fail(f"{node_id}: non-stopped node carries stop reason")

    for start in ids:
        seen: set[str] = set()
        cur = start
        while cur:
            if cur in seen:
                fail(f"cycle through {cur}")
            seen.add(cur)
            cur = str(by_id[cur]["parent_id"]) if cur in by_id else ""

    for row in rows:
        if row.get("children_expected") is False and children.get(row["id"]):
            fail(f"{row['id']}: marked leaf but has children")

    queue = [row for row in rows if row["status"] in RUNNABLE_STATUSES]
    rank = {"DONOR_SUBTRACTION": 0, "PROTOCOL_FROZEN": 1, "OPEN": 2}
    queue.sort(key=lambda r: (-int(r["priority"]), rank[r["status"]], r["id"].count("."), r["id"]))
    queue_rows = [
        {
            "id": row["id"],
            "priority": row["priority"],
            "status": row["status"],
            "question": row["question"],
            "resource_axes": row["resource_axes"],
            "cross_domain_targets": row["cross_domain_targets"],
        }
        for row in queue
    ]

    summary = {
        "schema": "ORION.FrontierAtomRegistryValidation.v1",
        "node_count": len(rows),
        "status_counts": dict(sorted(Counter(row["status"] for row in rows).items())),
        "disposition_counts": dict(sorted(Counter(row["candidate_disposition"] for row in rows).items())),
        "root_id": roots[0]["id"],
        "controlled_positive_ids": sorted(row["id"] for row in rows if row["status"] == "CONTROLLED_POSITIVE"),
        "runtime_gated_or_blocked_count": sum(row["status"] in BLOCKED_STATUSES for row in rows),
        "runnable_count": len(queue_rows),
        "top_runnable_ids": [row["id"] for row in queue_rows[:15]],
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "terminal": "FRONTIER_RECURSIVE_ATOM_REGISTRY_VALID",
    }
    return queue_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-queue", action="store_true")
    args = parser.parse_args()
    queue, summary = validate(load())
    if args.write_queue:
        payload = {
            "schema": "ORION.FrontierAtomQueue.v1",
            "source_registry": REGISTRY.name,
            "queue": queue,
            "non_authorizing": True,
        }
        DEFAULT_QUEUE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
