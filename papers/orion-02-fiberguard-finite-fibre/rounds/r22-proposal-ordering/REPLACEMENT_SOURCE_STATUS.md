# ORION-02 Round-3 replacement-source status

Status: `RESEARCH_ONLY__NOT_FROZEN__NO_SOURCE_DATA_BYTES_ACCESSED`

## Preferred candidate: PMLB

The best untouched candidate found so far is
[`EpistasisLab/pmlb`](https://github.com/EpistasisLab/pmlb) at:

- commit `7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68`
- tree `ca5d36e9093c2f7360db57198c8c0586a3217a60`
- repository-level MIT license blob
  `ac14bc5ab72e5c2fc5643d879ad6bcc2be4d260a`
- summary-metadata blob
  `88c393504f3ad6c354f5d178de181543878e7782`

Only repository/commit/tree/license/summary metadata has been accessed. No
dataset bytes and no generated model outcomes have been accessed.

A deterministic metadata-only filter currently yields 45 classification
datasets: non-deprecated, non-GAMETES, 200--2000 instances, 2--40 features,
2--6 classes, and imbalance at most 0.4. This is a **candidate universe**, not a
freeze and not a scientific result.

PMLB is preferred because it is outside ASlib, has immutable public Git
objects, supports dataset-level held-out evaluation, and provides raw
prediction tasks rather than already-generated algorithm-selection outcomes.

## Gates before any data retrieval

1. Bind the exact selected dataset/LFS objects.
2. Review each selected dataset's rights and provenance; repository MIT alone
   is not final author/legal authority for every donor dataset.
3. Freeze the model portfolio, randomness, dataset folds, feature groups,
   acquisition charges, balanced-error endpoint, exact finite shield,
   proposal-order baselines, and disjoint terminals.
4. Add hostile synthetic tests, pinned dependencies, and a freeze-only workflow
   that cannot retrieve dataset bytes.
5. Commit the complete pre-outcome freeze before any data or outcome access.

Auto-sklearn benchmark metadata is deferred because its quality endpoint and
time-valued feature costs are not yet semantically aligned. SATzilla is rejected
for this round because a sufficiently clear repository-license binding was not
established and the family adds algorithm-selection prior-art pressure.

Round 3 has not been executed. Protected Task-3/P9 is untouched.
