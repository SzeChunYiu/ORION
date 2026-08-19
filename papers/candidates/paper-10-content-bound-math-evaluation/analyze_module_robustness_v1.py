from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "results" / "MATHLIB_TRANSFER_V2_1.json"
OUT = HERE / "results" / "MATHLIB_TRANSFER_V2_1_MODULE_ROBUSTNESS.json"

EXPECTED_POOLED_DELTA = 0.1046


def sign_test_two_sided(positive: int, negative: int) -> float:
    n = positive + negative
    if n == 0:
        return 1.0
    x = min(positive, negative)
    tail = sum(math.comb(n, i) for i in range(x + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def quantile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lo = math.floor(position)
    hi = math.ceil(position)
    if lo == hi:
        return ordered[lo]
    w = position - lo
    return ordered[lo] * (1.0 - w) + ordered[hi] * w


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    module = data["leave_top_module_out"]
    per_block = module["per_block"]
    if not isinstance(per_block, list) or not per_block:
        raise SystemExit("V2.1 result has no held-out-module block receipts")

    # The corpus has 31 active top-level labels, but the frozen result emits
    # block receipts only for labels with evaluable recognized transitions.
    # The current immutable artifact has 28 such receipts.  Robustness is
    # therefore defined on the exact emitted/evaluable block population rather
    # than silently manufacturing zero-transition blocks for the other labels.
    rows: list[dict[str, Any]] = []
    skipped_zero_transition_blocks: list[str] = []
    for item in per_block:
        transitions = int(item["transitions"])
        if transitions <= 0:
            skipped_zero_transition_blocks.append(str(item["held_out"]))
            continue
        markov_correct = int(item["markov_correct"])
        unigram_correct = int(item["unigram_correct"])
        rows.append(
            {
                "held_out": item["held_out"],
                "held_out_trajectories": int(item["held_out_trajectories"]),
                "transitions": transitions,
                "markov_accuracy": markov_correct / transitions,
                "unigram_accuracy": unigram_correct / transitions,
                "markov_minus_unigram": (markov_correct - unigram_correct) / transitions,
                "improvement_correct_count": markov_correct - unigram_correct,
                "bigram_coverage": item["coverage"]["2"]["coverage"],
                "trigram_coverage": item["coverage"]["3"]["coverage"],
            }
        )
    if not rows:
        raise SystemExit("V2.1 result has no positive-transition held-out-module blocks")

    deltas = [float(row["markov_minus_unigram"]) for row in rows]
    positive = sum(delta > 0 for delta in deltas)
    negative = sum(delta < 0 for delta in deltas)
    zero = sum(delta == 0 for delta in deltas)

    total_transitions = sum(int(row["transitions"]) for row in rows)
    total_improvement = sum(int(row["improvement_correct_count"]) for row in rows)
    pooled_delta = total_improvement / total_transitions
    recorded_delta = float(module["markov_minus_unigram"])
    if not math.isclose(pooled_delta, recorded_delta, abs_tol=1e-15, rel_tol=0.0):
        raise SystemExit(f"recomputed pooled delta mismatch: {pooled_delta} vs {recorded_delta}")
    if not math.isclose(round(pooled_delta, 4), EXPECTED_POOLED_DELTA, abs_tol=1e-12, rel_tol=0.0):
        raise SystemExit(f"unexpected frozen headline delta: {pooled_delta}")

    leave_one_out: list[dict[str, Any]] = []
    for row in rows:
        remaining_transitions = total_transitions - int(row["transitions"])
        remaining_improvement = total_improvement - int(row["improvement_correct_count"])
        if remaining_transitions <= 0:
            raise SystemExit("single module unexpectedly contains all transitions")
        leave_one_out.append(
            {
                "removed_module": row["held_out"],
                "pooled_delta_without_module": remaining_improvement / remaining_transitions,
            }
        )

    ranked = sorted(rows, key=lambda row: (float(row["markov_minus_unigram"]), str(row["held_out"])))
    loo_ranked = sorted(leave_one_out, key=lambda row: (float(row["pooled_delta_without_module"]), str(row["removed_module"])))

    positive_contributions = sorted(
        (max(0, int(row["improvement_correct_count"])) for row in rows), reverse=True
    )
    positive_total = sum(positive_contributions)
    top_k = max(1, math.ceil(0.20 * len(rows)))
    top_20_share = (
        sum(positive_contributions[:top_k]) / positive_total if positive_total else None
    )

    artifact = {
        "schema": "P10.MathlibTransferModuleRobustness.v1.1",
        "analysis_status": "POST_HOC_DERIVED_FROM_FROZEN_V2_1_BLOCK_RECEIPTS",
        "source": str(SOURCE.relative_to(HERE)),
        "emitted_block_receipts": len(per_block),
        "evaluable_held_out_modules": len(rows),
        "skipped_zero_transition_blocks": skipped_zero_transition_blocks,
        "total_transitions": total_transitions,
        "pooled_markov_minus_unigram": pooled_delta,
        "module_delta_distribution": {
            "positive_modules": positive,
            "zero_modules": zero,
            "negative_modules": negative,
            "positive_fraction": positive / len(rows),
            "nonnegative_fraction": (positive + zero) / len(rows),
            "sign_test_two_sided_p": sign_test_two_sided(positive, negative),
            "unweighted_mean": statistics.mean(deltas),
            "median": statistics.median(deltas),
            "q25": quantile(deltas, 0.25),
            "q75": quantile(deltas, 0.75),
            "minimum": min(deltas),
            "maximum": max(deltas),
        },
        "leave_one_module_out_sensitivity": {
            "minimum_pooled_delta": float(loo_ranked[0]["pooled_delta_without_module"]),
            "minimum_when_removed": loo_ranked[0]["removed_module"],
            "maximum_pooled_delta": float(loo_ranked[-1]["pooled_delta_without_module"]),
            "maximum_when_removed": loo_ranked[-1]["removed_module"],
            "all_positive": all(float(row["pooled_delta_without_module"]) > 0 for row in leave_one_out),
            "rows": leave_one_out,
        },
        "improvement_concentration": {
            "positive_improvement_correct_count": positive_total,
            "top_20pct_module_count": top_k,
            "top_20pct_share_of_positive_improvement": top_20_share,
        },
        "worst_five_modules": ranked[:5],
        "best_five_modules": list(reversed(ranked[-5:])),
        "per_module": rows,
        "claim_boundary": (
            "Derived robustness analysis of the already-frozen source-projection result. "
            "The source corpus has more active labels than emitted evaluable transition blocks; "
            "breadth statistics apply only to the exact emitted positive-transition blocks. "
            "This does not add native proof-state semantics, prover utility, or standalone tactic-mining novelty."
        ),
    }
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
