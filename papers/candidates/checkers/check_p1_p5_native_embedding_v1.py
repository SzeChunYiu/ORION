#!/usr/bin/env python3
"""Exact live P1-P5 native-decision fixtures for candidate embeddings.

Run from repository root:

    PYTHONPATH=src python papers/candidates/checkers/check_p1_p5_native_embedding_v1.py

This checker intentionally calls current ORION implementation functions rather
than re-implementing their expected policy in candidate code. Its purpose is to
freeze a small conservative-embedding boundary for P6-P8.

A PASS does *not* establish that the full candidate calculi embed every P1-P5
mechanism. It establishes only the exact native decisions enumerated below.
"""

from __future__ import annotations

from dataclasses import replace

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
from orion.study.p2.corpus import DiscoveryRoute
from orion.study.p2.freeze import load_suite
from orion.study.p2.systems import SystemReport
from orion.study.p2.runner import execute


FIXTURE_RUN_MANIFEST_HASH = "c" * 64


def check_p1_reframe_and_reopen() -> None:
    """P1: exact responsibility-to-local-reframe gate + dependency reopening."""

    # These are the live engine responsibilities licensed for local formulation
    # / search-space repair. Do not collapse them back into paper-level W/M
    # shorthand in executable embeddings.
    locally_reframable = {
        Responsibility.QUESTION,
        Responsibility.REPRESENTATION,
        Responsibility.SEARCH,
        Responsibility.ROUTING,
        Responsibility.DECOMPOSITION,
        Responsibility.INTERFACE,
        Responsibility.MEASUREMENT,
    }
    protected_or_nonreframe = {
        Responsibility.EVALUATOR,
        Responsibility.METHOD,
        Responsibility.EVIDENCE,
        Responsibility.EXECUTION,
    }
    assert all(local_reframe_allowed(item) for item in locally_reframable)
    assert not any(local_reframe_allowed(item) for item in protected_or_nonreframe)

    # High-impact revision requires a singular attribution, but singularity is
    # not sufficient for local REFRAME: EVIDENCE is uniquely diagnosed here and
    # still belongs to acquisition/verification rather than formulation rewrite.
    assert revision_allowed((Responsibility.REPRESENTATION,)) is True
    assert revision_allowed((Responsibility.EVIDENCE,)) is True
    assert local_reframe_allowed(Responsibility.EVIDENCE) is False
    assert revision_allowed(
        (Responsibility.REPRESENTATION, Responsibility.SEARCH)
    ) is False
    assert revision_allowed(()) is False

    state = OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="fixture"),
        closure_certificates=(
            ClosureCertificate("cert-W", "world-sensitive", ("W",)),
            ClosureCertificate("cert-M", "method-sensitive", ("M",)),
            ClosureCertificate("cert-WM", "joint", ("W", "M")),
        ),
    )
    result = ReopenOperator().run(
        state,
        changed_coordinates=("W",),
        reason="fixture-world-change",
    )
    assert result.output == ("cert-W", "cert-WM")
    by_id = {item.certificate_id: item for item in result.state.closure_certificates}
    assert by_id["cert-W"].stale is True
    assert by_id["cert-WM"].stale is True
    assert by_id["cert-M"].stale is False


class _P2SingleRoute:
    """Current P2 fixture pattern: exhaust lexical route, optionally claim closure."""

    def __init__(self, *, close: bool) -> None:
        self.close = close
        self.system_id = f"p6-p8-native-embedding-p2-close-{close}"

    def run(self, view, session, *, seed):
        found: set[str] = set()
        for probe in view.probes_for(DiscoveryRoute.LEXICAL):
            outcome = session.query(DiscoveryRoute.LEXICAL.value, probe)
            found.update(item.content_identity for item in outcome.records)
        session.declare_route_stop(DiscoveryRoute.LEXICAL.value, "no_more_probes")
        return SystemReport(tuple(sorted(found)), self.close)


