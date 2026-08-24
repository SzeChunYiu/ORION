#!/usr/bin/env python3
"""Run source, generic, and native lanes for non-quantum math M3."""
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
from orion_research_harness.domains.orion_rg.nonquantum_m3_support10 import (
    NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST,
)
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/orion-rg/NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json"
GENERIC = ROOT / "development/orion-rg-davenport/NONQUANTUM_M3_SUPPORT10_REPLAY_GENERIC_2026-08-24.json"
DUAL = ROOT / "development/orion-rg-davenport/NONQUANTUM_M3_SUPPORT10_REPLAY_DUAL_2026-08-24.json"
POSITIVE = (
    "NONQUANTUM_M3_C5CUBED_SUPPORT10_BOTH_DEFICIT_PATTERNS_EXCLUDED"
    "__OBSTRUCTION_SUPPORT_AT_LEAST11"
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def run_python(workspace: ResearchWorkspace, script: str) -> dict[str, Any]:
    request = workspace.get_or_create_request(
        capability="PYTHON",
        payload={
            "code": f"import runpy;runpy.run_path({script!r},run_name='__main__')",
            "cwd": ".",
            "timeout": 600,
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
        generic_workspace, "research/orion-rg/nonquantum_m3_support10_replay.py"
    )
    generic_execution = run_python(
        generic_workspace, "development/orion-rg-davenport/nonquantum_m3_generic_verify.py"
    )
    source = json.loads(SOURCE.read_text())
    generic = json.loads(GENERIC.read_text())

    validate_manifest(NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST)
    native_workspace = ResearchWorkspace.initialize(
        native_path, project_root=ROOT, allow_process_tools=True
    )
    campaign_id = NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST["campaign_id"]
    if native_workspace.load_latest_campaign_state(campaign_id) is not None:
        raise RuntimeError("native workspace was not fresh")
    outcome = run_campaign(
        native_workspace,
        NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST,
        max_cycles=4,
        auto_service_local=True,
    )
    state = CampaignState.from_dict(native_workspace.load_latest_campaign_state(campaign_id))
    native_decision = {
        "ACCEPT_RECORDED": "ACCEPT_SUPPORT10_EXCLUSION",
        "REJECT_RECORDED": "REJECT",
    }.get(state.phase_id, "INCOMPLETE")
    both_accept = (
        source.get("terminal") == POSITIVE
        and generic.get("decision") == "ACCEPT_SUPPORT10_EXCLUSION"
        and native_decision == "ACCEPT_SUPPORT10_EXCLUSION"
    )
    terminal = POSITIVE if both_accept else "NONQUANTUM_M3_GENERIC_NATIVE_DISAGREEMENT"
    cycles = outcome.get("cycles", []) if isinstance(outcome, dict) else []
    dual: dict[str, Any] = {
        "schema": "ORION.NonQuantumMath.M3.DualHarness.v1",
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
        "patterns_checked_per_c_engine": [[1, 3, 6], [3, 0, 7]],
        "solutions_per_pattern_per_c_engine": 0,
        "result_owner": "NON_QUANTUM_MATH",
        "bounded_support_le10_theorem_authority": True,
        "support_11_plus_theorem_authority": False,
        "support_23_theorem_authority": False,
        "independent_external_replay_complete": False,
        "prospective_validation_authority": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
        "novelty_authority": False,
        "venue_authority": False,
        "quantum_claim": False,
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
        generic_path = Path(tempfile.mkdtemp(prefix="orion-nonquantum-m3-generic-", dir="/tmp"))
        paths.append(generic_path)
        native_path = Path(tempfile.mkdtemp(prefix="orion-nonquantum-m3-native-", dir="/tmp"))
        paths.append(native_path)
        return _run(generic_path, native_path)
    finally:
        for path in paths:
            shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
