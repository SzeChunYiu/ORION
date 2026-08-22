import re

import pytest

from orion.study.ea import (
    DeltaKind,
    ExactFamily,
    NodeKind,
    NodeStatus,
    ViewMode,
    analyze_identifiability,
    generate_case,
    generate_obligation_hostile_pair,
    generate_representation_hostile_pair,
    generate_suite,
)


FORBIDDEN_ID_WORDS = {
    "failure",
    "obligation",
    "reopen",
    "remint",
    "material",
    "transport",
    "support",
    "defeat",
    "unknown",
    "train",
    "dev",
    "test",
}


def _changed_statuses(case):
    return {
        op.target_id: op.value
        for op in case.gold_delta
        if op.kind is DeltaKind.SET_STATUS
    }


def _nodes_by_kind(case, kind):
    return [node for node in case.pre_state.nodes if node.kind is kind]


@pytest.mark.parametrize("family", list(ExactFamily))
def test_exact_case_is_deterministic_and_seed_remints_identity(family):
    first = generate_case(family, "seed-a")
    replay = generate_case(family, "seed-a")
    other = generate_case(family, "seed-b")

    assert first == replay
    assert first.case_id != other.case_id
    assert first.pre_state.world_id != other.pre_state.world_id
    first.verify()
    other.verify()


def test_representation_hostile_pair_collides_when_semantics_hidden():
    remint, material = generate_representation_hostile_pair("rep-pair")

    assert remint.fingerprint(ViewMode.TYPED) == material.fingerprint(ViewMode.TYPED)
    assert remint.fingerprint(ViewMode.FULL) != material.fingerprint(ViewMode.FULL)
    assert remint.gold_delta != material.gold_delta

    typed = analyze_identifiability((remint, material), ViewMode.TYPED)
    full = analyze_identifiability((remint, material), ViewMode.FULL)
    assert typed.deterministic_accuracy_ceiling == pytest.approx(0.5)
    assert typed.is_identifying is False
    assert full.deterministic_accuracy_ceiling == pytest.approx(1.0)
    assert full.is_identifying is True


def test_obligation_hostile_pair_collides_when_scope_hidden():
    nontransport, transport = generate_obligation_hostile_pair("obligation-pair")

    assert nontransport.fingerprint(ViewMode.TYPED) == transport.fingerprint(ViewMode.TYPED)
    assert nontransport.fingerprint(ViewMode.FULL) != transport.fingerprint(ViewMode.FULL)
    assert nontransport.gold_delta != transport.gold_delta

    typed = analyze_identifiability((nontransport, transport), ViewMode.TYPED)
    full = analyze_identifiability((nontransport, transport), ViewMode.FULL)
    assert typed.deterministic_accuracy_ceiling == pytest.approx(0.5)
    assert typed.is_identifying is False
    assert full.deterministic_accuracy_ceiling == pytest.approx(1.0)
    assert full.is_identifying is True


def test_combined_hostile_pairs_have_exact_typed_ceiling_and_full_separation():
    rep = generate_representation_hostile_pair("combined-rep")
    obligation = generate_obligation_hostile_pair("combined-obligation")
    cases = (*rep, *obligation)

    typed = analyze_identifiability(cases, ViewMode.TYPED)
    full = analyze_identifiability(cases, ViewMode.FULL)

    assert typed.sample_count == 4
    assert typed.unique_fingerprint_count == 2
    assert typed.deterministic_accuracy_ceiling == pytest.approx(0.5)
    assert len(typed.collisions) == 2
    assert full.unique_fingerprint_count == 4
    assert full.deterministic_accuracy_ceiling == pytest.approx(1.0)
    assert full.is_identifying is True


def test_sparse_retraction_changes_only_dependency_component():
    case = generate_case(ExactFamily.SPARSE_RETRACTION, "sparse")
    statuses = _changed_statuses(case)

    assert list(statuses.values()).count(NodeStatus.RETRACTED.value) == 3
    assert len(statuses) == 3

    unchanged = {
        node.node_id: node.status
        for node in case.post_state.nodes
        if node.node_id not in statuses
    }
    assert unchanged
    assert set(unchanged.values()) == {NodeStatus.ACTIVE}


def test_independent_support_prevents_overbroad_descendant_retraction():
    case = generate_case(ExactFamily.INDEPENDENT_SUPPORT, "independent")
    statuses = _changed_statuses(case)

    assert len(statuses) == 1
    assert next(iter(statuses.values())) == NodeStatus.RETRACTED.value
    claims = _nodes_by_kind(case, NodeKind.CLAIM)
    post = {node.node_id: node.status for node in case.post_state.nodes}
    assert all(post[node.node_id] is NodeStatus.ACTIVE for node in claims)


