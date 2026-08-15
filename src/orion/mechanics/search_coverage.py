from __future__ import annotations

from dataclasses import dataclass, replace

from orion.core.search import SearchRouteKind

from .model import MechanicCell


@dataclass(frozen=True)
class CoverageRouteObligation:
    obligation_id: str
    mechanic_id: str
    route_kind: SearchRouteKind
    applicability: str
    independence_intent: str
    completion_evidence: str
    failure_semantics: str

    def __post_init__(self) -> None:
        required = (
            self.obligation_id,
            self.mechanic_id,
            self.applicability,
            self.independence_intent,
            self.completion_evidence,
            self.failure_semantics,
        )
        if any(not item.strip() for item in required):
            raise ValueError("search coverage obligation fields cannot be empty")


@dataclass(frozen=True)
class MechanicSearchCoveragePlan:
    mechanic_id: str
    obligations: tuple[CoverageRouteObligation, ...]
    route_independence_rule: str
    coverage_claim_boundary: str

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.obligations or not self.route_independence_rule.strip() or not self.coverage_claim_boundary.strip():
            raise ValueError("search coverage plan requires identity/obligations/independence/boundary")
        ids = [item.obligation_id for item in self.obligations]
        if len(set(ids)) != len(ids):
            raise ValueError("search coverage obligation ids must be unique")


def _obligation(cell: MechanicCell, kind: SearchRouteKind, applicability: str, independence: str, evidence: str) -> CoverageRouteObligation:
    return CoverageRouteObligation(
        obligation_id=f"coverage:{cell.mechanic_id}:{kind.value.lower()}",
        mechanic_id=cell.mechanic_id,
        route_kind=kind,
        applicability=applicability,
        independence_intent=independence,
        completion_evidence=evidence,
        failure_semantics="If applicable coverage is unrun, unstable or reveals a new material coordinate, the mechanic knowledge basis remains OPEN and any dependent saturation claim must reopen.",
    )


def default_search_coverage_plan(cell: MechanicCell) -> MechanicSearchCoveragePlan:
    """OWMD-derived route contract for researching one mechanic.

    This declares what route families must be challenged. It does not assert that any
    route has actually executed or that the route set is globally exhaustive.
    """

    specs = (
        (SearchRouteKind.CURRENT_VOCABULARY, "always", "recover direct nearest work without renaming the problem", "query/result/source ledger"),
        (SearchRouteKind.LEXICAL_VARIANT, "always", "reduce dependence on one terminology choice", "distinct lexical/paraphrase query ledger"),
        (SearchRouteKind.FUNCTION_ONLY, "always", "remove current framework/domain labels and search by I/O/constraints/dynamics/failure signature", "withheld-vocabulary/function-signature query receipt"),
        (SearchRouteKind.PARENT_DISCIPLINE, "always", "ask which mature fields own the operation as a canonical problem", "candidate-domain search and assimilation ledger"),
        (SearchRouteKind.HISTORICAL_PRECURSOR, "when the operation has a plausible pre-LLM/pre-current-field history", "escape recency and current-fashion bias", "historical terminology/source receipt or justified inapplicability"),
        (SearchRouteKind.MATHEMATICAL_EQUIVALENT, "when a mathematical/structural formulation exists", "search equivalent formal objects rather than labels", "formal-object/equivalence search receipt or justified inapplicability"),
        (SearchRouteKind.IMPLEMENTATION_ANALOG, "when the mechanic has an executable/control/software analogue", "find engineering mechanisms that perform the same function under different vocabulary", "implementation-system search receipt or justified inapplicability"),
        (SearchRouteKind.METHODOLOGICAL_INSPIRATION, "always", "search mature methods that solve the same meta-operation even if the target object differs", "method-family transfer ledger"),
        (SearchRouteKind.CROSS_DOMAIN, "always", "challenge domain fixation using distant but structurally comparable systems", "cross-domain mapping candidates with breakpoints"),
        (SearchRouteKind.LITERATURE_BRIDGE, "always", "search disconnected literatures linked by intermediate concepts/mechanisms", "bridge path and source lineage"),
        (SearchRouteKind.CITATION_NEIGHBORHOOD, "after at least one high-relevance source is acquired", "expand beyond query vocabulary through source lineage", "forward/backward/citation-neighborhood receipt and stability note"),
        (SearchRouteKind.ADVERSARIAL_OMISSION, "always", "actively search for what the current decomposition/domain list would fail to retrieve", "independent omission challenge with explicit withheld assumptions/labels"),
        (SearchRouteKind.CROSS_LANGUAGE, "when relevant literature may exist outside the active search language or cross-language terminology can change recall", "reduce language-conditioned closure", "cross-language query/translation provenance or justified inapplicability"),
        (SearchRouteKind.FRESHNESS, "always for time-sensitive or active fields", "detect work newer than the inherited knowledge cutoff", "searched-through cutoff and source receipt"),
    )
    return MechanicSearchCoveragePlan(
        mechanic_id=cell.mechanic_id,
        obligations=tuple(_obligation(cell, *spec) for spec in specs),
        route_independence_rule="Different query strings are not independent if they preserve the same conceptual basis. At least one route must alter vocabulary/domain/formalism or evidence lineage enough to challenge the incumbent ontology.",
        coverage_claim_boundary="Completion is bounded to the declared sources, languages, route implementations, cutoffs and applicability decisions. It never proves that no relevant knowledge exists outside the searched universe.",
    )


def apply_default_search_coverage_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_search_coverage_plan(cell)
    empirical_open = tuple(
        dict.fromkeys(
            cell.empirical_open_coordinates
            + (
                "actual route execution/recall, applicability decisions, query/source-family diversity, omission recall and live evidence-lineage independence",
            )
        )
    )
    return replace(
        cell,
        search_coverage_obligations=tuple(item.obligation_id for item in plan.obligations),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_search_coverage_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_search_coverage_plan(cell) for cell in cells)
