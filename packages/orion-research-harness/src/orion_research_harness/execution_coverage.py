from __future__ import annotations

import importlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from orion.engine.trace import MECHANIC_ID_BY_OPERATOR


class ExecutionMode(str, Enum):
    DIRECT_RUNTIME = "DIRECT_RUNTIME"
    DISTRIBUTED_RUNTIME = "DISTRIBUTED_RUNTIME"
    RECURSIVE_RUNTIME = "RECURSIVE_RUNTIME"
    HARNESS_GOVERNANCE = "HARNESS_GOVERNANCE"
    DEVELOPMENT_GATED = "DEVELOPMENT_GATED"
    EXTERNAL_GATED = "EXTERNAL_GATED"
    SPECIFICATION_ONLY = "SPECIFICATION_ONLY"


@dataclass(frozen=True)
class OwnerSpec:
    module: str
    attribute: str | None
    mode: ExecutionMode
    note: str

    @property
    def owner_ref(self) -> str:
        return self.module if self.attribute is None else f"{self.module}:{self.attribute}"


_DIRECT: dict[str, OwnerSpec] = {
    "ORION_SOLVE.v1": OwnerSpec("orion.engine.solver", "OrionSolver", ExecutionMode.DIRECT_RUNTIME, "guarded root solve and immutable mechanic receipts"),
    "FRAME.v1": OwnerSpec("orion.engine.operators.frame", "FrameOperator", ExecutionMode.DIRECT_RUNTIME, "runtime frame operator"),
    "SEARCH.v1": OwnerSpec("orion.engine.operators.search", "SearchOperator", ExecutionMode.DIRECT_RUNTIME, "runtime search operator"),
    "ABSORB.v1": OwnerSpec("orion.engine.operators.absorb", "AbsorbOperator", ExecutionMode.DIRECT_RUNTIME, "runtime absorb operator"),
    "RECONSTRUCT.v1": OwnerSpec("orion.engine.operators.reconstruct", "ReconstructOperator", ExecutionMode.DIRECT_RUNTIME, "runtime reconstruction operator"),
    "DETECT.v1": OwnerSpec("orion.engine.operators.detect", "DetectOperator", ExecutionMode.DIRECT_RUNTIME, "runtime residual detector"),
    "DIAGNOSE.v1": OwnerSpec("orion.engine.operators.diagnose", "DiagnoseOperator", ExecutionMode.DIRECT_RUNTIME, "runtime diagnosis operator"),
    "REFRAME.v1": OwnerSpec("orion.engine.operators.reframe", "ReframeOperator", ExecutionMode.DIRECT_RUNTIME, "runtime safe local reframe operator"),
    "REOPEN.v1": OwnerSpec("orion.engine.operators.reopen", "ReopenOperator", ExecutionMode.DIRECT_RUNTIME, "runtime dependency/closure invalidation operator"),
    "SATURATE_BOUNDED.v3": OwnerSpec("orion.engine.operators.saturate", "SaturateOperator", ExecutionMode.DIRECT_RUNTIME, "bounded non-absolute saturation operator"),
}

