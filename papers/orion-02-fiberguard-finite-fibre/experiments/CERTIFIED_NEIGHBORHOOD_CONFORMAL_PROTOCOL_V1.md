# ORION-02 (FiberGuard C) — C-NBR2 conformal certified neighborhood protocol V1

- schema: `ORION02.CNBR2.Protocol.v1`
- status: `FROZEN_BEFORE_OUTCOME_ACCESS`
- frozen_at: 2026-08-27
- lane: `PAPER_PORTFOLIO_REFACTOR_PLAN_V1.md` §3, lane C-NBR (revival iteration 2;
  compute on LUNARC)
- parent evidence: C-NBR V1
  (`CERTIFIED_NEIGHBORHOOD_RESULTS_V1.md`, LUNARC job 3544034) returned
  `CERTIFICATE_INVALID` on both pre-registered splits. Diagnosed mechanisms:
  (1) the pairwise-slope-quantile Lipschitz constants (`L_a` ~ 4400–9300 PAR10
  per standardized-distance unit) confine coverage to near-duplicates and give
  zero coverage on family-disjoint held-out scenarios; (2) the q0.95
  pairwise-slope quantile is a distribution-level rule that violates 14.3% on
  its own calibration set — it never carried per-instance validity. This
  protocol is the documented revival path: **split-conformal calibration of the
  certificate**. It is a new frozen protocol, not a retuning of V1.
- authoring rule: this file and the executor
  `certified_neighborhood_conformal.py` are committed before any outcome is
  computed. The executor implements this protocol exactly; any deviation is a
  defect.

## 1. Research question

Does replacing the distribution-level pairwise-slope quantile with
split-conformal per-instance calibration of the neighborhood certificate
produce a certified set that is (a) valid at the pre-registered level,
(b) non-empty beyond near-duplicate structure — including on family-disjoint
untouched scenarios, where V1 certified nothing — and (c) of paid decision
value over its own frozen fallback, at acceptable coverage? If not, the
boundary result (coverage tax of per-instance inductive certification at
these costs, now on two independent mechanisms with controls) is compiled as
ORION-02's manuscript-grade contribution.

## 2. Subject and custody

Identical to C-NBR V1 §2 (unchanged, restated for completeness):

- Upstream `coseal/aslib_data@551b22beef8df17de59286b4822ef720e0aa4d6f`,
  scenario `SAT11-HAND-ALGO`, in-tree at
  `papers/paper-xx-executable-research-core/benchmark/aslib_sat11_hand_algo/`
  with the six file digests pinned in the frozen harness protocol
  `ASLIB_SAT11_PROTOCOL_V1.json`; the live harness loader verifies every
  digest before any outcome is read. The frozen harness (loader, `impute`,
  `fit_router`) is imported and reused unchanged.
- Unit: ASlib `(instance_id, repetition)`. PAR10 accounting: observed runtime
  for `ok` runs, `10 x cutoff` (cutoff = 5000 s) otherwise. Feature
  acquisition charge `c_T = 0` (scenario records none), the most favorable
  setting for a covering relation; no operational claim from the absent
  charge.

## 3. Splits (identical to C-NBR V1, reused verbatim for comparability)

The V1 hash rules are reused **exactly**, so every split in this experiment
contains the same instances as V1's:

- **SPLIT_OFFICIAL_FOLD**: DEV = official `cv.arff` folds 1–5, HELD-OUT =
  folds 6–10.
- **SPLIT_FAMILY_DISJOINT**: family = first four path components of
  `instance_id`; families sorted by `sha256(family + ':cnbr-split-b')`,
  assigned greedily by instance count targeting 60/40, zero family overlap.
- Within DEV, an instance is DEV-CALIBRATION iff
  `sha256(instance_id + ':cnbr-inner') mod 5 == 0`, else DEV-TRAIN.

Two-stage honesty: the base relation (neighborhood predictor, normalization,
strata) is frozen on DEV-TRAIN only; the conformal quantile is calibrated on
DEV-CALIBRATION only (disjoint from the relation-freeze data and from
evaluation); HELD-OUT instances never enter any fitted or calibrated object.

## 4. Representations, predictor, and normalization

Imputation/standardization follow the V1 policy computed on DEV-TRAIN only
(median imputation, mean/std standardization, std floor 1e-12). Frozen
representations, both as in V1: `NBR_FULL` (115-dim standardized) primary and
`NBR_PCA10` (first 10 PCs of DEV-TRAIN, `svd_solver="full"`) coarsening.
Metric: Euclidean distance in the transformed space.

**Base neighborhood predictor (relation, DEV-TRAIN only).** For
`mu = CNBR2_MU_K` nearest DEV-TRAIN anchors (by representation distance) of
instance `x`:

- `m_a(x)` = mean over those anchors of the regret `R(a,z) = C(a,z) - C*(z)`
  (the kNN-regret estimate; at `mu = 16` this is exactly the KNN16 score
  vector);
- `d1(x)` = distance to the single nearest anchor;
- difficulty normalization `sigma(x) = CNBR2_SIGMA_OFFSET + d1(x)`.

