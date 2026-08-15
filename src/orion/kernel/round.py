from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from orion.experience.model import EpisodeOutcome, TaskEpisode
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell
from orion.mechanics.program import (
    MechanicsProgramMetrics,
    observe_mechanics_program,
    plan_program_questions,
)
from orion.mechanics.questioning import MechanicQuestion
from orion.mechanics.research import MechanicResearchTask, research_task_for_question

from .apply import GradedApplication, grade_and_apply
from .gate import AnswerAuthority, AnswerGrading, DiscriminatingCheck
from .guards import (
    GuardRule,
    apply_selection_guards,
    guard_refusals,
    structural_grading_signature,
    variation_grading_signature,
)
from .scheduler import observe_dimension_yields, order_by_observed_yield
from .store import EntryKind, LedgerStore


class AnswerSource(Protocol):
    """Where a round obtains candidate answers for its selected questions."""

    def fetch(
        self,
        tasks: tuple[MechanicResearchTask, ...],
        cells: tuple[MechanicCell, ...],
        round_index: int,
    ) -> tuple[AnswerRecord, ...]: ...


@dataclass(frozen=True)
class RoundOutcome:
    """Everything one round observed, decided and durably recorded."""

    round_index: int
    before: MechanicsProgramMetrics
    after: MechanicsProgramMetrics
    selected_question_ids: tuple[str, ...]
    fetched_record_ids: tuple[str, ...]
    application: GradedApplication
    guard_refusal_reasons: tuple[tuple[str, tuple[str, ...]], ...]
    false_progress_reasons: tuple[str, ...]
    episodes: tuple[TaskEpisode, ...]
    cells: tuple[MechanicCell, ...]

    @property
    def verified_closures(self) -> int:
        return self.before.open_question_count - self.after.open_question_count

    @property
    def productive(self) -> bool:
        """A round is productive only when it verifiably closed something."""

        return self.verified_closures > 0


def _episode(
    grading: AnswerGrading,
    *,
    run_id: str,
    round_index: int,
    outcome: EpisodeOutcome,
    pre_hash: str,
    post_hash: str,
    timestamp: str,
    extra_reasons: Sequence[str] = (),
) -> TaskEpisode:
    reasons = tuple(grading.reasons) + tuple(extra_reasons)
    return TaskEpisode(
        episode_id=f"{run_id}:r{round_index}:{grading.record_id}",
        task_id=f"{grading.mechanic_id}:{grading.dimension.value}",
        run_id=f"{run_id}:r{round_index}",
        parent_run_id=None,
        evaluation_epoch_id=f"{run_id}:epoch{round_index}",
        split_id=f"round-{round_index}",
        mechanic_id=grading.mechanic_id,
        problem_signature=(grading.mechanic_id, grading.dimension.value),
        variation_signature=variation_grading_signature(grading),
        pre_state_hash=pre_hash,
        action_ids=(f"answer:{grading.record_id}",),
        observation_ids=tuple(f"reason:{item}" for item in reasons),
        outcome=outcome,
        failure_signature=structural_grading_signature(grading)
        if outcome is not EpisodeOutcome.SUCCESS
        else (),
        residual_ids=(),
        evidence_ids=tuple(item.ref for item in grading.evidence if item.resolved),
        evidence_bindings=tuple(
            (item.ref, item.actual_digest) for item in grading.evidence if item.resolved
        ),
        post_state_hash=post_hash,
        timestamp=timestamp,
    )


