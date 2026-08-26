# FiberGuard R14 result — exact equality is a transductive certificate, not an inductive selector

Date: 2026-08-26

Prospective protocol commit: `346f55216b788bdbe60f229da099375190dda5f6`

Workflow run/job: `33012492715` / `98322103716`

Issue receipt: `#1386` comment `5430973130`

Full result SHA-256: `b50e4ec5ed065b3884019d65be5901bb78c1be011ba2a73cef77c0bf76321391`

Observed terminal:

`FIBERGUARD_ASLIB_HELDOUT_R14_PARTIAL_MEAN_ONLY`

## What was prospectively tested

Before any held-out outcome, R14 froze two panels on the pinned SAT12-ALL corpus:

1. the benchmark's official ten-fold split, using exactly repetition 1;
2. a five-fold identifier-derived source-family split with 219 complete families and zero family overlap.

Every fold selected among all 513 dependency-closed feature-step representations using training runtimes only. The R11 `{Pre,lobjois}` representation was retained without retuning. Held-out signatures absent from training used the frozen training-only global robust fallback. All arms paid recorded feature cost and used one common statewise virtual-best PAR10 oracle.

The complete audit was executed twice and the result, terminal text, and issue comment were byte-identical. The workflow verified source blobs, split coverage, zero family overlap, training-only representation selection, common-oracle accounting, fail-closed authority flags, and artifact hashes.

## Decisive result

The exact equality-fibre policy does **not** transfer as an inductive solver selector.

### Official benchmark split

The training-selected exact representation achieved:

- mean total excess `5380.232187112763`;
- p95 `12001.98`;
- maximum `12370.140000000001`;
- catastrophic wrong-action rate `0.4454770755885997`;
- exact-signature held-out coverage only `52/1614 = 0.0322180916976456`.

This is a small mean improvement over the no-feature robust arm (`5448.31466542751`), which explains the registered `PARTIAL_MEAN_ONLY` terminal. It is not competitive with the training single-best solver (`2838.5681350681534`) or the frozen-information 16-NN arm (`1465.0932775712515`). The kNN catastrophic rate is `0.11957868649318464`, versus `0.4454770755885997` for the exact policy.

### Zero-family-overlap split

The training-selected exact representation achieved:

- mean total excess `5341.5854337050805`;
- p95 `12001.95`;
- maximum `12370.140000000001`;
- catastrophic wrong-action rate `0.4423791821561338`;
- exact-signature coverage `82/1614 = 0.05080545229244114`.

It again improves only slightly over no-feature robust (`5448.31466542751`) and remains much worse than the training single-best solver (`2838.5681350681534`) and kNN (`1982.363884758364`). The kNN family-shift degradation from `1465.09` to `1982.36` is visible and adverse, but it still strongly dominates the exact-equality policy.

## Why the in-corpus R11 result and R14 refutation are consistent

R11 audited the complete frozen corpus and found 1,595 fibres among 1,614 instances for `{Pre,lobjois}`. On that transductive finite subject, almost every exact signature identifies a state and the same-corpus robust total excess is exactly `1712`.

R14 changes the quantifier. A policy is fitted without held-out runtimes and must act on future states. Exact numeric signatures then have negligible recurrence. The representation selected in training remained stable—`{Pre,lobjois}` was selected in 9/10 official folds and 4/5 family folds—so the failure is not primarily feature-menu instability. It is the mismatch between:

- a complete finite-fibre certificate, and
- an inductive prediction problem with mostly unseen fibres.

The R11 theorem and computation remain valid. Their authority is now sharply identified as **corpus-complete/transductive exact auditing**, not out-of-sample solver-selection superiority.

## Refuted claims

The following statements are not admissible after R14:

- exact equality fibres learned from a finite training sample provide useful held-out action coverage on SAT12-ALL;
- the R11 exact static optimum is a deployable inductive selector;
- exact representation selection by itself beats a simple learned selector;
- same-corpus robust improvement establishes held-out operational value;
- executing the R12/R13 adaptive controller on the same exact signatures is the next publication gate.

Adaptive acquisition cannot repair absent terminal coverage merely by sequencing the same equality tests. It requires a representation or certified neighborhood notion whose held-out coverage is prospectively meaningful.

## Positive scientific content retained

R14 is not a null result for FiberGuard as an audit method. It establishes four useful facts:

1. the protocol can distinguish complete-fibre decision value from inductive transfer without leakage;
2. exact-signature coverage is measurable and is a decisive operational quantity;
3. the fail-closed fallback prevents unseen signatures from being silently treated as certified;
4. the learned arm demonstrates that the underlying feature information has predictive value even when exact equality has almost none.

The central empirical lesson is therefore not that the features fail. It is that **exact equality is the wrong inductive equivalence relation for these continuous-valued solver features**.

## Manuscript disposition

The manuscript should integrate R14 as a prospective refutation and narrow its application claim:

> Complete finite fibres provide exact transductive action-regret certificates. Their use as inductive policies requires a separately justified coverage relation; on SAT12-ALL, exact numeric equality has only 3.2% official-fold and 5.1% family-shift recurrence and is dominated by a transparent learned selector.

This is stronger and more credible than retaining only the favorable same-corpus R11 result. It also creates a precise next theorem and experiment: characterize the coverage tax of finite-sample exact certificates and construct a prospectively frozen, nontrivial coarsening or neighborhood certificate that trades certificate radius against held-out coverage.

## Remaining top-tier gate

The next application tranche must not tune a threshold on these R14 test outcomes. It must first freeze, on a separate development scenario or nested training split:

- a coverage-producing representation relation;
- its deterministic action-regret certificate or valid upper bound;
- a training-only threshold-selection rule;
- stronger learned algorithm-selection baselines;
- at least one additional ASlib scenario or public solver portfolio;
- and a final untouched transfer panel.

External reproduction, cross-scenario transfer, strongest-baseline comparison, adaptive operational value, novelty adjudication, and journal authority remain open. No top-tier readiness follows from the R14 engineering success or the scientific refutation alone.
