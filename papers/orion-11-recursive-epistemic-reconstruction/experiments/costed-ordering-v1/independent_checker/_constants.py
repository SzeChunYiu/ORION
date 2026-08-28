"""Frozen vocabulary for the ORION-11 costed-ordering independent checker.

Every constant here is transcribed from one of the three frozen documents
(PROTOCOL.json, EXPECTED_TERMINALS.json, TRACE_SCHEMA_V1.json). Nothing is
taken from the runner, the candidate policies, the production scorer or the
statistics module.

Where the frozen documents disagree with each other, the disagreement is
recorded explicitly below rather than silently resolved.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Exit codes. These are load-bearing and are NOT a pass/fail axis.
#
#   0 = CHECKED. The recomputed terminal is emitted. This includes every
#       UNFAVOURABLE terminal: a falsification that the checker successfully
#       computed is a *checked* result, not an error.
#   2 = CHECKED, and the checker DISAGREES with a supplied RESULT_V1.json.
#   3 = COULD NOT CHECK. Missing, contaminated or non-decomposing traces.
#
# "Could not check" is never reported as "checked and fine".
# --------------------------------------------------------------------------
EXIT_CHECKED = 0
EXIT_DISAGREEMENT = 2
EXIT_CANNOT_CHECK = 3

# --------------------------------------------------------------------------
# Strata. PROTOCOL.json world_family.strata is authoritative for the ids.
#
# FROZEN-DOCUMENT DISCREPANCY #1
#   PROTOCOL.json         spells the A4 stratum  "violate_A4_cost"
#   TRACE_SCHEMA_V1.json  spells the A4 stratum  "violate_A4_nonnegative_cost"
# Both denote the same stratum by role. The checker accepts either spelling,
# canonicalises to the PROTOCOL spelling, records which spelling it saw, and
# REFUSES if both spellings appear in one trace file (ambiguous identity).
# --------------------------------------------------------------------------
STRATUM_THEOREM_VALID = "theorem_valid"
STRATUM_RATIO_ALIGNED = "ratio_aligned"
STRATUM_A1 = "violate_A1_noninterference"
STRATUM_A2 = "violate_A2_veto_monotonicity"
STRATUM_A3 = "violate_A3_safety"
STRATUM_A4 = "violate_A4_cost"

CANONICAL_STRATA = (
    STRATUM_THEOREM_VALID,
    STRATUM_RATIO_ALIGNED,
    STRATUM_A1,
    STRATUM_A2,
    STRATUM_A3,
    STRATUM_A4,
)

STRATUM_ALIASES = {
    "violate_A4_nonnegative_cost": STRATUM_A4,  # TRACE_SCHEMA_V1.json spelling
}

# Strata on which the theorem's assumptions all hold.
THEOREM_VALID_STRATA = (STRATUM_THEOREM_VALID, STRATUM_RATIO_ALIGNED)

# Assumption-violation control strata (PROTOCOL role=ASSUMPTION_VIOLATION_CONTROL).
VIOLATION_STRATA = (STRATUM_A1, STRATUM_A2, STRATUM_A3, STRATUM_A4)

# A3 (safety) holds everywhere except the stratum that violates it. Derived,
# not hardcoded as a list: each violation stratum breaks exactly one
# assumption (PROTOCOL world_family.strata assumptions_violated; THEORY H5).
A3_HOLDS_STRATA = tuple(s for s in CANONICAL_STRATA if s != STRATUM_A3)

# --------------------------------------------------------------------------
# Arms.
#
# FROZEN-DOCUMENT DISCREPANCY #2
#   PROTOCOL.json        arms[]  enumerates 8 arms, including
#                                "random_unsafe_ablation".
#   TRACE_SCHEMA_V1.json row.arm_id enumerates 7, omitting it.
# TRACE_SCHEMA_V1.json's own not_a_protocol_amendment block lists "arm set"
# among the items it does NOT touch, so its enumeration is an incomplete
# restatement, not an amendment: PROTOCOL governs the arm set.
#
# Consequence for refusal policy: a missing input refuses ONLY if a gate
# actually consumes it. random_unsafe_ablation is consumed by no gate G1-G7
# and the trace schema told the runner not to serialise it, so its absence is
# a warning, never a coverage failure.
# --------------------------------------------------------------------------
ARM_ORACLE = "exact_dp_oracle"
ARM_ORION = "orion_level_monotone"
ARM_FAITHFUL = "faithful_active_voi"
ARM_GLOBAL_FLAT = "global_flat_voi"
ARM_PC_GREEDY = "gain_per_cost_greedy"
ARM_COST_GREEDY = "cost_greedy_repair"
ARM_RANDOM_SAFE = "random_safe_ablation"
ARM_RANDOM_UNSAFE = "random_unsafe_ablation"

# Arms both frozen documents agree on, excluding the restricted oracle.
# These must appear on EVERY stratum.
REQUIRED_UNRESTRICTED_ARMS = (
    ARM_ORION,
    ARM_FAITHFUL,
    ARM_GLOBAL_FLAT,
    ARM_PC_GREEDY,
    ARM_COST_GREEDY,
    ARM_RANDOM_SAFE,
)

# Restricted arm: PROTOCOL says it "Runs on theorem_valid and ratio_aligned
# strata only". Appearing anywhere else is a coverage failure.
ARM_ORACLE_STRATA = THEOREM_VALID_STRATA

# Present in PROTOCOL, absent from TRACE_SCHEMA, consumed by no gate.
OPTIONAL_ARMS = (ARM_RANDOM_UNSAFE,)

KNOWN_ARMS = REQUIRED_UNRESTRICTED_ARMS + (ARM_ORACLE,) + OPTIONAL_ARMS

# Arms whose absence blocks a gate, mapped to the gates that consume them.
GATE_CONSUMED_ARMS = {
    ARM_ORION: ("G1", "G2", "G3", "G4", "G5", "G6", "G7"),
    ARM_FAITHFUL: ("G1", "G3", "G5"),
    ARM_PC_GREEDY: ("G6", "G7"),
    ARM_ORACLE: ("G4",),
}

# --------------------------------------------------------------------------
# Cost accounting (PROTOCOL cost_accounting; TRACE_SCHEMA row.cost).
# --------------------------------------------------------------------------
COST_COMPONENTS = ("inspection", "intervention", "reopening")
COST_FIELDS = COST_COMPONENTS + ("total",)
BUDGET_CEILING = 4.0
DECOMPOSITION_TOLERANCE = 1e-9

# --------------------------------------------------------------------------
# Registered margins and thresholds (PROTOCOL gates).
# --------------------------------------------------------------------------
G1_NONINFERIORITY_MARGIN = -0.01
G2_FORBIDDEN_CEILING = 0.0
G3_COST_RATIO_THRESHOLD = 0.80
G4_DP_GAP_MULTIPLIER = 1.10
G6_PARITY_RATIO = 1.0

# --------------------------------------------------------------------------
# Statistics (PROTOCOL statistics).
#
# FROZEN-DOCUMENT DEFECT #3
#   PROTOCOL.json statistics.interval_method reads
#     "stratified percentile bootstrap, 10000 resamples, seed frozen here"
#   but NO seed value appears anywhere in PROTOCOL.json,
#   EXPECTED_TERMINALS.json, TRACE_SCHEMA_V1.json or THEORY.md.
#
# The checker therefore declares its own default, overridable with
# --bootstrap-seed, and records bootstrap_seed_source in the output so no
# reader mistakes it for a frozen value. Exact numeric agreement with the
# runner's bootstrap is not achievable in any case (identical integer seeds
# still diverge under different draw orders and RNG APIs), so --compare
# treats interval bounds as tolerance fields, not exact fields.
#
# Because the seed is not frozen, the checker additionally probes verdict
# stability across SEED_PROBE_COUNT extra seeds. A verdict that flips with
# the seed is not a measured verdict: it is reported seed_sensitive and
# refused (exit 3), never silently reported at the default seed.
# --------------------------------------------------------------------------
BOOTSTRAP_RESAMPLES = 10000
BOOTSTRAP_SEED_DEFAULT = 20260828
BOOTSTRAP_SEED_SOURCE_DEFAULT = "CHECKER_DEFAULT__PROTOCOL_DECLARED_SEED_ABSENT"
BOOTSTRAP_BLOCK = 1000
SEED_PROBE_COUNT = 4
ALPHA = 0.05
CI_LEVEL = 0.95

# --------------------------------------------------------------------------
# Trace purity (TRACE_SCHEMA: "No aggregation, no derived statistics, no gate
# outcomes"; hard invariant: "No row carries a gate outcome, a bootstrap
# interval or a terminal. If one does, the trace is contaminated and the
# checker must refuse it.").
#
# Policy: schema keys are the whitelist. An unknown key is contamination only
# when it names a derived/adjudicated quantity (denylist below); any other
# unknown key is a warning. A checker that refuses a benign extra field on
# its first real run gets switched off.
# --------------------------------------------------------------------------
ROW_REQUIRED_KEYS = (
    "world_id",
    "stratum",
    "arm_id",
    "seed",
    "protected_root_task_success",
    "forbidden_high_level_mutation",
    "cost",
    "budget_exceeded",
    "actions",
    "terminated_reason",
)
ACTION_REQUIRED_KEYS = ("step", "kind", "level", "target", "cost_component", "cost")

# Matched case-insensitively against key names at any nesting depth.
CONTAMINATION_KEY_TOKENS = (
    "gate",
    "terminal",
    "verdict",
    "bootstrap",
    "resample",
    "confidence",
    "ci_low",
    "ci_high",
    "ci_upper",
    "ci_lower",
    "ucb",
    "lcb",
    "p_value",
    "pvalue",
    "holm",
    "adjusted_p",
    "significance",
    "conclusion",
    "decision",
    "analysis",
    "aggregate",
    "summary",
    "noninferior",
    "falsif",
)
# Whole-key matches (G1..G7 and friends) that the substring tokens would miss.
CONTAMINATION_EXACT_KEYS = tuple(f"g{i}" for i in range(1, 8)) + (
    "passed",
    "failed",
    "pass",
    "fail",
    "mean_cost",
    "cost_ratio",
    "success_rate",
    "forbidden_rate",
)

# --------------------------------------------------------------------------
# Independence self-check. The checker asserts at runtime that none of these
# module-name fragments has been imported into the interpreter.
# --------------------------------------------------------------------------
FORBIDDEN_IMPORT_FRAGMENTS = (
    "faithful_comparator_policies",
    "run_orion11",
    "orion11_runner",
    "production_scorer",
    "scorer",
    "policies",
    "candidate_policies",
    "statistics_module",
)
