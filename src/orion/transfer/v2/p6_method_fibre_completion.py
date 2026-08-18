from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest
from .p6_method_fibres import (
    CompositionContract,
    CompositionStatus,
    FibreMembership,
    FibreStatus,
    MethodFibre,
    MethodRealizationView,
    ReductionState,
    StructuralReduction,
    StructuralSignature,
    check_composition,
)

P1_UPSTREAM_SCHEMA = "P1.MethodRealization.v1@issue-404"

P1_TO_P6_FIELDS: tuple[tuple[str, str], ...] = (
    ("preconditions", "preconditions"),
    ("transformation_mechanic_graph", "actions"),
    ("dependency_order", "dependencies"),
    ("invariants", "invariants"),
    ("effect_contract", "effects"),
    ("terminal_condition", "termination"),
    ("reconstruction_map", "reconstruction"),
    ("failure_modes", "failures"),
    ("lineage_provenance", "lineage"),
)

P1_MANDATORY_FIELDS = (
    "method_id",
    "source_digest",
    "lineage_provenance",
    "authority_boundary",
)
P1_OPTIONAL_FIELDS = (
    "resources",
    "representation_in",
    "representation_out",
    "progress_measure",
)
P1_CLAIM_RELATIVE_FIELDS = (
    "target_problem_role_signature",
    "preconditions",
    "assumptions",
    "resources",
    "representation_in",
    "representation_out",
    "transformation_mechanic_graph",
    "dependency_order",
    "invariants",
    "progress_measure",
    "effect_contract",
    "terminal_condition",
    "reconstruction_map",
    "failure_modes",
)
P1_ADAPTER_PROFILE = {
    "upstream_schema": P1_UPSTREAM_SCHEMA,
    "mandatory": P1_MANDATORY_FIELDS,
    "optional": P1_OPTIONAL_FIELDS,
    "claim_relative": P1_CLAIM_RELATIVE_FIELDS,
}


