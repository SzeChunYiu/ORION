import dataclasses

import pytest

from orion.knowledge.backward_multiseed import (
    AlternativePredecessorSearch,
    BackwardObligation,
    BackwardObligationProposal,
    BackwardSeedFailureMode,
    ConnectionHistory,
    ConnectionNode,
    ConnectionNodeKind,
    ConnectionTrial,
    ConnectionVerdict,
    ImplicationStatus,
    MeetInMiddleVerdict,
    SeedFamily,
    SeedOrigin,
    TransitionEvidence,
    WaypointSeed,
    assess_meet_in_middle,
    assess_seed_diversity,
    audit_backward_seed_state,
    compute_bridge_residual,
    evaluate_connection,
    expand_backward,
)
from orion.knowledge.similarity import (
    DistinguishingProbeCertificate,
    MappingAdmissibility,
    ProbeFamily,
    SimilarityRelation,
    SimilarityWitness,
)


def _obligation(**overrides) -> BackwardObligation:
    values = dict(
        obligation_id="obl",
        root_goal_id="root",
        statement="local positivity on every index",
        structural_signature=("positivity", "index_family"),
        sufficient_for=("root",),
        supporting_family="INVARIANT",
        supporting_theorem_ids=("thm",),
        assumptions=("assumption",),
        representation="norm",
        scope="scope",
        source_evidence_ids=("evidence",),
        implication_status=ImplicationStatus.CANDIDATE_UNVERIFIED,
        alternative_search=AlternativePredecessorSearch.ALTERNATIVES_RECORDED,
        known_alternative_predecessor_families=("explicit-formula",),
    )
    values.update(overrides)
    return BackwardObligation(**values)


def _seed(seed_id: str, family: SeedFamily) -> WaypointSeed:
    return WaypointSeed(
        seed_id=seed_id,
        root_goal_id="root",
        atom_ids=("atom",),
        family=family,
        statement_or_object=f"object:{family.value}",
        representation="norm",
        structural_signature=("positivity",),
        origin=SeedOrigin.OPERATOR_APPLICATION,
        origin_operator_id="search_invariant",
        expected_useful_connection="expose norm-to-sign interface",
        falsifier_or_cheapest_connection_test="evaluate rank-one boundary",
        scope="scope",
    )


def _witness() -> SimilarityWitness:
    return SimilarityWitness(
        relation=SimilarityRelation.RELATIONALLY_ANALOGOUS,
        source_id="source",
        target_id="target",
        source_domain="A",
        target_domain="B",
        question_or_qoi="does positivity transport",
        mapping_pairs=(("norm", "sign"),),
        preserved=("monotonicity",),
        not_preserved=("index_uniformity",),
        regime=("regime",),
        evidence_ids=("evidence",),
        mapping_admissibility=MappingAdmissibility(
            family_id="mapping",
            declared_before_fit=True,
            constraints=("no-free-fit",),
            constraint_violations=(),
            null_calibration_passed=True,
        ),
        probe_family=ProbeFamily("probes", ("p1",)),
    )


def _nodes(source_id="forward", target_id="obligation"):
    source = ConnectionNode(source_id, ConnectionNodeKind.FORWARD_FRONTIER_STATE, "norm", ("positivity",))
    target = ConnectionNode(target_id, ConnectionNodeKind.BACKWARD_OBLIGATION, "norm", ("positivity",), frozenset({"candidate_invariant"}))
    return source, target


def _transition(*, checked=False, applicable=True) -> TransitionEvidence:
    return TransitionEvidence(
        operator_id="search_invariant",
        required_obstructions=frozenset({"missing_invariant"}),
        source_obstructions=frozenset({"missing_invariant"}) if applicable else frozenset(),
        source_facts=frozenset(),
        adds_facts=frozenset({"candidate_invariant"}),
        checker_id="checker" if checked else "",
        verification_artifact_id="artifact" if checked else "",
    )


