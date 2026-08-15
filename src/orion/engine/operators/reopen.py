from __future__ import annotations

from dataclasses import replace

from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition


class ReopenOperator:
    operator_id = "REOPEN.v1"

    def run(
        self,
        state: OrionState,
        *,
        changed_coordinates: tuple[str, ...],
        reason: str,
    ) -> OperatorResult[tuple[str, ...]]:
        changed = set(changed_coordinates)
        stale_ids: list[str] = []
        certificates = []
        for certificate in state.closure_certificates:
            if changed.intersection(certificate.dependency_coordinates):
                certificate = certificate.invalidate(reason)
                stale_ids.append(certificate.certificate_id)
            certificates.append(certificate)

        next_state = replace(state, closure_certificates=tuple(certificates))
        transition = Transition(
            operator=CycleOperator.REOPEN,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            changed_coordinates=("CLOSURE.STALE",) if stale_ids else (),
        )
        return OperatorResult(next_state, tuple(stale_ids), transition)
