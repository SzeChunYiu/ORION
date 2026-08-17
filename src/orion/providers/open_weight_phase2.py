from __future__ import annotations

from orion.providers.live_phase2 import LivePhase2ProviderManifest, LivePhase2ProviderStack
from orion.providers.llm.llama_cpp_cli import LlamaCppCLIConfig, LlamaCppCLILLMProvider
from orion.providers.retrieval.literature import (
    CrossrefRetrievalProvider,
    EuropePMCRetrievalProvider,
    MultiSourceLiteratureRetrievalProvider,
)
from orion.providers.verification.llama_cpp_cli import (
    LlamaCppCLIVerificationConfig,
    LlamaCppCLIVerificationProvider,
)


def _identity_tuple(mapping: dict[str, object]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(key), str(value)) for key, value in mapping.items()))


def build_phase2_open_weight_provider_stack(
    *,
    llama_cli_path: str,
    llama_cli_sha256: str,
    llama_runtime_release_tag: str,
    llama_runtime_commit: str,
    llama_runtime_asset_sha256: str,
    reasoner_model_path: str,
    reasoner_model_sha256: str,
    reasoner_model_repo_id: str,
    reasoner_model_revision: str,
    reasoner_model_filename: str,
    reasoner_model_family: str,
    evaluator_model_path: str,
    evaluator_model_sha256: str,
    evaluator_model_repo_id: str,
    evaluator_model_revision: str,
    evaluator_model_filename: str,
    evaluator_model_family: str,
    evaluation_epoch_id: str,
    crossref_mailto: str = "",
) -> LivePhase2ProviderStack:
    """Build a no-secret, content-addressed open-weight provider stack.

    Reasoner and protected evaluator use different model families and separate
    llama.cpp subprocesses. The model process itself has no retrieval, file,
    shell or network tool surface; literature access remains mediated through
    ORION's explicit retrieval provider.
    """

    if reasoner_model_sha256 == evaluator_model_sha256:
        raise ValueError("open-weight reasoner and evaluator model hashes must be distinct")
    if reasoner_model_family == evaluator_model_family:
        raise ValueError("open-weight reasoner and evaluator model families must be distinct")

    reasoner_config = LlamaCppCLIConfig(
        executable=llama_cli_path,
        executable_sha256=llama_cli_sha256,
        runtime_release_tag=llama_runtime_release_tag,
        runtime_commit=llama_runtime_commit,
        runtime_asset_sha256=llama_runtime_asset_sha256,
        model_path=reasoner_model_path,
        model_sha256=reasoner_model_sha256,
        model_repo_id=reasoner_model_repo_id,
        model_revision=reasoner_model_revision,
        model_filename=reasoner_model_filename,
        model_family=reasoner_model_family,
    )
    verifier_config = LlamaCppCLIVerificationConfig(
        executable=llama_cli_path,
        executable_sha256=llama_cli_sha256,
        runtime_release_tag=llama_runtime_release_tag,
        runtime_commit=llama_runtime_commit,
        runtime_asset_sha256=llama_runtime_asset_sha256,
        model_path=evaluator_model_path,
        model_sha256=evaluator_model_sha256,
        model_repo_id=evaluator_model_repo_id,
        model_revision=evaluator_model_revision,
        model_filename=evaluator_model_filename,
        model_family=evaluator_model_family,
        evaluation_epoch_id=evaluation_epoch_id,
    )
    reasoner = LlamaCppCLILLMProvider(reasoner_config)
    verification = LlamaCppCLIVerificationProvider(verifier_config)

    europe_pmc = EuropePMCRetrievalProvider()
    crossref = CrossrefRetrievalProvider(mailto=crossref_mailto)
    retrieval = MultiSourceLiteratureRetrievalProvider((europe_pmc, crossref))
    manifest = LivePhase2ProviderManifest(
        reasoner_provider=_identity_tuple(reasoner_config.public_identity),
        verification_provider=_identity_tuple(verifier_config.public_identity),
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


__all__ = ["build_phase2_open_weight_provider_stack"]