_EXACT: dict[str, OwnerSpec] = {
    "FRAME.AUTHORITY_TARGET.v0": OwnerSpec("orion_research_harness.runner", "run_problem", ExecutionMode.HARNESS_GOVERNANCE, "verified/provisional authority target is bound by the harness solve contract"),
    "FRAME.RESOURCES.v0": OwnerSpec("orion_research_harness.recursive_runner", "RecursiveRunLimits", ExecutionMode.HARNESS_GOVERNANCE, "iteration/depth/node/branch resources are explicit fail-closed solve inputs"),
    "FRAME.DECOMPOSE.v0": OwnerSpec("orion.engine.residual_recursion", "ProblemRecursionPlanner", ExecutionMode.RECURSIVE_RUNTIME, "root problems are recursively atomized before expensive work"),
    "SEARCH.ROUTE_STOP.v0": OwnerSpec("orion.engine.operators.saturate", "SaturateOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "route stopping is bounded by route-coverage and saturation semantics, not task-completeness authority"),
    "DIAGNOSE.HYPOTHESES.v0": OwnerSpec("orion.providers.reasoner.recursive_llm", "RecursiveLLMResearchReasoner", ExecutionMode.RECURSIVE_RUNTIME, "recursive decomposition proposes competing decision-separating child hypotheses"),
    "DIAGNOSE.EXPERIENCE_RETRIEVAL.v0": OwnerSpec("orion_research_harness.recursive_runner", "run_problem_recursive", ExecutionMode.RECURSIVE_RUNTIME, "recursive residual control reopens DevelopmentFibre/experience context before decomposition"),
    "DIAGNOSE.DISCRIMINATOR.v0": OwnerSpec("orion.engine.residual_recursion", "ResidualRecursionPlanner", ExecutionMode.RECURSIVE_RUNTIME, "each atomic child carries exactly one bounded discriminator and is solver-ordered"),
    "DIAGNOSE.ATTRIBUTION.v0": OwnerSpec("orion_research_harness.recursive_runner", "run_problem_recursive", ExecutionMode.RECURSIVE_RUNTIME, "parent refresh attributes discriminator outcomes without assuming residual-id stability"),
    "REFRAME.DECOMPOSITION.v0": OwnerSpec("orion.engine.residual_recursion", "ResidualRecursionPlanner", ExecutionMode.RECURSIVE_RUNTIME, "fresh evidence rebuilds the residual atom tree rather than running stale siblings"),
    "REFRAME.SEARCH_POLICY.v0": OwnerSpec("orion.engine.residual_recursion", "ProblemRecursionPlanner", ExecutionMode.RECURSIVE_RUNTIME, "child problems may change route/domain focus under unchanged parent acceptance criteria"),
    "REFRAME.METHOD.v0": OwnerSpec("orion.self_orion.research_loop", "ShadowSelfOrionResearchLoop", ExecutionMode.DEVELOPMENT_GATED, "method changes are correctly blocked from ordinary reframe and routed through protected Shadow Self-ORION development"),
    "REFRAME.OBJECTIVE.v0": OwnerSpec("orion.self_orion.research_loop", "ShadowSelfOrionResearchLoop", ExecutionMode.DEVELOPMENT_GATED, "scientific objective/QoI evolution is a high-impact development proposal, not an automatic child-problem rewrite"),
    "REOPEN.FIBRE.v0": OwnerSpec("orion_research_harness.recursive_runner", "run_problem_recursive", ExecutionMode.RECURSIVE_RUNTIME, "minimal affected DevelopmentFibres are compiled and rebound to residual investigation"),
    "CROSS.MEMORY.v0": OwnerSpec("orion_research_harness.workspace", "ResearchWorkspace", ExecutionMode.HARNESS_GOVERNANCE, "canonical problems, requests, results, runs and campaign receipts are replayable workspace state"),
    "CROSS.AUTHORITY.v0": OwnerSpec("orion.experience.authority", None, ExecutionMode.HARNESS_GOVERNANCE, "authority is certificate/gate governed and cannot be minted by ordinary mechanics"),
    "CROSS.EXPERIENCE.v0": OwnerSpec("orion.experience.recording", "episode_from_receipt", ExecutionMode.DISTRIBUTED_RUNTIME, "mechanic/root receipts become immutable experience episodes"),
    "CROSS.REVIEW.v0": OwnerSpec("orion_research_harness.governance_runtime", "request_independent_review", ExecutionMode.EXTERNAL_GATED, "independent/adversarial review is a replayable host capability and preserves FAIL/CANNOT_CHECK"),
    "CROSS.BENCHMARK.v0": OwnerSpec("orion_research_harness.governance_runtime", "request_benchmark", ExecutionMode.EXTERNAL_GATED, "benchmark subject/evaluator/acceptance identities are request-digest frozen before result ingestion"),
    "CROSS.EXPERIMENT_SELECTION.v0": OwnerSpec("orion.transfer.v2.epistemic_computation", "select_epistemic_computation", ExecutionMode.DISTRIBUTED_RUNTIME, "campaign and recursive control select discriminating work under cost/hard requirements"),
    "CROSS.EXECUTION.v0": OwnerSpec("orion_research_harness.broker", "CapabilityBroker", ExecutionMode.HARNESS_GOVERNANCE, "external effects are request/result receipted and fail closed"),
    "CROSS.CONTEXT_POLICY.v0": OwnerSpec("orion_research_harness.governance_runtime", "select_context", ExecutionMode.HARNESS_GOVERNANCE, "mandatory context is preserved before optional context is admitted under budget"),
}

_PREFIX: tuple[tuple[str, OwnerSpec], ...] = (
    ("FRAME.", OwnerSpec("orion.engine.operators.frame", "FrameOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented through the typed frame/problem contract")),
    ("SEARCH.", OwnerSpec("orion.engine.operators.search", "SearchOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented through search planning/retrieval/route receipts")),
    ("ABSORB.", OwnerSpec("orion.engine.operators.absorb", "AbsorbOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented through interpretation, evidence binding and typed contribution absorption")),
    ("RECONSTRUCT.", OwnerSpec("orion.engine.operators.reconstruct", "ReconstructOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented through portrait/atlas/search-universe reconstruction")),
    ("DETECT.", OwnerSpec("orion.engine.operators.detect", "DetectOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented through typed residual detection")),
    ("DIAGNOSE.", OwnerSpec("orion.engine.operators.diagnose", "DiagnoseOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented through diagnosis plus recursive-control extensions")),
    ("REFRAME.", OwnerSpec("orion.engine.operators.reframe", "ReframeOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented locally when safe; high-impact method/objective changes stay development-gated")),
    ("REOPEN.", OwnerSpec("orion.engine.operators.reopen", "ReopenOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented through dependency-directed closure invalidation plus recursive fibre reopening")),
    ("SATURATE.", OwnerSpec("orion.engine.operators.saturate", "SaturateOperator", ExecutionMode.DISTRIBUTED_RUNTIME, "implemented by non-compensatory bounded flatness/coverage/omission/stop assessment")),
)

_AUTOMATIC_REQUIRED = {
    "FRAME.DECOMPOSE.v0",
    "DIAGNOSE.HYPOTHESES.v0",
    "DIAGNOSE.EXPERIENCE_RETRIEVAL.v0",
    "DIAGNOSE.DISCRIMINATOR.v0",
    "DIAGNOSE.ATTRIBUTION.v0",
    "REFRAME.DECOMPOSITION.v0",
    "REOPEN.FIBRE.v0",
    "SATURATE.KNOWLEDGE_FLATNESS.v0",
    "SATURATE.FORMULATION_FLATNESS.v0",
    "SATURATE.ROUTE_COVERAGE.v0",
    "SATURATE.OMISSION_CHALLENGE.v0",
    "SATURATE.STOP.v0",
}

_AUTOMATIC_MODES = {
    ExecutionMode.DIRECT_RUNTIME,
    ExecutionMode.DISTRIBUTED_RUNTIME,
    ExecutionMode.RECURSIVE_RUNTIME,
    ExecutionMode.HARNESS_GOVERNANCE,
}


def _owner_for(mechanic_id: str) -> OwnerSpec:
    if mechanic_id in _DIRECT:
        return _DIRECT[mechanic_id]
    if mechanic_id in _EXACT:
        return _EXACT[mechanic_id]
    for prefix, owner in _PREFIX:
        if mechanic_id.startswith(prefix):
            return owner
    return OwnerSpec(
        "orion.mechanics.decomposition",
        None,
        ExecutionMode.SPECIFICATION_ONLY,
        "no executable owner registered",
    )


def _owner_resolves(owner: OwnerSpec) -> tuple[bool, str]:
    try:
        module = importlib.import_module(owner.module)
        if owner.attribute is not None:
            getattr(module, owner.attribute)
    except Exception as exc:  # noqa: BLE001 - coverage must surface all owner failures
        return False, f"{type(exc).__name__}: {exc}"
    return True, ""


def execution_coverage(cells: Iterable[Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    ids: set[str] = set()
    for cell in cells:
        mechanic_id = str(cell.mechanic_id)
        ids.add(mechanic_id)
        owner = _owner_for(mechanic_id)
        resolves, error = _owner_resolves(owner)
        rows.append(
            {
                "mechanic_id": mechanic_id,
                "execution_mode": owner.mode.value,
                "owner_ref": owner.owner_ref,
                "owner_resolves": resolves,
                "owner_error": error,
                "note": owner.note,
                "automatic_required": mechanic_id in _AUTOMATIC_REQUIRED,
                "automatic_ready": (
                    mechanic_id not in _AUTOMATIC_REQUIRED
                    or (resolves and owner.mode in _AUTOMATIC_MODES)
                ),
            }
        )

    runtime_ids = set(MECHANIC_ID_BY_OPERATOR.values())
    specification_only = sorted(
        row["mechanic_id"]
        for row in rows
        if row["execution_mode"] == ExecutionMode.SPECIFICATION_ONLY.value
    )
    owner_failures = sorted(
        row["mechanic_id"] for row in rows if row["owner_resolves"] is not True
    )
    automatic_missing = sorted(_AUTOMATIC_REQUIRED - ids)
    automatic_not_ready = sorted(
        row["mechanic_id"]
        for row in rows
        if row["automatic_required"] and row["automatic_ready"] is not True
    )
    direct_missing = sorted(runtime_ids - ids)
    mode_counts: dict[str, int] = {}
    for row in rows:
        mode_counts[row["execution_mode"]] = mode_counts.get(row["execution_mode"], 0) + 1

    ready = (
        not specification_only
        and not owner_failures
        and not automatic_missing
        and not automatic_not_ready
        and not direct_missing
    )
    return {
        "schema": "ORION.ResearchHarnessExecutionCoverage.v1",
        "authority": "EXECUTABLE_OWNER_COVERAGE_ONLY__NO_SCIENTIFIC_AUTHORITY",
        "mechanic_count": len(rows),
        "mode_counts": dict(sorted(mode_counts.items())),
        "specification_only_ids": specification_only,
        "owner_resolution_failures": owner_failures,
        "automatic_required_ids": sorted(_AUTOMATIC_REQUIRED),
        "automatic_missing_ids": automatic_missing,
        "automatic_not_ready_ids": automatic_not_ready,
        "direct_runtime_missing_ids": direct_missing,
        "rows": sorted(rows, key=lambda row: row["mechanic_id"]),
        "executable_owner_coverage_ready": ready,
        "note": (
            "DIRECT/DISTRIBUTED/RECURSIVE/HARNESS owners are executable paths; DEVELOPMENT_GATED and EXTERNAL_GATED are intentionally protected boundaries. "
            "SPECIFICATION_ONLY is never release-ready."
        ),
    }


__all__ = ["ExecutionMode", "execution_coverage"]
