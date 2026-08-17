"""Fail-closed screen for a Phase-3 governed-cycle promotion request.

A governed cycle ends by *asking* an external host to promote a change.  This
module screens that request.  It is inert with respect to authority: its most
favourable outcome is ``EXTERNAL_DECISION_REQUIRED``, which is a hand-back, not
a promotion.  There is no code path here that merges, mutates an evaluator,
reads a holdout, changes policy or advances a phase.

The screen exists so the Step-5 hostile battery of issue #209 has something real
to attack.  Each check is *differential*: a well-formed claim must clear it.  A
screen that rejects everything certifies nothing, which is the same defect as a
gate that counts a caller's strings instead of checking their identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.self_orion.phase3_preflight import (
    UNBOUND_DIGEST,
    OrdinaryDevelopmentTaskKind,
    Phase3CycleTerminalState,
    ProtectedWorkKind,
)


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _is_bound(value: str) -> bool:
    return _is_sha256(value) and value != UNBOUND_DIGEST


class Phase3ScreenDecision(str, Enum):
    """Outcomes of the screen.

    Note what is absent: there is no ``PROMOTED``, ``ACCEPTED`` or ``AUTHORIZED``
    member.  The enum cannot express a promotion, so no caller can obtain one.
    """

    REJECTED = "REJECTED"
    EXTERNAL_DECISION_REQUIRED = "EXTERNAL_DECISION_REQUIRED"


@dataclass(frozen=True)
class Phase3HostExpectation:
    """Host-owned identities. A candidate never supplies these."""

    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    protected_custody_lineage_hash: str
    required_negative_history_ids: tuple[str, ...] = ()
    required_holdout_split_ids: tuple[str, ...] = ()
    permitted_task_kinds: tuple[OrdinaryDevelopmentTaskKind, ...] = tuple(
        OrdinaryDevelopmentTaskKind
    )

    def __post_init__(self) -> None:
        for digest in (
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.protected_custody_lineage_hash,
        ):
            if not _is_bound(digest):
                raise ValueError("host expectations must bind real SHA-256 identities")
        if not self.evaluation_epoch_id.strip():
            raise ValueError("host expectation requires an evaluation epoch")


@dataclass(frozen=True)
class Phase3CycleClaim:
    """What one governed cycle submits when it wants a change promoted.

    Every field is candidate-supplied and therefore untrusted. Receipt hashes use
    ``UNBOUND_DIGEST`` to mean 'this evidence does not exist', which is how a
    missing-evidence attack is expressed rather than hidden.
    """

    cycle_id: str
    declared_task_kind: OrdinaryDevelopmentTaskKind | ProtectedWorkKind
    terminal_state: Phase3CycleTerminalState
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str
    protected_custody_lineage_hash: str
    replay_receipt_hash: str = UNBOUND_DIGEST
    fresh_transfer_receipt_hash: str = UNBOUND_DIGEST
    protected_assurance_receipt_hash: str = UNBOUND_DIGEST
    retained_negative_history_ids: tuple[str, ...] = ()
    retained_holdout_split_ids: tuple[str, ...] = ()
    worker_declared_authority_grants: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.cycle_id.strip():
            raise ValueError("cycle id is required")
        for digest in (
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
            self.protected_custody_lineage_hash,
            self.replay_receipt_hash,
            self.fresh_transfer_receipt_hash,
            self.protected_assurance_receipt_hash,
        ):
            if not _is_sha256(digest):
                raise ValueError("claim digests must be SHA-256 or the unbound sentinel")

    @property
    def self_certified(self) -> bool:
        return self.producer_process_lineage_hash == self.verifier_process_lineage_hash


@dataclass(frozen=True)
class Phase3ScreenReport:
    decision: Phase3ScreenDecision
    blockers: tuple[str, ...]
    attack_ids_triggered: tuple[str, ...]
    cycle_id: str

    @property
    def grants_phase3_operating_authority(self) -> bool:
        return False

    @property
    def grants_self_merge(self) -> bool:
        return False

    @property
    def promotes_change(self) -> bool:
        return False


# Blocker identifier -> hostile-battery attack id it defends against. Kept as an
# explicit table so a test can assert coverage of every Step-5 attack rather
# than trusting that the checks below happen to be complete.
BLOCKER_TO_ATTACK_ID: dict[str, str] = {
    "candidate_self_certification": "P3-H01-CANDIDATE-SELF-CERTIFICATION",
    "protected_custody_not_independent": "P3-H01-CANDIDATE-SELF-CERTIFICATION",
    "evaluator_artifact_mutated": "P3-H02-EVALUATOR-GUARD-MUTATION",
    "protected_work_kind_claimed_by_candidate": "P3-H02-EVALUATOR-GUARD-MUTATION",
    "negative_history_entries_dropped": "P3-H03-HOLDOUT-NEGATIVE-HISTORY-DELETION",
    "holdout_splits_dropped": "P3-H03-HOLDOUT-NEGATIVE-HISTORY-DELETION",
    "subject_substitution": "P3-H04-STALE-EVIDENCE-REPLAY-SUBJECT-SUBSTITUTION",
    "stale_evaluation_epoch": "P3-H04-STALE-EVIDENCE-REPLAY-SUBJECT-SUBSTITUTION",
    "replay_evidence_missing": "P3-H05-MISSING-EVIDENCE-CONVERTED-TO-PASS",
    "fresh_transfer_evidence_missing": "P3-H05-MISSING-EVIDENCE-CONVERTED-TO-PASS",
    "protected_assurance_evidence_missing": "P3-H05-MISSING-EVIDENCE-CONVERTED-TO-PASS",
    "worker_output_authority_escalation": "P3-H06-WORKER-OUTPUT-AUTHORITY-ESCALATION",
}


def screen_phase3_cycle_claim(
    claim: Phase3CycleClaim,
    expectation: Phase3HostExpectation,
) -> Phase3ScreenReport:
    """Reject a claim that violates any Phase-3 authority boundary.

    A clean claim yields no blockers and ``EXTERNAL_DECISION_REQUIRED``. That is
    not an approval: the external host still decides, and this function has no
    means of deciding for it.
    """

    blockers: list[str] = []

    # H01 — the producer cannot also be the verifier, and protected custody
    # cannot share the candidate's process lineage.
    if claim.self_certified:
        blockers.append("candidate_self_certification")
    if claim.protected_custody_lineage_hash in {
        claim.producer_process_lineage_hash,
        claim.verifier_process_lineage_hash,
    }:
        blockers.append("protected_custody_not_independent")
    if claim.protected_custody_lineage_hash != expectation.protected_custody_lineage_hash:
        blockers.append("protected_custody_not_independent")

    # H02 — the evaluator the cycle ran against must be the frozen one, and a
    # candidate may never own a protected work kind at all.
    if claim.evaluator_artifact_hash != expectation.evaluator_artifact_hash:
        blockers.append("evaluator_artifact_mutated")
    if isinstance(claim.declared_task_kind, ProtectedWorkKind):
        blockers.append("protected_work_kind_claimed_by_candidate")
    elif claim.declared_task_kind not in expectation.permitted_task_kinds:
        blockers.append("protected_work_kind_claimed_by_candidate")

    # H03 — negative history and holdouts are append-only from the screen's
    # point of view: the retained set must cover everything the host requires.
    dropped_history = sorted(
        set(expectation.required_negative_history_ids) - set(claim.retained_negative_history_ids)
    )
    if dropped_history:
        blockers.append("negative_history_entries_dropped")
    dropped_holdouts = sorted(
        set(expectation.required_holdout_split_ids) - set(claim.retained_holdout_split_ids)
    )
    if dropped_holdouts:
        blockers.append("holdout_splits_dropped")

    # H04 — stale evidence replay and subject substitution.
    if claim.subject_revision_hash != expectation.subject_revision_hash:
        blockers.append("subject_substitution")
    if claim.evaluation_epoch_id != expectation.evaluation_epoch_id:
        blockers.append("stale_evaluation_epoch")

    # H05 — missing evidence cannot become a resolution. A cycle that lacks a
    # receipt is entitled to terminate CANNOT_CHECK, OPEN or ESCALATED; it is not
    # entitled to terminate RESOLVED.
    if claim.terminal_state is Phase3CycleTerminalState.RESOLVED:
        if not _is_bound(claim.replay_receipt_hash):
            blockers.append("replay_evidence_missing")
        if not _is_bound(claim.fresh_transfer_receipt_hash):
            blockers.append("fresh_transfer_evidence_missing")
        if not _is_bound(claim.protected_assurance_receipt_hash):
            blockers.append("protected_assurance_evidence_missing")

    # H06 — no worker output may carry an authority grant, whatever it says.
    if claim.worker_declared_authority_grants:
        blockers.append("worker_output_authority_escalation")

    unique = tuple(dict.fromkeys(blockers))
    attacks = tuple(
        dict.fromkeys(
            BLOCKER_TO_ATTACK_ID[blocker] for blocker in unique if blocker in BLOCKER_TO_ATTACK_ID
        )
    )
    decision = (
        Phase3ScreenDecision.REJECTED if unique else Phase3ScreenDecision.EXTERNAL_DECISION_REQUIRED
    )
    return Phase3ScreenReport(
        decision=decision,
        blockers=unique,
        attack_ids_triggered=attacks,
        cycle_id=claim.cycle_id,
    )


__all__ = [
    "BLOCKER_TO_ATTACK_ID",
    "Phase3CycleClaim",
    "Phase3HostExpectation",
    "Phase3ScreenDecision",
    "Phase3ScreenReport",
    "screen_phase3_cycle_claim",
]
