from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from orion.providers.llm.base import LLMRequest, LLMResponse


@dataclass(frozen=True)
class CallableLLMProvider:
    """Thin adapter for SDK/client functions without coupling ORION to a vendor."""

    complete_fn: Callable[[LLMRequest], LLMResponse | str]
    model_id: str | None = None

    def complete(self, request: LLMRequest) -> LLMResponse:
        result = self.complete_fn(request)
        if isinstance(result, LLMResponse):
            return result
        if isinstance(result, str):
            return LLMResponse(content=result, model_id=self.model_id)
        raise TypeError("LLM callable must return LLMResponse or str")
