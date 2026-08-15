from __future__ import annotations

from dataclasses import replace

from .audit import audit_recursive
from .model import MechanicCell
from .questioning import MechanicQuestion
from .workflow import ORION_WORKFLOW_CELLS, ORION_WORKFLOW_ROOT_ID

# Provisional child mechanics recovered from ORION's own bootstrap residuals and
# selectively reconstructed from RAKL method surfaces. These are research objects,
# not a declaration that the decomposition is final.
_CHILD_SPECS: dict[str, tuple[tuple[str, str], ...]] = {
    "FRAME.v1": (
        ("FRAME.QUESTION.v0", "Define the active question, target and decision relevance."),
        ("FRAME.CONTEXT.v0", "Bind scope, population, regime, time, assumptions and observation boundary."),
        ("FRAME.AUTHORITY_TARGET.v0", "Declare the target authority/evidence level and blocking invariants."),
        ("FRAME.RESOURCES.v0", "Declare compute, token, time, data, tool and external-resource budgets."),
        ("FRAME.DECOMPOSE.v0", "Decompose the root problem into recursive decision-relevant mechanics/fibres."),
    ),
    "SEARCH.v1": (
        ("SEARCH.ROUTE.v0", "Select heterogeneous search route families without minting authority."),
        ("SEARCH.QUERY.v0", "Generate evidence-acquisition queries targeted at active residuals."),
        ("SEARCH.SOURCE.v0", "Select and qualify sources with identity, reliability and lineage awareness."),
        ("SEARCH.RETRIEVE.v0", "Execute retrieval and preserve exact query/source/result provenance."),
        ("SEARCH.ROUTE_STOP.v0", "Decide whether to continue, reformulate or stop one search route without claiming task saturation."),
    ),
    "ABSORB.v1": (
        ("ABSORB.SCIENTIFIC_LANGUAGE.v0", "Interpret scientific language, discourse, modality and scope into candidate structure."),
        ("ABSORB.CLAIM.v0", "Extract atomic scoped claims with exact evidence selectors."),
        ("ABSORB.REFERENCE_IDENTITY.v0", "Resolve entities, events, referents, aliases and identity hypotheses."),
        ("ABSORB.CONTEXT.v0", "Extract measurement, population, scale, regime, assumption and intervention context."),
        ("ABSORB.REPRESENTATION_MAP.v0", "Map terminology, mathematical coordinates and typed equivalence/approximation relations."),
        ("ABSORB.EVIDENCE_BIND.v0", "Bind claims/structures to evidence, provenance, source identity and verification state."),
    ),
    "RECONSTRUCT.v1": (
        ("RECONSTRUCT.ATLAS_UPDATE.v0", "Update the multi-representation atlas without collapsing distinct views."),
        ("RECONSTRUCT.GLUE.v0", "Test compatibility, transitions and local-to-global gluing across projections."),
        ("RECONSTRUCT.PORTRAIT.v0", "Construct the current global portrait while retaining pluralism, uncertainty and obstructions."),
        ("RECONSTRUCT.SEARCH_UNIVERSE.v0", "Update W_t when absorbed knowledge exposes new domains, representations or search routes."),
    ),
    "DETECT.v1": (
        ("DETECT.CONTRADICTION.v0", "Detect genuine contradictions only after identity/context/alignment checks."),
        ("DETECT.GAP.v0", "Detect evidence, representation, method, measurement and interface gaps relevant to the root target."),
        ("DETECT.COVERAGE.v0", "Detect search-universe and route-coverage residuals, including possible false flatness."),
        ("DETECT.FAILURE.v0", "Convert unsuccessful/partial executions into typed failure observations and residuals."),
    ),
    "DIAGNOSE.v1": (
        ("DIAGNOSE.HYPOTHESES.v0", "Generate competing responsibility/cause hypotheses for an observed residual."),
        ("DIAGNOSE.EXPERIENCE_RETRIEVAL.v0", "Retrieve structurally related prior episodes, failures, guards and negative history."),
        ("DIAGNOSE.DISCRIMINATOR.v0", "Select observations/experiments/computations that separate surviving cause hypotheses."),
        ("DIAGNOSE.ATTRIBUTION.v0", "Update failure responsibility only from discriminating evidence rather than recurrence alone."),
    ),
    "REFRAME.v1": (
        ("REFRAME.REPRESENTATION.v0", "Change the active representation when evidence shows the current coordinates are inadequate."),
        ("REFRAME.DECOMPOSITION.v0", "Split, merge or restructure mechanics/fibres after a supported decomposition residual."),
        ("REFRAME.SEARCH_POLICY.v0", "Change route/query/source policy after a supported retrieval/routing diagnosis."),
        ("REFRAME.METHOD.v0", "Construct a proposal-only method/operator challenger under Self-ORION governance."),
        ("REFRAME.OBJECTIVE.v0", "Propose an objective/QoI change when the current objective is diagnosed as inadequate."),
    ),
    "REOPEN.v1": (
        ("REOPEN.DEPENDENCY.v0", "Identify which downstream conclusions/receipts depend on a changed coordinate."),
        ("REOPEN.CLOSURE.v0", "Stale only dependent closure/saturation certificates while preserving unaffected evidence."),
        ("REOPEN.FIBRE.v0", "Reactivate the minimal affected research fibres/ancestor challenges."),
    ),
    "SATURATE_BOUNDED.v3": (
        ("SATURATE.KNOWLEDGE_FLATNESS.v0", "Measure substantive knowledge growth after typed deduplication."),
        ("SATURATE.FORMULATION_FLATNESS.v0", "Test whether question/representation/decomposition/measurement/evaluator formulation remains open."),
        ("SATURATE.ROUTE_COVERAGE.v0", "Audit heterogeneous route/source/domain coverage and lineage diversity."),
        ("SATURATE.OMISSION_CHALLENGE.v0", "Challenge the saturation basis for missed parents, representations and unknown unknowns."),
        ("SATURATE.STOP.v0", "Issue bounded stop/open/cannot-check without representing universal completeness."),
    ),
}

