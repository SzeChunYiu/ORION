"""Typed knowledge-web, proof-economy, transfer, and self-application contracts.

This module is deliberately non-authorizing.  It helps a research programme
state which ingredients, support families, proof obligations, transfer
correspondences, and synchronization surfaces are load-bearing.  It never
turns an internally generated proposal or a locally green test into
scientific, novelty, publication, or adoption authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import Iterable, Mapping, Sequence


class ContractError(ValueError):
    """Raised when a frozen contract is structurally malformed."""


class NodeKind(str, Enum):
    QUESTION = "QUESTION"
    OBJECT = "OBJECT"
    REPRESENTATION = "REPRESENTATION"
    ASSUMPTION = "ASSUMPTION"
    HYPOTHESIS = "HYPOTHESIS"
    MECHANISM = "MECHANISM"
    INVARIANT = "INVARIANT"
    METHOD = "METHOD"
    OPERATOR = "OPERATOR"
    EXPERIMENT = "EXPERIMENT"
    INSTRUMENT = "INSTRUMENT"
    VALIDATOR = "VALIDATOR"
    EVIDENCE = "EVIDENCE"
    DONOR = "DONOR"
    RESOURCE = "RESOURCE"
    AUTHORITY = "AUTHORITY"
    FAILURE = "FAILURE"
    CLAIM = "CLAIM"
    THEORY = "THEORY"
    CODE = "CODE"
    HARNESS = "HARNESS"
    PAPER = "PAPER"
    MANIFEST = "MANIFEST"
    ISSUE = "ISSUE"
    OPEN_MOVE_CLASS = "OPEN_MOVE_CLASS"


class EdgeKind(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    DERIVES = "DERIVES"
    REFINES = "REFINES"
    CORRESPONDS_TO = "CORRESPONDS_TO"
    ANALOGOUS_TO = "ANALOGOUS_TO"
    COMPOSES_WITH = "COMPOSES_WITH"
    CONTRADICTS = "CONTRADICTS"
    OBSTRUCTS = "OBSTRUCTS"
    EXPLAINS = "EXPLAINS"
    PREDICTS = "PREDICTS"
    DISTINGUISHES = "DISTINGUISHES"
    VALIDATES = "VALIDATES"
    SUBSUMES = "SUBSUMES"
    REOPENS = "REOPENS"
    COSTS = "COSTS"
    AUTHORIZES = "AUTHORIZES"
    SYNCHRONIZES = "SYNCHRONIZES"


class ProofMethod(str, Enum):
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    CONSTRUCTIVE_WITNESS = "CONSTRUCTIVE_WITNESS"
    EXHAUSTIVE_ENUMERATION = "EXHAUSTIVE_ENUMERATION"
    REDUCTION = "REDUCTION"
    FORMAL_PROOF = "FORMAL_PROOF"
    INDUCTION = "INDUCTION"
    MATCHED_COUNTERMODEL = "MATCHED_COUNTERMODEL"
    ABLATION = "ABLATION"
    INTERVENTION = "INTERVENTION"
    HELD_OUT_TRANSFER = "HELD_OUT_TRANSFER"
    COUNTERFACTUAL_TWIN = "COUNTERFACTUAL_TWIN"
    EXTERNAL_REVIEW = "EXTERNAL_REVIEW"


class AuthorityClass(str, Enum):
    LOCAL_EXACT = "LOCAL_EXACT"
    SAME_PROGRAMME = "SAME_PROGRAMME"
    PROTECTED_EVALUATOR = "PROTECTED_EVALUATOR"
    EXTERNAL_DOMAIN = "EXTERNAL_DOMAIN"
    EXTERNAL_NOVELTY = "EXTERNAL_NOVELTY"
    EXTERNAL_ADOPTION = "EXTERNAL_ADOPTION"


class ClaimDelta(str, Enum):
    NONE = "NONE"
    SCOPE_NOTE_ONLY = "SCOPE_NOTE_ONLY"
    THEOREM_NARROWED = "THEOREM_NARROWED"
    THEOREM_EXTENDED = "THEOREM_EXTENDED"
    EMPIRICAL_CLAIM_CHANGED = "EMPIRICAL_CLAIM_CHANGED"


class SelfApplicationState(str, Enum):
    VALID_FOR_FROZEN_EXECUTION = "VALID_FOR_FROZEN_EXECUTION"
    SELF_EVALUATION_INVALID = "SELF_EVALUATION_INVALID"
    SELF_ADOPTION_INVALID = "SELF_ADOPTION_INVALID"
    ORIGIN_UNSEALED = "ORIGIN_UNSEALED"
    OLD_CLOSURE_UNSEALED = "OLD_CLOSURE_UNSEALED"
    HIDDEN_CONSEQUENCE_EMPTY = "HIDDEN_CONSEQUENCE_EMPTY"
    ALTERNATIVE_FAMILY_EMPTY = "ALTERNATIVE_FAMILY_EMPTY"
    TERMINAL_FAMILY_INCOMPLETE = "TERMINAL_FAMILY_INCOMPLETE"


class TransferState(str, Enum):
    STRUCTURAL_TRANSFER_CANDIDATE = "STRUCTURAL_TRANSFER_CANDIDATE"
    SURFACE_ANALOGY_ONLY = "SURFACE_ANALOGY_ONLY"
    TARGET_VALIDATOR_MISSING = "TARGET_VALIDATOR_MISSING"
    DONOR_FIRST_REFUSAL_MISSING = "DONOR_FIRST_REFUSAL_MISSING"
    RESOURCE_CONTRACT_MISSING = "RESOURCE_CONTRACT_MISSING"
    AUTHORITY_LAUNDERING_INVALID = "AUTHORITY_LAUNDERING_INVALID"


@dataclass(frozen=True)
class KnowledgeNode:
    node_id: str
    kind: NodeKind
    domain: str
    description: str
    content_identity: str

    def __post_init__(self) -> None:
        for field_name in ("node_id", "domain", "description", "content_identity"):
            if not getattr(self, field_name).strip():
                raise ContractError(f"KnowledgeNode.{field_name} must be non-empty")


@dataclass(frozen=True)
class KnowledgeEdge:
    edge_id: str
    source_id: str
    target_id: str
    kind: EdgeKind
    load_bearing: bool = False
    reopen_on_change: bool = False
    scope: str = "declared"

    def __post_init__(self) -> None:
        for field_name in ("edge_id", "source_id", "target_id", "scope"):
            if not getattr(self, field_name).strip():
                raise ContractError(f"KnowledgeEdge.{field_name} must be non-empty")
        if self.source_id == self.target_id:
            raise ContractError("self-edges are not allowed in KnowledgeWeb.v1")


@dataclass(frozen=True)
class SupportFamily:
    family_id: str
    target_id: str
    required_node_ids: tuple[str, ...]
    required_edge_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.family_id.strip() or not self.target_id.strip():
            raise ContractError("SupportFamily identifiers must be non-empty")
        if not self.required_node_ids:
            raise ContractError("a support family requires at least one ingredient")
        if len(set(self.required_node_ids)) != len(self.required_node_ids):
            raise ContractError("duplicate required node in support family")
        if len(set(self.required_edge_ids)) != len(self.required_edge_ids):
            raise ContractError("duplicate required edge in support family")


@dataclass(frozen=True)
class SupportFamilyStatus:
    family_id: str
    complete: bool
    present_node_ids: tuple[str, ...]
    missing_node_ids: tuple[str, ...]
    present_edge_ids: tuple[str, ...]
    missing_edge_ids: tuple[str, ...]

    @property
    def missing_count(self) -> int:
        return len(self.missing_node_ids) + len(self.missing_edge_ids)


@dataclass(frozen=True)
class TargetSupportStatus:
    target_id: str
    supported: bool
    family_statuses: tuple[SupportFamilyStatus, ...]
    best_missing_count: int


@dataclass(frozen=True)
class KnowledgeWeb:
    nodes: tuple[KnowledgeNode, ...]
    edges: tuple[KnowledgeEdge, ...]
    support_families: tuple[SupportFamily, ...] = ()
    version: str = "orion.knowledge-web.v1"
    _nodes_by_id: Mapping[str, KnowledgeNode] = field(init=False, repr=False)
    _edges_by_id: Mapping[str, KnowledgeEdge] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ContractError("KnowledgeWeb.version must be non-empty")
        nodes_by_id = _unique_index(self.nodes, "node_id", "knowledge node")
        edges_by_id = _unique_index(self.edges, "edge_id", "knowledge edge")
        for edge in self.edges:
            if edge.source_id not in nodes_by_id or edge.target_id not in nodes_by_id:
                raise ContractError(f"edge {edge.edge_id} has an unknown endpoint")
        family_ids: set[str] = set()
        for family in self.support_families:
            if family.family_id in family_ids:
                raise ContractError(f"duplicate support family: {family.family_id}")
            family_ids.add(family.family_id)
            if family.target_id not in nodes_by_id:
                raise ContractError(f"support family {family.family_id} has unknown target")
            unknown_nodes = set(family.required_node_ids) - set(nodes_by_id)
            unknown_edges = set(family.required_edge_ids) - set(edges_by_id)
            if unknown_nodes or unknown_edges:
                raise ContractError(
                    f"support family {family.family_id} references unknown objects: "
                    f"nodes={sorted(unknown_nodes)}, edges={sorted(unknown_edges)}"
                )
        object.__setattr__(self, "_nodes_by_id", nodes_by_id)
        object.__setattr__(self, "_edges_by_id", edges_by_id)

    def node(self, node_id: str) -> KnowledgeNode:
        try:
            return self._nodes_by_id[node_id]
        except KeyError as exc:
            raise ContractError(f"unknown node: {node_id}") from exc

    def support_status(
        self,
        target_id: str,
        available_node_ids: Iterable[str],
        available_edge_ids: Iterable[str] | None = None,
    ) -> TargetSupportStatus:
        self.node(target_id)
        available_nodes = set(available_node_ids)
        available_edges = set(available_edge_ids) if available_edge_ids is not None else set(self._edges_by_id)
        unknown_nodes = available_nodes - set(self._nodes_by_id)
        unknown_edges = available_edges - set(self._edges_by_id)
        if unknown_nodes or unknown_edges:
            raise ContractError(
                f"availability set references unknown objects: "
                f"nodes={sorted(unknown_nodes)}, edges={sorted(unknown_edges)}"
            )
        families = [family for family in self.support_families if family.target_id == target_id]
        if not families:
            return TargetSupportStatus(target_id, False, (), 0)
        statuses: list[SupportFamilyStatus] = []
        for family in families:
            req_nodes = set(family.required_node_ids)
            req_edges = set(family.required_edge_ids)
            missing_nodes = tuple(sorted(req_nodes - available_nodes))
            missing_edges = tuple(sorted(req_edges - available_edges))
            statuses.append(
                SupportFamilyStatus(
                    family_id=family.family_id,
                    complete=not missing_nodes and not missing_edges,
                    present_node_ids=tuple(sorted(req_nodes & available_nodes)),
                    missing_node_ids=missing_nodes,
                    present_edge_ids=tuple(sorted(req_edges & available_edges)),
                    missing_edge_ids=missing_edges,
                )
            )
        return TargetSupportStatus(
            target_id=target_id,
            supported=any(status.complete for status in statuses),
            family_statuses=tuple(statuses),
            best_missing_count=min(status.missing_count for status in statuses),
        )

    def impact_closure(self, changed_node_ids: Iterable[str]) -> tuple[str, ...]:
        changed = set(changed_node_ids)
        unknown = changed - set(self._nodes_by_id)
        if unknown:
            raise ContractError(f"unknown changed node(s): {sorted(unknown)}")
        impacted = set(changed)
        frontier = list(changed)
        outgoing: dict[str, list[KnowledgeEdge]] = {}
        for edge in self.edges:
            if edge.reopen_on_change:
                outgoing.setdefault(edge.source_id, []).append(edge)
        while frontier:
            source = frontier.pop()
            for edge in outgoing.get(source, []):
                if edge.target_id not in impacted:
                    impacted.add(edge.target_id)
                    frontier.append(edge.target_id)
        return tuple(sorted(impacted))

    def load_bearing_ancestors(self, target_id: str) -> tuple[str, ...]:
        self.node(target_id)
        ancestors = {target_id}
        frontier = [target_id]
        incoming: dict[str, list[KnowledgeEdge]] = {}
        for edge in self.edges:
            if edge.load_bearing:
                incoming.setdefault(edge.target_id, []).append(edge)
        while frontier:
            target = frontier.pop()
            for edge in incoming.get(target, []):
                if edge.source_id not in ancestors:
                    ancestors.add(edge.source_id)
                    frontier.append(edge.source_id)
        return tuple(sorted(ancestors))


@dataclass(frozen=True)
class CostVector:
    dimensions: tuple[str, ...]
    values: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.dimensions or len(self.dimensions) != len(self.values):
            raise ContractError("cost dimensions and values must have equal non-zero length")
        if len(set(self.dimensions)) != len(self.dimensions):
            raise ContractError("cost dimensions must be unique")
        if any(not dimension.strip() for dimension in self.dimensions):
            raise ContractError("cost dimension names must be non-empty")
        if any(value < 0 for value in self.values):
            raise ContractError("cost values must be non-negative")

    def __add__(self, other: "CostVector") -> "CostVector":
        self._check_compatible(other)
        return CostVector(self.dimensions, tuple(a + b for a, b in zip(self.values, other.values)))

    def weakly_dominates(self, other: "CostVector") -> bool:
        self._check_compatible(other)
        return all(a <= b for a, b in zip(self.values, other.values))

    def strictly_dominates(self, other: "CostVector") -> bool:
        return self.weakly_dominates(other) and self.values != other.values

    def weighted_total(self, weights: Mapping[str, float]) -> float:
        if set(weights) != set(self.dimensions):
            raise ContractError("explicit weights must cover every and only declared cost dimension")
        if any(value < 0 for value in weights.values()):
            raise ContractError("weights must be non-negative")
        return sum(weights[name] * value for name, value in zip(self.dimensions, self.values))

    def _check_compatible(self, other: "CostVector") -> None:
        if self.dimensions != other.dimensions:
            raise ContractError("cost vectors have incompatible dimensions")


@dataclass(frozen=True)
class ProofObligation:
    obligation_id: str
    acceptable_methods: frozenset[ProofMethod]
    acceptable_authorities: frozenset[AuthorityClass]

    def __post_init__(self) -> None:
        if not self.obligation_id.strip():
            raise ContractError("ProofObligation.obligation_id must be non-empty")
        if not self.acceptable_methods or not self.acceptable_authorities:
            raise ContractError("proof obligations require methods and authorities")


@dataclass(frozen=True)
class ProofOption:
    option_id: str
    method: ProofMethod
    authority: AuthorityClass
    discharges: frozenset[str]
    cost: CostVector
    exact_scope: str
    required_preconditions: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.option_id.strip() or not self.exact_scope.strip():
            raise ContractError("ProofOption identifiers and scope must be non-empty")
        if not self.discharges:
            raise ContractError("a proof option must discharge at least one obligation")


@dataclass(frozen=True)
class ProofPlan:
    option_ids: tuple[str, ...]
    discharged_obligation_ids: tuple[str, ...]
    cost: CostVector


@dataclass(frozen=True)
class ProofEconomyResult:
    obligations: tuple[str, ...]
    adequate_plans: tuple[ProofPlan, ...]
    pareto_plans: tuple[ProofPlan, ...]


def pareto_minimal_proof_plans(
    obligations: Sequence[ProofObligation],
    options: Sequence[ProofOption],
    available_preconditions: Iterable[str] = (),
    *,
    max_options: int = 20,
) -> ProofEconomyResult:
    """Enumerate adequate proof plans and retain the Pareto frontier.

    The search is exact for the supplied option set.  No scalar exchange rate
    is invented: scalar selection is a separate operation requiring explicit
    weights from an authority outside the compared outcomes.
    """

    if not obligations:
        raise ContractError("at least one proof obligation is required")
    if len(options) > max_options:
        raise ContractError(f"exact proof-plan search capped at {max_options} options")
    obligation_index = _unique_index(obligations, "obligation_id", "proof obligation")
    option_index = _unique_index(options, "option_id", "proof option")
    del obligation_index, option_index
    dimensions = options[0].cost.dimensions if options else ()
    for option in options:
        if option.cost.dimensions != dimensions:
            raise ContractError("all proof options must share one cost-vector contract")
    preconditions = set(available_preconditions)
    adequate: list[ProofPlan] = []
    for count in range(1, len(options) + 1):
        for selected in combinations(options, count):
            if any(not option.required_preconditions <= preconditions for option in selected):
                continue
            discharged: set[str] = set()
            for obligation in obligations:
                if any(
                    obligation.obligation_id in option.discharges
                    and option.method in obligation.acceptable_methods
                    and option.authority in obligation.acceptable_authorities
                    for option in selected
                ):
                    discharged.add(obligation.obligation_id)
            if len(discharged) != len(obligations):
                continue
            total = CostVector(dimensions, tuple(0 for _ in dimensions))
            for option in selected:
                total = total + option.cost
            adequate.append(
                ProofPlan(
                    option_ids=tuple(sorted(option.option_id for option in selected)),
                    discharged_obligation_ids=tuple(sorted(discharged)),
                    cost=total,
                )
            )
    pareto = [
        plan
        for plan in adequate
        if not any(other.cost.strictly_dominates(plan.cost) for other in adequate if other != plan)
    ]
    return ProofEconomyResult(
        obligations=tuple(obligation.obligation_id for obligation in obligations),
        adequate_plans=tuple(sorted(adequate, key=lambda plan: plan.option_ids)),
        pareto_plans=tuple(sorted(pareto, key=lambda plan: (plan.cost.values, plan.option_ids))),
    )


def select_proof_plan_with_explicit_weights(
    plans: Sequence[ProofPlan], weights: Mapping[str, float]
) -> ProofPlan:
    if not plans:
        raise ContractError("cannot select from an empty plan family")
    ranked = sorted(
        plans,
        key=lambda plan: (plan.cost.weighted_total(weights), plan.cost.values, plan.option_ids),
    )
    return ranked[0]


@dataclass(frozen=True)
class SelfApplicationContract:
    subject_version: str
    problem_identity: str
    proposer_principal: str
    evaluator_principal: str
    adopter_principal: str
    proposal_origin_sealed: bool
    old_closure_sealed: bool
    hidden_consequence_ids: tuple[str, ...]
    registered_alternative_ids: tuple[str, ...]
    positive_terminal: str
    negative_terminal: str
    cannot_check_terminal: str


def assess_self_application(contract: SelfApplicationContract) -> SelfApplicationState:
    if contract.proposer_principal == contract.evaluator_principal:
        return SelfApplicationState.SELF_EVALUATION_INVALID
    if contract.adopter_principal in {contract.proposer_principal, contract.evaluator_principal}:
        return SelfApplicationState.SELF_ADOPTION_INVALID
    if not contract.proposal_origin_sealed:
        return SelfApplicationState.ORIGIN_UNSEALED
    if not contract.old_closure_sealed:
        return SelfApplicationState.OLD_CLOSURE_UNSEALED
    if not contract.hidden_consequence_ids:
        return SelfApplicationState.HIDDEN_CONSEQUENCE_EMPTY
    if not contract.registered_alternative_ids:
        return SelfApplicationState.ALTERNATIVE_FAMILY_EMPTY
    if not all(
        value.strip()
        for value in (
            contract.subject_version,
            contract.problem_identity,
            contract.positive_terminal,
            contract.negative_terminal,
            contract.cannot_check_terminal,
        )
    ):
        return SelfApplicationState.TERMINAL_FAMILY_INCOMPLETE
    return SelfApplicationState.VALID_FOR_FROZEN_EXECUTION


@dataclass(frozen=True)
class TransferContract:
    source_domain: str
    target_domain: str
    relational_correspondence_ids: tuple[str, ...]
    target_validator_id: str | None
    donor_first_refusal_completed: bool
    resource_contract_id: str | None
    authority_nontransfer: bool


def assess_transfer(contract: TransferContract) -> TransferState:
    if not contract.relational_correspondence_ids:
        return TransferState.SURFACE_ANALOGY_ONLY
    if not contract.target_validator_id:
        return TransferState.TARGET_VALIDATOR_MISSING
    if not contract.donor_first_refusal_completed:
        return TransferState.DONOR_FIRST_REFUSAL_MISSING
    if not contract.resource_contract_id:
        return TransferState.RESOURCE_CONTRACT_MISSING
    if not contract.authority_nontransfer:
        return TransferState.AUTHORITY_LAUNDERING_INVALID
    return TransferState.STRUCTURAL_TRANSFER_CANDIDATE


@dataclass(frozen=True)
class ChangeImpactReceipt:
    changed_node_ids: tuple[str, ...]
    impacted_node_ids: tuple[str, ...]
    impacted_kinds: tuple[NodeKind, ...]
    claim_delta: ClaimDelta
    authority_receipt_present: bool
    claim_bearing_paper_update_allowed: bool
    required_sync_surfaces: tuple[NodeKind, ...]


def derive_change_impact(
    web: KnowledgeWeb,
    changed_node_ids: Iterable[str],
    *,
    claim_delta: ClaimDelta = ClaimDelta.NONE,
    authority_receipt_present: bool = False,
) -> ChangeImpactReceipt:
    changed = tuple(sorted(set(changed_node_ids)))
    impacted = web.impact_closure(changed)
    impacted_kinds = tuple(sorted({web.node(node_id).kind for node_id in impacted}, key=lambda kind: kind.value))
    claim_bearing_allowed = (
        NodeKind.PAPER not in impacted_kinds
        or (claim_delta not in {ClaimDelta.NONE, ClaimDelta.SCOPE_NOTE_ONLY} and authority_receipt_present)
    )
    sync_kinds = tuple(
        kind
        for kind in (
            NodeKind.THEORY,
            NodeKind.CODE,
            NodeKind.HARNESS,
            NodeKind.PAPER,
            NodeKind.AUTHORITY,
            NodeKind.MANIFEST,
            NodeKind.ISSUE,
        )
        if kind in impacted_kinds
    )
    return ChangeImpactReceipt(
        changed_node_ids=changed,
        impacted_node_ids=impacted,
        impacted_kinds=impacted_kinds,
        claim_delta=claim_delta,
        authority_receipt_present=authority_receipt_present,
        claim_bearing_paper_update_allowed=claim_bearing_allowed,
        required_sync_surfaces=sync_kinds,
    )


def _unique_index(items: Sequence[object], attribute: str, label: str) -> dict[str, object]:
    index: dict[str, object] = {}
    for item in items:
        key = getattr(item, attribute)
        if key in index:
            raise ContractError(f"duplicate {label}: {key}")
        index[key] = item
    return index
