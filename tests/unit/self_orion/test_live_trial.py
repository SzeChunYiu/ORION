from types import SimpleNamespace

import pytest

from orion.core.problem import Problem
from orion.core.search import RetrievedItem, SearchQuery, SearchRouteKind
from orion.core.solution import SolutionStatus
from orion.self_orion.live_trial import (
    BaselineTaskResult,
    FrozenLiveTrialPacket,
    FrozenTrialTask,
    RecordingRetrievalProvider,
    ResearchTrialKind,
    ShadowLiveTrialRunner,
)


class _Baseline:
    def run(self, task, *, evaluation_epoch_id):
        return BaselineTaskResult(
            task.task_id,
            False,
            (),
            ("baseline-open",),
            10.0,
            "baseline-artifact",
        )


class _Orion:
    def solve(self, problem, *, variation_signature, evaluation_epoch_id, split_id):
        receipt = SimpleNamespace(cost_units=4.0)
        event = SimpleNamespace(receipt=receipt)
        solution = SimpleNamespace(
            status=SolutionStatus.BLOCKED,
            evidence_ids=(),
            residual_ids=("coverage-open",),
        )
        return SimpleNamespace(
            solution=solution,
            trace=SimpleNamespace(events=(event,)),
            experience_episode_id=f"episode:{problem.problem_id}",
            mechanic_experience_episode_ids=(f"mechanic-episode:{problem.problem_id}",),
        )


class _Retrieval:
    def search(self, query, *, limit):
        assert isinstance(query, SearchQuery)
        assert limit == 2
        return (
            RetrievedItem(
                "source:used",
                "verbatim document used by the answer",
                "https://example.test/used",
                ("domain:test",),
            ),
            RetrievedItem(
                "source:unused",
                "verbatim document retrieved but not used",
                "https://example.test/unused",
                ("domain:test",),
            ),
        )


class _InstrumentedOrion:
    def __init__(self, retrieval):
        self._retrieval = retrieval

    def solve(self, problem, *, variation_signature, evaluation_epoch_id, split_id):
        query = SearchQuery(
            query_id=f"query:{problem.problem_id}",
            text=f"raw frozen query for {problem.problem_id}",
            route_id="route:parent-discipline",
            route_kind=SearchRouteKind.PARENT_DISCIPLINE,
            domain_hint="domain:test",
        )
        self._retrieval.search(query, limit=2)
        receipt = SimpleNamespace(
            cost_units=4.0,
            receipt_id=f"receipt:{problem.problem_id}:search",
            mechanic_id="SEARCH.v1",
            status=SimpleNamespace(value="SUCCEEDED"),
            action_ids=("SEARCH",),
            evidence_ids=("source:used", "source:unused"),
            residual_ids=(),
            failure_signature=(),
            handoff_values=(("changed_coordinates", "W.SEARCHED"),),
            provenance_ids=(),
        )
        event = SimpleNamespace(
            operator=SimpleNamespace(value="SEARCH"),
            summary="searched two raw documents",
            receipt=receipt,
        )
        solution = SimpleNamespace(
            status=SolutionStatus.PROVISIONAL,
            evidence_ids=("source:used",),
            residual_ids=("coverage-open",),
        )
        return SimpleNamespace(
            solution=solution,
            final_state=SimpleNamespace(
                knowledge=SimpleNamespace(evidence_ids=("source:used",))
            ),
            trace=SimpleNamespace(events=(event,)),
            experience_episode_id=f"episode:{problem.problem_id}",
            mechanic_experience_episode_ids=(
                f"mechanic-episode:{problem.problem_id}",
            ),
        )


def _task(task_id: str, kind: ResearchTrialKind):
    return FrozenTrialTask(
        task_id,
        kind,
        Problem(
            task_id,
            f"Research {task_id}",
            success_criteria=("preserve evidence",),
        ),
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


def test_recording_retrieval_provider_is_transparent_and_retains_raw_provider_output():
    recorder = RecordingRetrievalProvider(_Retrieval())
    query = SearchQuery(
        "query:one",
        "raw query text",
        "route:one",
        SearchRouteKind.PARENT_DISCIPLINE,
        "domain:test",
    )
    mark = recorder.mark()
    returned = recorder.search(query, limit=2)

    assert tuple(item.item_id for item in returned) == ("source:used", "source:unused")
    observations = recorder.observations_since(mark)
    assert len(observations) == 1
    observation = observations[0]
    assert observation.query_text == "raw query text"
    assert observation.route_kind == "PARENT_DISCIPLINE"
    assert tuple(item.content for item in observation.items) == (
        "verbatim document used by the answer",
        "verbatim document retrieved but not used",
    )


def test_live_trial_retains_raw_queries_documents_mechanic_use_and_unused_attribution():
    recorder = RecordingRetrievalProvider(_Retrieval())
    runner = ShadowLiveTrialRunner(
        orion=_InstrumentedOrion(recorder),
        baseline=_Baseline(),
        retrieval_recorder=recorder,
    )
    report = runner.run(_packet())

    assert report.raw_search_trace_retained
    assert len(report.evidence_artifact_hash) == 64
    assert report.evidence_artifact_hash == report.evidence_artifact_hash
    assert not report.grants_self_promotion

    for comparison in report.comparisons:
        assert comparison.raw_query_count == 1
        assert comparison.raw_retrieved_item_count == 2
        assert comparison.search_observations[0].query_text.startswith(
            "raw frozen query for"
        )
        assert comparison.search_observations[0].items[0].content == (
            "verbatim document used by the answer"
        )
        assert comparison.solution_evidence_ids == ("source:used",)
        assert comparison.absorbed_evidence_ids == ("source:used",)
        assert comparison.retrieved_but_unused_ids == ("source:unused",)
        assert comparison.retrieved_but_unabsorbed_ids == ("source:unused",)
        assert comparison.mechanic_trace[0].mechanic_id == "SEARCH.v1"
        assert comparison.mechanic_trace[0].evidence_ids == (
            "source:used",
            "source:unused",
        )
