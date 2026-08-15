"""Mechanics-of-mechanics primitives for recursively auditing ORION steps."""

from .audit import MechanicAuditReport, RecursiveMechanicAudit, audit_mechanic, audit_recursive
from .decomposition import RAKL_SURFACE_TO_CHILDREN, expanded_mechanical_backlog, expanded_workflow_cells
from .failure import FailureDetectionKind, FailureModeDefinition, MechanicFailurePlan, apply_default_failure_plan, apply_default_failure_plans, default_failure_plan
from .handoff import AuthorityTransport, FieldPresence, HandoffRequirement, MechanicHandoffPlan, apply_default_handoff_plan, apply_default_handoff_plans, default_handoff_plan
from .model import DimensionWaiver, HandoffField, MechanicCell, MechanicDimension, MetricDirection, MetricKind, MetricObservation, MetricSpec
from .observability import MechanicObservationPlan, ObservationClass, ObservationSpec, apply_default_observation_plan, apply_default_observation_plans, default_observation_plan
from .program import MechanicsProgramMetrics, current_program_cells, observe_current_mechanics_program, observe_mechanics_program, plan_current_program_questions, plan_current_program_research, plan_program_questions, plan_program_research
from .questioning import MechanicQuestion, generate_mechanic_questions, plan_next_questions
from .receipt import MechanicReceipt, MechanicRunStatus
from .research import MechanicResearchTask, plan_mechanic_research, research_task_for_question
from .state_plan import MechanicStatePlan, StateMutability, StatePersistence, StateRole, StateVariableSpec, apply_default_state_plan, apply_default_state_plans, default_state_plan
from .verification import MechanicVerificationPlan, VerificationMethod, VerificationObligation, VerificationStage, apply_default_verification_plan, apply_default_verification_plans, default_verification_plan
from .workflow import ORION_WORKFLOW_CELLS, ORION_WORKFLOW_ROOT_ID, mechanical_workflow_backlog

__all__ = [name for name in globals() if not name.startswith("_")]
