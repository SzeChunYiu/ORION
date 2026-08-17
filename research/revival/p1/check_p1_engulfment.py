#!/usr/bin/env python3
"""Fail-closed validation of Paper-1 donor engulfment.

Nearest-work rows are allowed to disappear from novelty, but they are not
allowed to disappear from the framework.  Every merged matrix row must have one
and only one integration destination, and adopted/adapted/composed mechanisms
must become active substrate/orchestration/evaluation/knowledge rather than
citation-only prose.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COVERAGE = ROOT / "research" / "revival" / "p1" / "P1_DONOR_ASSIMILATION_COVERAGE_V1.json"
DEFAULT_ENGULFMENT = ROOT / "research" / "revival" / "p1" / "P1_DONOR_ENGULFMENT_V1.json"

ACTIVE_MODES = frozenset(
    {
        "EXECUTABLE_SUBSTRATE",
        "FRAMEWORK_ORCHESTRATION",
        "EVALUATION_GOVERNANCE",
        "FRAMEWORK_KNOWLEDGE",
    }
)


def validate_engulfment(
    coverage: dict[str, Any],
    engulfment: dict[str, Any],
) -> tuple[str, ...]:
    errors: list[str] = []
    if coverage.get("schema_version") != "P1.donor-assimilation-coverage.v1":
        errors.append("coverage_schema")
    if engulfment.get("schema_version") != "P1.donor-engulfment.v1":
        errors.append("engulfment_schema")

    rows = coverage.get("rows")
    components = engulfment.get("components")
    if not isinstance(rows, list) or not rows:
        errors.append("coverage_rows_missing")
        return tuple(errors)
    if not isinstance(components, list) or not components:
        errors.append("engulfment_components_missing")
        return tuple(errors)

    expected = {str(item.get("id", "")): item for item in rows}
    if "" in expected or len(expected) != len(rows):
        errors.append("coverage_ids_invalid_or_duplicate")

    assigned: dict[str, str] = {}
    component_ids: set[str] = set()
    for component in components:
        component_id = str(component.get("component_id", ""))
        mode = str(component.get("integration_mode", ""))
        if not component_id or component_id in component_ids:
            errors.append(f"component_id_invalid_or_duplicate:{component_id}")
        component_ids.add(component_id)
        matrix_rows = component.get("matrix_rows")
        if not isinstance(matrix_rows, list):
            errors.append(f"component_rows_not_list:{component_id}")
            continue
        if mode == "EXECUTABLE_SUBSTRATE":
            for field in ("extracted_structure", "orion_role"):
                if not str(component.get(field, "")).strip():
                    errors.append(f"{component_id}:missing_{field}")
        for raw_row_id in matrix_rows:
            row_id = str(raw_row_id)
            if row_id not in expected:
                errors.append(f"unknown_matrix_row:{row_id}")
                continue
            if row_id in assigned:
                errors.append(
                    f"duplicate_matrix_assignment:{row_id}:{assigned[row_id]}:{component_id}"
                )
                continue
            assigned[row_id] = component_id

    missing = sorted(set(expected) - set(assigned))
    for row_id in missing:
        errors.append(f"unengulfed_matrix_row:{row_id}")

    component_by_id = {
        str(item.get("component_id", "")): item for item in components
    }
    for row_id, row in expected.items():
        component_id = assigned.get(row_id)
        if component_id is None:
            continue
        component = component_by_id[component_id]
        mode = str(component.get("integration_mode", ""))
        disposition = str(row.get("disposition", ""))
        if disposition in {"ADOPT", "ADAPT", "COMPOSE"} and mode not in ACTIVE_MODES:
            errors.append(f"active_donor_not_integrated:{row_id}:{mode}")
        elif disposition == "DEFER" and mode != "DEFERRED_WATCHLIST":
            errors.append(f"deferred_donor_not_watchlisted:{row_id}:{mode}")
        elif disposition == "REJECT" and mode != "REJECTED":
            errors.append(f"rejected_donor_granted_wrong_mode:{row_id}:{mode}")

    expected_total = int(coverage.get("expected_total", -1))
    if expected_total != len(rows) or len(assigned) != expected_total:
        errors.append(
            f"coverage_count:{expected_total}:{len(rows)}:{len(assigned)}"
        )

    residual = str(engulfment.get("current_residual_after_engulfment", ""))
    if not residual.strip():
        errors.append("residual_missing")
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--engulfment", type=Path, default=DEFAULT_ENGULFMENT)
    args = parser.parse_args()
    errors = validate_engulfment(
        json.loads(args.coverage.read_text()),
        json.loads(args.engulfment.read_text()),
    )
    print(json.dumps({"valid": not errors, "errors": list(errors)}, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
