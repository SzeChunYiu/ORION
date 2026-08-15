from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell
from .receipt import MechanicRunStatus


class FailureDetectionKind(str, Enum):
    EXPECTATION_VIOLATION = "EXPECTATION_VIOLATION"
    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    INTERFACE_VIOLATION = "INTERFACE_VIOLATION"
    VERIFICATION_UNAVAILABLE = "VERIFICATION_UNAVAILABLE"
    RESOURCE_BOUND = "RESOURCE_BOUND"
    ROOT_PROGRESS_VIOLATION = "ROOT_PROGRESS_VIOLATION"


@dataclass(frozen=True)
class FailureModeDefinition:
    """One declared way a mechanic can fail or become non-actionable.

    The mode/effect/cause/detection/recovery fields are deliberately separated so
    recurrence of an observed mode cannot silently become a causal explanation.
    """

    mode_id: str
    mechanic_id: str
    outcome: MechanicRunStatus
    local_mode: str
    propagated_effects: tuple[str, ...]
    cause_hypotheses: tuple[str, ...]
    detection_kind: FailureDetectionKind
    detection_signals: tuple[str, ...]
    detection_rule: str
    recovery_actions: tuple[str, ...]
    falsifier: str
    acceptance_rationale: str

    def __post_init__(self) -> None:
        text = (
            self.mode_id,
            self.mechanic_id,
            self.local_mode,
            self.detection_rule,
            self.falsifier,
            self.acceptance_rationale,
        )
        if any(not item.strip() for item in text):
            raise ValueError("failure-mode identity, semantics, detection, falsifier and rationale are required")
        required_groups = (
            self.propagated_effects,
            self.cause_hypotheses,
            self.detection_signals,
            self.recovery_actions,
        )
        if any(not group for group in required_groups):
            raise ValueError("failure modes require effects, cause hypotheses, detection signals and recovery actions")


@dataclass(frozen=True)
class MechanicFailurePlan:
    mechanic_id: str
    modes: tuple[FailureModeDefinition, ...]
    step_specific_analysis_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.modes:
            raise ValueError("mechanic failure plan requires identity and modes")
        if any(item.mechanic_id != self.mechanic_id for item in self.modes):
            raise ValueError("failure mode mechanic mismatch")
        ids = [item.mode_id for item in self.modes]
        if len(set(ids)) != len(ids):
            raise ValueError("failure mode ids must be unique")


def _mode(
    cell: MechanicCell,
    suffix: str,
    outcome: MechanicRunStatus,
    local_mode: str,
    effects: tuple[str, ...],
    causes: tuple[str, ...],
    detection_kind: FailureDetectionKind,
    signals: tuple[str, ...],
    detection_rule: str,
    recovery: tuple[str, ...],
    falsifier: str,
    rationale: str,
) -> FailureModeDefinition:
    return FailureModeDefinition(
        mode_id=f"failure:{cell.mechanic_id}:{suffix}",
        mechanic_id=cell.mechanic_id,
        outcome=outcome,
        local_mode=local_mode,
        propagated_effects=effects,
        cause_hypotheses=causes,
        detection_kind=detection_kind,
        detection_signals=signals,
        detection_rule=detection_rule,
        recovery_actions=recovery,
        falsifier=falsifier,
        acceptance_rationale=rationale,
    )


