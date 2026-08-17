from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request

import pytest

from orion.core.contributions import AssimilationOutcome, KnowledgeContribution
from orion.core.search import RetrievedItem
from orion.providers.live_phase2 import (
    build_phase2_auto_provider_stack_from_env,
    build_phase2_github_models_provider_stack,
    write_live_phase2_provider_manifest,
)
from orion.providers.llm.base import LLMRequest
from orion.providers.llm.github_models import GitHubModelsConfig, GitHubModelsLLMProvider
from orion.providers.verification.github_models import (
    GitHubModelsVerificationConfig,
    GitHubModelsVerificationProvider,
    evaluator_artifact_hash,
)


def _contribution() -> KnowledgeContribution:
    return KnowledgeContribution(
        contribution_id="c1",
        text="The intervention increased the measured response.",
        assimilation=AssimilationOutcome.COMPLEMENTARY_FACET,
        evidence_ids=("item-1",),
    )


def _item() -> RetrievedItem:
    return RetrievedItem(
        item_id="item-1",
        content="The intervention increased the measured response by 18 percent relative to control.",
        source_uri="https://example.test/paper",
        domain_ids=("domain:test",),
    )


def test_github_models_llm_provider_is_secret_free_and_parses_response() -> None:
    observed: dict[str, object] = {}

    def transport(request: Request, timeout: float) -> bytes:
        observed["authorization"] = request.headers.get("Authorization")
        observed["timeout"] = timeout
        payload = json.loads(request.data or b"{}")
        observed["payload"] = payload
        return json.dumps(
            {
                "id": "ghm-response-1",
                "model": "openai/gpt-5",
                "choices": [{"message": {"role": "assistant", "content": '{"answer":"ok"}'}}],
            }
        ).encode()

    config = GitHubModelsConfig(model="openai/gpt-5", token="transport-secret")
    provider = GitHubModelsLLMProvider(config, transport=transport)
    response = provider.complete(
        LLMRequest(
            task="fixture",
            system="Return the requested object.",
            user="Answer the fixture.",
            response_schema='{"answer":"string"}',
        )
    )

    assert response.content == '{"answer":"ok"}'
    assert response.model_id == "openai/gpt-5"
    assert response.response_id == "ghm-response-1"
    assert observed["authorization"] == "Bearer transport-secret"
    assert config.public_identity["provider"] == "github-models-chat-completions"
    assert "transport-secret" not in json.dumps(config.public_identity, sort_keys=True)
    payload = observed["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "openai/gpt-5"
    assert "OUTPUT CONTRACT" in payload["messages"][1]["content"]


def test_github_models_verifier_binds_request_artifact_epoch_and_certificate() -> None:
    config = GitHubModelsVerificationConfig(
        model="openai/gpt-4.1",
        token="evaluator-secret",
        evaluation_epoch_id="epoch-1",
    )

    def transport(request: Request, timeout: float) -> bytes:
        assert request.headers.get("Authorization") == "Bearer evaluator-secret"
        chat = json.loads(request.data or b"{}")
        user = chat["messages"][1]["content"]
        bound = json.loads(user.split("\n", 1)[1])
        verdict = {
            "request_hash": bound["request_hash"],
            "evaluator_artifact_hash": bound["evaluator_artifact_hash"],
            "evaluation_epoch_id": bound["evaluation_epoch_id"],
            "passed": True,
            "reason": "retrieved item materially supports the contribution",
        }
        return json.dumps(
            {
                "id": "eval-response-1",
                "model": "openai/gpt-4.1",
                "choices": [{"message": {"role": "assistant", "content": json.dumps(verdict)}}],
            }
        ).encode()

    provider = GitHubModelsVerificationProvider(config, transport=transport)
    result = provider.verify(_contribution(), _item())

    assert result.passed is True
    assert result.reason
    assert len(result.certificate_ids) == 1
    assert result.certificate_ids[0].startswith("github-models-verification:")
    assert config.evaluator_artifact_hash == evaluator_artifact_hash("openai/gpt-4.1")
    assert "evaluator-secret" not in json.dumps(config.public_identity, sort_keys=True)


def test_github_models_verifier_fails_closed_on_binding_mismatch() -> None:
    config = GitHubModelsVerificationConfig(
        model="openai/gpt-4.1",
        token="secret",
        evaluation_epoch_id="epoch-1",
    )

    def transport(request: Request, timeout: float) -> bytes:
        verdict = {
            "request_hash": "0" * 64,
            "evaluator_artifact_hash": config.evaluator_artifact_hash,
            "evaluation_epoch_id": config.evaluation_epoch_id,
            "passed": True,
            "reason": "forged binding",
        }
        return json.dumps(
            {
                "id": "eval-response-forged",
                "model": config.model,
                "choices": [{"message": {"role": "assistant", "content": json.dumps(verdict)}}],
            }
        ).encode()

    result = GitHubModelsVerificationProvider(config, transport=transport).verify(
        _contribution(), _item()
    )
    assert result.passed is False
    assert result.certificate_ids == ()
    assert result.reason == "github_models_verifier_request_binding_mismatch"


def test_github_models_verifier_does_not_call_external_model_for_unbound_item() -> None:
    called = False

    def transport(request: Request, timeout: float) -> bytes:
        nonlocal called
        called = True
        return b"{}"

    contribution = KnowledgeContribution(
        contribution_id="c2",
        text="claim",
        assimilation=AssimilationOutcome.COMPLEMENTARY_FACET,
        evidence_ids=("other-item",),
    )
    config = GitHubModelsVerificationConfig(
        model="openai/gpt-4.1",
        token="secret",
        evaluation_epoch_id="epoch-1",
    )
    result = GitHubModelsVerificationProvider(config, transport=transport).verify(
        contribution, _item()
    )
    assert result.passed is False
    assert result.reason == "contribution_does_not_bind_the_item_being_verified"
    assert called is False


def test_github_models_phase2_stack_manifest_contains_no_token(tmp_path: Path) -> None:
    stack = build_phase2_github_models_provider_stack(
        github_token="github-actions-token",
        reasoner_model="openai/gpt-5",
        evaluator_model="openai/gpt-4.1",
        evaluation_epoch_id="epoch-1",
    )
    path = tmp_path / "manifest.json"
    write_live_phase2_provider_manifest(stack, path)
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)
    assert "github-actions-token" not in text
    assert payload["secret_material_included"] is False
    assert payload["reasoner_provider"]["provider"] == "github-models-chat-completions"
    assert payload["verification_provider"]["provider"] == "github-models-protected-verifier"
    assert payload["verification_provider"]["evaluator_artifact_hash"] == evaluator_artifact_hash(
        "openai/gpt-4.1"
    )


