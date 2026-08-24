from __future__ import annotations

import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Callable

from orion.core.closure import ClosureCertificate
from orion.core.method import MethodState
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.engine.cycle import Responsibility, local_reframe_allowed, revision_allowed
from orion.engine.operators.reopen import ReopenOperator
from orion.kernel.hard_gates import (
    HardGateContract,
    HardGateObservation,
    HardGateRequirement,
    HardGateState,
    evaluate_hard_gates,
)
from orion.knowledge.semantics import (
    MeaningRelation,
    ScientificMeaningProjection,
    compare_meaning,
)
from orion.self_orion.readiness import (
    EvidenceStatus,
    ReadinessCriterion,
    ReadinessEvidenceRecord,
    SelfOrionReadinessStage,
    ShadowSelfDrivingArchitectureEvidence,
    assess_readiness_stage,
)
from orion.study.p9.identifiability import analyze_identifiability
from orion.study.p9.structural_world import (
    AffineTransport,
    Atom,
    AtomType,
    GoldKind,
    GoldTarget,
    GluingVerdict,
    P9StructuralWorld,
    ViewMode,
)

from .broker import CapabilityBroker, HostCapabilityFailed
from .epistemic_authority import (
    AuthorityContext,
    AuthorityTerminal,
    BlockerDetermination,
    Coercion,
    EffectRequest,
    HardAuthorityObligation,
    Judgment,
    JudgmentType,
    RootClass,
    RootGrant,
    authorize_effect,
)
from .epistemic_mechanics import (
    AuthorityGrant,
    ClaimStatus,
    EpistemicMechanicState,
    MechanicContract,
    MechanicTerminal,
    apply_mechanic,
    certificate_aware_reopen,
)
from .epistemic_navigation import (
    EpistemicChart,
    NavigationAction,
    NavigationState,
    Obligation,
    ObligationStatus,
    RouteContract,
    plan_navigation,
    record_route_stop,
)
from .ocme_runtime import (
    LowerLevelResult,
    MethodEdit,
    OCMEEpisode,
    OCMETerminal,
    ObstructionCertificate,
    ObstructionKind,
    OutsideClosureVerification,
    TransferEvidence,
    assess_ocme_episode,
)
from .paper_programme_runtime import (
    P13Action,
    p11_accessible_rank_dimension,
    p11_cached_future_coverage,
    p12_joint_alloc,
    p12_success,
    p13_rcs_action,
    p14_governance_disposition,
)
from .workspace import ResearchWorkspace


class _P2SingleRoute:
    def __init__(self, *, close: bool) -> None:
        self.close = close
        self.system_id = f"harness-programme-p2-close-{close}"

    def run(self, view, session, *, seed):
        from orion.study.p2.corpus import DiscoveryRoute
        from orion.study.p2.systems import SystemReport

        found: set[str] = set()
        for probe in view.probes_for(DiscoveryRoute.LEXICAL):
            outcome = session.query(DiscoveryRoute.LEXICAL.value, probe)
            found.update(item.content_identity for item in outcome.records)
        session.declare_route_stop(DiscoveryRoute.LEXICAL.value, "no_more_probes")
        return SystemReport(tuple(sorted(found)), self.close)


def _p2_fixture():
    from orion.study.p2.freeze import load_suite

    suite = load_suite()
    task = next(
        item
        for item in suite.tasks
        if item.task_id == "p2-measurement-invariance-complete-gold-multiroute"
    )
    return suite, task


def _p1() -> tuple[bool, bool, str]:
    positive = (
        local_reframe_allowed(Responsibility.REPRESENTATION)
        and revision_allowed((Responsibility.REPRESENTATION,))
        and not local_reframe_allowed(Responsibility.EVIDENCE)
    )
    state = OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="programme-fixture"),
        closure_certificates=(
            ClosureCertificate("cert-W", "world", ("W",)),
            ClosureCertificate("cert-M", "method", ("M",)),
            ClosureCertificate("cert-WM", "joint", ("W", "M")),
        ),
    )
    result = ReopenOperator().run(state, changed_coordinates=("W",), reason="programme-fixture")
    by_id = {item.certificate_id: item for item in result.state.closure_certificates}
    fail_closed = (
        result.output == ("cert-W", "cert-WM")
        and by_id["cert-W"].stale
        and by_id["cert-WM"].stale
        and not by_id["cert-M"].stale
        and revision_allowed((Responsibility.REPRESENTATION, Responsibility.SEARCH)) is False
    )
    return positive, fail_closed, "live responsibility gate + ReopenOperator"