`a_base(x) = argmin_a m_a(x)` is the predictor's action (selection depends on
DEV-TRAIN outcomes only, never on calibration or held-out outcomes).

## 5. Split-conformal calibration (the revival mechanism)

**Nonconformity score** (computed on DEV-CALIBRATION, per representation):

`s_j = ( R(a_base(x_j), x_j) - m_{a_base}(x_j) ) / sigma(x_j)`.

Because `m`, `sigma`, and `a_base` are DEV-TRAIN-only functions and
DEV-CALIBRATION outcomes are disjoint, the scores are exchangeable with the
held-out score of any fresh instance under the same split. Let `n` be the
calibration count and `alpha` the miscoverage level.

**Pooled quantile (primary arm CNF_POOLED):** with `k = ceil((n+1)(1-alpha))`,
`q_hat` = the `k`-th smallest score (1-based); if `k > n`, `q_hat = +inf`
(fail-closed: the bound never certifies at this calibration size).

**Mondrian-by-distance (secondary arm CNF_MONDRIAN3):** DEV-TRAIN
nearest-anchor distances are split at their 1/3 and 2/3 quantiles into
NEAR/MID/FAR strata; each held-out/calibration instance is assigned by its
`d1` against those frozen cut points; a separate `q_hat_s` is calibrated per
stratum with the same finite-sample rule (`n` = stratum calibration count;
`k > n` ⇒ that stratum's quantile is `+inf`, i.e. it never certifies — the
honest small-sample behavior, not silent pooling).

**Certificate.** `U(x) = m_{a_base}(x) + q_hat * sigma(x)` (per-arm quantile).
Certified set `K_eps = { x : U(x) <= eps }`. On `K_eps` the policy runs
`a_base(x)`; outside it abstains to the frozen fallback (SBS on DEV-TRAIN);
abstention is counted in attempt coverage (abstain = PAR10, unsolved).

**Validity claim (stated precisely).** Split conformal gives the
finite-sample marginal guarantee
`P( R(a_base(x), x) <= U(x) ) >= 1 - alpha` over the calibration + test draw
under exchangeability. It is per-instance in the sense that every instance
carries its own bound; it is NOT conditional-on-covariates validity, and no
such claim is made. Because the action selection `a_base` is part of the
fixed (DEV-TRAIN-only) predictor, no post-selection validity correction is
needed. The guarantee is audited empirically (Section 7); the audit, not the
claim, is what the gate reads.

**Hostile control.** The quantile recomputed at level `1 - CNBR2_HOSTILE_ALPHA_FACTOR*alpha`
(default 4x alpha, i.e. over-confident) must show an elevated held-out
violation rate for the audit to be considered sensitive.

## 6. Arms (identical information and accounting)

All arms evaluate the same HELD-OUT instances under harness PAR10 accounting
with the same statewise VBS. All fitting is DEV-only.

| Arm | Definition |
|---|---|
| `SBS` | frozen fallback: single solver minimizing DEV-TRAIN mean PAR10 |
| `VBS` | statewise virtual-best (unattainable ceiling; descriptive) |
| `RF_ROUTER` | harness frozen router, reused unchanged (300 trees, seeds `20260818 + solver_index`, DEV-TRAIN) |
| `KNN16` | 16 nearest DEV-TRAIN anchors in `NBR_FULL`, solver minimizing neighbor mean PAR10 — the uncertificated neighborhood heuristic |
| `CNF_POOLED` | Section 5 pooled arm on `NBR_FULL`, primary epsilon 5000 — PRIMARY |
| `CNF_POOLED_PCA10` | pooled arm on `NBR_PCA10`, primary epsilon 5000 |
| `CNF_MONDRIAN3` | Mondrian-by-distance arm on `NBR_FULL`, primary epsilon 5000 |
| `EXACT_EQ` | negative control as in V1: exact equality of 115 imputed features rounded to 6 decimals vs DEV-TRAIN keys |

## 7. Metrics and validity audit

Per arm and split, on HELD-OUT instances: mean PAR10, solve rate, attempt
coverage, catastrophic rate, mean PAR10 regret vs VBS; certificate coverage
`q_eps = |K_eps|/n_held` at `{500, 5000}`; **bound-violation audit**
`P(R(a_base(x),x) > U(x))` with Wilson 95% interval, plus the same audit on
DEV-CALIBRATION and for the hostile control; median nearest-anchor distance
of covered vs uncovered instances (near-duplicate diagnostic); paired
instance-level bootstrap 95% intervals (10000 resamples, frozen seeds) for
`SBS - CNF_POOLED` and the descriptive `KNN16 - CNF_POOLED`,
`RF_ROUTER - CNF_POOLED`.

## 8. Pre-registered gates and verdicts

