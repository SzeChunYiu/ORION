"""Q1-XOVER crossover/resource evaluation over the frozen R6 stack.

Executes the frozen protocol `Q1_XOVER_PROTOCOL_V1.md` (ORION-05 paper lane,
plan gate Q1-XOVER): exact crossover table for the support-two active core
(A_DXX) against the strongest available baselines (A_DP unrestricted DP
referee; A_DPLUS support-one enlarged donor family; C_R6L donor referee) across
instance size, instance structure, and compute-budget regimes.

Registered modules are imported UNMODIFIED. The single declared in-memory
amendment is the `r6p.EXPECTED_PAIR_COUNTS` guard extension for n in {4,5,6},
independently recounted here and cross-checked against
`r6s.PAIR_COUNTS_SUPPORT2`; the committed file is untouched and the amendment
is recorded in the receipt under `integrity.guard_extensions`.

Outputs (mode "x"): Q1_XOVER_RESULTS_V1.json (deterministic modulo the
documented machine-dependent keys), Q1_XOVER_TIMING_V1.json (machine
dependent). Env config: Q1XOVER_SEED, Q1XOVER_DXX_BUDGET_S, Q1XOVER_OUT_DIR,
ORIONQ_R6R_CACHE (fresh-subject DUCC clone cache). CLI `--smoke`: tiny local
sanity core, no network.
"""

from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402
import max_r6r_prospective_fresh_subject as r6r  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402
import max_r5h_mixed_cardinality_development as base  # noqa: E402  (SUBJECTS)

# ---- frozen configuration (protocol V1; every constant is protocol-declared) --

