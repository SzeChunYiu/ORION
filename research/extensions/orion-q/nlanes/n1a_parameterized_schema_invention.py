"""ORION-Q N1-A fresh re-execution: parameterized operator-schema invention.

Frozen protocol: development/orion-q-nlane-closure/N1_A_PROTOCOL.md (issue #674, family N1-A).
Re-executes the registered design of issue comment 5355044616 (never committed). Deterministic
exact-synthetic diagnostic; no P10, novelty, or real-quantum authority.

Run:
    python research/extensions/orion-q/nlanes/n1a_parameterized_schema_invention.py
"""

from __future__ import annotations

import itertools
import json
import math
import os

import numpy as np

TOL = 1e-12
SCHEMA = "ORIONQ.N1A_ParamSchemaInvention.v1"
AUTHORITY = "N1A_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY"

TRAIN_X = np.array([-1.2 + 0.2 * j for j in range(13)])
TEST_X = np.array([-1.5 + 0.185 * i for i in range(17)])
FINITE_ANGLES = np.array([k * math.pi / 8 for k in range(-8, 9)])


def theta_true(x: np.ndarray) -> np.ndarray:
    """Hidden target schema (evaluator-owned)."""
    return 0.7 * x - 0.4 * x**3


def rz(theta: float) -> np.ndarray:
    return np.diag([np.exp(-0.5j * theta), np.exp(0.5j * theta)])


def crz(theta: float) -> np.ndarray:
    u = np.eye(4, dtype=complex)
    u[2, 2] = np.exp(-0.5j * theta)
    u[3, 3] = np.exp(0.5j * theta)
    return u


def wrap(a: np.ndarray) -> np.ndarray:
    return (a + math.pi) % (2 * math.pi) - math.pi


def phase_of_rz(u: np.ndarray) -> float:
    """Phase-safe relative-phase extraction for Rz-type unitaries."""
    return float(np.angle(u[-1, -1] / u[-2, -2]))


def phase_err(target_theta: np.ndarray, cand_theta: np.ndarray) -> np.ndarray:
    return np.abs(wrap(target_theta - cand_theta))


def solves(target_theta: np.ndarray, cand_theta: np.ndarray) -> tuple[int, float]:
    err = phase_err(target_theta, cand_theta)
    return int(np.sum(err <= TOL)), float(np.max(err))


