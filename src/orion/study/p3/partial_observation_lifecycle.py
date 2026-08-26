"""Content-bound authority lineage for P3's partial-observation amendments."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

SCHEMA = "ORION.P3.PartialObservationLifecycle.v1"
ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/orion-13-global-knowledge-portrait"

ROWS = (
    (
        "BASE",
        "protocol/P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.json",
        "evidence/partial-observation-t5/P3_PARTIAL_OBSERVATION_RESULT_2026-08-21.json",
        "evidence/partial-observation-t5/PROBE_CASES_2026-08-21.jsonl",
    ),
    *tuple(
        (
            f"A00{index}",
            f"protocol/P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_00{index}.json",
            f"evidence/partial-observation-t5/P3_PARTIAL_OBSERVATION_RESULT_2026-08-22_AMENDMENT_00{index}.json",
            f"evidence/partial-observation-t5/PROBE_CASES_2026-08-22_AMENDMENT_00{index}.jsonl",
        )
        for index in range(1, 5)
    ),
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_lifecycle() -> dict[str, Any]:
    nodes = []
    for node_id, protocol, result, cases in ROWS:
        result_payload = json.loads((PAPER / result).read_text(encoding="utf-8"))
        nodes.append(
            {
                "node_id": node_id,
                "predecessor": None if node_id == "BASE" else ("BASE" if node_id == "A001" else f"A00{int(node_id[-1]) - 1}"),
                "protocol": protocol,
                "protocol_sha256": digest(PAPER / protocol),
                "result": result,
                "result_sha256": digest(PAPER / result),
                "cases": cases,
                "cases_sha256": digest(PAPER / cases),
                "parameters_sha256": result_payload["parameters_sha256"],
                "overall_outcome": result_payload["overall_outcome"],
                "authority_state": (
                    "ACTIVE_ADJUDICATIVE" if node_id == "A004" else "HISTORICAL_PREDECESSOR"
                ),
            }
        )
    return {
        "schema": SCHEMA,
        "paper_id": "P3",
        "claim_id": "P3_U_T5_PARTIAL_OBSERVATION",
        "selection_rule": "EXPLICIT_CONTENT_BOUND_NODE_ID__NEVER_FILENAME_OR_DATE_ORDER",
        "active_leaf": "A004",
        "nodes": nodes,
        "document_states": [
            {
                "path": "JOURNAL_GATE_CHECK.md",
                "sha256": digest(PAPER / "JOURNAL_GATE_CHECK.md"),
                "state": "HISTORICAL_PREPARATORY_SNAPSHOT",
            },
            {
                "path": "JOURNAL_READINESS.md",
                "sha256": digest(PAPER / "JOURNAL_READINESS.md"),
                "state": "CURRENT_SCOPED_READINESS",
            },
        ],
        "scientific_disposition": (
            "A004 is the sole active adjudicative leaf and remains FAIL on evidence; this "
            "lifecycle repair grants no positive authority and preserves all predecessors."
        ),
    }


def validate_lifecycle(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = build_lifecycle()
    if payload.get("schema") != SCHEMA:
        errors.append("schema mismatch")
    nodes = payload.get("nodes")
    if not isinstance(nodes, list):
        return errors + ["nodes must be a list"]
    ids = [item.get("node_id") for item in nodes if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("duplicate node id")
    if ids != [row[0] for row in ROWS]:
        errors.append("node set/order differs from explicit registered lineage")
    active = [item.get("node_id") for item in nodes if item.get("authority_state") == "ACTIVE_ADJUDICATIVE"]
    if active != [payload.get("active_leaf")]:
        errors.append("exactly one explicit active leaf is required")
    if payload.get("active_leaf") != "A004":
        errors.append("A004 must be selected explicitly")
    if payload != expected:
        errors.append("content binding or explicit lineage differs from the registered lifecycle")
    return errors


__all__ = ["SCHEMA", "build_lifecycle", "validate_lifecycle"]
