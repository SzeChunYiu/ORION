import hashlib
import json

import pytest

from orion.providers.development.sandbox_http import (
    ProtectedHTTPSandboxConfig,
    ProtectedHTTPSandboxPatchExecutor,
)


SANDBOX_HASH = "a" * 64


def _config():
    return ProtectedHTTPSandboxConfig(
        endpoint="https://sandbox.example.test/v1/execute",
        bearer_token="sandbox-secret",
        sandbox_artifact_hash=SANDBOX_HASH,
    )


def test_protected_http_sandbox_binds_exact_patch_base_and_service_identity():
    captured = {}

    def transport(request, timeout):
        payload = json.loads(request.data)
        captured["payload"] = payload
        return json.dumps(
            {
                "request_hash": payload["request_hash"],
                "sandbox_artifact_hash": SANDBOX_HASH,
                "base_revision": "commit:abc",
                "patch_sha256": hashlib.sha256(b"patch-bytes").hexdigest(),
                "candidate_revision_hash": "c" * 64,
                "passed_required_tests": True,
                "test_result_ids": ["test:one"],
                "failure_signatures": [],
                "resource_units": 4.5,
                "artifact_ids": ["artifact:test-log"],
            }
        ).encode()

    config = _config()
    result = ProtectedHTTPSandboxPatchExecutor(config, transport=transport).execute_patch(
        base_revision="commit:abc",
        patch=b"patch-bytes",
        touched_paths=("src/orion/example.py",),
        test_plan=("pytest:test-one",),
    )
    assert result.candidate_revision_hash == "c" * 64
    assert result.passed_required_tests
    assert result.resource_units == 4.5
    assert captured["payload"]["patch_sha256"] == hashlib.sha256(b"patch-bytes").hexdigest()
    assert "sandbox-secret" not in repr(config.public_identity)


def test_protected_http_sandbox_rejects_replayed_or_rebound_response():
    def transport(request, timeout):
        payload = json.loads(request.data)
        return json.dumps(
            {
                "request_hash": "0" * 64,
                "sandbox_artifact_hash": payload["sandbox_artifact_hash"],
                "base_revision": payload["base_revision"],
                "patch_sha256": payload["patch_sha256"],
                "candidate_revision_hash": "c" * 64,
                "passed_required_tests": True,
                "test_result_ids": [],
                "failure_signatures": [],
                "resource_units": 1.0,
                "artifact_ids": [],
            }
        ).encode()

    with pytest.raises(RuntimeError, match="request binding mismatch"):
        ProtectedHTTPSandboxPatchExecutor(_config(), transport=transport).execute_patch(
            base_revision="commit:abc",
            patch=b"patch",
            touched_paths=("a.py",),
            test_plan=("test",),
        )


def test_protected_http_sandbox_requires_clean_https_endpoint():
    with pytest.raises(ValueError, match="absolute HTTPS"):
        ProtectedHTTPSandboxConfig(
            endpoint="http://sandbox.example.test",
            bearer_token="secret",
            sandbox_artifact_hash=SANDBOX_HASH,
        )
