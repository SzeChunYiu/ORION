from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from orion.core.contributions import KnowledgeContribution
from orion.core.search import RetrievedItem

from .base import VerificationProvider, VerificationResult


_VERIFIER_SCHEMA = "CopilotCLIProtectedVerifierPolicy.v1"
_VERIFIER_POLICY = (
    "You are an independent scientific evidence verifier. Judge only whether the proposed knowledge "
    "contribution is faithfully and materially supported by the supplied retrieved item. Do not reward "
    "fluency, plausibility, novelty, or agreement with the candidate. Reject unsupported generalization, "
    "contradiction, citation laundering, or evidence that does not materially support the contribution. "
    "Return one JSON object only with exactly request_hash, evaluator_artifact_hash, evaluation_epoch_id, "
    "passed, reason. Echo the three binding fields exactly. passed must be a JSON boolean; reason must be "
    "a non-empty concise string. Do not invoke tools."
)


def evaluator_artifact_hash(model: str, cli_version: str) -> str:
    payload = {
        "schema": _VERIFIER_SCHEMA,
        "provider": "github-copilot-cli",
        "model": model,
        "cli_version": cli_version,
        "policy": _VERIFIER_POLICY,
        "tool_access": "DENIED",
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
class CopilotCLIVerificationConfig:
    model: str
    token: str = field(repr=False)
    cli_version: str
    evaluation_epoch_id: str
    evaluator_artifact_hash: str | None = None
    executable: str = "copilot"
    timeout_seconds: float = 180.0

    def __post_init__(self) -> None:
        if not self.model.strip() or not self.token.strip() or not self.cli_version.strip():
            raise ValueError("Copilot CLI verifier model, token and CLI version are required")
        if not self.evaluation_epoch_id.strip():
            raise ValueError("Copilot CLI verifier evaluation epoch is required")
        if self.executable != "copilot":
            raise ValueError("Copilot CLI verifier executable identity is frozen to 'copilot'")
        if self.timeout_seconds <= 0:
            raise ValueError("Copilot CLI verifier timeout must be positive")
        expected = evaluator_artifact_hash(self.model, self.cli_version)
        if self.evaluator_artifact_hash is None:
            object.__setattr__(self, "evaluator_artifact_hash", expected)
        elif self.evaluator_artifact_hash != expected:
            raise ValueError("Copilot CLI evaluator artifact hash does not bind frozen policy/runtime")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "github-copilot-cli-protected-verifier",
            "model": self.model,
            "cli_version": self.cli_version,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "programmatic": True,
            "tool_access": "DENIED",
            "timeout_seconds": self.timeout_seconds,
        }


