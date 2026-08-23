#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from orion.engine.solver import SolverConfig
from orion.providers.experience.memory import InMemoryExperienceStore
from orion.providers.llm.ollama import OllamaConfig, OllamaLLMProvider
from orion.providers.retrieval.literature import (
    CrossrefRetrievalProvider,
    EuropePMCRetrievalProvider,
    MultiSourceLiteratureRetrievalProvider,
)
from orion.providers.verification.base import VerificationResult
from orion.self_orion.baseline import SimpleLLMRetrievalBaseline, write_baseline_bundle
from orion.self_orion.live_accounted import AccountedShadowLiveTrialRunner
from orion.self_orion.live_trial import FrozenLiveTrialPacket
from orion.self_orion.phase2_preflight import DEEP_TARGET_TASK, WIDE_LITERATURE_TASK
from orion.self_orion.trial_io import write_shadow_live_trial_report


DIAGNOSTIC_SCHEMA = "Phase2OpenLiveDiagnostic.v1"
DIAGNOSTIC_EPOCH = "phase2:open-live-diagnostic:2026-08-16"
DIAGNOSTIC_BASELINE_ID = "simple-llm-retrieval-baseline-v1"
RETRIEVAL_CALL_COST_UNITS = 1.0
LLM_CALL_COST_UNITS = 1.0


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _ollama_model_digest(model: str) -> str:
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/tags",
        headers={"Accept": "application/json", "User-Agent": "orion-research-os/0.1"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=30.0) as response:  # noqa: S310 - loopback-only
        raw = json.loads(response.read())
    models = raw.get("models", []) if isinstance(raw, dict) else []
    if not isinstance(models, list):
        raise RuntimeError("Ollama /api/tags response models must be an array")
    for record in models:
        if not isinstance(record, dict):
            continue
        if record.get("name") != model and record.get("model") != model:
            continue
        digest = record.get("digest")
        if not isinstance(digest, str):
            break
        normalized = digest.removeprefix("sha256:")
        if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
            break
        return normalized
    raise RuntimeError(f"Ollama model digest unavailable for pulled model: {model}")


@dataclass(frozen=True)
class UnavailableProtectedVerifier:
    """Fail-closed authority boundary used only for open live diagnostics."""

    reason: str = "protected_verifier_unavailable_in_open_diagnostic"

    def verify(self, contribution, item) -> VerificationResult:
        return VerificationResult(False, reason=self.reason)


