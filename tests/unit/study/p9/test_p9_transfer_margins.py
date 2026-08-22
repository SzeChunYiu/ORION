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


@pytest.fixture(scope="module")
def audit_report() -> dict:
    """One audit per module.

    ``audit_p9_transfer_margins`` re-runs the whole frozen protocol, so computing
    it once per assertion is a minute of wall clock per test and buys nothing:
    every test below reads a different part of the same report.
    """

    return audit_p9_transfer_margins()


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
    from orion.study.p9.d1_experiment import D1FeatureFamily, _fit, _predict, model_specs

    assert d1_runtime.run_d1 is not None
    dataset = p9.frozen_d1_dataset()
    for spec in model_specs():
        model = _fit(dataset.train, D1FeatureFamily.TRANSCRIPT_BAG, spec)
        predictions = _predict(model, dataset.test, D1FeatureFamily.TRANSCRIPT_BAG)
        assert len(set(predictions)) == 1, spec.config_id


# --------------------------------------------------------------------------
# The protected denominator: why it is one, and that saying so is a measurement
# --------------------------------------------------------------------------


def test_the_transcript_denominator_is_the_remint_not_the_holdout(collapse):
    """The finding, with the controls that separate it from two fixable ones.

    ``512 of 515 keys are missing`` is the same sentence in three worlds.
    Refitting the vocabulary on a same-size corpus the same generator draws from
    the protected split's own domain restores every key the holdout hid, and none
    of these. That was read as "the keys are minted per instance", which is true
    and is not the cause: rebuilding the corpus with one alphabet per split
    removes every per-instance key and leaves the denominator at one, because the
    remint is disjoint across splits and that is what the protocol asks for.
    ``test_repairing_the_minting_scope_does_not_give_the_view_a_second_row``
    holds that half.
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
    assert transcript.reason is p9.ViewCollapseReason.SURFACE_REMINTED_ACROSS_SPLITS
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

    dataset = p9.frozen_d1_dataset()
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

    from orion.study.p9.d1 import COMPARISON_COORDINATES

    frozen = p9.frozen_d1_dataset()
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


def test_the_audit_blocks_and_names_the_arms_that_never_answered(audit_report):
    report = audit_report

    assert report["outcome"] is Outcome.CANNOT_CHECK
    with pytest.raises(PriorValuedMargin, match="TRANSCRIPT_BAG"):
        require_responsive_comparator(report["margins"], label="P9 D1")


def test_the_audit_entry_point_exits_three_and_serialises(audit_report):
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
    assert report_as_json(audit_report) == payload


# --- The audit measures a regenerated dataset; these say which one.


def _fresh_generator_digest() -> str:
    """What ``generate_d1_dataset`` returns in a process that imported nothing else.

    Run in a subprocess: protocol v1.2's correction is installed by an import and
    an import cannot be undone within a process, so any in-process check of the
    un-adapted generator is answering a question about test collection order.
    """

    import subprocess
    import sys

    script = (
        "from orion.study.p9.d1 import generate_d1_dataset;"
        "print(generate_d1_dataset(seed='p9-d1-method-transfer-v1').manifest_digest)"
    )
    out = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def test_the_bare_generator_does_not_produce_the_shipped_dataset() -> None:
    """The defect this guard exists for, stated as a fact rather than a worry.

    ``d1_data_runtime`` installs protocol v1.2's dependency-mutation correction by
    rebinding ``d1._mutated_value`` when it is imported. Without that import the
    generator builds the v1.1 corpus, and until ``frozen_d1_dataset`` existed the
    audit took whichever one the process happened to have.
    """

    assert _fresh_generator_digest() != p9.D1_SHIPPED_DATASET_MANIFEST_DIGEST


def test_frozen_d1_dataset_installs_the_adapter_and_checks_the_digest() -> None:
    dataset = p9.frozen_d1_dataset()

    assert dataset.manifest_digest == p9.D1_SHIPPED_DATASET_MANIFEST_DIGEST
    assert p9._v12_generator_installed() is True


def test_the_provenance_guard_refuses_a_dataset_that_is_not_the_shipped_one() -> None:
    """A guard that cannot fail is not a guard. Move the expectation, see it fire."""

    original = p9.D1_SHIPPED_DATASET_MANIFEST_DIGEST
    p9.D1_SHIPPED_DATASET_MANIFEST_DIGEST = "sha256:" + "0" * 64
    try:
        with pytest.raises(p9.D1DatasetProvenanceError, match="different corpus"):
            p9.frozen_d1_dataset()
    finally:
        p9.D1_SHIPPED_DATASET_MANIFEST_DIGEST = original


def test_the_audit_reports_which_dataset_it_measured() -> None:
    provenance = p9.d1_dataset_provenance()

    assert (
        provenance["measured_dataset_manifest_digest"]
        == provenance["shipped_dataset_manifest_digest"]
    )
    assert provenance["generator_correction_is_an_import_side_effect"] is True


# --- Per-instance minting is real, and is not what holds the denominator down.


def test_the_remint_scope_control_removes_every_per_instance_key() -> None:
    collapse = p9.d1_view_collapse_report()["TRANSCRIPT_BAG"]

    assert collapse.train_keys_in_one_train_row == 1152
    assert collapse.train_vocabulary == 1155
    assert collapse.remint_scope_train_keys_in_one_train_row == 0


def test_repairing_the_minting_scope_does_not_give_the_view_a_second_row() -> None:
    """The measurement that makes ``PER_INSTANCE_KEY_SPACE`` the wrong answer."""

    collapse = p9.d1_view_collapse_report()["TRANSCRIPT_BAG"]

    assert collapse.distinct_protected_rows == 1
    assert collapse.remint_scope_distinct_protected_rows == 1
    assert collapse.repaired_by_remint_scope is False
    assert collapse.reason is p9.ViewCollapseReason.SURFACE_REMINTED_ACROSS_SPLITS


def test_the_remint_control_leaves_the_responding_views_alone() -> None:
    """A control that changed the other three arms would be a different experiment."""

    report = p9.d1_view_collapse_report()
    for view in ("TYPED_RELATIONAL", "UNTYPED_PAIR", "TYPED_SERIALIZED_BAG"):
        collapse = report[view]
        assert collapse.remint_scope_distinct_protected_rows == (
            collapse.distinct_protected_rows
        ), view
        assert collapse.reason is p9.ViewCollapseReason.VIEW_RESPONDED, view


def test_the_remint_scope_control_changes_only_the_surface() -> None:
    from orion.study.p9.d1 import SurfaceRemintScope, generate_d1_dataset

    frozen = p9.frozen_d1_dataset()
    repaired = generate_d1_dataset(
        seed=p9.D1_SEED, surface_remint_scope=SurfaceRemintScope.PER_SPLIT
    )

    assert [row.instance_id for row in repaired.test] == [
        row.instance_id for row in frozen.test
    ]
    assert [row.label for row in repaired.test] == [row.label for row in frozen.test]
    assert repaired.test[0].surface_left != frozen.test[0].surface_left


# --- The archive's numbers, re-run rather than transcribed.


@pytest.fixture(scope="module")
def reproduction() -> dict:
    return p9.d1_reproduction_report()


def test_three_of_the_four_archived_arms_come_back(reproduction) -> None:
    for arm in ("TRANSCRIPT_BAG", "TYPED_RELATIONAL", "UNTYPED_PAIR"):
        item = reproduction[arm]
        assert item.reason is p9.ArmReproductionReason.ARM_REPRODUCED, arm
        assert item.outcome is Outcome.PASS, arm
        assert item.archived_config_id == item.reproduced_config_id, arm
        assert item.archived_accuracy == item.reproduced_accuracy, arm


def test_the_serialized_bag_arm_does_not_come_back(reproduction) -> None:
    """The one arm whose collapse drives a published CANNOT_CHECK.

    Same dataset digest, same selected configuration, different protected
    accuracy: 0.5 archived against 0.75 re-run. The audit measured that archived
    0.5 as a constant comparator for as long as it existed and never asked
    whether the 0.5 came back.
    """

    item = reproduction["TYPED_SERIALIZED_BAG"]

    assert item.archived_config_id == item.reproduced_config_id == "logistic-C1"
    assert item.archived_accuracy == 0.5
    assert item.reproduced_accuracy == 0.75
    assert item.reason is p9.ArmReproductionReason.SCORE_DIVERGED


def test_the_reproduced_serialized_bag_arm_is_not_constant(reproduction) -> None:
    """Why the divergence matters rather than being a rounding difference.

    ``COMPARATOR_CONSTANT`` on the published margin against this arm is a fact
    about the archived run. Re-run, the same configuration emits two labels, so
    the comparator responds and the margin would be measurable.
    """

    item = reproduction["TYPED_SERIALIZED_BAG"]

    assert item.archived_distinct_predictions == 1
    assert item.reproduced_distinct_predictions == 2


def test_a_divergence_off_the_recorded_environment_does_not_convict_the_archive(
    reproduction,
) -> None:
    """Two things changed and only one was measured, so the verdict says so."""

    item = reproduction["TYPED_SERIALIZED_BAG"]

    assert item.environment_departures, "this environment is not the recorded one"
    assert item.outcome is Outcome.CANNOT_CHECK
    assert "does not convict the archive" in item.detail


def test_the_same_divergence_under_the_recorded_environment_would_be_a_failure() -> None:
    """The verdict is environment-conditional, and both branches are reachable."""

    diverged = p9.ArmReproduction(
        arm_id="TYPED_SERIALIZED_BAG",
        archived_config_id="logistic-C1",
        reproduced_config_id="logistic-C1",
        archived_accuracy=0.5,
        reproduced_accuracy=0.75,
        archived_distinct_predictions=1,
        reproduced_distinct_predictions=2,
        environment_departures=(),
    )

    assert diverged.outcome is Outcome.FAIL
    assert diverged.reason is p9.ArmReproductionReason.SCORE_DIVERGED


def test_a_different_selection_is_reported_apart_from_a_different_score() -> None:
    """Two divergences with two different repairs must not share one verdict."""

    selection = p9.ArmReproduction(
        arm_id="ANY",
        archived_config_id="logistic-C1",
        reproduced_config_id="tree-depth6",
        archived_accuracy=0.5,
        reproduced_accuracy=0.5,
        archived_distinct_predictions=1,
        reproduced_distinct_predictions=1,
        environment_departures=(),
    )

    assert selection.reason is p9.ArmReproductionReason.SELECTION_DIVERGED
    assert "selected tree-depth6" in selection.detail


def test_the_recorded_environment_is_pinned_from_the_committed_record() -> None:
    assert p9.D1_RECORDED_ENVIRONMENT == {
        "python": "3.12.13",
        "numpy": "2.5.2",
        "scikit-learn": "1.9.0",
        "scipy": "1.18.0",
    }
    assert set(p9.d1_observed_environment()) == set(p9.D1_RECORDED_ENVIRONMENT)


def test_the_audit_carries_the_reproduction_and_it_reaches_the_rollup(audit_report) -> None:
    report = audit_report

    assert set(report["reproduction"]) == {
        "TRANSCRIPT_BAG",
        "TYPED_RELATIONAL",
        "TYPED_SERIALIZED_BAG",
        "UNTYPED_PAIR",
    }
    assert report["outcome"].blocks is True
    encoded = report_as_json(report)
    assert encoded["reproduction"]["TYPED_SERIALIZED_BAG"]["reason"] == "SCORE_DIVERGED"


# --------------------------------------------------------------------------
# The evaluator branch, checked by a comparator that could have denied it
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def independence():
    return p9.d1_independent_oracle()


def _pair(*, left_changes: dict, right_changes: dict):
    """One D1 instance built by hand, so a divergence can be read rather than counted."""

    from orion.transfer.v2.canonical import content_digest
    from orion.transfer.v2.p1_method_realization import build_method_realization

    from orion.study.p9.d1 import D1Domain, D1Instance, D1Split, classify_methods

    shared = dict(
        source_digest=content_digest({"p9-d1-hand-built-pair": "v1"}),
        source_version="p9-d1-hand-built-pair-v1",
        authority_boundary="REPRESENTATION_ONLY",
        target_role="hand_built",
        assumptions=("a1",),
        resources=("r1",),
        representation_in="in",
        representation_out="out",
        mechanics=("alpha", "beta"),
        lineage=("donor:hand",),
        preconditions=("p1",),
        invariants=("i1",),
        effects=("e1",),
        progress_measure="pm",
        terminal_condition="tc",
        reconstruction_map="rm",
        failure_modes=("f1",),
        dependencies=(("alpha", "beta"),),
    )
    left = build_method_realization(method_id="hand-left", **{**shared, **left_changes})
    right = build_method_realization(method_id="hand-right", **{**shared, **right_changes})
    instance = D1Instance(
        instance_id="hand-built",
        domain=D1Domain.WORKFLOW,
        split=D1Split.TEST,
        left=left,
        right=right,
        label=classify_methods(left, right),
        mutation_coordinates=(),
        surface_left=("l0", "l1"),
        surface_right=("r0", "r1"),
        surface_role_left="l-role",
        surface_role_right="r-role",
    )
    instance.verify()
    return instance


def test_the_declaration_is_read_off_the_frozen_protocol_files() -> None:
    """The comparator's specification, bound to the bytes that declare it."""

    declaration = p9.d1_protocol_declaration()

    assert declaration.comparison_coordinates == (
        "preconditions",
        "invariants",
        "effects",
        "progress_measure",
        "terminal_condition",
        "reconstruction_map",
        "failure_modes",
        "dependencies",
    )
    assert declaration.labels == ("ALIGNED", "OBSTRUCTION", "UNRESOLVED")
    assert declaration.typed_payload_schema == "P9.D1Typed.v1"
    assert declaration.unknown_holdout_coordinate == "reconstruction_map"
    assert declaration.unknown_must_be_marked_not_fabricated is True
    # Exactly the three coordinates the declaration allows an explicit UNKNOWN.
    assert set(declaration.scalar_coordinates) == {
        "progress_measure",
        "terminal_condition",
        "reconstruction_map",
    }
    assert declaration.kind("dependencies") is (
        p9.DeclaredComparison.DEPENDENCY_TOPOLOGY_OVER_ROLE_INDICES
    )
    assert set(declaration.digests) == set(p9.D1_PROTOCOL_PATHS)


