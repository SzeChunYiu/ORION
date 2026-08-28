# FiberGuard R22 — prospectively frozen PMLB safe learned proposal ordering

Date frozen: 2026-08-27

Parent: #1512, Round 3 safe learned proposal-ordering mechanism (behind the
exact certificate shield); publication umbrella #1507; closure playbook #1541
section 2.

Status at this commit: **subject identity, rights review, corpus selection,
portfolio, landmarkers, meta-feature groups, split custody, cell/certificate
grammar, arms, gates, executor, and hostile tests are frozen before any PMLB
dataset byte (`*.tsv.gz` content) or generated model outcome is read**.
Metadata-only access before this freeze is exactly the access recorded in
`REPLACEMENT_SOURCE_STATUS.json` (repository/tree/licence/summary metadata,
per-dataset `metadata.yaml`, LFS pointer oids) plus this round's own freeze
table `FIBERGUARD_PMLB_R22_DATASET_FREEZE.json`.

## Mechanism (Round-3 language from #1512)

Learning may only propose refinement/order choices behind the exact certificate
shield. Learning may not change admissibility and may not claim conditional
validity. Concretely: at every state the exact finite-fibre shield computes the
certified-admissible portfolio set; learned (and control) scorers only rank
(i) which costly feature group to acquire next and (ii) which certified model
to commit to. A model outside the certified set can never be executed by any
learned arm; an empty certificate forces the registered fallback.

## Immutable permission-bearing subject

- repository: `https://github.com/EpistasisLab/pmlb.git`;
- commit: `7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68`;
- tree: `ca5d36e9093c2f7360db57198c8c0586a3217a60`;
- licence: repository-level MIT, `LICENSE` blob
  `ac14bc5ab72e5c2fc5643d879ad6bcc2be4d260a`;
- summary metadata: `pmlb/all_summary_stats.tsv` blob
  `88c393504f3ad6c354f5d178de181543878e7782`.

Data are retrieved and identity-checked (content SHA-256 against the pinned
LFS pointer oid), never vendored into this repository.

### Rights review (gate 2 of REPLACEMENT_SOURCE_STATUS.json)

The repository-level MIT licence governs the PMLB distribution. Per-dataset
`metadata.yaml` `source`/`publication` fields are recorded verbatim in the
freeze table: 19 of 45 candidate datasets carry a recorded source citation; the
remaining 26 carry PMLB's `None yet` placeholder. Frozen decision: the corpus
is used for internal scientific evaluation with PMLB citation only; no dataset
bytes are redistributed; no per-dataset rights claim beyond the repository MIT
distribution licence is asserted. Datasets are not renamed and remain
 attributable to PMLB.

## Corpus (gate 1)

`FIBERGUARD_PMLB_R22_DATASET_FREEZE.json` binds all 45 datasets selected by the
already-recorded metadata-only filter (non-deprecated, non-GAMETES,
classification, 200–2000 instances, 2–40 features, 2–6 classes, imbalance at
most 0.4) with, per dataset: the summary-metadata row, the LFS pointer oid
(content SHA-256) and size, the git blob of the pointer, and the
`metadata.yaml` blob. This reproduces `candidate_count = 45` exactly.

Mechanical load-time admissibility rule (fires before any outcome access): a
dataset whose rarest class has fewer than 5 members is excluded, because
stratified 5-fold evaluation cannot keep every fold class-complete; exclusions
are recorded by name and never silently dropped. After exclusions the corpus is
shuffled once with `numpy.random.default_rng(20260827).permutation` over the
sorted names and dealt round-robin into 9 outer folds (sizes differ by at most
one). Fold sizes and memberships are binding receipts.

## Task, endpoint, and costs

- Instances are datasets. The target is last-column `target`.
- Categorical/binary features are integer-coded by sorted unique string values;
  the target is coded by sorted unique labels. Missing cells stay missing.
- Portfolio (6, pinned `scikit-learn==1.9.0`, per-arm seeds derived by
  SHA-256 of `20260827|<dataset>|<arm>`):
  `logreg` = LogisticRegression(max_iter=2000),
  `knn5` = KNeighborsClassifier(n_neighbors=5),
  `dct` = DecisionTreeClassifier,
  `gnb` = GaussianNB,
  `rf300` = RandomForestClassifier(n_estimators=300, n_jobs=1),
  `hgb` = HistGradientBoostingClassifier.
- Endpoint per (dataset, model): mean over 3 repetitions x stratified 5-fold CV
  of `1 - balanced_accuracy_score`. Imputation is per-split column medians
  fitted on the training split only. Model fit+score wall seconds are recorded
  informationally in a separate environment-bound timings receipt; they never
  enter gates or byte-compared results.