SEED = int(os.environ.get("Q1XOVER_SEED", "20260827"))
DXX_BUDGET_S = float(os.environ.get("Q1XOVER_DXX_BUDGET_S", "600"))
DIRECT_DXX_MAX_N = 6  # a-priori memory rule: 8*4^(2n) bytes per zeta array
PANEL_SIZES = {1: 24, 2: 32, 3: 32, 4: 24, 5: 12, 6: 4}
FAMILIES = ("uniform", "commuting_symmetric", "lowweight")
DETERMINISM_MAX_N = 3
WITNESS_HEAD = 2  # first instances per cell that request a D++ witness
PROTOCOL_NAME = "Q1_XOVER_PROTOCOL_V1.md"
INF = r6m.INF
MATCHING = r6m._SYNTHETIC_MATCHING
PREVIOUSLY_READ_BLOBS = frozenset(
    {
        *r6r.COMMITTED_SUBJECT_BLOBS,
        # benzene DUCC2 read by the R6R prospective run itself (receipt blob):
        "5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915",
    }
)
MACHINE_DEPENDENT_KEYS = (
    "dxx.status",
    "dxx.C_Dxx",
    "dxx.witness_seconds",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_text(path.read_text())


# ---- structure generators (frozen laws; deterministic given SEED) ------------


def _sample_nonzero(rng, n: int):
    while True:
        x = int(rng.integers(0, 1 << n))
        z = int(rng.integers(0, 1 << n))
        if x or z:
            return (x, z)


def gen_uniform(rng, n: int):
    return tuple(_sample_nonzero(rng, n) for _ in range(6))


def gen_lowweight(rng, n: int):
    out = []
    while len(out) < 6:
        key = _sample_nonzero(rng, n)
        if p10.wt(key) <= 2:
            out.append(key)
    return tuple(out)


def gen_commuting_symmetric(rng, n: int):
    """Six pairwise-commuting targets z = A x with A = D + P + P^T over F_2.

    Symmetry of A gives sym(t_i, t_j) = x_i^T A x_j + x_j^T A x_i = 0 (mod 2).
    D is a random diagonal, P a random partial permutation with n//2 ones
    (row-weight of A <= 3).
    """
    diag = int(rng.integers(0, 1 << n))
    perm = list(range(n))
    rng.shuffle(perm)
    k = n // 2
    mapping = [(perm[2 * i], perm[2 * i + 1]) for i in range(k)]

    def matvec(x: int) -> int:
        z = x & diag
        for row, col in mapping:
            if (x >> col) & 1:
                z ^= 1 << row
            if (x >> row) & 1:
                z ^= 1 << col
        return z

    targets = []
    for _ in range(6):
        x = 0
        while x == 0:
            x = int(rng.integers(0, 1 << n))
        targets.append((x, matvec(x)))
    return tuple(targets)


GENERATORS = {
    "uniform": gen_uniform,
    "commuting_symmetric": gen_commuting_symmetric,
    "lowweight": gen_lowweight,
}


# ---- independent pair recount + guard extension ------------------------------


def recount_pairs(n: int) -> int:
    keys = [
        (x, z) for x in range(1 << n) for z in range(1 << n) if (x, z) != (0, 0)
    ]
    small = [k for k in keys if p10.wt(k) <= 2]
    return sum(1 for a in small for b in small if p10.symp(a, b) == 1)


def extend_pair_guard() -> dict[str, Any]:
    committed = dict(r6p.EXPECTED_PAIR_COUNTS)
    recount_low = {n: recount_pairs(n) for n in sorted(committed)}
    if recount_low != committed:
        raise AssertionError({"guard_recount_mismatch": [recount_low, committed]})
    registered = dict(r6s.PAIR_COUNTS_SUPPORT2)
    recount_high = {n: recount_pairs(n) for n in (4, 5, 6)}
    if recount_high.get(4) != registered.get(4):
        raise AssertionError(
            {"n4_recount_vs_r6s": [recount_high.get(4), registered.get(4)]}
        )
    for n, value in recount_high.items():
        r6p.EXPECTED_PAIR_COUNTS[n] = value
    return {
        "committed_guard_values": {str(k): v for k, v in committed.items()},
        "recounted_n4_5_6": {str(k): v for k, v in recount_high.items()},
        "r6s_registered": {str(k): v for k, v in registered.items()},
        "amendment": "in-memory only; committed r6p file untouched",
    }


# ---- family-size exact table -------------------------------------------------


def family_size_table() -> dict[str, Any]:
    rows = {}
    for n in range(1, 21):
        unrestricted = (4**n - 1) ** 6
        active = (3 * n + 9 * (n * (n - 1) // 2)) ** 6
        support_one = (3 * n) ** 6
        rows[str(n)] = {
            "per_block_unrestricted": 4**n - 1,
            "per_block_active_core": 3 * n + 9 * (n * (n - 1) // 2),
            "per_block_support_one": 3 * n,
            "family_unrestricted": unrestricted,
            "family_active_core": active,
            "family_support_one": support_one,
            "active_core_equals_unrestricted": active == unrestricted,
            "ratio_active_over_unrestricted": active / unrestricted,
        }
    equal_ns = [n for n in range(1, 21) if rows[str(n)]["active_core_equals_unrestricted"]]
    strict_ns = [n for n in range(1, 21) if not rows[str(n)]["active_core_equals_unrestricted"]]
    return {
        "rows": rows,
        "identity_holds_for_n": equal_ns,
        "strict_for_n": strict_ns,
        "integer_crossover": (
            "active_core_family == unrestricted_family iff n <= 2; "
            "strict subset from n = 3"
        ),
    }


# ---- arm execution -----------------------------------------------------------


def _dxx_child(target_pairs, n: int, want_witness: bool, queue) -> None:
    try:
        out = r6p.dxx_search(target_pairs, n, max_weight=2, want_witness=want_witness)
        payload = {
            "status": "EXACT",
            "C_Dxx": int(out["C_Dxx"]),
            "witness": out.get("witness") if want_witness else None,
        }
    except BaseException as exc:  # child-side; surfaced as ERROR cell
        payload = {"status": "ERROR", "error": repr(exc)[:300]}
    queue.put(payload)


def run_dxx_bounded(target_pairs, n: int, want_witness: bool) -> dict[str, Any]:
    """Direct A_DXX under the frozen wall-clock budget, cold tables per call.

    The parent never calls dxx_search, so every forked child rebuilds the
    (n, 2) tables: t_dxx is the honest cold per-instance direct-search cost.
    """
    ctx = multiprocessing.get_context("fork")
    queue = ctx.Queue()
    proc = ctx.Process(target=_dxx_child, args=(target_pairs, n, want_witness, queue))
    t0 = time.perf_counter()
    proc.start()
    proc.join(DXX_BUDGET_S)
    elapsed = time.perf_counter() - t0
    if proc.is_alive():
        proc.terminate()
        proc.join()
        return {"status": "TIMEOUT", "budget_s": DXX_BUDGET_S, "witness_seconds": elapsed}
    try:
        payload = queue.get_nowait()
    except Exception:
        payload = {"status": "ERROR", "error": "child produced no payload"}
    payload["witness_seconds"] = elapsed
    return payload


def frame_support_total_dp(wit: dict[str, Any]) -> int:
    return int(sum(p10.wt(tuple(r)) for block in wit["R"].values() for r in block))


def frame_support_total_dxx(wit: dict[str, Any]) -> int:
    return int(sum(b["support"][0] + b["support"][1] for b in wit["blocks"]))


def run_instance(six_targets, n: int, instance_idx: int, timing_rows: list) -> dict[str, Any]:
    target_pairs = (
        (six_targets[0], six_targets[1]),
        (six_targets[2], six_targets[3]),
        (six_targets[4], six_targets[5]),
    )
    terms = r6m._synthetic_terms(target_pairs)
    r6m._local_table.cache_clear()
    r6o._block_cache.clear()
    r6q._borrow_block_cache.clear()

    t0 = time.perf_counter()
    dp = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
    t_dp = time.perf_counter() - t0
    c_dp = int(dp["C_R6M"])
    if not all(dp["checks"].values()):
        raise AssertionError("dp witness checks failed")

    r6m._local_table.cache_clear()
    t0 = time.perf_counter()
    r6l = r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))
    t_r6l = time.perf_counter() - t0
    c_r6l = int(r6l["C_R6L"])

    t0 = time.perf_counter()
    dplus = r6o.dplus_pairs(target_pairs, n)
    t_dplus = time.perf_counter() - t0
    c_dplus = int(dplus["C_Dplus"])

    if not (c_dp <= c_r6l):
        raise AssertionError({"r6l_containment_violated": [c_dp, c_r6l]})
    if not (c_dp <= c_dplus):
        raise AssertionError({"dplus_containment_violated": [c_dp, c_dplus]})

    want_witness = instance_idx < WITNESS_HEAD or c_dplus > c_dp
    dxx_cell: dict[str, Any]
    timing_row: dict[str, Any] = {
        "n": n,
        "instance": instance_idx,
        "t_dp": t_dp,
        "t_r6l": t_r6l,
        "t_dplus": t_dplus,
        "want_witness": want_witness,
    }
    if n <= DIRECT_DXX_MAX_N:
        dxx = run_dxx_bounded(target_pairs, n, want_witness)
        timing_row["t_dxx"] = dxx.get("witness_seconds")
        timing_row["dxx_status"] = dxx["status"]
        if dxx["status"] == "EXACT":
            c_dxx = int(dxx["C_Dxx"])
            wit = dxx["witness"]
            wit_support = frame_support_total_dxx(wit) if wit else None
            wit_verified = bool(r6p.verify_dxx_witness(target_pairs, n, wit)) if wit else None
            if not c_dp <= c_dxx <= c_dplus:
                raise AssertionError(
                    {"sandwich_violated": [c_dp, c_dxx, c_dplus]}
                )
            dxx_cell = {
                "status": "EXACT",
                "C_Dxx": c_dxx,
                "witness_requested": want_witness,
                "witness_verified": wit_verified,
                "witness_frame_support_total": wit_support,
                "witness_max_frame_support": (
                    int(wit["max_frame_support"]) if wit else None
                ),
            }
        else:
            dxx_cell = {
                "status": dxx["status"],
                "C_Dxx": None,
                "error": dxx.get("error"),
            }
    else:
        dxx_cell = {
            "status": "A_PRIORI_INFEASIBLE_N_GT_6",
            "C_Dxx": None,
            "memory_bytes_per_zeta_array": 8 * 4 ** (2 * n),
        }

    dp_support = frame_support_total_dp(dp)
    row = {
        "targets": [[int(v) for v in t] for t in six_targets],
        "C_DP": c_dp,
        "C_R6L": c_r6l,
        "C_Dplus": c_dplus,
        "dp_witness_frame_support_total": dp_support,
        "dp_tag_weight": int(p10.wt(tuple(dp["S"]))),
        "critical_dplus_gt_dp": c_dplus > c_dp,
        "gap_dplus_minus_dp": c_dplus - c_dp,
        "dxx": dxx_cell,
    }
    timing_row["C_DP"] = c_dp
    timing_row["C_Dplus"] = c_dplus
    timing_rows.append(timing_row)
    return row


def run_cell(family: str, n: int, count: int, rng, timing_rows: list) -> dict[str, Any]:
    gen = GENERATORS[family]
    instances = [run_instance(gen(rng, n), n, i, timing_rows) for i in range(count)]
    critical = sum(1 for r in instances if r["critical_dplus_gt_dp"])
    dxx_executed = [r for r in instances if r["dxx"]["status"] == "EXACT"]
    dxx_mismatch = [
        {"instance": instances.index(r), "C_DP": r["C_DP"], "C_Dxx": r["dxx"]["C_Dxx"]}
        for r in dxx_executed
        if r["dxx"]["C_Dxx"] != r["C_DP"]
    ]
    support_totals = [
        r["dp_witness_frame_support_total"] for r in instances
    ]
    return {
        "family": family,
        "n": n,
        "instance_count": count,
        "critical_count": critical,
        "max_gap_dplus_minus_dp": max(r["gap_dplus_minus_dp"] for r in instances),
        "dxx_executed": len(dxx_executed),
        "dxx_timeout_or_error": count - len(dxx_executed),
        "dxx_cost_mismatches": dxx_mismatch,
        "dpp_witness_support": {
            "min": min(support_totals),
            "max": max(support_totals),
        },
        "all_equal_regime": all(
            r["C_DP"] == r["C_Dplus"] == r["C_R6L"] for r in instances
        ),
        "instances": instances,
    }


# ---- chemistry lane (registered subjects) ------------------------------------


def run_chemistry(timing: dict[str, Any]) -> dict[str, Any]:
    import max_r5h_mixed_cardinality_development as base

    out = {}
    for name, cfg in base.SUBJECTS.items():
        n = int(cfg["n_qubits"])
        terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"chem_blob_mismatch": name})
        six = [int(i) for i in source_indices]
        six_targets = [terms[i][0] for i in six]
        if not all(
            p10.symp(six_targets[i], six_targets[j]) == 0
            for i in range(6)
            for j in range(i + 1, 6)
        ):
            raise AssertionError({"chem_not_pairwise_commuting": name})
        rows = []
        for pairs in r6m.perfect_matchings(six):
            target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            r6m._local_table.cache_clear()
            r6o._block_cache.clear()
            t0 = time.perf_counter()
            r6l_wit = r6m.donor_r6l_matching(terms, pairs, n, six)
            t_r6l = time.perf_counter() - t0
            t0 = time.perf_counter()
            dplus = r6o.dplus_pairs(target_pairs, n)
            t_dplus = time.perf_counter() - t0
            r6m._local_table.cache_clear()
            t0 = time.perf_counter()
            dp = r6m.exact_r6m_matching(terms, pairs, n, six)
            t_dp = time.perf_counter() - t0
            c_dp, c_dplus, c_r6l = (
                int(dp["C_R6M"]), int(dplus["C_Dplus"]), int(r6l_wit["C_R6L"])
            )
            if not (c_dp <= c_r6l and c_dp <= c_dplus):
                raise AssertionError({"chem_containment": [c_dp, c_dplus, c_r6l]})
            # containment pinch (n > 6): C_DP <= C_Dxx <= C_Dplus, and here the
            # chemistry regime has C_DP == C_Dplus (checked below), forcing
            # C_Dxx == C_DP without any direct family search.
            pinched = c_dp == c_dplus
            rows.append(
                {
                    "matching": [list(p) for p in pairs],
                    "C_DP": c_dp,
                    "C_R6L": c_r6l,
                    "C_Dplus": c_dplus,
                    "dxx": {
                        "status": (
                            "CONTAINMENT_PINCH_EQUAL_ENDPOINTS"
                            if pinched
                            else "A_PRIORI_INFEASIBLE_N_GT_6_UNPINCHED"
                        ),
                        "C_Dxx": c_dp if pinched else None,
                    },
                    "dp_witness_frame_support_total": frame_support_total_dp(dp),
                    "critical_dplus_gt_dp": c_dplus > c_dp,
                    "timings": {
                        "t_r6l": t_r6l, "t_dplus": t_dplus, "t_dp": t_dp
                    },
                }
            )
        timing.setdefault("chemistry", {})[name] = {
            "n_qubits": n,
            "rows": rows,
        }
        out[name] = {
            "n_qubits": n,
            "blob": cfg["blob"],
            "blob_verified": True,
            "matching_count": len(rows),
            "all_equal_regime": all(
                r["C_DP"] == r["C_Dplus"] == r["C_R6L"] for r in rows
            ),
            "critical_count": sum(1 for r in rows if r["critical_dplus_gt_dp"]),
            "rows": rows,
        }
    return out


