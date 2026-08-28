#!/usr/bin/env python3
"""Post-outcome hostile-extension diagnosis for the four strict-gap words.

The fail-closed path never runs the hostile cross-move extensions (they are a
success-path gate).  This script runs the frozen hostile-extension battery on
each committed strict-gap word so the adverse gap evidence is interpretable:
a gap that survives bialg/hopf/gadget_phasepoly extensions applied to the
native output is a stronger registry-realization signal than one that
collapses.  NOT a frozen input; NOT terminal evidence.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "orion01_round2_atomic_registry.py"
spec = importlib.util.spec_from_file_location("r2gap_base", MODULE_PATH)
assert spec is not None and spec.loader is not None
study = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = study
spec.loader.exec_module(study)

GAP_WORDS = [(135, ["H0", "CX10", "CX01"]), (192, ["H1", "CX01", "CX10"]),
             (514, ["CX01", "CX10", "H1"]), (569, ["CX10", "CX01", "H0"])]


def main() -> int:
    registry = study.load_registry()
    cap = int(registry["max_states_per_input_fail_closed"])
    rows: list[dict[str, Any]] = []
    for index, word in GAP_WORDS:
        task = study.WordTask(word=tuple(word), word_index=index, mode="execute",
                              domain="primary", cap=cap)
        record = study.analyze_word(task)
        start = study.start_state_from_word(tuple(word))
        native_state, _native_resource = study.native_full_reduce(start)
        hostile = study.hostile_extension_outcomes(
            native_state, tuple(record["optimum_resource"])
        )
        rows.append(
            {
                "word": list(word),
                "word_index": index,
                "native_resource": record["native_resource"],
                "optimum_resource": record["optimum_resource"],
                "generic_resource": record["generic_resource"],
                "generic_match": record["generic_match"],
                "witness_length": record["witness_length"],
                "hostile": hostile,
            }
        )
        print(
            "GAP", "-".join(word),
            "native", record["native_resource"],
            "optimum", record["optimum_resource"],
            "generic", record["generic_resource"],
            "gmatch", record["generic_match"],
            "hostile_collapse", hostile["any_collapse"],
        )
    report = {
        "schema": "ORION.ORION01.Round2.PyZXGapHostileDiagnosis.v1",
        "paper_id": "ORION-01",
        "round": 2,
        "purpose": "POST_OUTCOME_DIAGNOSIS__NOT_A_FROZEN_INPUT__NOT_TERMINAL_EVIDENCE",
        "rows": rows,
    }
    target = HERE / "ORION01_ROUND2_ATOMIC_GAP_HOSTILE_DIAGNOSIS.json"
    target.write_text(study.canonical_json(report) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
