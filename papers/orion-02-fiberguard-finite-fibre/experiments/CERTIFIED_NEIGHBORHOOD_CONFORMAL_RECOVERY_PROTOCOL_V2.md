# ORION-02 C-NBR2 defect-only recovery protocol V2

Freeze date: 2026-08-27

Status at this commit: **implementation-repair protocol only; no corrected C-NBR2 outcome has been read or admitted.**

Base: live `main@0deff0ad44fc945b3d7d4755d8522105e5ccadc1`.

Pinned defective executor blob: `2608d414b2ef3e92d9f6ab3d9e3ce06d6b035cd8`.

Pinned scientific protocol: `CERTIFIED_NEIGHBORHOOD_CONFORMAL_PROTOCOL_V1.md`, unchanged.

## 1. Quarantined deviation

The frozen V1 protocol defines `d1(x)` as the Euclidean distance from query state `x` to its **nearest DEV-TRAIN anchor**. The merged executor instead computed

`d1 = distances[:, 0]`,

which is the distance to DEV-TRAIN row zero. The same column-zero deviation was used in the covered/uncovered geometry receipt. The error affects normalized calibration scores, conformal quantiles, Mondrian strata, held-out bounds, certificate coverage, and the nearest-anchor mechanism diagnosis.

The existing V1 result files remain immutable provenance for that defective execution. Their positive/null/adverse terminal is not scientific or manuscript authority.

## 2. Frozen defect-only repair

The recovery changes exactly two scientific expressions:

1. in `neighborhood_predictor`, set

   `d1 = distances[np.arange(len(phi_query)), neighbour_rows[:, 0]]`;

2. in the geometry receipt, set the nearest-anchor vector to

   `pairwise_distances(query, anchors).min(axis=1)`.

No scenario, source commit, feature representation, split, seed, model, alpha, epsilon, calibration rule, Mondrian rule, comparator, bootstrap, gate, or terminal is changed.

## 3. Mandatory hostile controls

Before outcome execution, the repaired subject must pass all of the following:

- a query whose nearest anchor is not column zero;
- equality with an independently computed rowwise minimum;
- invariance of `d1`, neighbor mean regrets, and selected base action under a joint permutation of anchor and regret rows;
- an anchor-order hostile case in which the defective column-zero value changes materially;
- exact source inspection proving both column-zero distance projections are absent;
- unchanged V1 protocol bytes.

## 4. Recovery execution

The corrected executor must run twice byte-identically under the V1 pinned environment and source inputs. The workflow must:

1. bind the exact repaired source commit before any result exists;
2. preserve the original V1 result bytes;
3. execute into temporary paths;
4. compare complete JSON, Markdown, and terminal bytes across two runs;
5. upload the complete raw result and environment receipt;
6. retain every registered V1 verdict (`CONFORMAL_INVALID`, `ADVERSE`, `CONFORMAL_NEIGHBORHOOD_REVIVED`, `VALID_WITHOUT_COVERAGE_OR_VALUE`);
7. commit a successor custody record only after execution.

## 5. Authority

Because the former defective result was exposed, the corrected run is

`OUTCOME_EXPOSED_DEFECT_ONLY_RECOVERY_CORROBORATION`.

It is not a new prospective first result. The scientific protocol remains prospective; only the implementation repair occurs after outcome exposure.

Even a positive corrected terminal would establish at most same-owner, one-scenario, marginal split-conformal evidence under the exact V1 protocol. It would not establish conditional routed-case validity, family-shift validity, deterministic fibre safety, external independence, production value, novelty, or journal authority.
