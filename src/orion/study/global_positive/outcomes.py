"""Candidate outcome bundles. Numeric per-dimension reports are not authority."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from orion.study.global_positive.schema import FORBIDDEN_SCALAR_KEYS, digest, load_schema

ADOPTION_BOUNDARY = "V2_ADDITIVE"


class ObservationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


def _status(value: Any, field: str) -> ObservationStatus:
    if isinstance(value, ObservationStatus):
        return value
    try:
        return ObservationStatus(str(value))
    except ValueError as exc:
        raise ValueError(f"{field} must be PASS, FAIL or CANNOT_CHECK") from exc


@dataclass(frozen=True)
class DimensionObservation:
    dimension_id: str
    status: ObservationStatus
    delta: float | None

    def __post_init__(self) -> None:
        if self.status is ObservationStatus.CANNOT_CHECK and self.delta is not None:
            raise ValueError(
                f"{self.dimension_id}: CANNOT_CHECK cannot carry a numeric delta"
            )
        if self.status is not ObservationStatus.CANNOT_CHECK and self.delta is None:
            spec = load_schema().spec(self.dimension_id)
            if spec.direction.value != "fail_closed":
                raise ValueError(
                    f"{self.dimension_id}: observed status requires a delta"
                )


@dataclass(frozen=True)
class FamilyOutcome:
    family_id: str
    split_coverage: tuple[str, ...]
    observations: tuple[DimensionObservation, ...]

    def observation(self, dimension_id: str) -> DimensionObservation | None:
        for item in self.observations:
            if item.dimension_id == dimension_id:
                return item
        return None


@dataclass(frozen=True)
class NegativeHistoryRecord:
    failure_class: str
    candidate_digest: str
    terminal: str
    dimension_ids: tuple[str, ...]
    family_ids: tuple[str, ...]


@dataclass(frozen=True)
class NegativeHistory:
    records: tuple[NegativeHistoryRecord, ...]

    def recurrence_classes(self, failure_classes: tuple[str, ...]) -> tuple[str, ...]:
        harmful = {
            item.failure_class
            for item in self.records
            if item.terminal == "HARMFUL_REGRESSION"
        }
        return tuple(item for item in failure_classes if item in harmful)


@dataclass(frozen=True)
class CandidateOutcomeBundle:
    candidate_id: str
    candidate_digest: str
    family_outcomes: tuple[FamilyOutcome, ...]
    evaluator_integrity: ObservationStatus
    failure_classes: tuple[str, ...]
    extra_keys: tuple[str, ...] = ()

    @property
    def family_ids(self) -> tuple[str, ...]:
        return tuple(item.family_id for item in self.family_outcomes)

    def family(self, family_id: str) -> FamilyOutcome | None:
        for item in self.family_outcomes:
            if item.family_id == family_id:
                return item
        return None

    @property
    def scalar_compensation_keys(self) -> tuple[str, ...]:
        return tuple(key for key in self.extra_keys if key in FORBIDDEN_SCALAR_KEYS)


def observation(
    dimension_id: str,
    delta: float | None,
    *,
    status: ObservationStatus | str = ObservationStatus.PASS,
) -> DimensionObservation:
    return DimensionObservation(
        dimension_id=dimension_id,
        status=_status(status, dimension_id),
        delta=delta,
    )


def family_outcome(
    family_id: str,
    deltas: Mapping[str, float],
    *,
    split_coverage: tuple[str, ...] | None = None,
    cannot_check: tuple[str, ...] = (),
) -> FamilyOutcome:
    from orion.study.global_positive.portfolio import REQUIRED_SPLIT_IDS

    coverage = split_coverage if split_coverage is not None else REQUIRED_SPLIT_IDS
    schema = load_schema()
    observations: list[DimensionObservation] = []
    for spec in schema.dimensions:
        if spec.scope.value != "per_family":
            continue
        if spec.dimension_id in cannot_check:
            observations.append(
                DimensionObservation(
                    spec.dimension_id, ObservationStatus.CANNOT_CHECK, None
                )
            )
            continue
        if spec.dimension_id not in deltas:
            observations.append(
                DimensionObservation(
                    spec.dimension_id, ObservationStatus.CANNOT_CHECK, None
                )
            )
            continue
        observations.append(
            DimensionObservation(
                spec.dimension_id,
                ObservationStatus.PASS,
                float(deltas[spec.dimension_id]),
            )
        )
    return FamilyOutcome(family_id, tuple(coverage), tuple(observations))


def bundle_from_mapping(payload: Mapping[str, Any]) -> CandidateOutcomeBundle:
    extra = tuple(sorted(str(key) for key in payload if key in FORBIDDEN_SCALAR_KEYS))
    families_raw = payload.get("family_outcomes", ())
    families: list[FamilyOutcome] = []
    for item in families_raw:
        if not isinstance(item, Mapping):
            raise ValueError("family_outcomes entries must be objects")
        deltas = item.get("deltas", {})
        if not isinstance(deltas, Mapping):
            raise ValueError("deltas must be an object")
        families.append(
            family_outcome(
                str(item["family_id"]),
                {str(key): float(value) for key, value in deltas.items()},
                split_coverage=tuple(item.get("split_coverage", ())),
                cannot_check=tuple(item.get("cannot_check", ())),
            )
        )
    digest_value = payload.get("candidate_digest")
    candidate_id = str(payload.get("candidate_id", ""))
    if not digest_value:
        digest_value = digest({"candidate_id": candidate_id, "families": list(payload.get("family_ids", ()))})
    return CandidateOutcomeBundle(
        candidate_id=candidate_id,
        candidate_digest=str(digest_value),
        family_outcomes=tuple(families),
        evaluator_integrity=_status(
            payload.get("evaluator_integrity", "CANNOT_CHECK"),
            "evaluator_integrity",
        ),
        failure_classes=tuple(payload.get("failure_classes", ())),
        extra_keys=extra,
    )
