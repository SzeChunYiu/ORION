#!/usr/bin/env python3
"""Run the outcome-blind P1--P5 successor readiness checks."""

from __future__ import annotations

import json
from pathlib import Path
import runpy
from typing import Any

from orion.study.p1_p5_successor_readiness import (
    load_and_assess,
    validate_attainability_fixture,
)

ROOT = Path(__file__).resolve().parents[2]
PROTOCOLS = (
    ROOT / "research/claim_expansion/p1/gpt_r7/R7A_MAXT_POWER_AMENDMENT_V2.json",
    ROOT / "papers/paper-02-open-world-scientific-discovery/protocol/P2_TASK_WORLD_SUCCESSOR_V2.json",
    ROOT / "papers/paper-03-global-knowledge-portrait/protocol/P3_PARTIAL_IDENTIFICATION_SUCCESSOR_V1.json",
    ROOT / "papers/paper-04-verified-scientific-discovery/protocol/P4_NATURALISTIC_IDENTIFIABILITY_SUCCESSOR_V1.json",
    ROOT / "papers/paper-05-self-orion/protocol/P5_WIDE_REVISION_LEVEL_SUCCESSOR_V1.json",
)
FIXTURES = {
    "P3": ROOT / "research/paper-programme-v1/fixtures/P3_PARTIAL_IDENTIFICATION_ATTAINABILITY_FIXTURE_V1.json",
    "P4": ROOT / "research/paper-programme-v1/fixtures/P4_NATURALISTIC_IDENTIFIABILITY_ATTAINABILITY_FIXTURE_V1.json",
    "P5": ROOT / "research/paper-programme-v1/fixtures/P5_REVISION_LEVEL_ATTAINABILITY_FIXTURE_V1.json",
}


def derive() -> dict[str, Any]:
    assessments = [load_and_assess(path, root=ROOT) for path in PROTOCOLS]
    fixture_errors = {
        paper_id: list(
            validate_attainability_fixture(
                paper_id,
                json.loads(path.read_text(encoding="utf-8")),
            )
        )
        for paper_id, path in FIXTURES.items()
    }
    p1_power_namespace = runpy.run_path(
        str(ROOT / "research/claim_expansion/p1/gpt_r7a/max_t_power.py")
    )
    regenerated_p1_power = p1_power_namespace["build_receipt"]()
    committed_p1_power = json.loads(
        (
            ROOT
            / "research/claim_expansion/p1/gpt_r7a/R7A_MAXT_POWER_RECEIPT_V1.json"
        ).read_text(encoding="utf-8")
    )
    p5_namespace = runpy.run_path(
        str(ROOT / "research/self-orion-v3/run_confirmatory_preflight_v1.py")
    )
    p5_existing_preflight = p5_namespace["derive"]()
    local_pass = (
        all(item.status == "READY_FOR_EXTERNAL_BINDING" for item in assessments)
        and all(not errors for errors in fixture_errors.values())
        and regenerated_p1_power == committed_p1_power
    )
    return {
        "schema_version": "orion.p1-p5.successor-preoutcome-closure-receipt.v1",
        "status": (
            "LOCAL_PREOUTCOME_CLOSURE_PASS__EXTERNAL_EXECUTION_BLOCKED"
            if local_pass
            else "LOCAL_PREOUTCOME_CLOSURE_FAILED"
        ),
        "outcomes_accessed": False,
        "grants_scientific_authority": False,
        "execution_authorized": False,
        "assessments": [item.as_dict() for item in assessments],
        "attainability_fixture_errors": fixture_errors,
        "p1_max_t_receipt_reproduced": regenerated_p1_power == committed_p1_power,
        "p5_existing_confirmatory_preflight": p5_existing_preflight,
    }


def main() -> None:
    print(json.dumps(derive(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
