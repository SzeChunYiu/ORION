from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.self_orion.epistemic_control import compose_epistemic_control
from orion.self_orion.revision_gate import assess_revision_gate
from orion.transfer.v2.epistemic_computation import (
    ComputationActionState,
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from orion.transfer.v2.epistemic_responsibility import (
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
from orion.transfer.v2.social_evidence import (
    TruthfulnessState,
    assess_social_evidence_independence,
    build_social_evidence_record,
)
from orion.transfer.v2.uncertainty_containment import (
    ValidityState,
    assess_containment,
    build_validity_envelope,
)

CLAIM = "claim:t7"
ROOT = Path(__file__).resolve().parent
DEFAULT_PROTOCOL = ROOT / "T7_COUNTERMODELS_V1.json"
DEFAULT_OUTPUT = ROOT / "T7_COUNTERMODEL_SUMMARY_V1.json"


def _responsibility(*, ambiguous: bool = False):
    left = build_responsibility_hypothesis(
        hypothesis_id="interface-gap",
        claim_id=CLAIM,
        expected_observations={"probe": ("INTERFACE",)},
        support_evidence_ids=("e:left",),
    )
    right = build_responsibility_hypothesis(
        hypothesis_id="model-gap",
        claim_id=CLAIM,
        expected_observations={"probe": ("INTERFACE",) if ambiguous else ("MODEL",)},
        support_evidence_ids=("e:right",),
    )
    return assess_responsibility((left, right), observed_outcomes={"probe": "INTERFACE"})


def _interface(state: InterfaceCheckState = InterfaceCheckState.PASS):
    return assess_interface_adequacy(
        (
            build_interface_check(
                check_id="frame",
                scope="F",
                state=state,
                evidence_ids=("e:frame",),
                required=True,
            ),
        )
    )


def _revision_candidate():
    responsibility = _responsibility()
    interface = _interface()
    narrow = build_mechanic(
        mechanic_id="repair-interface",
        claim_id=CLAIM,
        kind="INTERFACE_REPAIR",
        write_coordinates=("F",),
        hard_requirements=("diagnostic",),
        preservation_obligations=("preserve:M",),
    )
    broad = build_mechanic(
        mechanic_id="rewrite-model",
        claim_id=CLAIM,
        kind="MODEL_REVISION",
        write_coordinates=("F", "M"),
        hard_requirements=("diagnostic",),
    )
    mechanics = (narrow, broad)
    assessments = tuple(
        assess_mechanic(item, obligation_states={"diagnostic": ObligationState.SATISFIED})
        for item in mechanics
    )
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("repair-interface", "rewrite-model")},
        interface_repair_mechanic_ids=("repair-interface",),
        interface_coordinates=("F",),
    )


def _revision_unresolved():
    responsibility = _responsibility(ambiguous=True)
    interface = _interface()
    mechanic = build_mechanic(
        mechanic_id="candidate",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("M",),
    )
    assessment = assess_mechanic(mechanic, obligation_states={})
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=(mechanic,),
        assessments=(assessment,),
        responsibility_bindings={"interface-gap": ("candidate",), "model-gap": ("candidate",)},
    )


def _revision_multiple():
    responsibility = _responsibility()
    interface = _interface()
    left = build_mechanic(
        mechanic_id="left",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("M",),
        preservation_obligations=("preserve:F",),
    )
    right = build_mechanic(
        mechanic_id="right",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("Q",),
        preservation_obligations=("preserve:F",),
    )
    mechanics = (left, right)
    assessments = tuple(assess_mechanic(item, obligation_states={}) for item in mechanics)
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("left", "right")},
    )


def _revision_no_admissible():
    responsibility = _responsibility()
    interface = _interface()
    mechanic = build_mechanic(
        mechanic_id="blocked",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("M",),
        hard_requirements=("required",),
    )
    assessment = assess_mechanic(
        mechanic,
        obligation_states={"required": ObligationState.VIOLATED},
    )
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=(mechanic,),
        assessments=(assessment,),
        responsibility_bindings={"interface-gap": ("blocked",)},
    )


def _computation(*, hard: bool = False, optional_value: float = 5.0, blocked: bool = False):
    action = build_computation_action(
        action_id="verify" if hard else "diagnose",
        claim_id=CLAIM,
        kind="VERIFY" if hard else "DIAGNOSE",
        expected_decision_value=0.0 if hard else optional_value,
        cost=1.0,
        hard_requirements=("ready",) if blocked else (),
        discharges_obligations=("must-verify",) if hard else (),
    )
    assessment = assess_computation_action(
        action,
        requirement_states={"ready": ComputationActionState.VIOLATED} if blocked else {},
    )
    return select_epistemic_computation(
        (action,),
        (assessment,),
        active_hard_obligations=("must-verify",) if hard else (),
    )


def _local_stop_computation():
    action = build_computation_action(
        action_id="wait",
        claim_id=CLAIM,
        kind="WAIT",
        expected_decision_value=1.0,
        cost=1.0,
    )
    assessment = assess_computation_action(action, requirement_states={})
    return select_epistemic_computation((action,), (assessment,))


