"""Revived Self-ORION subject for the pre-registered V4 successor panel.

``FULL_T7_V4`` is the V3 ``FULL_T7`` chain with the preservation wiring the V3
confirmatory execution left unexercised (frozen one-stage attribution, receipt
of 2026-08-24): candidate-visible preservation obligations are projected into
the revision gate as obligation states and forbidden writes, so a repair that
diagnosis licenses but whose write coordinate is preserved blocks with
``RevisionGateStatus.NO_ADMISSIBLE`` and the policy refuses (``UNRESOLVED``)
instead of promoting.

Pre-registered revival lever (frozen in the V3 execution receipt before this
module existed): "Successor panel with hypothesis expectation sets completable
within the bounded protocol (the committed development-suite contract) plus
preservation-conflict cases exercising the revision-gate blocking branch;
strictly more coverage than this panel."  This module implements the subject
side of that lever; ``build_confirmatory_suite_v2.py`` implements the panel
side.  All V3 baseline policies are reused verbatim through delegation so the
arms stay identical to the frozen V3 execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from orion.self_orion.epistemic_control import (
    EpistemicControlStatus,
    compose_epistemic_control,
)
from orion.self_orion.revision_gate import assess_revision_gate
from orion.study.p5.revision_level_v3_policies import (
    FeedbackMode,
    PolicyKind,
    ProtectedFeedbackOracle,
    RevisionPolicyDecision,
    _choose_discriminator,
    run_revision_policy,
)
from orion.transfer.v2.epistemic_computation import (
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    ObligationState,
    assess_mechanic,
    build_mechanic,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)

SUBJECT_POLICY_ID = "FULL_T7_V4"
_PRESERVE_PREFIX = "preserve:"
_MECHANIC_PREFIX = "v4:"


def _write_coordinate_v4(label: str, invasiveness: Mapping[str, Any]) -> str:
    return f"revision/{int(invasiveness.get(label, 999))}/{label.lower()}"


def _preservation_projection(case: Mapping[str, Any]) -> tuple[dict[str, ObligationState], tuple[str, ...]]:
    """Project candidate-visible preservation obligations into gate inputs.

    Each ``preserve:<target>`` obligation contributes one SATISFIED obligation
    state (the protected target currently holds) and one forbidden write (the
    target must still hold after any revision).  Obligations that do not use
    the coordinate-shaped ``preserve:`` form are carried as mechanic-level
    preservation obligations only, exactly as in V3.
    """

    obligation_states: dict[str, ObligationState] = {}
    forbidden: list[str] = []
    for raw in case.get("preservation_obligations", ()):
        obligation = str(raw)
        if not obligation.startswith(_PRESERVE_PREFIX):
            continue
        target = obligation[len(_PRESERVE_PREFIX):]
        if not target:
            continue
        obligation_states[target] = ObligationState.SATISFIED
        if target not in forbidden:
            forbidden.append(target)
    return obligation_states, tuple(forbidden)


def _simple_decision_v4(
    case: Mapping[str, Any],
    selected: str,
    *,
    trace: tuple[str, ...],
    actions: tuple[str, ...] = (),
    feedback: tuple[tuple[str, str], ...] = (),
) -> RevisionPolicyDecision:
    return RevisionPolicyDecision.build(
        policy_id=SUBJECT_POLICY_ID,
        case_id=str(case["case_id"]),
        diagnostic_actions=actions,
        observed_feedback=feedback,
        selected_revision_class=selected,
        trace=trace,
        analysis_only=False,
        excluded_from_superiority_claim=False,
    )


def _run_full_t7_v4(case: Mapping[str, Any], oracle: ProtectedFeedbackOracle) -> RevisionPolicyDecision:
    action_id = _choose_discriminator(case)
    if action_id is None:
        return _simple_decision_v4(case, "UNRESOLVED", trace=("T7V4:NO_AFFORDABLE_DIAGNOSTIC",))
    outcome = oracle.observe(action_id)
    claim_id = f"P5.V4:{case['case_id']}"
    hypotheses_raw = case.get("hypotheses")
    if not isinstance(hypotheses_raw, Mapping):
        raise ValueError("hypotheses must be an object")
    responsibility_hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id=str(label),
            claim_id=claim_id,
            expected_observations={
                str(discriminator_id): tuple(map(str, outcomes))
                for discriminator_id, outcomes in prediction.items()
            },
            support_evidence_ids=(f"candidate-hypothesis:{label}",),
        )
        for label, prediction in sorted(hypotheses_raw.items())
        if isinstance(prediction, Mapping)
    )
    responsibility = assess_responsibility(
        responsibility_hypotheses,
        observed_outcomes={action_id: outcome},
    )
    if responsibility.status is not ResponsibilityStatus.IDENTIFIED:
        return _simple_decision_v4(
            case,
            "UNRESOLVED",
            trace=("T7V4:RESPONSIBILITY_NOT_IDENTIFIED", responsibility.status.value),
            actions=(action_id,),
            feedback=((action_id, outcome),),
        )

    interface = assess_interface_adequacy(
        (
            build_interface_check(
                check_id="registered-benchmark-interface",
                scope="benchmark/candidate-interface",
                state=InterfaceCheckState.PASS,
                evidence_ids=(f"candidate-packet:{case['case_id']}",),
                required=True,
            ),
        )
    )
    invasiveness = case.get("revision_invasiveness", {})
    if not isinstance(invasiveness, Mapping):
        raise ValueError("revision_invasiveness must be an object")
    labels = tuple(map(str, case.get("competing_revision_classes", ())))
    mechanics = tuple(
        build_mechanic(
            mechanic_id=f"{_MECHANIC_PREFIX}{label}",
            claim_id=claim_id,
            kind=label,
            write_coordinates=(_write_coordinate_v4(label, invasiveness),),
            preservation_obligations=tuple(map(str, case.get("preservation_obligations", ()))),
        )
        for label in labels
    )
    obligation_states, forbidden_writes = _preservation_projection(case)
    assessments = tuple(
        assess_mechanic(
            mechanic,
            obligation_states=obligation_states,
            forbidden_writes=forbidden_writes,
        )
        for mechanic in mechanics
    )
    blocked = tuple(
        reason
        for assessment in assessments
        for reason in assessment.reasons
        if reason.startswith("FORBIDDEN_WRITE:")
    )
    bindings = {label: (f"{_MECHANIC_PREFIX}{label}",) for label in labels}
    revision = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings=bindings,
    )
    idle = build_computation_action(
        action_id="v4-local-stop",
        claim_id=claim_id,
        kind="LOCAL_STOP_SENTINEL",
        expected_decision_value=0.0,
        cost=0.0,
    )
    idle_assessment = assess_computation_action(idle, requirement_states={})
    computation = select_epistemic_computation((idle,), (idle_assessment,))
    control = compose_epistemic_control(revision=revision, computation=computation)
    if control.status is EpistemicControlStatus.REVISION_CANDIDATE and control.selected_revision_mechanic_id:
        mechanic_id = control.selected_revision_mechanic_id
        selected = (
            mechanic_id[len(_MECHANIC_PREFIX):]
            if mechanic_id.startswith(_MECHANIC_PREFIX)
            else mechanic_id
        )
    else:
        selected = "UNRESOLVED"
    trace = (
        "T7V4:RESPONSIBILITY_GATE",
        f"RESPONSIBILITY:{responsibility.status.value}",
        f"REVISION_GATE:{revision.status.value}",
        f"CONTROL:{control.status.value}",
    )
    if blocked:
        trace = trace + (f"PRESERVATION_BLOCKED:{','.join(sorted(blocked))}",)
    return _simple_decision_v4(
        case,
        selected,
        trace=trace,
        actions=(action_id,),
        feedback=((action_id, outcome),),
    )


def run_revision_policy_v4(
    policy: "PolicyKind | str",
    case: Mapping[str, Any],
    feedback_oracle: ProtectedFeedbackOracle,
    *,
    protected_gold_revision_class: str | None = None,
) -> RevisionPolicyDecision:
    """Dispatch for the V4 successor panel.

    ``FULL_T7_V4`` runs the preservation-wired subject; every other policy id
    delegates to the frozen V3 implementation unchanged (arms stay identical to
    the V3 confirmatory execution, including the ``FULL_T7`` parent arm).
    """

    if str(case.get("case_id", "")) != feedback_oracle.case_id:
        raise ValueError("feedback oracle case identity mismatch")
    if str(policy) == SUBJECT_POLICY_ID:
        if protected_gold_revision_class is not None:
            raise ValueError("protected gold may only be supplied to the analysis-only oracle ceiling")
        return _run_full_t7_v4(case, feedback_oracle)
    return run_revision_policy(
        policy,
        case,
        feedback_oracle,
        protected_gold_revision_class=protected_gold_revision_class,
    )


__all__ = [
    "FeedbackMode",
    "PolicyKind",
    "ProtectedFeedbackOracle",
    "RevisionPolicyDecision",
    "SUBJECT_POLICY_ID",
    "run_revision_policy_v4",
]
