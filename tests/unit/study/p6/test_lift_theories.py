"""P6's shipped formal checkers, and the refutation capacity they now have.

Every number pinned here was read off the shipped artifacts
``research/claim_expansion/p6/P6_X2_CERTIFICATE_LIFTING_RESULT_V1.json`` and
``P6_X_FINITE_MODEL_RESULT_V1.json`` or off the checkers that produced them.

Five of those checkers' quantities used to reject **no** declared false theory:
each compared an expression against a copy of itself, or asserted only the
premise of the claim it was named for. This file is now split in two, and the
split is the point.

*What the repair bought* is pinned as refutations that must not go away ---
:func:`test_no_shipped_check_accepts_every_false_theory` fails the moment any
check goes back to accepting the whole register, and the tests around it name
which primitive earns which rejection.

*What the repair did not buy* is pinned just as hard. The ``donor`` axis is still
inert and the shipped result must keep publishing its own multiplicity; the
"independent" verifier still diverges from the primary on 0 of 320 points; the
``t5`` transition counter still adds nothing over ``t2`` on this register. A test
that only pinned the good news would let those quietly stop being reported.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    MechanizedCheck,
    ModelPoint,
    assess_theory_coverage,
    axis_sensitivity,
    divergence_of,
    measure_refutation_capacity,
    require_refutable,
)
from orion.study.p6 import finite_model_theories as finite
from orion.study.p6 import lift_theories as lifting
from orion.study.p6.refutation_audit import audit_p6_formal_checkers, main, report_as_json

REPO_ROOT = Path(__file__).resolve().parents[4]
P6X = REPO_ROOT / "research/claim_expansion/p6"
X2_RESULT = P6X / "P6_X2_CERTIFICATE_LIFTING_RESULT_V1.json"
X_RESULT = P6X / "P6_X_FINITE_MODEL_RESULT_V1.json"
X2_CHECKER = P6X / "check_p6_x2_certificate_lifting.py"
X_CHECKER = P6X / "check_p6_x_finite_models.py"


def _load(name: str, path: Path) -> Any:
    """Import a shipped checker from its published file.

    Loaded by path rather than ``exec``-ed from a string because both checkers
    gate their equivalence counters on :func:`inspect.getsource`; a module with
    no file behind it cannot establish that its two sides are distinct, and the
    checkers correctly report ``CANNOT_CHECK`` instead of a pass.
    """

    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_x2(module: Any) -> dict:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        module.main()
    return json.loads(buffer.getvalue())


def _lifting_capacity(check: MechanizedCheck):
    return measure_refutation_capacity(
        check,
        reference=lifting.reference_lift,
        reference_id=lifting.REFERENCE_ID,
        theories=lifting.FALSE_LIFT_THEORIES,
        space=lifting.lifting_model_space(),
    )


def _finite_capacity(check: MechanizedCheck):
    return measure_refutation_capacity(
        check,
        reference=finite.reference_admissible,
        reference_id=finite.REFERENCE_ID,
        theories=finite.FALSE_ADMISSIBILITY_THEORIES,
        space=finite.finite_model_space(),
    )


def _by_id(capacities):
    return {item.check_id: item for item in capacities}


def _lifting_capacities():
    return _by_id(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS)


def _finite_capacities():
    return _by_id(_finite_capacity(check) for check in finite.SHIPPED_CHECKS)


# --------------------------------------------------------------------------
# Fidelity: the instrument is pointed at the published artifact.
# --------------------------------------------------------------------------


def test_the_transcription_reproduces_the_shipped_row_digest() -> None:
    published = json.loads(X2_RESULT.read_text())
    assert lifting.SHIPPED_ROWS_SHA256 == published["canonical_rows_sha256"]
    assert lifting.canonical_rows_digest() == lifting.SHIPPED_ROWS_SHA256
    assert len(lifting.lifting_model_space()) == published["state_evaluations"] == 320


def test_the_finite_model_space_is_the_shipped_one() -> None:
    published = json.loads(X_RESULT.read_text())
    space = finite.finite_model_space()
    assert len(space) == published["state_evaluations"] == 1536
    assert len(space) // len(finite.EMBEDDINGS) == published["states_per_embedding"] == 512


def test_every_shipped_check_accepts_the_rule_the_artifact_ran() -> None:
    """A transcription that rejects the shipped rule would credit its own bug."""

    for check in lifting.SHIPPED_CHECKS:
        assert check.accepts(lifting.reference_lift), check.check_id
    for check in finite.SHIPPED_CHECKS:
        assert check.accepts(finite.reference_admissible), check.check_id


def test_every_registered_theory_actually_departs_from_its_reference() -> None:
    """A register of paraphrases has the same denominator as an empty one."""

    for theory in lifting.FALSE_LIFT_THEORIES:
        assert divergence_of(
            theory.rule,
            theory_id=theory.theory_id,
            reference=lifting.reference_lift,
            space=lifting.lifting_model_space(),
        ).applied, theory.theory_id
    for theory in finite.FALSE_ADMISSIBILITY_THEORIES:
        assert divergence_of(
            theory.rule,
            theory_id=theory.theory_id,
            reference=finite.reference_admissible,
            space=finite.finite_model_space(),
        ).applied, theory.theory_id


# --------------------------------------------------------------------------
# The capacity that must not go away.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "check_id",
    [check.check_id for check in lifting.SHIPPED_CHECKS]
    + [check.check_id for check in finite.SHIPPED_CHECKS],
)
def test_no_shipped_check_accepts_every_false_theory(check_id: str) -> None:
    """The regression guard the whole repair exists for.

    Five of these ten quantities used to refute 0 of their register. If any of
    them collapses back into a comparison the rule cannot enter --- a copy
    restored, a projection re-flattened, a conclusion dropped for its premise ---
    it lands here by name rather than as a case count nobody reads.
    """

    capacities = {**_lifting_capacities(), **_finite_capacities()}
    capacity = capacities[check_id]

    assert capacity.refuted, f"{check_id} rejects no declared false theory"
    assert capacity.outcome is Outcome.PASS
    assert not capacity.blocks


def test_the_projection_primitive_is_what_rejects_the_donor_irrelevant_theory() -> None:
    """``science_lifts_without_donor`` walked through all five checks; now T1 rejects it.

    Not by a rule about that theory. The image of the lift along the donor
    projection must equal the donor's own verdict, and both directions of that
    equality bite: manufacturing donor validity (``science_lifts_without_donor``,
    ``everything_lifts``) and withdrawing it (``nothing_lifts``).
    """

    capacity = _lifting_capacities()["donor_conservativity_violations"]

    assert set(capacity.refuted) == {
        "science_lifts_without_donor",
        "everything_lifts",
        "nothing_lifts",
        "donor_family_decides",
    }


def test_the_three_assertion_blocks_still_never_visit_an_invalid_donor_certificate() -> None:
    """The hole is closed by T1, not by the blocks that had it.

    Every assertion in the separation, countermodel and revalidation blocks still
    evaluates the rule at ``native_valid=True``, so each still accepts the
    donor-irrelevant theory. That is worth keeping visible: the panel is complete
    because a new claim covers those states, not because the old claims changed.
    """

    capacities = _lifting_capacities()

    for check_id in (
        "single_coordinate_separation_witnesses",
        "certificate_product_countermodels",
        "selective_revalidation",
    ):
        assert "science_lifts_without_donor" in capacities[check_id].survivors, check_id


def test_the_extension_strictly_dominates_the_ad_hoc_exception() -> None:
    """P6-U-T5's unblock, as a comparison rather than a claim.

    :data:`lifting.DONOR_REQUIREMENT_CHECK` is the one-line exception --- nothing
    lifts without a valid donor. It closes the same coverage hole. The shipped
    conservativity check rejects everything it rejects and more, because it is an
    equality rather than a prohibition, and it is not about any one theory.
    """

    exception = _lifting_capacity(lifting.DONOR_REQUIREMENT_CHECK)
    extension = _lifting_capacities()["donor_conservativity_violations"]

    assert "science_lifts_without_donor" in exception.refuted
    assert set(exception.refuted) < set(extension.refuted)


def test_the_forgetful_map_is_what_rejects_science_without_donor() -> None:
    """The finite-model twin of the same primitive."""

    capacity = _finite_capacities()["t1_violations"]

    assert set(capacity.refuted) == {
        "science_without_donor",
        "everything_admissible",
        "nothing_admissible",
        "embedding_decides",
    }


def test_the_transition_primitive_is_what_gives_t5_a_falsifier() -> None:
    """``t5`` asserted only the premise of its own countermodel; now it asserts both."""

    capacity = _finite_capacities()["t5_violations"]

    assert "donor_recomputation_launders" in capacity.refuted
    assert len(finite.donor_valid_transitions()) == 2880


def test_both_panels_reject_every_theory_in_their_registers() -> None:
    lifting_coverage = assess_theory_coverage(
        tuple(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS), label="P6.V4.6"
    )
    finite_coverage = assess_theory_coverage(
        tuple(_finite_capacity(check) for check in finite.SHIPPED_CHECKS), label="P6-U-T1"
    )

    assert lifting_coverage.unrefuted == ()
    assert finite_coverage.unrefuted == ()
    assert lifting_coverage.outcome is Outcome.PASS
    assert finite_coverage.outcome is Outcome.PASS


def test_require_refutable_now_passes_both_panels() -> None:
    require_refutable(
        tuple(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS), label="P6.V4.6"
    )
    require_refutable(
        tuple(_finite_capacity(check) for check in finite.SHIPPED_CHECKS), label="P6-U-T1"
    )


def test_the_instrument_still_fails_a_check_that_accepts_everything() -> None:
    """The measurement is only worth its passes if it can still produce a FAIL.

    A panel of passes is what the original defect looked like from the outside,
    so the instrument is exercised on a check that is a tautology by
    construction.
    """

    tautology = MechanizedCheck(
        check_id="compares_the_rule_with_itself",
        asserts="the rule agrees with the rule on every enumerated point",
        accepts=lambda rule: not any(
            rule(point) != rule(point) for point in lifting.lifting_model_space()
        ),
    )

    capacity = _lifting_capacity(tautology)

    assert capacity.refuted == ()
    assert capacity.outcome is Outcome.FAIL
    assert capacity.blocks


# --------------------------------------------------------------------------
# What the repair did not buy, pinned so it keeps being reported.
# --------------------------------------------------------------------------


def test_the_donor_axis_is_still_a_pure_loop_multiplier() -> None:
    """``liftable`` does not take the donor family, and the artifact must say so.

    Donor-independence is a claim P6 makes --- ``donor_family_decides`` is in the
    register precisely because the verdict must not depend on the issuing family
    --- so this axis is inert by design and no repair should make it otherwise.
    What was wrong was publishing 320 / 25 / 155 / 1,055 without saying they are
    64 / 5 / 31 / 211 and a five-fold relabelling. The result now carries its own
    multiplicity, and this pins that it keeps carrying it.
    """

    sensitivity = axis_sensitivity(
        "donor", reference=lifting.reference_lift, space=lifting.lifting_model_space()
    )

    assert sensitivity.values == 5
    assert sensitivity.comparable_pairs == 640
    assert sensitivity.verdict_changing_pairs == 0
    assert sensitivity.inert
    assert sensitivity.multiplier == 5

    published = json.loads(X2_RESULT.read_text())
    axis = published["donor_axis"]
    assert axis["read_by_liftable"] is False
    assert axis["multiplier"] == 5
    assert (
        axis["distinct_state_evaluations"],
        axis["distinct_separation_witnesses"],
        axis["distinct_full_revalidation_successes"],
        axis["distinct_partial_revalidation_failures"],
        axis["distinct_product_countermodels"],
    ) == (64, 5, 31, 211, 31)


def test_every_published_count_is_reported_with_its_multiplicity() -> None:
    """"Every count repeated 5x" is the fact; the audit has to print the table.

    ``320`` is 64 observed once per donor family and ``25`` is 5 observed five
    times, and both are numbers a reader misreads without the factor beside them.
    Only the 31 product countermodels are 31 distinct facts, because their loop
    does not range over donors.
    """

    rows = {row["count"]: row for row in lifting.published_count_multiplicity()}

    assert (rows["state_evaluations"]["published"], rows["state_evaluations"]["factor"]) == (
        320,
        5,
    )
    assert rows["state_evaluations"]["distinct"] == 64
    assert rows["single_coordinate_separation_witnesses"]["distinct"] == 5
    assert rows["single_coordinate_separation_witnesses"]["factor"] == 5
    assert rows["full_revalidation_successes"]["distinct"] == 31
    assert rows["partial_revalidation_failures"]["distinct"] == 211
    assert rows["certificate_product_countermodels"]["factor"] == 1
    assert rows["certificate_product_countermodels"]["distinct"] == 31


def test_the_native_validity_axis_is_read_on_one_distinct_state() -> None:
    sensitivity = axis_sensitivity(
        "native_valid", reference=lifting.reference_lift, space=lifting.lifting_model_space()
    )

    assert sensitivity.comparable_pairs == 160
    assert sensitivity.verdict_changing_pairs == 5
    assert not sensitivity.inert


def test_the_independent_verifier_still_diverges_on_no_point() -> None:
    """A second implementation that cannot disagree confirms a digest, not a theorem.

    Untouched by this repair and not fixable by it: what P6-U-T4 needs is a
    reviewer, and a repository cannot produce one for itself. The audit must keep
    reporting the 0.
    """

    divergence = divergence_of(
        lifting.INDEPENDENT_LIFT.rule,
        theory_id=lifting.INDEPENDENT_LIFT.theory_id,
        reference=lifting.reference_lift,
        space=lifting.lifting_model_space(),
    )

    assert (divergence.points, divergence.points_changed) == (320, 0)
    assert not divergence.applied
    assert audit_p6_formal_checkers()[0]["independent_divergence"].points_changed == 0


def test_t5_adds_no_refutation_over_t2_on_this_register() -> None:
    """Honestly stated rather than hidden by a well-chosen formulation.

    ``t2``'s separation pairs are a subset of ``t5``'s donor-valid transitions, so
    ``t5`` cannot reject less --- and on this register it rejects no more. The
    check is worth having because its claim is now asserted rather than assumed;
    it is not worth having as extra coverage, and nothing here pretends it is.
    """

    capacities = _finite_capacities()

    assert set(capacities["t5_violations"].refuted) == set(
        capacities["t2_separation_pairs"].refuted
    )


def test_the_no_alarm_counter_still_cannot_separate_laundering_from_lifting() -> None:
    """Under its own guard ``scientific_admissible`` reduces to ``donor_valid``."""

    assert "donor_validity_is_admissibility" in _finite_capacities()["t3_violations"].survivors


# --------------------------------------------------------------------------
# The published artifacts, and the shipped scripts run against wrong theories.
# --------------------------------------------------------------------------


def test_the_lifting_result_publishes_two_checked_counters_and_a_complete_panel() -> None:
    """Both structural counters are measurements now, and the terminal is earned.

    The five measured quantities are untouched and the row digest is byte for
    byte the shipped one: the repair changed what the checker *claims*, not what
    it found. ``assertion_coverage_status`` is ``COMPLETE`` because the
    conservativity block quantifies over each fibre of the projection, so the 32
    states with an invalid donor certificate are visited by T1 itself --- not
    because a "nothing lifts without a donor" assertion was bolted on.
    """

    published = json.loads(X2_RESULT.read_text())

    assert published["terminal"] == "PASS"
    assert published["donor_conservativity_status"] == "CHECKED"
    assert published["donor_conservativity_violations"] == 0
    assert published["ideal_product_status"] == "CHECKED"
    assert published["ideal_product_mismatches"] == 0
    assert published["cannot_check_reasons"] == []
    assert published["assertion_coverage_status"] == "COMPLETE"
    assert published["assertion_covered_states"] == published["assertion_state_space"] == 64
    assert published["assertion_covered_states_native_invalid"] == 32
    assert published["assertion_uncovered_states"] == 0
    assert published["canonical_rows_sha256"] == lifting.SHIPPED_ROWS_SHA256
    assert (
        published["state_evaluations"],
        published["single_coordinate_separation_witnesses"],
        published["certificate_product_countermodels"],
        published["full_revalidation_successes"],
        published["partial_revalidation_failures"],
    ) == (320, 25, 31, 155, 1055)


def test_the_finite_model_result_publishes_three_checked_counters() -> None:
    published = json.loads(X_RESULT.read_text())

    assert published["terminal"] == "PASS"
    assert published["t1_status"] == "CHECKED"
    assert published["t4_status"] == "CHECKED"
    assert published["cannot_check_reasons"] == []
    assert (
        published["t1_violations"],
        published["t3_violations"],
        published["t4_violations"],
        published["t5_violations"],
    ) == (0, 0, 0, 0)
    assert published["t1_donor_visible_states"] == 96
    assert published["t5_donor_valid_transitions"] == 2880
    assert (published["t2_separation_pairs"], published["t5_countermodels"]) == (96, 96)


def _science_lifts_without_donor(native_valid: bool, science: tuple[bool, ...]) -> bool:
    """P6.V4.1 denied outright, as a substitutable rule with recoverable source."""

    del native_valid
    return all(science)


def test_the_shipped_lifting_script_now_rejects_the_donor_irrelevant_theory() -> None:
    """Executed against the published file, not against this module's transcription.

    This test used to pin the defect: the script ran to completion under this
    theory and printed P6.V4.6's headline sentence unchanged, with both
    structural counters reading 0. The five measured quantities still do not
    move --- their assertion blocks never leave ``native_valid=True`` --- and that
    is the finding. What moves is the conservativity counter, which is what
    having the projection buys.
    """

    shipped = _run_x2(_load("p6_x2_shipped", X2_CHECKER))
    module = _load("p6_x2_under_test", X2_CHECKER)
    module.liftable = _science_lifts_without_donor
    donor_irrelevant = _run_x2(module)

    assert shipped["terminal"] == "PASS"
    assert shipped["canonical_rows_sha256"] == lifting.SHIPPED_ROWS_SHA256

    for key in (
        "state_evaluations",
        "single_coordinate_separation_witnesses",
        "certificate_product_countermodels",
        "full_revalidation_successes",
        "partial_revalidation_failures",
    ):
        assert donor_irrelevant[key] == shipped[key], key

    assert donor_irrelevant["canonical_rows_sha256"] != shipped["canonical_rows_sha256"]
    assert donor_irrelevant["donor_conservativity_violations"] > 0
    assert donor_irrelevant["ideal_product_mismatches"] > 0
    assert donor_irrelevant["terminal"] == "FAIL"


def test_the_shipped_finite_script_now_rejects_science_without_donor() -> None:
    module = _load("p6_x_under_test", X_CHECKER)
    sci_fields = module.SCI_FIELDS

    def science_without_donor(state, embedding):
        del embedding
        return all(state[field] for field in sci_fields)

    module.scientific_admissible = science_without_donor
    result = module.run()

    assert result["t1_violations"] == 72
    assert result["t4_violations"] > 0
    assert result["terminal"] == "FAIL"
    assert _load("p6_x_shipped", X_CHECKER).run()["terminal"] == "PASS"


def test_the_structural_independence_gates_still_catch_a_collapse() -> None:
    """The repair is only as durable as the distinction between the two sides.

    Both checkers keep a gate that refuses to publish a violation count when the
    two sides of a comparison are one expression written twice. It has to say yes
    to the shipped pairs and no to a collapse, or it is decoration.
    """

    def left(point: ModelPoint) -> bool:
        return bool(point["native_valid"])

    def right(point: ModelPoint) -> bool:
        """Same statements, different prose: a docstring must not buy independence."""

        return bool(point["native_valid"])

    for checker in (_load("p6_x2_gate", X2_CHECKER), _load("p6_x_gate", X_CHECKER)):
        gate: Callable[..., bool] = checker._independently_defined
        assert gate(left, right) is False
        assert gate(checker.ideal_product, left) is True


def test_the_audit_passes_and_names_both_checkers() -> None:
    reports = audit_p6_formal_checkers()
    payload = report_as_json(reports)

    assert payload["outcome"] == "PASS"
    assert not Outcome(payload["outcome"]).blocks
    assert [item["checker_id"] for item in payload["checkers"]] == [
        "check_p6_x2_certificate_lifting",
        "check_p6_x_finite_models",
    ]
    assert reports[0]["reproduces_shipped_digest"] is True
    assert json.dumps(payload)  # the report must survive serialisation


def test_the_cli_exits_zero() -> None:
    assert main([]) == 0
    assert main(["--json"]) == 0
