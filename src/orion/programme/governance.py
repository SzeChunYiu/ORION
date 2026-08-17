"""Step-3 programme governance freeze — record shape only, not a live freeze.

Pre-registering the policy surface while #209 is open is legitimate.
Pre-registering a bound host identity or a claimed freeze-in-force would be
fabrication. Every external identity here is the unbound sentinel; every
``grants_*`` property is hardwired ``False``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orion.programme.activation import (
    BLOCKING_DEPENDENCIES,
    PREPARATORY_STATUS,
    UNBOUND_DIGEST,
)
from orion.programme.identity import is_sha256, seal
from orion.programme.records import required_text_errors

GOVERNANCE_SCHEMA = "orion.programme.governance-freeze.v1"
GOVERNANCE_FREEZE_ID = "phase4:governance-freeze:preparatory-v1"


@dataclass(frozen=True)
class GovernanceFreeze:
    """Declared programme governance. Inert until an external host binds it."""

    freeze_id: str
    objectives: tuple[str, ...]
    research_question_queue_policy: tuple[str, ...]
    exploration_exploitation_policy: tuple[str, ...]
    budget_ceilings: tuple[tuple[str, str], ...]
    stop_rules: tuple[str, ...]
    protected_benchmark_families: tuple[str, ...]
    held_out_refresh_policy: tuple[str, ...]
    evaluator_custody_policy: tuple[str, ...]
    evaluator_versioning_policy: tuple[str, ...]
    search_web_contamination_policy: tuple[str, ...]
    halt_revert_conditions: tuple[str, ...]
    host_authority_id: str = ""
    evaluator_artifact_hash: str = UNBOUND_DIGEST
    held_out_split_hash: str = UNBOUND_DIGEST
    programme_status: str = PREPARATORY_STATUS

    @property
    def grants_self_sustaining_authority(self) -> bool:
        return False

    @property
    def grants_phase4_closure(self) -> bool:
        return False

    @property
    def freeze_in_force(self) -> bool:
        return False


def repository_governance_freeze() -> GovernanceFreeze:
    """The repository's pre-registered governance document."""

    return GovernanceFreeze(
        freeze_id=GOVERNANCE_FREEZE_ID,
        objectives=(
            "Co-evolve object, search-universe and method knowledge under protected evaluation.",
            "Keep external authority able to halt, reopen, audit and revert programme state.",
            "Never convert missing evidence into a positive conclusion.",
        ),
        research_question_queue_policy=(
            "Questions are selected from auditable programme state, never from candidate whim.",
            "The queue is append-only; withdrawn questions remain as negative or null history.",
            "Protected or constitutional questions are excluded from candidate-owned cycles.",
        ),
        exploration_exploitation_policy=(
            "Exploration is obligated where coverage, blind spots or unresolved contradictions exist.",
            "Exploitation of a method requires replay plus independent fresh transfer.",
            "Exploitation cannot retire an unexamined source family or failure class.",
        ),
        budget_ceilings=(
            ("wall_clock_per_cycle", "host-bound"),
            ("llm_calls_per_cycle", "host-bound"),
            ("compute_units_per_epoch", "host-bound"),
            ("host_interventions_per_cycle", "host-bound"),
        ),
        stop_rules=(
            "Stop the cycle on CANNOT_CHECK, OPEN, or insufficient protected evidence.",
            "Stop the programme on host halt, evaluator-custody breach, or budget exhaustion.",
            "Stop rules are not overridable by programme pressure or candidate output.",
        ),
        protected_benchmark_families=(
            "held-out evaluation families outside candidate custody",
            "fresh-transfer families disjoint from motivating replay",
            "worst-family / worst-epoch regression panels",
        ),
        held_out_refresh_policy=(
            "Refresh is a host action, never a candidate action.",
            "A refresh produces a new epoch; it does not rewrite a prior epoch.",
            "Labels of a held-out family are unreadable to candidate and worker processes.",
        ),
        evaluator_custody_policy=(
            "Evaluator custody is EXTERNAL.",
            "Candidate and LLM processes have no writer for evaluators, held-outs, or phase rules.",
            "Any evaluator swap must be a typed reopen event, not an in-place edit.",
        ),
        evaluator_versioning_policy=(
            "Every epoch binds an evaluator artifact hash.",
            "A hash change without a matching reopen event is HC-EVALUATOR-GAMING.",
            "Versioning is content-addressed; names are not identities.",
        ),
        search_web_contamination_policy=(
            "Search and web retrieval cannot read held-out labels or protected evaluator internals.",
            "Retrieved evidence binds source_id, source_uri, source_family and source_version.",
            "Unversioned retrieval is unevaluable and blocks promotion.",
        ),
        halt_revert_conditions=(
            "External host halt is immediate and does not require candidate consent.",
            "Revert reconstructs any prior sealed programme state from the reopen ledger.",
            "Audit access is host-owned and outside candidate custody.",
        ),
    )


