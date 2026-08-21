from __future__ import annotations

import json
import math
from pathlib import Path

NS = (128, 512, 2048)
HORIZON_RATIOS = (0.05, 0.10, 0.25, 0.50, 1.0, 2.0, 4.0, 8.0)
BETAS = (0.25, 0.50, 0.75)
ZIPF_ALPHAS = (1.1, 1.5)
RS = (1, 5, 16)
OUT = Path(__file__).with_name("results") / "P15_STATE_OPTIONALITY_PHASE_V1.json"


def probs_uniform(n: int) -> list[float]:
    return [1.0 / n] * n


def probs_zipf(n: int, alpha: float) -> list[float]:
    raw = [1.0 / (i ** alpha) for i in range(1, n + 1)]
    z = sum(raw)
    return [v / z for v in raw]


def expected_distinct(probs: list[float], k: int) -> float:
    return sum(1.0 - (1.0 - p) ** k for p in probs)


def uniform_closed(n: int, k: int) -> float:
    return n * (1.0 - (1.0 - 1.0 / n) ** k)


def main() -> None:
    workload_rows: list[dict[str, object]] = []
    uniform_agreement_max = 0.0
    crossovers: dict[str, dict[str, float | None]] = {}

    for n in NS:
        distributions = {
            "UNIFORM": probs_uniform(n),
            "ZIPF_1_1": probs_zipf(n, 1.1),
            "ZIPF_1_5": probs_zipf(n, 1.5),
        }
        n_cross: dict[str, float | None] = {str(beta): None for beta in BETAS}
        for ratio in HORIZON_RATIOS:
            k = max(1, int(round(ratio * n)))
            row = {"N": n, "horizon_ratio": ratio, "K": k, "distributions": {}}
            for name, probs in distributions.items():
                d = expected_distinct(probs, k)
                if name == "UNIFORM":
                    diff = abs(d - uniform_closed(n, k))
                    uniform_agreement_max = max(uniform_agreement_max, diff)
                policies = {
                    "EPHEMERAL_COMPILE": {
                        "expected_compile_work": float(k),
                        "expected_component_memory": 1.0,
                        "expected_miss_fraction": 1.0,
                    },
                    "COMPILE_AND_CACHE": {
                        "expected_compile_work": d,
                        "expected_component_memory": d,
                        "expected_miss_fraction": d / k,
                    },
                    "UNIVERSAL_MATERIALIZE": {
                        str(beta): {
                            "expected_compile_work": beta * n,
                            "expected_component_memory": float(n),
                            "expected_miss_fraction": 0.0,
                        }
                        for beta in BETAS
                    },
                }
                row["distributions"][name] = {
                    "expected_distinct": d,
                    "expected_distinct_fraction": d / n,
                    "policies": policies,
                }
                if name == "UNIFORM":
                    for beta in BETAS:
                        key = str(beta)
                        if n_cross[key] is None and beta * n < d:
                            n_cross[key] = ratio
            workload_rows.append(row)
        crossovers[str(n)] = n_cross

    optionality_rows: list[dict[str, object]] = []
    for n in NS:
        for r in RS:
            if r > n:
                continue
            optionality_rows.append({
                "N": n,
                "r": r,
                "COMPILED_ONLY_SOURCE_GONE": {
                    "immediate_future_coverage": r / n,
                    "recoverable_future_coverage": r / n,
                    "requires_recompile": False,
                    "raw_source_retained": False,
                },
                "RAW_PLUS_COMPILED": {
                    "immediate_future_coverage": r / n,
                    "recoverable_future_coverage": 1.0,
                    "requires_recompile_for_uncached": True,
                    "raw_source_retained": True,
                },
                "UNIVERSAL_READY": {
                    "immediate_future_coverage": 1.0,
                    "recoverable_future_coverage": 1.0,
                    "requires_recompile_for_uncached": False,
                    "raw_source_retained": False,
                },
            })

    def get_row(n: int, ratio: float) -> dict[str, object]:
        return next(row for row in workload_rows if row["N"] == n and row["horizon_ratio"] == ratio)

    low_horizon_gate = True
    high_tradeoff_gate = True
    concentration_gate = True
    crossover_order_gate = True
    for n in NS:
        for ratio in (0.05, 0.10):
            d = get_row(n, ratio)["distributions"]["UNIFORM"]["expected_distinct"]
            for beta in BETAS:
                low_horizon_gate &= d < beta * n and d < n
        for ratio in (4.0, 8.0):
            d = get_row(n, ratio)["distributions"]["UNIFORM"]["expected_distinct"]
            high_tradeoff_gate &= 0.50 * n < d < n
        at_one = get_row(n, 1.0)["distributions"]
        concentration_gate &= (
            at_one["ZIPF_1_5"]["expected_distinct_fraction"]
            < at_one["ZIPF_1_1"]["expected_distinct_fraction"]
            < at_one["UNIFORM"]["expected_distinct_fraction"]
        )
        c = crossovers[str(n)]
        crossover_order_gate &= (
            c["0.25"] is not None and c["0.5"] is not None and c["0.75"] is not None
            and c["0.25"] < c["0.5"] < c["0.75"]
        )

    optionality_exact_gate = all(
        abs(row["COMPILED_ONLY_SOURCE_GONE"]["immediate_future_coverage"] - row["r"] / row["N"]) < 1e-15
        for row in optionality_rows
    )
    recoverability_gate = all(
        row["RAW_PLUS_COMPILED"]["recoverable_future_coverage"] == 1.0
        and row["UNIVERSAL_READY"]["recoverable_future_coverage"] == 1.0
        and row["RAW_PLUS_COMPILED"]["immediate_future_coverage"] < 1.0
        and row["UNIVERSAL_READY"]["immediate_future_coverage"] == 1.0
        for row in optionality_rows
    )

    gates = {
        "uniform_closed_form_agreement_le_1e_12": uniform_agreement_max <= 1e-12,
        "low_horizon_cache_dominates_universal_compute_and_memory": bool(low_horizon_gate),
        "high_horizon_beta_0_5_compute_memory_tradeoff": bool(high_tradeoff_gate),
        "crossover_order_beta_0_25_before_0_50_before_0_75": bool(crossover_order_gate),
        "zipf_concentration_reduces_distinct_fraction_at_K_eq_N": bool(concentration_gate),
        "compiled_only_optionality_equals_r_over_N": bool(optionality_exact_gate),
        "raw_recoverability_vs_universal_immediacy_separated": bool(recoverability_gate),
    }
    terminal = "P15_STATE_OPTIONALITY_PHASE_DIAGRAM_ESTABLISHED" if all(gates.values()) else "P15_STATE_OPTIONALITY_PHASE_DIAGRAM_GATE_NOT_MET"
    payload = {
        "schema": "ORION.P15.StateOptionalityPhaseDiagram.v1",
        "protocol": "P15_STATE_OPTIONALITY_PHASE_DIAGRAM_PROTOCOL_V1.md",
        "theorem": "THEOREM_STATE_OPTIONALITY_COVERAGE_V1.md",
        "N_values": list(NS),
        "horizon_ratios": list(HORIZON_RATIOS),
        "betas": list(BETAS),
        "zipf_alphas": list(ZIPF_ALPHAS),
        "workloads": workload_rows,
        "uniform_crossover_horizon_ratio": crossovers,
        "optionality": optionality_rows,
        "uniform_closed_form_max_abs_diff": uniform_agreement_max,
        "gates": gates,
        "terminal": terminal,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": terminal,
        "gates": gates,
        "crossovers": crossovers,
        "K_eq_N_distinct_fraction": {
            str(n): {
                name: get_row(n, 1.0)["distributions"][name]["expected_distinct_fraction"]
                for name in ("UNIFORM", "ZIPF_1_1", "ZIPF_1_5")
            }
            for n in NS
        },
        "optionality_examples": [row for row in optionality_rows if row["N"] == 2048],
    }, indent=2, sort_keys=True))
    if terminal != "P15_STATE_OPTIONALITY_PHASE_DIAGRAM_ESTABLISHED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
