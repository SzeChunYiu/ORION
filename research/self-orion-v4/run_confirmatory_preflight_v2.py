from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.study.p5.revision_level_v3_preflight import (
    BaselineBindingDisposition,
    BaselineStructuralBinding,
    ConfirmatoryExecutionBinding,
    ConfirmatoryPreflightStatus,
    assess_confirmatory_preflight,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = ROOT / "papers" / "orion-15-self-orion" / "protocol" / "SELF_ORION_V4_REVISION_LEVEL_PROTOCOL_V1.json"
DEFAULT_BASELINES = ROOT / "research" / "self-orion-v3" / "BASELINE_STRUCTURAL_BINDINGS_V2.json"


def derive(protocol_path: Path = DEFAULT_PROTOCOL, baseline_path: Path = DEFAULT_BASELINES) -> dict[str, object]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    raw_bindings = json.loads(baseline_path.read_text(encoding="utf-8"))
    raw = protocol["confirmatory_execution_bindings"]
    binding = ConfirmatoryExecutionBinding(
        protocol_id=protocol["protocol_id"],
        subject_revision=raw["subject_revision"],
        protected_suite_commitment=raw["protected_suite_commitment"],
        candidate_packet_sha256=raw["candidate_packet_sha256"],
        final_split_sha256=raw["final_split_sha256"],
        evaluator_sha256=raw["evaluator_sha256"],
        evaluation_epoch=raw["evaluation_epoch"],
        baseline_config_sha256=raw["baseline_config_sha256"],
        fresh_transfer_evaluator_sha256=raw["fresh_transfer_evaluator_sha256"],
        result_verifier_owner=raw["result_verifier_owner"],
        candidate_policy_owner=raw["candidate_policy_owner"],
        protected_evaluator_owner=raw["protected_evaluator_owner"],
        outcome_accessed=raw["outcome_accessed"],
    )
    baselines = tuple(
        BaselineStructuralBinding.build(
            baseline_id=item["baseline_id"],
            donor_id=item["donor_id"],
            source_identity=item["source_identity"],
            disposition=BaselineBindingDisposition(item["disposition"]),
            structural_binding_id=item["structural_binding_id"],
            official_reproduction=item["official_reproduction"],
            notes=tuple(item.get("notes", ())),
        )
        for item in raw_bindings["records"]
    )
    report = assess_confirmatory_preflight(
        binding,
        baselines,
        required_baseline_ids=tuple(protocol["confirmatory_required_baseline_bindings"]),
    )
    return {
        "schema": "SelfOrionV4ConfirmatoryPreflightCommand.v1",
        "protocol_id": report.protocol_id,
        "status": report.status.value,
        "blockers": list(report.blockers),
        "baseline_binding_digests": list(report.baseline_binding_digests),
        "authorizes_execution": report.authorizes_execution,
        "grants_scientific_authority": report.grants_scientific_authority,
        "grants_p5_peer_review_ready": report.grants_p5_peer_review_ready,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Report or enforce Self-ORION V4 confirmatory readiness.")
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--baselines", type=Path, default=DEFAULT_BASELINES)
    parser.add_argument("--require-ready", action="store_true", help="Exit nonzero unless every confirmatory binding is complete.")
    args = parser.parse_args()
    result = derive(args.protocol, args.baselines)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_ready and result["status"] != ConfirmatoryPreflightStatus.READY_TO_FREEZE_CONFIRMATORY.value:
        raise SystemExit("Self-ORION V4 confirmatory execution is not ready; see blockers above")


if __name__ == "__main__":
    main()
