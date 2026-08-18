#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    ObligationState,
    assess_mechanic,
    build_mechanic,
    select_minimal_admissible,
)

ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "COUNTERMODELS_V1.json"
SUMMARY = ROOT / "COUNTERMODEL_SUMMARY_V1.json"


def _state_map(raw: dict[str, str]):
    return {name: ObligationState(value) for name, value in raw.items()}


def evaluate_case(case: dict[str, object]) -> dict[str, object]:
    claim_id = f"countermodel:{case['id']}"
    mechanics = []
    assessments = []
    names_by_digest: dict[str, str] = {}

    for spec in case["mechanics"]:
        mechanic = build_mechanic(
            mechanic_id=spec["mechanic_id"],
            claim_id=claim_id,
            kind=spec.get("kind", "GENERIC"),
            read_coordinates=spec.get("read_coordinates", ()),
            write_coordinates=spec.get("write_coordinates", ()),
            preconditions=spec.get("preconditions", ()),
            hard_requirements=spec.get("hard_requirements", ()),
            preservation_obligations=spec.get(
                "preservation_obligations", ()
            ),
            required_authorities=spec.get("required_authorities", ()),
            cost=spec.get("cost", 0.0),
        )
        assessment = assess_mechanic(
            mechanic,
            obligation_states=_state_map(spec.get("obligation_states", {})),
            granted_authorities=spec.get("granted_authorities", ()),
            forbidden_writes=spec.get("forbidden_writes", ()),
        )
        mechanics.append(mechanic)
        assessments.append(assessment)
        names_by_digest[mechanic.digest] = mechanic.mechanic_id

    selection = select_minimal_admissible(mechanics, assessments)
    selected_name = (
        None
        if selection.selected_mechanic_digest is None
        else names_by_digest[selection.selected_mechanic_digest]
    )
    expected_status = case["expected_status"]
    expected_selected = case["expected_selected"]
    passed = (
        selection.status.value == expected_status
        and selected_name == expected_selected
    )
    return {
        "id": case["id"],
        "family": case["family"],
        "expected_status": expected_status,
        "actual_status": selection.status.value,
        "expected_selected": expected_selected,
        "actual_selected": selected_name,
        "minimal_mechanics": [
            names_by_digest[digest]
            for digest in selection.minimal_mechanic_digests
        ],
        "reasons": list(selection.reasons),
        "pass": passed,
    }


def run(panel: dict[str, object]) -> dict[str, object]:
    rows = [evaluate_case(case) for case in panel["cases"]]
    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["actual_status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    result = {
        "result_version": "P6_HIGHER_ORDER_COUNTERMODEL_SUMMARY_V1",
        "protocol_id": panel["protocol_id"],
        "panel_digest": content_digest(panel),
        "n_cases": len(rows),
        "n_pass": sum(bool(row["pass"]) for row in rows),
        "accuracy": sum(bool(row["pass"]) for row in rows) / len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "rows": rows,
        "terminal": "TRANCHE1_FORMAL_COUNTERMODELS_GREEN",
        "claim_ceiling": panel["claim_ceiling"],
        "grants_scientific_authority": False,
        "grants_self_orion_adoption": False,
    }
    result["result_digest"] = content_digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    panel = json.loads(PANEL.read_text())
    result = run(panel)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"

    if args.write:
        SUMMARY.write_text(text)
    if args.check:
        if not SUMMARY.exists() or SUMMARY.read_text() != text:
            raise SystemExit("higher-order epistemic countermodel summary drift")
    if not args.write and not args.check:
        print(text, end="")


if __name__ == "__main__":
    main()