def _p2() -> tuple[bool, bool, str]:
    from orion.study.p2.runner import execute as execute_p2
    from orion.study.p2.systems import StopScope

    suite, task = _p2_fixture()
    local = execute_p2(
        _P2SingleRoute(close=False),
        suite.world,
        task,
        seed=1,
        run_manifest_hash="c" * 64,
    )
    positive = local.record["metrics"]["premature_task_closure"] == 0.0
    route_audits = [
        item for item in local.artifact["evaluation"]["stop_audits"]
        if item["scope"] == StopScope.ROUTE.value
    ]
    positive = positive and bool(route_audits) and route_audits[0]["premature"] is False

    global_claim = execute_p2(
        _P2SingleRoute(close=True),
        suite.world,
        task,
        seed=1,
        run_manifest_hash="c" * 64,
    )
    task_audit = next(
        item for item in global_claim.artifact["evaluation"]["stop_audits"]
        if item["scope"] == StopScope.TASK.value
    )
    fail_closed = (
        global_claim.record["status"] == "FAIL"
        and global_claim.record["failure_class"] == "premature_closure"
        and task_audit["premature"] is True
        and task_audit["still_reachable_count"] > 0
    )
    return positive, fail_closed, "live P2 discovery suite route-stop/task-stop evaluator"


def _meaning(projection_id: str, measurement: str) -> ScientificMeaningProjection:
    return ScientificMeaningProjection(
        projection_id=projection_id,
        source_id=f"source:{projection_id}",
        source_span="programme fixture",
        predicate="increases",
        referent_ids=("referent:system",),
        construct_ids=("construct:performance",),
        measurement_ids=(measurement,),
    )


def _p3() -> tuple[bool, bool, str]:
    left = _meaning("left", "measurement:accuracy")
    same = _meaning("same", "measurement:accuracy")
    other = _meaning("other", "measurement:latency")
    compatible = compare_meaning(left, same)
    blocked = compare_meaning(left, other)
    return (
        compatible.relation is MeaningRelation.COMPATIBLE and compatible.glue_eligible,
        blocked.relation is MeaningRelation.DISTINCT_MEASUREMENT and not blocked.glue_eligible,
        "ScientificMeaningProjection + compare_meaning",
    )


def _p4_observation(contract: HardGateContract, gate_id: str, state: HardGateState, *, evidence: bool = True) -> HardGateObservation:
    return HardGateObservation(
        gate_id=gate_id,
        subject_id="claim:fixture",
        state=state,
        contract_fingerprint=contract.fingerprint,
        evidence_ids=(f"e:{gate_id}",) if evidence else (),
    )


def _p4() -> tuple[bool, bool, str]:
    contract = HardGateContract(
        contract_id="programme-p4",
        requirements=(
            HardGateRequirement("CONTENT_BOUND", "content-bound support"),
            HardGateRequirement("INDEPENDENT_CHECK", "independent protected check"),
        ),
        frozen_at_round=1,
    )
    passed = evaluate_hard_gates(
        contract,
        (
            _p4_observation(contract, "CONTENT_BOUND", HardGateState.PASS),
            _p4_observation(contract, "INDEPENDENT_CHECK", HardGateState.PASS),
        ),
        subject_id="claim:fixture",
        round_index=2,
    )
    unresolved = evaluate_hard_gates(
        contract,
        (
            _p4_observation(contract, "CONTENT_BOUND", HardGateState.PASS),
            _p4_observation(contract, "INDEPENDENT_CHECK", HardGateState.CANNOT_CHECK, evidence=False),
        ),
        subject_id="claim:fixture",
        round_index=2,
    )
    return (
        passed.state is HardGateState.PASS and passed.permits_closure,
        unresolved.state is HardGateState.CANNOT_CHECK and not unresolved.permits_closure,
        "HardGateContract + evaluate_hard_gates",
    )


def _p5_records() -> tuple[ReadinessEvidenceRecord, ...]:
    return tuple(
        ReadinessEvidenceRecord(
            criterion=criterion,
            evidence_artifact_id=f"artifact:{criterion.value}",
            evidence_artifact_hash="a" * 64,
            subject_revision_hash="b" * 64,
            evaluator_artifact_hash="c" * 64,
            producer_process_lineage_hash="d" * 64,
            verifier_process_lineage_hash="e" * 64,
            evaluation_epoch_id="epoch:fixture",
            split_id="split:fresh",
            status=EvidenceStatus.PASS,
            frozen_before_candidate=True,
            fresh_split=True,
            reason="programme fixture",
        )
        for criterion in ReadinessCriterion
    )


