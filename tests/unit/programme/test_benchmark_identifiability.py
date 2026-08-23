"""An audit that could not run must not read as an audit that found nothing.

The module under test exists because P4 repaired one label leak and shipped
another, and nothing in the harness was positioned to notice. These tests hold
the instrument to the property that makes noticing possible: every way for the
audit to establish nothing has to come back ``CANNOT_CHECK``, and no path may
produce a ``PASS`` that was never earned.
"""

from __future__ import annotations

import pytest

from orion.programme.benchmark_identifiability import (
    AuditedGuardVerdict,
    AuditedScore,
    CaseSplit,
    CueKind,
    IdentifiabilityAudit,
    IdentifiabilityReason,
    LabelledCase,
    ProbeResult,
    ShortcutProbe,
    audit_label_identifiability,
    require_identified,
    score_probe,
)
from orion.programme.guard_exercise import GuardExercise, assess_guard
from orion.programme.records import Outcome

LEAKY = ShortcutProbe(
    probe_id="length",
    kind=CueKind.STRING_SHAPE,
    cue_names=("length",),
    cue_rationale="a character count reads no word of the evidence",
)
BLIND = ShortcutProbe(
    probe_id="count",
    kind=CueKind.COUNT,
    cue_names=("count",),
    cue_rationale="how many objects the case carries is fixed by the generator",
)


def _case(case_id: str, label: str, split: CaseSplit, *, length: int, count: int = 1):
    return LabelledCase(
        case_id=case_id, label=label, split=split, cues={"length": length, "count": count}
    )


def _battery(*, leak: bool) -> list[LabelledCase]:
    """Ten cases per split, two labels, with the length cue leaking or not."""

    cases = []
    for split in (CaseSplit.FIT, CaseSplit.EVAL):
        for index in range(10):
            hit = index < 4
            label = "CANNOT_CHECK" if hit else "BLOCK"
            length = (122 if hit else 86) if leak else 86
            cases.append(_case(f"{split.value}-{index}", label, split, length=length))
    return cases


def _audit(cases, probes=(LEAKY, BLIND), **kwargs) -> IdentifiabilityAudit:
    return audit_label_identifiability(
        benchmark_id="bench", label="CANNOT_CHECK", cases=cases, probes=probes, **kwargs
    )


def test_a_cue_that_separates_the_label_fails_the_audit() -> None:
    audit = _audit(_battery(leak=True))
    assert audit.outcome is Outcome.FAIL
    assert audit.reason is IdentifiabilityReason.LABEL_RECOVERED_BY_CUE
    assert audit.worst_recovery == 1.0
    assert "length" in audit.detail


def test_a_cue_that_does_not_separate_the_label_passes() -> None:
    """The audit has to be capable of a pass, or failing means nothing."""

    audit = _audit(_battery(leak=False))
    assert audit.outcome is Outcome.PASS
    assert audit.reason is IdentifiabilityReason.NO_CUE_RECOVERED_LABEL
    assert audit.worst_recovery == 0.0


def test_registering_no_probe_blocks_rather_than_passes() -> None:
    """Nobody looked. Zero recovered labels records that, not a clean benchmark."""

    audit = _audit(_battery(leak=True), probes=())
    assert audit.outcome is Outcome.CANNOT_CHECK
    assert audit.reason is IdentifiabilityReason.NO_PROBE_REGISTERED
    assert audit.outcome.blocks


def test_an_empty_eval_split_blocks() -> None:
    cases = [case for case in _battery(leak=True) if case.split is CaseSplit.FIT]
    audit = _audit(cases)
    assert audit.reason is IdentifiabilityReason.NO_EVAL_CASES
    assert audit.outcome is Outcome.CANNOT_CHECK


def test_an_empty_fit_split_blocks() -> None:
    cases = [case for case in _battery(leak=True) if case.split is CaseSplit.EVAL]
    audit = _audit(cases)
    assert audit.reason is IdentifiabilityReason.NO_FIT_CASES
    assert audit.outcome is Outcome.CANNOT_CHECK


def test_a_constant_eval_label_blocks() -> None:
    """The saturation itself, typed.

    An eval split on which every case carries the same terminal cannot tell a
    probe from a constant predictor --- and cannot tell two scored systems apart
    either, which is what H3's eleven identical 1.0s were.
    """

    cases = [
        case
        for case in _battery(leak=True)
        if case.split is CaseSplit.FIT or case.label == "BLOCK"
    ]
    audit = _audit(cases)
    assert audit.reason is IdentifiabilityReason.LABEL_CONSTANT_ON_EVAL
    assert audit.outcome is Outcome.CANNOT_CHECK


ABSENT = ShortcutProbe(
    probe_id="absent",
    kind=CueKind.FIELD_MISSINGNESS,
    cue_names=("no_such_cue",),
    cue_rationale="whether a field is null says nothing about support",
)


def test_a_probe_whose_cue_is_absent_scores_nothing_and_blocks() -> None:
    """A probe that never ran reports no leak. That is P1's lesson, one layer in."""

    audit = _audit(_battery(leak=True), probes=(ABSENT,))
    assert audit.reason is IdentifiabilityReason.NO_PROBE_SCORED
    assert audit.outcome is Outcome.CANNOT_CHECK
    assert audit.results[0].unscored == 10  # every eval case, none of them scored
    assert audit.results[0].recovery is None


