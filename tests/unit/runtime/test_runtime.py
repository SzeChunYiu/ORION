from orion.core.problem import Problem
from orion.engine.solver import SolverConfig
from orion.providers.llm import CallableLLMProvider, LLMResponse
from orion.providers.retrieval import InMemoryRetrievalProvider
from orion.providers.verification import InMemoryVerificationProvider
from orion.runtime import OrionRuntime


def test_callable_llm_adapter_accepts_string_or_typed_response():
    string_adapter = CallableLLMProvider(lambda request: '{"queries":[]}', model_id="string-model")
    response = string_adapter.complete(type("Request", (), {})())
    assert response.content == '{"queries":[]}'
    assert response.model_id == "string-model"

    typed_adapter = CallableLLMProvider(lambda request: LLMResponse(content="{}", model_id="typed"))
    assert typed_adapter.complete(type("Request", (), {})()).model_id == "typed"


def test_runtime_can_be_composed_without_vendor_dependencies():
    llm = CallableLLMProvider(lambda request: '{"queries":[]}', model_id="fake")
    runtime = OrionRuntime.from_providers(
        llm=llm,
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        config=SolverConfig(max_iterations=1),
    )
    result = runtime.solve(Problem("runtime-smoke", "What can be established?"))
    assert result.solution.problem_id == "runtime-smoke"
    assert result.trace.trace_id.startswith("trace:runtime-smoke:")
