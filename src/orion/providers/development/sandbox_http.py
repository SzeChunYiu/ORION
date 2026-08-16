from __future__ import annotations

import base64
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from .sandbox import SandboxExecutionResult, SandboxPatchExecutor


SandboxHTTPTransport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint validated HTTPS
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"protected sandbox HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"protected sandbox transport failed: {error.reason}") from error


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


@dataclass(frozen=True)
class ProtectedHTTPSandboxConfig:
    endpoint: str
    bearer_token: str = field(repr=False)
    sandbox_artifact_hash: str
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        parsed = urllib.parse.urlparse(self.endpoint)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("protected sandbox endpoint must be an absolute HTTPS URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("protected sandbox endpoint cannot contain userinfo/query/fragment")
        if not self.bearer_token.strip() or not _sha256(self.sandbox_artifact_hash):
            raise ValueError("protected sandbox token and artifact hash are required")
        if self.timeout_seconds <= 0:
            raise ValueError("protected sandbox timeout must be positive")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "protected-http-sandbox",
            "endpoint": self.endpoint,
            "sandbox_artifact_hash": self.sandbox_artifact_hash,
            "timeout_seconds": self.timeout_seconds,
        }


class ProtectedHTTPSandboxPatchExecutor(SandboxPatchExecutor):
    """Delegate exact patch execution to a separately controlled sandbox service."""

    def __init__(
        self,
        config: ProtectedHTTPSandboxConfig,
        *,
        transport: SandboxHTTPTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    def execute_patch(
        self,
        *,
        base_revision: str,
        patch: bytes,
        touched_paths: tuple[str, ...],
        test_plan: tuple[str, ...],
    ) -> SandboxExecutionResult:
        patch_hash = hashlib.sha256(patch).hexdigest()
        payload = {
            "schema": "ProtectedSandboxExecutionRequest.v1",
            "sandbox_artifact_hash": self.config.sandbox_artifact_hash,
            "base_revision": base_revision,
            "patch_sha256": patch_hash,
            "patch_base64": base64.b64encode(patch).decode("ascii"),
            "touched_paths": list(touched_paths),
            "test_plan": list(test_plan),
        }
        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps({**payload, "request_hash": request_hash}, separators=(",", ":")).encode(),
            headers={
                "Authorization": f"Bearer {self.config.bearer_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "orion-research-os/0.1",
            },
            method="POST",
        )
        raw = json.loads(self._transport(request, self.config.timeout_seconds))
        if not isinstance(raw, dict):
            raise RuntimeError("protected sandbox response must be a JSON object")
        if raw.get("request_hash") != request_hash:
            raise RuntimeError("protected sandbox request binding mismatch")
        if raw.get("sandbox_artifact_hash") != self.config.sandbox_artifact_hash:
            raise RuntimeError("protected sandbox artifact binding mismatch")
        if raw.get("base_revision") != base_revision or raw.get("patch_sha256") != patch_hash:
            raise RuntimeError("protected sandbox subject/patch binding mismatch")
        candidate_hash = raw.get("candidate_revision_hash")
        if not isinstance(candidate_hash, str) or not _sha256(candidate_hash):
            raise RuntimeError("protected sandbox candidate revision must be SHA-256")
        if type(raw.get("passed_required_tests")) is not bool:
            raise RuntimeError("protected sandbox passed_required_tests must be boolean")
        test_ids = raw.get("test_result_ids")
        failures = raw.get("failure_signatures")
        artifact_ids = raw.get("artifact_ids")
        resource_units = raw.get("resource_units")
        if not isinstance(test_ids, list) or any(not isinstance(item, str) or not item for item in test_ids):
            raise RuntimeError("protected sandbox test_result_ids must be strings")
        if not isinstance(failures, list) or any(not isinstance(item, str) or not item for item in failures):
            raise RuntimeError("protected sandbox failure_signatures must be strings")
        if not isinstance(artifact_ids, list) or any(not isinstance(item, str) or not item for item in artifact_ids):
            raise RuntimeError("protected sandbox artifact_ids must be strings")
        if isinstance(resource_units, bool) or not isinstance(resource_units, (int, float)) or resource_units < 0:
            raise RuntimeError("protected sandbox resource_units must be non-negative")
        return SandboxExecutionResult(
            candidate_revision_hash=candidate_hash,
            passed_required_tests=raw["passed_required_tests"],
            test_result_ids=tuple(test_ids),
            failure_signatures=tuple(failures),
            resource_units=float(resource_units),
            artifact_ids=tuple(artifact_ids),
        )


__all__ = [
    "ProtectedHTTPSandboxConfig",
    "ProtectedHTTPSandboxPatchExecutor",
    "SandboxHTTPTransport",
]
