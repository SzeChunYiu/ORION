"""Protected/candidate custody for the prospective Self-ORION V3 experiment.

The schema is deliberately benchmark-local.  Revision labels are strings frozen
by a specific protocol; this module does not promote #452's provisional taxonomy
into a universal ORION enum.  Candidate packets expose hypotheses and allowed
interventions, never protected outcomes or gold responsibility labels.
"""

from __future__ import annotations

import copy
from pathlib import PurePosixPath
from typing import Any, Mapping

from orion.study.p5.freeze import sha256_json

PROTECTED_SCHEMA = "orion.p5.revision-level-v3.protected-suite.v1"
CANDIDATE_SCHEMA = "orion.p5.revision-level-v3.candidate-packet.v1"
_HEX = frozenset("0123456789abcdef")
_PROTECTED_KEYS = frozenset(
    {
        "protected_diagnostic_outcomes",
        "protected_gold_revision_class",
        "protected_fresh_outcomes",
        "protected_evaluator_state",
    }
)


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _strings(value: Any, field: str, *, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{field} must contain at least {minimum} item(s)")
    result = [_text(item, f"{field}[{index}]") for index, item in enumerate(value)]
    if len(result) != len(set(result)):
        raise ValueError(f"{field} contains duplicate values")
    return result


def _nonce(value: Any, field: str) -> str:
    value = _text(value, field)
    if len(value) != 64 or value.lower() != value or any(char not in _HEX for char in value):
        raise ValueError(f"{field} must be a lowercase SHA-256-shaped nonce")
    if value == "0" * 64:
        raise ValueError(f"{field} nonce must not be all zero")
    return value


def _surface(value: str, field: str) -> tuple[str, ...]:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must be a relative non-traversing surface")
    parts = tuple(part for part in path.parts if part not in ("", "."))
    if not parts:
        raise ValueError(f"{field} must identify a concrete surface")
    return parts


def _surfaces_overlap(left: list[str], right: list[str]) -> bool:
    left_parts = [_surface(value, "allowed_change_surface") for value in left]
    right_parts = [_surface(value, "protected_surface") for value in right]
    return any(
        a == b[: len(a)] or b == a[: len(b)]
        for a in left_parts
        for b in right_parts
    )


def _validate_invasiveness(raw: Any) -> dict[str, int]:
    mapping = _mapping(raw, "revision_invasiveness")
    result: dict[str, int] = {}
    for key, value in mapping.items():
        label = _text(key, "revision_invasiveness label")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"revision_invasiveness[{label}] must be a non-negative integer")
        result[label] = value
    if not result:
        raise ValueError("revision_invasiveness must not be empty")
    return result


