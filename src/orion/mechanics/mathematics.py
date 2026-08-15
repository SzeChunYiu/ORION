from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class MathematicalFamily(str, Enum):
    SET_VALUED_RELATION = "SET_VALUED_RELATION"
    STATE_MACHINE = "STATE_MACHINE"
    GRAPH_HYPERGRAPH = "GRAPH_HYPERGRAPH"
    PARTIAL_ORDER = "PARTIAL_ORDER"
    CONSTRAINT_SYSTEM = "CONSTRAINT_SYSTEM"
    MULTIOBJECTIVE_OPTIMIZATION = "MULTIOBJECTIVE_OPTIMIZATION"
    INFORMATION_SELECTION = "INFORMATION_SELECTION"
    MEASUREMENT_MODEL = "MEASUREMENT_MODEL"
    HYPOTHESIS_SET = "HYPOTHESIS_SET"
    SIMILARITY_RETRIEVAL = "SIMILARITY_RETRIEVAL"
    DEPENDENCY_REACHABILITY = "DEPENDENCY_REACHABILITY"
    SET_GROWTH_FIXED_POINT = "SET_GROWTH_FIXED_POINT"
    STOPPING_RULE = "STOPPING_RULE"
    CONTENT_ADDRESSING = "CONTENT_ADDRESSING"


@dataclass(frozen=True)
class MathematicalFormulation:
    formulation_id: str
    mechanic_id: str
    families: tuple[MathematicalFamily, ...]
    objects: tuple[str, ...]
    canonical_relation: str
    assumptions: tuple[str, ...]
    forbidden_implicit_assumptions: tuple[str, ...]
    fallback_semantics: str
    falsifiers: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(not item.strip() for item in (self.formulation_id, self.mechanic_id, self.canonical_relation, self.fallback_semantics)):
            raise ValueError("mathematical formulation identity/relation/fallback are required")
        if not self.families or not self.objects or not self.assumptions or not self.falsifiers:
            raise ValueError("mathematical formulation requires families/objects/assumptions/falsifiers")


