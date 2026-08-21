from __future__ import annotations

import json
import math
import random
from pathlib import Path
from statistics import mean
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
OUT = HERE / "results" / "RUNTIME_GATED_NOVELTY_ANALYSIS_V1.json"
BOOTSTRAP_N = 10_000


def load_optional(name: str) -> dict[str, Any] | None:
    path = INPUTS / name
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{name} must contain a JSON object")
    return value


def quantile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    w = pos - lo
    return ordered[lo] * (1 - w) + ordered[hi] * w


def paired_bootstrap(values: list[float], seed: int) -> list[float]:
    if not values:
        return []
    rng = random.Random(seed)
    n = len(values)
    return [mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(BOOTSTRAP_N)]


def block_bootstrap(blocks: dict[str, list[float]], seed: int) -> list[float]:
    names = sorted(blocks)
    if not names:
        return []
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(BOOTSTRAP_N):
        chosen = [names[rng.randrange(len(names))] for _ in names]
        values: list[float] = []
        for name in chosen:
            values.extend(blocks[name])
        out.append(mean(values))
    return out


def interval(samples: list[float]) -> list[float] | None:
    if not samples:
        return None
    return [quantile(samples, 0.025), quantile(samples, 0.975)]


def all_green(controls: Any) -> bool:
    if controls is True:
        return True
    if not isinstance(controls, dict) or not controls:
        return False
    return all(v is True for v in controls.values())


def analyze_llm(data: dict[str, Any]) -> dict[str, Any]:
    try:
        models = sorted(data["models"], key=lambda x: int(x["parameters"]))
        if len(models) < 3 or len({m["id"] for m in models}) != len(models):
            raise ValueError("need at least three unique model checkpoints")
        if any(int(b["parameters"]) <= int(a["parameters"]) for a, b in zip(models[:-1], models[1:])):
            raise ValueError("parameter counts must be strictly increasing")
        budgets = sorted({int(v) for v in data["budgets"]})
        primary_budget = int(data["primary_budget"])
        if primary_budget not in budgets:
            raise ValueError("primary budget not in budget grid")
        targets = [float(v) for v in data["target_qualities"]]
        if any(v not in {0.50, 0.70, 0.85} for v in targets):
            raise ValueError("target qualities outside frozen set")
        items = data["items"]
        if not items:
            raise ValueError("no items")

        # Build a complete cell map: model,budget,representation -> item rows.
        by_cell: dict[tuple[str, int, str], dict[str, dict[str, Any]]] = {}
        domains_by_item: dict[str, str] = {}
        for item in items:
            iid = str(item["item_id"])
            domain = str(item["domain"])
            domains_by_item[iid] = domain
            for result in item["results"]:
                key = (str(result["model_id"]), int(result["budget"]), str(result["representation"]))
                by_cell.setdefault(key, {})[iid] = result

        model_ids = [str(m["id"]) for m in models]
        item_ids = sorted(domains_by_item)
        for mid in model_ids:
            for budget in budgets:
                for rep in ("R1_SAME_INFO", "R2_TYPED_STATE"):
                    rows = by_cell.get((mid, budget, rep), {})
                    if sorted(rows) != item_ids:
                        raise ValueError(f"incomplete paired cell {(mid, budget,rep)}")

        cell_accuracy: dict[str, Any] = {}
        primary_positive_all = True
        for mid in model_ids:
            cell_accuracy[mid] = {}
            for budget in budgets:
                r1 = by_cell[(mid, budget, "R1_SAME_INFO")]
                r2 = by_cell[(mid, budget, "R2_TYPED_STATE")]
                a1 = mean(1.0 if r1[i]["correct"] else 0.0 for i in item_ids)
                a2 = mean(1.0 if r2[i]["correct"] else 0.0 for i in item_ids)
                cell_accuracy[mid][str(budget)] = {"R1": a1, "R2": a2, "delta": a2 - a1}
                if budget == primary_budget and not a2 - a1 > 0:
                    primary_positive_all = False

        largest = model_ids[-1]
        r1 = by_cell[(largest, primary_budget, "R1_SAME_INFO")]
        r2 = by_cell[(largest, primary_budget, "R2_TYPED_STATE")]
        effects_by_domain: dict[str, list[float]] = {}
        for iid in item_ids:
            effect = (1.0 if r2[iid]["correct"] else 0.0) - (1.0 if r1[iid]["correct"] else 0.0)
            effects_by_domain.setdefault(domains_by_item[iid], []).append(effect)
        bs = block_bootstrap(effects_by_domain, 914031)
        ci = interval(bs)
        domain_means = {d: mean(v) for d, v in effects_by_domain.items()}
        nonnegative_fraction = mean(1.0 if v >= 0 else 0.0 for v in domain_means.values())

        substitutions: list[dict[str, Any]] = []
        for q in targets:
            for budget in budgets:
                for i, small in enumerate(model_ids[:-1]):
                    for large in model_ids[i + 1 :]:
                        small_r2 = cell_accuracy[small][str(budget)]["R2"]
                        large_r1 = cell_accuracy[large][str(budget)]["R1"]
                        if small_r2 >= q and large_r1 >= q and small_r2 >= large_r1:
                            substitutions.append({"q": q, "budget": budget, "smaller_R2": small, "larger_R1": large, "smaller_R2_accuracy": small_r2, "larger_R1_accuracy": large_r1})

        compute_substitutions: list[dict[str, Any]] = []
        for mid in model_ids:
            for q in targets:
                minima: dict[str, int | None] = {}
                for rep_key, rep_name in (("R1", "R1_SAME_INFO"), ("R2", "R2_TYPED_STATE")):
                    hit = None
                    for budget in budgets:
                        if cell_accuracy[mid][str(budget)][rep_key] >= q:
                            hit = budget
                            break
                    minima[rep_name] = hit
                if minima["R1_SAME_INFO"] is not None and minima["R2_TYPED_STATE"] is not None and minima["R2_TYPED_STATE"] < minima["R1_SAME_INFO"]:
                    compute_substitutions.append({"model": mid, "q": q, "R1_budget": minima["R1_SAME_INFO"], "R2_budget": minima["R2_TYPED_STATE"]})

        controls_green = all_green(data.get("controls")) and bool(data.get("semantic_equivalence_all_pass"))
        checks = {
            "primary_delta_positive_every_model": primary_positive_all,
            "largest_model_domain_bootstrap_lower_gt_zero": ci is not None and ci[0] > 0,
            "domain_nonnegative_fraction_ge_0_60": nonnegative_fraction >= 0.60,
            "on_grid_model_substitution_exists": bool(substitutions),
            "all_equivalence_and_hostile_controls_green": controls_green,
        }
        terminal = "LLM_STRUCTURE_SCALING_FRONTIER_SUPPORTED" if all(checks.values()) else "LLM_STRUCTURE_SCALING_GATE_NOT_MET"
        return {"terminal": terminal, "checks": checks, "cell_accuracy": cell_accuracy, "largest_model_primary_domain_effects": domain_means, "bootstrap_95pct_interval": ci, "nonnegative_domain_fraction": nonnegative_fraction, "model_substitutions": substitutions, "compute_substitutions": compute_substitutions}
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_LLM_SCALING_INPUT", "error": str(exc)}


