from __future__ import annotations

from dataclasses import replace

import pytest

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p6_method_fibres import (
    CompositionContract,
    CompositionKind,
    CompositionStatus,
    FibreStatus,
    ReductionState,
    assess_membership,
    build_fibre,
    build_reduction,
    build_signature,
    membership_evidence,
)
from orion.transfer.v2.p6_method_fibre_completion import (
    FibreCompositionOutcome,
    P1_ADAPTER_PROFILE,
    adapt_p1_method_realization,
    bind_fibre_lineage,
    bind_signature_contract,
    build_reduction_procedure,
    check_substitution,
    classify_fibre_composition,
    preorder_witness,
    representation_project,
)


def d(value: str) -> str:
    return content_digest({"value": value})


def p1_payload(method_id: str = "bisection") -> dict[str, object]:
    return {
        "method_id": method_id,
        "source_digest": d(f"source:{method_id}"),
        "target_problem_role_signature": "bounded_monotone_threshold_localization",
        "preconditions": ["ordered_interval", "bracketed_target"],
        "assumptions": ["monotone_response"],
        "resources": ["binary_test"],
        "representation_in": "interval",
        "representation_out": "interval",
        "transformation_mechanic_graph": ["midpoint_probe", "retain_compatible_half"],
        "dependency_order": [["midpoint_probe", "retain_compatible_half"]],
        "invariants": ["target_remains_bracketed"],
        "progress_measure": "interval_width",
        "effect_contract": ["shrink_interval"],
        "terminal_condition": "width<=epsilon",
        "reconstruction_map": "return_midpoint",
        "failure_modes": ["target_not_bracketed", "response_not_monotone"],
        "lineage_provenance": [f"donor:{method_id}"],
        "authority_boundary": "FORMAL_STRUCTURE_ONLY",
        "unknown_fields": [],
    }


def reduction_and_signature(method_id: str = "bisection"):
    view, adapter = adapt_p1_method_realization(
        p1_payload(method_id),
        upstream_digest=d(f"p1:{method_id}"),
    )
    reduction = build_reduction(
        view,
        reduction_id=f"red:{method_id}",
        claim_id="threshold-localization",
        preserved=("preconditions", "invariants", "effects", "reconstruction"),
        erased=("actions", "dependencies", "termination", "failures", "lineage"),
        load_bearing=("preconditions", "invariants", "effects", "reconstruction"),
        obligations=("effect_equivalence", "reconstruction_equivalence"),
        justifications={
            "actions": "surface realization may vary",
            "dependencies": "internal schedule is not part of this claim",
            "termination": "bounded separately by retained progress obligation",
            "failures": "failure region retained in membership evidence",
            "lineage": "retained by content-addressed adapter/fibre lineage index",
        },
    )
    signature = build_signature(view, reduction)
    return view, adapter, reduction, signature


def member(signature, view, **updates):
    values = dict(
        assumptions=True,
        invariants=True,
        effects=True,
        reconstruction=True,
        provenance=True,
        beyond_single_panel=True,
    )
    values.update(updates)
    return assess_membership(
        signature,
        view,
        membership_evidence(signature, view, **values),
    )


def test_p1_adapter_is_version_gated_and_preserves_context():
    view, adapter, _, _ = reduction_and_signature()
    assert adapter.upstream_schema == "P1.MethodRealization.v1@issue-404"
    assert "authority_boundary" in P1_ADAPTER_PROFILE["mandatory"]
    assert dict(adapter.context_fields)["target_problem_role_signature"] == "bounded_monotone_threshold_localization"
    assert dict(adapter.context_fields)["assumptions"] == ("monotone_response",)
    assert view.lineage == ("donor:bisection",)
    assert adapter.authority_boundary == "FORMAL_STRUCTURE_ONLY"
    adapter.verify()


def test_adapter_rejects_missing_mandatory_identity_or_lineage():
    payload = p1_payload()
    payload.pop("lineage_provenance")
    with pytest.raises(ValueError, match="missing mandatory P1 fields"):
        adapt_p1_method_realization(payload, upstream_digest=d("p1"))


def test_reduction_procedure_binds_transformations_normalizations_and_context_partition():
    _, adapter, reduction, _ = reduction_and_signature()
    context_names = {name for name, _ in adapter.context_fields}
    procedure = build_reduction_procedure(
        reduction,
        adapter,
        transformations=("rename_domain_objects_to_roles",),
        normalizations=("canonicalize_ordered_interval",),
        preserved_context=tuple(sorted(context_names)),
        preservation_obligations=("context_transport_is_lossless_for_claim",),
    )
    procedure.verify()
    assert procedure.transformations == ("rename_domain_objects_to_roles",)
    assert procedure.normalizations == ("canonicalize_ordered_interval",)
    with pytest.raises(ValueError, match="unclassified"):
        build_reduction_procedure(
            reduction,
            adapter,
            transformations=("rename_domain_objects_to_roles",),
            preserved_context=(),
        )
    with pytest.raises(ValueError):
        replace(procedure, transformations=("tampered",)).verify()


