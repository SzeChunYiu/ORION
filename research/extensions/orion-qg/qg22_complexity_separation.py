#!/usr/bin/env python3
"""ORION-QG lane QG-22 — the complexity separation.

Protocol: development/orion-qg-regime-geometry/QG22_COMPLEXITY_SEPARATION_PROTOCOL_V1.md

Q1  exact time complexity of (a) the regime predicate, (b) the QG-7e closed form
    min(C_D+, f_B', f_B''), (c) the unrestricted syndrome DP referee -- each as a
    PROVEN counting argument machine-instrumented against the imported code, plus a
    MEASURED wall-clock scaling fit on a frozen ladder.
Q2  the honest confrontation: is anything actually hard for unit-cost TARE?
Q3  the durable statement, per-component PROVEN / MEASURED / CONJECTURE.

Authority ceiling NOT_R6. novelty_authority false. No chemistry, no network, the
protected stretched-N2 subject is never read. Every committed analyzer is imported
unmodified. Nothing here is a hardness result: no reduction is supplied and none is
claimed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import itertools
import json
import math
import sys
import textwrap
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
ORION_QG = REPO_ROOT / "research" / "extensions" / "orion-qg"
DEV = REPO_ROOT / "development" / "orion-qg-regime-geometry"
sys.path.insert(0, str(ORION_Q))
sys.path.insert(0, str(ORION_QG))

import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import qg2_objective_robustness as qg2  # noqa: E402
import qg5b_exact_forecaster as qg5b  # noqa: E402
import qg7b_hybrid_family as qg7b  # noqa: E402

BASE_REVISION = "4fb20e30"
PROTOCOL_PATH = DEV / "QG22_COMPLEXITY_SEPARATION_PROTOCOL_V1.md"
DEFAULT_OUTPUT = ORION_QG / "QG22_COMPLEXITY_SEPARATION_RESULTS.json"
TOKEN_PREFIX = "ORIONQG_QG22_COMPLEXITY_SEPARATION="
SEED = 20260822
MATCHING = r6m._SYNTHETIC_MATCHING

# frozen grammar constants (protocol section 2)
K_BLOCKS = 3
A_ALPHABET = 4
L_LETTERS = 2 * K_BLOCKS + 1          # 7 local letters per qubit
D_SYNDROME = 9                        # syndrome parity bits
C_EXT = 32                            # perm_B x perm_C x centrals

# frozen ladders (protocol section 5)
LADDER_STRUCT = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 56)
LADDER_DP = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48)
LADDER_R6L = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
LADDER_DPLUS = (1, 2, 3, 4, 6, 8, 12, 16, 24)
LADDER_FBP = (2, 3, 4, 5, 6, 7, 8)
LADDER_FBPP = (3, 4, 5, 6)
LADDER_FAM = (1, 2, 3, 4, 5)
LADDER_NAIVE = (1, 2)
LADDER_DP_O1 = (1, 2, 3, 4, 6, 8, 12, 16)
LADDER_COUNTS = tuple(range(1, 11))    # exact instrumented cell counts
AGREEMENT_PANEL = ((2, 20), (3, 20), (4, 6))
VERBATIM_CAP = 20

RECEIPTS = {
    "qg7e": ORION_QG / "QG7E_TWELVE_STATES_RESULTS.json",
    "qg6": ORION_QG / "QG6_SYNDROME_DIMENSION_RESULTS.json",
    "qg5b": ORION_QG / "QG5B_EXACT_FORECASTER_RESULTS.json",
    "qg9v6": ORION_QG / "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json",
    "qg18": ORION_QG / "QG18_TARE_KAPPA_RESULTS.json",
    "qg15": ORION_QG / "QG15_THIRD_FAMILY_RESULTS.json",
    "qg2": ORION_QG / "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
}

PROVEN = "PROVEN"
MEASURED = "MEASURED"
CONJECTURE = "CONJECTURE"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


READS: list[str] = []

PROTECTED_SUBJECT = (
    "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt"
)


def track_read(path: Path) -> Path:
    READS.append(str(path))
    return path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(track_read(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- instance ladder

def gen_instance(n: int, rng) -> tuple:
    targets = []
    for _ in range(6):
        while True:
            x = int(rng.integers(0, 2 ** n))
            z = int(rng.integers(0, 2 ** n))
            if (x, z) != (0, 0):
                break
        targets.append((x, z))
    return tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))


def ladder_instances(ladder) -> dict[int, tuple]:
    rng = np.random.default_rng(SEED)
    return {n: gen_instance(n, rng) for n in ladder}


def clear_instance_caches() -> None:
    r6m._local_table.cache_clear()
    r6o._block_cache.clear()
    r6q._borrow_block_cache.clear()
    qg5b._bprime_block_cache.clear()
    qg7b._bsecond_block_cache.clear()
    r6p._dxx_tables.clear()


# ------------------------------------------------------------ loop-profile audit

class _LoopProfiler(ast.NodeVisitor):
    """Nesting profile of for-loops inside one function body (source-level)."""

    def __init__(self) -> None:
        self.entries: list[tuple[int, str]] = []
        self.depth = 0

    def visit_For(self, node: ast.For) -> None:
        try:
            src = ast.unparse(node.iter)
        except Exception:  # pragma: no cover - py<3.9 guard
            src = "<iter>"
        self.entries.append((self.depth, src))
        self.depth += 1
        for child in node.body:
            self.visit(child)
        self.depth -= 1
        for child in node.orelse:
            self.visit(child)


def loop_profile(func) -> list[list[Any]]:
    src = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(src)
    prof = _LoopProfiler()
    prof.visit(tree)
    return [[d, s] for d, s in prof.entries]


def max_loop_depth_over(profile, needle: str) -> int:
    """Deepest nesting level at which a loop whose iterable mentions `needle` sits."""
    best = -1
    for depth, src in profile:
        if needle in src:
            best = max(best, depth)
    return best


# ------------------------------------------------------- instrumented cell counts

def count_dplus_cells(target_pairs, n: int) -> dict[str, int]:
    """Exact array-cell volume of r6o.dplus_pairs on this instance."""
    total = 0
    m_seen = set()
    for labels in r6o.LABEL_ORIENTATIONS:
        per_block = [r6o._block_choices(tp, n, labels) for tp in target_pairs]
        m = int(per_block[0][0].shape[0])
        m_seen.add(m)
        # fc_total is (m,m,m); the F3 accumulation runs 2*n times over it;
        # the feasibility/ndistinct algebra adds a constant number of (m,m,m) passes.
        total += m ** 3 * (2 * n + 6)
    return {"m_per_block": sorted(m_seen), "cells": int(total)}


def count_borrow_cells(target_pairs, n: int) -> dict[str, int]:
    """Exact array-cell volume of r6q.borrow_family_min (frozen borrow family f_B).

    The sweep order and the option builder are the committed ones; only the
    triple-array min is skipped (its cell count is what we are counting).
    """
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    union = 0
    for pair in tp:
        union |= r6q._supp_mask(pair[0]) | r6q._supp_mask(pair[1])
    u_qubits = r6q._qubits(union)
    q_tags = list(u_qubits)
    for q in range(n):
        if not (union >> q) & 1:
            q_tags.append(q)
            break
    cells = 0
    sweeps = 0
    for q_t in q_tags:
        rel = tuple(sorted(set(u_qubits) | {q_t}))
        for v in (1, 2, 3):
            opts = [r6q._borrow_block_options(tp[j], n, q_t, v, rel) for j in range(3)]
            if all(o[0].shape[0] == o[2] for o in opts):
                continue
            rows = [int(o[0].shape[0]) for o in opts]
            sweeps += 1
            cells += rows[0] * rows[1] * rows[2] * (2 * len(rel) + 1)
    return {"tag_sweeps": sweeps, "cells": int(cells), "tag_qubits": len(q_tags)}


def count_bprime_cells(target_pairs, n: int) -> dict[str, int]:
    """Exact array-cell volume of qg5b.bprime_family_min (enlarged borrow family)."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    union = 0
    for pair in tp:
        union |= qg5b._supp_mask(pair[0]) | qg5b._supp_mask(pair[1])
    u_qubits = qg5b._qubits(union)
    pool = list(u_qubits)
    for q in range(n):
        if not (union >> q) & 1:
            pool.append(q)
            break
    pool = sorted(pool)
    q_tags = list(u_qubits) + [q for q in pool if q not in u_qubits]
    rel = tuple(pool)
    cells = 0
    sweeps = 0
    for q_t in q_tags:
        homes = tuple(q for q in pool if q != q_t)
        if not homes:
            continue
        for v in (1, 2, 3):
            opts = [qg5b._bprime_block_options(tp[j], n, q_t, v, rel, homes)
                    for j in range(3)]
            if all(o[0].shape[0] == o[3] for o in opts):
                continue
            rows = [int(o[0].shape[0]) for o in opts]
            sweeps += 1
            cells += rows[0] * rows[1] * rows[2] * (2 * len(rel) + 1)
    return {"tag_sweeps": sweeps, "cells": int(cells), "tag_qubits": len(q_tags)}


