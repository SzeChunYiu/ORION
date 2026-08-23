from __future__ import annotations

import hashlib
import json

from orion.self_orion.saturation_vector import DevelopmentSaturationAxis
from orion_research_harness.epistemic_navigation import (
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
from orion_research_harness.paper_conformance import paper_contract_conformance
from orion_research_harness.paper_structure import run_paper_structure
from orion_research_harness.research_saturation import (
    ResearchRoundEvidence,
    assess_evidence_derived_saturation,
)
from orion_research_harness.workspace import ResearchWorkspace


def _all_axes() -> tuple[DevelopmentSaturationAxis, ...]:
    return tuple(DevelopmentSaturationAxis)


def _flat_round(round_id: str, route: RouteContract, *, resource_bound: bool = False):
    return ResearchRoundEvidence(
        round_id=round_id,
        route_contracts=(route,),
        observed_axes=_all_axes(),
        axis_item_ids=(),
        resource_bound=resource_bound,
    )


def test_raw_text_method_structure_is_extracted_through_replayable_capabilities(tmp_path):
    source = tmp_path / "paper.txt"
    source.write_text(
        "We localize a bracketed monotone target on an ordered interval.\n"
        "The method assumes deterministic responses and requires a bracketed target.\n"
        "First measure the midpoint, then discard the inconsistent half.\n"
        "The target remains bracketed and interval width decreases.\n"
        "Stop when interval width is below tolerance and return an interval representative.\n"
        "Failure occurs for a non-monotone response.\n",
        encoding="utf-8",
    )
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)

    pending = run_paper_structure(
        workspace,
        source_path="paper.txt",
        method_id="method:bisection",
        source_id="paper:bisection",
        source_version="v1",
    )
    assert pending["status"] == "PENDING_CAPABILITY"
    request = pending["request"]
    assert request["capability"] == "LLM_COMPLETE"
    assert request["payload"]["task"] == "paper_method_structure_extract_v1"
    assert "MethodRealization" not in request["payload"]["user"]

    claims = {
        "claims": [
            {"coordinate": "target_role", "value": "bounded_monotone_localization", "quote": "localize a bracketed monotone target"},
            {"coordinate": "preconditions", "value": "bracketed_target", "quote": "requires a bracketed target"},
            {"coordinate": "assumptions", "value": "deterministic_response", "quote": "assumes deterministic responses"},
            {"coordinate": "representation_in", "value": "ordered_interval", "quote": "ordered interval"},
            {"coordinate": "representation_out", "value": "shrinking_interval", "quote": "interval width decreases"},
            {"coordinate": "mechanics", "value": "measure_midpoint", "quote": "measure the midpoint"},
            {"coordinate": "mechanics", "value": "discard_inconsistent_half", "quote": "discard the inconsistent half"},
            {"coordinate": "dependencies", "value": ["measure_midpoint", "discard_inconsistent_half"], "quote": "First measure the midpoint, then discard the inconsistent half."},
            {"coordinate": "invariants", "value": "target_remains_bracketed", "quote": "target remains bracketed"},
            {"coordinate": "progress_measure", "value": "interval_width_decreases", "quote": "interval width decreases"},
            {"coordinate": "effects", "value": "shrink_candidate_interval", "quote": "interval width decreases"},
            {"coordinate": "terminal_condition", "value": "interval_width_below_tolerance", "quote": "interval width is below tolerance"},
            {"coordinate": "reconstruction_map", "value": "return_interval_representative", "quote": "return an interval representative"},
            {"coordinate": "failure_modes", "value": "non_monotone_response", "quote": "non-monotone response"},
        ]
    }
    workspace.ingest_result(
        request["request_id"],
        success=True,
        output={"content": json.dumps(claims)},
        executor="test-model",
    )

    verify_pending = run_paper_structure(
        workspace,
        source_path="paper.txt",
        method_id="method:bisection",
        source_id="paper:bisection",
        source_version="v1",
    )
    assert verify_pending["status"] == "PENDING_CAPABILITY"
    verify_request = verify_pending["request"]
    assert verify_request["capability"] == "VERIFY_EVIDENCE"
    workspace.ingest_result(
        verify_request["request_id"],
        success=True,
        output={"passed": True, "certificate_ids": ["cert:independent"], "reason": "source spans support the projection"},
        executor="test-verifier",
    )

    complete = run_paper_structure(
        workspace,
        source_path="paper.txt",
        method_id="method:bisection",
        source_id="paper:bisection",
        source_version="v1",
    )
    assert complete["status"] == "COMPLETE"
    assert complete["verification"]["passed"] is True
    assert complete["method_realization"]["state"] == "COMPLETE"
    assert complete["method_realization"]["payload"]["mechanics"] == [
        "discard_inconsistent_half",
        "measure_midpoint",
    ]
    assert complete["method_structure_projection"]["payload"]["can_claim_method_fibre"] is False
    assert complete["grants_scientific_authority"] is False
    assert complete["grants_novelty_authority"] is False


