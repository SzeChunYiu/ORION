"""A novelty claim must show its donor search, or fail closed.

Regression for the ORION-QG QG-19 finding: six novelty claims frozen without
literature access were attacked, and none survived -- two SUBSUMED, three
INSTANCE_OF_KNOWN_GENERAL, one NEAREST_MISS. The headline structural criterion
was Wolf's 1978 syndrome trellis. One mechanism, six instances, closable in code.
"""

import pytest

from orion_research_harness.donor_search import (
    CANNOT_ASSESS,
    INSTANCE_OF_KNOWN_GENERAL,
    NEAREST_MISS,
    NO_PRIOR_ART_FOUND,
    QUERY_FAMILIES,
    SUBSUMED,
    SUBSUMED_IN_SPECIAL_CASE,
    describe,
    validate_donor_search,
)

ALL_FAMILIES = list(QUERY_FAMILIES)


def _claim(**overrides):
    record = {
        "asserts_novelty": True,
        "verdict": NEAREST_MISS,
        "query_families": list(ALL_FAMILIES),
        "verbatim_passage": "extracting an optimal term can be efficiently done",
    }
    record.update(overrides)
    return record


def test_a_novelty_claim_with_no_search_at_all_is_refused():
    with pytest.raises(ValueError, match="verdict must be one of"):
        validate_donor_search({"asserts_novelty": True})


def test_a_claim_that_does_not_assert_novelty_needs_nothing():
    validate_donor_search({"asserts_novelty": False})
    validate_donor_search({})


@pytest.mark.parametrize("dropped", ALL_FAMILIES)
def test_every_query_family_is_mandatory(dropped):
    families = [f for f in ALL_FAMILIES if f != dropped]
    with pytest.raises(ValueError, match="missing query families"):
        validate_donor_search(_claim(query_families=families))


@pytest.mark.parametrize(
    "verdict",
    [SUBSUMED, SUBSUMED_IN_SPECIAL_CASE, INSTANCE_OF_KNOWN_GENERAL, NEAREST_MISS],
)
def test_a_verdict_against_a_source_must_quote_it(verdict):
    with pytest.raises(ValueError, match="verbatim_passage"):
        validate_donor_search(_claim(verdict=verdict, verbatim_passage="   "))
    validate_donor_search(_claim(verdict=verdict, verbatim_passage="a real quote"))


def test_no_prior_art_found_is_not_a_novelty_grant_without_its_log():
    with pytest.raises(ValueError, match="query_log_ref"):
        validate_donor_search(_claim(verdict=NO_PRIOR_ART_FOUND, verbatim_passage=""))
    validate_donor_search(
        _claim(
            verdict=NO_PRIOR_ART_FOUND,
            verbatim_passage="",
            query_log_ref="QG19_QUERY_LOG.md",
        )
    )


def test_cannot_assess_needs_no_passage_because_nothing_was_read():
    validate_donor_search(_claim(verdict=CANNOT_ASSESS, verbatim_passage=""))


def test_query_families_must_be_a_sequence_not_a_string():
    with pytest.raises(ValueError, match="must be a sequence"):
        validate_donor_search(_claim(query_families="OWN_VOCABULARY"))


def test_the_qg19_verdicts_replay_through_the_gate():
    """The six real QG-19 outcomes must all validate as recorded."""
    for verdict in (
        SUBSUMED,
        SUBSUMED,
        INSTANCE_OF_KNOWN_GENERAL,
        INSTANCE_OF_KNOWN_GENERAL,
        INSTANCE_OF_KNOWN_GENERAL,
        NEAREST_MISS,
    ):
        validate_donor_search(_claim(verdict=verdict))


def test_no_verdict_describes_itself_as_granting_novelty():
    for verdict in (
        SUBSUMED,
        SUBSUMED_IN_SPECIAL_CASE,
        INSTANCE_OF_KNOWN_GENERAL,
        NEAREST_MISS,
        NO_PRIOR_ART_FOUND,
        CANNOT_ASSESS,
    ):
        text = describe(verdict)
        assert text
        assert "novelty established" not in text
    assert "novelty NOT established" in describe(NO_PRIOR_ART_FOUND)
    with pytest.raises(ValueError):
        describe("LOOKS_NOVEL_TO_ME")
