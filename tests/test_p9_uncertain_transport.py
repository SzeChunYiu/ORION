from dataclasses import replace

from orion.study.p9.uncertain_transport import (
    AffineEstimate,
    AffineObservation,
    CandidateProbe,
    HiddenAffineMap,
    LocalTransformCase,
    ObservedAffineTransform,
    TransformCycleCase,
    TransformResponsibility,
    classify_transform_responsibility,
    infer_exact_affine,
    minimal_identifying_probe_ids,
    resolve_visible_cycle,
)
from orion.study.p9.structural_world import GluingVerdict


def _edge(
    *,
    transform_id: str = "edge-a",
    observations: tuple[AffineObservation, ...],
    probes: tuple[CandidateProbe, ...] = (),
    historical: AffineEstimate | None = None,
) -> ObservedAffineTransform:
    return ObservedAffineTransform(
        transform_id=transform_id,
        source_chart_id="chart-a",
        target_chart_id="chart-b",
        observations=observations,
        candidate_probes=probes,
        historical_estimate=historical,
    )


def test_two_distinct_exact_observations_point_identify_affine_map():
    observations = (AffineObservation(0.0, 2.0), AffineObservation(3.0, 8.0))
    estimate = infer_exact_affine(observations)

    assert estimate == AffineEstimate(scale=2.0, offset=2.0)
    assert classify_transform_responsibility(_edge(observations=observations)) is (
        TransformResponsibility.IDENTIFIABLE_NOW
    )


def test_repeated_x_is_nonidentifying_but_distinct_probe_creates_measurement_route():
    observations = (AffineObservation(1.0, 5.0), AffineObservation(1.0, 5.0))
    edge = _edge(
        observations=observations,
        probes=(
            CandidateProbe("same-x", x=1.0, cost=0.1),
            CandidateProbe("distinct-x", x=3.0, cost=0.7),
        ),
    )

    assert infer_exact_affine(observations) is None
    assert classify_transform_responsibility(edge) is TransformResponsibility.NEEDS_MORE_MEASUREMENTS
    assert minimal_identifying_probe_ids(edge) == ("distinct-x",)


def test_no_available_distinct_x_probe_is_explicitly_nonidentifiable():
    edge = _edge(
        observations=(AffineObservation(1.0, 5.0),),
        probes=(CandidateProbe("same-a", x=1.0, cost=0.1), CandidateProbe("same-b", x=1.0, cost=0.2)),
    )

    assert classify_transform_responsibility(edge) is (
        TransformResponsibility.NONIDENTIFIABLE_UNDER_AVAILABLE_PROBES
    )
    assert minimal_identifying_probe_ids(edge) == ()


def test_zero_observations_requires_two_distinct_probe_inputs():
    edge = _edge(
        observations=(),
        probes=(
            CandidateProbe("p0", x=0.0, cost=0.9),
            CandidateProbe("p1", x=1.0, cost=0.4),
            CandidateProbe("p2", x=2.0, cost=0.4),
        ),
    )

    assert classify_transform_responsibility(edge) is TransformResponsibility.NEEDS_MORE_MEASUREMENTS
    # Minimum cost wins; lexical ids break the equal-cost tie only after total cost.
    assert minimal_identifying_probe_ids(edge) == ("p1", "p2")


def test_historical_estimate_is_usable_until_visible_observation_contradicts_it():
    estimate = AffineEstimate(scale=2.0, offset=1.0)
    compatible = _edge(
        observations=(AffineObservation(4.0, 9.0),),
        historical=estimate,
    )
    changed = replace(
        compatible,
        transform_id="edge-changed",
        observations=(AffineObservation(4.0, 10.0),),
    )

    assert classify_transform_responsibility(compatible) is TransformResponsibility.IDENTIFIABLE_NOW
    assert classify_transform_responsibility(changed) is TransformResponsibility.CHANGED_SINCE_ESTIMATE


def test_observation_and_probe_order_do_not_change_responsibility_or_minimal_probe():
    edge = _edge(
        observations=(AffineObservation(1.0, 5.0), AffineObservation(1.0, 5.0)),
        probes=(CandidateProbe("expensive", x=4.0, cost=2.0), CandidateProbe("cheap", x=2.0, cost=0.5)),
    )
    permuted = replace(
        edge,
        observations=tuple(reversed(edge.observations)),
        candidate_probes=tuple(reversed(edge.candidate_probes)),
    )

    assert classify_transform_responsibility(edge) == classify_transform_responsibility(permuted)
    assert minimal_identifying_probe_ids(edge) == minimal_identifying_probe_ids(permuted) == ("cheap",)
    assert edge.candidate_fingerprint() == permuted.candidate_fingerprint()