def test_backward_obligation_is_structurally_candidate_only_never_necessary():
    obligation = _obligation()
    assert obligation.candidate_only
    assert not obligation.establishes_necessity
    assert not obligation.grants_root_progress
    names = {field.name for field in dataclasses.fields(obligation)}
    assert "candidate_only" not in names
    with pytest.raises(TypeError):
        dataclasses.replace(obligation, candidate_only=False)  # type: ignore[call-overload]


def test_alternative_search_cannot_express_global_no_alternatives():
    assert {member.value for member in AlternativePredecessorSearch} == {
        "ALTERNATIVES_RECORDED", "ALTERNATIVES_NOT_SEARCHED", "BOUNDED_SEARCH_NONE_FOUND"
    }
    with pytest.raises(ValueError):
        _obligation(known_alternative_predecessor_families=())
    with pytest.raises(ValueError):
        _obligation(
            alternative_search=AlternativePredecessorSearch.BOUNDED_SEARCH_NONE_FOUND,
            known_alternative_predecessor_families=(),
            alternative_search_boundary=(),
        )
    survivor = _obligation(
        alternative_search=AlternativePredecessorSearch.BOUNDED_SEARCH_NONE_FOUND,
        known_alternative_predecessor_families=(),
        alternative_search_boundary=("formula-and-trace-only",),
    )
    assert not survivor.establishes_necessity


def test_verified_implication_requires_checker_and_still_is_not_necessity():
    with pytest.raises(ValueError):
        _obligation(implication_status=ImplicationStatus.IMPLICATION_VERIFIED, implication_checker="")
    verified = _obligation(implication_status=ImplicationStatus.IMPLICATION_VERIFIED, implication_checker="checker")
    assert not verified.establishes_necessity


def test_expand_backward_rejects_necessity_claim_and_preserves_negative_history():
    expansion = expand_backward(
        target_id="root",
        root_goal_id="root",
        generator_id="generator",
        proposals=(
            BackwardObligationProposal(
                "ok", "sufficient predecessor", ("positivity",), "INVARIANT", "norm", "scope",
                ImplicationStatus.CANDIDATE_UNVERIFIED, AlternativePredecessorSearch.ALTERNATIVES_NOT_SEARCHED,
            ),
            BackwardObligationProposal(
                "bad", "only possible route", ("positivity",), "INVARIANT", "norm", "scope",
                ImplicationStatus.CANDIDATE_UNVERIFIED, AlternativePredecessorSearch.ALTERNATIVES_NOT_SEARCHED,
                claims_necessity=True,
            ),
        ),
    )
    assert tuple(item.obligation_id for item in expansion.obligations) == ("ok",)
    assert tuple(item.proposal_id for item in expansion.rejected) == ("bad",)
    assert BackwardSeedFailureMode.BACKWARD_SUFFICIENCY_AS_NECESSITY in expansion.rejected[0].failure_modes
    assert not expansion.grants_necessity_authority


def test_seed_families_are_closed_and_seed_is_never_evidence_or_progress():
    assert len(SeedFamily) == 13
    seed = _seed("s", SeedFamily.CANDIDATE_LEMMA)
    assert seed.candidate_only and not seed.is_evidence and not seed.grants_root_progress
    with pytest.raises(ValueError):
        dataclasses.replace(seed, falsifier_or_cheapest_connection_test="")


def test_seed_family_collapse_is_diagnostic_not_progress():
    collapsed = assess_seed_diversity(_seed(f"s{i}", SeedFamily.CANDIDATE_LEMMA) for i in range(20))
    assert collapsed.collapsed and collapsed.total_seeds == 20
    assert any("SEED_FAMILY_COLLAPSE" in reason for reason in collapsed.reasons)
    assert not collapsed.grants_progress_credit
    spread = assess_seed_diversity((_seed("a", SeedFamily.CANDIDATE_LEMMA), _seed("b", SeedFamily.NORMAL_FORM), _seed("c", SeedFamily.REDUCTION_TARGET)))
    assert not spread.collapsed


