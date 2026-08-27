# ORION-02 C-NBR2 corrected recovery result

Date: 2026-08-27

Immutable repaired subject: `240d9f455b22ea53e8c18173d123222d4276f36b`.

Execution run: `33042986210`.

Corrected result SHA-256: `0f5fb813ac9baa25efbba795b18452af36eeb47a3878f7181b9f063ac08a5c21`.

Terminal:

`VALID_WITHOUT_COVERAGE_OR_VALUE`

Authority:

`OUTCOME_EXPOSED_DEFECT_ONLY_RECOVERY_CORROBORATION`

## Defect repaired

The V1 executor used distance to DEV-TRAIN row zero where the frozen protocol required distance to the nearest DEV-TRAIN anchor. The recovery changes only the two distance projections identified before execution:

- predictor normalization now uses the rowwise nearest-neighbor index;
- the geometry receipt now uses the rowwise minimum distance.

The V1 protocol bytes, source corpus, folds, models, alpha, epsilon, conformal quantile, Mondrian rule, comparators, bootstrap, gates, and terminal vocabulary are unchanged.

Outcome-blind hostile controls show that the repaired distance equals the independent rowwise minimum and that distance, mean neighbor regret, and base action are invariant under a joint permutation of anchor and regret rows. The defective column-zero expression is absent.

## Corrected result

The corrected executor ran twice byte-identically. Both registered splits return `VALID_WITHOUT_COVERAGE_OR_VALUE`.

| Split | Exact-equality coverage | Pooled certificate coverage at epsilon 5000 | Pooled held-out violation | RF-router mean PAR10 | CNF pooled mean PAR10 |
|---|---:|---:|---:|---:|---:|
| Official folds | 0 | 0 | 0 | 17530.8555 | 27196.3961 |
| Family-disjoint | 0 | 0 | 0 | 17677.7996 | 24063.1779 |

The nearest-anchor repair materially changes normalized geometry and calibration. For example, official-fold pooled `q_hat` changes from about 3347.98 in the quarantined execution to 25091.58 after repair, while median uncovered distance changes from about 14.12 to 3.14. The scientific conclusion is not byte-equivalent to the defective run even though the top-level terminal string is unchanged.

The corrected pooled and PCA10 certificates satisfy the registered marginal violation criterion only by abstaining on every held-out instance at the primary tolerance. They therefore provide no deployed certificate coverage and no decision-value improvement over the single-best fallback. The learned RF comparator remains materially better in mean PAR10, but it is an empirical selector, not an exact certificate.

## Disposition

The repaired experiment supports the narrow statement:

> A correctly normalized split-conformal neighborhood envelope can satisfy the registered marginal violation criterion while remaining operationally vacuous because its held-out coverage is zero.

It does not revive the representation-neighborhood law as an inductive exact certificate. It does not establish routed-case conditional validity, family-shift validity, deterministic fibre safety, production value, external independence, novelty, or journal authority.

The old V1 result remains immutable provenance with authority `QUARANTINED_IMPLEMENTATION_DEVIATION`; it must not be cited for numerical geometry or calibration values.