_CROSSCUT_SPECS: tuple[tuple[str, str], ...] = (
    ("CROSS.MEMORY.v0", "Persist canonical evidence/experience while compiling bounded operation-specific working views."),
    ("CROSS.AUTHORITY.v0", "Govern evidence certificates, non-escalation and scoped authority promotion."),
    ("CROSS.EXPERIENCE.v0", "Store episodes and govern failure/success-derived reusable lessons."),
    ("CROSS.REVIEW.v0", "Perform adversarial/independent checks with process and evidence-lineage separation."),
    ("CROSS.BENCHMARK.v0", "Freeze and execute known-answer, hostile, matched-resource and fresh-transfer evaluations."),
    ("CROSS.EXPERIMENT_SELECTION.v0", "Select discriminating information-acquisition actions under declared cost/uncertainty models."),
    ("CROSS.EXECUTION.v0", "Provide reproducible, recoverable, identity-bound software/tool/model execution."),
    ("CROSS.CONTEXT_POLICY.v0", "Compile the smallest sufficient epistemic working context under resource limits."),
)


# Every historical RAKL method surface is retained as provenance, not as an ORION
# ontology requirement. Multiple ORION child mechanics may refine one old surface.
RAKL_SURFACE_TO_CHILDREN: dict[str, tuple[str, ...]] = {
    "decomposition": ("FRAME.DECOMPOSE.v0", "REFRAME.DECOMPOSITION.v0"),
    "routing": ("SEARCH.ROUTE.v0", "REFRAME.SEARCH_POLICY.v0"),
    "search_query_generation": ("SEARCH.QUERY.v0",),
    "source_selection_reliability": ("SEARCH.SOURCE.v0", "ABSORB.EVIDENCE_BIND.v0"),
    "claim_extraction": ("ABSORB.SCIENTIFIC_LANGUAGE.v0", "ABSORB.CLAIM.v0"),
    "ontology_terminology_normalization": ("ABSORB.REFERENCE_IDENTITY.v0", "ABSORB.CONTEXT.v0"),
    "mathematical_context_translation": ("ABSORB.REPRESENTATION_MAP.v0",),
    "equivalence_similarity": ("ABSORB.REPRESENTATION_MAP.v0", "RECONSTRUCT.ATLAS_UPDATE.v0"),
    "contextual_theory_gluing": ("RECONSTRUCT.GLUE.v0",),
    "contradiction_diagnosis": ("DETECT.CONTRADICTION.v0", "DIAGNOSE.HYPOTHESES.v0"),
    "gap_discovery": ("DETECT.GAP.v0", "DETECT.COVERAGE.v0"),
    "experiment_query_selection": ("CROSS.EXPERIMENT_SELECTION.v0", "DIAGNOSE.DISCRIMINATOR.v0"),
    "synthesis": ("RECONSTRUCT.PORTRAIT.v0",),
    "memory": ("CROSS.MEMORY.v0", "DIAGNOSE.EXPERIENCE_RETRIEVAL.v0"),
    "review": ("CROSS.REVIEW.v0", "DIAGNOSE.ATTRIBUTION.v0"),
    "benchmarking": ("CROSS.BENCHMARK.v0",),
    "authority_promotion": ("CROSS.AUTHORITY.v0",),
    "saturation_stopping": ("SATURATE.KNOWLEDGE_FLATNESS.v0", "SATURATE.ROUTE_COVERAGE.v0", "SATURATE.STOP.v0"),
    "prompting_context_policy": ("CROSS.CONTEXT_POLICY.v0",),
    "capability_shaping": ("REFRAME.METHOD.v0", "DIAGNOSE.ATTRIBUTION.v0"),
    "software_architecture_execution": ("CROSS.EXECUTION.v0",),
    "research_portfolio_tree": ("FRAME.DECOMPOSE.v0", "REOPEN.FIBRE.v0"),
    "objective_evolution": ("FRAME.QUESTION.v0", "REFRAME.OBJECTIVE.v0"),
    "generator_transport": ("CROSS.EXECUTION.v0", "REFRAME.METHOD.v0"),
}


