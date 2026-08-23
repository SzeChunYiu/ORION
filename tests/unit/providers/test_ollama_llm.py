import json
import urllib.request

import pytest

from orion.providers.llm.base import LLMRequest
from orion.providers.llm.ollama import OllamaConfig, OllamaLLMProvider


def _transport(payload):
    def transport(request: urllib.request.Request, timeout: float) -> bytes:
        assert timeout == 300.0
        sent = json.loads(request.data)
        payload["sent"] = sent
        return json.dumps(
            {
                "model": "qwen3:0.6b",
                "created_at": "2026-08-16T15:00:00Z",
                "message": {"role": "assistant", "content": '{"ok":true}'},
                "done": True,
            }
        ).encode()

    return transport


def test_ollama_formal_schema_is_sent_as_native_format():
    captured = {}
    provider = OllamaLLMProvider(
        OllamaConfig("qwen3:0.6b"), transport=_transport(captured)
    )
    schema = {
        "type": "object",
        "required": ["ok"],
        "properties": {"ok": {"type": "boolean"}},
    }
    response = provider.complete(
        LLMRequest(
            task="diagnostic",
            system="system",
            user="user",
            response_schema=json.dumps(schema),
        )
    )
    assert json.loads(response.content) == {"ok": True}
    assert captured["sent"]["format"] == schema
    assert captured["sent"]["think"] is False
    assert response.model_id == "qwen3:0.6b"
    assert response.response_id.startswith("ollama:")


def test_ollama_legacy_example_contract_uses_json_mode_and_prompt_contract():
    captured = {}
    provider = OllamaLLMProvider(
        OllamaConfig("qwen3:0.6b"), transport=_transport(captured)
    )
    provider.complete(
        LLMRequest(
            task="legacy",
            system="system",
            user="answer",
            response_schema='{"answer":"string"}',
        )
    )
    assert captured["sent"]["format"] == "json"
    assert "OUTPUT CONTRACT" in captured["sent"]["messages"][1]["content"]


def test_ollama_rejects_non_loopback_endpoint():
    with pytest.raises(ValueError, match="loopback"):
        OllamaConfig("qwen3:0.6b", endpoint="http://example.com/api/chat")


def test_ollama_rejects_incomplete_response():
    def transport(request, timeout):
        return json.dumps(
            {"model": "qwen3:0.6b", "message": {"content": "x"}, "done": False}
        ).encode()

    provider = OllamaLLMProvider(OllamaConfig("qwen3:0.6b"), transport=transport)
    with pytest.raises(RuntimeError, match="incomplete"):
        provider.complete(LLMRequest("diagnostic", "system", "user"))
