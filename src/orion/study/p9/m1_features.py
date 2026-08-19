"""Generic, leakage-controlled feature maps for P9 M1.

These feature maps deliberately avoid solving the synthetic tasks by hand.  Raw
opaque identities are never emitted as reusable categorical features.  Identity
may be used only through equality/overlap relations that are themselves visible
in the declared task payload.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import math
import re
from typing import Iterable, Mapping, Sequence

from .m0_tasks import CandidateInput, GluingTask, MechanicRankingTask, P9Task
from .structural_world import ViewMode


_OPAQUE = re.compile(r"^[a-z][0-9a-f]{16}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


class FeatureFamily(str, Enum):
    F0_FIELD_BAG = "F0_FIELD_BAG"
    F1_PAIRWISE = "F1_PAIRWISE"
    F2_CYCLE_NUMERIC = "F2_CYCLE_NUMERIC"


def is_opaque_identity(value: object) -> bool:
    return isinstance(value, str) and bool(_OPAQUE.fullmatch(value) or _SHA256.fullmatch(value))


def _collect_strings(value: object) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, Mapping):
        for item in value.values():
            out.extend(_collect_strings(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            out.extend(_collect_strings(item))
    return out


def _structural_tokens(value: object, *, path: str = "root") -> tuple[str, ...]:
    """Return path-aware non-opaque categorical tokens from a JSON-like payload."""

    tokens: list[str] = []
    if isinstance(value, Mapping):
        for key in sorted(value):
            child = value[key]
            child_path = f"{path}.{key}"
            tokens.extend(_structural_tokens(child, path=child_path))
        tokens.append(f"shape:{path}:keys={len(value)}")
    elif isinstance(value, (list, tuple)):
        tokens.append(f"shape:{path}:len={len(value)}")
        for item in value:
            # List positions are intentionally not categorical features in F0/F1.
            # This prevents pair/row presentation from becoming a shortcut.
            tokens.extend(_structural_tokens(item, path=f"{path}[]"))
    elif isinstance(value, str):
        if not is_opaque_identity(value):
            tokens.append(f"cat:{path}={value}")
    elif isinstance(value, bool):
        tokens.append(f"cat:{path}={str(value).lower()}")
    elif value is None:
        tokens.append(f"cat:{path}=<NONE>")
    return tuple(sorted(tokens))


def _numeric_features(value: object, *, path: str = "root") -> dict[str, float]:
    """Return generic numeric scalar features using visible serialization paths."""

    out: dict[str, float] = {}

    def walk(item: object, item_path: str) -> None:
        if isinstance(item, Mapping):
            for key in sorted(item):
                walk(item[key], f"{item_path}.{key}")
        elif isinstance(item, (list, tuple)):
            numeric_values = [
                float(child)
                for child in item
                if isinstance(child, (int, float)) and not isinstance(child, bool)
            ]
            if numeric_values:
                out[f"num:{item_path}:count"] = float(len(numeric_values))
                out[f"num:{item_path}:sum"] = float(sum(numeric_values))
                out[f"num:{item_path}:min"] = float(min(numeric_values))
                out[f"num:{item_path}:max"] = float(max(numeric_values))
            for index, child in enumerate(item):
                # Numeric list position is visible serialization information.  It
                # is allowed in F0, but transport ordering is reminted/random;
                # F2 supplies a separate canonical topology-relative ordering.
                walk(child, f"{item_path}[{index}]")
        elif isinstance(item, (int, float)) and not isinstance(item, bool):
            numeric = float(item)
            if not math.isfinite(numeric):
                raise ValueError("M1 feature payload contains non-finite numeric value")
            out[f"num:{item_path}"] = numeric

    walk(value, path)
    return out


def _base_feature_dict(value: object, *, prefix: str) -> dict[str, object]:
    features: dict[str, object] = {}
    for token in _structural_tokens(value, path=prefix):
        features[token] = 1.0
    features.update(_numeric_features(value, path=prefix))
    return features


def _candidate_equality_features(
    context: Mapping[str, object], candidate: CandidateInput
) -> dict[str, float]:
    strings = _collect_strings(context)
    count = sum(1 for value in strings if value == candidate.candidate_id)
    return {
        "eq:candidate_id_occurs_in_context": float(count > 0),
        "eq:candidate_id_context_occurrence_count": float(count),
    }


def _candidate_overlap_features(
    context: Mapping[str, object], candidate: CandidateInput
) -> dict[str, float]:
    context_strings = set(_collect_strings(context))
    read_ids = set(map(str, candidate.payload.get("read_atom_ids", ())))
    write_ids = set(map(str, candidate.payload.get("write_atom_ids", ())))
    return {
        "overlap:read_with_context": float(len(read_ids & context_strings)),
        "overlap:write_with_context": float(len(write_ids & context_strings)),
        "count:candidate_reads": float(len(read_ids)),
        "count:candidate_writes": float(len(write_ids)),
    }


def mechanic_features(
    task: MechanicRankingTask,
    candidate: CandidateInput,
    family: FeatureFamily,
) -> dict[str, object]:
    task.verify()
    candidate.verify()
    if family not in (FeatureFamily.F0_FIELD_BAG, FeatureFamily.F1_PAIRWISE):
        raise ValueError(f"feature family {family.value} is not a mechanic-ranking feature map")

    features = _base_feature_dict(task.context, prefix="context")
    features.update(_base_feature_dict(candidate.payload, prefix="candidate"))
    features["meta:task=MECHANIC_RANKING"] = 1.0
    features[f"meta:view={task.mode.value}"] = 1.0

    if family is FeatureFamily.F1_PAIRWISE:
        context_tokens = [
            token
            for token in _structural_tokens(task.context, path="context")
            if token.startswith("cat:")
        ]
        candidate_tokens = [
            token
            for token in _structural_tokens(candidate.payload, path="candidate")
            if token.startswith("cat:")
        ]
        for left in context_tokens:
            for right in candidate_tokens:
                features[f"cross:{left}|{right}"] = 1.0
        features.update(_candidate_equality_features(task.context, candidate))
        features.update(_candidate_overlap_features(task.context, candidate))
    return features


def _transport_cycle_sequence(context: Mapping[str, object]) -> tuple[tuple[float, float], ...]:
    transports = context.get("transports")
    if not isinstance(transports, list) or not transports:
        raise ValueError("F2 requires visible transport values")

    edges: dict[tuple[str, str], tuple[float, float]] = {}
    nodes: set[str] = set()
    for raw in transports:
        if not isinstance(raw, list) or len(raw) != 4:
            raise ValueError("invalid visible transport record")
        source, target, scale, offset = raw
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("transport endpoints must be string identities")
        key = (source, target)
        if key in edges:
            raise ValueError("F2 requires a unique visible transport per directed edge")
        edges[key] = (float(scale), float(offset))
        nodes.update((source, target))

    outgoing: dict[str, list[str]] = {}
    for source, target in edges:
        outgoing.setdefault(source, []).append(target)
    if any(len(outgoing.get(node, ())) != 1 for node in nodes):
        raise ValueError("F2 requires one directed outgoing edge per visible chart")

    start = min(nodes)
    sequence: list[tuple[float, float]] = []
    current = start
    visited: set[str] = set()
    for _ in range(len(nodes)):
        if current in visited:
            raise ValueError("transport cycle repeats a chart before closure")
        visited.add(current)
        target = outgoing[current][0]
        sequence.append(edges[(current, target)])
        current = target
    if current != start or visited != nodes:
        raise ValueError("visible transports do not form one complete directed cycle")
    return tuple(sequence)


def gluing_features(task: GluingTask, family: FeatureFamily) -> dict[str, object]:
    task.verify()
    if family not in (FeatureFamily.F0_FIELD_BAG, FeatureFamily.F2_CYCLE_NUMERIC):
        raise ValueError(f"feature family {family.value} is not a gluing feature map")
    if family is FeatureFamily.F2_CYCLE_NUMERIC and task.mode not in (
        ViewMode.CURRENT,
        ViewMode.SEMANTIC,
    ):
        raise ValueError("F2 cycle numeric features require CURRENT or SEMANTIC view")

    features = _base_feature_dict(task.context, prefix="context")
    features["meta:task=GLUING"] = 1.0
    features[f"meta:view={task.mode.value}"] = 1.0
    if family is FeatureFamily.F2_CYCLE_NUMERIC:
        for index, (scale, offset) in enumerate(_transport_cycle_sequence(task.context)):
            features[f"cycle:{index}:scale"] = scale
            features[f"cycle:{index}:offset"] = offset
    return features


def task_feature_rows(task: P9Task, family: FeatureFamily) -> tuple[dict[str, object], ...]:
    if isinstance(task, MechanicRankingTask):
        return tuple(mechanic_features(task, candidate, family) for candidate in task.candidates)
    if isinstance(task, GluingTask):
        return (gluing_features(task, family),)
    raise TypeError(f"unsupported P9 task: {type(task)!r}")


def opaque_feature_names(features: Mapping[str, object]) -> tuple[str, ...]:
    """Return feature names that accidentally contain an opaque identity token."""

    leaks: list[str] = []
    for name in features:
        pieces = re.split(r"[^0-9A-Za-z_:.-]+", name)
        if any(is_opaque_identity(piece) for piece in pieces):
            leaks.append(name)
    return tuple(sorted(leaks))


__all__ = [
    "FeatureFamily",
    "gluing_features",
    "is_opaque_identity",
    "mechanic_features",
    "opaque_feature_names",
    "task_feature_rows",
]
