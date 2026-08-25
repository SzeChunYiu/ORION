"""Typed composition, structural-transfer, and residual-completion records.

This module is a finite reference semantics for the three candidate-source modes
used by ORION discovery research:

* donor composition (assemble known fragments),
* structural transfer (transport a source structure across a typed map), and
* residual completion (generate semantic structure not absorbed by either the
  local closure or a registered donor map).

The classifications are relative to a frozen equivalence relation, donor set,
product grammar, and resource contract.  They report provenance and the maximum
eligible research terminal only; they do not grant scientific validity,
novelty, or adoption authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _ordered_unique(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        item = str(value)
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


class SemanticElementKind(str, Enum):
    QUESTION = "QUESTION"
    OBJECT = "OBJECT"
    RELATION = "RELATION"
    CONSTRAINT = "CONSTRAINT"
    OPERATOR = "OPERATOR"
    COMPOSITION_EDGE = "COMPOSITION_EDGE"
    INTERFACE = "INTERFACE"
    VALIDATION_RULE = "VALIDATION_RULE"


class ProvenanceClass(str, Enum):
    LOCAL_CLOSURE = "LOCAL_CLOSURE"
    DONOR_MAPPED = "DONOR_MAPPED"
    GENERATED_RESIDUAL = "GENERATED_RESIDUAL"
    UNRESOLVED = "UNRESOLVED"


class SynthesisMode(str, Enum):
    FIXED_REGIME_SEARCH = "FIXED_REGIME_SEARCH"
    DONOR_COMPOSITION = "DONOR_COMPOSITION"
    STRUCTURAL_TRANSFER = "STRUCTURAL_TRANSFER"
    RESIDUAL_COMPLETION = "RESIDUAL_COMPLETION"
    HYBRID = "HYBRID"
    UNRESOLVED = "UNRESOLVED"


class TransferStrength(str, Enum):
    EXACT_INTERPRETATION = "EXACT_INTERPRETATION"
    PARTIAL_ANALOGY = "PARTIAL_ANALOGY"
    CANNOT_CHECK = "CANNOT_CHECK"


class SynthesisTerminal(str, Enum):
    NO_REACH = "NO_REACH"
    NO_JUMP_SEARCH = "NO_JUMP_SEARCH"
    DONOR_COMPOSITION_ONLY = "DONOR_COMPOSITION_ONLY"
    STRUCTURAL_TRANSFER_ONLY = "STRUCTURAL_TRANSFER_ONLY"
    RESIDUAL_COMPLETION_CANDIDATE = "RESIDUAL_COMPLETION_CANDIDATE"
    HYBRID_SYNTHESIS_CANDIDATE = "HYBRID_SYNTHESIS_CANDIDATE"
    HIDDEN_CONSEQUENCE_PENDING = "HIDDEN_CONSEQUENCE_PENDING"
    VALIDITY_CANNOT_CHECK = "VALIDITY_CANNOT_CHECK"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class CandidateElement:
    element_id: str
    kind: SemanticElementKind
    equivalence_class_id: str
    in_local_closure: bool
    donor_source_ids: tuple[str, ...]
    generated_origin_id: str | None

    def verify(self) -> None:
        if not self.element_id or not self.equivalence_class_id:
            raise ValueError("candidate element requires identity and equivalence class")
        if any(not source_id for source_id in self.donor_source_ids):
            raise ValueError("donor source identities must be non-empty")
        if self.generated_origin_id is not None and not self.generated_origin_id:
            raise ValueError("generated origin identity must be non-empty")

    @property
    def provenance(self) -> ProvenanceClass:
        """Classify with conservative priority local -> donor -> generated.

        A generated item that is subsequently absorbed by a donor is donor-mapped,
        not a present-day semantic residual.  The origin record remains useful for
        process analysis but does not override donor absorption.
        """

        self.verify()
        if self.in_local_closure:
            return ProvenanceClass.LOCAL_CLOSURE
        if self.donor_source_ids:
            return ProvenanceClass.DONOR_MAPPED
        if self.generated_origin_id is not None:
            return ProvenanceClass.GENERATED_RESIDUAL
        return ProvenanceClass.UNRESOLVED


@dataclass(frozen=True)
class DonorFragment:
    fragment_id: str
    domain_id: str
    element_ids: tuple[str, ...]
    required_interface_ids: tuple[str, ...]
    guarantee_ids: tuple[str, ...]

    def verify(self) -> None:
        if not self.fragment_id or not self.domain_id:
            raise ValueError("donor fragment requires identity and domain")
        if not self.element_ids or not self.guarantee_ids:
            raise ValueError("donor fragment requires elements and guarantees")
        if any(
            not item
            for item in self.element_ids + self.required_interface_ids + self.guarantee_ids
        ):
            raise ValueError("donor fragment identities must be non-empty")


@dataclass(frozen=True)
class CompositionEdge:
    edge_id: str
    operator_id: str
    input_fragment_ids: tuple[str, ...]
    output_contract_ids: tuple[str, ...]
    in_registered_product_closure: bool
    required_obligation_ids: tuple[str, ...]
    discharged_obligation_ids: tuple[str, ...]
    generated_origin_id: str | None

    def verify(self) -> None:
        if not self.edge_id or not self.operator_id:
            raise ValueError("composition edge requires identity and operator")
        if len(self.input_fragment_ids) < 2:
            raise ValueError("composition edge requires at least two input fragments")
        if not self.output_contract_ids:
            raise ValueError("composition edge requires an output contract")
        if any(
            not item
            for item in (
                self.input_fragment_ids
                + self.output_contract_ids
                + self.required_obligation_ids
                + self.discharged_obligation_ids
            )
        ):
            raise ValueError("composition edge identities must be non-empty")

    @property
    def unresolved_obligation_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(set(self.required_obligation_ids) - set(self.discharged_obligation_ids))
        )

    @property
    def provenance(self) -> ProvenanceClass:
        self.verify()
        if self.in_registered_product_closure:
            return ProvenanceClass.LOCAL_CLOSURE
        if self.generated_origin_id is not None:
            return ProvenanceClass.GENERATED_RESIDUAL
        return ProvenanceClass.UNRESOLVED


@dataclass(frozen=True)
class StructuralTransferMap:
    map_id: str
    source_domain_id: str
    target_domain_id: str
    mapped_element_ids: tuple[str, ...]
    required_relation_ids: tuple[str, ...]
    preserved_relation_ids: tuple[str, ...]
    target_obligation_ids: tuple[str, ...]
    discharged_target_obligation_ids: tuple[str, ...]
    validation_correspondence: bool
    negative_twin_id: str | None

    def verify(self) -> None:
        if not self.map_id or not self.source_domain_id or not self.target_domain_id:
            raise ValueError("transfer map requires map/source/target identities")
        if self.source_domain_id == self.target_domain_id:
            raise ValueError("structural transfer requires distinct source and target domains")
        if not self.mapped_element_ids or not self.required_relation_ids:
            raise ValueError("transfer map requires mapped elements and load-bearing relations")
        if any(
            not item
            for item in (
                self.mapped_element_ids
                + self.required_relation_ids
                + self.preserved_relation_ids
                + self.target_obligation_ids
                + self.discharged_target_obligation_ids
            )
        ):
            raise ValueError("transfer-map identities must be non-empty")

    @property
    def unresolved_relation_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(set(self.required_relation_ids) - set(self.preserved_relation_ids))
        )

    @property
    def unresolved_target_obligation_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                set(self.target_obligation_ids)
                - set(self.discharged_target_obligation_ids)
            )
        )

    @property
    def strength(self) -> TransferStrength:
        self.verify()
        if (
            not self.unresolved_relation_ids
            and not self.unresolved_target_obligation_ids
            and self.validation_correspondence
        ):
            return TransferStrength.EXACT_INTERPRETATION
        return TransferStrength.PARTIAL_ANALOGY


def minimal_successful_subsets(
    universe_ids: Sequence[str],
    successful_subsets: Sequence[Sequence[str]],
) -> tuple[tuple[str, ...], ...]:
    """Return all inclusion-minimal successful subsets in a finite registry."""

    universe = set(_sorted_unique(universe_ids))
    if not universe:
        raise ValueError("donor universe cannot be empty")
    rows: set[frozenset[str]] = set()
    for raw in successful_subsets:
        row = frozenset(str(item) for item in raw)
        if not row.issubset(universe):
            raise ValueError("successful subset references an unregistered donor")
        rows.add(row)
    minimal = [row for row in rows if not any(other < row for other in rows)]
    return tuple(sorted((tuple(sorted(row)) for row in minimal), key=lambda row: (len(row), row)))


def minimum_separating_panels(
    alternative_pair_ids: Sequence[str],
    experiment_coverage: Mapping[str, Sequence[str]],
) -> tuple[tuple[str, ...], ...]:
    """Solve the finite minimum theorem-identifying experiment problem.

    Each experiment covers the alternative pairs it distinguishes.  The exact
    minimum panel is the minimum set cover over the registered pair universe.
    """

    pairs = set(_sorted_unique(alternative_pair_ids))
    if not pairs:
        raise ValueError("at least one alternative pair is required")
    experiments = tuple(sorted(str(item) for item in experiment_coverage))
    coverage = {
        experiment_id: set(str(pair_id) for pair_id in experiment_coverage[experiment_id])
        for experiment_id in experiments
    }
    covered = set().union(*coverage.values()) if coverage else set()
    if covered != pairs:
        raise ValueError("registered experiments do not identify every alternative pair")
    for size in range(1, len(experiments) + 1):
        panels: list[tuple[str, ...]] = []
        for panel in combinations(experiments, size):
            covered: set[str] = set()
            for experiment_id in panel:
                covered.update(coverage[experiment_id])
            if covered == pairs:
                panels.append(panel)
        if panels:
            return tuple(panels)
    raise AssertionError("finite set-cover search should have returned a panel")


def minimal_semantic_residuals(
    candidate_element_ids: Sequence[str],
    donor_explained_element_sets: Sequence[Sequence[str]],
) -> tuple[tuple[str, ...], ...]:
    """Return all inclusion-minimal residuals across admissible donor decompositions.

    The decomposition of a scientific object into donor-owned and residual parts
    need not be unique.  Returning the family prevents an arbitrary decomposition
    from becoming novelty authority.
    """

    candidate = set(_sorted_unique(candidate_element_ids))
    if not candidate:
        raise ValueError("candidate semantic element set cannot be empty")
    residuals: set[frozenset[str]] = set()
    for explained_raw in donor_explained_element_sets:
        explained = set(str(item) for item in explained_raw)
        if not explained.issubset(candidate):
            raise ValueError("donor explanation contains a non-candidate element")
        residuals.add(frozenset(candidate - explained))
    if not residuals:
        residuals.add(frozenset(candidate))
    minimal = [row for row in residuals if not any(other < row for other in residuals)]
    return tuple(sorted((tuple(sorted(row)) for row in minimal), key=lambda row: (len(row), row)))


@dataclass(frozen=True)
class CandidateSynthesisRecord:
    candidate_id: str
    target_domain_id: str
    target_contract_id: str
    elements: tuple[CandidateElement, ...]
    donor_fragments: tuple[DonorFragment, ...]
    composition_edges: tuple[CompositionEdge, ...]
    transfer_maps: tuple[StructuralTransferMap, ...]
    old_regime_reaches_target: bool
    candidate_reaches_target: bool
    hidden_consequence_passed: bool
    independent_validity_passed: bool
    successful_donor_subsets: tuple[tuple[str, ...], ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "CandidateSynthesisRecord.v1",
            "candidate_id": self.candidate_id,
            "target_domain_id": self.target_domain_id,
            "target_contract_id": self.target_contract_id,
            "elements": [
                {
                    "element_id": row.element_id,
                    "kind": row.kind.value,
                    "equivalence_class_id": row.equivalence_class_id,
                    "in_local_closure": row.in_local_closure,
                    "donor_source_ids": list(row.donor_source_ids),
                    "generated_origin_id": row.generated_origin_id,
                }
                for row in self.elements
            ],
            "donor_fragments": [
                {
                    "fragment_id": row.fragment_id,
                    "domain_id": row.domain_id,
                    "element_ids": list(row.element_ids),
                    "required_interface_ids": list(row.required_interface_ids),
                    "guarantee_ids": list(row.guarantee_ids),
                }
                for row in self.donor_fragments
            ],
            "composition_edges": [
                {
                    "edge_id": row.edge_id,
                    "operator_id": row.operator_id,
                    "input_fragment_ids": list(row.input_fragment_ids),
                    "output_contract_ids": list(row.output_contract_ids),
                    "in_registered_product_closure": row.in_registered_product_closure,
                    "required_obligation_ids": list(row.required_obligation_ids),
                    "discharged_obligation_ids": list(row.discharged_obligation_ids),
                    "generated_origin_id": row.generated_origin_id,
                }
                for row in self.composition_edges
            ],
            "transfer_maps": [
                {
                    "map_id": row.map_id,
                    "source_domain_id": row.source_domain_id,
                    "target_domain_id": row.target_domain_id,
                    "mapped_element_ids": list(row.mapped_element_ids),
                    "required_relation_ids": list(row.required_relation_ids),
                    "preserved_relation_ids": list(row.preserved_relation_ids),
                    "target_obligation_ids": list(row.target_obligation_ids),
                    "discharged_target_obligation_ids": list(
                        row.discharged_target_obligation_ids
                    ),
                    "validation_correspondence": row.validation_correspondence,
                    "negative_twin_id": row.negative_twin_id,
                }
                for row in self.transfer_maps
            ],
            "old_regime_reaches_target": self.old_regime_reaches_target,
            "candidate_reaches_target": self.candidate_reaches_target,
            "hidden_consequence_passed": self.hidden_consequence_passed,
            "independent_validity_passed": self.independent_validity_passed,
            "successful_donor_subsets": [list(row) for row in self.successful_donor_subsets],
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
        }

    def verify(self) -> None:
        if not self.candidate_id or not self.target_domain_id or not self.target_contract_id:
            raise ValueError("candidate synthesis requires candidate/domain/target identities")
        if not self.elements:
            raise ValueError("candidate synthesis requires semantic elements")
        element_ids = [row.element_id for row in self.elements]
        fragment_ids = [row.fragment_id for row in self.donor_fragments]
        edge_ids = [row.edge_id for row in self.composition_edges]
        map_ids = [row.map_id for row in self.transfer_maps]
        for label, values in (
            ("element", element_ids),
            ("fragment", fragment_ids),
            ("edge", edge_ids),
            ("transfer map", map_ids),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"duplicate {label} identity")
        for row in self.elements:
            row.verify()
        element_set = set(element_ids)
        for row in self.donor_fragments:
            row.verify()
            if not set(row.element_ids).issubset(element_set):
                raise ValueError("donor fragment references unknown candidate element")
        fragment_set = set(fragment_ids)
        for row in self.composition_edges:
            row.verify()
            if not set(row.input_fragment_ids).issubset(fragment_set):
                raise ValueError("composition edge references unknown donor fragment")
        for row in self.transfer_maps:
            row.verify()
            if not set(row.mapped_element_ids).issubset(element_set):
                raise ValueError("transfer map references unknown candidate element")
        if fragment_ids or self.successful_donor_subsets:
            minimal_successful_subsets(fragment_ids, self.successful_donor_subsets)
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("candidate synthesis digest mismatch")


@dataclass(frozen=True)
class SynthesisAssessment:
    candidate_id: str
    mode: SynthesisMode
    terminal: SynthesisTerminal
    local_element_ids: tuple[str, ...]
    donor_mapped_element_ids: tuple[str, ...]
    generated_residual_element_ids: tuple[str, ...]
    unresolved_element_ids: tuple[str, ...]
    generated_residual_edge_ids: tuple[str, ...]
    unresolved_edge_ids: tuple[str, ...]
    exact_transfer_map_ids: tuple[str, ...]
    partial_transfer_map_ids: tuple[str, ...]
    minimal_successful_donor_sets: tuple[tuple[str, ...], ...]
    interaction_order: int | None
    reasons: tuple[str, ...]
    digest: str

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SynthesisAssessment.v1",
            "candidate_id": self.candidate_id,
            "mode": self.mode.value,
            "terminal": self.terminal.value,
            "local_element_ids": list(self.local_element_ids),
            "donor_mapped_element_ids": list(self.donor_mapped_element_ids),
            "generated_residual_element_ids": list(
                self.generated_residual_element_ids
            ),
            "unresolved_element_ids": list(self.unresolved_element_ids),
            "generated_residual_edge_ids": list(self.generated_residual_edge_ids),
            "unresolved_edge_ids": list(self.unresolved_edge_ids),
            "exact_transfer_map_ids": list(self.exact_transfer_map_ids),
            "partial_transfer_map_ids": list(self.partial_transfer_map_ids),
            "minimal_successful_donor_sets": [
                list(row) for row in self.minimal_successful_donor_sets
            ],
            "interaction_order": self.interaction_order,
            "reasons": list(self.reasons),
            "grants_novelty_authority": False,
        }

    def verify(self) -> None:
        if not self.candidate_id:
            raise ValueError("synthesis assessment requires candidate identity")
        if self.interaction_order is not None and self.interaction_order < 0:
            raise ValueError("interaction order cannot be negative")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("synthesis assessment digest mismatch")


def _build_assessment(record: CandidateSynthesisRecord) -> SynthesisAssessment:
    record.verify()
    by_provenance: dict[ProvenanceClass, list[str]] = {
        state: [] for state in ProvenanceClass
    }
    for element in record.elements:
        by_provenance[element.provenance].append(element.element_id)

    residual_edges = sorted(
        row.edge_id
        for row in record.composition_edges
        if row.provenance is ProvenanceClass.GENERATED_RESIDUAL
    )
    unresolved_edges = sorted(
        row.edge_id
        for row in record.composition_edges
        if row.provenance is ProvenanceClass.UNRESOLVED
        or row.unresolved_obligation_ids
    )
    exact_maps = sorted(
        row.map_id
        for row in record.transfer_maps
        if row.strength is TransferStrength.EXACT_INTERPRETATION
    )
    partial_maps = sorted(
        row.map_id
        for row in record.transfer_maps
        if row.strength is not TransferStrength.EXACT_INTERPRETATION
    )
    minimal_sets = minimal_successful_subsets(
        [row.fragment_id for row in record.donor_fragments],
        record.successful_donor_subsets,
    ) if record.donor_fragments else ()
    positive_sets = tuple(row for row in minimal_sets if row)
    interaction_order = min((len(row) for row in positive_sets), default=None)

    has_residual = bool(
        by_provenance[ProvenanceClass.GENERATED_RESIDUAL] or residual_edges
    )
    has_transfer = bool(exact_maps)
    has_donor_composition = bool(
        by_provenance[ProvenanceClass.DONOR_MAPPED]
        or any(len(row) >= 2 for row in positive_sets)
        or record.composition_edges
    )
    unresolved = bool(
        by_provenance[ProvenanceClass.UNRESOLVED]
        or unresolved_edges
        or partial_maps
    )

    if unresolved:
        mode = SynthesisMode.UNRESOLVED
    elif has_residual and (has_transfer or has_donor_composition):
        mode = SynthesisMode.HYBRID
    elif has_residual:
        mode = SynthesisMode.RESIDUAL_COMPLETION
    elif has_transfer:
        mode = SynthesisMode.STRUCTURAL_TRANSFER
    elif has_donor_composition:
        mode = SynthesisMode.DONOR_COMPOSITION
    elif record.old_regime_reaches_target:
        mode = SynthesisMode.FIXED_REGIME_SEARCH
    else:
        mode = SynthesisMode.UNRESOLVED

    reasons: list[str] = []
    if not record.candidate_reaches_target:
        terminal = SynthesisTerminal.NO_REACH
        reasons.append("candidate does not reach the registered target")
    elif unresolved:
        terminal = SynthesisTerminal.CANNOT_CHECK
        reasons.append("one or more semantic, composition, or transfer debts remain")
    elif not record.independent_validity_passed:
        terminal = SynthesisTerminal.VALIDITY_CANNOT_CHECK
        reasons.append("target reach lacks independent validity")
    elif not record.hidden_consequence_passed:
        terminal = SynthesisTerminal.HIDDEN_CONSEQUENCE_PENDING
        reasons.append("development reach has not survived a hidden consequence")
    elif mode is SynthesisMode.FIXED_REGIME_SEARCH:
        terminal = SynthesisTerminal.NO_JUMP_SEARCH
    elif mode is SynthesisMode.DONOR_COMPOSITION:
        terminal = SynthesisTerminal.DONOR_COMPOSITION_ONLY
    elif mode is SynthesisMode.STRUCTURAL_TRANSFER:
        terminal = SynthesisTerminal.STRUCTURAL_TRANSFER_ONLY
    elif mode is SynthesisMode.RESIDUAL_COMPLETION:
        terminal = SynthesisTerminal.RESIDUAL_COMPLETION_CANDIDATE
    elif mode is SynthesisMode.HYBRID:
        terminal = SynthesisTerminal.HYBRID_SYNTHESIS_CANDIDATE
    else:
        terminal = SynthesisTerminal.CANNOT_CHECK

    if record.old_regime_reaches_target and mode is not SynthesisMode.FIXED_REGIME_SEARCH:
        reasons.append("old regime already reaches target; expansion credit is blocked")
        terminal = SynthesisTerminal.NO_JUMP_SEARCH
    if has_donor_composition and not has_residual:
        reasons.append("candidate lies inside the registered donor-product envelope")
    if has_transfer:
        reasons.append("at least one cross-domain map discharges all registered transfer debt")
    if has_residual:
        reasons.append("candidate contains a generated semantic or bridge residual")
    if interaction_order is not None:
        reasons.append(f"minimum successful donor interaction order is {interaction_order}")

    payload = {
        "version": "SynthesisAssessment.v1",
        "candidate_id": record.candidate_id,
        "mode": mode.value,
        "terminal": terminal.value,
        "local_element_ids": sorted(by_provenance[ProvenanceClass.LOCAL_CLOSURE]),
        "donor_mapped_element_ids": sorted(
            by_provenance[ProvenanceClass.DONOR_MAPPED]
        ),
        "generated_residual_element_ids": sorted(
            by_provenance[ProvenanceClass.GENERATED_RESIDUAL]
        ),
        "unresolved_element_ids": sorted(
            by_provenance[ProvenanceClass.UNRESOLVED]
        ),
        "generated_residual_edge_ids": residual_edges,
        "unresolved_edge_ids": unresolved_edges,
        "exact_transfer_map_ids": exact_maps,
        "partial_transfer_map_ids": partial_maps,
        "minimal_successful_donor_sets": [list(row) for row in minimal_sets],
        "interaction_order": interaction_order,
        "reasons": sorted(set(reasons)),
        "grants_novelty_authority": False,
    }
    assessment = SynthesisAssessment(
        candidate_id=payload["candidate_id"],
        mode=SynthesisMode(payload["mode"]),
        terminal=SynthesisTerminal(payload["terminal"]),
        local_element_ids=tuple(payload["local_element_ids"]),
        donor_mapped_element_ids=tuple(payload["donor_mapped_element_ids"]),
        generated_residual_element_ids=tuple(
            payload["generated_residual_element_ids"]
        ),
        unresolved_element_ids=tuple(payload["unresolved_element_ids"]),
        generated_residual_edge_ids=tuple(payload["generated_residual_edge_ids"]),
        unresolved_edge_ids=tuple(payload["unresolved_edge_ids"]),
        exact_transfer_map_ids=tuple(payload["exact_transfer_map_ids"]),
        partial_transfer_map_ids=tuple(payload["partial_transfer_map_ids"]),
        minimal_successful_donor_sets=tuple(
            tuple(row) for row in payload["minimal_successful_donor_sets"]
        ),
        interaction_order=payload["interaction_order"],
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    assessment.verify()
    return assessment


def assess_candidate_synthesis(record: CandidateSynthesisRecord) -> SynthesisAssessment:
    """Classify a finite candidate without granting novelty or adoption."""

    return _build_assessment(record)


def build_candidate_synthesis_record(
    *,
    candidate_id: str,
    target_domain_id: str,
    target_contract_id: str,
    elements: Sequence[CandidateElement],
    donor_fragments: Sequence[DonorFragment] = (),
    composition_edges: Sequence[CompositionEdge] = (),
    transfer_maps: Sequence[StructuralTransferMap] = (),
    old_regime_reaches_target: bool,
    candidate_reaches_target: bool,
    hidden_consequence_passed: bool,
    independent_validity_passed: bool,
    successful_donor_subsets: Sequence[Sequence[str]] = (),
) -> CandidateSynthesisRecord:
    element_rows = tuple(sorted(elements, key=lambda row: row.element_id))
    fragment_rows = tuple(sorted(donor_fragments, key=lambda row: row.fragment_id))
    edge_rows = tuple(sorted(composition_edges, key=lambda row: row.edge_id))
    transfer_rows = tuple(sorted(transfer_maps, key=lambda row: row.map_id))
    subset_rows = tuple(tuple(sorted(str(item) for item in row)) for row in successful_donor_subsets)

    provisional = CandidateSynthesisRecord(
        candidate_id=str(candidate_id),
        target_domain_id=str(target_domain_id),
        target_contract_id=str(target_contract_id),
        elements=element_rows,
        donor_fragments=fragment_rows,
        composition_edges=edge_rows,
        transfer_maps=transfer_rows,
        old_regime_reaches_target=bool(old_regime_reaches_target),
        candidate_reaches_target=bool(candidate_reaches_target),
        hidden_consequence_passed=bool(hidden_consequence_passed),
        independent_validity_passed=bool(independent_validity_passed),
        successful_donor_subsets=subset_rows,
        digest="",
    )
    payload = provisional.unsigned()
    record = CandidateSynthesisRecord(
        **{**provisional.__dict__, "digest": content_digest(payload)}
    )
    record.verify()
    return record


__all__ = [
    "CandidateElement",
    "CandidateSynthesisRecord",
    "CompositionEdge",
    "DonorFragment",
    "ProvenanceClass",
    "SemanticElementKind",
    "StructuralTransferMap",
    "SynthesisAssessment",
    "SynthesisMode",
    "SynthesisTerminal",
    "TransferStrength",
    "assess_candidate_synthesis",
    "build_candidate_synthesis_record",
    "minimal_semantic_residuals",
    "minimal_successful_subsets",
    "minimum_separating_panels",
]
