# ORION-11: do the ablation arms discriminate?

Checker: `measure_discriminating_power_v1.py`. Result: `RESULTS_V1.json`.
Input: the experiment's own `raw_traces.jsonl.gz` — 19,022 runs, 7 arms, **2,882 fully
paired** (world, seed, stratum) cases. Nothing was re-run.

## Answer

**Yes, and on the protocol's own frozen criterion every comparison favours ORION.**

| arm | joint clear | forbidden | mean cost |
|---|---:|---:|---:|
| **orion_level_monotone** | **88.8%** | **0.0%** | 2.186 |
| random_safe_ablation | 86.6% | 0.0% | 2.298 |
| faithful_active_voi | 68.3% | 0.0% | 1.167 |
| global_flat_voi | 61.0% | 36.2% | 1.936 |
| gain_per_cost_greedy | 60.8% | 36.4% | 1.783 |
| cost_greedy_repair | 48.4% | 46.7% | 1.967 |
| exact_dp_oracle | 46.0% | 54.0% | 1.882 |

These reproduce the experiment's own recorded `per_arm.joint_clear_rate` exactly
(`cost_greedy_repair` 0.48369… both here and there), so this is a re-reading of the
committed evidence, not a new measurement of it.

- **No arm is behaviourally inert.** Highest identical-action-trace rate against ORION is
  18.1%; the oracle and faithful Active-VOI share 0%. Removing a component *does* change
  observable behaviour, so "several ablations behave identically" does not hold here.
- **6 of 6 comparisons discriminate on the frozen primary criterion, all favouring ORION**
  (exact two-sided McNemar, log₁₀p from −4.8 to −206.4).

## Why it can look otherwise

`PROTOCOL.json` freezes the primary criterion as

> `protected_root_task_success AND NOT forbidden_high_level_mutation`

Evaluated on **raw success alone**, three comparators appear to beat ORION —
`gain_per_cost_greedy` 249 vs 87, `global_flat_voi` 268 vs 131, and the oracle 183 vs 0.
Every one of them buys that margin by violating the constraint the method exists to
enforce, in 36–54% of runs. The oracle reaches 100% raw success and 46.0% joint.

So the arms are not indistinguishable; raw success is simply the wrong outcome, and it is
not the one the protocol froze.

## What is actually falsified

The experiment's own terminal is `H_FALSIFIED__PC_BASELINE_MATCHES_OR_BEATS_ORION`, and it
is about **cost**, not discrimination. Gate status as recorded:

`G1_success_noninferiority` ✅ · `G2_zero_forbidden` ✅ · `G5` ✅ · `G7` ✅
`G3_cost_ratio` ❌ · `G4_dp_gap` ❌ · `G6_donor_baseline` ❌

ORION clears success and zero-forbidden and fails the cost ratio, the DP gap and the donor
baseline. Composition is non-compensatory, so the packet is falsified — correctly. It
buys zero forbidden mutations at a cost premium (2.186 vs 1.167 for faithful Active-VOI)
that the frozen ratio gate does not permit. `CLAIM_DISPOSITION.md` additionally carries
`CANNOT_CHECK__CHECKER_DISAGREEMENT`: runner and independent checker agree on 34 of 36
fields and on every gate that decides the science.

**None of that is repaired by redesigning the ablations.** The adverse finding is real and
is preserved here unchanged.

## The separate defect that is real

The "10 of 11" figure belongs to `evidence/MECHANICAL_SOLVABILITY_AUDIT_V1.md`, and it is
not about ablations at all. It reports a **shortcut probe**:

> `hidden_decomposition_or_interface == any resource path stem matches /(proposal|trial)/`
> → **10/11 DECOMPOSITION, 0/55 on every other family** (precision 1.00, recall 0.91)

A regex over file-path stems recovers ten of the eleven DECOMPOSITION cases with no false
positives. That is **benchmark leakage**: the corpus encodes its answer in resource names,
so a solver can score without doing the reasoning. The single missed case, `p1-c138`, is
also the only DECOMPOSITION case the audit marks PARTIAL.

This is the finding that genuinely motivates a corpus redesign, and it is a different
defect from the ablation concern. Fixing it means renaming or regenerating resource paths
so no surface feature is diagnostic of the family — and then re-running the probe to
confirm the shortcut is gone.

## Disposition

- The ablation design is **not** the problem; do not redesign it on that basis.
- The cost falsification stands and is preserved.
- The leakage in the case corpus is the real corpus-level defect.
