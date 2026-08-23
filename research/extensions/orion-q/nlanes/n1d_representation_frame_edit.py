"""ORION-Q N1-D fresh re-execution: representation-changing frame edit.

Frozen protocol: development/orion-q-nlane-closure/N1_D_PROTOCOL.md (issue #674, family N1-D).
Re-executes the registered design of issue comment 5355080062 (never committed). Deterministic
exact-synthetic diagnostic; no P10, novelty, or real-quantum authority.

Run:
    python research/extensions/orion-q/nlanes/n1d_representation_frame_edit.py
"""

from __future__ import annotations

import json
import math
import os

import numpy as np

SCHEMA = "ORIONQ.N1D_RepresentationFrameEdit.v1"
AUTHORITY = "N1D_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY"

SEED = 20260821
N_TARGETS = 2_000
TOL = 1e-12
MENU = [-math.pi / 2, -math.pi / 4, 0.0, math.pi / 4, math.pi / 2]

SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def ry(a: float) -> np.ndarray:
    c, s = math.cos(a / 2), math.sin(a / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def rz(a: float) -> np.ndarray:
    return np.diag([np.exp(-0.5j * a), np.exp(0.5j * a)])


def offdiag(u: np.ndarray) -> float:
    return float(max(abs(u[0, 1]), abs(u[1, 0])))


def main() -> None:
    rng = np.random.default_rng(SEED)
    phis, thetas = [], []
    while len(phis) < N_TARGETS:
        phi = float(rng.uniform(-1.4, 1.4))
        if min(abs(phi - m) for m in MENU) < 0.02:
            continue
        phis.append(phi)
        thetas.append(float(rng.uniform(0.2, 2.9)))
    targets = [ry(p) @ rz(t) @ ry(-p) for p, t in zip(phis, thetas)]

    menu_solved = 0
    menu_best = 0.0
    menu_cost = 0
    gen_solved = 0
    gen_max_resid = 0.0
    gen_roundtrip_max = 0.0
    gen_cost = 0
    par_solved = 0
    par_max_resid = 0.0
    par_max_nonunitary = 0.0
    par_cost = 0

    for u in targets:
        # --- Arm 1: finite frame menu (each conjugation attempt costs 1).
        best = math.inf
        hit = False
        for m in MENU:
            w = ry(-m)
            menu_cost += 1
            r = offdiag(w @ u @ w.conj().T)
            best = min(best, r)
            if r <= TOL:
                hit = True
                break
        menu_solved += int(hit)
        menu_best = max(menu_best, 0.0 if hit else best if best < math.inf else 0.0)

        # --- Arm 2: generated continuous frame edit from the Pauli axis.
        a = np.array([np.trace(s @ u) / 2 for s in (SX, SY, SZ)])
        v = -np.imag(a)  # = sin(theta/2) * n, with sin(theta/2) > 0 on the frozen theta range
        assert abs(v[1]) <= 1e-10, "unexpected y-axis component"
        phi_hat = math.atan2(v[0], v[2])
        w = ry(-phi_hat)
        gen_cost += 1
        d = w @ u @ w.conj().T
        r = offdiag(d)
        gen_max_resid = max(gen_max_resid, r)
        gen_solved += int(r <= TOL)
        back = w.conj().T @ d @ w
        gen_roundtrip_max = max(gen_roundtrip_max, float(np.max(np.abs(back - u))))

        # --- Arm 3: canonical eigendecomposition parent.
        vals, vecs = np.linalg.eig(u)
        order = np.argsort(np.angle(vals))
        vecs = vecs[:, order] / np.linalg.norm(vecs[:, order], axis=0)
        par_cost += 1
        nonuni = float(np.max(np.abs(vecs.conj().T @ vecs - np.eye(2))))
        par_max_nonunitary = max(par_max_nonunitary, nonuni)
        rr = offdiag(vecs.conj().T @ u @ vecs)
        par_max_resid = max(par_max_resid, rr)
        par_solved += int(rr <= TOL and nonuni <= 1e-10)

    gates = {
        "G1_WORLD_VALID": bool(menu_solved == 0),
        "G2_GENERATED_EXACT": bool(gen_solved == N_TARGETS and gen_max_resid <= TOL),
        "G3_ROUND_TRIP": bool(gen_roundtrip_max <= TOL),
        "G4_PARENT_GEQ_GENERATED": bool(par_solved >= gen_solved),
    }
    if not gates["G1_WORLD_VALID"]:
        terminal = "N1D_WORLD_INVALID"
    elif not gates["G2_GENERATED_EXACT"]:
        terminal = "N1D_NO_INCREMENTAL_VALUE"
    elif gates["G4_PARENT_GEQ_GENERATED"]:
        terminal = "N1D_CANONICAL_TRANSFORM_PARENT_SUFFICIENT"
    else:
        terminal = "N1D_REPRESENTATION_EDIT_VALUE"

    result = {
        "schema": SCHEMA,
        "issue": 674,
        "family": "N1-D",
        "reexecution_of": "issue-674 comment 5355080062 (original run never committed)",
        "protocol": "development/orion-q-nlane-closure/N1_D_PROTOCOL.md",
        "date": "2026-08-21",
        "seed": SEED,
        "world": {
            "targets": N_TARGETS,
            "family": "U(phi,theta) = Ry(phi) Rz(theta) Ry(-phi), continuous phi/theta",
            "menu": MENU,
            "tolerance": TOL,
        },
        "arms": {
            "FINITE_FRAME_MENU": {
                "solved_of_2000": menu_solved,
                "conjugation_cost_total": menu_cost,
                "mean_cost_per_target": menu_cost / N_TARGETS,
            },
            "GENERATED_FRAME_EDIT": {
                "solved_of_2000": gen_solved,
                "max_offdiag_residual": gen_max_resid,
                "roundtrip_max_error": gen_roundtrip_max,
                "conjugation_cost_total": gen_cost,
                "mean_cost_per_target": gen_cost / N_TARGETS,
            },
            "EIGENDECOMPOSITION_PARENT": {
                "solved_of_2000": par_solved,
                "max_offdiag_residual": par_max_resid,
                "max_nonunitarity": par_max_nonunitary,
                "conjugation_cost_total": par_cost,
                "mean_cost_per_target": par_cost / N_TARGETS,
            },
        },
        "gates": gates,
        "terminal": terminal,
        "root_cause": "KNOWN_TRANSFORM_PARENT_SUFFICIENT" if terminal == "N1D_CANONICAL_TRANSFORM_PARENT_SUFFICIENT" else None,
        "authority": AUTHORITY,
        "claim_boundary": (
            "Exact-synthetic diagnostic only. A generated continuous frame beats a finite "
            "representation menu, but canonical eigendecomposition supplies the same "
            "representation once the full operator is visible; no representation-invention, "
            "novelty, P10, or real-quantum claim is authorized."
        ),
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N1_D_REPRESENTATION_EDIT_RESULTS.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N1D_REPRESENTATION_EDIT=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
