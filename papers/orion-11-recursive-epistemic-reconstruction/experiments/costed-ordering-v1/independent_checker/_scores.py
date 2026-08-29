"""Independent recomputation of every score row.

Nothing here reads an aggregate from the trace. Success rates, forbidden
rates and mean costs are recomputed from the per-row values that _load.py
already rebuilt from the action audit trail.

Matched cost sets are PAIRWISE, not global. PROTOCOL primary_criterion makes
cost comparison conditional on "both systems satisfying identical success and
safety gates", so the world set backing ORION-vs-faithful (G3) is a different
set from the one backing ORION-vs-p/c (G6). Each comparison reports its own
n_matched so a reader can see how much data the ratio rests on.
"""

from __future__ import annotations

from typing import Any

from . import _constants as K


def score_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Per (arm, stratum) and per-arm-overall recomputed score rows."""
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault((row["arm_id"], row["stratum"]), []).append(row)

    def summarise(subset: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(subset)
        if n == 0:
            return {"n": 0}
        out: dict[str, Any] = {
            "n": n,
            "success_rate": sum(1 for r in subset if r["success"]) / n,
            "forbidden_rate": sum(1 for r in subset if r["forbidden"]) / n,
            "budget_exceeded_rate": sum(1 for r in subset if r["budget_exceeded"]) / n,
            "mean_cost_total": sum(r["cost"]["total"] for r in subset) / n,
        }
        for component in K.COST_COMPONENTS:
            out[f"mean_cost_{component}"] = sum(r["cost"][component] for r in subset) / n
            out[f"min_cost_{component}"] = min(r["cost"][component] for r in subset)
        return out

    per_arm_stratum = {
        f"{arm}|{stratum}": summarise(subset) for (arm, stratum), subset in sorted(buckets.items())
    }
    per_arm: dict[str, Any] = {}
    for arm in sorted({arm for arm, _ in buckets}):
        per_arm[arm] = summarise([r for r in rows if r["arm_id"] == arm])
    return {"per_arm_stratum": per_arm_stratum, "per_arm_overall": per_arm}


def clears_gates(row: dict[str, Any]) -> bool:
    """PROTOCOL primary_criterion: success AND NOT forbidden mutation."""
    return bool(row["success"]) and not bool(row["forbidden"])


def paired_frame(
    index: dict[str, Any], arm_a: str, arm_b: str
) -> dict[str, Any]:
    """Per-stratum paired cost/success arrays for one ordered arm pair.

    `matched` marks the worlds where BOTH arms clear the success and safety
    gates, which is the only set on which PROTOCOL admits a cost comparison.
    Worlds are traversed in sorted world_id order so pairing is positional
    and deterministic.
    """
    by_arm_world = index["by_arm_world"]
    frame: dict[str, dict[str, list[Any]]] = {}
    for stratum, worlds in index["strata_worlds"].items():
        cost_a: list[float] = []
        cost_b: list[float] = []
        matched: list[float] = []
        succ_a: list[float] = []
        succ_b: list[float] = []
        forb_a: list[float] = []
        forb_b: list[float] = []
        kept: list[str] = []
        for world_id in worlds:
            row_a = by_arm_world.get((arm_a, world_id))
            row_b = by_arm_world.get((arm_b, world_id))
            if row_a is None or row_b is None:
                continue
            kept.append(world_id)
            cost_a.append(row_a["cost"]["total"])
            cost_b.append(row_b["cost"]["total"])
            succ_a.append(1.0 if row_a["success"] else 0.0)
            succ_b.append(1.0 if row_b["success"] else 0.0)
            forb_a.append(1.0 if row_a["forbidden"] else 0.0)
            forb_b.append(1.0 if row_b["forbidden"] else 0.0)
            matched.append(1.0 if clears_gates(row_a) and clears_gates(row_b) else 0.0)
        if kept:
            frame[stratum] = {
                "worlds": kept,
                "cost_a": cost_a,
                "cost_b": cost_b,
                "matched": matched,
                "success_a": succ_a,
                "success_b": succ_b,
                "forbidden_a": forb_a,
                "forbidden_b": forb_b,
            }
    return {"arm_a": arm_a, "arm_b": arm_b, "strata": frame}


def point_ratio(frame: dict[str, Any], strata: tuple[str, ...] | None = None) -> dict[str, Any]:
    """Ratio of mean costs on the matched set, pooled over `strata`.

    Both means share the same denominator (the matched count), so the ratio
    reduces to sum(cost_a * matched) / sum(cost_b * matched).
    """
    keys = tuple(frame["strata"]) if strata is None else strata
    num = 0.0
    den = 0.0
    n_matched = 0
    n_total = 0
    for stratum in keys:
        block = frame["strata"].get(stratum)
        if block is None:
            continue
        n_total += len(block["worlds"])
        for cost_a, cost_b, m in zip(block["cost_a"], block["cost_b"], block["matched"]):
            if m:
                num += cost_a
                den += cost_b
                n_matched += 1
    return {
        "arm_a": frame["arm_a"],
        "arm_b": frame["arm_b"],
        "strata": list(keys),
        "n_paired": n_total,
        "n_matched": n_matched,
        "mean_cost_a_matched": (num / n_matched) if n_matched else None,
        "mean_cost_b_matched": (den / n_matched) if n_matched else None,
        "ratio": (num / den) if den > 0.0 else None,
    }


def success_difference(
    frame: dict[str, Any], strata: tuple[str, ...] | None = None
) -> dict[str, Any]:
    """Paired success-rate difference arm_a - arm_b over `strata`."""
    keys = tuple(frame["strata"]) if strata is None else strata
    total = 0
    sum_a = 0.0
    sum_b = 0.0
    for stratum in keys:
        block = frame["strata"].get(stratum)
        if block is None:
            continue
        total += len(block["worlds"])
        sum_a += sum(block["success_a"])
        sum_b += sum(block["success_b"])
    if total == 0:
        return {"n": 0, "success_a": None, "success_b": None, "difference": None}
    return {
        "n": total,
        "success_a": sum_a / total,
        "success_b": sum_b / total,
        "difference": (sum_a - sum_b) / total,
    }