def test_evaluator_truth_and_gold_never_change_candidate_fingerprint():
    observed = _edge(
        observations=(AffineObservation(1.0, 5.0),),
        probes=(CandidateProbe("p", x=2.0, cost=1.0),),
    )
    left = LocalTransformCase(
        case_id="case-left",
        observed=observed,
        truth=HiddenAffineMap(scale=2.0, offset=3.0),
        gold_responsibility=TransformResponsibility.NEEDS_MORE_MEASUREMENTS,
    )
    right = replace(
        left,
        case_id="case-right",
        truth=HiddenAffineMap(scale=-3.0, offset=8.0),
        gold_responsibility=TransformResponsibility.NONIDENTIFIABLE_UNDER_AVAILABLE_PROBES,
    )

    assert left.candidate_fingerprint() == right.candidate_fingerprint()
    payload_text = repr(left.candidate_payload())
    assert "gold" not in payload_text.lower()
    assert "truth" not in payload_text.lower()
    assert "case-left" not in payload_text


def test_reminting_opaque_ids_changes_fingerprint_but_not_semantic_decision():
    original = _edge(
        observations=(AffineObservation(0.0, 1.0), AffineObservation(2.0, 5.0)),
    )
    reminted = replace(
        original,
        transform_id="x-9348",
        source_chart_id="q-112",
        target_chart_id="q-991",
    )

    assert original.candidate_fingerprint() != reminted.candidate_fingerprint()
    assert classify_transform_responsibility(original) == classify_transform_responsibility(reminted)
    assert infer_exact_affine(original.observations) == infer_exact_affine(reminted.observations)


def _identified_edge(
    transform_id: str,
    source: str,
    target: str,
    scale: float,
    offset: float,
) -> ObservedAffineTransform:
    return ObservedAffineTransform(
        transform_id=transform_id,
        source_chart_id=source,
        target_chart_id=target,
        observations=(
            AffineObservation(0.0, offset),
            AffineObservation(1.0, scale + offset),
        ),
    )


def test_fully_identified_cycle_reuses_existing_exact_gluing_algebra():
    glue = TransformCycleCase(
        cycle_id="cycle-glue",
        edges=(
            _identified_edge("ab", "a", "b", 2.0, 1.0),
            _identified_edge("bc", "b", "c", 0.5, -0.5),
            _identified_edge("ca", "c", "a", 1.0, 0.0),
        ),
        hidden_truth=(),
        gold_if_fully_known=GluingVerdict.GLUE,
    )
    obstruction = replace(
        glue,
        cycle_id="cycle-obstruction",
        edges=glue.edges[:-1] + (_identified_edge("ca", "c", "a", 1.0, 1.0),),
        gold_if_fully_known=GluingVerdict.OBSTRUCTION,
    )

    assert resolve_visible_cycle(glue) is GluingVerdict.GLUE
    assert resolve_visible_cycle(obstruction) is GluingVerdict.OBSTRUCTION


def test_one_unresolved_edge_forces_global_unknown():
    unresolved = ObservedAffineTransform(
        transform_id="ca",
        source_chart_id="c",
        target_chart_id="a",
        observations=(AffineObservation(0.0, 0.0),),
        candidate_probes=(),
    )
    cycle = TransformCycleCase(
        cycle_id="cycle-unresolved",
        edges=(
            _identified_edge("ab", "a", "b", 2.0, 1.0),
            _identified_edge("bc", "b", "c", 0.5, -0.5),
            unresolved,
        ),
        hidden_truth=(HiddenAffineMap(2.0, 1.0), HiddenAffineMap(0.5, -0.5), HiddenAffineMap(1.0, 0.0)),
        gold_if_fully_known=GluingVerdict.GLUE,
    )

    assert resolve_visible_cycle(cycle) is GluingVerdict.UNKNOWN


def test_same_unresolved_candidate_cycle_can_hide_opposite_fully_known_truths():
    unresolved = ObservedAffineTransform(
        transform_id="ca",
        source_chart_id="c",
        target_chart_id="a",
        observations=(AffineObservation(0.0, 0.0),),
        candidate_probes=(),
    )
    visible_edges = (
        _identified_edge("ab", "a", "b", 2.0, 1.0),
        _identified_edge("bc", "b", "c", 0.5, -0.5),
        unresolved,
    )
    glue = TransformCycleCase(
        cycle_id="hidden-glue",
        edges=visible_edges,
        hidden_truth=(HiddenAffineMap(2.0, 1.0), HiddenAffineMap(0.5, -0.5), HiddenAffineMap(1.0, 0.0)),
        gold_if_fully_known=GluingVerdict.GLUE,
    )
    obstruct = replace(
        glue,
        cycle_id="hidden-obstruct",
        hidden_truth=(HiddenAffineMap(2.0, 1.0), HiddenAffineMap(0.5, -0.5), HiddenAffineMap(-1.0, 0.0)),
        gold_if_fully_known=GluingVerdict.OBSTRUCTION,
    )

    assert glue.candidate_fingerprint() == obstruct.candidate_fingerprint()
    assert resolve_visible_cycle(glue) is GluingVerdict.UNKNOWN
    assert resolve_visible_cycle(obstruct) is GluingVerdict.UNKNOWN
