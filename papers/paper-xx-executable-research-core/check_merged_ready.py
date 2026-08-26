#!/usr/bin/env python3
"""Fail closed if the P9 merged-evidence terminal drifts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANDIDATES = HERE.parent
FRAMEWORK = CANDIDATES / "orion-learning-machine"
RESULT = HERE / "results" / "ASLIB_SAT11_HAND_ALGO_V1.json"
EXPECTED_RESULT_SHA256 = "8246d007260be1bc5df437002c1de004bc98868edd114b29c3ffb22046532f06"


def require_text(path: Path, *needles: str) -> str:
    if not path.is_file():
        raise AssertionError(f"missing required artifact: {path}")
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"{path}: missing required text {needle!r}")
    return text


def main() -> None:
    digest = hashlib.sha256(RESULT.read_bytes()).hexdigest()
    if digest != EXPECTED_RESULT_SHA256:
        raise AssertionError(f"public result drift: {digest}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    primary = result["primary_comparison"]
    assert result["numerical_standalone_gate"]["passes"] is True
    assert primary["estimate"] == 0.7142857142857143
    assert primary["paired_bootstrap_95_percent_interval"][0] > 0.0
    assert primary["rf_solved_retention"] >= 0.95

    saturation = require_text(
        HERE / "SATURATION_LEDGER_2026-08-18.md",
        "saturation before residual",
        "`MERGE_P9_INTO_P8_PROGRAMME`",
        "`ABSORBED`",
        "`ALREADY_PRESENT`",
        "`DEFERRED_WITH_TRIGGER`",
    )
    donor_rows = [
        line
        for line in saturation.splitlines()
        if line.startswith("| ")
        and any(
            token in line
            for token in ("`ABSORBED`", "`ALREADY_PRESENT`", "`DEFERRED_WITH_TRIGGER`")
        )
    ]
    if len(donor_rows) < 8:
        raise AssertionError(f"constructive saturation shrank to {len(donor_rows)} donors")

    require_text(
        HERE / "MERGE_DISPOSITION.md",
        "MERGE_P9_INTO_P8_PROGRAMME",
        "deliberately not created",
    )
    require_text(HERE / "CLAIM_LEDGER.md", "NOT_MEASURED", "No superiority over AutoFolio")
    require_text(HERE / "JOURNAL_READINESS.md", "NO_RESIDUAL", "PASS_BOUNDED")
    require_text(HERE / "README.md", "MERGED INTO P8/PROGRAMME", "0.7143")
    require_text(
        CANDIDATES
        / "orion-18-epistemic-authority-autonomous-science"
        / "benchmark"
        / "P9_GOVERNED_CAPABILITY_COMPANION.md",
        "authorizes_execution=False",
        "0.6104–0.8182",
    )
    require_text(
        FRAMEWORK / "framework" / "orion_learning_machine" / "types.py",
        "class CapabilityRoute",
        "authorizes_execution: bool = False",
    )
    require_text(
        FRAMEWORK / "framework" / "orion_learning_machine" / "runtime.py",
        "def route_capability(",
        "external authorization still required",
    )
    require_text(
        FRAMEWORK / "results" / "PHASE1_MECHANIC_COMPOSITION_V2.txt",
        "false_commit_status=NOT_MEASURED",
    )
    print("P9 merged-evidence readiness gate: PASS")


if __name__ == "__main__":
    main()
