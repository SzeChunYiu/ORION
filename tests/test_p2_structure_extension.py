from __future__ import annotations

from dataclasses import replace

import pytest

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p2_structure import (
    CandidateMethodSignature,
    StructuralCandidateStatus,
    StructuralNeed,
    StructuralRouteKind,
    StructuralRouteStop,
    assess_structural_candidate,
    build_structural_route,
    routes_are_earned_independent,
    stop_structural_route,
    structural_match_score,
)


def digest(label: str) -> str:
    return content_digest({"label": label})


def need() -> StructuralNeed:
    return StructuralNeed(
        need_id="need:preserve-structure",
        source_object_id="P6:signature:17",
        source_object_digest=digest("signature-17"),
        assumptions=("finite_state",),
        invariants=("preserve_feasibility",),
        effects=("reduce_search_space",),
        failure_signature=("local_minimum",),
        representation_signature=("state_graph",),
        reconstruction="lift_solution",
    )


def candidate(**changes: object) -> CandidateMethodSignature:
    payload: dict[str, object] = {
        "candidate_id": "donor:valid",
        "domain": "distant-domain",
        "assumptions": ("finite_state",),
        "invariants": ("preserve_feasibility",),
        "effects": ("reduce_search_space",),
        "reconstruction": "lift_solution",
        "provenance_digest": digest("donor"),
    }
    payload.update(changes)
    return CandidateMethodSignature(**payload)


def test_valid_different_domain_candidate_is_candidate_only():
    receipt = assess_structural_candidate(need(), candidate())
    receipt.verify()
    assert receipt.status is StructuralCandidateStatus.CANDIDATE
    assert receipt.authority_terminal == "NONE"
    assert set(receipt.matched_coordinates) == {
        "assumptions",
        "effects",
        "invariants",
        "reconstruction",
    }
    assert receipt.unsigned_payload()["can_certify_transfer"] is False


def test_same_surface_shape_with_incompatible_assumption_is_obstruction():
    receipt = assess_structural_candidate(
        need(),
        candidate(assumptions=("continuous_state",)),
    )
    assert receipt.status is StructuralCandidateStatus.OBSTRUCTION
    assert "ASSUMPTION_MISMATCH:finite_state" in receipt.reason_codes
    assert structural_match_score(need(), candidate(assumptions=("continuous_state",))) < 0


def test_missing_reconstruction_is_cannot_check_not_candidate():
    receipt = assess_structural_candidate(need(), candidate(reconstruction=None))
    assert receipt.status is StructuralCandidateStatus.CANNOT_CHECK
    assert receipt.reason_codes == ("RECONSTRUCTION_UNKNOWN",)


def test_missing_provenance_is_cannot_check():
    receipt = assess_structural_candidate(need(), candidate(provenance_digest=""))
    assert receipt.status is StructuralCandidateStatus.CANNOT_CHECK
    assert receipt.reason_codes == ("PROVENANCE_UNKNOWN",)


def test_structural_route_derives_from_bound_need_and_cannot_close_task():
    route = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.FAILURE_SIGNATURE,
        backend_identity="backend:openalex:v1",
        query_derivation_identity="derive:failure:v1",
        capture_identity="capture:2026-08-18:a",
    )
    route.verify()
    assert "local_minimum" in route.query_terms
    assert route.unsigned_payload()["can_close_task"] is False
    assert route.unsigned_payload()["can_certify_transfer"] is False


def test_route_label_does_not_create_earned_independence():
    first = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.METHOD_SIGNATURE,
        backend_identity="backend:shared",
        query_derivation_identity="derive:shared",
        capture_identity="capture:shared",
    )
    second = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.REPRESENTATION_ANALOGY,
        backend_identity="backend:shared",
        query_derivation_identity="derive:shared",
        capture_identity="capture:shared",
    )
    assert first.route_id != second.route_id
    assert not routes_are_earned_independent(first, second)


def test_earned_independence_requires_backend_derivation_and_capture_difference():
    first = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.METHOD_SIGNATURE,
        backend_identity="backend:a",
        query_derivation_identity="derive:a",
        capture_identity="capture:a",
    )
    second = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.FAILURE_SIGNATURE,
        backend_identity="backend:b",
        query_derivation_identity="derive:b",
        capture_identity="capture:b",
    )
    assert routes_are_earned_independent(first, second)


def test_unavailable_structural_route_remains_task_open():
    route = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.METHOD_SIGNATURE,
        backend_identity="backend:a",
        query_derivation_identity="derive:a",
        capture_identity="capture:a",
    )
    stop = stop_structural_route(
        route,
        terminal=StructuralRouteStop.UNAVAILABLE,
        reason="provider unavailable",
    )
    stop.verify()
    assert stop.task_terminal == "OPEN"
    assert stop.unsigned_payload()["can_close_task"] is False


def test_exhausted_method_family_cannot_become_task_stop():
    route = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.METHOD_SIGNATURE,
        backend_identity="backend:a",
        query_derivation_identity="derive:a",
        capture_identity="capture:a",
    )
    stop = stop_structural_route(
        route,
        terminal=StructuralRouteStop.EXHAUSTED,
        reason="bounded local family exhausted",
    )
    assert stop.task_terminal == "OPEN"


def test_structural_route_is_content_bound_to_source_signature():
    route = build_structural_route(
        need(),
        derivation_kind=StructuralRouteKind.METHOD_SIGNATURE,
        backend_identity="backend:a",
        query_derivation_identity="derive:a",
        capture_identity="capture:a",
    )
    with pytest.raises(ValueError):
        replace(route, source_object_digest=digest("changed-signature")).verify()


def test_random_semantic_distance_has_no_privileged_status():
    unrelated = candidate(
        candidate_id="donor:random-distant",
        domain="very-distant",
        assumptions=("continuous_state",),
        invariants=("preserve_mass",),
        effects=("increase_entropy",),
        reconstruction="different_lift",
    )
    receipt = assess_structural_candidate(need(), unrelated)
    assert receipt.status is StructuralCandidateStatus.OBSTRUCTION


def test_mapping_adapter_preserves_unknowns_instead_of_inventing_coordinates():
    adapted = StructuralNeed.from_mapping(
        need_id="need:adapter",
        source_object_id="P3:projection:4",
        source_object_digest=digest("projection"),
        coordinates={
            "invariants": ["preserve_feasibility"],
            "failure_signature": ["branch_explosion"],
        },
    )
    assert adapted.assumptions == ()
    assert adapted.reconstruction is None
    assert adapted.invariants == ("preserve_feasibility",)
