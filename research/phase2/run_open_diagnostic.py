#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from orion.engine.solver import SolverConfig
from orion.providers.llm.ollama import OllamaConfig, OllamaLLMProvider
from orion.providers.retrieval.literature import (
    CrossrefRetrievalProvider,
    EuropePMCRetrievalProvider,
    MultiSourceLiteratureRetrievalProvider,
)
from orion.providers.verification.base import VerificationResult
from orion.self_orion.baseline import (
    SimpleLLMRetrievalBaseline,
    write_baseline_bundle,
)
from orion.self_orion.live_trial import FrozenLiveTrialPacket, ShadowLiveTrialRunner
from orion.self_orion.phase2_preflight import DEEP_TARGET_TASK, WIDE_LITERATURE_TASK
from orion.self_orion.trial_io import write_shadow_live_trial_report


DIAGNOSTIC_SCHEMA = "Phase2OpenLiveDiagnostic.v1"
DIAGNOSTIC_EPOCH = "phase2:open-live-diagnostic:2026-08-16"
DIAGNOSTIC_BASELINE_ID = "simple-llm-retrieval-baseline-v1"


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class UnavailableProtectedVerifier:
    """Fail-closed authority boundary used only for open live diagnostics."""

    reason: str = "protected_verifier_unavailable_in_open_diagnostic"

    def verify(self, contribution, item) -> VerificationResult:
        return VerificationResult(False, reason=self.reason)


@dataclass(frozen=True)
class DiagnosticIdentity:
    model: str
    ollama_endpoint: str
    europe_pmc_endpoint: str
    crossref_endpoint: str

    @property
    def provider_manifest(self) -> dict[str, object]:
        return {
            "schema": "Phase2OpenDiagnosticProviderManifest.v1",
            "reasoner": {
                "provider": "ollama-loopback-chat",
                "endpoint": self.ollama_endpoint,
                "model": self.model,
                "authority_role": "semantic-reasoner-only",
            },
            "retrieval": [
                {
                    "provider": "europe-pmc-rest",
                    "endpoint": self.europe_pmc_endpoint,
                    "result_type": "core",
                },
                {
                    "provider": "crossref-rest",
                    "endpoint": self.crossref_endpoint,
                    "query": "query.bibliographic",
                },
            ],
            "retrieval_policy": "strict-all-sources",
            "verification": {
                "provider": "unavailable-protected-verifier",
                "passed_verification_possible": False,
                "reason": "protected_verifier_unavailable_in_open_diagnostic",
            },
            "closure_eligible": False,
            "secret_material_included": False,
        }

    @property
    def provider_manifest_hash(self) -> str:
        return _canonical_hash(self.provider_manifest)

    @property
    def evaluator_artifact_hash(self) -> str:
        return _canonical_hash(
            {
                "schema": "Phase2OpenDiagnosticNoAuthorityEvaluator.v1",
                "passed_verification_possible": False,
                "reason": "protected_verifier_unavailable_in_open_diagnostic",
            }
        )


def _summary(report, baseline, *, identity: DiagnosticIdentity) -> dict[str, object]:
    return {
        "schema": DIAGNOSTIC_SCHEMA,
        "subject_commit": os.environ.get("GITHUB_SHA", "local-unbound"),
        "evaluation_epoch_id": DIAGNOSTIC_EPOCH,
        "provider_manifest_hash": identity.provider_manifest_hash,
        "evaluator_artifact_hash": identity.evaluator_artifact_hash,
        "protected_verification_available": False,
        "closure_eligible": False,
        "grants_phase2_closure": False,
        "grants_governed_self_orion": False,
        "packet_id": report.packet_id,
        "packet_fingerprint": report.packet_fingerprint,
        "evidence_artifact_hash": report.evidence_artifact_hash,
        "raw_search_trace_retained": report.raw_search_trace_retained,
        "all_failures_recordable": report.all_failures_recordable,
        "all_resource_matched": report.all_resource_matched,
        "tasks": [
            {
                "task_id": item.task_id,
                "kind": item.kind.value,
                "orion_status": item.orion_status.value,
                "orion_evidence_count": item.orion_evidence_count,
                "orion_residual_count": item.orion_residual_count,
                "orion_resource_units": item.orion_resource_units,
                "baseline_solved": item.baseline_solved,
                "baseline_evidence_count": item.baseline_evidence_count,
                "baseline_residual_count": item.baseline_residual_count,
                "baseline_resource_units": item.baseline_resource_units,
                "resource_matched": item.resource_matched,
                "raw_query_count": item.raw_query_count,
                "raw_retrieved_item_count": item.raw_retrieved_item_count,
                "retrieved_but_unused_count": len(item.retrieved_but_unused_ids),
                "retrieved_but_unabsorbed_count": len(
                    item.retrieved_but_unabsorbed_ids
                ),
                "root_episode_recorded": item.root_episode_id is not None,
                "mechanic_episode_count": len(item.mechanic_episode_ids),
            }
            for item in report.comparisons
        ],
        "baseline_artifact_hashes": {
            artifact.task_id: artifact.artifact_hash for artifact in baseline.artifacts
        },
        "boundary": (
            "This is a real-network/open-weight diagnostic, not Phase-2 closure evidence. "
            "The reasoner and public literature retrieval are live, but the verifier is deliberately fail-closed and cannot mint VERIFIED authority."
        ),
    }


def run(*, model: str, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    llm = OllamaLLMProvider(OllamaConfig(model=model))
    europe_pmc = EuropePMCRetrievalProvider()
    crossref = CrossrefRetrievalProvider(mailto=os.environ.get("CROSSREF_MAILTO", ""))
    retrieval = MultiSourceLiteratureRetrievalProvider((europe_pmc, crossref))
    verifier = UnavailableProtectedVerifier()
    identity = DiagnosticIdentity(
        model=model,
        ollama_endpoint=llm.config.endpoint,
        europe_pmc_endpoint=europe_pmc.endpoint,
        crossref_endpoint=crossref.endpoint,
    )
    baseline = SimpleLLMRetrievalBaseline(
        llm=llm,
        retrieval=retrieval,
        max_results=8,
    )
    runner = ShadowLiveTrialRunner.from_providers(
        llm=llm,
        retrieval=retrieval,
        verification=verifier,
        baseline=baseline,
        config=SolverConfig(
            max_iterations=6,
            search_limit_per_query=8,
            require_verified_answer=True,
        ),
        evaluator_artifact_hash=identity.evaluator_artifact_hash,
    )
    packet = FrozenLiveTrialPacket(
        packet_id="phase2:open-live-diagnostic:v1",
        evaluation_epoch_id=DIAGNOSTIC_EPOCH,
        tasks=(WIDE_LITERATURE_TASK.to_trial_task(), DEEP_TARGET_TASK.to_trial_task()),
        provider_manifest_hash=identity.provider_manifest_hash,
        evaluator_artifact_hash=identity.evaluator_artifact_hash,
        baseline_id=DIAGNOSTIC_BASELINE_ID,
        resource_budget_units=120.0,
        max_orion_to_baseline_resource_ratio=1.0,
    )
    report = runner.run(packet)

    provider_payload = {
        **identity.provider_manifest,
        "provider_manifest_hash": identity.provider_manifest_hash,
    }
    (output_dir / "provider-manifest.json").write_text(
        json.dumps(provider_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_shadow_live_trial_report(report, output_dir / "live-trial.json")
    write_baseline_bundle(baseline, output_dir / "baseline.json")
    summary = _summary(report, baseline, identity=identity)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3:0.6b")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = run(model=args.model, output_dir=args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
