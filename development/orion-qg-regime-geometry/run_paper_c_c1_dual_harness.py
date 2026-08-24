#!/usr/bin/env python3
"""Run Paper C / C1 through isolated generic and native harness lanes."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg.paper_c_c1_all_m import (
    PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST,
)
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "research"
    / "extensions"
    / "orion-qg"
    / "PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json"
)
GENERIC = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C1_ALL_M_GENERIC_VERIFICATION_2026-08-24.json"
)
DUAL = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C1_ALL_M_DUAL_HARNESS_2026-08-24.json"
)
GENERIC_WS = ROOT / ".orion-paper-c-c1-generic"
NATIVE_WS = ROOT / ".orion-paper-c-c1-native"
POSITIVE = (
    "PAPER_C_C1_ALL_M_GE_5_FOUR_INDEX_DECISION_THEOREM_MACHINE_CORROBORATED"
    "__M4_SHARP_COUNTEREXAMPLE"
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


def main() -> int:
    for workspace_path in (GENERIC_WS, NATIVE_WS):
        if workspace_path.exists():
            shutil.rmtree(workspace_path)
    for artifact in (SOURCE, GENERIC, DUAL):
        artifact.unlink(missing_ok=True)

    generic_workspace = ResearchWorkspace.initialize(
        GENERIC_WS, project_root=ROOT, allow_process_tools=True
    )
    analyzer_execution = run_python(
        generic_workspace,
        "research/extensions/orion-qg/paper_c_c1_all_m_decision.py",
        1200,
    )
    generic_execution = run_python(
        generic_workspace,
        "development/orion-qg-regime-geometry/paper_c_c1_generic_verify.py",
        1200,
    )
    source = json.loads(SOURCE.read_text())
    generic = json.loads(GENERIC.read_text())

    validate_manifest(PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST)
    native_workspace = ResearchWorkspace.initialize(
        NATIVE_WS, project_root=ROOT, allow_process_tools=True
    )
    native_outcome = run_campaign(
        native_workspace,
        PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST,
        max_cycles=4,
        auto_service_local=True,
    )
    native_state = CampaignState.from_dict(
        native_workspace.load_latest_campaign_state(
            PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST["campaign_id"]
        )
    )
    native_decision = {
        "ACCEPT_RECORDED": "ACCEPT_EXACT_FROZEN_ALL_M_DECISION_THEOREM",
        "REJECT_RECORDED": "REJECT",
    }.get(native_state.phase_id, "INCOMPLETE")

    both_accept = (
        source.get("terminal") == POSITIVE
        and generic.get("decision") == "ACCEPT_EXACT_FROZEN_ALL_M_DECISION_THEOREM"
        and native_decision == "ACCEPT_EXACT_FROZEN_ALL_M_DECISION_THEOREM"
    )
    terminal = POSITIVE if both_accept else "PAPER_C_C1_NATIVE_GENERIC_DISAGREEMENT"
    dual: dict[str, Any] = {
        "schema": "ORION.PaperC.C1.DualHarness.v1",
        "terminal": terminal,
        "both_accept": both_accept,
        "source_result_digest": source.get("result_digest"),
        "generic_verification_digest": generic.get("verification_digest"),
        "generic_decision": generic.get("decision"),
        "native_decision": native_decision,
        "native_manifest_digest": native_state.manifest_digest,
        "native_terminal_phase": native_state.phase_id,
        "native_run_status": native_outcome.get("status") if isinstance(native_outcome, dict) else None,
        "native_cycle_count": len(native_outcome.get("cycles", []))
        if isinstance(native_outcome, dict)
        else None,
        "native_cycle_statuses": [
            cycle.get("status") for cycle in native_outcome.get("cycles", [])
        ]
        if isinstance(native_outcome, dict)
        else None,
        "executions": {
            "analyzer": analyzer_execution,
            "generic_verifier": generic_execution,
            "native_auto_service_local": True,
        },
        "theorem_authority": "FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY" if both_accept else "NONE",
        "m4_counterexample_preserved": source.get("sharpness", {}).get("all_checks") is True,
        "maximum_clause_support_terms": source.get("certificate", {}).get(
            "maximum_clause_support_terms"
        ),
        "exact_value_authority": False,
        "optimizer_witness_authority": False,
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
                "m5_n2": source.get("complete_regressions", {}).get("m5_n2", {}).get("count"),
                "m4_sharp": dual["m4_counterexample_preserved"],
                "receipt_digest": dual["receipt_digest"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