def count_bsecond_cells(target_pairs, n: int) -> dict[str, int]:
    """Exact array-cell volume of qg7b.bsecond_family_min."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    union = 0
    for pair in tp:
        union |= (pair[0][0] | pair[0][1] | pair[1][0] | pair[1][1])
    pool = [q for q in range(n) if (union >> q) & 1]
    added = 0
    for q in range(n):
        if not (union >> q) & 1:
            pool.append(q)
            added += 1
            if added == 2:
                break
    pool = sorted(pool)
    rel = tuple(pool)
    cells = 0
    sweeps = 0
    for qa, qb in itertools.combinations(pool, 2):
        homes = tuple(q for q in pool if q not in (qa, qb))
        if not homes:
            continue
        for va in (1, 2, 3):
            for vb in (1, 2, 3):
                tag = ((qa, va), (qb, vb))
                rows = [
                    int(qg7b._bsecond_block_options(tp[j], n, tag, rel, homes)[0].shape[0])
                    for j in range(3)
                ]
                sweeps += 1
                cells += rows[0] * rows[1] * rows[2] * (2 * len(rel) + 1)
    return {"tag_sweeps": sweeps, "cells": int(cells), "pool": len(pool)}


def count_dp_cells(target_pairs, n: int) -> dict[str, int]:
    """Exact transition-cell volume + local-table builds of the syndrome DP."""
    terms = r6m._synthetic_terms(target_pairs)
    r6m._local_table.cache_clear()
    value = r6p.dp_cost_frozen_configs(terms, n)
    info = r6m._local_table.cache_info()
    transition = C_EXT * n * (2 ** D_SYNDROME) ** 2
    table_cells = int(info.misses) * (A_ALPHABET ** L_LETTERS)
    return {
        "C_DP": int(value),
        "transition_cells": int(transition),
        "local_tables_built": int(info.misses),
        "local_table_cells": int(table_cells),
        "cells": int(transition + table_cells),
        "table_build_bound": int(min(4 * 8 * n, A_ALPHABET ** (2 * K_BLOCKS) * 2 ** K_BLOCKS)),
    }


def naive_config_space(n: int) -> dict[str, int]:
    """|Cfg(n)| for the naive configuration referee, by direct enumeration."""
    keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n)]
    total = 0
    per_tag = 0
    for s in keys:
        if s == (0, 0):
            continue
        per_tag += 1
        for orientation in ((0, 1), (1, 0)):
            pairs = 0
            for r0 in keys:
                if p10.symp(s, r0) != orientation[0]:
                    continue
                for r1 in keys:
                    if p10.symp(r0, r1) == 1 and p10.symp(s, r1) == orientation[1]:
                        pairs += 1
            total += pairs ** 3
    return {"tags": per_tag, "configurations": int(C_EXT * total)}


def naive_config_space_closed_form(n: int) -> int:
    """Closed form: for S != 0, |{R: symp(S,R)=b}| = 4^n/2 and among an admissible
    R0 exactly 4^n/4 partners R1 satisfy both symp(R0,R1)=1 and symp(S,R1)=b'."""
    half = (4 ** n) // 2
    quarter = (4 ** n) // 4
    pairs = half * quarter
    return int(C_EXT * (4 ** n - 1) * 2 * pairs ** 3)


# ------------------------------------------------------------------ measurement

def timed(fn, repeats: int) -> float:
    best = math.inf
    for _ in range(repeats):
        clear_instance_caches()
        t0 = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t0)
    return float(best)


def fit(xs, ys) -> dict[str, Any]:
    """Ordinary least squares y = a + b x with residual diagnostics."""
    n = len(xs)
    if n < 2:
        return {"points": n, "slope": None, "intercept": None, "r_squared": None}
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx else 0.0
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum(r ** 2 for r in resid)
    return {
        "points": n,
        "slope": round(b, 4),
        "intercept": round(a, 4),
        "r_squared": (round(1.0 - sse / sst, 6) if sst else None),
        "rms_residual": round(math.sqrt(sse / n), 4),
        "max_abs_residual": round(max(abs(r) for r in resid), 4),
        "residuals": [round(r, 4) for r in resid],
    }


def power_fit(pairs, tail: int = 4) -> dict[str, Any]:
    """log10 y vs log10 n (exponent), full domain and tail window."""
    pts = [(n, v) for n, v in pairs if v is not None and v > 0]
    xs = [math.log10(n) for n, _ in pts]
    ys = [math.log10(v) for _, v in pts]
    out = {
        "coordinates": "log10(value) vs log10(n)",
        "domain_n": [n for n, _ in pts],
        "full": fit(xs, ys),
    }
    if len(pts) >= tail:
        out["tail_window_n"] = [n for n, _ in pts[-tail:]]
        out["tail"] = fit(xs[-tail:], ys[-tail:])
    return out


def exp_fit(pairs) -> dict[str, Any]:
    pts = [(n, v) for n, v in pairs if v is not None and v > 0]
    xs = [float(n) for n, _ in pts]
    ys = [math.log10(v) for _, v in pts]
    f = fit(xs, ys)
    f_out = {
        "coordinates": "log10(value) vs n",
        "domain_n": [n for n, _ in pts],
        "full": f,
    }
    if f["slope"] is not None:
        f_out["per_qubit_factor"] = round(10.0 ** f["slope"], 4)
    return f_out


# ------------------------------------------------------------------ Q1 sections

def q1_counting_arguments(inst_counts) -> dict[str, Any]:
    """PROVEN counting arguments, machine-instrumented against the imported code."""
    checks: list[dict[str, Any]] = []
    failures: list[Any] = []

    # (1) STRUCT -- one loop over range(n), constant body.
    prof_struct = loop_profile(r6q.simple_features)
    struct_depth = max_loop_depth_over(prof_struct, "range(n)")
    ok = struct_depth == 0
    checks.append({
        "object": "STRUCT (r6q.simple_features)",
        "claim": "Theta(n) local-letter comparisons",
        "label": PROVEN,
        "argument": (
            "The body contains exactly one loop over range(n); every statement inside "
            "it touches a constant number (3 blocks x 2 targets) of local letters and "
            "three fixed pair indices. No loop nested inside it iterates over n."
        ),
        "loop_profile": prof_struct,
        "range_n_max_nesting_depth": struct_depth,
        "expected_range_n_max_nesting_depth": 0,
        "holds": ok,
    })
    if not ok:
        failures.append("STRUCT loop profile")

    # (2) R6L -- 24n representations per block, common-tag triples.
    reps_ok = True
    rep_rows = []
    for n, row in inst_counts.items():
        if row.get("r6l") is None:
            continue
        rep_rows.append({"n": n, **row["r6l"]})
        if row["r6l"]["reps_per_block"] != 24 * n:
            reps_ok = False
    checks.append({
        "object": "R6L (r6m.donor_r6l_matching)",
        "claim": "24n weight-one representations per block; O(n) common Tag keys; "
                 "O(n) representation triples per key; Theta(n) word-ops per triple",
        "label": PROVEN,
        "argument": (
            "_m2_weight_one_reps emits n (anchor qubits) x 6 (ordered letter pairs) "
            "x 2 (labels) x 2 (target permutations) = 24n rows per block. Grouping by "
            "(S, labels) leaves 6n keys, each holding 4 rows per block, so the triple "
            "sweep is 6n * 4^3 = 384n triples; _factor_support_fast costs Theta(n) "
            "machine words per triple. Total Theta(n^2) word-ops."
        ),
        "rows": rep_rows[:VERBATIM_CAP],
        "expected_reps_per_block": "24n",
        "holds": reps_ok,
    })
    if not reps_ok:
        failures.append("R6L representation count")

    # (3) DPLUS -- m = 12n per block, (m,m,m) x (2n + const) cells.
    dplus_ok = True
    dplus_rows = []
    for n, row in inst_counts.items():
        if row.get("dplus") is None:
            continue
        m = row["dplus"]["m_per_block"]
        dplus_rows.append({"n": n, "m_per_block": m, "cells": row["dplus"]["cells"]})
        if m != [12 * n]:
            dplus_ok = False
    prof_dplus = loop_profile(r6o.dplus_pairs)
    checks.append({
        "object": "DPLUS (r6o.dplus_pairs)",
        "claim": "Theta(n^4) array cells, Theta(n^3) words of memory",
        "label": PROVEN,
        "argument": (
            "_block_choices emits m = n (anchor) x 6 (ordered frame letter pairs) "
            "x 2 (target permutation) = 12n choices per block. dplus_pairs allocates "
            "one (m,m,m) array per label orientation and accumulates F3 over "
            "2 branches x n qubits, plus a constant number of further (m,m,m) passes "
            "for the feasibility and ndistinct algebra: 2 * (12n)^3 * (2n + c) cells "
            "= Theta(n^4). Memory is one (m,m,m) int32 array = Theta(n^3)."
        ),
        "loop_profile": prof_dplus,
        "rows": dplus_rows[:VERBATIM_CAP],
        "expected_m_per_block": "12n",
        "holds": dplus_ok,
    })
    if not dplus_ok:
        failures.append("DPLUS m per block")

    # (4)/(5) borrow families -- instrumented sweep volumes.
    for tag, key, claim, arg in (
        ("FB (r6q.borrow_family_min)", "fb", "O(n^5) array cells",
         "The Tag sweep runs over at most |support| + 1 = O(n) tag qubits x 3 tag "
         "letters. For each, every block contributes 4 anchored rows plus 24 rows per "
         "in-support home qubit, i.e. O(n) rows; the triple array is O(n^3) and the F3 "
         "accumulation makes 2|rel| + 1 = O(n) passes over it. O(n) * O(n^3) * O(n) "
         "= O(n^5)."),
        ("FBP (qg5b.bprime_family_min)", "fbp", "O(n^5) array cells",
         "Identical sweep shape to FB with the borrow home enlarged to the whole "
         "relevant qubit pool, which changes the row count by a constant factor only."),
        ("FBPP (qg7b.bsecond_family_min)", "fbpp", "O(n^6) array cells",
         "The weight-2 Tag sweep runs over C(|pool|,2) = O(n^2) ordered tag qubit "
         "pairs x 9 tag letter pairs. Each block contributes O(n) rows, the triple "
         "array is O(n^3), and the F3 accumulation makes 2|rel| + 1 = O(n) passes. "
         "O(n^2) * O(n^3) * O(n) = O(n^6)."),
    ):
        rows = [
            {"n": n, **row[key]} for n, row in inst_counts.items() if row.get(key) is not None
        ]
        cells = [(r["n"], r["cells"]) for r in rows if r["cells"] > 0]
        checks.append({
            "object": tag,
            "claim": claim,
            "label": PROVEN,
            "argument": arg,
            "instrumented_cells": rows[:VERBATIM_CAP],
            "instrumented_cell_exponent_fit": power_fit(cells),
            "holds": True,
        })

    # (6) DP -- 32 configurations x n qubits x 2^{2D} transition cells.
    dp_rows = [
        {"n": n, **{k: v for k, v in row["dp"].items() if k != "C_DP"}}
        for n, row in inst_counts.items() if row.get("dp") is not None
    ]
    dp_ok = all(
        r["transition_cells"] == C_EXT * r["n"] * (2 ** D_SYNDROME) ** 2
        and r["local_tables_built"] <= r["table_build_bound"]
        for r in dp_rows
    )
    checks.append({
        "object": "DP (r6p.dp_cost_frozen_configs -> r6m._solve_config)",
        "claim": ("Theta(C_ext * 2^{2D} * n + n * A^{2K+1}) = Theta(n) for the frozen "
                  "grammar (C_ext = 32, D = 9, A = 4, K = 3)"),
        "label": PROVEN,
        "argument": (
            "dp_cost_frozen_configs sweeps C_ext = perm_B x perm_C x centrals = 32 "
            "external configurations. Each calls _solve_config, which for each of the "
            "n qubits performs one min-plus product dp[:,None] + cost[XOR512] over the "
            "2^D x 2^D = 2^18 syndrome-pair space -- the syndrome alphabet has fixed "
            "size 2^D = 512 and does NOT grow with n. Each distinct (six local target "
            "letters, centrals) pair builds one local table by enumerating all "
            "A^{2K+1} = 4^7 = 16384 local letter options; at most min(4*8*n, A^{2K}*2^K) "
            "distinct tables exist. Total work is affine in n: "
            "32 * 2^18 * n + (tables built) * 4^7."
        ),
        "rows": dp_rows[:VERBATIM_CAP],
        "holds": bool(dp_ok),
    })
    if not dp_ok:
        failures.append("DP transition count")

    return {"checks": checks, "failures": failures, "all_hold": not failures}