def main() -> None:
    assert not set(np.round(TRAIN_X, 12)) & set(np.round(TEST_X, 12)), "train/test overlap"
    th_train = theta_true(TRAIN_X)
    th_test = theta_true(TEST_X)
    assert float(np.max(np.abs(th_train))) < math.pi and float(np.max(np.abs(th_test))) < math.pi

    # Verifier sanity: phase extraction through the actual unitaries is exact.
    extract_train = np.array([phase_of_rz(rz(t)) for t in th_train])
    extract_crz = np.array([phase_of_rz(crz(t)) for t in th_test])
    assert float(np.max(np.abs(wrap(extract_train - th_train)))) < 1e-14
    assert float(np.max(np.abs(wrap(extract_crz - th_test)))) < 1e-14

    # --- Arm 1: finite fixed-angle edit enumeration (best angle per instance).
    def finite_arm(th: np.ndarray) -> tuple[int, float]:
        best = FINITE_ANGLES[
            np.argmin(np.abs(wrap(th[:, None] - FINITE_ANGLES[None, :])), axis=1)
        ]
        return solves(th, best)

    fin_train_solved, _ = finite_arm(th_train)
    fin_test_solved, fin_test_err = finite_arm(th_test)
    fin_crz_solved, fin_crz_err = finite_arm(th_test)  # same fixed-angle CRz library

    # --- Arm 2: ORION obstruction-driven schema invention.
    # Certified obstruction per failed train instance = exact required residual phase.
    # (a) odd-symmetry pattern check on paired train coordinates.
    sym_ok = True
    for j, x in enumerate(TRAIN_X):
        k = np.argmin(np.abs(TRAIN_X + x))
        if abs(TRAIN_X[k] + x) < 1e-12:
            sym_ok &= abs(th_train[j] + th_train[k]) < 1e-12
    assert sym_ok, "odd-symmetry probe failed; schema proposal not licensed"
    # (b) typed odd-cubic schema theta_hat = a*x + b*x^3, exact least squares on obstructions.
    A = np.stack([TRAIN_X, TRAIN_X**3], axis=1)
    coef, *_ = np.linalg.lstsq(A, th_train, rcond=None)
    orion_train = A @ coef
    assert float(np.max(np.abs(orion_train - th_train))) <= TOL, "train verification failed"
    orion_test = np.stack([TEST_X, TEST_X**3], axis=1) @ coef
    orion_test_solved, orion_test_err = solves(th_test, orion_test)
    orion_crz_solved, orion_crz_err = solves(th_test, orion_test)  # exact transfer, no refit

    # --- Arm 3: symbolic-synthesis parent (same visible pairs, superset vocabulary).
    basis = {
        "x": TRAIN_X,
        "x2": TRAIN_X**2,
        "x3": TRAIN_X**3,
        "sin": np.sin(TRAIN_X),
        "cosm1": np.cos(TRAIN_X) - 1.0,
        "x5": TRAIN_X**5,
    }
    basis_test = {
        "x": TEST_X,
        "x2": TEST_X**2,
        "x3": TEST_X**3,
        "sin": np.sin(TEST_X),
        "cosm1": np.cos(TEST_X) - 1.0,
        "x5": TEST_X**5,
    }
    names = sorted(basis)
    best_sub, best_err, best_coef = None, np.inf, None
    for r in (1, 2, 3):
        for sub in itertools.combinations(names, r):
            M = np.stack([basis[n] for n in sub], axis=1)
            c, *_ = np.linalg.lstsq(M, th_train, rcond=None)
            e = float(np.max(np.abs(M @ c - th_train)))
            if e < best_err - 1e-15:
                best_sub, best_err, best_coef = sub, e, c
        if best_err <= TOL:
            break  # minimal-size exact subset wins (frozen tie rule)
    parent_test = np.stack([basis_test[n] for n in best_sub], axis=1) @ best_coef
    parent_test_solved, parent_test_err = solves(th_test, parent_test)
    parent_crz_solved, parent_crz_err = solves(th_test, parent_test)

    # --- Arm 4: lookup interpolation control.
    lookup_test = np.interp(TEST_X, TRAIN_X, th_train)
    lookup_solved, lookup_err = solves(th_test, lookup_test)

    gates = {
        "G1_WORLD_VALID": bool(fin_test_solved == 0 and fin_crz_solved == 0),
        "G2_LOOKUP_FAILS": bool(lookup_solved == 0),
        "G3_ORION_EXACT": bool(
            orion_test_solved == 17 and orion_crz_solved == 17 and orion_test_err <= TOL
        ),
        "G4_PARENT_GEQ_ORION": bool(
            parent_test_solved >= orion_test_solved and parent_crz_solved >= orion_crz_solved
        ),
    }
    if not (gates["G1_WORLD_VALID"] and gates["G2_LOOKUP_FAILS"]):
        terminal = "N1A_WORLD_INVALID"
    elif not gates["G3_ORION_EXACT"]:
        terminal = "N1A_NO_INCREMENTAL_VALUE"
    elif gates["G4_PARENT_GEQ_ORION"]:
        terminal = "N1A_SYMBOLIC_SYNTHESIS_PARENT_SUFFICIENT"
    else:
        terminal = "N1A_SCHEMA_INVENTION_SUPPORTED"

    result = {
        "schema": SCHEMA,
        "issue": 674,
        "family": "N1-A",
        "reexecution_of": "issue-674 comment 5355044616 (original run never committed)",
        "protocol": "development/orion-q-nlane-closure/N1_A_PROTOCOL.md",
        "date": "2026-08-21",
        "deterministic": True,
        "world": {
            "target": "U(x)=Rz(theta(x)), theta(x)=0.7x-0.4x^3 (hidden)",
            "train_points": 13,
            "test_points": 17,
            "held_out_family": "CRz(theta(x)) two-qubit, same 17 test coordinates",
            "finite_library": "17 fixed angles k*pi/8, k=-8..8",
            "tolerance": TOL,
        },
        "arms": {
            "FINITE_EDIT_ENUMERATION": {
                "train_solved_of_13": fin_train_solved,
                "test_solved_of_17": fin_test_solved,
                "test_max_phase_err": fin_test_err,
                "crz_solved_of_17": fin_crz_solved,
                "crz_max_phase_err": fin_crz_err,
            },
            "ORION_SCHEMA_INVENTION": {
                "fitted_schema": "theta_hat(x) = a*x + b*x^3",
                "a": float(coef[0]),
                "b": float(coef[1]),
                "test_solved_of_17": orion_test_solved,
                "test_max_phase_err": orion_test_err,
                "crz_solved_of_17": orion_crz_solved,
                "crz_max_phase_err": orion_crz_err,
            },
            "SYMBOLIC_SYNTHESIS_PARENT": {
                "selected_terms": list(best_sub),
                "coefficients": [float(v) for v in best_coef],
                "train_max_err": best_err,
                "test_solved_of_17": parent_test_solved,
                "test_max_phase_err": parent_test_err,
                "crz_solved_of_17": parent_crz_solved,
                "crz_max_phase_err": parent_crz_err,
            },
            "LOOKUP_INTERPOLATION_CONTROL": {
                "test_solved_of_17": lookup_solved,
                "test_max_phase_err": lookup_err,
            },
        },
        "gates": gates,
        "terminal": terminal,
        "authority": AUTHORITY,
        "claim_boundary": (
            "Exact-synthetic diagnostic only. A continuous parameterized schema genuinely escapes "
            "the finite edit list, but generic symbolic synthesis with the same evidence closes the "
            "task; no ORION-specific method-invention value, no novelty over CEGIS(T)/DreamCoder-"
            "family parents, and no real-quantum authority is claimed."
        ),
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N1_A_PARAM_SCHEMA_RESULTS.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N1A_PARAM_SCHEMA=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
