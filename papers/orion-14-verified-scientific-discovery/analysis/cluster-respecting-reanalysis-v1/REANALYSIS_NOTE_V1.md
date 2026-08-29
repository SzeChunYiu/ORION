# ORION-14 — cluster-respecting reanalysis of the protected campaign

Campaign run `31968809206`. RUN_QUEUE item **P0.3**. Checker:
`check_cluster_respecting_reanalysis_v1.py`; machine-readable result: `RESULTS_V1.json`.

## The question

The published H1 interval is computed over **cases**. The campaign varies its
adversarial conditions by **attack family**. If verdicts are constant within a family,
the case count overstates the number of independent observations and the interval is
too narrow. This note establishes what the effect looks like at the family unit.

## 1. The published aggregate reproduces exactly

H1 is `ORION − provenai-citation-fidelity-influence` on false-promotion rate over the
**12 families other than `CLEAN_POSITIVE`** (a false promotion is undefined on a family
whose correct terminal *is* promotion):

| | value |
|---|---|
| ORION false-promotion rate | 0.000 |
| comparator rate (180/360) | 0.500 |
| reproduced H1 | **−0.500** |
| published H1 | **−0.500** |

Exact match. The comparator is not chosen here — it is the one the campaign artifact
names in its own `strongest_frozen_comparator` field. The checker aborts with a distinct
exit code if this reproduction ever stops holding, because a reanalysis that cannot
recover the published number is not evidence about that number.

## 2. Within-family constancy is measured, not assumed

Across the case rows carrying a family label: **130 (system, family) cells, 1,500 rows,
0 cells with more than one distinct `authority_terminal`.** Verdicts are constant within
a family, so the family — not the case — is the independent unit.

**Scope, stated plainly:** family labels are published for **150 of 420 cases**. The
constancy above is measured on those 150. For the remaining **270** the label is absent
from the public manifest, so constancy is **not directly verifiable**; the checker records
`CANNOT_CHECK_DIRECT_CONSTANCY` for them and infers no clustering on their behalf. The
`family_summary` rates are degenerate (every cell exactly 0 or 1) across all 420, which is
consistent with constancy campaign-wide, but consistency is not measurement and is not
claimed as such.

## 3. The effect survives at the clustering unit

Independent clusters: **12**. Of these, **6 are discordant and all 6 favour ORION**;
6 are tied (both systems at zero).

Exact two-sided randomisation test over family-label assignment — null: *ORION's advantage
is unrelated to which attack family it faces* — gives **p = 0.03125**. Ties are excluded,
as they carry no directional information.

A randomisation null is used rather than a Bernoulli sign test on purpose: with degenerate
0/1 cells there is no within-cell sampling variation, so the honest null is over which
families ORION faces, not over repeated draws of a noisy measurement.

Cluster bootstrap (20,000 resamples of **families**, seed 20260829): **95% CI
[−0.750, −0.250]**, excluding zero.

## 4. What changes, and what does not

**Does not change:** the sign, the direction, and the significance of H1 against the named
strongest comparator. The claim survives.

**Does change:** the precision. The published half-width is 0.0528, consistent with a
case-level N = 360 (normal approximation gives 0.0517). At the clustering unit the
normal half-width is **0.2829 — 5.48× wider**. Any statement that leans on the tightness
of the published interval rather than on the sign of the effect is not supported at the
unit the campaign actually varies.

The defensible form of the claim is therefore: *the H1 effect retains its sign and
direction against the named strongest comparator at the pre-registered clustering unit,
with 12 independent clusters and exact p = 0.031* — not a statement about ±0.05 precision.

## 5. Context that belongs with any use of this campaign

- `repeat_count = 5`: the 420 cases are 84 base cases × 5 repeats. Repeats are not
  independent observations either.
- `human_rubric_triggered_cases = 0` against `mechanical_gold_cases = 420`: **no case in
  this campaign received human adjudication.** Every terminal is mechanical.
- `retained_error_case_count = 2370` of 4,200 rows — retained, as the campaign's own
  null/false-positive/false-negative preservation flag asserts.

## Reproduce

```bash
python3 check_cluster_respecting_reanalysis_v1.py            # full, 20k bootstrap
python3 check_cluster_respecting_reanalysis_v1.py --smoke    # fast, 200 reps
```

Exit codes: `0` PASS · `1` FAIL · `3` CANNOT_CHECK · `4` REPRO_FAILED.
