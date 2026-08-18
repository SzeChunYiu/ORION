# P10 programme-scale Mathlib transfer result V2.1

> Generated from the frozen v2 protocol and exact corpus manifest. The JSON
> result and null-distribution files are the machine-readable sources of truth.

## Population

- selected Mathlib files: 457
- active top-level modules: 31
- files with recognized tactic trajectories: 349
- theorem/lemma trajectories: 4825
- projected tactic-family actions: 16667
- excluded unknown proof-body lines: 6097

## Blocked transfer

| Split | Bigram coverage | Trigram coverage | Markov accuracy | Unigram accuracy | Difference |
|---|---:|---:|---:|---:|---:|
| Leave source out | 0.9970 | 0.9521 | 0.3851 | 0.2796 | 0.1055 |
| Leave top module out | 0.9959 | 0.9450 | 0.3842 | 0.2796 | 0.1046 |

The top-module bootstrap 95% interval for Markov minus unigram is [0.08629353664876105, 0.1223223805369778].

## Frozen standalone gate

Cross-module macro counts are 151 bigrams and 518 trigrams. Full five-seed, two-null summaries and distribution hashes are in the JSON artifacts.

Under every seed and both null families, the observed bigram and trigram
counts fall in the significant lower tail. The source sequences therefore
concentrate recurrence into fewer distinct cross-module patterns than the nulls.

The pre-registered **numerical conditions** pass. Prediction condition: True; every-seed/two-null order condition: True.
The full standalone gate **does not yet pass** because native-receipt and nearest-work conditions remain unresolved.

## Interpretation boundary

This is a conservative source-text projection. It is not a Lean parser, proof-state
trace, semantic tactic model, theorem-correctness check, prover evaluation or authority
decision. Failure to reject a null is not evidence of randomness or equivalence.