def analyze_native(data: dict[str, Any]) -> dict[str, Any]:
    try:
        rows = data["rows"]
        if not rows:
            raise ValueError("no transition rows")
        coverage = float(data["eligibility_coverage"])
        effects_by_module: dict[str, list[float]] = {}
        losses = {"B1": [], "B4": []}
        correct = {"B1": 0, "B4": 0}
        for row in rows:
            module = str(row["module"])
            effect = (1.0 if row["B4"]["predicted_action"] == row["true_action"] else 0.0) - (1.0 if row["B1"]["predicted_action"] == row["true_action"] else 0.0)
            effects_by_module.setdefault(module, []).append(effect)
            for arm in ("B1", "B4"):
                correct[arm] += int(row[arm]["predicted_action"] == row["true_action"])
                p = max(float(row[arm]["p_true"]), 1e-15)
                losses[arm].append(-math.log(p))
        n = len(rows)
        acc = {arm: correct[arm] / n for arm in correct}
        logloss = {arm: mean(losses[arm]) for arm in losses}
        delta = acc["B4"] - acc["B1"]
        module_means = {m: mean(v) for m, v in effects_by_module.items()}
        nonnegative_fraction = mean(1.0 if v >= 0 else 0.0 for v in module_means.values())
        ci = interval(block_bootstrap(effects_by_module, 914033))
        controls_green = all_green(data.get("controls"))
        checks = {
            "B4_minus_B1_accuracy_positive": delta > 0,
            "module_bootstrap_lower_gt_zero": ci is not None and ci[0] > 0,
            "nonnegative_module_fraction_ge_0_60": nonnegative_fraction >= 0.60,
            "B4_logloss_lower_than_B1": logloss["B4"] < logloss["B1"],
            "controls_green": controls_green,
            "eligibility_coverage_ge_0_80": coverage >= 0.80,
        }
        terminal = "P10_NATIVE_STATE_INCREMENTAL_VALUE_SUPPORTED" if all(checks.values()) else "P10_NATIVE_STATE_INCREMENTAL_VALUE_GATE_NOT_MET"
        return {"terminal": terminal, "checks": checks, "coverage": coverage, "accuracy": acc, "B4_minus_B1_accuracy": delta, "log_loss": logloss, "module_effects": module_means, "bootstrap_95pct_interval": ci, "nonnegative_module_fraction": nonnegative_fraction}
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_P10_NATIVE_STATE_INPUT", "error": str(exc)}


