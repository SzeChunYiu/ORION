from __future__ import annotations

from dataclasses import dataclass

from orion.core.state import OrionState


@dataclass(frozen=True)
class SaturationAssessment:
    bounded_closed: bool
    flat_suffix: int
    reasons: tuple[str, ...]


class SaturateOperator:
    operator_id = "SATURATE_BOUNDED.v1"

    def assess(self, state: OrionState, *, required_flat_rounds: int = 2) -> SaturationAssessment:
        reasons: list[str] = []
        if any(residual.material for residual in state.knowledge.residuals):
            reasons.append("material_residual_open")
        if any(not certificate.stale for certificate in state.closure_certificates) is False and state.closure_certificates:
            reasons.append("all_closure_certificates_stale")

        flat_suffix = 0
        for record in reversed(state.iterations):
            if record.flat:
                flat_suffix += 1
            else:
                break
        if flat_suffix < required_flat_rounds:
            reasons.append("insufficient_flat_suffix")

        return SaturationAssessment(
            bounded_closed=not reasons,
            flat_suffix=flat_suffix,
            reasons=tuple(reasons),
        )
