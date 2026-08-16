import json

import pytest

from orion.providers.live_phase2 import build_phase2_live_provider_stack
from orion.self_orion.live_shadow_development import (
    build_live_shadow_development_stack,
    build_live_shadow_development_stack_from_env,
    write_shadow_development_service_manifest,
)


SANDBOX_HASH = "a" * 64


def _providers():
    return build_phase2_live_provider_stack(
        reasoner_api_key="reasoner-secret",
        reasoner_model="gpt-reasoner-test",
        protected_verifier_endpoint="https://verifier.example.test/v1/verify",
        protected_verifier_token="runtime-verifier-secret",
        evaluator_artifact_hash="e" * 64,
        evaluation_epoch_id="epoch:frozen",
    )


def test_live_shadow_development_stack_is_frozen_and_secret_free(tmp_path):
    stack = build_live_shadow_development_stack(
        provider_stack=_providers(),
        artifact_root=tmp_path / "artifacts",
        sandbox_endpoint="https://sandbox.example.test/v1/execute",
        sandbox_token="sandbox-secret",
        sandbox_artifact_hash=SANDBOX_HASH,
        development_evaluator_endpoint="https://development-evaluator.example.test/v1/evaluate",
        development_evaluator_token="development-secret",
        base_revision="git-commit:base",
        producer_process_lineage_hash="f" * 64,
    )

    assert len(stack.service_manifest_hash) == 64
    assert stack.artifact_store.root == (tmp_path / "artifacts").resolve()
    assert stack.sandbox_executor.config.sandbox_artifact_hash == SANDBOX_HASH
    assert stack.assurance_evaluator.config.evaluator_artifact_hash == "e" * 64
    assert stack.assurance_evaluator.config.evaluation_epoch_id == "epoch:frozen"
    rendered = json.dumps(stack.manifest.payload)
    assert "reasoner-secret" not in rendered
    assert "runtime-verifier-secret" not in rendered
    assert "sandbox-secret" not in rendered
    assert "development-secret" not in rendered
    assert "protected-http-sandbox" in rendered
    assert "protected-development-http-evaluator" in rendered

    path = tmp_path / "development-services.json"
    write_shadow_development_service_manifest(stack, path)
    raw = json.loads(path.read_text())
    assert raw["service_manifest_hash"] == stack.service_manifest_hash
    assert not raw["secret_material_included"]


def test_env_builder_requires_all_protected_development_services(monkeypatch, tmp_path):
    for name in (
        "ORION_PROTECTED_SANDBOX_URL",
        "ORION_PROTECTED_SANDBOX_TOKEN",
        "ORION_PROTECTED_SANDBOX_ARTIFACT_HASH",
        "ORION_PROTECTED_DEVELOPMENT_EVALUATOR_URL",
        "ORION_PROTECTED_DEVELOPMENT_EVALUATOR_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError, match="ORION_PROTECTED_SANDBOX_URL"):
        build_live_shadow_development_stack_from_env(
            provider_stack=_providers(),
            artifact_root=tmp_path / "artifacts",
            base_revision="commit",
        )
