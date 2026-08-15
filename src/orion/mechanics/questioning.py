from __future__ import annotations

from dataclasses import dataclass

from .model import MechanicCell, MechanicDimension


@dataclass(frozen=True)
class MechanicQuestion:
    question_id: str
    mechanic_id: str
    dimension: MechanicDimension
    question: str
    blocking: bool = True


_PROMPTS: dict[MechanicDimension, str] = {
    MechanicDimension.INPUTS: "What exact typed inputs does this mechanic require, and which are mandatory versus optional?",
    MechanicDimension.OUTPUTS: "What exact typed outputs can this mechanic produce, including blocked or cannot-check outputs?",
    MechanicDimension.HANDOFF: "What fields, metrics, uncertainty and provenance must the next mechanic receive, and under what schema?",
    MechanicDimension.STATE: "What internal state does this mechanic maintain, what is latent versus explicit, and what state transition is allowed?",
    MechanicDimension.OBSERVABILITY: "What numbers/signals can a problem solver directly observe at this step, with units, cadence and measurement semantics?",
    MechanicDimension.ACTIONS: "What actions/effectors can this mechanic invoke, and which actions are forbidden?",
    MechanicDimension.TRANSITION_MODEL: "What relation maps inputs, state and actions to next state and outputs? Is it deterministic, stochastic, set-valued or partially known?",
    MechanicDimension.MATHEMATICS: "What mathematical formalism is needed to make this step precise enough to analyze, compose and falsify?",
    MechanicDimension.INVARIANTS: "Which invariants and hard constraints must hold regardless of local performance?",
    MechanicDimension.OBJECTIVE: "What is this mechanic trying to improve or preserve for the root problem?",
    MechanicDimension.METRICS: "Which non-compensatory metric vector should be measured here, and which numbers must flow downstream?",
    MechanicDimension.OPTIMIZATION: "Given its objective, metrics and constraints, how should this mechanic select or improve actions without hiding tradeoffs in one scalar?",
    MechanicDimension.UNCERTAINTY: "How are uncertainty, calibration, bounds and cannot-check states represented and propagated?",
    MechanicDimension.RESOURCES: "Which token/time/compute/memory/tool/data resources does this mechanic consume, and what are its budget/floor semantics?",
    MechanicDimension.FAILURE: "How can this mechanic fail, partially fail, silently fail or create false progress; what are the failure signatures and falsifiers?",
    MechanicDimension.DIAGNOSIS: "Given a failed or weak result, what observable evidence separates competing causes before repair?",
    MechanicDimension.STORAGE: "What must be stored durably from this step, at what granularity, and what can be recomputed rather than persisted?",
    MechanicDimension.PROVENANCE: "How are source identity, state version, action lineage, receipts and supersession represented so the step is reproducible?",
    MechanicDimension.VERIFICATION: "What independent or protected evidence can verify that this mechanic did what it claims, and what artifact closes each requirement?",
    MechanicDimension.AUTHORITY_SECURITY: "What authority may this mechanic create, what must it never create, and what trust/security boundaries protect that rule?",
    MechanicDimension.ENGINEERING: "What engineering properties matter here: idempotency, concurrency, recovery, determinism, latency, throughput, SLOs, observability and failure containment?",
    MechanicDimension.DEPENDENCIES: "Which upstream mechanics, external services, evidence or assumptions does this mechanic depend on, and which dependency failures propagate?",
    MechanicDimension.REOPEN: "What new observation, failure, contradiction or dependency change must stale this mechanic's closure and reopen it?",
    MechanicDimension.SEARCH_COVERAGE: "What search/source/representation route families must be challenged before claiming this mechanic's knowledge basis is flat?",
    MechanicDimension.PARENT_DISCIPLINE: "Which mature disciplines study this operation as a canonical problem, and what decomposition or variables do they use that ORION may be missing?",
    MechanicDimension.SATURATION: "What does bounded saturation mean for this exact mechanic, and how could apparently flat search still be falsely saturated?",
    MechanicDimension.EMPIRICAL_OPEN: "Which important performance, transfer or validity coordinates remain empirically unestablished after the current implementation?",
}

