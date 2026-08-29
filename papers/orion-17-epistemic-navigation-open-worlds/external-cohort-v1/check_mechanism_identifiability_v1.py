#!/usr/bin/env python3
"""Independent checker for ORION17.MECHANISM_IDENTIFIABILITY.v1.

Reads only frozen study measurements and STUDY_V1.json. It does not import run_study.py,
score_study.py, the campaign instrument, or any ORION policy code.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    rows = json.loads((HERE / "STUDY_MEASUREMENTS_V1.json").read_text())
    study = json.loads((HERE / "STUDY_V1.json").read_text())
    errors = []

    usable = [r for r in rows if r.get("usable")]
    if len(usable) != 20:
        errors.append(f"usable count {len(usable)} != 20")

    # Re-derive the declared outcome from the raw measurement field.
    for r in usable:
        derived = "unsound" if r["false_closure_retention"] > 0 else "sound"
        if r.get("outcome") != derived:
            errors.append(f"outcome mismatch {r['project']}: {r.get('outcome')} vs {derived}")

    nondeg = [r for r in usable if not r.get("donor_degenerate")]
    degen = [r for r in usable if r.get("donor_degenerate")]
    if len(nondeg) != 16 or any(r["outcome"] != "unsound" for r in nondeg):
        errors.append("nondegenerate panel is not exactly 16/16 UNSOUND")
    if len(degen) != 4 or any(r["outcome"] != "sound" for r in degen):
        errors.append("degenerate panel is not exactly 4/4 SOUND")
    if any(r.get("layout") != "src" for r in degen):
        errors.append("a recorded degenerate case is not src-layout")
    if any(r.get("donor_preserve") != 0 for r in degen):
        errors.append("a recorded degenerate case preserves donor closures")

    # The disagreement strata must still be opposite-prediction regions.
    small = [r for r in nondeg if r["stratum"] == "small_fewedge_dense"]
    large = [r for r in nondeg if r["stratum"] == "large_manyedge_sparse"]
    if len(small) != 10 or len(large) != 6:
        errors.append(f"nondegenerate stratum sizes changed: {len(small)}, {len(large)}")

    def predictions_ok(r, density, rival):
        return (
            r["predictions"]["density_rule"] == density
            and r["predictions"]["module_rule"] == rival
            and r["predictions"]["edge_rule"] == rival
        )

    if any(not predictions_ok(r, "unsound", "sound") for r in small):
        errors.append("small/dense predictions no longer density=UNSOUND rivals=SOUND")
    if any(not predictions_ok(r, "sound", "unsound") for r in large):
        errors.append("large/sparse predictions no longer density=SOUND rivals=UNSOUND")

    def wins(rule, subset):
        return sum(r["predictions"][rule] == r["outcome"] for r in subset)

    density_nd = wins("density_rule", nondeg)
    module_nd = wins("module_rule", nondeg)
    edge_nd = wins("edge_rule", nondeg)
    density_all = wins("density_rule", usable)
    module_all = wins("module_rule", usable)
    edge_all = wins("edge_rule", usable)

    if (density_nd, module_nd, edge_nd) != (10, 6, 6):
        errors.append(f"nondegenerate win decomposition changed: {(density_nd, module_nd, edge_nd)}")
    if (density_all, module_all, edge_all) != (14, 6, 6):
        errors.append(f"all-panel win decomposition changed: {(density_all, module_all, edge_all)}")
    if density_all != density_nd + len(degen):
        errors.append("density 14-win total does not decompose into 10 informative + 4 degenerate")

    # Cross-check the committed scorer output rather than trusting our own counts only.
    if study["cuts"]["all_measured"]["rules"]["density_rule"]["correct"] != density_all:
        errors.append("STUDY_V1 all-measured density count mismatch")
    if study["cuts"]["non_degenerate_only"]["rules"]["density_rule"]["correct"] != density_nd:
        errors.append("STUDY_V1 nondegenerate density count mismatch")
    if study["protocol_gate"].get("passes_as_written") is not False:
        errors.append("frozen protocol gate no longer fails")
    if study["verdict"].get("terminal") != "NO_DISCRIMINATION":
        errors.append("study terminal is no longer NO_DISCRIMINATION")
    if "does NOT define the outcome measurement" not in study["outcome_definition"].get("protocol_gap", ""):
        errors.append("protocol operationalization gap disappeared")
    if study["frozen_constants"] != {
        "density": ">=1.5", "modules": ">=49", "edges": ">=216", "refit": False
    }:
        errors.append("frozen rival constants changed")

    report = {
        "status": "PASS" if not errors else "MISMATCH",
        "terminal": (
            "MECHANISM_NOT_IDENTIFIABLE__CONSTANT_INFORMATIVE_OUTCOME_PLUS_LAYOUT_DEGENERACY"
            if not errors else "CANNOT_CHECK_IDENTIFIABILITY_BINDING"
        ),
        "usable": len(usable),
        "nondegenerate": len(nondeg),
        "nondegenerate_outcomes": {
            "unsound": sum(r["outcome"] == "unsound" for r in nondeg),
            "sound": sum(r["outcome"] == "sound" for r in nondeg),
        },
        "degenerate": len(degen),
        "degenerate_outcomes": {
            "unsound": sum(r["outcome"] == "unsound" for r in degen),
            "sound": sum(r["outcome"] == "sound" for r in degen),
        },
        "nondegenerate_rule_wins": {
            "density": density_nd, "module": module_nd, "edge": edge_nd
        },
        "all_rule_wins": {
            "density": density_all, "module": module_all, "edge": edge_all
        },
        "density_all_decomposition": {
            "informative_wins": density_nd,
            "degenerate_sound_credits": len(degen),
            "total": density_all,
        },
        "errors": errors,
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 5


if __name__ == "__main__":
    raise SystemExit(main())
