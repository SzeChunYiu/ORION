from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .protocol import content_digest
from .workspace import ResearchWorkspace

_ALLOWED_EXTERNAL_TERMINALS = {"PASS", "FAIL", "CANNOT_CHECK"}
_FORBIDDEN_AUTHORITY_KEYS = {
    "grants_scientific_authority",
    "grants_novelty_authority",
    "grants_adoption_authority",
    "grants_promotion_authority",
    "grants_merge_authority",
    "grants_global_task_stop_authority",
    "r6_authority",
}


def _string(value: Any, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{name} must be a non-empty string")
    return value


def _strings(value: Sequence[str], *, name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{name} must be an array")
    result = tuple(_string(item, name=f"{name} entry") for item in value)
    if len(result) != len(set(result)):
        raise ValueError(f"{name} entries must be unique")
    return result


def _scan_no_authority(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("external governance result keys must be strings")
            if key in _FORBIDDEN_AUTHORITY_KEYS and item is True:
                raise ValueError(f"external governance result attempted authority escalation: {key}")
            _scan_no_authority(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _scan_no_authority(item)


@dataclass(frozen=True)
class ContextCandidate:
    context_id: str
    priority: float
    cost_units: int = 1
    mandatory: bool = False

    def __post_init__(self) -> None:
        _string(self.context_id, name="context_id")
        if isinstance(self.priority, bool) or not isinstance(self.priority, (int, float)):
            raise TypeError("context priority must be numeric")
        if isinstance(self.cost_units, bool) or not isinstance(self.cost_units, int):
            raise TypeError("context cost_units must be an integer")
        if self.cost_units < 1:
            raise ValueError("context cost_units must be positive")
        if not isinstance(self.mandatory, bool):
            raise TypeError("context mandatory must be a boolean")


@dataclass(frozen=True)
class ContextSelection:
    selected_ids: tuple[str, ...]
    omitted_ids: tuple[str, ...]
    used_cost_units: int
    budget_units: int
    mandatory_preserved: bool
    authority: str = "CONTEXT_SELECTION_ONLY__NO_SCIENTIFIC_AUTHORITY"


def select_context(
    candidates: Sequence[ContextCandidate],
    *,
    budget_units: int,
) -> ContextSelection:
    """Select the smallest bounded context without ever dropping mandatory material.

    Mandatory items are admitted first. Optional items are then ranked by decreasing
    priority-per-cost, with deterministic identity tie-breaking. If mandatory material
    alone exceeds the budget, the policy fails closed rather than silently truncating it.
    """

    if isinstance(budget_units, bool) or not isinstance(budget_units, int):
        raise TypeError("context budget_units must be an integer")
    if budget_units < 1:
        raise ValueError("context budget_units must be positive")
    rows = tuple(candidates)
    ids = [item.context_id for item in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("context candidates must have unique identities")

    mandatory = tuple(sorted((item for item in rows if item.mandatory), key=lambda item: item.context_id))
    mandatory_cost = sum(item.cost_units for item in mandatory)
    if mandatory_cost > budget_units:
        raise ValueError("mandatory context exceeds budget; CANNOT_CHECK rather than truncate")

    selected = list(mandatory)
    used = mandatory_cost
    optional = sorted(
        (item for item in rows if not item.mandatory),
        key=lambda item: (
            -(float(item.priority) / float(item.cost_units)),
            -float(item.priority),
            item.cost_units,
            item.context_id,
        ),
    )
    for item in optional:
        if used + item.cost_units > budget_units:
            continue
        selected.append(item)
        used += item.cost_units

    selected_ids = tuple(item.context_id for item in selected)
    selected_set = set(selected_ids)
    omitted_ids = tuple(sorted(item.context_id for item in rows if item.context_id not in selected_set))
    return ContextSelection(
        selected_ids=selected_ids,
        omitted_ids=omitted_ids,
        used_cost_units=used,
        budget_units=budget_units,
        mandatory_preserved=all(item.context_id in selected_set for item in mandatory),
    )


def _external_governance_check(
    workspace: ResearchWorkspace,
    *,
    capability: str,
    check_id: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    check_id = _string(check_id, name="check_id")
    capability = _string(capability, name="capability")
    frozen_payload = {
        "check_id": check_id,
        "payload": dict(payload),
        "authority_ceiling": "NON_AUTHORIZING_GOVERNANCE_CHECK",
        "instruction": (
            "Return {terminal: PASS|FAIL|CANNOT_CHECK, evidence_ids:[], residual_ids:[], detail:...}. "
            "Do not grant scientific, novelty, adoption, promotion, merge or global-stop authority."
        ),
    }
    request = workspace.get_or_create_request(capability=capability, payload=frozen_payload)
    result = workspace.load_result(request.request_id)
    base = {
        "schema": "ORION.HarnessExternalGovernanceCheck.v1",
        "check_id": check_id,
        "capability": capability,
        "request_id": request.request_id,
        "payload_digest": content_digest(frozen_payload),
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_promotion_authority": False,
    }
    if result is None:
        return {**base, "status": "PENDING_CAPABILITY"}
    if not result.success:
        return {
            **base,
            "status": "CAPABILITY_FAILED",
            "executor": result.executor,
            "error": result.error,
        }
    output = result.output
    if not isinstance(output, Mapping):
        raise TypeError("external governance output must be an object")
    _scan_no_authority(output)
    terminal = output.get("terminal")
    if terminal not in _ALLOWED_EXTERNAL_TERMINALS:
        raise ValueError("external governance terminal must be PASS, FAIL, or CANNOT_CHECK")
    evidence_ids = _strings(output.get("evidence_ids", ()), name="evidence_ids")
    residual_ids = _strings(output.get("residual_ids", ()), name="residual_ids")
    detail = output.get("detail", "")
    if not isinstance(detail, str):
        raise TypeError("external governance detail must be a string")
    if terminal == "PASS" and not evidence_ids:
        raise ValueError("passing external governance check requires evidence_ids")
    return {
        **base,
        "status": "COMPLETE",
        "terminal": terminal,
        "evidence_ids": list(evidence_ids),
        "residual_ids": list(residual_ids),
        "detail": detail,
        "executor": result.executor,
    }


def request_independent_review(
    workspace: ResearchWorkspace,
    *,
    review_id: str,
    claim_ids: Sequence[str],
    evidence_ids: Sequence[str],
    review_question: str,
) -> dict[str, Any]:
    """Execute CROSS.REVIEW through a replayable independent host capability."""

    return _external_governance_check(
        workspace,
        capability="INDEPENDENT_REVIEW",
        check_id=_string(review_id, name="review_id"),
        payload={
            "claim_ids": list(_strings(claim_ids, name="claim_ids")),
            "evidence_ids": list(_strings(evidence_ids, name="evidence_ids")),
            "review_question": _string(review_question, name="review_question"),
            "required_separation": "independent/adversarial review; preserve disagreements and CANNOT_CHECK",
        },
    )


def request_benchmark(
    workspace: ResearchWorkspace,
    *,
    benchmark_id: str,
    subject_ids: Sequence[str],
    evaluator_id: str,
    acceptance_rule: str,
) -> dict[str, Any]:
    """Execute CROSS.BENCHMARK through a frozen replayable host capability."""

    return _external_governance_check(
        workspace,
        capability="BENCHMARK_RUN",
        check_id=_string(benchmark_id, name="benchmark_id"),
        payload={
            "subject_ids": list(_strings(subject_ids, name="subject_ids")),
            "evaluator_id": _string(evaluator_id, name="evaluator_id"),
            "acceptance_rule": _string(acceptance_rule, name="acceptance_rule"),
            "freeze": "subject/evaluator/acceptance identities are bound by this request digest before result ingestion",
        },
    )


__all__ = [
    "ContextCandidate",
    "ContextSelection",
    "request_benchmark",
    "request_independent_review",
    "select_context",
]
