#!/usr/bin/env python3
"""Outcome-blind A3 baseline policies for external change-transport.

These functions operate only on fields available before reuse-validity gold.
They do not implement the candidate policy and they do not select the strongest
baseline; selection remains a development-only preregistered step.
"""
from __future__ import annotations

import json
from typing import Any

REUSE = "REUSE"
REOPEN = "REOPEN"
CANNOT_CHECK = "CANNOT_CHECK"
TERMINALS = (REUSE, REOPEN, CANNOT_CHECK)
BASELINES = (
    "ALWAYS_REUSE",
    "ALWAYS_REOPEN",
    "VERSION_PROVENANCE_ONLY",
    "SEMANTIC_DIFF_ONLY",
    "CONFIDENCE_ONLY",
)


def _bool_or_none(value: Any, name: str) -> bool | None:
    if value is None or type(value) is bool:
        return value
    raise ValueError(f"{name} must be bool or null")


def always_reuse(_: dict[str, Any]) -> str:
    return REUSE


def always_reopen(_: dict[str, Any]) -> str:
    return REOPEN


def version_provenance_only(record: dict[str, Any]) -> str:
    version_changed = _bool_or_none(record.get("version_changed"), "version_changed")
    provenance_changed = _bool_or_none(record.get("provenance_changed"), "provenance_changed")
    if version_changed is None or provenance_changed is None:
        return CANNOT_CHECK
    return REOPEN if version_changed or provenance_changed else REUSE


def semantic_diff_only(record: dict[str, Any]) -> str:
    material = _bool_or_none(record.get("semantic_diff_material"), "semantic_diff_material")
    if material is None:
        return CANNOT_CHECK
    return REOPEN if material else REUSE


def confidence_only(record: dict[str, Any]) -> str:
    meaningful = _bool_or_none(record.get("confidence_signal_meaningful"), "confidence_signal_meaningful")
    if meaningful is not True:
        return CANNOT_CHECK
    value = record.get("confidence_signal")
    threshold = record.get("confidence_reopen_threshold")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return CANNOT_CHECK
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        return CANNOT_CHECK
    # Threshold direction is frozen: low confidence reopens; equality reuses.
    return REOPEN if float(value) < float(threshold) else REUSE


FUNCTIONS = {
    "ALWAYS_REUSE": always_reuse,
    "ALWAYS_REOPEN": always_reopen,
    "VERSION_PROVENANCE_ONLY": version_provenance_only,
    "SEMANTIC_DIFF_ONLY": semantic_diff_only,
    "CONFIDENCE_ONLY": confidence_only,
}


def evaluate(record: dict[str, Any]) -> dict[str, str]:
    return {name: FUNCTIONS[name](record) for name in BASELINES}


def self_test() -> dict[str, Any]:
    cases = [
        ({"version_changed": False, "provenance_changed": False, "semantic_diff_material": False, "confidence_signal_meaningful": True, "confidence_signal": 0.9, "confidence_reopen_threshold": 0.5}, {"ALWAYS_REUSE": REUSE, "ALWAYS_REOPEN": REOPEN, "VERSION_PROVENANCE_ONLY": REUSE, "SEMANTIC_DIFF_ONLY": REUSE, "CONFIDENCE_ONLY": REUSE}),
        ({"version_changed": True, "provenance_changed": False, "semantic_diff_material": True, "confidence_signal_meaningful": True, "confidence_signal": 0.2, "confidence_reopen_threshold": 0.5}, {"ALWAYS_REUSE": REUSE, "ALWAYS_REOPEN": REOPEN, "VERSION_PROVENANCE_ONLY": REOPEN, "SEMANTIC_DIFF_ONLY": REOPEN, "CONFIDENCE_ONLY": REOPEN}),
        ({"version_changed": None, "provenance_changed": False, "semantic_diff_material": None, "confidence_signal_meaningful": False, "confidence_signal": None, "confidence_reopen_threshold": None}, {"ALWAYS_REUSE": REUSE, "ALWAYS_REOPEN": REOPEN, "VERSION_PROVENANCE_ONLY": CANNOT_CHECK, "SEMANTIC_DIFF_ONLY": CANNOT_CHECK, "CONFIDENCE_ONLY": CANNOT_CHECK}),
    ]
    observed = []
    for rec, expected in cases:
        got = evaluate(rec)
        assert got == expected
        observed.append(got)
    return {"decision": "GREEN", "baselines": list(BASELINES), "cases": observed, "protected_gold_consumed": False}


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
