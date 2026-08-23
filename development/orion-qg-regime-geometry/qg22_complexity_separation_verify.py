import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
ORION_QG = REPO_ROOT / "research" / "extensions" / "orion-qg"
PROTOCOL_PATH = (
    REPO_ROOT / "development" / "orion-qg-regime-geometry"
    / "QG22_COMPLEXITY_SEPARATION_PROTOCOL_V1.md"
)
DEFAULT_INPUT = ORION_QG / "QG22_COMPLEXITY_SEPARATION_RESULTS.json"
DEFAULT_OUTPUT = (
    REPO_ROOT / "development" / "orion-qg-regime-geometry"
    / "QG22_GENERIC_VERIFICATION.json"
)
TOKEN_PREFIX = "ORIONQG_QG22_GENERIC_VERIFY="
SEED = 20260822

sys.path.insert(0, str(ORION_Q))
sys.path.insert(0, str(ORION_QG))

import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402


def canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------ own toolkit

def own_instance(n: int, rng) -> tuple:
    """Independent re-implementation of the frozen generator (protocol section 6)."""
    out = []
    for _ in range(6):
        while True:
            x = int(rng.integers(0, 2 ** n))
            z = int(rng.integers(0, 2 ** n))
            if x or z:
                break
        out.append((x, z))
    return tuple((out[2 * i], out[2 * i + 1]) for i in range(3))


def own_fit(xs, ys) -> dict[str, Any]:
    m = len(xs)
    mx = sum(xs) / m
    my = sum(ys) / m
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum(r * r for r in res)
    return {
        "slope": round(b, 4),
        "intercept": round(a, 4),
        "r_squared": round(1 - sse / sst, 6) if sst else None,
        "max_abs_residual": round(max(abs(r) for r in res), 4),
        "points": m,
    }


def own_semilog(pairs) -> dict[str, Any]:
    pts = [(n, v) for n, v in pairs if v and v > 0]
    return {
        "domain_n": [n for n, _ in pts],
        **own_fit([float(n) for n, _ in pts], [math.log10(v) for _, v in pts]),
    }


def own_loglog(pairs) -> dict[str, Any]:
    pts = [(n, v) for n, v in pairs if v and v > 0]
    return {
        "domain_n": [n for n, _ in pts],
        **own_fit([math.log10(n) for n, _ in pts], [math.log10(v) for _, v in pts]),
    }


def own_time(fn, repeats: int) -> float:
    best = math.inf
    for _ in range(repeats):
        r6m._local_table.cache_clear()
        r6o._block_cache.clear()
        r6p._dxx_tables.clear()
        t0 = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t0)
    return best


# ------------------------------------------------------- independent re-derivation

def own_naive_config_count(n: int) -> int:
    """Direct enumeration of the naive configuration space (small n only)."""
    keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n)]
    total = 0
    for s in keys:
        if s == (0, 0):
            continue
        for l0, l1 in ((0, 1), (1, 0)):
            cnt = 0
            for r0 in keys:
                if p10.symp(s, r0) != l0:
                    continue
                for r1 in keys:
                    if p10.symp(r0, r1) == 1 and p10.symp(s, r1) == l1:
                        cnt += 1
            total += cnt ** 3
    return 32 * total


def own_naive_closed_form(n: int) -> int:
    half = 4 ** n // 2
    quarter = 4 ** n // 4
    return 32 * (4 ** n - 1) * 2 * (half * quarter) ** 3


def own_stabprep(n: int) -> int:
    v = 2 ** n
    for k in range(1, n + 1):
        v *= 2 ** k + 1
    return v


def perfect_cube_root(x: int):
    if x <= 0:
        return None
    r = round(x ** (1.0 / 3.0))
    for cand in (r - 2, r - 1, r, r + 1, r + 2):
        if cand > 0 and cand ** 3 == x:
            return cand
    return None