def default_failure_plan(cell: MechanicCell) -> MechanicFailurePlan:
    """Universal fail-closed baseline, not a complete step-specific FMEA.

    The plan supplies a common vocabulary for failure observations before each
    mechanic's domain-specific failure modes have been researched and tested.
    """

    return MechanicFailurePlan(
        mechanic_id=cell.mechanic_id,
        modes=(
            _mode(
                cell,
                "contract-violation",
                MechanicRunStatus.FAILED,
                "The mechanic violates a declared invariant, postcondition or interface contract.",
                ("downstream output is unsafe to treat as contract-conformant",),
                ("implementation defect", "invalid assumption", "incorrect input/state binding"),
                FailureDetectionKind.INVARIANT_VIOLATION,
                ("invariant checks", "postcondition checks", "interface checks"),
                "A declared invariant, postcondition or interface predicate evaluates false.",
                ("quarantine the output", "localize the violated contract", "route to diagnosis before retry"),
                "A hostile/known-answer case exercises the registered contract without the predicted violation.",
                "A declared contract violation must fail closed rather than be averaged into a quality score.",
            ),
            _mode(
                cell,
                "blocked-prerequisite",
                MechanicRunStatus.BLOCKED,
                "A mandatory prerequisite, dependency, evidence item or authority certificate is unavailable.",
                ("the mechanic cannot safely execute its intended transition",),
                ("upstream dependency failure", "missing evidence", "unmet precondition"),
                FailureDetectionKind.INTERFACE_VIOLATION,
                ("prerequisite availability", "dependency status", "required evidence/certificate presence"),
                "At least one declared mandatory prerequisite is absent or invalid.",
                ("open/acquire the missing prerequisite", "repair the upstream dependency", "return BLOCKED"),
                "The mechanic executes successfully after every declared mandatory prerequisite is supplied under the same scope.",
                "Blocked is distinct from scientific refutation and from an implementation failure.",
            ),
            _mode(
                cell,
                "cannot-check",
                MechanicRunStatus.CANNOT_CHECK,
                "The mechanic cannot establish a required observation or verification condition.",
                ("the target conclusion remains unresolved at this mechanic",),
                ("missing instrument", "missing verifier", "unavailable measurement", "unresolved identification"),
                FailureDetectionKind.VERIFICATION_UNAVAILABLE,
                ("verification artifact availability", "measurement availability", "identifiability status"),
                "A required verification/measurement obligation is unrun, unavailable or not identifiable.",
                ("acquire the missing verification capability", "narrow the claim", "return CANNOT_CHECK"),
                "The required observation/verifier becomes available and resolves the obligation without changing the claimed scope.",
                "Unchecked is not evidence of success or failure; it remains epistemically open.",
            ),
            _mode(
                cell,
                "resource-bound-open",
                MechanicRunStatus.CANNOT_CHECK,
                "The declared resource budget is exhausted while material obligations remain open.",
                ("local work stops without licensing task or mechanic closure",),
                ("insufficient compute/time/token/tool budget", "poor allocation policy", "unexpected task complexity"),
                FailureDetectionKind.RESOURCE_BOUND,
                ("remaining budget", "open obligation count", "marginal progress"),
                "Budget reaches its declared floor while at least one material obligation remains open.",
                ("return CANNOT_CHECK", "record unfinished obligations", "request/justify additional resources or reallocate"),
                "A matched-resource rerun closes the obligations without changing the task or acceptance criteria.",
                "Resource exhaustion must never be rounded up to bounded saturation or scientific closure.",
            ),
            _mode(
                cell,
                "false-progress",
                MechanicRunStatus.PARTIAL,
                "A local metric improves while root-relevant, authority, interface or falsifier obligations remain unchanged or worsen.",
                ("the system may report progress that does not advance the root problem",),
                ("surrogate misalignment", "metric gaming", "interface mismatch", "hidden residual"),
                FailureDetectionKind.ROOT_PROGRESS_VIOLATION,
                ("local metric delta", "root-obligation delta", "interface invariants", "blocking residual count"),
                "Local improvement is observed without a licensed improvement in the registered root-relevant coordinate, or a blocking invariant regresses.",
                ("do not promote the local result", "diagnose surrogate/root mismatch", "reframe metric or interface if supported"),
                "The same local change reliably improves the registered root-relevant coordinate under preserved blocking invariants on fresh cases.",
                "Local improvement is evidence only for the local coordinate unless root transport is independently witnessed.",
            ),
            _mode(
                cell,
                "silent-degradation",
                MechanicRunStatus.FAILED,
                "The mechanic returns an apparently admissible result while a protected expectation is violated but not surfaced by ordinary success reporting.",
                ("invalid output can propagate as if successful",),
                ("missing monitor", "coverage gap", "latent data corruption", "unmodeled regime change"),
                FailureDetectionKind.EXPECTATION_VIOLATION,
                ("independent expectation checks", "cross-route consistency", "hostile canaries", "fresh assurance"),
                "An independent expectation, canary or protected evaluator rejects an otherwise nominally successful result.",
                ("quarantine the result", "open diagnosis and monitoring gap", "add a regression canary only after cause localization"),
                "Hostile/fresh tests fail to reproduce the degradation under the hypothesized cause boundary.",
                "Silent failure requires independent detection because self-reported success is not sufficient evidence.",
            ),
        ),
        step_specific_analysis_open=True,
    )


def apply_default_failure_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_failure_plan(cell)
    empirical_open = cell.empirical_open_coordinates
    if plan.step_specific_analysis_open:
        empirical_open = tuple(
            dict.fromkeys(
                empirical_open
                + ("step-specific failure-mode/effect/cause/detectability analysis and hostile validation",)
            )
        )
    return replace(
        cell,
        failure_signatures=tuple(item.mode_id for item in plan.modes),
        falsifiers=tuple(item.falsifier for item in plan.modes),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_failure_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_failure_plan(cell) for cell in cells)
