"""Evidence-bounded recursive paper-refinement controller.

This module turns the Q-series publication protocol into typed records. It is not
an acceptance predictor, reviewer simulator, or scientific authority. External
writing/reviewer skills produce inputs to this controller; the controller only
checks scope, blocker closure, target readiness and recursive stopping rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from .protocol import content_digest

PAPER_REFINEMENT_STATE_SCHEMA = "ORION.PaperRefinementState.v1"
PAPER_REVIEW_RECEIPT_SCHEMA = "ORION.PaperReviewReceipt.v1"
PAPER_CONCERN_SCHEMA = "ORION.PaperConcern.v1"

QUALITY_DIMENSIONS = (
    "problem_and_question",
    "contribution_clarity",
    "claim_evidence_alignment",
    "technical_rigor",
    "novelty_positioning",
    "significance_or_field_advance",
    "generality_and_boundaries",
    "reproducibility_and_availability",
    "figure_data_statistics_quality",
    "writing_and_evaluability",
    "venue_fit",
)

REVIEW_ROLES = (
    "VALIDITY",
    "POSITIONING",
    "REPRO_BOUNDARY",
)


class ConcernClass(str, Enum):
    PUBLICATION_CRITERIA_BLOCKER = "PUBLICATION_CRITERIA_BLOCKER"
    TECHNICAL_BLOCKER = "TECHNICAL_BLOCKER"
    MAJOR_REPAIRABLE = "MAJOR_REPAIRABLE"
    CLAIM_RECALIBRATION = "CLAIM_RECALIBRATION"
    CLARITY_OR_REPORTING = "CLARITY_OR_REPORTING"
    OPTIONAL_ENRICHMENT = "OPTIONAL_ENRICHMENT"

    @property
    def blocks(self) -> bool:
        return self in {
            ConcernClass.PUBLICATION_CRITERIA_BLOCKER,
            ConcernClass.TECHNICAL_BLOCKER,
        }


class RepairRoute(str, Enum):
    ADD_DECISIVE_EVIDENCE = "ADD_DECISIVE_EVIDENCE"
    REANALYSE_EXISTING_EVIDENCE = "REANALYSE_EXISTING_EVIDENCE"
    CORRECT_ERROR = "CORRECT_ERROR"
    CLARIFY_OR_RESTRUCTURE = "CLARIFY_OR_RESTRUCTURE"
    NARROW_CLAIM = "NARROW_CLAIM"
    REMOVE_CLAIM = "REMOVE_CLAIM"
    CHANGE_TARGET_OR_ARTICLE_TYPE = "CHANGE_TARGET_OR_ARTICLE_TYPE"


class ConcernClosure(str, Enum):
    OPEN = "OPEN"
    RESOLVED_BY_EVIDENCE = "RESOLVED_BY_EVIDENCE"
    RESOLVED_BY_ANALYSIS = "RESOLVED_BY_ANALYSIS"
    RESOLVED_BY_CORRECTION = "RESOLVED_BY_CORRECTION"
    RESOLVED_BY_CLARIFICATION = "RESOLVED_BY_CLARIFICATION"
    RESOLVED_BY_CLAIM_NARROWING = "RESOLVED_BY_CLAIM_NARROWING"
    RESOLVED_BY_CLAIM_REMOVAL = "RESOLVED_BY_CLAIM_REMOVAL"
    RESOLVED_BY_TARGET_CHANGE = "RESOLVED_BY_TARGET_CHANGE"

    @property
    def resolved(self) -> bool:
        return self is not ConcernClosure.OPEN


class RefinementTerminal(str, Enum):
    CONTINUE_REFINEMENT = "CONTINUE_REFINEMENT"
    READY_FOR_SCOPED_TARGET = "READY_FOR_SCOPED_TARGET"
    READY_FOR_FALLBACK = "READY_FOR_FALLBACK"
    EVIDENCE_BLOCKED = "EVIDENCE_BLOCKED"
    TRANSFER_RECOMMENDED = "TRANSFER_RECOMMENDED"
    PLATEAU_STOP = "PLATEAU_STOP"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class PaperConcern:
    concern_id: str
    reviewer_role: str
    concern_class: ConcernClass
    criterion: str
    claim_pointer: str
    evidence_pointer: str
    concern: str
    resolution_test: str
    repair_route: RepairRoute
    closure: ConcernClosure = ConcernClosure.OPEN
    schema: str = PAPER_CONCERN_SCHEMA

    def validate(self) -> None:
        if self.schema != PAPER_CONCERN_SCHEMA:
            raise ValueError("unsupported paper concern schema")
        if not self.concern_id.strip():
            raise ValueError("paper concern requires concern_id")
        if self.reviewer_role not in REVIEW_ROLES:
            raise ValueError(f"unsupported reviewer role: {self.reviewer_role}")
        for name, value in (
            ("criterion", self.criterion),
            ("claim_pointer", self.claim_pointer),
            ("evidence_pointer", self.evidence_pointer),
            ("concern", self.concern),
            ("resolution_test", self.resolution_test),
        ):
            if not value.strip():
                raise ValueError(f"paper concern {self.concern_id} requires {name}")

    @property
    def open_blocker(self) -> bool:
        return self.concern_class.blocks and not self.closure.resolved

    @property
    def evidence_blocker(self) -> bool:
        return self.open_blocker and self.repair_route is RepairRoute.ADD_DECISIVE_EVIDENCE

    @property
    def target_blocker(self) -> bool:
        return self.open_blocker and self.repair_route is RepairRoute.CHANGE_TARGET_OR_ARTICLE_TYPE

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema": self.schema,
            "concern_id": self.concern_id,
            "reviewer_role": self.reviewer_role,
            "concern_class": self.concern_class.value,
            "criterion": self.criterion,
            "claim_pointer": self.claim_pointer,
            "evidence_pointer": self.evidence_pointer,
            "concern": self.concern,
            "resolution_test": self.resolution_test,
            "repair_route": self.repair_route.value,
            "closure": self.closure.value,
        }


@dataclass(frozen=True)
class PaperReviewReceipt:
    paper_id: str
    round_index: int
    manuscript_digest: str
    reviewer_role: str
    context_id: str
    target_profile: str
    concerns: tuple[PaperConcern, ...]
    mutual_blindness_guaranteed: bool
    receipt_digest: str
    schema: str = PAPER_REVIEW_RECEIPT_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "paper_id": self.paper_id,
            "round_index": self.round_index,
            "manuscript_digest": self.manuscript_digest,
            "reviewer_role": self.reviewer_role,
            "context_id": self.context_id,
            "target_profile": self.target_profile,
            "concerns": [item.as_dict() for item in self.concerns],
            "mutual_blindness_guaranteed": self.mutual_blindness_guaranteed,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "predicts_acceptance": False,
        }

    def validate(self) -> None:
        if self.schema != PAPER_REVIEW_RECEIPT_SCHEMA:
            raise ValueError("unsupported paper review receipt schema")
        if self.reviewer_role not in REVIEW_ROLES:
            raise ValueError(f"unsupported reviewer role: {self.reviewer_role}")
        if self.round_index < 0:
            raise ValueError("review round cannot be negative")
        for name, value in (
            ("paper_id", self.paper_id),
            ("manuscript_digest", self.manuscript_digest),
            ("context_id", self.context_id),
            ("target_profile", self.target_profile),
            ("receipt_digest", self.receipt_digest),
        ):
            if not value.strip():
                raise ValueError(f"paper review receipt requires {name}")
        if len(self.concerns) != len({item.concern_id for item in self.concerns}):
            raise ValueError("duplicate concern id inside review receipt")
        for item in self.concerns:
            item.validate()
            if item.reviewer_role != self.reviewer_role:
                raise ValueError("concern reviewer role does not match review receipt")
        if self.receipt_digest != content_digest(self.unsigned()):
            raise ValueError("paper review receipt digest mismatch")

    @classmethod
    def create(
        cls,
        *,
        paper_id: str,
        round_index: int,
        manuscript_digest: str,
        reviewer_role: str,
        context_id: str,
        target_profile: str,
        concerns: Sequence[PaperConcern] = (),
        mutual_blindness_guaranteed: bool = False,
    ) -> "PaperReviewReceipt":
        base = cls(
            paper_id=paper_id,
            round_index=round_index,
            manuscript_digest=manuscript_digest,
            reviewer_role=reviewer_role,
            context_id=context_id,
            target_profile=target_profile,
            concerns=tuple(concerns),
            mutual_blindness_guaranteed=mutual_blindness_guaranteed,
            receipt_digest="",
        )
        receipt = cls(**{**base.__dict__, "receipt_digest": content_digest(base.unsigned())})
        receipt.validate()
        return receipt


@dataclass(frozen=True)
class VenueReadinessProfile:
    profile_id: str
    hard_gates: tuple[str, ...]
    dimension_floor: float
    mean_floor: float
    requires_exceptionality_axis: bool = False

    def validate(self) -> None:
        if not self.profile_id.strip():
            raise ValueError("venue profile requires id")
        if not self.hard_gates:
            raise ValueError("venue profile requires hard gates")
        if not 0 <= self.dimension_floor <= 10 or not 0 <= self.mean_floor <= 10:
            raise ValueError("venue readiness thresholds must lie in [0, 10]")


@dataclass(frozen=True)
class PaperRefinementState:
    paper_id: str
    round_index: int
    manuscript_path: str
    manuscript_digest: str
    target_profile: str
    fallback_profile: str
    question: str
    answer: str
    evidence_chain: tuple[str, ...]
    boundary: str
    meaning: str
    dimension_scores: tuple[tuple[str, float], ...]
    hard_gate_status: tuple[tuple[str, bool], ...]
    exceptionality_axes_passed: tuple[str, ...]
    review_receipts: tuple[PaperReviewReceipt, ...]
    prior_round_means: tuple[float, ...]
    terminal: RefinementTerminal
    state_digest: str
    schema: str = PAPER_REFINEMENT_STATE_SCHEMA

    @property
    def score_map(self) -> dict[str, float]:
        return dict(self.dimension_scores)

    @property
    def gate_map(self) -> dict[str, bool]:
        return dict(self.hard_gate_status)

    @property
    def mean_score(self) -> float:
        values = tuple(self.score_map.values())
        if not values:
            raise ValueError("paper refinement state has no quality scores")
        return sum(values) / len(values)

    @property
    def concerns(self) -> tuple[PaperConcern, ...]:
        return tuple(concern for receipt in self.review_receipts for concern in receipt.concerns)

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "paper_id": self.paper_id,
            "round_index": self.round_index,
            "manuscript_path": self.manuscript_path,
            "manuscript_digest": self.manuscript_digest,
            "target_profile": self.target_profile,
            "fallback_profile": self.fallback_profile,
            "question": self.question,
            "answer": self.answer,
            "evidence_chain": list(self.evidence_chain),
            "boundary": self.boundary,
            "meaning": self.meaning,
            "dimension_scores": [[key, value] for key, value in self.dimension_scores],
            "hard_gate_status": [[key, value] for key, value in self.hard_gate_status],
            "exceptionality_axes_passed": list(self.exceptionality_axes_passed),
            "review_receipts": [receipt.unsigned() | {"receipt_digest": receipt.receipt_digest} for receipt in self.review_receipts],
            "prior_round_means": list(self.prior_round_means),
            "terminal": self.terminal.value,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "predicts_acceptance": False,
        }

    def validate(self) -> None:
        if self.schema != PAPER_REFINEMENT_STATE_SCHEMA:
            raise ValueError("unsupported paper refinement state schema")
        if self.round_index < 0:
            raise ValueError("paper refinement round cannot be negative")
        for name, value in (
            ("paper_id", self.paper_id),
            ("manuscript_path", self.manuscript_path),
            ("manuscript_digest", self.manuscript_digest),
            ("target_profile", self.target_profile),
            ("fallback_profile", self.fallback_profile),
            ("question", self.question),
            ("answer", self.answer),
            ("boundary", self.boundary),
            ("meaning", self.meaning),
            ("state_digest", self.state_digest),
        ):
            if not value.strip():
                raise ValueError(f"paper refinement state requires {name}")
        if not self.evidence_chain:
            raise ValueError("paper refinement state requires evidence chain")
        if tuple(key for key, _ in self.dimension_scores) != QUALITY_DIMENSIONS:
            raise ValueError("paper refinement quality dimensions are incomplete or out of order")
        for key, value in self.dimension_scores:
            if not 0 <= value <= 10:
                raise ValueError(f"quality score {key} must lie in [0, 10]")
        if len(self.hard_gate_status) != len({key for key, _ in self.hard_gate_status}):
            raise ValueError("duplicate hard gate status")
        for receipt in self.review_receipts:
            receipt.validate()
            if receipt.paper_id != self.paper_id:
                raise ValueError("review receipt belongs to another paper")
            if receipt.round_index != self.round_index:
                raise ValueError("review receipt belongs to another refinement round")
            if receipt.manuscript_digest != self.manuscript_digest:
                raise ValueError("review receipt was not produced from the frozen manuscript")
            if receipt.target_profile != self.target_profile:
                raise ValueError("review receipt used another target profile")
        roles = [receipt.reviewer_role for receipt in self.review_receipts]
        if len(roles) != len(set(roles)):
            raise ValueError("duplicate reviewer role in refinement round")
        if self.state_digest != content_digest(self.unsigned()):
            raise ValueError("paper refinement state digest mismatch")


def _review_blockers(review_receipts: Sequence[PaperReviewReceipt]) -> tuple[PaperConcern, ...]:
    return tuple(
        concern
        for receipt in review_receipts
        for concern in receipt.concerns
        if concern.open_blocker
    )


def assess_refinement_terminal(
    *,
    profile: VenueReadinessProfile,
    scores: Mapping[str, float],
    hard_gate_status: Mapping[str, bool],
    review_receipts: Sequence[PaperReviewReceipt],
    prior_round_means: Sequence[float] = (),
    round_index: int = 0,
    exceptionality_axes_passed: Sequence[str] = (),
    fallback_ready: bool = False,
) -> RefinementTerminal:
    """Return the strongest honest recursive terminal under one target profile."""

    profile.validate()
    if set(scores) != set(QUALITY_DIMENSIONS):
        return RefinementTerminal.CANNOT_CHECK
    if any(not 0 <= value <= 10 for value in scores.values()):
        return RefinementTerminal.CANNOT_CHECK
    if any(gate not in hard_gate_status for gate in profile.hard_gates):
        return RefinementTerminal.CANNOT_CHECK

    blockers = _review_blockers(review_receipts)
    if any(item.evidence_blocker for item in blockers):
        return RefinementTerminal.EVIDENCE_BLOCKED
    if any(item.target_blocker for item in blockers):
        return (
            RefinementTerminal.READY_FOR_FALLBACK
            if fallback_ready
            else RefinementTerminal.TRANSFER_RECOMMENDED
        )
    if blockers:
        return RefinementTerminal.CONTINUE_REFINEMENT

    hard_gates_pass = all(hard_gate_status[gate] for gate in profile.hard_gates)
    dimension_floor_pass = all(value >= profile.dimension_floor for value in scores.values())
    mean_score = sum(scores.values()) / len(scores)
    exceptionality_pass = (
        not profile.requires_exceptionality_axis or bool(tuple(exceptionality_axes_passed))
    )

    if hard_gates_pass and dimension_floor_pass and mean_score >= profile.mean_floor and exceptionality_pass:
        return RefinementTerminal.READY_FOR_SCOPED_TARGET

    if round_index >= 3:
        return RefinementTerminal.PLATEAU_STOP
    if len(prior_round_means) >= 2:
        if (
            mean_score - prior_round_means[-1] < 0.25
            and prior_round_means[-1] - prior_round_means[-2] < 0.25
        ):
            return RefinementTerminal.PLATEAU_STOP

    return RefinementTerminal.CONTINUE_REFINEMENT


def create_refinement_state(
    *,
    paper_id: str,
    round_index: int,
    manuscript_path: str,
    manuscript_digest: str,
    target_profile: str,
    fallback_profile: str,
    question: str,
    answer: str,
    evidence_chain: Sequence[str],
    boundary: str,
    meaning: str,
    dimension_scores: Mapping[str, float],
    hard_gate_status: Mapping[str, bool],
    exceptionality_axes_passed: Sequence[str],
    review_receipts: Sequence[PaperReviewReceipt],
    prior_round_means: Sequence[float],
    terminal: RefinementTerminal,
) -> PaperRefinementState:
    scores = tuple((key, float(dimension_scores[key])) for key in QUALITY_DIMENSIONS)
    gates = tuple(sorted((str(key), bool(value)) for key, value in hard_gate_status.items()))
    base = PaperRefinementState(
        paper_id=paper_id,
        round_index=round_index,
        manuscript_path=manuscript_path,
        manuscript_digest=manuscript_digest,
        target_profile=target_profile,
        fallback_profile=fallback_profile,
        question=question,
        answer=answer,
        evidence_chain=tuple(str(item) for item in evidence_chain),
        boundary=boundary,
        meaning=meaning,
        dimension_scores=scores,
        hard_gate_status=gates,
        exceptionality_axes_passed=tuple(sorted(set(exceptionality_axes_passed))),
        review_receipts=tuple(review_receipts),
        prior_round_means=tuple(float(value) for value in prior_round_means),
        terminal=terminal,
        state_digest="",
    )
    state = PaperRefinementState(**{**base.__dict__, "state_digest": content_digest(base.unsigned())})
    state.validate()
    return state


__all__ = [
    "ConcernClass",
    "ConcernClosure",
    "PAPER_CONCERN_SCHEMA",
    "PAPER_REFINEMENT_STATE_SCHEMA",
    "PAPER_REVIEW_RECEIPT_SCHEMA",
    "PaperConcern",
    "PaperRefinementState",
    "PaperReviewReceipt",
    "QUALITY_DIMENSIONS",
    "REVIEW_ROLES",
    "RefinementTerminal",
    "RepairRoute",
    "VenueReadinessProfile",
    "assess_refinement_terminal",
    "create_refinement_state",
]