def _child(parent_id: str, mechanic_id: str, purpose: str) -> MechanicCell:
    return MechanicCell(
        mechanic_id=mechanic_id,
        purpose=purpose,
        scope=f"child mechanic of {parent_id}",
        input_ids=("ParentMechanicContext",),
        output_ids=("ChildMechanicReceipt",),
        authority_boundaries=("proposal-only unless an explicit protected verification/promotion path grants authority",),
        reopen_triggers=("fresh hostile failure", "parent contract changes", "new decision-relevant residual"),
        empirical_open_coordinates=("real-task utility", "fresh transfer", "cost/performance envelope"),
    )


def expanded_workflow_cells() -> tuple[MechanicCell, ...]:
    """Return a provisional recursively decomposed ORION workflow for research/audit."""

    cells = {item.mechanic_id: item for item in ORION_WORKFLOW_CELLS}
    for parent_id, specs in _CHILD_SPECS.items():
        child_ids = tuple(mechanic_id for mechanic_id, _ in specs)
        cells[parent_id] = replace(cells[parent_id], child_mechanic_ids=child_ids)
        for mechanic_id, purpose in specs:
            cells[mechanic_id] = _child(parent_id, mechanic_id, purpose)

    crosscut_ids = tuple(mechanic_id for mechanic_id, _ in _CROSSCUT_SPECS)
    root = cells[ORION_WORKFLOW_ROOT_ID]
    cells[ORION_WORKFLOW_ROOT_ID] = replace(
        root,
        child_mechanic_ids=tuple(dict.fromkeys(root.child_mechanic_ids + crosscut_ids)),
    )
    for mechanic_id, purpose in _CROSSCUT_SPECS:
        cells[mechanic_id] = _child(ORION_WORKFLOW_ROOT_ID, mechanic_id, purpose)
    return tuple(cells[key] for key in sorted(cells))


def expanded_mechanical_backlog() -> tuple[MechanicQuestion, ...]:
    cells = expanded_workflow_cells()
    by_id = {item.mechanic_id: item for item in cells}
    report = audit_recursive(by_id, ORION_WORKFLOW_ROOT_ID)
    return tuple(question for item in report.reports for question in item.open_questions)