def _freeze_value(value: object) -> object:
    if isinstance(value, Mapping):
        return tuple(sorted((str(k), _freeze_value(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_freeze_value(v) for v in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


@dataclass(frozen=True)
class P1AdapterReceipt:
    upstream_schema: str
    upstream_digest: str
    realization_view_digest: str
    field_map: tuple[tuple[str, str], ...]
    mandatory_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    claim_relative_fields: tuple[str, ...]
    context_fields: tuple[tuple[str, object], ...]
    unresolved_fields: tuple[str, ...]
    authority_boundary: str
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P6.P1MethodRealizationAdapter.v1",
            "upstream_schema": self.upstream_schema,
            "upstream_digest": self.upstream_digest,
            "realization_view_digest": self.realization_view_digest,
            "field_map": [list(x) for x in self.field_map],
            "mandatory_fields": list(self.mandatory_fields),
            "optional_fields": list(self.optional_fields),
            "claim_relative_fields": list(self.claim_relative_fields),
            "context_fields": [[k, v] for k, v in self.context_fields],
            "unresolved_fields": list(self.unresolved_fields),
            "authority_boundary": self.authority_boundary,
            "ownership": "P1_CONCRETE_RECONSTRUCTION__P6_CLAIM_RELATIVE_REDUCTION",
        }

    def verify(self) -> None:
        if not self.upstream_digest.startswith("sha256:"):
            raise ValueError("P1 upstream digest must be content-bound")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("P1 adapter receipt digest mismatch")


def adapt_p1_method_realization(
    payload: Mapping[str, object],
    *,
    upstream_digest: str,
) -> tuple[MethodRealizationView, P1AdapterReceipt]:
    missing = [name for name in P1_MANDATORY_FIELDS if not payload.get(name)]
    if missing:
        raise ValueError(f"missing mandatory P1 fields: {missing}")

    method_id = str(payload["method_id"])
    view_payload: dict[str, object] = {
        "preconditions": payload.get("preconditions", ()),
        "actions": payload.get("transformation_mechanic_graph", ()),
        "dependencies": payload.get("dependency_order", ()),
        "invariants": payload.get("invariants", ()),
        "effects": payload.get("effect_contract", ()),
        "terminal_condition": payload.get("terminal_condition"),
        "reconstruction_map": payload.get("reconstruction_map"),
        "failure_modes": payload.get("failure_modes", ()),
        "lineage": payload.get("lineage_provenance", ()),
        "unknown_coordinates": payload.get("unknown_coordinates", ()),
    }
    view = MethodRealizationView.from_mapping(
        realization_id=method_id,
        source_digest=str(payload["source_digest"]),
        payload=view_payload,
    )

    mapped_upstream = {name for name, _ in P1_TO_P6_FIELDS}
    context_names = set(P1_CLAIM_RELATIVE_FIELDS) - mapped_upstream
    context = tuple(
        sorted(
            (name, _freeze_value(payload.get(name)))
            for name in context_names
            if name in payload
        )
    )
    unresolved = tuple(sorted(str(x) for x in payload.get("unknown_fields", ())))
    authority_boundary = str(payload["authority_boundary"])
    base = {
        "version": "P6.P1MethodRealizationAdapter.v1",
        "upstream_schema": P1_UPSTREAM_SCHEMA,
        "upstream_digest": upstream_digest,
        "realization_view_digest": view.digest,
        "field_map": [list(x) for x in P1_TO_P6_FIELDS],
        "mandatory_fields": list(P1_MANDATORY_FIELDS),
        "optional_fields": list(P1_OPTIONAL_FIELDS),
        "claim_relative_fields": list(P1_CLAIM_RELATIVE_FIELDS),
        "context_fields": [[k, v] for k, v in context],
        "unresolved_fields": list(unresolved),
        "authority_boundary": authority_boundary,
        "ownership": "P1_CONCRETE_RECONSTRUCTION__P6_CLAIM_RELATIVE_REDUCTION",
    }
    receipt = P1AdapterReceipt(
        P1_UPSTREAM_SCHEMA,
        upstream_digest,
        view.digest,
        P1_TO_P6_FIELDS,
        P1_MANDATORY_FIELDS,
        P1_OPTIONAL_FIELDS,
        P1_CLAIM_RELATIVE_FIELDS,
        context,
        unresolved,
        authority_boundary,
        content_digest(base),
    )
    receipt.verify()
    return view, receipt


@dataclass(frozen=True)
class ReductionProcedureReceipt:
    reduction_digest: str
    adapter_digest: str
    transformations: tuple[str, ...]
    normalizations: tuple[str, ...]
    preserved_context: tuple[str, ...]
    erased_context: tuple[str, ...]
    unresolved_context: tuple[str, ...]
    preservation_obligations: tuple[str, ...]
    erasure_justifications: tuple[tuple[str, str], ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P6.StructuralReductionProcedure.v1",
            "reduction_digest": self.reduction_digest,
            "adapter_digest": self.adapter_digest,
            "transformations": list(self.transformations),
            "normalizations": list(self.normalizations),
            "preserved_context": list(self.preserved_context),
            "erased_context": list(self.erased_context),
            "unresolved_context": list(self.unresolved_context),
            "preservation_obligations": list(self.preservation_obligations),
            "erasure_justifications": [list(x) for x in self.erasure_justifications],
            "authority_scope": "FORMAL_REDUCTION_PROCEDURE_ONLY",
        }

    def verify(self) -> None:
        groups = [
            set(self.preserved_context),
            set(self.erased_context),
            set(self.unresolved_context),
        ]
        if any(a & b for i, a in enumerate(groups) for b in groups[i + 1 :]):
            raise ValueError("context coordinate classified more than once")
        if set(dict(self.erasure_justifications)) != set(self.erased_context):
            raise ValueError("context erasure requires exact justification")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("reduction procedure digest mismatch")


def build_reduction_procedure(
    reduction: StructuralReduction,
    adapter: P1AdapterReceipt,
    *,
    transformations: Sequence[str] = (),
    normalizations: Sequence[str] = (),
    preserved_context: Sequence[str] = (),
    erased_context: Sequence[str] = (),
    unresolved_context: Sequence[str] = (),
    preservation_obligations: Sequence[str] = (),
    erasure_justifications: Mapping[str, str] | None = None,
) -> ReductionProcedureReceipt:
    reduction.verify()
    adapter.verify()
    available = {name for name, _ in adapter.context_fields} | set(adapter.unresolved_fields)
    classified = set(preserved_context) | set(erased_context) | set(unresolved_context)
    missing = available - classified
    extra = classified - available
    if missing:
        raise ValueError(f"P1 context fields unclassified: {sorted(missing)}")
    if extra:
        raise ValueError(f"unknown P1 context fields classified: {sorted(extra)}")
    justifications = erasure_justifications or {}
    base = {
        "version": "P6.StructuralReductionProcedure.v1",
        "reduction_digest": reduction.digest,
        "adapter_digest": adapter.digest,
        "transformations": list(transformations),
        "normalizations": list(normalizations),
        "preserved_context": sorted(set(preserved_context)),
        "erased_context": sorted(set(erased_context)),
        "unresolved_context": sorted(set(unresolved_context)),
        "preservation_obligations": sorted(set(preservation_obligations)),
        "erasure_justifications": [
            [k, str(justifications[k])] for k in sorted(justifications)
        ],
        "authority_scope": "FORMAL_REDUCTION_PROCEDURE_ONLY",
    }
    receipt = ReductionProcedureReceipt(
        reduction.digest,
        adapter.digest,
        tuple(base["transformations"]),
        tuple(base["normalizations"]),
        tuple(base["preserved_context"]),
        tuple(base["erased_context"]),
        tuple(base["unresolved_context"]),
        tuple(base["preservation_obligations"]),
        tuple((x[0], x[1]) for x in base["erasure_justifications"]),
        content_digest(base),
    )
    receipt.verify()
    return receipt


@dataclass(frozen=True)
class StructuralSignatureContract:
    signature_digest: str
    reduction_digest: str
    contributor_realization_digests: tuple[str, ...]
    load_bearing_coordinates: tuple[str, ...]
    effect_obligations: tuple[str, ...]
    reconstruction_obligations: tuple[str, ...]
    state: ReductionState
    digest: str
    can_authorize_transfer: bool = False
    can_claim_novelty: bool = False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P6.StructuralSignatureContract.v1",
            "signature_digest": self.signature_digest,
            "reduction_digest": self.reduction_digest,
            "contributor_realization_digests": list(self.contributor_realization_digests),
            "load_bearing_coordinates": list(self.load_bearing_coordinates),
            "effect_obligations": list(self.effect_obligations),
            "reconstruction_obligations": list(self.reconstruction_obligations),
            "state": self.state.value,
            "can_authorize_transfer": False,
            "can_claim_novelty": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("signature contract digest mismatch")


def bind_signature_contract(
    signature: StructuralSignature,
    reduction: StructuralReduction,
    *,
    contributor_realization_digests: Sequence[str],
    effect_obligations: Sequence[str],
    reconstruction_obligations: Sequence[str],
) -> StructuralSignatureContract:
    signature.verify()
    reduction.verify()
    contributors = tuple(
        sorted(set(contributor_realization_digests) | {signature.realization_digest})
    )
    base = {
        "version": "P6.StructuralSignatureContract.v1",
        "signature_digest": signature.digest,
        "reduction_digest": reduction.digest,
        "contributor_realization_digests": list(contributors),
        "load_bearing_coordinates": list(reduction.load_bearing),
        "effect_obligations": sorted(set(effect_obligations)),
        "reconstruction_obligations": sorted(set(reconstruction_obligations)),
        "state": signature.state.value,
        "can_authorize_transfer": False,
        "can_claim_novelty": False,
    }
    out = StructuralSignatureContract(
        signature.digest,
        reduction.digest,
        contributors,
        tuple(reduction.load_bearing),
        tuple(base["effect_obligations"]),
        tuple(base["reconstruction_obligations"]),
        signature.state,
        content_digest(base),
    )
    out.verify()
    return out


@dataclass(frozen=True)
class FibreLineageIndex:
    fibre_digest: str
    member_links: tuple[tuple[str, str], ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P6.FibreLineageIndex.v1",
            "fibre_digest": self.fibre_digest,
            "member_links": [list(x) for x in self.member_links],
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("fibre lineage index digest mismatch")


def bind_fibre_lineage(
    fibre: MethodFibre,
    member_adapter_digests: Mapping[str, str],
) -> FibreLineageIndex:
    missing = set(fibre.members) - set(member_adapter_digests)
    if missing:
        raise ValueError(f"member lineage missing: {sorted(missing)}")
    links = tuple(sorted((m, str(member_adapter_digests[m])) for m in fibre.members))
    base = {
        "version": "P6.FibreLineageIndex.v1",
        "fibre_digest": fibre.digest,
        "member_links": [list(x) for x in links],
    }
    out = FibreLineageIndex(fibre.digest, links, content_digest(base))
    out.verify()
    return out


@dataclass(frozen=True)
class SubstitutionReceipt:
    signature_digest: str
    source_realization_digest: str
    target_realization_digest: str
    status: CompositionStatus
    reasons: tuple[str, ...]
    digest: str
    can_authorize_transfer: bool = False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P6.CompatibleRealizationSubstitution.v1",
            "signature_digest": self.signature_digest,
            "source_realization_digest": self.source_realization_digest,
            "target_realization_digest": self.target_realization_digest,
            "status": self.status.value,
            "reasons": list(self.reasons),
            "can_authorize_transfer": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("substitution receipt digest mismatch")


def check_substitution(
    source: FibreMembership,
    target: FibreMembership,
    *,
    interface: bool | None,
    invariants: bool | None,
    effects: bool | None,
    reconstruction: bool | None,
    authority: bool | None,
) -> SubstitutionReceipt:
    blocked: list[str] = []
    unresolved: list[str] = []
    if source.signature_digest != target.signature_digest:
        blocked.append("SIGNATURE_MISMATCH")
    if source.status is FibreStatus.BLOCKED or target.status is FibreStatus.BLOCKED:
        blocked.append("MEMBERSHIP_BLOCKED")
    elif source.status is not FibreStatus.MEMBER or target.status is not FibreStatus.MEMBER:
        unresolved.append("MEMBERSHIP_UNRESOLVED")

    checks = {
        "INTERFACE": interface,
        "INVARIANTS": invariants,
        "EFFECTS": effects,
        "RECONSTRUCTION": reconstruction,
        "AUTHORITY": authority,
    }
    blocked += [f"{k}_NOT_PRESERVED" for k, value in checks.items() if value is False]
    unresolved += [f"{k}_UNRESOLVED" for k, value in checks.items() if value is None]
    status = (
        CompositionStatus.BLOCKED
        if blocked
        else (CompositionStatus.UNRESOLVED if unresolved else CompositionStatus.COMPATIBLE)
    )
    reasons = tuple(sorted(blocked + unresolved))
    base = {
        "version": "P6.CompatibleRealizationSubstitution.v1",
        "signature_digest": source.signature_digest,
        "source_realization_digest": source.realization_digest,
        "target_realization_digest": target.realization_digest,
        "status": status.value,
        "reasons": list(reasons),
        "can_authorize_transfer": False,
    }
    out = SubstitutionReceipt(
        source.signature_digest,
        source.realization_digest,
        target.realization_digest,
        status,
        reasons,
        content_digest(base),
    )
    out.verify()
    return out


@dataclass(frozen=True)
class StructuralPreorderWitness:
    claim_id: str
    lower_id: str
    upper_id: str
    related: bool | None
    digest: str
    can_grant_fibre_membership: bool = False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P6.StructuralPreorderWitness.v1",
            "claim_id": self.claim_id,
            "lower_id": self.lower_id,
            "upper_id": self.upper_id,
            "related": self.related,
            "can_grant_fibre_membership": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("preorder witness digest mismatch")


def preorder_witness(
    *,
    claim_id: str,
    lower_id: str,
    upper_id: str,
    lower_preconditions: Sequence[str],
    upper_preconditions: Sequence[str],
    lower_effects: Sequence[str],
    upper_effects: Sequence[str],
    obligations_satisfied: bool | None,
) -> StructuralPreorderWitness:
    lower_p, upper_p = set(lower_preconditions), set(upper_preconditions)
    lower_e, upper_e = set(lower_effects), set(upper_effects)
    related = (
        None
        if obligations_satisfied is None
        else bool(obligations_satisfied and lower_p <= upper_p and lower_e <= upper_e)
    )
    base = {
        "version": "P6.StructuralPreorderWitness.v1",
        "claim_id": claim_id,
        "lower_id": lower_id,
        "upper_id": upper_id,
        "related": related,
        "can_grant_fibre_membership": False,
    }
    out = StructuralPreorderWitness(
        claim_id,
        lower_id,
        upper_id,
        related,
        content_digest(base),
    )
    out.verify()
    return out


class FibreCompositionOutcome(str, Enum):
    STAYS_IN_FIBRE = "STAYS_IN_FIBRE"
    NEW_SIGNATURE_REQUIRED = "NEW_SIGNATURE_REQUIRED"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"


def classify_fibre_composition(
    contract: CompositionContract,
    *,
    retained_contract_preserved: bool | None,
    footprint_changed: bool | None,
) -> FibreCompositionOutcome:
    status, _ = check_composition(contract)
    if status is CompositionStatus.BLOCKED:
        return FibreCompositionOutcome.BLOCKED
    if status is CompositionStatus.UNRESOLVED:
        return FibreCompositionOutcome.UNRESOLVED
    if retained_contract_preserved is None or footprint_changed is None:
        return FibreCompositionOutcome.UNRESOLVED
    if not retained_contract_preserved or footprint_changed:
        return FibreCompositionOutcome.NEW_SIGNATURE_REQUIRED
    return FibreCompositionOutcome.STAYS_IN_FIBRE


def representation_project(reconstruction_valid: bool | None) -> ReductionState:
    if reconstruction_valid is True:
        return ReductionState.SUPPORTED
    if reconstruction_valid is False:
        return ReductionState.OBSTRUCTION
    return ReductionState.UNRESOLVED