class CopilotCLIVerificationProvider(VerificationProvider):
    """Prompt-only protected verifier backed by a separately pinned Copilot model.

    The evaluator runs in a fresh empty directory with a minimal environment,
    no built-in MCPs, and shell/read/write/url/memory tools denied. Its verdict
    must echo exact request/artifact/epoch bindings; the host derives a content-
    addressed certificate from the externally produced verdict rather than
    trusting candidate- or model-supplied certificate identifiers.
    """

    def __init__(self, config: CopilotCLIVerificationConfig) -> None:
        self.config = config

    @staticmethod
    def _request_payload(
        contribution: KnowledgeContribution,
        item: RetrievedItem,
        config: CopilotCLIVerificationConfig,
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

    def _environment(self, home: Path) -> dict[str, str]:
        return {
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(home),
            "CI": "true",
            "NO_COLOR": "1",
            "COPILOT_AUTO_UPDATE": "false",
            "COPILOT_GITHUB_TOKEN": self.config.token,
            "GITHUB_TOKEN": self.config.token,
        }

    def verify(self, contribution: KnowledgeContribution, item: RetrievedItem) -> VerificationResult:
        if item.item_id not in contribution.evidence_ids:
            return VerificationResult(False, reason="contribution_does_not_bind_the_item_being_verified")

        payload = self._request_payload(contribution, item, self.config)
        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        bound = {**payload, "request_hash": request_hash}
        prompt = (
            "SYSTEM INSTRUCTION:\n"
            + _VERIFIER_POLICY
            + "\n\nFROZEN VERIFICATION REQUEST:\n"
            + json.dumps(bound, sort_keys=True, separators=(",", ":"))
        )

        with tempfile.TemporaryDirectory(prefix="orion-copilot-verifier-") as directory:
            root = Path(directory)
            home = root / "home"
            work = root / "work"
            home.mkdir()
            work.mkdir()
            command = [
                self.config.executable,
                "-s",
                "-p",
                prompt,
                "--model",
                self.config.model,
                "--no-ask-user",
                "--disable-builtin-mcps",
                "--deny-tool=shell",
                "--deny-tool=write",
                "--deny-tool=read",
                "--deny-tool=url",
                "--deny-tool=memory",
                "--excluded-tools=task,skill,web_fetch,bash,edit,view,grep,glob",
                "--secret-env-vars=COPILOT_GITHUB_TOKEN,GITHUB_TOKEN",
            ]
            try:
                completed = subprocess.run(
                    command,
                    cwd=work,
                    env=self._environment(home),
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return VerificationResult(False, reason="copilot_cli_verifier_timeout")
            if completed.returncode != 0:
                return VerificationResult(False, reason="copilot_cli_verifier_process_failed")
            external_output = completed.stdout.strip()
            if not external_output:
                return VerificationResult(False, reason="copilot_cli_verifier_output_empty")

        try:
            raw = json.loads(external_output)
        except json.JSONDecodeError:
            return VerificationResult(False, reason="copilot_cli_verifier_output_unparseable")
        if not isinstance(raw, dict):
            return VerificationResult(False, reason="copilot_cli_verifier_output_not_object")
        if set(raw) != {
            "request_hash",
            "evaluator_artifact_hash",
            "evaluation_epoch_id",
            "passed",
            "reason",
        }:
            return VerificationResult(False, reason="copilot_cli_verifier_output_schema_invalid")
        for field_name in (
            "request_hash",
            "evaluator_artifact_hash",
            "evaluation_epoch_id",
            "reason",
        ):
            if not isinstance(raw.get(field_name), str) or not raw[field_name].strip():
                return VerificationResult(False, reason="copilot_cli_verifier_output_schema_invalid")
        if type(raw.get("passed")) is not bool:
            return VerificationResult(False, reason="copilot_cli_verifier_output_schema_invalid")
        if raw["request_hash"] != request_hash:
            return VerificationResult(False, reason="copilot_cli_verifier_request_binding_mismatch")
        if raw["evaluator_artifact_hash"] != self.config.evaluator_artifact_hash:
            return VerificationResult(False, reason="copilot_cli_verifier_artifact_binding_mismatch")
        if raw["evaluation_epoch_id"] != self.config.evaluation_epoch_id:
            return VerificationResult(False, reason="copilot_cli_verifier_epoch_binding_mismatch")
        if raw["passed"] is not True:
            return VerificationResult(False, reason=raw["reason"])

        certificate_payload = {
            "schema": "CopilotCLIVerificationCertificate.v1",
            "request_hash": request_hash,
            "evaluator_artifact_hash": self.config.evaluator_artifact_hash,
            "evaluation_epoch_id": self.config.evaluation_epoch_id,
            "provider": "github-copilot-cli",
            "model": self.config.model,
            "cli_version": self.config.cli_version,
            "external_output_sha256": hashlib.sha256(external_output.encode("utf-8")).hexdigest(),
            "passed": True,
            "reason": raw["reason"],
        }
        certificate_id = "copilot-cli-verification:" + hashlib.sha256(
            json.dumps(certificate_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return VerificationResult(True, certificate_ids=(certificate_id,), reason=raw["reason"])


__all__ = [
    "CopilotCLIVerificationConfig",
    "CopilotCLIVerificationProvider",
    "evaluator_artifact_hash",
]