_PRIORITY: tuple[MechanicDimension, ...] = (
    MechanicDimension.AUTHORITY_SECURITY,
    MechanicDimension.VERIFICATION,
    MechanicDimension.FAILURE,
    MechanicDimension.OBSERVABILITY,
    MechanicDimension.HANDOFF,
    MechanicDimension.STATE,
    MechanicDimension.TRANSITION_MODEL,
    MechanicDimension.MATHEMATICS,
    MechanicDimension.METRICS,
    MechanicDimension.UNCERTAINTY,
    MechanicDimension.INVARIANTS,
    MechanicDimension.DEPENDENCIES,
    MechanicDimension.PARENT_DISCIPLINE,
    MechanicDimension.SEARCH_COVERAGE,
    MechanicDimension.SATURATION,
    MechanicDimension.INPUTS,
    MechanicDimension.OUTPUTS,
    MechanicDimension.ACTIONS,
    MechanicDimension.OBJECTIVE,
    MechanicDimension.OPTIMIZATION,
    MechanicDimension.RESOURCES,
    MechanicDimension.DIAGNOSIS,
    MechanicDimension.STORAGE,
    MechanicDimension.PROVENANCE,
    MechanicDimension.ENGINEERING,
    MechanicDimension.REOPEN,
    MechanicDimension.EMPIRICAL_OPEN,
)


def _satisfied(cell: MechanicCell, dimension: MechanicDimension) -> bool:
    if dimension in cell.waived_dimensions:
        return True
    mapping = {
        MechanicDimension.INPUTS: bool(cell.input_ids),
        MechanicDimension.OUTPUTS: bool(cell.output_ids),
        MechanicDimension.HANDOFF: bool(cell.handoff_fields),
        MechanicDimension.STATE: bool(cell.state_ids),
        MechanicDimension.OBSERVABILITY: bool(cell.observable_ids),
        MechanicDimension.ACTIONS: bool(cell.action_ids),
        MechanicDimension.TRANSITION_MODEL: bool(cell.transition_semantics),
        MechanicDimension.MATHEMATICS: bool(cell.mathematical_semantics),
        MechanicDimension.INVARIANTS: bool(cell.invariant_ids or cell.constraint_ids),
        MechanicDimension.OBJECTIVE: bool(cell.objective_ids),
        MechanicDimension.METRICS: bool(cell.metrics),
        MechanicDimension.OPTIMIZATION: bool(cell.optimization_rules),
        MechanicDimension.UNCERTAINTY: bool(cell.uncertainty_semantics),
        MechanicDimension.RESOURCES: bool(cell.resource_coordinates),
        MechanicDimension.FAILURE: bool(cell.failure_signatures and cell.falsifiers),
        MechanicDimension.DIAGNOSIS: bool(cell.diagnosis_rules),
        MechanicDimension.STORAGE: bool(cell.storage_contracts),
        MechanicDimension.PROVENANCE: bool(cell.provenance_contracts),
        MechanicDimension.VERIFICATION: bool(cell.verification_contracts),
        MechanicDimension.AUTHORITY_SECURITY: bool(cell.authority_boundaries),
        MechanicDimension.ENGINEERING: bool(cell.engineering_contracts),
        MechanicDimension.DEPENDENCIES: bool(cell.dependency_ids),
        MechanicDimension.REOPEN: bool(cell.reopen_triggers),
        MechanicDimension.SEARCH_COVERAGE: bool(cell.search_coverage_obligations),
        MechanicDimension.PARENT_DISCIPLINE: bool(cell.parent_domain_hypotheses),
        MechanicDimension.SATURATION: bool(cell.saturation_criteria),
        MechanicDimension.EMPIRICAL_OPEN: bool(cell.empirical_open_coordinates),
    }
    return mapping[dimension]


def generate_mechanic_questions(cell: MechanicCell) -> tuple[MechanicQuestion, ...]:
    """Deterministically expose every unfilled mechanic dimension.

    This is intentionally not an LLM prompt. It is a fixed audit grammar that an
    LLM may help answer, but cannot silently omit.
    """

    questions: list[MechanicQuestion] = []
    for dimension in _PRIORITY:
        if _satisfied(cell, dimension):
            continue
        questions.append(
            MechanicQuestion(
                question_id=f"{cell.mechanic_id}:{dimension.value}",
                mechanic_id=cell.mechanic_id,
                dimension=dimension,
                question=_PROMPTS[dimension],
                blocking=True,
            )
        )
    return tuple(questions)


def plan_next_questions(
    questions: tuple[MechanicQuestion, ...],
    *,
    limit: int = 8,
) -> tuple[MechanicQuestion, ...]:
    """V0 fixed-policy metareasoner: select the highest-priority open questions.

    Later versions may use value-of-computation evidence. V0 stays deterministic
    and auditable; the order above is policy, not scientific truth.
    """

    if limit < 1:
        raise ValueError("question plan limit must be positive")
    rank = {dimension: index for index, dimension in enumerate(_PRIORITY)}
    return tuple(sorted(questions, key=lambda item: (rank[item.dimension], item.question_id))[:limit])