def run(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    checks: dict[str, Any] = {}
    evidence: dict[str, Any] = {}

    # ---- digest reproduction (the lane appends 'measured' and 'timing' after
    # sealing the digest, per the R6P convention it declares).
    unsigned = {k: v for k, v in raw.items()
                if k not in ("result_digest", "measured", "timing",
                             "measured_fields_extracted_from_core")}
    checks["result_digest_reproduces"] = (
        raw.get("result_digest")
        == hashlib.sha256(canon(unsigned).encode()).hexdigest()
    )
    checks["protocol_sha256_matches_file"] = (
        raw.get("protocol_sha256") == sha256_file(PROTOCOL_PATH)
    )

    counts = {int(k): v for k, v in raw["q1_instrumented_counts"].items()}

    # ---- 1. R6L: 24n reps per block, 6n common Tag keys, 384n triples.
    r6l_rows = []
    r6l_ok = True
    for n in sorted(counts):
        row = counts[n]["r6l"]
        pred = {"reps_per_block": 24 * n, "common_tag_keys": 6 * n,
                "representation_triples": 384 * n}
        ok = all(int(row[k]) == v for k, v in pred.items())
        r6l_ok = r6l_ok and ok
        r6l_rows.append({"n": n, "observed": row, "predicted": pred, "ok": ok})
    checks["r6l_counting_reproduced"] = r6l_ok
    evidence["r6l"] = r6l_rows

    # ---- 2. D+: m = 12n, cells = 2 * (12n)^3 * (2n + 6).
    dplus_rows = []
    dplus_ok = True
    for n in sorted(counts):
        row = counts[n]["dplus"]
        pred_cells = 2 * (12 * n) ** 3 * (2 * n + 6)
        ok = row["m_per_block"] == [12 * n] and int(row["cells"]) == pred_cells
        dplus_ok = dplus_ok and ok
        dplus_rows.append({"n": n, "observed": row, "predicted_cells": pred_cells,
                           "ok": ok})
    checks["dplus_counting_reproduced"] = dplus_ok
    evidence["dplus"] = dplus_rows
    evidence["dplus_cell_exponent"] = own_loglog(
        [(n, counts[n]["dplus"]["cells"]) for n in sorted(counts)]
    )
    # cells = 2*(12n)^3*(2n+6): a degree-4 polynomial whose fitted log-log exponent
    # approaches 4 from below at these n because of the +6 term. Band, not point.
    checks["dplus_cell_exponent_in_band_3_to_4p3"] = (
        3.0 <= evidence["dplus_cell_exponent"]["slope"] <= 4.3
    )

    # ---- 3. DP: 32 * n * 2^18 transition cells, tables <= 32n, affine in n.
    dp_rows = []
    dp_ok = True
    for n in sorted(counts):
        row = counts[n]["dp"]
        pred = 32 * n * (2 ** 9) ** 2
        ok = (int(row["transition_cells"]) == pred
              and int(row["local_tables_built"]) <= 32 * n)
        dp_ok = dp_ok and ok
        dp_rows.append({"n": n, "observed": row, "predicted_transition_cells": pred,
                        "ok": ok})
    checks["dp_counting_reproduced"] = dp_ok
    evidence["dp"] = dp_rows
    evidence["dp_cell_exponent"] = own_loglog(
        [(n, counts[n]["dp"]["cells"]) for n in sorted(counts)]
    )
    checks["dp_cell_exponent_is_1"] = (
        abs(evidence["dp_cell_exponent"]["slope"] - 1.0) < 0.25
    )

    # ---- 4. borrow families: independent combinatorial prediction of the sweep
    # shape from regenerated instances, plus a polynomial-growth signature.
    rng_c = np.random.default_rng(SEED)
    regen = {}
    for n in sorted(counts):
        tp = own_instance(n, rng_c)
        union = 0
        supports = []
        for pair in tp:
            m = pair[0][0] | pair[0][1] | pair[1][0] | pair[1][1]
            supports.append(bin(m).count("1"))
            union |= m
        u = bin(union).count("1")
        regen[n] = {"union_support": u, "block_supports": supports}

    fam_ev = {}
    fam_ok = True
    for key in ("fb", "fbp", "fbpp"):
        rows = []
        ok_all = True
        for n in sorted(counts):
            row = counts[n][key]
            u = regen[n]["union_support"]
            sweeps = int(row["tag_sweeps"])
            if key in ("fb", "fbp"):
                tag_qubits = u + (1 if u < n else 0)
                pred_tag_qubits = int(row["tag_qubits"]) == tag_qubits
                pred_sweeps = 0 <= sweeps <= 3 * tag_qubits
                ok = pred_tag_qubits and pred_sweeps and (sweeps > 0) == (u >= 2)
                rows.append({"n": n, "union_support": u,
                             "observed_tag_qubits": int(row["tag_qubits"]),
                             "predicted_tag_qubits": tag_qubits,
                             "observed_sweeps": sweeps,
                             "sweeps_upper_bound": 3 * tag_qubits, "ok": ok})
            else:
                pool = u + min(2, n - u)
                pred_pool = int(row["pool"]) == pool
                upper = 9 * (pool * (pool - 1) // 2)
                ok = pred_pool and 0 <= sweeps <= upper and (sweeps > 0) == (pool >= 3)
                rows.append({"n": n, "union_support": u,
                             "observed_pool": int(row["pool"]),
                             "predicted_pool": pool,
                             "observed_sweeps": sweeps,
                             "sweeps_upper_bound": upper, "ok": ok})
            ok_all = ok_all and ok
        pairs = [(n, counts[n][key]["cells"]) for n in sorted(counts)]
        nz = [(n, v) for n, v in pairs if v > 0]
        log_ratios = [
            round(math.log10(nz[i + 1][1] / nz[i][1]), 4) for i in range(len(nz) - 1)
        ]
        ll = own_loglog(pairs)
        sl = own_semilog(pairs)
        fam_ev[key] = {
            "rows": rows,
            "cell_exponent": ll,
            "semilog_fit_exponential_model": sl,
            "successive_log10_ratios": log_ratios,
            "power_law_beats_exponential_model": (
                ll["r_squared"] is not None and sl["r_squared"] is not None
                and ll["r_squared"] > sl["r_squared"]
            ),
        }
        fam_ok = fam_ok and ok_all
    checks["borrow_sweep_shape_reproduced"] = fam_ok
    checks["borrow_growth_is_polynomial_not_exponential"] = all(
        fam_ev[k]["power_law_beats_exponential_model"]
        and fam_ev[k]["cell_exponent"]["r_squared"] is not None
        and fam_ev[k]["cell_exponent"]["r_squared"] > 0.97
        and fam_ev[k]["cell_exponent"]["slope"] < 9.0
        for k in ("fb", "fbp", "fbpp")
    )
    evidence["borrow_families"] = fam_ev
    evidence["regenerated_instances"] = {str(k): v for k, v in regen.items()}
    checks["fbpp_cell_exponent_exceeds_dp"] = (
        fam_ev["fbpp"]["cell_exponent"]["slope"]
        > evidence["dp_cell_exponent"]["slope"] + 3.0
    )

    # ---- 5. naive configuration space, independently enumerated and closed-form.
    naive = raw["q1_naive_referee"]
    own_enum = {n: own_naive_config_count(n) for n in (1, 2)}
    own_cf = {n: own_naive_closed_form(n) for n in (1, 2, 3, 4, 5, 6)}
    checks["naive_enumeration_reproduced"] = all(
        own_enum[n] == int(naive["enumerated"][str(n)]["configurations"]) for n in (1, 2)
    )
    checks["naive_closed_form_reproduced"] = all(
        own_cf[n] == int(naive["closed_form_projection"][str(n)]) for n in (1, 2, 3, 4, 5, 6)
    )
    # |Cfg(n)| = C * (4^n - 1) * 4^{6n}, so the successive ratio is
    # 4^6 * (4^{n+1} - 1)/(4^n - 1), which tends to 4^7 from ABOVE and is never
    # exactly 4^7 at finite n. Check the limit behaviour, not an exact equality.
    ratios = [own_cf[n + 1] / own_cf[n] for n in (2, 3, 4, 5)]
    checks["naive_growth_tends_to_4_to_the_7n"] = (
        all(r > 4 ** 7 for r in ratios)
        and all(ratios[i] > ratios[i + 1] for i in range(len(ratios) - 1))
        and abs(ratios[-1] / 4 ** 7 - 1.0) < 0.01
    )
    checks["naive_semilog_beats_powerlaw"] = (
        own_semilog([(n, own_cf[n]) for n in range(1, 7)])["r_squared"]
        > own_loglog([(n, own_cf[n]) for n in range(1, 7)])["r_squared"]
    )
    evidence["naive"] = {"own_enumeration": {str(k): v for k, v in own_enum.items()},
                         "own_closed_form": {str(k): v for k, v in own_cf.items()},
                         "successive_ratios": [round(r, 6) for r in ratios],
                         "A_pow_L": 4 ** 7}

    # ---- 6. StabPrep state space, independently computed.
    stab = raw["q2"]["q2d_located_candidate_family_without_a_conserved_syndrome"]
    own_stab = {n: own_stabprep(n) for n in range(1, 13)}
    checks["stabprep_state_space_reproduced"] = all(
        own_stab[n] == int(stab["state_space_counts"][str(n)]) for n in range(1, 13)
    )
    checks["stabprep_matches_qg15_counts"] = (
        own_stab[1] == 6 and own_stab[2] == 60 and own_stab[3] == 1080
        and own_stab[4] == 36720
    )
    evidence["stabprep"] = {"own_counts": {str(k): v for k, v in own_stab.items()}}

    # ---- 7. INDEPENDENT re-measurement (own ladder, own timing, own fit).
    rng = np.random.default_rng(SEED)
    ladder = (2, 3, 4, 6, 8, 12, 16)
    inst = {n: own_instance(n, rng) for n in ladder}
    dp_pts, dplus_pts = [], []
    for n in ladder:
        terms = r6m._synthetic_terms(inst[n])
        dp_pts.append((n, own_time(lambda t=terms, n=n:
                                   r6p.dp_cost_frozen_configs(t, n), 2)))
        dplus_pts.append((n, own_time(lambda tp=inst[n], n=n:
                                      r6o.dplus_pairs(tp, n), 2)))
    dp_fit = own_loglog(dp_pts)
    dplus_fit = own_loglog(dplus_pts)
    evidence["own_measurement"] = {
        "ladder_n": list(ladder),
        "repeats": 2,
        "dp_seconds": {str(n): round(v, 6) for n, v in dp_pts},
        "dplus_seconds": {str(n): round(v, 6) for n, v in dplus_pts},
        "dp_loglog_fit": dp_fit,
        "dplus_loglog_fit": dplus_fit,
    }
    checks["own_measurement_dp_is_subquadratic"] = dp_fit["slope"] < 1.5
    checks["own_measurement_dplus_is_superquadratic"] = dplus_fit["slope"] > 2.5
    checks["own_measurement_dp_cheaper_than_dplus"] = dp_fit["slope"] < dplus_fit["slope"]

    # ---- 8. independent agreement spot-check: C_DP == naive optimum at n in {1,2}.
    rng2 = np.random.default_rng(SEED + 1)
    spot = []
    spot_ok = True
    for n in (1, 2):
        for _ in range(6):
            tp = own_instance(n, rng2)
            terms = r6m._synthetic_terms(tp)
            r6m._local_table.cache_clear()
            c_dp = int(r6p.dp_cost_frozen_configs(terms, n))
            best = None
            for pb in (0, 1):
                for pc in (0, 1):
                    for ce in itertools.product((0, 1), repeat=3):
                        v = (r6m._brute_config_n1(tp, pb, pc, ce) if n == 1
                             else r6m._brute_config_n2(tp, pb, pc, ce))
                        if v is not None and (best is None or v < best):
                            best = v
            c_naive = int(best)
            ok = c_dp == c_naive
            spot_ok = spot_ok and ok
            spot.append({"n": n, "C_DP": c_dp, "C_naive": c_naive, "ok": ok})
    checks["dp_equals_naive_optimum_spotcheck"] = spot_ok
    evidence["dp_vs_naive_spotcheck"] = spot

    # ---- 9. honesty discipline of the receipt itself.
    text = canon(raw)
    banned = ("np-hard", "np hard", "np-complete", "#p-hard", "pspace-hard",
              "w[1]-hard", "exptime-hard")
    unguarded = []
    low = text.lower()
    for verb in banned:
        i = 0
        while True:
            j = low.find(verb, i)
            if j < 0:
                break
            win = low[max(0, j - 90): j + len(verb) + 40]
            if not any(m in win for m in ("no ", "not ", "never", "none", "cannot",
                                          "without a reduction", "forbidden")):
                unguarded.append(win)
            i = j + len(verb)
    checks["no_unguarded_hardness_verb"] = not unguarded
    checks["complexity_class_claim_is_none"] = raw.get("complexity_class_claim") == "none"
    checks["reduction_not_supplied_and_declared"] = (
        raw.get("reduction_supplied") is False and raw.get("lower_bound_supplied") is False
    )
    checks["authority_ceiling_not_r6"] = (
        raw.get("r6_authority") is False
        and raw.get("novelty_authority") is False
        and raw.get("novelty_credit") is False
        and raw.get("donor_novelty_credit") is False
        and raw.get("physical_quantum_advantage_claim") is False
    )
    checks["protected_and_chemistry_untouched"] = (
        raw.get("protected_subject_read") is False
        and raw.get("chemistry_sources_read") is False
        and raw.get("network_access") is False
        and raw.get("reserved_stretched_n2_accessed") is False
    )
    checks["every_complexity_statement_labelled"] = all(
        c.get("label") in ("PROVEN", "MEASURED", "CONJECTURE")
        for c in raw["q1_counting_arguments"]["checks"]
    )
    checks["lane_gates_all_true"] = all(raw.get("gates", {}).values())
    checks["closed_form_identity_holds_on_panel"] = (
        raw["agreement_panel"]["closed_form_identity_holds"] is True
        and raw["agreement_panel"]["mismatches_total"] == 0
    )
    checks["terminal_is_a_frozen_terminal"] = raw.get("terminal") in (
        "QG22_SEPARATION_ESTABLISHED",
        "QG22_NO_SEPARATION__CLASSIFICATION_COLLAPSES_THE_PROBLEM",
        "QG22_PARTIAL__HARDNESS_LOCATED_ELSEWHERE",
        "QG22_CANNOT_CHECK",
    )

    decision = "ACCEPT" if all(bool(v) for v in checks.values()) else "REJECT"
    return {
        "schema": "ORION.QG.QG22.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "failed_checks": [k for k, v in checks.items() if not v],
        "evidence": evidence,
        "source_result_digest": raw.get("result_digest"),
        "source_terminal": raw.get("terminal"),
        "check_design_notes": [
            ("Two CHECK FORMULATIONS in this verifier were revised after they misfired "
             "on correct data; the lane's numbers were not touched. (1) "
             "'naive_growth_is_4_to_the_7n' originally demanded the successive ratio "
             "equal 4^7 to 1e-6. That is provably false at finite n: the exact count is "
             "C*(4^n - 1)*4^{6n}, whose ratio is 4^6*(4^{n+1}-1)/(4^n-1), approaching "
             "4^7 from above. Replaced by the limit test now recorded. (2) "
             "'borrow_growth_is_polynomial_not_exponential' originally required the "
             "successive log-ratios to be monotonically decreasing; f_B's tag-qubit "
             "count jumps when the union support is smaller than n (the extra empty Tag "
             "representative), which breaks monotonicity without being exponential. "
             "Replaced by a model-comparison test: the power-law fit must explain the "
             "exact cell counts better than the exponential fit."),
            ("No check that tests the lane's counting arguments against an independent "
             "closed-form prediction (r6l, dplus, dp, naive closed form, StabPrep) was "
             "altered; those passed on the first execution."),
        ],
        "verifier_independence": (
            "This verifier imports the committed ORION-Q analyzers under study but shares "
            "no code with the lane script: its instance generator, timing loop, "
            "least-squares fit, configuration-space enumeration, StabPrep count and "
            "counting-argument formulas are written independently and compared against "
            "the lane's instrumented numbers."
        ),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "reduction_supplied": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run(Path(args.input))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(TOKEN_PREFIX + canon({"decision": result["decision"], "path": str(out)}))
    if result["failed_checks"]:
        print("FAILED: " + canon(result["failed_checks"]))
    return 0 if result["decision"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