- `VBS(dataset)` = portfolio minimum endpoint; excess of a commit is its
  endpoint minus VBS. There is no timeout/PAR convention in this domain.
- Acquisition charge unit = number of costly feature groups acquired (deterministic;
  0-3 per instance). Measured seconds are informational only. No invented
  quality-time exchange rate is used anywhere.

## Meta-feature groups (deterministic, dependency-free lattice)

`G0` is free (from the frozen metadata row): `[n_instances, n_features,
n_classes, imbalance]`. Costly groups are computed from dataset bytes:

- `G1` distribution (10 scalars, on the column-median-imputed full matrix):
  median feature std (ddof=0); median feature skewness (standardized third
  moment, zero-variance -> 0); median feature kurtosis (fourth moment, same
  convention); median feature min; median feature max; median
  distinct-value/instances ratio; global zero-cell fraction; zero-variance
  feature fraction; log10(instances/features); median feature IQR (linear
  interpolation quartiles).
- `G2` correlation (3 scalars): max |Pearson| over feature pairs; mean
  |Pearson| over feature pairs; mean over features of max over one-vs-rest
  classes of |Pearson(feature, indicator)|.
- `G3` landmark (3 scalars): balanced error of stump
  (DecisionTreeClassifier(max_depth=1)), `nn1` (KNeighborsClassifier(1)), and
  `ridgec` (RidgeClassifier(alpha=1.0)) under stratified 5-fold x 2 repetitions
  with train-split-fitted imputation. Landmarkers are disjoint from the
  portfolio.

States are subsets J of {G1, G2, G3} (G0 always acquired). All 8 states are
legal; acquisition order is what policies may learn.

## Exact certificate shield (learned-free)

Per fold, per state J: every scalar of the groups in J (G0 included) is
coarsened by one median split whose edge is the median over proposer-train
datasets (tie at edge -> lower bin). The cell of a dataset is its bin tuple.
Shield members of a cell are the shield-table datasets in that cell. With
`excess_a(z) = err_a(z) - min_b err_b(z)` on shield-table datasets:

- `wc_a(cell) = max over members of excess_a` (exact finite-fibre worst case);
- `A(cell, tau) = { a : wc_a(cell) <= tau }` when the cell has at least 2
  members, else the empty set;
- `F*` = single best portfolio model on the shield table (mean endpoint,
  lexical ties) — the registered fallback, always executable, uncertified.

Primary `tau = 0.02` balanced-error units (2 percentage points, the predeclared
materiality tolerance); the coverage-risk frontier reports
`tau in {0.00, 0.01, 0.02, 0.05, 0.10}`. Certificate transfer to held-out
datasets is measured, never assumed: the shield claims DEV-internal finite
bounds only.

## Split custody (9 outer folds, cyclic roles as in R21)

For test fold t (all 9 folds execute): proposer-train = folds t+1..t+4;
shield-table = folds t+5..t+7; threshold-select = fold t+8 (indices mod 9).
Proposers see proposer-train only; cell edges come from proposer-train only;
the shield table and F* come from shield-table only; learned-profile selection
and the shuffled control read threshold-select only; test outcomes are touched
only by final evaluation. Executors enforce these partitions with hostile
set-membership assertions.

## Arms (all behind the same shield unless stated)

1. `VBS` per-dataset oracle (upper anchor, no acquisition).
2. `SBS_SHIELD` = commit F* always (do-nothing anchor).
3. `SHIELD_FREE` = state G0 only; commit certified minimax
   `argmin_{a in A} wc_a` (lexical ties); empty -> F*.
4. `SHIELD_FULL` = acquire G1,G2,G3; same commit rule.
5. `STATIC_ADAPTIVE` (primary comparator): myopic exact walk. At state J,
   `commit_loss(J) = min_{a in A(c_J)} wc_a` (infinite when empty); for each
   legal g, `gain(g) = commit_loss(J) - commit_loss(J+g)`; acquire the
   argmax-gain group (lexical ties) while max gain > 1e-9, at most 3
   acquisitions, else commit certified minimax; if the commit set is empty
   acquire the lexical-first remaining group, and at the full state commit or
   fall back to F*.
6. `RANDOM_ADAPTIVE`: seeded coin-flip refinement control — at each state
   draw u ~ U(0,1) (seed text includes fold, dataset, state); u < 0.5 commits
   immediately, u >= 0.5 acquires the seeded-random-ranked first remaining
   group among refinements that keep a nonempty commit set (rank seed
   includes fold, dataset, state). Commit rule identical (exact minimax).
7. `VARIANCE_ADAPTIVE`: gain(g) = summed proposer-train variance of g's
   scalars (uncertainty-only ordering); commit rule identical (exact).
