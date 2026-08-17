"""Step-6 longitudinal sustainability evidence — schema, not data.

The eight longitudinal claims in issue #210 are represented as fields. Every
field defaults to ``CANNOT_CHECK``. A report that claims improvement, coverage
expansion, or envelope compliance without epoch snapshots is refused. The
module cannot close Phase 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orion.programme.activation import BLOCKING_DEPENDENCIES, PREPARATORY_STATUS
from orion.programme.identity import seal
from orion.programme.records import Outcome

LONGITUDINAL_SCHEMA = "orion.programme.longitudinal-evidence.v1"

LONGITUDINAL_CLAIMS: tuple[str, ...] = (
    "multiple_evaluation_epochs",
    "object_knowledge_quality_trend",
    "search_universe_coverage_trend",
    "method_selection_without_fresh_transfer_regression",
    "worst_family_worst_epoch_regressions_reported",
    "cost_latency_within_sustainability_envelope",
    "host_can_halt_and_reconstruct_prior_state",
    "independent_audit_validates_conclusions",
)


@dataclass(frozen=True)
class LongitudinalEvidence:
    """Longitudinal claims. Absence is ``CANNOT_CHECK``; fabrication is ``FAIL``."""

    epoch_count: int = 0
    claims: tuple[tuple[str, Outcome], ...] = tuple(
        (claim, Outcome.CANNOT_CHECK) for claim in LONGITUDINAL_CLAIMS
    )

    @property
    def grants_phase4_closure(self) -> bool:
        return False


def longitudinal_payload(evidence: LongitudinalEvidence) -> dict[str, Any]:
    return seal(
        {
            "schema_version": LONGITUDINAL_SCHEMA,
            "programme_status": PREPARATORY_STATUS,
            "blocking_dependencies": list(BLOCKING_DEPENDENCIES),
            "epoch_count": evidence.epoch_count,
            "claims": {name: outcome.value for name, outcome in evidence.claims},
            "grants_phase4_closure": evidence.grants_phase4_closure,
            "evidence_status": "NO_PROTECTED_EVIDENCE",
        }
    )


def validate_longitudinal_evidence(evidence: LongitudinalEvidence) -> tuple[str, ...]:
    errors: list[str] = []
    listed = tuple(name for name, _ in evidence.claims)
    if listed != LONGITUDINAL_CLAIMS:
        errors.append("longitudinal claims do not match the frozen eight-claim set")
    if evidence.epoch_count < 0:
        errors.append("epoch_count must be non-negative")
    if evidence.epoch_count == 0:
        for name, outcome in evidence.claims:
            if outcome is Outcome.PASS:
                errors.append(f"{name} cannot PASS with zero evaluation epochs")
    if any(outcome is Outcome.PASS for _, outcome in evidence.claims) and evidence.epoch_count < 2:
        errors.append("longitudinal PASS requires multiple evaluation epochs")
    return tuple(dict.fromkeys(errors))


def assess_longitudinal(evidence: LongitudinalEvidence | None = None) -> Outcome:
    """Preparatory scaffolding cannot certify longitudinal success.

    Validation of a caller-supplied record is separate
    (``validate_longitudinal_evidence``). This function never returns ``PASS``.
    """

    current = evidence if evidence is not None else LongitudinalEvidence()
    validate_longitudinal_evidence(current)
    return Outcome.CANNOT_CHECK


def unexecuted_longitudinal_evidence() -> LongitudinalEvidence:
    return LongitudinalEvidence()


__all__ = [
    "LONGITUDINAL_CLAIMS",
    "LONGITUDINAL_SCHEMA",
    "LongitudinalEvidence",
    "assess_longitudinal",
    "longitudinal_payload",
    "unexecuted_longitudinal_evidence",
    "validate_longitudinal_evidence",
]
