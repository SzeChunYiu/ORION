"""Payload-only explicit diagnostics for P9 D0 relation and history atoms."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Mapping

from orion.transfer.v2.canonical import content_digest

from .generated_worlds import HostileFamily, generate_pair
from .m0_tasks import MechanicRankingTask, build_task
from .structural_world import ViewMode


AMBIGUOUS = "AMBIGUOUS"


def _candidate_effects(task: MechanicRankingTask) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for candidate in task.candidates:
        raw = candidate.payload.get("effects")
        if isinstance(raw, list):
            out[candidate.candidate_id] = set(map(str, raw))
        else:
            out[candidate.candidate_id] = set()
    return out


def predict_relation_explicit(task: MechanicRankingTask) -> str:
    task.verify()
    raw_relations = task.context.get("relations")
    if not isinstance(raw_relations, list):
        return AMBIGUOUS
    relation_types = {str(row[2]) for row in raw_relations if isinstance(row, list) and len(row) >= 3}
    decisive = relation_types & {"SUPPORTS", "DEFEATS"}
    if len(decisive) != 1:
        return AMBIGUOUS
    required_effect = {"SUPPORTS": "ASSIMILATE_EVIDENCE", "DEFEATS": "REOPEN_CLAIM"}[next(iter(decisive))]
    matches = [candidate_id for candidate_id, effects in _candidate_effects(task).items() if required_effect in effects]
    return matches[0] if len(matches) == 1 else AMBIGUOUS


def predict_history_explicit(task: MechanicRankingTask) -> str:
    task.verify()
    history = task.context.get("history")
    failed: set[str] = set()
    if isinstance(history, list):
        for row in history:
            if isinstance(row, list) and row and isinstance(row[0], str):
                failed.add(row[0])
    current_ids = {candidate.candidate_id for candidate in task.candidates}
    failed &= current_ids
    if failed:
        remaining = [candidate.candidate_id for candidate in task.candidates if candidate.candidate_id not in failed]
        return remaining[0] if len(remaining) == 1 else AMBIGUOUS
    cost_rows: list[tuple[float, str]] = []
    for candidate in task.candidates:
        raw_cost = candidate.payload.get("cost")
        if not isinstance(raw_cost, (int, float)) or isinstance(raw_cost, bool):
            return AMBIGUOUS
        cost_rows.append((float(raw_cost), candidate.candidate_id))
    if not cost_rows:
        return AMBIGUOUS
    minimum = min(cost for cost, _ in cost_rows)
    minima = [candidate_id for cost, candidate_id in cost_rows if cost == minimum]
    return minima[0] if len(minima) == 1 else AMBIGUOUS


def _metrics(rows: list[dict[str, object]]) -> dict[str, object]:
    total = len(rows)
    covered = [row for row in rows if row["prediction"] != AMBIGUOUS]
    full_correct = sum(int(row["correct"]) for row in rows)
    covered_correct = sum(int(row["correct"]) for row in covered)
    return {"sample_count": total, "coverage": len(covered) / total if total else None, "full_task_accuracy": full_correct / total if total else None, "accuracy_on_non_ambiguous_predictions": covered_correct / len(covered) if covered else None, "prediction_counts": dict(Counter(str(row["prediction"]) for row in rows)), "predictions_digest": content_digest(rows)}


def run_a2_a4_explicit(*, seed: str = "p9-a2-a4-d0-explicit-v1", relation_pairs: int = 256, history_pairs: int = 256, subject_sha: str | None = None) -> dict[str, object]:
    if relation_pairs <= 0 or history_pairs <= 0:
        raise ValueError("pair counts must be positive")
    relation_views: dict[str, object] = {}; history_views: dict[str, object] = {}
    for mode in ViewMode:
        relation_rows: list[dict[str, object]] = []
        for index in range(relation_pairs):
            pair = generate_pair(HostileFamily.RELATION_SEMANTICS, f"{seed}|rel|{index}")
            for world in pair.worlds:
                task = build_task(world, mode=mode, order_seed="explicit-rel")
                if not isinstance(task, MechanicRankingTask): raise TypeError("relation family produced non-ranking task")
                prediction = predict_relation_explicit(task)
                relation_rows.append({"world_id": world.world_id, "gold": task.target_candidate_id, "prediction": prediction, "correct": prediction == task.target_candidate_id})
        relation_views[mode.value] = _metrics(relation_rows)
        history_rows: list[dict[str, object]] = []; pair_consistency: list[bool] = []
        for index in range(history_pairs):
            pair = generate_pair(HostileFamily.FAILURE_HISTORY, f"{seed}|hist|{index}")
            pair_predictions: list[str] = []
            for world in pair.worlds:
                task = build_task(world, mode=mode, order_seed="explicit-hist")
                if not isinstance(task, MechanicRankingTask): raise TypeError("history family produced non-ranking task")
                prediction = predict_history_explicit(task); pair_predictions.append(prediction)
                history_rows.append({"world_id": world.world_id, "gold": task.target_candidate_id, "prediction": prediction, "correct": prediction == task.target_candidate_id})
            if mode is not ViewMode.SEMANTIC: pair_consistency.append(len(set(pair_predictions)) == 1)
        metrics = _metrics(history_rows); metrics["hidden_view_pair_prediction_equal"] = all(pair_consistency) if pair_consistency else None; history_views[mode.value] = metrics
    relation_ok = all(relation_views[m.value]["full_task_accuracy"] == 1.0 for m in (ViewMode.TYPED, ViewMode.CURRENT, ViewMode.SEMANTIC))
    relation_weak_ambiguous = all(relation_views[m.value]["coverage"] == 0.0 for m in (ViewMode.SURFACE, ViewMode.TOPOLOGY))
    history_semantic_ok = history_views[ViewMode.SEMANTIC.value]["full_task_accuracy"] == 1.0
    history_hidden_equal = all(history_views[m.value]["hidden_view_pair_prediction_equal"] is True for m in (ViewMode.SURFACE, ViewMode.TOPOLOGY, ViewMode.TYPED, ViewMode.CURRENT))
    terminal = "A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT" if relation_ok and relation_weak_ambiguous and history_semantic_ok and history_hidden_equal else "A2_A4_D0_EXPLICIT_INFERENCE_NARROW_OR_FAIL"
    result: dict[str, object] = {"schema": "P9.A2A4D0ExplicitResult.v1", "protocol": "P9.A2A4D0ExplicitProtocol.v1", "subject_sha": subject_sha, "seed_digest": content_digest(seed), "relation_views": relation_views, "history_views": history_views, "terminal": terminal, "claim_ceiling": "D0 relation-semantics and admitted-failure-history mechanic selection only", "scientific_authority": "NONE_DIAGNOSTIC_ONLY", "grants_neural_escalation": False}
    result["result_digest"] = content_digest(result); return result


__all__ = ["AMBIGUOUS", "predict_history_explicit", "predict_relation_explicit", "run_a2_a4_explicit"]
