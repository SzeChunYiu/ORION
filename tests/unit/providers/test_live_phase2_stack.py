import json

import pytest

from orion.core.search import SearchQuery, SearchRouteKind
from orion.providers.experience.memory import InMemoryExperienceStore
from orion.providers.live_phase2 import (
    PROVIDER_MANIFEST_SCHEMA,
    build_phase2_live_provider_stack,
    build_phase2_live_provider_stack_from_env,
    write_live_phase2_provider_manifest,
)
from orion.self_orion.live_accounted import (
    AccountedShadowLiveTrialRunner,
    AttemptRecordingRetrievalProvider,
)
from orion.self_orion.live_campaign_factory import build_live_phase2_trial_harness


def test_live_phase2_provider_manifest_is_content_addressed_and_contains_no_secrets(tmp_path):
    stack = build_phase2_live_provider_stack(
        reasoner_api_key="reasoner-secret",
        reasoner_model="gpt-reasoner-test",
        protected_verifier_endpoint="https://verifier.example.test/v1/verify",
        protected_verifier_token="verifier-secret",
        evaluator_artifact_hash="b" * 64,
        evaluation_epoch_id="epoch:frozen",
        crossref_mailto="research@example.test",
    )

    assert len(stack.provider_manifest_hash) == 64
    assert stack.manifest.payload["schema"] == PROVIDER_MANIFEST_SCHEMA
    assert not stack.manifest.payload["secret_material_included"]
    rendered = json.dumps(stack.manifest.payload)
    assert "reasoner-secret" not in rendered
    assert "verifier-secret" not in rendered
    assert "gpt-reasoner-test" in rendered
    assert "protected-http-verifier" in rendered
    assert "europe-pmc-rest" in rendered
    assert "crossref-rest" in rendered
    assert stack.evaluator_artifact_hash == "b" * 64
    assert stack.evaluation_epoch_id == "epoch:frozen"

    path = tmp_path / "provider-manifest.json"
    write_live_phase2_provider_manifest(stack, path)
    persisted = path.read_text()
    assert "reasoner-secret" not in persisted
    assert "verifier-secret" not in persisted
    raw = json.loads(persisted)
    assert raw["provider_manifest_hash"] == stack.provider_manifest_hash


def test_env_builder_requires_reasoner_and_protected_verifier_configuration(monkeypatch):
    variables = (
        "OPENAI_API_KEY",
        "ORION_PROTECTED_VERIFIER_URL",
        "ORION_PROTECTED_VERIFIER_TOKEN",
        "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
        "ORION_PHASE2_EVALUATION_EPOCH_ID",
    )
    for variable in variables:
        monkeypatch.delenv(variable, raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        build_phase2_live_provider_stack_from_env(reasoner_model="reasoner")

    monkeypatch.setenv("OPENAI_API_KEY", "reasoner-secret")
    with pytest.raises(RuntimeError, match="ORION_PROTECTED_VERIFIER_URL"):
        build_phase2_live_provider_stack_from_env(reasoner_model="reasoner")


def test_live_harness_reuses_provider_family_binds_verifier_records_and_accounts_by_default():
    stack = build_phase2_live_provider_stack(
        reasoner_api_key="reasoner-secret",
        reasoner_model="gpt-reasoner-test",
        protected_verifier_endpoint="https://verifier.example.test/v1/verify",
        protected_verifier_token="verifier-secret",
        evaluator_artifact_hash="b" * 64,
        evaluation_epoch_id="epoch:frozen",
    )
    harness = build_live_phase2_trial_harness(
        stack,
        producer_process_lineage_hash="a" * 64,
        baseline_retrieval_call_cost_units=2.0,
        baseline_llm_call_cost_units=3.0,
    )

    assert harness.stack is stack
    assert harness.provider_manifest_hash == stack.provider_manifest_hash
    assert harness.evaluator_artifact_hash == "b" * 64
    assert harness.baseline._llm is stack.llm
    assert harness.baseline._retrieval is stack.retrieval
    assert isinstance(harness.runner, AccountedShadowLiveTrialRunner)
    assert harness.runner._baseline is harness.baseline
    assert isinstance(
        harness.runner._retrieval_recorder, AttemptRecordingRetrievalProvider
    )
    assert harness.runner._retrieval_recorder._delegate is stack.retrieval
    assert harness.runner._retrieval_call_cost_units == 2.0
    assert harness.runner._llm_call_cost_units == 3.0
    assert isinstance(harness.runner._orion._experience_store, InMemoryExperienceStore)

    with pytest.raises(ValueError, match="must match"):
        build_live_phase2_trial_harness(stack, evaluator_artifact_hash="c" * 64)


def test_live_harness_preserves_explicit_host_experience_store():
    stack = build_phase2_live_provider_stack(
        reasoner_api_key="reasoner-secret",
        reasoner_model="gpt-reasoner-test",
        protected_verifier_endpoint="https://verifier.example.test/v1/verify",
        protected_verifier_token="verifier-secret",
        evaluator_artifact_hash="b" * 64,
        evaluation_epoch_id="epoch:frozen",
    )
    store = InMemoryExperienceStore()
    harness = build_live_phase2_trial_harness(stack, experience_store=store)
    assert harness.runner._orion._experience_store is store


def test_attempt_recorder_keeps_query_when_provider_raises():
    class Broken:
        def search(self, query, *, limit):
            raise TimeoutError("source timeout")

    recorder = AttemptRecordingRetrievalProvider(Broken())
    query = SearchQuery(
        "query:failed",
        "microglia complement",
        "route:failed",
        SearchRouteKind.PARENT_DISCIPLINE,
        "neuroimmunology",
    )
    mark = recorder.mark()
    with pytest.raises(TimeoutError, match="source timeout"):
        recorder.search(query, limit=7)
    observations = recorder.observations_since(mark)
    assert len(observations) == 1
    observation = observations[0]
    assert observation.query_id == "query:failed"
    assert observation.query_text == "microglia complement"
    assert observation.route_id == "route:failed"
    assert observation.limit == 7
    assert observation.items == ()
