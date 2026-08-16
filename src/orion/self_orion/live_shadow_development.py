from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from orion.engine.guards import MechanicGuard
from orion.engine.solver import SolverConfig
from orion.providers.development.artifacts import FileSystemDevelopmentArtifactStore
from orion.providers.development.sandbox_http import (
    ProtectedHTTPSandboxConfig,
    ProtectedHTTPSandboxPatchExecutor,
)
from orion.providers.experience.base import ExperienceStore
from orion.providers.live_phase2 import LivePhase2ProviderStack
from orion.runtime.runtime import OrionRuntime
from orion.self_orion.development_http import (
    ProtectedDevelopmentHTTPConfig,
    ProtectedDevelopmentHTTPEvaluator,
)
from orion.self_orion.factory import build_llm_shadow_self_driving_controller
from orion.self_orion.self_driving import ShadowSelfDrivingController


@dataclass(frozen=True)
class ShadowDevelopmentServiceManifest:
    development_worker: tuple[tuple[str, str], ...]
    sandbox_service: tuple[tuple[str, str], ...]
    assurance_service: tuple[tuple[str, str], ...]
    artifact_store: str = "filesystem-content-addressed-sha256-v1"

    @property
    def payload(self) -> dict[str, object]:
        return {
            "schema": "ShadowDevelopmentServiceManifest.v1",
            "development_worker": dict(self.development_worker),
            "sandbox_service": dict(self.sandbox_service),
            "assurance_service": dict(self.assurance_service),
            "artifact_store": self.artifact_store,
            "secret_material_included": False,
        }

    @property
    def hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True)
class LiveShadowDevelopmentStack:
    controller: ShadowSelfDrivingController
    artifact_store: FileSystemDevelopmentArtifactStore
    sandbox_executor: ProtectedHTTPSandboxPatchExecutor
    assurance_evaluator: ProtectedDevelopmentHTTPEvaluator
    manifest: ShadowDevelopmentServiceManifest

    @property
    def service_manifest_hash(self) -> str:
        return self.manifest.hash


def _identity(mapping: dict[str, object]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(key), str(value)) for key, value in mapping.items()))


def build_live_shadow_development_stack(
    *,
    provider_stack: LivePhase2ProviderStack,
    artifact_root: Path | str,
    sandbox_endpoint: str,
    sandbox_token: str,
    sandbox_artifact_hash: str,
    development_evaluator_endpoint: str,
    development_evaluator_token: str,
    base_revision: str,
    experience_store: ExperienceStore | None = None,
    config: SolverConfig | None = None,
    guards: tuple[MechanicGuard, ...] = (),
    producer_process_lineage_hash: str | None = None,
) -> LiveShadowDevelopmentStack:
    """Build the live consequential Shadow-repair stack around protected services."""

    artifact_store = FileSystemDevelopmentArtifactStore(artifact_root)
    sandbox_config = ProtectedHTTPSandboxConfig(
        endpoint=sandbox_endpoint,
        bearer_token=sandbox_token,
        sandbox_artifact_hash=sandbox_artifact_hash,
    )
    assurance_config = ProtectedDevelopmentHTTPConfig(
        endpoint=development_evaluator_endpoint,
        bearer_token=development_evaluator_token,
        evaluator_artifact_hash=provider_stack.evaluator_artifact_hash,
        evaluation_epoch_id=provider_stack.evaluation_epoch_id,
    )
    sandbox = ProtectedHTTPSandboxPatchExecutor(sandbox_config)
    assurance = ProtectedDevelopmentHTTPEvaluator(assurance_config)
    research_runtime = OrionRuntime.from_providers(
        llm=provider_stack.llm,
        retrieval=provider_stack.retrieval,
        verification=provider_stack.verification,
        experience_store=experience_store,
        config=config,
        guards=guards,
        producer_process_lineage_hash=producer_process_lineage_hash,
        evaluator_artifact_hash=provider_stack.evaluator_artifact_hash,
    )
    controller = build_llm_shadow_self_driving_controller(
        research_runtime=research_runtime,
        development_llm=provider_stack.llm,
        artifact_store=artifact_store,
        sandbox_executor=sandbox,
        protected_evaluator=assurance,
        base_revision=base_revision,
    )
    manifest = ShadowDevelopmentServiceManifest(
        development_worker=_identity(provider_stack.llm.config.public_identity),
        sandbox_service=_identity(sandbox_config.public_identity),
        assurance_service=_identity(assurance_config.public_identity),
    )
    return LiveShadowDevelopmentStack(
        controller=controller,
        artifact_store=artifact_store,
        sandbox_executor=sandbox,
        assurance_evaluator=assurance,
        manifest=manifest,
    )


def build_live_shadow_development_stack_from_env(
    *,
    provider_stack: LivePhase2ProviderStack,
    artifact_root: Path | str,
    base_revision: str,
    sandbox_endpoint_env: str = "ORION_PROTECTED_SANDBOX_URL",
    sandbox_token_env: str = "ORION_PROTECTED_SANDBOX_TOKEN",
    sandbox_artifact_hash_env: str = "ORION_PROTECTED_SANDBOX_ARTIFACT_HASH",
    development_evaluator_endpoint_env: str = "ORION_PROTECTED_DEVELOPMENT_EVALUATOR_URL",
    development_evaluator_token_env: str = "ORION_PROTECTED_DEVELOPMENT_EVALUATOR_TOKEN",
    experience_store: ExperienceStore | None = None,
    config: SolverConfig | None = None,
    guards: tuple[MechanicGuard, ...] = (),
    producer_process_lineage_hash: str | None = None,
) -> LiveShadowDevelopmentStack:
    values = {
        sandbox_endpoint_env: os.environ.get(sandbox_endpoint_env, ""),
        sandbox_token_env: os.environ.get(sandbox_token_env, ""),
        sandbox_artifact_hash_env: os.environ.get(sandbox_artifact_hash_env, ""),
        development_evaluator_endpoint_env: os.environ.get(
            development_evaluator_endpoint_env, ""
        ),
        development_evaluator_token_env: os.environ.get(
            development_evaluator_token_env, ""
        ),
    }
    missing = tuple(name for name, value in values.items() if not value)
    if missing:
        raise RuntimeError(
            "missing live Shadow development service configuration: "
            + ",".join(missing)
        )
    return build_live_shadow_development_stack(
        provider_stack=provider_stack,
        artifact_root=artifact_root,
        sandbox_endpoint=values[sandbox_endpoint_env],
        sandbox_token=values[sandbox_token_env],
        sandbox_artifact_hash=values[sandbox_artifact_hash_env],
        development_evaluator_endpoint=values[development_evaluator_endpoint_env],
        development_evaluator_token=values[development_evaluator_token_env],
        base_revision=base_revision,
        experience_store=experience_store,
        config=config,
        guards=guards,
        producer_process_lineage_hash=producer_process_lineage_hash,
    )


def write_shadow_development_service_manifest(
    stack: LiveShadowDevelopmentStack,
    path: Path | str,
) -> None:
    payload = {
        **stack.manifest.payload,
        "service_manifest_hash": stack.service_manifest_hash,
    }
    # The manifest is built exclusively from public_identity projections. It
    # contains no token/key fields by schema, so serialization does not require
    # reading private component state back out of the controller.
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "LiveShadowDevelopmentStack",
    "ShadowDevelopmentServiceManifest",
    "build_live_shadow_development_stack",
    "build_live_shadow_development_stack_from_env",
    "write_shadow_development_service_manifest",
]
