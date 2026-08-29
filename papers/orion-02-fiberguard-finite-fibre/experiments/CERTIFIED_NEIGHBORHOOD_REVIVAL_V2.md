# ORION-02 C-NBR2 — defect-only frozen rerun disposition (V2)

> Quarantine repair-gate rerun per issue #1495. The V1 run
> (`results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V1.json`, PR #1493) implemented
> `d1(x)` as `distances[:, 0]` — the distance to DEV-TRAIN **row 0** — instead of the
> protocol §4 definition (distance to the single **nearest** anchor); the same defect
> class sat in the coverage diagnostic. This V2 execution repairs only that defect:
> same source digests, same protocol SHA-256, same splits (148/120/28/148 official-fold;
> 168/130/38/128 family-disjoint), same arms, same frozen parameters (SEED 20260818,
> BOOTSTRAP_SEED 20260819, BOOTSTRAPS 10000, ALPHA 0.10, MU_K 16, SIGMA_OFFSET 1.0,
> EPSILON 5000, MONDRIAN_STRATA 3, HOSTILE 4.0, KNN 16, RF 300, PCA 10, MIN_CAL 20).
> Repair committed pre-outcome (`39762b215`); receipts written mode `x` to V2 paths;
> V1 receipts preserved untouched. Machine-readable source of truth:
> `results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V2.json` (git SHA `39762b215`).

## Repair and its guard

- `d1 = np.take_along_axis(distances, neighbour_rows[:, :1], axis=1).ravel()`
  (rowwise nearest-anchor); coverage diagnostic `[:, 0]` → `.min(axis=1)`.
- New hostile anchor-order self-tests (random + reversed anchor permutations) assert
  recorded `d1`/`m`/`a_base`/`q_hat`/coverage/violations are permutation-invariant;
  verified to FAIL on the defective line (executor aborts at the self-test, no
  receipt written), GREEN on the repair.

## What the corrected d1 revealed

| Quantity | V1 (defective) | V2 (repaired) |
|---|---:|---:|
| pooled q_hat (official / family) | 3348.0 / 3375.2 | **25091.6 / 17230.3** |
| pooled certified radius 5000/q_hat | 1.49 / 1.48 | **0.199 / 0.290** |
| median "nearest-anchor" d1 (held-out) | 14.12 / 16.83 (row-0 distance) | **3.14 / 9.62 (true nearest)** |
| implied geometric gap | ~9.5x / ~11.4x | **15.8x / 33.1x** |
| PCA10 q_hat; median true d1 | 4173.5 / 4030.6 | 31496.5 / 25828.0; d1 1.51 / 4.34 (gap 9.5x / 22.4x) |

The defect made `sigma = 1 + d1` ~4–5x too large, which deflated the normalized
scores and the calibrated constant together: with true nearest-anchor distances the
residual scale per distance unit is ~5–7.5x larger, `q_hat` rises accordingly, and the
certified radius **shrinks** to 0.2–0.3 units. The certificate certifies nothing:
coverage at eps 5000 (and 500) is **0.0000** on both splits for all three relations
(`CNF_POOLED`, `CNF_POOLED_PCA10`, `CNF_MONDRIAN3`), all three degenerate to SBS
(`SBS − CNF_POOLED = 0.00 [0.0, 0.0]`), and the exact-equality control is 0.0000
(5x = 0.0000). Mondrian mid/far strata fail closed (cal 8/6 and 7/12 → `q_hat = inf`
where `k > n`). Bound validity holds conservatively (held-out violation 0.0000 pooled,
both splits); the 4x-alpha hostile control violates 0.378 / 0.750, so the audit is
sensitive. Self-test GREEN (synthetic violation rate 0.0675 ≤ tolerance 0.1201;
hostile 644 > 135; anchor-order invariance GREEN).

## Does the geometric-blocker story survive?

**Yes — strengthened, not rescued.** The specific V1 numbers ("radius 1.5 vs median
14.1/16.8, a ~10x gap") were defect artifacts, but on TRUE nearest-anchor distances the
gap is **larger, not smaller** (15.8x official, 33.1x family-disjoint, pooled; 9.5x /
22.4x PCA10): the conformal constant inflates with the smaller true `sigma` faster than
the nearest distance shrinks. The blocker is confirmed geometric — anchor-set spacing
against residual PAR10 per distance unit — and the split-conformal lever does not close
it in either direction of the defect.

## Honest terminal (as recorded by the executor)

- Split verdicts: `VALID_WITHOUT_COVERAGE_OR_VALUE` (SPLIT_OFFICIAL_FOLD),
  `VALID_WITHOUT_COVERAGE_OR_VALUE` (SPLIT_FAMILY_DISJOINT).
- Overall verdict: **`VALID_WITHOUT_COVERAGE_OR_VALUE`**;
  disposition `EXECUTED__FROZEN_PROTOCOL_APPLIED`.
- This confirms the V1 terminal verdict on corrected mechanics: the C-NBR lane
  boundary result stands (coverage tax of per-instance inductive certification at
  these costs, two mechanisms, controls in place). Descriptive context, not in the
  verdict: `KNN16 − CNF_POOLED = −4576 [−7808, −1397]` (official),
  −2080 [−6292, +1850] (family); `RF_ROUTER − CNF_POOLED` negative on both.

## Claim boundary

One bounded public scenario (ASlib SAT11-HAND-ALGO fold + family-disjoint split);
no ASlib-wide, SAT-wide, cross-domain, or selective-prediction superiority claim.
The conformal bound is a finite-sample **marginal** guarantee under exchangeability —
not conditional-on-covariates validity, and the family-disjoint panel is a transfer
observation under that boundary. Certificate coverage is not action authority.
`CERTIFIED_NEIGHBORHOOD_REVIVAL_V1.md` and the V1 result files remain immutable
provenance of the defective execution, per #1495.
