from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from orion.core.contributions import AssimilationOutcome, KnowledgeContribution
from orion.core.search import RetrievedItem
from orion.providers.live_phase2 import (
    build_phase2_auto_provider_stack_from_env,
    build_phase2_copilot_provider_stack,
    write_live_phase2_provider_manifest,
)
from orion.providers.llm.base import LLMRequest
from orion.providers.llm.copilot_cli import CopilotCLIConfig, CopilotCLILLMProvider
from orion.providers.verification.copilot_cli import (
    CopilotCLIVerificationConfig,
    CopilotCLIVerificationProvider,
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


def _assert_isolated_command(command: list[str], env: dict[str, str], cwd: Path) -> None:
    assert command[0] == "copilot"
    assert "--no-ask-user" in command
    assert "--disable-builtin-mcps" in command
    for denied in (
        "--deny-tool=shell",
        "--deny-tool=write",
        "--deny-tool=read",
        "--deny-tool=url",
        "--deny-tool=memory",
    ):
        assert denied in command
    assert "--excluded-tools=task,skill,web_fetch,bash,edit,view,grep,glob" in command
    assert cwd.name == "work"
    assert list(cwd.iterdir()) == []
    assert set(env) == {
        "PATH",
        "HOME",
        "CI",
        "NO_COLOR",
        "COPILOT_AUTO_UPDATE",
        "COPILOT_GITHUB_TOKEN",
        "GITHUB_TOKEN",
    }
    assert env["COPILOT_GITHUB_TOKEN"] == "transport-secret"
    assert env["GITHUB_TOKEN"] == "transport-secret"


def test_copilot_reasoner_is_prompt_only_and_token_free(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, object] = {}

    def fake_run(command, *, cwd, env, capture_output, text, timeout, check):
        observed["command"] = command
        observed["env"] = env
        observed["cwd"] = cwd
        _assert_isolated_command(command, env, Path(cwd))
        assert "transport-secret" not in command[command.index("-p") + 1]
        return subprocess.CompletedProcess(command, 0, stdout='{"answer":"ok"}\n', stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    config = CopilotCLIConfig(
        model="gpt-5.2",
        token="transport-secret",
        cli_version="1.2.3",
    )
    response = CopilotCLILLMProvider(config).complete(
        LLMRequest(
            task="fixture",
            system="Return the requested object.",
            user="Answer the fixture.",
            response_schema='{"answer":"string"}',
        )
    )
    assert response.content == '{"answer":"ok"}'
    assert response.model_id == "gpt-5.2"
    assert response.response_id and response.response_id.startswith("copilot-cli-response:")
    assert "transport-secret" not in json.dumps(config.public_identity, sort_keys=True)


def test_copilot_verifier_binds_request_artifact_epoch_and_certificate(monkeypatch: pytest.MonkeyPatch) -> None:
    config = CopilotCLIVerificationConfig(
        model="claude-sonnet-4.6",
        token="transport-secret",
        cli_version="1.2.3",
        evaluation_epoch_id="epoch-1",
    )

    def fake_run(command, *, cwd, env, capture_output, text, timeout, check):
        _assert_isolated_command(command, env, Path(cwd))
        prompt = command[command.index("-p") + 1]
        assert "transport-secret" not in prompt
        bound = json.loads(prompt.split("FROZEN VERIFICATION REQUEST:\n", 1)[1])
        verdict = {
            "request_hash": bound["request_hash"],
            "evaluator_artifact_hash": bound["evaluator_artifact_hash"],
            "evaluation_epoch_id": bound["evaluation_epoch_id"],
            "passed": True,
            "reason": "retrieved item materially supports the contribution",
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(verdict), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = CopilotCLIVerificationProvider(config).verify(_contribution(), _item())
    assert result.passed is True
    assert len(result.certificate_ids) == 1
    assert result.certificate_ids[0].startswith("copilot-cli-verification:")
    assert config.evaluator_artifact_hash == evaluator_artifact_hash("claude-sonnet-4.6", "1.2.3")
    assert "transport-secret" not in json.dumps(config.public_identity, sort_keys=True)


def test_copilot_verifier_fails_closed_on_forged_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    config = CopilotCLIVerificationConfig(
        model="claude-sonnet-4.6",
        token="transport-secret",
        cli_version="1.2.3",
        evaluation_epoch_id="epoch-1",
    )

    def fake_run(command, *, cwd, env, capture_output, text, timeout, check):
        verdict = {
            "request_hash": "0" * 64,
            "evaluator_artifact_hash": config.evaluator_artifact_hash,
            "evaluation_epoch_id": config.evaluation_epoch_id,
            "passed": True,
            "reason": "forged binding",
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(verdict), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = CopilotCLIVerificationProvider(config).verify(_contribution(), _item())
    assert result.passed is False
    assert result.certificate_ids == ()
    assert result.reason == "copilot_cli_verifier_request_binding_mismatch"


def test_copilot_verifier_never_calls_model_for_unbound_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_run(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("external verifier should not be called")

    monkeypatch.setattr(subprocess, "run", fake_run)
    contribution = KnowledgeContribution(
        contribution_id="c2",
        text="claim",
        assimilation=AssimilationOutcome.COMPLEMENTARY_FACET,
        evidence_ids=("different-item",),
    )
    config = CopilotCLIVerificationConfig(
        model="claude-sonnet-4.6",
        token="transport-secret",
        cli_version="1.2.3",
        evaluation_epoch_id="epoch-1",
    )
    result = CopilotCLIVerificationProvider(config).verify(contribution, _item())
    assert result.passed is False
    assert result.reason == "contribution_does_not_bind_the_item_being_verified"
    assert called is False


def test_copilot_stack_requires_distinct_reasoner_and_evaluator_models() -> None:
    with pytest.raises(ValueError, match="must be distinct"):
        build_phase2_copilot_provider_stack(
            token="transport-secret",
            reasoner_model="gpt-5.2",
            evaluator_model="gpt-5.2",
            cli_version="1.2.3",
            evaluation_epoch_id="epoch-1",
        )


def test_copilot_provider_manifest_excludes_token(tmp_path: Path) -> None:
    stack = build_phase2_copilot_provider_stack(
        token="transport-secret",
        reasoner_model="gpt-5.2",
        evaluator_model="claude-sonnet-4.6",
        cli_version="1.2.3",
        evaluation_epoch_id="epoch-1",
    )
    path = tmp_path / "manifest.json"
    write_live_phase2_provider_manifest(stack, path)
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)
    assert "transport-secret" not in text
    assert payload["secret_material_included"] is False
    assert payload["reasoner_provider"]["provider"] == "github-copilot-cli"
    assert payload["verification_provider"]["provider"] == "github-copilot-cli-protected-verifier"
    assert payload["reasoner_provider"]["model"] == "gpt-5.2"
    assert payload["verification_provider"]["model"] == "claude-sonnet-4.6"


def test_auto_stack_uses_copilot_only_when_private_lane_fully_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "OPENAI_API_KEY",
        "ORION_PROTECTED_VERIFIER_URL",
        "ORION_PROTECTED_VERIFIER_TOKEN",
        "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
        "ORION_PHASE2_EVALUATION_EPOCH_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "transport-secret")
    monkeypatch.setenv("ORION_COPILOT_CLI_VERSION", "1.2.3")
    stack, mode = build_phase2_auto_provider_stack_from_env(
        private_reasoner_model="gpt-5.6",
        copilot_reasoner_model="gpt-5.2",
        copilot_evaluator_model="claude-sonnet-4.6",
        copilot_evaluation_epoch_id="github-actions-1-attempt-1",
    )
    assert mode == "github-copilot-cli-external"
    assert dict(stack.manifest.reasoner_provider)["model"] == "gpt-5.2"
    assert dict(stack.manifest.verification_provider)["model"] == "claude-sonnet-4.6"


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
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "transport-secret")
    monkeypatch.setenv("ORION_COPILOT_CLI_VERSION", "1.2.3")
    with pytest.raises(RuntimeError, match="partial private Phase-2 provider configuration is forbidden"):
        build_phase2_auto_provider_stack_from_env(
            private_reasoner_model="gpt-5.6",
            copilot_reasoner_model="gpt-5.2",
            copilot_evaluator_model="claude-sonnet-4.6",
            copilot_evaluation_epoch_id="github-actions-1-attempt-1",
        )
