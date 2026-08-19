"""Exact payload-only inference for the P9 D0 affine gluing atom."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest

from .generated_worlds import HostileFamily, generate_pair
from .m0_tasks import GluingTask, build_task
from .structural_world import GluingVerdict, ViewMode


def _context(task: GluingTask) -> Mapping[str, object]:
    task.verify()
    payload = task.model_payload()
    context = payload.get("context")
    if not isinstance(context, Mapping):
        raise ValueError("gluing task context must be a mapping")
    return context


def _representation_nodes(context: Mapping[str, object]) -> tuple[str, ...]:
    raw = context.get("atoms")
    if not isinstance(raw, list):
        return ()
    nodes: list[str] = []
    for item in raw:
        if not isinstance(item, list) or len(item) < 2:
            continue
        if item[1] == "REPRESENTATION" and isinstance(item[0], str):
            nodes.append(item[0])
    return tuple(sorted(set(nodes)))


def _maps_to_edges(context: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    raw = context.get("relations")
    if not isinstance(raw, list):
        return ()
    edges: list[tuple[str, str]] = []
    for item in raw:
        if not isinstance(item, list) or len(item) < 3:
            continue
        source, target, relation_type = item[:3]
        if relation_type == "MAPS_TO" and isinstance(source, str) and isinstance(target, str):
            edges.append((source, target))
    return tuple(edges)


def _recover_cycle(context: Mapping[str, object]) -> tuple[str, ...] | None:
    nodes = set(_representation_nodes(context))
    if len(nodes) < 2:
        return None
    edges = _maps_to_edges(context)
    outgoing: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        if source in nodes and target in nodes:
            outgoing[source].append(target)
    if any(len(outgoing.get(node, ())) != 1 for node in nodes):
        return None
    start = min(nodes)
    path = [start]
    current = start
    visited: set[str] = set()
    for _ in range(len(nodes)):
        if current in visited:
            return None
        visited.add(current)
        target = outgoing[current][0]
        path.append(target)
        current = target
    if current != start or visited != nodes:
        return None
    return tuple(path)


def _transport_map(context: Mapping[str, object]) -> dict[tuple[str, str], tuple[float, float]] | None:
    raw = context.get("transports")
    if not isinstance(raw, list):
        return None
    grouped: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for item in raw:
        if not isinstance(item, list) or len(item) != 4:
            return None
        source, target, scale, offset = item
        if not isinstance(source, str) or not isinstance(target, str):
            return None
        try:
            numeric = (float(scale), float(offset))
        except (TypeError, ValueError):
            return None
        grouped[(source, target)].append(numeric)
    if any(len(values) != 1 for values in grouped.values()):
        return None
    return {edge: values[0] for edge, values in grouped.items()}


def predict_explicit_gluing(task: GluingTask, *, atol: float = 1e-9) -> str:
    """Infer gluing from visible task payload only; missing data => UNKNOWN."""

    if atol < 0:
        raise ValueError("atol must be non-negative")
    context = _context(task)
    cycle = _recover_cycle(context)
    transports = _transport_map(context)
    if cycle is None or transports is None:
        return GluingVerdict.UNKNOWN.value

    scale = 1.0
    offset = 0.0
    for source, target in zip(cycle[:-1], cycle[1:], strict=True):
        values = transports.get((source, target))
        if values is None:
            return GluingVerdict.UNKNOWN.value
        edge_scale, edge_offset = values
        scale, offset = edge_scale * scale, edge_scale * offset + edge_offset
    if abs(scale - 1.0) <= atol and abs(offset) <= atol:
        return GluingVerdict.GLUE.value
    return GluingVerdict.OBSTRUCTION.value


def run_a5_explicit(
    *,
    seed: str = "p9-a5-d0-explicit-v1",
    transport_pairs: int = 256,
    subject_sha: str | None = None,
) -> dict[str, object]:
    if transport_pairs <= 0:
        raise ValueError("transport_pairs must be positive")
    views: dict[str, object] = {}
    for mode in (ViewMode.TYPED, ViewMode.CURRENT, ViewMode.SEMANTIC):
        rows: list[dict[str, object]] = []
        for index in range(transport_pairs):
            pair = generate_pair(HostileFamily.TRANSPORT_GLUING, f"{seed}|{index}")
            for world in pair.worlds:
                task = build_task(world, mode=mode, order_seed="unused")
                if not isinstance(task, GluingTask):
                    raise TypeError("transport family produced non-gluing task")
                prediction = predict_explicit_gluing(task)
                rows.append(
                    {
                        "world_id": world.world_id,
                        "gold": task.target_label,
                        "prediction": prediction,
                        "correct": prediction == task.target_label,
                    }
                )
        total = len(rows)
        correct = sum(int(row["correct"]) for row in rows)
        unknown = sum(int(row["prediction"] == GluingVerdict.UNKNOWN.value) for row in rows)
        per_gold: dict[str, list[bool]] = defaultdict(list)
        for row in rows:
            per_gold[str(row["gold"])].append(bool(row["correct"]))
        views[mode.value] = {
            "sample_count": total,
            "accuracy": correct / total,
            "unknown_rate": unknown / total,
            "prediction_counts": dict(Counter(str(row["prediction"]) for row in rows)),
            "per_gold_accuracy": {
                gold: sum(values) / len(values) for gold, values in sorted(per_gold.items())
            },
            "predictions_digest": content_digest(rows),
        }

    typed = views[ViewMode.TYPED.value]
    current = views[ViewMode.CURRENT.value]
    semantic = views[ViewMode.SEMANTIC.value]
    if (
        typed["unknown_rate"] == 1.0
        and current["accuracy"] == 1.0
        and semantic["accuracy"] == 1.0
        and current["unknown_rate"] == 0.0
        and semantic["unknown_rate"] == 0.0
    ):
        terminal = "A5_D0_EXPLICIT_INFERENCE_SUFFICIENT"
    else:
        terminal = "A5_D0_EXPLICIT_INFERENCE_NARROW_OR_FAIL"

    result: dict[str, object] = {
        "schema": "P9.A5D0ExplicitInferenceResult.v1",
        "protocol": "P9.A5D0ExplicitInferenceProtocol.v1",
        "subject_sha": subject_sha,
        "seed_digest": content_digest(seed),
        "transport_pairs": transport_pairs,
        "views": views,
        "terminal": terminal,
        "claim_ceiling": "D0 one-dimensional affine local-transport gluing only",
        "scientific_authority": "NONE_DIAGNOSTIC_ONLY",
        "grants_neural_escalation": False,
    }
    result["result_digest"] = content_digest(result)
    return result


__all__ = ["predict_explicit_gluing", "run_a5_explicit"]
