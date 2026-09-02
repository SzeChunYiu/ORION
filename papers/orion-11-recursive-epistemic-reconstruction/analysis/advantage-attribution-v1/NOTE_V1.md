# ORION-11: which conjunct produces the advantage?

**Checker:** `attribute_advantage_v1.py` · **Result:** `RESULTS_V1.json`
**Terminal:** `ADVANTAGE_ATTRIBUTABLE_TO_SAFETY_CONJUNCT`
**Scientific authority delta:** `NONE`. This narrows the paper. It adds no
experiment, rescues no claim, and leaves both falsifications standing.

## The gap this closes

`analysis/discriminating-power-v1` establishes that **six of six** ablation
comparisons discriminate on the frozen primary criterion, all favouring ORION.
That criterion is a conjunction:

```
protected_root_task_success AND NOT forbidden_high_level_mutation
```

so "favours ORION" does not say which conjunct produced the margin.
`REFRAMED_CONTRIBUTION_V2.md` records exactly that gap as
`ATTRIBUTION_INCOMPLETE`: the audit "cannot distinguish donor-owned ordering
mathematics from ORION-side ordering".

Decomposing the same committed comparison set by outcome answers it. Nothing was
re-run: this reads `discriminating-power-v1/RESULTS_V1.json` and the costed
packet's `per_arm` block, both already committed.

## The decomposition

| comparator | forbidden rate | raw success alone | frozen primary |
|---|---:|---|---|
| `exact_dp_oracle` | 54.0% | **COMPARATOR** — 0 / 183, log₁₀p −54.8 | ORION — 925 / 174 |
| `cost_greedy_repair` | 46.7% | **no discrimination** — 245 / 222, log₁₀p −0.51 | ORION — 1383 / 218 |
| `gain_per_cost_greedy` | 36.4% | **COMPARATOR** — 87 / 249, log₁₀p −18.5 | ORION — 1051 / 244 |
| `global_flat_voi` | 36.2% | **COMPARATOR** — 131 / 268, log₁₀p −11.2 | ORION — 1065 / 264 |
| `faithful_active_voi` | **0.0%** | ORION — 902 / 310, log₁₀p −66.7 | *identical* |
| `random_safe_ablation` | **0.0%** | ORION — 139 / 75, log₁₀p −4.84 | *identical* |

Counts are discordant pairs, ORION-better / comparator-better.

## What it says

**The separation is exact.** Every comparator ORION beats *only* under the joint
criterion has a nonzero forbidden-mutation rate. The two arms whose forbidden
rate is zero produce **bit-identical discordant counts under both views**,
because for them the second conjunct is vacuous. There is no arm that ORION
beats on raw success while making forbidden mutations, and none that it fails to
beat on raw success while making none.

So the measured advantage is **constituted by the safety conjunct**, not by
repair-ordering competence. Three consequences follow, and all three are adverse:

1. **On raw task success ORION is not the best policy.** Against the exact DP
   oracle it wins **zero** of 183 discordant worlds. Against two further arms it
   loses, and against a third it is statistically indistinguishable. Only two of
   six comparisons favour it, and both are the arms that make no forbidden
   mutations at all.
2. **Against a safety-matched control the margin nearly collapses.**
   `random_safe_ablation` is random subject to the same safety constraint. ORION
   still beats it — 139 to 75, log₁₀p −4.84 — but that is roughly two orders of
   magnitude weaker than the −113 to −206 it posts against unsafe arms. Most of
   the "6 of 6" headline is the constraint, not the ordering.
3. **It does not restore anything.** Comparative necessity remains falsified by
   R4; the economy hypothesis remains falsified by the costed packet at 1.82× the
   faithful Active-VOI comparator on the matched set. This note touches no gate,
   no terminal and none of the paper's `forbidden_promotions`.

## Why an adverse post-hoc decomposition is admissible here

Post-outcome discretion is forbidden in this programme because it manufactures
*favourable* terminals — choosing a criterion after seeing which one wins. This
analysis runs the other way: it takes the frozen criterion as given, reports a
strictly harsher reading alongside it, and narrows the claim. No gate is
re-read, no arm is re-executed, no threshold is moved.

The honest limitation is that a decomposition is not an experiment. It shows
that the safety conjunct carries the margin *on this world family*; it does not
show that a differently-designed ordering would fare better, and it does not
license any claim about ordering value in general.

## Controls

The checker fails closed rather than silently passing:

- it re-asserts all seven published `joint_clear_rate` values and exits **3**
  (`CANNOT_CHECK`) if any has moved, so a changed source table is not read as a
  new result;
- it requires both outcome views on every comparator, exiting **3** if either is
  absent;
- it exits **2** on a genuine finding — a safety-matched arm whose views
  disagree, an unsafe arm favouring ORION on raw success, or the frozen
  criterion no longer favouring ORION in all six.

`test_attribute_advantage_v1.py` builds a mutant for each of those and requires
the matching exit code, plus a control that the committed `RESULTS_V1.json`
equals a fresh run. **8 passed.** The upstream discriminating-power checker was
re-run first and reproduces its committed `RESULTS_V1.json` byte-identically, so
the input is the table the published note described.

## Scope

`costed-ordering-v1` only — the sole ORION-11 experiment that emits per-run
traces. Nothing here extends to `r4-faithful-comparator-v1`, which ships no
per-run traces and therefore cannot be decomposed this way.