def test_unchecked_transition_is_candidate_bridge_but_checked_transition_is_road():
    source, target = _nodes()
    weak = evaluate_connection(ConnectionTrial("weak", source, target, True, transition=_transition()))
    assert weak.verdict is ConnectionVerdict.CANDIDATE_BRIDGE
    assert not weak.is_road
    assert BackwardSeedFailureMode.UNVERIFIED_CONNECTION_AS_ROAD in weak.failure_modes
    checked = evaluate_connection(ConnectionTrial("checked", source, target, True, transition=_transition(checked=True)))
    assert checked.verdict is ConnectionVerdict.VERIFIED_TRANSITION
    assert checked.is_road
    assert not checked.grants_route_authority


def test_unmet_preconditions_or_distinguishing_probe_refute_connection():
    source, target = _nodes()
    unmet = evaluate_connection(ConnectionTrial("unmet", source, target, True, transition=_transition(checked=True, applicable=False)))
    assert unmet.verdict is ConnectionVerdict.REFUTED and unmet.is_negative_history
    refuted = evaluate_connection(ConnectionTrial(
        "probe", source, target, True,
        refutation=DistinguishingProbeCertificate("p", source.node_id, target.node_id, "sign flips", "exact", ("regime",), ("evidence",)),
    ))
    assert refuted.verdict is ConnectionVerdict.REFUTED
    assert "refutation_retained_as_negative_history" in refuted.reasons


def test_similarity_is_analogy_only_and_blocked_dependency_is_not_refutation():
    source, target = _nodes()
    analogy = evaluate_connection(ConnectionTrial("analogy", source, target, True, witness=_witness()))
    assert analogy.verdict is ConnectionVerdict.ANALOGY_ONLY and not analogy.is_road
    blocked = evaluate_connection(ConnectionTrial("blocked", source, target, True, blocked_dependency="formal library"))
    assert blocked.verdict is ConnectionVerdict.BLOCKED and blocked.is_negative_history


def test_unknown_or_posthoc_chronology_cannot_check():
    source, target = _nodes()
    assert evaluate_connection(ConnectionTrial("unknown", source, target, None, transition=_transition(checked=True))).verdict is ConnectionVerdict.CANNOT_CHECK
    assert evaluate_connection(ConnectionTrial("posthoc", source, target, False, transition=_transition(checked=True))).verdict is ConnectionVerdict.CANNOT_CHECK
    assert evaluate_connection(ConnectionTrial("empty", source, target, True)).verdict is ConnectionVerdict.CANNOT_CHECK


def test_connection_history_retains_and_counts_repeated_failures():
    source, target = _nodes()
    first = evaluate_connection(ConnectionTrial("a", source, target, True, transition=_transition(checked=True, applicable=False)))
    second = dataclasses.replace(first, trial_id="b")
    history = ConnectionHistory().record(first).record(second)
    assert history.is_known_failure(source.node_id, target.node_id)
    assert history.repeated_known_failure_count() == 1
    assert history.failed_bridge_ids == ("a", "b")


def _road(trial_id: str, source_id: str, target_id: str):
    source, target = _nodes(source_id, target_id)
    return evaluate_connection(ConnectionTrial(trial_id, source, target, True, transition=_transition(checked=True)))


def test_meet_in_middle_requires_every_link_verified_and_never_grants_solution_authority():
    verified = _road("l1", "forward", "mid")
    mid = ConnectionNode("mid", ConnectionNodeKind.WAYPOINT_SEED, "norm", ("positivity",))
    target = ConnectionNode("obligation", ConnectionNodeKind.BACKWARD_OBLIGATION, "norm", ("positivity",), frozenset({"candidate_invariant"}))
    weak = evaluate_connection(ConnectionTrial("l2", mid, target, True, transition=_transition()))
    candidate = assess_meet_in_middle((verified, weak), forward_frontier_ids=("forward",), backward_obligation_ids=("obligation",))
    assert candidate.verdict is MeetInMiddleVerdict.CANDIDATE_GLUE_UNVERIFIED
    assert BackwardSeedFailureMode.MEET_IN_MIDDLE_FALSE_GLUE in candidate.failure_modes
    assert not candidate.grants_solution_authority
    strong = assess_meet_in_middle((_road("l1", "forward", "mid"), _road("l2", "mid", "obligation")), forward_frontier_ids=("forward",), backward_obligation_ids=("obligation",))
    assert strong.verdict is MeetInMiddleVerdict.VERIFIED_GLUE
    assert not strong.grants_solution_authority