def analyze_abstraction(data: dict[str, Any]) -> dict[str, Any]:
    try:
        theorems = data["theorems"]
        if not theorems:
            raise ValueError("no theorem rows")
        executable = [str(v) for v in data["executable_arms"]]
        for required in ("A0_ATOMIC", "A1_RAW_TACTIC", "A2_COARSE_FAMILY", "A3_EFFECT_GROUNDED"):
            if required not in executable:
                raise ValueError(f"missing required arm {required}")
        rates: dict[str, float] = {}
        receipts_green = True
        for arm in executable:
            vals = []
            for theorem in theorems:
                result = theorem["results"][arm]
                vals.append(1.0 if result["solved"] else 0.0)
                receipts_green = receipts_green and bool(result["receipt_valid"])
            rates[arm] = mean(vals)
        intermediate = max(("A2_COARSE_FAMILY", "A3_EFFECT_GROUNDED"), key=lambda a: (rates[a], a))
        baseline = max(("A0_ATOMIC", "A1_RAW_TACTIC"), key=lambda a: (rates[a], a))
        paired = [
            (1.0 if t["results"][intermediate]["solved"] else 0.0) - (1.0 if t["results"][baseline]["solved"] else 0.0)
            for t in theorems
        ]
        ci = interval(paired_bootstrap(paired, 914035))
        maximum_rate = max(rates.values())
        macro_exec = "A4_MACRO" in executable
        checks = {
            "intermediate_highest_allowing_tie": rates[intermediate] >= maximum_rate - 1e-15,
            "intermediate_beats_A0_and_A1": rates[intermediate] > rates["A0_ATOMIC"] and rates[intermediate] > rates["A1_RAW_TACTIC"],
            "paired_bootstrap_lower_gt_zero": ci is not None and ci[0] > 0,
            "common_verifier_call_cap": bool(data["common_verifier_call_cap"]),
            "macro_noninferiority_if_executable": (not macro_exec) or rates[intermediate] >= rates["A4_MACRO"] - 0.01,
            "all_receipts_valid": receipts_green,
        }
        if all(checks.values()):
            terminal = "INTERMEDIATE_ACTION_ABSTRACTION_FRONTIER_SUPPORTED" if macro_exec else "BOUNDED_INTERMEDIATE_FRONTIER_WITHOUT_MACRO_BASELINE"
        else:
            terminal = "ACTION_ABSTRACTION_FRONTIER_GATE_NOT_MET"
        return {"terminal": terminal, "checks": checks, "solve_rates": rates, "selected_intermediate": intermediate, "comparison_baseline": baseline, "paired_delta": mean(paired), "bootstrap_95pct_interval": ci, "macro_executable": macro_exec}
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_P10_ACTION_ABSTRACTION_INPUT", "error": str(exc)}


def analyze_feedback(data: dict[str, Any]) -> dict[str, Any]:
    try:
        items = data["items"]
        if not items:
            raise ValueError("no repair items")
        equivalence = all(bool(item["F1_F2_equivalence_pass"]) for item in items)
        rates: dict[str, float] = {}
        receipts_green = True
        for arm in ("F0_RAW", "F1_CANONICAL_TEXT", "F2_TYPED_DELTA", "F3_DEPENDENCY_DELTA"):
            vals = []
            for item in items:
                result = item["results"][arm]
                vals.append(1.0 if result["verified_success"] else 0.0)
                receipts_green = receipts_green and bool(result["final_receipt_valid"])
            rates[arm] = mean(vals)
        paired = [
            (1.0 if item["results"]["F2_TYPED_DELTA"]["verified_success"] else 0.0)
            - (1.0 if item["results"]["F1_CANONICAL_TEXT"]["verified_success"] else 0.0)
            for item in items
        ]
        ci = interval(paired_bootstrap(paired, 914037))
        checks = {
            "F1_F2_equivalence_all_pass": equivalence,
            "F2_success_gt_F1": rates["F2_TYPED_DELTA"] > rates["F1_CANONICAL_TEXT"],
            "paired_bootstrap_lower_gt_zero": ci is not None and ci[0] > 0,
            "budgets_equal": bool(data["budgets_equal"]),
            "all_final_receipts_valid": receipts_green,
        }
        terminal = "TYPED_LEAN_FEEDBACK_ACCESSIBILITY_SUPPORTED" if all(checks.values()) else "TYPED_LEAN_FEEDBACK_GATE_NOT_MET"
        return {"terminal": terminal, "checks": checks, "success_rates": rates, "F2_minus_F1": mean(paired), "bootstrap_95pct_interval": ci}
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_P10_LEAN_FEEDBACK_INPUT", "error": str(exc)}


