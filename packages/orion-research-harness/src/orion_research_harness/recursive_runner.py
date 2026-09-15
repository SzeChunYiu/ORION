from __future__ import annotations

import dataclasses
import hashlib
import re
from dataclasses import dataclass, replace
from enum import Enum
from collections.abc import Iterable
from typing import Any, Mapping
from uuid import uuid4

from orion import Problem
from orion.core.problem_tree import ProblemAtom, ResidualAtom
from orion.core.residuals import Residual
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import OrionState
from orion.engine.residual_recursion import (
    ProblemRecursionPlanner,
    ResidualRecursionPlanner,
    ResidualRecursionPolicy,
)
from orion.engine.solver import OrionSolver, SolverConfig
from orion.engine.trace import SolveTrace
from orion.providers.experience import InMemoryExperienceStore
from orion.providers.reasoner.recursive_llm import RecursiveLLMResearchReasoner
from orion.runtime import OrionRuntime, RuntimeResult

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

_VOLATILE_RESIDUAL_METADATA_KEYS = {
    "epoch",
    "state_epoch",
    "iteration",
    "iteration_index",
    "cycle",
    "cycle_index",
    "timestamp",
    "created_at",
    "updated_at",
    "trace_id",
    "run_id",
    "receipt_id",
}


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
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