def run_round(
    cells: tuple[MechanicCell, ...],
    *,
    store: LedgerStore,
    source: AnswerSource,
    evidence_roots: Mapping[str, Path],
    checks: Mapping[str, DiscriminatingCheck] = {},
    guards: tuple[GuardRule, ...] = (),
    run_id: str = "orion",
    round_index: int = 0,
    selection_limit: int = 16,
    timestamp: str = "1970-01-01T00:00:00Z",
    require_digest: bool = True,
) -> RoundOutcome:
    """Execute one governed self-driving round and persist what it decided.

    The round is deliberately fail-closed at every write-back edge: answers that
    do not resolve their evidence are refused, answers refused by an active
    guard are refused again, and any closure the applied answers cannot account
    for is reported as false progress rather than banked as work done.
    """

    before = observe_mechanics_program(cells)
    # Fixed audit priority first, then the run's own measured yield, then what
    # it has learned to refuse. Each stage only reorders, never drops: a
    # scheduler that could delete a question would close the audit by looking
    # away from it.
    selected = apply_selection_guards(
        order_by_observed_yield(
            plan_program_questions(cells, limit=selection_limit),
            observe_dimension_yields(store),
        ),
        guards,
    )
    by_id = {cell.mechanic_id: cell for cell in cells}
    tasks = tuple(
        research_task_for_question(by_id[question.mechanic_id], question)
        for question in selected
        if question.mechanic_id in by_id
    )

    fetched = source.fetch(tasks, cells, round_index)
    application = grade_and_apply(
        cells,
        fetched,
        evidence_roots=evidence_roots,
        checks=checks,
        require_digest=require_digest,
        round_index=round_index,
    )

    refusals: list[tuple[str, tuple[str, ...]]] = []
    withheld: set[str] = set()
    for grading in application.gradings:
        reasons = guard_refusals(grading, guards)
        if reasons:
            refusals.append((grading.record_id, reasons))
            withheld.add(grading.record_id)

    if withheld:
        # Re-apply from the original cells with guard-refused answers removed so a
        # guard actually withholds content rather than annotating it after the fact.
        application = grade_and_apply(
            cells,
            tuple(item for item in fetched if item.record_id not in withheld),
            evidence_roots=evidence_roots,
            checks=checks,
            require_digest=require_digest,
        )

    after = observe_mechanics_program(application.cells)
    from orion.mechanics.answers import audit_answer_application

    false_progress = tuple(
        item.note
        for item in audit_answer_application(
            before.open_question_count, after.open_question_count, application.report
        )
    )

    pre_hash = f"open:{before.open_question_count}"
    post_hash = f"open:{after.open_question_count}"
    episodes: list[TaskEpisode] = []
    for grading in application.gradings:
        if grading.authority is AnswerAuthority.VERIFIED:
            outcome = EpisodeOutcome.SUCCESS
        elif grading.authority is AnswerAuthority.EVIDENCE_BOUND:
            outcome = EpisodeOutcome.PARTIAL_SUCCESS
        else:
            outcome = EpisodeOutcome.FAILURE
        extra = dict(refusals).get(grading.record_id, ())
        episodes.append(
            _episode(
                grading,
                run_id=run_id,
                round_index=round_index,
                outcome=EpisodeOutcome.BLOCKED if extra else outcome,
                pre_hash=pre_hash,
                post_hash=post_hash,
                timestamp=timestamp,
                extra_reasons=extra,
            )
        )

    outcome = RoundOutcome(
        round_index=round_index,
        before=before,
        after=after,
        selected_question_ids=tuple(item.question_id for item in selected),
        fetched_record_ids=tuple(item.record_id for item in fetched),
        application=application,
        guard_refusal_reasons=tuple(refusals),
        false_progress_reasons=false_progress,
        episodes=tuple(episodes),
        cells=application.cells,
    )
    _persist(store, outcome, fetched)
    return outcome


def _persist(
    store: LedgerStore, outcome: RoundOutcome, fetched: tuple[AnswerRecord, ...]
) -> None:
    for record in fetched:
        store.append(
            EntryKind.ANSWER,
            {
                "record_id": record.record_id,
                "mechanic_id": record.mechanic_id,
                "dimension": record.dimension.value,
                "lane": record.lane,
                "evidence_refs": list(record.evidence_refs),
                "evidence_bindings": [list(item) for item in record.evidence_bindings],
                "payload": [[name, list(values)] for name, values in record.payload],
                "waiver_reason": record.waiver_reason,
                "supersedes": record.supersedes,
                "round_index": outcome.round_index,
            },
        )
    for grading in outcome.application.gradings:
        store.append(
            EntryKind.GRADING,
            {
                "record_id": grading.record_id,
                "mechanic_id": grading.mechanic_id,
                "dimension": grading.dimension.value,
                "authority": grading.authority.value,
                "check_id": grading.check_id,
                "check_outcome": grading.check_outcome.value
                if grading.check_outcome
                else "",
                "reasons": list(grading.reasons),
                "round_index": outcome.round_index,
            },
        )
    for episode in outcome.episodes:
        store.append(
            EntryKind.EPISODE,
            {
                "episode_id": episode.episode_id,
                "task_id": episode.task_id,
                "run_id": episode.run_id,
                "mechanic_id": episode.mechanic_id,
                "outcome": episode.outcome.value,
                "failure_signature": list(episode.failure_signature),
                "variation_signature": list(episode.variation_signature),
                "evaluation_epoch_id": episode.evaluation_epoch_id,
                "split_id": episode.split_id,
                "problem_signature": list(episode.problem_signature),
                "action_ids": list(episode.action_ids),
                "observation_ids": list(episode.observation_ids),
                "evidence_ids": list(episode.evidence_ids),
                "evidence_bindings": [list(item) for item in episode.evidence_bindings],
                "pre_state_hash": episode.pre_state_hash,
                "post_state_hash": episode.post_state_hash,
                "timestamp": episode.timestamp,
                "round_index": outcome.round_index,
            },
        )
    for reason in outcome.false_progress_reasons:
        store.append(
            EntryKind.RESIDUAL,
            {"kind": "FALSE_PROGRESS", "note": reason, "round_index": outcome.round_index},
        )
    store.append(
        EntryKind.ROUND,
        {
            "round_index": outcome.round_index,
            "open_before": outcome.before.open_question_count,
            "open_after": outcome.after.open_question_count,
            "verified_closures": outcome.verified_closures,
            "ready_before": outcome.before.ready_mechanic_count,
            "ready_after": outcome.after.ready_mechanic_count,
            "selected_question_ids": list(outcome.selected_question_ids),
            "fetched_record_ids": list(outcome.fetched_record_ids),
            "verified_record_ids": list(outcome.application.verified_record_ids),
            "evidence_bound_record_ids": list(
                outcome.application.evidence_bound_record_ids
            ),
            "refused_record_ids": list(outcome.application.refused_record_ids),
            "guard_refusals": [list(item) for _, item in outcome.guard_refusal_reasons],
            "false_progress_reasons": list(outcome.false_progress_reasons),
        },
    )


def selected_question_set(questions: tuple[MechanicQuestion, ...]) -> tuple[str, ...]:
    return tuple(item.question_id for item in questions)
