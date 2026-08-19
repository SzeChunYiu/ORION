"""Exact responsibility diagnosis for partially observed P9 affine transports.

This module is a model-independent successor to the closed P9 D0 transport atom.
The previous result showed that once affine transport parameters are visible,
exact composition is sufficient. S1 asks an upstream question instead: whether
a local transform is currently licensed for composition, requires more
measurement, has become stale relative to an admitted historical estimate, or
cannot be identified using the declared probes.

V1 is deliberately exact/noiseless. It contains no neural model, no training
loop, and no scientific/adoption authority. Evaluator-only truth and gold are
kept in separate case objects and are excluded from candidate fingerprints.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
import math
from typing import Iterable, Sequence

from orion.transfer.v2.canonical import content_digest

from .structural_world import (
    AffineTransport,
    Atom,
    AtomType,
    GluingVerdict,
    GoldKind,
    GoldTarget,
    P9StructuralWorld,
    classify_cycle_gluing,
)


_ABS_TOL = 1e-9


def _finite(value: float, *, what: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{what} must be finite")


def _close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=_ABS_TOL)


class TransformResponsibility(str, Enum):
    IDENTIFIABLE_NOW = "IDENTIFIABLE_NOW"
    NEEDS_MORE_MEASUREMENTS = "NEEDS_MORE_MEASUREMENTS"
    CHANGED_SINCE_ESTIMATE = "CHANGED_SINCE_ESTIMATE"
    NONIDENTIFIABLE_UNDER_AVAILABLE_PROBES = "NONIDENTIFIABLE_UNDER_AVAILABLE_PROBES"


@dataclass(frozen=True)
class AffineObservation:
    x: float
    y: float

    def verify(self) -> None:
        _finite(self.x, what="observation x")
        _finite(self.y, what="observation y")


@dataclass(frozen=True)
class AffineEstimate:
    scale: float
    offset: float

    def verify(self) -> None:
        _finite(self.scale, what="affine scale")
        _finite(self.offset, what="affine offset")

    def apply(self, x: float) -> float:
        _finite(x, what="affine input")
        return self.scale * x + self.offset

    def is_compatible(self, observation: AffineObservation) -> bool:
        observation.verify()
        return _close(self.apply(observation.x), observation.y)


@dataclass(frozen=True)
class HiddenAffineMap:
    """Evaluator-only true local map. Never appears in a candidate payload."""

    scale: float
    offset: float

    def verify(self) -> None:
        _finite(self.scale, what="hidden affine scale")
        _finite(self.offset, what="hidden affine offset")

    def apply(self, x: float) -> float:
        self.verify()
        _finite(x, what="hidden affine input")
        return self.scale * x + self.offset

    def as_estimate(self) -> AffineEstimate:
        self.verify()
        return AffineEstimate(scale=self.scale, offset=self.offset)


@dataclass(frozen=True)
class CandidateProbe:
    probe_id: str
    x: float
    cost: float

    def verify(self) -> None:
        if not self.probe_id:
            raise ValueError("probe id is required")
        _finite(self.x, what="probe x")
        _finite(self.cost, what="probe cost")
        if self.cost < 0:
            raise ValueError("probe cost must be non-negative")


@dataclass(frozen=True)
class ObservedAffineTransform:
    """Candidate-visible local transform state.

    `historical_estimate`, when present, is treated as a previously admitted
    estimate. Its continued validity is tested only against current visible
    observations; no hidden change bit exists in this object.
    """

    transform_id: str
    source_chart_id: str
    target_chart_id: str
    observations: tuple[AffineObservation, ...] = ()
    candidate_probes: tuple[CandidateProbe, ...] = ()
    historical_estimate: AffineEstimate | None = None

    def verify(self) -> None:
        if not self.transform_id:
            raise ValueError("transform id is required")
        if not self.source_chart_id or not self.target_chart_id:
            raise ValueError("transform chart endpoints are required")
        if self.source_chart_id == self.target_chart_id:
            raise ValueError("transform endpoints must be distinct")
        for observation in self.observations:
            observation.verify()
        seen_probe_ids: set[str] = set()
        for probe in self.candidate_probes:
            probe.verify()
            if probe.probe_id in seen_probe_ids:
                raise ValueError(f"duplicate probe id: {probe.probe_id}")
            seen_probe_ids.add(probe.probe_id)
        if self.historical_estimate is not None:
            self.historical_estimate.verify()

    def candidate_payload(self) -> dict[str, object]:
        """Canonical model-visible payload; tuple order is not information."""

        self.verify()
        observations = sorted((item.x, item.y) for item in self.observations)
        probes = sorted(
            ((item.probe_id, item.x, item.cost) for item in self.candidate_probes),
            key=lambda item: (item[0], item[1], item[2]),
        )
        historical = None
        if self.historical_estimate is not None:
            historical = [
                self.historical_estimate.scale,
                self.historical_estimate.offset,
            ]
        return {
            "schema": "P9.S1.ObservedAffineTransform.v1",
            "transform_id": self.transform_id,
            "source_chart_id": self.source_chart_id,
            "target_chart_id": self.target_chart_id,
            "observations": [[x, y] for x, y in observations],
            "candidate_probes": [[probe_id, x, cost] for probe_id, x, cost in probes],
            "historical_estimate": historical,
        }

    def candidate_fingerprint(self) -> str:
        return content_digest(self.candidate_payload())


@dataclass(frozen=True)
class LocalTransformCase:
    """Evaluator record joining candidate-visible state to hidden truth/gold."""

    case_id: str
    observed: ObservedAffineTransform
    truth: HiddenAffineMap
    gold_responsibility: TransformResponsibility

    def verify(self) -> None:
        if not self.case_id:
            raise ValueError("case id is required")
        self.observed.verify()
        self.truth.verify()
        for observation in self.observed.observations:
            if not _close(self.truth.apply(observation.x), observation.y):
                raise ValueError("observation is incompatible with evaluator true map")
        derived = classify_transform_responsibility(self.observed)
        if derived is not self.gold_responsibility:
            raise ValueError(
                "gold responsibility disagrees with candidate-visible exact semantics: "
                f"derived={derived.value} gold={self.gold_responsibility.value}"
            )

    def candidate_payload(self) -> dict[str, object]:
        # Deliberately does not call self.verify(): evaluator truth/gold can be
        # mutated in hostile leakage tests without changing the model projection.
        return self.observed.candidate_payload()

    def candidate_fingerprint(self) -> str:
        return content_digest(self.candidate_payload())


@dataclass(frozen=True)
class TransformCycleCase:
    """Evaluator record for one directed cycle of candidate-visible transforms."""

    cycle_id: str
    edges: tuple[ObservedAffineTransform, ...]
    hidden_truth: tuple[HiddenAffineMap, ...]
    gold_if_fully_known: GluingVerdict

    def verify_visible_cycle(self) -> tuple[str, ...]:
        if not self.cycle_id:
            raise ValueError("cycle id is required")
        if len(self.edges) < 2:
            raise ValueError("cycle needs at least two edges")
        for edge in self.edges:
            edge.verify()
        charts = [self.edges[0].source_chart_id, self.edges[0].target_chart_id]
        for previous, current in zip(self.edges, self.edges[1:], strict=False):
            if previous.target_chart_id != current.source_chart_id:
                raise ValueError("cycle edges are not endpoint-contiguous")
            charts.append(current.target_chart_id)
        if self.edges[-1].target_chart_id != self.edges[0].source_chart_id:
            raise ValueError("last cycle edge must close to the first source chart")
        return tuple(charts)

    def verify(self) -> None:
        chart_cycle = self.verify_visible_cycle()
        if self.gold_if_fully_known not in {
            GluingVerdict.GLUE,
            GluingVerdict.OBSTRUCTION,
            GluingVerdict.UNKNOWN,
        }:
            raise ValueError("invalid fully-known gluing gold")
        if self.hidden_truth and len(self.hidden_truth) != len(self.edges):
            raise ValueError("hidden truth must be empty or align one-to-one with cycle edges")
        for truth in self.hidden_truth:
            truth.verify()

        if self.hidden_truth:
            for edge, truth in zip(self.edges, self.hidden_truth, strict=True):
                for observation in edge.observations:
                    if not _close(truth.apply(observation.x), observation.y):
                        raise ValueError(
                            "hidden truth is incompatible with a visible observation"
                        )
            hidden_verdict = _classify_cycle_from_estimates(
                self.edges,
                tuple(truth.as_estimate() for truth in self.hidden_truth),
                chart_cycle,
            )
            if hidden_verdict is not self.gold_if_fully_known:
                raise ValueError(
                    "fully-known gold disagrees with exact composition of hidden truth: "
                    f"computed={hidden_verdict.value} gold={self.gold_if_fully_known.value}"
                )

    def candidate_payload(self) -> dict[str, object]:
        self.verify_visible_cycle()
        return {
            "schema": "P9.S1.TransformCycle.v1",
            "edges": [edge.candidate_payload() for edge in self.edges],
        }

    def candidate_fingerprint(self) -> str:
        return content_digest(self.candidate_payload())


def _distinct_x(observations: Iterable[AffineObservation]) -> tuple[float, ...]:
    return tuple(sorted({float(item.x) for item in observations}))


def infer_exact_affine(
    observations: Iterable[AffineObservation],
) -> AffineEstimate | None:
    """Return the unique exact affine map, or None when observations underdetermine it.

    An inconsistent exact observation set is a model-family/data-integrity error,
    not an `UNKNOWN` answer, and therefore raises ValueError.
    """

    items = tuple(observations)
    for item in items:
        item.verify()
    distinct = _distinct_x(items)
    if len(distinct) < 2:
        for x in distinct:
            ys = [item.y for item in items if _close(item.x, x)]
            if ys and any(not _close(value, ys[0]) for value in ys[1:]):
                raise ValueError("inconsistent exact observations at the same x")
        return None

    x0, x1 = distinct[0], distinct[1]
    y0_values = [item.y for item in items if _close(item.x, x0)]
    y1_values = [item.y for item in items if _close(item.x, x1)]
    if any(not _close(value, y0_values[0]) for value in y0_values[1:]):
        raise ValueError("inconsistent exact observations at first identifying x")
    if any(not _close(value, y1_values[0]) for value in y1_values[1:]):
        raise ValueError("inconsistent exact observations at second identifying x")

    scale = (y1_values[0] - y0_values[0]) / (x1 - x0)
    offset = y0_values[0] - scale * x0
    estimate = AffineEstimate(scale=scale, offset=offset)
    estimate.verify()
    if any(not estimate.is_compatible(item) for item in items):
        raise ValueError("exact observations are inconsistent with one affine map")
    return estimate


def _historical_changed(edge: ObservedAffineTransform) -> bool:
    if edge.historical_estimate is None:
        return False
    return any(
        not edge.historical_estimate.is_compatible(observation)
        for observation in edge.observations
    )


def minimal_identifying_probe_ids(edge: ObservedAffineTransform) -> tuple[str, ...]:
    """Minimum-cost declared probe subset that would make an affine map identifiable.

    Probe outputs are not known yet; only distinct input x-values matter for exact
    affine identifiability. Ties are broken lexicographically by probe id tuple.
    """

    edge.verify()
    if edge.historical_estimate is not None and not _historical_changed(edge):
        return ()
    if infer_exact_affine(edge.observations) is not None:
        return ()

    observed_x = set(_distinct_x(edge.observations))
    probes = tuple(sorted(edge.candidate_probes, key=lambda item: item.probe_id))
    candidates: list[tuple[float, tuple[str, ...]]] = []
    for size in range(1, len(probes) + 1):
        for subset in combinations(probes, size):
            combined_x = observed_x | {float(probe.x) for probe in subset}
            if len(combined_x) < 2:
                continue
            ids = tuple(sorted(probe.probe_id for probe in subset))
            candidates.append((sum(probe.cost for probe in subset), ids))
    if not candidates:
        return ()
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][1]


def classify_transform_responsibility(
    edge: ObservedAffineTransform,
) -> TransformResponsibility:
    edge.verify()
    if edge.historical_estimate is not None:
        if _historical_changed(edge):
            return TransformResponsibility.CHANGED_SINCE_ESTIMATE
        return TransformResponsibility.IDENTIFIABLE_NOW

    if infer_exact_affine(edge.observations) is not None:
        return TransformResponsibility.IDENTIFIABLE_NOW
    if minimal_identifying_probe_ids(edge):
        return TransformResponsibility.NEEDS_MORE_MEASUREMENTS
    return TransformResponsibility.NONIDENTIFIABLE_UNDER_AVAILABLE_PROBES


def admitted_estimate(edge: ObservedAffineTransform) -> AffineEstimate | None:
    """Return the currently licensed local estimate, never a guessed map."""

    responsibility = classify_transform_responsibility(edge)
    if responsibility is not TransformResponsibility.IDENTIFIABLE_NOW:
        return None
    if edge.historical_estimate is not None:
        return edge.historical_estimate
    return infer_exact_affine(edge.observations)


def _classify_cycle_from_estimates(
    edges: Sequence[ObservedAffineTransform],
    estimates: Sequence[AffineEstimate],
    chart_cycle: Sequence[str],
) -> GluingVerdict:
    """Use the original P9 exact affine-cycle evaluator without consulting case gold."""

    if len(edges) != len(estimates):
        raise ValueError("cycle edge/estimate lengths differ")
    chart_ids = tuple(dict.fromkeys(chart_cycle[:-1]))
    atoms = tuple(Atom(chart_id, AtomType.REPRESENTATION, chart_id) for chart_id in chart_ids)
    transports = tuple(
        AffineTransport(
            transport_id=edge.transform_id,
            source_chart_id=edge.source_chart_id,
            target_chart_id=edge.target_chart_id,
            scale=estimate.scale,
            offset=estimate.offset,
        )
        for edge, estimate in zip(edges, estimates, strict=True)
    )
    world = P9StructuralWorld(
        world_id="p9-s1-cycle-evaluator",
        atoms=atoms,
        relations=(),
        transports=transports,
        mechanics=(),
        history=(),
        # Gold is structurally required by P9StructuralWorld but is deliberately
        # constant here; classify_cycle_gluing does not consult it.
        gold=GoldTarget(GoldKind.GLUING, GluingVerdict.UNKNOWN.value),
    )
    return classify_cycle_gluing(world, chart_cycle)


def resolve_visible_cycle(case: TransformCycleCase) -> GluingVerdict:
    """Resolve a cycle only when every local operand is currently admitted."""

    chart_cycle = case.verify_visible_cycle()
    estimates = tuple(admitted_estimate(edge) for edge in case.edges)
    if any(estimate is None for estimate in estimates):
        return GluingVerdict.UNKNOWN
    admitted = tuple(estimate for estimate in estimates if estimate is not None)
    return _classify_cycle_from_estimates(case.edges, admitted, chart_cycle)
