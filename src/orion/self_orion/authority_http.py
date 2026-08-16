from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from orion.self_orion.authority_trial import (
    AuthorityAttackExecution,
    AuthorityAttackEvaluationStatus,
    AuthorityTrialBinding,
    FrozenAuthorityAttackSpec,
    ProtectedAuthorityEvaluation,
)


AuthorityHTTPTransport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoints validated HTTPS
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"authority service HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"authority service transport failed: {error.reason}") from error


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _endpoint(value: str) -> None:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("authority service endpoint must be absolute HTTPS")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("authority service endpoint cannot contain userinfo/query/fragment")


def _binding_payload(binding: AuthorityTrialBinding) -> dict[str, object]:
    return {
        "subject_revision_hash": binding.subject_revision_hash,
        "evaluator_artifact_hash": binding.evaluator_artifact_hash,
        "evaluation_epoch_id": binding.evaluation_epoch_id,
        "split_id": binding.split_id,
        "producer_process_lineage_hash": binding.producer_process_lineage_hash,
        "evaluator_process_lineage_hash": binding.evaluator_process_lineage_hash,
        "evaluator_frozen_before_candidate": binding.evaluator_frozen_before_candidate,
        "fresh_split": binding.fresh_split,
    }


@dataclass(frozen=True)
class ProtectedAuthorityExecutorHTTPConfig:
    endpoint: str
    bearer_token: str = field(repr=False)
    executor_artifact_hash: str
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        _endpoint(self.endpoint)
        if not self.bearer_token.strip() or not _sha256(self.executor_artifact_hash):
            raise ValueError("authority executor token/artifact are required")
        if self.timeout_seconds <= 0:
            raise ValueError("authority executor timeout must be positive")


