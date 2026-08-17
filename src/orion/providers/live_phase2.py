from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from orion.providers.llm.github_models import GitHubModelsConfig, GitHubModelsLLMProvider
from orion.providers.llm.openai_responses import OpenAIResponsesConfig, OpenAIResponsesLLMProvider
from orion.providers.retrieval.literature import (
    CrossrefRetrievalProvider,
    EuropePMCRetrievalProvider,
    MultiSourceLiteratureRetrievalProvider,
)
from orion.providers.verification.github_models import (
    GitHubModelsVerificationConfig,
    GitHubModelsVerificationProvider,
)
from orion.providers.verification.protected_http import (
    ProtectedHTTPVerificationConfig,
    ProtectedHTTPVerificationProvider,
)


PROVIDER_MANIFEST_SCHEMA = "LivePhase2ProviderManifest.v1"
_PRIVATE_CONFIG_NAMES = (
    "OPENAI_API_KEY",
    "ORION_PROTECTED_VERIFIER_URL",
    "ORION_PROTECTED_VERIFIER_TOKEN",
    "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
    "ORION_PHASE2_EVALUATION_EPOCH_ID",
)


@dataclass(frozen=True)
class LivePhase2ProviderManifest:
    reasoner_provider: tuple[tuple[str, str], ...]
    verification_provider: tuple[tuple[str, str], ...]
    retrieval_sources: tuple[tuple[tuple[str, str], ...], ...]
    retrieval_policy: str = "strict-all-sources"

    @property
    def payload(self) -> dict[str, object]:
        return {
            "schema": PROVIDER_MANIFEST_SCHEMA,
            "reasoner_provider": dict(self.reasoner_provider),
            "verification_provider": dict(self.verification_provider),
            "retrieval_sources": [dict(item) for item in self.retrieval_sources],
            "retrieval_policy": self.retrieval_policy,
            "secret_material_included": False,
        }

    @property
    def hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True)
class LivePhase2ProviderStack:
    llm: OpenAIResponsesLLMProvider | GitHubModelsLLMProvider
    retrieval: MultiSourceLiteratureRetrievalProvider
    verification: ProtectedHTTPVerificationProvider | GitHubModelsVerificationProvider
    manifest: LivePhase2ProviderManifest

    @property
    def provider_manifest_hash(self) -> str:
        return self.manifest.hash

    @property
    def evaluator_artifact_hash(self) -> str:
        return str(self.verification.config.evaluator_artifact_hash)

    @property
    def evaluation_epoch_id(self) -> str:
        return self.verification.config.evaluation_epoch_id


def _identity_tuple(mapping: dict[str, object]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(key), str(value)) for key, value in mapping.items()))


def _retrieval_stack(crossref_mailto: str) -> tuple[
    MultiSourceLiteratureRetrievalProvider,
    tuple[tuple[tuple[str, str], ...], ...],
]:
    europe_pmc = EuropePMCRetrievalProvider()
    crossref = CrossrefRetrievalProvider(mailto=crossref_mailto)
    retrieval = MultiSourceLiteratureRetrievalProvider((europe_pmc, crossref))
    identities = (
        _identity_tuple({"provider": "europe-pmc-rest", "endpoint": europe_pmc.endpoint, "result_type": "core"}),
        _identity_tuple({"provider": "crossref-rest", "endpoint": crossref.endpoint, "query": "query.bibliographic"}),
    )
    return retrieval, identities


def _secret_values(stack: LivePhase2ProviderStack) -> tuple[str, ...]:
    secrets: list[str] = []
    for provider in (stack.llm, stack.verification):
        config = getattr(provider, "config", None)
        if config is None:
            continue
        for attribute in ("api_key", "bearer_token", "token"):
            value = getattr(config, attribute, "")
            if isinstance(value, str) and value:
                secrets.append(value)
    return tuple(secrets)


def write_live_phase2_provider_manifest(stack: LivePhase2ProviderStack, path: Path | str) -> None:
    payload = {**stack.manifest.payload, "provider_manifest_hash": stack.provider_manifest_hash}
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if any(secret in serialized for secret in _secret_values(stack)):
        raise RuntimeError("provider manifest serialization attempted to include secret material")
    Path(path).write_text(serialized, encoding="utf-8")