def _p2_task(suite):
    return next(
        item
        for item in suite.tasks
        if item.task_id == "p2-measurement-invariance-complete-gold-multiroute"
    )


def check_p2_route_stop_vs_task_stop() -> None:
    """P2: a correct local route stop does not license global completion."""

    suite = load_suite()
    task = _p2_task(suite)

    local_only = execute(
        _P2SingleRoute(close=False),
        suite.world,
        task,
        seed=1,
        run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
    )
    assert local_only.record["metrics"]["premature_task_closure"] == 0.0
    assert local_only.record["failure_class"] != "premature_closure"
    # Post-#1078: route stops live in their own list. RouteStopAudit is
    # route-scoped by construction, so there is nothing left to filter -- the
    # old "scope" discriminator does not exist because the split into
    # route_stop_audits and route_exhaustion_audits replaced it.
    route_audits = list(local_only.artifact["evaluation"]["route_stop_audits"])
    assert route_audits
    assert route_audits[0]["false_positive"] is False
    assert route_audits[0]["residual_yield_at_stop"] == 0

    global_claim = execute(
        _P2SingleRoute(close=True),
        suite.world,
        task,
        seed=1,
        run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
    )
    assert global_claim.record["status"] == "FAIL"
    assert global_claim.record["failure_class"] == "premature_closure"
    assert global_claim.record["metrics"]["premature_task_closure"] == 1.0
    # Post-#1078 there is no TASK-scoped stop audit. The scoped list was split
    # into route_stop_audits and route_exhaustion_audits, and task-level closure
    # became fields on the evaluation itself. The three assertions below are the
    # same three claims against the new shape: the task closed prematurely,
    # residual work was still discoverable within budget, and the closure was
    # actually declared rather than forced by a cap.
    evaluation = global_claim.artifact["evaluation"]
    assert evaluation["metrics"]["premature_task_closure"] == 1.0
    assert evaluation["metrics"]["task_residual_discoverable_within_budget"] > 0
    assert evaluation["metrics"]["task_closure_declared"] == 1.0


def _projection(
    projection_id: str,
    *,
    measurement: str,
) -> ScientificMeaningProjection:
    return ScientificMeaningProjection(
        projection_id=projection_id,
        source_id=f"source:{projection_id}",
        source_span="fixture span",
        predicate="increases",
        referent_ids=("referent:system-a",),
        construct_ids=("construct:performance",),
        measurement_ids=(measurement,),
    )


def check_p3_merge_obstruction() -> None:
    """P3: semantic compatibility is conservative and measurement mismatch blocks glue."""

    left = _projection("left", measurement="measurement:accuracy")
    same = _projection("same", measurement="measurement:accuracy")
    different = _projection("different", measurement="measurement:latency")

    compatible = compare_meaning(left, same)
    assert compatible.relation is MeaningRelation.COMPATIBLE
    assert compatible.glue_eligible is True

    blocked = compare_meaning(left, different)
    assert blocked.relation is MeaningRelation.DISTINCT_MEASUREMENT
    assert blocked.glue_eligible is False


def _gate_observation(
    contract: HardGateContract,
    gate_id: str,
    state: HardGateState,
    *,
    evidence: bool = True,
) -> HardGateObservation:
    return HardGateObservation(
        gate_id=gate_id,
        subject_id="claim:fixture",
        state=state,
        contract_fingerprint=contract.fingerprint,
        evidence_ids=(f"evidence:{gate_id}",) if evidence else (),
    )


