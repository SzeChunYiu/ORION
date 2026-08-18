from __future__ import annotations

from orion.self_orion.revision_gate import RevisionGateStatus, assess_revision_gate
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


def responsibility(*, identified: bool = True):
    left = build_responsibility_hypothesis(
        hypothesis_id="interface-gap",
        claim_id="claim:v3",
        expected_observations={"probe": ("INTERFACE",)},
        support_evidence_ids=("evidence:left",),
    )
    right = build_responsibility_hypothesis(
        hypothesis_id="model-gap",
        claim_id="claim:v3",
        expected_observations={"probe": ("MODEL",) if identified else ("INTERFACE",)},
        support_evidence_ids=("evidence:right",),
    )
    return assess_responsibility(
        (left, right), observed_outcomes={"probe": "INTERFACE"}
    )


def interface(state: InterfaceCheckState):
    return assess_interface_adequacy(
        (
            build_interface_check(
                check_id="interface-check",
                scope="FRAME",
                state=state,
                evidence_ids=("evidence:interface",),
                required=True,
            ),
        )
    )


def mechanics():
    narrow = build_mechanic(
        mechanic_id="repair-interface",
        claim_id="claim:v3",
        kind="INTERFACE_REPAIR",
        write_coordinates=("F",),
        hard_requirements=("interface-failure",),
        preservation_obligations=("preserve:model", "preserve:objective"),
    )
    broad = build_mechanic(
        mechanic_id="rewrite-model",
        claim_id="claim:v3",
        kind="MODEL_REVISION",
        write_coordinates=("F", "M"),
        hard_requirements=("interface-failure",),
        preservation_obligations=("preserve:objective",),
    )
    obligations = {"interface-failure": ObligationState.SATISFIED}
    return (
        narrow,
        broad,
    ), (
        assess_mechanic(narrow, obligation_states=obligations),
        assess_mechanic(broad, obligation_states=obligations),
    )


def test_failed_interface_selects_only_registered_narrow_interface_repair() -> None:
    candidates, assessments = mechanics()

    report = assess_revision_gate(
        responsibility=responsibility(),
        interface=interface(InterfaceCheckState.FAIL),
        mechanics=candidates,
        assessments=assessments,
        responsibility_bindings={
            "interface-gap": ("repair-interface",),
            "model-gap": ("rewrite-model",),
        },
        interface_repair_mechanic_ids=("repair-interface",),
        interface_coordinates=("F",),
    )

    assert report.status is RevisionGateStatus.CANDIDATE_SELECTED
    assert report.selected_mechanic_id == "repair-interface"
    assert "INTERFACE_REPAIR_PRECEDENCE" in report.reasons
    assert report.grants_adoption_authority is False
    assert report.grants_promotion_authority is False


def test_failed_interface_has_no_broad_fallback_when_narrow_repair_unavailable() -> None:
    candidates, assessments = mechanics()

    report = assess_revision_gate(
        responsibility=responsibility(),
        interface=interface(InterfaceCheckState.FAIL),
        mechanics=candidates,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("rewrite-model",)},
        interface_repair_mechanic_ids=(),
        interface_coordinates=("F",),
    )

    assert report.status is RevisionGateStatus.INTERFACE_REPAIR_REQUIRED
    assert report.selected_mechanic_id is None


def test_unresolved_interface_blocks_material_revision() -> None:
    candidates, assessments = mechanics()

    report = assess_revision_gate(
        responsibility=responsibility(),
        interface=interface(InterfaceCheckState.UNRESOLVED),
        mechanics=candidates,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("repair-interface",)},
        interface_repair_mechanic_ids=("repair-interface",),
        interface_coordinates=("F",),
    )

    assert report.status is RevisionGateStatus.UNRESOLVED
    assert report.selected_mechanic_id is None
    assert "INTERFACE_ADEQUACY_UNRESOLVED" in report.reasons


def test_ambiguous_responsibility_blocks_selection_even_when_interface_is_adequate() -> None:
    candidates, assessments = mechanics()

    report = assess_revision_gate(
        responsibility=responsibility(identified=False),
        interface=interface(InterfaceCheckState.PASS),
        mechanics=candidates,
        assessments=assessments,
        responsibility_bindings={
            "interface-gap": ("repair-interface",),
            "model-gap": ("rewrite-model",),
        },
        interface_repair_mechanic_ids=("repair-interface",),
        interface_coordinates=("F",),
    )

    assert report.status is RevisionGateStatus.UNRESOLVED
    assert report.selected_mechanic_id is None
    assert "RESPONSIBILITY_NOT_IDENTIFIED" in report.reasons


def test_adequate_interface_and_identified_responsibility_use_t1_minimal_selection() -> None:
    candidates, assessments = mechanics()

    report = assess_revision_gate(
        responsibility=responsibility(),
        interface=interface(InterfaceCheckState.PASS),
        mechanics=candidates,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("repair-interface", "rewrite-model")},
        interface_repair_mechanic_ids=("repair-interface",),
        interface_coordinates=("F",),
    )

    assert report.status is RevisionGateStatus.CANDIDATE_SELECTED
    assert report.selected_mechanic_id == "repair-interface"
    assert report.selection_digest is not None


def test_missing_responsibility_binding_fails_closed() -> None:
    candidates, assessments = mechanics()

    report = assess_revision_gate(
        responsibility=responsibility(),
        interface=interface(InterfaceCheckState.PASS),
        mechanics=candidates,
        assessments=assessments,
        responsibility_bindings={},
        interface_repair_mechanic_ids=("repair-interface",),
        interface_coordinates=("F",),
    )

    assert report.status is RevisionGateStatus.UNRESOLVED
    assert report.selected_mechanic_id is None
    assert "RESPONSIBILITY_BINDING_MISSING:interface-gap" in report.reasons


def test_out_of_scope_interface_repair_is_refused() -> None:
    candidates, assessments = mechanics()

    report = assess_revision_gate(
        responsibility=responsibility(),
        interface=interface(InterfaceCheckState.FAIL),
        mechanics=candidates,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("repair-interface",)},
        interface_repair_mechanic_ids=("rewrite-model",),
        interface_coordinates=("F",),
    )

    assert report.status is RevisionGateStatus.INTERFACE_REPAIR_REQUIRED
    assert report.selected_mechanic_id is None
    assert "INTERFACE_REPAIR_FOOTPRINT_OUT_OF_SCOPE:rewrite-model" in report.reasons
