"""The three knowledge layers: what each schema admits, and what it refuses."""

from __future__ import annotations

from dataclasses import replace

import pytest

from orion.core.claims import ClaimAuthority
from orion.programme.identity import verify_seal
from orion.programme.method_knowledge import (
    CausalSupportLink,
    MethodKnowledgeRecord,
    method_knowledge_payload,
    method_promotion_blockers,
    validate_method_knowledge_record,
)
from orion.programme.object_knowledge import (
    ObjectKnowledgeRecord,
    object_knowledge_payload,
    validate_object_knowledge_layer,
    validate_object_knowledge_record,
)
from orion.programme.records import ObjectAuthority, Outcome, RouteAvailability
from orion.programme.search_universe_knowledge import (
    BlindSpotTest,
    RouteState,
    SearchUniverseKnowledgeRecord,
    search_universe_payload,
    validate_search_universe_record,
)


def test_object_authority_is_a_superset_of_claim_authority() -> None:
    """The extension relationship is pinned, so core cannot drift away silently."""

    for authority in ClaimAuthority:
        assert authority.value in {item.value for item in ObjectAuthority}


def test_well_formed_records_validate(
    object_record: ObjectKnowledgeRecord,
    search_universe: SearchUniverseKnowledgeRecord,
    method_record: MethodKnowledgeRecord,
) -> None:
    assert validate_object_knowledge_record(object_record) == ()
    assert validate_search_universe_record(search_universe) == ()
    assert validate_method_knowledge_record(method_record) == ()
    assert method_promotion_blockers(method_record) == ()


def test_payloads_are_sealed(
    object_record: ObjectKnowledgeRecord,
    search_universe: SearchUniverseKnowledgeRecord,
    method_record: MethodKnowledgeRecord,
) -> None:
    for payload in (
        object_knowledge_payload(object_record),
        search_universe_payload(search_universe),
        method_knowledge_payload(method_record),
    ):
        assert verify_seal(payload) == ()


def test_verified_claim_with_contradiction_needs_a_resolution_certificate(
    object_record: ObjectKnowledgeRecord,
) -> None:
    contested = replace(
        object_record,
        contradicts_object_ids=("obj-2",),
        view_group_id="vg-1",
    )
    errors = validate_object_knowledge_record(contested)
    assert any("resolution certificate" in error for error in errors)


def test_verified_claim_must_name_its_search_universe(
    object_record: ObjectKnowledgeRecord,
) -> None:
    unbound = replace(object_record, search_universe_record_id=None)
    errors = validate_object_knowledge_record(unbound)
    assert any("search-universe record" in error for error in errors)


def test_open_claim_may_carry_no_evidence(object_record: ObjectKnowledgeRecord) -> None:
    open_claim = replace(
        object_record,
        authority=ObjectAuthority.OPEN,
        evidence_ids=(),
        provenance=(),
        search_universe_record_id=None,
    )
    assert validate_object_knowledge_record(open_claim) == ()


def test_one_sided_contradiction_is_rejected(object_record: ObjectKnowledgeRecord) -> None:
    left = replace(
        object_record,
        contradicts_object_ids=("obj-2",),
        view_group_id="vg-1",
        resolution_certificate_id="cert-1",
    )
    right = replace(
        object_record,
        object_id="obj-2",
        claim_id="claim-2",
        authority=ObjectAuthority.SOURCE_PROJECTION,
    )
    errors = validate_object_knowledge_layer((left, right))
    assert any("not mutual" in error for error in errors)


def test_records_without_coordinates_cannot_be_invalidated(
    object_record: ObjectKnowledgeRecord,
) -> None:
    floating = replace(object_record, depends_on_coordinates=())
    errors = validate_object_knowledge_record(floating)
    assert any("depends_on_coordinates" in error for error in errors)


def test_unrooted_coordinate_is_rejected(object_record: ObjectKnowledgeRecord) -> None:
    errors = validate_object_knowledge_record(
        replace(object_record, depends_on_coordinates=("Z.SOMETHING",))
    )
    assert any("rooted coordinate" in error for error in errors)


def test_saturation_claim_refused_while_a_route_was_never_attempted(
    search_universe: SearchUniverseKnowledgeRecord,
) -> None:
    unwalked = replace(
        search_universe,
        routes=(
            *search_universe.routes,
            RouteState(
                "r-3", "literature", "preprint", RouteAvailability.NOT_ATTEMPTED, "no budget"
            ),
        ),
    )
    errors = validate_search_universe_record(unwalked)
    assert any("NOT_ATTEMPTED" in error for error in errors)


def test_saturation_claim_refused_when_blind_spot_test_did_not_run(
    search_universe: SearchUniverseKnowledgeRecord,
) -> None:
    unrun = replace(
        search_universe,
        blind_spot_tests=(BlindSpotTest("bs-1", "probe", Outcome.CANNOT_CHECK),),
    )
    errors = validate_search_universe_record(unrun)
    assert any("did not run" in error for error in errors)


def test_universe_without_reopen_rules_is_permanently_closed(
    search_universe: SearchUniverseKnowledgeRecord,
) -> None:
    errors = validate_search_universe_record(replace(search_universe, reopen_rules=()))
    assert any("reopen" in error for error in errors)


def test_multi_stage_failure_attribution_is_rejected(
    method_record: MethodKnowledgeRecord,
) -> None:
    diffuse = replace(
        method_record,
        causal_support=(
            CausalSupportLink(
                link_id="cs-1",
                failure_class="F-A",
                attributed_stage="ENTRY_EXECUTION,EXIT_POLICY",
                intervention_id="I-1",
                evidence_ids=("ev-2",),
            ),
        ),
    )
    errors = validate_method_knowledge_record(diffuse)
    assert any("several stages" in error for error in errors)


def test_self_verified_fresh_transfer_is_rejected(
    method_record: MethodKnowledgeRecord,
) -> None:
    fresh = method_record.fresh_transfer[0]
    self_graded = replace(
        method_record,
        transfer_evidence=(
            method_record.replay[0],
            replace(fresh, independently_verified=False),
        ),
    )
    errors = validate_method_knowledge_record(self_graded)
    assert any("self-verified" in error for error in errors)


def test_method_without_applicability_boundary_is_rejected(
    method_record: MethodKnowledgeRecord,
) -> None:
    errors = validate_method_knowledge_record(replace(method_record, applicability=()))
    assert any("applicability" in error for error in errors)


def test_promotion_blocks_without_fresh_transfer(
    method_record: MethodKnowledgeRecord,
) -> None:
    replay_only = replace(method_record, transfer_evidence=(method_record.replay[0],))
    assert "no independent fresh-transfer evidence" in method_promotion_blockers(replay_only)


def test_record_version_below_one_is_rejected(object_record: ObjectKnowledgeRecord) -> None:
    with pytest.raises(ValueError):
        replace(object_record, record_version=0)