def test_the_declared_coordinates_are_the_ones_the_evaluator_compares() -> None:
    """Read from the protocol, compared to the evaluator's tuple, never imported from it."""

    from orion.study.p9.d1 import COMPARISON_COORDINATES

    assert p9.d1_protocol_declaration().comparison_coordinates == COMPARISON_COORDINATES


def test_the_declaration_refuses_a_protocol_that_is_not_the_declared_one() -> None:
    """A guard that cannot fail is not a guard. Move the expectation, see it fire."""

    original = p9.D1_PROTOCOL_DIGESTS
    p9.D1_PROTOCOL_DIGESTS = {
        schema: "sha256:" + "0" * 64 for schema in p9.D1_PROTOCOL_PATHS
    }
    try:
        with pytest.raises(
            p9.D1ProtocolDeclarationError, match="not the declaration this comparator"
        ):
            p9.d1_protocol_declaration()
    finally:
        p9.D1_PROTOCOL_DIGESTS = original


def test_the_declaration_refuses_a_comparison_semantics_it_never_implemented() -> None:
    """The per-coordinate meaning is looked up in the protocol, not assumed."""

    original = p9._DECLARED_COMPARISON
    p9._DECLARED_COMPARISON = {
        text: kind
        for text, kind in original.items()
        if kind is not p9.DeclaredComparison.SEMANTIC_VALUE_OR_EXPLICIT_UNKNOWN
    }
    try:
        with pytest.raises(
            p9.D1ProtocolDeclarationError, match="does not implement"
        ):
            p9.d1_protocol_declaration()
    finally:
        p9._DECLARED_COMPARISON = original


