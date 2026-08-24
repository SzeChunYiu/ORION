# Paper A / A1 — MultiTag-TARE constraint-rank result

Date: 2026-08-24

Base revision: `346cbf8bffbbaef200b86a9f9921393cce916716`

Primary owner: `PAPER_A`

Terminal: `PAPER_A_A1_MULTITAG_TARE_ALL_N_SUPPORT_AT_MOST_CONSTRAINT_RANK__R6M_SHARP_BINARY_COROLLARY`

## Result

For the explicitly defined three-block MultiTag-TARE-M2 grammar with `s>=0` shared Tags, minimum frame multiplier `mu`, Restore coefficient `t_R`, and arbitrary nonnegative Tag weights, every optimum in the region `mu>=2*t_R` has

`support(R) <= rank(realized signature multiset) <= s+1`

for every frame Pauli. The exchange fixes every Tag, preserves the partner and Tag symplectic labels, refunds at least `mu` frame cost, and incurs at most `2*t_R` Restore cost. The frozen `s=1`, `mu=2`, `t_R=1` specialization binds the independent all-`n` upper theorem and exact lower witness, giving the sharp R6M corollary `kappa=2`.

## Machine corroboration

- The source and independent implementations both enumerate 768 local Restore replacements. The exact delta histogram is `{-2:18,-1:144,0:444,1:144,2:18}`.
- Every one of the `2^(s+1)` signatures is independently realized for `s=0,...,8`.
- The zero-signature descent is exhaustively checked in dimensions 1, 2, and 3 on 2, 48, and 3,584 nonzero-total words, with zero failures. Standard-basis sharp abstract words are checked through dimension 9.
- The source, generic verifier, and native campaign all accept the same bounded theorem.
- Four clean dual-harness reruns produced the same receipt digest and file hash.
- Focused validation: `5 passed`.
- Visual QA: not applicable; no manuscript or figure was modified.

## Receipts

- Protocol SHA-256: `e572676c9bd0dbe5eb0755146369d7503cb16cd3588b7d30389f249cea8aa428`
- Source result digest: `ff149b9ca1c5fef83d1411e9fed43460b716c88d126f560dcad8d73247e03c57`
- Source result file SHA-256: `465e6556456893fc1aef002be79a678f8e8eaeed7c85be7350d0c5d4823a29a5`
- Generic verification digest: `e72b2d006aa8b719ea2efeafcefd3d7b43f4cac133e66f5772d6eda35609a770`
- Generic verification file SHA-256: `0c762f20734f4470a4c42bac189be9bae79f55c16b103539509d8074104dca77`
- Native manifest digest: `167ab1f90502ba4d24c1d977abc26274fcb79b3d1966c9780344d47c63f35a2f`
- Dual receipt digest: `49318ced07223717e6b11bd6ef3216d232e28e22b79f5379f41eca47e8ca5c08`
- Dual receipt file SHA-256: `76547a80f0edeea02513407070c21e9b51cf32fa660a05e3db2abf91b2df4b84`
- R6M upper parent SHA-256: `b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875`
- R6M lower parent SHA-256: `ace665d82f07bc7ffc12f51fb5813ab7886f4d9bcc415f8f3d1bca6b2610f013`

## Authority boundary

Authority is limited to `DEFINED_MULTITAG_TARE_M2_STRUCTURAL_GRAMMAR_ONLY`. The result does not prove `s+1` sharp for `s=0` or `s>=2`; it does not transfer to every possible multi-Tag grammar or an unrelated grammar; and a point outside `mu>=2*t_R` means only that this exchange proof is unavailable. The structural objective is not a physical T-count, runtime, or qubit advantage. Linear dependence, Pauli symplectic algebra, zero-sum deletion, and generic sparsification remain donor material. The harness grants neither novelty nor venue authority. CI was intentionally skipped and is not scientific evidence.
