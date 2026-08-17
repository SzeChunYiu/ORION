"""Independent host scorer for P1 epistemic-mutation necessity v2.2.

The scorer imports the task contract only. It never imports candidate policies or
ORION licensing code. Scientific validity is derived from the protected
counterfactual response matrix, minimal causal level and public dependency graph.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping, Any

from .necessity_cases import LEVEL_ORDER, NecessityWorld, RepairLevel


@dataclass(frozen=True)
class NecessityScore:
    task_id: str
    family_id: str
    arm_id: str
    hidden_shift: bool
    negative_control: bool
    protected_root_task_success: bool
    selected_repair_id: str | None
    selected_level: str
    selected_repair_tested: bool
    target_success: bool
    protected_sibling_ok: bool
    protected_sibling_regression: bool
    unnecessary_high_level_reframe: bool
    forbidden_high_level_mutation: bool
    dependency_reopen_precision: float
    dependency_reopen_recall: float
    dependency_reopen_f1: float
    unrelated_closure_reopened: bool
    spent_budget: float

    def to_payload(self) -> dict:
        return asdict(self)


def _prf(predicted: set[str], gold: set[str]) -> tuple[float, float, float]:
    if not predicted and not gold:
        return (1.0, 1.0, 1.0)
    precision = len(predicted & gold) / len(predicted) if predicted else 0.0
    recall = len(predicted & gold) / len(gold) if gold else (1.0 if not predicted else 0.0)
    f1 = 0.0 if precision + recall == 0 else 2.0 * precision * recall / (precision + recall)
    return (precision, recall, f1)


def score_necessity_world(world: NecessityWorld, outcome: Mapping[str, Any]) -> NecessityScore:
    arm_id = str(outcome.get("arm_id", ""))
    selected_raw = outcome.get("selected_repair_id")
    selected_id = None if selected_raw in (None, "") else str(selected_raw)
    tested_ids = {str(item) for item in outcome.get("tested_repair_ids", ())}
    reopened = {str(item) for item in outcome.get("reopened_ids", ())}
    spent = float(outcome.get("spent_budget", 0.0))

    selected_level = "NONE"
    target_success = False
    sibling_ok = True
    sibling_regression = False
    selected_tested = selected_id is None
    high_level = False
    if selected_id is not None:
        repair = next((item for item in world.public.repairs if item.repair_id == selected_id), None)
        if repair is None:
            raise ValueError(f"unknown selected repair:{selected_id}")
        selected_level = repair.level.value
        high_level = repair.level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}
        selected_tested = selected_id in tested_ids
        response = world.protected.repair_response(selected_id)
        target_success = response.target_success
        sibling_ok = response.protected_sibling_ok
        sibling_regression = not sibling_ok

    gold_ids = set(world.protected.gold_minimal_repair_ids)
    minimal_selected = selected_id is not None and selected_id in gold_ids
    lower_valid_exists = False
    if world.protected.negative_control:
        minimal_levels = {
            next(item for item in world.public.repairs if item.repair_id == repair_id).level
            for repair_id in gold_ids
        }
        lower_valid_exists = any(level in {RepairLevel.EVIDENCE, RepairLevel.EXECUTION} for level in minimal_levels)
    unnecessary_high = bool(world.protected.negative_control and high_level and lower_valid_exists)
    forbidden_high = unnecessary_high

    gold_impact = set(world.protected.gold_dependency_impact_ids)
    unrelated = {
        item.closure_id
        for item in world.public.dependencies
        if item.declared_coordinate == "UNRELATED"
    }
    precision, recall, f1 = _prf(reopened, gold_impact)
    unrelated_reopened = bool(reopened & unrelated)

    if selected_id is None:
        protected_success = False
    elif not selected_tested or not target_success or not sibling_ok:
        protected_success = False
    elif not minimal_selected:
        protected_success = False
    elif high_level:
        protected_success = f1 == 1.0 and not unrelated_reopened
    else:
        protected_success = not reopened and not unrelated_reopened

    return NecessityScore(
        task_id=world.public.task_id,
        family_id=world.protected.family_id,
        arm_id=arm_id,
        hidden_shift=world.protected.hidden_shift,
        negative_control=world.protected.negative_control,
        protected_root_task_success=protected_success,
        selected_repair_id=selected_id,
        selected_level=selected_level,
        selected_repair_tested=selected_tested,
        target_success=target_success,
        protected_sibling_ok=sibling_ok,
        protected_sibling_regression=sibling_regression,
        unnecessary_high_level_reframe=unnecessary_high,
        forbidden_high_level_mutation=forbidden_high,
        dependency_reopen_precision=precision,
        dependency_reopen_recall=recall,
        dependency_reopen_f1=f1,
        unrelated_closure_reopened=unrelated_reopened,
        spent_budget=spent,
    )


def aggregate_necessity_scores(scores: tuple[NecessityScore, ...]) -> dict[str, float | int]:
    n = len(scores)
    if n == 0:
        return {"n": 0}

    def rate(field: str) -> float:
        return sum(bool(getattr(item, field)) for item in scores) / n

    hidden = tuple(item for item in scores if item.hidden_shift)
    controls = tuple(item for item in scores if item.negative_control)
    return {
        "n": n,
        "hidden_shift_n": len(hidden),
        "negative_control_n": len(controls),
        "protected_root_task_success_rate": rate("protected_root_task_success"),
        "hidden_shift_protected_root_task_success_rate": (
            sum(item.protected_root_task_success for item in hidden) / len(hidden)
            if hidden
            else 1.0
        ),
        "negative_control_unnecessary_high_level_reframe_rate": (
            sum(item.unnecessary_high_level_reframe for item in controls) / len(controls)
            if controls
            else 0.0
        ),
        "protected_sibling_regression_rate": rate("protected_sibling_regression"),
        "forbidden_high_level_mutation_rate": rate("forbidden_high_level_mutation"),
        "mean_dependency_reopen_f1": sum(item.dependency_reopen_f1 for item in scores) / n,
        "mean_spent_budget": sum(item.spent_budget for item in scores) / n,
    }


__all__ = ["NecessityScore", "aggregate_necessity_scores", "score_necessity_world"]
