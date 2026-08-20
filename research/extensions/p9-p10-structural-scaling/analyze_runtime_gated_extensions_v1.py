from __future__ import annotations

import json
import math
import random
from pathlib import Path
from statistics import mean
from typing import Any

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
OUT = HERE / "results" / "RUNTIME_GATED_EXTENSION_ANALYSIS_V1.json"
BOOTSTRAP_N = 10_000


def load_optional(name: str) -> dict[str, Any] | None:
    path = INPUTS / name
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{name} must contain a JSON object")
    return value


def q(values: list[float], p: float) -> float:
    s = sorted(values)
    pos = (len(s) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return s[lo]
    w = pos - lo
    return s[lo] * (1 - w) + s[hi] * w


def interval(values: list[float]) -> list[float] | None:
    return None if not values else [q(values, 0.025), q(values, 0.975)]


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
        sampled = [names[rng.randrange(len(names))] for _ in names]
        vals: list[float] = []
        for name in sampled:
            vals.extend(blocks[name])
        out.append(mean(vals))
    return out


def green(value: Any) -> bool:
    if value is True:
        return True
    return isinstance(value, dict) and bool(value) and all(v is True for v in value.values())


def analyze_semantic_orbit(data: dict[str, Any]) -> dict[str, Any]:
    try:
        items = data["items"]
        if not items:
            raise ValueError("no semantic-orbit items")
        if not bool(data["same_information_equivalence_all_pass"]):
            raise ValueError("same-information equivalence not established")
        if not green(data.get("controls")):
            raise ValueError("hostile controls not all green")

        acc_effects: list[float] = []
        oir_adv_by_domain: dict[str, list[float]] = {}
        oir = {"R1": [], "R2": []}
        accuracy = {"R1": [], "R2": []}
        for item in items:
            domain = str(item["domain"])
            true = item["true_label"]
            arm_oir: dict[str, float] = {}
            arm_acc: dict[str, float] = {}
            for arm in ("R1_SAME_INFO", "R2_TYPED_STATE"):
                preds = item[arm]["orbit_predictions"]
                if len(preds) < 2:
                    raise ValueError("orbit must contain at least two transformations")
                counts: dict[str, int] = {}
                for pred in preds:
                    key = json.dumps(pred, sort_keys=True)
                    counts[key] = counts.get(key, 0) + 1
                local_oir = 1.0 - max(counts.values()) / len(preds)
                local_acc = mean(1.0 if pred == true else 0.0 for pred in preds)
                key = "R1" if arm.startswith("R1") else "R2"
                arm_oir[key] = local_oir
                arm_acc[key] = local_acc
                oir[key].append(local_oir)
                accuracy[key].append(local_acc)
            acc_effects.append(arm_acc["R2"] - arm_acc["R1"])
            oir_adv_by_domain.setdefault(domain, []).append(arm_oir["R1"] - arm_oir["R2"])

        mean_acc = {k: mean(v) for k, v in accuracy.items()}
        mean_oir = {k: mean(v) for k, v in oir.items()}
        acc_delta = mean(acc_effects)
        oir_adv = mean(v for vals in oir_adv_by_domain.values() for v in vals)
        oir_ci = interval(block_bootstrap(oir_adv_by_domain, 914041))
        checks = {
            "R2_accuracy_gt_R1": mean_acc["R2"] > mean_acc["R1"],
            "R2_mean_oir_lt_R1": mean_oir["R2"] < mean_oir["R1"],
            "domain_block_oir_advantage_lower_gt_zero": oir_ci is not None and oir_ci[0] > 0,
            "same_information_equivalence_all_pass": True,
            "controls_green": True,
        }
        terminal = "LLM_SEMANTIC_ORBIT_STABILITY_SUPPORTED" if all(checks.values()) else "LLM_SEMANTIC_ORBIT_GATE_NOT_MET"
        return {
            "terminal": terminal,
            "checks": checks,
            "mean_accuracy": mean_acc,
            "R2_minus_R1_accuracy": acc_delta,
            "mean_oir": mean_oir,
            "R1_minus_R2_oir": oir_adv,
            "oir_domain_block_bootstrap_95pct_interval": oir_ci,
        }
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_LLM_SEMANTIC_ORBIT_INPUT", "error": str(exc)}


def analyze_adaptive_compute(data: dict[str, Any]) -> dict[str, Any]:
    try:
        batches = data["batches"]
        if not batches:
            raise ValueError("no adaptive-compute batches")
        arms = ("UNIFORM", "FLAT_ALLOCATOR", "STRUCTURED_ALLOCATOR", "ORACLE")
        success = {arm: [] for arm in arms}
        equal_budget = True
        for batch in batches:
            totals = []
            for arm in arms:
                result = batch["results"][arm]
                success[arm].append(float(result["success_fraction"]))
                totals.append(int(result["total_budget_used"]))
            equal_budget = equal_budget and len(set(totals)) == 1 and totals[0] == int(batch["total_budget_cap"])
        means = {arm: mean(vals) for arm, vals in success.items()}
        paired = [s - f for s, f in zip(success["STRUCTURED_ALLOCATOR"], success["FLAT_ALLOCATOR"])]
        ci = interval(paired_bootstrap(paired, 914043))
        controls_green = bool(data.get("allocator_answer_blind")) and green(data.get("controls"))
        checks = {
            "equal_total_budget_every_batch": equal_budget,
            "structured_allocator_gt_flat_allocator": means["STRUCTURED_ALLOCATOR"] > means["FLAT_ALLOCATOR"],
            "paired_bootstrap_lower_gt_zero": ci is not None and ci[0] > 0,
            "structured_allocator_ge_uniform": means["STRUCTURED_ALLOCATOR"] >= means["UNIFORM"],
            "structured_allocator_not_above_oracle": means["STRUCTURED_ALLOCATOR"] <= means["ORACLE"] + 1e-15,
            "answer_blind_and_controls_green": controls_green,
        }
        terminal = "STRUCTURED_STATE_ADAPTIVE_COMPUTE_ALLOCATION_SUPPORTED" if all(checks.values()) else "ADAPTIVE_COMPUTE_ALLOCATION_GATE_NOT_MET"
        return {
            "terminal": terminal,
            "checks": checks,
            "mean_batch_success": means,
            "structured_minus_flat": mean(paired),
            "paired_bootstrap_95pct_interval": ci,
        }
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_ADAPTIVE_COMPUTE_INPUT", "error": str(exc)}


def analyze_cross_domain(data: dict[str, Any]) -> dict[str, Any]:
    try:
        p9 = data["P9_PROCEDURAL"]
        formal = data["FORMAL_DOMAIN"]
        for name, result in (("P9_PROCEDURAL", p9), ("FORMAL_DOMAIN", formal)):
            if not bool(result["same_information_control"]):
                raise ValueError(f"{name} lacks same-information control")
            if not green(result.get("controls")):
                raise ValueError(f"{name} controls not green")
            if float(result["structured_minus_same_info"]) <= 0:
                raise ValueError(f"{name} structural effect is not positive")
        p9_effect = float(p9["structured_minus_same_info"])
        formal_effect = float(formal["structured_minus_same_info"])
        checks = {
            "P9_positive_same_information_effect": p9_effect > 0,
            "formal_positive_same_information_effect": formal_effect > 0,
            "P9_claim_terminal_positive": str(p9["terminal"]).endswith("SUPPORTED") or "SUPPORTED" in str(p9["terminal"]),
            "formal_claim_terminal_positive": str(formal["terminal"]).endswith("SUPPORTED") or "SUPPORTED" in str(formal["terminal"]),
            "domains_frozen_independently": bool(data["domains_frozen_independently"]),
        }
        terminal = "CROSS_DOMAIN_STRUCTURAL_ACCESSIBILITY_SUPPORTED_BOUNDED" if all(checks.values()) else "CROSS_DOMAIN_STRUCTURAL_ACCESSIBILITY_GATE_NOT_MET"
        return {
            "terminal": terminal,
            "checks": checks,
            "effects": {"P9_PROCEDURAL": p9_effect, "FORMAL_DOMAIN": formal_effect},
            "heterogeneity": formal_effect - p9_effect,
            "claim_boundary": "Two-domain bounded composition only; no universal law or pooled-only rescue is permitted.",
        }
    except (KeyError, TypeError, ValueError) as exc:
        return {"terminal": "INVALID_CROSS_DOMAIN_INPUT", "error": str(exc)}


def main() -> None:
    specs = [
        ("C_llm_semantic_orbit", "P9_LLM_SEMANTIC_ORBIT_RUNS_V1.json", "CANNOT_CHECK_LLM_SEMANTIC_ORBIT_RUNTIME", analyze_semantic_orbit),
        ("D_adaptive_compute", "P9_ADAPTIVE_COMPUTE_RUNS_V1.json", "CANNOT_CHECK_MULTI_BUDGET_MODEL_RUNTIME", analyze_adaptive_compute),
        ("H_cross_domain_composition", "P9_P10_CROSS_DOMAIN_STRUCTURAL_RESULT_V1.json", "BLOCKED_PENDING_SECOND_DOMAIN_SAME_INFORMATION_RESULT", analyze_cross_domain),
    ]
    lanes: dict[str, Any] = {}
    for name, filename, missing, analyzer in specs:
        data = load_optional(filename)
        lanes[name] = {"terminal": missing, "input": f"inputs/{filename}"} if data is None else analyzer(data)
    result = {
        "schema": "P9P10.RuntimeGatedExtensionAnalysis.v1",
        "lanes": lanes,
        "bootstrap_resamples": BOOTSTRAP_N,
        "policy": "Missing inputs are CANNOT_CHECK/BLOCKED; malformed inputs are INVALID; no missing or invalid state is positive evidence.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
