from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class EngineeringConcern(str, Enum):
    DETERMINISM_REPLAY = "DETERMINISM_REPLAY"
    IDEMPOTENCY_SIDE_EFFECTS = "IDEMPOTENCY_SIDE_EFFECTS"
    CONCURRENCY = "CONCURRENCY"
    TIMEOUT_CANCELLATION = "TIMEOUT_CANCELLATION"
    RECOVERY_CHECKPOINT = "RECOVERY_CHECKPOINT"
    VERSION_CONFIGURATION = "VERSION_CONFIGURATION"
    OBSERVABILITY = "OBSERVABILITY"
    PERFORMANCE_SLO = "PERFORMANCE_SLO"
    SCHEMA_VALIDATION = "SCHEMA_VALIDATION"
    SECURITY_PRIVILEGE = "SECURITY_PRIVILEGE"
    TESTING_FAULT_INJECTION = "TESTING_FAULT_INJECTION"


@dataclass(frozen=True)
class EngineeringRequirement:
    requirement_id: str
    mechanic_id: str
    concern: EngineeringConcern
    contract: str
    failure_semantics: str
    verification_artifact: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.requirement_id, self.mechanic_id, self.contract, self.failure_semantics, self.verification_artifact)):
            raise ValueError("engineering requirement fields cannot be empty")


def default_engineering_requirements(cell: MechanicCell) -> tuple[EngineeringRequirement, ...]:
    def req(concern: EngineeringConcern, contract: str, failure: str, artifact: str) -> EngineeringRequirement:
        return EngineeringRequirement(f"engineering:{cell.mechanic_id}:{concern.value.lower()}", cell.mechanic_id, concern, contract, failure, artifact)

    return (
        req(EngineeringConcern.DETERMINISM_REPLAY, "Declare which computations are deterministic. Replayable paths bind exact input/state/config/provider/tool identities and reproduce the same canonical receipt or explicitly record stochastic variation.", "A promised deterministic/replay path producing unbound or inconsistent output is an execution defect.", "replay/conformance receipt"),
        req(EngineeringConcern.IDEMPOTENCY_SIDE_EFFECTS, "External side effects use idempotency keys/transactional or receipt guards; terminal receipts are replayed instead of blindly repeating an effect.", "Ambiguous side-effect completion fails closed pending reconciliation.", "side-effect/idempotency test"),
        req(EngineeringConcern.CONCURRENCY, "Concurrent work must declare shared state, synchronization/merge policy and ordering assumptions; independent work may parallelize only where writes/authority cannot race.", "Race-induced state/provenance ambiguity invalidates the affected run/receipt.", "concurrency/race test"),
        req(EngineeringConcern.TIMEOUT_CANCELLATION, "Long-running provider/tool/actions have explicit timeout/cancellation semantics and distinguish cancellation from scientific failure.", "Timeout with open obligations becomes resource-bound CANNOT_CHECK/BLOCKED as appropriate.", "timeout/cancellation hostile test"),
        req(EngineeringConcern.RECOVERY_CHECKPOINT, "Checkpoint/recovery binds state/event identities and never assumes an external side effect did not occur after an ambiguous crash.", "Uncertain recovery state is quarantined until reconciled.", "crash/recovery test"),
        req(EngineeringConcern.VERSION_CONFIGURATION, "Mechanic code, schemas, prompts/config, model/provider/tool/data/evaluator versions material to behavior are bound to run identity.", "Untracked configuration drift invalidates strict replay/comparison claims.", "configuration/attestation receipt"),
        req(EngineeringConcern.OBSERVABILITY, "Status, latency, cost, residuals, evidence/provenance and handoff presence are emitted with stable semantic identities.", "Missing mandatory telemetry/receipt fields block observability-dependent verification rather than being silently ignored.", "observability schema test"),
        req(EngineeringConcern.PERFORMANCE_SLO, "Declare latency/throughput/queue/resource SLOs only where operational decisions depend on them; performance is evaluated under preserved correctness/authority gates.", "SLO improvement cannot compensate for correctness/validity regressions.", "load/performance receipt"),
        req(EngineeringConcern.SCHEMA_VALIDATION, "All typed inputs/outputs/handoffs/receipts are validated against versioned schemas with explicit required-field and compatibility semantics.", "Invalid/missing required fields fail the interface closed.", "schema/compatibility test"),
        req(EngineeringConcern.SECURITY_PRIVILEGE, "Providers/tools/storage receive the minimum capability required for the declared action; untrusted content cannot silently acquire code/tool/authority write privileges.", "Privilege/capability violation blocks the action and is preserved as a security failure episode.", "capability/permission hostile test"),
        req(EngineeringConcern.TESTING_FAULT_INJECTION, "Maintain unit, known-answer, hostile, integration and fresh-transfer tests; inject dependency, malformed-input, timeout, partial-output and side-effect ambiguity failures where relevant.", "A mechanic without tested failure paths cannot claim implementation robustness.", "test/fault-injection ledger"),
    )


def apply_default_engineering_contract(cell: MechanicCell) -> MechanicCell:
    requirements = default_engineering_requirements(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific concurrency/load/SLO/security/fault model, provider limitations, operational failure rates and production recovery evidence",)))
    return replace(
        cell,
        engineering_contracts=tuple(f"{item.requirement_id}:{item.contract}:failure={item.failure_semantics}:verify={item.verification_artifact}" for item in requirements),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_engineering_contracts(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_engineering_contract(cell) for cell in cells)
