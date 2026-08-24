# P10 programme-scale Mathlib transfer result

> Generated from the frozen v2 protocol and exact corpus manifest. The JSON
> result and null-distribution files are the machine-readable sources of truth.

## Population

- selected Mathlib files: 457
- active top-level modules: 31
- files with recognized tactic trajectories: 349
- theorem/lemma trajectories: 4861
- projected tactic-family actions: 19843
- excluded unknown proof-body lines: 21720

## Blocked transfer

| Split | Bigram coverage | Trigram coverage | Markov accuracy | Unigram accuracy | Difference |
|---|---:|---:|---:|---:|---:|
| Leave source out | 0.9977 | 0.9632 | 0.3562 | 0.2588 | 0.0975 |
| Leave top module out | 0.9968 | 0.9571 | 0.3544 | 0.2588 | 0.0956 |

The top-module bootstrap 95% interval for Markov minus unigram is [0.07788671023965142, 0.11349633568973344].

## Frozen standalone gate

Cross-module macro counts are 158 bigrams and 613 trigrams. Full five-seed, two-null summaries and distribution hashes are in the JSON artifacts.

The pre-registered standalone gate **passes**. Numerical prediction condition: True; every-seed/two-null order condition: True.

## Interpretation boundary

This is a conservative source-text projection. It is not a Lean parser, proof-state
trace, semantic tactic model, theorem-correctness check, prover evaluation or authority
decision. Failure to reject a null is not evidence of randomness or equivalence.
