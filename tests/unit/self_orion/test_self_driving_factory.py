import json
from types import SimpleNamespace

from orion.core.solution import SolutionStatus
from orion.providers.development import InMemoryDevelopmentArtifactStore, SandboxExecutionResult
from orion.providers.llm.base import LLMResponse
from orion.self_orion.change_control import ProtectedDevelopmentAssuranceReceipt
from orion.self_orion.factory import build_llm_shadow_self_driving_controller
from orion.self_orion.self_driving import SelfDrivingCycleStatus


class _ResearchRuntime:
    def solve(self, problem, *, variation_signature, evaluation_epoch_id, split_id):
        return SimpleNamespace(
            solution=SimpleNamespace(
                status=SolutionStatus.PROVISIONAL,
                evidence_ids=("evidence:research",),
                residual_ids=("residual:repairable",),
            ),
            experience_episode_id="episode:root",
            mechanic_experience_episode_ids=("episode:mechanic",),
        )


class _DevelopmentLLM:
    def complete(self, request):
        return LLMResponse(
            json.dumps(
                {
                    "touched_paths": ["src/orion/mechanics/repair_candidate.py"],
                    "patch": "diff --git a/src/orion/mechanics/repair_candidate.py b/src/orion/mechanics/repair_candidate.py\n",
                    "rationale": "repair the diagnosed coordinate",
                    "expected_effects": ["improve fresh assurance"],
                    "test_plan": ["test:hostile"],
                    "falsifier": "fresh assurance does not improve",
                }
            ),
            model_id="coding-model:test",
            response_id="coding-response:1",
        )


class _Sandbox:
    def execute_patch(self, *, base_revision, patch, touched_paths, test_plan):
        assert base_revision == "main:a5e1ed8"
        assert patch.startswith(b"diff --git")
        assert "test:hostile" in test_plan
        return SandboxExecutionResult(
            candidate_revision_hash="b" * 64,
            passed_required_tests=True,
            test_result_ids=("test:required", "test:hostile", "test:fresh"),
            failure_signatures=(),
            resource_units=4.0,
            artifact_ids=("artifact:test-report",),
        )


class _ProtectedEvaluator:
    def evaluate(self, request, proposal, execution):
        return ProtectedDevelopmentAssuranceReceipt(
            receipt_id="assurance:known-world",
            proposal_id=proposal.proposal_id,
            candidate_revision_hash=execution.candidate_revision_hash,
            evaluator_artifact_hash="c" * 64,
            evaluation_epoch_id="epoch:protected",
            development_delta=1.0,
            fresh_assurance_delta=0.25,
            blocking_invariants_passed=True,
            evaluator_frozen_before_candidate=True,
            fresh_split=True,
            resource_matched=True,
            reasons=("known-world protected evaluator passed",),
        )


def _controller():
    return build_llm_shadow_self_driving_controller(
        research_runtime=_ResearchRuntime(),
        development_llm=_DevelopmentLLM(),
        artifact_store=InMemoryDevelopmentArtifactStore(),
        sandbox_executor=_Sandbox(),
        protected_evaluator=_ProtectedEvaluator(),
        base_revision="main:a5e1ed8",
    )


def test_factory_composes_shadow_ready_controller():
    controller = _controller()
    assert controller.shadow_self_driving_ready


def test_factory_known_world_cycle_recommends_host_promotion_only():
    controller = _controller()
    result = controller.run_cycle(
        limit=1,
        evaluation_epoch_id="epoch:development",
        split_id="split:development",
    )[0]
    assert result.status is SelfDrivingCycleStatus.HOST_PROMOTION_RECOMMENDED
    assert result.change_control is not None
    assert result.change_control.proposal.patch_artifact_id.startswith("development-artifact:")
    assert not result.self_merge_authorized
    assert not result.change_control.self_merge_authorized