def _p5() -> tuple[bool, bool, str]:
    architecture = ShadowSelfDrivingArchitectureEvidence(
        structural_open_questions=0,
        graph_defect_count=0,
        mechanical_work_item_count=1,
        component_artifact_ids=("component:fixture",),
        protected_boundary_artifact_ids=("protected:fixture",),
        failure_history_artifact_ids=("failure:fixture",),
        self_merge_capability_present=False,
    )
    records = _p5_records()
    positive = assess_readiness_stage(architecture, records) is SelfOrionReadinessStage.READY_PENDING_EXTERNAL_ATTESTATION
    nonfresh = tuple(replace(record, fresh_split=False) if index == 0 else record for index, record in enumerate(records))
    fail_closed = assess_readiness_stage(architecture, nonfresh) is SelfOrionReadinessStage.SHADOW_SELF_DRIVING
    return positive, fail_closed, "Self-ORION protected readiness stage evaluator"


def _p6_state() -> EpistemicMechanicState:
    return EpistemicMechanicState(
        coordinate_values=(("x", "old"), ("y", "0")),
        claim_statuses=(("q_root", ClaimStatus.CERTIFIED), ("q_child", ClaimStatus.CERTIFIED)),
        dependencies=(("q_root", "q_child"),),
        evidence_ids=("e:base",),
        provenance_ids=("p:base",),
        hard_obligations=(),
        authorities=(AuthorityGrant("a:root", ("x",), "root:protected", 1),),
        protected_root_ids=("root:protected",),
        epoch=1,
        history=(),
    )


def _p6() -> tuple[bool, bool, str]:
    repaired = certificate_aware_reopen(_p6_state(), changed_ids=("q_root",), certificates=())
    status = dict(repaired.claim_statuses)
    positive = status["q_root"] is ClaimStatus.OPEN and status["q_child"] is ClaimStatus.OPEN
    bad = apply_mechanic(
        _p6_state(),
        MechanicContract(
            mechanic_id="m:bad-write",
            read_ids=(),
            write_ids=("x",),
            write_values=(("y", "forbidden"),),
        ),
    )
    fail_closed = bad.terminal is MechanicTerminal.DENIED and bad.state == _p6_state()
    return positive, fail_closed, "P6 epistemic_mechanics root-inclusive repair/admissibility"


def _p7() -> tuple[bool, bool, str]:
    chart = EpistemicChart("chart", ("s",), (), ("o",))
    closed = NavigationState(
        active_chart=chart,
        current_location_id="s",
        frontier_ids=(),
        routes=(),
        obligations=(Obligation("o", mandatory=True, status=ObligationStatus.SATISFIED, evidence_ids=("e:o",)),),
        remaining_budget=1,
    )
    positive = plan_navigation(closed).action is NavigationAction.TASK_STOP
    route = RouteContract("r", "LEXICAL", ("o",), ("assumption:index",), ("scope:o",))
    open_state = NavigationState(
        active_chart=chart,
        current_location_id="s",
        frontier_ids=(),
        routes=(route,),
        obligations=(Obligation("o", mandatory=True),),
        remaining_budget=1,
    )
    stopped = record_route_stop(open_state, "r", evidence_ids=("e:route-stop",))
    fail_closed = plan_navigation(stopped).action is NavigationAction.CANNOT_CHECK
    return positive, fail_closed, "P7 chart/route/obligation navigation runtime"


def _p8_type(domain: str) -> JudgmentType:
    return JudgmentType(domain, "PASS", ("subject",), "sha256:content", 1)


def _p8_context(*, judgments=(), coercions=()) -> AuthorityContext:
    return AuthorityContext(
        judgments=tuple(judgments),
        hard_obligations=(HardAuthorityObligation("o", _p8_type("ASSERT"), additional_premise_ids=("premise:science",)),),
        roots=(RootGrant("grant", "ASSERT", ("subject",), "root:standing", RootClass.STANDING_POLICY, 1, "sha256:payload"),),
        coercions=tuple(coercions),
        blocker_determinations=(("blocker:absolute", BlockerDetermination.REFUTED),),
        required_blocker_type_ids=("blocker:absolute",),
        valid_premise_ids=("premise:science", "premise:coercion", "root:standing"),
        revoked_premise_ids=(),
        support_families=(),
        history=(),
    )


