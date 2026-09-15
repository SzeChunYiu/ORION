"""Anthropic Messages API provider (no SDK dependency).

Adapter for the Anthropic Messages endpoint (``/v1/messages``) using only the
standard library, mirroring ``OpenAIResponsesLLMProvider``. Supports a proxy
base URL (``ANTHROPIC_BASE_URL``) and bearer token (``ANTHROPIC_AUTH_TOKEN``
/ ``ANTHROPIC_API_KEY``); this is the transport used for the frozen P3
evaluation model family.

Structured output is enforced at the prompt level with a JSON Schema contract
appended to the system prompt, then validated by the caller.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from .base import LLMProvider, LLMRequest, LLMResponse


MessagesTransport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint is validated HTTPS
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Anthropic Messages HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Anthropic Messages transport failed: {error.reason}") from error


@dataclass(frozen=True)
class AnthropicMessagesConfig:
    model: str
    api_key: str = field(repr=False)
    endpoint: str = "https://api.anthropic.com/v1/messages"
    base_url: str = "https://api.anthropic.com"
    timeout_seconds: float = 300.0
    max_tokens: int = 8192

    def __post_init__(self) -> None:
        if not self.model.strip() or not self.api_key.strip():
            raise ValueError("Anthropic model and API key are required")
        if not self.endpoint.startswith("https://"):
            raise ValueError("Anthropic Messages endpoint must be HTTPS")
        if self.timeout_seconds <= 0:
            raise ValueError("Anthropic request timeout must be positive")
        if self.max_tokens <= 0:
            raise ValueError("Anthropic max_tokens must be positive")

    @classmethod
    def from_env(
        cls,
        *,
        model: str,
        api_key_env: str = "ANTHROPIC_API_KEY",
        auth_token_env: str = "ANTHROPIC_AUTH_TOKEN",
        base_url_env: str = "ANTHROPIC_BASE_URL",
        timeout_seconds: float = 300.0,
        max_tokens: int = 8192,
    ) -> AnthropicMessagesConfig:
        api_key = os.environ.get(api_key_env, "") or os.environ.get(auth_token_env, "")
        if not api_key:
            raise RuntimeError(
                f"required Anthropic API key environment variable is missing: {api_key_env}"
            )
        base_url = os.environ.get(base_url_env, "").rstrip("/") or "https://api.anthropic.com"
        endpoint = f"{base_url}/v1/messages"
        return cls(
            model=model,
            api_key=api_key,
            endpoint=endpoint,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
        )

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "anthropic-messages",
            "endpoint": self.endpoint,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "max_tokens": self.max_tokens,
        }


class AnthropicMessagesLLMProvider(LLMProvider):
    """Anthropic Messages API adapter via stdlib urllib (proxy-capable)."""

    def __init__(
        self,
        config: AnthropicMessagesConfig,
        *,
        transport: MessagesTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    @staticmethod
    def _output_text(raw: dict[str, object]) -> str:
        content = raw.get("content")
        if not isinstance(content, list):
            raise RuntimeError("Anthropic Messages payload has no content array")
        chunks: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text":
                text = item.get("text")
                if isinstance(text, str) and text:
                    chunks.append(text)
            elif item.get("type") in {"tool_use", "thinking", "redacted_thinking"}:
                # Non-text content; ignored for plain completions.
                continue
        if not chunks:
            stop = raw.get("stop_reason")
            raise RuntimeError(
                f"Anthropic Messages payload contains no text content (stop_reason={stop})"
            )
        return "\n".join(chunks)

    @staticmethod
    def _system_for(request: LLMRequest) -> str:
        contract = ""
        if request.response_schema:
            contract = (
                "\n\nOUTPUT CONTRACT: Return ONLY valid JSON conforming exactly to this "
                "JSON Schema. Do not include markdown fences, prose, or keys outside "
                "the schema:\n" + request.response_schema
            )
        if request.system and contract:
            return request.system + contract
        return request.system + contract  # one of them is non-empty

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, object] = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "system": self._system_for(request),
            "messages": [
                {
                    "role": "user",
                    "content": f"TASK: {request.task}\n\n{request.user}",
                }
            ],
        }
        encoded = json.dumps(payload).encode("utf-8")
        http_request = urllib.request.Request(
            self.config.endpoint,
            data=encoded,
            headers={
                "x-api-key": self.config.api_key,
                "Authorization": f"Bearer {self.config.api_key}",
                "anthropic-version": "2023-06-01",
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
            raise RuntimeError("Anthropic Messages returned non-JSON content") from error
        if not isinstance(raw, dict):
            raise RuntimeError("Anthropic Messages returned a non-object JSON payload")
        if raw.get("type") == "error" or "error" in raw:
            raise RuntimeError(f"Anthropic Messages error: {raw.get('error')} ({body[:500]})")
        content = self._output_text(raw)
        # Some proxies report the effective model; otherwise use configured model.
        model_id = str(raw.get("model") or self.config.model)
        response_id = str(raw.get("id") or "") or None
        return LLMResponse(content=content, model_id=model_id, response_id=response_id)


__all__ = [
    "AnthropicMessagesConfig",
    "AnthropicMessagesLLMProvider",
    "MessagesTransport",
]