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
    """Control signal for host execution/contract failure, never scientific evidence."""

    def __init__(
        self,
        request: CapabilityRequest,
        result: CapabilityResult,
        *,
        detail: str | None = None,
    ) -> None:
        self.request = request
        self.result = result
        self.detail = detail or result.error or "unspecified error"
        super().__init__(
            f"host capability failed: {request.capability} via {result.executor}: {self.detail}"
        )


class CapabilityBroker:
    def __init__(self, workspace: ResearchWorkspace) -> None:
        self.workspace = workspace

    def require_result(
        self, capability: str, payload: Mapping[str, Any]
    ) -> tuple[CapabilityRequest, CapabilityResult]:
        request = self.workspace.get_or_create_request(
            capability=str(capability),
            payload=_jsonable(payload),
        )
        result = self.workspace.load_result(request.request_id)
        if result is None:
            raise HostCapabilityRequired(request)
        if not result.success:
            raise HostCapabilityFailed(request, result)
        return request, result

    def require(self, capability: str, payload: Mapping[str, Any]) -> Any:
        _, result = self.require_result(capability, payload)
        return result.output

    @staticmethod
    def invalid_result(
        request: CapabilityRequest,
        result: CapabilityResult,
        exc: Exception,
    ) -> HostCapabilityFailed:
        return HostCapabilityFailed(
            request,
            result,
            detail=f"invalid host result: {type(exc).__name__}: {exc}",
        )


class BrokerLLMProvider:
    def __init__(self, broker: CapabilityBroker) -> None:
        self._broker = broker

    def complete(self, request: LLMRequest) -> LLMResponse:
        capability_request, result = self._broker.require_result(
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
        try:
            output = result.output
            if isinstance(output, str):
                return LLMResponse(content=output, model_id="external-host")
            if not isinstance(output, Mapping):
                raise TypeError("LLM_COMPLETE output must be a string or object")
            if "content" not in output or not isinstance(output["content"], str):
                raise TypeError("LLM_COMPLETE.content must be a string")
            for optional in ("model_id", "response_id"):
                if output.get(optional) is not None and not isinstance(output[optional], str):
                    raise TypeError(f"LLM_COMPLETE.{optional} must be a string when provided")
            return LLMResponse(
                content=output["content"],
                model_id=output.get("model_id"),
                response_id=output.get("response_id"),
            )
        except Exception as exc:
            raise self._broker.invalid_result(capability_request, result, exc) from exc


class BrokerRetrievalProvider:
    def __init__(self, broker: CapabilityBroker) -> None:
        self._broker = broker

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        capability_request, result = self._broker.require_result(
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
        try:
            output = result.output
            if not isinstance(output, Mapping) or not isinstance(output.get("items"), list):
                raise TypeError("WEB_SEARCH output must be an object containing an items list")
            if limit < 0:
                raise ValueError("WEB_SEARCH limit must be non-negative")
            items: list[RetrievedItem] = []
            for index, raw in enumerate(output["items"][:limit]):
                if not isinstance(raw, Mapping):
                    raise TypeError("WEB_SEARCH item must be an object")
                source_uri = raw.get("source_uri")
                content = raw.get("content")
                if not isinstance(source_uri, str) or not source_uri.strip():
                    raise TypeError("WEB_SEARCH item.source_uri must be a non-empty string")
                if not isinstance(content, str) or not content.strip():
                    raise TypeError("WEB_SEARCH item.content must be a non-empty string")
                raw_item_id = raw.get("item_id")
                if raw_item_id is not None and (
                    not isinstance(raw_item_id, str) or not raw_item_id.strip()
                ):
                    raise TypeError("WEB_SEARCH item.item_id must be a non-empty string when provided")
                raw_domains = raw.get("domain_ids", ())
                if isinstance(raw_domains, (str, bytes)) or not isinstance(raw_domains, (tuple, list)):
                    raise TypeError("WEB_SEARCH item.domain_ids must be an array")
                if any(not isinstance(item, str) or not item.strip() for item in raw_domains):
                    raise TypeError("WEB_SEARCH item.domain_ids entries must be non-empty strings")
                stable_id = content_digest({"source_uri": source_uri, "content": content})[:24]
                item_id = raw_item_id or f"host-web:{query.query_id}:{index}:{stable_id}"
                items.append(
                    RetrievedItem(
                        item_id=item_id,
                        content=content,
                        source_uri=source_uri,
                        domain_ids=tuple(raw_domains),
                    )
                )
            return tuple(items)
        except Exception as exc:
            raise self._broker.invalid_result(capability_request, result, exc) from exc


class BrokerVerificationProvider:
    def __init__(self, broker: CapabilityBroker) -> None:
        self._broker = broker

    def verify(self, contribution, item: RetrievedItem) -> VerificationResult:
        capability_request, result = self._broker.require_result(
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
        try:
            output = result.output
            if not isinstance(output, Mapping):
                raise TypeError("VERIFY_EVIDENCE output must be an object")
            passed = output.get("passed", False)
            if not isinstance(passed, bool):
                raise TypeError("VERIFY_EVIDENCE.passed must be a boolean")
            raw_certificates = output.get("certificate_ids", ())
            if isinstance(raw_certificates, (str, bytes)) or not isinstance(
                raw_certificates, (tuple, list)
            ):
                raise TypeError("VERIFY_EVIDENCE.certificate_ids must be an array")
            certificates = tuple(raw_certificates)
            if any(not isinstance(value, str) or not value.strip() for value in certificates):
                raise TypeError(
                    "VERIFY_EVIDENCE.certificate_ids entries must be non-empty strings"
                )
            if passed and not certificates:
                raise ValueError("passing VERIFY_EVIDENCE result requires a certificate_id")
            reason = output.get("reason", "")
            if not isinstance(reason, str):
                raise TypeError("VERIFY_EVIDENCE.reason must be a string")
            return VerificationResult(
                passed=passed,
                certificate_ids=certificates,
                reason=reason,
            )
        except Exception as exc:
            raise self._broker.invalid_result(capability_request, result, exc) from exc
