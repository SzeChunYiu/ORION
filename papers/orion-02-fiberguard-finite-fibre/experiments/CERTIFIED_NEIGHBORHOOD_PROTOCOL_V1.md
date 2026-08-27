# ORION-02 (FiberGuard C) — C-NBR certified neighborhood protocol V1

- schema: `ORION02.CNBR.Protocol.v1`
- status: `FROZEN_BEFORE_OUTCOME_ACCESS`
- frozen_at: 2026-08-27
- lane: `PAPER_PORTFOLIO_REFACTOR_PLAN_V1.md` §3, lane C-NBR (compute, LUNARC)
- parent evidence: R14 exact-equality transfer refutation (held-out exact-signature
  coverage 3.22%/5.08% on SAT12-ALL) and the R15 coverage-tax/Lipschitz theory
  (Theorem C-R15.9 training-anchor upper certificate). This protocol is the
  successor gate R14 named: freeze a coverage-producing coarsening/neighborhood
  relation on disjoint development data and test it on untouched held-out data
  against strong baselines.
- authoring rule: this file and the executor `certified_neighborhood.py` are
  committed before any outcome is computed. The executor implements this
  protocol exactly; any deviation is a defect.

## 1. Research question

Can a neighborhood relation that certifiably covers held-out scenarios —
unlike the refuted exact-equality relation — be frozen on disjoint development
data, remain valid on untouched held-out scenarios, and add paid decision value
over its own frozen fallback and over strong learned baselines, on the live
ASlib SAT11-HAND-ALGO harness subject?

## 2. Subject and custody

- Upstream: `coseal/aslib_data@551b22beef8df17de59286b4822ef720e0aa4d6f`,
  scenario `SAT11-HAND-ALGO`, in-tree at
  `papers/paper-xx-executable-research-core/benchmark/aslib_sat11_hand_algo/`
  with the six file digests pinned in
  `papers/paper-xx-executable-research-core/benchmark/ASLIB_SAT11_PROTOCOL_V1.json`.
  The live harness loader verifies every digest before any outcome is read.
- The harness protocol `ASLIB_SAT11_PROTOCOL_V1.json` is FROZEN and is not
  modified. This experiment extends alongside it: it imports the harness module
  and reuses its digest-verified loader and its frozen RF router unchanged.
- Unit: ASlib `(instance_id, repetition)` as in the harness. PAR10 accounting:
  observed runtime for `ok` runs, `10 x cutoff` (cutoff = 5000 s) otherwise.
- Feature acquisition charge: SAT11-HAND-ALGO records no feature-runstep costs
  in this tree, so the acquisition charge `c_T = 0`. The R15 coverage-tax
  identity then reduces to `E[L_T - L_0] = -q_T E[G_T | S_T]`; this reduced form
  is the most favorable setting for a covering relation and is stated as such.
  No operational claim is made from the absent charge.

## 3. Splits (outcome-blind, deterministic, frozen)

Two disjoint DEV / HELD-OUT splits are computed before any model is fit:

- **SPLIT_OFFICIAL_FOLD** (the harness fold discipline): DEV = official
  `cv.arff` folds 1–5, HELD-OUT = folds 6–10. The fold column is
  scenario-provided and outcome-blind.
- **SPLIT_FAMILY_DISJOINT** (untouched scenarios): family = first four path
  components of `instance_id` (e.g. `SAT11/crafted/skvortsov/battleship`).
  Families are sorted by `sha256(family + ':cnbr-split-b')` and assigned
  greedily to the currently lighter side by DEV-instance count, targeting a
  60/40 DEV/HELD-OUT instance balance with ZERO family overlap. Held-out
  families are untouched: no instance from them contributes to any fitted
  object.

Within DEV, an inner deterministic split (mirroring the harness inner-fold
discipline): an instance is DEV-CALIBRATION iff
`sha256(instance_id + ':cnbr-inner') mod 5 == 0`, else DEV-TRAIN. All fitted
objects (imputation, standardization, PCA, Lipschitz constants, SBS fallback,
RF router, kNN selector, exact-equality keys) use DEV-TRAIN only, except the
per-action Lipschitz constants, which use DEV-CALIBRATION pairs only.
HELD-OUT instances never enter any fitting statistic.

## 4. Representations and metric (frozen before outcomes)

Imputation and scaling follow the harness policy computed on DEV-TRAIN only:
feature-median imputation (median 0 if a feature is all-NaN in DEV-TRAIN),
then mean/std standardization (std clipped below at 1e-12 → 1.0). Two frozen
representations:

