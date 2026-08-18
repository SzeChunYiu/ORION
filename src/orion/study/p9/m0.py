"""P9 M0 evaluator, leakage sentinels, and exact synthetic-world oracle.

M0 validates the task and evaluator only.  The oracle deliberately reads the
full exact *world semantics* but never the evaluator gold target.  It is a
harness ceiling, not a learned baseline and not scientific authority.
"""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Iterable, Sequence

from orion.transfer.v2.canonical import content_digest

from .generated_worlds import GeneratedCorpus, GeneratedSplit, HostileFamily
from .identifiability import analyze_identifiability
from .m0_tasks import GluingTask, MechanicRankingTask, P9Task, TaskKind, build_task
from .structural_world import (
    AtomType,
    GluingVerdict,
    P9StructuralWorld,
    RelationType,
    ViewMode,
    classify_cycle_gluing,
)


class M0Baseline(str, Enum):
    FIRST_CANDIDATE = "FIRST_CANDIDATE"
    LAST_CANDIDATE = "LAST_CANDIDATE"
    LEXICOGRAPHIC_ID = "LEXICOGRAPHIC_ID"
    HASH_PARITY = "HASH_PARITY"
    ALWAYS_GLUE = "ALWAYS_GLUE"
    ALWAYS_OBSTRUCTION = "ALWAYS_OBSTRUCTION"
    ALWAYS_UNKNOWN = "ALWAYS_UNKNOWN"


_CANDIDATE_BASELINES = {
    M0Baseline.FIRST_CANDIDATE,
    M0Baseline.LAST_CANDIDATE,
    M0Baseline.LEXICOGRAPHIC_ID,
    M0Baseline.HASH_PARITY,
}
_GLUING_BASELINES = {
    M0Baseline.ALWAYS_GLUE,
    M0Baseline.ALWAYS_OBSTRUCTION,
    M0Baseline.ALWAYS_UNKNOWN,
}


def evaluate_prediction(task: P9Task, prediction: str) -> bool:
    """Validate a prediction against the current-example output contract."""

    if isinstance(task, MechanicRankingTask):
        candidate_ids = {candidate.candidate_id for candidate in task.candidates}
        if prediction not in candidate_ids:
            raise ValueError(f"unknown candidate prediction: {prediction}")
        return prediction == task.target_candidate_id

    if isinstance(task, GluingTask):
        if prediction not in task.allowed_labels:
            raise ValueError(f"invalid gluing prediction: {prediction}")
        return prediction == task.target_label

    raise TypeError(f"unsupported P9 task: {type(task)!r}")


def predict_null(task: P9Task, baseline: M0Baseline) -> str:
    """Return one deterministic null/sentinel prediction using model-visible input."""

    if isinstance(task, MechanicRankingTask):
        if baseline not in _CANDIDATE_BASELINES:
            raise ValueError(f"baseline {baseline.value} not applicable to mechanic ranking")
        candidates = task.candidates
        if baseline is M0Baseline.FIRST_CANDIDATE:
            return candidates[0].candidate_id
        if baseline is M0Baseline.LAST_CANDIDATE:
            return candidates[-1].candidate_id
        if baseline is M0Baseline.LEXICOGRAPHIC_ID:
            return min(candidate.candidate_id for candidate in candidates)
        if baseline is M0Baseline.HASH_PARITY:
            digest = content_digest(task.model_payload())
            index = int(digest[-16:], 16) % len(candidates)
            return candidates[index].candidate_id
        raise AssertionError("unreachable candidate baseline")

    if isinstance(task, GluingTask):
        if baseline not in _GLUING_BASELINES:
            raise ValueError(f"baseline {baseline.value} not applicable to gluing")
        if baseline is M0Baseline.ALWAYS_GLUE:
            return GluingVerdict.GLUE.value
        if baseline is M0Baseline.ALWAYS_OBSTRUCTION:
            return GluingVerdict.OBSTRUCTION.value
        if baseline is M0Baseline.ALWAYS_UNKNOWN:
            return GluingVerdict.UNKNOWN.value
        raise AssertionError("unreachable gluing baseline")

    raise TypeError(f"unsupported P9 task: {type(task)!r}")


def _single_candidate_with_effect(world: P9StructuralWorld, effect: str) -> str:
    matches = [
        mechanic.mechanic_id
        for mechanic in world.mechanics
        if effect in set(mechanic.effects)
    ]
    if len(matches) != 1:
        raise ValueError(f"exact oracle expected one candidate with effect {effect!r}")
    return matches[0]


def _oracle_mechanic(world: P9StructuralWorld) -> str:
    """Solve generated mechanic worlds from semantics without reading `world.gold`."""

    relation_types = {relation.relation_type for relation in world.relations}
    if RelationType.SUPPORTS in relation_types:
        return _single_candidate_with_effect(world, "ASSIMILATE_EVIDENCE")
    if RelationType.DEFEATS in relation_types:
        return _single_candidate_with_effect(world, "REOPEN_CLAIM")

    failed_mechanics = {record.mechanic_id for record in world.history}
    admissible = [
        mechanic
        for mechanic in world.mechanics
        if mechanic.mechanic_id not in failed_mechanics
    ]
    if not admissible:
        raise ValueError("exact oracle has no non-failed candidate mechanic")
    admissible.sort(key=lambda mechanic: (mechanic.cost, mechanic.mechanic_id))
    return admissible[0].mechanic_id


