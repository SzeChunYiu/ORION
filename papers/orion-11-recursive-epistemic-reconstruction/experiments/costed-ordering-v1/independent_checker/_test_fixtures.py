"""Synthetic trace fixtures used to validate the checker itself.

A checker is not trustworthy because it runs. It is trustworthy when it has
been shown to FIRE on each defect it claims to catch and to STAY SILENT on a
clean trace. These fixtures exist to demonstrate both halves.

The clean fixture is built with near-zero within-stratum variance so the
gates resolve deterministically at small resample counts and the tests assert
on terminals rather than on luck.
"""

from __future__ import annotations

import copy
import json
from typing import Any

from . import _constants as K

WORLDS_PER_STRATUM = 12

# Cost profile per (stratum, arm) as (inspection, intervention, reopening).
# theorem_valid / ratio_aligned: ORION 1.8, faithful 2.7 -> ratio 0.667 < 0.80.
# violation strata: ORION and faithful tie, so the advantage disappears (G5).
_CHEAP = (1.0, 0.6, 0.2)      # total 1.8
_DEAR = (1.5, 0.9, 0.3)       # total 2.7
_ORACLE = (0.9, 0.6, 0.2)     # total 1.7  -> 1.8 <= 1.10 * 1.7 = 1.87 (G4)
_TIE = (1.3, 0.8, 0.3)        # total 2.4


def _profile(stratum: str, arm: str) -> tuple[float, float, float]:
    theorem_side = stratum in K.THEOREM_VALID_STRATA
    if arm == K.ARM_ORACLE:
        return _ORACLE
    if arm == K.ARM_ORION:
        return _CHEAP if theorem_side else _TIE
    if arm == K.ARM_PC_GREEDY:
        return _CHEAP if theorem_side else _TIE
    if arm == K.ARM_FAITHFUL:
        return _DEAR if theorem_side else _TIE
    return _DEAR


def _actions(profile: tuple[float, float, float], arm: str) -> list[dict[str, Any]]:
    """Three actions, one per cost component, in a stable order.

    ORION and gain_per_cost_greedy share an identical signature so the
    ratio_aligned instrument control (G7) holds by construction in the clean
    fixture and can be broken deliberately in the mutated ones.
    """
    family = "levelordered" if arm in (K.ARM_ORION, K.ARM_PC_GREEDY) else arm
    out = []
    for step, (component, cost) in enumerate(zip(K.COST_COMPONENTS, profile), start=1):
        out.append(
            {
                "step": step,
                "kind": component,
                "level": step - 1,
                "target": f"{family}_class_{step}",
                "cost_component": component,
                "cost": cost,
            }
        )
    return out


def _row(world_id: str, stratum: str, arm: str, seed: int, *, forbidden: bool = False) -> dict:
    profile = _profile(stratum, arm)
    total = round(sum(profile), 12)
    return {
        "world_id": world_id,
        "stratum": stratum,
        "arm_id": arm,
        "seed": seed,
        "protected_root_task_success": True,
        "forbidden_high_level_mutation": forbidden,
        "cost": {
            "inspection": profile[0],
            "intervention": profile[1],
            "reopening": profile[2],
            "total": total,
        },
        "budget_exceeded": total > K.BUDGET_CEILING,
        "actions": _actions(profile, arm),
        "terminated_reason": "repair_confirmed",
    }


