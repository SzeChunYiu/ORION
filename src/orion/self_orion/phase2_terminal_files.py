from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from orion.self_orion.phase2_campaign_files import (
    Phase2CampaignFileSet,
    load_phase2_campaign_evidence,
)
from orion.self_orion.phase2_terminal import (
    Phase2TerminalEvidence,
    Phase2TerminalReport,
    assess_phase2_terminal,
)
from orion.self_orion.phase2_terminal_io import (
    load_failure_replay_receipt,
    load_final_integration_receipt,
    load_repository_subject_attestation,
    sha256_file,
)


@dataclass(frozen=True)
class Phase2TerminalFileSet:
    campaign: Phase2CampaignFileSet
    failure_replay_receipt: Path | None = None
    frozen_failure_index: Path | None = None
    final_integration_receipt: Path | None = None
    final_subject_attestation: Path | None = None
    ci_evidence: Path | None = None
    papers_claim_ledger: Path | None = None


def assess_phase2_terminal_files(
    files: Phase2TerminalFileSet,
) -> Phase2TerminalReport:
    """Replay all Phase-2 closure gates from retained protected files only."""

    campaign = load_phase2_campaign_evidence(files.campaign)
    replay = (
        load_failure_replay_receipt(files.failure_replay_receipt)
        if files.failure_replay_receipt is not None
        else None
    )
    replay_blockers: list[str] = []
    if replay is not None:
        if files.frozen_failure_index is None:
            replay_blockers.append("frozen_failure_index_artifact_missing")
        elif (
            sha256_file(files.frozen_failure_index)
            != replay.frozen_failure_index_artifact_hash
        ):
            replay_blockers.append("frozen_failure_index_artifact_hash_mismatch")

    integration = (
        load_final_integration_receipt(files.final_integration_receipt)
        if files.final_integration_receipt is not None
        else None
    )
    integration_blockers: list[str] = []
    if integration is not None:
        if replay is None:
            integration_blockers.append("final_integration_missing_failure_replay")
        elif integration.failure_replay_artifact_hash != replay.artifact_hash:
            integration_blockers.append("final_integration_failure_replay_mismatch")

        if files.final_subject_attestation is None:
            integration_blockers.append("final_subject_attestation_missing")
        else:
            subject = load_repository_subject_attestation(files.final_subject_attestation)
            if integration.integration_commit_oid != subject.commit_oid:
                integration_blockers.append("final_integration_commit_attestation_mismatch")
            if integration.integration_tree_sha256 != subject.source_tree_sha256:
                integration_blockers.append("final_integration_tree_attestation_mismatch")

        if files.ci_evidence is None:
            integration_blockers.append("final_integration_ci_evidence_missing")
        elif sha256_file(files.ci_evidence) != integration.ci_evidence_artifact_hash:
            integration_blockers.append("final_integration_ci_evidence_hash_mismatch")

        external_manifest_path = files.campaign.external_manifest
        if external_manifest_path is None:
            integration_blockers.append("final_integration_external_manifest_missing")
        elif (
            sha256_file(external_manifest_path)
            != integration.external_manifest_artifact_hash
        ):
            integration_blockers.append(
                "final_integration_external_manifest_hash_mismatch"
            )

        if files.papers_claim_ledger is None:
            integration_blockers.append("papers_claim_ledger_artifact_missing")
        elif (
            sha256_file(files.papers_claim_ledger)
            != integration.papers_claim_ledger_artifact_hash
        ):
            integration_blockers.append("papers_claim_ledger_artifact_hash_mismatch")

    return assess_phase2_terminal(
        Phase2TerminalEvidence(
            campaign=campaign,
            failure_replay=replay,
            final_integration=integration,
            failure_replay_file_blockers=tuple(replay_blockers),
            final_integration_file_blockers=tuple(integration_blockers),
        )
    )


__all__ = ["Phase2TerminalFileSet", "assess_phase2_terminal_files"]
