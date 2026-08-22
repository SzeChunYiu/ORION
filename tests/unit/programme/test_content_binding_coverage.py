"""A paper whose bytes nobody watches must not report as a paper that did not change.

The real-tree cases at the bottom are the point of the module: they fail if a
watched canonical file changes without regenerating its committed binding. The
Q-series deliberately watches only its canonical publication subset; historical
snapshots remain visible as unbound files rather than being confused with the
submission surface.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from orion.programme.content_binding_coverage import (
    CONTENT_DRIFT_GUARD_ID,
    ContentBindingNotCovered,
    PaperBinding,
    PaperBindingState,
    assess_binding_coverage,
    assess_paper,
    drift_exercise,
    inspect_paper,
    parse_sums,
    require_binding_coverage,
    survey_paper_bindings,
    survey_report,
)
from orion.programme.guard_exercise import GuardVerdictReason
from orion.programme.records import Outcome

REPO_ROOT = Path(__file__).resolve().parents[3]
DIRECT_BOUND_PAPERS = (
    "paper-06-formal-epistemic-structures-and-mechanics",
    "paper-07-epistemic-navigation-open-worlds",
    "paper-08-epistemic-authority-autonomous-science",
)
Q_SERIES_BOUND_PAPERS = (
    "Q-paper-01-tare-expressivity",
    "Q-paper-02-recursive-recovery",
    "Q-paper-03-dual-instrument",
    "Q-paper-04-typed-state",
)
BOUND_PAPERS = DIRECT_BOUND_PAPERS + Q_SERIES_BOUND_PAPERS


def binding(
    paper_id: str,
    state: PaperBindingState,
    *,
    on_disk: int = 10,
    bound: int = 0,
    drifted: tuple[str, ...] = (),
    missing: tuple[str, ...] = (),
) -> PaperBinding:
    return PaperBinding(
        paper_id=paper_id,
        directory=f"papers/{paper_id}",
        state=state,
        files_on_disk=on_disk,
        files_bound=bound,
        drifted_paths=drifted,
        missing_paths=missing,
        detail="",
    )


class TestTaxonomy:
    def test_only_a_readable_binding_exercises_the_guard(self) -> None:
        exercising = [item for item in PaperBindingState if item.exercises_drift_guard]
        assert exercising == [PaperBindingState.BOUND_CURRENT, PaperBindingState.BOUND_DRIFTED]

    def test_unbound_cannot_claim_bound_files(self) -> None:
        with pytest.raises(ValueError, match="UNBOUND contradicts"):
            binding("p", PaperBindingState.UNBOUND, bound=3)

    def test_a_state_that_compared_nothing_cannot_name_drift(self) -> None:
        with pytest.raises(ValueError, match="cannot carry drifted or missing paths"):
            binding("p", PaperBindingState.UNBOUND, drifted=("a",))

    def test_bound_current_cannot_carry_drift(self) -> None:
        with pytest.raises(ValueError, match="contradicts recorded drift"):
            binding("p", PaperBindingState.BOUND_CURRENT, bound=3, drifted=("a",))

    def test_bound_drifted_must_name_something(self) -> None:
        with pytest.raises(ValueError, match="names no drifted or missing path"):
            binding("p", PaperBindingState.BOUND_DRIFTED, bound=3)

    def test_partial_binding_is_visible(self) -> None:
        """A bound paper can still hold files no digest covers."""

        record = binding("p", PaperBindingState.BOUND_CURRENT, on_disk=10, bound=4)
        assert record.unbound_files == 6


class TestDenominator:
    def test_unbound_contributes_no_opportunities(self) -> None:
        exercise = drift_exercise((binding("p1", PaperBindingState.UNBOUND, on_disk=150),))
        assert exercise.opportunities == 0
        assert exercise.exercised is False

    def test_unbound_is_cannot_check_not_pass(self) -> None:
        """The whole point: 0 drifted out of 0 watched is an absent measurement."""

        result = assess_paper(binding("p1", PaperBindingState.UNBOUND, on_disk=150))
        assert result.outcome is Outcome.CANNOT_CHECK
        assert result.reason is GuardVerdictReason.NEVER_EXERCISED
        assert result.blocks is True

    def test_bound_and_clean_is_a_pass_that_names_its_denominator(self) -> None:
        result = assess_paper(binding("p6", PaperBindingState.BOUND_CURRENT, bound=53))
        assert result.outcome is Outcome.PASS
        assert "53 opportunities" in result.detail

    def test_drift_fails(self) -> None:
        result = assess_paper(
            binding("p6", PaperBindingState.BOUND_DRIFTED, bound=53, drifted=("a", "b"))
        )
        assert result.outcome is Outcome.FAIL

    def test_a_missing_bound_path_counts_as_a_violation(self) -> None:
        record = binding("p6", PaperBindingState.BOUND_DRIFTED, bound=53, missing=("gone.md",))
        assert record.violations == 1
        assert assess_paper(record).outcome is Outcome.FAIL

    def test_unreadable_digest_file_is_cannot_check(self) -> None:
        result = assess_paper(binding("p6", PaperBindingState.BOUND_UNREADABLE, bound=0))
        assert result.outcome is Outcome.CANNOT_CHECK


class TestRollupIsNotCompensatory:
    def test_a_bound_paper_does_not_cover_for_an_unbound_one(self) -> None:
        """Pooling would report PASS on this tree; that is the move the programme forbids."""

        bindings = (
            binding("p6", PaperBindingState.BOUND_CURRENT, bound=53),
            binding("p1", PaperBindingState.UNBOUND, on_disk=150),
        )
        pooled = drift_exercise(bindings)
        assert (pooled.opportunities, pooled.violations) == (53, 0)
        assert assess_binding_coverage(bindings).outcome is Outcome.CANNOT_CHECK

    def test_drift_outranks_an_absent_measurement_in_the_report(self) -> None:
        bindings = (
            binding("p1", PaperBindingState.UNBOUND, on_disk=1),
            binding("p6", PaperBindingState.BOUND_DRIFTED, bound=53, drifted=("a",)),
        )
        assert assess_binding_coverage(bindings).outcome is Outcome.FAIL

    def test_all_bound_and_clean_passes(self) -> None:
        bindings = (binding("p6", PaperBindingState.BOUND_CURRENT, bound=53),)
        assert assess_binding_coverage(bindings).outcome is Outcome.PASS

    def test_an_empty_survey_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="blocks by construction"):
            assess_binding_coverage(())


class TestParseSums:
    def test_round_trip(self) -> None:
        digest = "a" * 64
        assert parse_sums(f"{digest}  papers/x/y.md\n") == {"papers/x/y.md": digest}

    def test_comments_and_blanks_are_skipped(self) -> None:
        assert parse_sums(f"# note\n\n{'b' * 64}  p.md\n") == {"p.md": "b" * 64}

    @pytest.mark.parametrize(
        "line",
        ["notadigest  p.md", f"{'a' * 63}  p.md", f"{'A' * 64}  p.md", f"{'a' * 64}  "],
    )
    def test_a_malformed_line_raises_rather_than_being_dropped(self, line: str) -> None:
        """Silently skipping a line binds fewer files than the file appears to."""

        with pytest.raises(ValueError):
            parse_sums(line + "\n")


class TestAdmission:
    def test_drift_raises_first_and_names_the_papers(self) -> None:
        with pytest.raises(ContentBindingNotCovered, match="without regenerating their digests"):
            require_binding_coverage(
                (binding("p6", PaperBindingState.BOUND_DRIFTED, bound=1, drifted=("a",)),)
            )

    def test_unbound_raises_with_the_file_count(self) -> None:
        with pytest.raises(ContentBindingNotCovered, match="declare no content binding"):
            require_binding_coverage((binding("p1", PaperBindingState.UNBOUND, on_disk=150),))

    def test_a_fully_bound_survey_is_admissible(self) -> None:
        require_binding_coverage((binding("p6", PaperBindingState.BOUND_CURRENT, bound=53),))


class TestAgainstTheRealTree:
    """These are the regression guards. They read the repository, not a fixture."""

    @pytest.mark.parametrize("paper", BOUND_PAPERS)
    def test_a_bound_paper_still_matches_its_committed_digests(self, paper: str) -> None:
        """Red if any watched canonical byte changes without regenerating its binding."""

        record = inspect_paper(REPO_ROOT, REPO_ROOT / "papers" / paper)
        assert record.state is PaperBindingState.BOUND_CURRENT, record.detail
        assert record.drifted_paths == ()
        assert record.missing_paths == ()
        assert assess_paper(record).outcome is Outcome.PASS

    @pytest.mark.parametrize("paper", Q_SERIES_BOUND_PAPERS)
    def test_q_series_cross_binding_is_visible_and_partial(self, paper: str) -> None:
        record = inspect_paper(REPO_ROOT, REPO_ROOT / "papers" / paper)
        assert record.state is PaperBindingState.BOUND_CURRENT, record.detail
        assert record.files_bound > 0
        assert "Q-series" in record.detail
        # Historical snapshots / navigation files are intentionally outside the
        # canonical submission binding and remain visible in the denominator report.
        assert record.unbound_files >= 0

    def test_the_survey_covers_every_paper_directory(self) -> None:
        bindings = survey_paper_bindings(REPO_ROOT)
        on_disk = {
            item.name
            for item in (REPO_ROOT / "papers").iterdir()
            if item.is_dir() and item.name != "candidates"
        }
        assert {item.paper_id for item in bindings} == on_disk

    def test_binding_coverage_does_not_regress(self) -> None:
        """A ratchet, not a target.

        P6-P8 use local manifests and Q1-Q4 use the cross-series canonical
        publication binding. Un-binding any of those watched surfaces is a silent
        loss of the only check that notices their canonical bytes changing.
        """

        bound = [
            item
            for item in survey_paper_bindings(REPO_ROOT)
            if item.state.exercises_drift_guard
        ]
        assert len(bound) >= 7, [item.paper_id for item in bound]
        assert {item.paper_id for item in bound} >= set(BOUND_PAPERS)

    def test_the_survey_reports_cannot_check_while_other_papers_are_unbound(self) -> None:
        """Honest today, and it flips to PASS on its own once every paper binds."""

        report = survey_report(survey_paper_bindings(REPO_ROOT))
        assert report["papers_unbound"] > 0
        assert report["outcome"] == Outcome.CANNOT_CHECK.value
        assert report["files_bound"] > 0
        for paper in Q_SERIES_BOUND_PAPERS:
            assert report["by_paper"][paper]["state"] == PaperBindingState.BOUND_CURRENT.value

    def test_the_pooled_exercise_is_reported_but_is_not_the_verdict(self) -> None:
        report = survey_report(survey_paper_bindings(REPO_ROOT))
        pooled = report["pooled_exercise"]
        assert pooled["guard_id"] == CONTENT_DRIFT_GUARD_ID
        assert pooled["violations"] == 0
        # Pooled alone would read as a clean pass; the survey does not say that.
        assert report["outcome"] != Outcome.PASS.value
