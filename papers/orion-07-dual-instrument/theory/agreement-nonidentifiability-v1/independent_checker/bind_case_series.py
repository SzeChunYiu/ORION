#!/usr/bin/env python3
"""Regenerate the ORION-07 case-series numbers in THEORY.md section 5 from the
immutable scored artifacts, and verify Theorem 1 holds on them with residual 0.

Issue #1609 section A requires that headline quantitative statements be generated
from immutable result artifacts rather than transcribed by hand. This script is
that generator. It reads only already-frozen files, writes only its own report,
and mutates nothing.

The V0 unit predates the per-instance directory layout; its disposition
(`AGREE + DEFERRED_ALIGNED`) is read as a literal string from the frozen claim
ledger rather than assumed, and the run fails if that string is absent.

Exit codes
    0  numbers regenerated and Theorem 1 verified with residual 0
    2  a bound artifact disagrees with the recorded numbers
    3  an artifact is missing or unreadable  (CANNOT_CHECK)
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
PAPER = PACKET.parent.parent                       # papers/orion-07-dual-instrument
LEDGER = PAPER / "CLAIM_LEDGER_PROSPECTIVE_CASE_SERIES_2026-08-23.md"
V0_DISPOSITION_MARKER = "V0 is `AGREE + DEFERRED_ALIGNED`"

INSTANCES = [
    ("Q3-R1 / QG-19", PAPER / "instances/Q3-R1-QG19/FINAL_SCORE.json"),
    ("Q3-R2 / QG-20", PAPER / "instances/Q3-R2-QG20/FINAL_SCORE.json"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    try:
        units = []

        if not LEDGER.is_file():
            raise FileNotFoundError(LEDGER)
        ledger_text = LEDGER.read_text()
        if V0_DISPOSITION_MARKER not in ledger_text:
            print(json.dumps({
                "status": "FAIL",
                "why": "V0 disposition marker absent from the frozen claim ledger",
                "expected_marker": V0_DISPOSITION_MARKER,
            }, indent=2))
            return 2
        units.append({
            "unit": "V0",
            "source": str(LEDGER.relative_to(PAPER.parent.parent)),
            "sha256": sha256(LEDGER),
            "agree": True, "x_aligned": True, "y_aligned": True,
        })

        for name, path in INSTANCES:
            if not path.is_file():
                raise FileNotFoundError(path)
            score = json.loads(path.read_text())
            rel = score["preoutcome_instrument_relation"]["responsibility"]
            units.append({
                "unit": name,
                "source": str(path.relative_to(PAPER.parent.parent)),
                "sha256": sha256(path),
                "agree": rel == "AGREE",
                "x_aligned": bool(score["lane_a"]["responsibility_alignment"]),
                "y_aligned": bool(score["lane_b"]["responsibility_alignment"]),
                "aggregate_reliability_claim_authorized":
                    score["aggregate_reliability_claim_authorized"],
            })
    except Exception as exc:                                    # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK",
                          "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 3

    n = len(units)
    a = Fraction(sum(1 for u in units if u["agree"]), n)
    c = Fraction(sum(1 for u in units if u["agree"] and u["x_aligned"]
                     and u["y_aligned"]), n)
    p_x = Fraction(sum(1 for u in units if u["x_aligned"]), n)
    p_y = Fraction(sum(1 for u in units if u["y_aligned"]), n)
    q = (p_x + p_y) / 2
    residual = q - ((1 - a) / 2 + c)

    # Guard: no artifact may authorize an aggregate reliability claim.
    reliability_guard = all(
        u.get("aggregate_reliability_claim_authorized") is not True
        for u in units
    )

    report = {
        "schema": "ORION.ORION07.AgreementNonidentifiability.CaseSeriesBinding.v1",
        "axis": "responsibility alignment against the frozen deferred map",
        "generated_from": "immutable scored artifacts; no value transcribed by hand",
        "units": units,
        "n_valid": n,
        "a_hat": str(a),
        "c_hat": str(c),
        "pX_hat": str(p_x),
        "pY_hat": str(p_y),
        "q_hat": str(q),
        "theorem_1_residual": str(residual),
        "theorem_1_holds": residual == 0,
        "theorem_2_interval_at_a_hat": [str((1 - a) / 2), str((1 + a) / 2)],
        "corollary_2_1_applies": a == 1,
        "interpretation": (
            "Observed agreement constrains mean accuracy to the stated interval. "
            "At a_hat = 1 that interval is [0,1], so the agreement carries no "
            "information about accuracy; q_hat is carried entirely by the "
            "deferred outcomes."
        ),
        "aggregate_reliability_claim_authorized_anywhere": not reliability_guard,
        "authority": "descriptive re-reading of frozen artifacts; no rescoring, "
                     "no new unit, no reliability claim",
    }
    ok = report["theorem_1_holds"] and reliability_guard
    report["status"] = "PASS" if ok else "FAIL"

    (PACKET / "CASE_SERIES_BINDING.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps({k: report[k] for k in
                      ("status", "n_valid", "a_hat", "c_hat", "q_hat",
                       "theorem_1_residual", "corollary_2_1_applies")}, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
