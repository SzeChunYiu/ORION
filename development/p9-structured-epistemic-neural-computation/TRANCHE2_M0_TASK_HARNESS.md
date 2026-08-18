# P9 tranche 2 — M0 task interface, leakage sentinels, and exact oracle

## Development question

Before training any learner, can ORION freeze **architecture-neutral task interfaces** and null/oracle controls so every later P9 model solves the same problem with the same admissible information?

This tranche is `M0`: it evaluates the task/evaluator/data plumbing, not machine-learning capability.

## Why this is necessary

The exact-world corpus now remints object/mechanic identities across pairs and protected splits. A fixed global class vocabulary would therefore be scientifically wrong for mechanic selection: the learner must reason about **candidate mechanics supplied in the current example**.

Likewise, gluing/obstruction is not naturally a mechanic-ranking task. Forcing both into one output representation would privilege some model families and complicate attribution.

## Atomic fibres

1. Separate model context from candidate mechanics for mechanic-selection tasks.
2. Keep candidate identity opaque and example-local.
3. Preserve the selected mechanic under candidate-order permutation.
4. Expose only the fields admitted by the selected `ViewMode`.
5. Never expose pair family, split namespace, generator seed, evaluator gold, row index, or pair orientation.
6. Define a fixed gluing output vocabulary `GLUE / OBSTRUCTION / UNKNOWN`.
7. Define null baselines that can reveal pair/order/id leakage.
8. Define an exact semantic oracle that uses world semantics but never reads evaluator gold.
9. Bind corpus/task protocol identity before result-bearing execution.
10. Keep every M0 result explicitly non-authorizing and non-P9-positive.

## Task API hypothesis

### Mechanic ranking

Input:

`(context_view, candidate_mechanic_views)`

Output:

- a score/ranking over **the current example's candidate ids**;
- optionally `UNKNOWN` only in later protocols that contain unresolved mechanic-selection gold.

The candidate list is order-permutable. A valid system should select the same mechanic identity after permutation.

### Gluing

Input:

`context_view`

Output:

`GLUE | OBSTRUCTION | UNKNOWN`.

No candidate mechanic list is present.

## View projection hypothesis

The task adapter must preserve tranche-0 view semantics while separating mechanics:

- `SURFACE`: surface labels + topology only;
- `TOPOLOGY`: ids/connectivity/incidence;
- `TYPED`: atom/relation/mechanic types/contracts, no transport values/history;
- `CURRENT`: typed + transport values, no failure history;
- `SEMANTIC`: current + admitted failure history.

The candidate-relative task is not allowed to smuggle a field into a weaker view merely because it is convenient for a scorer.

## Frozen M0 corpus

Use generated exact corpus only:

- corpus seed: `p9-m0-task-harness-v0`;
- train pairs/family: 32;
- dev pairs/family: 8;
- test pairs/family: 16.

M0 does not train on these splits; the counts make the task pipeline identical to the first M1 pilot and create enough examples to expose ordering/id leakage.

## Frozen candidate-order protocol

For mechanic tasks, derive candidate order independently from:

`sha256(order_seed | world semantic fingerprint | candidate id)`.

Order seeds:

- development/default: `p9-m0-order-a`;
- independent permutation check: `p9-m0-order-b`.

The target is always stored/evaluated by candidate identity, never by original index.

## Frozen M0 baselines

### Null/sentinel

1. `FIRST_CANDIDATE` — select presented candidate index 0;
2. `LAST_CANDIDATE` — select last candidate;
3. `LEXICOGRAPHIC_ID` — select lexicographically smallest candidate id;
4. `HASH_PARITY` — deterministic choice from example fingerprint without semantic features;
5. `ALWAYS_GLUE`;
6. `ALWAYS_OBSTRUCTION`;
7. `ALWAYS_UNKNOWN`.

These are leakage/prior diagnostics, not serious scientific baselines.

### Exact semantic oracle

For generated exact worlds only:

- if a claim has a typed `SUPPORTS` relation, select the candidate whose declared effect is `ASSIMILATE_EVIDENCE`;
- if it has a typed `DEFEATS` relation, select the candidate whose effect is `REOPEN_CLAIM`;
- if admitted failure history names a candidate mechanic, select the lowest-cost candidate not named by matching failure history;
- if no admitted failure history exists in the failure-history family, select the lowest-cost candidate;
- for representation cycles, use exact `classify_cycle_gluing`.

The oracle **must not read `world.gold`**. Its purpose is to prove that the full exact semantic object contains enough information and that the task adapter/evaluator can express a perfect solver. It is not a learnable baseline and grants no scientific authority.

## Frozen M0 metrics

Report separately by task and hostile family:

- exact accuracy;
- candidate-order consistency under the two frozen order seeds;
- surface-remint consistency where applicable;
- count of invalid candidate ids / invalid fixed outputs;
- view-specific deterministic accuracy ceiling from the existing identifiability analyzer;
- a ceiling violation flag if any predictor restricted to a declared view is scored above the exact empirical deterministic ceiling.

Do not average mechanic-ranking and gluing accuracy into one headline scalar.

## Expected/null properties — not outcomes

The protocol expects only harness invariants, not model performance:

- exact oracle should reach 1.0 or the harness is broken;
- view ceilings must match the already-frozen generated-corpus information lattice;
- candidate permutation must not change oracle-selected identity;
- null baselines should not be used as evidence of architecture value even if finite-sample accuracy deviates from chance.

No null-baseline numeric result is promoted into a P9 claim.

## RED / hostile tests to write after this protocol commit

1. task serialization contains no `gold`, pair id, hostile-family id, raw seed, split namespace, or row index;
2. candidate ids are exactly the current world's mechanic ids;
3. candidate-order permutation changes presentation order but not correct identity;
4. `SURFACE/TOPOLOGY` candidate payloads omit typed mechanic contracts;
5. `TYPED` candidate payload includes declared mechanic contracts but no history/transport values;
6. history appears only in `SEMANTIC` context;
7. exact oracle does not accept a gold argument and reaches full correctness on the frozen corpus;
8. oracle remains correct under candidate-order permutation;
9. invalid candidate prediction is rejected rather than coerced;
10. invalid gluing label is rejected;
11. null baselines are deterministic and replayable;
12. M0 report is content-bound and explicitly `NO_SCIENTIFIC_AUTHORITY`.

## Reopen triggers

- a serious donor requires a task interface that cannot be adapted without giving it additional task information;
- candidate-order or row-order materially changes a semantic model prediction in a way not attributable to model stochasticity;
- an M0 sentinel exceeds a representation ceiling, indicating leakage/evaluator mismatch;
- the exact oracle fails because the generated world omitted a required coordinate;
- task adaptation requires changing the frozen generated-world gold after outcome access.

## Nonclaims

M0 does not demonstrate learning, neural reasoning, cross-domain generalization, ecological validity, or P9 novelty. It only fixes the experimental interface and catches leakage/evaluator defects before M1+.
