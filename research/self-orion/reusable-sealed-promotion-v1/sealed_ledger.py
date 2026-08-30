#!/usr/bin/env python3
"""Exact append-only ledger for reusable sealed promotion campaigns."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

ZERO_DIGEST = "0" * 64
CONFIG_NAME = "CAMPAIGN.json"
EVENTS_NAME = "events.jsonl"
FINAL_NAME = "FINAL_RECEIPT.json"


class LedgerError(RuntimeError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def rational(value: dict[str, Any]) -> Fraction:
    if set(value) != {"numerator", "denominator"}:
        raise LedgerError("rational must contain numerator and denominator only")
    numerator = value["numerator"]
    denominator = value["denominator"]
    if not isinstance(numerator, int) or not isinstance(denominator, int) or denominator <= 0:
        raise LedgerError("invalid rational")
    return Fraction(numerator, denominator)


def rational_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def is_hex(value: Any, lengths: Iterable[int]) -> bool:
    return (
        isinstance(value, str)
        and len(value) in set(lengths)
        and all(character in "0123456789abcdef" for character in value)
    )


def read_events(root: Path) -> list[dict[str, Any]]:
    path = root / EVENTS_NAME
    if not path.exists():
        return []
    result = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            raise LedgerError(f"blank event line {line_number}")
        raw = json.loads(line)
        if not isinstance(raw, dict):
            raise LedgerError(f"event line {line_number} is not an object")
        result.append(raw)
    return result


def initialize_campaign(
    root: Path,
    *,
    campaign_id: str,
    alpha_total: Fraction,
    protocol_sha256: str,
    subject_revision: str,
    candidate_generator_identity: str,
    protected_evaluator_identity: str,
    promotion_authority_identity: str,
    archivist_identity: str,
) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=False)
    if not 0 < alpha_total <= 1:
        raise LedgerError("alpha_total must lie in (0, 1]")
    if candidate_generator_identity == promotion_authority_identity:
        raise LedgerError("candidate generator and promotion authority must be distinct")
    config = {
        "schema": "ORION.SelfOrion.ReusableSealedCampaign.v1",
        "protocol_id": "SELF_ORION.REUSABLE_SEALED_LONGITUDINAL.v1",
        "campaign_id": campaign_id,
        "alpha_total": rational_json(alpha_total),
        "protocol_sha256": protocol_sha256,
        "subject_revision": subject_revision,
        "initial_chain_digest": ZERO_DIGEST,
        "identities": {
            "candidate_generator": candidate_generator_identity,
            "protected_evaluator": protected_evaluator_identity,
            "promotion_authority": promotion_authority_identity,
            "archivist": archivist_identity,
        },
        "formal_conformance_only": True,
        "protected_longitudinal_transfer_authority": False,
        "fair_comparator_superiority_authority": False,
        "negative_history_causal_effect_authority": False,
        "frontier_agent_performance_authority": False,
        "external_independent_reproduction": False,
        "submission_authority": False,
    }
    (root / CONFIG_NAME).write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (root / EVENTS_NAME).write_text("")
    return config


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "receipt_id",
        "candidate_id",
        "candidate_sha256",
        "subject_revision",
        "epoch_id",
        "protected_dataset_commitment",
        "raw_alpha",
        "leakage_inflation",
        "leakage_beta",
        "component_gates",
        "deterministic_gates",
        "candidate_generator_identity",
        "protected_evaluator_identity",
        "promotion_authority_identity",
        "outcome_note",
    }
    if set(payload) != required:
        missing = sorted(required - set(payload))
        extra = sorted(set(payload) - required)
        raise LedgerError(f"payload field mismatch missing={missing} extra={extra}")
    normalized = json.loads(canonical(payload))
    if not isinstance(normalized["receipt_id"], str) or not normalized["receipt_id"]:
        raise LedgerError("receipt_id is required")
    if not isinstance(normalized["candidate_id"], str) or not normalized["candidate_id"]:
        raise LedgerError("candidate_id is required")
    if not is_hex(normalized["candidate_sha256"], (64,)):
        raise LedgerError("candidate_sha256 must be lowercase SHA-256")
    if not is_hex(normalized["subject_revision"], (40, 64)):
        raise LedgerError("subject_revision must be a lowercase commit or content digest")
    if not isinstance(normalized["epoch_id"], str) or not normalized["epoch_id"]:
        raise LedgerError("epoch_id is required")
    if not is_hex(normalized["protected_dataset_commitment"], (64,)):
        raise LedgerError("protected_dataset_commitment must be lowercase SHA-256")
    raw_alpha = rational(normalized["raw_alpha"])
    inflation = rational(normalized["leakage_inflation"])
    beta = rational(normalized["leakage_beta"])
    if not 0 <= raw_alpha <= 1:
        raise LedgerError("raw alpha must lie in [0, 1]")
    if inflation < 1:
        raise LedgerError("leakage inflation must be at least one")
    if not 0 <= beta <= 1:
        raise LedgerError("leakage beta must lie in [0, 1]")

    components = normalized["component_gates"]
    deterministic = normalized["deterministic_gates"]
    if set(components) != {"fresh", "retention", "harm"} or not all(
        isinstance(value, bool) for value in components.values()
    ):
        raise LedgerError("component gates must be exactly fresh, retention, and harm booleans")
    expected_deterministic = {
        "resource",
        "custody",
        "authority",
        "candidate_bytes",
        "current_execution",
        "negative_history_retained",
    }
    if set(deterministic) != expected_deterministic or not all(
        isinstance(value, bool) for value in deterministic.values()
    ):
        raise LedgerError("deterministic gate set is incomplete")
    for identity_field in (
        "candidate_generator_identity",
        "protected_evaluator_identity",
        "promotion_authority_identity",
    ):
        if not isinstance(normalized[identity_field], str) or not normalized[identity_field]:
            raise LedgerError(f"{identity_field} is required")
    if not isinstance(normalized["outcome_note"], str):
        raise LedgerError("outcome_note must be a string")
    return normalized


def last_cumulative(events: list[dict[str, Any]]) -> Fraction:
    if not events:
        return Fraction(0)
    return rational(events[-1]["cumulative_effective_debit"])


def append_payload(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    config = json.loads((root / CONFIG_NAME).read_text())
    events = read_events(root)
    normalized = normalize_payload(payload)
    payload_digest = digest(normalized)

    matching = [event for event in events if event.get("receipt_id") == normalized["receipt_id"]]
    if matching:
        prior = matching[0]
        if prior.get("payload_digest") == payload_digest:
            return prior
        return append_conflict(root, normalized["receipt_id"], payload_digest)

    identities = config["identities"]
    identity_match = (
        normalized["candidate_generator_identity"] == identities["candidate_generator"]
        and normalized["protected_evaluator_identity"] == identities["protected_evaluator"]
        and normalized["promotion_authority_identity"] == identities["promotion_authority"]
    )
    independent_authority = (
        normalized["candidate_generator_identity"]
        != normalized["promotion_authority_identity"]
    )
    subject_match = normalized["subject_revision"] == config["subject_revision"]

    raw_alpha = rational(normalized["raw_alpha"])
    inflation = rational(normalized["leakage_inflation"])
    beta = rational(normalized["leakage_beta"])
    effective = inflation * raw_alpha + beta
    cumulative = last_cumulative(events) + effective
    alpha_total = rational(config["alpha_total"])
    within_budget = cumulative <= alpha_total

    components_pass = all(normalized["component_gates"].values())
    deterministic_pass = all(normalized["deterministic_gates"].values())
    prerequisites_pass = (
        deterministic_pass
        and within_budget
        and identity_match
        and independent_authority
        and subject_match
    )
    if components_pass and prerequisites_pass:
        decision = "PROMOTE"
        disposition = "ALL_NONCOMPENSATORY_GATES_PASS"
    elif not components_pass and prerequisites_pass:
        decision = "REJECT"
        disposition = "STATISTICAL_COMPONENT_GATE_FAILED"
    else:
        decision = "UNRESOLVED"
        disposition = "FAIL_CLOSED_CONTROL_OR_AUTHORITY_GATE"

    prior_digest = events[-1]["event_digest"] if events else config["initial_chain_digest"]
    unsigned_event = {
        "schema": "ORION.SelfOrion.ReusableSealedLedgerEvent.v1",
        "sequence": len(events) + 1,
        "prior_digest": prior_digest,
        "event_type": "EVALUATION",
        "receipt_id": normalized["receipt_id"],
        "payload_digest": payload_digest,
        "payload": normalized,
        "effective_debit": rational_json(effective),
        "cumulative_effective_debit": rational_json(cumulative),
        "within_global_budget": within_budget,
        "identity_match": identity_match,
        "independent_promotion_authority": independent_authority,
        "subject_match": subject_match,
        "decision": decision,
        "disposition": disposition,
        "empirical_authority_delta": "NONE",
    }
    event = dict(unsigned_event)
    event["event_digest"] = digest(unsigned_event)
    with (root / EVENTS_NAME).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(event) + "\n")
    return event


def append_conflict(root: Path, receipt_id: str, conflicting_payload_digest: str) -> dict[str, Any]:
    config = json.loads((root / CONFIG_NAME).read_text())
    events = read_events(root)
    prior_digest = events[-1]["event_digest"] if events else config["initial_chain_digest"]
    cumulative = last_cumulative(events)
    unsigned_event = {
        "schema": "ORION.SelfOrion.ReusableSealedLedgerEvent.v1",
        "sequence": len(events) + 1,
        "prior_digest": prior_digest,
        "event_type": "DUPLICATE_CONFLICT",
        "receipt_id": receipt_id,
        "conflicting_payload_digest": conflicting_payload_digest,
        "effective_debit": rational_json(Fraction(0)),
        "cumulative_effective_debit": rational_json(cumulative),
        "within_global_budget": False,
        "identity_match": False,
        "independent_promotion_authority": False,
        "subject_match": False,
        "decision": "UNRESOLVED",
        "disposition": "CONFLICTING_DUPLICATE_BLOCKS_CAMPAIGN",
        "empirical_authority_delta": "NONE",
    }
    event = dict(unsigned_event)
    event["event_digest"] = digest(unsigned_event)
    with (root / EVENTS_NAME).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(event) + "\n")
    return event


def finalize_campaign(root: Path) -> dict[str, Any]:
    config = json.loads((root / CONFIG_NAME).read_text())
    events = read_events(root)
    decisions = {name: 0 for name in ("PROMOTE", "REJECT", "UNRESOLVED")}
    conflicts = 0
    for event in events:
        decisions[event["decision"]] += 1
        conflicts += event["event_type"] == "DUPLICATE_CONFLICT"
    final = {
        "schema": "ORION.SelfOrion.ReusableSealedFinalReceipt.v1",
        "protocol_id": config["protocol_id"],
        "campaign_id": config["campaign_id"],
        "event_count": len(events),
        "final_chain_digest": events[-1]["event_digest"] if events else config["initial_chain_digest"],
        "cumulative_effective_debit": rational_json(last_cumulative(events)),
        "alpha_total": config["alpha_total"],
        "decision_counts": decisions,
        "duplicate_conflict_count": conflicts,
        "formal_terminal": "SELF_ORION_REUSABLE_SEALED_FORMAL_CONFORMANCE_ONLY",
        "protected_longitudinal_transfer_authority": False,
        "fair_comparator_superiority_authority": False,
        "negative_history_causal_effect_authority": False,
        "frontier_agent_performance_authority": False,
        "external_independent_reproduction": False,
        "submission_authority": False,
    }
    unsigned = dict(final)
    final["receipt_digest"] = digest(unsigned)
    (root / FINAL_NAME).write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")
    return final
