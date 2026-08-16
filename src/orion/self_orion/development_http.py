from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from orion.providers.development.base import (
    CandidateExecutionReceipt,
    DevelopmentChangeProposal,
    DevelopmentChangeRequest,
)
from orion.self_orion.change_control import ProtectedDevelopmentAssuranceReceipt


DevelopmentAssuranceTransport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint validated HTTPS
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"protected development evaluator HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"protected development evaluator transport failed: {error.reason}"
        ) from error


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


@dataclass(frozen=True)
class ProtectedDevelopmentHTTPConfig:
    endpoint: str
    bearer_token: str = field(repr=False)
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        parsed = urllib.parse.urlparse(self.endpoint)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("protected development evaluator endpoint must be absolute HTTPS")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError(
                "protected development evaluator endpoint cannot contain userinfo/query/fragment"
            )
        if not self.bearer_token.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("protected development evaluator token/epoch are required")
        if not _sha256(self.evaluator_artifact_hash):
            raise ValueError("protected development evaluator artifact must be SHA-256")
        if self.timeout_seconds <= 0:
            raise ValueError("protected development evaluator timeout must be positive")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "protected-development-http-evaluator",
            "endpoint": self.endpoint,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "timeout_seconds": self.timeout_seconds,
        }


class ProtectedDevelopmentHTTPEvaluator:
    """Protected assurance client for one executed Shadow development candidate."""

    def __init__(
        self,
        config: ProtectedDevelopmentHTTPConfig,
        *,
        transport: DevelopmentAssuranceTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    def evaluate(
        self,
        request: DevelopmentChangeRequest,
        proposal: DevelopmentChangeProposal,
        execution: CandidateExecutionReceipt,
    ) -> ProtectedDevelopmentAssuranceReceipt:
        payload = {
            "schema": "ProtectedDevelopmentAssuranceRequest.v1",
            "evaluator_artifact_hash": self.config.evaluator_artifact_hash,
            "evaluation_epoch_id": self.config.evaluation_epoch_id,
            "request": {
                "request_id": request.request_id,
                "mechanic_id": request.mechanic_id,
                "problem_statement": request.problem_statement,
                "base_revision": request.base_revision,
                "evidence_ids": list(request.evidence_ids),
                "failure_episode_ids": list(request.failure_episode_ids),
                "protected_constraints": list(request.protected_constraints),
                "required_tests": list(request.required_tests),
                "falsifier": request.falsifier,
                "protected_path_prefixes": list(request.protected_path_prefixes),
                "development_issue_id": request.development_issue_id,
                "observed_failure_artifact_hash": request.observed_failure_artifact_hash,
                "candidate_cause_ids": list(request.candidate_cause_ids),
                "supported_cause_id": request.supported_cause_id,
                "discriminator_artifact_hash": request.discriminator_artifact_hash,
                "discriminator_evidence_ids": list(request.discriminator_evidence_ids),
                "negative_alternative_ids": list(request.negative_alternative_ids),
            },
            "proposal": {
                "proposal_id": proposal.proposal_id,
                "request_id": proposal.request_id,
                "base_revision": proposal.base_revision,
                "patch_artifact_id": proposal.patch_artifact_id,
                "patch_artifact_hash": proposal.patch_artifact_hash,
                "touched_paths": list(proposal.touched_paths),
                "expected_effects": list(proposal.expected_effects),
                "test_plan": list(proposal.test_plan),
                "falsifier": proposal.falsifier,
                "provenance_ids": list(proposal.provenance_ids),
            },
            "execution": {
                "receipt_id": execution.receipt_id,
                "proposal_id": execution.proposal_id,
                "candidate_revision_hash": execution.candidate_revision_hash,
                "passed_required_tests": execution.passed_required_tests,
                "test_result_ids": list(execution.test_result_ids),
                "failure_signatures": list(execution.failure_signatures),
                "resource_units": execution.resource_units,
                "artifact_ids": list(execution.artifact_ids),
            },
        }
        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        http_request = urllib.request.Request(
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
        raw = json.loads(self._transport(http_request, self.config.timeout_seconds))
        if not isinstance(raw, dict):
            raise RuntimeError("protected development evaluator response must be an object")
        if raw.get("request_hash") != request_hash:
            raise RuntimeError("protected development evaluator request binding mismatch")
        if raw.get("evaluator_artifact_hash") != self.config.evaluator_artifact_hash:
            raise RuntimeError("protected development evaluator artifact binding mismatch")
        if raw.get("evaluation_epoch_id") != self.config.evaluation_epoch_id:
            raise RuntimeError("protected development evaluator epoch binding mismatch")
        if raw.get("proposal_id") != proposal.proposal_id:
            raise RuntimeError("protected development evaluator proposal binding mismatch")
        if raw.get("candidate_revision_hash") != execution.candidate_revision_hash:
            raise RuntimeError("protected development evaluator candidate binding mismatch")
        booleans = (
            "blocking_invariants_passed",
            "evaluator_frozen_before_candidate",
            "fresh_split",
            "resource_matched",
        )
        if any(type(raw.get(name)) is not bool for name in booleans):
            raise RuntimeError("protected development evaluator boolean fields are invalid")
        for name in ("development_delta", "fresh_assurance_delta"):
            if isinstance(raw.get(name), bool) or not isinstance(raw.get(name), (int, float)):
                raise RuntimeError(f"protected development evaluator {name} must be numeric")
        reasons = raw.get("reasons")
        receipt_id = raw.get("receipt_id")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise RuntimeError("protected development evaluator receipt id is required")
        if not isinstance(reasons, list) or any(not isinstance(item, str) or not item for item in reasons):
            raise RuntimeError("protected development evaluator reasons must be strings")
        return ProtectedDevelopmentAssuranceReceipt(
            receipt_id=receipt_id,
            proposal_id=proposal.proposal_id,
            candidate_revision_hash=execution.candidate_revision_hash,
            evaluator_artifact_hash=self.config.evaluator_artifact_hash,
            evaluation_epoch_id=self.config.evaluation_epoch_id,
            development_delta=float(raw["development_delta"]),
            fresh_assurance_delta=float(raw["fresh_assurance_delta"]),
            blocking_invariants_passed=raw["blocking_invariants_passed"],
            evaluator_frozen_before_candidate=raw["evaluator_frozen_before_candidate"],
            fresh_split=raw["fresh_split"],
            resource_matched=raw["resource_matched"],
            reasons=tuple(reasons),
        )


__all__ = [
    "DevelopmentAssuranceTransport",
    "ProtectedDevelopmentHTTPConfig",
    "ProtectedDevelopmentHTTPEvaluator",
]
