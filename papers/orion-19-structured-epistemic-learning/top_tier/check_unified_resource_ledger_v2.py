#!/usr/bin/env python3
"""Independent audit for the P9 unified resource ledger V2.

Recomputes schema completeness, information preservation, corrected-coordinate
presence, decision reproduction and the survival verdict from the emitted
ledger alone, then cross-binds the frozen causal receipt tokens.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ("I_sem", "A_dim", "A_transform", "M_state", "C_fit", "C_infer", "C_explicit", "R_registered")
PHYSICAL = FIELDS[:7]
FROZEN_DECISIONS = {
    "D-A": {"predicted": "ACCESSIBILITY", "protected_gold": "CANNOT_CHECK"},
    "D-I": {"predicted": "INFORMATION", "protected_gold": "INFORMATION"},
    "B-I": {"predicted": "INFORMATION", "protected_gold": "INFORMATION"},
    "B-A": {"predicted": "ACCESSIBILITY", "protected_gold": "ACCESSIBILITY"},
    "B-C": {"predicted": "COMPUTATION", "protected_gold": "COMPUTATION"},
}
COST = {"INFORMATION": 8.0, "ACCESSIBILITY": 2.0, "COMPUTATION": 12.0}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("p9_unified_resource_ledger_v2.json")
    p = json.loads(path.read_text(encoding="utf-8"))
    rows = p["rows"]
    cells = p["cell_summaries"]

    assert p["schema"] == "P9.UnifiedResourceLedger.v2"
    assert p["scalarization"] == "PROHIBITED"
    assert set(cells) == set(FROZEN_DECISIONS) == {"D-A", "D-I", "B-I", "B-A", "B-C"}

    # Full vector completeness over all 15 arm rows.
    keys = {(r["task"], r["intervention"]) for r in rows}
    assert len(rows) == 15 and keys == {(t, i) for t in FROZEN_DECISIONS for i in COST}
    by = {(r["task"], r["intervention"]): r for r in rows}
    for r in rows:
        assert all(f in r and isinstance(r[f], (int, float)) and r[f] >= 0 for f in FIELDS), r
        assert r["R_registered"] == COST[r["intervention"]]
        assert "probe_quality" in r and "protected_quality" in r
        assert "probe_reaches_target" in r and "protected_reaches_target" in r

    # Corrected accounting is actually present (the three audit repairs).
    # Logistic parameter counts are analytic (10 classes * n_features + 10):
    # scaler coordinates must be included on top of them.
    assert by[("D-A", "INFORMATION")]["M_state"] == 650 + 128
    assert by[("D-A", "ACCESSIBILITY")]["M_state"] == 650 + 128
    assert by[("D-I", "INFORMATION")]["M_state"] == 650 + 128
    assert by[("D-I", "ACCESSIBILITY")]["M_state"] == 20 + 2
    for task in ("D-A", "D-I"):
        assert by[(task, "COMPUTATION")]["M_state"] > 2, "SVC arm lost scaler state"
        for iv in COST:
            assert "base_state_fitted_coordinates" in by[(task, iv)]
    for task in ("B-I", "B-A", "B-C"):
        for iv in COST:
            assert by[(task, iv)]["C_infer"] == 1, ("readout touch missing", task, iv)
    assert by[("B-C", "ACCESSIBILITY")]["A_transform"] == 7, "B-C serialization work hidden"

    # Information preservation: accessibility/computation must not add I_sem.
    for task in FROZEN_DECISIONS:
        base = by[(task, "COMPUTATION")]["I_sem"]
        assert by[(task, "ACCESSIBILITY")]["I_sem"] == base
    assert by[("D-I", "INFORMATION")]["I_sem"] > by[("D-I", "COMPUTATION")]["I_sem"]
    assert by[("B-I", "INFORMATION")]["I_sem"] > by[("B-I", "COMPUTATION")]["I_sem"]

    # Learned arms carry fit + state cost; exact computation arms carry work.
    assert all(by[(t, i)]["C_fit"] > 0 and by[(t, i)]["M_state"] > 0 for t in ("D-A", "D-I") for i in COST)
    assert all(by[(t, "COMPUTATION")]["C_explicit"] > 0 for t in ("B-I", "B-A", "B-C"))

    # Decision reproduction from the ledger's own quality columns.
    for task, frozen_d in FROZEN_DECISIONS.items():
        c = cells[task]
        assert c["frozen_prediction"] == frozen_d["predicted"] == c["probe_prediction_rederived"]
        assert c["frozen_protected_gold"] == frozen_d["protected_gold"] == c["protected_gold_rederived"]
        assert c["prediction_reproduced"] and c["gold_reproduced"]
        target = c["target"]
        for iv in COST:
            r = by[(task, iv)]
            assert r["probe_reaches_target"] == (r["probe_quality"] >= target)
            assert r["protected_reaches_target"] == (r["protected_quality"] >= target)
        # matched comparison present with full vectors
        mc = c["matched_comparison"]
        assert set(mc["generic_vector"]) == set(FIELDS)
        if mc["diagnostic_vector"] is not None:
            assert set(mc["diagnostic_vector"]) == set(FIELDS)
            assert set(mc["per_coordinate_delta_generic_minus_diagnostic"]) == set(PHYSICAL)

    # Survival verdict recomputed from the cells themselves.
    assert sum(cells[t]["diagnostic_correct"] for t in cells) == 4
    assert sum(cells[t]["generic_correct"] for t in cells) == 1
    assert sum(cells[t]["false_compute_escalation"] for t in cells) == 0
    assert sum(cells[t]["generic_false_compute_escalation"] for t in cells) == 4
    assert cells["D-A"]["protected_gold_rederived"] == "CANNOT_CHECK"
    assert p["survival_verdict"] == "SURVIVES_FULL_ACCOUNTING"
    assert p["survival"] == {
        "all_five_decisions_reproduced": True,
        "diagnostic_accuracy_four_of_five": True,
        "generic_accuracy_one_of_five": True,
        "d_a_protected_remains_cannot_check": True,
        "false_compute_escalation_zero": True,
        "generic_false_compute_escalation_four": True,
    }

    # Receipt self-hash binding.
    body = {k: v for k, v in p.items() if k != "receipt_sha256"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(raw).hexdigest() == p["receipt_sha256"], "receipt hash mismatch"

    receipt = {
        "schema": "P9.UnifiedResourceLedgerIndependent.v2",
        "source_ledger_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "row_count": len(rows),
        "full_vector_green": True,
        "information_preservation_green": True,
        "corrected_accounting_green": True,
        "decision_reproduction_green": True,
        "survival_recomputed": "SURVIVES_FULL_ACCOUNTING",
        "scalarization_prohibited": True,
        "terminal": "P9_UNIFIED_RESOURCE_LEDGER_SECOND_CHECKER_V2_GREEN",
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
