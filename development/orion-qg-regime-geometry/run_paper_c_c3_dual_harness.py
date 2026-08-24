#!/usr/bin/env python3
"""Run Paper C / C3 source, generic, and native lanes in isolation."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg.paper_c_c3_rwise_value import (
    PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST,
)
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "research"
    / "extensions"
    / "orion-qg"
    / "PAPER_C_C3_RWISE_VALUE_SEPARATION_RESULTS_2026-08-24.json"
)
GENERIC = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C3_RWISE_VALUE_GENERIC_VERIFICATION_2026-08-24.json"
)
DUAL = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C3_RWISE_VALUE_DUAL_HARNESS_2026-08-24.json"
)
POSITIVE = (
    "PAPER_C_C3_ARBITRARY_FIXED_ORDER_INTERACTION_DATA_VALUE_INSUFFICIENT"
    "__LINEAR_GAP_MACHINE_CORROBORATED"
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def run_python(workspace: ResearchWorkspace, script: str, timeout: int) -> dict[str, Any]:
    request = workspace.get_or_create_request(
        capability="PYTHON",
        payload={
            "code": f"import runpy;runpy.run_path({script!r},run_name='__main__')",
            "cwd": ".",
            "timeout": timeout,
        },
    )
    result = service_local_request(workspace, request.request_id)
    if not result.success:
        raise RuntimeError(result.error)
    if not isinstance(result.output, dict) or result.output.get("returncode") != 0:
        raise RuntimeError({"script": script, "output": result.output})
    if result.output.get("sandboxed") is not False:
        raise RuntimeError("local execution provenance missing")
    return {
        "returncode": result.output["returncode"],
        "sandboxed": result.output["sandboxed"],
        "single_service_local_request_call": True,
    }


def _run(generic_path: Path, native_path: Path) -> int:
    for artifact in (SOURCE, GENERIC, DUAL):
        artifact.unlink(missing_ok=True)
    generic_workspace = ResearchWorkspace.initialize(
        generic_path, project_root=ROOT, allow_process_tools=True
    )
    analyzer_execution = run_python(
        generic_workspace,
        "research/extensions/orion-qg/paper_c_c3_rwise_value_separation.py",
        1200,
    )
    generic_execution = run_python(
        generic_workspace,
        "development/orion-qg-regime-geometry/paper_c_c3_generic_verify.py",
        1200,
    )
    source = json.loads(SOURCE.read_text())
    generic = json.loads(GENERIC.read_text())

    validate_manifest(PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST)
    native_workspace = ResearchWorkspace.initialize(
        native_path, project_root=ROOT, allow_process_tools=True
    )
    campaign_id = PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST["campaign_id"]
    if native_workspace.load_latest_campaign_state(campaign_id) is not None:
        raise RuntimeError("native workspace was not fresh before campaign execution")
    native_outcome = run_campaign(
        native_workspace,
        PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST,
        max_cycles=4,
        auto_service_local=True,
    )
    native_state = CampaignState.from_dict(
        native_workspace.load_latest_campaign_state(campaign_id)
    )
    native_decision = {
        "ACCEPT_RECORDED": "ACCEPT_RWISE_VALUE_SEPARATION",
        "REJECT_RECORDED": "REJECT",
    }.get(native_state.phase_id, "INCOMPLETE")
    both_accept = (
        source.get("terminal") == POSITIVE
        and generic.get("decision") == "ACCEPT_RWISE_VALUE_SEPARATION"
        and native_decision == "ACCEPT_RWISE_VALUE_SEPARATION"
    )
    terminal = POSITIVE if both_accept else "PAPER_C_C3_GENERIC_NATIVE_DISAGREEMENT"
    cycles = native_outcome.get("cycles", []) if isinstance(native_outcome, dict) else []
    rows = source.get("direct_exact_checks", {}).get("rows", [])
    dual: dict[str, Any] = {
        "schema": "ORION.PaperC.C3.DualHarness.v1",
        "terminal": terminal,
        "both_accept": both_accept,
        "source_result_digest": source.get("result_digest"),
        "generic_verification_digest": generic.get("verification_digest"),
        "generic_decision": generic.get("decision"),
        "native_decision": native_decision,
        "native_manifest_digest": native_state.manifest_digest,
        "native_terminal_phase": native_state.phase_id,
        "native_run_status": native_outcome.get("status")
        if isinstance(native_outcome, dict)
        else None,
        "native_cycle_count": len(cycles),
        "native_cycle_statuses": [cycle.get("status") for cycle in cycles],
        "executions": {
            "analyzer": analyzer_execution,
            "generic_verifier": generic_execution,
            "native_auto_service_local": True,
        },
        "direct_m": [row.get("m") for row in rows],
        "maximum_verified_tensor_order": max(
            (row.get("tensor_order", 0) for row in rows), default=0
        ),
        "m_minus_2_tensor_identical": all(
            row.get("interaction_tensor_identical") for row in rows
        ),
        "unbounded_additive_value_ambiguity": source.get(
            "unbounded_additive_value_ambiguity"
        ),
        "theorem_authority": "FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY"
        if both_accept
        else "NONE",
        "optimizer_separation_new_in_c3": False,
        "minimal_padding_authority": False,
        "multiplicative_approximation_lower_bound": False,
        "cross_grammar_transfer": False,
        "cross_objective_transfer": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "ci_authority": False,
    }
    dual["receipt_digest"] = hashlib.sha256(canonical(dual).encode()).hexdigest()
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n")
    print(
        canonical(
            {
                "terminal": terminal,
                "generic": generic.get("decision"),
                "native": native_decision,
                "direct_m": dual["direct_m"],
                "receipt_digest": dual["receipt_digest"],
            }
        )
    )
    return 0


def main() -> int:
    workspace_paths: list[Path] = []
    try:
        generic_path = Path(
            tempfile.mkdtemp(prefix="orion-paper-c-c3-generic-", dir="/tmp")
        )
        workspace_paths.append(generic_path)
        native_path = Path(
            tempfile.mkdtemp(prefix="orion-paper-c-c3-native-", dir="/tmp")
        )
        workspace_paths.append(native_path)
        return _run(generic_path, native_path)
    finally:
        for workspace_path in workspace_paths:
            shutil.rmtree(workspace_path, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

