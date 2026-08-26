# ORION-21 selective compile-tolerance placement protocol V1

**Programme:** NR-12 of `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`
**Purpose:** revive the `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET` negative by changing the
placement POLICY, not the frozen battery: a pre-registered, train-only compile-tolerance
selector decides per responsibility whether compilation is placed, and the same frozen
family battery is re-run under that selective placement.

## Chronology and non-retuning statement

This protocol is frozen before the selective runner is executed. It does not modify, retune
or supersede `P11_QUERY_FAMILY_PHASE_V1` (protocol frozen in #978; negative bound in #996,
folded in #1016). The frozen battery elements reused byte-for-byte:

- dataset: scikit-learn digits, `d=64`;
- ten binary responsibilities `q_j(x) = 1 iff digit(x)==j`;
- outer `StratifiedKFold(5, shuffle=True, random_state=20261121)`;
- `StandardScaler` on training source state; `SelectKBest(f_classif, k=16)` per query;
- access classes LINEAR `LogisticRegression(C=1, solver=lbfgs, max_iter=5000)`,
  RBF `SVC(C=1, kernel=rbf, gamma=scale)`, KNN `KNeighborsClassifier(n_neighbors=7,
  weights=distance)`;
- per-query tolerance `compiled_mean >= universal_mean - 0.02`;
- the V1 negative (`COMPILE-ALL` fails 3/10, 5/10, 5/10) stands unedited.

The V1 attribution that motivates the lever (verified read-only from the frozen primary
JSON, `nr12_verify_attribution_v1.py`): the compiled-vs-universal delta partitions 77.4%
responsibility main effect / 2.4% access main effect / 20.2% interaction; five
responsibilities (q1, q3, q5, q8, q9) are compile-intolerant under EVERY access class and
three (q0, q4, q6) under all; pooled delta correlates +0.51 (Pearson) with universal
difficulty. Compile-tolerance is therefore a per-responsibility property that a train-only
selector can in principle detect. The selector below is frozen from this mechanism, not
from any V1 test-cell value.

## Selector rule (frozen)

For each outer fold `f` (training part only) and each responsibility `q`:

1. inner `StratifiedKFold(n_splits=5, shuffle=True, random_state=2026112207)` over the
   outer training part;
2. on each inner-training part: fit `StandardScaler`, fit `SelectKBest(f_classif, k=16)`
   on the binary responsibility; compiled inner state = selected 16 standardized
   coordinates; universal inner state = all 64 standardized coordinates;
3. train the frozen LINEAR access model on both states
   (seed `2026112500 + f*10 + q`), score balanced accuracy on the inner-validation part;
4. place compilation for `(f, q)` iff `mean_inner(compiled) >= mean_inner(universal) - 0.02`
   — the SAME frozen tolerance as the battery gate, evaluated on train-internal
   held-out data only.

The selector uses LINEAR only: it is the primary gate class and the cheapest probe. No
test fold, no other access class, and no V1 test outcome participates in placement.
Placement is decided per (fold, query): each outer fold is one independent deployment
draw with its own training data.

## Selective placement execution

For fold `f`, query `q`, access class `a`:

- if placed: serve from the COMPILED state exactly as in V1 (identical pipeline, seeds,
  selected coordinates);
- if not placed: serve from the UNIVERSAL state exactly as in V1.

The frozen battery is re-executed unmodified by the same code path; the only new degree of
freedom is the placement bit. Retained (non-placed) queries therefore contribute delta
exactly 0 by construction — the gate content below is selector precision plus non-vacuity,
and a compile-nothing placement is explicitly refused as answer laundering (P11B rule).

## Gate (frozen; positive terminal `P11_SELECTIVE_PLACEMENT_V1_SUPPORTED`)

All components evaluated on the frozen outer seed `20261121` battery:

1. **Non-vacuity:** every outer fold places at least one responsibility (`|S_f| >= 1`).
2. **Family quality (the original V1 frozen rule, on the selectively-placed system):**
   LINEAR support `>= 8/10`; `max(RBF, KNN)` support `>= 8/10`; all ten reported, where
   per-query support is `placed_mean >= universal_mean - 0.02`.
3. **No family below its frozen baseline:** selective support counts must satisfy
   LINEAR `>= 3`, RBF `>= 5`, KNN `>= 5` (the V1 observed counts).
4. **Resource identities for the selective system** (deterministic, no free parameters):
   - selective stored state per example `= 64 + 16*|S_f|` floats — strictly greater than
     the universal 64 whenever non-vacuous (memory never wins under selective placement;
     the win axis is service touches only);
   - per-placed-query LINEAR break-even horizon `= floor(n_train_f*64/48) + 1` service
     examples (48 = 64−16 touch saving per served example per placed query, one compiler
     fit charge `n_train_f*64`), fold-mean expected 1917 at V1's mean train size 1437.6;
   - future-query arrival tax: one compiler fit iff the arriving responsibility would be
     placed by the same train-only rule, zero otherwise — the tax is paid only on the
     placeable subset, never family-wide.
5. **Honesty endpoints (reported, not gated):** per access class, selector false
   positives (placed but test-intolerant) and false negatives (declined but
   test-tolerant); per-fold placement size `|S_f|`; placement stability across folds.
6. **Leakage/determinism:** scaler, selector and compilers see training folds only;
   byte-identical replay of two consecutive full runs.

A positive licenses ONLY: "on digits, a train-only inner-CV tolerance selector places
compilation on a subset such that the selectively-placed family meets the frozen 8/10
quality bar that compile-all fails". It does NOT relabel the V1 negative, claim
family-scale compile-all support, transfer beyond digits, or alter the V1 resource
identities.

## Secondary generalization read (pre-registered, non-gating)

Repeat the full selective battery on outer seeds `20261122`, `20261123`, `20261124`
(inner selector seed unchanged), reporting gate components 1–3 and 5 per seed. The primary
terminal is decided on the frozen `20261121` battery only; the secondary seeds exist to
show whether the selector rule is fold-draw-specific.

## Independent second checker

A structurally independent implementation (manual NumPy scaling, manual binary-ANOVA
F-ranking with explicit stable tie-breaking, manual balanced accuracy, independent
inner-fold bookkeeping) must agree with the primary runner on every placement bit,
support count, placed mean (≤1e-12), resource identity, and the terminal.

## Endpoints

- placement bit per (fold, query) and per-fold sizes `|S_f|`;
- selectively-placed vs universal per-query means and deltas for all three access classes;
- selective support counts vs the V1 frozen counts;
- selector FP/FN per access class;
- selective resource vector (memory gap, break-even, arrival tax);
- secondary-seed gate components;
- deterministic replay digests.