# ---- fresh-subject prospective lane (R6R machinery reused unmodified) --------


def run_fresh_subject(timing: dict[str, Any]) -> dict[str, Any]:
    listing = r6r.pinned_tree_listing()
    candidates = r6r.eligible_candidates(listing)
    attempts = []
    selected = None
    admitted = None
    for cfg in candidates[: r6r.CANDIDATE_CAP]:
        if cfg["blob"] in PREVIOUSLY_READ_BLOBS:
            attempts.append(
                {
                    "path": cfg["path"],
                    "blob": cfg["blob"],
                    "n_qubits": cfg["n_qubits"],
                    "admitted": False,
                    "reason": "previously_read_blob_excluded",
                }
            )
            continue
        result = r6r.try_admit(cfg)
        attempts.append(
            {
                "path": cfg["path"],
                "blob": cfg["blob"],
                "n_qubits": cfg["n_qubits"],
                "admitted": result["admitted"],
                "reason": None if result["admitted"] else result["reason"],
            }
        )
        if result["admitted"]:
            selected = cfg
            admitted = result
            break
    if selected is None:
        return {
            "available": False,
            "eligible_candidate_count": len(candidates),
            "admission_attempts": attempts,
        }

    n = int(selected["n_qubits"])
    terms, six = admitted["terms"], admitted["six"]
    t0 = time.perf_counter()
    matchings, predictions = r6r.stage1_predict(terms, six, n)
    t_stage1 = time.perf_counter() - t0
    payload = {
        "schema": "ORIONQ.Q1XOVER.Stage1FreshSubjectPrediction.v1",
        "subject": selected["path"],
        "blob": selected["blob"],
        "n_qubits": n,
        "predicted_rows": predictions,
    }
    digest = r6r.emit_stage1(payload)
    t0 = time.perf_counter()
    rows = r6r.stage2_referee(terms, six, n, matchings, predictions)
    t_stage2 = time.perf_counter() - t0
    timing.setdefault("fresh_subject", {})[
        "t_stage1_predict_s"
    ] = t_stage1
    timing["fresh_subject"]["t_stage2_referee_s"] = t_stage2

    cost_matches = [bool(r["cost_match"]) for r in rows]
    regime_matches = [bool(r["regime_match"]) for r in rows]
    all_pinched_equal = all(bool(r["dxx_pinched_equal"]) for r in rows)
    return {
        "available": True,
        "subject": selected["path"],
        "blob": selected["blob"],
        "n_qubits": n,
        "eligible_candidate_count": len(candidates),
        "admission_attempts": attempts,
        "stage1_digest": digest,
        "matching_count": len(rows),
        "all_cost_matches": all(cost_matches),
        "all_regime_matches": all(regime_matches),
        "all_dxx_pinched_equal": all_pinched_equal,
        "observed_regimes": sorted({r["truth_regime"] for r in rows}),
        "rows": rows,
    }