Let `q` = HELD-OUT coverage of `CNF_POOLED` at primary epsilon 5000 on a
split, `v` = that arm's HELD-OUT bound-violation rate, `D = mean_PAR10(SBS) -
mean_PAR10(CNF_POOLED)` with paired bootstrap 95% CI, and `q_eq` = EXACT_EQ
coverage.

- `bound_valid := v <= alpha` (alpha = 0.10, the V1 validity level)
- `coverage_producing := q >= 0.10 AND q >= 5 * q_eq`
- `value_over_fallback := D > 0 AND lower(CI(D)) > 0`

Verdict per split (overall verdict = the SPLIT_FAMILY_DISJOINT verdict if the
two disagree):

1. `CONFORMAL_INVALID` — not `bound_valid`.
2. `ADVERSE` — bound valid but `upper(CI(D)) < 0`.
3. `CONFORMAL_NEIGHBORHOOD_REVIVED` — all three properties hold.
4. `VALID_WITHOUT_COVERAGE_OR_VALUE` (null/boundary) — otherwise.

All four outcomes are reportable. Under discipline rule 3 of this lane, a
terminal overall verdict of `CONFORMAL_INVALID` or
`VALID_WITHOUT_COVERAGE_OR_VALUE` — after this conformal revival already
replaced the V1 mechanism — is compiled as the ORION-02 boundary result in
`CERTIFIED_NEIGHBORHOOD_REVIVAL_V1.md`; no third mechanism is invented in this
protocol. KNN16/RF_ROUTER comparisons are descriptive dominance context and
do not enter the verdict.

## 9. Parameters (env-configurable; defaults justified)

| Env var | Default | Justification |
|---|---|---|
| `CNBR2_SEED` | 20260818 | harness SEED (V1) |
| `CNBR2_BOOTSTRAP_SEED` | 20260819 | V1 bootstrap seed, distinct from SEED |
| `CNBR2_BOOTSTRAPS` | 10000 | V1 bootstrap count |
| `CNBR2_ALPHA` | 0.10 | the V1 pre-registered validity level; conformal miscoverage target matches it so gates are comparable |
| `CNBR2_MU_K` | 16 | the KNN16 neighborhood width; at 16 the base predictor is the strong R14 comparator, isolating the certificate as the only difference |
| `CNBR2_SIGMA_OFFSET` | 1.0 | keeps `sigma` PAR10-per-unit interpretable and finite at duplicates; the conformal quantile absorbs the scale |
| `CNBR2_EPSILON_LEVELS` | 500,5000 | V1 levels (0.1x, 1x cutoff) |
| `CNBR2_PRIMARY_EPSILON` | 5000 | V1 primary epsilon |
| `CNBR2_MONDRIAN_STRATA` | 3 | NEAR/MID/FAR terciles on DEV-TRAIN distances |
| `CNBR2_HOSTILE_ALPHA_FACTOR` | 4.0 | over-confidence hostile control (V1 used 0.25x on L; the analogue here is inflating alpha) |
| `CNBR2_KNN_K` | 16 | V1 comparator k |
| `CNBR2_RF_TREES` | 300 | harness RF size (reused unchanged) |
| `CNBR2_PCA_COMPONENTS` | 10 | V1 coarsening dimensionality |
| `CNBR2_EQ_ROUND` | 6 | V1 control rounding |
| `CNBR2_MIN_CAL` | 20 | fail-closed calibration-count floor (pooled) |
| `CNBR2_SPLIT_A_DEV_FOLDS` | 1,2,3,4,5 | V1 fold split |
| `CNBR2_SPLIT_B_TARGET_DEV_FRACTION` | 0.6 | V1 family-disjoint balance target |

## 10. Receipts

The executor writes
`results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V1.json` and a generated
`results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V1.md` from the same
in-memory result, both in mode `x`. The JSON binds: this protocol's SHA-256,
the executor's own SHA-256, the harness protocol SHA-256, the six source-file
digests (verified at load), resolved parameters, environment versions, git
SHA (from `CNBR2_SOURCE_GIT_SHA`), per-split full metrics, calibration
receipts (score quantiles, strata sizes), validity audits, hostile control,
self-test results, and the computed verdicts. No held-out statistic enters
any fitted or calibrated object. A synthetic self-test must pass before the
receipt is written and the job fails closed otherwise: on exchangeable
synthetic regret data the pooled conformal bound's empirical violation rate
on 2000 fresh instances must be `<= alpha + 3*sqrt(alpha(1-alpha)/2000)`
(three-sigma tolerance for a marginal guarantee), and the hostile
(4x alpha) bound must violate strictly more than the honest bound.

## 11. Nonclaims

- One bounded public scenario; no ASlib-wide, SAT-wide, cross-domain,
  algorithm-selection, selective-prediction or LLM-routing superiority claim.
- The conformal bound is a finite-sample marginal guarantee under
  exchangeability of DEV-CALIBRATION with HELD-OUT within a split; it is not
  conditional-on-covariates validity and not a proof under covariate shift.
- The VBS is an unattainable accounting ceiling, not a baseline.
- Certificate coverage is not action authority; abstention remains a routing
  terminal.
- `paper_authority_delta: NONE`; this receipt informs the ORION-02 C-NBR
  revival gate only.
