"""Two-generation scientific projection refinement benchmark.

CEGAR owns the refinement pattern.  This research-local module applies it to
future scientific-standing distinctions.  F0 begins with no lineage-coordinate
families, F1 is refined on three registered delayed-pair families, and an unseen
obligation-provenance family then forces F2 refinement.

Full reconstructive lineage is the fidelity ceiling throughout.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import importlib.util
from pathlib import Path
import random
import sys
from typing import Iterable


_CORE_PATH = Path(__file__).resolve().with_name("successor_conditioned_core.py")
_SPEC = importlib.util.spec_from_file_location("successor_conditioned_core_for_projection", _CORE_PATH)
sc = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = sc
_SPEC.loader.exec_module(sc)


class Coordinate(str, Enum):
    EVIDENCE_ROUTE = "EVIDENCE_ROUTE"
    NEGATIVE_CAUSE = "NEGATIVE_CAUSE"
    AUTHORITY_ORIGIN = "AUTHORITY_ORIGIN"
    OBLIGATION_PROVENANCE = "OBLIGATION_PROVENANCE"


@dataclass(frozen=True)
class ConcreteRecord:
    record_id: str
    family_id: str
    current_answer: str
    current_standing: str
    current_object_kind: str
    future_kind: str
    future_target: str
    lineage: tuple[tuple[Coordinate, str], ...]
    protected_future_standing: str

    def lineage_map(self) -> dict[Coordinate, str]:
        return dict(self.lineage)

    def public_key(self) -> tuple[str, str, str, str, str]:
        return (
            self.current_answer,
            self.current_standing,
            self.current_object_kind,
            self.future_kind,
            self.future_target,
        )


@dataclass(frozen=True)
class ConcretePair:
    pair_id: str
    family_id: str
    left: ConcreteRecord
    right: ConcreteRecord

    def records(self) -> tuple[ConcreteRecord, ConcreteRecord]:
        return self.left, self.right


@dataclass(frozen=True)
class AbstractionSpec:
    coordinates: frozenset[Coordinate] = frozenset()

    def refine(self, coordinate: Coordinate) -> "AbstractionSpec":
        return AbstractionSpec(self.coordinates | {coordinate})

    def payload(self) -> tuple[str, ...]:
        return tuple(sorted(item.value for item in self.coordinates))


@dataclass(frozen=True)
class CegarStep:
    pair_id: str
    added_coordinate: Coordinate
    before: AbstractionSpec
    after: AbstractionSpec


@dataclass(frozen=True)
class CegarResult:
    spec: AbstractionSpec
    steps: tuple[CegarStep, ...]


def _opaque(seed: int, tag: str) -> str:
    return hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()[:16]


def _record_from_base(pair: sc.DelayedPair, variant: sc.DelayedVariant) -> ConcreteRecord:
    lineage: list[tuple[Coordinate, str]] = []
    history = variant.history
    if pair.family_id == "evidence_route_dependency_debt":
        value = "INDEPENDENT" if history.independent_evidence_route else "SCOPED"
        lineage.append((Coordinate.EVIDENCE_ROUTE, value))
    elif pair.family_id == "negative_cause_debt":
        if history.failure_cause.startswith("MISSING_OPERATOR:"):
            value = f"MISSING:{history.failure_cause.split(':', 1)[1]}"
        else:
            value = "HARD_INVARIANT"
        lineage.append((Coordinate.NEGATIVE_CAUSE, value))
    elif pair.family_id == "authority_origin_debt":
        value = (
            f"TRANSPORT:{history.transported_authority_target}"
            if history.transported_authority_target
            else f"SCOPED:{history.authority_scope}"
        )
        lineage.append((Coordinate.AUTHORITY_ORIGIN, value))
    else:
        raise ValueError(f"unregistered base family:{pair.family_id}")
    return ConcreteRecord(
        record_id=variant.variant_id,
        family_id=pair.family_id,
        current_answer=variant.current.current_answer,
        current_standing=variant.current.current_standing.value,
        current_object_kind=variant.current.object_kind,
        future_kind=variant.future.kind.value,
        future_target=variant.future.target,
        lineage=tuple(lineage),
        protected_future_standing=variant.protected_future_standing.value,
    )


def base_pairs(seed: int, per_family: int) -> tuple[ConcretePair, ...]:
    result: list[ConcretePair] = []
    for pair in sc.generate_pairs(seed=seed, per_family=per_family):
        result.append(
            ConcretePair(
                pair_id=pair.pair_id,
                family_id=pair.family_id,
                left=_record_from_base(pair, pair.left),
                right=_record_from_base(pair, pair.right),
            )
        )
    return tuple(result)


def obligation_pairs(seed: int, per_family: int) -> tuple[ConcretePair, ...]:
    family = "obligation_provenance_debt"
    result: list[ConcretePair] = []
    for index in range(per_family):
        pair_id = f"dpair-{_opaque(seed, family + ':' + str(index))}"
        answer = f"ans-{_opaque(seed + index, 'obligation-answer')}"
        future_target = f"goal-{_opaque(seed + index, 'new-goal')}"
        common = {
            "family_id": family,
            "current_answer": answer,
            "current_standing": "VERIFIED",
            "current_object_kind": "CLAIM",
            "future_kind": "CHANGE_OBJECTIVE",
            "future_target": future_target,
        }
        left = ConcreteRecord(
            record_id=f"v-{_opaque(seed + index, 'obligation-left')}",
            **common,
            lineage=((Coordinate.OBLIGATION_PROVENANCE, "OBJECTIVE_SCOPED"),),
            protected_future_standing="REOPENED",
        )
        right = ConcreteRecord(
            record_id=f"v-{_opaque(seed + index, 'obligation-right')}",
            **common,
            lineage=((Coordinate.OBLIGATION_PROVENANCE, "INDEPENDENT_STRONG"),),
            protected_future_standing="VERIFIED",
        )
        result.append(ConcretePair(pair_id, family, left, right))
    rng = random.Random(seed ^ 0x0B17)
    rng.shuffle(result)
    return tuple(result)


def abstraction_key(record: ConcreteRecord, spec: AbstractionSpec) -> tuple:
    lineage = record.lineage_map()
    selected = tuple(
        (coordinate.value, lineage.get(coordinate, "UNREGISTERED"))
        for coordinate in sorted(spec.coordinates, key=lambda item: item.value)
    )
    return record.public_key() + (selected,)


def pair_is_spuriously_merged(pair: ConcretePair, spec: AbstractionSpec) -> bool:
    return (
        abstraction_key(pair.left, spec) == abstraction_key(pair.right, spec)
        and pair.left.protected_future_standing != pair.right.protected_future_standing
    )


def differing_lineage_coordinates(pair: ConcretePair) -> tuple[Coordinate, ...]:
    left = pair.left.lineage_map()
    right = pair.right.lineage_map()
    all_coordinates = set(left) | set(right)
    return tuple(
        sorted(
            (coordinate for coordinate in all_coordinates if left.get(coordinate) != right.get(coordinate)),
            key=lambda item: item.value,
        )
    )


def next_counterexample(pairs: Iterable[ConcretePair], spec: AbstractionSpec) -> ConcretePair | None:
    for pair in pairs:
        if pair_is_spuriously_merged(pair, spec):
            return pair
    return None


def refine_from_counterexample(spec: AbstractionSpec, pair: ConcretePair) -> CegarStep:
    candidates = tuple(
        coordinate
        for coordinate in differing_lineage_coordinates(pair)
        if coordinate not in spec.coordinates
    )
    if not candidates:
        raise ValueError("counterexample has no unregistered distinguishing lineage coordinate")
    coordinate = candidates[0]
    after = spec.refine(coordinate)
    return CegarStep(pair.pair_id, coordinate, spec, after)


def cegar_refine(
    pairs: Iterable[ConcretePair],
    initial: AbstractionSpec | None = None,
) -> CegarResult:
    materialized = tuple(pairs)
    spec = initial or AbstractionSpec()
    steps: list[CegarStep] = []
    while True:
        pair = next_counterexample(materialized, spec)
        if pair is None:
            return CegarResult(spec, tuple(steps))
        step = refine_from_counterexample(spec, pair)
        spec = step.after
        steps.append(step)


def predict_from_projection(record: ConcreteRecord, spec: AbstractionSpec) -> str:
    lineage = record.lineage_map()
    if record.future_kind == sc.FutureKind.EXIT_REPRESENTATION_SCOPE.value:
        if Coordinate.EVIDENCE_ROUTE in spec.coordinates:
            return "REOPENED" if lineage.get(Coordinate.EVIDENCE_ROUTE) == "SCOPED" else record.current_standing
        return record.current_standing
    if record.future_kind == sc.FutureKind.ADD_OPERATOR.value:
        if Coordinate.NEGATIVE_CAUSE in spec.coordinates:
            value = lineage.get(Coordinate.NEGATIVE_CAUSE, "")
            return "REOPENED" if value == f"MISSING:{record.future_target}" else record.current_standing
        return record.current_standing
    if record.future_kind == sc.FutureKind.MIGRATE_SCHEMA.value:
        if Coordinate.AUTHORITY_ORIGIN in spec.coordinates:
            value = lineage.get(Coordinate.AUTHORITY_ORIGIN, "")
            return record.current_standing if value == f"TRANSPORT:{record.future_target}" else "REOPENED"
        return record.current_standing
    if record.future_kind == "CHANGE_OBJECTIVE":
        if Coordinate.OBLIGATION_PROVENANCE in spec.coordinates:
            value = lineage.get(Coordinate.OBLIGATION_PROVENANCE, "")
            return "REOPENED" if value == "OBJECTIVE_SCOPED" else record.current_standing
        return record.current_standing
    raise ValueError(f"unregistered future kind:{record.future_kind}")


def predict_from_full_lineage(record: ConcreteRecord) -> str:
    return predict_from_projection(
        record,
        AbstractionSpec(frozenset(Coordinate)),
    )


def evaluate_projection(pairs: Iterable[ConcretePair], spec: AbstractionSpec) -> dict:
    n = 0
    exact = 0
    per_family: dict[str, list[int]] = {}
    for pair in pairs:
        for record in pair.records():
            predicted = predict_from_projection(record, spec)
            correct = int(predicted == record.protected_future_standing)
            n += 1
            exact += correct
            per_family.setdefault(pair.family_id, []).append(correct)
    return {
        "n": n,
        "exact": exact,
        "accuracy": exact / n if n else 0.0,
        "coordinate_count": len(spec.coordinates),
        "coordinates": spec.payload(),
        "family_accuracy": {
            family: sum(values) / len(values)
            for family, values in sorted(per_family.items())
        },
    }


def evaluate_full_lineage(pairs: Iterable[ConcretePair]) -> dict:
    n = 0
    exact = 0
    for pair in pairs:
        for record in pair.records():
            n += 1
            exact += int(predict_from_full_lineage(record) == record.protected_future_standing)
    return {"n": n, "exact": exact, "accuracy": exact / n if n else 0.0}


def two_generation_experiment(
    *,
    f1_train_seed: int = 301,
    f1_holdout_seed: int = 401,
    f2_refine_seed: int = 501,
    f2_holdout_seed: int = 601,
    per_family: int = 5,
) -> dict:
    f1_train = base_pairs(f1_train_seed, per_family)
    f1_result = cegar_refine(f1_train)
    f1 = f1_result.spec

    f1_holdout = base_pairs(f1_holdout_seed, per_family)
    f1_holdout_score = evaluate_projection(f1_holdout, f1)

    new_family_before = obligation_pairs(f2_refine_seed, per_family)
    f1_on_new = evaluate_projection(new_family_before, f1)

    # Refine using development instances from the new family only.
    f2_result = cegar_refine(new_family_before, initial=f1)
    f2 = f2_result.spec

    f2_holdout_new = obligation_pairs(f2_holdout_seed, per_family)
    f2_holdout_all = base_pairs(f2_holdout_seed ^ 0x1234, per_family) + f2_holdout_new
    f2_new_score = evaluate_projection(f2_holdout_new, f2)
    f2_all_score = evaluate_projection(f2_holdout_all, f2)
    full_lineage_score = evaluate_full_lineage(f2_holdout_all)

    return {
        "f0_coordinate_count": 0,
        "f1_coordinates": f1.payload(),
        "f1_refinement_steps": [step.added_coordinate.value for step in f1_result.steps],
        "f1_holdout_accuracy": f1_holdout_score["accuracy"],
        "f1_new_family_accuracy_before_refinement": f1_on_new["accuracy"],
        "f2_coordinates": f2.payload(),
        "f2_refinement_steps": [step.added_coordinate.value for step in f2_result.steps],
        "f2_new_family_holdout_accuracy": f2_new_score["accuracy"],
        "f2_all_family_holdout_accuracy": f2_all_score["accuracy"],
        "full_lineage_holdout_accuracy": full_lineage_score["accuracy"],
        "f1_coordinate_count": len(f1.coordinates),
        "f2_coordinate_count": len(f2.coordinates),
    }
