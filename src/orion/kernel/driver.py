from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from orion.experience.model import EpisodeOutcome, LessonAuthority, TaskEpisode
from orion.experience.learning import propose_failure_pattern
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.program import current_program_cells

from .apply import grade_and_apply
from .gate import DiscriminatingCheck
from .guards import GuardRule, derive_guard_rule
from .round import AnswerSource, RoundOutcome, run_round
from .store import EntryKind, LedgerStore

_FAILURE_OUTCOMES = {
    EpisodeOutcome.FAILURE,
    EpisodeOutcome.PARTIAL_SUCCESS,
    EpisodeOutcome.BLOCKED,
    EpisodeOutcome.CANNOT_CHECK,
}


@dataclass(frozen=True)
class RunReport:
    """The outcome of a bounded self-driving run."""

    rounds: tuple[RoundOutcome, ...]
    guards: tuple[GuardRule, ...]
    stop_reason: str
    open_at_start: int
    open_at_end: int

    @property
    def verified_closures(self) -> int:
        return self.open_at_start - self.open_at_end


def _record_from_payload(payload: Mapping[str, object]) -> AnswerRecord | None:
    try:
        return AnswerRecord(
            record_id=str(payload["record_id"]),
            mechanic_id=str(payload["mechanic_id"]),
            dimension=MechanicDimension(str(payload["dimension"])),
            lane=str(payload["lane"]),
            evidence_refs=tuple(payload.get("evidence_refs", ()) or ()),  # type: ignore[arg-type]
            payload=tuple(
                (str(name), tuple(values))
                for name, values in (payload.get("payload", ()) or ())  # type: ignore[union-attr]
            ),
            waiver_reason=str(payload.get("waiver_reason", "") or ""),
            supersedes=str(payload.get("supersedes", "") or ""),
        )
    except (KeyError, ValueError):
        return None


def replay_cells(
    store: LedgerStore,
    *,
    seed_cells: tuple[MechanicCell, ...],
    evidence_roots: Mapping[str, Path],
    checks: Mapping[str, DiscriminatingCheck] = {},
    require_digest: bool = True,
) -> tuple[MechanicCell, ...]:
    """Rebuild current cells by re-grading the whole persisted answer history.

    Resume re-validates rather than trusts: evidence is resolved again, so an
    answer whose cited artifact has since changed loses its authority instead
    of silently surviving as closed work.
    """

    cells = seed_cells
    entries = store.entries(EntryKind.ANSWER)
    by_round: dict[int, list[AnswerRecord]] = {}
    for entry in entries:
        record = _record_from_payload(entry.payload)
        if record is None:
            continue
        by_round.setdefault(int(entry.payload.get("round_index", 0)), []).append(record)
    for round_index in sorted(by_round):
        result = grade_and_apply(
            cells,
            tuple(by_round[round_index]),
            evidence_roots=evidence_roots,
            checks=checks,
            require_digest=require_digest,
            round_index=round_index,
        )
        cells = result.cells
    return cells


def _episodes_from_ledger(store: LedgerStore) -> tuple[TaskEpisode, ...]:
    episodes: list[TaskEpisode] = []
    for entry in store.entries(EntryKind.EPISODE):
        payload = entry.payload
        try:
            episodes.append(
                TaskEpisode(
                    episode_id=str(payload["episode_id"]),
                    task_id=str(payload["task_id"]),
                    run_id=str(payload["run_id"]),
                    parent_run_id=None,
                    evaluation_epoch_id=str(payload["evaluation_epoch_id"]),
                    split_id=str(payload["split_id"]),
                    mechanic_id=str(payload["mechanic_id"]),
                    problem_signature=tuple(payload.get("problem_signature", ())),  # type: ignore[arg-type]
                    variation_signature=tuple(payload.get("variation_signature", ())),  # type: ignore[arg-type]
                    pre_state_hash=str(payload["pre_state_hash"]),
                    action_ids=tuple(payload.get("action_ids", ())),  # type: ignore[arg-type]
                    observation_ids=tuple(payload.get("observation_ids", ())),  # type: ignore[arg-type]
                    outcome=EpisodeOutcome(str(payload["outcome"])),
                    failure_signature=tuple(payload.get("failure_signature", ())),  # type: ignore[arg-type]
                    residual_ids=(),
                    evidence_ids=tuple(payload.get("evidence_ids", ())),  # type: ignore[arg-type]
                    evidence_bindings=tuple(
                        (str(item[0]), str(item[1]))
                        for item in payload.get("evidence_bindings", ())  # type: ignore[union-attr]
                    ),
                    post_state_hash=str(payload["post_state_hash"]),
                    timestamp=str(payload["timestamp"]),
                )
            )
        except (KeyError, ValueError):
            continue
    return tuple(episodes)


