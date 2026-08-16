from types import SimpleNamespace

import pytest

from orion.core.problem import Problem
from orion.core.solution import SolutionStatus
from orion.self_orion.live_trial import (
    BaselineTaskResult,
    FrozenLiveTrialPacket,
    FrozenTrialTask,
    ResearchTrialKind,
    ShadowLiveTrialRunner,
)


class _Baseline:
    def run(self, task, *, evaluation_epoch_id):
        return BaselineTaskResult(task.task_id, False, (), ("baseline-open",), 10.0, "baseline-artifact")


class _Orion:
    def solve(self, problem, *, variation_signature, evaluation_epoch_id, split_id):
        receipt = SimpleNamespace(cost_units=4.0)
        event = SimpleNamespace(receipt=receipt)
        solution = SimpleNamespace(status=SolutionStatus.BLOCKED, evidence_ids=(), residual_ids=("coverage-open",))
        return SimpleNamespace(
            solution=solution,
            trace=SimpleNamespace(events=(event,)),
            experience_episode_id=f"episode:{problem.problem_id}",
            mechanic_experience_episode_ids=(f"mechanic-episode:{problem.problem_id}",),
        )


def _task(task_id: str, kind: ResearchTrialKind):
    return FrozenTrialTask(
        task_id,
        kind,
        Problem(task_id, f"Research {task_id}", success_criteria=("preserve evidence",)),
        ("v1",),
        f"split:{kind.value.lower()}",
    )


def _packet():
    return FrozenLiveTrialPacket(
        packet_id="trial:shadow-v1",
        evaluation_epoch_id="epoch:frozen-v1",
        tasks=(
            _task("task:wide", ResearchTrialKind.WIDE_LITERATURE),
            _task("task:deep", ResearchTrialKind.DEEP_TARGET),
        ),
        provider_manifest_hash="a" * 64,
        evaluator_artifact_hash="b" * 64,
        baseline_id="baseline:llm-retrieval",
        resource_budget_units=12.0,
        max_orion_to_baseline_resource_ratio=1.0,
    )


def test_live_trial_requires_wide_and_deep_tasks():
    with pytest.raises(ValueError, match="wide-literature and one deep-target"):
        FrozenLiveTrialPacket(
            packet_id="bad",
            evaluation_epoch_id="epoch",
            tasks=(_task("task:wide", ResearchTrialKind.WIDE_LITERATURE),),
            provider_manifest_hash="a" * 64,
            evaluator_artifact_hash="b" * 64,
            baseline_id="baseline",
            resource_budget_units=10.0,
        )


def test_shadow_trial_preserves_failure_episode_identity_and_never_grants_self_promotion():
    report = ShadowLiveTrialRunner(orion=_Orion(), baseline=_Baseline()).run(_packet())
    assert report.wide_task_count == 1
    assert report.deep_task_count == 1
    assert report.all_resource_matched
    assert report.all_failures_recordable
    assert not report.grants_self_promotion
    assert all(item.root_episode_id for item in report.comparisons)
    assert all(item.orion_resource_units == 4.0 for item in report.comparisons)