def validate_protected_suite(raw_suite: Mapping[str, Any]) -> None:
    suite = _mapping(raw_suite, "suite")
    if suite.get("schema_version") != PROTECTED_SCHEMA:
        raise ValueError(f"schema_version must be {PROTECTED_SCHEMA!r}")
    _text(suite.get("suite_id"), "suite_id")
    if suite.get("development_only") not in (True, False):
        raise ValueError("development_only must be boolean")
    if suite.get("created_before_outcome_access") is not True:
        raise ValueError("created_before_outcome_access must be true")
    _nonce(suite.get("suite_nonce"), "suite_nonce")
    invasiveness = _validate_invasiveness(suite.get("revision_invasiveness"))

    raw_cases = suite.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("cases must be a non-empty array")
    seen_cases: set[str] = set()
    for index, raw_case in enumerate(raw_cases):
        case = _mapping(raw_case, f"cases[{index}]")
        case_id = _text(case.get("case_id"), f"cases[{index}].case_id")
        if case_id in seen_cases:
            raise ValueError(f"duplicate case_id: {case_id}")
        seen_cases.add(case_id)
        _text(case.get("symptom_family"), f"case {case_id}.symptom_family")
        _text(case.get("visible_symptom"), f"case {case_id}.visible_symptom")
        _mapping(case.get("candidate_visible_context"), f"case {case_id}.candidate_visible_context")

        competing = _strings(
            case.get("competing_revision_classes"),
            f"case {case_id}.competing_revision_classes",
            minimum=2,
        )
        hypotheses = _mapping(case.get("hypotheses"), f"case {case_id}.hypotheses")
        if set(map(str, hypotheses)) != set(competing):
            raise ValueError(f"case {case_id} hypotheses must exactly match competing revision classes")

        raw_actions = case.get("allowed_diagnostics")
        if not isinstance(raw_actions, list):
            raise ValueError(f"case {case_id}.allowed_diagnostics must be an array")
        actions: dict[str, float] = {}
        for action_index, raw_action in enumerate(raw_actions):
            action = _mapping(raw_action, f"case {case_id}.allowed_diagnostics[{action_index}]")
            action_id = _text(action.get("action_id"), f"case {case_id}.diagnostic.action_id")
            if action_id in actions:
                raise ValueError(f"duplicate diagnostic action_id in case {case_id}: {action_id}")
            cost = action.get("cost")
            if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0:
                raise ValueError(f"case {case_id} diagnostic cost must be non-negative")
            actions[action_id] = float(cost)
        budget = case.get("diagnostic_budget")
        if not isinstance(budget, (int, float)) or isinstance(budget, bool) or budget < 0:
            raise ValueError(f"case {case_id}.diagnostic_budget must be non-negative")

        for label, raw_prediction in hypotheses.items():
            prediction = _mapping(raw_prediction, f"case {case_id}.hypotheses[{label}]")
            unknown_actions = set(map(str, prediction)) - set(actions)
            if unknown_actions:
                raise ValueError(f"case {case_id} hypothesis references unavailable diagnostic")
            for action_id, outcomes in prediction.items():
                _strings(outcomes, f"case {case_id}.hypotheses[{label}][{action_id}]")

        observed = _mapping(
            case.get("protected_diagnostic_outcomes"),
            f"case {case_id}.protected_diagnostic_outcomes",
        )
        if set(map(str, observed)) != set(actions):
            raise ValueError(f"case {case_id} protected outcomes must exactly match allowed diagnostics")
        for action_id, outcome in observed.items():
            _text(outcome, f"case {case_id}.protected_diagnostic_outcomes[{action_id}]")

        gold = _text(
            case.get("protected_gold_revision_class"),
            f"case {case_id}.protected_gold_revision_class",
        )
        if gold != "UNRESOLVED" and gold not in competing:
            raise ValueError(f"case {case_id} gold revision must be competing class or UNRESOLVED")
        for label in (*competing, gold):
            if label not in invasiveness:
                raise ValueError(f"case {case_id} revision class {label!r} lacks invasiveness binding")

        _strings(case.get("preservation_obligations"), f"case {case_id}.preservation_obligations")
        allowed = _strings(case.get("allowed_change_surface"), f"case {case_id}.allowed_change_surface")
        protected = _strings(case.get("protected_surface"), f"case {case_id}.protected_surface")
        if _surfaces_overlap(allowed, protected):
            raise ValueError(f"case {case_id} allowed/protected surfaces overlap")
        _text(case.get("fresh_transfer_family"), f"case {case_id}.fresh_transfer_family")


def _candidate_case(case: Mapping[str, Any], invasiveness: Mapping[str, int]) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "symptom_family": case["symptom_family"],
        "visible_symptom": case["visible_symptom"],
        "candidate_visible_context": copy.deepcopy(case["candidate_visible_context"]),
        "competing_revision_classes": list(case["competing_revision_classes"]),
        "hypotheses": copy.deepcopy(case["hypotheses"]),
        "allowed_diagnostics": copy.deepcopy(case["allowed_diagnostics"]),
        "diagnostic_budget": float(case["diagnostic_budget"]),
        "revision_invasiveness": dict(invasiveness),
        "preservation_obligations": list(case["preservation_obligations"]),
        "allowed_change_surface": list(case["allowed_change_surface"]),
        "fresh_transfer_family": case["fresh_transfer_family"],
    }