def test_signature_contract_binds_provenance_load_bearing_and_equivalence_obligations():
    view, _, reduction, signature = reduction_and_signature()
    other = d("other-realization")
    contract = bind_signature_contract(
        signature,
        reduction,
        contributor_realization_digests=(view.digest, other),
        effect_obligations=("same_abstract_effect",),
        reconstruction_obligations=("maps_back_to_original_target",),
    )
    assert set(contract.contributor_realization_digests) == {view.digest, other}
    assert set(contract.load_bearing_coordinates) == set(reduction.load_bearing)
    assert contract.can_authorize_transfer is False
    assert contract.can_claim_novelty is False
    contract.verify()


def test_fibre_lineage_is_recoverable_from_member_digest():
    view, adapter, _, signature = reduction_and_signature()
    alt_view, alt_adapter, _, _ = reduction_and_signature("dose-titration")
    first = member(signature, view)
    second = member(signature, alt_view)
    assert first.status is FibreStatus.MEMBER
    assert second.status is FibreStatus.MEMBER
    fibre = build_fibre(signature, (first, second))
    index = bind_fibre_lineage(
        fibre,
        {view.digest: adapter.digest, alt_view.digest: alt_adapter.digest},
    )
    assert dict(index.member_links)[view.digest] == adapter.digest
    assert dict(index.member_links)[alt_view.digest] == alt_adapter.digest
    index.verify()


def test_compatible_substitution_is_explicit_and_non_authorizing():
    view, _, _, signature = reduction_and_signature()
    alt_view, _, _, _ = reduction_and_signature("dose-titration")
    source = member(signature, view)
    target = member(signature, alt_view)
    ok = check_substitution(
        source,
        target,
        interface=True,
        invariants=True,
        effects=True,
        reconstruction=True,
        authority=True,
    )
    assert ok.status is CompositionStatus.COMPATIBLE
    assert ok.can_authorize_transfer is False
    bad = check_substitution(
        source,
        target,
        interface=True,
        invariants=False,
        effects=True,
        reconstruction=True,
        authority=True,
    )
    assert bad.status is CompositionStatus.BLOCKED
    unknown = check_substitution(
        source,
        target,
        interface=True,
        invariants=True,
        effects=True,
        reconstruction=None,
        authority=True,
    )
    assert unknown.status is CompositionStatus.UNRESOLVED


def test_structural_preorder_is_reflexive_transitive_on_supported_examples_but_not_membership():
    a = preorder_witness(
        claim_id="c",
        lower_id="general",
        upper_id="mid",
        lower_preconditions=("finite",),
        upper_preconditions=("finite", "ordered"),
        lower_effects=("solve",),
        upper_effects=("solve",),
        obligations_satisfied=True,
    )
    b = preorder_witness(
        claim_id="c",
        lower_id="mid",
        upper_id="specific",
        lower_preconditions=("finite", "ordered"),
        upper_preconditions=("finite", "ordered", "bracketed"),
        lower_effects=("solve",),
        upper_effects=("solve",),
        obligations_satisfied=True,
    )
    ac = preorder_witness(
        claim_id="c",
        lower_id="general",
        upper_id="specific",
        lower_preconditions=("finite",),
        upper_preconditions=("finite", "ordered", "bracketed"),
        lower_effects=("solve",),
        upper_effects=("solve",),
        obligations_satisfied=True,
    )
    aa = preorder_witness(
        claim_id="c",
        lower_id="general",
        upper_id="general",
        lower_preconditions=("finite",),
        upper_preconditions=("finite",),
        lower_effects=("solve",),
        upper_effects=("solve",),
        obligations_satisfied=True,
    )
    assert a.related is b.related is ac.related is aa.related is True
    assert a.can_grant_fibre_membership is False


def test_composition_outcome_distinguishes_same_fibre_from_new_signature_and_failure():
    clean = CompositionContract(
        CompositionKind.SEQUENTIAL,
        right_preconditions=("ready",),
        left_guarantees=("ready",),
    )
    assert classify_fibre_composition(
        clean,
        retained_contract_preserved=True,
        footprint_changed=False,
    ) is FibreCompositionOutcome.STAYS_IN_FIBRE
    assert classify_fibre_composition(
        clean,
        retained_contract_preserved=True,
        footprint_changed=True,
    ) is FibreCompositionOutcome.NEW_SIGNATURE_REQUIRED
    bad = CompositionContract(
        CompositionKind.SEQUENTIAL,
        right_preconditions=("ready",),
        left_guarantees=(),
    )
    assert classify_fibre_composition(
        bad,
        retained_contract_preserved=True,
        footprint_changed=False,
    ) is FibreCompositionOutcome.BLOCKED
    recursive_unknown = CompositionContract(CompositionKind.RECURSIVE, rank_decreases=None)
    assert classify_fibre_composition(
        recursive_unknown,
        retained_contract_preserved=True,
        footprint_changed=False,
    ) is FibreCompositionOutcome.UNRESOLVED


def test_representation_project_requires_reconstruction():
    assert representation_project(True) is ReductionState.SUPPORTED
    assert representation_project(False) is ReductionState.OBSTRUCTION
    assert representation_project(None) is ReductionState.UNRESOLVED
