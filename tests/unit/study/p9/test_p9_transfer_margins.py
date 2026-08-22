"""P9's shipped D1 transfer margins, measured against the arms they name.

Every number pinned here was read off the shipped archive
``research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json``
(``result_digest sha256:34003fb8...``) or recomputed from the frozen dataset
builders in :mod:`orion.study.p9.d1`. The digest assertion is the fidelity
anchor: a failure below is about P9, not about a local fixture.
"""

from __future__ import annotations

import contextlib
import io
import json

import pytest

from orion.programme.comparator_response import (
    MarginReason,
    PriorValuedMargin,
    require_responsive_comparator,
)
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import divergence_of
from orion.study.p9 import transfer_margins as p9
from orion.study.p9.transfer_audit import audit_p9_transfer_margins, main, report_as_json


@pytest.fixture(scope="module")
def archive() -> dict:
    return p9.load_shipped_d1_result()


@pytest.fixture(scope="module")
def collapse() -> dict:
    return p9.d1_view_collapse_report()


@pytest.fixture(scope="module")
def oracle():
    return p9.d1_oracle_identity()


def test_the_archive_reproduces_its_committed_digest(archive):
    assert archive["result_digest"] == p9.D1_RESULT_DIGEST
    assert archive["terminal"] == "D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED"
    assert archive["typed_minus_transcript"] == 0.75
    assert archive["typed_minus_same_information_serialized"] == 0.5


def test_both_headline_comparators_answered_the_protected_split_with_one_label(archive):
    responses = p9.d1_arm_responses(archive)

    for arm, emitted, accuracy in (
        ("TRANSCRIPT_BAG", "ALIGNED", 0.25),
        ("TYPED_SERIALIZED_BAG", "OBSTRUCTION", 0.5),
    ):
        response = responses[arm]
        assert response.eval_cases == 128
        assert response.distinct_predictions == 1
        assert response.prediction_counts == ((emitted, 128),)
        assert response.accuracy == accuracy
        # The identity that makes the published margin a statistic of the split.
        assert response.accuracy == response.prior_of_emitted
        assert response.informedness == 0.0
        assert response.departures == 0


def test_the_untyped_arm_is_the_one_comparator_that_responded(archive):
    response = p9.d1_arm_responses(archive)["UNTYPED_PAIR"]

    assert response.distinct_predictions == 3
    assert response.accuracy == 0.90625
    assert response.departures == 76
    assert response.informedness == pytest.approx(0.8958333, abs=1e-6)


def test_the_two_headline_margins_are_one_minus_a_label_prior(archive):
    margins = {item.comparator.arm_id: item for item in p9.d1_contrast_margins(archive)}
    priors = dict(margins["TRANSCRIPT_BAG"].comparator.label_counts)

    assert priors == {"ALIGNED": 32, "OBSTRUCTION": 64, "UNRESOLVED": 32}
    assert margins["TRANSCRIPT_BAG"].published_margin == 1.0 - priors["ALIGNED"] / 128
    assert margins["TYPED_SERIALIZED_BAG"].published_margin == 1.0 - priors["OBSTRUCTION"] / 128


def test_both_headline_margins_block_and_the_untyped_one_does_not(archive):
    margins = {item.comparator.arm_id: item for item in p9.d1_contrast_margins(archive)}

    for arm in ("TRANSCRIPT_BAG", "TYPED_SERIALIZED_BAG"):
        assert margins[arm].outcome is Outcome.CANNOT_CHECK
        assert margins[arm].reason is MarginReason.COMPARATOR_CONSTANT
        assert margins[arm].blocks is True
    assert margins["UNTYPED_PAIR"].outcome is Outcome.PASS
    assert margins["UNTYPED_PAIR"].reason is MarginReason.COMPARATOR_RESPONDED
    assert margins["UNTYPED_PAIR"].published_margin == 0.09375


def test_a_quarter_of_the_transcript_margin_is_supplied_by_the_label_prior(archive):
    margin = next(
        item
        for item in p9.d1_contrast_margins(archive)
        if item.comparator.arm_id == "TRANSCRIPT_BAG"
    )

    assert margin.comparator.trivial_floor == 0.5
    assert margin.earned_margin == 0.5
    assert margin.prior_supplied == 0.25