def test_the_independent_comparator_agrees_with_gold_on_every_shipped_case(
    independence,
) -> None:
    """The measurement the branch was supposed to make and never could."""

    assert independence.frozen_space.points == 512
    assert independence.frozen_space.points_changed == 0
    assert independence.protected_space.points == 128
    assert independence.protected_space.points_changed == 0


def test_the_independent_comparator_can_disagree_with_the_one_the_artifact_ran(
    independence,
) -> None:
    """The test of independence: a second implementation that cannot differ is the first.

    384 of the 1,280 pairs the D1 generator never builds get a different answer
    from the comparator ``run_d1`` grades with. That is what makes the zeros
    above a measurement instead of a restatement.
    """

    assert independence.against_shipped_comparator.points == 1280
    assert independence.against_shipped_comparator.points_changed == 384
    assert independence.is_independent is True
    assert independence.widened_space.points_changed == 384


def test_the_branch_is_reachable_for_a_conforming_comparator_and_does_not_fire(
    independence,
) -> None:
    assert independence.branch == "D1_EVALUATOR_FAILURE"
    assert independence.branch_reachable is True
    assert independence.branch_fires is False
    assert independence.verdict is p9.IndependenceVerdict.INDEPENDENT_AND_AGREED
    assert independence.outcome is Outcome.PASS
    assert independence.blocks is False