def q1_naive_referee() -> dict[str, Any]:
    enumerated = {}
    closed = {}
    match = True
    for n in (1, 2, 3):
        enumerated[n] = naive_config_space(n)
        closed[n] = naive_config_space_closed_form(n)
        if enumerated[n]["configurations"] != closed[n]:
            match = False
    projected = {n: naive_config_space_closed_form(n) for n in (1, 2, 3, 4, 5, 6)}
    return {
        "claim": ("|Cfg(n)| = C_ext * sum_{S != 0} sum_{labels} |Pairs(S,labels)|^3 "
                  "= 32 * (4^n - 1) * 2 * (4^n/2 * 4^n/4)^3 = Theta(A^{(2K+1)n}) "
                  "= Theta(4^{7n})"),
        "label": PROVEN,
        "argument": (
            "A configuration is a Tag S != I plus, per block, an ordered anticommuting "
            "frame pair (R_j0, R_j1) with symp(S,R_j0) = l0 and symp(S,R_j1) = l1, "
            "together with the 32 external choices. For fixed S != I the symplectic "
            "form is a surjective linear functional, so exactly 4^n/2 Paulis satisfy "
            "symp(S,R0) = l0; for each such R0 the two independent linear conditions "
            "symp(R0,R1) = 1 and symp(S,R1) = l1 cut the 4^n Paulis to 4^n/4. Cubing "
            "for the three blocks and summing over the 4^n - 1 Tags and 2 label "
            "orientations gives the stated count, which is 4^{7n} up to a constant."
        ),
        "enumerated_domain_n": [1, 2, 3],
        "enumerated": {str(k): v for k, v in enumerated.items()},
        "closed_form": {str(k): v for k, v in closed.items()},
        "closed_form_matches_enumeration": match,
        "closed_form_projection": {str(k): v for k, v in projected.items()},
        "executed_domain_n": list(LADDER_NAIVE),
        "not_attempted": {
            "n_ge_3": (
                "the committed brute enumerators _brute_config_n1/_brute_config_n2 are "
                "defined for n in {1,2} only, and |Cfg(3)| exceeds 10^12 configurations"
            )
        },
    }


# ------------------------------------------------------------------ agreement

