"""P6's shipped formal checkers, measured against the wrong theories they accept.

Every number pinned here was read off the shipped artifacts
``research/claim_expansion/p6/P6_X2_CERTIFICATE_LIFTING_RESULT_V1.json`` and
``P6_X_FINITE_MODEL_RESULT_V1.json`` or off the checkers that produced them.
"""

from __future__ import annotations

import contextlib
import io
import json
import types
from pathlib import Path

import pytest

from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    UnrefutableCheck,
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
X2_RESULT = REPO_ROOT / "research/claim_expansion/p6/P6_X2_CERTIFICATE_LIFTING_RESULT_V1.json"
X_RESULT = REPO_ROOT / "research/claim_expansion/p6/P6_X_FINITE_MODEL_RESULT_V1.json"


def _lifting_capacity(check):
    return measure_refutation_capacity(
        check,
        reference=lifting.reference_lift,
        reference_id=lifting.REFERENCE_ID,
        theories=lifting.FALSE_LIFT_THEORIES,
        space=lifting.lifting_model_space(),
    )


def _finite_capacity(check):
    return measure_refutation_capacity(
        check,
        reference=finite.reference_admissible,
        reference_id=finite.REFERENCE_ID,
        theories=finite.FALSE_ADMISSIBILITY_THEORIES,
        space=finite.finite_model_space(),
    )


def _by_id(capacities):
    return {item.check_id: item for item in capacities}


def test_the_transcription_reproduces_the_shipped_row_digest() -> None:
    """The instrument is pointed at the published artifact, not at a fixture."""

    published = json.loads(X2_RESULT.read_text())
    assert lifting.SHIPPED_ROWS_SHA256 == published["canonical_rows_sha256"]
    assert lifting.canonical_rows_digest() == lifting.SHIPPED_ROWS_SHA256
    assert len(lifting.lifting_model_space()) == published["state_evaluations"] == 320


def test_the_finite_model_space_is_the_shipped_one() -> None:
    published = json.loads(X_RESULT.read_text())
    space = finite.finite_model_space()
    assert len(space) == published["state_evaluations"] == 1536
    assert len(space) // len(finite.EMBEDDINGS) == published["states_per_embedding"] == 512


def test_the_two_lifting_counters_reject_no_false_theory_at_all() -> None:
    """``donor_conservativity_violations`` and ``ideal_product_mismatches`` are ``x != x``."""

    capacities = _by_id(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS)

    for check_id in ("donor_conservativity_violations", "ideal_product_mismatches"):
        capacity = capacities[check_id]
        assert capacity.outcome is Outcome.FAIL
        assert capacity.refuted == ()
        assert len(capacity.survivors) == len(lifting.FALSE_LIFT_THEORIES) == 8


def test_the_three_lifting_assertion_blocks_do_have_falsifiers() -> None:
    """The instrument can credit a check, which is what makes its FAILs worth acting on."""

    capacities = _by_id(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS)

    for check_id in (
        "single_coordinate_separation_witnesses",
        "certificate_product_countermodels",
        "selective_revalidation",
    ):
        assert capacities[check_id].outcome is Outcome.PASS, check_id


def test_no_lifting_assertion_ever_visits_an_invalid_donor_certificate() -> None:
    """A theory that drops the donor certificate walks through all three assertion blocks."""

    asserting = (
        "single_coordinate_separation_witnesses",
        "certificate_product_countermodels",
        "selective_revalidation",
    )
    capacities = _by_id(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS)

    for check_id in asserting:
        assert "science_lifts_without_donor" in capacities[check_id].survivors


def test_the_omitted_donor_requirement_check_closes_the_panel() -> None:
    """The repair is one assertion, and it covers the theory the shipped panel misses."""

    shipped = tuple(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS)
    assert assess_theory_coverage(shipped, label="shipped").unrefuted == (
        "science_lifts_without_donor",
    )

    repaired = shipped + (_lifting_capacity(lifting.DONOR_REQUIREMENT_CHECK),)
    coverage = assess_theory_coverage(repaired, label="repaired")

    assert "science_lifts_without_donor" in repaired[-1].refuted
    assert coverage.outcome is Outcome.PASS
    assert coverage.unrefuted == ()


