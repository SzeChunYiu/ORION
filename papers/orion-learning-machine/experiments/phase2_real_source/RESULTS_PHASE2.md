# Phase 2 real-source results — closure snapshot

**Date:** 2026-08-18  
**Authority:** real-source representation/falsification evidence; no Lean kernel replay; no broad theorem-proving claim.

## Phase 2A — public Lean source mining

Frozen corpus: seven source files from two independent Lean projects, represented locally by provenance-bound normalized/extracted source copies. The local extracts are **not** claimed byte-identical and are not used as kernel-verifiable proofs.

- 31 theorem trajectories
- 106 conservative family-level actions
- 105 raw tactic-head actions
- 11 family types vs 17 raw heads

Leave-one-file-out coverage:

| representation | bigram coverage | trigram coverage | Markov next-action | unigram baseline |
|---|---:|---:|---:|---:|
| family abstraction | **0.5733** | **0.2075** | 0.2400 | **0.3067** |
| raw tactic head | 0.4459 | 0.1400 | 0.2432 | **0.3108** |

Family abstraction therefore increased held-out sequence coverage on this small corpus, but neither family nor raw Markov prediction beat its unigram baseline.

Six recurring family macros met cross-source and cross-donor support/provenance gates. However, the stronger shuffle falsifier rejected the interpretation that their ordering was meaningful structure beyond action frequency:

- cross-donor bigram count: observed `5`, shuffle mean `5.632`, empirical `p_ge=0.829`;
- cross-donor trigram count: observed `1`, shuffle mean `0.644`, empirical `p_ge=0.500`.

**Conclusion:** surface tactic recurrence is not admitted as evidence of learned problem-solving structure.

## Phase 2B — goal-state/effect transition smoke test

A second frozen study manually transcribed 29 public Mathlib Tactics viewer rows containing real goal→tactic→post-goals observations across 23 modules. Five tactics had support in at least two modules: `Nat.cast_succ`, `exact`, `mul_add`, `simp`, and `split_ifs`.

For the 15 leave-one-module-out rows where such a mechanic contract was eligible:

- empirical mechanic-specific goal-count effect accuracy: **1.000**;
- global effect baseline accuracy: **0.600**;
- coverage of all 29 sample rows: **0.517**.

This is a small, manually transcribed smoke test. It supports the **plumbing and representation choice**—mechanic-specific empirical state/effect contracts can carry signal beyond a global effect prior on this sample. It does not establish semantic tactic understanding, general theorem-proving transfer, competence-boundary learning, or publication-level superiority.

## Reopen

The surviving P9 object is therefore not “a grammar of repeated tactic sequences.” It is a provenance-bound learned model over **state/context → mechanic → observed effect/failure**, augmented with competence/UNKNOWN evidence, donor-protected identity and explicit composition.

## Required next external gate

Full public trace execution (or equivalent) with immutable dataset revision, kernel-grounded transitions, real failed actions, source/domain/time holdouts, matched skill-composition/tactic-search baselines, and protected independent reproduction remains `CANNOT_CHECK` in this environment.
