from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

# parents[2]: the papers-directory refactor moved this file up one level and
# the index was not followed, so ROOT resolved outside the repository.
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULT = ROOT / "research" / "extensions" / "p9-structured-neural" / "execution" / "D1_EXECUTION_RESULT_V1_2.json"
OUT = HERE / "evidence" / "D1_PAIRED_EFFECTS_V1.json"

PRIMARY = "TYPED_RELATIONAL"
COMPARATORS = ("TRANSCRIPT_BAG", "UNTYPED_PAIR", "TYPED_SERIALIZED_BAG")
EXPECTED_RESULT_DIGEST = "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a"
BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 913_771


def load() -> dict[str, Any]:
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    if data.get("result_digest") != EXPECTED_RESULT_DIGEST:
        raise SystemExit(f"unexpected D1 result digest: {data.get('result_digest')!r}")
    if data.get("terminal") != "D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED":
        raise SystemExit(f"unexpected D1 terminal: {data.get('terminal')!r}")
    return data


def prediction_map(arm: dict[str, Any]) -> dict[str, dict[str, Any]]:
    predictions = arm.get("test_predictions")
    if not isinstance(predictions, list):
        raise SystemExit("D1 arm lacks test_predictions")
    mapped: dict[str, dict[str, Any]] = {}
    for row in predictions:
        instance_id = row.get("instance_id")
        if not isinstance(instance_id, str) or instance_id in mapped:
            raise SystemExit(f"invalid or duplicate instance id: {instance_id!r}")
        mapped[instance_id] = row
    return mapped


def exact_mcnemar_two_sided(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    x = min(b, c)
    tail = sum(math.comb(n, i) for i in range(x + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def percentile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("empty percentile input")
    values = sorted(values)
    position = (len(values) - 1) * p
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return values[lo]
    w = position - lo
    return values[lo] * (1.0 - w) + values[hi] * w


def paired_bootstrap_ci(differences: list[int], seed_offset: int) -> tuple[float, float]:
    rng = random.Random(BOOTSTRAP_SEED + seed_offset)
    n = len(differences)
    draws: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        total = 0
        for _ in range(n):
            total += differences[rng.randrange(n)]
        draws.append(total / n)
    return percentile(draws, 0.025), percentile(draws, 0.975)


def arm_strata(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    groups: dict[int, list[bool]] = defaultdict(list)
    labels: dict[str, list[bool]] = defaultdict(list)
    for row in rows.values():
        groups[int(row["mutation_count"])].append(bool(row["correct"]))
        labels[str(row["target"])].append(bool(row["correct"]))
    return {
        "by_mutation_count": {
            str(k): {
                "n": len(vals),
                "correct": sum(vals),
                "accuracy": sum(vals) / len(vals),
            }
            for k, vals in sorted(groups.items())
        },
        "by_target": {
            label: {
                "n": len(vals),
                "correct": sum(vals),
                "accuracy": sum(vals) / len(vals),
            }
            for label, vals in sorted(labels.items())
        },
    }


def main() -> None:
    data = load()
    results = data["results"]
    maps = {name: prediction_map(results[name]) for name in (PRIMARY, *COMPARATORS)}

    ids = set(maps[PRIMARY])
    if len(ids) != 128:
        raise SystemExit(f"expected 128 protected D1 instances, got {len(ids)}")
    for name, rows in maps.items():
        if set(rows) != ids:
            raise SystemExit(f"{name} instance set differs from {PRIMARY}")
        reported = float(results[name]["test"]["accuracy"])
        observed = sum(bool(row["correct"]) for row in rows.values()) / len(rows)
        if not math.isclose(reported, observed, abs_tol=1e-12, rel_tol=0.0):
            raise SystemExit(f"{name} reported accuracy mismatch: {reported} vs {observed}")

    for instance_id in ids:
        target = maps[PRIMARY][instance_id]["target"]
        mutation_count = maps[PRIMARY][instance_id]["mutation_count"]
        for name in COMPARATORS:
            row = maps[name][instance_id]
            if row["target"] != target or row["mutation_count"] != mutation_count:
                raise SystemExit(f"paired metadata mismatch for {instance_id} in {name}")

    comparisons: dict[str, Any] = {}
    primary_rows = maps[PRIMARY]
    primary_accuracy = sum(bool(row["correct"]) for row in primary_rows.values()) / len(ids)
    for offset, comparator in enumerate(COMPARATORS):
        other_rows = maps[comparator]
        differences: list[int] = []
        typed_correct_other_wrong = 0
        typed_wrong_other_correct = 0
        both_correct = 0
        both_wrong = 0
        for instance_id in sorted(ids):
            a = bool(primary_rows[instance_id]["correct"])
            b = bool(other_rows[instance_id]["correct"])
            differences.append(int(a) - int(b))
            if a and not b:
                typed_correct_other_wrong += 1
            elif b and not a:
                typed_wrong_other_correct += 1
            elif a and b:
                both_correct += 1
            else:
                both_wrong += 1
        other_accuracy = sum(bool(row["correct"]) for row in other_rows.values()) / len(ids)
        ci_lo, ci_hi = paired_bootstrap_ci(differences, offset)
        comparisons[comparator] = {
            "n": len(ids),
            "typed_accuracy": primary_accuracy,
            "comparator_accuracy": other_accuracy,
            "absolute_accuracy_delta": primary_accuracy - other_accuracy,
            "paired_bootstrap_95pct_interval": [ci_lo, ci_hi],
            "discordant": {
                "typed_correct_comparator_wrong": typed_correct_other_wrong,
                "typed_wrong_comparator_correct": typed_wrong_other_correct,
            },
            "both_correct": both_correct,
            "both_wrong": both_wrong,
            "exact_mcnemar_two_sided_p": exact_mcnemar_two_sided(
                typed_correct_other_wrong, typed_wrong_other_correct
            ),
        }

    artifact = {
        "schema": "P9.D1PairedEffects.v1",
        "analysis_status": "POST_HOC_DERIVED_FROM_FROZEN_RAW_PREDICTIONS_NO_NEW_OUTCOME",
        "source_result": str(RESULT.relative_to(ROOT)),
        "source_result_digest": EXPECTED_RESULT_DIGEST,
        "primary_arm": PRIMARY,
        "protected_n": len(ids),
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "comparisons": comparisons,
        "stratified_accuracy": {name: arm_strata(rows) for name, rows in maps.items()},
        "claim_boundary": (
            "Derived paired statistics quantify the already-frozen D1 held-out-domain effect. "
            "They are not a preregistered new endpoint and do not expand the D1 domain or model claim."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
