from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search import SearchRouteKind
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.providers.llm.base import LLMRequest, LLMResponse
from orion.providers.reasoner.llm import LLMResearchReasoner


class FakeLLMProvider:
    def __init__(self):
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(
            content='{"queries":[{"query_id":"q1","text":"parent field for semantic normalization","route_id":"parent","route_kind":"PARENT_DISCIPLINE","domain_hint":null}]}',
            model_id="fake",
        )


def test_llm_provider_is_adapted_to_typed_search_plan():
    provider = FakeLLMProvider()
    reasoner = LLMResearchReasoner(provider)
    state = OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
    )
    queries = reasoner.plan_search(Problem("p", "How should claims be normalized?"), state)
    assert len(queries) == 1
    assert queries[0].route_kind is SearchRouteKind.PARENT_DISCIPLINE
    assert provider.requests[0].task == "plan_search"
