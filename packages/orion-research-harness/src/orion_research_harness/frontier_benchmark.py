"""Typed records for prospective scientific decisions with deferred outcome scoring.

The records make Q3's benchmark object executable: a frontier item is frozen from
its question/evidence/scoring contract, instrument decisions bind to that item,
and later outcome evidence scores each decision without changing the original
item. These types do not claim statistical independence, correctness, or
scientific authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from .protocol import content_digest

FRONTIER_ITEM_SCHEMA = "ORION.FrontierDecisionItem.v1"
FRONTIER_DECISION_SCHEMA = "ORION.FrontierInstrumentDecision.v1"
DEFERRED_SCORE_SCHEMA = "ORION.FrontierDeferredScore.v1"


class FrontierRelation(str, Enum):
    AGREE = "AGREE"
    PARTIAL = "PARTIAL"
    DISAGREE = "DISAGREE"
    CANNOT_CHECK_A = "CANNOT_CHECK_A"
    CANNOT_CHECK_B = "CANNOT_CHECK_B"
    CANNOT_CHECK_BOTH = "CANNOT_CHECK_BOTH"


class DeferredAlignment(str, Enum):
    ALIGNED = "ALIGNED"
    MISALIGNED = "MISALIGNED"
    UNRESOLVED = "UNRESOLVED"
    INVALIDATED_ITEM = "INVALIDATED_ITEM"


def _nonempty(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


@dataclass(frozen=True)
class FrontierDecisionItem:
    item_id: str
    programme_id: str
    question: str
    evidence_digest: str
    admissible_evidence: tuple[str, ...]
    diagnosis_coordinates: tuple[str, ...]
    move_coordinates: tuple[str, ...]
    deferred_scoring_rule: str
    outcome_unknown_at_freeze: bool
    freeze_epoch: str
    item_digest: str
    schema: str = FRONTIER_ITEM_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "item_id": self.item_id,
            "programme_id": self.programme_id,
            "question": self.question,
            "evidence_digest": self.evidence_digest,
            "admissible_evidence": list(self.admissible_evidence),
            "diagnosis_coordinates": list(self.diagnosis_coordinates),
            "move_coordinates": list(self.move_coordinates),
            "deferred_scoring_rule": self.deferred_scoring_rule,
            "outcome_unknown_at_freeze": self.outcome_unknown_at_freeze,
            "freeze_epoch": self.freeze_epoch,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
        }

    def validate(self) -> None:
        if self.schema != FRONTIER_ITEM_SCHEMA:
            raise ValueError("unsupported frontier item schema")
        for name, value in (
            ("item_id", self.item_id),
            ("programme_id", self.programme_id),
            ("question", self.question),
            ("evidence_digest", self.evidence_digest),
            ("deferred_scoring_rule", self.deferred_scoring_rule),
            ("freeze_epoch", self.freeze_epoch),
            ("item_digest", self.item_digest),
        ):
            _nonempty(value, name=name)
        if not self.outcome_unknown_at_freeze:
            raise ValueError("primary frontier item must be unresolved at freeze")
        if not self.admissible_evidence:
            raise ValueError("frontier item requires admissible evidence")
        if not self.diagnosis_coordinates or not self.move_coordinates:
            raise ValueError("frontier item requires diagnosis and move coordinates")
        if self.item_digest != content_digest(self.unsigned()):
            raise ValueError("frontier item digest mismatch")

    @classmethod
    def create(
        cls,
        *,
        item_id: str,
        programme_id: str,
        question: str,
        evidence_digest: str,
        admissible_evidence: Sequence[str],
        diagnosis_coordinates: Sequence[str],
        move_coordinates: Sequence[str],
        deferred_scoring_rule: str,
        freeze_epoch: str,
    ) -> "FrontierDecisionItem":
        base = cls(
            item_id=item_id,
            programme_id=programme_id,
            question=question,
            evidence_digest=evidence_digest,
            admissible_evidence=tuple(admissible_evidence),
            diagnosis_coordinates=tuple(diagnosis_coordinates),
            move_coordinates=tuple(move_coordinates),
            deferred_scoring_rule=deferred_scoring_rule,
            outcome_unknown_at_freeze=True,
            freeze_epoch=freeze_epoch,
            item_digest="",
        )
        item = cls(**{**base.__dict__, "item_digest": content_digest(base.unsigned())})
        item.validate()
        return item


@dataclass(frozen=True)
class FrontierInstrumentDecision:
    item_digest: str
    instrument_id: str
    evidence_digest: str
    diagnosis: tuple[str, ...]
    move: tuple[str, ...]
    cannot_check: bool
    decision_epoch: str
    decision_digest: str
    schema: str = FRONTIER_DECISION_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "item_digest": self.item_digest,
            "instrument_id": self.instrument_id,
            "evidence_digest": self.evidence_digest,
            "diagnosis": list(self.diagnosis),
            "move": list(self.move),
            "cannot_check": self.cannot_check,
            "decision_epoch": self.decision_epoch,
            "grants_scientific_authority": False,
            "predicts_correctness": False,
        }

    def validate_against(self, item: FrontierDecisionItem) -> None:
        item.validate()
        if self.schema != FRONTIER_DECISION_SCHEMA:
            raise ValueError("unsupported frontier decision schema")
        if self.item_digest != item.item_digest:
            raise ValueError("frontier decision belongs to another item")
        if self.evidence_digest != item.evidence_digest:
            raise ValueError("frontier decision used another evidence state")
        _nonempty(self.instrument_id, name="instrument_id")
        _nonempty(self.decision_epoch, name="decision_epoch")
        if self.cannot_check and (self.diagnosis or self.move):
            raise ValueError("cannot-check decision cannot simultaneously select diagnosis/move")
        if not self.cannot_check and (not self.diagnosis or not self.move):
            raise ValueError("scorable decision requires diagnosis and move")
        if self.decision_digest != content_digest(self.unsigned()):
            raise ValueError("frontier decision digest mismatch")

    @classmethod
    def create(
        cls,
        *,
        item: FrontierDecisionItem,
        instrument_id: str,
        diagnosis: Sequence[str] = (),
        move: Sequence[str] = (),
        cannot_check: bool = False,
        decision_epoch: str,
    ) -> "FrontierInstrumentDecision":
        base = cls(
            item_digest=item.item_digest,
            instrument_id=instrument_id,
            evidence_digest=item.evidence_digest,
            diagnosis=tuple(diagnosis),
            move=tuple(move),
            cannot_check=cannot_check,
            decision_epoch=decision_epoch,
            decision_digest="",
        )
        decision = cls(**{**base.__dict__, "decision_digest": content_digest(base.unsigned())})
        decision.validate_against(item)
        return decision


@dataclass(frozen=True)
class FrontierDeferredScore:
    item_digest: str
    decision_digest: str
    resolving_evidence_digest: str
    alignment: DeferredAlignment
    scorer_rule: str
    resolution_epoch: str
    score_digest: str
    schema: str = DEFERRED_SCORE_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "item_digest": self.item_digest,
            "decision_digest": self.decision_digest,
            "resolving_evidence_digest": self.resolving_evidence_digest,
            "alignment": self.alignment.value,
            "scorer_rule": self.scorer_rule,
            "resolution_epoch": self.resolution_epoch,
            "grants_scientific_authority": False,
            "agreement_is_not_score": True,
        }

    def validate_against(
        self,
        *,
        item: FrontierDecisionItem,
        decision: FrontierInstrumentDecision,
    ) -> None:
        decision.validate_against(item)
        if self.schema != DEFERRED_SCORE_SCHEMA:
            raise ValueError("unsupported deferred score schema")
        if self.item_digest != item.item_digest or self.decision_digest != decision.decision_digest:
            raise ValueError("deferred score does not bind the declared item/decision")
        for name, value in (
            ("resolving_evidence_digest", self.resolving_evidence_digest),
            ("scorer_rule", self.scorer_rule),
            ("resolution_epoch", self.resolution_epoch),
        ):
            _nonempty(value, name=name)
        if self.score_digest != content_digest(self.unsigned()):
            raise ValueError("deferred score digest mismatch")


__all__ = [
    "DEFERRED_SCORE_SCHEMA",
    "FRONTIER_DECISION_SCHEMA",
    "FRONTIER_ITEM_SCHEMA",
    "DeferredAlignment",
    "FrontierDecisionItem",
    "FrontierDeferredScore",
    "FrontierInstrumentDecision",
    "FrontierRelation",
]
