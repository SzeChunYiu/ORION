# Paper C / C2 — complete pair information does not determine value or optimizer

Date: 2026-08-24  
Primary owner: `PAPER_C`  
Status: generic and native dual-harness acceptance under the frozen structural grammar.

## Result

For every `t>=1`, there are two `5t`-term Pauli instances `A_t` and `B_t` with:

- the same ordered term-weight vector;
- the same complete labeled pair-common-factor matrix;
- therefore the same complete labeled pair-gain matrix;
- the same decision outcome: both strictly beat the unary compiler.

Nevertheless their exact structural improvements are

`Delta(A_t)=12t-2`,

`Delta(B_t)=10t-1`.

The exact-value ambiguity inside one complete pair-information fiber is `2t-1`, which grows without bound.

This is stronger than the earlier fixed-domain mixed-feature result: it supplies the full labeled pair matrix, not a histogram or selected low-order summary, and proves a scalable value gap rather than exhibiting one finite mixed cell.

## Optimizer separation

The same construction also forces incompatible optimizer structures.

- Every optimum for `A_t` contains one distinguished triple block and one pair block per gadget.
- Every optimum for `B_t` uses pair blocks and singletons only; any block of size at least three is strictly suboptimal after the global index-width penalty.

Thus complete pair information does not determine even whether an optimal compiler contains a triple block.

## Proof mechanism

Each five-term gadget has weights `(4,4,4,2,2)`. A four-column marginal trade replaces one triple column plus three singleton columns by three pair columns plus an empty column. It preserves every term weight and pair codegree while changing the triple common factor.

Writing the exact partition gain as `sum U(S)-max b(|S|)` gives local maxima 12 for `A` and 10 for `B`. Blocks crossing gadgets have zero common factor and strictly negative `U`, so splitting them is always better. The local maxima therefore compose, and the one global maximum-bit penalty yields the two closed forms above.

Marginal trades and the generic insufficiency of pairwise data are donor mathematics. The candidate paper contribution is only this exact compiler realization and its decision/value/optimizer consequences.

## Independent corroboration

- Both implementations derived all 31 local subsets and all 52 local set partitions.
- Full exact optimization over all 52 partitions at `t=1` gave improvements 10 and 9.
- Full exact optimization over all 115,975 partitions at `t=2` gave improvements 22 and 19.
- These finite checks corroborate but do not supply the scalable proof.
- Generic and native decisions both returned `ACCEPT_PAIR_INFORMATION_VALUE_AND_OPTIMIZER_SEPARATION`.
- Four consecutive isolated dual runs produced the same two-transition native trace and the same receipt digest.

Positive terminal:

`PAPER_C_C2_COMPLETE_PAIR_INFORMATION_VALUE_GAP_2T_MINUS_1_UNBOUNDED__OPTIMIZER_TRIPLE_VS_PAIR_SEPARATION`

## Immutable identities

- Protocol SHA-256: `d006ba86d524ea9366e021a14c0678d3dfc750381489c39344f6b718d94cce7e`
- Source result digest: `b82a965e6f2d063c8aff07b5f21513a4f5e8aecd11b811b9781713ff6dfc7c9f`
- Generic verification digest: `26a4bcde83e042257657db3d2bc584170e267051472fc198790dfde83844c788`
- Native campaign manifest digest: `498178f7eb4e0f307087cc3707ba617b416fd11bb8e1d5abe51c72d616ad7e6a`
- Dual receipt digest: `27ddf01acd9ea83183f76e958e734395be2a3c44605b26f34761ba7ab0fecf2f`
- C1 parent result file SHA-256: `3ffdd36ab1c73680930f3e5471ec095a5dd2ea33438765d3ccca0584bc9afeff`

## Adverse engineering history

The first formal run rejected noncanonical histogram-key digests. Fixed workspace paths later produced nondeterministic transition counts under repeated execution. Both failures are preserved in `PAPER_C_C2_ENGINEERING_AMENDMENT_1_2026-08-24.md`; neither was relabelled scientific evidence.

## Remaining authority boundary

The theorem is exact only for the frozen equal-weight structural `SELECT+PREP+WIDTH` compiler. It proves an unbounded additive ambiguity, not a multiplicative approximation lower bound. It makes no physical T-count, circuit-depth, runtime, qubit, fault-tolerance, cross-objective, cross-grammar, novelty, or venue-readiness claim. A primary-source review of marginal trades, contingency-table fibers, block-design trades, and LCU compiler analyses remains mandatory.
