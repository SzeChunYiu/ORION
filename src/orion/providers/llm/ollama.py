from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

from .base import LLMRequest, LLMResponse


OllamaTransport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint is loopback-only
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Ollama transport failed: {error.reason}") from error


@dataclass(frozen=True)
class OllamaConfig:
    model: str
    endpoint: str = "http://127.0.0.1:11434/api/chat"
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("Ollama model is required")
        if self.endpoint not in {
            "http://127.0.0.1:11434/api/chat",
            "http://localhost:11434/api/chat",
        }:
            raise ValueError("Ollama diagnostic endpoint must be the local loopback API")
        if self.timeout_seconds <= 0:
            raise ValueError("Ollama timeout must be positive")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "ollama-loopback-chat",
            "endpoint": self.endpoint,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "authority_role": "semantic-reasoner-only",
        }


class OllamaLLMProvider:
    """Credential-free local diagnostic reasoner; never an authority provider."""

    def __init__(
        self,
        config: OllamaConfig,
        *,
        transport: OllamaTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    @staticmethod
    def _schema_contract(request: LLMRequest) -> tuple[object | None, str]:
        if not request.response_schema:
            return None, request.user
        try:
            schema = json.loads(request.response_schema)
        except json.JSONDecodeError as error:
            raise ValueError("LLMRequest response_schema must be valid JSON") from error
        if not isinstance(schema, dict):
            raise ValueError("LLMRequest response_schema must decode to a JSON object")
        if "type" in schema:
            return schema, request.user
        return (
            "json",
            request.user
            + "\n\nOUTPUT CONTRACT: Return only JSON matching this example shape exactly: "
            + request.response_schema,
        )

    def complete(self, request: LLMRequest) -> LLMResponse:
        response_format, user_prompt = self._schema_contract(request)
        payload: dict[str, object] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
        }
        if response_format is not None:
            payload["format"] = response_format
        http_request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps(payload, separators=(",", ":")).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "orion-research-os/0.1",
            },
            method="POST",
        )
        raw = json.loads(self._transport(http_request, self.config.timeout_seconds))
        if not isinstance(raw, dict) or raw.get("done") is not True:
            raise RuntimeError("Ollama response is incomplete")
        message = raw.get("message")
        if not isinstance(message, dict):
            raise RuntimeError("Ollama response has no message object")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama response has no assistant content")
        response_identity = hashlib.sha256(
            json.dumps(
                {
                    "model": raw.get("model", self.config.model),
                    "created_at": raw.get("created_at", ""),
                    "content": content,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        return LLMResponse(
            content=content,
            model_id=str(raw.get("model") or self.config.model),
            response_id=f"ollama:{response_identity}",
        )


__all__ = ["OllamaConfig", "OllamaLLMProvider", "OllamaTransport"]