def check_p4_noncompensatory_authority_gate() -> None:
    """P4 substrate: every frozen hard gate must pass with required evidence."""

    contract = HardGateContract(
        contract_id="p4-native-embedding",
        requirements=(
            HardGateRequirement("CONTENT_BOUND", "content-bound support"),
            HardGateRequirement("INDEPENDENT_CHECK", "independent protected check"),
        ),
        frozen_at_round=1,
    )

    passed = evaluate_hard_gates(
        contract,
        (
            _gate_observation(contract, "CONTENT_BOUND", HardGateState.PASS),
            _gate_observation(contract, "INDEPENDENT_CHECK", HardGateState.PASS),
        ),
        subject_id="claim:fixture",
        round_index=2,
    )
    assert passed.state is HardGateState.PASS
    assert passed.permits_closure is True

    unresolved = evaluate_hard_gates(
        contract,
        (
            _gate_observation(contract, "CONTENT_BOUND", HardGateState.PASS),
            _gate_observation(
                contract,
                "INDEPENDENT_CHECK",
                HardGateState.CANNOT_CHECK,
                evidence=False,
            ),
        ),
        subject_id="claim:fixture",
        round_index=2,
    )
    assert unresolved.state is HardGateState.CANNOT_CHECK
    assert unresolved.permits_closure is False

    failed = evaluate_hard_gates(
        contract,
        (
            _gate_observation(contract, "CONTENT_BOUND", HardGateState.PASS),
            _gate_observation(contract, "INDEPENDENT_CHECK", HardGateState.FAIL),
        ),
        subject_id="claim:fixture",
        round_index=2,
    )
    assert failed.state is HardGateState.FAIL
    assert failed.permits_closure is False


def _sha(character: str) -> str:
    return character * 64


def _p5_pass_records() -> tuple[ReadinessEvidenceRecord, ...]:
    return tuple(
        ReadinessEvidenceRecord(
            criterion=criterion,
            evidence_artifact_id=f"artifact:{criterion.value}",
            evidence_artifact_hash=_sha("a"),
            subject_revision_hash=_sha("b"),
            evaluator_artifact_hash=_sha("c"),
            producer_process_lineage_hash=_sha("d"),
            verifier_process_lineage_hash=_sha("e"),
            evaluation_epoch_id="epoch:fixture",
            split_id="split:fresh",
            status=EvidenceStatus.PASS,
            frozen_before_candidate=True,
            fresh_split=True,
            reason="fixture pass",
        )
        for criterion in ReadinessCriterion
    )


def check_p5_protected_self_change_readiness() -> None:
    """P5: complete internal evidence still stops at external-attestation boundary."""

    architecture = ShadowSelfDrivingArchitectureEvidence(
        structural_open_questions=0,
        graph_defect_count=0,
        mechanical_work_item_count=1,
        component_artifact_ids=("component:fixture",),
        protected_boundary_artifact_ids=("protected:fixture",),
        failure_history_artifact_ids=("failure-history:fixture",),
        self_merge_capability_present=False,
    )
    records = _p5_pass_records()
    assert assess_readiness_stage(
        architecture, records
    ) is SelfOrionReadinessStage.READY_PENDING_EXTERNAL_ATTESTATION
    assert "GOVERNED_SELF_ORION" not in {
        item.value for item in SelfOrionReadinessStage
    }

    # Matched negative control: one non-fresh criterion prevents the pending-
    # external-attestation stage despite all caller-visible PASS statuses.
    nonfresh = tuple(
        replace(record, fresh_split=False)
        if index == 0
        else record
        for index, record in enumerate(records)
    )
    assert assess_readiness_stage(
        architecture, nonfresh
    ) is SelfOrionReadinessStage.SHADOW_SELF_DRIVING


def main() -> int:
    check_p1_reframe_and_reopen()
    print("PASS P1 responsibility/reframe/reopen native decisions")
    check_p2_route_stop_vs_task_stop()
    print("PASS P2 route-stop/task-stop native decisions")
    check_p3_merge_obstruction()
    print("PASS P3 semantic merge/obstruction native decisions")
    check_p4_noncompensatory_authority_gate()
    print("PASS P4 non-compensatory hard-gate native decisions")
    check_p5_protected_self_change_readiness()
    print("PASS P5 protected readiness/no-self-promotion native decisions")
    print("P1-P5 NATIVE EMBEDDING V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