@dataclass(frozen=True)
class DiagnosticIdentity:
    model: str
    model_digest: str
    ollama_endpoint: str
    europe_pmc_endpoint: str
    crossref_endpoint: str

    def __post_init__(self) -> None:
        if len(self.model_digest) != 64 or any(
            ch not in "0123456789abcdef" for ch in self.model_digest
        ):
            raise ValueError("diagnostic model digest must be SHA-256")

    @property
    def provider_manifest(self) -> dict[str, object]:
        return {
            "schema": "Phase2OpenDiagnosticProviderManifest.v1",
            "reasoner": {
                "provider": "ollama-loopback-chat",
                "endpoint": self.ollama_endpoint,
                "model": self.model,
                "model_digest_sha256": self.model_digest,
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
            "resource_accounting": {
                "unit": "provider-call",
                "retrieval_call_cost_units": RETRIEVAL_CALL_COST_UNITS,
                "llm_call_cost_units": LLM_CALL_COST_UNITS,
                "attempted_calls_count_even_when_provider_fails": True,
            },
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


def _summary(
    report,
    baseline,
    *,
    identity: DiagnosticIdentity,
    experience_store: InMemoryExperienceStore,
    runner: AccountedShadowLiveTrialRunner,
) -> dict[str, object]:
    return {
        "schema": DIAGNOSTIC_SCHEMA,
        "subject_commit": os.environ.get("GITHUB_SHA", "local-unbound"),
        "evaluation_epoch_id": DIAGNOSTIC_EPOCH,
        "reasoner_model": identity.model,
        "reasoner_model_digest_sha256": identity.model_digest,
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
        "recorded_episode_count": len(experience_store.episodes()),
        "resource_accounting": {
            "unit": "provider-call",
            "retrieval_call_cost_units": RETRIEVAL_CALL_COST_UNITS,
            "llm_call_cost_units": LLM_CALL_COST_UNITS,
        },
        "tasks": [
            {
                "task_id": item.task_id,
                "kind": item.kind.value,
                "orion_status": item.orion_status.value,
                "orion_evidence_count": item.orion_evidence_count,
                "orion_residual_count": item.orion_residual_count,
                "orion_resource_units": item.orion_resource_units,
                "orion_llm_call_count": runner.llm_calls_for_task(item.task_id),
                "orion_retrieval_call_count": item.raw_query_count,
                "baseline_solved": item.baseline_solved,
                "baseline_evidence_count": item.baseline_evidence_count,
                "baseline_residual_count": item.baseline_residual_count,
                "baseline_resource_units": item.baseline_resource_units,
                "resource_matched": item.resource_matched,
                "raw_query_count": item.raw_query_count,
                "raw_retrieved_item_count": item.raw_retrieved_item_count,
                "retrieved_but_unused_count": len(item.retrieved_but_unused_ids),
                "retrieved_but_unabsorbed_count": len(item.retrieved_but_unabsorbed_ids),
                "root_episode_id": item.root_episode_id,
                "mechanic_episode_ids": list(item.mechanic_episode_ids),
                "solution_evidence_ids": list(item.solution_evidence_ids),
                "absorbed_evidence_ids": list(item.absorbed_evidence_ids),
                "search_queries": [
                    {
                        "query_id": observation.query_id,
                        "query_text": observation.query_text,
                        "route_id": observation.route_id,
                        "route_kind": observation.route_kind,
                        "retrieved_count": len(observation.items),
                    }
                    for observation in item.search_observations
                ],
                "mechanic_trace": [
                    {
                        "operator": event.operator,
                        "mechanic_id": event.mechanic_id,
                        "status": event.status,
                        "summary": event.summary,
                        "residual_ids": list(event.residual_ids),
                        "failure_signature": list(event.failure_signature),
                        "evidence_ids": list(event.evidence_ids),
                    }
                    for event in item.mechanic_trace
                ],
            }
            for item in report.comparisons
        ],
        "llm_call_observations": [
            {
                "task": observation.task,
                "problem_id": observation.problem_id,
                "completed": observation.completed,
            }
            for observation in runner.llm_call_observations
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
    model_digest = _ollama_model_digest(model)
    europe_pmc = EuropePMCRetrievalProvider()
    crossref = CrossrefRetrievalProvider(mailto=os.environ.get("CROSSREF_MAILTO", ""))
    retrieval = MultiSourceLiteratureRetrievalProvider((europe_pmc, crossref))
    verifier = UnavailableProtectedVerifier()
    experience_store = InMemoryExperienceStore()
    identity = DiagnosticIdentity(
        model=model,
        model_digest=model_digest,
        ollama_endpoint=llm.config.endpoint,
        europe_pmc_endpoint=europe_pmc.endpoint,
        crossref_endpoint=crossref.endpoint,
    )
    baseline = SimpleLLMRetrievalBaseline(
        llm=llm,
        retrieval=retrieval,
        max_results=8,
        retrieval_call_cost_units=RETRIEVAL_CALL_COST_UNITS,
        llm_call_cost_units=LLM_CALL_COST_UNITS,
    )
    runner = AccountedShadowLiveTrialRunner.from_providers(
        llm=llm,
        retrieval=retrieval,
        verification=verifier,
        baseline=baseline,
        experience_store=experience_store,
        config=SolverConfig(
            max_iterations=6,
            search_limit_per_query=8,
            require_verified_answer=True,
        ),
        evaluator_artifact_hash=identity.evaluator_artifact_hash,
        retrieval_call_cost_units=RETRIEVAL_CALL_COST_UNITS,
        llm_call_cost_units=LLM_CALL_COST_UNITS,
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
    summary = _summary(
        report,
        baseline,
        identity=identity,
        experience_store=experience_store,
        runner=runner,
    )
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
