"""One content-bound, non-authorizing P15+Q3 instrument receipt."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Mapping, Sequence

from .frontier_benchmark import (
    DeferredAlignment,
    FrontierDecisionItem,
    FrontierDeferredScore,
    FrontierInstrumentDecision,
    FrontierRelation,
)
from .protocol import content_digest
from .scientific_execution_integrity import (
    ScientificDisposition,
    ScientificExecutionRecord,
)

P15_Q3_INSTRUMENT_SCHEMA = "ORION.P15Q3.SharedInstrumentReceipt.v1"
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


def _sha256(value: str, *, name: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{name} must be an exact lowercase SHA-256 digest")
    return value


def _epoch(value: str, *, name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return parsed


def _unique_nonempty(values: Sequence[str], *, name: str) -> None:
    if not values:
        raise ValueError(f"{name} must not be empty")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{name} entries must be non-empty strings")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} entries must be unique")


def _relation(decisions: Sequence[FrontierInstrumentDecision]) -> FrontierRelation:
    left, right = decisions
    if left.cannot_check and right.cannot_check:
        return FrontierRelation.CANNOT_CHECK_BOTH
    if left.cannot_check:
        return FrontierRelation.CANNOT_CHECK_A
    if right.cannot_check:
        return FrontierRelation.CANNOT_CHECK_B
    if left.diagnosis == right.diagnosis and left.move == right.move:
        return FrontierRelation.AGREE
    if set(left.diagnosis) & set(right.diagnosis) or set(left.move) & set(right.move):
        return FrontierRelation.PARTIAL
    return FrontierRelation.DISAGREE


@dataclass(frozen=True)
class P15Q3InstrumentReceipt:
    execution_record_id: str
    execution_content_digest: str
    execution_disposition: str
    frontier_item_digest: str
    decision_digests: tuple[str, str]
    frontier_relation: FrontierRelation
    deferred_score_digests: tuple[str, ...]
    receipt_digest: str
    schema: str = P15_Q3_INSTRUMENT_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "execution_record_id": self.execution_record_id,
            "execution_content_digest": self.execution_content_digest,
            "execution_disposition": self.execution_disposition,
            "frontier_item_digest": self.frontier_item_digest,
            "decision_digests": list(self.decision_digests),
            "frontier_relation": self.frontier_relation.value,
            "deferred_score_digests": list(self.deferred_score_digests),
            "grants_scientific_authority": False,
            "grants_independent_authority": False,
            "independent_authority": "CANNOT_CHECK",
            "public_data_confers_custody": False,
        }

    def as_dict(self) -> dict[str, Any]:
        return {**self.unsigned(), "receipt_digest": self.receipt_digest}

    def validate(self) -> None:
        if self.schema != P15_Q3_INSTRUMENT_SCHEMA:
            raise ValueError("unsupported P15+Q3 instrument schema")
        if not isinstance(self.execution_record_id, str) or not self.execution_record_id.strip():
            raise ValueError("execution_record_id must be a non-empty string")
        _sha256(self.execution_content_digest, name="execution_content_digest")
        if self.execution_disposition not in {
            disposition.value for disposition in ScientificDisposition
        }:
            raise ValueError("execution_disposition is not a declared P15 disposition")
        _sha256(self.frontier_item_digest, name="frontier_item_digest")
        if len(self.decision_digests) != 2 or len(set(self.decision_digests)) != 2:
            raise ValueError("receipt requires two distinct instrument decisions")
        for digest in self.decision_digests:
            _sha256(digest, name="decision_digest")
        if not isinstance(self.frontier_relation, FrontierRelation):
            raise ValueError("frontier_relation is not a declared relation")
        if len(set(self.deferred_score_digests)) != len(self.deferred_score_digests):
            raise ValueError("receipt contains duplicate deferred scores")
        for digest in self.deferred_score_digests:
            _sha256(digest, name="deferred_score_digest")
        _sha256(self.receipt_digest, name="receipt_digest")
        if self.receipt_digest != content_digest(self.unsigned()):
            raise ValueError("P15+Q3 receipt digest mismatch")

    @classmethod
    def create(
        cls,
        *,
        execution: ScientificExecutionRecord,
        item: FrontierDecisionItem,
        decisions: Sequence[FrontierInstrumentDecision],
        deferred_scores: Sequence[FrontierDeferredScore] = (),
    ) -> "P15Q3InstrumentReceipt":
        execution = ScientificExecutionRecord.from_mapping(execution.as_dict())
        item.validate()
        if type(item.outcome_unknown_at_freeze) is not bool:
            raise TypeError("outcome_unknown_at_freeze must be a boolean")
        _sha256(item.evidence_digest, name="item evidence_digest")
        _sha256(item.item_digest, name="item_digest")
        _unique_nonempty(item.admissible_evidence, name="admissible_evidence")
        _unique_nonempty(item.diagnosis_coordinates, name="diagnosis_coordinates")
        _unique_nonempty(item.move_coordinates, name="move_coordinates")
        freeze_epoch = _epoch(item.freeze_epoch, name="freeze_epoch")
        if len(decisions) != 2:
            raise ValueError("exactly two Q3 instrument decisions are required")
        if len({decision.instrument_id for decision in decisions}) != 2:
            raise ValueError("Q3 instrument identities must be distinct")
        for decision in decisions:
            decision.validate_against(item)
            if type(decision.cannot_check) is not bool:
                raise TypeError("cannot_check must be a boolean")
            _sha256(decision.evidence_digest, name="decision evidence_digest")
            _sha256(decision.decision_digest, name="decision_digest")
            if len(set(decision.diagnosis)) != len(decision.diagnosis):
                raise ValueError("decision diagnosis coordinates must be unique")
            if len(set(decision.move)) != len(decision.move):
                raise ValueError("decision move coordinates must be unique")
            if not set(decision.diagnosis) <= set(item.diagnosis_coordinates):
                raise ValueError("decision contains an out-of-vocabulary diagnosis coordinate")
            if not set(decision.move) <= set(item.move_coordinates):
                raise ValueError("decision contains an out-of-vocabulary move coordinate")
            if _epoch(decision.decision_epoch, name="decision_epoch") <= freeze_epoch:
                raise ValueError("decision_epoch must be after the frozen item epoch")
        if len({decision.decision_digest for decision in decisions}) != 2:
            raise ValueError("Q3 decision digests must be distinct")
        latest_decision_epoch = max(
            _epoch(decision.decision_epoch, name="decision_epoch")
            for decision in decisions
        )
        by_digest = {decision.decision_digest: decision for decision in decisions}
        if len({score.decision_digest for score in deferred_scores}) != len(deferred_scores):
            raise ValueError("at most one deferred score is permitted per decision")
        if len(deferred_scores) > 1 and len({
            score.resolving_evidence_digest for score in deferred_scores
        }) != 1:
            raise ValueError("multiple deferred scores require common resolving evidence")
        for score in deferred_scores:
            decision = by_digest.get(score.decision_digest)
            if decision is None:
                raise ValueError("deferred score belongs to an undeclared decision")
            if not isinstance(score.alignment, DeferredAlignment):
                raise TypeError("alignment must be a declared DeferredAlignment")
            score.validate_against(item=item, decision=decision)
            _sha256(score.resolving_evidence_digest, name="resolving_evidence_digest")
            _sha256(score.score_digest, name="score_digest")
            if _epoch(score.resolution_epoch, name="resolution_epoch") <= latest_decision_epoch:
                raise ValueError("resolution_epoch must be after both decision epochs")
        if len({score.score_digest for score in deferred_scores}) != len(deferred_scores):
            raise ValueError("deferred score digests must be distinct")
        base = cls(
            execution_record_id=execution.record_id,
            execution_content_digest=content_digest(execution.as_dict()),
            execution_disposition=execution.disposition().value,
            frontier_item_digest=item.item_digest,
            decision_digests=tuple(decision.decision_digest for decision in decisions),
            frontier_relation=_relation(decisions),
            deferred_score_digests=tuple(score.score_digest for score in deferred_scores),
            receipt_digest="",
        )
        receipt = cls(**{**base.__dict__, "receipt_digest": content_digest(base.unsigned())})
        receipt.validate()
        return receipt


def _strings(raw: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = raw.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise TypeError(f"{key} must be a list of strings")
    return tuple(value)


def _exact_keys(raw: Mapping[str, Any], required: set[str], *, label: str) -> None:
    if set(raw) != required:
        raise ValueError(
            f"{label} fields must be exact; missing={sorted(required - set(raw))!r}; "
            f"extra={sorted(set(raw) - required)!r}"
        )


def _strict_bool(raw: Mapping[str, Any], key: str) -> bool:
    value = raw.get(key)
    if type(value) is not bool:
        raise TypeError(f"{key} must be a boolean")
    return value


def receipt_from_mapping(payload: Mapping[str, Any]) -> P15Q3InstrumentReceipt:
    """Parse the CLI interchange object and emit the fail-closed receipt."""
    required = {"execution", "item", "decisions", "scores"}
    if not isinstance(payload, Mapping) or set(payload) != required:
        raise ValueError("payload requires exactly execution, item, decisions and scores")
    execution = ScientificExecutionRecord.from_mapping(payload["execution"])
    raw_item = payload["item"]
    if not isinstance(raw_item, Mapping):
        raise TypeError("item must be an object")
    _exact_keys(
        raw_item,
        {
            "schema", "item_id", "programme_id", "question", "evidence_digest",
            "admissible_evidence", "diagnosis_coordinates", "move_coordinates",
            "deferred_scoring_rule", "outcome_unknown_at_freeze", "freeze_epoch",
            "item_digest",
        },
        label="item",
    )
    item = FrontierDecisionItem(
        item_id=raw_item["item_id"], programme_id=raw_item["programme_id"],
        question=raw_item["question"], evidence_digest=raw_item["evidence_digest"],
        admissible_evidence=_strings(raw_item, "admissible_evidence"),
        diagnosis_coordinates=_strings(raw_item, "diagnosis_coordinates"),
        move_coordinates=_strings(raw_item, "move_coordinates"),
        deferred_scoring_rule=raw_item["deferred_scoring_rule"],
        outcome_unknown_at_freeze=_strict_bool(raw_item, "outcome_unknown_at_freeze"),
        freeze_epoch=raw_item["freeze_epoch"], item_digest=raw_item["item_digest"],
        schema=raw_item["schema"],
    )
    item.validate()
    if not isinstance(payload["decisions"], list):
        raise TypeError("decisions must be a list")
    decisions = []
    for raw in payload["decisions"]:
        if not isinstance(raw, Mapping):
            raise TypeError("each decision must be an object")
        _exact_keys(
            raw,
            {
                "schema", "item_digest", "instrument_id", "evidence_digest",
                "diagnosis", "move", "cannot_check", "decision_epoch", "decision_digest",
            },
            label="decision",
        )
        decisions.append(FrontierInstrumentDecision(
            item_digest=raw["item_digest"], instrument_id=raw["instrument_id"],
            evidence_digest=raw["evidence_digest"], diagnosis=_strings(raw, "diagnosis"),
            move=_strings(raw, "move"), cannot_check=_strict_bool(raw, "cannot_check"),
            decision_epoch=raw["decision_epoch"], decision_digest=raw["decision_digest"],
            schema=raw["schema"],
        ))
    if not isinstance(payload["scores"], list):
        raise TypeError("scores must be a list")
    scores = []
    for raw in payload["scores"]:
        if not isinstance(raw, Mapping):
            raise TypeError("each score must be an object")
        _exact_keys(
            raw,
            {
                "schema", "item_digest", "decision_digest", "resolving_evidence_digest",
                "alignment", "scorer_rule", "resolution_epoch", "score_digest",
            },
            label="score",
        )
        scores.append(FrontierDeferredScore(
            item_digest=raw["item_digest"], decision_digest=raw["decision_digest"],
            resolving_evidence_digest=raw["resolving_evidence_digest"],
            alignment=DeferredAlignment(raw["alignment"]), scorer_rule=raw["scorer_rule"],
            resolution_epoch=raw["resolution_epoch"], score_digest=raw["score_digest"],
            schema=raw["schema"],
        ))
    return P15Q3InstrumentReceipt.create(
        execution=execution, item=item, decisions=decisions, deferred_scores=scores
    )


__all__ = ["P15_Q3_INSTRUMENT_SCHEMA", "P15Q3InstrumentReceipt", "receipt_from_mapping"]
