import json

import pytest

from orion.core.contributions import AssimilationOutcome, KnowledgeContribution
from orion.core.search import RetrievedItem
from orion.providers.verification.protected_http import (
    ProtectedHTTPVerificationConfig,
    ProtectedHTTPVerificationProvider,
)


def _contribution(evidence_ids=("doc:one",)):
    return KnowledgeContribution(
        contribution_id="claim:one",
        text="The exact source reports the stated mechanism-specific effect.",
        assimilation=AssimilationOutcome.COMPLEMENTARY_FACET,
        evidence_ids=evidence_ids,
    )


def _item():
    return RetrievedItem(
        "doc:one",
        "The experiment reports the stated mechanism-specific effect.",
        "https://example.test/doc",
    )


def _config():
    return ProtectedHTTPVerificationConfig(
        endpoint="https://verifier.example.test/v1/verify",
        bearer_token="verifier-secret",
        evaluator_artifact_hash="e" * 64,
        evaluation_epoch_id="epoch:frozen",
    )


def test_protected_http_verifier_requires_exact_item_binding_before_network():
    calls = []
    verifier = ProtectedHTTPVerificationProvider(
        _config(),
        transport=lambda request, timeout: calls.append(request) or b"{}",
    )
    result = verifier.verify(_contribution(("other:item",)), _item())
    assert not result.passed
    assert result.reason == "contribution_does_not_bind_the_item_being_verified"
    assert calls == []


def test_protected_http_verifier_accepts_only_exact_request_evaluator_and_epoch_binding():
    captured = {}

    def transport(request, timeout):
        payload = json.loads(request.data)
        captured["payload"] = payload
        captured["authorization"] = request.get_header("Authorization")
        return json.dumps(
            {
                "request_hash": payload["request_hash"],
                "evaluator_artifact_hash": "e" * 64,
                "evaluation_epoch_id": "epoch:frozen",
                "passed": True,
                "certificate_ids": ["certificate:protected:one"],
                "reason": "independently supported by exact source content",
            }
        ).encode()

    config = _config()
    verifier = ProtectedHTTPVerificationProvider(config, transport=transport)
    result = verifier.verify(_contribution(), _item())

    assert result.passed
    assert result.certificate_ids == ("certificate:protected:one",)
    assert captured["payload"]["schema"] == "ProtectedVerificationRequest.v1"
    assert captured["payload"]["retrieved_item"]["content"] == _item().content
    assert captured["payload"]["evaluator_artifact_hash"] == "e" * 64
    assert "verifier-secret" not in repr(config.public_identity)


def test_protected_http_verifier_fails_closed_on_binding_mismatch_or_bare_pass():
    def wrong_hash(request, timeout):
        return json.dumps(
            {
                "request_hash": "0" * 64,
                "evaluator_artifact_hash": "e" * 64,
                "evaluation_epoch_id": "epoch:frozen",
                "passed": True,
                "certificate_ids": ["certificate:bad"],
                "reason": "wrong request",
            }
        ).encode()

    result = ProtectedHTTPVerificationProvider(_config(), transport=wrong_hash).verify(
        _contribution(), _item()
    )
    assert not result.passed
    assert result.reason == "protected_verifier_request_binding_mismatch"

    def bare_pass(request, timeout):
        payload = json.loads(request.data)
        return json.dumps(
            {
                "request_hash": payload["request_hash"],
                "evaluator_artifact_hash": "e" * 64,
                "evaluation_epoch_id": "epoch:frozen",
                "passed": True,
                "certificate_ids": [],
                "reason": "bare boolean without certificate",
            }
        ).encode()

    result = ProtectedHTTPVerificationProvider(_config(), transport=bare_pass).verify(
        _contribution(), _item()
    )
    assert not result.passed
    assert result.reason == "protected_verifier_pass_missing_certificates"


def test_protected_verifier_endpoint_must_be_clean_https():
    with pytest.raises(ValueError, match="absolute HTTPS"):
        ProtectedHTTPVerificationConfig(
            endpoint="http://verifier.example.test",
            bearer_token="secret",
            evaluator_artifact_hash="e" * 64,
            evaluation_epoch_id="epoch",
        )
    with pytest.raises(ValueError, match="userinfo/query/fragment"):
        ProtectedHTTPVerificationConfig(
            endpoint="https://user:pass@verifier.example.test/v1/verify?x=1",
            bearer_token="secret",
            evaluator_artifact_hash="e" * 64,
            evaluation_epoch_id="epoch",
        )
