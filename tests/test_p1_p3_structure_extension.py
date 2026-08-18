from dataclasses import replace

import pytest

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p1_method_realization import (
    PairDecision,
    RealizationState,
    assess_substitutability,
    build_method_realization,
    completeness_errors,
    from_mapping,
    material_differences,
)
from orion.transfer.v2.p3_method_projection import (
    AlignmentState,
    align_projections,
    build_projection,
    obstruction_certificate,
)


def d(name: str) -> str:
    return content_digest({"source": name})


def method(name="bisect", **kw):
    values = dict(
        method_id=name,
        source_digest=d(name),
        source_version="fixture-v1",
        target_role="bounded_monotone_localization",
        preconditions=("ordered_domain", "bracketed_target", "monotone_response"),
        assumptions=("deterministic_response",),
        resources=("oracle",),
        representation_in="ordered_interval",
        representation_out="shrinking_interval",
        mechanics=("measure_midpoint", "discard_inconsistent_half"),
        dependencies=(("measure_midpoint", "discard_inconsistent_half"),),
        invariants=("target_remains_bracketed",),
        progress_measure="interval_width_decreases",
        effects=("shrink_candidate_interval",),
        terminal_condition="interval_width_below_tolerance",
        reconstruction_map="return_interval_representative",
        failure_modes=("non_monotone_response", "target_not_bracketed"),
        lineage=(f"donor:{name}",),
        authority_boundary="REPRESENTATION_ONLY",
        unknown_coordinates=(),
    )
    values.update(kw)
    return build_method_realization(**values)


def projection(realization, name=None, **kw):
    return build_projection(
        realization,
        projection_id=f"proj:{name or realization.method_id}",
        source_id=f"source:{name or realization.method_id}",
        source_span_digests=(d(f"span:{name or realization.method_id}"),),
        initial_obstruction=("direct_search_expensive",),
        author_rationale=("reduce uncertainty by preserving a bracket",),
        **kw,
    )


def test_valid_round_trip_and_complete_no_alarm():
    original = method()
    rebuilt = from_mapping(original.unsigned())
    assert rebuilt.unsigned() == original.unsigned()
    assert rebuilt.digest == original.digest
    assert rebuilt.state is RealizationState.COMPLETE
    assert completeness_errors(rebuilt) == ()


def test_unknown_is_explicit_not_fabricated():
    partial = method(reconstruction_map=None, unknown_coordinates=("reconstruction_map",))
    assert partial.state is RealizationState.PARTIAL
    assert "UNKNOWN:reconstruction_map" in completeness_errors(partial)


def test_dependency_corruption_detected_even_when_transcript_unchanged():
    corrupted = method(dependencies=(("discard_inconsistent_half", "measure_midpoint"),))
    assert "dependencies" in material_differences(method(), corrupted)


def test_invariant_and_reconstruction_corruptions_change_material_structure():
    base = method()
    no_invariant = method(invariants=("response_is_finite",))
    wrong_reconstruction = method(reconstruction_map="return_raw_midpoint_without_mapping")
    assert "invariants" in material_differences(base, no_invariant)
    assert "reconstruction_map" in material_differences(base, wrong_reconstruction)


def test_precondition_swap_and_failure_collapse_are_detected():
    base = method()
    swapped = method(preconditions=("unordered_domain",))
    collapsed = method(failure_modes=("FAIL",))
    assert "preconditions" in material_differences(base, swapped)
    assert "failure_modes" in material_differences(base, collapsed)


def test_lineage_deletion_and_authority_widening_are_detected():
    base = method()
    no_lineage = method(lineage=())
    widened = method(authority_boundary="ADOPTION_ALLOWED")
    assert "lineage" in material_differences(base, no_lineage)
    assert "authority_boundary" in material_differences(base, widened)
    assert any(x.startswith("MISSING:lineage") for x in completeness_errors(no_lineage))
    assert "INVALID:authority_boundary" in completeness_errors(widened)


def test_digest_tamper_fails_closed():
    base = method()
    with pytest.raises(ValueError, match="digest mismatch"):
        replace(base, effects=("different",)).verify()


def test_claim_relative_substitution_and_unresolved():
    base = method()
    renamed = method(
        name="threshold_calibration",
        source_digest=d("threshold_calibration"),
        mechanics=("sample_candidate", "discard_inconsistent_region"),
        dependencies=(("sample_candidate", "discard_inconsistent_region"),),
        lineage=("donor:threshold_calibration",),
    )
    required = ("preconditions", "invariants", "effects", "terminal_condition", "reconstruction_map")
    assert assess_substitutability(base, renamed, required_coordinates=required) is PairDecision.SUBSTITUTABLE_FOR_CLAIM
    bad = method(name="bad", preconditions=("ordered_domain",), lineage=("donor:bad",))
    assert assess_substitutability(base, bad, required_coordinates=required) is PairDecision.NOT_SUBSTITUTABLE
    unknown = method(name="unknown", reconstruction_map=None, unknown_coordinates=("reconstruction_map",), lineage=("donor:unknown",))
    assert assess_substitutability(base, unknown, required_coordinates=required) is PairDecision.UNRESOLVED


def test_p3_different_terms_same_source_local_structure_can_align_without_claiming_fibre():
    left = projection(method())
    right = projection(method(
        name="threshold_calibration",
        mechanics=("sample_candidate", "discard_inconsistent_region"),
        dependencies=(("sample_candidate", "discard_inconsistent_region"),),
        lineage=("donor:threshold",),
    ))
    result = align_projections(
        left, right, alignment_id="a", purpose="bounded monotone localization",
        required_coordinates=("preconditions", "invariants", "progress", "termination", "reconstruction"),
    )
    assert result.state is AlignmentState.ALIGNED
    assert result.unsigned()["can_claim_method_fibre"] is False


def test_p3_same_topology_incompatible_assumption_yields_obstruction():
    left = projection(method())
    right = projection(method(name="nonmonotone", preconditions=("ordered_domain", "bracketed_target"), lineage=("donor:nonmonotone",)))
    result = align_projections(left, right, alignment_id="b", purpose="bounded monotone localization", required_coordinates=("preconditions", "invariants"))
    assert result.state is AlignmentState.OBSTRUCTION
    cert = obstruction_certificate(result)
    assert "preconditions" in cert["obstructed_coordinates"]


def test_p3_same_result_different_reconstruction_yields_obstruction():
    left = projection(method())
    right = projection(method(name="raw", reconstruction_map="return_transformed_coordinate", lineage=("donor:raw",)))
    result = align_projections(left, right, alignment_id="c", purpose="solve original target", required_coordinates=("reconstruction",))
    assert result.state is AlignmentState.OBSTRUCTION


def test_p3_missing_rationale_stays_source_local_unknown_not_inferred_fact():
    partial = method(name="partial", unknown_coordinates=("progress_measure",), lineage=("donor:partial",))
    p = build_projection(
        partial, projection_id="p", source_id="source:p", source_span_digests=(d("span:p"),),
        author_rationale=(), unknown_coordinates=("progress",),
    )
    other = projection(method())
    result = align_projections(p, other, alignment_id="u", purpose="progress semantics", required_coordinates=("progress",))
    assert result.state is AlignmentState.UNRESOLVED


def test_projection_requires_source_span_and_preserves_source_identity():
    with pytest.raises(ValueError, match="source span"):
        build_projection(method(), projection_id="x", source_id="s", source_span_digests=())
    p = projection(method())
    assert p.source_digest == method().source_digest
    assert p.realization_digest == method().digest
