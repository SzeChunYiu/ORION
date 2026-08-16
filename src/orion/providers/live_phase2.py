from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from orion.providers.llm.openai_responses import (
    OpenAIResponsesConfig,
    OpenAIResponsesLLMProvider,
)
from orion.providers.retrieval.literature import (
    CrossrefRetrievalProvider,
    EuropePMCRetrievalProvider,
    MultiSourceLiteratureRetrievalProvider,
)
from orion.providers.verification.protected_http import (
    ProtectedHTTPVerificationConfig,
    ProtectedHTTPVerificationProvider,
)


PROVIDER_MANIFEST_SCHEMA = "LivePhase2ProviderManifest.v1"


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
    llm: OpenAIResponsesLLMProvider
    retrieval: MultiSourceLiteratureRetrievalProvider
    verification: ProtectedHTTPVerificationProvider
    manifest: LivePhase2ProviderManifest

    @property
    def provider_manifest_hash(self) -> str:
        return self.manifest.hash

    @property
    def evaluator_artifact_hash(self) -> str:
        return self.verification.config.evaluator_artifact_hash

    @property
    def evaluation_epoch_id(self) -> str:
        return self.verification.config.evaluation_epoch_id


def _identity_tuple(mapping: dict[str, object]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(key), str(value)) for key, value in mapping.items()))


def write_live_phase2_provider_manifest(
    stack: LivePhase2ProviderStack,
    path: Path | str,
) -> None:
    payload = {**stack.manifest.payload, "provider_manifest_hash": stack.provider_manifest_hash}
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    secrets = (stack.llm.config.api_key, stack.verification.config.bearer_token)
    if any(secret and secret in serialized for secret in secrets):
        raise RuntimeError("provider manifest serialization attempted to include secret material")
    Path(path).write_text(serialized, encoding="utf-8")


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
    """Build a concrete real-network stack with authority outside the LLM lane.

    The OpenAI model supplies semantic reasoning only. Scientific-authority
    verification is delegated to a separately controlled HTTPS service that
    must bind decisions to the frozen evaluator artifact, epoch and exact
    request hash. The protected Phase-2 campaign evaluator remains an even
    higher-level external boundary and is not constructed here.
    """

    reasoner_config = OpenAIResponsesConfig(
        model=reasoner_model,
        api_key=reasoner_api_key,
        store=False,
    )
    verification_config = ProtectedHTTPVerificationConfig(
        endpoint=protected_verifier_endpoint,
        bearer_token=protected_verifier_token,
        evaluator_artifact_hash=evaluator_artifact_hash,
        evaluation_epoch_id=evaluation_epoch_id,
    )
    reasoner = OpenAIResponsesLLMProvider(reasoner_config)
    verification = ProtectedHTTPVerificationProvider(verification_config)
    europe_pmc = EuropePMCRetrievalProvider()
    crossref = CrossrefRetrievalProvider(mailto=crossref_mailto)
    retrieval = MultiSourceLiteratureRetrievalProvider((europe_pmc, crossref))
    manifest = LivePhase2ProviderManifest(
        reasoner_provider=_identity_tuple(reasoner_config.public_identity),
        verification_provider=_identity_tuple(verification_config.public_identity),
        retrieval_sources=(
            _identity_tuple(
                {
                    "provider": "europe-pmc-rest",
                    "endpoint": europe_pmc.endpoint,
                    "result_type": "core",
                }
            ),
            _identity_tuple(
                {
                    "provider": "crossref-rest",
                    "endpoint": crossref.endpoint,
                    "query": "query.bibliographic",
                }
            ),
        ),
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


__all__ = [
    "PROVIDER_MANIFEST_SCHEMA",
    "LivePhase2ProviderManifest",
    "LivePhase2ProviderStack",
    "build_phase2_live_provider_stack",
    "build_phase2_live_provider_stack_from_env",
    "write_live_phase2_provider_manifest",
]
