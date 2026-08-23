from __future__ import annotations

import dataclasses
import hashlib
from enum import Enum
from collections.abc import Iterable
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
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .operator_coverage import require_operators_exercised, run_operator_coverage
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


def _sha256_label(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def run_problem(
    workspace: ResearchWorkspace,
    problem_data: Mapping[str, Any],
    *,
    max_iterations: int = 3,
    require_verified_answer: bool = True,
    require_operators: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Run canonical ORION once and return a receipted outcome.

    ``require_operators`` names cycle operators this caller's experiment depends
    on --- ``{"DIAGNOSE"}`` for an arm whose whole purpose is to diagnose. When a
    completed run did not reach one, this raises ``OperatorNotExercised`` naming
    it, instead of returning an outcome that will be scored as a weak result. The
    P1-U R6 campaign scored 48 rows from runs that never reached ``DIAGNOSE``;
    this parameter is the one line that would have stopped it at episode one. It
    is checked only on ``COMPLETE`` outcomes: a pending or failed host capability
    means no run happened, which is a different condition and says so itself.
    """

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
        producer_process_lineage_hash=_sha256_label("orion-research-harness-v1"),
        evaluator_artifact_hash=_sha256_label("external-host-capability-receipts-v1"),
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
    except HostCapabilityFailed as failed:
        return {
            "schema": "ORION.HarnessSolveOutcome.v1",
            "status": "HOST_CAPABILITY_FAILED",
            "problem_id": problem.problem_id,
            "request": failed.request.as_dict(),
            "result": failed.result.as_dict(),
            "error": failed.detail,
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
    outcome = {
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
        # Which cycle operators this run actually reached. Static execution
        # coverage says a mechanic *has* an owner; this says whether the run got
        # there. See operator_coverage for why the difference cost a campaign.
        "operator_coverage": run_operator_coverage(
            [item.value for item in result.trace.operator_sequence]
        ),
    }
    if require_operators is not None:
        require_operators_exercised(
            outcome, require_operators, label=f"run_problem:{problem.problem_id}"
        )
    return outcome