def test_the_donor_axis_is_a_pure_loop_multiplier() -> None:
    """320 / 25 / 155 / 1,055 are 64 / 5 / 31 / 211 facts and a five-fold relabelling."""

    sensitivity = axis_sensitivity(
        "donor", reference=lifting.reference_lift, space=lifting.lifting_model_space()
    )

    assert sensitivity.values == 5
    assert sensitivity.comparable_pairs == 640
    assert sensitivity.verdict_changing_pairs == 0
    assert sensitivity.inert
    assert sensitivity.multiplier == 5

    published = json.loads(X2_RESULT.read_text())
    for key in (
        "state_evaluations",
        "single_coordinate_separation_witnesses",
        "full_revalidation_successes",
        "partial_revalidation_failures",
    ):
        assert published[key] % sensitivity.multiplier == 0


def test_the_native_validity_axis_is_read_on_one_distinct_state() -> None:
    sensitivity = axis_sensitivity(
        "native_valid", reference=lifting.reference_lift, space=lifting.lifting_model_space()
    )

    assert sensitivity.comparable_pairs == 160
    assert sensitivity.verdict_changing_pairs == 5
    assert not sensitivity.inert


def test_the_independent_verifier_diverges_on_no_point() -> None:
    """A second implementation that cannot disagree confirms a digest, not a theorem."""

    divergence = divergence_of(
        lifting.INDEPENDENT_LIFT.rule,
        theory_id=lifting.INDEPENDENT_LIFT.theory_id,
        reference=lifting.reference_lift,
        space=lifting.lifting_model_space(),
    )

    assert divergence.points == 320
    assert divergence.points_changed == 0
    assert not divergence.applied


def test_the_finite_model_terminal_rests_on_three_unsatisfiable_counters() -> None:
    """``"terminal": "PASS"`` is ``not (t1 or t3 or t4)`` and t1/t4 read nothing."""

    published = json.loads(X_RESULT.read_text())
    assert published["terminal"] == "PASS"
    assert (published["t1_violations"], published["t3_violations"], published["t4_violations"]) == (
        0,
        0,
        0,
    )

    capacities = _by_id(_finite_capacity(check) for check in finite.SHIPPED_CHECKS)
    for check_id in ("t1_violations", "t4_violations", "t5_countermodels"):
        capacity = capacities[check_id]
        assert capacity.outcome is Outcome.FAIL
        assert capacity.refuted == ()
        assert len(capacity.survivors) == len(finite.FALSE_ADMISSIBILITY_THEORIES) == 7


def test_the_no_alarm_counter_cannot_separate_laundering_from_lifting() -> None:
    """Under its own guard ``scientific_admissible`` reduces to ``donor_valid``."""

    capacity = _by_id(_finite_capacity(check) for check in finite.SHIPPED_CHECKS)["t3_violations"]

    assert "donor_validity_is_admissibility" in capacity.survivors


def test_the_finite_model_separations_do_have_a_falsifier() -> None:
    """The instrument is capable of crediting a check, which is why its FAILs mean something."""

    capacity = _by_id(_finite_capacity(check) for check in finite.SHIPPED_CHECKS)[
        "t2_separation_pairs"
    ]

    assert set(capacity.refuted) >= {
        "donor_validity_is_admissibility",
        "epoch_field_inert",
        "majority_of_science_suffices",
        "everything_admissible",
    }


