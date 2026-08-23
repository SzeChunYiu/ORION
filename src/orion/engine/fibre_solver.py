from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from orion.donors import DonorExecutionMode, DonorRegistry
from orion.engine.navigation import FibreNavigation


@dataclass(frozen=True)
class FibreSolverSelection:
    mechanic_id: str
    primary_solver_id: str
    fallback_solver_ids: tuple[str, ...]
    donor_solver_ids: tuple[str, ...]
    verification_required: bool
    selection_digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "schema": "ORION.FibreSolverSelection.v1",
            "mechanic_id": self.mechanic_id,
            "primary_solver_id": self.primary_solver_id,
            "fallback_solver_ids": list(self.fallback_solver_ids),
            "donor_solver_ids": list(self.donor_solver_ids),
            "verification_required": self.verification_required,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
        }

    def validate(self) -> None:
        digest = hashlib.sha256(
            json.dumps(self.unsigned(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if digest != self.selection_digest:
            raise ValueError("fibre solver selection digest mismatch")


def select_fibre_solver(
    route: FibreNavigation,
    donors: DonorRegistry,
) -> FibreSolverSelection:
    """Select the least-authoritative capable solver while honoring strongest donors first."""

    donor_solver_ids: list[str] = []
    for capability_id in route.executable_donor_ids:
        donor = donors.get(capability_id)
        if donor.execution_mode is DonorExecutionMode.EXTERNAL_HOST:
            donor_solver_ids.append(f"host:DONOR_EXECUTE:{capability_id}")
        elif donor.execution_mode is DonorExecutionMode.NATIVE:
            donor_solver_ids.append(f"native-donor:{capability_id}")

    native = f"native-mechanic:{route.mechanic_id}"
    modality = route.execution_modality
    if donor_solver_ids:
        primary = donor_solver_ids[0]
        fallbacks = tuple((*donor_solver_ids[1:], native))
    elif modality in {"MECHANICAL_REQUIRED", "MECHANICAL_PREFERRED"}:
        primary = native
        fallbacks = ()
    elif modality == "HYBRID_SEMANTIC":
        primary = native
        fallbacks = ("host:LLM_COMPLETE",)
    elif modality == "LLM_PROPOSAL":
        primary = "host:LLM_COMPLETE"
        fallbacks = (native,)
    elif modality == "EXTERNAL_SOLVER":
        primary = "host:EXTERNAL_SOLVER"
        fallbacks = (native,)
    else:
        primary = native
        fallbacks = ()

    seed = FibreSolverSelection(
        mechanic_id=route.mechanic_id,
        primary_solver_id=primary,
        fallback_solver_ids=fallbacks,
        donor_solver_ids=tuple(donor_solver_ids),
        verification_required=True,
        selection_digest="",
    )
    digest = hashlib.sha256(
        json.dumps(seed.unsigned(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    selection = FibreSolverSelection(**{**seed.__dict__, "selection_digest": digest})
    selection.validate()
    return selection


__all__ = ["FibreSolverSelection", "select_fibre_solver"]
