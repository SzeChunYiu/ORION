from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from .base import LLMProvider, LLMRequest, LLMResponse


OpenAITransport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint is frozen/validated
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI Responses HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"OpenAI Responses transport failed: {error.reason}") from error


@dataclass(frozen=True)
class OpenAIResponsesConfig:
    model: str
    api_key: str = field(repr=False)
    endpoint: str = "https://api.openai.com/v1/responses"
    timeout_seconds: float = 120.0
    store: bool = False

    def __post_init__(self) -> None:
        if not self.model.strip() or not self.api_key.strip():
            raise ValueError("OpenAI model and API key are required")
        if self.endpoint != "https://api.openai.com/v1/responses":
            raise ValueError("OpenAI Responses provider endpoint is frozen to the official HTTPS endpoint")
        if self.timeout_seconds <= 0:
            raise ValueError("OpenAI request timeout must be positive")

    @classmethod
    def from_env(
        cls,
        *,
        model: str,
        api_key_env: str = "OPENAI_API_KEY",
        timeout_seconds: float = 120.0,
        store: bool = False,
    ) -> OpenAIResponsesConfig:
        api_key = os.environ.get(api_key_env, "")
        if not api_key:
            raise RuntimeError(f"required OpenAI API key environment variable is missing: {api_key_env}")
        return cls(model=model, api_key=api_key, timeout_seconds=timeout_seconds, store=store)

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "openai-responses",
            "endpoint": self.endpoint,
            "model": self.model,
            "store": self.store,
            "timeout_seconds": self.timeout_seconds,
        }


class OpenAIResponsesLLMProvider(LLMProvider):
    """Concrete OpenAI Responses API adapter with no SDK dependency.

    API credentials are transport configuration only and never enter response
    artifacts/provider manifests. Formal JSON Schema contracts use Responses
    structured outputs. Historical ORION contracts that are example JSON shapes
    remain prompt-level contracts for backward compatibility.
    """

    def __init__(
        self,
        config: OpenAIResponsesConfig,
        *,
        transport: OpenAITransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    @staticmethod
    def _output_text(raw: dict[str, object]) -> str:
        output = raw.get("output")
        if not isinstance(output, list):
            raise RuntimeError("OpenAI Responses payload has no output array")
        chunks: list[str] = []
        for item in output:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "refusal":
                    raise RuntimeError(f"OpenAI Responses refusal: {part.get('refusal')}")
                if part.get("type") != "output_text":
                    continue
                text = part.get("text")
                if isinstance(text, str) and text:
                    chunks.append(text)
        if not chunks:
            raise RuntimeError("OpenAI Responses payload contains no output_text content")
        return "\n".join(chunks)

    @staticmethod
    def _schema_contract(request: LLMRequest) -> tuple[dict[str, object] | None, str]:
        if not request.response_schema:
            return None, request.user
        try:
            schema = json.loads(request.response_schema)
        except json.JSONDecodeError as error:
            raise ValueError("LLMRequest response_schema must be valid JSON") from error
        if not isinstance(schema, dict):
            raise ValueError("LLMRequest response_schema must decode to a JSON object")
        if "type" not in schema:
            return (
                None,
                request.user
                + "\n\nOUTPUT CONTRACT: Return only JSON matching this example shape exactly: "
                + request.response_schema,
            )
        name_digest = hashlib.sha256(
            f"{request.task}\n{request.response_schema}".encode()
        ).hexdigest()[:16]
        return (
            {
                "type": "json_schema",
                "name": f"orion_{name_digest}",
                "schema": schema,
                # OpenAI strict structured output requires the supported strict
                # JSON-schema subset; use strict only when the caller has made
                # object closure explicit. ORION still validates parsed output.
                "strict": schema.get("additionalProperties") is False,
            },
            request.user,
        )

    def complete(self, request: LLMRequest) -> LLMResponse:
        structured, user = self._schema_contract(request)
        payload: dict[str, object] = {
            "model": self.config.model,
            "instructions": request.system,
            "input": f"TASK: {request.task}\n\n{user}",
            "store": self.config.store,
        }
        if structured is not None:
            payload["text"] = {"format": structured}
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        http_request = urllib.request.Request(
            self.config.endpoint,
            data=encoded,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "orion-research-os/0.1",
            },
            method="POST",
        )
        body = self._transport(http_request, self.config.timeout_seconds)
        try:
            raw = json.loads(body)
        except json.JSONDecodeError as error:
            raise RuntimeError("OpenAI Responses returned non-JSON content") from error
        if not isinstance(raw, dict):
            raise RuntimeError("OpenAI Responses returned a non-object JSON payload")
        if raw.get("status") in {"failed", "cancelled", "incomplete"}:
            raise RuntimeError(
                "OpenAI Responses did not complete successfully: "
                + str(raw.get("error") or raw.get("incomplete_details") or raw.get("status"))
            )
        return LLMResponse(
            content=self._output_text(raw),
            model_id=str(raw.get("model") or self.config.model),
            response_id=str(raw.get("id") or "") or None,
        )


__all__ = ["OpenAIResponsesConfig", "OpenAIResponsesLLMProvider", "OpenAITransport"]
