import json

import pytest

from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search import SearchRouteKind
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.providers.llm.base import LLMRequest, LLMResponse
from orion.providers.reasoner.llm import LLMResearchReasoner


class FakeLLMProvider:
    def __init__(self, content=None):
        self.requests: list[LLMRequest] = []
        self.content = content or '{"queries":[{"query_id":"q1","text":"parent field for semantic normalization","route_id":"parent","route_kind":"PARENT_DISCIPLINE","domain_hint":null}]}'

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(content=self.content, model_id="fake")


def _state():
    return OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
    )


def test_llm_provider_is_adapted_to_typed_search_plan_with_formal_schema():
    provider = FakeLLMProvider()
    reasoner = LLMResearchReasoner(provider)
    queries = reasoner.plan_search(
        Problem("p", "How should claims be normalized?"), _state()
    )
    assert len(queries) == 1
    assert queries[0].route_kind is SearchRouteKind.PARENT_DISCIPLINE
    request = provider.requests[0]
    assert request.task == "plan_search"
    schema = json.loads(request.response_schema)
    assert schema["type"] == "object"
    assert schema["properties"]["queries"]["minItems"] == 1
    item_schema = schema["properties"]["queries"]["items"]
    assert set(item_schema["required"]) == {
        "query_id",
        "text",
        "route_id",
        "route_kind",
        "domain_hint",
    }
    assert item_schema["additionalProperties"] is False


def test_reasoner_rejects_missing_search_field_as_typed_validation_not_keyerror():
    provider = FakeLLMProvider(
        '{"queries":[{"query_id":"q1","text":"query","route_id":"route","domain_hint":null}]}'
    )
    with pytest.raises(ValueError, match="route_kind"):
        LLMResearchReasoner(provider).plan_search(
            Problem("p", "question"), _state()
        )