def _p8() -> tuple[bool, bool, str]:
    source_type = _p8_type("REFRAME")
    target_type = _p8_type("ASSERT")
    foreign = Judgment("j:foreign", source_type, support_premise_ids=("premise:science",))
    coercion = Coercion(
        "c:typed",
        source_type,
        target_type,
        "root:standing",
        ("premise:coercion",),
        ("j:foreign",),
        1,
        1,
    )
    effect = EffectRequest("effect", "ASSERT", "commit", ("subject",), "sha256:payload", 1)
    positive = authorize_effect(effect, _p8_context(judgments=(foreign,), coercions=(coercion,))).terminal is AuthorityTerminal.AUTHORIZED
    fail_closed = authorize_effect(effect, _p8_context(judgments=(foreign,)), confidence=1.0, expected_utility=1e12).terminal is not AuthorityTerminal.AUTHORIZED
    return positive, fail_closed, "P8 exact typed coercion/anti-laundering authority runtime"


def _p9_world(world_id: str, *, scale: float, gold: GluingVerdict) -> P9StructuralWorld:
    return P9StructuralWorld(
        world_id=world_id,
        atoms=(
            Atom("chart:a", AtomType.REPRESENTATION, "chart-a"),
            Atom("chart:b", AtomType.REPRESENTATION, "chart-b"),
        ),
        relations=(),
        transports=(AffineTransport("t", "chart:a", "chart:b", scale, 0.0),),
        mechanics=(),
        history=(),
        gold=GoldTarget(GoldKind.GLUING, gold.value),
    )


def _p9() -> tuple[bool, bool, str]:
    worlds = (
        _p9_world("w:glue", scale=1.0, gold=GluingVerdict.GLUE),
        _p9_world("w:obstruction", scale=2.0, gold=GluingVerdict.OBSTRUCTION),
    )
    restricted = analyze_identifiability(worlds, ViewMode.SURFACE)
    semantic = analyze_identifiability(worlds, ViewMode.SEMANTIC)
    positive = semantic.is_identifying and semantic.deterministic_accuracy_ceiling == 1.0
    fail_closed = (not restricted.is_identifying) and restricted.deterministic_accuracy_ceiling == 0.5
    return positive, fail_closed, "live P9 structural_world + exact identifiability analyzer"


def _ocme_lower() -> tuple[LowerLevelResult, ...]:
    return tuple(
        LowerLevelResult(check, check, False, (f"e:{check}",))
        for check in (
            "SEARCH_MORE",
            "REPRESENTATION_REPAIR",
            "IMPLEMENTATION_REPAIR",
            "LIBRARY_RETRIEVAL",
            "PROOF_REPAIR",
            "PROGRAM_SYNTHESIS",
            "EVOLUTIONARY_SEARCH",
        )
    )


def _p10_episode(*, timeout: bool = False) -> OCMEEpisode:
    obstruction = ObstructionCertificate(
        "obs",
        ObstructionKind.EXACT_FINITE_NONREACHABILITY if not timeout else ObstructionKind.RESOURCE_BOUNDED_OBSTRUCTION,
        "target",
        ("m:a", "m:b"),
        ("e:obs",),
        True,
        not timeout,
        timeout,
    )
    if timeout:
        return OCMEEpisode("ocme:bad", True, True, True, True, _ocme_lower(), obstruction, None, None, None, True, False, False)
    edit = MethodEdit("edit:new", ("m:new",), ("target", "held:1"), False, ("access:v1",))
    outside = OutsideClosureVerification("outside", edit.edit_id, "checker:independent", "candidate:generator", True, ("e:outside",))
    transfer = TransferEvidence(("held:1",), ("held:1",), ("access:v1",), 0.0, 0.05, True, False, ("e:transfer",))
    return OCMEEpisode("ocme:good", True, True, True, True, _ocme_lower(), obstruction, edit, outside, transfer, True, False, True)


def _p10() -> tuple[bool, bool, str]:
    positive = assess_ocme_episode(_p10_episode()).terminal is OCMETerminal.OCME_METHOD_EXPANSION_SUPPORTED
    failed = assess_ocme_episode(_p10_episode(timeout=True))
    fail_closed = failed.terminal is OCMETerminal.CANNOT_CHECK and not failed.jump_open
    return positive, fail_closed, "P10 OCME O0-O6 obstruction/outside-closure runtime"


def _p11() -> tuple[bool, bool, str]:
    positive = p11_accessible_rank_dimension(20, 3) == 1140 and p11_cached_future_coverage(retained=5, universe=20, cache_count=2) > 0.25
    try:
        p11_accessible_rank_dimension(3, 4)
    except ValueError:
        fail_closed = True
    else:
        fail_closed = False
    return positive, fail_closed, "P11 accessible-rank and future-optionality laws"


