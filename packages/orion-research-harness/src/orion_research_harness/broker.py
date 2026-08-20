from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Mapping

from orion.core.search import RetrievedItem, SearchQuery
from orion.providers.llm.base import LLMRequest, LLMResponse
from orion.providers.verification.base import VerificationResult

from .protocol import CapabilityRequest, CapabilityResult, content_digest
from .workspace import ResearchWorkspace


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


class HostCapabilityRequired(BaseException):
    """Control signal for missing orchestration capability, not scientific evidence."""

    def __init__(self, request: CapabilityRequest) -> None:
        self.request = request
        super().__init__(f"host capability required: {request.capability} ({request.request_id})")


class HostCapabilityFailed(BaseException):
    """Control signal for host execution failure, never scientific operator evidence."""

    def __init__(self, request: CapabilityRequest, result: CapabilityResult) -> None:
        self.request = request
        self.result = result
        detail = result.error or "unspecified error"
        super().__init__(
            f"host capability failed: {request.capability} via {result.executor}: {detail}"
        )


class CapabilityBroker:
    def __init__(self, workspace: ResearchWorkspace) -> None:
        self.workspace = workspace

    def require(self, capability: str, payload: Mapping[str, Any]) -> Any:
        request = self.workspace.get_or_create_request(
            capability=str(capability),
            payload=_jsonable(payload),
        )
        result = self.workspace.load_result(request.request_id)
        if result is None:
            raise HostCapabilityRequired(request)
        if not result.success:
            raise HostCapabilityFailed(request, result)
        return result.output


class BrokerLLMProvider:
    def __init__(self, broker: CapabilityBroker) -> None:
        self._broker = broker

    def complete(self, request: LLMRequest) -> LLMResponse:
        output = self._broker.require(
            "LLM_COMPLETE",
            {
                "task": request.task,
                "system": request.system,
                "user": request.user,
                "response_schema": request.response_schema,
                "instruction": (
                    "Return an object with `content` containing the model response text. "
                    "For ORION semantic tasks, content itself must be JSON matching response_schema."
                ),
            },
        )
        if isinstance(output, str):
            return LLMResponse(content=output, model_id="external-host")
        if not isinstance(output, Mapping):
            raise TypeError("LLM_COMPLETE output must be a string or object")
        return LLMResponse(
            content=str(output["content"]),
            model_id=(str(output["model_id"]) if output.get("model_id") else None),
            response_id=(str(output["response_id"]) if output.get("response_id") else None),
        )


class BrokerRetrievalProvider:
    def __init__(self, broker: CapabilityBroker) -> None:
        self._broker = broker

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        output = self._broker.require(
            "WEB_SEARCH",
            {
                "query": _jsonable(query),
                "limit": int(limit),
                "instruction": (
                    "Use current web search. Open/inspect relevant primary or authoritative sources "
                    "when useful. Return `items`, each with content, source_uri, optional item_id, "
                    "and optional domain_ids. Do not fabricate sources."
                ),
            },
        )
        if not isinstance(output, Mapping) or not isinstance(output.get("items"), list):
            raise TypeError("WEB_SEARCH output must be an object containing an items list")
        items: list[RetrievedItem] = []
        for index, raw in enumerate(output["items"][:limit]):
            if not isinstance(raw, Mapping):
                raise TypeError("WEB_SEARCH item must be an object")
            source_uri = str(raw["source_uri"])
            content = str(raw["content"])
            stable_id = content_digest({"source_uri": source_uri, "content": content})[:24]
            item_id = str(raw.get("item_id") or f"host-web:{query.query_id}:{index}:{stable_id}")
            domain_ids = tuple(str(item) for item in raw.get("domain_ids", ()))
            items.append(
                RetrievedItem(
                    item_id=item_id,
                    content=content,
                    source_uri=source_uri,
                    domain_ids=domain_ids,
                )
            )
        return tuple(items)


class BrokerVerificationProvider:
    def __init__(self, broker: CapabilityBroker) -> None:
        self._broker = broker

    def verify(self, contribution, item: RetrievedItem) -> VerificationResult:
        output = self._broker.require(
            "VERIFY_EVIDENCE",
            {
                "contribution": _jsonable(contribution),
                "retrieved_item": _jsonable(item),
                "instruction": (
                    "Independently check whether the contribution is supported by the retrieved "
                    "source item. Fail closed when support cannot be established. A passing result "
                    "must include at least one externally meaningful certificate_id."
                ),
            },
        )
        if not isinstance(output, Mapping):
            raise TypeError("VERIFY_EVIDENCE output must be an object")
        passed = bool(output.get("passed", False))
        certificates = tuple(str(item) for item in output.get("certificate_ids", ()))
        reason = str(output.get("reason", ""))
        return VerificationResult(
            passed=passed,
            certificate_ids=certificates,
            reason=reason,
        )
