"""Contract tests for the open-world acquisition successor study.

These pin the *mechanism*, not the outcome. Every assertion here is checked
against a hand-built micro-corpus or against the frozen parameter record; none
of them reads the campaign's result artifact, because a test that asserted a
gate outcome would turn the gate into something the test could be edited to
satisfy.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p2 import acq_campaign, acq_mechanics as mech, acq_world
from orion.study.p2.arb_runtime import (
    derive_current_vocabulary_query,
    derive_lexical_variant_query,
)
from orion.study.p2.corpus import Document

REPO_ROOT = Path(__file__).resolve().parents[3]


# --------------------------------------------------------------------------
# A micro-corpus with the same strata as the constructed world, small enough to
# reason about by hand.
# --------------------------------------------------------------------------


def _document(doc_id: str, title: str, abstract: str, references: tuple[str, ...] = ()) -> Document:
    return Document(
        doc_id=doc_id,
        content_identity=f"work:{doc_id}",
        content_digest=doc_id,
        version=1,
        title=title,
        abstract=abstract,
        venue="venue-01",
        year=2020,
        authors=("author-001",),
        references=references,
        concept_tags=(),
        access_keys=(),
    )


@pytest.fixture(scope="module")
def micro_index() -> mech.AcquisitionIndex:
    documents = [
        # Gold: three content terms, no apparatus word.
        _document("gold-0", "Perovskite Exciton", "perovskite exciton polaron section", ("gold-1",)),
        _document("gold-1", "Exciton Polaron", "exciton polaron perovskite note", ("gold-0",)),
        # Adjacent: two content terms, apparatus repeated.
        _document("near-0", "Perovskite Benchmark", "perovskite perovskite exciton benchmark benchmark benchmark"),
        _document("near-1", "Exciton Benchmark", "exciton exciton polaron benchmark benchmark benchmark"),
        # A bridge between a term and its variant.
        _document("bridge-0", "Polaron Metastability", "polaron metastability metastability"),
        # A record reachable only by the variant vocabulary.
        _document("variant-0", "Metastability Note", "metastability metastability note"),
    ]
    # Enough background that the 5% apparatus gate has a realistic denominator:
    # in a twenty-document index the gate would admit only hapaxes.
    documents += [
        _document(f"filler-{i:02d}", "Filler Record", f"benchmark section note zirconia-{i}")
        for i in range(94)
    ]
    return mech.build_index(documents)


class _Task:
    def __init__(self, question: str) -> None:
        self.task_id = "MICRO-0000"
        self.family = "micro"
        self.question = question


QUESTION = (
    "I am looking for benchmark perovskite exciton that benchmark polaron; in "
    "particular the benchmark benchmark of polaron and exciton for perovskite."
)


# --------------------------------------------------------------------------
# The shipped derivations are untouched.
# --------------------------------------------------------------------------


def test_shipped_derivations_are_used_verbatim() -> None:
    question = "alpha beta alpha gamma delta"
    assert mech.d1_terms(question, 6) == derive_current_vocabulary_query(question, 6).source_terms
    assert mech.d2_terms(question) == derive_lexical_variant_query(question).source_terms


def test_arb_runtime_derivations_still_join_the_way_the_campaign_ran_them() -> None:
    """D1 remains a conjunction and D2 remains free text. This study adds, never edits."""

    derivation = derive_current_vocabulary_query("alpha beta gamma")
    assert " AND " in derivation.query
    assert " AND " not in derive_lexical_variant_query("alpha beta gamma").query


# --------------------------------------------------------------------------
# D5 term selection.
# --------------------------------------------------------------------------


def test_d5_drops_terms_the_index_has_never_seen(micro_index: mech.AcquisitionIndex) -> None:
    terms = mech.d5_terms("perovskite unseenwordxyz exciton", micro_index)
    assert "unseenwordxyz" not in terms
    assert "perovskite" in terms


def test_d5_drops_high_document_frequency_apparatus(micro_index: mech.AcquisitionIndex) -> None:
    assert micro_index.df_fraction("benchmark") > mech.SCAFFOLD_DF_FRACTION
    terms = mech.d5_terms(QUESTION, micro_index)
    assert "benchmark" not in terms
    assert set(terms) <= {"perovskite", "exciton", "polaron"}


def test_d1_keeps_the_apparatus_term_that_d5_drops(micro_index: mech.AcquisitionIndex) -> None:
    """The two selections must genuinely differ on this question, not be relabelled."""

    assert "benchmark" in mech.d1_terms(QUESTION, mech.QUERY_WIDTH)


def test_conjunction_width_refuses_an_unsatisfiable_prefix(
    micro_index: mech.AcquisitionIndex,
) -> None:
    """A prefix whose expected yield falls below the floor is never issued."""

    rare = ("perovskite", "exciton", "polaron")
    width = mech.satisfiable_conjunction_width(rare, micro_index)
    assert mech.MIN_CONJUNCTION_WIDTH <= width <= mech.MAX_CONJUNCTION_WIDTH
    expectation = float(micro_index.size)
    for term in rare[:width]:
        expectation *= micro_index.df_fraction(term)
    assert expectation >= mech.MIN_EXPECTED_CONJUNCTION_HITS or width == mech.MIN_CONJUNCTION_WIDTH


def test_conjunction_width_is_zero_without_groundable_terms(
    micro_index: mech.AcquisitionIndex,
) -> None:
    assert mech.satisfiable_conjunction_width(("nothereatall",), micro_index) == 0


# --------------------------------------------------------------------------
# Provider semantics.
# --------------------------------------------------------------------------


def test_conjunction_requires_every_term(micro_index: mech.AcquisitionIndex) -> None:
    hits = micro_index.search(
        mech.Query("t", mech.QueryKind.CONJUNCTION, terms=("perovskite", "metastability"))
    )
    assert hits == ()


def test_disjunction_admits_any_term(micro_index: mech.AcquisitionIndex) -> None:
    hits = micro_index.search(
        mech.Query("t", mech.QueryKind.DISJUNCTION, terms=("perovskite", "metastability"))
    )
    assert "variant-0" in hits


def test_provider_truncates_at_the_matched_result_cap(
    micro_index: mech.AcquisitionIndex,
) -> None:
    hits = micro_index.search(
        mech.Query("t", mech.QueryKind.DISJUNCTION, terms=("benchmark",)), max_results=3
    )
    assert len(hits) == 3


def test_citation_route_follows_a_held_record(micro_index: mech.AcquisitionIndex) -> None:
    hits = micro_index.search(
        mech.Query("t", mech.QueryKind.CITATION, seed_doc_id="gold-0")
    )
    assert hits == ("gold-1",)


# --------------------------------------------------------------------------
# Merges.
# --------------------------------------------------------------------------


def test_round_robin_gives_every_call_an_equal_share() -> None:
    merged = mech.select_round_robin(4, [("a", "b", "c"), ("x", "y", "z")])
    assert merged == ("a", "x", "b", "y")


def test_coverage_merge_prefers_more_distinct_term_agreement(
    micro_index: mech.AcquisitionIndex,
) -> None:
    """Three distinct matches beat two repeated ones. That is the whole selection claim."""

    merged = mech.select_coverage_first(
        2,
        [("gold-0", "near-0")],
        ("perovskite", "exciton", "polaron"),
        (),
        micro_index,
    )
    assert merged[0] == "gold-0"


def test_coverage_merge_demotes_rather_than_deletes(
    micro_index: mech.AcquisitionIndex,
) -> None:
    """A low-coverage candidate must still be reachable at a large enough cap."""

    merged = mech.select_coverage_first(
        20, [("variant-0", "gold-0")], ("perovskite", "exciton", "polaron"), (), micro_index
    )
    assert set(merged) == {"variant-0", "gold-0"}
    assert merged[0] == "gold-0"


# --------------------------------------------------------------------------
# Expansion.
# --------------------------------------------------------------------------


def test_expansion_finds_bridge_vocabulary(micro_index: mech.AcquisitionIndex) -> None:
    expanded = mech.expansion_terms(("bridge-0",), ("perovskite", "polaron"), micro_index)
    assert "metastability" in expanded


def test_expansion_never_admits_apparatus_vocabulary(
    micro_index: mech.AcquisitionIndex,
) -> None:
    expanded = mech.expansion_terms(
        tuple(f"filler-{i:02d}" for i in range(8)), ("perovskite",), micro_index
    )
    assert "benchmark" not in expanded


def test_expansion_is_empty_without_feedback(micro_index: mech.AcquisitionIndex) -> None:
    assert mech.expansion_terms((), ("perovskite",), micro_index) == ()


def test_d5_falls_back_when_the_apparatus_gate_empties_the_query(
    micro_index: mech.AcquisitionIndex,
) -> None:
    """`D4`'s named untested exposure, handled rather than left open.

    A question whose entire vocabulary sits above the gate must still produce a
    query. It degrades to the grounded terms ranked by idf, never to silence.
    """

    terms = mech.d5_terms("benchmark section note", micro_index)
    assert terms
    assert all(micro_index.document_frequency(term) > 0 for term in terms)


# --------------------------------------------------------------------------
# Arms: budgets, determinism, custody.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("arm", mech.ARM_ORDER)
def test_every_arm_spends_exactly_the_matched_budget(
    arm: str, micro_index: mech.AcquisitionIndex
) -> None:
    run = mech.run_arm(arm, _Task(QUESTION), micro_index)
    assert run.provider_calls == mech.PROVIDER_CALLS_PER_TASK
    assert all(len(group) <= mech.RESULTS_PER_CALL for group in run.per_call_results)
    assert len(run.candidates) <= mech.CANDIDATE_CAP


@pytest.mark.parametrize("arm", mech.ARM_ORDER)
def test_every_arm_is_deterministic(arm: str, micro_index: mech.AcquisitionIndex) -> None:
    first = mech.run_arm(arm, _Task(QUESTION), micro_index)
    second = mech.run_arm(arm, _Task(QUESTION), micro_index)
    assert first.candidates == second.candidates


def test_an_arm_receives_only_the_question(micro_index: mech.AcquisitionIndex) -> None:
    """`run_arm` reads `task.question`, `task.task_id` and `task.family` and nothing else.

    A task object exposing only those three attributes must still work; if an arm
    ever reached for `gold_doc_ids` this would raise.
    """

    run = mech.run_arm(mech.ARM_S2, _Task("perovskite exciton polaron"), micro_index)
    assert run.candidates


def test_scoring_is_applied_outside_the_arm(micro_index: mech.AcquisitionIndex) -> None:
    run = mech.run_arm(mech.ARM_S2, _Task(QUESTION), micro_index)
    score = mech.score_run(run, ("gold-0", "gold-1"))
    assert 0.0 <= score.recall <= 1.0
    assert score.gold == 2


# --------------------------------------------------------------------------
# Statistics.
# --------------------------------------------------------------------------


def test_sign_test_drops_ties_and_is_two_sided() -> None:
    result = mech.sign_test_exact([1.0, 1.0, 0.0], [0.0, 0.0, 0.0])
    assert result["trials"] == 2
    assert result["p_value"] == pytest.approx(0.5)


def test_sign_test_is_vacuous_without_discordant_pairs() -> None:
    assert mech.sign_test_exact([0.0, 0.0], [0.0, 0.0])["p_value"] == 1.0


def test_paired_bootstrap_is_seeded_and_reproducible() -> None:
    left, right = [0.5, 0.4, 0.9], [0.1, 0.0, 0.2]
    first = mech.paired_bootstrap(left, right, resamples=200, seed=7)
    second = mech.paired_bootstrap(left, right, resamples=200, seed=7)
    assert first == second
    assert first["ci_low"] <= first["mean"] <= first["ci_high"]


# --------------------------------------------------------------------------
# World construction.
# --------------------------------------------------------------------------


def test_question_templates_yield_the_intended_query_composition() -> None:
    """D1 must take two apparatus terms and four content terms on the wide template.

    Checked on placeholder tokens rather than on the generated world, so the
    assertion is about the template and not about an outcome.
    """

    question = acq_world.WIDE_QUESTION_TEMPLATE.format(
        s1="SCAF1", s2="SCAF2", c1="CON1", c2="CON2", c3="CON3", c4="CON4", c5="CON5"
    )
    chosen = derive_current_vocabulary_query(question, 6).source_terms
    assert sum(1 for term in chosen if term.startswith("scaf")) == 2
    assert sum(1 for term in chosen if term.startswith("con")) == 4

    well_posed = acq_world.WELL_POSED_QUESTION_TEMPLATE.format(
        c1="CON1", c2="CON2", c3="CON3", c4="CON4", c5="CON5"
    )
    assert all(
        term.startswith("con")
        for term in derive_current_vocabulary_query(well_posed, 6).source_terms
    )


def test_lexicons_are_pairwise_disjoint() -> None:
    scaffold = set(acq_world.SCAFFOLD_LEXICON)
    domain = set(acq_world.DOMAIN_LEXICON)
    variant = set(acq_world.VARIANT_LEXICON)
    neutral = set(acq_world.NEUTRAL_LEXICON)
    assert not (scaffold & domain) and not (scaffold & variant) and not (scaffold & neutral)
    assert not (domain & variant) and not (domain & neutral) and not (variant & neutral)
    assert len(domain) == len(acq_world.DOMAIN_LEXICON)


def test_world_is_deterministic_in_its_seed() -> None:
    first = acq_world.build_acquisition_world(4242)
    second = acq_world.build_acquisition_world(4242)
    assert first.content_hash == second.content_hash


def test_a_different_seed_gives_a_different_world() -> None:
    """The premise a fresh basis rests on. `corpus.build_world` does *not* have it."""

    assert (
        acq_world.build_acquisition_world(4242).content_hash
        != acq_world.build_acquisition_world(4243).content_hash
    )


def test_committed_offline_gold_world_is_seed_invariant_for_retrieval() -> None:
    """The finding that ruled out a fresh seed of the committed world as a new basis.

    `corpus.build_world(seed)` varies venue, year, authors and the noise tags of
    non-gold records. Titles, abstracts of gold records, access keys and topic
    vocabulary are identical for every seed, so a new seed is not a new
    development basis for anything that reads document text.
    """

    from orion.study.p2.corpus import build_world

    left = {item.doc_id: item for item in build_world(20260816).documents}
    right = {item.doc_id: item for item in build_world(11223344).documents}
    assert set(left) == set(right)
    assert all(left[key].title == right[key].title for key in left)
    assert all(left[key].access_keys == right[key].access_keys for key in left)


# --------------------------------------------------------------------------
# Freeze integrity.
# --------------------------------------------------------------------------


def test_runner_parameters_match_the_frozen_twin() -> None:
    twin = json.loads((REPO_ROOT / acq_campaign.FREEZE_TWIN).read_text(encoding="utf-8"))
    assert twin["parameters_sha256"] == acq_campaign.frozen_digest()
    assert twin["status"] == "FROZEN_BEFORE_EXECUTION"


def test_freeze_prose_and_twin_both_exist() -> None:
    assert (REPO_ROOT / acq_campaign.FREEZE_DOCUMENT).exists()
    assert (REPO_ROOT / acq_campaign.FREEZE_TWIN).exists()


def test_inherited_constants_are_not_retuned() -> None:
    """`D5` reuses `D4`'s validated thresholds rather than re-fitting them here."""

    from orion.study.p2 import echo_mechanics

    assert mech.SCAFFOLD_DF_FRACTION == echo_mechanics.INCIDENTAL_DF_FRACTION
    assert mech.TF_SATURATION == echo_mechanics.TF_SATURATION
    assert mech.QUERY_WIDTH == echo_mechanics.QUERY_WIDTH


def test_matched_budgets_equal_the_archived_campaign() -> None:
    assert mech.PROVIDER_CALLS_PER_TASK == 3
    assert mech.RESULTS_PER_CALL == 20
    assert mech.CANDIDATE_CAP == 20