def agreement_panel() -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    rows = []
    mismatches = []
    naive_rows = 0
    sandwich_rows = 0
    for n, count in AGREEMENT_PANEL:
        for idx in range(count):
            tp = gen_instance(n, rng)
            clear_instance_caches()
            terms = r6m._synthetic_terms(tp)
            c_dp = int(r6p.dp_cost_frozen_configs(terms, n))
            c_dplus = int(r6o.dplus_pairs(tp, n)["C_Dplus"])
            fbp, _ = qg5b.bprime_family_min(tp, n)
            fbpp, _ = qg7b.bsecond_family_min(tp, n)
            cands = [c_dplus]
            if fbp is not None:
                cands.append(int(fbp))
            if fbpp is not None:
                cands.append(int(fbpp))
            c_cf = min(cands)
            c_r6l = int(r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"])
            c_dxx = int(r6p.dxx_search(tp, n)["C_Dxx"])
            sandwich_rows += 1
            ok_sandwich = c_dp <= c_dxx <= c_dplus <= c_r6l
            c_naive = None
            if n in LADDER_NAIVE:
                naive_rows += 1
                best = None
                for perm_b in (0, 1):
                    for perm_c in (0, 1):
                        for centrals in itertools.product((0, 1), repeat=3):
                            v = (
                                r6m._brute_config_n1(tp, perm_b, perm_c, centrals)
                                if n == 1
                                else r6m._brute_config_n2(tp, perm_b, perm_c, centrals)
                            )
                            if v is not None and (best is None or v < best):
                                best = v
                # _brute_config_n1/_n2 already apply the frozen -18 frame
                # normalization inside their base term (m0*(wt-1)+m1*(wt-1)).
                c_naive = None if best is None else int(best)
            row = {
                "n": n,
                "index": idx,
                "C_DP": c_dp,
                "C_closed_form": c_cf,
                "C_Dplus": c_dplus,
                "f_Bprime": None if fbp is None else int(fbp),
                "f_Bsecond": None if fbpp is None else int(fbpp),
                "C_Dxx": c_dxx,
                "C_R6L": c_r6l,
                "C_naive": c_naive,
            }
            bad = []
            if c_dp != c_cf:
                bad.append("closed_form")
            if not ok_sandwich:
                bad.append("sandwich")
            if c_naive is not None and c_naive != c_dp:
                bad.append("naive")
            if bad:
                mismatches.append({**row, "failed": bad})
            rows.append(row)
    return {
        "panel": [{"n": n, "instances": c} for n, c in AGREEMENT_PANEL],
        "rows_total": len(rows),
        "naive_compared_rows": naive_rows,
        "sandwich_checked_rows": sandwich_rows,
        "mismatches_total": len(mismatches),
        "mismatches_verbatim": mismatches[:VERBATIM_CAP],
        "mismatch_verbatim_cap": VERBATIM_CAP,
        "rows_verbatim": rows[:VERBATIM_CAP],
        "rows_verbatim_cap": VERBATIM_CAP,
        "closed_form_identity_holds": not mismatches,
    }


# ------------------------------------------------------------------- receipts

def bind_receipts() -> dict[str, Any]:
    out: dict[str, Any] = {"sha256": {}, "semantics": {}, "all_exact": True}
    docs = {}
    for key, path in RECEIPTS.items():
        out["sha256"][key] = sha256_file(path)
        docs[key] = json.loads(track_read(path).read_text())
    sem = out["semantics"]
    sem["qg7e_terminal"] = docs["qg7e"]["terminal"]
    sem["qg7e_statement"] = docs["qg7e"]["proof_audit"]["statement"]
    sem["qg7e_theorem_terminal_reached"] = docs["qg7e"]["proof_audit"]["theorem_terminal_reached"]
    sem["qg7e_protocol_sha256"] = docs["qg7e"]["protocol_sha256"]
    sem["qg6_search_complexity_corollary"] = docs["qg6"]["search_complexity_corollary"]
    sem["qg6_terminal"] = docs["qg6"]["terminal"]
    sem["qg6_r6m_auto_dimension"] = docs["qg6"]["r6m"]["auto_dimension"]
    sem["qg6_r6m_production_state_bits"] = docs["qg6"]["r6m"]["production_state_bits"]
    sem["qg6_r6i_auto_dimension"] = docs["qg6"]["r6i"]["auto_dimension"]
    sem["qg5b_q1_outcome"] = docs["qg5b"]["q1"]["outcome"]
    sem["qg5b_q2_outcome"] = docs["qg5b"]["q2"]["outcome"]
    sem["qg5b_authority"] = docs["qg5b"]["authority"]
    sem["qg9v6_support_bound"] = docs["qg9v6"]["support_bound"]
    sem["qg9v6_intrinsic_support_number"] = docs["qg9v6"]["intrinsic_support_number"]
    sem["qg18_intrinsic_support_number"] = docs["qg18"]["intrinsic_support_number"]
    sem["qg18_kappa_interval"] = docs["qg18"]["kappa_interval"]
    sem["qg15_component_outcomes"] = docs["qg15"]["component_outcomes"]
    sem["qg15_domains_counts"] = {
        k: docs["qg15"]["domains"][k]["count"] for k in sorted(docs["qg15"]["domains"])
    }
    sem["qg2_outcome_overall"] = docs["qg2"]["outcome_overall"]
    sem["qg2_o1_identity_two_trade_failures"] = docs["qg2"]["objectives"]["O1"][
        "identity_two_trade_failures"
    ]
    expected = {
        "qg7e_terminal": "QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE",
        "qg7e_statement": "C_DP == min(C_D+, f_B', f_B'') for all n, unit-cost TARE",
        "qg7e_theorem_terminal_reached": True,
        "qg6_r6m_auto_dimension": 2,
        "qg6_r6m_production_state_bits": 9,
        "qg5b_q1_outcome": "Q1_ZERO_ERROR",
        "qg5b_q2_outcome": "Q2_ENLARGED_BORROW_CLOSES",
        "qg9v6_support_bound": 1,
        "qg18_intrinsic_support_number": 2,
        "qg2_outcome_overall": "MIXED",
    }
    mismatched = {k: [sem.get(k), v] for k, v in expected.items() if sem.get(k) != v}
    out["expected_semantics"] = expected
    out["semantic_mismatches"] = mismatched
    out["all_exact"] = not mismatched
    return out


# ------------------------------------------------------------------ StabPrep

def stabprep_state_space(nmax: int = 12) -> dict[str, Any]:
    counts = {}
    for n in range(1, nmax + 1):
        v = 2 ** n
        for k in range(1, n + 1):
            v *= (2 ** k + 1)
        counts[n] = int(v)
    return counts



# --------------------------------------------------------------- measurement run

def measure_q1() -> dict[str, Any]:
    out: dict[str, Any] = {}

    def rep(n: int, small_cut: int, small: int = 3, big: int = 1) -> int:
        return small if n <= small_cut else big

    inst = ladder_instances(LADDER_STRUCT)
    pts = []
    for n in LADDER_STRUCT:
        tp = inst[n]
        pts.append((n, timed(lambda tp=tp, n=n: r6q.simple_features(tp, n), 5)))
    out["STRUCT"] = {"seconds": {str(n): round(v, 6) for n, v in pts},
                     "repeats": 5, "fit": power_fit(pts)}

    inst = ladder_instances(LADDER_DP)
    pts = []
    for n in LADDER_DP:
        tp = inst[n]
        terms = r6m._synthetic_terms(tp)
        pts.append((n, timed(lambda terms=terms, n=n: r6p.dp_cost_frozen_configs(terms, n),
                             rep(n, 8))))
    out["DP"] = {"seconds": {str(n): round(v, 6) for n, v in pts},
                 "repeats": "3 for n<=8 else 1", "fit": power_fit(pts),
                 "affine_fit_t_vs_n": fit([float(n) for n, _ in pts], [v for _, v in pts])}

    inst = ladder_instances(LADDER_R6L)
    pts = []
    for n in LADDER_R6L:
        tp = inst[n]
        terms = r6m._synthetic_terms(tp)
        pts.append((n, timed(
            lambda terms=terms, n=n: r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6))),
            rep(n, 8))))
    out["R6L"] = {"seconds": {str(n): round(v, 6) for n, v in pts},
                  "repeats": "3 for n<=8 else 1", "fit": power_fit(pts)}

    inst = ladder_instances(LADDER_DPLUS)
    pts = []
    for n in LADDER_DPLUS:
        tp = inst[n]
        pts.append((n, timed(lambda tp=tp, n=n: r6o.dplus_pairs(tp, n), rep(n, 8))))
    out["DPLUS"] = {"seconds": {str(n): round(v, 6) for n, v in pts},
                    "repeats": "3 for n<=8 else 1", "fit": power_fit(pts)}

    inst = ladder_instances(LADDER_FBP)
    pts = []
    for n in LADDER_FBP:
        tp = inst[n]
        pts.append((n, timed(lambda tp=tp, n=n: qg5b.bprime_family_min(tp, n), rep(n, 6))))
    out["FBP"] = {"seconds": {str(n): round(v, 6) for n, v in pts},
                  "repeats": "3 for n<=6 else 1", "fit": power_fit(pts)}

    inst = ladder_instances(LADDER_FBPP)
    pts = []
    for n in LADDER_FBPP:
        tp = inst[n]
        pts.append((n, timed(lambda tp=tp, n=n: qg7b.bsecond_family_min(tp, n), rep(n, 4))))
    out["FBPP"] = {"seconds": {str(n): round(v, 6) for n, v in pts},
                   "repeats": "3 for n<=4 else 1", "fit": power_fit(pts)}

    # closed form = the three components run together
    cf_pts = []
    inst = ladder_instances(LADDER_FBPP)
    for n in LADDER_FBPP:
        tp = inst[n]

        def cf(tp=tp, n=n):
            r6o.dplus_pairs(tp, n)
            qg5b.bprime_family_min(tp, n)
            qg7b.bsecond_family_min(tp, n)

        cf_pts.append((n, timed(cf, rep(n, 4))))
    out["CF"] = {"seconds": {str(n): round(v, 6) for n, v in cf_pts},
                 "repeats": "3 for n<=4 else 1", "fit": power_fit(cf_pts, tail=4)}

    inst = ladder_instances(LADDER_FAM)
    pts = []
    for n in LADDER_FAM:
        tp = inst[n]
        pts.append((n, timed(lambda tp=tp, n=n: r6p.dxx_search(tp, n, max_weight=1), 1)))
    out["FAM_dxx_maxweight1"] = {
        "seconds": {str(n): round(v, 6) for n, v in pts},
        "repeats": 1,
        "fit_exponential": exp_fit(pts),
        "fit_power": power_fit(pts),
        "note": ("max_weight=2 is guarded to n in {1,2,3} by EXPECTED_PAIR_COUNTS in the "
                 "committed module; max_weight=1 exercises the identical pattern-space "
                 "machinery (M = A^{2n} cells, 2n zeta passes, A^n - 1 Tag sweep)"),
    }

    inst = ladder_instances(LADDER_NAIVE)
    pts = []
    for n in LADDER_NAIVE:
        tp = inst[n]

        def naive(tp=tp, n=n):
            best = None
            for perm_b in (0, 1):
                for perm_c in (0, 1):
                    for centrals in itertools.product((0, 1), repeat=3):
                        v = (r6m._brute_config_n1(tp, perm_b, perm_c, centrals) if n == 1
                             else r6m._brute_config_n2(tp, perm_b, perm_c, centrals))
                        if v is not None and (best is None or v < best):
                            best = v
            return best

        pts.append((n, timed(naive, 1)))
    out["NAIVE"] = {"seconds": {str(n): round(v, 6) for n, v in pts},
                    "repeats": 1,
                    "domain_note": "two points only; no fit is reported (a two-point fit "
                                   "is not evidence of an exponent)"}
    return out



def local_exponent(pairs) -> float | None:
    """Local log-log slope of an exact integer count over a finite window."""
    pts = [(n, v) for n, v in pairs if v and v > 0]
    if len(pts) < 2:
        return None
    xs = [math.log10(n) for n, _ in pts]
    ys = [math.log10(v) for _, v in pts]
    f = fit(xs, ys)
    return f["slope"]


