#!/usr/bin/env python3
"""Fail-closed static authority gate for Wave-A quantum papers ORION-05/09/10.

This gate is intentionally separate from ``papers/check_q_qg_publication.py``.
That historical checker protects the six-paper Q/QG synthesis chronology and
contains wording contracts for manuscripts that are not Wave-A submission
objects. Wave A instead checks the *current* bounded authority objects used by
ORION-05, ORION-09 and ORION-10. Heavy independent execution is performed by
``run_wave_a_quantum_replays.py`` immediately afterwards.

A PASS grants no novelty, physical-quantum, acceptance or submission authority.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

R11_RESULT = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json"
R11_PROTOCOL = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
R11_SOLVER = ROOT / "papers/orion-05-tare-expressivity/q1_r11_sparse_direct_solver.py"
R11_PAIR_CHECKER = ROOT / "papers/orion-05-tare-expressivity/q1_r11_pair_count_independent.py"
QG1_MANUSCRIPT = ROOT / "papers/orion-09-compilation-regime-geometry/MANUSCRIPT_V3.md"
QG2_MANUSCRIPT = ROOT / "papers/orion-10-certified-static-forecasting/MANUSCRIPT_V3.md"
QG_PROGRAMME = ROOT / "research/extensions/orion-qg/ORION_QG_PROGRAMME_SCIENTIFIC_CLOSURE_RESULTS.json"

R11_TERMINAL = "Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM"
QG_PROGRAMME_TERMINAL = (
    "ORION_QG_PROGRAMME_SCIENTIFICALLY_CLOSED__"
    "THEOREMS_REFUTATIONS_AND_BOUNDED_CANNOT_CHECKS_RECEIPTED__NOT_NOVELTY_AUTHORITY"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def require_all(body: str, label: str, tokens: tuple[str, ...], errors: list[str]) -> None:
    lower = body.lower()
    for token in tokens:
        if token.lower() not in lower:
            errors.append(f"{label}_MISSING:{token}")


def require_any(body: str, label: str, alternatives: tuple[str, ...], errors: list[str]) -> None:
    lower = body.lower()
    if not any(token.lower() in lower for token in alternatives):
        errors.append(f"{label}_MISSING_ANY:{' | '.join(alternatives)}")


def main() -> int:
    errors: list[str] = []

    for path in (R11_RESULT, R11_PROTOCOL, R11_SOLVER, R11_PAIR_CHECKER, QG1_MANUSCRIPT, QG2_MANUSCRIPT, QG_PROGRAMME):
        if not path.is_file():
            errors.append(f"MISSING_REQUIRED:{path.relative_to(ROOT)}")
    if errors:
        print("WAVE_A_QUANTUM_AUTHORITY_CHECK=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    # ORION-05: the current Wave-A projection may consume R11 only if the
    # committed result remains theorem-scoped, all executable gates are green,
    # and the live protocol/solver/independent-checker bytes still match it.
    r11 = load_json(R11_RESULT)
    if r11.get("terminal") != R11_TERMINAL:
        errors.append(f"ORION05_R11_TERMINAL:{r11.get('terminal')}")
    authority = r11.get("authority", {})
    expected = {
        "algorithmic_theorem": True,
        "novelty_authority": False,
        "physical_quantum_resource_authority": False,
        "production_runtime_value": False,
        "submission_authority": False,
        "scope": "frozen R6M six-slot grammar and declared objective only",
    }
    if not isinstance(authority, dict):
        errors.append("ORION05_R11_AUTHORITY_OBJECT_MISSING")
    else:
        for key, value in expected.items():
            if authority.get(key) != value:
                errors.append(f"ORION05_R11_AUTHORITY_DRIFT:{key}")
    gates = r11.get("gates", {})
    if not isinstance(gates, dict) or not gates or not all(gates.values()):
        errors.append("ORION05_R11_GATES_NOT_ALL_GREEN")
    complete = r11.get("complete_n1", {})
    if complete.get("pass") is not True or complete.get("denominator") != 729:
        errors.append("ORION05_R11_COMPLETE_N1_DRIFT")
    if r11.get("protocol_sha256") != sha256(R11_PROTOCOL):
        errors.append("ORION05_R11_PROTOCOL_DIGEST_DRIFT")
    if r11.get("solver_sha256") != sha256(R11_SOLVER):
        errors.append("ORION05_R11_SOLVER_DIGEST_DRIFT")
    if r11.get("pair_checker_sha256") != sha256(R11_PAIR_CHECKER):
        errors.append("ORION05_R11_INDEPENDENT_CHECKER_DIGEST_DRIFT")

    # ORION-09: enforce the current multi-coordinate scientific object rather
    # than obsolete prose sentences. These are scope/boundary invariants; fresh
    # theorem replays are executed separately by the quantum replay runner.
    qg1 = QG1_MANUSCRIPT.read_text(encoding="utf-8")
    require_all(
        qg1,
        "ORION09",
        (
            "intrinsic support",
            "proof-derived ceiling",
            "objective-indexed certificate",
            "prospective falsification",
            "not a claim that all compiler families",
        ),
        errors,
    )
    require_any(
        qg1,
        "ORION09_FEATURE_IDENTIFIABILITY",
        (
            "identical feature vectors carry both labels",
            "feature vocabulary cannot determine",
            "irreducible 43/1,146 error floor",
        ),
        errors,
    )
    require_any(qg1, "ORION09_DONOR", ("instance space analysis", "algorithm-selection problem"), errors)

    # ORION-10: preserve the four authority layers and the explicit subtraction
    # of generic static quantum-cost/resource-estimation novelty. The novelty
    # boundary uses alternatives so ordinary Markdown emphasis cannot make a
    # semantically unchanged sentence fail the gate.
    qg2 = QG2_MANUSCRIPT.read_text(encoding="utf-8")
    require_all(
        qg2,
        "ORION10",
        (
            "constructive upper-bound layer",
            "theorem-backed support/exact-family layer",
            "finite/conjectural closed-form layer",
            "forecast-only layer",
            "qet",
        ),
        errors,
    )
    require_any(
        qg2,
        "ORION10_GENERIC_NOVELTY_SUBTRACTION",
        (
            "contribution here is not the generic idea",
            "claim novelty for static quantum cost analysis",
        ),
        errors,
    )
    require_any(
        qg2,
        "ORION10_SCOPE",
        (
            "compiler-specific case study in authority-layered forecasting and falsification",
            "not predictive dominance over current quantum cost-analysis tools",
        ),
        errors,
    )

    # Programme history must retain theorem/refutation/CANNOT_CHECK separation.
    programme = load_json(QG_PROGRAMME)
    if programme.get("terminal") != QG_PROGRAMME_TERMINAL:
        errors.append(f"QG_PROGRAMME_TERMINAL:{programme.get('terminal')}")
    if programme.get("scientifically_closed") is not True or programme.get("all_gates") is not True:
        errors.append("QG_PROGRAMME_GATES_NOT_CLOSED")
    if programme.get("novelty_authority") is not False:
        errors.append("QG_PROGRAMME_ILLEGAL_NOVELTY_AUTHORITY")
    cannot = programme.get("bounded_cannot_checks", {})
    if not isinstance(cannot, dict) or not {"qg7d", "qg11"}.issubset(cannot):
        errors.append("QG_PROGRAMME_CANNOT_CHECK_HISTORY_DRIFT")

    if errors:
        print("WAVE_A_QUANTUM_AUTHORITY_CHECK=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("WAVE_A_QUANTUM_AUTHORITY_CHECK=PASS")
    print("ORION05_R11=BOUND_THEOREM_SCOPED")
    print("ORION09=CURRENT_MULTI_COORDINATE_BOUNDARY_PRESENT")
    print("ORION10=CURRENT_AUTHORITY_LAYERS_PRESENT")
    print("QG_NEGATIVE_HISTORY=RETAINED")
    print("SCIENTIFIC_AUTHORITY_DELTA=NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
