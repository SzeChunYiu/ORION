"""Arm coverage, oracle placement, world identity and pairing completeness.

Refusal policy (the guard against a checker that cries wolf): a missing
input refuses only when a registered gate actually consumes it. Everything
else is reported as a warning with the affected gates named.
"""

from __future__ import annotations

from typing import Any

from . import _constants as K
from . import _faults as F


def index_rows(rows: list[dict[str, Any]], ledger: F.Ledger) -> dict[str, Any]:
    """Build the (arm, world) index and enforce identity invariants."""
    by_arm_world: dict[tuple[str, str], dict[str, Any]] = {}
    world_stratum: dict[str, str] = {}
    world_seed: dict[str, int] = {}

    for row in rows:
        key = (row["arm_id"], row["world_id"])
        if key in by_arm_world:
            ledger.fault(
                F.FAULT_DUPLICATE_ROW,
                "more than one row for the same (world_id, arm_id); "
                "paired comparison is not well defined",
                {
                    "world_id": row["world_id"],
                    "arm_id": row["arm_id"],
                    "lines": [by_arm_world[key]["line"], row["line"]],
                },
            )
            continue
        by_arm_world[key] = row

        prior = world_stratum.get(row["world_id"])
        if prior is None:
            world_stratum[row["world_id"]] = row["stratum"]
        elif prior != row["stratum"]:
            ledger.fault(
                F.FAULT_INCONSISTENT_WORLD_STRATUM,
                "the same world_id carries different strata across arms",
                {"world_id": row["world_id"], "strata": sorted({prior, row["stratum"]})},
            )

        prior_seed = world_seed.get(row["world_id"])
        if prior_seed is None:
            world_seed[row["world_id"]] = row["seed"]
        elif prior_seed != row["seed"]:
            ledger.fault(
                F.FAULT_INCONSISTENT_WORLD_SEED,
                "the same world_id carries different seeds across arms; "
                "TRACE_SCHEMA_V1 fixes the seed per world",
                {"world_id": row["world_id"], "seeds": sorted({prior_seed, row["seed"]})},
            )

    # Deterministic, positional pairing: sorted world identity throughout.
    strata_worlds: dict[str, list[str]] = {s: [] for s in K.CANONICAL_STRATA}
    for world_id, stratum in world_stratum.items():
        strata_worlds[stratum].append(world_id)
    for stratum in strata_worlds:
        strata_worlds[stratum].sort()

    arms_present = sorted({arm for arm, _ in by_arm_world})
    return {
        "by_arm_world": by_arm_world,
        "world_stratum": world_stratum,
        "world_seed": world_seed,
        "strata_worlds": strata_worlds,
        "strata_present": [s for s in K.CANONICAL_STRATA if strata_worlds[s]],
        "arms_present": arms_present,
        "all_worlds": sorted(world_stratum),
    }


