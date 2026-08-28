"""Independent recomputation of gates G1-G7.

Each gate records the frozen statement it implements, the operationalisation
this checker chose where the statement is prose, and every component of the
decision, so a reader can audit the reading rather than trust it.

Declared readings where the frozen documents leave latitude:

* G1  PROTOCOL states the gate without a stratum scope; the terminal
      H_FALSIFIED__SUCCESS_NONINFERIORITY_FAILED scopes it "on any stratum".
      The terminal governs, and the pooled figure is reported alongside.
* G2  PROTOCOL says "every stratum"; the terminal scopes it to strata "where
      A3 holds". The terminal governs, because requiring zero forbidden
      mutation on the stratum whose whole construction makes the safety gate
      vacuous is not a test. Both readings are reported.
* G3  PROTOCOL states no stratum scope, unlike G4 ("on the theorem_valid
      stratum"), G5 ("assumption-violation control stratum") and G7 ("on the
      ratio_aligned stratum"), all of which are scoped explicitly. The
      decision is therefore taken on the theorem-valid strata, where the
      mechanism is claimed to operate, because G3 and G5 are otherwise in
      mathematical tension: G5 REQUIRES the advantage to vanish on the
      violation controls, and at the registered shares (0.60 theorem-valid,
      0.40 violation) pooling those null strata into G3 drags the ratio
      towards the 0.80 threshold from below, so satisfying G5 can by itself
      make G3 unsatisfiable. The all-strata figure is computed and reported
      as a sensitivity, and the gate is flagged scope_sensitive whenever the
      two readings disagree.
* G4  A point comparison against the oracle mean, per the frozen wording.
      No oracle means no denominator: unmeasured, never passed.
* G5  "The advantage disappears" is an absence claim, so its detection runs
      UNADJUSTED. Holm would reduce power to detect exactly the mechanism-
      attribution failure the gate exists to catch, which would let a
      multiplicity correction manufacture a pass. The adjusted variant is
      reported but does not decide.
* G6  Holm-adjusted in the direction that makes an ORION cost advantage
      HARDER to establish, so multiplicity can never suppress the
      theory-predicted falsification.
* G7  An instrument control. Any difference is a fault, not a gate failure.
"""

from __future__ import annotations

from typing import Any

from . import _constants as K
from . import _faults as F
from . import _scores as S
from . import _gate_stats as GS
from . import _stats as ST

UNMEASURED = "UNMEASURED"


def _gate(gate_id: str, statement: str, operationalisation: str) -> dict[str, Any]:
    return {
        "id": gate_id,
        "statement": statement,
        "operationalisation": operationalisation,
        "measured": False,
        "passed": None,
        "components": {},
    }


def _advantage(point: float | None, ci_high: float | None, threshold: float) -> bool | None:
    """A cost advantage is established only by point estimate AND interval."""
    if point is None or ci_high is None:
        return None
    return bool(point < threshold and ci_high < threshold)


