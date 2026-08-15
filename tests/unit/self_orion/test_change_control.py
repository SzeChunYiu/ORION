from orion.core.solution import SolutionStatus
from orion.providers.development.base import DevelopmentChangeProposal
from orion.self_orion.change_control import (
    CandidateExecutionReceipt,
    ChangeControlVerdict,
    ProtectedDevelopmentAssuranceReceipt,
    SelfOrionChangeController,
    change_request_from_investigation,
)
from orion.self_orion.development_driver import SelfOrionDevelopmentDriver
from orion.self_orion.development_fibre import compile_development_fibre
from orion.self_orion.research_loop import DevelopmentInvestigationResult


class _Provider:
    def __init__(self, *, touched_paths=("src/orion/mechanics/example.py",)):
        self.touched_paths = touched_paths

    def propose(self, request):
        return DevelopmentChangeProposal(
            proposal_id="proposal:1",
            request_id=request.request_id,
            base_revision=request.base_revision,
            patch_artifact_id="development-artifact:" + "a" * 64,
            patch_artifact_hash="a" * 64,
            touched_paths=self.touched_paths,
            rationale="small scoped repair",
            expected_effects=("improve diagnosed coordinate",),
            test_plan=request.required_tests,
            falsifier=request.falsifier,
            provenance_ids=("evidence:1",),
        )


class _Runner:
    def execute(self, proposal):
        return CandidateExecutionReceipt(
            "exec:1",
            proposal.proposal_id,
            "b" * 64,
            True,
            ("tests:unit", "tests:fresh"),
            (),
            5.0,
            ("artifact:candidate",),
        )


class _Evaluator:
    def __init__(self, *, fresh=True, blockers=True):
        self._fresh = fresh
        self._blockers = blockers

    def evaluate(self, request, proposal, execution):
        return ProtectedDevelopmentAssuranceReceipt(
            "assurance:1",
            proposal.proposal_id,
            execution.candidate_revision_hash,
            "c" * 64,
            "epoch:protected",
            1.0,
            0.5,
            self._blockers,
            True,
            self._fresh,
            True,
            ("protected comparison complete",),
        )


def _request():
    cells = SelfOrionDevelopmentDriver().local_transfer_cells()
    fibre = compile_development_fibre("SEARCH.QUERY.v0", cells)
    investigation = DevelopmentInvestigationResult(
        work_id="empirical:SEARCH.QUERY.v0:0",
        mechanic_id="SEARCH.QUERY.v0",
        problem_id="self-orion:empirical:SEARCH.QUERY.v0:0",
        solution_status=SolutionStatus.PROVISIONAL,
        evidence_ids=("evidence:1",),
        residual_ids=("query-selection-open",),
        root_episode_id="episode:root",
        mechanic_episode_ids=("episode:mechanic",),
        proposal_only=True,
    )
    return change_request_from_investigation(investigation, fibre, base_revision="main:abc")


def test_change_request_binds_evidence_failures_protected_constraints_and_fresh_test():
    request = _request()
    assert request.evidence_ids == ("evidence:1",)
    assert "episode:mechanic" in request.failure_episode_ids
    assert any("no self-merge" in item for item in request.protected_constraints)
    assert any("fresh-assurance" in item for item in request.required_tests)
    assert ".github/workflows/" in request.protected_path_prefixes


def test_good_candidate_can_only_recommend_host_promotion_not_self_merge():
    result = SelfOrionChangeController(provider=_Provider(), runner=_Runner(), evaluator=_Evaluator()).evaluate_change(_request())
    assert result.verdict is ChangeControlVerdict.RECOMMEND_HOST_PROMOTION
    assert not result.self_merge_authorized
    assert result.reasons == ()
    assert result.proposal.patch_artifact_id.startswith("development-artifact:")


def test_nonfresh_assurance_stays_candidate_only_and_blocker_failure_rejects():
    nonfresh = SelfOrionChangeController(provider=_Provider(), runner=_Runner(), evaluator=_Evaluator(fresh=False)).evaluate_change(_request())
    assert nonfresh.verdict is ChangeControlVerdict.CANDIDATE_ONLY
    assert "assurance_split_not_fresh" in nonfresh.reasons

    blocked = SelfOrionChangeController(provider=_Provider(), runner=_Runner(), evaluator=_Evaluator(blockers=False)).evaluate_change(_request())
    assert blocked.verdict is ChangeControlVerdict.REJECT
    assert "blocking_invariant_failed" in blocked.reasons


def test_protected_evaluator_or_workflow_paths_are_hard_rejected_even_if_sandbox_tests_pass():
    controller = SelfOrionChangeController(
        provider=_Provider(touched_paths=("src/orion/self_orion/readiness.py",)),
        runner=_Runner(),
        evaluator=_Evaluator(),
    )
    result = controller.evaluate_change(_request())
    assert result.verdict is ChangeControlVerdict.REJECT
    assert "protected_path_touched:src/orion/self_orion/readiness.py" in result.reasons