def _containment(state: ValidityState):
    envelope = build_validity_envelope(
        envelope_id="env:t7",
        claim_id=CLAIM,
        subject_id="subject:t7",
        context_states={"current": state},
        evidence_ids=("e:validity",),
    )
    return assess_containment(envelope, context_id="current")


def _social(*, correlated: bool):
    left = build_social_evidence_record(
        report_id="r1",
        agent_id="a",
        claim_id=CLAIM,
        direct_observation_ids=("oa",),
        upstream_source_ids=("shared" if correlated else "sa",),
        truthfulness_state=TruthfulnessState.SATISFIED,
    )
    right = build_social_evidence_record(
        report_id="r2",
        agent_id="b",
        claim_id=CLAIM,
        direct_observation_ids=("ob",),
        upstream_source_ids=("shared" if correlated else "sb",),
        truthfulness_state=TruthfulnessState.SATISFIED,
    )
    return assess_social_evidence_independence((left, right))


def _case_report(kind: str):
    if kind == "hard_compute_preempts_revision":
        return compose_epistemic_control(revision=_revision_candidate(), computation=_computation(hard=True))
    if kind == "revision_preempts_optional_compute":
        return compose_epistemic_control(revision=_revision_candidate(), computation=_computation(optional_value=100.0))
    if kind == "unresolved_revision_recommends_compute":
        return compose_epistemic_control(revision=_revision_unresolved(), computation=_computation(optional_value=5.0))
    if kind == "invalid_context_contained":
        return compose_epistemic_control(
            revision=_revision_candidate(),
            computation=_local_stop_computation(),
            containment=_containment(ValidityState.INVALID),
        )
    if kind == "unresolved_context_fails_closed":
        return compose_epistemic_control(
            revision=_revision_candidate(),
            computation=_local_stop_computation(),
            containment=_containment(ValidityState.UNRESOLVED),
        )
    if kind == "correlated_social_evidence_blocks":
        return compose_epistemic_control(
            revision=_revision_candidate(),
            computation=_local_stop_computation(),
            social_evidence=(_social(correlated=True),),
            require_independent_social_evidence=True,
        )
    if kind == "independent_social_evidence_allows_revision":
        return compose_epistemic_control(
            revision=_revision_candidate(),
            computation=_local_stop_computation(),
            social_evidence=(_social(correlated=False),),
            require_independent_social_evidence=True,
        )
    if kind == "multiple_minimal_revisions":
        return compose_epistemic_control(revision=_revision_multiple(), computation=_computation(optional_value=100.0))
    if kind == "local_compute_stop_not_global_stop":
        return compose_epistemic_control(revision=_revision_unresolved(), computation=_local_stop_computation())
    if kind == "no_admissible_revision_or_compute":
        return compose_epistemic_control(revision=_revision_no_admissible(), computation=_computation(blocked=True))
    raise ValueError(f"unknown T7 countermodel kind: {kind}")


def derive_summary(protocol_path: Path = DEFAULT_PROTOCOL) -> dict[str, object]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    passed = 0
    for case in protocol["cases"]:
        report = _case_report(case["kind"])
        actual = {
            "id": case["id"],
            "status": report.status.value,
            "selected_computation": report.selected_computation_action_id,
            "selected_revision": report.selected_revision_mechanic_id,
            "grants_scientific_authority": report.grants_scientific_authority,
            "grants_revision_authority": report.grants_revision_authority,
            "grants_adoption_authority": report.grants_adoption_authority,
            "grants_promotion_authority": report.grants_promotion_authority,
            "grants_merge_authority": report.grants_merge_authority,
            "grants_global_task_stop_authority": report.grants_global_task_stop_authority,
        }
        ok = actual["status"] == case["expected_status"]
        if "expected_computation" in case:
            ok = ok and actual["selected_computation"] == case["expected_computation"]
        else:
            ok = ok and actual["selected_computation"] is None
        if "expected_revision" in case:
            ok = ok and actual["selected_revision"] == case["expected_revision"]
        else:
            ok = ok and actual["selected_revision"] is None
        ok = ok and not any(
            actual[key]
            for key in (
                "grants_scientific_authority",
                "grants_revision_authority",
                "grants_adoption_authority",
                "grants_promotion_authority",
                "grants_merge_authority",
                "grants_global_task_stop_authority",
            )
        )
        actual["pass"] = ok
        passed += int(ok)
        results.append(actual)
    terminal = protocol["expected_terminal"] if passed == len(results) else "T7_CONTROL_COMPOSITION_RED"
    return {
        "schema": "P6.HigherOrderEpistemicMechanics.T7CountermodelSummary.v1",
        "protocol_id": protocol["protocol_id"],
        "base_subject": protocol["base_subject"],
        "n_cases": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "terminal": terminal,
        "claim_ceiling": protocol["claim_ceiling"],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    summary = derive_summary(args.protocol)
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file():
            raise SystemExit(f"missing frozen T7 summary: {args.output}")
        if args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("frozen T7 summary differs from deterministic rederivation")
        print(summary["terminal"])
        return
    args.output.write_text(rendered, encoding="utf-8")
    print(summary["terminal"])


if __name__ == "__main__":
    main()
