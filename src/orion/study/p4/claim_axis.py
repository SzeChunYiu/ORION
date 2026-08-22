"""Claim-scoped authority for P4 identifiability registers.

An identifiability register is multi-axis. A result on one terminal may be cited
only when that exact terminal clears both the construction audit and every
registered seed. Failures on other terminals remain disclosed diagnostics; they
are neither averaged away nor allowed to change the authority of the claimed
axis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ClaimAxisAssessment:
    """Fail-closed authority decision for one construction/terminal pair."""

    construction: str
    terminal: str
    ceiling: float
    seed_count: int
    off_axis_residual_count: int
    authority: str
    blockers: tuple[str, ...]

    @property
    def authorized(self) -> bool:
        return self.authority == "AUTHORIZED_FOR_CLAIM_SCOPE"

    def as_json(self) -> dict[str, Any]:
        return {
            "schema": "P4ClaimAxisAssessment.v1",
            "construction": self.construction,
            "terminal": self.terminal,
            "informedness_ceiling": self.ceiling,
            "seed_count": self.seed_count,
            "off_axis_residual_count": self.off_axis_residual_count,
            "authority": self.authority,
            "authorized": self.authorized,
            "blockers": list(self.blockers),
        }


def assess_claim_axis(
    register: Mapping[str, Any], *, construction: str, terminal: str
) -> ClaimAxisAssessment:
    """Assess one exact claim axis without whole-register aggregation."""

    blockers: list[str] = []
    if register.get("schema") != "P4IdentifiabilityRegister.v1":
        blockers.append("REGISTER_SCHEMA_INVALID")

    ceiling_raw = register.get("informedness_ceiling")
    if not isinstance(ceiling_raw, (int, float)):
        blockers.append("INFORMEDNESS_CEILING_MISSING")
        ceiling = 0.0
    else:
        ceiling = float(ceiling_raw)

    constructions = register.get("constructions")
    construction_block = (
        constructions.get(construction) if isinstance(constructions, Mapping) else None
    )
    terminals = (
        construction_block.get("terminals")
        if isinstance(construction_block, Mapping)
        else None
    )
    axis = terminals.get(terminal) if isinstance(terminals, Mapping) else None
    if not isinstance(axis, Mapping):
        blockers.append("CLAIM_AXIS_MISSING")
    else:
        if axis.get("outcome") != "PASS":
            blockers.append("CONSTRUCTION_AXIS_DID_NOT_PASS")
        recovery = axis.get("worst_recovery")
        if not isinstance(recovery, (int, float)) or float(recovery) > ceiling:
            blockers.append("CONSTRUCTION_AXIS_EXCEEDS_CEILING")
        results = axis.get("results")
        if not isinstance(results, list) or not results:
            blockers.append("REGISTERED_PROBE_RESULTS_MISSING")
        else:
            for item in results:
                if not isinstance(item, Mapping):
                    blockers.append("REGISTERED_PROBE_RESULT_INVALID")
                    break
                item_recovery = item.get("recovery")
                if not isinstance(item_recovery, (int, float)):
                    blockers.append("REGISTERED_PROBE_UNSCORED")
                    break
                if float(item_recovery) > ceiling:
                    blockers.append("REGISTERED_PROBE_EXCEEDS_CEILING")
                    break
                if item.get("unscored") != 0:
                    blockers.append("REGISTERED_PROBE_UNSCORED")
                    break

    seed_invariance = register.get("seed_invariance")
    if not isinstance(seed_invariance, Mapping) or not seed_invariance:
        blockers.append("SEED_INVARIANCE_MISSING")
        seed_count = 0
        off_axis_residual_count = 0
    else:
        seed_count = len(seed_invariance)
        off_axis_residual_count = 0
        for seed, seed_terminals in seed_invariance.items():
            if not isinstance(seed_terminals, Mapping):
                blockers.append(f"SEED_BLOCK_INVALID:{seed}")
                continue
            seed_axis = seed_terminals.get(terminal)
            if not isinstance(seed_axis, Mapping):
                blockers.append(f"CLAIM_AXIS_MISSING_AT_SEED:{seed}")
            else:
                seed_recovery = seed_axis.get("worst_recovery")
                if seed_axis.get("outcome") != "PASS":
                    blockers.append(f"CLAIM_AXIS_DID_NOT_PASS_AT_SEED:{seed}")
                if not isinstance(seed_recovery, (int, float)) or float(seed_recovery) > ceiling:
                    blockers.append(f"CLAIM_AXIS_EXCEEDS_CEILING_AT_SEED:{seed}")
            off_axis_residual_count += sum(
                1
                for other_terminal, entry in seed_terminals.items()
                if other_terminal != terminal
                and isinstance(entry, Mapping)
                and entry.get("outcome") != "PASS"
            )

    unique_blockers = tuple(dict.fromkeys(blockers))
    authority = (
        "AUTHORIZED_FOR_CLAIM_SCOPE" if not unique_blockers else "AUTHORITY_WITHHELD"
    )
    return ClaimAxisAssessment(
        construction=construction,
        terminal=terminal,
        ceiling=ceiling,
        seed_count=seed_count,
        off_axis_residual_count=off_axis_residual_count,
        authority=authority,
        blockers=unique_blockers,
    )
