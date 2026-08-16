from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from .store import canonical_bytes


class HardGateState(str, Enum):
    """The three outcomes a blocking gate may report.

    CANNOT_CHECK is not a soft FAIL and must never be folded into one. A gate
    nobody observed and a gate observed to fail call for different actions — go
    and measure, versus stop — and collapsing them loses exactly the distinction
    that makes the gate worth having.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class HardGateRequirement:
    """One blocking condition. Not a metric: it has no scale to trade against."""

    gate_id: str
    description: str
    evidence_required: bool = True

    def __post_init__(self) -> None:
        if not self.gate_id.strip() or not self.description.strip():
            raise ValueError("a gate requirement needs an id and a description")


@dataclass(frozen=True)
class HardGateContract:
    """The set of blocking conditions, frozen before results are read.

    RAKL carried chronology as a declared tri-state boolean —
    `frozen_before_candidate_results` — which the contract's own author set.
    ORION pins it to a round index instead, matching how a DiscriminatingCheck
    proves it predates the answer it judges. A contract written after seeing the
    results is a description of those results.
    """

    contract_id: str
    requirements: tuple[HardGateRequirement, ...]
    frozen_at_round: int | None = None

    def __post_init__(self) -> None:
        if not self.contract_id.strip():
            raise ValueError("a gate contract needs an id")
        if not self.requirements:
            raise ValueError("a gate contract with no requirements gates nothing")
        ids = [item.gate_id for item in self.requirements]
        if len(set(ids)) != len(ids):
            raise ValueError("gate ids must be unique within a contract")

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            canonical_bytes(
                {
                    "contract_id": self.contract_id,
                    "requirements": [
                        [item.gate_id, item.description, item.evidence_required]
                        for item in self.requirements
                    ],
                    "frozen_at_round": self.frozen_at_round,
                }
            )
        ).hexdigest()

    def predates(self, round_index: int) -> bool:
        """Unknown chronology is never treated as satisfied."""

        return self.frozen_at_round is not None and self.frozen_at_round <= round_index


@dataclass(frozen=True)
class HardGateObservation:
    """One measurement of one gate, bound to the contract it was made under."""

    gate_id: str
    subject_id: str
    state: HardGateState
    contract_fingerprint: str
    evidence_ids: tuple[str, ...] = ()
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.gate_id.strip() or not self.subject_id.strip():
            raise ValueError("an observation needs a gate id and a subject")
        if not self.contract_fingerprint.strip():
            raise ValueError(
                "an observation must name the contract it was made under, or it "
                "can be replayed against a contract that was edited afterwards"
            )


@dataclass(frozen=True)
class HardGateReport:
    state: HardGateState
    reasons: tuple[str, ...] = ()
    passed_gate_ids: tuple[str, ...] = ()
    failed_gate_ids: tuple[str, ...] = ()
    unresolved_gate_ids: tuple[str, ...] = ()

    @property
    def permits_closure(self) -> bool:
        """Deliberately the only boolean here, and it is not a score.

        There is no aggregate, ratio or count of passes on this report, because
        any such field invites the substitution the gate exists to refuse: a
        blocking condition cannot be outweighed by other conditions passing.
        """

        return self.state is HardGateState.PASS


def evaluate_hard_gates(
    contract: HardGateContract,
    observations: Sequence[HardGateObservation],
    *,
    subject_id: str,
    round_index: int,
) -> HardGateReport:
    """Evaluate blocking gates non-compensatorily, failing closed throughout.

    Ported from RAKL's hard-gate evaluator, which ORION had declared and never
    implemented: `MetricDirection.NON_COMPENSATORY_GATE` existed as an enum
    member that no code branched on, so a declared blocking gate could not
    actually block anything.

    Order matters. Admissibility is settled before any observation is read: a
    contract with unknown chronology, or one edited after the results it judges,
    is refused before its numbers are consulted. An inadmissible measurement is
    not a low measurement.
    """

    if contract.frozen_at_round is None:
        return HardGateReport(
            HardGateState.CANNOT_CHECK,
            ("gate_contract_chronology_unknown",),
        )
    if not contract.predates(round_index):
        return HardGateReport(
            HardGateState.FAIL,
            (f"gate_contract_frozen_after_round:{round_index}",),
            failed_gate_ids=("CONTRACT_INTEGRITY",),
        )

    relevant = [item for item in observations if item.subject_id == subject_id]
    stale = [
        item.gate_id
        for item in relevant
        if item.contract_fingerprint != contract.fingerprint
    ]
    if stale:
        return HardGateReport(
            HardGateState.FAIL,
            tuple(f"observation_under_a_different_contract:{item}" for item in stale),
            failed_gate_ids=("CONTRACT_INTEGRITY",),
        )

    passed: list[str] = []
    failed: list[str] = []
    unresolved: list[str] = []
    reasons: list[str] = []

    for requirement in contract.requirements:
        matching = [item for item in relevant if item.gate_id == requirement.gate_id]
        if not matching:
            unresolved.append(requirement.gate_id)
            reasons.append(f"gate_unobserved:{requirement.gate_id}")
            continue
        states = {item.state for item in matching}
        if len(states) > 1:
            # Never last-write-wins: two measurements disagreeing about a
            # blocking condition is a reason to stop, not to pick one.
            failed.append(requirement.gate_id)
            reasons.append(f"gate_observations_conflict:{requirement.gate_id}")
            continue
        state = states.pop()
        if state is HardGateState.FAIL:
            failed.append(requirement.gate_id)
            reasons.append(f"gate_failed:{requirement.gate_id}")
            continue
        if state is HardGateState.CANNOT_CHECK:
            unresolved.append(requirement.gate_id)
            reasons.append(f"gate_cannot_check:{requirement.gate_id}")
            continue
        if requirement.evidence_required and not any(
            item.evidence_ids for item in matching
        ):
            unresolved.append(requirement.gate_id)
            reasons.append(f"gate_passed_without_evidence:{requirement.gate_id}")
            continue
        passed.append(requirement.gate_id)

    if failed:
        state = HardGateState.FAIL
    elif unresolved:
        state = HardGateState.CANNOT_CHECK
    else:
        state = HardGateState.PASS

    return HardGateReport(
        state=state,
        reasons=tuple(reasons),
        passed_gate_ids=tuple(passed),
        failed_gate_ids=tuple(failed),
        unresolved_gate_ids=tuple(unresolved),
    )