class ProtectedAuthorityHTTPExecutor:
    """Remote host-owned executor for the exact frozen hostile attack specification."""

    def __init__(
        self,
        config: ProtectedAuthorityExecutorHTTPConfig,
        *,
        transport: AuthorityHTTPTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    def execute(
        self,
        attack: FrozenAuthorityAttackSpec,
        *,
        binding: AuthorityTrialBinding,
    ) -> AuthorityAttackExecution:
        payload = {
            "schema": "AuthorityAttackExecutionRequest.v1",
            "executor_artifact_hash": self.config.executor_artifact_hash,
            "attack": {
                "attack_id": attack.attack_id,
                "description": attack.description,
                "expected_outcome": attack.expected_outcome.value,
            },
            "binding": _binding_payload(binding),
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
            raise RuntimeError("authority executor response must be an object")
        if raw.get("request_hash") != request_hash:
            raise RuntimeError("authority executor request binding mismatch")
        if raw.get("executor_artifact_hash") != self.config.executor_artifact_hash:
            raise RuntimeError("authority executor artifact binding mismatch")
        if raw.get("attack_id") != attack.attack_id:
            raise RuntimeError("authority executor attack binding mismatch")
        if raw.get("subject_revision_hash") != binding.subject_revision_hash:
            raise RuntimeError("authority executor subject binding mismatch")
        if type(raw.get("candidate_authority_increased")) is not bool:
            raise RuntimeError("authority executor candidate authority flag must be boolean")
        resource = raw.get("resource_units")
        if isinstance(resource, bool) or not isinstance(resource, (int, float)) or resource < 0:
            raise RuntimeError("authority executor resource units must be non-negative")
        strings = ("artifact_id", "artifact_hash", "observed_authority_outcome", "note")
        if any(not isinstance(raw.get(name), str) or not raw[name].strip() for name in strings):
            raise RuntimeError("authority executor response identity/outcome/note fields are required")
        if not _sha256(raw["artifact_hash"]):
            raise RuntimeError("authority executor artifact hash must be SHA-256")
        return AuthorityAttackExecution(
            attack_id=attack.attack_id,
            subject_revision_hash=binding.subject_revision_hash,
            artifact_id=raw["artifact_id"],
            artifact_hash=raw["artifact_hash"],
            resource_units=float(resource),
            observed_authority_outcome=raw["observed_authority_outcome"],
            candidate_authority_increased=raw["candidate_authority_increased"],
            note=raw["note"],
        )


@dataclass(frozen=True)
class ProtectedAuthorityEvaluatorHTTPConfig:
    endpoint: str
    bearer_token: str = field(repr=False)
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        _endpoint(self.endpoint)
        if not self.bearer_token.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("authority evaluator token/epoch are required")
        if not _sha256(self.evaluator_artifact_hash):
            raise ValueError("authority evaluator artifact must be SHA-256")
        if self.timeout_seconds <= 0:
            raise ValueError("authority evaluator timeout must be positive")


class ProtectedAuthorityHTTPEvaluator:
    """Remote separately controlled evaluator for one executed hostile attack."""

    def __init__(
        self,
        config: ProtectedAuthorityEvaluatorHTTPConfig,
        *,
        transport: AuthorityHTTPTransport = _default_transport,
    ) -> None:
        self.config = config
        self._transport = transport

    def evaluate(
        self,
        attack: FrozenAuthorityAttackSpec,
        execution: AuthorityAttackExecution,
        *,
        binding: AuthorityTrialBinding,
    ) -> ProtectedAuthorityEvaluation:
        if binding.evaluator_artifact_hash != self.config.evaluator_artifact_hash:
            raise ValueError("authority evaluator config does not match trial binding")
        if binding.evaluation_epoch_id != self.config.evaluation_epoch_id:
            raise ValueError("authority evaluator epoch does not match trial binding")
        payload = {
            "schema": "ProtectedAuthorityEvaluationRequest.v1",
            "attack": {
                "attack_id": attack.attack_id,
                "description": attack.description,
                "expected_outcome": attack.expected_outcome.value,
            },
            "execution": {
                "attack_id": execution.attack_id,
                "subject_revision_hash": execution.subject_revision_hash,
                "artifact_id": execution.artifact_id,
                "artifact_hash": execution.artifact_hash,
                "resource_units": execution.resource_units,
                "observed_authority_outcome": execution.observed_authority_outcome,
                "candidate_authority_increased": execution.candidate_authority_increased,
                "note": execution.note,
            },
            "binding": _binding_payload(binding),
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
            raise RuntimeError("authority evaluator response must be an object")
        if raw.get("request_hash") != request_hash:
            raise RuntimeError("authority evaluator request binding mismatch")
        if raw.get("attack_id") != attack.attack_id:
            raise RuntimeError("authority evaluator attack binding mismatch")
        if raw.get("execution_artifact_hash") != execution.artifact_hash:
            raise RuntimeError("authority evaluator execution binding mismatch")
        if raw.get("evaluator_artifact_hash") != self.config.evaluator_artifact_hash:
            raise RuntimeError("authority evaluator artifact binding mismatch")
        if raw.get("evaluation_epoch_id") != self.config.evaluation_epoch_id:
            raise RuntimeError("authority evaluator epoch binding mismatch")
        try:
            status = AuthorityAttackEvaluationStatus(raw.get("status"))
        except ValueError as error:
            raise RuntimeError("authority evaluator returned unknown status") from error
        for name in (
            "expected_outcome_observed",
            "false_promotion_observed",
            "tamper_or_leakage_detected",
        ):
            if type(raw.get(name)) is not bool:
                raise RuntimeError(f"authority evaluator {name} must be boolean")
        evidence_ids = raw.get("evidence_ids")
        note = raw.get("note")
        if not isinstance(evidence_ids, list) or not evidence_ids or any(
            not isinstance(item, str) or not item for item in evidence_ids
        ):
            raise RuntimeError("authority evaluator evidence_ids must be non-empty strings")
        if not isinstance(note, str) or not note.strip():
            raise RuntimeError("authority evaluator note is required")
        return ProtectedAuthorityEvaluation(
            attack_id=attack.attack_id,
            execution_artifact_hash=execution.artifact_hash,
            evaluator_artifact_hash=self.config.evaluator_artifact_hash,
            evaluation_epoch_id=self.config.evaluation_epoch_id,
            status=status,
            expected_outcome_observed=raw["expected_outcome_observed"],
            false_promotion_observed=raw["false_promotion_observed"],
            tamper_or_leakage_detected=raw["tamper_or_leakage_detected"],
            evidence_ids=tuple(evidence_ids),
            note=note,
        )


__all__ = [
    "AuthorityHTTPTransport",
    "ProtectedAuthorityEvaluatorHTTPConfig",
    "ProtectedAuthorityExecutorHTTPConfig",
    "ProtectedAuthorityHTTPEvaluator",
    "ProtectedAuthorityHTTPExecutor",
]
