from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orion.self_orion.phase2_preflight import Phase2ClosurePreflight


BINDING_SCHEMA = "Phase2ClosureBinding.v1"


def _require_mapping(value: object, *, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be a JSON object")
    return value


def _require_positive_number(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a JSON number")
    converted = float(value)
    if converted <= 0:
        raise ValueError(f"{field} must be positive")
    return converted


def repository_phase2_preflight() -> Phase2ClosurePreflight:
    """Frozen Phase-2 structure with deliberately unbound external identities."""

    return Phase2ClosurePreflight(
        protocol_id="phase2-shadow-closure-v1",
        subject_revision_hash="0" * 64,
        provider_manifest_hash="0" * 64,
        evaluator_artifact_hash="0" * 64,
        evaluation_epoch_id="phase2:epoch:frozen-before-outcomes",
        baseline_id="simple-llm-retrieval-baseline-v1",
        resource_budget_units=100.0,
    )


def load_phase2_binding(path: Path | str) -> Phase2ClosurePreflight:
    """Load host-owned bindings without allowing task/attack mutation."""

    source = Path(path)
    raw = _require_mapping(json.loads(source.read_text(encoding="utf-8")), where="phase2 binding")
    if raw.get("schema") != BINDING_SCHEMA:
        raise ValueError(f"phase2 binding schema must be {BINDING_SCHEMA}")

    return Phase2ClosurePreflight(
        protocol_id=raw["protocol_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        provider_manifest_hash=raw["provider_manifest_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        baseline_id=raw["baseline_id"],
        resource_budget_units=_require_positive_number(
            raw["resource_budget_units"], field="resource_budget_units"
        ),
    )


def phase2_binding_to_dict(preflight: Phase2ClosurePreflight) -> dict[str, object]:
    """Serialize bindings only; frozen tasks/attacks remain code-owned protocol state."""

    return {
        "schema": BINDING_SCHEMA,
        "protocol_id": preflight.protocol_id,
        "subject_revision_hash": preflight.subject_revision_hash,
        "provider_manifest_hash": preflight.provider_manifest_hash,
        "evaluator_artifact_hash": preflight.evaluator_artifact_hash,
        "evaluation_epoch_id": preflight.evaluation_epoch_id,
        "baseline_id": preflight.baseline_id,
        "resource_budget_units": preflight.resource_budget_units,
    }


def write_phase2_binding(preflight: Phase2ClosurePreflight, path: Path | str) -> None:
    Path(path).write_text(
        json.dumps(phase2_binding_to_dict(preflight), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "BINDING_SCHEMA",
    "load_phase2_binding",
    "phase2_binding_to_dict",
    "repository_phase2_preflight",
    "write_phase2_binding",
]
