from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from orion.core.contributions import KnowledgeContribution
from orion.core.search import RetrievedItem

from .base import VerificationProvider, VerificationResult


ProtectedVerifierTransport = Callable[[urllib.request.Request, float], bytes]


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - host endpoint is validated HTTPS
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"protected verifier HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"protected verifier transport failed: {error.reason}") from error


@dataclass(frozen=True)
class ProtectedHTTPVerificationConfig:
    endpoint: str
    bearer_token: str = field(repr=False)
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        parsed = urllib.parse.urlparse(self.endpoint)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("protected verifier endpoint must be an absolute HTTPS URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("protected verifier endpoint cannot contain userinfo/query/fragment")
        if not self.bearer_token.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("protected verifier token and evaluation epoch are required")
        if not _sha256(self.evaluator_artifact_hash):
            raise ValueError("protected verifier artifact identity must be SHA-256")
        if self.timeout_seconds <= 0:
            raise ValueError("protected verifier timeout must be positive")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "protected-http-verifier",
            "endpoint": self.endpoint,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "timeout_seconds": self.timeout_seconds,
        }


class ProtectedHTTPVerificationProvider(VerificationProvider):
    """Client for a separately controlled scientific-authority verification service.

    The external service must bind its decision to `request_hash`, the frozen
    evaluator artifact and the frozen evaluation epoch. A bare boolean response
    is never accepted. This keeps the authority-producing boundary outside the
    candidate/reasoner process while making the live stack executable.
    """

    def __init__(
        self,
        config: ProtectedHTTPVerificationConfig,
        *,
        transport: ProtectedVerifierTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    @staticmethod
    def _request_payload(
        contribution: KnowledgeContribution,
        item: RetrievedItem,
        config: ProtectedHTTPVerificationConfig,
    ) -> dict[str, object]:
        return {
            "schema": "ProtectedVerificationRequest.v1",
            "evaluator_artifact_hash": config.evaluator_artifact_hash,
            "evaluation_epoch_id": config.evaluation_epoch_id,
            "contribution": {
                "contribution_id": contribution.contribution_id,
                "text": contribution.text,
                "assimilation": contribution.assimilation.value,
                "evidence_ids": list(contribution.evidence_ids),
                "discovered_domain_ids": list(contribution.discovered_domain_ids),
                "representation_ids": list(contribution.representation_ids),
                "contradicts_claim_ids": list(contribution.contradicts_claim_ids),
                "related_claim_ids": list(contribution.related_claim_ids),
                "context_ids": list(contribution.context_ids),
                "assumption_ids": list(contribution.assumption_ids),
            },
            "retrieved_item": {
                "item_id": item.item_id,
                "content": item.content,
                "source_uri": item.source_uri,
                "domain_ids": list(item.domain_ids),
            },
        }

    def verify(
        self,
        contribution: KnowledgeContribution,
        item: RetrievedItem,
    ) -> VerificationResult:
        if item.item_id not in contribution.evidence_ids:
            return VerificationResult(
                passed=False,
                reason="contribution_does_not_bind_the_item_being_verified",
            )
        payload = self._request_payload(contribution, item, self.config)
        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        wire_payload = {**payload, "request_hash": request_hash}
        request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps(wire_payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.bearer_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "orion-research-os/0.1",
            },
            method="POST",
        )
        body = self._transport(request, self.config.timeout_seconds)
        try:
            raw = json.loads(body)
        except json.JSONDecodeError:
            return VerificationResult(False, reason="protected_verifier_output_unparseable")
        if not isinstance(raw, dict):
            return VerificationResult(False, reason="protected_verifier_output_not_object")
        required_strings = (
            "request_hash",
            "evaluator_artifact_hash",
            "evaluation_epoch_id",
            "reason",
        )
        if any(not isinstance(raw.get(key), str) or not raw[key].strip() for key in required_strings):
            return VerificationResult(False, reason="protected_verifier_output_schema_invalid")
        if type(raw.get("passed")) is not bool:
            return VerificationResult(False, reason="protected_verifier_output_schema_invalid")
        if raw["request_hash"] != request_hash:
            return VerificationResult(False, reason="protected_verifier_request_binding_mismatch")
        if raw["evaluator_artifact_hash"] != self.config.evaluator_artifact_hash:
            return VerificationResult(False, reason="protected_verifier_artifact_binding_mismatch")
        if raw["evaluation_epoch_id"] != self.config.evaluation_epoch_id:
            return VerificationResult(False, reason="protected_verifier_epoch_binding_mismatch")
        if raw["passed"] is not True:
            return VerificationResult(False, reason=raw["reason"])
        certificates = raw.get("certificate_ids")
        if not isinstance(certificates, list) or not certificates or any(
            not isinstance(item, str) or not item.strip() for item in certificates
        ):
            return VerificationResult(False, reason="protected_verifier_pass_missing_certificates")
        return VerificationResult(
            passed=True,
            certificate_ids=tuple(certificates),
            reason=raw["reason"],
        )


__all__ = [
    "ProtectedHTTPVerificationConfig",
    "ProtectedHTTPVerificationProvider",
    "ProtectedVerifierTransport",
]