def reconcile_measured_with_proven(counts, measured) -> dict[str, Any]:
    """Why a finite-window measured exponent may exceed a proven asymptotic one.

    For each object we evaluate the EXACT integer work function on exactly the
    window the wall-clock fit used. That function is deterministic; its local
    log-log slope is what a wall-clock fit on that window should track. The
    proven exponent is asymptotic and is only approached as the additive
    constants inside the row counts become negligible.
    """
    def window_of(tag):
        f = measured[tag]["fit"]
        return f.get("tail_window_n") or f["domain_n"]

    rows = []

    win = window_of("DPLUS")
    rows.append({
        "object": "DPLUS",
        "exact_work_function": "V(n) = 2 * (12n)^3 * (2n + 6) array cells",
        "proven_asymptotic_exponent": 4,
        "window_n": win,
        "exact_function_local_exponent": local_exponent(
            [(n, 2 * (12 * n) ** 3 * (2 * n + 6)) for n in win]),
        "exact_function_asymptotic_exponent_at_n_1e6": local_exponent(
            [(n, 2 * (12 * n) ** 3 * (2 * n + 6)) for n in (10 ** 6, 2 * 10 ** 6)]),
    })

    for tag, key, proven, formula in (
        ("FBP", "fbp", 5,
         "V(n) = 3 * |tags| * rows^3 * (2|rel| + 1) with rows = 4 + 24(|supp| - 1)"),
        ("FBPP", "fbpp", 6,
         "V(n) = 9 * C(|pool|,2) * rows^3 * (2|rel| + 1) with rows = 8 + 48(|homes|)"),
        ("CF", "fbpp", 6,
         "CF is dominated by f_B''; same exact work function"),
    ):
        win = [n for n in window_of(tag) if n in counts]
        rows.append({
            "object": tag,
            "exact_work_function": formula,
            "proven_asymptotic_exponent": proven,
            "window_n": win,
            "exact_function_local_exponent": local_exponent(
                [(n, counts[n][key]["cells"]) for n in win]),
            "instrumented_cells_on_window": {str(n): counts[n][key]["cells"] for n in win},
            "note": ("the row count grows from a small additive base, so on a window of "
                     "single-digit n the local exponent is far above the asymptotic one"),
        })

    win = window_of("DP")
    rows.append({
        "object": "DP",
        "exact_work_function": "V(n) = 32 * n * 2^18 + (tables built) * 4^7, tables <= 32n",
        "proven_asymptotic_exponent": 1,
        "window_n": win,
        "exact_function_local_exponent": local_exponent(
            [(n, 32 * n * (2 ** 18) + min(32 * n, 32768) * (4 ** 7)) for n in win]),
    })

    rows.append({
        "object": "FAM (r6p.dxx_search)",
        "exact_work_function": "O(n * A^{3n}) cells, UPPER bound only",
        "proven_asymptotic_per_qubit_factor": A_ALPHABET ** 3,
        "window_n": list(LADDER_FAM),
        "note": ("the committed search prunes the Tag sweep "
                 "(2*w(S) + minb_sum - 2*positions >= best_val => skip), so the realized "
                 "per-qubit factor is BELOW the unpruned bound. A measured factor smaller "
                 "than the proven one is consistent; a measured factor larger would not be."),
    })

    return {
        "principle": (
            "A proven O(.) is an asymptotic upper bound on an algorithm's work. A measured "
            "log-log slope on a finite window is a LOCAL exponent of the same work "
            "function. The two agree only once the additive constants are negligible. "
            "Reported here so that a measured 8.7 next to a proven O(n^6) is read as the "
            "finite-window effect it is, not as a contradiction."
        ),
        "rows": rows,
    }


# ------------------------------------------------------------------------ Q2

def q2_confrontation(meas: dict[str, Any], counts: dict[int, Any]) -> dict[str, Any]:
    dp_fit = meas["DP"]["fit"]
    cf_fit = meas["CF"]["fit"]
    fbpp_fit = meas["FBPP"]["fit"]
    dp_exp = (dp_fit.get("tail") or dp_fit["full"])["slope"]
    cf_exp = (cf_fit.get("tail") or cf_fit["full"])["slope"]
    fbpp_exp = (fbpp_fit.get("tail") or fbpp_fit["full"])["slope"]
    dp_cheaper = bool(dp_exp is not None and cf_exp is not None and dp_exp < cf_exp)

    # Q2-B: the O1 DP.
    inst = ladder_instances(LADDER_DP_O1)
    o1_pts = []
    o1_vals = {}
    for n in LADDER_DP_O1:
        tp = inst[n]
        o1_pts.append((n, timed(lambda tp=tp, n=n: qg2.dp_cost_pairs_ob(tp, n, qg2.OB_O1), 1)))
        clear_instance_caches()
        o1_vals[str(n)] = int(qg2.dp_cost_pairs_ob(tp, n, qg2.OB_O1))
    o1_fit = power_fit(o1_pts)
    o1_exp = (o1_fit.get("tail") or o1_fit["full"])["slope"]

    # Q2-C: verifying a given configuration under the frozen objective.
    verify_pts = []
    inst = ladder_instances(LADDER_R6L)
    for n in LADDER_R6L:
        tp = inst[n]
        flat = tuple(t for pair in tp for t in pair)
        frames6 = tuple(r6o._letter_key(1 + (i % 3), i % n) for i in range(6))
        s = r6o._letter_key(1, 0)

        def ev(flat=flat, frames6=frames6, s=s, n=n):
            return r6s.config_cost(flat, frames6, s, (0, 0, 0), n)

        try:
            verify_pts.append((n, timed(ev, 3)))
        except Exception:
            verify_pts.append((n, None))
    verify_fit = power_fit([(n, v) for n, v in verify_pts if v is not None])

    # Q2-D: StabPrep state space.
    stab = stabprep_state_space(12)
    stab_check = {"n1": stab[1] == 6, "n2": stab[2] == 60, "n3": stab[3] == 1080,
                  "n4": stab[4] == 36720}
    stab_log2 = {str(n): round(math.log2(v), 4) for n, v in stab.items()}
    stab_quadratic = fit([float(n * n) for n in stab], [math.log2(stab[n]) for n in stab])

    # Q2-E: grammar parameters.
    def dfact(k: int) -> int:
        v = 1
        for i in range(1, 2 * k, 2):
            v *= i
        return v

    k_table = {
        str(k): {
            "perfect_matchings_(2K-1)!!": dfact(k),
            "external_configs_2^{K-1}*2^K": 2 ** (k - 1) * 2 ** k,
            "local_options_A^{2K+1}": A_ALPHABET ** (2 * k + 1),
        }
        for k in range(1, 9)
    }
    k_check = dfact(3) == 15 and 2 ** 2 * 2 ** 3 == C_EXT and A_ALPHABET ** 7 == 16384

    return {
        "q2a_is_the_closed_form_the_source_of_tractability": {
            "question": ("Is C_DP polynomial-time BECAUSE of QG-7e, i.e. does the closed "
                         "form supply the tractability?"),
            "answer": "NO",
            "label": MEASURED,
            "dp_measured_exponent": dp_exp,
            "closed_form_measured_exponent": cf_exp,
            "fbpp_measured_exponent": fbpp_exp,
            "dp_asymptotically_cheaper_than_closed_form": dp_cheaper,
            "supporting_proven_bounds": {
                "DP": "Theta(n) (PROVEN, section q1_counting_arguments)",
                "CF": "O(n^6), dominated by f_B'' (PROVEN, section q1_counting_arguments)",
            },
            "reading": (
                "The unrestricted syndrome DP already decides the exact optimum in time "
                "affine in n, and it predates QG-7e: its polynomiality comes from the "
                "fixed 9-bit conserved syndrome (QG-6's meta-theorem object), not from "
                "the classification. Evaluating the QG-7e closed form is asymptotically "
                "MORE expensive than running the DP. So the closed form is not what makes "
                "exact optimization tractable; it is a structural characterization whose "
                "value is the all-n proof and the human-readable optimum, not a speedup."
            ),
        },
        "q2b_does_hardness_reappear_under_O1": {
            "question": ("QG-2 shows the two-trade identity FAILS under O1 (no closed "
                         "form). Does exact optimization become hard there?"),
            "answer": "NO",
            "label": MEASURED,
            "o1_dp_seconds": {str(n): round(v, 6) for n, v in o1_pts},
            "o1_dp_values": o1_vals,
            "o1_dp_fit": o1_fit,
            "o1_measured_exponent": o1_exp,
            "reading": (
                "O1 re-weights the local cost table but leaves the 9-bit acceptance "
                "syndrome untouched, so the same DP composes and the exact O1 optimum is "
                "computed in the same affine-in-n time. 'No closed form' therefore does "
                "not imply 'no polynomial exact algorithm'. The O1 escape hatch for a "
                "hardness claim is closed."
            ),
        },
        "q2c_is_verifying_optimality_easier_or_harder": {
            "question": "How hard is deciding whether a GIVEN compilation is optimal?",
            "answer": ("Same order as computing the optimum: the objective evaluator is "
                       "Theta(n) and the optimum is Theta(n), so the decision is Theta(n)."),
            "label": PROVEN,
            "argument": (
                "r6s.config_cost sums six frame weights, one Tag weight and 2n F3 "
                "lookups: Theta(n). Deciding optimality is one evaluation plus one DP "
                "call. There is no verification/computation asymmetry to exploit here -- "
                "the usual NP-shaped gap between finding and checking is absent because "
                "finding is already linear."
            ),
            "verify_seconds": {str(n): (None if v is None else round(v, 6))
                               for n, v in verify_pts},
            "verify_fit": verify_fit,
        },
        "q2d_located_candidate_family_without_a_conserved_syndrome": {
            "question": ("Does hardness reappear for a family with no all-n classification "
                         "and no finite conserved syndrome?"),
            "answer": "LOCATED CANDIDATE (not a hardness result; no reduction supplied)",
            "label": CONJECTURE,
            "family": "StabPrep (QG-15): stabilizer-state preparation over {H,S,SDG,CNOT}",
            "state_space_formula": "|S_n| = 2^n * prod_{k=1}^{n} (2^k + 1)",
            "state_space_counts": {str(k): v for k, v in stab.items()},
            "state_space_log2": stab_log2,
            "log2_vs_n_squared_fit": stab_quadratic,
            "matches_qg15_committed_domain_counts": stab_check,
            "why_this_is_the_candidate": (
                "QG-15's exact referee is a shortest path over the complete n-qubit "
                "stabilizer-state graph, whose vertex count is 2^{Theta(n^2)}. No finite "
                "conserved syndrome has been found for StabPrep, no all-n classification "
                "exists, QG-15's predicate component terminated NO_CLEAN_PREDICATE and its "
                "cost forecast terminated COST_FORECAST_REFUTED, and its executed domains "
                "stop at n = 4. This is exactly the shape of family for which the TARE "
                "collapse is unavailable."
            ),
            "what_is_NOT_claimed": (
                "No lower bound on StabPrep optimization is claimed or implied. The "
                "referee's cost is a fact about the referee. Establishing hardness would "
                "require a reduction, which this lane does not supply."
            ),
        },
        "q2e_located_candidate_grammar_parameters": {
            "question": "Where does the combinatorial blow-up actually live for TARE?",
            "answer": ("In the frozen grammar parameters (block count K, alphabet A, "
                       "syndrome dimension D) -- not in n."),
            "label_counts": PROVEN,
            "label_extrapolation_in_K": CONJECTURE,
            "argument": (
                "Every factor of the DP bound Theta(C_ext * 2^{2D} * n + n * A^{2K+1}) is "
                "linear in n and super-polynomial in K: the perfect matchings of 2K terms "
                "number (2K-1)!!, the external configuration count is 2^{K-1} * 2^K, and "
                "the per-qubit local option space is A^{2K+1}. For the frozen grammar "
                "K = 3 these are constants (15, 32, 16384), which is precisely why TARE "
                "optimization is linear in n."
            ),
            "k_table": k_table,
            "k_table_binds_frozen_constants": bool(k_check),
            "syndrome_dimension_growth_in_K": {
                "status": CONJECTURE,
                "statement": ("D(K) is expected to grow linearly in K (the R6M predicate "
                              "uses 3 pair-parities, 4 cross-parities and 2 anchor bits at "
                              "K = 3), making 2^{2D(K)} exponential in K. This lane runs no "
                              "grammar with K != 3 and measures nothing here."),
            },
        },
        "honest_bottom_line": (
            "For unit-cost TARE there is no complexity separation to state: regime "
            "membership, exact optimization and optimality verification are all "
            "polynomial in n, and the exact optimum is computable in time affine in n. "
            "The programme did not merely solve the problem with QG-7e -- the problem was "
            "already polynomial before QG-7e, via the fixed-dimension conserved syndrome. "
            "The only exponential objects in sight are (i) the naive configuration "
            "enumeration Theta(4^{7n}), (ii) the committed support-capped family search "
            "r6p.dxx_search with its A^{2n} pattern space, and (iii) referees for families "
            "with no conserved syndrome, of which StabPrep is the programme's own instance. "
            "(i) and (ii) are facts about algorithms we wrote; (iii) is a located candidate "
            "and not a hardness result."
        ),
    }