def _semantic_state_hash(state: OrionState) -> str:
    """Ignore epoch/iteration bookkeeping when deciding whether research progressed."""

    payload = repr(
        (
            state.knowledge,
            state.search_universe,
            state.method,
            state.closure_certificates,
            state.metadata,
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _without_problem_local_residuals(state: OrionState) -> OrionState:
    """Carry knowledge forward without leaking one problem's residual objects into a child."""

    if not state.knowledge.residuals:
        return state
    knowledge = replace(state.knowledge, residuals=())
    return replace(state, knowledge=knowledge)


def _material_residuals(result: RuntimeResult) -> tuple[Residual, ...]:
    return tuple(item for item in result.final_state.knowledge.residuals if item.material)


def _normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _stable_metadata(residual: Residual) -> tuple[tuple[str, str], ...]:
    """Remove execution-local coordinates while retaining scientific/context identity."""

    rows: list[tuple[str, str]] = []
    for key, value in residual.metadata:
        normalized_key = key.casefold()
        if normalized_key in _VOLATILE_RESIDUAL_METADATA_KEYS:
            continue
        if normalized_key.endswith("_epoch") or normalized_key.endswith("_timestamp"):
            continue
        rows.append((key, value))
    return tuple(sorted(rows))


def _logical_residual_fingerprint(residual: Residual) -> str:
    """Stable logical identity independent of receipt/epoch minting.

    The fingerprint deliberately excludes ``residual_id``. Detector-generated IDs
    may change after every parent re-solve even when the same scientific failure is
    still present. Ambiguous semantic matches are never guessed.
    """

    payload = repr(
        (
            residual.kind.value,
            _normalize_text(residual.description),
            tuple(item.value for item in residual.candidate_responsibilities),
            _stable_metadata(residual),
            bool(residual.material),
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class _ResidualMatch:
    status: str
    residual: Residual | None
    candidate_ids: tuple[str, ...] = ()


def _match_material_residual(
    result: RuntimeResult,
    previous: Residual,
) -> _ResidualMatch:
    material = _material_residuals(result)
    exact = tuple(item for item in material if item.residual_id == previous.residual_id)
    if len(exact) == 1:
        return _ResidualMatch("EXACT_ID", exact[0], (exact[0].residual_id,))
    if len(exact) > 1:
        return _ResidualMatch(
            "AMBIGUOUS_EXACT_ID", None, tuple(item.residual_id for item in exact)
        )

    fingerprint = _logical_residual_fingerprint(previous)
    logical = tuple(
        item for item in material if _logical_residual_fingerprint(item) == fingerprint
    )
    if len(logical) == 1:
        return _ResidualMatch(
            "SEMANTIC_FINGERPRINT", logical[0], (logical[0].residual_id,)
        )
    if len(logical) > 1:
        return _ResidualMatch(
            "AMBIGUOUS_SEMANTIC_FINGERPRINT",
            None,
            tuple(item.residual_id for item in logical),
        )
    return _ResidualMatch("ABSENT", None, ())


@dataclass(frozen=True)
class RecursiveRunLimits:
    max_depth: int = 5
    max_nodes: int = 32
    max_children_per_residual: int = 12
    max_children_per_problem: int = 12

    def __post_init__(self) -> None:
        for name, value in (
            ("max_depth", self.max_depth),
            ("max_nodes", self.max_nodes),
            ("max_children_per_residual", self.max_children_per_residual),
            ("max_children_per_problem", self.max_children_per_problem),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 1:
                raise ValueError(f"{name} must be positive")


class _RecursiveSession:
    def __init__(
        self,
        *,
        runtime: OrionRuntime,
        residual_planner: ResidualRecursionPlanner,
        problem_planner: ProblemRecursionPlanner,
        limits: RecursiveRunLimits,
        evaluation_epoch_id: str,
    ) -> None:
        self.runtime = runtime
        self.residual_planner = residual_planner
        self.problem_planner = problem_planner
        self.limits = limits
        self.evaluation_epoch_id = evaluation_epoch_id
        self.nodes: list[dict[str, Any]] = []
        self.plans: list[dict[str, Any]] = []
        self.pruned_atoms: list[dict[str, str]] = []
        self.stop_records: list[dict[str, Any]] = []
        self.visited: set[tuple[str, str]] = set()
        self.max_depth_reached = 0
        self.resource_bound_hit = False
        self.identity_ambiguity_hit = False

    def _consume_node(self) -> None:
        if len(self.nodes) >= self.limits.max_nodes:
            self.resource_bound_hit = True
            raise RuntimeError("RECURSIVE_NODE_BUDGET_EXHAUSTED")

    def _record_stop(
        self,
        *,
        problem_id: str,
        residual_id: str,
        stop_reason: str,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        if stop_reason == "CANNOT_CHECK_RESOURCE_BOUND":
            self.resource_bound_hit = True
        if stop_reason == "CANNOT_CHECK_AMBIGUOUS_RESIDUAL_IDENTITY":
            self.identity_ambiguity_hit = True
        record: dict[str, Any] = {
            "problem_id": problem_id,
            "residual_id": residual_id,
            "stop_reason": stop_reason,
        }
        if details:
            record["details"] = dict(details)
        self.stop_records.append(record)

    def _resource_bound_snapshot(
        self,
        *,
        problem: Problem,
        state: OrionState,
    ) -> RuntimeResult:
        """Return a root-scoped CANNOT_CHECK snapshot without consuming a node."""

        trace_id = "recursive-resource-bound:" + uuid4().hex
        residual_ids = tuple(
            item.residual_id for item in state.knowledge.residuals if item.material
        )
        return RuntimeResult(
            solution=Solution(
                problem_id=problem.problem_id,
                status=SolutionStatus.CANNOT_CHECK,
                answer=(
                    "Recursive resource bound reached before the root problem "
                    "could be fully checked."
                ),
                residual_ids=residual_ids,
                trace_id=trace_id,
            ),
            final_state=state,
            trace=SolveTrace(trace_id=trace_id, events=()),
        )

    def _record_runtime(
        self,
        *,
        problem: Problem,
        result: RuntimeResult,
        role: str,
        before_hash: str,
        recursion_depth: int,
        parent_problem_id: str | None,
        parent_residual_id: str | None,
    ) -> None:
        after_hash = _semantic_state_hash(result.final_state)
        self.nodes.append(
            {
                "node_index": len(self.nodes),
                "role": role,
                "problem": _jsonable(problem),
                "recursion_depth": recursion_depth,
                "parent_problem_id": parent_problem_id,
                "parent_residual_id": parent_residual_id,
                "semantic_state_before": before_hash,
                "semantic_state_after": after_hash,
                "semantic_progress": before_hash != after_hash,
                "solution": _jsonable(result.solution),
                "trace": _jsonable(result.trace),
                "material_residual_ids": [
                    item.residual_id for item in _material_residuals(result)
                ],
                "material_residual_fingerprints": [
                    _logical_residual_fingerprint(item)
                    for item in _material_residuals(result)
                ],
                "experience_episode_id": result.experience_episode_id,
                "mechanic_experience_episode_ids": list(
                    result.mechanic_experience_episode_ids
                ),
            }
        )
        self.max_depth_reached = max(self.max_depth_reached, recursion_depth)

    def _single_solve(
        self,
        *,
        problem: Problem,
        state: OrionState,
        role: str,
        recursion_depth: int,
        parent_problem_id: str | None = None,
        parent_residual_id: str | None = None,
    ) -> RuntimeResult:
        self._consume_node()
        before_hash = _semantic_state_hash(state)
        visit = (problem.problem_id, before_hash)
        if visit in self.visited:
            raise RuntimeError("RECURSIVE_NO_PROGRESS_CYCLE")
        self.visited.add(visit)
        result = self.runtime.solve(
            problem,
            initial_state=state,
            variation_signature=(
                "recursive-problem-residual-solver-v3",
                f"depth:{recursion_depth}",
                f"role:{role}",
                f"parent_problem:{parent_problem_id or '-'}",
                f"parent_residual:{parent_residual_id or '-'}",
            ),
            evaluation_epoch_id=self.evaluation_epoch_id,
            split_id="recursive-research",
        )
        self._record_runtime(
            problem=problem,
            result=result,
            role=role,
            before_hash=before_hash,
            recursion_depth=recursion_depth,
            parent_problem_id=parent_problem_id,
            parent_residual_id=parent_residual_id,
        )
        return result

    def _record_problem_plan(
        self,
        *,
        problem: Problem,
        recursion_depth: int,
        atoms: tuple[ProblemAtom, ...],
        decomposition,
    ) -> None:
        self.plans.append(
            {
                "plan_index": len(self.plans),
                "plan_kind": "PROBLEM_DECOMPOSITION",
                "parent_problem_id": problem.problem_id,
                "parent_residual_id": None,
                "recursion_depth": recursion_depth,
                "rationale": decomposition.rationale,
                "stop_reason": (
                    None
                    if decomposition.stop_reason is None
                    else decomposition.stop_reason.value
                ),
                "ordered_atoms": [_jsonable_atom(atom) for atom in atoms],
                "grants_scientific_authority": False,
                "grants_novelty_authority": False,
                "grants_promotion_authority": False,
            }
        )

    def _record_residual_plan(
        self,
        *,
        problem: Problem,
        residual: Residual,
        recursion_depth: int,
        atoms: tuple[ResidualAtom, ...],
        decomposition,
    ) -> None:
        self.plans.append(
            {
                "plan_index": len(self.plans),
                "plan_kind": "RESIDUAL_DECOMPOSITION",
                "parent_problem_id": problem.problem_id,
                "parent_residual_id": residual.residual_id,
                "parent_residual_fingerprint": _logical_residual_fingerprint(residual),
                "recursion_depth": recursion_depth,
                "rationale": decomposition.rationale,
                "stop_reason": (
                    None
                    if decomposition.stop_reason is None
                    else decomposition.stop_reason.value
                ),
                "ordered_atoms": [_jsonable_atom(atom) for atom in atoms],
                "grants_scientific_authority": False,
                "grants_novelty_authority": False,
                "grants_promotion_authority": False,
            }
        )

    def solve_root(
        self,
        *,
        problem: Problem,
        state: OrionState,
    ) -> tuple[RuntimeResult, OrionState]:
        """Decompose the root problem before expensive work, then adapt after evidence."""

        working_state = state
        while True:
            decomposition = self.problem_planner.decompose(
                problem=problem,
                state=working_state,
                recursion_depth=0,
            )
            ordered_atoms = self.problem_planner.order_atoms(decomposition.atoms)
            self._record_problem_plan(
                problem=problem,
                recursion_depth=0,
                atoms=ordered_atoms,
                decomposition=decomposition,
            )
            if not ordered_atoms:
                if decomposition.stop_reason is not None:
                    self._record_stop(
                        problem_id=problem.problem_id,
                        residual_id="",
                        stop_reason=decomposition.stop_reason.value,
                    )
                return self.solve_problem(
                    problem=problem,
                    state=working_state,
                    role="root",
                    recursion_depth=0,
                )

            replanned = False
            for atom_index, atom in enumerate(ordered_atoms):
                if len(self.nodes) >= self.limits.max_nodes:
                    self._record_stop(
                        problem_id=problem.problem_id,
                        residual_id="",
                        stop_reason="CANNOT_CHECK_RESOURCE_BOUND",
                    )
                    snapshot = self._resource_bound_snapshot(
                        problem=problem,
                        state=working_state,
                    )
                    return snapshot, working_state
                child = atom.as_problem(parent_problem=problem)
                before_child_hash = _semantic_state_hash(working_state)
                _child_result, child_state = self.solve_problem(
                    problem=child,
                    state=working_state,
                    role=f"problem-atom:{atom.discriminator.kind.value}",
                    recursion_depth=1,
                    parent_problem_id=problem.problem_id,
                )
                after_child_hash = _semantic_state_hash(child_state)
                working_state = child_state
                if before_child_hash == after_child_hash:
                    continue

                refreshed, refreshed_state = self.solve_problem(
                    problem=problem,
                    state=working_state,
                    role="root-refresh",
                    recursion_depth=0,
                )
                working_state = refreshed_state
                if not _material_residuals(refreshed):
                    for remaining in ordered_atoms[atom_index + 1 :]:
                        self.pruned_atoms.append(
                            {
                                "parent_problem_id": problem.problem_id,
                                "parent_residual_id": "",
                                "atom_id": remaining.atom_id,
                                "reason": "ROOT_PROBLEM_CLOSED_AFTER_CHEAPER_DISCRIMINATOR",
                            }
                        )
                    return refreshed, working_state

                replanned = True
                break

            if replanned:
                continue

            self._record_stop(
                problem_id=problem.problem_id,
                residual_id="",
                stop_reason="NO_PROBLEM_ATOM_PRODUCED_SEMANTIC_PROGRESS",
            )
            return self.solve_problem(
                problem=problem,
                state=working_state,
                role="root-after-null-decomposition",
                recursion_depth=0,
            )

    def solve_problem(
        self,
        *,
        problem: Problem,
        state: OrionState,
        role: str,
        recursion_depth: int,
        parent_problem_id: str | None = None,
        parent_residual_id: str | None = None,
    ) -> tuple[RuntimeResult, OrionState]:
        result = self._single_solve(
            problem=problem,
            state=state,
            role=role,
            recursion_depth=recursion_depth,
            parent_problem_id=parent_problem_id,
            parent_residual_id=parent_residual_id,
        )
        working_state = _without_problem_local_residuals(result.final_state)
        if not _material_residuals(result):
            return result, working_state

        if recursion_depth >= self.limits.max_depth:
            for residual in _material_residuals(result):
                self._record_stop(
                    problem_id=problem.problem_id,
                    residual_id=residual.residual_id,
                    stop_reason="CANNOT_CHECK_RESOURCE_BOUND",
                )
            return result, working_state

        # The queue is rebuilt after every parent refresh.  This prevents a new
        # detector-minted residual id from escaping merely because the previous
        # solve used another epoch-bound id.
        pending: list[Residual] = list(_material_residuals(result))
        processed_fingerprints: set[str] = set()

        while pending:
            current_residual = pending.pop(0)
            current_fingerprint = _logical_residual_fingerprint(current_residual)
            if current_fingerprint in processed_fingerprints:
                continue

            while True:
                decomposition = self.residual_planner.decompose(
                    residual=current_residual,
                    problem=problem,
                    state=result.final_state,
                    recursion_depth=recursion_depth,
                )
                ordered_atoms = self.residual_planner.order_atoms(decomposition.atoms)
                self._record_residual_plan(
                    problem=problem,
                    residual=current_residual,
                    recursion_depth=recursion_depth,
                    atoms=ordered_atoms,
                    decomposition=decomposition,
                )
                if not ordered_atoms:
                    assert decomposition.stop_reason is not None
                    self._record_stop(
                        problem_id=problem.problem_id,
                        residual_id=current_residual.residual_id,
                        stop_reason=decomposition.stop_reason.value,
                    )
                    processed_fingerprints.add(current_fingerprint)
                    break

                replanned_same_logical_residual = False
                replaced_or_ambiguous = False
                for atom_index, atom in enumerate(ordered_atoms):
                    if len(self.nodes) >= self.limits.max_nodes:
                        self._record_stop(
                            problem_id=problem.problem_id,
                            residual_id=current_residual.residual_id,
                            stop_reason="CANNOT_CHECK_RESOURCE_BOUND",
                        )
                        return result, working_state

                    child = atom.as_problem(
                        parent_problem=problem,
                        parent_residual=current_residual,
                    )
                    before_child_hash = _semantic_state_hash(working_state)
                    _child_result, child_state = self.solve_problem(
                        problem=child,
                        state=working_state,
                        role=f"residual-atom:{atom.discriminator.kind.value}",
                        recursion_depth=recursion_depth + 1,
                        parent_problem_id=problem.problem_id,
                        parent_residual_id=current_residual.residual_id,
                    )
                    after_child_hash = _semantic_state_hash(child_state)
                    working_state = child_state
                    if before_child_hash == after_child_hash:
                        continue

                    if len(self.nodes) >= self.limits.max_nodes:
                        self._record_stop(
                            problem_id=problem.problem_id,
                            residual_id=current_residual.residual_id,
                            stop_reason="CANNOT_CHECK_RESOURCE_BOUND",
                        )
                        return result, working_state

                    refreshed = self._single_solve(
                        problem=problem,
                        state=working_state,
                        role="parent-refresh",
                        recursion_depth=recursion_depth,
                        parent_problem_id=parent_problem_id,
                        parent_residual_id=parent_residual_id,
                    )
                    working_state = _without_problem_local_residuals(
                        refreshed.final_state
                    )
                    match = _match_material_residual(refreshed, current_residual)
                    refreshed_material = _material_residuals(refreshed)
                    result = refreshed

                    if match.status in {
                        "AMBIGUOUS_EXACT_ID",
                        "AMBIGUOUS_SEMANTIC_FINGERPRINT",
                    }:
                        self._record_stop(
                            problem_id=problem.problem_id,
                            residual_id=current_residual.residual_id,
                            stop_reason="CANNOT_CHECK_AMBIGUOUS_RESIDUAL_IDENTITY",
                            details={
                                "match_status": match.status,
                                "candidate_ids": list(match.candidate_ids),
                                "logical_fingerprint": current_fingerprint,
                            },
                        )
                        # Do not prune any sibling. Rebuild the queue from every
                        # material residual in the refreshed parent state.
                        pending = list(refreshed_material)
                        processed_fingerprints.add(current_fingerprint)
                        replaced_or_ambiguous = True
                        break

                    if match.residual is not None:
                        # Same logical residual survived even if its concrete id
                        # changed with the parent epoch. Replan against fresh evidence.
                        current_residual = match.residual
                        current_fingerprint = _logical_residual_fingerprint(
                            current_residual
                        )
                        pending = [
                            item
                            for item in refreshed_material
                            if _logical_residual_fingerprint(item)
                            != current_fingerprint
                        ] + pending
                        replanned_same_logical_residual = True
                        break

                    if not refreshed_material:
                        # Closure is safe only when the refreshed parent exposes no
                        # material residual matching or replacing the branch.
                        for remaining in ordered_atoms[atom_index + 1 :]:
                            self.pruned_atoms.append(
                                {
                                    "parent_problem_id": problem.problem_id,
                                    "parent_residual_id": current_residual.residual_id,
                                    "atom_id": remaining.atom_id,
                                    "reason": "PARENT_RESIDUAL_CLOSED_AFTER_CHEAPER_DISCRIMINATOR",
                                }
                            )
                        processed_fingerprints.add(current_fingerprint)
                        replaced_or_ambiguous = True
                        break

                    # The old logical fingerprint disappeared, but other material
                    # residuals remain. That is a reclassification/replacement,
                    # not proof that the scientific branch closed. Never prune the
                    # stale siblings as a scientific shortcut; rebuild from the
                    # fresh residual set instead.
                    self._record_stop(
                        problem_id=problem.problem_id,
                        residual_id=current_residual.residual_id,
                        stop_reason="RESIDUAL_RECLASSIFIED_AFTER_PARENT_REFRESH",
                        details={
                            "old_logical_fingerprint": current_fingerprint,
                            "fresh_residual_ids": [
                                item.residual_id for item in refreshed_material
                            ],
                        },
                    )
                    processed_fingerprints.add(current_fingerprint)
                    pending = list(refreshed_material)
                    replaced_or_ambiguous = True
                    break

                if replanned_same_logical_residual:
                    continue
                if replaced_or_ambiguous:
                    break

                # Every child was attempted without semantic progress. Preserve
                # the residual as open rather than looping or rounding up.
                self._record_stop(
                    problem_id=problem.problem_id,
                    residual_id=current_residual.residual_id,
                    stop_reason="NO_CHILD_PRODUCED_SEMANTIC_PROGRESS",
                )
                processed_fingerprints.add(current_fingerprint)
                break

            # Refresh pending with any currently material logical residual not yet
            # processed. This also catches residuals that were minted during a
            # sibling's parent refresh.
            known_pending = {
                _logical_residual_fingerprint(item) for item in pending
            }
            for item in _material_residuals(result):
                fingerprint = _logical_residual_fingerprint(item)
                if (
                    fingerprint not in processed_fingerprints
                    and fingerprint not in known_pending
                ):
                    pending.append(item)
                    known_pending.add(fingerprint)

        return result, working_state


def _jsonable_atom(atom: ProblemAtom | ResidualAtom) -> dict[str, Any]:
    return {
        "atom_id": atom.atom_id,
        "question": atom.question,
        "responsibility": atom.responsibility.value,
        "discriminator_id": atom.discriminator.discriminator_id,
        "discriminator_kind": atom.discriminator.kind.value,
        "expected_cost_units": atom.discriminator.expected_cost_units,
        "success_criterion": atom.discriminator.success_criterion,
        "metadata": dict(atom.metadata),
    }


def run_problem_recursive(
    workspace: ResearchWorkspace,
    problem_data: Mapping[str, Any],
    *,
    max_iterations: int = 3,
    require_verified_answer: bool = True,
    limits: RecursiveRunLimits | None = None,
    require_operators: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Run canonical ORION with recursive problem/residual control.

    Root problems are decomposed before expensive solving. Material residuals are
    then recursively treated as child problems. Host capability interruptions stay
    replayable because immutable request/result receipts are reused on the next
    invocation. Recursive planning is proposal-only and cannot mint authority.

    ``require_operators`` names cycle operators the caller's experiment depends on.
    A completed run that never reached one raises ``OperatorNotExercised`` naming
    it. This is the path whose trace shape --- ``FRAME SEARCH ABSORB RECONSTRUCT
    DETECT RECURSE SATURATE_BOUNDED``, no ``DIAGNOSE`` --- the P1-U R6 campaign
    scored 48 times without noticing.
    """

    limits = limits or RecursiveRunLimits()
    broker = CapabilityBroker(workspace)
    llm = BrokerLLMProvider(broker)
    reasoner = RecursiveLLMResearchReasoner(llm)
    experiences = InMemoryExperienceStore()
    solver = OrionSolver(
        reasoner=reasoner,
        retrieval=BrokerRetrievalProvider(broker),
        verification=BrokerVerificationProvider(broker),
        config=SolverConfig(
            max_iterations=int(max_iterations),
            require_verified_answer=bool(require_verified_answer),
        ),
    )
    runtime = OrionRuntime(
        solver,
        experience_store=experiences,
        producer_process_lineage_hash=_sha256_label(
            "orion-research-harness-recursive-v3"
        ),
        evaluator_artifact_hash=_sha256_label(
            "external-host-capability-receipts-recursive-v3"
        ),
    )
    policy = ResidualRecursionPolicy(
        max_depth=limits.max_depth,
        max_children_per_residual=limits.max_children_per_residual,
        max_children_per_problem=limits.max_children_per_problem,
    )
    residual_planner = ResidualRecursionPlanner(reasoner, policy=policy)
    problem_planner = ProblemRecursionPlanner(reasoner, policy=policy)
    session = _RecursiveSession(
        runtime=runtime,
        residual_planner=residual_planner,
        problem_planner=problem_planner,
        limits=limits,
        evaluation_epoch_id=f"harness-recursive:{workspace.session_id}",
    )
    problem = Problem(
        problem_id=str(problem_data["problem_id"]),
        question=str(problem_data["question"]),
        scope=str(problem_data.get("scope", "")),
        initial_domain_ids=tuple(
            str(x) for x in problem_data.get("initial_domain_ids", ())
        ),
        success_criteria=tuple(
            str(x) for x in problem_data.get("success_criteria", ())
        ),
    )
    initial_state = solver.initial_state(problem)
    try:
        result, _working_state = session.solve_root(
            problem=problem,
            state=initial_state,
        )
    except HostCapabilityRequired as pending:
        return {
            "schema": "ORION.HarnessRecursiveSolveOutcome.v3",
            "status": "PENDING_CAPABILITY",
            "problem_id": problem.problem_id,
            "request": pending.request.as_dict(),
            "recursive_progress": {
                "completed_nodes": len(session.nodes),
                "completed_plans": len(session.plans),
                "max_depth_reached": session.max_depth_reached,
                "resource_bound_hit": session.resource_bound_hit,
            },
        }
    except HostCapabilityFailed as failed:
        return {
            "schema": "ORION.HarnessRecursiveSolveOutcome.v3",
            "status": "HOST_CAPABILITY_FAILED",
            "problem_id": problem.problem_id,
            "request": failed.request.as_dict(),
            "result": failed.result.as_dict(),
            "error": failed.detail,
            "recursive_progress": {
                "completed_nodes": len(session.nodes),
                "completed_plans": len(session.plans),
                "max_depth_reached": session.max_depth_reached,
                "resource_bound_hit": session.resource_bound_hit,
            },
        }
    except (ValueError, TypeError, KeyError) as exc:
        # A successful host receipt whose content violates the task schema
        # (bad JSON, wrong field type, invalid enum value) surfaces here from
        # the reasoner's strict parsing. That is an orchestration condition of
        # the host boundary, never scientific failure evidence, so it maps to
        # the documented HOST_CAPABILITY_FAILED contract instead of a raw
        # traceback. The receipt itself stays immutable; recovery goes through
        # `retry-failed --invalid-content`.
        return {
            "schema": "ORION.HarnessRecursiveSolveOutcome.v3",
            "status": "HOST_CAPABILITY_FAILED",
            "problem_id": problem.problem_id,
            "error": f"reasoner content invalid: {exc}",
            "recursive_progress": {
                "completed_nodes": len(session.nodes),
                "completed_plans": len(session.plans),
                "max_depth_reached": session.max_depth_reached,
                "resource_bound_hit": session.resource_bound_hit,
            },
        }
    except RuntimeError as exc:
        if str(exc) not in {
            "RECURSIVE_NODE_BUDGET_EXHAUSTED",
            "RECURSIVE_NO_PROGRESS_CYCLE",
        }:
            raise
        run_status = str(exc)
        if run_status == "RECURSIVE_NODE_BUDGET_EXHAUSTED":
            session.resource_bound_hit = True
        result = None
    else:
        run_status = "COMPLETE"

    if session.resource_bound_hit:
        public_status = "CANNOT_CHECK_RESOURCE_BOUND"
    elif session.identity_ambiguity_hit:
        public_status = "CANNOT_CHECK_RESIDUAL_IDENTITY"
    elif result is None:
        public_status = "CANNOT_CHECK"
    else:
        public_status = "COMPLETE"

    run_id = "recursive-run:" + uuid4().hex
    record = {
        "schema": "ORION.HarnessRecursiveRun.v3",
        "run_id": run_id,
        "session_id": workspace.session_id,
        "created_at": utc_now(),
        "problem": _jsonable(problem),
        "limits": _jsonable(limits),
        "status": public_status,
        "internal_run_status": run_status,
        "nodes": session.nodes,
        "decomposition_plans": session.plans,
        "pruned_atoms": session.pruned_atoms,
        "stop_records": session.stop_records,
        "max_depth_reached": session.max_depth_reached,
        "resource_bound_hit": session.resource_bound_hit,
        "identity_ambiguity_hit": session.identity_ambiguity_hit,
        "experience_episodes": [_jsonable(item) for item in experiences.episodes()],
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_promotion_authority": False,
    }
    if result is not None:
        record["final_solution"] = _jsonable(result.solution)
        record["final_state"] = _jsonable(result.final_state)
    workspace.save_run(run_id, record)

    material = () if result is None else _material_residuals(result)
    if public_status != "COMPLETE":
        return {
            "schema": "ORION.HarnessRecursiveSolveOutcome.v3",
            "status": public_status,
            "problem_id": problem.problem_id,
            "run_id": run_id,
            "recursive_status": run_status,
            "node_count": len(session.nodes),
            "max_depth_reached": session.max_depth_reached,
            "pruned_atom_count": len(session.pruned_atoms),
            "residual_ids": [item.residual_id for item in material],
            "stop_records": session.stop_records,
        }

    assert result is not None
    recursive_status = "RESIDUALS_OPEN" if material else "RESIDUAL_TREE_CLOSED"
    operator_sequence = [item.value for item in result.trace.operator_sequence]
    outcome = {
        "schema": "ORION.HarnessRecursiveSolveOutcome.v3",
        "status": "COMPLETE",
        "problem_id": problem.problem_id,
        "run_id": run_id,
        "solution_status": result.solution.status.value,
        "answer": result.solution.answer,
        "evidence_ids": list(result.solution.evidence_ids),
        "residual_ids": [item.residual_id for item in material],
        "trace_id": result.trace.trace_id,
        "recursive_status": recursive_status,
        "node_count": len(session.nodes),
        "plan_count": len(session.plans),
        "max_depth_reached": session.max_depth_reached,
        "pruned_atom_count": len(session.pruned_atoms),
        "stop_records": session.stop_records,
        "operator_sequence": operator_sequence,
        # Which operators this run actually reached, not which ones have an owner.
        "operator_coverage": run_operator_coverage(operator_sequence),
    }
    if require_operators is not None:
        require_operators_exercised(
            outcome,
            require_operators,
            label=f"run_problem_recursive:{problem.problem_id}",
        )
    return outcome
