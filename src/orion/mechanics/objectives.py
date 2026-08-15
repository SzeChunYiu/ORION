from __future__ import annotations

from dataclasses import dataclass, replace

from .model import MechanicCell


@dataclass(frozen=True)
class MechanicObjective:
    objective_id: str
    mechanic_id: str
    target: str
    hard_gates: tuple[str, ...]
    root_progress_semantics: str
    anti_objectives: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.objective_id, self.mechanic_id, self.target, self.root_progress_semantics)):
            raise ValueError("mechanic objective identity/target/root-progress semantics are required")
        if not self.hard_gates or not self.anti_objectives:
            raise ValueError("mechanic objective requires hard gates and anti-objectives")


_OBJECTIVE_BY_PREFIX: tuple[tuple[str, str], ...] = (
    ("FRAME.", "Produce the smallest decision-sufficient, falsifiable/boundable scoped task formulation that preserves material alternatives and required evidence/authority targets."),
    ("SEARCH.", "Acquire the highest-value root-relevant evidence/knowledge coverage per declared resource cost while preserving route diversity and source/provenance integrity."),
    ("ABSORB.", "Maximize faithful recoverable structure from sources while minimizing false normalization, identity collapse, scope loss and unsupported authority."),
    ("RECONSTRUCT.", "Increase the explanatory/decision-useful global portrait by connecting compatible projections while minimizing false gluing and loss of plural/obstructed structure."),
    ("DETECT.", "Expose material root-relevant contradictions, gaps, coverage failures and execution failures with calibrated/explicit detection limitations."),
    ("DIAGNOSE.", "Reduce the set of plausible responsible causes/layers using discriminating evidence at acceptable cost without promoting recurrence into causality."),
    ("REFRAME.", "Construct the smallest supported formulation/method change that resolves the diagnosed residual and improves root-relevant capability under preserved invariants."),
    ("REOPEN.", "Reopen the minimal complete dependent work set needed after a material change while preserving unaffected evidence/history/closure."),
    ("SATURATE.", "Stop research only when registered knowledge/formulation/coverage/failure/method coordinates are bounded-flat under heterogeneous challenge and further material value is unestablished."),
    ("CROSS.MEMORY", "Maximize retrieval of mandatory/root-relevant canonical knowledge and experience within the working-context budget without silently erasing provenance or negative history."),
    ("CROSS.AUTHORITY", "Permit the strongest scoped authority justified by evidence certificates while preventing cross-axis escalation and self-promotion."),
    ("CROSS.EXPERIENCE", "Increase reusable problem-solving competence from immutable episodes while minimizing false transfer and preserving harmful/null experience."),
    ("CROSS.REVIEW", "Maximize detection of material unsupported claims, hidden assumptions and failure modes under process/evidence-lineage separation."),
    ("CROSS.BENCHMARK", "Measure the intended target construct with sufficient validity/reliability/uncertainty information to support the registered decision."),
    ("CROSS.EXPERIMENT_SELECTION", "Select the lowest-cost admissible information-acquisition action that best separates root-relevant surviving alternatives."),
    ("CROSS.EXECUTION", "Execute declared actions reproducibly and recoverably with exact identity, bounded side effects and complete receipts."),
    ("CROSS.CONTEXT_POLICY", "Compile the smallest sufficient working context that contains all mandatory epistemic material within the resource budget."),
)

_TOP_LEVEL_PREFIX = {
    "ORION_SOLVE.v1": "CROSS.EXECUTION",
    "FRAME.v1": "FRAME.",
    "SEARCH.v1": "SEARCH.",
    "ABSORB.v1": "ABSORB.",
    "RECONSTRUCT.v1": "RECONSTRUCT.",
    "DETECT.v1": "DETECT.",
    "DIAGNOSE.v1": "DIAGNOSE.",
    "REFRAME.v1": "REFRAME.",
    "REOPEN.v1": "REOPEN.",
    "SATURATE_BOUNDED.v3": "SATURATE.",
}


def candidate_objective(cell: MechanicCell) -> MechanicObjective:
    lookup_id = _TOP_LEVEL_PREFIX.get(cell.mechanic_id, cell.mechanic_id)
    target = "Advance the declared root-relevant obligation of this mechanic under its typed contract."
    for prefix, candidate in _OBJECTIVE_BY_PREFIX:
        if lookup_id.startswith(prefix):
            target = candidate
            break
    return MechanicObjective(
        objective_id=f"objective:{cell.mechanic_id}:candidate-v0",
        mechanic_id=cell.mechanic_id,
        target=target,
        hard_gates=(
            "all blocking authority/safety/interface/evaluator invariants pass",
            "missing mandatory evidence/verification does not count as success",
            "local metric improvement cannot substitute for root-progress transport",
            "resource exhaustion cannot be rounded up to closure",
        ),
        root_progress_semantics="Progress is credited to the root only through an explicit typed dependency/transport witness showing that the local change improves or closes a registered root obligation under preserved blocking invariants.",
        anti_objectives=(
            "maximize raw idea/source/token/action count",
            "optimize a proxy by weakening the task/evaluator",
            "hide uncertainty, failures, negative history or verification debt",
        ),
    )


def apply_candidate_objective(cell: MechanicCell) -> MechanicCell:
    objective = candidate_objective(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific objective/utility construct, root-transport validity, tradeoff semantics and harmful proxy controls",)))
    return replace(cell, objective_ids=(objective.objective_id,), empirical_open_coordinates=empirical_open)


def apply_candidate_objectives(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_candidate_objective(cell) for cell in cells)