# ---- integrity + predictions -------------------------------------------------


def module_hashes() -> dict[str, str]:
    out = {}
    for name, mod in sorted(sys.modules.items()):
        file = getattr(mod, "__file__", None)
        if file and str(Path(file).resolve()).startswith(str(HERE)):
            out[str(Path(file).relative_to(HERE))] = sha256_file(Path(file))
    return out


def build_predictions() -> dict[str, Any]:
    return {
        "P1_all_size_theorem": (
            "for every executed direct A_DXX cell, C_Dxx == C_DP"
        ),
        "P2_sandwich": (
            "everywhere C_DP <= C_Dxx <= C_Dplus and C_DP <= C_R6L"
        ),
        "P3_family_size_identity": (
            "active_core_family(n) == unrestricted_family(n) iff n <= 2; "
            "strict subset for 3 <= n <= 20"
        ),
        "P4_witness_support": (
            "every verified A_DXX witness has six-frame support total <= 12; "
            "A_DP witness support recorded (unbounded a priori)"
        ),
        "P5_r6q_identity_fresh_subject": (
            "predicted C_DP == min(C_R6L, C_Dplus, f_B) on all 15 matchings "
            "with regime labels matching (R6Q two-trade identity)"
        ),
        "P6_feasibility_rule": (
            "direct A_DXX attempted iff n <= 6; chemistry/fresh cells record "
            "A_PRIORI_INFEASIBLE_N_GT_6 (or containment pinch where endpoints "
            "are equal)"
        ),
    }


