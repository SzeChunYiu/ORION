from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class ProvenanceKind(str, Enum):
    EVIDENTIAL = "EVIDENTIAL"
    TRANSFORMATION = "TRANSFORMATION"
    COMPUTATIONAL = "COMPUTATIONAL"
    EXPERIENCE = "EXPERIENCE"
    GOVERNANCE = "GOVERNANCE"
    DEPENDENCY = "DEPENDENCY"


@dataclass(frozen=True)
class ProvenanceRequirement:
    provenance_id: str
    mechanic_id: str
    kind: ProvenanceKind
    binds: str
    required_fields: tuple[str, ...]
    authority_semantics: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.provenance_id, self.mechanic_id, self.binds, self.authority_semantics)):
            raise ValueError("provenance requirement identity/binding/authority semantics are required")
        if not self.required_fields:
            raise ValueError("provenance requirement needs fields")


def default_provenance_requirements(cell: MechanicCell) -> tuple[ProvenanceRequirement, ...]:
    def req(kind: ProvenanceKind, binds: str, fields: tuple[str, ...], authority: str) -> ProvenanceRequirement:
        return ProvenanceRequirement(f"provenance:{cell.mechanic_id}:{kind.value.lower()}", cell.mechanic_id, kind, binds, fields, authority)

    return (
        req(ProvenanceKind.EVIDENTIAL, "source/evidence -> claim/contribution/measurement lineage", ("source identity", "exact selector/span/artifact", "context/cutoff", "evidence identity", "claim/contribution identity"), "Evidential lineage can support authority only through the registered verification/promotion path; citation count is not authority."),
        req(ProvenanceKind.TRANSFORMATION, "input representation -> normalized/mapped/derived object", ("input identities", "operator/mechanic version", "assumptions/context", "output identity", "loss/erasure/approximation metadata"), "A transformation record explains derivation but cannot strengthen relation/mechanism authority beyond its licensed rule."),
        req(ProvenanceKind.COMPUTATIONAL, "run/action/provider/tool -> outputs/receipts", ("run identity", "mechanic/action identity", "input/state digest", "provider/tool/environment identity", "output/receipt identity", "timing/resource data"), "Computational influence is not scientific evidence unless an explicit evidence instrument/verification contract says so."),
        req(ProvenanceKind.EXPERIENCE, "task variation/mechanic execution -> outcome/failure/lesson candidate", ("episode identity", "variation signature", "pre/post state", "actions", "observations", "outcome/failure signature", "support/replay/fresh-transfer identities"), "Experience supports local/reusable method lessons only through the experience-learning gates; recurrence cannot self-promote."),
        req(ProvenanceKind.GOVERNANCE, "candidate/evaluator/verification/promotion chronology", ("candidate exact identity", "evaluator/protected criteria identity", "freeze timestamp/cutoff", "verification receipt", "promotion decision"), "A candidate may not rewrite or self-certify its protected evaluator after outcome access."),
        req(ProvenanceKind.DEPENDENCY, "upstream dependency/version -> downstream mechanic/result", ("dependency identity/version", "consumer identity", "interface/schema version", "upstream receipt", "failure/supersession status"), "Dependency lineage drives scoped reopening/staleness; changing a dependency does not erase historical evidence identity."),
    )


def apply_default_provenance_contract(cell: MechanicCell) -> MechanicCell:
    requirements = default_provenance_requirements(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific provenance granularity, source/selector fidelity, lineage independence, privacy/security and cross-system identity reconciliation",)))
    return replace(
        cell,
        provenance_contracts=tuple(f"{item.provenance_id}:{item.binds}:fields={','.join(item.required_fields)}:{item.authority_semantics}" for item in requirements),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_provenance_contracts(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_provenance_contract(cell) for cell in cells)
