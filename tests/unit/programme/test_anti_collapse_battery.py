"""One alarm case and one no-alarm case per anti-collapse check.

The no-alarm assertion (:func:`test_a_healthy_programme_raises_no_alarm`) is not
decoration. A battery that fires on a well-formed programme is worse than no
battery, because it gets switched off. Every negative fixture named in
``catalogue.ALL_CHECKS`` lives in this module, and
:func:`test_every_declared_negative_fixture_exists_here` enforces that.
"""

from __future__ import annotations

from dataclasses import replace

from orion.programme.catalogue import ALL_CHECKS, run_anti_collapse_battery
from orion.programme.checks_diversity import (
    CIRCULAR_SELF_CITATION,
    FORGOTTEN_NEGATIVE_HISTORY,
    METHOD_MONOCULTURE,
    REPEATED_FAILURE_CLASS,
    UNIVERSE_COLLAPSE,
)
from orion.programme.checks_evidence import (
    BENCHMARK_OVERFIT,
    EVALUATOR_GAMING,
    HIDDEN_DELETION,
    INSUFFICIENT_PROTECTED_EVIDENCE,
    STALE_AUTHORITY,
)
from orion.programme.programme_state import CANDIDATE_CUSTODY, ProgrammeState
from orion.programme.records import Outcome


def _outcome(state: ProgrammeState, check_id: str) -> Outcome:
    report = run_anti_collapse_battery(state)
    return next(result.outcome for result in report.results if result.check_id == check_id)


def test_a_healthy_programme_raises_no_alarm(clean_state: ProgrammeState) -> None:
    report = run_anti_collapse_battery(clean_state)
    offenders = {
        result.check_id: (result.outcome.value, result.reason, result.findings)
        for result in report.results
        if result.outcome is not Outcome.PASS
    }
    assert offenders == {}
    assert report.blocked is False
    assert report.grants_phase4_closure is False


def test_benchmark_overfit_fails_on_diverging_epochs(clean_state: ProgrammeState) -> None:
    later = replace(clean_state.epochs[1], fresh_transfer_metric=0.41)
    state = replace(clean_state, epochs=(clean_state.epochs[0], later))
    assert _outcome(state, BENCHMARK_OVERFIT) is Outcome.FAIL


def test_evaluator_gaming_fails_on_candidate_custody(clean_state: ProgrammeState) -> None:
    captured = replace(clean_state.epochs[1], evaluator_custody=CANDIDATE_CUSTODY)
    state = replace(clean_state, epochs=(clean_state.epochs[0], captured))
    assert _outcome(state, EVALUATOR_GAMING) is Outcome.FAIL


def test_evaluator_gaming_fails_on_undeclared_evaluator_swap(
    clean_state: ProgrammeState,
) -> None:
    swapped = replace(clean_state.epochs[1], evaluator_artifact_hash="b" * 64)
    state = replace(clean_state, epochs=(clean_state.epochs[0], swapped))
    assert _outcome(state, EVALUATOR_GAMING) is Outcome.FAIL


def test_stale_authority_fails_on_source_version_substitution(
    clean_state: ProgrammeState,
) -> None:
    state = replace(clean_state, current_source_versions=(("s-1", "v4"),))
    assert _outcome(state, STALE_AUTHORITY) is Outcome.FAIL


def test_stale_authority_cannot_check_without_a_version_map(
    clean_state: ProgrammeState,
) -> None:
    state = replace(clean_state, current_source_versions=())
    assert _outcome(state, STALE_AUTHORITY) is Outcome.CANNOT_CHECK


def test_hidden_deletion_fails_when_negative_history_shrinks(
    clean_state: ProgrammeState,
) -> None:
    pruned = replace(clean_state.epochs[1], negative_history_entry_ids=("nh-2",))
    state = replace(clean_state, epochs=(clean_state.epochs[0], pruned))
    assert _outcome(state, HIDDEN_DELETION) is Outcome.FAIL


