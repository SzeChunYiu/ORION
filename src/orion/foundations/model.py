"""Typed finite objects for the ORION Scientific Transition Calculus.

This module deliberately contains no paper-specific decision code.  It is a
small, executable language in which the local theorem tranche can be stated and
falsified.  The objects are finite and hashable so exhaustive model checking is
possible without external services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Hashable, Iterable, Mapping


class Terminal(str, Enum):
    ESTABLISH = "ESTABLISH"
    RETAIN = "RETAIN"
    REOPEN = "REOPEN"
    CONTINUE = "CONTINUE"
    BLOCK = "BLOCK"
    DENY = "DENY"
    CANNOT_CHECK = "CANNOT_CHECK"


class ObligationStatus(str, Enum):
    OPEN = "OPEN"
    DISCHARGED = "DISCHARGED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"
    REVOKED = "REVOKED"


class EventKind(str, Enum):
    OBSERVE = "OBSERVE"
    ACQUIRE = "ACQUIRE"
    RETRIEVE = "RETRIEVE"
    EXECUTE = "EXECUTE"
    VERIFY_NATIVE = "VERIFY_NATIVE"
    INFER = "INFER"
    MAP = "MAP"
    MERGE = "MERGE"
    SPLIT = "SPLIT"
    REFRAME = "REFRAME"
    REVISE = "REVISE"
    OPEN_OBLIGATION = "OPEN_OBLIGATION"
    DISCHARGE = "DISCHARGE"
    BLOCK = "BLOCK"
    REVOKE = "REVOKE"
    TRANSPORT = "TRANSPORT"
    REVALIDATE = "REVALIDATE"
    DELEGATE = "DELEGATE"
    COERCE = "COERCE"
    PROPOSE_CHANGE = "PROPOSE_CHANGE"
    ISOLATE = "ISOLATE"
    REPLAY = "REPLAY"
    FRESH_TRANSFER = "FRESH_TRANSFER"
    ADOPT_EXTERNAL = "ADOPT_EXTERNAL"
    PUBLISH = "PUBLISH"
    INVALIDATE = "INVALIDATE"
    EPOCH_CHANGE = "EPOCH_CHANGE"


@dataclass(frozen=True, order=True)
class ScientificObject:
    object_id: str
    domain: str
    kind: str
    scope: str
    content_identity: str
    epoch: str


@dataclass(frozen=True, order=True)
class Responsibility:
    responsibility_id: str
    target: ScientificObject
    question: str
    required_resolution: str
    loss_contract: str
    authority_class: str


@dataclass(frozen=True, order=True)
class Judgment:
    target: ScientificObject
    responsibility: Responsibility
    terminal: Terminal


@dataclass(frozen=True, order=True)
class ExecutionIntegrity:
    attributable: bool = False
    occurrence_bound: bool = False
    content_bound: bool = False
    environment_bound: bool = False
    chronology_valid: bool = False
    replayable: bool = False
    cross_implementation_agreement: bool = False
    attested: bool = False
    custody_bound: bool = False
    freshness_bound: bool = False

    def satisfies(self, required: Iterable[str]) -> bool:
        return all(bool(getattr(self, name)) for name in required)


@dataclass(frozen=True, order=True)
class Artifact:
    artifact_id: str
    subject: ScientificObject
    native_type: str
    content_identity: str
    native_valid: bool
    issuer: str
    provenance: str
    epoch: str
    execution_occurrence: str
    authority_signature: str
    integrity: ExecutionIntegrity = field(default_factory=ExecutionIntegrity)


@dataclass(frozen=True, order=True)
class Obligation:
    obligation_id: str
    target_judgment: Judgment
    predicate: str
    obligation_kind: str
    required_authority: str
    status: ObligationStatus
    dependencies: frozenset[str] = frozenset()


@dataclass(frozen=True, order=True)
class SupportFamily:
    family_id: str
    target_judgment: Judgment
    artifact_ids: frozenset[str]
    bridge_ids: frozenset[str]
    authority_ids: frozenset[str]
    blocker_ids: frozenset[str] = frozenset()


@dataclass(frozen=True, order=True)
class BridgeRule:
    bridge_id: str
    premise_judgments: frozenset[str]
    target_judgment: str
    target_object: ScientificObject
    responsibility_id: str
    required_authority: str
    scope: str
    epoch: str
    sound: bool = True


@dataclass(frozen=True, order=True)
class ResourceVector:
    acquisition: Fraction = Fraction(0)
    accessibility: Fraction = Fraction(0)
    compilation: Fraction = Fraction(0)
    state: Fraction = Fraction(0)
    inference: Fraction = Fraction(0)
    verification: Fraction = Fraction(0)
    cache: Fraction = Fraction(0)
    recovery: Fraction = Fraction(0)
    latency: Fraction = Fraction(0)

    def as_tuple(self) -> tuple[Fraction, ...]:
        return (
            self.acquisition,
            self.accessibility,
            self.compilation,
            self.state,
            self.inference,
            self.verification,
            self.cache,
            self.recovery,
            self.latency,
        )

    def __add__(self, other: ResourceVector) -> ResourceVector:
        values = (a + b for a, b in zip(self.as_tuple(), other.as_tuple(), strict=True))
        return ResourceVector(*values)

    def weighted_cost(self, prices: ResourceVector) -> Fraction:
        return sum(
            (
                quantity * price
                for quantity, price in zip(self.as_tuple(), prices.as_tuple(), strict=True)
            ),
            Fraction(0),
        )

    def weakly_dominates(self, other: ResourceVector) -> bool:
        return all(a <= b for a, b in zip(self.as_tuple(), other.as_tuple(), strict=True))


@dataclass(frozen=True)
class ScientificState:
    state_id: str
    knowledge: frozenset[str] = frozenset()
    world_model: frozenset[str] = frozenset()
    method_state: frozenset[str] = frozenset()
    regime: str = "default"
    responsibilities: frozenset[str] = frozenset()
    interface_value: Hashable | None = None
    method_language: frozenset[str] = frozenset()
    artifacts: tuple[Artifact, ...] = ()
    obligations: tuple[Obligation, ...] = ()
    support_families: tuple[SupportFamily, ...] = ()
    bridge_rules: tuple[BridgeRule, ...] = ()
    authorities: frozenset[str] = frozenset()
    blockers: Mapping[str, ObligationStatus] = field(default_factory=dict)
    execution: ExecutionIntegrity = field(default_factory=ExecutionIntegrity)
    negative_history: tuple[str, ...] = ()
    resources: ResourceVector = field(default_factory=ResourceVector)


@dataclass(frozen=True, order=True)
class Event:
    event_id: str
    kind: EventKind
    target_judgment: Judgment | None = None
    artifact_ids: frozenset[str] = frozenset()
    bridge_id: str | None = None
    authority_id: str | None = None
    support_family_id: str | None = None
    note: str = ""
