from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from orion.core.contributions import KnowledgeContribution
from orion.core.search import RetrievedItem
from orion.providers.llm.llama_cpp_cli import sha256_file

from .base import VerificationProvider, VerificationResult


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_VERIFIER_POLICY_SCHEMA = "LlamaCppProtectedVerifierPolicy.v1"
_VERIFIER_POLICY = (
    "You are an independent scientific evidence verifier running under protected host custody. "
    "Judge only whether the proposed knowledge contribution is faithfully and materially supported by "
    "the supplied retrieved item. Do not reward fluency, plausibility, novelty, or agreement with the "
    "candidate. Reject unsupported generalization, contradiction, citation laundering, or evidence that "
    "does not materially support the contribution. Return exactly the required JSON object. Echo the "
    "request_hash, evaluator_artifact_hash, and evaluation_epoch_id exactly. passed must be a JSON boolean "
    "and reason must be a non-empty concise string."
)
_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "request_hash",
        "evaluator_artifact_hash",
        "evaluation_epoch_id",
        "passed",
        "reason",
    ],
    "properties": {
        "request_hash": {"type": "string"},
        "evaluator_artifact_hash": {"type": "string"},
        "evaluation_epoch_id": {"type": "string"},
        "passed": {"type": "boolean"},
        "reason": {"type": "string", "minLength": 1},
    },
}


def _require_sha256(value: str, field: str) -> None:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256 hex digest")


def evaluator_artifact_hash(
    *,
    runtime_release_tag: str,
    runtime_commit: str,
    runtime_asset_sha256: str,
    runtime_binary_sha256: str,
    model_repo_id: str,
    model_revision: str,
    model_filename: str,
    model_sha256: str,
    model_family: str,
) -> str:
    payload = {
        "schema": _VERIFIER_POLICY_SCHEMA,
        "provider": "llama-cpp-cli-protected-verifier",
        "runtime_release_tag": runtime_release_tag,
        "runtime_commit": runtime_commit,
        "runtime_asset_sha256": runtime_asset_sha256,
        "runtime_binary_sha256": runtime_binary_sha256,
        "model_repo_id": model_repo_id,
        "model_revision": model_revision,
        "model_filename": model_filename,
        "model_sha256": model_sha256,
        "model_family": model_family,
        "policy": _VERIFIER_POLICY,
        "output_schema": _OUTPUT_SCHEMA,
        "tool_access": "NONE",
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class LlamaCppCLIVerificationConfig:
    executable: str
    executable_sha256: str
    runtime_release_tag: str
    runtime_commit: str
    runtime_asset_sha256: str
    model_path: str
    model_sha256: str
    model_repo_id: str
    model_revision: str
    model_filename: str
    model_family: str
    evaluation_epoch_id: str
    evaluator_artifact_hash: str | None = None
    context_size: int = 4096
    max_tokens: int = 384
    seed: int = 20260817
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        for field, value in (
            ("executable_sha256", self.executable_sha256),
            ("runtime_asset_sha256", self.runtime_asset_sha256),
            ("model_sha256", self.model_sha256),
        ):
            _require_sha256(value, field)
        if not self.evaluation_epoch_id.strip():
            raise ValueError("evaluation_epoch_id is required")
        if not self.model_family.strip():
            raise ValueError("model_family is required")
        if self.context_size <= 0 or self.max_tokens <= 0 or self.timeout_seconds <= 0:
            raise ValueError("verifier context, max tokens and timeout must be positive")
        executable = Path(self.executable)
        model = Path(self.model_path)
        if not executable.is_file() or not model.is_file():
            raise ValueError("llama.cpp verifier executable/model must exist")
        if sha256_file(executable) != self.executable_sha256:
            raise ValueError("llama.cpp verifier executable SHA-256 mismatch")
        if sha256_file(model) != self.model_sha256:
            raise ValueError("llama.cpp verifier model SHA-256 mismatch")
        expected = evaluator_artifact_hash(
            runtime_release_tag=self.runtime_release_tag,
            runtime_commit=self.runtime_commit,
            runtime_asset_sha256=self.runtime_asset_sha256,
            runtime_binary_sha256=self.executable_sha256,
            model_repo_id=self.model_repo_id,
            model_revision=self.model_revision,
            model_filename=self.model_filename,
            model_sha256=self.model_sha256,
            model_family=self.model_family,
        )
        if self.evaluator_artifact_hash is None:
            object.__setattr__(self, "evaluator_artifact_hash", expected)
        elif self.evaluator_artifact_hash != expected:
            raise ValueError("evaluator_artifact_hash does not bind frozen verifier/runtime/model")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "llama-cpp-cli-protected-verifier",
            "runtime_release_tag": self.runtime_release_tag,
            "runtime_commit": self.runtime_commit,
            "runtime_asset_sha256": self.runtime_asset_sha256,
            "runtime_binary_sha256": self.executable_sha256,
            "model_repo_id": self.model_repo_id,
            "model_revision": self.model_revision,
            "model_filename": self.model_filename,
            "model_sha256": self.model_sha256,
            "model_family": self.model_family,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "context_size": self.context_size,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
            "timeout_seconds": self.timeout_seconds,
            "tool_access": "NONE",
        }