def test_method_structure_rejects_nonexistent_source_quote(tmp_path):
    source = tmp_path / "paper.txt"
    source.write_text("The method measures the midpoint.\n", encoding="utf-8")
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    pending = run_paper_structure(
        workspace,
        source_path="paper.txt",
        method_id="method:x",
        source_id="paper:x",
        source_version="v1",
    )
    workspace.ingest_result(
        pending["request"]["request_id"],
        success=True,
        output={
            "content": json.dumps(
                {"claims": [{"coordinate": "mechanics", "value": "invented_step", "quote": "this quote does not exist"}]}
            )
        },
        executor="test-model",
    )
    failed = run_paper_structure(
        workspace,
        source_path="paper.txt",
        method_id="method:x",
        source_id="paper:x",
        source_version="v1",
    )
    assert failed["status"] == "HOST_CAPABILITY_FAILED"
    assert "quote" in failed["error"].lower()


def test_pdf_text_conversion_request_is_bound_to_exact_pdf_bytes(tmp_path):
    raw = b"%PDF-1.7\nsynthetic fixture\n"
    (tmp_path / "paper.pdf").write_bytes(raw)
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    pending = run_paper_structure(
        workspace,
        source_path="paper.pdf",
        method_id="method:pdf",
        source_id="paper:pdf",
        source_version="v1",
    )
    assert pending["status"] == "PENDING_CAPABILITY"
    request = pending["request"]
    assert request["capability"] == "DOCUMENT_TEXT_EXTRACT"
    assert request["payload"]["source_digest"] == "sha256:" + hashlib.sha256(raw).hexdigest()


def test_route_independence_is_structural_not_label_based():
    left = RouteContract(
        route_id="r:left",
        route_family="PARENT_DISCIPLINE",
        obligation_ids=("o",),
        critical_assumption_ids=("assumption:index-a",),
        coverage_scope_ids=("scope:o",),
    )
    same_failure = RouteContract(
        route_id="r:right",
        route_family="FRESHNESS",
        obligation_ids=("o",),
        critical_assumption_ids=("assumption:index-a",),
        coverage_scope_ids=("scope:o",),
    )
    independent = RouteContract(
        route_id="r:independent",
        route_family="ADVERSARIAL_OMISSION",
        obligation_ids=("o",),
        critical_assumption_ids=("assumption:manual-citation-trace",),
        coverage_scope_ids=("scope:o",),
    )
    missing = RouteContract(
        route_id="r:missing",
        route_family="LITERATURE_BRIDGE",
        obligation_ids=("o",),
        critical_assumption_ids=(),
        coverage_scope_ids=("scope:o",),
    )
    assert structurally_independent(left, same_failure) is False
    assert structurally_independent(left, independent) is True
    assert structurally_independent(left, missing) is False


def test_dependent_flat_routes_do_not_establish_multi_axis_saturation():
    r1 = RouteContract("r1", "A", ("o",), ("shared",), ("scope",))
    r2 = RouteContract("r2", "B", ("o",), ("shared",), ("scope",))
    report = assess_evidence_derived_saturation((_flat_round("1", r1), _flat_round("2", r2)))
    assert report.bounded_saturated is False
    assert any("independent" in reason.lower() for reason in report.reasons)


