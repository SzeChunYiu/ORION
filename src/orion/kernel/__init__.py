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
the question stays open. Raw discriminating checks remain diagnostics; verified
closure requires the separate protected transition lifecycle.
"""

from .apply import GradedApplication, grade_and_apply
from .driver import RunReport, SelfDrivingDriver, learn_guards, replay_cells
from .evidence import (
    EvidenceResolution,
    EvidenceRoleBinding,
    EvidenceStatus,
    HostEvidenceManifest,
    HostEvidenceRecord,
    HostEvidenceSnapshot,
    HostEvidenceSource,
    capture_host_evidence_snapshot,
    resolve_evidence_ref,
    snapshot_hash,
)
from .battery import battery_order, host_battery
from .gate import (
    AnswerAuthority,
    AnswerGrading,
    CheckOutcome,
    DiscriminatingCheck,
    discrimination_order,
    grade_answer,
    run_discriminating_check,
)
from .guards import GuardEffect, GuardRule, apply_selection_guards, derive_guard_rule
from .round import RoundOutcome, run_round
from .sources import DirectoryAnswerSource, StaticAnswerSource
from .store import EntryKind, LedgerEntry, LedgerIntegrityError, LedgerStore
from .transition import (
    CANONICALIZATION_VERSION,
    MAX_CANONICAL_BYTES,
    MAX_CANONICAL_DEPTH,
    MAX_CANONICAL_NODES,
    PROJECTION_SCHEMA_VERSION,
    REDUCER_VERSION,
    UNICODE_DATABASE_VERSION,
    UNICODE_POLICY,
    WORKFLOW_VERSION,
    CanonicalizationError,
    LedgerExpectation,
    ProgramProjection,
    TransitionKind,
    answer_record_hash,
    canonical_answer_record,
    canonical_digest,
    canonical_json_bytes,
    canonical_json_loads,
    canonical_mechanic_cell,
    projection_hash,
)

__all__ = [
    "AnswerAuthority",
    "AnswerGrading",
    "CheckOutcome",
    "DirectoryAnswerSource",
    "DiscriminatingCheck",
    "EntryKind",
    "EvidenceResolution",
    "EvidenceRoleBinding",
    "EvidenceStatus",
    "HostEvidenceManifest",
    "HostEvidenceRecord",
    "HostEvidenceSnapshot",
    "HostEvidenceSource",
    "GradedApplication",
    "GuardEffect",
    "GuardRule",
    "LedgerEntry",
    "LedgerIntegrityError",
    "LedgerStore",
    "LedgerExpectation",
    "ProgramProjection",
    "CanonicalizationError",
    "CANONICALIZATION_VERSION",
    "MAX_CANONICAL_BYTES",
    "MAX_CANONICAL_DEPTH",
    "MAX_CANONICAL_NODES",
    "PROJECTION_SCHEMA_VERSION",
    "REDUCER_VERSION",
    "UNICODE_DATABASE_VERSION",
    "UNICODE_POLICY",
    "WORKFLOW_VERSION",
    "TransitionKind",
    "RoundOutcome",
    "RunReport",
    "SelfDrivingDriver",
    "StaticAnswerSource",
    "apply_selection_guards",
    "answer_record_hash",
    "battery_order",
    "canonical_answer_record",
    "canonical_digest",
    "canonical_json_bytes",
    "canonical_json_loads",
    "canonical_mechanic_cell",
    "capture_host_evidence_snapshot",
    "discrimination_order",
    "host_battery",
    "derive_guard_rule",
    "grade_and_apply",
    "grade_answer",
    "learn_guards",
    "replay_cells",
    "resolve_evidence_ref",
    "projection_hash",
    "run_discriminating_check",
    "run_round",
    "snapshot_hash",
]
