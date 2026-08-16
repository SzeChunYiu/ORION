import json

import pytest

from orion.providers.llm.base import LLMRequest, LLMResponse
from orion.providers.llm.openai_responses import (
    OpenAIResponsesConfig,
    OpenAIResponsesLLMProvider,
)


def _completed(text='{"answer":"ok"}'):
    return json.dumps(
        {
            "id": "resp_test",
            "model": "gpt-test",
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": text}],
                }
            ],
        }
    ).encode()


def test_openai_responses_adapter_uses_official_endpoint_structured_output_and_excludes_secret():
    captured = {}

    def transport(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["payload"] = json.loads(request.data)
        captured["timeout"] = timeout
        return _completed()

    config = OpenAIResponsesConfig(model="gpt-test", api_key="secret-key", timeout_seconds=9)
    provider = OpenAIResponsesLLMProvider(config, transport=transport)
    response = provider.complete(
        LLMRequest(
            task="test",
            system="system rule",
            user="user question",
            response_schema=(
                '{"type":"object","required":["answer"],'
                '"properties":{"answer":{"type":"string"}},"additionalProperties":false}'
            ),
        )
    )

    assert response == LLMResponse('{"answer":"ok"}', "gpt-test", "resp_test")
    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["payload"]["model"] == "gpt-test"
    assert captured["payload"]["instructions"] == "system rule"
    assert captured["payload"]["store"] is False
    assert captured["payload"]["input"] == "TASK: test\n\nuser question"
    format_spec = captured["payload"]["text"]["format"]
    assert format_spec["type"] == "json_schema"
    assert format_spec["strict"] is True
    assert format_spec["schema"]["required"] == ["answer"]
    assert captured["timeout"] == 9
    assert "secret-key" not in repr(config.public_identity)
    assert "api_key" not in config.public_identity


def test_existing_reasoner_example_shape_remains_prompt_contract_not_invalid_json_schema():
    captured = {}

    def transport(request, timeout):
        captured["payload"] = json.loads(request.data)
        return _completed('{"summary":"ok"}')

    provider = OpenAIResponsesLLMProvider(
        OpenAIResponsesConfig(model="gpt-test", api_key="secret"),
        transport=transport,
    )
    response = provider.complete(
        LLMRequest(
            "reconstruct",
            "system",
            "payload",
            response_schema='{"summary":"..."}',
        )
    )
    assert response.content == '{"summary":"ok"}'
    assert "text" not in captured["payload"]
    assert "OUTPUT CONTRACT" in captured["payload"]["input"]
    assert '{"summary":"..."}' in captured["payload"]["input"]


def test_openai_responses_adapter_fails_closed_without_output_text_or_on_refusal():
    provider = OpenAIResponsesLLMProvider(
        OpenAIResponsesConfig(model="gpt-test", api_key="secret"),
        transport=lambda request, timeout: json.dumps(
            {"id": "x", "status": "completed", "output": []}
        ).encode(),
    )
    with pytest.raises(RuntimeError, match="no output_text"):
        provider.complete(LLMRequest("t", "s", "u"))

    refusing = OpenAIResponsesLLMProvider(
        OpenAIResponsesConfig(model="gpt-test", api_key="secret"),
        transport=lambda request, timeout: json.dumps(
            {
                "id": "x",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "refusal", "refusal": "cannot comply"}],
                    }
                ],
            }
        ).encode(),
    )
    with pytest.raises(RuntimeError, match="refusal"):
        refusing.complete(LLMRequest("t", "s", "u"))


def test_openai_adapter_rejects_invalid_response_schema_before_transport():
    calls = []
    provider = OpenAIResponsesLLMProvider(
        OpenAIResponsesConfig(model="gpt-test", api_key="secret"),
        transport=lambda request, timeout: calls.append(request) or b"{}",
    )
    with pytest.raises(ValueError, match="valid JSON"):
        provider.complete(LLMRequest("t", "s", "u", response_schema="not-json"))
    assert calls == []


def test_openai_config_rejects_nonofficial_endpoint():
    with pytest.raises(ValueError, match="official HTTPS endpoint"):
        OpenAIResponsesConfig(
            model="gpt-test",
            api_key="secret",
            endpoint="https://example.test/responses",
        )
