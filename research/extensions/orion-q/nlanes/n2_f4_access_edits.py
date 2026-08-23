"""ORION-Q N2-F4: representation/access edits under a NO_STRONGER_ORACLE gate.

Executes successor family 4 of issue #675 exactly as frozen in
development/orion-q-nlane-closure/N2_F4_PROTOCOL.md (protocol frozen before outcomes).

Exact-synthetic scope only: frozen accounting cost model (Q = d*alpha, counted
classical preprocessing, mu = 1e-3). Not a compiled circuit estimator; any residual
is accounting-level and contingent on the frozen counters.
"""

from __future__ import annotations

import itertools
import json
import math
import os

import numpy as np

SEED = 20260821
N_QUBITS = 4
DEGREE = 32
MU = 1e-3
TOL_ALPHA = 1e-9
TOL_TARGET = 1e-10
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(HERE, "N2_F4_ACCESS_EDITS_RESULTS.json")

PAULI = {
    "I": np.array([[1, 0], [0, 1]], dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def pauli_matrix(string: str) -> np.ndarray:
    m = PAULI[string[0]]
    for ch in string[1:]:
        m = np.kron(m, PAULI[ch])
    return m


def build_matrix(rep: dict) -> np.ndarray:
    m = np.zeros((2 ** N_QUBITS, 2 ** N_QUBITS), dtype=complex)
    for s, a in zip(rep["strings"], rep["coeffs"]):
        m = m + a * pauli_matrix(s)
    return m


# ---------------- admissible alpha derivations (the only lawful tags) ----------------

def alpha_l1(rep: dict) -> float:
    return float(sum(abs(a) for a in rep["coeffs"]))


def alpha_grouped_l2(rep: dict, m: int) -> float:
    coeffs = sorted((abs(a) for a in rep["coeffs"]), reverse=True)
    L = len(coeffs)
    if L % m:
        raise ValueError("m must divide L")
    return float(sum(
        math.sqrt(m) * math.sqrt(sum(x * x for x in coeffs[i:i + m]))
        for i in range(0, L, m)
    ))


def sparse_stats(rep: dict) -> tuple[int, float]:
    """Row sparsity s and ||A||_max, computed exactly FROM THE REPRESENTATION.

    Each Pauli string maps computational row i to a single column (its X/Y flip
    pattern); entries with a shared flip pattern combine. s = max over rows of
    distinct nonzero flip-pattern contributions; ||A||_max from the exact matrix
    (equivalently computable by summing signed coefficients per pattern).
    """
    A = build_matrix(rep)
    s = int(max(np.count_nonzero(np.abs(A[i, :]) > 1e-14) for i in range(A.shape[0])))
    s = max(s, 1)
    a_max = float(np.max(np.abs(A)))
    return s, a_max


def alpha_sparse(rep: dict) -> float:
    s, a_max = sparse_stats(rep)
    return float(s * a_max)


def recompute_alpha(rep: dict, tag: str) -> float:
    if tag == "l1":
        return alpha_l1(rep)
    if tag.startswith("grouped_l2_m"):
        return alpha_grouped_l2(rep, int(tag.rsplit("m", 1)[1]))
    if tag == "sparse":
        return alpha_sparse(rep)
    raise ValueError(f"inadmissible derivation tag: {tag}")


def ancillas_for(rep: dict, tag: str) -> int:
    if tag == "sparse":
        s, _ = sparse_stats(rep)
        return int(math.ceil(math.log2(max(s, 2)))) + 1
    return int(math.ceil(math.log2(max(len(rep["coeffs"]), 2))))


# ---------------- edits ----------------

def edit_merge(rep: dict) -> tuple[dict, float]:
    L = len(rep["coeffs"])
    acc: dict[str, float] = {}
    order: list[str] = []
    for s, a in zip(rep["strings"], rep["coeffs"]):
        if s not in acc:
            acc[s] = 0.0
            order.append(s)
        acc[s] += a
    strings = [s for s in order if abs(acc[s]) > 1e-15]
    new = {"strings": strings, "coeffs": [acc[s] for s in strings], "tag": "l1"}
    return new, float(L)  # preprocessing counter: merge = L_current


def edit_regroup(rep: dict, m: int) -> tuple[dict, float] | None:
    L = len(rep["coeffs"])
    if L % m:
        return None
    new = dict(rep)
    new["tag"] = f"grouped_l2_m{m}"
    return new, float(L * math.ceil(math.log2(max(L, 2))) + L)


def edit_sparse(rep: dict) -> tuple[dict, float]:
    L = len(rep["coeffs"])
    new = dict(rep)
    new["tag"] = "sparse"
    return new, float(L * L + 16 * L)


EDIT_KINDS = ["merge", "regroup2", "regroup4", "sparse"]


def apply_edit(rep: dict, kind: str) -> tuple[dict, float] | None:
    if kind == "merge":
        return edit_merge(rep)
    if kind == "regroup2":
        return edit_regroup(rep, 2)
    if kind == "regroup4":
        return edit_regroup(rep, 4)
    if kind == "sparse":
        return edit_sparse(rep)
    raise ValueError(kind)


# ---------------- NO_STRONGER_ORACLE / SAME_TARGET checker ----------------

def check_edit(rep_before: dict, rep_after: dict, claimed_alpha: float,
               target: np.ndarray) -> tuple[bool, str]:
    try:
        lawful = recompute_alpha(rep_after, rep_after["tag"])
    except ValueError:
        return False, "NO_STRONGER_ORACLE:inadmissible_tag"
    if claimed_alpha < lawful - TOL_ALPHA:
        return False, "NO_STRONGER_ORACLE:claimed_alpha_below_lawful_derivation"
    dev = float(np.max(np.abs(build_matrix(rep_after) - target)))
    if dev > TOL_TARGET:
        return False, "TARGET_CHANGED"
    return True, "OK"


def scalar_cost(alpha: float, preproc: float) -> float:
    return DEGREE * alpha + MU * preproc


# ---------------- instance generation ----------------

def make_pool(rng: np.random.Generator) -> list[str]:
    all_strings = ["".join(p) for p in itertools.product("IXYZ", repeat=N_QUBITS)]
    idx = rng.choice(len(all_strings), size=40, replace=False)
    return [all_strings[i] for i in sorted(idx)]


def make_instances(rng: np.random.Generator, pool: list[str], n: int) -> list[dict]:
    out = []
    for _ in range(n):
        L = int(rng.choice([12, 20, 32]))
        strings = [pool[int(i)] for i in rng.integers(0, len(pool), size=L)]
        coeffs = [round(float(rng.uniform(-1, 1)), 6) for _ in range(L)]
        out.append({"strings": strings, "coeffs": coeffs, "tag": "l1"})
    return out


# ---------------- arms ----------------

def orion_chain(rep0: dict, target: np.ndarray) -> dict:
    """Exhaustive typed search over admissible edit chains up to length 3."""
    best = None
    chains = [()]
    for r in (1, 2, 3):
        chains += [c for c in itertools.permutations(EDIT_KINDS, r)]
    for chain in chains:
        rep = rep0
        preproc = 0.0
        ok = True
        receipts = []
        for kind in chain:
            step = apply_edit(rep, kind)
            if step is None:
                ok = False
                break
            new_rep, cost = step
            alpha_claim = recompute_alpha(new_rep, new_rep["tag"])
            passed, why = check_edit(rep, new_rep, alpha_claim, target)
            receipts.append({"edit": kind, "verdict": why})
            if not passed:
                ok = False
                break
            rep, preproc = new_rep, preproc + cost
        if not ok:
            continue
        alpha = recompute_alpha(rep, rep["tag"])
        cost = scalar_cost(alpha, preproc)
        if best is None or cost < best["scalar_cost"] - 1e-15:
            best = {
                "chain": list(chain), "alpha": alpha, "preproc": preproc,
                "queries": DEGREE * alpha, "ancillas": ancillas_for(rep, rep["tag"]),
                "scalar_cost": cost, "receipts": receipts,
            }
    return best


def single_edit_best(rep0: dict, target: np.ndarray) -> dict:
    best = {"chain": [], "alpha": alpha_l1(rep0), "preproc": 0.0,
            "scalar_cost": scalar_cost(alpha_l1(rep0), 0.0)}
    for kind in EDIT_KINDS:
        step = apply_edit(rep0, kind)
        if step is None:
            continue
        new_rep, cost = step
        alpha = recompute_alpha(new_rep, new_rep["tag"])
        passed, _ = check_edit(rep0, new_rep, alpha, target)
        if not passed:
            continue
        sc = scalar_cost(alpha, cost)
        if sc < best["scalar_cost"] - 1e-15:
            best = {"chain": [kind], "alpha": alpha, "preproc": cost, "scalar_cost": sc}
    return best


def retrain_from_scratch(rep0: dict, target: np.ndarray) -> dict:
    merged, _ = edit_merge(rep0)
    sparse_rep, _ = edit_sparse(merged)
    alpha = recompute_alpha(sparse_rep, "sparse")
    alpha = min(alpha, alpha_l1(merged))  # retrainer picks its best admissible rep
    preproc = float(4 ** N_QUBITS * N_QUBITS)
    return {"alpha": alpha, "preproc": preproc, "scalar_cost": scalar_cost(alpha, preproc)}


# ---------------- laundering attempts (must be rejected) ----------------

def laundering_verdicts(rep0: dict, target: np.ndarray) -> dict:
    A = build_matrix(rep0)
    spectral = float(np.max(np.abs(np.linalg.eigvalsh((A + A.conj().T) / 2.0))))
    # LA1: tag "sparse" but claimed alpha = ||A||_2 (stronger oracle smuggle)
    la1_rep = dict(rep0)
    la1_rep["tag"] = "sparse"
    la1_ok, la1_why = check_edit(rep0, la1_rep, spectral, target)
    # LA2: drop small terms then honest l1 (changes the target). Per protocol
    # Amendment A1 the attempt is never a no-op: if no |a| < 0.05 term exists,
    # the single smallest-magnitude term is deleted instead.
    kept = [(s, a) for s, a in zip(rep0["strings"], rep0["coeffs"]) if abs(a) >= 0.05]
    if len(kept) == len(rep0["coeffs"]) and kept:
        smallest = min(range(len(kept)), key=lambda i: abs(kept[i][1]))
        kept = [x for i, x in enumerate(kept) if i != smallest]
    la2_rep = {"strings": [s for s, _ in kept], "coeffs": [a for _, a in kept], "tag": "l1"}
    la2_ok, la2_why = check_edit(rep0, la2_rep, alpha_l1(la2_rep), target)
    return {
        "spectral_norm": spectral,
        "LA1_spectral_smuggle": {"rejected": not la1_ok, "verdict": la1_why},
        "LA2_drop_small_terms": {"rejected": not la2_ok, "verdict": la2_why},
    }


# ---------------- pipeline ----------------

def pipeline() -> dict:
    rng = np.random.default_rng(SEED)
    pool = make_pool(rng)
    instances = make_instances(rng, pool, 60)

    per_instance = []
    la1_rejected = la2_rejected = 0
    consistency_ok = target_ok = True
    orion_wins = 0
    for rep0 in instances:
        target = build_matrix(rep0)
        orion = orion_chain(rep0, target)
        b0 = scalar_cost(alpha_l1(rep0), 0.0)
        b1 = single_edit_best(rep0, target)
        b2 = retrain_from_scratch(rep0, target)
        laund = laundering_verdicts(rep0, target)
        la1_rejected += laund["LA1_spectral_smuggle"]["rejected"]
        la2_rejected += laund["LA2_drop_small_terms"]["rejected"]
        if orion["alpha"] < laund["spectral_norm"] - TOL_ALPHA:
            consistency_ok = False
        if any(r["verdict"] != "OK" for r in orion["receipts"]):
            target_ok = False
        best_baseline = min(b0, b1["scalar_cost"], b2["scalar_cost"])
        win = orion["scalar_cost"] < best_baseline - 1e-9
        orion_wins += win
        per_instance.append({
            "L_raw": len(rep0["coeffs"]),
            "orion_chain": orion["chain"],
            "orion_alpha": orion["alpha"],
            "orion_scalar_cost": orion["scalar_cost"],
            "orion_queries": orion["queries"],
            "orion_ancillas": orion["ancillas"],
            "orion_preproc": orion["preproc"],
            "b0_no_edit_cost": b0,
            "b1_single_edit_cost": b1["scalar_cost"],
            "b1_single_edit": b1["chain"],
            "b2_retrain_cost": b2["scalar_cost"],
            "forbidden_spectral_bound_queries": DEGREE * laund["spectral_norm"],
            "orion_beats_all_baselines": bool(win),
            "laundering": {
                "LA1_rejected": laund["LA1_spectral_smuggle"]["rejected"],
                "LA1_verdict": laund["LA1_spectral_smuggle"]["verdict"],
                "LA2_rejected": laund["LA2_drop_small_terms"]["rejected"],
                "LA2_verdict": laund["LA2_drop_small_terms"]["verdict"],
            },
        })

    n = len(instances)
    win_frac = orion_wins / n
    gates = {
        "F4_G2_laundering_caught": la1_rejected == n and la2_rejected == n,
        "F4_G3_no_admissible_beats_spectral_bound": consistency_ok,
        "F4_G4_same_target": target_ok,
        "F4_G5_residual": win_frac >= 0.60,
    }
    chains_used = sorted({json.dumps(pi["orion_chain"]) for pi in per_instance})
    summary = {
        "n_instances": n,
        "orion_win_fraction": win_frac,
        "mean_orion_scalar_cost": float(np.mean([p["orion_scalar_cost"] for p in per_instance])),
        "mean_b0_cost": float(np.mean([p["b0_no_edit_cost"] for p in per_instance])),
        "mean_b1_cost": float(np.mean([p["b1_single_edit_cost"] for p in per_instance])),
        "mean_b2_cost": float(np.mean([p["b2_retrain_cost"] for p in per_instance])),
        "mean_forbidden_bound_queries": float(np.mean(
            [p["forbidden_spectral_bound_queries"] for p in per_instance])),
        "la1_rejection_rate": la1_rejected / n,
        "la2_rejection_rate": la2_rejected / n,
        "distinct_orion_chains": [json.loads(c) for c in chains_used],
    }
    return {
        "schema": "ORIONQ.N2F4AccessEditsResult.v1",
        "issue": "SzeChunYiu/ORION#675",
        "family": "successor_family_4_representation_access_edits",
        "protocol": "development/orion-q-nlane-closure/N2_F4_PROTOCOL.md",
        "seed": SEED,
        "degree": DEGREE,
        "mu": MU,
        "summary": summary,
        "per_instance": per_instance,
        "gates": gates,
        "amendments": {
            "A1": (
                "LA2 made never-no-op after first run exposed a defective control "
                "(first-run LA2 rejection rate 0.5 because the attempt deleted nothing "
                "on instances without |a|<0.05 terms; first-run terminal "
                "N2_F4_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED). Mechanism, "
                "world, baselines, scoring, gate thresholds unchanged."
            ),
        },
        "authority": "exact_synthetic_frozen_accounting_only; not compiled-circuit, hardware, or novelty authority",
        "claim_boundary": (
            "Residual (or its absence) is accounting-level, contingent on the frozen "
            "counters/mu of N2_F4_PROTOCOL.md; the tested contribution is the typed "
            "edit-chain search with enforced NO_STRONGER_ORACLE/SAME_TARGET gates; "
            "no LOWER_BOUND claim."
        ),
    }


def main() -> None:
    r1 = pipeline()
    r2 = pipeline()
    deterministic = json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)
    r1["gates"]["F4_G1_determinism"] = deterministic
    hostile_ok = all(r1["gates"][g] for g in (
        "F4_G1_determinism", "F4_G2_laundering_caught",
        "F4_G3_no_admissible_beats_spectral_bound", "F4_G4_same_target"))
    if not hostile_ok:
        terminal = "N2_F4_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED"
    elif r1["gates"]["F4_G5_residual"]:
        terminal = "N2_F4_ACCESS_EDITS_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY"
    else:
        terminal = "N2_F4_ACCESS_EDITS_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY"
    r1["terminal"] = terminal
    with open(RESULTS_PATH, "w") as fh:
        json.dump(r1, fh, indent=2, sort_keys=True)
        fh.write("\n")
    receipt = {k: v for k, v in r1.items() if k != "per_instance"}
    print("ORIONQ_N2_F4_ACCESS_EDITS=" + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
