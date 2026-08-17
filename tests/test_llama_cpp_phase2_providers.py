from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

from orion.core.contributions import AssimilationOutcome, KnowledgeContribution
from orion.core.search import RetrievedItem
from orion.providers.llm.base import LLMRequest
from orion.providers.llm.llama_cpp_cli import (
    LlamaCppCLIConfig,
    LlamaCppCLILLMProvider,
    sha256_file,
)
from orion.providers.open_weight_phase2 import build_phase2_open_weight_provider_stack
from orion.providers.verification.llama_cpp_cli import (
    LlamaCppCLIVerificationConfig,
    LlamaCppCLIVerificationProvider,
    evaluator_artifact_hash,
)


RUNTIME_TAG = "b10218"
RUNTIME_COMMIT = "de699957b92f490efebad149665b0dccf127eaff"
ASSET_SHA = "a" * 64


def _files(tmp_path: Path) -> tuple[Path, Path, Path]:
    executable = tmp_path / "llama-cli"
    executable.write_bytes(b"llama-runtime-fixture")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    reasoner = tmp_path / "reasoner.gguf"
    evaluator = tmp_path / "evaluator.gguf"
    reasoner.write_bytes(b"qwen-reasoner-fixture")
    evaluator.write_bytes(b"smollm-evaluator-fixture")
    return executable, reasoner, evaluator


def _reasoner_config(executable: Path, model: Path) -> LlamaCppCLIConfig:
    return LlamaCppCLIConfig(
        executable=str(executable),
        executable_sha256=sha256_file(executable),
        runtime_release_tag=RUNTIME_TAG,
        runtime_commit=RUNTIME_COMMIT,
        runtime_asset_sha256=ASSET_SHA,
        model_path=str(model),
        model_sha256=sha256_file(model),
        model_repo_id="bartowski/Qwen2.5-1.5B-Instruct-GGUF",
        model_revision="0" * 40,
        model_filename="Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
        model_family="qwen2.5",
        max_tokens=64,
    )


