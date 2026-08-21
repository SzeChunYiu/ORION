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
from orion.study.p9 import transfer_margins as p9
from orion.study.p9.transfer_audit import audit_p9_transfer_margins, main, report_as_json


@pytest.fixture(scope="module")
def archive() -> dict:
    return p9.load_shipped_d1_result()


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


def test_the_evaluator_failure_branch_recomputes_the_gold_it_grades():
    """P6's question, answered with P6's instrument rather than a second one."""

    divergence = p9.d1_oracle_divergence()

    assert divergence.points == 512
    assert divergence.points_changed == 0
    assert divergence.applied is False


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
