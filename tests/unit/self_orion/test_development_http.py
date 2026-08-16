import json

import pytest

from orion.providers.development.base import (
    CandidateExecutionReceipt,
    DevelopmentChangeProposal,
    DevelopmentChangeRequest,
)
from orion.self_orion.development_http import (
    ProtectedDevelopmentHTTPConfig,
    ProtectedDevelopmentHTTPEvaluator,
)


def _request():
    return DevelopmentChangeRequest(
        request_id="change:one",
        mechanic_id="SEARCH.QUERY.v0",
        problem_statement="repair the observed routing failure",
        base_revision="commit:base",
        evidence_ids=("evidence:one",),
        failure_episode_ids=("episode:failure",),
        protected_constraints=("no authority escalation",),
        required_tests=("test:regression", "test:fresh"),
        falsifier="reject if fresh assurance does not improve",
    )


def _proposal():
    return DevelopmentChangeProposal(
        proposal_id="proposal:one",
        request_id="change:one",
        base_revision="commit:base",
        patch_artifact_id="development-artifact:" + "a" * 64,
        patch_artifact_hash="a" * 64,
        touched_paths=("src/orion/example.py",),
        rationale="small repair",
        expected_effects=("recover route",),
        test_plan=("test:regression", "test:fresh"),
        falsifier="reject on no fresh improvement",
        provenance_ids=("source:diagnosis",),
    )


def _execution():
    return CandidateExecutionReceipt(
        receipt_id="execution:one",
        proposal_id="proposal:one",
        candidate_revision_hash="c" * 64,
        passed_required_tests=True,
        test_result_ids=("result:regression", "result:fresh"),
        failure_signatures=(),
        resource_units=5.0,
        artifact_ids=("artifact:test-log",),
    )


def _config():
    return ProtectedDevelopmentHTTPConfig(
        endpoint="https://development-evaluator.example.test/v1/evaluate",
        bearer_token="evaluator-secret",
        evaluator_artifact_hash="e" * 64,
        evaluation_epoch_id="epoch:frozen",
    )


def test_protected_development_evaluator_binds_request_proposal_candidate_and_epoch():
    captured = {}

    def transport(http_request, timeout):
        payload = json.loads(http_request.data)
        captured["payload"] = payload
        return json.dumps(
            {
                "request_hash": payload["request_hash"],
                "evaluator_artifact_hash": "e" * 64,
                "evaluation_epoch_id": "epoch:frozen",
                "proposal_id": "proposal:one",
                "candidate_revision_hash": "c" * 64,
                "receipt_id": "assurance:one",
                "development_delta": 0.2,
                "fresh_assurance_delta": 0.1,
                "blocking_invariants_passed": True,
                "evaluator_frozen_before_candidate": True,
                "fresh_split": True,
                "resource_matched": True,
                "reasons": [],
            }
        ).encode()

    config = _config()
    receipt = ProtectedDevelopmentHTTPEvaluator(config, transport=transport).evaluate(
        _request(), _proposal(), _execution()
    )
    assert receipt.receipt_id == "assurance:one"
    assert receipt.candidate_revision_hash == "c" * 64
    assert receipt.evaluator_artifact_hash == "e" * 64
    assert receipt.evaluation_epoch_id == "epoch:frozen"
    assert receipt.fresh_split
    assert captured["payload"]["request"]["failure_episode_ids"] == ["episode:failure"]
    assert captured["payload"]["proposal"]["patch_artifact_hash"] == "a" * 64
    assert captured["payload"]["execution"]["candidate_revision_hash"] == "c" * 64
    assert "evaluator-secret" not in repr(config.public_identity)


def test_protected_development_evaluator_rejects_replayed_candidate_binding():
    def transport(http_request, timeout):
        payload = json.loads(http_request.data)
        return json.dumps(
            {
                "request_hash": payload["request_hash"],
                "evaluator_artifact_hash": "e" * 64,
                "evaluation_epoch_id": "epoch:frozen",
                "proposal_id": "proposal:one",
                "candidate_revision_hash": "d" * 64,
                "receipt_id": "assurance:wrong",
                "development_delta": 1.0,
                "fresh_assurance_delta": 1.0,
                "blocking_invariants_passed": True,
                "evaluator_frozen_before_candidate": True,
                "fresh_split": True,
                "resource_matched": True,
                "reasons": [],
            }
        ).encode()

    with pytest.raises(RuntimeError, match="candidate binding mismatch"):
        ProtectedDevelopmentHTTPEvaluator(_config(), transport=transport).evaluate(
            _request(), _proposal(), _execution()
        )


def test_protected_development_evaluator_requires_https_endpoint():
    with pytest.raises(ValueError, match="absolute HTTPS"):
        ProtectedDevelopmentHTTPConfig(
            endpoint="http://example.test/evaluate",
            bearer_token="secret",
            evaluator_artifact_hash="e" * 64,
            evaluation_epoch_id="epoch",
        )