def evaluate_predictions(receipt: dict[str, Any]) -> dict[str, bool]:
    fam = receipt["family_sizes"]
    panel = receipt["panel"]
    outcomes = {}
    mismatches = []
    timeouts = 0
    for family, cells in panel.items():
        for cell in cells:
            mismatches.extend(
                {"family": family, **m} for m in cell["dxx_cost_mismatches"]
            )
            timeouts += cell["dxx_timeout_or_error"]
    outcomes["P1_all_size_theorem"] = not mismatches
    sandwich_ok = True
    for family, cells in panel.items():
        for cell in cells:
            for row in cell["instances"]:
                if row["C_DP"] > row["C_R6L"] or row["C_DP"] > row["C_Dplus"]:
                    sandwich_ok = False
                d = row["dxx"]
                if d["status"] == "EXACT" and not (
                    row["C_DP"] <= d["C_Dxx"] <= row["C_Dplus"]
                ):
                    sandwich_ok = False
    outcomes["P2_sandwich"] = sandwich_ok
    outcomes["P3_family_size_identity"] = fam["identity_holds_for_n"] == [1, 2] and fam[
        "strict_for_n"
    ] == list(range(3, 21))
    p4_ok = True
    for family, cells in panel.items():
        for cell in cells:
            for row in cell["instances"]:
                d = row["dxx"]
                if d.get("witness_verified") is False:
                    p4_ok = False
                if d.get("witness_frame_support_total") is not None and d[
                    "witness_frame_support_total"
                ] > 12:
                    p4_ok = False
    outcomes["P4_witness_support"] = p4_ok
    fresh = receipt.get("fresh_subject") or {}
    outcomes["P5_r6q_identity_fresh_subject"] = bool(
        fresh.get("available")
        and fresh.get("all_cost_matches")
        and fresh.get("all_regime_matches")
        and fresh.get("all_dxx_pinched_equal")
    )
    p6_ok = timeouts == 0
    for family, cells in panel.items():
        for cell in cells:
            for row in cell["instances"]:
                if cell["n"] > DIRECT_DXX_MAX_N and row["dxx"]["status"] not in (
                    "A_PRIORI_INFEASIBLE_N_GT_6",
                    "CONTAINMENT_PINCH_EQUAL_ENDPOINTS",
                ):
                    p6_ok = False
    outcomes["P6_feasibility_rule"] = p6_ok
    return outcomes


