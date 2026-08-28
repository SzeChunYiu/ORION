# FiberGuard R23 result — coverage improved below gate

Terminal: `C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE`

R23 is counted as ORION-02 revival attempt 001 of at most 100. It is a genuine
verified adverse/improved-below-gate result, not a positive terminal and not a
paper-freeze authority.

## Measured result

| Quantity | Corrected exact parent | R23 Hamming k=2 | Lexical k=2 negative control | Gate |
|---|---:|---:|---:|---:|
| Full-state certified coverage | 0/44 = 0.0000 | 32/44 = 0.7273 | 39/44 = 0.8864 | 0.95 |

The Hamming backoff restored substantial coverage relative to the corrected
exact-cell parent but missed the frozen gate. The outcome-independent lexical
negative control covered more held-out datasets than Hamming; therefore the
result does not validate the proposed Hamming geometry.

The primary learned ordering minus the matched static adaptive arm had mean
excess difference `-0.001218244987`, bootstrap 95% interval
`[-0.011716227308, 0.008821064426]`, while acquiring more groups on average
(`1.113636363636` versus `0.840909090909`). It does not establish learned
ordering value. The primary learned arm also had 24 strict realized-bound
violations among 42 certified commits; the coverage-below-gate terminal has
precedence, so this remains visible rather than being promoted or hidden.

The matched R23 static arm minus corrected exact static had mean excess
difference `0.001295960276`, bootstrap 95% interval
`[-0.007979258917, 0.010033119242]`. Thus coverage increased, but measured
endpoint performance did not improve convincingly.

## Execution and verification note

LUNARC job 3550005 completed two scientific processes with byte-identical
result, corrected-parent, and terminal files, then exited nonzero at the
independent-verifier stage. The pre-amendment verifier disagreed only on the
last serialized decimal unit of `best_bound` (six Hamming records and ten
lexical-control records; maximum absolute difference `1e-12`); memberships,
admissible arms, coverage, and the independently derived terminal all matched.

Verifier amendment A was committed and pushed before re-verification. It
permits absolute tolerance `1.1e-12` only for `best_bound` and requires every
structural field exactly. Both preserved outputs then returned `VERIFY_OK`
without scientific recomputation, while a greater-than-tolerance hostile
mutation was rejected. The original failure log and adverse result remain
bound in the custody receipt.

## Authority boundary

`scientific_authority_delta` remains `NONE`. This local, pinned-corpus result
does not grant external independence, broad transfer, submission readiness,
top-tier authority, or final freeze. ORION-02 remains active with 99 possible
revival attempts remaining unless an earlier valid bounded positive, exact
within-scope impossibility proof, or named external resource/authorization
block is reached.