_PREFIX_FORMULATIONS: tuple[tuple[str, tuple[MathematicalFamily, ...], str, tuple[str, ...]], ...] = (
    ("FRAME.", (MathematicalFamily.CONSTRAINT_SYSTEM, MathematicalFamily.GRAPH_HYPERGRAPH), "Frame the task as a typed constraint/context object and a recursive obligation graph.", ("scope and target coordinates are explicitly typed",)),
    ("SEARCH.", (MathematicalFamily.INFORMATION_SELECTION, MathematicalFamily.GRAPH_HYPERGRAPH), "Select/query source and route candidates from a search frontier under hard coverage/resource constraints.", ("candidate/search identities and route provenance are observable",)),
    ("ABSORB.", (MathematicalFamily.SET_VALUED_RELATION, MathematicalFamily.GRAPH_HYPERGRAPH), "Map source observations into zero or more typed contextual contributions while preserving ambiguity and provenance.", ("source selectors and context are retained",)),
    ("RECONSTRUCT.", (MathematicalFamily.CONSTRAINT_SYSTEM, MathematicalFamily.GRAPH_HYPERGRAPH), "Construct compatible global/partial objects from typed local projections subject to relation and context constraints.", ("local projections need not admit a unique global object",)),
    ("DETECT.", (MathematicalFamily.CONSTRAINT_SYSTEM, MathematicalFamily.HYPOTHESIS_SET), "Compute residual/obstruction sets where current evidence/model/interface obligations are inconsistent or incomplete.", ("absence of detected residual is not proof of completeness",)),
    ("DIAGNOSE.", (MathematicalFamily.HYPOTHESIS_SET, MathematicalFamily.INFORMATION_SELECTION), "Maintain a set of competing cause/responsibility hypotheses and select discriminators that separate them.", ("probabilities are optional and must not be fabricated",)),
    ("REFRAME.", (MathematicalFamily.SET_VALUED_RELATION, MathematicalFamily.MULTIOBJECTIVE_OPTIMIZATION), "Select a scoped representation/decomposition/policy/method change subject to non-compensatory invariants.", ("candidate reframes remain proposal-only until validated",)),
    ("REOPEN.", (MathematicalFamily.DEPENDENCY_REACHABILITY, MathematicalFamily.GRAPH_HYPERGRAPH), "Propagate staleness/reopen only along typed dependency edges from changed coordinates.", ("dependency graph identity is explicit",)),
    ("SATURATE.", (MathematicalFamily.SET_GROWTH_FIXED_POINT, MathematicalFamily.STOPPING_RULE), "Assess bounded flatness of registered growth coordinates after heterogeneous challenge; emit OPEN/CANNOT_CHECK/CLOSED-at-cutoff.", ("search universe and basis are declared rather than universal",)),
    ("CROSS.MEMORY", (MathematicalFamily.INFORMATION_SELECTION, MathematicalFamily.CONTENT_ADDRESSING), "Select a bounded working view from content-addressed canonical memory while preserving mandatory epistemic material.", ("canonical storage and working context are distinct",)),
    ("CROSS.AUTHORITY", (MathematicalFamily.PARTIAL_ORDER,), "Compare scoped certificate sets by a non-escalating partial order rather than a universal scalar confidence.", ("certificate coordinates and scopes are explicit",)),
    ("CROSS.EXPERIENCE", (MathematicalFamily.SIMILARITY_RETRIEVAL, MathematicalFamily.GRAPH_HYPERGRAPH), "Retrieve and relate immutable task episodes by typed structural similarity and provenance.", ("similarity does not imply causal equivalence",)),
    ("CROSS.REVIEW", (MathematicalFamily.GRAPH_HYPERGRAPH, MathematicalFamily.CONSTRAINT_SYSTEM), "Audit claims against independent process/evidence lineages and blocking invariants.", ("role multiplicity is not evidence independence",)),
    ("CROSS.BENCHMARK", (MathematicalFamily.MEASUREMENT_MODEL,), "Map latent target constructs and task conditions through a declared instrument/evaluator to observed benchmark outcomes.", ("instrument/evaluator identity and construct interpretation are explicit",)),
    ("CROSS.EXPERIMENT_SELECTION", (MathematicalFamily.INFORMATION_SELECTION, MathematicalFamily.MULTIOBJECTIVE_OPTIMIZATION), "Select an information-acquisition action by discriminating value subject to cost and hard invariants.", ("scalar expected value is used only when calibration/tradeoffs are justified",)),
    ("CROSS.EXECUTION", (MathematicalFamily.STATE_MACHINE, MathematicalFamily.CONTENT_ADDRESSING), "Execute identity-bound state transitions and append reproducible receipts/events.", ("external side effects and runtime identities are explicit",)),
    ("CROSS.CONTEXT_POLICY", (MathematicalFamily.MULTIOBJECTIVE_OPTIMIZATION, MathematicalFamily.INFORMATION_SELECTION), "Choose a bounded context subset that contains mandatory material and optimizes declared utility/cost coordinates.", ("mandatory context cannot be silently truncated",)),
)

