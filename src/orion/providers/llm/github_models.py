from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from .base import LLMProvider, LLMRequest, LLMResponse


GitHubModelsTransport = Callable[[urllib.request.Request, float], bytes]
GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint is frozen/validated
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub Models HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"GitHub Models transport failed: {error.reason}") from error


@dataclass(frozen=True)
class GitHubModelsConfig:
    model: str
    token: str = field(repr=False)
    endpoint: str = GITHUB_MODELS_ENDPOINT
    timeout_seconds: float = 120.0

    def __post_init__(self) -> None:
        if not self.model.strip() or not self.token.strip():
            raise ValueError("GitHub Models model and token are required")
        if self.endpoint != GITHUB_MODELS_ENDPOINT:
            raise ValueError("GitHub Models endpoint is frozen to the official HTTPS inference endpoint")
        if self.timeout_seconds <= 0:
            raise ValueError("GitHub Models timeout must be positive")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "github-models-chat-completions",
            "endpoint": self.endpoint,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
        }


class GitHubModelsLLMProvider(LLMProvider):
    """GitHub Models adapter authenticated by an Actions/PAT token.

    The token is transport configuration only and never enters provider
    manifests or response artifacts. JSON contracts are prompt-level and are
    still validated by the ORION caller after parsing.
    """

    def __init__(
        self,
        config: GitHubModelsConfig,
        *,
        transport: GitHubModelsTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    @staticmethod
    def _user_text(request: LLMRequest) -> str:
        text = f"TASK: {request.task}\n\n{request.user}"
        if request.response_schema:
            try:
                schema = json.loads(request.response_schema)
            except json.JSONDecodeError as error:
                raise ValueError("LLMRequest response_schema must be valid JSON") from error
            if not isinstance(schema, dict):
                raise ValueError("LLMRequest response_schema must decode to a JSON object")
            text += (
                "\n\nOUTPUT CONTRACT: Return only valid JSON matching this contract. "
                "Do not wrap it in Markdown fences. CONTRACT: "
                + request.response_schema
            )
        return text

    @staticmethod
    def _content(raw: dict[str, object]) -> str:
        choices = raw.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("GitHub Models payload has no choices")
        first = choices[0]
        if not isinstance(first, dict):
            raise RuntimeError("GitHub Models first choice is not an object")
        message = first.get("message")
        if not isinstance(message, dict):
            raise RuntimeError("GitHub Models first choice has no message")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("GitHub Models response has no message content")
        return content

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": self._user_text(request)},
            ],
        }
        http_request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
                "User-Agent": "orion-research-os/0.1",
            },
            method="POST",
        )
        body = self._transport(http_request, self.config.timeout_seconds)
        try:
            raw = json.loads(body)
        except json.JSONDecodeError as error:
            raise RuntimeError("GitHub Models returned non-JSON content") from error
        if not isinstance(raw, dict):
            raise RuntimeError("GitHub Models returned a non-object JSON payload")
        return LLMResponse(
            content=self._content(raw),
            model_id=str(raw.get("model") or self.config.model),
            response_id=str(raw.get("id") or "") or None,
        )


__all__ = [
    "GITHUB_MODELS_ENDPOINT",
    "GitHubModelsConfig",
    "GitHubModelsLLMProvider",
    "GitHubModelsTransport",
]