def governance_payload(freeze: GovernanceFreeze) -> dict[str, Any]:
    """Sealed wire form. A consumer that reads only JSON still sees the inertness."""

    return seal(
        {
            "schema_version": GOVERNANCE_SCHEMA,
            "freeze_id": freeze.freeze_id,
            "programme_status": freeze.programme_status,
            "blocking_dependencies": list(BLOCKING_DEPENDENCIES),
            "authority_granted": False,
            "freeze_in_force": freeze.freeze_in_force,
            "grants_self_sustaining_authority": freeze.grants_self_sustaining_authority,
            "grants_phase4_closure": freeze.grants_phase4_closure,
            "host_authority_id": freeze.host_authority_id,
            "evaluator_artifact_hash": freeze.evaluator_artifact_hash,
            "held_out_split_hash": freeze.held_out_split_hash,
            "objectives": list(freeze.objectives),
            "research_question_queue_policy": list(freeze.research_question_queue_policy),
            "exploration_exploitation_policy": list(freeze.exploration_exploitation_policy),
            "budget_ceilings": {key: value for key, value in freeze.budget_ceilings},
            "stop_rules": list(freeze.stop_rules),
            "protected_benchmark_families": list(freeze.protected_benchmark_families),
            "held_out_refresh_policy": list(freeze.held_out_refresh_policy),
            "evaluator_custody_policy": list(freeze.evaluator_custody_policy),
            "evaluator_versioning_policy": list(freeze.evaluator_versioning_policy),
            "search_web_contamination_policy": list(freeze.search_web_contamination_policy),
            "halt_revert_conditions": list(freeze.halt_revert_conditions),
        }
    )


def validate_governance_payload(document: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(required_text_errors(document.get("freeze_id"), "freeze_id"))
    if document.get("schema_version") != GOVERNANCE_SCHEMA:
        errors.append("governance schema_version mismatch")
    if document.get("programme_status") != PREPARATORY_STATUS:
        errors.append("governance document must declare PREPARATORY_AWAITING_ACTIVATION")
    if document.get("authority_granted") is not False:
        errors.append("governance document must not grant authority")
    if document.get("freeze_in_force") is not False:
        errors.append("governance freeze is not in force while activation is withheld")
    if document.get("grants_self_sustaining_authority") is not False:
        errors.append("governance document must not grant self-sustaining authority")
    if document.get("grants_phase4_closure") is not False:
        errors.append("governance document must not grant Phase-4 closure")
    if document.get("host_authority_id"):
        errors.append("host_authority_id must remain unbound until an external host binds it")
    for field_name in ("evaluator_artifact_hash", "held_out_split_hash"):
        value = document.get(field_name)
        if not is_sha256(value):
            errors.append(f"{field_name} must be a SHA-256 digest")
        elif value != UNBOUND_DIGEST:
            errors.append(f"{field_name} must remain the unbound sentinel until a host binds it")
    missing = [
        name
        for name in (
            "objectives",
            "research_question_queue_policy",
            "exploration_exploitation_policy",
            "budget_ceilings",
            "stop_rules",
            "protected_benchmark_families",
            "held_out_refresh_policy",
            "evaluator_custody_policy",
            "evaluator_versioning_policy",
            "search_web_contamination_policy",
            "halt_revert_conditions",
        )
        if not document.get(name)
    ]
    errors.extend(f"governance field {name} is empty" for name in missing)
    return tuple(dict.fromkeys(errors))


__all__ = [
    "GOVERNANCE_FREEZE_ID",
    "GOVERNANCE_SCHEMA",
    "GovernanceFreeze",
    "governance_payload",
    "repository_governance_freeze",
    "validate_governance_payload",
]
