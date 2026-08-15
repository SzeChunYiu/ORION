"""Provider-neutral integration sketch.

Replace the three callables with real SDK/search/verification functions. The example is
not executed by default because ORION core contains no vendor credentials or network side effects.
"""

from orion import Problem
from orion.providers.llm import CallableLLMProvider
from orion.providers.retrieval import CallableRetrievalProvider
from orion.providers.verification import CallableVerificationProvider
from orion.runtime import OrionRuntime


def build_runtime(llm_complete, retrieve, verify):
    return OrionRuntime.from_providers(
        llm=CallableLLMProvider(llm_complete),
        retrieval=CallableRetrievalProvider(retrieve),
        verification=CallableVerificationProvider(verify),
    )


def solve(runtime: OrionRuntime, question: str):
    return runtime.solve(Problem("external-problem", question))