def load_live_phase2_provider_manifest(path: Path | str) -> LivePhase2ProviderManifest:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != PROVIDER_MANIFEST_SCHEMA:
        raise ValueError(f"provider manifest schema must be {PROVIDER_MANIFEST_SCHEMA}")
    if raw.get("secret_material_included") is not False:
        raise ValueError("provider manifest must explicitly exclude secret material")
    reasoner = raw.get("reasoner_provider")
    verification = raw.get("verification_provider")
    retrieval = raw.get("retrieval_sources")
    policy = raw.get("retrieval_policy")
    if not isinstance(reasoner, dict) or not isinstance(verification, dict):
        raise ValueError("provider manifest reasoner/verification identities must be objects")
    if not isinstance(retrieval, list) or not retrieval or any(not isinstance(item, dict) for item in retrieval):
        raise ValueError("provider manifest retrieval_sources must be a non-empty array of objects")
    if not isinstance(policy, str) or not policy.strip():
        raise ValueError("provider manifest retrieval_policy is required")
    manifest = LivePhase2ProviderManifest(
        reasoner_provider=_identity_tuple(reasoner),
        verification_provider=_identity_tuple(verification),
        retrieval_sources=tuple(_identity_tuple(item) for item in retrieval),
        retrieval_policy=policy,
    )
    if raw.get("provider_manifest_hash") != manifest.hash:
        raise ValueError("provider manifest hash mismatch")
    return manifest


def build_phase2_live_provider_stack(
    *,
    reasoner_api_key: str,
    reasoner_model: str,
    protected_verifier_endpoint: str,
    protected_verifier_token: str,
    evaluator_artifact_hash: str,
    evaluation_epoch_id: str,
    crossref_mailto: str = "",
) -> LivePhase2ProviderStack:
    """Build the private OpenAI + separately controlled HTTPS verifier stack."""

    reasoner_config = OpenAIResponsesConfig(model=reasoner_model, api_key=reasoner_api_key, store=False)
    verification_config = ProtectedHTTPVerificationConfig(
        endpoint=protected_verifier_endpoint,
        bearer_token=protected_verifier_token,
        evaluator_artifact_hash=evaluator_artifact_hash,
        evaluation_epoch_id=evaluation_epoch_id,
    )
    reasoner = OpenAIResponsesLLMProvider(reasoner_config)
    verification = ProtectedHTTPVerificationProvider(verification_config)
    retrieval, retrieval_identities = _retrieval_stack(crossref_mailto)
    manifest = LivePhase2ProviderManifest(
        reasoner_provider=_identity_tuple(reasoner_config.public_identity),
        verification_provider=_identity_tuple(verification_config.public_identity),
        retrieval_sources=retrieval_identities,
    )
    return LivePhase2ProviderStack(reasoner, retrieval, verification, manifest)


def build_phase2_github_models_provider_stack(
    *,
    github_token: str,
    reasoner_model: str,
    evaluator_model: str,
    evaluation_epoch_id: str,
    crossref_mailto: str = "",
) -> LivePhase2ProviderStack:
    """Build a credentialless-for-the-repo GitHub Models external stack.

    GitHub Actions supplies the token at runtime with `models: read`. The
    verifier has a distinct frozen model/policy identity and produces content-
    bound certificates; neither token is serialized into evidence manifests.
    """

    reasoner_config = GitHubModelsConfig(model=reasoner_model, token=github_token)
    verification_config = GitHubModelsVerificationConfig(
        model=evaluator_model,
        token=github_token,
        evaluation_epoch_id=evaluation_epoch_id,
    )
    reasoner = GitHubModelsLLMProvider(reasoner_config)
    verification = GitHubModelsVerificationProvider(verification_config)
    retrieval, retrieval_identities = _retrieval_stack(crossref_mailto)
    manifest = LivePhase2ProviderManifest(
        reasoner_provider=_identity_tuple(reasoner_config.public_identity),
        verification_provider=_identity_tuple(verification_config.public_identity),
        retrieval_sources=retrieval_identities,
    )
    return LivePhase2ProviderStack(reasoner, retrieval, verification, manifest)