def test_recomposing_the_protected_split_sweeps_the_published_margins(archive):
    sensitivity = p9.d1_composition_sensitivity(archive)

    for arm in ("TRANSCRIPT_BAG", "TYPED_SERIALIZED_BAG"):
        item = sensitivity[arm]
        assert item.published_margin_low == pytest.approx(0.0588235, abs=1e-6)
        assert item.published_margin_high == pytest.approx(0.9705882, abs=1e-6)
        assert item.informedness_margin_low == 1.0
        assert item.informedness_margin_high == 1.0
        assert item.composition_valued is True
    assert sensitivity["UNTYPED_PAIR"].composition_valued is False


def test_the_transcript_view_presents_one_row_to_every_estimator_in_the_grid():
    collapse = p9.d1_view_collapse()

    transcript = collapse["TRANSCRIPT_BAG"]
    assert transcript["test_keys"] == 515
    assert transcript["test_keys_in_train_vocabulary"] == 3
    assert transcript["distinct_in_vocabulary_test_signatures"] == 1
    # The two arms that responded keep their whole vocabulary across the holdout.
    assert collapse["TYPED_RELATIONAL"]["distinct_in_vocabulary_test_signatures"] == 13
    assert collapse["UNTYPED_PAIR"]["distinct_in_vocabulary_test_signatures"] == 9
    assert collapse["TYPED_SERIALIZED_BAG"]["distinct_in_vocabulary_test_signatures"] == 7


def test_no_model_in_the_frozen_grid_can_give_the_transcript_arm_a_second_answer():
    """The structural claim, executed: one design-matrix row means one prediction."""

    from orion.study.p9 import d1_runtime  # side effect: the official v1.2 estimator
    from orion.study.p9.d1 import generate_d1_dataset
    from orion.study.p9.d1_experiment import D1FeatureFamily, _fit, _predict, model_specs

    assert d1_runtime.run_d1 is not None
    dataset = generate_d1_dataset(seed="p9-d1-method-transfer-v1")
    for spec in model_specs():
        model = _fit(dataset.train, D1FeatureFamily.TRANSCRIPT_BAG, spec)
        predictions = _predict(model, dataset.test, D1FeatureFamily.TRANSCRIPT_BAG)
        assert len(set(predictions)) == 1, spec.config_id


# --------------------------------------------------------------------------
# The protected denominator: why it is one, and that saying so is a measurement
# --------------------------------------------------------------------------


def test_the_transcript_denominator_is_per_instance_minting_not_the_holdout(collapse):
    """The finding, with the control that separates it from a fixable one.

    ``512 of 515 keys are missing`` is the same sentence in two worlds. Refitting
    the vocabulary on a same-size corpus the same generator draws from the
    protected split's own domain restores every key the holdout hid, and none of
    the keys that are minted per instance. Zero restored is the whole finding.
    """

    transcript = collapse["TRANSCRIPT_BAG"]

    assert transcript.test_keys == 515
    assert transcript.test_keys_in_train_vocabulary == 3
    assert transcript.distinct_protected_rows == 1
    # The control ran, on a corpus the same size as the frozen training split.
    assert transcript.in_domain_train_rows == transcript.train_rows == 288
    assert transcript.restored_by_in_domain_refit == 0
    assert transcript.distinct_protected_rows_in_domain == 1
    assert transcript.recoverable_by_refitting is False
    assert transcript.reason is p9.ViewCollapseReason.PER_INSTANCE_KEY_SPACE
    assert transcript.outcome is Outcome.CANNOT_CHECK
    # Why no corpus could have carried them: every fitted key but the three
    # arity counts occurs in exactly one training row.
    assert transcript.train_keys_in_one_train_row == 1152
    assert transcript.train_vocabulary == 1155
    assert transcript.hapax_share == pytest.approx(1152 / 1155)
    # And the second, independent reason the denominator is one.
    assert transcript.constant_surviving_keys == 3
    assert transcript.surviving_keys_all_constant is True


