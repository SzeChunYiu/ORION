import json

from orion.core.problem import Problem
from orion.core.search import RetrievedItem, SearchRouteKind
from orion.core.solution import SolutionStatus
from orion.providers.llm.base import LLMResponse
from orion.self_orion.baseline import (
    SimpleLLMRetrievalBaseline,
    baseline_bundle_to_dict,
    write_baseline_bundle,
)
from orion.self_orion.live_trial import (
    FrozenTrialTask,
    MechanicTraceSnapshot,
    ResearchTrialKind,
    RetrievedItemSnapshot,
    SearchObservation,
    ShadowLiveTrialReport,
    TrialTaskComparison,
)
from orion.self_orion.trial_io import write_shadow_live_trial_report


class _Retrieval:
    def __init__(self):
        self.queries = []

    def search(self, query, *, limit):
        self.queries.append((query, limit))
        return (
            RetrievedItem(
                "doc:used",
                "raw evidence used by the baseline",
                "https://example.test/used",
                ("domain:test",),
            ),
            RetrievedItem(
                "doc:other",
                "raw evidence the baseline ignored",
                "https://example.test/other",
                ("domain:test",),
            ),
        )


class _LLM:
    def __init__(self, content):
        self.content = content
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        return LLMResponse(
            self.content,
            model_id="baseline-model",
            response_id="baseline-response",
        )


def _task():
    return FrozenTrialTask(
        "task:baseline",
        ResearchTrialKind.WIDE_LITERATURE,
        Problem(
            "task:baseline",
            "What does the evidence establish?",
            initial_domain_ids=("domain:test",),
            success_criteria=("cite retrieved evidence",),
        ),
        ("baseline",),
        "split:frozen",
    )


def test_simple_baseline_is_one_search_one_completion_and_persists_raw_artifact(tmp_path):
    retrieval = _Retrieval()
    llm = _LLM(
        json.dumps(
            {
                "solved": True,
                "answer": "The used document establishes the result.",
                "used_item_ids": ["doc:used"],
                "residual_ids": [],
            }
        )
    )
    baseline = SimpleLLMRetrievalBaseline(
        llm=llm,
        retrieval=retrieval,
        max_results=7,
        retrieval_call_cost_units=2.0,
        llm_call_cost_units=3.0,
    )

    result = baseline.run(_task(), evaluation_epoch_id="epoch:frozen")

    assert result.solved
    assert result.evidence_ids == ("doc:used",)
    assert result.resource_units == 5.0
    assert len(result.artifact_hash) == 64
    assert len(retrieval.queries) == 1
    assert retrieval.queries[0][0].route_kind is SearchRouteKind.CURRENT_VOCABULARY
    assert retrieval.queries[0][1] == 7
    assert len(llm.requests) == 1

    artifact = baseline.artifact("task:baseline")
    assert artifact is not None
    assert artifact.retrieved_items[0].content == "raw evidence used by the baseline"
    assert artifact.response_content == llm.content
    assert artifact.artifact_hash == result.artifact_hash

    bundle = baseline_bundle_to_dict(baseline)
    assert bundle["artifacts"][0]["artifact_hash"] == result.artifact_hash
    assert len(bundle["bundle_hash"]) == 64
    path = tmp_path / "baseline.json"
    write_baseline_bundle(baseline, path)
    persisted = json.loads(path.read_text())
    assert persisted["bundle_hash"] == bundle["bundle_hash"]
    assert persisted["artifacts"][0]["retrieved_items"][1]["item_id"] == "doc:other"


def test_simple_baseline_fails_closed_on_unparseable_or_hallucinated_evidence():
    malformed = SimpleLLMRetrievalBaseline(
        llm=_LLM("not-json"),
        retrieval=_Retrieval(),
    ).run(_task(), evaluation_epoch_id="epoch:frozen")
    assert not malformed.solved
    assert "baseline_output_unparseable" in malformed.residual_ids

    hallucinating = SimpleLLMRetrievalBaseline(
        llm=_LLM(
            json.dumps(
                {
                    "solved": True,
                    "answer": "unsupported",
                    "used_item_ids": ["doc:invented"],
                    "residual_ids": [],
                }
            )
        ),
        retrieval=_Retrieval(),
    ).run(_task(), evaluation_epoch_id="epoch:frozen")
    assert not hallucinating.solved
    assert hallucinating.evidence_ids == ()
    assert "baseline_unknown_evidence_id" in hallucinating.residual_ids


def test_live_trial_writer_persists_raw_trace_and_content_address(tmp_path):
    observation = SearchObservation(
        "q:one",
        "raw query",
        "route:one",
        SearchRouteKind.PARENT_DISCIPLINE.value,
        "domain:test",
        2,
        (
            RetrievedItemSnapshot(
                "doc:used",
                "raw document content",
                "https://example.test/used",
                ("domain:test",),
            ),
        ),
    )
    mechanic = MechanicTraceSnapshot(
        "SEARCH",
        "searched",
        "receipt:one",
        "SEARCH.v1",
        "SUCCEEDED",
        ("SEARCH",),
        ("doc:used",),
        (),
        (),
        (("changed_coordinates", "W.SEARCHED"),),
        (),
    )
    comparison = TrialTaskComparison(
        task_id="task:one",
        kind=ResearchTrialKind.WIDE_LITERATURE,
        orion_status=SolutionStatus.PROVISIONAL,
        orion_evidence_count=1,
        orion_residual_count=1,
        orion_resource_units=3.0,
        baseline_solved=True,
        baseline_evidence_count=1,
        baseline_residual_count=0,
        baseline_resource_units=3.0,
        resource_matched=True,
        required_evidence_recovered=True,
        root_episode_id="episode:one",
        mechanic_episode_ids=("mechanic-episode:one",),
        search_observations=(observation,),
        mechanic_trace=(mechanic,),
        solution_evidence_ids=("doc:used",),
        absorbed_evidence_ids=("doc:used",),
    )
    report = ShadowLiveTrialReport(
        "packet:one",
        "f" * 64,
        (comparison,),
        True,
        True,
        1,
        0,
        "shadow only",
    )

    path = tmp_path / "shadow-live-trial.json"
    write_shadow_live_trial_report(report, path)
    persisted = json.loads(path.read_text())

    assert persisted["schema"] == "ShadowLiveTrialReport.v1"
    assert persisted["raw_search_trace_retained"]
    assert persisted["evidence_artifact_hash"] == report.evidence_artifact_hash
    assert persisted["comparisons"][0]["search_observations"][0]["query_text"] == "raw query"
    assert persisted["comparisons"][0]["search_observations"][0]["items"][0]["content"] == "raw document content"
    assert not persisted["grants_self_promotion"]
