import pytest

from orion.knowledge.route_family_health import (
    DEFAULT_CONTINUITY_POLICY,
    DEFAULT_NON_COMPENSATORY,
    ChronologyKind,
    ChronologyRecord,
    ContinuityCoordinate,
    ContinuityPolicy,
    ContinuityVerdict,
    ProgrammeHealthVector,
    ProgressKind,
    RootPreservationStatus,
    RouteEpisodeDescriptor,
    RouteFamilyLineage,
    RouteHealthFailureMode,
    RouteHealthState,
    RouteWindowObservation,
    SurrogateImprovement,
    assess_route_family_health,
    classify_surrogate_improvement,
    same_route_family,
)


class _Established:
    def preservation_status(self, *, surrogate_id: str, root_goal_id: str, scope: str) -> RootPreservationStatus:
        del surrogate_id, root_goal_id
        return RootPreservationStatus.PRESERVATION_INTERFACE_ESTABLISHED if scope == "scope" else RootPreservationStatus.PRESERVATION_INTERFACE_ABSENT


def _lineage(episodes: int = 8) -> RouteFamilyLineage:
    ids = tuple(f"ep-{i}" for i in range(episodes))
    return RouteFamilyLineage(
        lineage_id="lineage",
        root_goal_id="root",
        route_family_id="family",
        core_representation_or_mechanism="representation",
        root_bridge_hypothesis="bridge",
        founding_episode_id=ids[0],
        episode_ids_in_chronology=ids,
        continuity_policy_id=DEFAULT_CONTINUITY_POLICY.policy_id,
    )


def _observation(**overrides) -> RouteWindowObservation:
    values = dict(
        lineage_id="lineage",
        window_episode_ids=tuple(f"ep-{i}" for i in range(8)),
        root_obligations_verified_closed=0,
        root_reachable_states_from_verified_root_work=0,
        residual_contraction=0.0,
        discriminating_falsifiers_yielded=0,
        representation_gain=0.0,
        retrieval_gain=0.0,
        verified_local_results=0,
        auxiliary_assumptions_added_after_failure=0,
        exception_classes_added=0,
        route_specific_repair_lemmas=0,
        interfaces_opened=0,
        interfaces_closed=0,
        repeated_failure_redundancy=0.0,
        root_bridge_stability=1.0,
        verification_debt_growth=0.0,
        cost_per_epistemic_gain=1.0,
        exploration_diversity=0.5,
        actions_blocked_externally=0,
        actions_attempted=10,
        named_external_blockers=(),
        search_space_eliminated=0.0,
        stable_obstruction_identified=False,
        forced_productive_representation_reset=False,
        representation_reset_declared=False,
    )
    values.update(overrides)
    return RouteWindowObservation(**values)


def test_route_health_states_are_descriptive_not_truth_verdicts():
    assert {member.value for member in RouteHealthState} == {
        "PROGRESSIVE_SIGNAL", "LOCALLY_PROGRESSIVE_ROOT_STALLED", "STAGNANT_SIGNAL",
        "PATCH_ACCUMULATION_SIGNAL", "RESTRUCTURING_SIGNAL", "EXTERNALLY_BLOCKED",
        "INSUFFICIENT_HISTORY", "CANNOT_CHECK",
    }
    assert len(RouteHealthFailureMode) == 10
    report = assess_route_family_health(_lineage(), _observation())
    assert not report.grants_scientific_authority
    assert not report.grants_abandonment_authority
    assert not report.recommends_abandonment
    assert not report.is_truth_verdict


def test_health_vector_is_structurally_non_compensatory():
    vector = assess_route_family_health(_lineage(), _observation()).vector
    assert vector is not None
    for forbidden in ("score", "total", "aggregate", "sum", "overall"):
        assert not hasattr(vector, forbidden)
    with pytest.raises(TypeError):
        float(vector)
    with pytest.raises(TypeError):
        list(vector)
    assert not vector.shows_movement("root_bridge_stability")
    with pytest.raises(ValueError):
        vector.shows_movement("cost_per_epistemic_gain")


def test_context_only_coordinate_cannot_be_non_compensatory():
    with pytest.raises(ValueError):
        assess_route_family_health(_lineage(), _observation(), non_compensatory_coordinates=("cost_per_epistemic_gain",))


def test_many_local_results_cannot_compensate_for_motionless_root_bridge():
    for local_results in (1, 10, 30, 300):
        report = assess_route_family_health(
            _lineage(),
            _observation(
                verified_local_results=local_results,
                residual_contraction=0.99,
                representation_gain=0.99,
                retrieval_gain=0.99,
                discriminating_falsifiers_yielded=50,
                exploration_diversity=1.0,
                cost_per_epistemic_gain=0.0,
            ),
        )
        assert report.state is RouteHealthState.LOCALLY_PROGRESSIVE_ROOT_STALLED
        assert set(report.stalled_non_compensatory_coordinates) == set(DEFAULT_NON_COMPENSATORY)