def _p12() -> tuple[bool, bool, str]:
    positive = (
        p12_joint_alloc(2.0, 0.0, budget=2) == (2, 0)
        and p12_joint_alloc(0.0, 2.0, budget=2) == (0, 2)
        and p12_success((1, 1), (1, 1))
    )
    try:
        p12_joint_alloc(1.0, 1.0, budget=-1)
    except ValueError:
        fail_closed = True
    else:
        fail_closed = False
    return positive, fail_closed, "P12 matched-budget state/reasoning allocation law"


def _p13() -> tuple[bool, bool, str]:
    positive = p13_rcs_action("Z1", "PREDICT", recoverable=False) is P13Action.REUSE and p13_rcs_action("Z1", "VERIFY", recoverable=True) is P13Action.REOPEN
    fail_closed = p13_rcs_action("Z1", "VERIFY", recoverable=False) is P13Action.CANNOT_CHECK
    return positive, fail_closed, "P13 responsibility-scoped reuse/reopen/CANNOT_CHECK law"


def _p14() -> tuple[bool, bool, str]:
    facts = {
        "evidence_integrity": True,
        "frozen_protocol": True,
        "identifiable": True,
        "positive": True,
        "donor_owned": False,
        "interaction_only": False,
        "live_negative_history": False,
        "material_new_evidence": True,
    }
    positive = p14_governance_disposition(facts) == "SUPPORTED_RESIDUAL"
    fail_closed = p14_governance_disposition({**facts, "evidence_integrity": False}) == "CANNOT_CHECK"
    try:
        p14_governance_disposition({**facts, "gold_disposition": "SUPPORTED_RESIDUAL"})
    except ValueError:
        fail_closed = fail_closed and True
    else:
        fail_closed = False
    return positive, fail_closed, "P14 specification-separated governance disposition law"


def _p15() -> tuple[bool, bool, str]:
    with tempfile.TemporaryDirectory(prefix="orion-harness-p15-") as directory:
        root = Path(directory)
        workspace = ResearchWorkspace.initialize(root / "ws", project_root=root)
        broker = CapabilityBroker(workspace)
        request = workspace.get_or_create_request(capability="WEB_SEARCH", payload={"query": "fixture"})
        workspace.ingest_result(request.request_id, success=False, error="simulated host outage", executor="fixture-host")
        isolated = False
        try:
            broker.require("WEB_SEARCH", {"query": "fixture"})
        except HostCapabilityFailed:
            isolated = True
        positive = isolated and workspace.run_ids() == ()
        try:
            workspace.ingest_result(request.request_id, success=True, output={"items": []}, executor="different-host")
        except ValueError:
            immutable = True
        else:
            immutable = False
        fail_closed = immutable and workspace.run_ids() == ()
    return positive, fail_closed, "P15 capability-failure isolation + immutable receipt identity"


_PROBES: tuple[tuple[str, Callable[[], tuple[bool, bool, str]]], ...] = (
    ("P1", _p1),
    ("P2", _p2),
    ("P3", _p3),
    ("P4", _p4),
    ("P5", _p5),
    ("P6", _p6),
    ("P7", _p7),
    ("P8", _p8),
    ("P9", _p9),
    ("P10", _p10),
    ("P11", _p11),
    ("P12", _p12),
    ("P13", _p13),
    ("P14", _p14),
    ("P15", _p15),
)


def paper_programme_conformance() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for paper_id, probe in _PROBES:
        try:
            positive, fail_closed, owner = probe()
            error = ""
        except Exception as exc:  # semantic gate must report a failed row, not disappear
            positive = fail_closed = False
            owner = "probe raised before owner completed"
            error = f"{type(exc).__name__}: {exc}"
        operational = bool(positive and fail_closed)
        rows.append(
            {
                "paper_id": paper_id,
                "positive_probe": bool(positive),
                "fail_closed_probe": bool(fail_closed),
                "operational": operational,
                "owner": owner,
                "error": error,
            }
        )
    failed = [row["paper_id"] for row in rows if not row["operational"]]
    operational = not failed and len(rows) == 15
    return {
        "schema": "ORION.HarnessPaperProgrammeConformance.v1",
        "terminal": "ORION_HARNESS_P1_P15_OPERATIONAL" if operational else "ORION_HARNESS_PAPER_PROGRAMME_OPEN",
        "paper_programme_operational": operational,
        "failed_paper_ids": failed,
        "papers": rows,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_promotion_authority": False,
        "grants_global_task_stop_authority": False,
        "note": "Operational means the registered paper decision contract executes a positive and a fail-closed control. It does not promote any paper claim or replace external scientific evaluation.",
    }


__all__ = ["paper_programme_conformance"]
