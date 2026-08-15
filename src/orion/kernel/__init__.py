"""Self-driving kernel: the governed loop that lets ORION answer its own audit.

The mechanics substrate can already decompose ORION into cells, expose every
unfilled dimension as a typed question and turn questions into research tasks.
What it could not do was hold an answer. This package closes that edge under
explicit governance:

    audit -> select (guard-aware) -> fetch answers -> grade -> apply what passed
          -> re-audit -> false-progress check -> persist -> learn -> repeat

Two rules keep the loop from certifying itself. Evidence must resolve to a real
artifact at a pinned digest, and a machine's own answer stops at
`EVIDENCE_BOUND`, which applies content but leaves the dimension provisional so
the question stays open. Only an independently laned discriminating check,
frozen before the round it judges, reaches `VERIFIED` and closes anything.
"""

from .apply import GradedApplication, grade_and_apply
from .driver import RunReport, SelfDrivingDriver, learn_guards, replay_cells
from .evidence import EvidenceResolution, EvidenceStatus, resolve_evidence_ref
from .gate import (
    AnswerAuthority,
    AnswerGrading,
    CheckOutcome,
    DiscriminatingCheck,
    grade_answer,
    run_discriminating_check,
)
from .guards import GuardEffect, GuardRule, apply_selection_guards, derive_guard_rule
from .round import RoundOutcome, run_round
from .sources import DirectoryAnswerSource, StaticAnswerSource
from .store import EntryKind, LedgerEntry, LedgerIntegrityError, LedgerStore

__all__ = [
    "AnswerAuthority",
    "AnswerGrading",
    "CheckOutcome",
    "DirectoryAnswerSource",
    "DiscriminatingCheck",
    "EntryKind",
    "EvidenceResolution",
    "EvidenceStatus",
    "GradedApplication",
    "GuardEffect",
    "GuardRule",
    "LedgerEntry",
    "LedgerIntegrityError",
    "LedgerStore",
    "RoundOutcome",
    "RunReport",
    "SelfDrivingDriver",
    "StaticAnswerSource",
    "apply_selection_guards",
    "derive_guard_rule",
    "grade_and_apply",
    "grade_answer",
    "learn_guards",
    "replay_cells",
    "resolve_evidence_ref",
    "run_discriminating_check",
    "run_round",
]
