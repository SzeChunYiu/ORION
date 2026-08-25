#!/usr/bin/env python3
"""Focused validation for the P12-DES-01 fail-closed packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
TERMINAL = "CANNOT_CHECK_PROTECTED_SUBSTRATE_AND_NONFLAT_SUCCESSOR_NOT_RUN"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def validate() -> dict:
    freeze = load("FREEZE_V1.json")
    preflight = load("LUNARC_PREFLIGHT_V1.json")
    raw = load("RAW_MANIFEST_V1.json")
    primary = load("PRIMARY_RESULT_V1.json")
    donor = load("IDEAL_DONOR_RESULT_V1.json")
    controls = load("NEGATIVE_CONTROLS_V1.json")
    resources = load("RESOURCE_LEDGER_V1.json")
    transfer = load("TRANSFER_RESULT_V1.json")
    packet = load("RESULT_BINDING_PACKET_V1.json")

    rows = packet["case_outcomes"]
    assert len(rows) == 96 and len({row["instance_id"] for row in rows}) == 96
    assert all(row["status"] == "CANNOT_CHECK" and row["task_outcome"] is None for row in rows)
    assert packet["case_outcomes"] == raw["case_outcomes"]
    assert packet["denominators"]["task_families"] == 24
    assert packet["denominators"]["domains"] == 4
    assert packet["denominators"]["planned_run_cell_denominator"] == "CANNOT_CHECK_NOT_FROZEN"
    assert packet["denominators"]["run_cells_executed"] == 0
    assert packet["denominators"]["slurm_jobs_submitted"] == 0
    assert primary["exact_terminal"] == packet["exact_terminal"] == TERMINAL
    assert primary["cannot_check_rows"] == 96 and primary["rows_dropped"] == 0
    assert all(result["estimate"] is None for result in packet["endpoint_results"].values())
    assert donor["weak_proxy_substituted"] is False
    assert donor["historical_price_aware_successor_reused"] is False
    assert controls["metadata_parseability_substituted_for_task_outcomes"] is False
    assert controls["missing_custody_treated_as_censoring"] is False
    assert resources["slurm_jobs_submitted"] == 0 and resources["gpu_hours"] == 0
    assert transfer["authority_delta"] == "NONE"
    assert packet["manuscript_writing_owner"] == "P1_P15_REWRITE_LANE"
    assert packet["computation_session_paper_authority_delta"] == "NONE"
    assert packet["freeze_sha256"] == digest(HERE / "FREEZE_V1.json")
    assert packet["lunarc_preflight_sha256"] == digest(HERE / "LUNARC_PREFLIGHT_V1.json")
    assert packet["raw_manifest_sha256"] == digest(HERE / "RAW_MANIFEST_V1.json")
    for name, expected in packet["component_sha256"].items():
        assert digest(HERE / name) == expected
    assert preflight["scienceagentbench"]["official_evaluation_runnable"] is False
    assert freeze["nonflat_successor"]["terminal"] == packet["nonflat_successor_terminal"]
    assert not any(state["attained"] for key, state in packet["hard_preconditions"].items() if key.startswith("HP"))

    return {
        "schema": "orion.p12-des-01.focused-validation.v1",
        "valid": True,
        "terminal": TERMINAL,
        "case_rows": 96,
        "rows_dropped": 0,
        "run_cells_executed": 0,
        "slurm_jobs_submitted": 0,
        "digest_bindings_checked": 8,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