def analyze_cross_revision(data: dict[str, Any]) -> dict[str, Any]:
    try:
        source = data["source_revision"]
        target = data["target_revision"]
        rows = target["rows"]
        if not rows:
            raise ValueError("no target revision rows")
        effects_by_block: dict[str, list[float]] = {}
        b1_correct = b4_correct = 0
        receipts_green = True
        for row in rows:
            b1 = bool(row["B1_correct"])
            b4 = bool(row["B4_correct"])
            b1_correct += int(b1)
            b4_correct += int(b4)
            effects_by_block.setdefault(str(row["block"]), []).append(float(int(b4) - int(b1)))
            receipts_green = receipts_green and bool(row["receipt_valid"])
        n = len(rows)
        target_b1 = b1_correct / n
        target_b4 = b4_correct / n
        source_b1 = float(source["B1_accuracy"])
        source_b4 = float(source["B4_accuracy"])
        degradation = {"B1": source_b1 - target_b1, "B4": source_b4 - target_b4}
        ci = interval(block_bootstrap(effects_by_block, 914039))
        checks = {
            "coverage_ge_0_80": float(target["eligibility_coverage"]) >= 0.80,
            "target_B4_gt_B1": target_b4 > target_b1,
            "B4_degradation_smaller": degradation["B4"] < degradation["B1"],
            "target_block_bootstrap_lower_gt_zero": ci is not None and ci[0] > 0,
            "no_target_refitting": bool(data["no_target_refitting"]),
            "all_receipts_valid": receipts_green and all_green(data.get("controls")),
        }
        terminal = "STRUCTURAL_COORDINATES_CROSS_REVISION_ROBUSTNESS_SUPPORTED" if all(checks.values()) else "STRUCTURAL_COORDINATES_CROSS_REVISION_GATE_NOT_MET"
        return {"terminal": terminal, "checks": checks, "source_accuracy": {"B1": source_b1, "B4": source_b4}, "target_accuracy": {"B1": target_b1, "B4": target_b4}, "degradation": degradation, "target_B4_minus_B1": target_b4 - target_b1, "bootstrap_95pct_interval": ci}
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_P10_CROSS_REVISION_INPUT", "error": str(exc)}


def dispatch(name: str, filename: str, missing_terminal: str, analyzer: Callable[[dict[str, Any]], dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    data = load_optional(filename)
    if data is None:
        return name, {"terminal": missing_terminal, "input": f"inputs/{filename}"}
    return name, analyzer(data)


def main() -> None:
    lanes = dict([
        dispatch("L_llm_structure_scaling", "P9_LLM_STRUCTURE_SCALING_RUNS_V1.json", "CANNOT_CHECK_LLM_RUNTIME", analyze_llm),
        dispatch("N_p10_native_state", "P10_NATIVE_STATE_PREDICTIONS_V1.json", "CANNOT_CHECK_NATIVE_STATE_EXECUTION", analyze_native),
        dispatch("A_p10_action_abstraction", "P10_ACTION_ABSTRACTION_SEARCH_V1.json", "CANNOT_CHECK_NATIVE_RAW_TRACE_CORPUS", analyze_abstraction),
        dispatch("F_p10_lean_feedback", "P10_LEAN_FEEDBACK_REPAIR_V1.json", "CANNOT_CHECK_LEAN_REPAIR_RUNTIME", analyze_feedback),
        dispatch("G_p10_cross_revision", "P10_CROSS_REVISION_TRANSFER_V1.json", "CANNOT_CHECK_SECOND_FROZEN_MATHLIB_REVISION", analyze_cross_revision),
    ])
    result = {
        "schema": "P9P10.RuntimeGatedNoveltyAnalysis.v1",
        "contract": "RUNTIME_GATED_ANALYSIS_CONTRACT_V1.md",
        "bootstrap_resamples": BOOTSTRAP_N,
        "lanes": lanes,
        "policy": "Missing inputs are CANNOT_CHECK, malformed inputs are INVALID, and neither state is positive evidence.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