def check_coverage(index: dict[str, Any], ledger: F.Ledger) -> dict[str, Any]:
    """Arm coverage, oracle placement and pairing completeness."""
    by_arm_world = index["by_arm_world"]
    strata_worlds = index["strata_worlds"]
    strata_present = index["strata_present"]
    arms_present = set(index["arms_present"])

    arm_worlds: dict[str, set[str]] = {}
    for arm, world_id in by_arm_world:
        arm_worlds.setdefault(arm, set()).add(world_id)

    # ---- gate-consumed arms must be present at all -----------------------
    for arm, gates in K.GATE_CONSUMED_ARMS.items():
        if arm not in arms_present:
            if arm == K.ARM_ORACLE:
                ledger.fault(
                    F.FAULT_DP_ORACLE_INFEASIBLE,
                    "exact_dp_oracle produced no rows, so G4 has no denominator; "
                    "the optimality gap is unmeasured, not satisfied",
                    {"gates_blocked": list(gates)},
                )
            else:
                ledger.fault(
                    F.FAULT_MISSING_GATE_CONSUMED_ARM,
                    f"arm {arm!r} is absent but is consumed by gates {list(gates)}",
                    {"arm": arm, "gates_blocked": list(gates)},
                )

    # ---- optional arms: warn, never refuse -------------------------------
    for arm in K.OPTIONAL_ARMS:
        if arm not in arms_present:
            ledger.warn(
                "OPTIONAL_ARM_ABSENT",
                f"arm {arm!r} is enumerated in PROTOCOL.json but omitted from "
                "TRACE_SCHEMA_V1.json and consumed by no gate G1-G7; its absence is "
                "recorded, not refused",
                {"arm": arm},
            )

    # ---- unrestricted arms must appear on every stratum present ----------
    for arm in K.REQUIRED_UNRESTRICTED_ARMS:
        if arm not in arms_present:
            if arm not in K.GATE_CONSUMED_ARMS:
                ledger.fault(
                    F.FAULT_ARM_COVERAGE,
                    f"arm {arm!r} is required on every stratum by both frozen documents "
                    "but produced no rows",
                    {"arm": arm},
                )
            continue
        for stratum in strata_present:
            missing = set(strata_worlds[stratum]) - arm_worlds[arm]
            if missing:
                ledger.fault(
                    F.FAULT_ARM_COVERAGE,
                    f"arm {arm!r} does not cover every world of stratum {stratum!r}",
                    {
                        "arm": arm,
                        "stratum": stratum,
                        "n_missing": len(missing),
                        "examples": sorted(missing)[: F.MAX_EXAMPLES],
                    },
                )

    # ---- oracle placement is restricted ----------------------------------
    if K.ARM_ORACLE in arms_present:
        oracle_worlds = arm_worlds[K.ARM_ORACLE]
        allowed = {
            world_id
            for stratum in K.ARM_ORACLE_STRATA
            for world_id in strata_worlds[stratum]
        }
        outside = oracle_worlds - allowed
        if outside:
            offending = sorted({index["world_stratum"][w] for w in outside})
            ledger.fault(
                F.FAULT_ORACLE_PLACEMENT,
                "exact_dp_oracle appears outside theorem_valid and ratio_aligned",
                {"strata": offending, "n_rows": len(outside)},
            )
        uncovered = allowed - oracle_worlds
        if uncovered:
            ledger.fault(
                F.FAULT_DP_ORACLE_INFEASIBLE,
                "exact_dp_oracle does not cover every theorem-valid world, so G4's "
                "denominator is incomplete; the optimality gap is unmeasured",
                {
                    "n_uncovered": len(uncovered),
                    "examples": sorted(uncovered)[: F.MAX_EXAMPLES],
                },
            )

    # ---- pairing completeness across the unrestricted arms ---------------
    reference: set[str] | None = None
    reference_arm = ""
    for arm in K.REQUIRED_UNRESTRICTED_ARMS:
        if arm not in arm_worlds:
            continue
        if reference is None:
            reference, reference_arm = arm_worlds[arm], arm
            continue
        if arm_worlds[arm] != reference:
            only_here = sorted(arm_worlds[arm] - reference)
            only_there = sorted(reference - arm_worlds[arm])
            ledger.fault(
                F.FAULT_PAIRING_INCOMPLETE,
                f"world_id set of arm {arm!r} differs from arm {reference_arm!r}; "
                "paired comparison is not well defined",
                {
                    "arm": arm,
                    "reference_arm": reference_arm,
                    "n_only_in_arm": len(only_here),
                    "n_only_in_reference": len(only_there),
                    "examples_only_in_arm": only_here[: F.MAX_EXAMPLES],
                    "examples_only_in_reference": only_there[: F.MAX_EXAMPLES],
                },
            )

    # ---- strata coverage --------------------------------------------------
    absent_strata = [s for s in K.CANONICAL_STRATA if s not in strata_present]
    if absent_strata:
        ledger.warn(
            "STRATUM_ABSENT",
            "strata registered in PROTOCOL.json produced no rows; gates scoped to them "
            "are reported unmeasured rather than passed",
            {"strata": absent_strata},
        )

    return {
        "arm_worlds": {arm: sorted(worlds) for arm, worlds in arm_worlds.items()},
        "n_worlds": len(index["all_worlds"]),
        "n_rows": len(by_arm_world),
        "strata_sizes": {s: len(strata_worlds[s]) for s in strata_present},
        "arms_present": sorted(arms_present),
        "strata_present": strata_present,
        "absent_strata": absent_strata,
    }