def test_disjoint_flat_routes_can_establish_bounded_multi_axis_saturation():
    r1 = RouteContract("r1", "A", ("o",), ("assumption:a",), ("scope",))
    r2 = RouteContract("r2", "B", ("o",), ("assumption:b",), ("scope",))
    report = assess_evidence_derived_saturation((_flat_round("1", r1), _flat_round("2", r2)))
    assert report.bounded_saturated is True
    assert report.grants_absolute_completeness is False


def test_axis_residual_and_resource_bound_reopen_saturation():
    r1 = RouteContract("r1", "A", ("o",), ("assumption:a",), ("scope",))
    r2 = RouteContract("r2", "B", ("o",), ("assumption:b",), ("scope",))
    residual_round = ResearchRoundEvidence(
        round_id="2",
        route_contracts=(r2,),
        observed_axes=_all_axes(),
        axis_item_ids=(),
        residual_axes=(DevelopmentSaturationAxis.OBSTRUCTION,),
        residual_signature=("residual:open",),
    )
    report = assess_evidence_derived_saturation((_flat_round("1", r1), residual_round))
    assert report.bounded_saturated is False
    assert any("OBSTRUCTION" in reason for reason in report.reasons)

    resource = assess_evidence_derived_saturation(
        (_flat_round("1", r1), _flat_round("2", r2, resource_bound=True))
    )
    assert resource.bounded_saturated is False
    assert resource.cannot_check_resource_bound is True


def test_route_stop_does_not_imply_task_stop_and_budget_exhaustion_is_cannot_check():
    route = RouteContract("r", "A", ("o",), ("assumption:a",), ("scope",))
    chart = EpistemicChart("chart", ("s",), (), ("o",))
    state = NavigationState(
        active_chart=chart,
        current_location_id="s",
        frontier_ids=(),
        routes=(route,),
        obligations=(Obligation("o", mandatory=True),),
        remaining_budget=1,
    )
    stopped = record_route_stop(state, "r", evidence_ids=("e:route-flat",))
    decision = plan_navigation(stopped)
    assert decision.action is NavigationAction.CANNOT_CHECK
    assert decision.action is not NavigationAction.TASK_STOP

    no_budget = NavigationState(
        active_chart=chart,
        current_location_id="s",
        frontier_ids=(),
        routes=(route,),
        obligations=(Obligation("o", mandatory=True),),
        remaining_budget=0,
    )
    assert plan_navigation(no_budget).action is NavigationAction.CANNOT_CHECK


def test_reframe_preserves_evidence_but_reopens_unproved_closure_and_cannot_check_unmapped_obligation():
    old_chart = EpistemicChart("old", ("s",), (), ("o1", "o2"))
    new_chart = EpistemicChart("new", ("s2",), (), ("o1-new",))
    state = NavigationState(
        active_chart=old_chart,
        current_location_id="s",
        frontier_ids=(),
        routes=(),
        obligations=(
            Obligation("o1", mandatory=True, status=ObligationStatus.SATISFIED, evidence_ids=("e1",)),
            Obligation("o2", mandatory=True, status=ObligationStatus.SATISFIED, evidence_ids=("e2",)),
        ),
        evidence_ids=("e1", "e2"),
        remaining_budget=2,
    )
    morphism = ReframeMorphism(
        reframe_id="rho",
        source_chart_id="old",
        target_chart_id="new",
        location_map=(("s", "s2"),),
        obligation_map=(("o1", "o1-new"),),
        support_preserved_obligation_ids=(),
    )
    reframed = apply_reframe(state, new_chart, morphism)
    by_id = {item.obligation_id: item for item in reframed.obligations}
    assert by_id["o1-new"].status is ObligationStatus.OPEN
    assert by_id["o2"].status is ObligationStatus.CANNOT_CHECK
    assert reframed.evidence_ids == ("e1", "e2")
    assert plan_navigation(reframed).action is NavigationAction.CANNOT_CHECK


def test_paper_contract_conformance_executes_hostile_semantic_probes():
    report = paper_contract_conformance()
    assert report["schema"] == "ORION.HarnessPaperContractConformance.v1"
    assert report["paper_contract_operational"] is True
    assert report["failed_probes"] == []
    assert all(report["probes"].values())
    assert report["grants_scientific_authority"] is False
    assert report["grants_novelty_authority"] is False