def test_active_defeater_retracts_claim_and_hard_dependent():
    case = generate_case(ExactFamily.ACTIVE_DEFEATER, "defeater")
    statuses = _changed_statuses(case)
    claims = _nodes_by_kind(case, NodeKind.CLAIM)

    assert all(statuses[node.node_id] == NodeStatus.RETRACTED.value for node in claims)
    evidence = _nodes_by_kind(case, NodeKind.EVIDENCE)
    activated = [node for node in evidence if node.status is NodeStatus.RETRACTED]
    assert len(activated) == 1
    assert statuses[activated[0].node_id] == NodeStatus.ACTIVE.value


def test_material_representation_change_reopens_scoped_failure():
    case = generate_case(ExactFamily.FAILURE_REOPEN_MATERIAL, "material")
    statuses = _changed_statuses(case)
    failure = _nodes_by_kind(case, NodeKind.FAILURE)[0]
    method = _nodes_by_kind(case, NodeKind.METHOD)[0]

    assert statuses[failure.node_id] == NodeStatus.STALE.value
    assert statuses[method.node_id] == NodeStatus.ACTIVE.value


def test_representation_remint_does_not_reopen_failure():
    case = generate_case(ExactFamily.FAILURE_REOPEN_REMINT, "remint")
    statuses = _changed_statuses(case)
    failure = _nodes_by_kind(case, NodeKind.FAILURE)[0]
    method = _nodes_by_kind(case, NodeKind.METHOD)[0]

    assert failure.node_id not in statuses
    assert method.node_id not in statuses
    post = {node.node_id: node.status for node in case.post_state.nodes}
    assert post[failure.node_id] is NodeStatus.ACTIVE
    assert post[method.node_id] is NodeStatus.BLOCKED


def test_nontransportable_obligation_becomes_unknown_and_propagates():
    case = generate_case(ExactFamily.OBLIGATION_NONTRANSPORT, "nontransport")
    statuses = _changed_statuses(case)
    obligation = _nodes_by_kind(case, NodeKind.OBLIGATION)[0]
    claim = _nodes_by_kind(case, NodeKind.CLAIM)[0]

    assert statuses[obligation.node_id] == NodeStatus.UNKNOWN.value
    assert statuses[claim.node_id] == NodeStatus.UNKNOWN.value


def test_transportable_obligation_survives_representation_change():
    case = generate_case(ExactFamily.OBLIGATION_TRANSPORT, "transport")
    statuses = _changed_statuses(case)

    assert statuses == {}
    assert all(node.status is NodeStatus.ACTIVE for node in case.post_state.nodes)


def test_unknown_prerequisite_propagates_unknown_not_refutation():
    case = generate_case(ExactFamily.UNKNOWN_PROPAGATION, "unknown")
    statuses = _changed_statuses(case)

    assert len(statuses) == 3
    assert set(statuses.values()) == {NodeStatus.UNKNOWN.value}


def test_irrelevant_retraction_preserves_supported_claim():
    case = generate_case(ExactFamily.IRRELEVANT_RETRACTION, "irrelevant")
    statuses = _changed_statuses(case)
    claim = _nodes_by_kind(case, NodeKind.CLAIM)[0]
    post = {node.node_id: node.status for node in case.post_state.nodes}

    assert claim.node_id not in statuses
    assert post[claim.node_id] is NodeStatus.ACTIVE


def test_model_payload_excludes_evaluator_family_case_and_gold():
    case = generate_case(ExactFamily.FAILURE_REOPEN_MATERIAL, "metadata")

    for mode in ViewMode:
        serialized = repr(case.model_payload(mode)).lower()
        assert case.family.value.lower() not in serialized
        assert case.case_id.lower() not in serialized
        assert "gold_delta" not in serialized
        assert "family" not in serialized


def test_generated_identity_tokens_are_opaque():
    for case in generate_suite("opaque-suite"):
        tokens = [case.pre_state.world_id, case.case_id]
        tokens.extend(node.node_id for node in case.pre_state.nodes)
        tokens.extend(node.surface_label for node in case.pre_state.nodes)
        tokens.extend(edge.edge_id for edge in case.pre_state.edges)
        tokens.extend(edge.surface_label for edge in case.pre_state.edges)
        tokens.extend(
            (
                case.pre_state.representation.representation_id,
                case.pre_state.representation.semantic_key,
            )
        )
        if case.intervention.new_representation is not None:
            tokens.extend(
                (
                    case.intervention.new_representation.representation_id,
                    case.intervention.new_representation.semantic_key,
                )
            )
        for token in tokens:
            lowered = token.lower()
            assert re.fullmatch(r"[a-z][0-9a-f]{12,24}", token), token
            assert not any(word in lowered for word in FORBIDDEN_ID_WORDS)