# ---- determinism projection --------------------------------------------------


def determinism_projection(receipt: dict[str, Any], max_n: int) -> str:
    proj = {
        "panel": {
            family: [
                {
                    k: v
                    for k, v in cell.items()
                    if k
                    not in (
                        "instances",
                    )
                }
                for cell in cells
                if cell["n"] <= max_n
            ]
            for family, cells in receipt["panel"].items()
        },
        "instance_digests": {
            family: [
                {
                    "n": cell["n"],
                    "rows": [
                        canonical_json(
                            {
                                kk: vv
                                for kk, vv in row.items()
                                if kk not in ("dxx",)
                                or row["dxx"]["status"] == "EXACT"
                            }
                        )
                        for row in cell["instances"]
                    ],
                }
                for cell in cells
                if cell["n"] <= max_n
            ]
            for family, cells in receipt["panel"].items()
        },
    }
    return sha256_text(canonical_json(proj))


# ---- main --------------------------------------------------------------------

SMOKE_PANEL = {1: 2, 2: 2}


def main() -> dict[str, Any]:
    smoke = "--smoke" in sys.argv
    panel_sizes = SMOKE_PANEL if smoke else PANEL_SIZES
    out_dir = Path(os.environ.get("Q1XOVER_OUT_DIR") or HERE)
    results_path = out_dir / "Q1_XOVER_RESULTS_V1.json"
    timing_path = out_dir / "Q1_XOVER_TIMING_V1.json"
    draft_path = out_dir / "Q1_XOVER_RESULTS_DRAFT.json"

    protocol_path = HERE / PROTOCOL_NAME
    protocol_sha = sha256_file(protocol_path)

    guard = extend_pair_guard()
    predictions = build_predictions()
    predictions_digest = sha256_text(canonical_json(predictions))
    print("ORIONQ_Q1XOVER_STAGE0_PREDICTIONS=" + canonical_json(predictions))
    print("ORIONQ_Q1XOVER_STAGE0_DIGEST=" + predictions_digest)
    sys.stdout.flush()

    receipt: dict[str, Any] = {
        "schema": "ORIONQ.Q1XOVER.CrossoverEvaluation.v1",
        "scope": (
            "EXACT_CROSSOVER_RESOURCE_EVALUATION_OVER_FROZEN_R6_STACK__"
            "NO_NEW_THEOREM_AUTHORITY"
        ),
        "protocol": PROTOCOL_NAME,
        "protocol_sha256": protocol_sha,
        "smoke_run": smoke,
        "frozen_config": {
            "seed": SEED,
            "panel_sizes": {str(k): v for k, v in panel_sizes.items()},
            "families": list(FAMILIES),
            "dxx_budget_s": DXX_BUDGET_S,
            "direct_dxx_max_n": DIRECT_DXX_MAX_N,
            "witness_head_per_cell": WITNESS_HEAD,
            "determinism_max_n": DETERMINISM_MAX_N,
            "machine_dependent_keys": list(MACHINE_DEPENDENT_KEYS),
        },
        "integrity": {
            "module_hashes": module_hashes(),
            "guard_extensions": guard,
        },
        "predictions": predictions,
        "predictions_digest": predictions_digest,
    }

    timing: dict[str, Any] = {
        "host": platform.node(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "note": (
            "all wall-clock numbers machine-dependent; receipt cost cells "
            "deterministic modulo machine_dependent_keys"
        ),
        "panel_rows": [],
    }

    receipt["family_sizes"] = family_size_table()

    panel_timing_rows = timing["panel_rows"]
    panel: dict[str, Any] = {}
    for family in FAMILIES:
        rng = np.random.default_rng(SEED)
        cells = []
        for n in sorted(panel_sizes):
            cell = run_cell(family, n, panel_sizes[n], rng, panel_timing_rows)
            cells.append(cell)
            panel[family] = cells
            receipt["panel"] = panel
            draft_path.write_text(canonical_json(receipt))
        print(f"ORIONQ_Q1XOVER_PANEL_DONE family={family}", flush=True)

    if not smoke:
        projection_run1 = determinism_projection(receipt, DETERMINISM_MAX_N)
        # Checker repair (post-run, commit-level root cause): the main panel run
        # reseeds `rng = default_rng(SEED)` PER FAMILY; this double-run originally
        # seeded rng2 once outside the family loop, so from the second family
        # onward it compared cells built from a different RNG stream position —
        # a harness artifact, not scientific nondeterminism. Reseed per family to
        # reproduce the main run's stream schedule exactly. Panel/prediction code
        # is untouched; rerun outcomes must reproduce run 1 (job 3544037).
        rerun_rows: list = []
        panel2 = {}
        for family in FAMILIES:
            rng2 = np.random.default_rng(SEED)
            cells = []
            for n in sorted(k for k in panel_sizes if k <= DETERMINISM_MAX_N):
                cells.append(
                    run_cell(family, n, panel_sizes[n], rng2, rerun_rows)
                )
            panel2[family] = cells
        receipt2 = dict(receipt)
        receipt2["panel"] = panel2
        projection_run2 = determinism_projection(receipt2, DETERMINISM_MAX_N)
        receipt["determinism"] = {
            "double_run_core_max_n": DETERMINISM_MAX_N,
            "projection_run1": projection_run1,
            "projection_run2": projection_run2,
            "equal": projection_run1 == projection_run2,
        }
        timing["panel_rows"].extend(
            {"rerun": True, **r} for r in rerun_rows
        )

        receipt["chemistry"] = run_chemistry(timing)
        receipt["fresh_subject"] = run_fresh_subject(timing)
        print("ORIONQ_Q1XOVER_CHEM_AND_FRESH_DONE", flush=True)

        outcomes = evaluate_predictions(receipt)
        receipt["prediction_outcomes"] = outcomes
        if all(outcomes.values()):
            receipt["verdict"] = "CROSSOVER_EVALUATION_CONFIRMED"
        elif any(
            k.startswith("P") and not v
            for k, v in outcomes.items()
            if k != "P6_feasibility_rule"
        ):
            receipt["verdict"] = "PREDICTION_REFUTED"
        else:
            receipt["verdict"] = "RUN_INCOMPLETE"
    else:
        receipt["verdict"] = "SMOKE_COMPLETE"
    receipt["claim_boundary"] = (
        "exact crossover/resource table for the frozen grammar only; no DP "
        "acceleration claim; active-core wall-clock losses are reported as "
        "losses; registered modules imported unmodified"
    )

    payload = canonical_json(receipt)
    with open(results_path, "x") as fh:
        fh.write(payload)
    timing_payload = canonical_json(timing)
    with open(timing_path, "x") as fh:
        fh.write(timing_payload)
    print(f"ORIONQ_Q1XOVER_VERDICT={receipt['verdict']}")
    print(f"ORIONQ_Q1XOVER_RESULTS={payload}")
    print(f"ORIONQ_Q1XOVER_RESULTS_SHA256={sha256_text(payload)}")
    print(f"ORIONQ_Q1XOVER_TIMING_SHA256={sha256_text(timing_payload)}")
    if draft_path.exists():
        draft_path.unlink()
    return receipt


if __name__ == "__main__":
    main()