- `NBR_FULL` (primary): the full 115-dimensional standardized feature vector.
- `NBR_PCA10` (declared coarsening): the first 10 principal components of the
  DEV-TRAIN standardized matrix (`svd_solver="full"`, deterministic), a
  dimension-reducing coarsening of the same representation.

Metric `d` for both: Euclidean distance in the (transformed) representation
space.

## 5. Certified neighborhood relation (Theorem C-R15.9)

Let `C(a,x)` be the PAR10 cost of solver `a` on state `x`, `C*(x)` the
statewise virtual-best cost, and regret `R(a,x) = C(a,x) - C*(x)`. For
DEV-TRAIN anchor set `T` and a per-action regret-Lipschitz constant `L_a`:

`U_T(a,x) = min_{z in T} [ R(a,z) + L_a * d(Phi(x), Phi(z)) ]`.

Certified action `a_cert(x) = argmin_a U_T(a,x)`; certificate value
`U(x) = min_a U_T(a,x)`; certified set `K_eps = { x : U(x) <= eps }`.
On `K_eps` the policy runs `a_cert(x)`; outside it abstains to the frozen
fallback (SBS on DEV-TRAIN), and the abstention is counted in the harness's
attempt-coverage accounting (abstain = PAR10, unsolved).

**Authority of `L_a` (declared, training-only):** computed from DEV-CALIBRATION
pairwise slopes `|R(a,z_i) - R(a,z_j)| / max(d(Phi(z_i),Phi(z_j)), 1e-9)`,
taking the quantile at `beta = 0.95`. Pairs at distance `< 1e-9` are excluded
from the quantile and counted; if such a pair has differing regret the
representation has a duplicate-point degeneracy that is reported (the true
constant there is unbounded). This is a probabilistic calibration constant
with stated authority, not a proof; its validity is therefore audited
empirically (Section 7). A hostile under-estimated control (`L_a * 0.25`) is
run alongside and must show an elevated violation rate for the audit to be
considered sensitive.

## 6. Arms (identical information and accounting)

All arms are evaluated on the same HELD-OUT instances with the same PAR10
accounting and the same statewise VBS baseline. All fitting is DEV-only.