def derive_candidate_packet(raw_suite: Mapping[str, Any]) -> dict[str, Any]:
    validate_protected_suite(raw_suite)
    invasiveness = dict(raw_suite["revision_invasiveness"])
    packet = {
        "schema_version": CANDIDATE_SCHEMA,
        "suite_id": raw_suite["suite_id"],
        "development_only": bool(raw_suite["development_only"]),
        "revision_invasiveness": invasiveness,
        "cases": [_candidate_case(case, invasiveness) for case in raw_suite["cases"]],
    }
    validate_candidate_packet(packet)
    return packet


def _walk_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in _PROTECTED_KEYS or str(key).startswith("protected_"):
                raise ValueError(f"candidate packet leaks protected field at {path}.{key}")
            _walk_forbidden(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_forbidden(item, f"{path}[{index}]")


def validate_candidate_packet(raw_packet: Mapping[str, Any]) -> None:
    packet = _mapping(raw_packet, "candidate packet")
    if packet.get("schema_version") != CANDIDATE_SCHEMA:
        raise ValueError(f"candidate packet schema must be {CANDIDATE_SCHEMA!r}")
    _text(packet.get("suite_id"), "candidate suite_id")
    if packet.get("development_only") not in (True, False):
        raise ValueError("candidate development_only must be boolean")
    _validate_invasiveness(packet.get("revision_invasiveness"))
    raw_cases = packet.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("candidate cases must be a non-empty array")
    seen: set[str] = set()
    for raw_case in raw_cases:
        case = _mapping(raw_case, "candidate case")
        case_id = _text(case.get("case_id"), "candidate case_id")
        if case_id in seen:
            raise ValueError(f"duplicate case_id: {case_id}")
        seen.add(case_id)
        _text(case.get("symptom_family"), f"candidate {case_id}.symptom_family")
        _text(case.get("visible_symptom"), f"candidate {case_id}.visible_symptom")
        _mapping(case.get("candidate_visible_context"), f"candidate {case_id}.context")
        competing = _strings(case.get("competing_revision_classes"), f"candidate {case_id}.competing", minimum=2)
        hypotheses = _mapping(case.get("hypotheses"), f"candidate {case_id}.hypotheses")
        if set(map(str, hypotheses)) != set(competing):
            raise ValueError(f"candidate {case_id} hypotheses mismatch")
        actions = case.get("allowed_diagnostics")
        if not isinstance(actions, list):
            raise ValueError(f"candidate {case_id}.allowed_diagnostics must be an array")
        action_ids = [
            _text(_mapping(action, "candidate diagnostic").get("action_id"), "candidate action_id")
            for action in actions
        ]
        if len(action_ids) != len(set(action_ids)):
            raise ValueError(f"duplicate diagnostic in candidate {case_id}")
        budget = case.get("diagnostic_budget")
        if not isinstance(budget, (int, float)) or isinstance(budget, bool) or budget < 0:
            raise ValueError(f"candidate {case_id}.diagnostic_budget invalid")
        _strings(case.get("preservation_obligations"), f"candidate {case_id}.preservation")
        _strings(case.get("allowed_change_surface"), f"candidate {case_id}.allowed_surface")
        _text(case.get("fresh_transfer_family"), f"candidate {case_id}.fresh_transfer_family")
    _walk_forbidden(packet)


def derive_protected_commitment(raw_suite: Mapping[str, Any]) -> str:
    validate_protected_suite(raw_suite)
    nonce = str(raw_suite["suite_nonce"])
    protected_projection = {
        "schema_version": PROTECTED_SCHEMA,
        "suite_id": raw_suite["suite_id"],
        "development_only": raw_suite["development_only"],
        "revision_invasiveness": raw_suite["revision_invasiveness"],
        "cases": raw_suite["cases"],
    }
    return sha256_json(
        {
            "kind": "SelfOrionV3ProtectedSuiteCommitment.v1",
            "payload_sha256": sha256_json(protected_projection),
            "nonce": nonce,
        }
    )


__all__ = [
    "CANDIDATE_SCHEMA",
    "PROTECTED_SCHEMA",
    "derive_candidate_packet",
    "derive_protected_commitment",
    "validate_candidate_packet",
    "validate_protected_suite",
]