def test_auto_stack_uses_github_models_only_when_private_lane_is_fully_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "OPENAI_API_KEY",
        "ORION_PROTECTED_VERIFIER_URL",
        "ORION_PROTECTED_VERIFIER_TOKEN",
        "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
        "ORION_PHASE2_EVALUATION_EPOCH_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GITHUB_MODELS_TOKEN", "actions-token")

    stack, mode = build_phase2_auto_provider_stack_from_env(
        private_reasoner_model="gpt-5.6",
        github_reasoner_model="openai/gpt-5",
        github_evaluator_model="openai/gpt-4.1",
        github_evaluation_epoch_id="github-actions-1-attempt-1",
    )
    assert mode == "github-models-external"
    assert dict(stack.manifest.reasoner_provider)["model"] == "openai/gpt-5"
    assert dict(stack.manifest.verification_provider)["model"] == "openai/gpt-4.1"


def test_auto_stack_rejects_partial_private_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "OPENAI_API_KEY",
        "ORION_PROTECTED_VERIFIER_URL",
        "ORION_PROTECTED_VERIFIER_TOKEN",
        "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
        "ORION_PHASE2_EVALUATION_EPOCH_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "partial-secret")
    monkeypatch.setenv("GITHUB_MODELS_TOKEN", "actions-token")

    with pytest.raises(RuntimeError, match="partial private Phase-2 provider configuration is forbidden"):
        build_phase2_auto_provider_stack_from_env(
            private_reasoner_model="gpt-5.6",
            github_reasoner_model="openai/gpt-5",
            github_evaluator_model="openai/gpt-4.1",
            github_evaluation_epoch_id="github-actions-1-attempt-1",
        )