| Arm | Definition |
|---|---|
| `SBS` | frozen fallback: single solver minimizing DEV-TRAIN mean PAR10 |
| `VBS` | statewise virtual-best solver (unattainable ceiling; descriptive) |
| `RF_ROUTER` | the harness's frozen router, reused unchanged: per-solver `RandomForestRegressor` on `log1p(PAR10)`, 300 trees, `max_features=sqrt`, `min_samples_leaf=2`, seeds `20260818 + solver_index`, fit on DEV-TRAIN |
| `KNN16` | transparent learned selector: 16 nearest DEV-TRAIN anchors in the standardized `NBR_FULL` space (`k = min(16, n_train)`), choose the solver minimizing mean PAR10 over the neighbors — the neighborhood heuristic WITHOUT a certificate (R14's comparator class) |
| `NBR_CERT_FULL` | Section 5 relation on `NBR_FULL`, primary epsilon 5000 |
| `NBR_CERT_PCA10` | Section 5 relation on `NBR_PCA10`, primary epsilon 5000 |
| `EXACT_EQ` | negative control (R14's refuted relation on this subject): exact equality of the 115 imputed feature values rounded to 6 decimals; covered iff the signature occurs in DEV-TRAIN, action = best mean-PAR10 solver over the matched anchors, else fallback |

## 7. Metrics and validity audit

Per arm and split, on HELD-OUT instances:

- mean PAR10, solve rate, attempt coverage, catastrophic rate (cost == PAR10),
  mean PAR10 regret vs VBS;
- certificate coverage `q_eps = |K_eps| / n_held` at epsilon levels
  `{500, 5000}` (0.1x and 1x cutoff);
- **certificate validity audit**: empirical violation rate
  `P( R(a_cert(x), x) > U(a_cert(x), x) )` on HELD-OUT with a Wilson 95%
  interval, plus the same audit on DEV-CALIBRATION and for the hostile
  under-estimated control;
- paired instance-level bootstrap 95% intervals (10000 resamples, frozen seed
  20260819) for `SBS - NBR_CERT` mean PAR10 and for the descriptive
  comparisons `KNN16 - NBR_CERT`, `RF_ROUTER - NBR_CERT`.

## 8. Pre-registered gates and verdicts

Let `q` be HELD-OUT certificate coverage at the primary epsilon 5000 for the
primary relation `NBR_CERT_FULL`, `v` the HELD-OUT certificate violation rate,
`D = mean_PAR10(SBS) - mean_PAR10(NBR_CERT_FULL)`, `CI(D)` its paired
bootstrap 95% interval, and `q_eq` the EXACT_EQ coverage.

- `coverage_producing := q >= 0.10 AND q >= 5 * q_eq`
- `certificate_valid := v <= 0.10`
- `value_over_fallback := D > 0 AND lower(CI(D)) > 0`

Verdict (per split; overall verdict = the SPLIT_FAMILY_DISJOINT verdict if
they disagree, since it is the untouched-scenario test):

1. `CERTIFICATE_INVALID` — not `certificate_valid` (on either split).
2. `ADVERSE` — certificate valid but `upper(CI(D)) < 0` (worse than its own
   fallback with interval excluding zero).
3. `CERTIFIED_NEIGHBORHOOD_POSITIVE` — all three properties hold.
4. `COVERAGE_WITHOUT_VALUE` (null) — otherwise.

Positive, null and adverse outcomes are all reportable; the verdict is
reported verbatim with the numbers, not softened. Comparisons against KNN16
and RF_ROUTER are descriptive dominance context (R14/R16 established learned
baselines as strong); they do not enter the verdict because the gate's value
question is paid value over the relation's own fallback, and learned-selector
dominance is already established doctrine.

## 9. Parameters (env-configurable; defaults justified)

| Env var | Default | Justification |
|---|---|---|
| `CNBR_SEED` | 20260818 | harness SEED |
| `CNBR_BOOTSTRAP_SEED` | 20260819 | frozen, distinct from harness seed |
| `CNBR_BOOTSTRAPS` | 10000 | harness bootstrap count |
| `CNBR_INNER_MODULUS` | 5 | harness inner-fold count |
| `CNBR_SLOPE_QUANTILE` | 0.95 | standard calibration quantile; authority declared in §5 |
| `CNBR_EPSILON_LEVELS` | 500,5000 | 0.1x and 1x cutoff |
| `CNBR_PRIMARY_EPSILON` | 5000 | one cutoff unit of certified regret |
| `CNBR_KNN_K` | 16 | R14's frozen comparator k |
| `CNBR_RF_TREES` | 300 | harness RF size (reused unchanged) |
| `CNBR_PCA_COMPONENTS` | 10 | declared coarsening dimensionality |
| `CNBR_EQ_ROUND` | 6 | decimal rounding for the exact-equality control signature |
| `CNBR_HOSTILE_FACTOR` | 0.25 | hostile under-estimated constant control |
| `CNBR_MIN_CAL_PAIRS` | 100 | fail-closed calibration-pair floor |
| `CNBR_SPLIT_A_DEV_FOLDS` | 1,2,3,4,5 | half of the official folds |
| `CNBR_SPLIT_B_TARGET_DEV_FRACTION` | 0.6 | family-disjoint balance target |

## 10. Receipts

The executor writes `results/CERTIFIED_NEIGHBORHOOD_RESULT_V1.json` and a
generated `results/CERTIFIED_NEIGHBORHOOD_RESULT_V1.md` from the same
in-memory result, both in mode `x`. The JSON binds: this protocol's SHA-256,
the executor's own SHA-256, the six source-file digests (verified at load),
the resolved parameters, environment versions, git SHA (from
`CNBR_SOURCE_GIT_SHA`), per-split full metrics, validity audits, hostile
control, self-test results, and the computed verdicts. No held-out statistic
enters any fitted object. A synthetic self-test (exactly-Lipschitz ground
truth: zero violations with the true constant; strictly positive violations
with an under-estimated constant) must pass before the receipt is written, and
the job fails closed otherwise.

## 11. Nonclaims

- One bounded public scenario; no ASlib-wide, SAT-wide, cross-domain,
  algorithm-selection, selective-prediction or LLM-routing superiority claim.
- The calibrated `L_a` is not a proof; validity is an audited empirical
  property of this run, reported with intervals.
- The VBS is an unattainable accounting ceiling, not a baseline.
- Certificate coverage is not action authority; abstention remains a routing
  terminal.
- `paper_authority_delta: NONE`; this receipt informs the ORION-02 gate only.
