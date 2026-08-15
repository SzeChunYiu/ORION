from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class ActionClass(str, Enum):
    INSPECT = "INSPECT"
    INFORMATION_ACQUISITION = "INFORMATION_ACQUISITION"
    TRANSFORM = "TRANSFORM"
    CONTROL = "CONTROL"
    VERIFY = "VERIFY"
    EXTERNAL_EFFECT = "EXTERNAL_EFFECT"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True)
class MechanicAction:
    action_id: str
    mechanic_id: str
    action_class: ActionClass
    description: str
    preconditions: tuple[str, ...]
    authority_effect: str
    side_effect_semantics: str
    failure_semantics: str

    def __post_init__(self) -> None:
        required = (
            self.action_id,
            self.mechanic_id,
            self.description,
            self.authority_effect,
            self.side_effect_semantics,
            self.failure_semantics,
        )
        if any(not item.strip() for item in required) or not self.preconditions:
            raise ValueError("mechanic action requires identity/description/preconditions/authority/side-effect/failure semantics")


_ACTIONS_BY_PREFIX: tuple[tuple[str, tuple[tuple[str, ActionClass, str], ...]], ...] = (
    ("FRAME.", (("inspect-problem", ActionClass.INSPECT, "Inspect the problem/question/context/resource inputs."), ("bind-task-contract", ActionClass.TRANSFORM, "Bind a typed scoped task contract."), ("decompose", ActionClass.TRANSFORM, "Open/restructure recursive child obligations without creating scientific authority."))),
    ("SEARCH.", (("inspect-frontier", ActionClass.INSPECT, "Inspect open residuals, parent-domain seeds and route coverage."), ("form-query", ActionClass.TRANSFORM, "Construct a typed query proposal under a declared route."), ("retrieve", ActionClass.INFORMATION_ACQUISITION, "Execute evidence/source retrieval through a provider adapter."), ("expand-route", ActionClass.CONTROL, "Open or reformulate a search route."), ("stop-route", ActionClass.CONTROL, "Stop/suspend one route without implying task saturation."))),
    ("ABSORB.", (("interpret-source", ActionClass.TRANSFORM, "Interpret source content into candidate structured projections."), ("resolve-identity-context", ActionClass.TRANSFORM, "Propose identity/context/reference bindings while preserving ambiguity."), ("map-representation", ActionClass.TRANSFORM, "Propose typed representation/equivalence mappings."), ("bind-evidence", ActionClass.TRANSFORM, "Bind contribution candidates to exact evidence/provenance."), ("quarantine-ambiguous", ActionClass.FAIL_CLOSED, "Preserve unresolved/ambiguous material without forced normalization."))),
    ("RECONSTRUCT.", (("update-atlas", ActionClass.TRANSFORM, "Add/update contextual projections and typed relations."), ("test-compatibility", ActionClass.VERIFY, "Test compatibility/contradiction/gluing obligations."), ("construct-portrait", ActionClass.TRANSFORM, "Construct the current plural/global portrait or obstruction."), ("expand-search-universe", ActionClass.TRANSFORM, "Add newly discovered domains/representations/routes to W_t."))),
    ("DETECT.", (("inspect-obligations", ActionClass.INSPECT, "Inspect current claims, residuals, coverage and failure receipts."), ("evaluate-residual-predicate", ActionClass.VERIFY, "Evaluate a typed contradiction/gap/coverage/failure predicate."), ("emit-residual", ActionClass.TRANSFORM, "Create a typed residual with evidence/provenance."))),
    ("DIAGNOSE.", (("retrieve-experience", ActionClass.INFORMATION_ACQUISITION, "Retrieve structurally related prior episodes/negative history."), ("propose-causes", ActionClass.TRANSFORM, "Construct competing cause/responsibility hypotheses."), ("select-discriminator", ActionClass.CONTROL, "Select a computation/observation/experiment that separates hypotheses."), ("update-attribution", ActionClass.TRANSFORM, "Narrow responsibility only from discriminating evidence."))),
    ("REFRAME.", (("construct-reframe", ActionClass.TRANSFORM, "Construct a scoped representation/decomposition/policy/method/objective change proposal."), ("compare-incumbent", ActionClass.VERIFY, "Compare proposal against incumbent obligations and protected invariants."), ("stage-reframe", ActionClass.CONTROL, "Stage a justified reframe; method/authority changes remain proposal-only until promotion."))),
    ("REOPEN.", (("compute-dependent-set", ActionClass.INSPECT, "Compute typed dependents of a changed coordinate."), ("stale-closure", ActionClass.TRANSFORM, "Invalidate only dependent closure/saturation receipts."), ("reopen-fibres", ActionClass.CONTROL, "Reactivate minimal affected research fibres/ancestor challenges."))),
    ("SATURATE.", (("compute-growth", ActionClass.INSPECT, "Compute registered substantive growth coordinates."), ("audit-route-basis", ActionClass.VERIFY, "Audit route/domain/freshness/lineage coverage."), ("challenge-omission", ActionClass.INFORMATION_ACQUISITION, "Run an adversarial false-saturation challenge."), ("issue-stop-status", ActionClass.CONTROL, "Emit OPEN/CANNOT_CHECK/bounded-stop under the frozen basis."))),
    ("CROSS.MEMORY", (("retrieve-working-context", ActionClass.INFORMATION_ACQUISITION, "Retrieve a bounded operation-specific working view from canonical memory."), ("persist-canonical", ActionClass.TRANSFORM, "Persist canonical evidence/experience/artifact state through the storage contract."))),
    ("CROSS.AUTHORITY", (("inspect-certificates", ActionClass.INSPECT, "Inspect scoped authority/evidence certificates."), ("evaluate-promotion", ActionClass.VERIFY, "Evaluate a promotion/non-escalation predicate."), ("promote-or-block", ActionClass.CONTROL, "Promote only through a protected certificate path or fail closed."))),
    ("CROSS.EXPERIENCE", (("record-episode", ActionClass.TRANSFORM, "Persist an immutable execution episode."), ("match-experience", ActionClass.INFORMATION_ACQUISITION, "Retrieve structurally related episodes."), ("propose-lesson", ActionClass.TRANSFORM, "Propose a failure/success-derived lesson without self-promotion."))),
    ("CROSS.REVIEW", (("construct-review-packet", ActionClass.TRANSFORM, "Freeze review inputs/claims/evidence boundaries."), ("execute-review", ActionClass.VERIFY, "Run an adversarial/independent review process."), ("record-review-residuals", ActionClass.TRANSFORM, "Preserve review findings, disagreements and CANNOT_CHECK outcomes."))),
    ("CROSS.BENCHMARK", (("freeze-instrument", ActionClass.CONTROL, "Freeze benchmark/instrument/evaluator identity before outcome access."), ("execute-instrument", ActionClass.VERIFY, "Run the benchmark/instrument under declared conditions."), ("interpret-measurement", ActionClass.TRANSFORM, "Interpret observed scores only under the construct/measurement model."))),
    ("CROSS.EXPERIMENT_SELECTION", (("enumerate-actions", ActionClass.INSPECT, "Enumerate admissible information-acquisition actions."), ("score-separation", ActionClass.TRANSFORM, "Compute set-valued or calibrated discriminating value/cost."), ("select-action", ActionClass.CONTROL, "Select an action under hard invariants and resource constraints."))),
    ("CROSS.EXECUTION", (("bind-execution", ActionClass.CONTROL, "Bind task/provider/tool/environment identities."), ("execute-effect", ActionClass.EXTERNAL_EFFECT, "Execute a declared external/model/tool action with side-effect guards."), ("write-receipt", ActionClass.TRANSFORM, "Persist identity-bound execution/event receipts."))),
    ("CROSS.CONTEXT_POLICY", (("identify-mandatory-context", ActionClass.INSPECT, "Identify mandatory epistemic material for the operation."), ("select-context", ActionClass.CONTROL, "Select the bounded working context under preserved mandatory material."))),
)