def clean_rows(
    *,
    pc_forbidden_outside_ratio_aligned: bool = True,
    include_optional_arm: bool = False,
    a4_spelling: str = K.STRATUM_A4,
) -> list[dict[str, Any]]:
    """A clean, fully covered, decomposing, paired trace.

    `pc_forbidden_outside_ratio_aligned` drives the G6 discriminator. When
    True the unconstrained p/c baseline mutates at high level, so it does NOT
    match ORION on safety and G6 passes. When False it matches ORION on every
    registered component, which is the falsification Theorem C predicts.
    """
    arms = list(K.REQUIRED_UNRESTRICTED_ARMS)
    if include_optional_arm:
        arms.append(K.ARM_RANDOM_UNSAFE)

    rows: list[dict[str, Any]] = []
    seed = 1000
    for stratum in K.CANONICAL_STRATA:
        written = a4_spelling if stratum == K.STRATUM_A4 else stratum
        for i in range(WORLDS_PER_STRATUM):
            world_id = f"w_{stratum}_{i:03d}"
            seed += 1
            for arm in arms:
                forbidden = False
                if arm == K.ARM_PC_GREEDY:
                    forbidden = pc_forbidden_outside_ratio_aligned and (
                        stratum != K.STRATUM_RATIO_ALIGNED
                    )
                elif arm in (K.ARM_GLOBAL_FLAT, K.ARM_RANDOM_SAFE, K.ARM_RANDOM_UNSAFE):
                    forbidden = i % 4 == 0
                row = _row(world_id, stratum, arm, seed, forbidden=forbidden)
                row["stratum"] = written
                rows.append(row)
            if stratum in K.THEOREM_VALID_STRATA:
                row = _row(world_id, stratum, K.ARM_ORACLE, seed)
                row["stratum"] = written
                rows.append(row)
    return rows


def write_jsonl(path: str, rows: list[dict[str, Any]]) -> str:
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    return path


def mutate(rows: list[dict[str, Any]], predicate, change) -> list[dict[str, Any]]:
    """Copy `rows`, applying `change` to the first row matching `predicate`."""
    out = copy.deepcopy(rows)
    for row in out:
        if predicate(row):
            change(row)
            break
    else:
        raise AssertionError("fixture mutation matched no row; the fixture drifted")
    return out


def find(arm: str, stratum: str | None = None):
    """Predicate selecting the first row of `arm` (optionally within `stratum`)."""
    def predicate(row: dict[str, Any]) -> bool:
        if row["arm_id"] != arm:
            return False
        return stratum is None or row["stratum"] == stratum

    return predicate


def noisy_rows(scale: float, noise: float, fixture_seed: int = 7) -> list[dict[str, Any]]:
    """A clean trace carrying real within-stratum cost variance.

    `scale` sets the ORION/faithful cost ratio on the theorem-valid strata and
    `noise` the spread, so the bootstrap UCB can be placed at, near or far from
    the 0.80 G3 threshold. Used to show that the seed-stability probe fires
    when the verdict genuinely depends on the unfrozen seed and stays silent
    when variance is present but the verdict does not.
    """
    import random

    rng = random.Random(fixture_seed)
    rows = clean_rows()
    for row in rows:
        if row["stratum"] not in K.THEOREM_VALID_STRATA:
            continue
        if row["arm_id"] not in (K.ARM_ORION, K.ARM_FAITHFUL):
            continue
        factor = scale if row["arm_id"] == K.ARM_ORION else 1.0
        base = max(0.05, 2.4 * factor * (1.0 + rng.uniform(-noise, noise)))
        parts = [round(base * f, 9) for f in (0.5, 0.3, 0.2)]
        total = round(sum(parts), 9)
        row["cost"] = dict(zip(K.COST_COMPONENTS, parts))
        row["cost"]["total"] = total
        row["budget_exceeded"] = total > K.BUDGET_CEILING
        for action, value in zip(row["actions"], parts):
            action["cost"] = value
    # G7 is an instrument control: ORION and p/c must stay identical on
    # ratio_aligned, so mirror ORION's perturbed rows onto the p/c arm.
    source = {
        row["world_id"]: row
        for row in rows
        if row["arm_id"] == K.ARM_ORION and row["stratum"] == K.STRATUM_RATIO_ALIGNED
    }
    for row in rows:
        if row["arm_id"] == K.ARM_PC_GREEDY and row["stratum"] == K.STRATUM_RATIO_ALIGNED:
            origin = source[row["world_id"]]
            row["cost"] = dict(origin["cost"])
            row["actions"] = [dict(a) for a in origin["actions"]]
            row["budget_exceeded"] = origin["budget_exceeded"]
    return rows
