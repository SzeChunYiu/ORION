"""LOCAL_ENGINEERING_ONLY: #136 structural-transfer substrate.

Not scientific cross-domain transfer evidence for #286.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from orion.transfer.types import AlgorithmCell, ProblemSignature, TransferStatus
from orion.transfer.diagnosis import DiagnosticProbe, ResponsibilityHypothesis
from orion.transfer.defeaters import Defeater
from orion.transfer.lenses import AffineLens
from orion.transfer.staging import CandidateRecord, CandidateVerdict, Stage, StageResult, StageVerdict
from orion.transfer.v2.canonical import canonical_json, content_digest
from orion.transfer.v2.manifest import validate_paper_v2_manifest
from orion.transfer.v2.models import build_transfer_receipt, problem_signature_payload
from orion.transfer.v2.p1 import EpistemicAction, P1DecisionStatus, diagnose_and_license
from orion.transfer.v2.p2 import ReplayableRouteSession, RouteConfig, RouteStep, RouteStepStatus, replay_route_session
from orion.transfer.v2.p3 import P3ConsistencyOutcome, ScientificCoordinateType, TypedLensEdge, TypedScientificLensNetwork
from orion.transfer.v2.p4 import EvidenceCustody, P4PlanReceipt, P4PlanStatus, ProtectedEvidenceAction, plan_protected_evidence
from orion.transfer.v2.p5 import AppendOnlyCandidateHistory, evaluate_and_archive
from orion.transfer.v2.portfolio import build_portfolio, verify_portfolio_replay
from orion.transfer.v2.registry import TransferRegistry


def sig(problem_id: str, domain: str = "control") -> ProblemSignature:
    return ProblemSignature(problem_id=problem_id, source_domain=domain, hidden_state="latent_fault", observability="partial", actions=frozenset({"probe", "repair"}), ground_truth="protected", dependence=0.7, authority_risk=0.8, nonstationarity=0.2, reversibility=0.6)


def cell(cell_id: str, domain: str = "control", mechanism: str = "active_test") -> AlgorithmCell:
    return AlgorithmCell(cell_id=cell_id, source_signature=sig(f"src-{cell_id}", domain), mechanism=mechanism, assumptions=("observable_probe",), invariants=("fail_closed",), stopping_rule="posterior concentrated", failure_modes=("confounding",), falsifiers=("probe_discriminates",))


def evidence(ok: bool | None = True) -> dict[str, object]:
    return {"assumptions": {"observable_probe": ok}, "falsifiers": {"probe_discriminates": ok}, "provenance": ["artifact:a"]}


def test_canonical_mapping_and_set_order_do_not_change_digest():
    a = {"z": {"b", "a"}, "x": {"q": 1, "p": 2}}
    b = {"x": {"p": 2, "q": 1}, "z": {"a", "b"}}
    assert canonical_json(a) == canonical_json(b)
    assert content_digest(a) == content_digest(b)


def test_changing_bound_field_changes_digest():
    a = problem_signature_payload(sig("target")); b = dict(a); b["authority_risk"] = 0.81
    assert content_digest(a) != content_digest(b)


def test_non_finite_float_rejected():
    with pytest.raises(ValueError): canonical_json({"x": float("nan")})


def test_registry_idempotent_same_content():
    registry = TransferRegistry(); first = registry.register_cell(cell("c1")); second = registry.register_cell(cell("c1"))
    assert first == second and len(registry.cells) == 1


def test_registry_rejects_same_cell_id_different_content():
    registry = TransferRegistry(); registry.register_cell(cell("c1", domain="control"))
    with pytest.raises(ValueError): registry.register_cell(cell("c1", domain="medicine"))


def test_registry_catalog_rejects_tampered_digest():
    registry = TransferRegistry(); registry.register_cell(cell("c1")); catalog = registry.to_catalog(); catalog["cells"][0]["payload"]["mechanism"] = "tampered"
    with pytest.raises(ValueError): TransferRegistry.from_catalog(catalog)


def test_false_assumption_overrides_high_structural_similarity():
    receipt = build_transfer_receipt(sig("target", "science"), cell("c1", "control"), assumption_truth={"observable_probe": False}, falsifier_results={"probe_discriminates": True})
    assert receipt.status is TransferStatus.BLOCKED_ASSUMPTION and receipt.structural_score > 0.9


def test_unknown_evidence_is_explicit_cannot_check():
    receipt = build_transfer_receipt(sig("target", "science"), cell("c1"), assumption_truth={}, falsifier_results={})
    assert receipt.status is TransferStatus.CANNOT_CHECK
    assert any(code.startswith("ASSUMPTION_UNKNOWN") for code in receipt.reason_codes)


def test_failed_falsifier_is_obstructed():
    receipt = build_transfer_receipt(sig("target", "science"), cell("c1"), assumption_truth={"observable_probe": True}, falsifier_results={"probe_discriminates": False})
    assert receipt.status is TransferStatus.OBSTRUCTED


def test_undeclared_evidence_is_rejected_not_silently_ignored():
    with pytest.raises(ValueError):
        build_transfer_receipt(sig("target"), cell("c1"), assumption_truth={"observable_probe": True, "secret": True}, falsifier_results={"probe_discriminates": True})


def test_transfer_receipt_detects_tampering():
    receipt = build_transfer_receipt(sig("target"), cell("c1"), assumption_truth={"observable_probe": True}, falsifier_results={"probe_discriminates": True}); receipt.verify()
    with pytest.raises(ValueError): replace(receipt, mechanism="other").verify()


def test_missing_cell_evidence_produces_decision_not_silent_skip():
    registry = TransferRegistry(); registry.register_cell(cell("c1")); portfolio = build_portfolio(sig("target", "science"), registry, {})
    assert len(portfolio.decisions) == 1 and portfolio.decisions[0].status is TransferStatus.CANNOT_CHECK and portfolio.selected_cell_ids == ()


def test_cross_confirmation_requires_distinct_domains():
    registry = TransferRegistry(); registry.register_cell(cell("c1", "control", "m")); registry.register_cell(cell("c2", "control", "m"))
    portfolio = build_portfolio(sig("target", "science"), registry, {"c1": evidence(), "c2": evidence()}, min_independent_domains=2)
    assert portfolio.confirmed_mechanisms == () and portfolio.selected_cell_ids == ()


def test_cross_confirmation_succeeds_across_distinct_domains():
    registry = TransferRegistry(); registry.register_cell(cell("c1", "control", "m")); registry.register_cell(cell("c2", "medicine", "m"))
    portfolio = build_portfolio(sig("target", "science"), registry, {"c1": evidence(), "c2": evidence()}, min_independent_domains=2)
    assert portfolio.confirmed_mechanisms == ("m",) and set(portfolio.selected_cell_ids) == {"c1", "c2"}


def test_portfolio_is_deterministic_under_registration_and_evidence_order():
    r1 = TransferRegistry(); r1.register_cell(cell("c1", "control", "m")); r1.register_cell(cell("c2", "medicine", "m"))
    r2 = TransferRegistry(); r2.register_cell(cell("c2", "medicine", "m")); r2.register_cell(cell("c1", "control", "m"))
    p1 = build_portfolio(sig("target", "science"), r1, {"c1": evidence(), "c2": evidence()}, min_independent_domains=2)
    p2 = build_portfolio(sig("target", "science"), r2, {"c2": evidence(), "c1": evidence()}, min_independent_domains=2)
    assert p1.to_payload() == p2.to_payload()


def test_portfolio_replay_detects_changed_evidence():
    registry = TransferRegistry(); registry.register_cell(cell("c1")); target = sig("target", "science"); original = {"c1": evidence()}; receipt = build_portfolio(target, registry, original)
    verify_portfolio_replay(receipt, target, registry, original)
    with pytest.raises(ValueError): verify_portfolio_replay(receipt, target, registry, {"c1": evidence(False)})


def p1_hypotheses(): return [ResponsibilityHypothesis("evidence", 0.5), ResponsibilityHypothesis("formulation", 0.5)]


def test_p1_blind_probe_is_non_diagnosable_and_cannot_license():
    blind = DiagnosticProbe("blind", {"evidence": 0.5, "formulation": 0.5})
    receipt = diagnose_and_license(p1_hypotheses(), [blind], requested_action=EpistemicAction.REFRAME_FORMULATION, observations=[("blind", True)])
    assert receipt.status is P1DecisionStatus.CANNOT_CHECK and receipt.reason_code == "NON_DIAGNOSABLE" and dict(receipt.information_gain)["blind"] == pytest.approx(0.0)


def test_p1_requires_probe_outcome_before_licensing():
    probe = DiagnosticProbe("disc", {"evidence": 0.1, "formulation": 0.9}); receipt = diagnose_and_license(p1_hypotheses(), [probe], requested_action=EpistemicAction.REFRAME_FORMULATION)
    assert receipt.status is P1DecisionStatus.CANNOT_CHECK and receipt.reason_code == "PROBE_REQUIRED"


def test_p1_supported_formulation_can_license_reframe():
    probe = DiagnosticProbe("disc", {"evidence": 0.01, "formulation": 0.99}); receipt = diagnose_and_license(p1_hypotheses(), [probe], requested_action=EpistemicAction.REFRAME_FORMULATION, observations=[("disc", True)], threshold=0.9)
    assert receipt.status is P1DecisionStatus.LICENSED and receipt.best_responsibility == "formulation"


def test_p1_evidence_responsibility_cannot_license_formulation_rewrite():
    probe = DiagnosticProbe("disc", {"evidence": 0.99, "formulation": 0.01}); receipt = diagnose_and_license(p1_hypotheses(), [probe], requested_action=EpistemicAction.REFRAME_FORMULATION, observations=[("disc", True)], threshold=0.9)
    assert receipt.best_responsibility == "evidence" and receipt.status is P1DecisionStatus.BLOCKED and receipt.reason_code == "RESPONSIBILITY_SCOPE_MISMATCH"


def test_p1_low_confidence_stays_cannot_check():
    probe = DiagnosticProbe("weak", {"evidence": 0.4, "formulation": 0.6}); receipt = diagnose_and_license(p1_hypotheses(), [probe], requested_action=EpistemicAction.REFRAME_FORMULATION, observations=[("weak", True)], threshold=0.8)
    assert receipt.status is P1DecisionStatus.CANNOT_CHECK and receipt.reason_code == "LOW_POSTERIOR_CONFIDENCE"


def test_p2_unsafe_rejection_is_transactional():
    session = ReplayableRouteSession(RouteConfig("bm25", 1.0, 0.1), ["dense"]); before = session.state_digest; receipt = session.apply(RouteStep("dense", reward=2.0, lower_bound=0.0))
    assert receipt.status is RouteStepStatus.REJECTED_SAFETY and session.state_digest == before == receipt.after_state_digest and receipt.unsigned_payload()["can_close_task"] is False


def test_p2_censored_observation_does_not_count_as_zero_reward():
    session = ReplayableRouteSession(RouteConfig("bm25", 1.0, 0.2), ["dense"]); session.apply(RouteStep("bm25", reward=1.0)); session.apply(RouteStep("bm25", reward=1.0)); receipt = session.apply(RouteStep("dense", reward=None, censored=True, lower_bound=0.6)); route = session.allocator.routes["dense"]
    assert receipt.status is RouteStepStatus.APPLIED and route.observed_attempts == 0 and route.observed_reward == 0.0 and route.censored_attempts == 1 and route.mean_reward is None


def test_p2_replay_reconstructs_same_state():
    config = RouteConfig("bm25", 1.0, 0.2); steps = [RouteStep("bm25", 1.0), RouteStep("bm25", 1.0), RouteStep("dense", 2.0, lower_bound=0.6)]; one = replay_route_session(config, ["dense"], steps); two = replay_route_session(config, ["dense"], steps)
    assert one.state_digest == two.state_digest and [r.to_payload() for r in one.receipts] == [r.to_payload() for r in two.receipts]


def test_p2_duplicate_route_identity_rejected():
    with pytest.raises(ValueError): ReplayableRouteSession(RouteConfig("bm25", 1.0, 0.2), ["dense", "dense"])


def digest(label: str) -> str: return content_digest({"label": label})


def test_p3_consistent_typed_cycle_glues():
    edges = [TypedLensEdge("A", "B", ScientificCoordinateType.MEASUREMENT, AffineLens(2, 1), provenance_digest=digest("ab")), TypedLensEdge("B", "C", ScientificCoordinateType.MEASUREMENT, AffineLens(3, -2), provenance_digest=digest("bc")), TypedLensEdge("C", "A", ScientificCoordinateType.MEASUREMENT, AffineLens(1/6, -1/6), provenance_digest=digest("ca"))]
    assert TypedScientificLensNetwork(edges).assess_cycle(ScientificCoordinateType.MEASUREMENT, ["A", "B", "C", "A"], [0.0, 2.0]).outcome is P3ConsistencyOutcome.GLUE


def test_p3_corrupted_cycle_obstructs():
    edges = [TypedLensEdge("A", "B", ScientificCoordinateType.MEASUREMENT, AffineLens(2, 0), provenance_digest=digest("ab")), TypedLensEdge("B", "C", ScientificCoordinateType.MEASUREMENT, AffineLens(3, 0), provenance_digest=digest("bc")), TypedLensEdge("C", "A", ScientificCoordinateType.MEASUREMENT, AffineLens(0.2, 0), provenance_digest=digest("ca"))]
    assert TypedScientificLensNetwork(edges).assess_cycle(ScientificCoordinateType.MEASUREMENT, ["A", "B", "C", "A"], [1.0]).outcome is P3ConsistencyOutcome.OBSTRUCTION


def test_p3_type_mismatch_obstructs_even_if_numeric_mapping_exists():
    edges = [TypedLensEdge("A", "B", ScientificCoordinateType.CONTEXT, AffineLens(1, 0), provenance_digest=digest("ab"))]; receipt = TypedScientificLensNetwork(edges).assess_cycle(ScientificCoordinateType.MEASUREMENT, ["A", "B", "A"], [1.0])
    assert receipt.outcome is P3ConsistencyOutcome.OBSTRUCTION and receipt.reason_code == "COORDINATE_TYPE_MISMATCH"


def test_p3_missing_anchors_is_cannot_check():
    edges = [TypedLensEdge("A", "B", ScientificCoordinateType.CONSTRUCT, AffineLens(1, 0), provenance_digest=digest("ab"))]
    assert TypedScientificLensNetwork(edges).assess_cycle(ScientificCoordinateType.CONSTRUCT, ["A", "B", "A"], []).outcome is P3ConsistencyOutcome.CANNOT_CHECK


def test_p3_unvalidated_bidirectionality_is_cannot_check():
    edges = [TypedLensEdge("A", "B", ScientificCoordinateType.REFERENT, AffineLens(1, 0), bidirectional_validated=False, provenance_digest=digest("ab"))]; receipt = TypedScientificLensNetwork(edges).assess_cycle(ScientificCoordinateType.REFERENT, ["A", "B", "A"], [1.0])
    assert receipt.outcome is P3ConsistencyOutcome.CANNOT_CHECK and receipt.reason_code == "BIDIRECTIONAL_VALIDATION_MISSING"


def test_p4_unprotected_self_check_cannot_clear_critical_defeater():
    receipt = plan_protected_evidence([Defeater("d1", 0.9)], [ProtectedEvidenceAction("self", frozenset({"d1"}), 1.0, 1.0, EvidenceCustody.SELF, digest("self"))])
    assert receipt.status is P4PlanStatus.CANNOT_CHECK and receipt.selected_action_id is None


def test_p4_protected_action_is_gather_evidence_not_authorized():
    receipt = plan_protected_evidence([Defeater("d1", 0.9)], [ProtectedEvidenceAction("host", frozenset({"d1"}), 0.8, 1.0, EvidenceCustody.INDEPENDENT_HOST, digest("host"))])
    assert receipt.status is P4PlanStatus.GATHER_EVIDENCE and receipt.selected_action_id == "host" and receipt.authority_terminal == "NONE"


def test_p4_receipt_type_rejects_authorized_terminal():
    with pytest.raises(ValueError):
        P4PlanReceipt(status=P4PlanStatus.GATHER_EVIDENCE, readiness=__import__("orion.transfer.defeaters", fromlist=["AuthorityReadiness"]).AuthorityReadiness.BLOCKED, selected_action_id="x", reason_code="x", expected_risk_reduction_per_cost=1.0, protected_action_ids=("x",), unresolved_defeater_ids=("d",), authority_terminal="AUTHORIZED", receipt_digest="x")


def test_p4_planner_prioritizes_critical_defeater_over_larger_noncritical_score():
    defeaters = [Defeater("critical", 0.9), Defeater("minor", 0.6)]; actions = [ProtectedEvidenceAction("critical-check", frozenset({"critical"}), 0.5, 1.0, EvidenceCustody.INDEPENDENT_HOST, digest("c")), ProtectedEvidenceAction("minor-cheap", frozenset({"minor"}), 1.0, 0.1, EvidenceCustody.INDEPENDENT_HOST, digest("m"))]
    assert plan_protected_evidence(defeaters, actions).selected_action_id == "critical-check"


def record_with(*results: StageResult) -> CandidateRecord:
    record = CandidateRecord("candidate")
    for result in results: record.record(result)
    return record


def test_p5_known_later_harm_dominates_missing_earlier_stage():
    receipt = evaluate_and_archive(record_with(StageResult(Stage.FRESH, StageVerdict.FAIL, harmful=True)), AppendOnlyCandidateHistory())
    assert receipt.verdict is CandidateVerdict.REJECT and "FRESH" in receipt.harmful_stages and "STATIC" in receipt.missing_stages


def test_p5_replay_gain_cannot_compensate_fresh_harm():
    record = record_with(StageResult(Stage.STATIC, StageVerdict.PASS), StageResult(Stage.REPLAY, StageVerdict.PASS, score_delta=1000), StageResult(Stage.FRESH, StageVerdict.PASS, score_delta=10, harmful=True), StageResult(Stage.PROTECTED, StageVerdict.PASS))
    assert evaluate_and_archive(record, AppendOnlyCandidateHistory()).verdict is CandidateVerdict.REJECT


def test_p5_protected_cannot_check_blocks_recommendation():
    record = record_with(StageResult(Stage.STATIC, StageVerdict.PASS), StageResult(Stage.REPLAY, StageVerdict.PASS), StageResult(Stage.FRESH, StageVerdict.PASS), StageResult(Stage.PROTECTED, StageVerdict.CANNOT_CHECK))
    assert evaluate_and_archive(record, AppendOnlyCandidateHistory()).verdict is CandidateVerdict.CANNOT_CHECK


def test_p5_all_pass_only_recommends_host_promotion():
    receipt = evaluate_and_archive(record_with(*(StageResult(stage, StageVerdict.PASS) for stage in Stage)), AppendOnlyCandidateHistory())
    assert receipt.verdict is CandidateVerdict.RECOMMEND_HOST_PROMOTION and receipt.terminal_authority == "HOST_ONLY_RECOMMENDATION"


def test_p5_negative_history_is_append_only_across_candidate_revisions():
    history = AppendOnlyCandidateHistory(); evaluate_and_archive(record_with(StageResult(Stage.STATIC, StageVerdict.FAIL)), history); evaluate_and_archive(record_with(StageResult(Stage.STATIC, StageVerdict.PASS)), history); revisions = history.revisions("candidate")
    assert len(revisions) == 2 and revisions[0][0] != revisions[1][0] and not hasattr(history, "delete")


def test_p5_history_views_cannot_mutate_retained_internal_evidence():
    history = AppendOnlyCandidateHistory(); evaluate_and_archive(record_with(StageResult(Stage.STATIC, StageVerdict.FAIL)), history); before = history.digest; payload = history.revisions("candidate")[0][1]; payload["results"]["STATIC"]["verdict"] = "PASS"; exported = history.to_payload(); exported["candidate"][0]["payload"]["results"]["STATIC"]["verdict"] = "PASS"
    assert history.digest == before and history.revisions("candidate")[0][1]["results"]["STATIC"]["verdict"] == "FAIL"


def valid_manifest(paper="ORION-P1", issue=137, adoption="V2_CANDIDATE", module="orion.transfer.v2.p1"):
    return {"manifest_version":"ORION_PAPER_V2_MANIFEST_V1","paper_id":paper,"mechanism_id":"mechanism","status":"V2_FUTURE_STUDY","adoption_class":adoption,"outcome_accessed":False,"execution_authority":"NONE","v1_protocol_mutated":False,"local_evidence_authority":"LOCAL_ENGINEERING_ONLY","requires_new_protocol_version":True,"source_issue":issue,"module":module,"preconditions_for_execution_freeze":["freeze a new protocol version","bind exact execution identities"]}


def test_manifest_validates_and_is_content_addressed():
    assert validate_paper_v2_manifest(valid_manifest()).startswith("sha256:")


@pytest.mark.parametrize("field,value", [("status","EXECUTION_FROZEN"),("outcome_accessed",True),("execution_authority","V1"),("v1_protocol_mutated",True),("local_evidence_authority","EXTERNAL"),("requires_new_protocol_version",False)])
def test_manifest_rejects_v1_or_authority_boundary_violation(field, value):
    manifest = valid_manifest(); manifest[field] = value
    with pytest.raises(ValueError): validate_paper_v2_manifest(manifest)
