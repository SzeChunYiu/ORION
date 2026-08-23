from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from orion.core.contributions import KnowledgeContribution
from orion.core.search import RetrievedItem

from .base import VerificationProvider, VerificationResult


GitHubModelsVerifierTransport = Callable[[urllib.request.Request, float], bytes]
GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
_VERIFIER_POLICY_SCHEMA = "GitHubModelsProtectedVerifierPolicy.v1"
_VERIFIER_POLICY = (
    "You are an independent scientific evidence verifier. Evaluate only whether the proposed "
    "knowledge contribution is faithfully and materially supported by the supplied retrieved item. "
    "Do not reward fluency, plausibility, novelty, or agreement with the candidate. Reject unsupported "
    "generalization, contradiction, citation laundering, or evidence that does not actually support the "
    "claim. Return one JSON object only, with exactly: request_hash, evaluator_artifact_hash, "
    "evaluation_epoch_id, passed, reason. Echo the three binding fields exactly. passed must be a JSON "
    "boolean and reason must be a non-empty concise string."
)


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint is frozen/validated
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub Models verifier HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"GitHub Models verifier transport failed: {error.reason}") from error


def evaluator_artifact_hash(model: str) -> str:
    payload = {
        "schema": _VERIFIER_POLICY_SCHEMA,
        "model": model,
        "endpoint": GITHUB_MODELS_ENDPOINT,
        "policy": _VERIFIER_POLICY,
        "output_schema": {
            "request_hash": "sha256",
            "evaluator_artifact_hash": "sha256",
            "evaluation_epoch_id": "string",
            "passed": "boolean",
            "reason": "non-empty-string",
        },
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class GitHubModelsVerificationConfig:
    model: str
    token: str = field(repr=False)
    evaluation_epoch_id: str
    evaluator_artifact_hash: str | None = None
    endpoint: str = GITHUB_MODELS_ENDPOINT
    timeout_seconds: float = 120.0

    def __post_init__(self) -> None:
        if not self.model.strip() or not self.token.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("GitHub Models verifier model, token and evaluation epoch are required")
        if self.endpoint != GITHUB_MODELS_ENDPOINT:
            raise ValueError("GitHub Models verifier endpoint is frozen to the official inference endpoint")
        if self.timeout_seconds <= 0:
            raise ValueError("GitHub Models verifier timeout must be positive")
        expected = evaluator_artifact_hash(self.model)
        if self.evaluator_artifact_hash is None:
            object.__setattr__(self, "evaluator_artifact_hash", expected)
        elif self.evaluator_artifact_hash != expected:
            raise ValueError("GitHub Models evaluator artifact hash does not bind the frozen verifier policy")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "github-models-protected-verifier",
            "endpoint": self.endpoint,
            "model": self.model,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "timeout_seconds": self.timeout_seconds,
        }


class GitHubModelsVerificationProvider(VerificationProvider):
    """External GitHub Models verifier with content-bound certificates.

    The candidate supplies neither the verdict nor certificate. The provider
    freezes the evaluator policy/model to a SHA-256 artifact identity, binds the
    external model decision to the exact request hash and evaluation epoch, and
    derives a certificate from the returned model response identity.
    """

    def __init__(
        self,
        config: GitHubModelsVerificationConfig,
        *,
        transport: GitHubModelsVerifierTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    @staticmethod
    def _request_payload(
        contribution: KnowledgeContribution,
        item: RetrievedItem,
        config: GitHubModelsVerificationConfig,
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

    @staticmethod
    def _message_content(raw: dict[str, object]) -> str:
        choices = raw.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise RuntimeError("GitHub Models verifier payload has no choice")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise RuntimeError("GitHub Models verifier choice has no message")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("GitHub Models verifier response has no content")
        return content.strip()

    def verify(self, contribution: KnowledgeContribution, item: RetrievedItem) -> VerificationResult:
        if item.item_id not in contribution.evidence_ids:
            return VerificationResult(False, reason="contribution_does_not_bind_the_item_being_verified")
        payload = self._request_payload(contribution, item, self.config)
        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        bound = {
            **payload,
            "request_hash": request_hash,
        }
        chat_payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": _VERIFIER_POLICY},
                {
                    "role": "user",
                    "content": (
                        "Evaluate this frozen verification request. Return JSON only.\n"
                        + json.dumps(bound, sort_keys=True, separators=(",", ":"))
                    ),
                },
            ],
        }
        http_request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps(chat_payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
                "User-Agent": "orion-research-os/0.1",
            },
            method="POST",
        )
        body = self._transport(http_request, self.config.timeout_seconds)
        try:
            raw_response = json.loads(body)
        except json.JSONDecodeError:
            return VerificationResult(False, reason="github_models_verifier_transport_non_json")
        if not isinstance(raw_response, dict):
            return VerificationResult(False, reason="github_models_verifier_transport_non_object")
        try:
            raw = json.loads(self._message_content(raw_response))
        except (json.JSONDecodeError, RuntimeError):
            return VerificationResult(False, reason="github_models_verifier_output_unparseable")
        if not isinstance(raw, dict):
            return VerificationResult(False, reason="github_models_verifier_output_not_object")
        required_strings = (
            "request_hash",
            "evaluator_artifact_hash",
            "evaluation_epoch_id",
            "reason",
        )
        if any(not isinstance(raw.get(key), str) or not raw[key].strip() for key in required_strings):
            return VerificationResult(False, reason="github_models_verifier_output_schema_invalid")
        if type(raw.get("passed")) is not bool:
            return VerificationResult(False, reason="github_models_verifier_output_schema_invalid")
        if raw["request_hash"] != request_hash:
            return VerificationResult(False, reason="github_models_verifier_request_binding_mismatch")
        if raw["evaluator_artifact_hash"] != self.config.evaluator_artifact_hash:
            return VerificationResult(False, reason="github_models_verifier_artifact_binding_mismatch")
        if raw["evaluation_epoch_id"] != self.config.evaluation_epoch_id:
            return VerificationResult(False, reason="github_models_verifier_epoch_binding_mismatch")
        if raw["passed"] is not True:
            return VerificationResult(False, reason=raw["reason"])

        response_id = str(raw_response.get("id") or "").strip()
        response_model = str(raw_response.get("model") or self.config.model).strip()
        if not response_id:
            return VerificationResult(False, reason="github_models_verifier_pass_missing_response_identity")
        certificate_payload = {
            "schema": "GitHubModelsVerificationCertificate.v1",
            "request_hash": request_hash,
            "evaluator_artifact_hash": self.config.evaluator_artifact_hash,
            "evaluation_epoch_id": self.config.evaluation_epoch_id,
            "response_id": response_id,
            "model": response_model,
            "passed": True,
            "reason": raw["reason"],
        }
        certificate_id = "github-models-verification:" + hashlib.sha256(
            json.dumps(certificate_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return VerificationResult(True, certificate_ids=(certificate_id,), reason=raw["reason"])


__all__ = [
    "GITHUB_MODELS_ENDPOINT",
    "GitHubModelsVerificationConfig",
    "GitHubModelsVerificationProvider",
    "GitHubModelsVerifierTransport",
    "evaluator_artifact_hash",
]
