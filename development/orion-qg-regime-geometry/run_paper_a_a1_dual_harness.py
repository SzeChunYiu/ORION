#!/usr/bin/env python3
"""Run Paper A / A1 source, generic, and native lanes."""
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
from orion_research_harness.domains.orion_qg.paper_a_a1_multitag import (
    PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST,
)
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json"
GENERIC = ROOT / "development/orion-qg-regime-geometry/PAPER_A_A1_MULTITAG_TARE_GENERIC_2026-08-24.json"
DUAL = ROOT / "development/orion-qg-regime-geometry/PAPER_A_A1_MULTITAG_TARE_DUAL_2026-08-24.json"
POSITIVE = (
    "PAPER_A_A1_MULTITAG_TARE_ALL_N_SUPPORT_AT_MOST_CONSTRAINT_RANK"
    "__R6M_SHARP_BINARY_COROLLARY"
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def run_python(workspace: ResearchWorkspace, script: str) -> dict[str, Any]:
    request = workspace.get_or_create_request(
        capability="PYTHON",
        payload={
            "code": f"import runpy;runpy.run_path({script!r},run_name='__main__')",
            "cwd": ".",
            "timeout": 1200,
        },
    )
    result = service_local_request(workspace, request.request_id)
    if not result.success or not isinstance(result.output, dict):
        raise RuntimeError({"script": script, "result": result.error})
    if result.output.get("returncode") != 0 or result.output.get("sandboxed") is not False:
        raise RuntimeError({"script": script, "output": result.output})
    return {"returncode": 0, "sandboxed": False, "single_service_local_request_call": True}


def _run(generic_path: Path, native_path: Path) -> int:
    for artifact in (SOURCE, GENERIC, DUAL):
        artifact.unlink(missing_ok=True)
    generic_workspace = ResearchWorkspace.initialize(
        generic_path, project_root=ROOT, allow_process_tools=True
    )
    source_execution = run_python(
        generic_workspace, "research/extensions/orion-qg/paper_a_a1_multitag_tare.py"
    )
    generic_execution = run_python(
        generic_workspace,
        "development/orion-qg-regime-geometry/paper_a_a1_generic_verify.py",
    )
    source = json.loads(SOURCE.read_text())
    generic = json.loads(GENERIC.read_text())

    validate_manifest(PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST)
    native_workspace = ResearchWorkspace.initialize(
        native_path, project_root=ROOT, allow_process_tools=True
    )
    campaign_id = PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST["campaign_id"]
    if native_workspace.load_latest_campaign_state(campaign_id) is not None:
        raise RuntimeError("native workspace was not fresh")
    outcome = run_campaign(
        native_workspace,
        PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST,
        max_cycles=4,
        auto_service_local=True,
    )
    state = CampaignState.from_dict(native_workspace.load_latest_campaign_state(campaign_id))
    native_decision = {
        "ACCEPT_RECORDED": "ACCEPT_MULTITAG_CONSTRAINT_RANK_THEOREM",
        "REJECT_RECORDED": "REJECT",
    }.get(state.phase_id, "INCOMPLETE")
    both_accept = (
        source.get("terminal") == POSITIVE
        and generic.get("decision") == "ACCEPT_MULTITAG_CONSTRAINT_RANK_THEOREM"
        and native_decision == "ACCEPT_MULTITAG_CONSTRAINT_RANK_THEOREM"
    )
    terminal = POSITIVE if both_accept else "PAPER_A_A1_GENERIC_NATIVE_DISAGREEMENT"
    cycles = outcome.get("cycles", []) if isinstance(outcome, dict) else []
    dual: dict[str, Any] = {
        "schema": "ORION.PaperA.A1.DualHarness.v1",
        "terminal": terminal,
        "both_accept": both_accept,
        "source_result_digest": source.get("result_digest"),
        "generic_verification_digest": generic.get("verification_digest"),
        "generic_decision": generic.get("decision"),
        "native_decision": native_decision,
        "native_manifest_digest": state.manifest_digest,
        "native_terminal_phase": state.phase_id,
        "native_run_status": outcome.get("status") if isinstance(outcome, dict) else None,
        "native_cycle_count": len(cycles),
        "native_cycle_statuses": [cycle.get("status") for cycle in cycles],
        "executions": {
            "source": source_execution,
            "generic": generic_execution,
            "native_auto_service_local": True,
        },
        "grammar": "MULTITAG_TARE_M2_THREE_BLOCK_STRUCTURAL",
        "objective_region": "mu>=2*t_restore",
        "normal_form": "support(R)<=rank(realized signature)<=s+1",
        "r6m_sharp_kappa": 2,
        "general_multitag_sharpness": False,
        "outside_cone_support_necessity": False,
        "generic_multitag_tare_transfer": False,
        "cross_unrelated_grammar_transfer": False,
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
                "receipt_digest": dual["receipt_digest"],
            }
        )
    )
    return 0


def main() -> int:
    paths: list[Path] = []
    try:
        generic_path = Path(tempfile.mkdtemp(prefix="orion-paper-a-a1-generic-", dir="/tmp"))
        paths.append(generic_path)
        native_path = Path(tempfile.mkdtemp(prefix="orion-paper-a-a1-native-", dir="/tmp"))
        paths.append(native_path)
        return _run(generic_path, native_path)
    finally:
        for path in paths:
            shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