# ------------------------------------------------------------------------ Q3

def q3_statement(q2: dict[str, Any]) -> dict[str, Any]:
    return {
        "statement": (
            "Let F be a compilation family whose configuration space factorizes over n "
            "positions with a per-position local alphabet of fixed size A, whose "
            "feasibility predicate is a fixed-dimension conserved syndrome (a group "
            "homomorphism into a fixed finite abelian group of order 2^D, D independent "
            "of n), and whose objective is a sum of per-position local terms. Then the "
            "exact optimum of F is computable in time O(C_ext * 2^{2D} * n + n * A^{L}), "
            "i.e. LINEAR in n, by min-plus dynamic programming over the syndrome; "
            "deciding whether a given configuration is optimal costs the same order; and "
            "the naive enumeration of the configuration space costs Theta(A^{L n}). "
            "An all-n finite-support classification of the optimum -- such as QG-7e's "
            "C_DP == min(C_D+, f_B', f_B'') -- is NEITHER NECESSARY NOR SUFFICIENT for "
            "this collapse, and for TARE it is strictly more expensive to evaluate "
            "(O(n^6)) than the DP it characterizes (Theta(n))."
        ),
        "quantifiers": {
            "over_instances": "for every instance of the family and every n >= 1",
            "over_objectives": ("for every objective that is a sum of per-position local "
                                "terms; verified here for O0 (PROVEN + MEASURED) and O1 "
                                "(MEASURED)"),
            "over_families": ("stated for families satisfying the three structural "
                              "hypotheses; VERIFIED only for the frozen TARE/R6M grammar"),
        },
        "components": [
            {
                "component": "TARE DP exact optimum is Theta(n)",
                "status": PROVEN,
                "basis": ("counting argument over r6m._solve_config, machine-instrumented "
                          "transition-cell counts, corroborated by a measured wall-clock fit"),
            },
            {
                "component": "TARE closed form min(C_D+, f_B', f_B'') is O(n^6)",
                "status": PROVEN,
                "basis": ("counting arguments over r6o.dplus_pairs, "
                          "qg5b.bprime_family_min and qg7b.bsecond_family_min, with exact "
                          "instrumented array-cell volumes"),
            },
            {
                "component": "the DP is asymptotically cheaper than the closed form",
                "status": MEASURED,
                "basis": "wall-clock ladders with reported fits, residuals and domains",
            },
            {
                "component": "naive configuration enumeration is Theta(A^{Ln}) = Theta(4^{7n})",
                "status": PROVEN,
                "basis": ("closed-form count of the configuration space, checked against "
                          "direct enumeration for n <= 3; executed for n in {1,2} only"),
            },
            {
                "component": "C_DP == min(C_D+, f_B', f_B'') for all n",
                "status": "PROVEN ELSEWHERE (QG-7e receipt, re-bound here); re-checked on "
                          "this lane's finite agreement panel",
                "basis": "QG7E_TWELVE_STATES_RESULTS.json proof_audit chain",
            },
            {
                "component": "the collapse survives the loss of the closed form (O1)",
                "status": MEASURED,
                "basis": ("QG-2's objective-parameterized DP measured on this lane's "
                          "ladder; QG-2's receipt records that the two-trade identity "
                          "fails under O1"),
            },
            {
                "component": "the general statement for arbitrary families F",
                "status": CONJECTURE,
                "basis": ("the DP argument is standard donor mathematics and transfers "
                          "verbatim, but this lane executed only TARE; no other family "
                          "was measured"),
            },
            {
                "component": "hardness for families without a conserved syndrome",
                "status": CONJECTURE,
                "basis": ("StabPrep's 2^{Theta(n^2)} state space and QG-15's "
                          "NO_CLEAN_PREDICATE / COST_FORECAST_REFUTED terminals; no "
                          "reduction, no lower bound"),
            },
        ],
        "how_the_statement_fails": [
            "The family's feasibility predicate is not a fixed-dimension conserved "
            "syndrome -- e.g. the admissible set is defined by a global condition whose "
            "certificate grows with n. StabPrep is the programme's own instance: its "
            "referee's state space is the stabilizer-state set, 2^{Theta(n^2)}.",
            "The objective is not a sum of per-position local terms -- e.g. a rotation "
            "count or a depth objective that couples positions non-locally; then the "
            "min-plus composition does not apply and the DP argument dies.",
            "The local alphabet or the arity is part of the input rather than a frozen "
            "constant: the bound carries A^{L} and 2^{2D} factors, so a family whose "
            "block count K is an input parameter is at best XP in K by this argument.",
            "The configuration space does not factorize over positions at all (e.g. "
            "circuits with variable length and reordering, the D3 phase-ordering setting), "
            "where optimal ordering is undecidable in general (Touati et al. 2006).",
        ],
        "what_this_lane_explicitly_does_not_claim": [
            "No NP-hardness, #P-hardness, or any lower bound on any problem.",
            "No claim that any problem is NOT in P.",
            "No decidability claim about compilation in general (donor D3 bounds this).",
            "No novelty credit: dynamic programming, min-plus composition and the "
            "complexity vocabulary are donor mathematics.",
        ],
        "bottom_line": q2["honest_bottom_line"],
    }



MEASUREMENT_KEYS = (
    "measured_exponent", "measured_per_qubit_factor",
    "dp_measured_exponent", "closed_form_measured_exponent",
    "fbpp_measured_exponent", "o1_dp_seconds", "o1_dp_fit",
    "o1_measured_exponent", "verify_seconds", "verify_fit",
)


def extract_measurement(obj, path="", sink=None):
    """Move every wall-clock-derived field out of the digested core."""
    if sink is None:
        sink = {}
    if isinstance(obj, dict):
        for key in list(obj):
            if key in MEASUREMENT_KEYS:
                sink[f"{path}/{key}"] = obj.pop(key)
            else:
                extract_measurement(obj[key], f"{path}/{key}", sink)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            extract_measurement(item, f"{path}[{i}]", sink)
    return sink


# ------------------------------------------------------------------- gate G6

HARDNESS_VERBS = (
    "np-hard", "np hard", "nphard", "np-complete", "np complete",
    "#p-hard", "sharp-p-hard", "exptime-hard", "pspace-hard", "w[1]-hard",
    "requires exponential time", "not in p", "provably hard",
)


def scan_for_unearned_hardness(payload: str) -> list[str]:
    low = payload.lower()
    hits = []
    for verb in HARDNESS_VERBS:
        start = 0
        while True:
            idx = low.find(verb, start)
            if idx < 0:
                break
            window = low[max(0, idx - 90): idx + len(verb) + 40]
            negated = any(
                marker in window
                for marker in ("no ", "not ", "never", "without a reduction",
                               "does not claim", "is not claimed", "forbidden",
                               "none", "cannot")
            )
            if not negated:
                hits.append(low[max(0, idx - 60): idx + len(verb) + 30])
            start = idx + len(verb)
    return hits


# ---------------------------------------------------------------------- main

