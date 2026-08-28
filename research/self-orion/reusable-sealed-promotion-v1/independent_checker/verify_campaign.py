#!/usr/bin/env python3
"""Independent verifier for reusable sealed promotion campaign ledgers."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

ACCEPT = "ACCEPT_SELF_ORION_REUSABLE_SEALED_FORMAL_CONFORMANCE"
REJECT = "REJECT_SELF_ORION_REUSABLE_SEALED_FORMAL_CONFORMANCE"
ZERO_DIGEST = "0" * 64


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def rational(raw: Any) -> Fraction:
    if not isinstance(raw, dict) or set(raw) != {"numerator", "denominator"}:
        raise ValueError("invalid rational fields")
    numerator = raw["numerator"]
    denominator = raw["denominator"]
    if not isinstance(numerator, int) or not isinstance(denominator, int) or denominator <= 0:
        raise ValueError("invalid rational values")
    return Fraction(numerator, denominator)


def rational_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def read_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict):
        raise ValueError(f"{path} is not an object")
    return raw


def read_events(path: Path) -> list[dict[str, Any]]:
    result = []
    for line in path.read_text().splitlines():
        if not line.strip():
            raise ValueError("blank event line")
        raw = json.loads(line)
        if not isinstance(raw, dict):
            raise ValueError("event is not an object")
        result.append(raw)
    return result


def expected_evaluation(
    event: dict[str, Any],
    config: dict[str, Any],
    prior_cumulative: Fraction,
) -> tuple[dict[str, bool], Fraction, str, str]:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        return {"payload_object": False}, prior_cumulative, "UNRESOLVED", "INVALID"
    components = payload.get("component_gates", {})
    deterministic = payload.get("deterministic_gates", {})
    expected_component_keys = {"fresh", "retention", "harm"}
    expected_deterministic_keys = {
        "resource",
        "custody",
        "authority",
        "candidate_bytes",
        "current_execution",
        "negative_history_retained",
    }
    try:
        raw_alpha = rational(payload.get("raw_alpha"))
        inflation = rational(payload.get("leakage_inflation"))
        beta = rational(payload.get("leakage_beta"))
    except (TypeError, ValueError):
        raw_alpha = Fraction(0)
        inflation = Fraction(0)
        beta = Fraction(0)
        rational_ok = False
    else:
        rational_ok = (
            0 <= raw_alpha <= 1
            and inflation >= 1
            and 0 <= beta <= 1
        )

    effective = inflation * raw_alpha + beta if rational_ok else Fraction(0)
    cumulative = prior_cumulative + effective
    alpha_total = rational(config["alpha_total"])
    identities = config["identities"]
    identity_match = (
        payload.get("candidate_generator_identity") == identities["candidate_generator"]
        and payload.get("protected_evaluator_identity") == identities["protected_evaluator"]
        and payload.get("promotion_authority_identity") == identities["promotion_authority"]
    )
    independent_authority = (
        payload.get("candidate_generator_identity")
        != payload.get("promotion_authority_identity")
    )
    subject_match = payload.get("subject_revision") == config["subject_revision"]
    components_well_formed = set(components) == expected_component_keys and all(
        isinstance(value, bool) for value in components.values()
    )
    deterministic_well_formed = set(deterministic) == expected_deterministic_keys and all(
        isinstance(value, bool) for value in deterministic.values()
    )
    components_pass = components_well_formed and all(components.values())
    deterministic_pass = deterministic_well_formed and all(deterministic.values())
    within_budget = rational_ok and cumulative <= alpha_total
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
    elif components_well_formed and not components_pass and prerequisites_pass:
        decision = "REJECT"
        disposition = "STATISTICAL_COMPONENT_GATE_FAILED"
    else:
        decision = "UNRESOLVED"
        disposition = "FAIL_CLOSED_CONTROL_OR_AUTHORITY_GATE"

    checks = {
        "payload_object": True,
        "payload_digest": event.get("payload_digest") == digest(payload),
        "rational_fields": rational_ok,
        "component_gate_shape": components_well_formed,
        "deterministic_gate_shape": deterministic_well_formed,
        "effective_debit": event.get("effective_debit") == rational_json(effective),
        "cumulative_debit": event.get("cumulative_effective_debit") == rational_json(cumulative),
        "within_budget": event.get("within_global_budget") is within_budget,
        "identity_match": event.get("identity_match") is identity_match,
        "independent_authority": event.get("independent_promotion_authority")
        is independent_authority,
        "subject_match": event.get("subject_match") is subject_match,
        "decision": event.get("decision") == decision,
        "disposition": event.get("disposition") == disposition,
        "no_empirical_authority": event.get("empirical_authority_delta") == "NONE",
    }
    return checks, cumulative, decision, disposition


def verify(campaign: Path, protocol: Path) -> dict[str, Any]:
    config = read_json(campaign / "CAMPAIGN.json")
    events = read_events(campaign / "events.jsonl")
    final = read_json(campaign / "FINAL_RECEIPT.json")
    summary = read_json(campaign / "CONFORMANCE_SUMMARY.json")

    checks: dict[str, bool] = {
        "config_schema": config.get("schema") == "ORION.SelfOrion.ReusableSealedCampaign.v1",
        "protocol_id": config.get("protocol_id")
        == "SELF_ORION.REUSABLE_SEALED_LONGITUDINAL.v1",
        "protocol_hash": config.get("protocol_sha256")
        == hashlib.sha256(protocol.read_bytes()).hexdigest(),
        "initial_digest": config.get("initial_chain_digest") == ZERO_DIGEST,
        "formal_only": config.get("formal_conformance_only") is True,
        "config_authority_fail_closed": all(
            config.get(field) is False
            for field in (
                "protected_longitudinal_transfer_authority",
                "fair_comparator_superiority_authority",
                "negative_history_causal_effect_authority",
                "frontier_agent_performance_authority",
                "external_independent_reproduction",
                "submission_authority",
            )
        ),
        "distinct_candidate_and_promotion_identities": config.get("identities", {}).get(
            "candidate_generator"
        )
        != config.get("identities", {}).get("promotion_authority"),
    }

    prior_digest = config.get("initial_chain_digest")
    cumulative = Fraction(0)
    decisions = {name: 0 for name in ("PROMOTE", "REJECT", "UNRESOLVED")}
    receipt_payloads: dict[str, str] = {}
    duplicate_conflicts = 0
    event_checks: list[dict[str, Any]] = []
    for index, event in enumerate(events, start=1):
        unsigned = dict(event)
        observed_digest = unsigned.pop("event_digest", None)
        local: dict[str, bool] = {
            "schema": event.get("schema") == "ORION.SelfOrion.ReusableSealedLedgerEvent.v1",
            "sequence": event.get("sequence") == index,
            "prior_digest": event.get("prior_digest") == prior_digest,
            "event_digest": observed_digest == digest(unsigned),
        }
        event_type = event.get("event_type")
        if event_type == "EVALUATION":
            evaluation_checks, cumulative, decision, _ = expected_evaluation(
                event, config, cumulative
            )
            local.update(evaluation_checks)
            receipt_id = event.get("receipt_id")
            payload_digest = event.get("payload_digest")
            local["receipt_id_first_occurrence"] = receipt_id not in receipt_payloads
            if isinstance(receipt_id, str) and isinstance(payload_digest, str):
                receipt_payloads[receipt_id] = payload_digest
        elif event_type == "DUPLICATE_CONFLICT":
            duplicate_conflicts += 1
            decision = "UNRESOLVED"
            local.update(
                {
                    "zero_conflict_debit": event.get("effective_debit")
                    == rational_json(Fraction(0)),
                    "conflict_cumulative_unchanged": event.get(
                        "cumulative_effective_debit"
                    )
                    == rational_json(cumulative),
                    "conflict_decision": event.get("decision") == "UNRESOLVED",
                    "conflict_disposition": event.get("disposition")
                    == "CONFLICTING_DUPLICATE_BLOCKS_CAMPAIGN",
                    "no_empirical_authority": event.get("empirical_authority_delta")
                    == "NONE",
                }
            )
        else:
            decision = "UNRESOLVED"
            local["known_event_type"] = False
        decisions[decision] += 1
        event_checks.append({"sequence": index, "checks": local})
        prior_digest = observed_digest

    checks["events_nonempty"] = bool(events)
    checks["all_event_checks"] = all(
        all(item["checks"].values()) for item in event_checks
    )
    checks["conformance_decision_mix"] = decisions == {
        "PROMOTE": 2,
        "REJECT": 2,
        "UNRESOLVED": 2,
    }
    checks["no_duplicate_conflict_in_conformance"] = duplicate_conflicts == 0
    checks["final_schema"] = (
        final.get("schema") == "ORION.SelfOrion.ReusableSealedFinalReceipt.v1"
    )
    checks["final_event_count"] = final.get("event_count") == len(events)
    checks["final_chain_digest"] = final.get("final_chain_digest") == prior_digest
    checks["final_cumulative"] = (
        final.get("cumulative_effective_debit") == rational_json(cumulative)
    )
    checks["final_alpha_total"] = final.get("alpha_total") == config.get("alpha_total")
    checks["final_decision_counts"] = final.get("decision_counts") == decisions
    checks["final_conflicts"] = final.get("duplicate_conflict_count") == duplicate_conflicts
    checks["final_formal_terminal"] = (
        final.get("formal_terminal")
        == "SELF_ORION_REUSABLE_SEALED_FORMAL_CONFORMANCE_ONLY"
    )
    checks["final_authority_fail_closed"] = all(
        final.get(field) is False
        for field in (
            "protected_longitudinal_transfer_authority",
            "fair_comparator_superiority_authority",
            "negative_history_causal_effect_authority",
            "frontier_agent_performance_authority",
            "external_independent_reproduction",
            "submission_authority",
        )
    )
    unsigned_final = dict(final)
    final_digest = unsigned_final.pop("receipt_digest", None)
    checks["final_receipt_digest"] = final_digest == digest(unsigned_final)
    checks["summary_terminal"] = (
        summary.get("formal_terminal")
        == "SELF_ORION_REUSABLE_SEALED_FORMAL_CONFORMANCE_ONLY"
    )
    checks["summary_no_empirical_authority"] = (
        summary.get("empirical_authority_delta") == "NONE"
    )
    checks["summary_decisions"] = summary.get("event_decisions") == [
        event.get("decision") for event in events
    ]
    checks["summary_final_digest"] = (
        summary.get("final_receipt_digest") == final.get("receipt_digest")
    )

    positive = all(checks.values())
    report: dict[str, Any] = {
        "schema": "ORION.SelfOrion.ReusableSealedIndependentVerification.v1",
        "decision": ACCEPT if positive else REJECT,
        "campaign_id": config.get("campaign_id"),
        "checks": checks,
        "event_checks": event_checks,
        "decision_counts": decisions,
        "cumulative_effective_debit": rational_json(cumulative),
        "formal_theorem_or_software_authority": positive,
        "protected_longitudinal_transfer_authority": False,
        "fair_comparator_superiority_authority": False,
        "negative_history_causal_effect_authority": False,
        "frontier_agent_performance_authority": False,
        "external_independent_reproduction": False,
        "submission_authority": False,
    }
    unsigned_report = dict(report)
    report["verification_digest"] = digest(unsigned_report)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    protocol = args.protocol or Path(__file__).resolve().parents[1] / "PROTOCOL.json"
    report = verify(args.campaign, protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        "SELF_ORION_RSP_VERIFY="
        + canonical(
            {
                "decision": report["decision"],
                "all_checks": all(report["checks"].values()),
                "verification_digest": report["verification_digest"],
            }
        )
    )
    return 0 if report["decision"] == ACCEPT else 1


if __name__ == "__main__":
    raise SystemExit(main())