_TOP_LEVEL_PREFIX: dict[str, str] = {
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


def candidate_action_plan(cell: MechanicCell) -> tuple[MechanicAction, ...]:
    lookup_id = _TOP_LEVEL_PREFIX.get(cell.mechanic_id, cell.mechanic_id)
    specs: tuple[tuple[str, ActionClass, str], ...] | None = None
    for prefix, candidate_specs in _ACTIONS_BY_PREFIX:
        if lookup_id.startswith(prefix):
            specs = candidate_specs
            break
    if specs is None:
        specs = (("inspect", ActionClass.INSPECT, "Inspect declared inputs/state/obligations."), ("transform", ActionClass.TRANSFORM, "Perform the typed local transformation under declared invariants."), ("fail-closed", ActionClass.FAIL_CLOSED, "Emit a typed non-success terminal when prerequisites/verification fail."))
    return tuple(
        MechanicAction(
            action_id=f"action:{cell.mechanic_id}:{suffix}",
            mechanic_id=cell.mechanic_id,
            action_class=action_class,
            description=description,
            preconditions=("declared lifecycle preconditions hold", "blocking authority/resource/dependency invariants hold"),
            authority_effect="No action directly mints scientific authority; certificate-producing verification/promotion is separate.",
            side_effect_semantics="External effects are allowed only through declared adapters/receipts; otherwise the action is local state/proposal work.",
            failure_semantics="Action failure emits a typed failure/residual and does not silently continue as success.",
        )
        for suffix, action_class, description in specs
    )


def apply_candidate_action_plan(cell: MechanicCell) -> MechanicCell:
    actions = candidate_action_plan(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific admissible action/effect set, action granularity, side-effect boundaries, costs and hostile invalid-action cases",)))
    return replace(cell, action_ids=tuple(item.action_id for item in actions), empirical_open_coordinates=empirical_open)


def apply_candidate_action_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_candidate_action_plan(cell) for cell in cells)
