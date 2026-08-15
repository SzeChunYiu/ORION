from __future__ import annotations

from .audit import audit_recursive
from .model import MechanicCell
from .questioning import MechanicQuestion

ORION_WORKFLOW_ROOT_ID = "ORION_SOLVE.v1"

_OPERATOR_IDS = (
    "FRAME.v1",
    "SEARCH.v1",
    "ABSORB.v1",
    "RECONSTRUCT.v1",
    "DETECT.v1",
    "DIAGNOSE.v1",
    "REFRAME.v1",
    "REOPEN.v1",
    "SATURATE_BOUNDED.v3",
)


def _operator(mechanic_id: str, purpose: str, *, dependencies: tuple[str, ...]) -> MechanicCell:
    """Seed known architecture while leaving unresolved mechanic dimensions visible."""

    return MechanicCell(
        mechanic_id=mechanic_id,
        purpose=purpose,
        scope="one scoped ORION research iteration",
        input_ids=("Problem", "OrionState"),
        output_ids=("OrionStateDelta", "MechanicReceipt"),
        dependency_ids=dependencies,
        authority_boundaries=("proposal-only unless a protected verification/promotion path explicitly grants authority",),
        reopen_triggers=("new native residual", "dependency contract changes", "fresh hostile failure"),
        empirical_open_coordinates=("live-provider quality", "fresh-task transfer", "cost/performance envelope"),
    )


ORION_WORKFLOW_CELLS: tuple[MechanicCell, ...] = (
    MechanicCell(
        mechanic_id=ORION_WORKFLOW_ROOT_ID,
        purpose="Solve a scoped problem by recursive epistemic reconstruction.",
        scope="one root research problem",
        input_ids=("Problem",),
        output_ids=("Solution", "OrionState", "SolveTrace"),
        child_mechanic_ids=_OPERATOR_IDS,
        authority_boundaries=("the workflow cannot promote scientific authority outside protected verification",),
        reopen_triggers=("any child mechanic reopens", "new root-relevant residual", "evaluation epoch changes"),
        empirical_open_coordinates=("general autonomous-research capability",),
    ),
    _operator("FRAME.v1", "Construct the active object, question, context, resources and blocking invariants.", dependencies=()),
    _operator("SEARCH.v1", "Expand computational access through heterogeneous knowledge/source/search routes.", dependencies=("FRAME.v1",)),
    _operator("ABSORB.v1", "Interpret retrieved material as contextual projections and typed knowledge contributions.", dependencies=("SEARCH.v1",)),
    _operator("RECONSTRUCT.v1", "Update the global portrait and search-universe model from absorbed contributions.", dependencies=("ABSORB.v1",)),
    _operator("DETECT.v1", "Detect typed object-level and method-level residuals.", dependencies=("RECONSTRUCT.v1",)),
    _operator("DIAGNOSE.v1", "Separate competing responsibility hypotheses before repair.", dependencies=("DETECT.v1",)),
    _operator("REFRAME.v1", "Apply the smallest justified typed change to the responsible layer.", dependencies=("DIAGNOSE.v1",)),
    _operator("REOPEN.v1", "Stale dependent closure while preserving unaffected knowledge and negative history.", dependencies=("REFRAME.v1",)),
    _operator("SATURATE_BOUNDED.v3", "Decide whether repeated heterogeneous challenges are flat enough to stop at a declared cutoff.", dependencies=("REOPEN.v1",)),
)


def mechanical_workflow_backlog() -> tuple[MechanicQuestion, ...]:
    cells = {cell.mechanic_id: cell for cell in ORION_WORKFLOW_CELLS}
    audit = audit_recursive(cells, ORION_WORKFLOW_ROOT_ID)
    return tuple(question for report in audit.reports for question in report.open_questions)
