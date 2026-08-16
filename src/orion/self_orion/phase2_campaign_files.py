from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from orion.benchmarks.authority_external import assess_authority_benchmark
from orion.benchmarks.authority_external_io import load_authority_benchmark_panel
from orion.benchmarks.external_io import load_external_manifest
from orion.self_orion.development_trial_io import load_development_trial_report_v2
from orion.self_orion.phase2_campaign import (
    Phase2CampaignEvidence,
    Phase2CampaignReport,
    assess_phase2_campaign,
)
from orion.self_orion.phase2_campaign_io import (
    load_authority_trial_report,
    load_external_observation_bundle,
)
from orion.self_orion.phase2_io import load_phase2_binding
from orion.self_orion.trial_io import load_shadow_live_trial_report


BASELINE_BUNDLE_SCHEMA = "SimpleLLMRetrievalBaselineBundle.v1"


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_baseline_bundle_hash(path: Path | str) -> str:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != BASELINE_BUNDLE_SCHEMA:
        raise ValueError(f"baseline bundle schema must be {BASELINE_BUNDLE_SCHEMA}")
    recorded = raw.pop("bundle_hash", None)
    if not isinstance(recorded, str) or recorded != _canonical_hash(raw):
        raise ValueError("baseline bundle hash mismatch")
    artifacts = raw.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("baseline bundle must retain at least one task artifact")
    return recorded


@dataclass(frozen=True)
class Phase2CampaignFileSet:
    binding: Path
    live_trial: Path | None = None
    baseline_bundle: Path | None = None
    development_trial: Path | None = None
    authority_trial: Path | None = None
    authority_benchmark: Path | None = None
    external_observations: Path | None = None
    external_manifest: Path | None = None


def load_phase2_campaign_evidence(files: Phase2CampaignFileSet) -> Phase2CampaignEvidence:
    """Load and verify protected campaign artifacts without making external calls."""

    preflight = load_phase2_binding(files.binding)
    live = (
        load_shadow_live_trial_report(files.live_trial)
        if files.live_trial is not None
        else None
    )
    baseline_hash = (
        load_baseline_bundle_hash(files.baseline_bundle)
        if files.baseline_bundle is not None
        else ""
    )
    # Phase-2 closure accepts only the causally bound V2 development receipt.
    # Historical V1 receipts remain readable through phase2_campaign_io but do
    # not establish that the candidate repaired the exact observed failure.
    development = (
        load_development_trial_report_v2(files.development_trial)
        if files.development_trial is not None
        else None
    )
    authority = (
        load_authority_trial_report(files.authority_trial)
        if files.authority_trial is not None
        else None
    )
    authority_assessment = None
    if files.authority_benchmark is not None:
        panel = load_authority_benchmark_panel(files.authority_benchmark)
        authority_assessment = assess_authority_benchmark(panel)
    observations = (
        load_external_observation_bundle(files.external_observations)
        if files.external_observations is not None
        else None
    )
    external_manifest = (
        load_external_manifest(files.external_manifest)
        if files.external_manifest is not None
        else None
    )
    return Phase2CampaignEvidence(
        preflight=preflight,
        live_trial=live,
        baseline_bundle_hash=baseline_hash,
        development_trial=development,
        authority_trial=authority,
        authority_benchmark=authority_assessment,
        external_observations=observations,
        flagship_external_manifest=external_manifest,
    )


def assess_phase2_campaign_files(files: Phase2CampaignFileSet) -> Phase2CampaignReport:
    """Replay Phase-2 status from protected artifacts without external calls."""

    return assess_phase2_campaign(load_phase2_campaign_evidence(files))


__all__ = [
    "BASELINE_BUNDLE_SCHEMA",
    "Phase2CampaignFileSet",
    "assess_phase2_campaign_files",
    "load_baseline_bundle_hash",
    "load_phase2_campaign_evidence",
]