def test_the_artifacts_own_comparator_is_still_an_identity(oracle, independence) -> None:
    """The repair is a second implementation in the audit, not a change to D1.

    ``run_d1`` still grades itself with ``exact_relational_comparator``, so
    ``D1_EVALUATOR_FAILURE`` remains unreachable *for the artifact as run*. Both
    verdicts are reported because they are about different things.
    """

    assert oracle.verdict is p9.OracleVerdict.IDENTITY_BY_CONSTRUCTION
    assert oracle.branch_reachable is False
    assert oracle.outcome is Outcome.CANNOT_CHECK
    assert independence.branch_reachable is True


def test_the_only_divergence_is_a_coordinate_that_carries_no_value(
    independence,
) -> None:
    """Every one of the 384, in one direction, with the shape that causes it."""

    assert independence.divergent_label_pairs == ((("OBSTRUCTION", "UNRESOLVED"), 384),)
    witness = independence.witness
    assert witness["perturbed_coordinates"] == ["reconstruction_map"]
    assert witness["evaluator_gold"] == "OBSTRUCTION"
    assert witness["protocol_declared"] == "UNRESOLVED"
    assert witness["coordinates_carrying_no_value"] == [
        {
            "coordinate": "reconstruction_map",
            "side": "right",
            "value": None,
            "marked_unknown": False,
        }
    ]


