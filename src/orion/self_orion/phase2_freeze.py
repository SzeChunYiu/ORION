from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from orion.providers.live_phase2 import (
    LivePhase2ProviderManifest,
    load_live_phase2_provider_manifest,
)
from orion.self_orion.phase2_io import write_phase2_binding
from orion.self_orion.phase2_preflight import (
    FrozenPacketBinding,
    Phase2ClosurePreflight,
    Phase2PreflightStatus,
    assess_phase2_preflight,
    build_frozen_live_trial_packet,
)
from orion.self_orion.subject_binding import (
    RepositorySubjectAttestation,
    attest_repository_subject,
    write_repository_subject_attestation,
)


@dataclass(frozen=True)
class FrozenPhase2BindingReport:
    subject: RepositorySubjectAttestation
    provider_manifest: LivePhase2ProviderManifest
    preflight: Phase2ClosurePreflight
    live_trial_packet_fingerprint: str

    @property
    def subject_revision_hash(self) -> str:
        return self.subject.subject_revision_hash

    @property
    def provider_manifest_hash(self) -> str:
        return self.provider_manifest.hash


def freeze_phase2_binding(
    *,
    repository_root: Path | str,
    provider_manifest_path: Path | str,
    subject_output_path: Path | str,
    binding_output_path: Path | str,
    resource_budget_units: float,
    baseline_id: str = "simple-llm-retrieval-baseline-v1",
    protocol_id: str = "phase2-shadow-closure-v1",
    repository_identity: str | None = None,
    frozen_packet: FrozenPacketBinding | None = None,
) -> FrozenPhase2BindingReport:
    """Freeze exact subject/provider/evaluator identities into the Phase-2 binding."""

    subject = attest_repository_subject(
        repository_root,
        repository_identity=repository_identity,
    )
    manifest = load_live_phase2_provider_manifest(provider_manifest_path)
    verification = dict(manifest.verification_provider)
    evaluator_artifact_hash = verification.get("evaluator_artifact_hash", "")
    evaluation_epoch_id = verification.get("evaluation_epoch_id", "")
    if not evaluator_artifact_hash or not evaluation_epoch_id:
        raise ValueError(
            "provider manifest verification identity must bind evaluator artifact and evaluation epoch"
        )
    # This tool CREATES a freeze; it does not verify one. At creation time there
    # is no prior expectation to compare against, so when the caller declares
    # none we bind the expectation to the values just attested: the real subject
    # revision, the real provider manifest hash, the real evaluator identity.
    # That is materially stronger than the shape check it replaces -- fabricated
    # hashes cannot reach here, because `attest_repository_subject` and
    # `load_live_phase2_provider_manifest` compute these from actual artifacts.
    #
    # Verifying a STORED freeze against live values is the execution-time job,
    # and there the caller must pass the published packet explicitly.
    if frozen_packet is None:
        frozen_packet = FrozenPacketBinding(
            packet_fingerprint="",
            subject_revision_hash=subject.subject_revision_hash,
            provider_manifest_hash=manifest.hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
            evaluation_epoch_id=evaluation_epoch_id,
            baseline_id=baseline_id,
            resource_budget_units=resource_budget_units,
            task_ids=tuple(
                task.task_id for task in Phase2ClosurePreflight.__dataclass_fields__["tasks"].default
            ),
        )
    preflight = Phase2ClosurePreflight(
        protocol_id=protocol_id,
        subject_revision_hash=subject.subject_revision_hash,
        provider_manifest_hash=manifest.hash,
        evaluator_artifact_hash=evaluator_artifact_hash,
        evaluation_epoch_id=evaluation_epoch_id,
        baseline_id=baseline_id,
        resource_budget_units=resource_budget_units,
        frozen_packet=frozen_packet,
    )
    assessed = assess_phase2_preflight(preflight)
    if assessed.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL:
        raise RuntimeError(
            "frozen Phase-2 binding is not executable: " + ",".join(assessed.blockers)
        )
    packet = build_frozen_live_trial_packet(preflight)
    write_repository_subject_attestation(subject, subject_output_path)
    write_phase2_binding(preflight, binding_output_path)
    return FrozenPhase2BindingReport(
        subject=subject,
        provider_manifest=manifest,
        preflight=preflight,
        live_trial_packet_fingerprint=packet.fingerprint,
    )


__all__ = ["FrozenPhase2BindingReport", "freeze_phase2_binding"]