8. `LEARNED_KNN_{1,3,5,9}`: k-nearest-neighbour multi-output proposer per
   state (direct-difference distances; ties by (distance, dataset name);
   features z-scored by proposer-train moments) predicting the 6 portfolio
   endpoints; `commit_loss(J) = min_{a in A(c_J)} e_hat_a`, gains from the
   same myopic walk, commit `argmin_{a in A} e_hat_a`. Admissibility stays
   exact: learned scores can execute only certified models.
9. `LEARNED_RF300`: RandomForestRegressor(n_estimators=300, n_jobs=1) proposer,
   same walk.
10. `UNSHIELDED_KNN9`, `UNSHIELDED_RF300`: commit `argmin_a e_hat_a` at the
    full state with no certificate restriction (reference arms outside the
    shield).
11. `SHUFFLED_<learned>` for each of the five learned arms (hostile,
    threshold-select fold only): proposer trained on seeded-permuted
    proposer-train target rows (perm seed includes arm, fold, state).

The primary learned arm is selected among the five learned arms on the
threshold-select fold by lexicographic (mean excess, p95 excess, max excess,
name) of their threshold-select out-of-fold excesses.

## Primary test, gates, and terminals

Paired statistic: per dataset d (all folds, out-of-fold),
`diff(d) = excess_PRIMARY_LEARNED(d) - excess_STATIC_ADAPTIVE(d)`;
20,000-resample paired bootstrap over datasets (seed text
`ORION02_R22_PMLB_PROPOSAL_ORDERING_BOOTSTRAP_V1`), percentile 95% interval.
Reported for every arm: mean/p95/max excess, mean costly groups acquired,
certified-commit fraction, and violation rates among certified commits
(strict: realized excess > wc + 1e-9; tau: realized excess > tau + 1e-9).
Coverage = pooled fraction of test datasets whose full-state cell has >=2
members and non-empty certificate; the per-state coverage ladder and the
tau-frontier are reported.

Terminals, in precedence order:

1. `CANNOT_CHECK_PMLB_PROPOSAL_ORDERING_SOURCE_OR_RESOURCE` for retrieval,
   identity, schema, fold, parser, or resource failure (including
   metadata-vs-bytes mismatch);
2. `C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE` when pooled full-state
   non-trivial coverage at primary tau is below 5%;
3. `C_R22_PMLB_PROPOSAL_ORDERING_CERTIFICATE_INVALID` when the strict
   violation rate among certified commits exceeds 10%;
4. `C_R22_PMLB_PROPOSAL_ORDERING_VALUE` when coverage and validity gates hold,
   the primary learned mean excess is at most 95% of STATIC_ADAPTIVE's, the
   paired 95% upper endpoint is below zero, and mean costly groups acquired is
   not larger than STATIC_ADAPTIVE's;
5. `C_R22_PMLB_PROPOSAL_ORDERING_STRICT_BUT_NOT_MATERIAL` for a strict mean
   improvement without every material gate;
6. `C_R22_PMLB_PROPOSAL_ORDERING_NULL` for |mean diff| <= 1e-9;
7. `C_R22_PMLB_PROPOSAL_ORDERING_ADVERSE` otherwise.

## Hostile controls (all gating)

- hand-computed synthetic certificate fixture reproduces cells, wc, A, F*
  exactly;
- admissibility invariance: a hostile scorer ranking an uncertified model
  first can never execute it (synthetic fixture);
- shuffled-target proposers must not beat their honest counterparts on the
  threshold-select fold (tolerance 1e-9);
- per-fold custody set assertions (proposer rows == proposer-train names;
  shield rows == shield names; test name absent from both), including a
  hostile subtest that a test row inside fitting raises;
- VBS dominance: no arm beats per-dataset VBS beyond 1e-9;
- metadata audit: bytes-derived instances/features/classes equal the frozen
  metadata row for every dataset;
- determinism: two in-process executions over the frozen outcome table are
  identical; CI executes two full processes and requires byte identity across
  runners;
- distance computation uses direct differences (no norm-expansion BLAS
  algebra) with (distance, name) tie sorting.

## Authority

Corpus-complete closed-world evidence on the pinned subject only. A positive
terminal is bounded historical out-of-fold evidence for learned proposal
ordering behind this exact shield on PMLB; it is not production value,
deterministic pathwise safety, unseen-domain transfer, generic selector
superiority, external independence, novelty, journal authority, or submission
authorization. Null/adverse/no-coverage/invalid outcomes are permanent Round-3
evidence; after this round the three-mechanism budget of #1512 is exhausted and
the predeclared specialist fallback applies unless the result is positive.

No protected Task-3/P9 lane is touched.