def test_all_root_coordinates_must_move_for_progressive_signal():
    partial = assess_route_family_health(
        _lineage(),
        _observation(root_obligations_verified_closed=3, root_reachable_states_from_verified_root_work=2, root_bridge_stability=1.0, verified_local_results=5),
    )
    assert partial.state is RouteHealthState.LOCALLY_PROGRESSIVE_ROOT_STALLED
    assert partial.stalled_non_compensatory_coordinates == ("root_bridge_stability",)

    progressive = assess_route_family_health(
        _lineage(),
        _observation(
            root_obligations_verified_closed=2,
            root_reachable_states_from_verified_root_work=3,
            root_bridge_stability=0.4,
            residual_contraction=0.5,
            verified_local_results=4,
            chronology_records=(ChronologyRecord("pred", "ep-2", ChronologyKind.PROSPECTIVE_DISCRIMINATOR, True, True),),
        ),
    )
    assert progressive.state is RouteHealthState.PROGRESSIVE_SIGNAL


def test_failures_that_eliminate_space_are_information_not_stagnation():
    informative = assess_route_family_health(
        _lineage(),
        _observation(search_space_eliminated=0.75, stable_obstruction_identified=True, discriminating_falsifiers_yielded=6),
    )
    assert informative.state is RouteHealthState.LOCALLY_PROGRESSIVE_ROOT_STALLED
    stagnant = assess_route_family_health(_lineage(), _observation(repeated_failure_redundancy=0.9))
    assert stagnant.state is RouteHealthState.STAGNANT_SIGNAL
    assert not stagnant.recommends_abandonment


def test_external_blocker_preempts_stagnation():
    report = assess_route_family_health(
        _lineage(),
        _observation(actions_blocked_externally=8, named_external_blockers=("missing dependency",)),
    )
    assert report.state is RouteHealthState.EXTERNALLY_BLOCKED


def test_patch_accumulation_requires_posthoc_repair_without_new_information():
    report = assess_route_family_health(
        _lineage(),
        _observation(
            auxiliary_assumptions_added_after_failure=4,
            exception_classes_added=3,
            interfaces_opened=5,
            interfaces_closed=1,
            chronology_records=(ChronologyRecord("repair", "ep-3", ChronologyKind.POSTHOC_REPAIR, False),),
        ),
    )
    assert report.state is RouteHealthState.PATCH_ACCUMULATION_SIGNAL


def test_representation_reset_and_short_history_are_not_stagnation():
    assert assess_route_family_health(_lineage(), _observation(representation_reset_declared=True)).state is RouteHealthState.RESTRUCTURING_SIGNAL
    assert assess_route_family_health(_lineage(), _observation(window_episode_ids=("ep-0", "ep-1"))).state is RouteHealthState.INSUFFICIENT_HISTORY


def test_surrogate_gain_is_local_without_preservation_interface():
    improvement = SurrogateImprovement("imp", "surrogate", "root", "scope")
    assert classify_surrogate_improvement(improvement, None).kind is ProgressKind.LOCAL_PROGRESS
    report = assess_route_family_health(_lineage(), _observation(surrogate_improvements=(improvement,) * 30))
    assert report.state is not RouteHealthState.PROGRESSIVE_SIGNAL
    assert report.vector is not None
    assert report.vector.value("new_root_reachable_states") == 0.0
    assert report.vector.value("new_verified_local_results") == 30.0


def test_surrogate_gain_counts_as_root_only_behind_established_interface():
    improvement = SurrogateImprovement("imp", "surrogate", "root", "scope")
    report = assess_route_family_health(
        _lineage(),
        _observation(surrogate_improvements=(improvement,), root_obligations_verified_closed=1, root_bridge_stability=0.5),
        root_preservation_interface=_Established(),
    )
    assert report.state is RouteHealthState.PROGRESSIVE_SIGNAL


def test_route_continuity_requires_mechanism_and_bridge_not_root_name_alone():
    with pytest.raises(ValueError):
        ContinuityPolicy("bad", (ContinuityCoordinate.ROOT_GOAL_ID,))
    left = RouteEpisodeDescriptor("a", "root", "rep", "bridge")
    same = RouteEpisodeDescriptor("b", "root", "rep", "bridge")
    changed = RouteEpisodeDescriptor("c", "root", "rep-2", "bridge")
    unknown = RouteEpisodeDescriptor("d", "root", "", "bridge")
    assert same_route_family(left, same).verdict is ContinuityVerdict.SAME_ROUTE_FAMILY
    assert same_route_family(left, changed).verdict is ContinuityVerdict.DIFFERENT_ROUTE_FAMILY
    assert same_route_family(left, unknown).verdict is ContinuityVerdict.CANNOT_CHECK


def test_vector_rejects_partial_coordinate_sets():
    with pytest.raises(ValueError):
        ProgrammeHealthVector((("root_critical_obligations_closed", 1.0),), ("root_critical_obligations_closed",), ())
