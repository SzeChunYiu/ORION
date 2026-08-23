from __future__ import annotations

from orion.self_orion.saturation_vector import DevelopmentSaturationAxis

from .epistemic_navigation import (
    EpistemicChart,
    NavigationAction,
    NavigationState,
    Obligation,
    ObligationStatus,
    ReframeMorphism,
    RouteContract,
    apply_reframe,
    plan_navigation,
    record_route_stop,
    structurally_independent,
)
from .paper_structure import (
    SourceChunk,
    SourceDocument,
    SupportedClaim,
    _canonical_objects,
    _locate_quote,
)
from .research_saturation import ResearchRoundEvidence, assess_evidence_derived_saturation


def _probe_span_rejection() -> bool:
    try:
        _locate_quote(SourceChunk("chunk:0", 0, 12, "known source"), "invented quote")
    except ValueError:
        return True
    return False


def _probe_unknown_preservation() -> bool:
    text = "measure midpoint"
    document = SourceDocument(
        source_id="paper:selftest",
        source_version="v1",
        source_path="selftest.txt",
        source_digest="sha256:" + "0" * 64,
        text=text,
        text_digest="sha256:" + "1" * 64,
    )
    claim = SupportedClaim(
        claim_id="support:selftest",
        coordinate="mechanics",
        value="measure_midpoint",
        quote=text,
        start=0,
        end=len(text),
        span_digest="sha256:" + "2" * 64,
    )
    realization, projection, unknown = _canonical_objects(
        document, method_id="method:selftest", claims=(claim,)
    )
    return (
        realization.state.value == "PARTIAL"
        and "target_role" in unknown
        and "terminal_condition" in unknown
        and projection.state.value == "PARTIAL"
    )


def _routes() -> tuple[RouteContract, RouteContract, RouteContract, RouteContract]:
    left = RouteContract("r:left", "PARENT", ("o",), ("assumption:a",), ("scope:o",))
    shared = RouteContract("r:shared", "FRESH", ("o",), ("assumption:a",), ("scope:o",))
    independent = RouteContract("r:ind", "OMISSION", ("o",), ("assumption:b",), ("scope:o",))
    unidentified = RouteContract("r:unknown", "BRIDGE", ("o",), (), ("scope:o",))
    return left, shared, independent, unidentified


def _probe_structural_routes() -> bool:
    left, shared, independent, unidentified = _routes()
    return (
        not structurally_independent(left, shared)
        and structurally_independent(left, independent)
        and not structurally_independent(left, unidentified)
    )


def _flat(round_id: str, route: RouteContract, *, residual: bool = False, resource: bool = False):
    return ResearchRoundEvidence(
        round_id=round_id,
        route_contracts=(route,),
        observed_axes=tuple(DevelopmentSaturationAxis),
        axis_item_ids=(),
        residual_axes=(DevelopmentSaturationAxis.OBSTRUCTION,) if residual else (),
        residual_signature=("residual:open",) if residual else (),
        resource_bound=resource,
    )


def _probe_saturation() -> bool:
    left, shared, independent, _ = _routes()
    dependent = assess_evidence_derived_saturation((_flat("1", left), _flat("2", shared)))
    independent_flat = assess_evidence_derived_saturation((_flat("1", left), _flat("2", independent)))
    reopened = assess_evidence_derived_saturation((_flat("1", left), _flat("2", independent, residual=True)))
    resource = assess_evidence_derived_saturation((_flat("1", left), _flat("2", independent, resource=True)))
    return (
        not dependent.bounded_saturated
        and independent_flat.bounded_saturated
        and not independent_flat.grants_absolute_completeness
        and not reopened.bounded_saturated
        and not resource.bounded_saturated
        and resource.cannot_check_resource_bound
    )


def _probe_route_stop_vs_task_stop() -> bool:
    route, _, _, _ = _routes()
    chart = EpistemicChart("chart", ("s",), (), ("o",))
    state = NavigationState(
        active_chart=chart,
        current_location_id="s",
        frontier_ids=(),
        routes=(route,),
        obligations=(Obligation("o", mandatory=True),),
        remaining_budget=1,
    )
    stopped = record_route_stop(state, route.route_id, evidence_ids=("e:flat",))
    return plan_navigation(stopped).action is NavigationAction.CANNOT_CHECK


def _probe_reframe_support_transport() -> bool:
    old = EpistemicChart("old", ("s",), (), ("o",))
    new = EpistemicChart("new", ("t",), (), ("o2",))
    state = NavigationState(
        active_chart=old,
        current_location_id="s",
        frontier_ids=(),
        routes=(),
        obligations=(
            Obligation(
                "o",
                mandatory=True,
                status=ObligationStatus.SATISFIED,
                evidence_ids=("e",),
                closure_certificate_ids=("cert",),
            ),
        ),
        evidence_ids=("e",),
        remaining_budget=1,
    )
    morphism = ReframeMorphism(
        reframe_id="rho",
        source_chart_id="old",
        target_chart_id="new",
        location_map=(("s", "t"),),
        obligation_map=(("o", "o2"),),
        support_preserved_obligation_ids=(),
    )
    reframed = apply_reframe(state, new, morphism)
    obligation = reframed.obligations[0]
    return (
        reframed.evidence_ids == ("e",)
        and obligation.obligation_id == "o2"
        and obligation.status is ObligationStatus.OPEN
        and obligation.closure_certificate_ids == ()
        and plan_navigation(reframed).action is NavigationAction.CANNOT_CHECK
    )


def _probe_task_stop_closed_only() -> bool:
    chart = EpistemicChart("chart", ("s",), (), ("o",))
    closed = NavigationState(
        active_chart=chart,
        current_location_id="s",
        frontier_ids=(),
        routes=(),
        obligations=(Obligation("o", mandatory=True, status=ObligationStatus.SATISFIED, evidence_ids=("e",)),),
        evidence_ids=("e",),
        remaining_budget=0,
    )
    return plan_navigation(closed).action is NavigationAction.TASK_STOP


def paper_contract_conformance() -> dict[str, object]:
    probes = {
        "raw_source_span_fabrication_rejected": _probe_span_rejection(),
        "unsupported_method_coordinates_preserved_unknown": _probe_unknown_preservation(),
        "route_independence_uses_structural_assumptions": _probe_structural_routes(),
        "multi_axis_saturation_is_noncompensatory_and_nonabsolute": _probe_saturation(),
        "route_stop_does_not_imply_task_stop": _probe_route_stop_vs_task_stop(),
        "reframe_preserves_evidence_without_unproved_closure": _probe_reframe_support_transport(),
        "task_stop_requires_closed_mandatory_obligations": _probe_task_stop_closed_only(),
    }
    failed = sorted(key for key, value in probes.items() if value is not True)
    return {
        "schema": "ORION.HarnessPaperContractConformance.v1",
        "terminal": (
            "ORION_HARNESS_PAPER_CONTRACT_P0_OPERATIONAL"
            if not failed
            else "ORION_HARNESS_PAPER_CONTRACT_P0_NOT_OPERATIONAL"
        ),
        "probes": probes,
        "failed_probes": failed,
        "paper_contract_operational": not failed,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_promotion_authority": False,
        "grants_global_task_stop_authority": False,
        "note": (
            "This gate executes hostile semantic counterexamples. Raw-source host-capability replay is additionally covered by package tests; "
            "passing this gate does not establish arbitrary-paper extraction accuracy or scientific correctness."
        ),
    }


__all__ = ["paper_contract_conformance"]
