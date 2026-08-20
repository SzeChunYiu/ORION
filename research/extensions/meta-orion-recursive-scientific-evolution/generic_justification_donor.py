"""Generic proof/justification-relevant donor for future scientific standing.

The donor is intentionally strong.  It uses a fixed, family-agnostic condition
interpreter over future transition events.  DPAIR-4 reuses an existing condition
operator rather than extending the interpreter after outcome access.

This module is a subtraction baseline: if it closes the exact families, ORION's
bespoke coordinate-refinement effect is not an incremental representation claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import importlib.util
from pathlib import Path
import sys
from typing import Iterable


_CORE_PATH = Path(__file__).resolve().with_name("projection_evolution_core.py")
_SPEC = importlib.util.spec_from_file_location("projection_evolution_core_for_donor", _CORE_PATH)
pe = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = pe
_SPEC.loader.exec_module(pe)


class ConditionKind(str, Enum):
    ALWAYS_VALID = "ALWAYS_VALID"
    INVALIDATE_ON_EVENT = "INVALIDATE_ON_EVENT"
    INVALIDATE_WHEN_EVENT_TARGET = "INVALIDATE_WHEN_EVENT_TARGET"
    VALID_ONLY_FOR_EVENT_TARGET = "VALID_ONLY_FOR_EVENT_TARGET"


@dataclass(frozen=True)
class ValidityCondition:
    kind: ConditionKind
    event_kind: str = ""
    target: str = ""


@dataclass(frozen=True)
class StandingJustification:
    current_standing: str
    condition: ValidityCondition


def compile_justification(record: pe.ConcreteRecord) -> StandingJustification:
    """Compile raw lineage into the fixed generic condition language.

    The compiler is frozen for all registered lineage kinds before held-out
    evaluation.  Crucially, obligation provenance reuses INVALIDATE_ON_EVENT,
    the same operator used for representation-scoped evidence.
    """
    lineage = record.lineage_map()

    if pe.Coordinate.EVIDENCE_ROUTE in lineage:
        route = lineage[pe.Coordinate.EVIDENCE_ROUTE]
        condition = (
            ValidityCondition(
                ConditionKind.INVALIDATE_ON_EVENT,
                event_kind=pe.sc.FutureKind.EXIT_REPRESENTATION_SCOPE.value,
            )
            if route == "SCOPED"
            else ValidityCondition(ConditionKind.ALWAYS_VALID)
        )
        return StandingJustification(record.current_standing, condition)

    if pe.Coordinate.NEGATIVE_CAUSE in lineage:
        cause = lineage[pe.Coordinate.NEGATIVE_CAUSE]
        if cause.startswith("MISSING:"):
            capability = cause.split(":", 1)[1]
            return StandingJustification(
                record.current_standing,
                ValidityCondition(
                    ConditionKind.INVALIDATE_WHEN_EVENT_TARGET,
                    event_kind=pe.sc.FutureKind.ADD_OPERATOR.value,
                    target=capability,
                ),
            )
        return StandingJustification(
            record.current_standing,
            ValidityCondition(ConditionKind.ALWAYS_VALID),
        )

    if pe.Coordinate.AUTHORITY_ORIGIN in lineage:
        origin = lineage[pe.Coordinate.AUTHORITY_ORIGIN]
        if origin.startswith("TRANSPORT:"):
            target = origin.split(":", 1)[1]
            return StandingJustification(
                record.current_standing,
                ValidityCondition(
                    ConditionKind.VALID_ONLY_FOR_EVENT_TARGET,
                    event_kind=pe.sc.FutureKind.MIGRATE_SCHEMA.value,
                    target=target,
                ),
            )
        return StandingJustification(
            record.current_standing,
            ValidityCondition(
                ConditionKind.INVALIDATE_ON_EVENT,
                event_kind=pe.sc.FutureKind.MIGRATE_SCHEMA.value,
            ),
        )

    if pe.Coordinate.OBLIGATION_PROVENANCE in lineage:
        provenance = lineage[pe.Coordinate.OBLIGATION_PROVENANCE]
        condition = (
            ValidityCondition(
                ConditionKind.INVALIDATE_ON_EVENT,
                event_kind="CHANGE_OBJECTIVE",
            )
            if provenance == "OBJECTIVE_SCOPED"
            else ValidityCondition(ConditionKind.ALWAYS_VALID)
        )
        return StandingJustification(record.current_standing, condition)

    raise ValueError("record has no registered justification-bearing lineage")


def condition_remains_valid(condition: ValidityCondition, record: pe.ConcreteRecord) -> bool:
    if condition.kind is ConditionKind.ALWAYS_VALID:
        return True
    if condition.kind is ConditionKind.INVALIDATE_ON_EVENT:
        return record.future_kind != condition.event_kind
    if condition.kind is ConditionKind.INVALIDATE_WHEN_EVENT_TARGET:
        return not (
            record.future_kind == condition.event_kind
            and record.future_target == condition.target
        )
    if condition.kind is ConditionKind.VALID_ONLY_FOR_EVENT_TARGET:
        if record.future_kind != condition.event_kind:
            return True
        return record.future_target == condition.target
    raise AssertionError(f"unhandled condition kind:{condition.kind}")


def predict_future_standing(record: pe.ConcreteRecord) -> str:
    justification = compile_justification(record)
    return (
        justification.current_standing
        if condition_remains_valid(justification.condition, record)
        else "REOPENED"
    )


def evaluate(pairs: Iterable[pe.ConcretePair]) -> dict:
    n = 0
    exact = 0
    family_counts: dict[str, list[int]] = {}
    condition_kinds: set[str] = set()
    for pair in pairs:
        for record in pair.records():
            justification = compile_justification(record)
            condition_kinds.add(justification.condition.kind.value)
            predicted = predict_future_standing(record)
            correct = int(predicted == record.protected_future_standing)
            n += 1
            exact += correct
            family_counts.setdefault(pair.family_id, []).append(correct)
    return {
        "n": n,
        "exact": exact,
        "accuracy": exact / n if n else 0.0,
        "condition_kinds_used": tuple(sorted(condition_kinds)),
        "family_accuracy": {
            family: sum(values) / len(values)
            for family, values in sorted(family_counts.items())
        },
    }


def subtraction_experiment(
    *,
    base_train_seed: int = 811,
    new_family_seed: int = 821,
    holdout_seed: int = 823,
    per_family: int = 6,
) -> dict:
    # Bespoke F1 is trained/refined only on the first three families.
    f1 = pe.cegar_refine(pe.base_pairs(base_train_seed, per_family)).spec
    unseen = pe.obligation_pairs(new_family_seed, per_family)
    f1_unseen = pe.evaluate_projection(unseen, f1)

    # Donor interpreter is frozen and evaluated on disjoint all-family holdout.
    holdout = pe.base_pairs(holdout_seed, per_family) + pe.obligation_pairs(
        holdout_seed ^ 0x77,
        per_family,
    )
    donor = evaluate(holdout)
    return {
        "f1_coordinate_count": len(f1.coordinates),
        "f1_unseen_obligation_accuracy": f1_unseen["accuracy"],
        "donor_all_family_accuracy": donor["accuracy"],
        "donor_condition_kinds_used": donor["condition_kinds_used"],
        "terminal_if_verified": (
            "GENERIC_JUSTIFICATION_DONOR_SUFFICIENT"
            if donor["accuracy"] == 1.0 and f1_unseen["accuracy"] < 1.0
            else "CANNOT_CHECK"
        ),
    }
