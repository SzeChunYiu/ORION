import pytest

from orion.knowledge.nearest_work import (
    AbsorptionDecision,
    AbsorptionDisposition,
    ExternalMechanism,
    NearestWorkComparison,
    NoveltyCase,
    NoveltyVerdict,
    WorkRelation,
    assess_novelty_case,
    validate_absorption,
)


def _mechanism(mid="m1"):
    return ExternalMechanism(
        work_id="work:a",
        mechanism_id=mid,
        description="A useful external mechanism.",
        evidence_refs=("arxiv:0000.00000",),
    )


def _comparison(relation=WorkRelation.OVERLAPS, deltas=("delta:1",)):
    return NearestWorkComparison(
        work_id="work:a",
        relation=relation,
        absorbed_mechanism_ids=("m1",),
        residual_delta_ids=deltas,
        note="Compared on the scoped claim.",
    )


def test_absorption_rejects_unknown_or_duplicate_mechanisms():
    mechanisms = (_mechanism(),)
    with pytest.raises(ValueError, match="unknown mechanisms"):
        validate_absorption(
            mechanisms,
            (
                AbsorptionDecision(
                    "missing",
                    AbsorptionDisposition.ADAPT,
                    ("SEARCH.v1",),
                    "Use the mechanism after adaptation.",
                ),
            ),
        )
    with pytest.raises(ValueError, match="at most one"):
        validate_absorption(
            mechanisms,
            (
                AbsorptionDecision("m1", AbsorptionDisposition.ADOPT, ("SEARCH.v1",), "Adopt."),
                AbsorptionDecision("m1", AbsorptionDisposition.DEFER, (), "Defer."),
            ),
        )


def test_novelty_is_blocked_without_nearest_work_or_with_open_routes():
    empty = NoveltyCase("paper-1", "claim", (), ("delta:1",), ("falsifier:1",))
    assert assess_novelty_case(empty).verdict is NoveltyVerdict.BLOCKED_NO_NEAREST_WORK

    open_search = NoveltyCase(
        "paper-1",
        "claim",
        (_comparison(),),
        ("delta:1",),
        ("falsifier:1",),
        ("historical-precursor",),
    )
    assert assess_novelty_case(open_search).verdict is NoveltyVerdict.BLOCKED_SEARCH_OPEN


def test_novelty_requires_a_falsifier_even_when_a_delta_survives():
    case = NoveltyCase("paper-1", "claim", (_comparison(),), ("delta:1",), ())
    assert assess_novelty_case(case).verdict is NoveltyVerdict.BLOCKED_NO_FALSIFIER


def test_subsumed_work_cannot_be_rebranded_as_novelty():
    case = NoveltyCase(
        "paper-1",
        "claim",
        (_comparison(WorkRelation.SUBSUMES_CANDIDATE, ()),),
        (),
        ("falsifier:1",),
    )
    result = assess_novelty_case(case)
    assert result.verdict is NoveltyVerdict.SUBSUMED
    assert not result.publication_novelty_authorized


def test_scoped_difference_is_only_a_candidate_delta():
    case = NoveltyCase(
        "paper-1",
        "claim",
        (_comparison(),),
        ("delta:typed-reopening",),
        ("falsifier:hidden-representation-shift",),
    )
    result = assess_novelty_case(case)
    assert result.verdict is NoveltyVerdict.CANDIDATE_DELTA
    assert result.candidate_delta_ids == ("delta:typed-reopening",)
    assert result.absorbed_mechanism_count == 1
    assert not result.publication_novelty_authorized