def _representation_cycle(world: P9StructuralWorld) -> tuple[str, ...]:
    """Recover the unique directed representation cycle from MAPS_TO relations."""

    representation_ids = {
        atom.atom_id
        for atom in world.atoms
        if atom.atom_type is AtomType.REPRESENTATION
    }
    if not representation_ids:
        raise ValueError("gluing oracle requires representation atoms")

    outgoing: dict[str, list[str]] = defaultdict(list)
    for relation in world.relations:
        if relation.relation_type is RelationType.MAPS_TO:
            outgoing[relation.source_id].append(relation.target_id)

    if any(len(outgoing.get(atom_id, ())) != 1 for atom_id in representation_ids):
        raise ValueError("gluing oracle requires one outgoing MAPS_TO edge per chart")

    start = min(representation_ids)
    path = [start]
    current = start
    for _ in range(len(representation_ids)):
        target = outgoing[current][0]
        path.append(target)
        current = target
    if current != start:
        raise ValueError("MAPS_TO relations do not form one closed representation cycle")
    if set(path[:-1]) != representation_ids:
        raise ValueError("MAPS_TO cycle does not visit every representation exactly once")
    return tuple(path)


def exact_semantic_oracle(world: P9StructuralWorld, task: P9Task) -> str:
    """Return the exact synthetic-world answer without consulting evaluator gold."""

    world.verify()
    task.verify()
    if isinstance(task, MechanicRankingTask):
        prediction = _oracle_mechanic(world)
        if prediction not in {candidate.candidate_id for candidate in task.candidates}:
            raise ValueError("oracle selected a mechanic absent from current task candidates")
        return prediction
    if isinstance(task, GluingTask):
        return classify_cycle_gluing(world, _representation_cycle(world)).value
    raise TypeError(f"unsupported P9 task: {type(task)!r}")


def _accuracy_record(tasks_and_predictions: Iterable[tuple[P9Task, str]]) -> dict[str, object]:
    total = 0
    correct = 0
    invalid = 0
    for task, prediction in tasks_and_predictions:
        total += 1
        try:
            if evaluate_prediction(task, prediction):
                correct += 1
        except ValueError:
            invalid += 1
    return {
        "sample_count": total,
        "correct_count": correct,
        "invalid_prediction_count": invalid,
        "accuracy": (correct / total) if total else None,
    }


def _split_report(
    split: GeneratedSplit,
    *,
    mode: ViewMode,
    order_seed: str,
) -> dict[str, object]:
    split.verify()
    task_records: list[tuple[HostileFamily, P9StructuralWorld, P9Task]] = []
    for pair in split.pairs:
        for world in pair.worlds:
            task_records.append(
                (
                    pair.family,
                    world,
                    build_task(world, mode=mode, order_seed=order_seed),
                )
            )

    oracle_pairs = [
        (task, exact_semantic_oracle(world, task))
        for _, world, task in task_records
    ]
    oracle = _accuracy_record(oracle_pairs)

    by_task: dict[str, list[tuple[P9Task, str]]] = defaultdict(list)
    by_family: dict[str, list[tuple[P9Task, str]]] = defaultdict(list)
    for family, world, task in task_records:
        prediction = exact_semantic_oracle(world, task)
        by_task[task.kind.value].append((task, prediction))
        by_family[family.value].append((task, prediction))

    nulls: dict[str, dict[str, object]] = {}
    for baseline in M0Baseline:
        if baseline in _CANDIDATE_BASELINES:
            eligible = [task for _, _, task in task_records if isinstance(task, MechanicRankingTask)]
        else:
            eligible = [task for _, _, task in task_records if isinstance(task, GluingTask)]
        nulls[baseline.value] = _accuracy_record(
            (task, predict_null(task, baseline)) for task in eligible
        )

    ceiling = analyze_identifiability(split.worlds, mode)
    return {
        "world_count": len(split.worlds),
        "pair_count": len(split.pairs),
        "view_mode": mode.value,
        "view_deterministic_accuracy_ceiling": ceiling.deterministic_accuracy_ceiling,
        "view_is_identifying": ceiling.is_identifying,
        "oracle": oracle,
        "oracle_by_task": {
            key: _accuracy_record(value) for key, value in sorted(by_task.items())
        },
        "oracle_by_family": {
            key: _accuracy_record(value) for key, value in sorted(by_family.items())
        },
        "null_baselines": nulls,
    }


def run_m0_harness(
    *,
    corpus: GeneratedCorpus,
    mode: ViewMode,
    order_seed: str,
) -> dict[str, object]:
    """Run deterministic M0 diagnostics over all frozen corpus splits."""

    corpus.verify()
    if not order_seed:
        raise ValueError("M0 order seed is required")

    payload: dict[str, object] = {
        "schema": "P9.M0HarnessResult.v0",
        "protocol": "P9.M0TaskHarnessProtocol.v0.1",
        "corpus_manifest_digest": corpus.manifest_digest,
        "view_mode": mode.value,
        "order_seed_digest": content_digest(order_seed),
        "train": _split_report(corpus.train, mode=mode, order_seed=order_seed),
        "dev": _split_report(corpus.dev, mode=mode, order_seed=order_seed),
        "test": _split_report(corpus.test, mode=mode, order_seed=order_seed),
        "authority": "NO_SCIENTIFIC_AUTHORITY",
        "grants_model_promotion": False,
        "terminal": "M0_TASK_HARNESS_VALIDATED_ONLY",
    }
    payload["result_digest"] = content_digest(payload)
    return payload


__all__ = [
    "M0Baseline",
    "evaluate_prediction",
    "exact_semantic_oracle",
    "predict_null",
    "run_m0_harness",
]