def test_every_registered_theory_actually_departs_from_its_reference() -> None:
    """A register of paraphrases has the same denominator as an empty one."""

    for theory in lifting.FALSE_LIFT_THEORIES:
        divergence = divergence_of(
            theory.rule,
            theory_id=theory.theory_id,
            reference=lifting.reference_lift,
            space=lifting.lifting_model_space(),
        )
        assert divergence.applied, theory.theory_id
    for theory in finite.FALSE_ADMISSIBILITY_THEORIES:
        divergence = divergence_of(
            theory.rule,
            theory_id=theory.theory_id,
            reference=finite.reference_admissible,
            space=finite.finite_model_space(),
        )
        assert divergence.applied, theory.theory_id


def test_every_shipped_check_accepts_the_rule_the_artifact_ran() -> None:
    """A transcription that rejects the shipped rule would credit its own bug."""

    for check in lifting.SHIPPED_CHECKS:
        assert check.accepts(lifting.reference_lift), check.check_id
    for check in finite.SHIPPED_CHECKS:
        assert check.accepts(finite.reference_admissible), check.check_id


def test_the_audit_blocks_and_names_both_checkers() -> None:
    reports = audit_p6_formal_checkers()
    payload = report_as_json(reports)

    assert payload["outcome"] == "FAIL"
    assert Outcome(payload["outcome"]).blocks
    assert [item["checker_id"] for item in payload["checkers"]] == [
        "check_p6_x2_certificate_lifting",
        "check_p6_x_finite_models",
    ]
    assert reports[0]["reproduces_shipped_digest"] is True
    assert json.dumps(payload)  # the report must survive serialisation


def test_require_refutable_blocks_the_shipped_lifting_panel() -> None:
    capacities = tuple(_lifting_capacity(check) for check in lifting.SHIPPED_CHECKS)

    with pytest.raises(UnrefutableCheck) as caught:
        require_refutable(capacities, label="P6.V4.6")

    message = str(caught.value)
    assert "ideal_product_mismatches" in message
    assert "donor_conservativity_violations" in message
    assert "science_lifts_without_donor" in message


def test_the_finite_model_panel_covers_its_whole_register() -> None:
    """Reported plainly: the 1,536-state panel's blind spot is per-quantity, not per-theory."""

    capacities = tuple(_finite_capacity(check) for check in finite.SHIPPED_CHECKS)

    assert assess_theory_coverage(capacities, label="P6-U-T1").unrefuted == ()


def test_the_cli_exits_three() -> None:
    assert main([]) == 3
    assert main(["--json"]) == 3


def test_the_shipped_script_reproduces_its_headline_under_a_donor_irrelevant_theory() -> None:
    """Executed against the published file, not against this module's transcription.

    ``science_lifts_without_donor`` denies P6.V4.1 outright, and the shipped
    checker runs to completion and prints the same 320 / 25 / 31 / 155 / 1,055
    and the same zero donor-conservativity violations. Only the row digest moves,
    and the primary checker prints it rather than asserting it.
    """

    source = (
        REPO_ROOT / "research/claim_expansion/p6/check_p6_x2_certificate_lifting.py"
    ).read_text()

    def run(rule=None) -> dict:
        module = types.ModuleType("p6_x2_under_test")
        module.__dict__["__name__"] = "p6_x2_under_test"
        exec(compile(source, "check_p6_x2_certificate_lifting.py", "exec"), module.__dict__)
        if rule is not None:
            module.liftable = rule
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            module.main()
        return json.loads(buffer.getvalue())

    shipped = run()
    donor_irrelevant = run(lambda native_valid, science: all(science))

    assert shipped["canonical_rows_sha256"] == lifting.SHIPPED_ROWS_SHA256
    for key in (
        "state_evaluations",
        "single_coordinate_separation_witnesses",
        "certificate_product_countermodels",
        "full_revalidation_successes",
        "partial_revalidation_failures",
        "donor_conservativity_violations",
    ):
        assert donor_irrelevant[key] == shipped[key], key
    assert donor_irrelevant["canonical_rows_sha256"] != shipped["canonical_rows_sha256"]
