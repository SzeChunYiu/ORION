"""Step-7 programme receipts, regeneration interface, and archival strategy.

Scripts that would regenerate trajectories from real cycles are declared, not
implemented. Calling the regenerator without sealed cycle receipts returns
``CANNOT_CHECK`` rather than inventing a trajectory. The archival strategy is
a policy document; it is not an archive of programme state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orion.programme.activation import BLOCKING_DEPENDENCIES, PREPARATORY_STATUS, UNBOUND_DIGEST
from orion.programme.identity import seal
from orion.programme.records import Outcome

PROGRAMME_RECEIPT_SCHEMA = "orion.programme.programme-receipt.v1"
ARCHIVAL_STRATEGY_SCHEMA = "orion.programme.archival-strategy.v1"
ARCHIVAL_STRATEGY_ID = "phase4:archival-strategy:preparatory-v1"


@dataclass(frozen=True)
class ProgrammeReceipt:
    """Programme-level receipt. Empty is honest; a closed terminal is refused."""

    protocol_digest: str = UNBOUND_DIGEST
    cycle_receipt_ids: tuple[str, ...] = ()
    epoch_manifest_ids: tuple[str, ...] = ()
    independent_reproduction_digest: str = UNBOUND_DIGEST
    exact_final_head: str = ""
    ci_green: bool = False

    @property
    def grants_phase4_closure(self) -> bool:
        return False


def programme_receipt_payload(receipt: ProgrammeReceipt) -> dict[str, Any]:
    return seal(
        {
            "schema_version": PROGRAMME_RECEIPT_SCHEMA,
            "programme_status": PREPARATORY_STATUS,
            "blocking_dependencies": list(BLOCKING_DEPENDENCIES),
            "protocol_digest": receipt.protocol_digest,
            "cycle_receipt_ids": list(receipt.cycle_receipt_ids),
            "epoch_manifest_ids": list(receipt.epoch_manifest_ids),
            "independent_reproduction_digest": receipt.independent_reproduction_digest,
            "exact_final_head": receipt.exact_final_head,
            "ci_green": receipt.ci_green,
            "grants_phase4_closure": receipt.grants_phase4_closure,
            "cycles_executed": len(receipt.cycle_receipt_ids),
        }
    )


def validate_programme_receipt(receipt: ProgrammeReceipt) -> tuple[str, ...]:
    errors: list[str] = []
    if receipt.cycle_receipt_ids:
        errors.append("programme receipt must not cite cycle receipts that have not been produced")
    if receipt.epoch_manifest_ids:
        errors.append("programme receipt must not cite epoch manifests that have not been produced")
    if receipt.ci_green:
        errors.append("exact-final-head CI cannot be declared green from preparatory scaffolding")
    if receipt.exact_final_head:
        errors.append("exact_final_head must remain empty until a terminal promotion attempt")
    if receipt.independent_reproduction_digest != UNBOUND_DIGEST:
        errors.append("independent reproduction digest must remain unbound")
    return tuple(dict.fromkeys(errors))


def regenerate_programme_trajectory(cycle_receipt_ids: tuple[str, ...] = ()) -> Outcome:
    """Refuse to invent a trajectory. Real regeneration is a post-authorization script."""

    if cycle_receipt_ids:
        return Outcome.FAIL
    return Outcome.CANNOT_CHECK


def archival_strategy_payload() -> dict[str, Any]:
    return seal(
        {
            "schema_version": ARCHIVAL_STRATEGY_SCHEMA,
            "strategy_id": ARCHIVAL_STRATEGY_ID,
            "programme_status": PREPARATORY_STATUS,
            "authority_granted": False,
            "rules": [
                "Accepted, null, harmful and rejected outcomes are archived with equal status.",
                "Archives are content-addressed and append-only.",
                "Supersession adds a successor; it never deletes a predecessor.",
                "Releasable programme state is reconstructible from sealed receipts and the reopen ledger.",
                "Candidate processes cannot write the archive.",
            ],
            "retention": "permanent for sealed programme receipts and epoch manifests",
            "live_archive_populated": False,
        }
    )


def validate_archival_strategy(document: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if document.get("schema_version") != ARCHIVAL_STRATEGY_SCHEMA:
        errors.append("archival strategy schema_version mismatch")
    if document.get("authority_granted") is not False:
        errors.append("archival strategy must not grant authority")
    if document.get("live_archive_populated") is not False:
        errors.append("archival strategy must not claim a populated live archive")
    if not document.get("rules"):
        errors.append("archival strategy rules are required")
    return tuple(dict.fromkeys(errors))


def unexecuted_programme_receipt() -> ProgrammeReceipt:
    return ProgrammeReceipt()


__all__ = [
    "ARCHIVAL_STRATEGY_ID",
    "ARCHIVAL_STRATEGY_SCHEMA",
    "PROGRAMME_RECEIPT_SCHEMA",
    "ProgrammeReceipt",
    "archival_strategy_payload",
    "programme_receipt_payload",
    "regenerate_programme_trajectory",
    "unexecuted_programme_receipt",
    "validate_archival_strategy",
    "validate_programme_receipt",
]