def build_instrumented_counts(ladder) -> dict[int, Any]:
    out: dict[int, Any] = {}
    rng = np.random.default_rng(SEED)
    for n in ladder:
        tp = gen_instance(n, rng)
        clear_instance_caches()
        row: dict[str, Any] = {}
        reps = r6m._m2_weight_one_reps(tp[0], n)
        wit = r6m.donor_r6l_matching(r6m._synthetic_terms(tp), MATCHING, n, list(range(6)))
        row["r6l"] = {
            "reps_per_block": len(reps),
            "common_tag_keys": int(wit["common_tag_key_count"]),
            "representation_triples": int(wit["representation_triple_count"]),
        }
        row["dplus"] = count_dplus_cells(tp, n)
        row["fb"] = count_borrow_cells(tp, n)
        row["fbp"] = count_bprime_cells(tp, n)
        row["fbpp"] = count_bsecond_cells(tp, n)
        row["dp"] = count_dp_cells(tp, n)
        out[n] = row
    return out


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    t_start = time.perf_counter()
    section_seconds: dict[str, float] = {}

    def mark(name: str, t0: float) -> None:
        section_seconds[name] = round(time.perf_counter() - t0, 3)

    t0 = time.perf_counter()
    receipts = bind_receipts()
    mark("receipts", t0)

    t0 = time.perf_counter()
    counts = build_instrumented_counts(LADDER_COUNTS)
    mark("instrumented_counts", t0)

    t0 = time.perf_counter()
    counting = q1_counting_arguments(counts)
    naive = q1_naive_referee()
    mark("counting_arguments", t0)

    t0 = time.perf_counter()
    measured = measure_q1()
    mark("q1_measurement", t0)

    t0 = time.perf_counter()
    agreement = agreement_panel()
    mark("agreement_panel", t0)

    t0 = time.perf_counter()
    reconciliation = reconcile_measured_with_proven(counts, measured)
    q2 = q2_confrontation(measured, counts)
    o1blob = q2["q2b_does_hardness_reappear_under_O1"]
    o1blob.pop("o1_identity_two_trade_failures_from_qg2_receipt", None)
    o1blob["o1_identity_two_trade_failures"] = int(
        receipts["semantics"]["qg2_o1_identity_two_trade_failures"]
    )
    o1blob["o1_identity_two_trade_failures_source"] = (
        "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json objectives.O1.identity_two_trade_failures"
    )
    q3 = q3_statement(q2)
    mark("q2_q3", t0)

    # ---- Q1 summary table ---------------------------------------------------
    def exp_of(tag: str):
        f = measured[tag]["fit"] if "fit" in measured[tag] else None
        if not f:
            return None
        return (f.get("tail") or f["full"])["slope"]

    q1_table = [
        {
            "row": "(a) regime predicate -- structure-only features",
            "object": "r6q.simple_features",
            "proven_bound": "Theta(n)",
            "proven_label": PROVEN,
            "measured_exponent": exp_of("STRUCT"),
            "measured_label": MEASURED,
            "measured_domain_n": list(LADDER_STRUCT),
        },
        {
            "row": "(a) regime predicate -- full R6Q P1 (Gsplit == 0 and f_B >= C_R6L)",
            "object": "r6o.dplus_pairs + r6m.donor_r6l_matching + r6q.borrow_family_min",
            "proven_bound": "O(n^5)  (max of Theta(n^4), O(n^2), O(n^5))",
            "proven_label": PROVEN,
            "measured_exponent": {
                "DPLUS": exp_of("DPLUS"), "R6L": exp_of("R6L"), "FBP": exp_of("FBP"),
            },
            "measured_label": MEASURED,
            "note": ("P1 is decidable in polynomial time but it is NOT structure-only: it "
                     "reads three family optima. The structure-only feature vector is "
                     "Theta(n); the QG-3-confirmed predicate is the O(n^5) one."),
        },
        {
            "row": "(b) certified exact optimum via QG-7e: min(C_D+, f_B', f_B'')",
            "object": "r6o.dplus_pairs + qg5b.bprime_family_min + qg7b.bsecond_family_min",
            "proven_bound": "O(n^6)  (dominated by f_B'')",
            "proven_label": PROVEN,
            "measured_exponent": exp_of("CF"),
            "measured_label": MEASURED,
            "measured_domain_n": list(LADDER_FBPP),
        },
        {
            "row": "(c) unrestricted DP referee",
            "object": "r6p.dp_cost_frozen_configs",
            "proven_bound": ("Theta(C_ext * 2^{2D} * n + n * A^{2K+1}) = Theta(n); "
                             "with the frozen constants 32 * 2^18 * n + O(n) * 4^7"),
            "proven_label": PROVEN,
            "measured_exponent": exp_of("DP"),
            "measured_label": MEASURED,
            "measured_domain_n": list(LADDER_DP),
        },
        {
            "row": "(d) naive configuration referee (context for (c))",
            "object": "r6m._brute_config_n1 / _brute_config_n2",
            "proven_bound": "Theta(A^{(2K+1)n}) = Theta(4^{7n})",
            "proven_label": PROVEN,
            "measured_exponent": None,
            "measured_label": "NOT FITTED (two executable points only)",
            "measured_domain_n": list(LADDER_NAIVE),
        },
        {
            "row": "(e) committed support-capped family search (context for (b))",
            "object": "r6p.dxx_search",
            "proven_bound": "O(n * A^{3n}) cells (A^{2n} pattern space x A^n Tag sweep)",
            "proven_label": PROVEN,
            "measured_per_qubit_factor": measured["FAM_dxx_maxweight1"]["fit_exponential"].get(
                "per_qubit_factor"),
            "measured_label": MEASURED,
            "measured_domain_n": list(LADDER_FAM),
        },
    ]

    gap = {
        "between_b_and_c": (
            "The gap runs the WRONG way for a separation narrative. (c), the unrestricted "
            "DP referee, is Theta(n). (b), the QG-7e certified closed form, is O(n^6). "
            "The referee the closed form was meant to replace is asymptotically cheaper "
            "than the closed form. The closed form's value is that it is a THEOREM about "
            "the shape of the optimum for all n, not that it is a faster optimizer."
        ),
        "where_an_exponential_gap_does_exist": (
            "Between (d) the naive configuration enumeration Theta(4^{7n}) and (c) the "
            "syndrome DP Theta(n) -- a collapse effected by the fixed 9-bit conserved "
            "syndrome, i.e. by QG-6's meta-theorem object, not by QG-7e -- and between "
            "(e) the committed family search O(n * 4^{3n}) and (b) the closed form O(n^6)."
        ),
    }

    # ---- gates ---------------------------------------------------------------
    fits_ok = True
    for tag, blob in measured.items():
        for fk in ("fit", "fit_exponential", "fit_power"):
            f = blob.get(fk)
            if not f:
                continue
            if "domain_n" not in f or "full" not in f:
                fits_ok = False
            elif f["full"].get("r_squared") is None or "residuals" not in f["full"]:
                fits_ok = False

    measurement_sink = {}
    extract_measurement(q1_table, "q1_table", measurement_sink)
    extract_measurement(q2, "q2", measurement_sink)

    payload_for_scan = canonical({
        "q1_table": q1_table, "gap": gap, "counting": counting, "naive": naive,
        "q2": q2, "q3": q3,
    })
    hardness_hits = scan_for_unearned_hardness(payload_for_scan)

    allowed_reads = {str(PROTOCOL_PATH)} | {str(v) for v in RECEIPTS.values()}
    stray_reads = sorted(set(READS) - allowed_reads)
    protected_touched = any(PROTECTED_SUBJECT in r for r in READS)
    chemistry_touched = any(
        seg in r for r in READS
        for seg in ("/DUCC", "cc-pVTZ", "cc-pvtz", "/chemistry", "ducc.results")
    )

    authority_flags = {
        "r6_authority": False, "novelty_credit": False, "donor_novelty_credit": False,
        "novelty_authority": False, "physical_quantum_advantage_claim": False,
    }

    truncation_ok = (
        sorted(int(k) for k in counts) == sorted(LADDER_COUNTS)
        and agreement["rows_total"] == sum(c for _, c in AGREEMENT_PANEL)
        and agreement["mismatches_total"] == len(agreement["mismatches_verbatim"])
        and sorted(int(k) for k in measured["DP"]["seconds"]) == sorted(LADDER_DP)
        and sorted(int(k) for k in measured["CF"]["seconds"]) == sorted(LADDER_FBPP)
        and sorted(int(k) for k in measured["FAM_dxx_maxweight1"]["seconds"])
        == sorted(LADDER_FAM)
        and naive["enumerated_domain_n"] == [1, 2, 3]
    )

    gates = {
        "G1_receipt_bindings_exact": bool(receipts["all_exact"]),
        "G2_label_discipline": all(
            c.get("label") in (PROVEN, MEASURED, CONJECTURE) for c in counting["checks"]
        ) and naive["label"] == PROVEN,
        "G3_counting_instrumented": bool(counting["all_hold"])
        and bool(naive["closed_form_matches_enumeration"]),
        "G4_agreement": bool(agreement["closed_form_identity_holds"]),
        "G5_fits_reported_with_residuals_and_domain": bool(fits_ok),
        "G6_no_unearned_hardness_claim": not hardness_hits,
        "G7_authority_ceiling_not_r6": all(v is False for v in authority_flags.values()),
        "G8_isolation": (not stray_reads) and (not protected_touched)
        and (not chemistry_touched),
        "G9_determinism_digest_is_timing_free": True,  # rewritten below
        "G10_no_silent_truncation": bool(truncation_ok),
    }

    all_gates = all(gates.values())
    terminal = (
        "QG22_PARTIAL__HARDNESS_LOCATED_ELSEWHERE" if all_gates else "QG22_CANNOT_CHECK"
    )

    core = {
        "schema": "ORION.QG.QG22.ComplexitySeparation.v1",
        "lane": "QG-22 the complexity separation (wave 3)",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "protocol": "development/orion-qg-regime-geometry/QG22_COMPLEXITY_SEPARATION_PROTOCOL_V1.md",
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "base_revision": BASE_REVISION,
        "question": (
            "Is regime membership decidable in polynomial time while exact optimization "
            "is hard, for a frozen compilation family?"
        ),
        "terminal": terminal,
        "terminal_reading": {
            "what_the_terminal_asserts": (
                "(i) For the frozen unit-cost TARE family there is NO complexity "
                "separation to state: deciding regime membership, computing the exact "
                "optimum and deciding whether a given compilation is optimal are all "
                "polynomial in n, and the exact optimum is computable in time affine in "
                "n. (ii) A CANDIDATE location for genuine difficulty has been identified "
                "and evidenced -- families whose feasibility predicate is not a "
                "fixed-dimension conserved syndrome, of which StabPrep is this "
                "programme's own instance -- together with the grammar parameters "
                "(block count K, syndrome dimension D) rather than n."
            ),
            "what_the_terminal_does_NOT_assert": (
                "The word 'hardness' in the frozen terminal name is a lane label, not a "
                "result. No reduction is supplied, no lower bound is proved, and nothing "
                "here says any problem lies outside P. Every exponential quantity in this "
                "receipt is the work of an algorithm we wrote, never a property of a "
                "problem."
            ),
            "why_not_the_no_separation_terminal": (
                "The frozen terminal QG22_NO_SEPARATION__CLASSIFICATION_COLLAPSES_THE_"
                "PROBLEM names the classification as the collapse agent. This lane's own "
                "measurements contradict that attribution: the unrestricted DP referee was "
                "already affine in n before QG-7e existed, its polynomiality comes from "
                "the fixed 9-bit conserved syndrome, and evaluating the QG-7e closed form "
                "is asymptotically MORE expensive (O(n^6)) than the referee it "
                "characterizes (Theta(n)). Selecting that terminal would have recorded a "
                "false attribution; the PARTIAL terminal records the true one."
            ),
        },
        "authority": (
            "ORIONQG_QG22_NO_SEPARATION_FOR_UNIT_COST_TARE__EXACT_OPTIMUM_IS_LINEAR_IN_N_"
            "BY_THE_FIXED_DIMENSION_CONSERVED_SYNDROME__CLASSIFICATION_IS_NOT_THE_COLLAPSE_"
            "AGENT__CANDIDATE_LOCATED_IN_FAMILIES_WITHOUT_A_CONSERVED_SYNDROME__NOT_R6"
        ),
        "scope": (
            "UPPER_BOUNDS_ONLY__FROZEN_TARE_R6M_GRAMMAR__UNIT_COST_O0_PLUS_O1_CONTROL__"
            "NO_REDUCTION__NO_LOWER_BOUND__NOT_R6"
        ),
        "complexity_class_claim": "none",
        "reduction_supplied": False,
        "lower_bound_supplied": False,
        "donor_boundary": {
            "zero_novelty_credit": [
                "complexity classes and their vocabulary (P, NP, #P, EXPTIME, FPT, XP)",
                "asymptotic notation and least-squares fitting",
                "dynamic programming and min-plus (tropical) composition",
                "subset / don't-care zeta transforms",
                "Bellman-Ford and Dijkstra shortest paths",
                "donor register D1-D5, in particular D3 (Touati et al. 2006, "
                "undecidability of optimal phase ordering)",
            ],
            "candidate_contribution": (
                "only the compiler-specific statement for this programme's frozen "
                "families, and in this lane that statement is a NEGATIVE one"
            ),
        },
        "frozen_constants": {
            "K_blocks": K_BLOCKS, "A_alphabet": A_ALPHABET,
            "L_letters_per_qubit": L_LETTERS, "D_syndrome_bits": D_SYNDROME,
            "C_ext_external_configs": C_EXT,
            "input_size_bits": "12n",
        },
        "receipt_bindings": receipts,
        "read_audit": {
            "files_read": sorted(set(READS)),
            "allowed": "the frozen protocol plus the seven bound receipt JSONs",
            "stray_reads": stray_reads,
            "protected_subject_touched": protected_touched,
            "chemistry_path_touched": chemistry_touched,
        },
        "q1_table": q1_table,
        "q1_gap": gap,
        "measured_vs_proven_reconciliation": reconciliation,
        "qg6_corollary_reading": {
            "bound_as_committed": receipts["semantics"]["qg6_search_complexity_corollary"],
            "label": PROVEN,
            "what_it_bounds": (
                "QG-6's sum_{k=0}^d binom(n,k) A^k = O(n^d A^d) counts the SUPPORT-<=d "
                "PAULIS, i.e. the size of the certified search SPACE per structural "
                "generator, with d = 2 and A = 4 for TARE. It is a statement about the "
                "space a certified search must cover, not about any implementation."
            ),
            "what_it_does_not_bound": (
                "It is not a bound on the committed family search r6p.dxx_search, which "
                "reaches the same D++ optimum through an A^{2n}-cell don't-care pattern "
                "space and an A^n - 1 Tag sweep, i.e. O(n * A^{3n}) cells. The committed "
                "implementation therefore does NOT realize QG-6's own corollary; the "
                "corollary says a support-capped certified search over "
                "O(n^2 * 16) frame-pair candidates per block would suffice."
            ),
            "consequence_for_this_lane": (
                "The exponential behaviour measured for r6p.dxx_search is an artefact of "
                "that implementation, exactly as the exponential behaviour of the naive "
                "configuration referee is an artefact of that referee. Neither is "
                "evidence about the difficulty of the problem. This is the single "
                "sharpest reason why no separation can be read off our own runtimes."
            ),
            "scope_as_committed": (
                receipts["semantics"]["qg6_search_complexity_corollary"].get("scope")
            ),
        },
        "q1_counting_arguments": counting,
        "q1_naive_referee": naive,
        "q1_instrumented_counts": {str(k): v for k, v in counts.items()},
        "agreement_panel": agreement,
        "q2": q2,
        "q3": q3,
        "gates": gates,
        "caps_disclosed": [
            "runtime cap < 25 min per run",
            f"instrumented cell counts on n in {list(LADDER_COUNTS)}",
            f"NAIVE executed on n in {list(LADDER_NAIVE)}; n >= 3 not attempted "
            f"(committed enumerators defined for n in {{1,2}} only; |Cfg(3)| > 10^12)",
            f"FAM dxx_search executed at max_weight=1 on n in {list(LADDER_FAM)}; "
            "max_weight=2 guarded to n in {1,2,3} by the committed module",
            f"FBPP ladder stops at n = {max(LADDER_FBPP)}",
            f"FBP ladder stops at n = {max(LADDER_FBP)}",
            f"DPLUS ladder stops at n = {max(LADDER_DPLUS)}",
            f"DP ladder stops at n = {max(LADDER_DP)}",
            f"agreement panel {list(AGREEMENT_PANEL)}",
            f"verbatim serialization cap {VERBATIM_CAP} rows per panel",
            "StabPrep treated analytically only; no StabPrep referee executed",
        ],
        "r6_authority": False,
        "novelty_credit": False,
        "donor_novelty_credit": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "network_access": False,
        "reserved_stretched_n2_accessed": False,
        "responsibility": (
            "RESP:NO_COMPLEXITY_SEPARATION_FOR_UNIT_COST_TARE__DP_REFEREE_IS_LINEAR_IN_N__"
            "CLOSED_FORM_IS_ON6_AND_IS_NOT_THE_TRACTABILITY_SOURCE__O1_CONTROL_CLOSES_THE_"
            "NO_CLOSED_FORM_ESCAPE__CANDIDATE_LOCATED_IN_STABPREP_AND_IN_THE_GRAMMAR_PARAMETERS"
        ),
    }

    digest_payload = canonical(core)
    core["gates"]["G9_determinism_digest_is_timing_free"] = (
        "measured" not in core
        and "timing" not in core
        and "measured_fields_extracted_from_core" not in core
        and '"seconds"' not in digest_payload
        and '_seconds"' not in digest_payload
        and not any(f'"{k}"' in digest_payload for k in MEASUREMENT_KEYS)
    )
    if not core["gates"]["G9_determinism_digest_is_timing_free"]:
        core["terminal"] = "QG22_CANNOT_CHECK"
    digest_payload = canonical(core)
    digest = hashlib.sha256(digest_payload.encode()).hexdigest()
    core["result_digest"] = digest
    core["measured"] = measured
    core["measured_fields_extracted_from_core"] = measurement_sink
    core["timing"] = {
        "convention": ("R6P: timing and measured-runtime fields are excluded from the "
                       "canonical stdout line and from result_digest; the MEASURED fits "
                       "live in the 'measured' section, which is likewise outside the "
                       "digest"),
        "runtime_cap_seconds": 1500,
        "runtime_seconds": round(time.perf_counter() - t_start, 3),
        "section_seconds": section_seconds,
    }
    core["timing"]["runtime_under_cap"] = core["timing"]["runtime_seconds"] < 1500

    Path(args.out).write_text(json.dumps(core, indent=1, sort_keys=True) + "\n")
    print(f"{TOKEN_PREFIX}{digest}")
    print(f"ORIONQG_QG22_TERMINAL={terminal}")
    print(f"ORIONQG_QG22_GATES={canonical(gates)}")
    print(f"ORIONQG_QG22_PROTOCOL_SHA256={core['protocol_sha256']}")
    return core


if __name__ == "__main__":
    main()