def test_the_evaluator_decides_an_obstruction_on_a_coordinate_no_source_stated() -> None:
    """The finding, hand-built so a reader can check it without the harness.

    Two methods identical on all eight compared coordinates except that the right
    one states no ``reconstruction_map`` and is not marked unknown. D1's
    ``unknown_holdout`` declares that an unstated coordinate is marked rather than
    fabricated, and ``D1_PROTOCOL_V1_1`` admits only "exact semantic value or
    explicit UNKNOWN" there. ``classify_methods`` compares the absent value like
    any other and answers a decided OBSTRUCTION.
    """

    from orion.study.p9.d1 import classify_methods
    from orion.study.p9.d1_experiment import exact_relational_comparator

    instance = _pair(left_changes={}, right_changes={"reconstruction_map": None})

    assert classify_methods(instance.left, instance.right).value == "OBSTRUCTION"
    assert exact_relational_comparator(instance) == "OBSTRUCTION"
    assert p9.protocol_declared_comparator(instance) == "UNRESOLVED"


def test_the_two_readings_coincide_wherever_the_d1_generator_can_reach() -> None:
    """Why no published number moves: D1 nulls a coordinate and marks it together."""

    from orion.study.p9.d1 import classify_methods

    marked = _pair(
        left_changes={},
        right_changes={
            "reconstruction_map": None,
            "unknown_coordinates": ("reconstruction_map",),
        },
    )
    aligned = _pair(left_changes={}, right_changes={})
    obstructed = _pair(left_changes={}, right_changes={"terminal_condition": "tc2"})

    for instance, label in ((marked, "UNRESOLVED"), (aligned, "ALIGNED"), (obstructed, "OBSTRUCTION")):
        assert classify_methods(instance.left, instance.right).value == label
        assert p9.protocol_declared_comparator(instance) == label