def test_insufficient_protected_evidence_fails_on_unbacked_claim(
    clean_state: ProgrammeState,
) -> None:
    unbacked = replace(clean_state.epochs[1], protected_evidence_present=False)
    state = replace(clean_state, epochs=(clean_state.epochs[0], unbacked))
    assert _outcome(state, INSUFFICIENT_PROTECTED_EVIDENCE) is Outcome.FAIL


def test_insufficient_protected_evidence_cannot_check_when_no_claim_is_made(
    clean_state: ProgrammeState,
) -> None:
    quiet = replace(
        clean_state.epochs[1],
        protected_evidence_present=False,
        conclusion_claimed=False,
    )
    state = replace(clean_state, epochs=(clean_state.epochs[0], quiet))
    assert _outcome(state, INSUFFICIENT_PROTECTED_EVIDENCE) is Outcome.CANNOT_CHECK


def test_universe_collapse_fails_on_source_family_monoculture(
    clean_state: ProgrammeState,
) -> None:
    narrowed = replace(
        clean_state.epochs[1],
        source_family_evidence_counts=(("arxiv", 20), ("journal", 1)),
    )
    state = replace(clean_state, epochs=(clean_state.epochs[0], narrowed))
    assert _outcome(state, UNIVERSE_COLLAPSE) is Outcome.FAIL


def test_universe_collapse_cannot_check_without_a_declared_ceiling(
    clean_state: ProgrammeState,
) -> None:
    state = replace(clean_state, source_family_share_ceiling=None)
    assert _outcome(state, UNIVERSE_COLLAPSE) is Outcome.CANNOT_CHECK


def test_method_monoculture_fails_without_challenger(clean_state: ProgrammeState) -> None:
    epochs = tuple(
        replace(epoch, selected_method_ids=("m-a",), evaluated_method_ids=("m-a",))
        for epoch in clean_state.epochs
    )
    state = replace(clean_state, epochs=epochs)
    assert _outcome(state, METHOD_MONOCULTURE) is Outcome.FAIL


def test_method_monoculture_passes_when_a_challenger_was_evaluated(
    clean_state: ProgrammeState,
) -> None:
    epochs = tuple(
        replace(epoch, selected_method_ids=("m-a",), evaluated_method_ids=("m-a", "m-b"))
        for epoch in clean_state.epochs
    )
    state = replace(clean_state, epochs=epochs)
    assert _outcome(state, METHOD_MONOCULTURE) is Outcome.PASS


def test_forgotten_negative_history_fails_on_unanswered_class(
    clean_state: ProgrammeState,
) -> None:
    forgetful = replace(clean_state.method_records[0], known_failure_classes=("F-A", "F-Z"))
    state = replace(clean_state, method_records=(forgetful,))
    assert _outcome(state, FORGOTTEN_NEGATIVE_HISTORY) is Outcome.FAIL


def test_circular_self_citation_fails_on_internal_only_support(
    clean_state: ProgrammeState,
) -> None:
    state = replace(clean_state, internal_source_families=("arxiv",))
    assert _outcome(state, CIRCULAR_SELF_CITATION) is Outcome.FAIL


def test_circular_self_citation_cannot_check_without_declared_internal_families(
    clean_state: ProgrammeState,
) -> None:
    state = replace(clean_state, internal_source_families=())
    assert _outcome(state, CIRCULAR_SELF_CITATION) is Outcome.CANNOT_CHECK


def test_repeated_failure_class_fails_on_unchanged_response(
    clean_state: ProgrammeState,
) -> None:
    repeated = replace(clean_state.epochs[1], cycle_failure_interventions=(("F-A", "I-1"),))
    state = replace(clean_state, epochs=(clean_state.epochs[0], repeated))
    assert _outcome(state, REPEATED_FAILURE_CLASS) is Outcome.FAIL


def test_every_declared_negative_fixture_exists_here() -> None:
    """A check whose fixture does not exist has never been shown to fail."""

    module_tests = {name for name in globals() if name.startswith("test_")}
    missing = sorted(
        check.negative_fixture_id
        for check in ALL_CHECKS
        if check.negative_fixture_id not in module_tests
    )
    assert missing == []