_TOP_LEVEL: dict[str, tuple[tuple[MathematicalFamily, ...], str, tuple[str, ...]]] = {
    "ORION_SOLVE.v1": ((MathematicalFamily.STATE_MACHINE, MathematicalFamily.GRAPH_HYPERGRAPH), "Compose mechanic transitions over a recursive obligation graph until verified bounded closure or a typed non-solution terminal.", ("all authority increases remain externally certified",)),
    "FRAME.v1": ((MathematicalFamily.CONSTRAINT_SYSTEM,), "Map a raw problem into a typed scoped task contract.", ("scope and blocking invariants are explicit",)),
    "SEARCH.v1": ((MathematicalFamily.INFORMATION_SELECTION,), "Select and execute heterogeneous information-acquisition actions.", ("retrieval output is proposal/evidence access, not authority",)),
    "ABSORB.v1": ((MathematicalFamily.SET_VALUED_RELATION,), "Map retrieved items to zero or more typed contextual contributions.", ("ambiguity is preserved",)),
    "RECONSTRUCT.v1": ((MathematicalFamily.CONSTRAINT_SYSTEM,), "Update the compatible global portrait/search-universe model from contributions.", ("global uniqueness is not assumed",)),
    "DETECT.v1": ((MathematicalFamily.HYPOTHESIS_SET,), "Emit the current set of material typed residuals.", ("detection coverage is bounded",)),
    "DIAGNOSE.v1": ((MathematicalFamily.HYPOTHESIS_SET,), "Narrow competing responsibility hypotheses using discriminating observations.", ("recurrence alone does not prove cause",)),
    "REFRAME.v1": ((MathematicalFamily.SET_VALUED_RELATION,), "Apply one justified typed state/formulation/policy proposal under governance.", ("ambiguous responsibility blocks high-impact revision",)),
    "REOPEN.v1": ((MathematicalFamily.DEPENDENCY_REACHABILITY,), "Invalidate dependent closure through typed dependency reachability.", ("negative history/evidence is monotone",)),
    "SATURATE_BOUNDED.v3": ((MathematicalFamily.SET_GROWTH_FIXED_POINT, MathematicalFamily.STOPPING_RULE), "Issue bounded stop/open/cannot-check from repeated flat registered growth under challenge.", ("absolute completeness is not representable",)),
}


def candidate_mathematical_formulation(cell: MechanicCell) -> MathematicalFormulation:
    selected = _TOP_LEVEL.get(cell.mechanic_id)
    if selected is None:
        for prefix, families, relation, assumptions in _PREFIX_FORMULATIONS:
            if cell.mechanic_id.startswith(prefix):
                selected = (families, relation, assumptions)
                break
    if selected is None:
        selected = ((MathematicalFamily.SET_VALUED_RELATION,), "Represent the mechanic as a typed relation from admissible input/state/action tuples to possible outputs/next states.", ("input/output/state/action domains are explicit",))
    families, relation, assumptions = selected
    return MathematicalFormulation(
        formulation_id=f"math:{cell.mechanic_id}:candidate-v0",
        mechanic_id=cell.mechanic_id,
        families=families,
        objects=("typed input domain", "typed state domain", "admissible action set", "typed output/status domain"),
        canonical_relation=relation,
        assumptions=assumptions,
        forbidden_implicit_assumptions=(
            "no fabricated probability distribution",
            "no unproved independence",
            "no assumed differentiability/convexity",
            "no scalar utility replacing hard non-compensatory gates without an explicit license",
        ),
        fallback_semantics="If a stronger formalism cannot be justified, retain a typed set-valued relation/identified set and return CANNOT_CHECK for computations requiring missing assumptions.",
        falsifiers=("a known/hostile case requires a distinction or state/action coordinate the candidate formalism cannot express", "the formalism licenses an invalid composition or hides a material uncertainty/obstruction"),
    )


def apply_candidate_mathematical_formulation(cell: MechanicCell) -> MechanicCell:
    formulation = candidate_mathematical_formulation(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("adequacy of the candidate mathematical family/relation and any stronger step-specific assumptions on real/fresh tasks",)))
    semantics = (
        f"family={','.join(item.value for item in formulation.families)}",
        formulation.canonical_relation,
        *formulation.assumptions,
        *formulation.forbidden_implicit_assumptions,
        formulation.fallback_semantics,
    )
    return replace(cell, mathematical_semantics=semantics, empirical_open_coordinates=empirical_open)


def apply_candidate_mathematical_formulations(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_candidate_mathematical_formulation(cell) for cell in cells)
