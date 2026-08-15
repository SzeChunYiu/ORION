"""Mechanics-of-mechanics primitives for recursively auditing ORION steps."""

from .audit import MechanicAuditReport, RecursiveMechanicAudit, audit_mechanic, audit_recursive
from .decomposition import RAKL_SURFACE_TO_CHILDREN, expanded_mechanical_backlog, expanded_workflow_cells
from .model import (
    DimensionWaiver,
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricObservation,
    MetricSpec,
)
from .program import MechanicsProgramMetrics, observe_mechanics_program, plan_program_questions, plan_program_research
from .questioning import MechanicQuestion, generate_mechanic_questions, plan_next_questions
from .receipt import MechanicReceipt, MechanicRunStatus
from .research import MechanicResearchTask, plan_mechanic_research, research_task_for_question
from .workflow import ORION_WORKFLOW_CELLS, ORION_WORKFLOW_ROOT_ID, mechanical_workflow_backlog

__all__ = [
    "DimensionWaiver",
    "HandoffField",
    "MechanicAuditReport",
    "MechanicCell",
    "MechanicDimension",
    "MechanicQuestion",
    "MechanicReceipt",
    "MechanicResearchTask",
    "MechanicRunStatus",
    "MechanicsProgramMetrics",
    "MetricDirection",
    "MetricKind",
    "MetricObservation",
    "MetricSpec",
    "ORION_WORKFLOW_CELLS",
    "ORION_WORKFLOW_ROOT_ID",
    "RAKL_SURFACE_TO_CHILDREN",
    "RecursiveMechanicAudit",
    "audit_mechanic",
    "audit_recursive",
    "expanded_mechanical_backlog",
    "expanded_workflow_cells",
    "generate_mechanic_questions",
    "mechanical_workflow_backlog",
    "observe_mechanics_program",
    "plan_mechanic_research",
    "plan_next_questions",
    "plan_program_questions",
    "plan_program_research",
    "research_task_for_question",
]