def test_the_in_domain_control_can_restore_keys_when_the_holdout_is_the_cause(collapse):
    """The control's positive case: without it, zero restored means nothing.

    ``TYPED_SERIALIZED_BAG`` loses keys because its value alphabet is scoped to a
    domain, and the same refit hands nineteen of them back and lifts the
    denominator. A control that restored nothing everywhere would be broken
    rather than informative, and this is the test that would notice.
    """

    serialized = collapse["TYPED_SERIALIZED_BAG"]

    assert serialized.test_keys_in_train_vocabulary == 26
    assert serialized.test_keys_in_in_domain_vocabulary == 45
    assert serialized.restored_by_in_domain_refit == 19
    assert serialized.distinct_protected_rows == 7
    assert serialized.distinct_protected_rows_in_domain == 11
    assert serialized.reason is p9.ViewCollapseReason.VIEW_RESPONDED


def test_the_in_domain_control_is_a_different_sample_of_the_protected_domain():
    """Guards the control against becoming the protected split under another name."""

    from orion.study.p9.d1 import generate_d1_dataset

    dataset = generate_d1_dataset(seed=p9.D1_SEED)
    control = p9._in_domain_vocabulary_control(dataset)

    assert {row.domain for row in control} == {row.domain for row in dataset.test}
    assert {row.domain for row in control}.isdisjoint({row.domain for row in dataset.train})
    protected_ids = {row.instance_id for row in dataset.test}
    assert protected_ids.isdisjoint({row.instance_id for row in control})
    assert len(control) == len(dataset.train)


def test_every_view_that_responded_keeps_more_than_one_protected_row(collapse):
    """Fails if any view's protected design matrix collapses to a single row."""

    assert {view: item.distinct_protected_rows for view, item in collapse.items()} == {
        "TRANSCRIPT_BAG": 1,
        "TYPED_RELATIONAL": 13,
        "TYPED_SERIALIZED_BAG": 7,
        "UNTYPED_PAIR": 9,
    }
    blocked = {view for view, item in collapse.items() if item.blocks}
    assert blocked == {"TRANSCRIPT_BAG"}
    for view in ("TYPED_RELATIONAL", "TYPED_SERIALIZED_BAG", "UNTYPED_PAIR"):
        assert collapse[view].outcome is Outcome.PASS
        assert collapse[view].surviving_keys_all_constant is False


# --------------------------------------------------------------------------
# The evaluator branch: an identity, reported as one
# --------------------------------------------------------------------------


def test_the_evaluator_failure_branch_recomputes_the_gold_it_grades():
    """P6's question, answered with P6's instrument rather than a second one."""

    divergence = p9.d1_oracle_divergence()

    assert divergence.points == 512
    assert divergence.points_changed == 0
    assert divergence.applied is False


def test_the_d1_comparator_is_an_identity_and_not_an_agreement(oracle):
    """``0 divergent`` reported as what it is, on three spaces rather than one."""

    assert oracle.frozen_space.points_changed == 0
    assert oracle.protected_space.points == 128
    assert oracle.protected_space.points_changed == 0
    # Agreement on a corpus one generator built is not an identity; agreement on
    # the pairs that generator never builds is what makes it one.
    assert oracle.widened_space.points == 1280
    assert oracle.widened_space.points_changed == 0
    assert oracle.reads_every_compared_coordinate is True
    assert set(oracle.comparator_read_coordinates) == set(oracle.compared_coordinates)
    assert oracle.verdict is p9.OracleVerdict.IDENTITY_BY_CONSTRUCTION
    assert oracle.branch_reachable is False
    # CANNOT_CHECK, not FAIL: nothing could have differed, and it blocks anyway.
    assert oracle.outcome is Outcome.CANNOT_CHECK
    assert oracle.blocks is True