def test_the_independent_comparator_ignores_what_the_declaration_excludes() -> None:
    """``mechanics`` is not a comparison coordinate, so an unknown mark on it is inert."""

    instance = _pair(left_changes={}, right_changes={"unknown_coordinates": ("mechanics",)})

    assert p9.protocol_declared_comparator(instance) == "ALIGNED"


def test_the_branch_still_rejects_every_declared_wrong_comparator(independence) -> None:
    """The instrument's refutation capacity, re-measured against the new reference."""

    capacity = independence.capacity

    assert capacity.check_id == p9.D1_EVALUATOR_BRANCH
    assert capacity.reference_id == p9.D1_PROTOCOL_COMPARATOR_ID
    assert set(capacity.refuted) == {
        "always-aligned",
        "cardinality-only",
        "modal-label",
        "obstruction-before-unresolved",
        "preconditions-only",
        "unknown-ignored",
    }
    assert capacity.survivors == ()
    assert capacity.inert_theories == ()
    assert capacity.outcome is Outcome.PASS


def _independence(real, *, shipped_divergence: int, protected_divergence: int):
    from orion.programme.refutation_capacity import TheoryDivergence

    return p9.OracleIndependence(
        comparator_id=real.comparator_id,
        reference_id=real.reference_id,
        shipped_comparator_id=real.shipped_comparator_id,
        branch=real.branch,
        declaration=real.declaration,
        frozen_space=real.frozen_space,
        protected_space=TheoryDivergence(
            theory_id="protected", points=128, points_changed=protected_divergence
        ),
        widened_space=real.widened_space,
        against_shipped_comparator=TheoryDivergence(
            theory_id="shipped", points=1280, points_changed=shipped_divergence
        ),
        divergent_label_pairs=real.divergent_label_pairs,
        divergence_shape=real.divergence_shape,
        witness=real.witness,
        capacity=real.capacity,
    )


def test_a_second_comparator_that_cannot_disagree_is_reported_as_no_measurement(
    independence,
) -> None:
    """The state this whole exercise replaces, still reachable in the type."""

    inert = _independence(independence, shipped_divergence=0, protected_divergence=0)

    assert inert.is_independent is False
    assert inert.branch_reachable is False
    assert inert.verdict is p9.IndependenceVerdict.NOT_INDEPENDENT
    assert inert.outcome is Outcome.CANNOT_CHECK


def test_a_second_comparator_that_denied_the_protected_split_would_fail(
    independence,
) -> None:
    """The other branch: a disagreement on the corpus the archive was scored on."""

    denied = _independence(independence, shipped_divergence=384, protected_divergence=1)

    assert denied.branch_fires is True
    assert denied.verdict is p9.IndependenceVerdict.DIVERGED_ON_THE_SHIPPED_CORPUS
    assert denied.outcome is Outcome.FAIL


def test_the_audit_carries_the_independence_check_without_promoting_the_archive(
    audit_report,
) -> None:
    report = audit_report

    assert report["independence_outcome"] is Outcome.PASS
    # The archive still does not clear: the view collapse and the unreproduced
    # serialized arm block, and the artifact's own branch is still an identity.
    assert report["oracle_outcome"] is Outcome.CANNOT_CHECK
    assert report["outcome"] is Outcome.CANNOT_CHECK
    encoded = report_as_json(report)
    assert encoded["independence"]["verdict"] == "INDEPENDENT_AND_AGREED"
    assert encoded["independence"]["against_shipped_comparator"]["points_changed"] == 384
    assert encoded["independence"]["branch_reachable"] is True
    assert encoded["independence"]["branch_fires"] is False