def learn_guards(store: LedgerStore) -> tuple[GuardRule, ...]:
    """Derive executable guards from repeated, structurally identical failures.

    A pattern seen inside a single round is a candidate only. It becomes active
    when the same core failure signature recurs in a later, distinct round —
    the cheapest honest replay criterion available without a second run.
    """

    episodes = _episodes_from_ledger(store)
    failures = tuple(item for item in episodes if item.outcome in _FAILURE_OUTCOMES)
    # `propose_failure_pattern` requires every supporting episode to come from a
    # distinct run, so repeated attempts inside one round cannot inflate the
    # evidence for a pattern. Keep one representative failure per run.
    by_mechanic: dict[str, list[TaskEpisode]] = {}
    seen_runs: set[tuple[str, str]] = set()
    for episode in sorted(failures, key=lambda item: item.episode_id):
        key = (episode.mechanic_id, episode.parent_run_id or episode.run_id)
        if key in seen_runs:
            continue
        seen_runs.add(key)
        by_mechanic.setdefault(episode.mechanic_id, []).append(episode)

    rounds_by_signature: dict[tuple[str, ...], set[str]] = {}
    for episode in failures:
        rounds_by_signature.setdefault(episode.failure_signature, set()).add(
            episode.split_id
        )

    guards: dict[str, GuardRule] = {}
    for mechanic_id, group in sorted(by_mechanic.items()):
        pattern_id = f"pattern:{mechanic_id}"
        candidate = propose_failure_pattern(
            tuple(group),
            pattern_id=pattern_id,
            candidate_guard=f"withhold unverifiable answers for {mechanic_id}",
            falsifier=(
                "an answer with this core signature is later verified by an "
                "independent discriminating check"
            ),
        )
        if candidate is None:
            continue
        observed_rounds = rounds_by_signature.get(candidate.core_failure_signature, set())
        authority = (
            LessonAuthority.VERIFIED_LOCAL
            if len(observed_rounds) >= 2
            else LessonAuthority.CANDIDATE
        )
        rule = derive_guard_rule(candidate, authority=authority)
        if rule is not None:
            guards[rule.guard_id] = rule
    return tuple(guards[key] for key in sorted(guards))


@dataclass
class SelfDrivingDriver:
    """Run bounded self-driving rounds against a durable ledger."""

    store: LedgerStore
    source: AnswerSource
    evidence_roots: Mapping[str, Path]
    checks: Mapping[str, DiscriminatingCheck] = field(default_factory=dict)
    seed_cells: tuple[MechanicCell, ...] | None = None
    run_id: str = "orion"
    selection_limit: int = 16
    require_digest: bool = True
    flat_rounds_to_stop: int = 2

    def cells(self) -> tuple[MechanicCell, ...]:
        seed = self.seed_cells if self.seed_cells is not None else current_program_cells()
        return replay_cells(
            self.store,
            seed_cells=seed,
            evidence_roots=self.evidence_roots,
            checks=self.checks,
            require_digest=self.require_digest,
        )

    def run(self, *, max_rounds: int = 4) -> RunReport:
        """Execute rounds until saturation, budget exhaustion or a stop condition."""

        if max_rounds < 1:
            raise ValueError("max_rounds must be positive")
        cells = self.cells()
        guards = learn_guards(self.store)
        open_at_start = None
        outcomes: list[RoundOutcome] = []
        flat_streak = 0
        stop_reason = "max_rounds_reached"
        start_index = self.store.completed_round_count()

        for offset in range(max_rounds):
            round_index = start_index + offset
            outcome = run_round(
                cells,
                store=self.store,
                source=self.source,
                evidence_roots=self.evidence_roots,
                checks=self.checks,
                guards=guards,
                run_id=self.run_id,
                round_index=round_index,
                selection_limit=self.selection_limit,
                timestamp=f"round-{round_index}",
                require_digest=self.require_digest,
            )
            if open_at_start is None:
                open_at_start = outcome.before.open_question_count
            outcomes.append(outcome)
            cells = outcome.cells

            fresh = learn_guards(self.store)
            if {item.guard_id for item in fresh} != {item.guard_id for item in guards}:
                for rule in fresh:
                    self.store.append(
                        EntryKind.GUARD,
                        {
                            "guard_id": rule.guard_id,
                            "pattern_id": rule.pattern_id,
                            "effect": rule.effect.value,
                            "argument": rule.argument,
                            "authority": rule.authority.value,
                            "rationale": rule.rationale,
                            "round_index": round_index,
                        },
                    )
            guards = fresh

            if outcome.false_progress_reasons:
                stop_reason = "false_progress_detected"
                break
            if outcome.productive:
                flat_streak = 0
                continue
            flat_streak += 1
            if flat_streak >= self.flat_rounds_to_stop:
                stop_reason = "bounded_flatness"
                break

        final_open = (
            outcomes[-1].after.open_question_count
            if outcomes
            else (open_at_start or 0)
        )
        return RunReport(
            rounds=tuple(outcomes),
            guards=guards,
            stop_reason=stop_reason,
            open_at_start=open_at_start or 0,
            open_at_end=final_open,
        )