def test_the_widened_space_carries_the_shapes_the_d1_generator_never_builds():
    """Fails if the widening degenerates into more of the frozen corpus."""

    from orion.study.p9.d1 import COMPARISON_COORDINATES, generate_d1_dataset

    frozen = generate_d1_dataset(seed=p9.D1_SEED)
    frozen_rows = (*frozen.train, *frozen.dev, *frozen.test)
    widened = p9._widened_oracle_space()

    def left_unknowns(rows):
        return {tuple(row.left.unknown_coordinates) for row in rows}

    def perturbed_widths(rows):
        return {len(row.mutation_coordinates) for row in rows}

    # The frozen corpus never marks the left method unknown, never marks a
    # coordinate outside the compared set, and never perturbs more than two
    # coordinates at once.
    assert left_unknowns(frozen_rows) == {()}
    assert left_unknowns(widened) - {()}
    assert max(perturbed_widths(frozen_rows)) == 2
    assert max(perturbed_widths(widened)) == len(COMPARISON_COORDINATES)
    outside = {
        coordinate
        for row in widened
        for coordinate in (*row.left.unknown_coordinates, *row.right.unknown_coordinates)
        if coordinate not in COMPARISON_COORDINATES
    }
    assert outside == {"mechanics"}
    # Sequence coordinates emptied outright, which the D1 mutation operator (which
    # only ever appends a token or replaces a scalar) never produces.
    assert any(row.right.invariants == () for row in widened)
    assert all(row.right.invariants != () for row in frozen_rows)


def test_gold_moves_across_the_widened_space(oracle):
    """The widening is only evidence if the reference itself varies over it."""

    assert dict(oracle.widened_gold_labels) == {
        "ALIGNED": 2,
        "OBSTRUCTION": 510,
        "UNRESOLVED": 768,
    }
    assert oracle.widened_space_is_varied is True


def test_a_comparator_that_can_disagree_does_disagree_on_the_same_space():
    """The probe's positive control: the zero is about the comparator, not the space.

    Every declared wrong comparator is run through the same instrument over the
    same widened space. If the space or ``divergence_of`` could not register a
    disagreement, these would be zero too and the identity finding would be an
    artifact of the measurement.
    """

    widened = p9._widened_oracle_space()
    for theory in p9.declared_false_comparators():
        divergence = divergence_of(
            theory.rule,
            theory_id=theory.theory_id,
            reference=p9._d1_evaluator_gold,
            space=widened,
        )
        assert divergence.points_changed > 0, theory.theory_id


def test_the_evaluator_branch_would_reject_every_declared_wrong_comparator(oracle):
    """"The branch is vacuous" and "the branch was aimed at its own reference"
    are different repairs, so both are measured."""

    capacity = oracle.capacity

    assert capacity.check_id == p9.D1_EVALUATOR_BRANCH
    assert capacity.reference_id == p9.D1_EVALUATOR_GOLD_ID
    assert set(capacity.refuted) == {
        "always-aligned",
        "cardinality-only",
        "modal-label",
        "obstruction-before-unresolved",
        "preconditions-only",
        "unknown-ignored",
    }
    assert capacity.survivors == ()
    # No registered theory is the reference restated: an inert register is as
    # vacuous as an empty one.
    assert capacity.inert_theories == ()
    assert capacity.outcome is Outcome.PASS


def test_every_declared_false_comparator_states_what_it_breaks():
    theories = p9.declared_false_comparators()

    assert len(theories) == 6
    assert len({theory.theory_id for theory in theories}) == 6
    for theory in theories:
        assert theory.breaks.strip()


def test_the_audit_blocks_and_names_the_arms_that_never_answered(archive):
    report = audit_p9_transfer_margins()

    assert report["outcome"] is Outcome.CANNOT_CHECK
    with pytest.raises(PriorValuedMargin, match="TRANSCRIPT_BAG"):
        require_responsive_comparator(report["margins"], label="P9 D1")


def test_the_audit_entry_point_exits_three_and_serialises():
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = main(["--json"])

    assert code == 3
    payload = json.loads(buffer.getvalue())
    assert payload["outcome"] == "CANNOT_CHECK"
    assert payload["result_digest"] == p9.D1_RESULT_DIGEST
    assert {item["reason"] for item in payload["margins"]} == {
        "COMPARATOR_CONSTANT",
        "COMPARATOR_RESPONDED",
    }
    assert report_as_json(audit_p9_transfer_margins()) == payload
