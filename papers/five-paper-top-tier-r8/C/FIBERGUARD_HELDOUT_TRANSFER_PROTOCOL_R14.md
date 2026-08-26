# FiberGuard R14 — prospectively frozen held-out transfer protocol

Date: 2026-08-26

Status at this commit: **protocol only; no held-out outcome has been computed or admitted.**

Parent theory/application stack: `6c23a3fe4ccf415bc3a73794878d72583ed48eb2` (R13), inheriting the positive corpus-complete R11 static result and the R12/R13 deterministic/randomized adaptive theory. This tranche intentionally executes the static transfer discriminator before any adaptive policy is run on SAT12-ALL.

## Scientific question

The R11 corpus-complete search found `{Pre,lobjois}` to be the exact best static representation when feature selection and fibre policies were optimized on all 1,614 SAT12-ALL instances. That is strong same-corpus evidence, but it does not establish transfer. R14 asks a narrower and prospectively falsifiable question:

> When feature representation and solver policy are selected using training runtimes only, does FiberGuard reduce held-out total excess, and does any gain survive a zero-family-overlap source shift?

A negative result is retained. In particular, exact continuous-valued signatures may be nearly unique, so low held-out fibre coverage is a first-class failure mode rather than something to repair after outcomes.

## Frozen external subject

- repository: `coseal/aslib_data`;
- commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`;
- scenario: `SAT12-ALL`;
- the five R11 source blobs remain unchanged;
- official CV blob: `63d3922abaae67e690f31a74c7daa1be6981fb70`.

The workflow must reject any byte drift before evaluating a split.

## Two prospectively frozen split panels

### Benchmark-native panel

Use exactly repetition 1 from the scenario's registered `cv.arff`, requiring folds 1 through 10 and exactly one test-fold assignment for every admitted instance. No other repetition may replace it after outcomes.

### Leave-source-family-out panel

Define the family of an instance as its first three nonempty slash-separated identifier components, or all components when fewer than three exist. Order complete families by descending size, then SHA-256 of the family key, then the key itself. Greedily assign each family to the currently smallest of five folds, breaking ties by fold number.

This panel must prove zero family overlap between train and test. The family definition is a transparent identifier-derived stress test; it is not asserted to be the uniquely correct scientific SAT family ontology.

## Representation and policy fitting

Enumerate all dependency-closed subsets of the ten declared feature steps. For every fold, choose the representation using training instances only by:

1. minimum training robust total excess;
2. then minimum training mean total excess;
3. then fewer feature steps;
4. then lexicographic step tuple.

For a fixed representation, each training signature chooses one solver minimizing its maximum training total excess. An unseen held-out exact signature uses the training-only global robust action minimizing maximum training action regret. Test runtimes never choose a representation, fallback, solver, or hyperparameter.

The R11 `{Pre,lobjois}` representation remains an untouched control; it is not retuned.

## Frozen arms

The required arms are:

1. training single-best solver by mean PAR10;
2. training global robust solver with no features;
3. all feature steps with a training-only exact-signature policy;
4. frozen `{Pre,lobjois}` with a training-only exact-signature policy;
5. training-selected dependency-closed representation with a training-only exact-signature policy;
6. a transparent 16-nearest-neighbor learned selector receiving exactly the frozen `{Pre,lobjois}` information and paying exactly its feature cost.

The kNN baseline uses training-median imputation, explicit missingness indicators, training mean/std scaling, fixed feature-step runstatus one-hot levels, training action regret as its target, deterministic neighbor ties, and lexicographic solver ties.

This kNN arm is a leakage-resistant transparent learned baseline, not a claim that the strongest current algorithm-selection baseline has been exhausted. AutoFolio-style and current robustness-oriented baselines remain a subsequent top-tier gate if the exact method survives this discriminator.

## Common cost and oracle

All arms use the same statewise virtual-best-solver PAR10 runtime with zero feature acquisition as the oracle baseline. Total excess is

`feature acquisition + selected solver PAR10 - statewise virtual-best PAR10`.

Non-`ok` solver runs use PAR10 at the declared 1,200-second cutoff. Feature cost uses the recorded finite value, or the prospectively frozen feature-cutoff fallback under the same R11 convention. No post-outcome exchange rate or penalty is admissible.

## Frozen metrics and promotion gate

For every arm and panel report mean, median, p95, and maximum total excess; mean and maximum feature cost; catastrophic wrong-action count/rate; exact-signature held-out coverage; and the representation selected in every fold.

The primary arm is the training-selected exact representation. A panel passes only if it:

- has strictly lower mean excess than no-feature robust, all-feature exact, and frozen-representation kNN;
- has no larger p95 than all three;
- has no larger maximum or catastrophic wrong-action rate than no-feature robust.

The strongest terminal requires this gate on both the official and leave-family-out panels. Official-only success is explicitly adverse evidence for source-family transfer.

## Execution custody

The protocol JSON, script, and workflow are committed before any result. On that exact commit, GitHub Actions sparse-fetches only the pinned scenario, runs the complete audit twice, requires byte-identical JSON and terminal text, posts a compact hash-bound result to issue #1386, and uploads the complete result artifact. A later result commit may quote only that posted terminal and digest.

## Prior-art and novelty boundary

Generic cross-validation, algorithm selection, kNN, active feature acquisition, robustness under distribution shift, and acquisition policies are donor-owned. Current algorithm-selection research explicitly targets robustness to distribution shift, while current active-feature-acquisition work learns sequential acquisition policies; FiberGuard cannot claim those mechanisms generically.

The residual candidate contribution is the exact complete-fibre action-regret audit, same-oracle acquisition accounting, explicit unseen-fibre coverage/fallback terminal, and the theorem-linked deterministic/randomized × static/adaptive certificate programme.

## Authority boundary

A positive R14 result would establish held-out transfer only within one pinned public ASlib scenario and one identifier-derived family stress test. It would not establish cross-scenario transfer, external independence, the strongest learned-baseline comparison, adaptive R12/R13 value, production deployment value, novelty, or journal authority. A null or adverse terminal narrows the paper rather than being hidden.