def build_phase2_live_provider_stack_from_env(
    *,
    reasoner_model: str,
    reasoner_api_key_env: str = "OPENAI_API_KEY",
    protected_verifier_endpoint_env: str = "ORION_PROTECTED_VERIFIER_URL",
    protected_verifier_token_env: str = "ORION_PROTECTED_VERIFIER_TOKEN",
    evaluator_artifact_hash_env: str = "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
    evaluation_epoch_id_env: str = "ORION_PHASE2_EVALUATION_EPOCH_ID",
    crossref_mailto_env: str = "CROSSREF_MAILTO",
) -> LivePhase2ProviderStack:
    values = {
        reasoner_api_key_env: os.environ.get(reasoner_api_key_env, ""),
        protected_verifier_endpoint_env: os.environ.get(protected_verifier_endpoint_env, ""),
        protected_verifier_token_env: os.environ.get(protected_verifier_token_env, ""),
        evaluator_artifact_hash_env: os.environ.get(evaluator_artifact_hash_env, ""),
        evaluation_epoch_id_env: os.environ.get(evaluation_epoch_id_env, ""),
    }
    missing = tuple(name for name, value in values.items() if not value)
    if missing:
        raise RuntimeError("missing live Phase-2 provider configuration: " + ",".join(missing))
    return build_phase2_live_provider_stack(
        reasoner_api_key=values[reasoner_api_key_env],
        reasoner_model=reasoner_model,
        protected_verifier_endpoint=values[protected_verifier_endpoint_env],
        protected_verifier_token=values[protected_verifier_token_env],
        evaluator_artifact_hash=values[evaluator_artifact_hash_env],
        evaluation_epoch_id=values[evaluation_epoch_id_env],
        crossref_mailto=os.environ.get(crossref_mailto_env, ""),
    )


def build_phase2_auto_provider_stack_from_env(
    *,
    private_reasoner_model: str,
    github_reasoner_model: str,
    github_evaluator_model: str,
    github_evaluation_epoch_id: str,
    github_token_env: str = "GITHUB_MODELS_TOKEN",
    crossref_mailto_env: str = "CROSSREF_MAILTO",
) -> tuple[LivePhase2ProviderStack, str]:
    """Select one fully bound provider lane, never a mixed partial lane."""

    private_values = {name: os.environ.get(name, "") for name in _PRIVATE_CONFIG_NAMES}
    present = tuple(name for name, value in private_values.items() if value)
    if len(present) == len(_PRIVATE_CONFIG_NAMES):
        return (
            build_phase2_live_provider_stack(
                reasoner_api_key=private_values["OPENAI_API_KEY"],
                reasoner_model=private_reasoner_model,
                protected_verifier_endpoint=private_values["ORION_PROTECTED_VERIFIER_URL"],
                protected_verifier_token=private_values["ORION_PROTECTED_VERIFIER_TOKEN"],
                evaluator_artifact_hash=private_values["ORION_PROTECTED_VERIFIER_ARTIFACT_HASH"],
                evaluation_epoch_id=private_values["ORION_PHASE2_EVALUATION_EPOCH_ID"],
                crossref_mailto=os.environ.get(crossref_mailto_env, ""),
            ),
            "private-openai-protected-http",
        )
    if present:
        missing = tuple(name for name in _PRIVATE_CONFIG_NAMES if name not in present)
        raise RuntimeError(
            "partial private Phase-2 provider configuration is forbidden; missing: "
            + ",".join(missing)
        )
    github_token = os.environ.get(github_token_env, "")
    if not github_token:
        raise RuntimeError(f"GitHub Models fallback token is missing: {github_token_env}")
    return (
        build_phase2_github_models_provider_stack(
            github_token=github_token,
            reasoner_model=github_reasoner_model,
            evaluator_model=github_evaluator_model,
            evaluation_epoch_id=github_evaluation_epoch_id,
            crossref_mailto=os.environ.get(crossref_mailto_env, ""),
        ),
        "github-models-external",
    )


__all__ = [
    "PROVIDER_MANIFEST_SCHEMA",
    "LivePhase2ProviderManifest",
    "LivePhase2ProviderStack",
    "build_phase2_auto_provider_stack_from_env",
    "build_phase2_github_models_provider_stack",
    "build_phase2_live_provider_stack",
    "build_phase2_live_provider_stack_from_env",
    "load_live_phase2_provider_manifest",
    "write_live_phase2_provider_manifest",
]