def evaluate(
    index: dict[str, Any],
    rows: list[dict[str, Any]],
    seed: int,
    resamples: int,
    ledger: F.Ledger,
) -> dict[str, Any]:
    strata_present = tuple(index["strata_present"])
    stratum_sizes = {s: len(index["strata_worlds"][s]) for s in strata_present}
    violation_present = tuple(s for s in K.VIOLATION_STRATA if s in strata_present)
    theorem_present = tuple(s for s in K.THEOREM_VALID_STRATA if s in strata_present)
    a3_present = tuple(s for s in K.A3_HOLDS_STRATA if s in strata_present)

    scores = S.score_rows(rows)
    arms = set(index["arms_present"])

    frames: dict[str, Any] = {}
    if {K.ARM_ORION, K.ARM_FAITHFUL} <= arms:
        frames["orion_vs_faithful"] = S.paired_frame(index, K.ARM_ORION, K.ARM_FAITHFUL)
    if {K.ARM_ORION, K.ARM_PC_GREEDY} <= arms:
        frames["orion_vs_pc"] = S.paired_frame(index, K.ARM_ORION, K.ARM_PC_GREEDY)
    if {K.ARM_ORION, K.ARM_ORACLE} <= arms:
        frames["orion_vs_oracle"] = S.paired_frame(index, K.ARM_ORION, K.ARM_ORACLE)

    stats = GS.build_stats(frames, strata_present, theorem_present, violation_present)
    draws = ST.run_bootstrap(stats, stratum_sizes, seed=seed, resamples=resamples)
    intervals = {name: ST.percentile_interval(values) for name, values in draws.items()}
    p_raw = GS.build_holm_family(draws, violation_present)
    holm = ST.holm(p_raw)

    def adjusted_rejected(name: str) -> bool | None:
        entry = holm["tests"].get(name)
        if entry is None:
            return None
        return entry.get("rejected_at_alpha")

    gates: dict[str, Any] = {}

    # ---------------------------------------------------------------- G1 --
    g1 = _gate(
        "G1_success_noninferiority",
        "ORION success noninferior to faithful_active_voi with margin -0.01.",
        "Per-stratum point test (terminal scope) AND pooled point test AND "
        "Holm-adjusted bootstrap support for the pooled noninferiority test.",
    )
    if "orion_vs_faithful" in frames:
        f = frames["orion_vs_faithful"]
        per_stratum = {
            s: S.success_difference(f, (s,)) for s in strata_present
        }
        pooled = S.success_difference(f, strata_present)
        failing = [
            s
            for s, d in per_stratum.items()
            if d["difference"] is not None and d["difference"] < K.G1_NONINFERIORITY_MARGIN
        ]
        support = adjusted_rejected("G1_success_noninferiority")
        g1["measured"] = True
        g1["components"] = {
            "margin": K.G1_NONINFERIORITY_MARGIN,
            "pooled": pooled,
            "per_stratum": per_stratum,
            "failing_strata": failing,
            "point_all_strata_pass": not failing,
            "point_pooled_pass": bool(
                pooled["difference"] is not None
                and pooled["difference"] >= K.G1_NONINFERIORITY_MARGIN
            ),
            "holm_support": support,
            "bootstrap": intervals.get("G1_success_diff_pooled"),
        }
        g1["passed"] = bool(
            g1["components"]["point_all_strata_pass"]
            and g1["components"]["point_pooled_pass"]
            and support is True
        )
    gates["G1"] = g1

    # ---------------------------------------------------------------- G2 --
    g2 = _gate(
        "G2_zero_forbidden",
        "ORION forbidden_high_level_mutation_rate == 0 on every stratum.",
        "Terminal reading governs: every stratum where A3 holds, derived as the "
        "strata whose assumptions_violated does not contain A3. The literal "
        "every-stratum reading is reported beside it.",
    )
    orion_forbidden = {
        s: scores["per_arm_stratum"].get(f"{K.ARM_ORION}|{s}", {}).get("forbidden_rate")
        for s in strata_present
    }
    if K.ARM_ORION in arms:
        literal_fail = [
            s for s, r in orion_forbidden.items() if r is not None and r > K.G2_FORBIDDEN_CEILING
        ]
        terminal_fail = [s for s in literal_fail if s in a3_present]
        g2["measured"] = True
        g2["components"] = {
            "forbidden_rate_by_stratum": orion_forbidden,
            "a3_holds_strata": list(a3_present),
            "a3_holds_derivation": "every stratum except violate_A3_safety",
            "literal_every_stratum_pass": not literal_fail,
            "literal_failing_strata": literal_fail,
            "terminal_a3_scoped_pass": not terminal_fail,
            "terminal_failing_strata": terminal_fail,
        }
        g2["passed"] = not terminal_fail
    gates["G2"] = g2

    # ---------------------------------------------------------------- G3 --
    g3 = _gate(
        "G3_cost_ratio",
        "Paired expected-cost ratio orion_level_monotone / faithful_active_voi "
        "< 0.80 AND its 95% upper confidence bound < 0.80.",
        "Ratio of matched mean costs pooled over every stratum, with the "
        "stratified percentile bootstrap UCB, plus Holm-adjusted support.",
    )
    if "orion_vs_faithful" in frames:
        f = frames["orion_vs_faithful"]
        decided = S.point_ratio(f, theorem_present)
        ci = intervals.get("G3_ratio_theorem_scope", {})
        support = adjusted_rejected("G3_cost_ratio")
        sensitivity = S.point_ratio(f, strata_present)
        sens_ci = intervals.get("G3_ratio_all_strata", {})
        advantage_theorem = _advantage(
            decided["ratio"], ci.get("ci_high"), K.G3_COST_RATIO_THRESHOLD
        )
        advantage_all = _advantage(
            sensitivity["ratio"], sens_ci.get("ci_high"), K.G3_COST_RATIO_THRESHOLD
        )
        scope_sensitive = (
            advantage_theorem is not None
            and advantage_all is not None
            and advantage_theorem != advantage_all
        )
        g3["measured"] = decided["ratio"] is not None
        g3["components"] = {
            "threshold": K.G3_COST_RATIO_THRESHOLD,
            "decision_scope": list(theorem_present),
            "decision_scope_rationale": "PROTOCOL leaves G3 unscoped while scoping G4, "
            "G5 and G7 explicitly; pooling the violation controls that G5 requires to be "
            "null would let G5 make G3 unsatisfiable",
            "pooled": decided,
            "bootstrap": ci,
            "point_pass": (
                None if decided["ratio"] is None else decided["ratio"] < K.G3_COST_RATIO_THRESHOLD
            ),
            "ucb_pass": (
                None
                if ci.get("ci_high") is None
                else ci["ci_high"] < K.G3_COST_RATIO_THRESHOLD
            ),
            "holm_support": support,
            "sensitivity_all_strata": {
                "point": sensitivity,
                "bootstrap": sens_ci,
                "advantage_present": advantage_all,
            },
            "scope_sensitive": scope_sensitive,
            "per_stratum": {
                s: {
                    "point": S.point_ratio(f, (s,)),
                    "bootstrap": intervals.get(f"G3_ratio__{s}"),
                }
                for s in theorem_present
            },
        }
        if scope_sensitive:
            ledger.defect(
                "PROTOCOL.json G3 fixes no stratum scope. On these traces the "
                "theorem-valid reading and the all-strata reading disagree on whether "
                "the cost advantage is established, so the G3 verdict depends on an "
                "unstated protocol choice. The theorem-valid reading decides; both are "
                "reported."
            )
        if g3["measured"]:
            g3["passed"] = bool(
                g3["components"]["point_pass"]
                and g3["components"]["ucb_pass"]
                and support is True
            )
        else:
            ledger.warn(
                "G3_NO_MATCHED_WORLDS",
                "no world clears the success and safety gates for both ORION and "
                "faithful_active_voi, so the cost ratio has no matched set",
            )
    gates["G3"] = g3

    # ---------------------------------------------------------------- G4 --
    g4 = _gate(
        "G4_dp_gap",
        "ORION mean cost <= 1.10 x exact_dp_oracle optimum on the theorem_valid "
        "stratum.",
        "Point comparison of unconditional mean costs on theorem_valid. Absent "
        "or incomplete oracle coverage leaves G4 UNMEASURED, never passed.",
    )
    orion_tv = scores["per_arm_stratum"].get(f"{K.ARM_ORION}|{K.STRATUM_THEOREM_VALID}", {})
    oracle_tv = scores["per_arm_stratum"].get(f"{K.ARM_ORACLE}|{K.STRATUM_THEOREM_VALID}", {})
    if orion_tv.get("mean_cost_total") is not None and oracle_tv.get("mean_cost_total"):
        bound = K.G4_DP_GAP_MULTIPLIER * oracle_tv["mean_cost_total"]
        g4["measured"] = True
        g4["components"] = {
            "multiplier": K.G4_DP_GAP_MULTIPLIER,
            "orion_mean_cost": orion_tv["mean_cost_total"],
            "oracle_mean_cost": oracle_tv["mean_cost_total"],
            "allowed_ceiling": bound,
            "observed_gap_ratio": orion_tv["mean_cost_total"] / oracle_tv["mean_cost_total"],
            "n_orion": orion_tv.get("n"),
            "n_oracle": oracle_tv.get("n"),
            "bootstrap": intervals.get("G4_ratio_orion_over_oracle"),
        }
        g4["passed"] = bool(orion_tv["mean_cost_total"] <= bound + K.DECOMPOSITION_TOLERANCE)
    else:
        g4["components"] = {
            "status": UNMEASURED,
            "reason": "exact_dp_oracle mean cost on theorem_valid is unavailable or zero",
        }
    gates["G4"] = g4

    # ---------------------------------------------------------------- G5 --
    g5 = _gate(
        "G5_assumption_attribution",
        "The ORION cost advantage disappears on every assumption-violation "
        "control stratum.",
        "Per violation stratum the advantage is declared present when the "
        "matched cost ratio is below 0.80 AND its 95% UCB is below 0.80, "
        "evaluated UNADJUSTED. G5 passes when no violation stratum shows it.",
    )
    if "orion_vs_faithful" in frames and violation_present:
        f = frames["orion_vs_faithful"]
        detail: dict[str, Any] = {}
        persisting: list[str] = []
        for stratum in violation_present:
            point = S.point_ratio(f, (stratum,))
            ci = intervals.get(f"G5_ratio__{stratum}", {})
            present = _advantage(point["ratio"], ci.get("ci_high"), K.G3_COST_RATIO_THRESHOLD)
            detail[stratum] = {
                "point": point,
                "bootstrap": ci,
                "advantage_present_unadjusted": present,
                "holm_adjusted_rejected": adjusted_rejected(f"G5_advantage__{stratum}"),
            }
            if present:
                persisting.append(stratum)
        g5["measured"] = True
        g5["components"] = {
            "threshold": K.G3_COST_RATIO_THRESHOLD,
            "violation_strata": list(violation_present),
            "per_stratum": detail,
            "strata_where_advantage_persists": persisting,
            "decision_uses": "UNADJUSTED__ABSENCE_CLAIM_MUST_NOT_GAIN_POWER_FROM_MULTIPLICITY",
        }
        g5["passed"] = not persisting
    gates["G5"] = g5

    # ---------------------------------------------------------------- G6 --
    g6 = _gate(
        "G6_donor_baseline",
        "Reported jointly with G3: ORION cost versus gain_per_cost_greedy at "
        "equal success and safety. Theorem C predicts ORION is NOT lower.",
        "gain_per_cost_greedy matches-or-beats ORION when it is noninferior on "
        "success at the registered -0.01 margin, no worse on forbidden-mutation "
        "rate, and no ORION cost advantage can be established on the matched "
        "set (point ratio AND Holm-adjusted UCB below 1.0). G6 passes when it "
        "does NOT match-or-beat.",
    )
    if "orion_vs_pc" in frames:
        f = frames["orion_vs_pc"]
        pooled = S.point_ratio(f, theorem_present)
        ci = intervals.get("G6_ratio_theorem_scope", {})
        sensitivity = S.point_ratio(f, strata_present)
        succ = S.success_difference(f, strata_present)
        orion_forb = scores["per_arm_overall"].get(K.ARM_ORION, {}).get("forbidden_rate")
        pc_forb = scores["per_arm_overall"].get(K.ARM_PC_GREEDY, {}).get("forbidden_rate")
        support = adjusted_rejected("G6_orion_cost_advantage_over_pc")
        orion_advantage = bool(
            pooled["ratio"] is not None
            and pooled["ratio"] < K.G6_PARITY_RATIO
            and ci.get("ci_high") is not None
            and ci["ci_high"] < K.G6_PARITY_RATIO
            and support is True
        )
        success_ok = bool(
            succ["difference"] is not None
            and -succ["difference"] >= K.G1_NONINFERIORITY_MARGIN
        )
        safety_ok = bool(
            orion_forb is not None and pc_forb is not None and pc_forb <= orion_forb
        )
        matches_or_beats = bool(success_ok and safety_ok and not orion_advantage)
        g6["measured"] = pooled["ratio"] is not None
        g6["components"] = {
            "parity_ratio": K.G6_PARITY_RATIO,
            "decision_scope": list(theorem_present),
            "decision_scope_rationale": "read jointly with G3, so computed on the same "
            "world scope (EXPECTED_TERMINALS reporting_rule.must_report_G3_and_G6_together)",
            "pooled_ratio_orion_over_pc": pooled,
            "bootstrap": ci,
            "sensitivity_all_strata": {
                "point": sensitivity,
                "bootstrap": intervals.get("G6_ratio_all_strata"),
            },
            "orion_success_rate": succ["success_a"],
            "pc_success_rate": succ["success_b"],
            "pc_success_noninferior": success_ok,
            "orion_forbidden_rate": orion_forb,
            "pc_forbidden_rate": pc_forb,
            "pc_safety_no_worse": safety_ok,
            "holm_support_for_orion_advantage": support,
            "orion_cost_advantage_established": orion_advantage,
            "pc_matches_or_beats_orion": matches_or_beats,
        }
        if g6["measured"]:
            g6["passed"] = not matches_or_beats
    gates["G6"] = g6

    # ---------------------------------------------------------------- G7 --
    g7 = _gate(
        "G7_instrument_control",
        "On the ratio_aligned stratum, orion_level_monotone and "
        "gain_per_cost_greedy must produce identical orderings and identical "
        "expected cost. Any difference is an instrument fault and forces "
        "CANNOT_CHECK.",
        "Per world on ratio_aligned: identical (kind, level, target) action "
        "sequence AND identical total cost within 1e-9, plus identical means.",
    )
    if K.STRATUM_RATIO_ALIGNED in strata_present and {K.ARM_ORION, K.ARM_PC_GREEDY} <= arms:
        by_arm_world = index["by_arm_world"]
        order_diffs: list[str] = []
        cost_diffs: list[dict[str, Any]] = []
        worlds = index["strata_worlds"][K.STRATUM_RATIO_ALIGNED]
        for world_id in worlds:
            row_o = by_arm_world.get((K.ARM_ORION, world_id))
            row_p = by_arm_world.get((K.ARM_PC_GREEDY, world_id))
            if row_o is None or row_p is None:
                continue
            if row_o["action_signature"] != row_p["action_signature"]:
                order_diffs.append(world_id)
            delta = row_o["cost"]["total"] - row_p["cost"]["total"]
            if abs(delta) > K.DECOMPOSITION_TOLERANCE:
                cost_diffs.append({"world_id": world_id, "delta": delta})
        mean_o = scores["per_arm_stratum"].get(
            f"{K.ARM_ORION}|{K.STRATUM_RATIO_ALIGNED}", {}
        ).get("mean_cost_total")
        mean_p = scores["per_arm_stratum"].get(
            f"{K.ARM_PC_GREEDY}|{K.STRATUM_RATIO_ALIGNED}", {}
        ).get("mean_cost_total")
        mean_delta = None if mean_o is None or mean_p is None else mean_o - mean_p
        g7["measured"] = True
        g7["components"] = {
            "n_worlds": len(worlds),
            "n_ordering_differences": len(order_diffs),
            "ordering_difference_examples": order_diffs[: F.MAX_EXAMPLES],
            "n_cost_differences": len(cost_diffs),
            "cost_difference_examples": cost_diffs[: F.MAX_EXAMPLES],
            "orion_mean_cost": mean_o,
            "pc_mean_cost": mean_p,
            "mean_cost_delta": mean_delta,
        }
        g7["passed"] = not order_diffs and not cost_diffs and (
            mean_delta is None or abs(mean_delta) <= K.DECOMPOSITION_TOLERANCE
        )
        if not g7["passed"]:
            ledger.fault(
                F.FAULT_G7_INSTRUMENT,
                "ratio_aligned is an INSTRUMENT_CONTROL where Theorem C makes "
                "level-monotone and flat p/c ordering coincide exactly; the measured "
                "difference is an instrument fault, so no arm may be read",
                {
                    "n_ordering_differences": len(order_diffs),
                    "n_cost_differences": len(cost_diffs),
                    "mean_cost_delta": mean_delta,
                },
            )
    else:
        g7["components"] = {
            "status": UNMEASURED,
            "reason": "ratio_aligned stratum or one of its two arms is absent",
        }
    gates["G7"] = g7

    # ---- anchor reproduction gate ----------------------------------------
    # PROTOCOL statistics.anchor_reproduction_gate is required and explicitly
    # "parameterised_per_world_set". No committed rates for THIS world family
    # exist in any frozen document, and hardcoding another world set's rates is
    # the exact defect that destroyed R4's replication arm. Reported unmeasured.
    anchor = {
        "required": True,
        "status": "CANNOT_CHECK__NO_ANCHOR_AVAILABLE_IN_FROZEN_BYTES",
        "reason": "PROTOCOL requires a per-world-set parameterised anchor gate, but no "
        "committed rates for this world family appear in PROTOCOL.json, "
        "EXPECTED_TERMINALS.json, TRACE_SCHEMA_V1.json or THEORY.md. The checker "
        "refuses to hardcode any other world set's rates: that is precisely the "
        "runner defect that lost R4's replication arm.",
        "counted_as_pass": False,
    }
    ledger.defect(
        "PROTOCOL.json statistics.anchor_reproduction_gate is required and "
        "parameterised per world set, but the packet freezes no committed rates for "
        "this world family, so the anchor gate cannot be reproduced from traces alone."
    )

    return {
        "score_rows": scores,
        "gates": gates,
        "anchor_reproduction_gate": anchor,
        "holm": holm,
        "bootstrap_intervals": intervals,
        "comparisons": {
            name: {
                "arm_a": frame["arm_a"],
                "arm_b": frame["arm_b"],
                "pooled": S.point_ratio(frame, strata_present),
                "per_stratum_n_matched": {
                    s: S.point_ratio(frame, (s,))["n_matched"] for s in frame["strata"]
                },
            }
            for name, frame in frames.items()
        },
        "strata_present": list(strata_present),
        "stratum_sizes": stratum_sizes,
    }
