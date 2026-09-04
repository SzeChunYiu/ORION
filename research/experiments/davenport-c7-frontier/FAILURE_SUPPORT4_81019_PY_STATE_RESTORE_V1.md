# Failure receipt: Python state-restoration undercount in support-four `(8,10,19)` prototype — V1

Status: **rejected engineering receipt, preserved for audit**.

An exploratory Python recursion for the support-four maximal-atom branch of `(8,10,19)` initially reported:

- only 55 `(V_10,W_8)` factor completions;
- no 8-atom extension for the canonical `a=2` maximal atom.

Both statements were false.

The prototype maintained cardinality-indexed companion subset-sum sets incrementally across recursion. Its branch restoration was incomplete, so stale subset-sum state from earlier siblings could remain active and incorrectly reject later candidates. This was a **false-negative enumeration bug**.

A clean C++ reimplementation from the mathematical specification gives:

- pair candidates `538,24,0` for `a=1,2,3`;
- extendable pair candidates `229,6,0`;
- completion counts `2772,24,0`, total `2796`;
- 1572 distinct length-37 sequences.

A structurally independent verifier using occurrence masks plus a minimum-base-depth table reproduces all these counts. Both implementations also prove that all 2796 factor triples four-pack.

Therefore the `55` count and the claimed `a=2` nonextension are permanently rejected and must not be cited as mathematical evidence.

No branch commit containing the false `55` result was promoted as a theorem. This file preserves the failed route because the user requested ORION-style failure retention.
