from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.benchmarks.external_evidence import empty_external_manifest
from orion.benchmarks.external_io import load_external_manifest
from orion.benchmarks.flagship import current_flagship_evidence_state
from orion.self_orion.phase2_freeze import freeze_phase2_binding
from orion.self_orion.phase2_io import load_phase2_binding, repository_phase2_preflight
from orion.self_orion.phase2_preflight import (
    Phase2PreflightStatus,
    assess_phase2_preflight,
    build_frozen_live_trial_packet,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m orion.benchmarks")
    subcommands = parser.add_subparsers(dest="command", required=True)

    external = subcommands.add_parser(
        "external-status",
        help="Assess P1-P5 external evidence from a frozen manifest JSON file.",
    )
    external.add_argument("--manifest", type=Path, default=None)

    phase2 = subcommands.add_parser(
        "phase2-preflight",
        help="Assess externally supplied bindings for the frozen Shadow live trial.",
    )
    phase2.add_argument("--binding", type=Path, default=None)

    freeze = subcommands.add_parser(
        "phase2-freeze",
        help="Attest a clean Git subject and freeze it with a verified live provider manifest.",
    )
    freeze.add_argument("--repo", type=Path, default=Path("."))
    freeze.add_argument("--provider-manifest", type=Path, required=True)
    freeze.add_argument("--subject-output", type=Path, required=True)
    freeze.add_argument("--binding-output", type=Path, required=True)
    freeze.add_argument("--resource-budget-units", type=float, required=True)
    freeze.add_argument("--baseline-id", default="simple-llm-retrieval-baseline-v1")
    freeze.add_argument("--protocol-id", default="phase2-shadow-closure-v1")
    freeze.add_argument("--repository-identity", default=None)
    return parser


def _external_status_payload(manifest_path: Path | None) -> dict[str, object]:
    manifest = empty_external_manifest() if manifest_path is None else load_external_manifest(manifest_path)
    state = current_flagship_evidence_state(manifest)
    return {
        "manifest_id": manifest.manifest_id,
        "subject_revision_hash": manifest.subject_revision_hash,
        "evaluator_artifact_hash": manifest.evaluator_artifact_hash,
        "evaluation_epoch_id": manifest.evaluation_epoch_id,
        "local_all_pass": state.local_all_pass,
        "external_all_pass": state.external_all_pass,
        "publication_ready": state.publication_ready,
        "cannot_check_papers": list(state.cannot_check_papers),
        "external": [
            {
                "paper_id": report.paper_id,
                "case_id": report.case_id,
                "status": report.status.value,
                "blockers": list(report.blockers),
                "metrics": dict(report.metrics),
            }
            for report in state.external_reports
        ],
    }


def _phase2_preflight_payload(binding_path: Path | None) -> dict[str, object]:
    preflight = repository_phase2_preflight() if binding_path is None else load_phase2_binding(binding_path)
    report = assess_phase2_preflight(preflight)
    payload: dict[str, object] = {
        "protocol_id": preflight.protocol_id,
        "status": report.status.value,
        "blockers": list(report.blockers),
        "subject_revision_hash": preflight.subject_revision_hash,
        "provider_manifest_hash": preflight.provider_manifest_hash,
        "evaluator_artifact_hash": preflight.evaluator_artifact_hash,
        "evaluation_epoch_id": preflight.evaluation_epoch_id,
        "baseline_id": preflight.baseline_id,
        "resource_budget_units": preflight.resource_budget_units,
        "frozen_task_ids": list(report.frozen_task_ids),
        "authority_attack_ids": list(report.attack_ids),
        "ready_to_execute_shadow_trial": report.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL,
        "grants_phase2_closure": False,
        "grants_governed_self_orion": False,
    }
    if report.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL:
        payload["live_trial_packet_fingerprint"] = build_frozen_live_trial_packet(preflight).fingerprint
    return payload


def _phase2_freeze_payload(args: argparse.Namespace) -> dict[str, object]:
    frozen = freeze_phase2_binding(
        repository_root=args.repo,
        provider_manifest_path=args.provider_manifest,
        subject_output_path=args.subject_output,
        binding_output_path=args.binding_output,
        resource_budget_units=args.resource_budget_units,
        baseline_id=args.baseline_id,
        protocol_id=args.protocol_id,
        repository_identity=args.repository_identity,
    )
    return {
        "status": "READY_TO_EXECUTE_SHADOW_TRIAL",
        "repository_identity": frozen.subject.repository_identity,
        "commit_oid": frozen.subject.commit_oid,
        "tree_oid": frozen.subject.tree_oid,
        "source_tree_sha256": frozen.subject.source_tree_sha256,
        "subject_revision_hash": frozen.subject_revision_hash,
        "provider_manifest_hash": frozen.provider_manifest_hash,
        "evaluator_artifact_hash": frozen.preflight.evaluator_artifact_hash,
        "evaluation_epoch_id": frozen.preflight.evaluation_epoch_id,
        "baseline_id": frozen.preflight.baseline_id,
        "resource_budget_units": frozen.preflight.resource_budget_units,
        "live_trial_packet_fingerprint": frozen.live_trial_packet_fingerprint,
        "subject_output": str(args.subject_output),
        "binding_output": str(args.binding_output),
        "grants_phase2_closure": False,
        "grants_governed_self_orion": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "external-status":
        payload = _external_status_payload(args.manifest)
    elif args.command == "phase2-preflight":
        payload = _phase2_preflight_payload(args.binding)
    elif args.command == "phase2-freeze":
        payload = _phase2_freeze_payload(args)
    else:  # pragma: no cover
        raise AssertionError("unreachable command")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


__all__ = ["main"]
