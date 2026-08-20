from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4

from orion import Problem
from orion.engine.solver import SolverConfig
from orion.providers.experience import InMemoryExperienceStore
from orion.runtime import OrionRuntime

from .broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    BrokerVerificationProvider,
    CapabilityBroker,
    HostCapabilityRequired,
)
from .protocol import utc_now
from .workspace import ResearchWorkspace


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def run_problem(
    workspace: ResearchWorkspace,
    problem_data: Mapping[str, Any],
    *,
    max_iterations: int = 3,
    require_verified_answer: bool = True,
) -> dict[str, Any]:
    broker = CapabilityBroker(workspace)
    experiences = InMemoryExperienceStore()
    runtime = OrionRuntime.from_providers(
        llm=BrokerLLMProvider(broker),
        retrieval=BrokerRetrievalProvider(broker),
        verification=BrokerVerificationProvider(broker),
        experience_store=experiences,
        config=SolverConfig(
            max_iterations=int(max_iterations),
            require_verified_answer=bool(require_verified_answer),
        ),
        producer_process_lineage_hash="orion-research-harness-v1",
        evaluator_artifact_hash="external-host-capability-receipts-v1",
    )
    problem = Problem(
        problem_id=str(problem_data["problem_id"]),
        question=str(problem_data["question"]),
        scope=str(problem_data.get("scope", "")),
        initial_domain_ids=tuple(str(x) for x in problem_data.get("initial_domain_ids", ())),
        success_criteria=tuple(str(x) for x in problem_data.get("success_criteria", ())),
    )
    try:
        result = runtime.solve(
            problem,
            evaluation_epoch_id=f"harness:{workspace.session_id}",
            split_id="interactive-research",
        )
    except HostCapabilityRequired as pending:
        return {
            "schema": "ORION.HarnessSolveOutcome.v1",
            "status": "PENDING_CAPABILITY",
            "problem_id": problem.problem_id,
            "request": pending.request.as_dict(),
        }

    run_id = "run:" + uuid4().hex
    record = {
        "schema": "ORION.HarnessRun.v1",
        "run_id": run_id,
        "session_id": workspace.session_id,
        "created_at": utc_now(),
        "problem": _jsonable(problem),
        "solution": _jsonable(result.solution),
        "final_state": _jsonable(result.final_state),
        "trace": _jsonable(result.trace),
        "experience_episode_id": result.experience_episode_id,
        "mechanic_experience_episode_ids": list(result.mechanic_experience_episode_ids),
        "experience_episodes": [_jsonable(item) for item in experiences.episodes()],
    }
    workspace.save_run(run_id, record)
    return {
        "schema": "ORION.HarnessSolveOutcome.v1",
        "status": "COMPLETE",
        "problem_id": problem.problem_id,
        "run_id": run_id,
        "solution_status": result.solution.status.value,
        "answer": result.solution.answer,
        "evidence_ids": list(result.solution.evidence_ids),
        "residual_ids": list(result.solution.residual_ids),
        "trace_id": result.trace.trace_id,
        "operator_sequence": [item.value for item in result.trace.operator_sequence],
    }
