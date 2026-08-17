"""Search-universe layer: versioned `W`, its coverage obligations and its blind spots.

Extends ``orion.core.search_universe.SearchUniverseState``, which already holds
the domain/route/representation id sets. What that state cannot express is the
difference between a route that was walked and found empty and a route that was
never attempted — and that difference is the whole of saturation. So this record
adds typed route availability, coverage obligations per source family, explicit
blind-spot tests, and the reopen rules that re-open `W` when a new domain,
route or representation appears.

Saturation is a claim that must be earned. ``saturation_claimed`` is inert on its
own: :func:`validate_search_universe_record` refuses it unless every obligation
is discharged and every blind-spot test has actually run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from orion.programme.coordinates import coordinate_errors
from orion.programme.identity import SEARCH_UNIVERSE_KNOWLEDGE_SCHEMA, seal
from orion.programme.records import (
    Outcome,
    RouteAvailability,
    dedup,
    required_ids_errors,
    required_text_errors,
)


@dataclass(frozen=True)
class RouteState:
    """One route of one source family, with its typed availability."""

    route_id: str
    route_kind_id: str
    source_family: str
    availability: RouteAvailability
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.route_id.strip() or not self.route_kind_id.strip():
            raise ValueError("route identity is required")
        if self.availability is not RouteAvailability.AVAILABLE and not self.reason.strip():
            raise ValueError("a non-available route must carry a reason")


@dataclass(frozen=True)
class CoverageObligation:
    """A source family / domain the universe is obliged to cover before closing."""

    obligation_id: str
    source_family: str
    domain_id: str
    required_route_kind_ids: tuple[str, ...]
    discharged: bool = False
    discharging_evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class BlindSpotTest:
    """A test that tries to show the search was falsely flat.

    Outcome ``PASS`` means the test ran and found no blind spot. ``CANNOT_CHECK``
    means it did not run — which is not evidence of coverage and must not be
    read as one.
    """

    test_id: str
    description: str
    outcome: Outcome = Outcome.CANNOT_CHECK
    finding: str = ""


@dataclass(frozen=True)
class ReopenRule:
    """When a discovery must reopen this universe."""

    rule_id: str
    trigger_kind: str
    coordinate: str
    description: str


@dataclass(frozen=True)
class SearchUniverseKnowledgeRecord:
    """Versioned `W` state plus the obligations that make its closure falsifiable."""

    universe_id: str
    universe_version: int
    active_domain_ids: tuple[str, ...]
    routes: tuple[RouteState, ...]
    representation_ids: tuple[str, ...]
    obligations: tuple[CoverageObligation, ...]
    blind_spot_tests: tuple[BlindSpotTest, ...]
    reopen_rules: tuple[ReopenRule, ...]
    depends_on_coordinates: tuple[str, ...] = ("W",)
    candidate_domain_ids: tuple[str, ...] = ()
    saturation_claimed: bool = False
    saturation_basis_digest: str | None = None
    open_coverage_residual_ids: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.universe_version < 1:
            raise ValueError("universe_version starts at 1")

    @property
    def source_families(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(route.source_family for route in self.routes))

    @property
    def unattempted_route_ids(self) -> tuple[str, ...]:
        return tuple(
            route.route_id
            for route in self.routes
            if route.availability is RouteAvailability.NOT_ATTEMPTED
        )


def search_universe_payload(record: SearchUniverseKnowledgeRecord) -> dict[str, Any]:
    """Serialize one record to the sealed wire form."""

    return seal(
        {
            "schema_version": SEARCH_UNIVERSE_KNOWLEDGE_SCHEMA,
            "universe_id": record.universe_id,
            "universe_version": record.universe_version,
            "active_domain_ids": list(record.active_domain_ids),
            "candidate_domain_ids": list(record.candidate_domain_ids),
            "representation_ids": list(record.representation_ids),
            "routes": [
                {
                    "route_id": route.route_id,
                    "route_kind_id": route.route_kind_id,
                    "source_family": route.source_family,
                    "availability": route.availability.value,
                    "reason": route.reason,
                }
                for route in record.routes
            ],
            "obligations": [
                {
                    "obligation_id": item.obligation_id,
                    "source_family": item.source_family,
                    "domain_id": item.domain_id,
                    "required_route_kind_ids": list(item.required_route_kind_ids),
                    "discharged": item.discharged,
                    "discharging_evidence_ids": list(item.discharging_evidence_ids),
                }
                for item in record.obligations
            ],
            "blind_spot_tests": [
                {
                    "test_id": test.test_id,
                    "description": test.description,
                    "outcome": test.outcome.value,
                    "finding": test.finding,
                }
                for test in record.blind_spot_tests
            ],
            "reopen_rules": [
                {
                    "rule_id": rule.rule_id,
                    "trigger_kind": rule.trigger_kind,
                    "coordinate": rule.coordinate,
                    "description": rule.description,
                }
                for rule in record.reopen_rules
            ],
            "depends_on_coordinates": list(record.depends_on_coordinates),
            "saturation_claimed": record.saturation_claimed,
            "saturation_basis_digest": record.saturation_basis_digest,
            "open_coverage_residual_ids": list(record.open_coverage_residual_ids),
            "metadata": [list(pair) for pair in record.metadata],
        }
    )


def validate_search_universe_record(
    record: SearchUniverseKnowledgeRecord,
) -> tuple[str, ...]:
    """Return deduplicated blockers for one versioned search universe."""

    errors: list[str] = []
    errors.extend(required_text_errors(record.universe_id, "universe_id"))
    errors.extend(required_ids_errors(record.active_domain_ids, "active_domain_ids"))
    errors.extend(coordinate_errors(record.depends_on_coordinates, "depends_on_coordinates"))

    if not record.routes:
        errors.append("a search universe must enumerate its routes")
    if not record.obligations:
        errors.append("a search universe must declare its coverage obligations")
    if not record.reopen_rules:
        errors.append(
            "a search universe with no reopen rule can never be reopened, which"
            " makes its closure permanent by construction"
        )

    route_kinds = {route.route_kind_id for route in record.routes}
    for obligation in record.obligations:
        missing = [kind for kind in obligation.required_route_kind_ids if kind not in route_kinds]
        if missing:
            errors.append(
                f"obligation {obligation.obligation_id} requires route kinds absent"
                f" from the universe: {sorted(missing)}"
            )
        if obligation.discharged and not obligation.discharging_evidence_ids:
            errors.append(
                f"obligation {obligation.obligation_id} is marked discharged with"
                " no discharging evidence"
            )

    if record.saturation_claimed:
        errors.extend(_saturation_errors(record))

    return dedup(errors)


def _saturation_errors(record: SearchUniverseKnowledgeRecord) -> list[str]:
    errors: list[str] = []
    if record.saturation_basis_digest is None:
        errors.append("a saturation claim requires a recorded basis digest")
    undischarged = [item.obligation_id for item in record.obligations if not item.discharged]
    if undischarged:
        errors.append(f"saturation claimed with undischarged obligations: {sorted(undischarged)}")
    if record.unattempted_route_ids:
        errors.append(
            "saturation claimed while routes remain NOT_ATTEMPTED:"
            f" {sorted(record.unattempted_route_ids)}"
        )
    if not record.blind_spot_tests:
        errors.append("saturation claimed with no blind-spot test")
    unrun = [test.test_id for test in record.blind_spot_tests
             if test.outcome is Outcome.CANNOT_CHECK]
    if unrun:
        errors.append(f"saturation claimed with blind-spot tests that did not run: {sorted(unrun)}")
    found = [test.test_id for test in record.blind_spot_tests if test.outcome is Outcome.FAIL]
    if found:
        errors.append(f"saturation claimed while blind spots stand open: {sorted(found)}")
    if record.open_coverage_residual_ids:
        errors.append("saturation claimed with open coverage residuals")
    return errors


__all__ = [
    "BlindSpotTest",
    "CoverageObligation",
    "ReopenRule",
    "RouteState",
    "SearchUniverseKnowledgeRecord",
    "search_universe_payload",
    "validate_search_universe_record",
]