class LlamaCppCLIVerificationProvider(VerificationProvider):
    """Protected open-weight verifier using a distinct content-addressed model."""

    def __init__(self, config: LlamaCppCLIVerificationConfig) -> None:
        self.config = config

    @staticmethod
    def _minimal_env(home: Path) -> dict[str, str]:
        return {
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(home),
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8",
            "NO_COLOR": "1",
        }

    @staticmethod
    def _request_payload(
        contribution: KnowledgeContribution,
        item: RetrievedItem,
        config: LlamaCppCLIVerificationConfig,
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

    def verify(self, contribution: KnowledgeContribution, item: RetrievedItem) -> VerificationResult:
        if item.item_id not in contribution.evidence_ids:
            return VerificationResult(False, reason="contribution_does_not_bind_the_item_being_verified")
        payload = self._request_payload(contribution, item, self.config)
        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        bound = {**payload, "request_hash": request_hash}
        prompt = json.dumps(bound, sort_keys=True, separators=(",", ":"))
        with tempfile.TemporaryDirectory(prefix="orion-llama-verifier-") as directory:
            root = Path(directory)
            home = root / "home"
            work = root / "work"
            home.mkdir()
            work.mkdir()
            command = [
                self.config.executable,
                "-m",
                self.config.model_path,
                "-st",
                "--simple-io",
                "--no-warmup",
                "--no-display-prompt",
                "--no-show-timings",
                "--temp",
                "0",
                "--seed",
                str(self.config.seed),
                "-c",
                str(self.config.context_size),
                "-n",
                str(self.config.max_tokens),
                "-sys",
                _VERIFIER_POLICY,
                "-p",
                prompt,
                "--json-schema",
                json.dumps(_OUTPUT_SCHEMA, separators=(",", ":")),
            ]
            try:
                completed = subprocess.run(
                    command,
                    cwd=work,
                    env=self._minimal_env(home),
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return VerificationResult(False, reason="llama_cpp_verifier_timeout")
        if completed.returncode != 0:
            return VerificationResult(False, reason="llama_cpp_verifier_process_failed")
        external_output = completed.stdout.strip()
        if not external_output:
            return VerificationResult(False, reason="llama_cpp_verifier_output_empty")
        try:
            raw = json.loads(external_output)
        except json.JSONDecodeError:
            return VerificationResult(False, reason="llama_cpp_verifier_output_unparseable")
        if not isinstance(raw, dict) or set(raw) != set(_OUTPUT_SCHEMA["required"]):
            return VerificationResult(False, reason="llama_cpp_verifier_output_schema_invalid")
        for field in ("request_hash", "evaluator_artifact_hash", "evaluation_epoch_id", "reason"):
            if not isinstance(raw.get(field), str) or not raw[field].strip():
                return VerificationResult(False, reason="llama_cpp_verifier_output_schema_invalid")
        if type(raw.get("passed")) is not bool:
            return VerificationResult(False, reason="llama_cpp_verifier_output_schema_invalid")
        if raw["request_hash"] != request_hash:
            return VerificationResult(False, reason="llama_cpp_verifier_request_binding_mismatch")
        if raw["evaluator_artifact_hash"] != self.config.evaluator_artifact_hash:
            return VerificationResult(False, reason="llama_cpp_verifier_artifact_binding_mismatch")
        if raw["evaluation_epoch_id"] != self.config.evaluation_epoch_id:
            return VerificationResult(False, reason="llama_cpp_verifier_epoch_binding_mismatch")
        if raw["passed"] is not True:
            return VerificationResult(False, reason=raw["reason"])
        certificate_payload = {
            "schema": "LlamaCppVerificationCertificate.v1",
            "request_hash": request_hash,
            "evaluator_artifact_hash": self.config.evaluator_artifact_hash,
            "evaluation_epoch_id": self.config.evaluation_epoch_id,
            "runtime_binary_sha256": self.config.executable_sha256,
            "model_sha256": self.config.model_sha256,
            "external_output_sha256": hashlib.sha256(external_output.encode("utf-8")).hexdigest(),
            "passed": True,
            "reason": raw["reason"],
        }
        certificate_id = "llama-cpp-verification:" + hashlib.sha256(
            json.dumps(certificate_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return VerificationResult(True, certificate_ids=(certificate_id,), reason=raw["reason"])


__all__ = [
    "LlamaCppCLIVerificationConfig",
    "LlamaCppCLIVerificationProvider",
    "evaluator_artifact_hash",
]