def test_bridge_residual_opens_only_the_cut_and_requires_discriminator():
    expansion = expand_backward(
        target_id="root", root_goal_id="root", generator_id="generator",
        proposals=(BackwardObligationProposal(
            "p1", "predecessor", ("sign_transport",), "INVARIANT", "norm", "scope",
            ImplicationStatus.CANDIDATE_UNVERIFIED, AlternativePredecessorSearch.ALTERNATIVES_NOT_SEARCHED,
        ),),
    )
    with pytest.raises(ValueError):
        compute_bridge_residual(
            residual_id="r", root_goal_id="root", forward_frontier_signature=("positivity",),
            expansion=expansion, history=ConnectionHistory(), cheapest_discriminating_action="",
        )
    residual = compute_bridge_residual(
        residual_id="r", root_goal_id="root", forward_frontier_signature=("positivity",),
        expansion=expansion, history=ConnectionHistory(),
        cheapest_discriminating_action="test sign transport on rank-one boundary",
    )
    assert residual.missing_coordinates == ("sign_transport",)
    assert residual.frontier_overlap == 0.0
    assert residual.opens_atom_only and not residual.grants_root_progress


def test_failure_audit_has_clean_and_hostile_controls():
    diversity = assess_seed_diversity((_seed("s1", SeedFamily.CANDIDATE_LEMMA), _seed("s2", SeedFamily.NORMAL_FORM), _seed("s3", SeedFamily.REDUCTION_TARGET)))
    history = ConnectionHistory().record(_road("road", "forward", "obligation"))
    clean = audit_backward_seed_state(
        diversity=diversity, history=history, connections_cited_as_roads=("road",),
        root_obligations_verified_closed=1, gold_path_exposed=False,
    )
    assert clean.clean and clean.triggered == ()

    collapsed = assess_seed_diversity(_seed(f"c{i}", SeedFamily.CANDIDATE_LEMMA) for i in range(5))
    hostile = audit_backward_seed_state(
        diversity=collapsed, history=ConnectionHistory(), necessity_claims=("obl",),
        connections_cited_as_roads=("fake-road",), root_progress_claimed_from_seed_ids=("c1",),
        root_obligations_verified_closed=0, gold_path_exposed=True,
    )
    assert set(hostile.triggered) == {
        BackwardSeedFailureMode.BACKWARD_SUFFICIENCY_AS_NECESSITY,
        BackwardSeedFailureMode.GOLD_PATH_LEAK,
        BackwardSeedFailureMode.SEED_FAMILY_COLLAPSE,
        BackwardSeedFailureMode.UNVERIFIED_CONNECTION_AS_ROAD,
        BackwardSeedFailureMode.LOCAL_WAYPOINT_AS_ROOT_PROGRESS,
    }
    assert not hostile.grants_scientific_authority


def test_failure_mode_vocabulary_is_frozen():
    assert {member.value for member in BackwardSeedFailureMode} == {
        "BACKWARD_SUFFICIENCY_AS_NECESSITY", "GOLD_PATH_LEAK", "RANDOM_SEED_NOISE",
        "WAYPOINT_INTERESTINGNESS_OVERREACH", "UNVERIFIED_CONNECTION_AS_ROAD",
        "LOCAL_WAYPOINT_AS_ROOT_PROGRESS", "SEED_FAMILY_COLLAPSE",
        "FRONTIER_REPRESENTATION_MISMATCH", "MEET_IN_MIDDLE_FALSE_GLUE",
        "CONNECTION_AUTHORITY_LEAK",
    }
