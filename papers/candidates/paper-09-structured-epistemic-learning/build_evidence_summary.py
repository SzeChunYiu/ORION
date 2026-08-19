from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "p9-structured-neural"
OUT = Path(__file__).resolve().parent / "evidence" / "OFFICIAL_EVIDENCE_SUMMARY_V1.json"

SOURCES = {
    "a5": RESEARCH / "A5_D0_EXPLICIT_RESULT_V1.json",
    "a2_a4": RESEARCH / "A2_A4_D0_EXPLICIT_RESULT_V1.json",
    "m1": RESEARCH / "M1_RESULT_V1.json",
    "d1": RESEARCH / "D1_RESULT_V1.json",
}

EXPECTED_TERMINALS = {
    "a5": {"A5_D0_EXPLICIT_INFERENCE_SUFFICIENT"},
    "a2_a4": {"A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT"},
    "m1": {
        "M1_SIMPLE_MODELS_SUFFICIENT_FOR_CURRENT_EXACT_WORLDS",
        "M1_NONLINEAR_RELATIONAL_RESIDUAL",
        "M1_GLOBAL_COMPOSITION_RESIDUAL",
        "M1_HISTORY_OR_BINDING_RESIDUAL",
        "M1_SAMPLE_EFFICIENCY_RESIDUAL",
    },
    "d1": {
        "D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED",
        "D1_TYPED_STRUCTURE_TRANSFER_NARROWED",
        "D1_NO_INCREMENTAL_TYPED_TRANSFER",
    },
}

INVALID_STATUS_MARKERS = {
    "INVALIDATED_PENDING_EXECUTABLE_HOSTILE_REPLAY",
    "INVALIDATED_PREVIOUS_ATTESTATION",
    "CANNOT_CHECK_PENDING_REEXECUTION",
}


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing official P9 evidence: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"official evidence is not a mapping: {path.relative_to(ROOT)}")
    return data


def _reject_invalid(name: str, data: dict[str, Any]) -> None:
    for field in ("status", "verification_state", "terminal"):
        value = data.get(field)
        if isinstance(value, str) and value in INVALID_STATUS_MARKERS:
            raise SystemExit(f"{name} evidence is invalid/pending: {field}={value}")
    terminal = data.get("terminal")
    if terminal not in EXPECTED_TERMINALS[name]:
        raise SystemExit(f"{name} has unrecognized/nonfinal terminal: {terminal!r}")


def _a5_summary(data: dict[str, Any]) -> dict[str, Any]:
    views = data.get("views")
    if not isinstance(views, dict):
        raise SystemExit("A5 official evidence lacks view results")
    return {
        "terminal": data["terminal"],
        "verification_state": data.get("verification_state"),
        "typed_accuracy": views["TYPED"]["full_task_accuracy"],
        "typed_unknown_rate": views["TYPED"]["unknown_rate"],
        "current_accuracy": views["CURRENT"]["full_task_accuracy"],
        "semantic_accuracy": views["SEMANTIC"]["full_task_accuracy"],
        "result_digest": data.get("result_digest"),
    }


def _a2_a4_summary(data: dict[str, Any]) -> dict[str, Any]:
    relation = data.get("relation_views")
    history = data.get("history_views")
    hostile = data.get("hostile_checks")
    if not isinstance(relation, dict) or not isinstance(history, dict) or not isinstance(hostile, dict):
        raise SystemExit("A2/A4 official evidence lacks measured result blocks")
    if not all(value is True for value in hostile.values()):
        raise SystemExit(f"A2/A4 hostile checks are not all green: {hostile!r}")
    return {
        "terminal": data["terminal"],
        "relation_typed_accuracy": relation["TYPED"]["full_task_accuracy"],
        "relation_surface_coverage": relation["SURFACE"]["coverage"],
        "history_current_accuracy": history["CURRENT"]["full_task_accuracy"],
        "history_semantic_accuracy": history["SEMANTIC"]["full_task_accuracy"],
        "hostile_checks": hostile,
        "result_digest": data.get("result_digest"),
    }


def _m1_summary(data: dict[str, Any]) -> dict[str, Any]:
    views = data.get("views")
    if not isinstance(views, dict):
        raise SystemExit("M1 official evidence lacks view results")
    return {
        "terminal": data["terminal"],
        "protocol": data.get("protocol"),
        "views": views,
        "result_digest": data.get("result_digest"),
    }


def _d1_summary(data: dict[str, Any]) -> dict[str, Any]:
    views = data.get("views") or data.get("results")
    if not isinstance(views, dict):
        raise SystemExit("D1 official evidence lacks representation-arm results")
    return {
        "terminal": data["terminal"],
        "protected_domain": data.get("protected_domain"),
        "views": views,
        "hostile_checks": data.get("hostile_checks"),
        "result_digest": data.get("result_digest"),
    }


def main() -> None:
    loaded = {name: _load(path) for name, path in SOURCES.items()}
    for name, data in loaded.items():
        _reject_invalid(name, data)

    summary = {
        "schema": "P9.OfficialEvidenceSummary.v1",
        "source_paths": {name: str(path.relative_to(ROOT)) for name, path in SOURCES.items()},
        "a5": _a5_summary(loaded["a5"]),
        "a2_a4": _a2_a4_summary(loaded["a2_a4"]),
        "m1": _m1_summary(loaded["m1"]),
        "d1": _d1_summary(loaded["d1"]),
        "independent_expectations_are_results": False,
        "authority": "PAPER_EVIDENCE_SUMMARY_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