def _verifier_config(executable: Path, model: Path) -> LlamaCppCLIVerificationConfig:
    return LlamaCppCLIVerificationConfig(
        executable=str(executable),
        executable_sha256=sha256_file(executable),
        runtime_release_tag=RUNTIME_TAG,
        runtime_commit=RUNTIME_COMMIT,
        runtime_asset_sha256=ASSET_SHA,
        model_path=str(model),
        model_sha256=sha256_file(model),
        model_repo_id="bartowski/SmolLM2-1.7B-Instruct-GGUF",
        model_revision="1" * 40,
        model_filename="SmolLM2-1.7B-Instruct-Q4_K_M.gguf",
        model_family="smollm2",
        evaluation_epoch_id="epoch-fixture",
        max_tokens=64,
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


def _assert_isolated(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    assert cwd.name == "work"
    assert list(cwd.iterdir()) == []
    assert set(env) == {"PATH", "HOME", "LC_ALL", "LANG", "NO_COLOR"}
    assert "-st" in command
    assert "--simple-io" in command
    assert "--no-warmup" in command
    assert "--no-display-prompt" in command
    assert "--no-show-timings" in command
    assert command[command.index("--temp") + 1] == "0"


def test_llama_reasoner_is_content_addressed_isolated_and_structured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable, reasoner, _ = _files(tmp_path)
    config = _reasoner_config(executable, reasoner)

    def fake_run(command, *, cwd, env, capture_output, text, timeout, check):
        _assert_isolated(command, Path(cwd), env)
        assert command[command.index("-m") + 1] == str(reasoner)
        assert "--json-schema" in command
        return subprocess.CompletedProcess(command, 0, stdout='{"answer":"ok"}\n', stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = LlamaCppCLILLMProvider(config).complete(
        LLMRequest(
            task="fixture",
            system="Return an answer.",
            user="Answer the fixture.",
            response_schema=json.dumps(
                {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["answer"],
                    "properties": {"answer": {"type": "string"}},
                }
            ),
        )
    )
    assert response.content == '{"answer":"ok"}'
    assert response.response_id and response.response_id.startswith("llama-cpp-response:")
    identity = config.public_identity
    assert identity["model_sha256"] == sha256_file(reasoner)
    assert identity["runtime_binary_sha256"] == sha256_file(executable)
    assert identity["tool_access"] == "NONE"


def test_llama_reasoner_keeps_historical_example_schema_as_prompt_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable, reasoner, _ = _files(tmp_path)
    config = _reasoner_config(executable, reasoner)

    def fake_run(command, *, cwd, env, capture_output, text, timeout, check):
        assert "--json-schema" not in command
        prompt = command[command.index("-p") + 1]
        assert "OUTPUT CONTRACT" in prompt
        return subprocess.CompletedProcess(command, 0, stdout='{"queries":["x"]}\n', stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = LlamaCppCLILLMProvider(config).complete(
        LLMRequest(
            task="search_plan",
            system="Return JSON.",
            user="Plan search.",
            response_schema='{"queries":["string"]}',
        )
    )
    assert json.loads(response.content) == {"queries": ["x"]}


def test_llama_reasoner_rejects_runtime_or_model_hash_mismatch(tmp_path: Path) -> None:
    executable, reasoner, _ = _files(tmp_path)
    with pytest.raises(ValueError, match="executable SHA-256 mismatch"):
        LlamaCppCLIConfig(
            executable=str(executable),
            executable_sha256="0" * 64,
            runtime_release_tag=RUNTIME_TAG,
            runtime_commit=RUNTIME_COMMIT,
            runtime_asset_sha256=ASSET_SHA,
            model_path=str(reasoner),
            model_sha256=sha256_file(reasoner),
            model_repo_id="repo",
            model_revision="rev",
            model_filename="model.gguf",
            model_family="family-a",
        )
    with pytest.raises(ValueError, match="model SHA-256 mismatch"):
        LlamaCppCLIConfig(
            executable=str(executable),
            executable_sha256=sha256_file(executable),
            runtime_release_tag=RUNTIME_TAG,
            runtime_commit=RUNTIME_COMMIT,
            runtime_asset_sha256=ASSET_SHA,
            model_path=str(reasoner),
            model_sha256="0" * 64,
            model_repo_id="repo",
            model_revision="rev",
            model_filename="model.gguf",
            model_family="family-a",
        )


def test_llama_verifier_binds_request_artifact_epoch_and_host_certificate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable, _, evaluator = _files(tmp_path)
    config = _verifier_config(executable, evaluator)

    def fake_run(command, *, cwd, env, capture_output, text, timeout, check):
        _assert_isolated(command, Path(cwd), env)
        assert "--json-schema" in command
        bound = json.loads(command[command.index("-p") + 1])
        verdict = {
            "request_hash": bound["request_hash"],
            "evaluator_artifact_hash": bound["evaluator_artifact_hash"],
            "evaluation_epoch_id": bound["evaluation_epoch_id"],
            "passed": True,
            "reason": "the retrieved item materially supports the contribution",
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(verdict), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = LlamaCppCLIVerificationProvider(config).verify(_contribution(), _item())
    assert result.passed is True
    assert len(result.certificate_ids) == 1
    assert result.certificate_ids[0].startswith("llama-cpp-verification:")
    assert config.evaluator_artifact_hash == evaluator_artifact_hash(
        runtime_release_tag=RUNTIME_TAG,
        runtime_commit=RUNTIME_COMMIT,
        runtime_asset_sha256=ASSET_SHA,
        runtime_binary_sha256=sha256_file(executable),
        model_repo_id=config.model_repo_id,
        model_revision=config.model_revision,
        model_filename=config.model_filename,
        model_sha256=sha256_file(evaluator),
        model_family=config.model_family,
    )


def test_llama_verifier_fails_closed_on_forged_request_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable, _, evaluator = _files(tmp_path)
    config = _verifier_config(executable, evaluator)

    def fake_run(command, *, cwd, env, capture_output, text, timeout, check):
        bound = json.loads(command[command.index("-p") + 1])
        verdict = {
            "request_hash": "0" * 64,
            "evaluator_artifact_hash": bound["evaluator_artifact_hash"],
            "evaluation_epoch_id": bound["evaluation_epoch_id"],
            "passed": True,
            "reason": "forged",
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(verdict), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = LlamaCppCLIVerificationProvider(config).verify(_contribution(), _item())
    assert result.passed is False
    assert result.certificate_ids == ()
    assert result.reason == "llama_cpp_verifier_request_binding_mismatch"


def test_open_weight_stack_requires_distinct_hashes_and_families(tmp_path: Path) -> None:
    executable, reasoner, evaluator = _files(tmp_path)
    common = dict(
        llama_cli_path=str(executable),
        llama_cli_sha256=sha256_file(executable),
        llama_runtime_release_tag=RUNTIME_TAG,
        llama_runtime_commit=RUNTIME_COMMIT,
        llama_runtime_asset_sha256=ASSET_SHA,
        reasoner_model_path=str(reasoner),
        reasoner_model_sha256=sha256_file(reasoner),
        reasoner_model_repo_id="reasoner/repo",
        reasoner_model_revision="r1",
        reasoner_model_filename="reasoner.gguf",
        reasoner_model_family="qwen2.5",
        evaluator_model_path=str(evaluator),
        evaluator_model_sha256=sha256_file(evaluator),
        evaluator_model_repo_id="evaluator/repo",
        evaluator_model_revision="e1",
        evaluator_model_filename="evaluator.gguf",
        evaluator_model_family="smollm2",
        evaluation_epoch_id="epoch-1",
    )
    stack = build_phase2_open_weight_provider_stack(**common)
    assert dict(stack.manifest.reasoner_provider)["model_family"] == "qwen2.5"
    assert dict(stack.manifest.verification_provider)["model_family"] == "smollm2"

    same_family = {**common, "evaluator_model_family": "qwen2.5"}
    with pytest.raises(ValueError, match="model families must be distinct"):
        build_phase2_open_weight_provider_stack(**same_family)

    same_hash = {**common, "evaluator_model_sha256": sha256_file(reasoner), "evaluator_model_path": str(reasoner)}
    with pytest.raises(ValueError, match="model hashes must be distinct"):
        build_phase2_open_weight_provider_stack(**same_hash)
