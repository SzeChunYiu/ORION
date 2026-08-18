"""Evidence-bound objective revision process. Candidate cannot self-author reward."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .protocol import PROTOCOL_ID, load_protocol
from .revision import (
    AuthorityProvenance,
    ObjectiveRevisionArchive,
    ObjectiveRevisionRecord,
    ObjectiveRevisionStatus,
    ObjectiveVersion,
    PROPOSAL_LEGAL_RESPONSIBILITIES,
    ResponsibilityClass,
    RevisionStatusEvent,
    append_status_event,
    append_version,
    empty_archive,
    register_revision,
)

_HOST = AuthorityProvenance(
    actor_id="host:goal-evolution",
    role="HOST",
    artifact_hash="a" * 64,
)
_POOR_SCORE_MARKERS = frozenset(
    {
        "candidate_score_poor",
        "score is poor",
        "poor_score_under_old_objective",
    }
)
_IMPLEMENTATION_SUCCESS_MARKERS = (
    "known-good implementation restores the score",
    "known-good implementation restores validity under the same objective",
)


class ProcessStage(str, Enum):
    OBSERVE = "OBSERVE"
    DIAGNOSE = "DIAGNOSE"
    DISCRIMINATE = "DISCRIMINATE"
    PROPOSE_OBJECTIVE_REVISION = "PROPOSE_OBJECTIVE_REVISION"
    FREEZE = "FREEZE"
    OPTIMIZE = "OPTIMIZE"
    PROTECTED_COMPARE = "PROTECTED_COMPARE"
    ADMIT_OR_REJECT = "ADMIT_OR_REJECT"


class ProcessRefusal(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(code if not detail else f"{code}: {detail}")


@dataclass(frozen=True)
class ProtectedCompareResult:
    status: str
    old_objective_score: float | None = None
    new_objective_score: float | None = None
    protected_intent_score: float | None = None


@dataclass(frozen=True)
class GoalEvolutionSession:
    protocol_id: str
    stage: ProcessStage
    archive: ObjectiveRevisionArchive
    evaluator_hash: str
    scientific_intent_ref: str
    constraints: tuple[str, ...]
    observations: tuple[str, ...] = ()
    hypotheses: tuple[ResponsibilityClass, ...] = ()
    assigned_responsibility: ResponsibilityClass | None = None
    discriminator_hash: str = ""
    revision_id: str = ""
    revision_cycles: int = 0
    optimizer_receipt_hash: str = ""
    scientific_terminal: str = "CANNOT_CHECK"
    freeze_hash: str = ""
    accessed_protected_intent: bool = False

    @property
    def current_operational_version_id(self) -> str:
        return self.archive.current_operational_version_id

    def claim_terminal(self, terminal: str) -> None:
        raise ProcessRefusal(
            "cannot_claim_supported_without_protected_intent_evidence",
            terminal,
        )

    def candidate_mutate(self, surface: str, new_value: str) -> None:
        del new_value
        raise ProcessRefusal("candidate_mutated_protected_surface", surface)

    def reopen_for_next_cycle(self) -> GoalEvolutionSession:
        _require_stage(self, ProcessStage.PROTECTED_COMPARE)
        return replace(
            self,
            stage=ProcessStage.OBSERVE,
            observations=(),
            hypotheses=(),
            assigned_responsibility=None,
            discriminator_hash="",
            revision_id="",
            optimizer_receipt_hash="",
            freeze_hash="",
            accessed_protected_intent=False,
        )


def _require_stage(session: GoalEvolutionSession, expected: ProcessStage) -> None:
    if session.stage is not expected:
        raise ProcessRefusal(
            "stage_out_of_order",
            f"expected {expected.value}, found {session.stage.value}",
        )


def _max_revision_cycles() -> int:
    return int(load_protocol()["max_revision_cycles"])


def start_session(
    *,
    operational_objective_id: str,
    operational_definition: str,
    operational_code_hash: str,
    constraints: tuple[str, ...],
    evaluator_hash: str,
    scientific_intent_ref: str,
) -> GoalEvolutionSession:
    version = ObjectiveVersion(
        version_id=operational_objective_id,
        definition=operational_definition,
        code_hash=operational_code_hash,
        constraints=constraints,
        proxy_assumptions=(),
    )
    return GoalEvolutionSession(
        protocol_id=PROTOCOL_ID,
        stage=ProcessStage.OBSERVE,
        archive=append_version(empty_archive(), version),
        evaluator_hash=evaluator_hash,
        scientific_intent_ref=scientific_intent_ref,
        constraints=constraints,
    )


def observe(session: GoalEvolutionSession, observations: tuple[str, ...]) -> GoalEvolutionSession:
    _require_stage(session, ProcessStage.OBSERVE)
    if not observations:
        raise ProcessRefusal("stage_out_of_order", "observations are required")
    return replace(session, stage=ProcessStage.DIAGNOSE, observations=tuple(observations))


def diagnose(
    session: GoalEvolutionSession, hypotheses: tuple[ResponsibilityClass, ...]
) -> GoalEvolutionSession:
    _require_stage(session, ProcessStage.DIAGNOSE)
    if len(set(hypotheses)) < 2:
        raise ProcessRefusal("unresolved_responsibility", "competing hypotheses are required")
    return replace(session, stage=ProcessStage.DISCRIMINATE, hypotheses=tuple(hypotheses))


def discriminate(
    session: GoalEvolutionSession,
    *,
    assigned_responsibility: ResponsibilityClass,
    evidence_ids: tuple[str, ...],
    predicted_if_objective: str,
    predicted_if_implementation: str,
    observed: str,
    discriminator_hash: str,
    accessed_protected_intent: bool,
) -> GoalEvolutionSession:
    _require_stage(session, ProcessStage.DISCRIMINATE)
    del predicted_if_objective, predicted_if_implementation
    if accessed_protected_intent:
        raise ProcessRefusal("protected_metric_accessed")
    if observed in _POOR_SCORE_MARKERS or set(evidence_ids) <= {"score:poor"}:
        raise ProcessRefusal("poor_score_insufficient_for_proposal")
    if assigned_responsibility in PROPOSAL_LEGAL_RESPONSIBILITIES and any(
        marker in observed for marker in _IMPLEMENTATION_SUCCESS_MARKERS
    ):
        raise ProcessRefusal("implementation_failure_not_objective_misspecification")
    return replace(
        session,
        stage=ProcessStage.PROPOSE_OBJECTIVE_REVISION,
        assigned_responsibility=assigned_responsibility,
        discriminator_hash=discriminator_hash,
        accessed_protected_intent=accessed_protected_intent,
    )


def propose_objective_revision(
    session: GoalEvolutionSession,
    *,
    new_version_id: str,
    new_definition: str,
    new_code_hash: str,
    mapping: tuple[tuple[str, str], ...],
    predicted_tradeoffs: tuple[str, ...],
    evaluator_hash: str,
    rewards_output_hash: str | None,
    dropped_constraints: tuple[str, ...],
    accessed_protected_metric: bool,
    claims_global_positive: bool,
    changes_denominator: bool,
    current_candidate_output_hash: str | None = None,
    redefine_after_protected_negative: bool = False,
) -> GoalEvolutionSession:
    _require_stage(session, ProcessStage.PROPOSE_OBJECTIVE_REVISION)
    if session.revision_cycles >= _max_revision_cycles():
        raise ProcessRefusal("revision_cycle_bound_exceeded")
    if session.assigned_responsibility not in PROPOSAL_LEGAL_RESPONSIBILITIES:
        raise ProcessRefusal("responsibility_not_objective_or_measurement")
    if accessed_protected_metric or session.accessed_protected_intent:
        raise ProcessRefusal("protected_metric_accessed")
    if redefine_after_protected_negative:
        raise ProcessRefusal("redefining_success_after_negative")
    if claims_global_positive:
        raise ProcessRefusal("global_positive_self_definition")
    if evaluator_hash != session.evaluator_hash:
        raise ProcessRefusal("simultaneous_objective_evaluator_change")
    if dropped_constraints:
        raise ProcessRefusal("dropped_protected_constraint")
    if changes_denominator:
        raise ProcessRefusal("change_denominator_or_exclusion")
    if rewards_output_hash and rewards_output_hash == current_candidate_output_hash:
        raise ProcessRefusal("candidate_rewrite_to_self_reward")
    if "reward the current candidate output exactly" in new_definition:
        raise ProcessRefusal("candidate_rewrite_to_self_reward")

    new_version = ObjectiveVersion(
        version_id=new_version_id,
        definition=new_definition,
        code_hash=new_code_hash,
        constraints=session.constraints,
        proxy_assumptions=(),
    )
    archive = append_version(session.archive, new_version)
    revision_id = f"rev:{len(archive.records) + 1}"
    record = ObjectiveRevisionRecord(
        revision_id=revision_id,
        old_version_id=session.current_operational_version_id,
        new_version_id=new_version_id,
        mapping=tuple(mapping),
        scientific_intent_ref=session.scientific_intent_ref,
        failure_observations=session.observations,
        competing_responsibility_hypotheses=tuple(
            item.value for item in session.hypotheses
        ),
        frozen_discriminator_hash=session.discriminator_hash,
        predicted_tradeoffs=tuple(predicted_tradeoffs),
        unchanged_protected_constraints=session.constraints,
        authority_provenance=_HOST,
    )
    archive = register_revision(archive, record)
    return replace(
        session,
        stage=ProcessStage.FREEZE,
        archive=archive,
        revision_id=revision_id,
        revision_cycles=session.revision_cycles + 1,
    )


def freeze_revision(session: GoalEvolutionSession) -> GoalEvolutionSession:
    _require_stage(session, ProcessStage.FREEZE)
    archive = append_status_event(
        session.archive,
        RevisionStatusEvent(
            event_id=f"status:{session.revision_id}:admitted",
            revision_id=session.revision_id,
            status=ObjectiveRevisionStatus.ADMITTED_FOR_TEST,
            authority_provenance=_HOST,
            reason="frozen for prospective test before protected outcomes",
        ),
    )
    return replace(
        session,
        stage=ProcessStage.OPTIMIZE,
        archive=archive,
        freeze_hash=session.discriminator_hash,
    )


def optimize(session: GoalEvolutionSession, *, optimizer_receipt_hash: str) -> GoalEvolutionSession:
    _require_stage(session, ProcessStage.OPTIMIZE)
    return replace(
        session,
        stage=ProcessStage.PROTECTED_COMPARE,
        optimizer_receipt_hash=optimizer_receipt_hash,
    )


def protected_compare(session: GoalEvolutionSession) -> ProtectedCompareResult:
    _require_stage(session, ProcessStage.PROTECTED_COMPARE)
    del session
    return ProtectedCompareResult(status="CANNOT_CHECK")


def admit_or_reject(
    session: GoalEvolutionSession, compare: ProtectedCompareResult
) -> GoalEvolutionSession:
    _require_stage(session, ProcessStage.PROTECTED_COMPARE)
    if compare.status == "CANNOT_CHECK":
        return replace(
            session,
            stage=ProcessStage.ADMIT_OR_REJECT,
            scientific_terminal="CANNOT_CHECK",
        )
    raise ProcessRefusal("cannot_claim_supported_without_protected_intent_evidence")
