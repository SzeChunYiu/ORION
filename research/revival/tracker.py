#!/usr/bin/env python3
"""Validate ORION research-revival programme infrastructure (#284).

This module is programme audit machinery, not scientific evidence. A green
check here never closes a child issue and never promotes a hypothesis.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parent
TRACKER_SCHEMA_VERSION = "orion.research-revival.programme-tracker.v1"
DOCTRINE_SCHEMA_VERSION = "orion.research-revival.doctrine-protocol.v1"
NOVELTY_SCHEMA_VERSION = "orion.research-revival.novelty-hypotheses.v1"
CORRECTIONS_SCHEMA_VERSION = "orion.research-revival.corrections.v1"

PARENT_ISSUE = 284
REQUIRED_CHILDREN = (278, 279, 280, 281, 282, 283, 285, 286, 287, 288)

IN_PROGRESS_STATES = frozenset(
    {
        "OPEN",
        "PRESERVED",
        "LOCALIZED",
        "LITERATURE_SATURATED",
        "DISCRIMINATOR_FROZEN",
        "PROTOCOL_FROZEN",
        "EXECUTED",
        "INDEPENDENT_VERIFICATION_IN_PROGRESS",
    }
)
PROGRESS_ORDER = (
    "OPEN",
    "PRESERVED",
    "LOCALIZED",
    "LITERATURE_SATURATED",
    "DISCRIMINATOR_FROZEN",
    "PROTOCOL_FROZEN",
    "EXECUTED",
    "INDEPENDENT_VERIFICATION_IN_PROGRESS",
)
PROGRAMME_STATUSES = frozenset({"SCAFFOLDING_ONLY", "IN_PROGRESS", "CLOSED"})

# Positive terminals promote a new scientific claim and require a #283 record.
POSITIVE_TERMINALS = frozenset(
    {
        "MECHANISM_SUPPORTED",
        "EXTERNAL_SUPPORTED",
        "REVIVED_AFTER_FAILURE",
        "BROADER_THEORY_SUPPORTED",
        "NARROW_THEORY_CONFIRMED",
        "FOLLOWUP_SUPPORTED",
        "TRANSFER_SUPPORTED",
        "VERIFICATION_COMPLETE",
        "GLOBAL_POSITIVE_SUPPORTED",
        "TRANSFER_MECHANISM_SUPPORTED",
        "NOVELTY_CERTIFICATE_SUPPORTED",
        "PROTECTED_GOAL_EVOLUTION_SUPPORTED",
    }
)
REFUTED_OR_BOUNDED_TERMINALS = frozenset(
    {
        "MECHANISM_REFUTED",
        "REFUTED/SHRINK",
        "POSITIVE_INVALIDATED",
        "NULL_CONFIRMED",
        "SECURITY_FAILURE",
        "DIAGNOSIS_ONLY",
        "HARMFUL/REFUTED",
        "INVALIDATED",
        "LOCAL_ONLY",
        "OVERCONSERVATIVE",
        "REFUTED",
        "ABSTRACTION_ONLY",
        "DOMAIN_LOCAL_ONLY",
        "PROCESS_USEFUL_NOT_NOVEL",
        "GOAL_EVOLUTION_USEFUL_BUT_UNPROTECTED",
        "OBJECTIVE_DRIFT/HARMFUL",
    }
)
CANNOT_CHECK_TERMINAL = "CANNOT_CHECK"

CHILD_TERMINALS: dict[int, frozenset[str]] = {
    278: frozenset({"MECHANISM_SUPPORTED", "MECHANISM_REFUTED", CANNOT_CHECK_TERMINAL}),
    279: frozenset(
        {"EXTERNAL_SUPPORTED", "REVIVED_AFTER_FAILURE", "REFUTED/SHRINK", CANNOT_CHECK_TERMINAL}
    ),
    280: frozenset(
        {
            "BROADER_THEORY_SUPPORTED",
            "NARROW_THEORY_CONFIRMED",
            "POSITIVE_INVALIDATED",
            CANNOT_CHECK_TERMINAL,
        }
    ),
    281: frozenset(
        {"FOLLOWUP_SUPPORTED", "NULL_CONFIRMED", "SECURITY_FAILURE", CANNOT_CHECK_TERMINAL}
    ),
    282: frozenset(
        {"TRANSFER_SUPPORTED", "DIAGNOSIS_ONLY", "HARMFUL/REFUTED", CANNOT_CHECK_TERMINAL}
    ),
    283: frozenset({"VERIFICATION_COMPLETE", "INVALIDATED", CANNOT_CHECK_TERMINAL}),
    285: frozenset(
        {
            "GLOBAL_POSITIVE_SUPPORTED",
            "LOCAL_ONLY",
            "OVERCONSERVATIVE",
            "REFUTED",
            CANNOT_CHECK_TERMINAL,
        }
    ),
    286: frozenset(
        {
            "TRANSFER_MECHANISM_SUPPORTED",
            "ABSTRACTION_ONLY",
            "DOMAIN_LOCAL_ONLY",
            "HARMFUL/REFUTED",
            CANNOT_CHECK_TERMINAL,
        }
    ),
    287: frozenset(
        {
            "NOVELTY_CERTIFICATE_SUPPORTED",
            "PROCESS_USEFUL_NOT_NOVEL",
            "REFUTED",
            CANNOT_CHECK_TERMINAL,
        }
    ),
    288: frozenset(
        {
            "PROTECTED_GOAL_EVOLUTION_SUPPORTED",
            "GOAL_EVOLUTION_USEFUL_BUT_UNPROTECTED",
            "OBJECTIVE_DRIFT/HARMFUL",
            "REFUTED",
            CANNOT_CHECK_TERMINAL,
        }
    ),
}

STALE_CLAIMS = (
    re.compile(r"P4.{0,40}hostile battery never run", re.I),
    re.compile(r"H2.{0,40}TIER_B", re.I),
    re.compile(r"H2.{0,40}n=385", re.I),
)

DOCTRINE_REQUIRED_TRUE = (
    "never_tune_outcomes_positive",
    "one_stage_attribution_required",
    "freeze_discriminator_before_repair",
    "new_immutable_protocol_for_repair",
    "preserve_negative_history",
)
DOCTRINE_REQUIRED_FALSE = (
    "margin_relaxation_after_outcome_access",
    "rewrite_v1_results_in_place",
    "delete_null_or_harmful_runs",
    "treat_larger_n_as_mechanism_repair",
    "call_implementation_novelty_scientific_novelty",
)


class TrackerError(ValueError):
    """Illegal programme-tracker state or transition."""


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TrackerError(f"{path} must contain one JSON object")
    return payload


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _terminal_class(state: str) -> str | None:
    if state in POSITIVE_TERMINALS:
        return "positive"
    if state in REFUTED_OR_BOUNDED_TERMINALS:
        return "refuted_or_bounded"
    if state == CANNOT_CHECK_TERMINAL:
        return "cannot_check"
    return None


def requires_verification_record(state: str) -> bool:
    return state in POSITIVE_TERMINALS


def validate_child(child: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    issue = child.get("issue")
    if issue not in CHILD_TERMINALS:
        errors.append(f"unknown or non-child issue: {issue!r}")
        return errors
    allowed = CHILD_TERMINALS[issue]
    declared = child.get("allowed_terminals")
    if not isinstance(declared, list) or set(declared) != set(allowed):
        errors.append(f"#{issue} allowed_terminals must be exactly {sorted(allowed)}")

    state = child.get("current_state")
    if state not in IN_PROGRESS_STATES and state not in allowed:
        errors.append(f"#{issue} illegal current_state {state!r}")

    terminal = _terminal_class(str(state)) if isinstance(state, str) else None
    reached = child.get("scientific_terminal_reached")
    if terminal is None:
        if reached is not False:
            errors.append(f"#{issue} in-progress state must set scientific_terminal_reached=false")
    elif reached is not True:
        errors.append(f"#{issue} terminal state {state!r} must set scientific_terminal_reached=true")

    if child.get("engineering_complete_counts_as_scientific") is not False:
        errors.append(f"#{issue} engineering/PR green must not count as scientific completion")

    cannot_check = child.get("cannot_check")
    if not isinstance(cannot_check, list) or not all(_nonempty_str(item) for item in cannot_check):
        errors.append(f"#{issue} cannot_check must be a list of non-empty strings")
    elif state == CANNOT_CHECK_TERMINAL and not cannot_check:
        errors.append(f"#{issue} CANNOT_CHECK terminal requires a non-empty cannot_check list")

    if terminal is None and not _nonempty_str(child.get("next_discriminator")):
        errors.append(f"#{issue} in-progress child must declare next_discriminator")

    record_id = child.get("verification_record_id")
    if requires_verification_record(str(state)):
        if not _nonempty_str(record_id):
            errors.append(
                f"#{issue} {state} requires verification_record_id from issue #283"
            )
    elif record_id not in (None, ""):
        if not _nonempty_str(record_id):
            errors.append(f"#{issue} verification_record_id must be null or a non-empty string")

    if child.get("claimed_done_without_terminal") is True:
        errors.append(f"#{issue} must not claim done without a scientific terminal")
    return errors


def validate_tracker(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != TRACKER_SCHEMA_VERSION:
        errors.append("wrong programme tracker schema_version")
    if payload.get("parent_issue") != PARENT_ISSUE:
        errors.append("parent_issue must be 284")
    if payload.get("authority") != "PROGRAMME_INFRASTRUCTURE_ONLY":
        errors.append("tracker authority must remain PROGRAMME_INFRASTRUCTURE_ONLY")
    status = payload.get("programme_status")
    if status not in PROGRAMME_STATUSES:
        errors.append(f"invalid programme_status: {status!r}")

    children = payload.get("children")
    if not isinstance(children, list):
        errors.append("children must be a list")
        return errors
    issues = [child.get("issue") for child in children if isinstance(child, Mapping)]
    if tuple(issues) != REQUIRED_CHILDREN:
        errors.append(f"children must be exactly {list(REQUIRED_CHILDREN)} in that order")

    reached = 0
    for child in children:
        if not isinstance(child, Mapping):
            errors.append("each child must be an object")
            continue
        errors.extend(validate_child(child))
        if child.get("scientific_terminal_reached") is True:
            reached += 1

    complete = payload.get("scientific_children_complete")
    total = payload.get("scientific_children_total")
    if total != len(REQUIRED_CHILDREN):
        errors.append("scientific_children_total must be 10")
    if complete != reached:
        errors.append("scientific_children_complete must equal children at scientific terminals")
    if status == "CLOSED" and reached != len(REQUIRED_CHILDREN):
        errors.append("programme cannot CLOSE until every child reaches a scientific terminal")
    if status == "SCAFFOLDING_ONLY" and reached != 0:
        errors.append("SCAFFOLDING_ONLY forbids any child scientific terminal")
    if payload.get("claims_children_done") is True:
        errors.append("tracker must not claim children are done")
    return errors


def _progress_index(state: str) -> int:
    try:
        return PROGRESS_ORDER.index(state)
    except ValueError:
        return -1


def apply_transition(
    child: Mapping[str, Any],
    new_state: str,
    *,
    verification_record_id: str | None = None,
    cannot_check: Sequence[str] | None = None,
    next_discriminator: str | None = None,
) -> dict[str, Any]:
    """Return a successor child record, or raise TrackerError on illegal transition."""
    errors = validate_child(child)
    if errors:
        raise TrackerError("; ".join(errors))
    issue = child["issue"]
    allowed = CHILD_TERMINALS[issue]
    old_state = str(child["current_state"])
    if new_state not in IN_PROGRESS_STATES and new_state not in allowed:
        raise TrackerError(f"#{issue} {new_state!r} is not an allowed state")

    old_terminal = _terminal_class(old_state)
    new_terminal = _terminal_class(new_state)
    if old_terminal is not None:
        raise TrackerError(f"#{issue} already at terminal {old_state}; start a new protocol instead")

    old_idx = _progress_index(old_state)
    new_idx = _progress_index(new_state)

    if new_terminal is None:
        if new_idx < old_idx:
            raise TrackerError(f"#{issue} cannot move backwards from {old_state} to {new_state}")
        if new_state == "PROTOCOL_FROZEN" and old_idx < _progress_index("DISCRIMINATOR_FROZEN"):
            raise TrackerError(
                f"#{issue} cannot freeze a repair protocol before the discriminator is frozen"
            )
        if new_state == "EXECUTED" and old_idx < _progress_index("PROTOCOL_FROZEN"):
            raise TrackerError(f"#{issue} cannot execute before a new immutable protocol is frozen")
        if new_state == "INDEPENDENT_VERIFICATION_IN_PROGRESS" and old_idx < _progress_index(
            "EXECUTED"
        ):
            raise TrackerError(f"#{issue} cannot verify a result that has not been executed")
    else:
        if new_state in POSITIVE_TERMINALS:
            if old_state != "INDEPENDENT_VERIFICATION_IN_PROGRESS":
                raise TrackerError(
                    f"#{issue} {new_state} is illegal from {old_state}; "
                    "positive terminals require an independent verification step"
                )
            if not _nonempty_str(verification_record_id):
                raise TrackerError(
                    f"#{issue} {new_state} without verification_record_id is an illegal transition"
                )
        elif new_state in REFUTED_OR_BOUNDED_TERMINALS:
            if old_idx < _progress_index("EXECUTED"):
                raise TrackerError(
                    f"#{issue} {new_state} requires executed evidence, not a pre-result label"
                )
        elif new_state == CANNOT_CHECK_TERMINAL:
            reasons = list(cannot_check or child.get("cannot_check") or [])
            if not reasons:
                raise TrackerError(f"#{issue} CANNOT_CHECK requires an explicit reason list")

    updated: dict[str, Any] = dict(child)
    updated["current_state"] = new_state
    updated["scientific_terminal_reached"] = new_terminal is not None
    if verification_record_id is not None:
        updated["verification_record_id"] = verification_record_id
    if cannot_check is not None:
        updated["cannot_check"] = list(cannot_check)
    if next_discriminator is not None:
        updated["next_discriminator"] = next_discriminator
    elif new_terminal is not None:
        updated["next_discriminator"] = None
    errors = validate_child(updated)
    if errors:
        raise TrackerError("; ".join(errors))
    return updated


def validate_doctrine(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != DOCTRINE_SCHEMA_VERSION:
        errors.append("wrong doctrine schema_version")
    if payload.get("status") != "IN_FORCE":
        errors.append("doctrine protocol must be IN_FORCE")
    if payload.get("outcome_tuning_permitted") is not False:
        errors.append("outcome tuning must be forbidden")
    checks = payload.get("checks")
    if not isinstance(checks, Mapping):
        errors.append("doctrine checks object is required")
        return errors
    for key in DOCTRINE_REQUIRED_TRUE:
        if checks.get(key) is not True:
            errors.append(f"doctrine check {key} must be true")
    for key in DOCTRINE_REQUIRED_FALSE:
        if checks.get(key) is not False:
            errors.append(f"doctrine check {key} must be false")
    rules = payload.get("rules")
    if not isinstance(rules, list) or len(rules) < 5:
        errors.append("doctrine must enumerate the five constitutional rules")
    else:
        required_ids = {
            "NEVER_TUNE_OUTCOME_POSITIVE",
            "ONE_STAGE_ATTRIBUTION",
            "FREEZE_DISCRIMINATOR_BEFORE_REPAIR",
            "NEW_IMMUTABLE_PROTOCOL",
            "PRESERVE_NEGATIVE_HISTORY",
        }
        found = {rule.get("id") for rule in rules if isinstance(rule, Mapping)}
        missing = sorted(required_ids - found)
        if missing:
            errors.append("doctrine missing rules: " + ", ".join(missing))
        for rule in rules:
            if isinstance(rule, Mapping) and rule.get("enforced") is not True:
                errors.append(f"doctrine rule {rule.get('id')} must be enforced")
    return errors


def validate_novelty(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != NOVELTY_SCHEMA_VERSION:
        errors.append("wrong novelty schema_version")
    if payload.get("authority") != "CERTIFICATES_TO_BE_NOT_CLAIMED_NOVELTY":
        errors.append("novelty document must not claim novelty")
    hypotheses = payload.get("hypotheses")
    if not isinstance(hypotheses, list):
        errors.append("hypotheses must be a list")
        return errors
    ids = [item.get("id") for item in hypotheses if isinstance(item, Mapping)]
    if ids[:4] != ["N1", "N2", "N3", "N4"]:
        errors.append("N1-N4 must be present in order as certificates-to-be")
    for item in hypotheses:
        if not isinstance(item, Mapping):
            errors.append("each hypothesis must be an object")
            continue
        hid = item.get("id")
        if item.get("claimed_novelty") is not False:
            errors.append(f"{hid} must set claimed_novelty=false")
        if item.get("status") != "CANDIDATE_CERTIFICATE_TO_BE":
            errors.append(f"{hid} status must be CANDIDATE_CERTIFICATE_TO_BE")
        if not _nonempty_str(item.get("pointer")):
            errors.append(f"{hid} must be a pointer, not a claim")
        if item.get("certificate_id") not in (None, ""):
            errors.append(f"{hid} must not mint a certificate_id before #287/#283 terminate")
    return errors


def validate_corrections(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != CORRECTIONS_SCHEMA_VERSION:
        errors.append("wrong corrections schema_version")
    facts = payload.get("facts")
    if not isinstance(facts, Mapping):
        errors.append("corrections facts object is required")
        return errors
    p4 = facts.get("p4_v2")
    if not isinstance(p4, Mapping) or p4.get("terminal") != "PEER_REVIEW_READY":
        errors.append("corrections must record P4 V2 as PEER_REVIEW_READY")
    if isinstance(p4, Mapping) and p4.get("hostile_battery_never_run") is not False:
        errors.append("corrections must not list the P4 hostile battery as never run")
    p1 = facts.get("p1_power")
    if not isinstance(p1, Mapping):
        errors.append("corrections must record distinct P1 H1/H2 power requirements")
    else:
        if p1.get("h1_required_n") != 385:
            errors.append("P1 H1 required n must be 385")
        if p1.get("h2_required_n") != 2401:
            errors.append("P1 H2 required n must be 2401, not the H1 n=385 tier")
        if p1.get("h1_and_h2_power_identical") is not False:
            errors.append("H1 and H2 power requirements must be marked distinct")
    if facts.get("post_outcome_margin_relaxation") is not False:
        errors.append("post-outcome margin relaxation must remain forbidden")
    p5 = facts.get("p5_attribution")
    if not isinstance(p5, Mapping) or p5.get("correct") != "21/24" or p5.get("stale") != "24/24":
        errors.append("corrections must record P5 attribution as 21/24, not 24/24")
    return errors


def scan_text_for_stale_claims(text: str, *, path: str) -> list[str]:
    errors: list[str] = []
    for pattern in STALE_CLAIMS:
        if pattern.search(text):
            errors.append(f"{path} contains stale claim matching {pattern.pattern}")
    return errors


def validate_tree(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    tracker = load_json(base / "PROGRAMME_TRACKER_V1.json")
    doctrine = load_json(base / "CONSTITUTIONAL_DOCTRINE_V1.json")
    novelty = load_json(base / "NOVELTY_HYPOTHESES_V1.json")
    corrections = load_json(base / "CORRECTIONS_V1.json")
    errors = [
        *validate_tracker(tracker),
        *validate_doctrine(doctrine),
        *validate_novelty(novelty),
        *validate_corrections(corrections),
    ]
    for rel in (
        "README.md",
        "CONSTITUTIONAL_DOCTRINE_V1.md",
        "CORRECTIONS_AGAINST_MAIN_V1.md",
        "REVIVAL_BACKLOG_SUCCESSOR_V1.md",
    ):
        path = base / rel
        if path.exists():
            errors.extend(scan_text_for_stale_claims(path.read_text(encoding="utf-8"), path=rel))
    return {
        "valid": not errors,
        "errors": errors,
        "scientific_children_complete": tracker.get("scientific_children_complete"),
        "programme_status": tracker.get("programme_status"),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=ROOT)
    return parser


def main() -> None:
    args = _parser().parse_args()
    report = validate_tree(args.root)
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["valid"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
