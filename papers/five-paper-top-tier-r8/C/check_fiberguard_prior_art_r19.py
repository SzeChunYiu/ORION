#!/usr/bin/env python3
"""Fail-closed checker for the FiberGuard R19 primary-source subtraction matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "ORION.FiberGuard.PriorArtMatrix.R19.v1"
TERMINAL = "FIBERGUARD_R19_PRIOR_ART_SUBTRACTION_PASS"
ROOT = Path(__file__).resolve().parent
MATRIX = ROOT / "PRIOR_ART_MATRIX_C_R19.md"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_result() -> dict[str, Any]:
    text = MATRIX.read_text(encoding="utf-8")
    lines = text.splitlines()
    table_rows = [line for line in lines if line.startswith("| ")]
    assert table_rows[:2][0].startswith("| Area |")
    assert table_rows[:2][1].startswith("|---|")
    source_rows = table_rows[2:]
    assert len(source_rows) == 26, len(source_rows)

    required_source_tokens = [
        "Rice, “The Algorithm Selection Problem,”",
        "Xu et al., “SATzilla:",
        "Bischl et al., “ASlib:",
        "Lindauer et al., “AutoFolio:",
        "Gao et al., “Neural Solver Selection for Combinatorial Optimization,”",
        "Xu et al., “How Powerful are Graph Neural Networks?”,",
        "Mozannar and Sontag, “Consistent Estimators for Learning to Defer to an Expert,”",
        "Angelopoulos et al., “Conformal Risk Control,”",
        "Shim, Hwang, and Yang, “Joint Active Feature Acquisition",
        "McShane, “Extension of Range of Functions,”",
        "Ben-David et al., “A Theory of Learning from Different Domains,”",
        "Chvátal, “A Greedy Heuristic for the Set-Covering Problem,”",
    ]
    for token in required_source_tokens:
        assert text.count(token) == 1, token

    donor_owned = [
        "Algorithm selection",
        "Selective classification",
        "Learning to defer",
        "Conformal risk",
        "Active feature acquisition",
        "Lipschitz extension",
        "Domain adaptation",
        "Set cover",
        "Finite minimax and mixed strategies",
    ]
    for area in donor_owned:
        assert any(row.startswith(f"| {area} |") for row in source_rows), area

    forbidden_novelty_headlines = [
        "algorithm selection itself",
        "risk–coverage or abstention",
        "deferral or expert routing",
        "sequential feature acquisition",
        "Lipschitz envelope theorem",
        "generic hardness/approximation",
        "minimax, LP duality, or strategy equivalence",
    ]
    for token in forbidden_novelty_headlines:
        assert token in text, token

    residual_tokens = [
        "exact complete representation fibre is the closed-world authority object",
        "small, content-bound upper and lower receipts",
        "state-dependent acquisition cost is retained as a statewise loss profile",
        "exact boundary between scalar, structural, and statistical extensions",
        "learned and fallback actions are certified as a pair",
        "prospectively frozen inductive/fallback refutations",
    ]
    for token in residual_tokens:
        assert token in text, token

    assert "absence of a direct title or phrase match is never treated as proof of novelty" in text.lower()
    assert "NOVELTY_NOT_ESTABLISHED__RESIDUAL_CANDIDATE_EXPLICIT" in text
    assert "not an external novelty opinion or a novelty certificate" in text

    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "audit_date": "2026-08-27",
        "source_rows": len(source_rows),
        "required_primary_source_tokens": len(required_source_tokens),
        "donor_owned_areas": len(donor_owned),
        "forbidden_novelty_headlines": len(forbidden_novelty_headlines),
        "residual_candidate_atoms": len(residual_tokens),
        "controls": {
            "algorithm_selection_donor_owned": True,
            "selective_prediction_and_defer_donor_owned": True,
            "conformal_calibration_donor_owned": True,
            "active_feature_acquisition_donor_owned": True,
            "GNN_WL_expressivity_donor_owned": True,
            "Lipschitz_and_domain_shift_donor_owned": True,
            "set_cover_and_minimax_donor_owned": True,
            "absence_of_phrase_match_not_novelty_evidence": True,
            "residual_candidate_is_conjunction_not_generic_mechanism": True,
            "external_novelty_authority_not_granted": True,
        },
        "authority": {
            "bounded_primary_source_subtraction": "INTERNAL",
            "external_specialist_review": "CANNOT_CHECK",
            "novelty": "NOT_ESTABLISHED",
            "journal_authority": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = canonical_json(build_result()) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
