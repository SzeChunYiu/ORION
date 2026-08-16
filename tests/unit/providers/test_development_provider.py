import hashlib
import json

import pytest

from orion.providers.development.artifacts import InMemoryDevelopmentArtifactStore
from orion.providers.development.base import DevelopmentChangeRequest
from orion.providers.development.llm import LLMDevelopmentChangeProvider
from orion.providers.development.sandbox import (
    ArtifactBackedSandboxCandidateRunner,
    SandboxExecutionResult,
)
from orion.providers.llm.base import LLMResponse


class _LLM:
    def __init__(self, payload):
        self.payload = payload
        self.request = None

    def complete(self, request):
        self.request = request
        return LLMResponse(json.dumps(self.payload), model_id="model:test", response_id="response:1")


class _Executor:
    def __init__(self):
        self.patch = None
        self.test_plan = None

    def execute_patch(self, *, base_revision, patch, touched_paths, test_plan):
        self.patch = patch
        self.test_plan = test_plan
        assert base_revision == "main:abc"
        assert touched_paths == ("src/orion/example.py",)
        return SandboxExecutionResult(
            candidate_revision_hash="b" * 64,
            passed_required_tests=True,
            test_result_ids=("test:unit", "test:fresh"),
            failure_signatures=(),
            resource_units=3.0,
            artifact_ids=("artifact:test-report",),
        )


def _request():
    return DevelopmentChangeRequest(
        request_id="change:1",
        mechanic_id="SEARCH.QUERY.v0",
        problem_statement="Improve query selection from evidence.",
        base_revision="main:abc",
        evidence_ids=("e:1",),
        failure_episode_ids=("episode:f1",),
        protected_constraints=("do not weaken evaluator",),
        required_tests=("test:required",),
        falsifier="fresh assurance does not improve",
    )


def test_llm_development_provider_stores_exact_patch_and_keeps_required_tests():
    patch = "--- a/src/orion/example.py\n+++ b/src/orion/example.py\n@@\n-old\n+new\n"
    llm = _LLM(
        {
            "touched_paths": ["src/orion/example.py"],
            "patch": patch,
            "rationale": "scoped query repair",
            "expected_effects": ["improve hidden query choice"],
            "test_plan": ["test:provider-suggested"],
            "falsifier": "hidden query choice does not improve",
        }
    )
    store = InMemoryDevelopmentArtifactStore()
    proposal = LLMDevelopmentChangeProvider(llm, store).propose(_request())
    assert store.get(proposal.patch_artifact_id) == patch.encode()
    assert proposal.patch_artifact_hash == hashlib.sha256(patch.encode()).hexdigest()
    assert proposal.test_plan[:1] == ("test:required",)
    assert "test:provider-suggested" in proposal.test_plan
    assert proposal.proposal_only
    assert "proposal-only coding worker" in llm.request.system


def test_artifact_backed_sandbox_verifies_patch_hash_and_returns_bound_receipt():
    patch = b"diff --git a/x b/x\n"
    store = InMemoryDevelopmentArtifactStore()
    store.put(patch, media_type="text/x-diff")
    llm = _LLM(
        {
            "touched_paths": ["src/orion/example.py"],
            "patch": patch.decode(),
            "rationale": "repair",
            "expected_effects": ["effect"],
            "test_plan": ["test:extra"],
            "falsifier": "no effect",
        }
    )
    proposal = LLMDevelopmentChangeProvider(llm, store).propose(_request())
    executor = _Executor()
    receipt = ArtifactBackedSandboxCandidateRunner(artifact_store=store, executor=executor).execute(proposal)
    assert executor.patch == patch
    assert receipt.proposal_id == proposal.proposal_id
    assert receipt.candidate_revision_hash == "b" * 64
    assert proposal.patch_artifact_id in receipt.artifact_ids

    # Tampering with the content-addressed artifact identity must fail before execution.
    store._content[proposal.patch_artifact_id] = b"tampered"  # hostile fixture against the in-memory test store
    with pytest.raises(ValueError, match="content hash mismatch"):
        ArtifactBackedSandboxCandidateRunner(artifact_store=store, executor=_Executor()).execute(proposal)


def test_llm_provider_rejects_invalid_json():
    class _BadLLM:
        def complete(self, request):
            return LLMResponse("not-json")

    with pytest.raises(ValueError, match="invalid JSON"):
        LLMDevelopmentChangeProvider(_BadLLM(), InMemoryDevelopmentArtifactStore()).propose(_request())
