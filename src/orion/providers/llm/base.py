from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    task: str
    system: str
    user: str
    response_schema: str | None = None


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model_id: str | None = None
    response_id: str | None = None


class LLMProvider(Protocol):
    """Vendor-neutral LLM boundary. Provider adapters implement one method."""

    def complete(self, request: LLMRequest) -> LLMResponse:
        ...