def test_one_inert_probe_blocks_an_otherwise_clean_audit() -> None:
    """A silent nothing must not average in with a real zero.

    The audit rolls up several probes. If an inert one could sit beside a scored
    one, the set would report "no cue recovered the label" while one of the cues
    was never read --- which is the failure the module exists to catch, committed
    by the module.
    """

    audit = _audit(_battery(leak=False), probes=(LEAKY, ABSENT))
    assert audit.outcome is Outcome.CANNOT_CHECK
    assert audit.reason is IdentifiabilityReason.NO_PROBE_SCORED
    assert "absent" in audit.detail


def test_a_ceiling_finer_than_the_split_can_express_blocks() -> None:
    """Four positives can express informedness 0, 0.25, 0.5 ...; 0.01 is not a bar."""

    audit = _audit(_battery(leak=False), max_recovery=0.01)
    assert audit.reason is IdentifiabilityReason.TOLERANCE_FINER_THAN_RESOLUTION
    assert audit.outcome is Outcome.CANNOT_CHECK


def test_an_unseen_signature_is_unscored_not_credited() -> None:
    """A probe may not earn credit on a pattern the fit split never showed it."""

    cases = _battery(leak=True)
    cases.append(_case("EVAL-novel", "CANNOT_CHECK", CaseSplit.EVAL, length=999))
    result = score_probe(LEAKY, cases, label="CANNOT_CHECK")
    assert result.unscored == 1
    assert result.true_positive == 4


def test_informedness_is_none_when_the_label_never_varies_on_eval() -> None:
    """Not 0.0. An absent measurement must not be reportable as a clean one."""

    result = ProbeResult(
        probe_id="p",
        label="CANNOT_CHECK",
        fitted_signatures=1,
        scored=10,
        unscored=0,
        true_positive=0,
        false_positive=0,
        true_negative=10,
        false_negative=0,
    )
    assert result.recovery is None
    assert result.resolution is None


def test_a_confusion_matrix_must_total_the_scored_cases() -> None:
    with pytest.raises(ValueError, match="confusion matrix"):
        ProbeResult(
            probe_id="p",
            label="l",
            fitted_signatures=1,
            scored=10,
            unscored=0,
            true_positive=1,
            false_positive=0,
            true_negative=0,
            false_negative=0,
        )


def test_a_probe_without_a_rationale_cannot_be_built() -> None:
    with pytest.raises(ValueError, match="rationale is required"):
        ShortcutProbe(
            probe_id="p", kind=CueKind.COUNT, cue_names=("count",), cue_rationale="  "
        )


def test_a_case_without_cues_cannot_be_built() -> None:
    with pytest.raises(ValueError, match="no cue values"):
        LabelledCase(case_id="c", label="BLOCK", split=CaseSplit.EVAL, cues={})


def test_a_vacuous_reason_cannot_be_paired_with_pass() -> None:
    """The substitution this module exists to prevent, refused at construction."""

    with pytest.raises(ValueError, match="cannot yield PASS"):
        IdentifiabilityAudit(
            benchmark_id="bench",
            label="CANNOT_CHECK",
            outcome=Outcome.PASS,
            reason=IdentifiabilityReason.NO_PROBE_REGISTERED,
            detail="nobody looked",
            results=(),
        )


def test_a_score_cannot_be_built_on_a_blocking_audit() -> None:
    audit = _audit(_battery(leak=True))
    with pytest.raises(ValueError, match="LABEL_RECOVERED_BY_CUE"):
        AuditedScore(score_name="correct_cannot_check_rate", value=1.0, audit=audit)


def test_a_score_survives_a_passing_audit() -> None:
    audit = _audit(_battery(leak=False))
    score = AuditedScore(score_name="correct_cannot_check_rate", value=1.0, audit=audit)
    assert score.as_json()["value"] == 1.0
    assert score.as_json()["audit"]["outcome"] == "PASS"


def _guard(violations: int) -> GuardExercise:
    return GuardExercise(
        guard_id="false_scientific_promotion",
        arm_id="ORION",
        opportunities=360,
        violations=violations,
        opportunity_definition="one case whose gold terminal is not PROMOTE",
    )


def test_a_guard_that_held_on_a_leaking_benchmark_is_cannot_check() -> None:
    """The P4 shape: real denominator, real zero, and still not evidence."""

    guard = assess_guard(_guard(0))
    assert guard.outcome is Outcome.PASS
    joined = AuditedGuardVerdict(guard=guard, audit=_audit(_battery(leak=True)))
    assert joined.outcome is Outcome.CANNOT_CHECK
    assert joined.blocks


def test_a_guard_that_failed_on_a_leaking_benchmark_still_fails() -> None:
    """A leak would only have made passing easier, so a violation still stands."""

    joined = AuditedGuardVerdict(
        guard=assess_guard(_guard(180)), audit=_audit(_battery(leak=True))
    )
    assert joined.outcome is Outcome.FAIL


def test_a_guard_that_held_on_an_identified_benchmark_passes() -> None:
    joined = AuditedGuardVerdict(
        guard=assess_guard(_guard(0)), audit=_audit(_battery(leak=False))
    )
    assert joined.outcome is Outcome.PASS
    assert not joined.blocks


def test_require_identified_names_what_it_blocked_on() -> None:
    with pytest.raises(ValueError, match="LABEL_RECOVERED_BY_CUE"):
        require_identified(_audit(_battery(leak=True)))
    require_identified(_audit(_battery(leak=False)))
