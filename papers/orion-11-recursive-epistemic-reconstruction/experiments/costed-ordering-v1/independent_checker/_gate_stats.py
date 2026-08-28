"""Which statistics are drawn, and which tests enter the Holm family.

Kept separate from the gate readings so a reviewer can audit the multiplicity
scope on its own. Two decisions live here and are deliberate:

* G3 and G6 are computed on the SAME world scope, because
  EXPECTED_TERMINALS.json reporting_rule requires them to be read jointly and
  a cost win reported on a different world set from its donor baseline would
  not be a joint reading. Each is also computed on all strata as a reported
  sensitivity.

* The Holm family contains only tests that genuinely have a sampling
  distribution: the pooled noninferiority test, the G3 cost-ratio test, the
  G6 ORION-advantage test and the per-stratum G5 advantage tests. G2 and G7
  are deterministic invariants and G4 is a point comparison against the
  oracle; manufacturing p-values for them to satisfy the wording "Holm across
  the registered gate family" would be worse than declaring the scope.
"""

from __future__ import annotations

from typing import Any

from . import _constants as K
from . import _stats as ST


def build_stats(
    frames: dict[str, Any],
    strata_present: tuple[str, ...],
    theorem_present: tuple[str, ...],
    violation_present: tuple[str, ...],
) -> list[ST.Stat]:
    """Every bootstrap statistic, evaluated on one shared resample scheme."""
    stats: list[ST.Stat] = []
    if "orion_vs_faithful" in frames:
        frame = frames["orion_vs_faithful"]
        stats.append(ST.success_diff_stat("G1_success_diff_pooled", frame, strata_present))
        stats.append(ST.ratio_stat("G3_ratio_theorem_scope", frame, theorem_present))
        stats.append(ST.ratio_stat("G3_ratio_all_strata", frame, strata_present))
        for stratum in violation_present:
            stats.append(ST.ratio_stat(f"G5_ratio__{stratum}", frame, (stratum,)))
        for stratum in theorem_present:
            stats.append(ST.ratio_stat(f"G3_ratio__{stratum}", frame, (stratum,)))
    if "orion_vs_pc" in frames:
        frame = frames["orion_vs_pc"]
        stats.append(ST.ratio_stat("G6_ratio_theorem_scope", frame, theorem_present))
        stats.append(ST.ratio_stat("G6_ratio_all_strata", frame, strata_present))
    if "orion_vs_oracle" in frames and K.STRATUM_THEOREM_VALID in theorem_present:
        stats.append(
            ST.unmatched_ratio_stat(
                "G4_ratio_orion_over_oracle",
                frames["orion_vs_oracle"],
                (K.STRATUM_THEOREM_VALID,),
            )
        )
    return stats


def build_holm_family(
    draws: dict[str, Any], violation_present: tuple[str, ...]
) -> dict[str, float | None]:
    """One-sided p-values for the tests that carry a sampling distribution."""
    p_raw: dict[str, float | None] = {}
    if "G1_success_diff_pooled" in draws:
        p_raw["G1_success_noninferiority"] = ST.one_sided_p(
            draws["G1_success_diff_pooled"], K.G1_NONINFERIORITY_MARGIN, "above"
        )
    if "G3_ratio_theorem_scope" in draws:
        p_raw["G3_cost_ratio"] = ST.one_sided_p(
            draws["G3_ratio_theorem_scope"], K.G3_COST_RATIO_THRESHOLD, "below"
        )
    if "G6_ratio_theorem_scope" in draws:
        p_raw["G6_orion_cost_advantage_over_pc"] = ST.one_sided_p(
            draws["G6_ratio_theorem_scope"], K.G6_PARITY_RATIO, "below"
        )
    for stratum in violation_present:
        name = f"G5_ratio__{stratum}"
        if name in draws:
            p_raw[f"G5_advantage__{stratum}"] = ST.one_sided_p(
                draws[name], K.G3_COST_RATIO_THRESHOLD, "below"
            )
    return p_raw
