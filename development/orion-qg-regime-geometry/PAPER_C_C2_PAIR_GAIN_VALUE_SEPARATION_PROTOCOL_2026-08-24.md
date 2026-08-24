# Paper C / C2 — pair-gain value and optimizer separation

Date: 2026-08-24  
Base: `35b1b591bf7fce5d61ec4edb7d8537c5255bda7b`  
Status: **FROZEN BEFORE FORMAL ANALYZER AND DUAL-HARNESS OUTCOME**  
Primary owner: `PAPER_C`  
Parent theorem: Paper C / C1 all-`m>=5` four-index decision theorem.  
Authority ceiling: exact frozen structural compiler grammar only; no novelty or physical-resource authority.

## Atomic question

Does the complete pair-derived information that suffices for the exact unary-versus-improved decision also determine the exact improvement value or the optimizer witness?

The information supplied to the putative value rule is deliberately strong:

1. the ordered term-weight vector;
2. the complete **labeled** pair-gain matrix, not merely its histogram, extrema, or isomorphism class;
3. the term count.

A separation against this representation automatically subsumes weaker pair-summary representations.

## Frozen construction

For every integer `t>=1`, construct two instances `A_t` and `B_t` with `m=5t` terms and `n=6t` qubit columns. Gadgets use disjoint six-column coordinate sets. Within gadget `r`, label its five terms `a_r,b_r,c_r,d_r,e_r`; every occupied column carries Pauli `X`.

Both instances have two columns supported on all five gadget terms.

The remaining four local columns are:

- `A` gadget: supports `{a,b,c}`, `{a}`, `{b}`, `{c}`;
- `B` gadget: supports `{a,b}`, `{a,c}`, `{b,c}`, and the empty set.

All terms are nonidentity because of the two all-five columns. Terms in different gadgets have disjoint coordinate support.

The four-column replacement is a degree-and-pair-codegree-preserving marginal trade. Such marginal trades and the generic fact that pairwise data need not determine higher-order structure are donor mathematics, not an ORION novelty claim.

## Frozen pair-information equivalence

In both local gadgets, term weights are

`(4,4,4,2,2)`.

The common-factor count of each pair is:

- 3 among `{a,b,c}`;
- 2 between one of `{a,b,c}` and one of `{d,e}`;
- 2 for `{d,e}`.

Therefore pair gains `g_ij=4f_ij-(w_i+w_j)` are respectively 4, 2, and 4 in both instances. Cross-gadget common-factor counts are zero and term weights are identical, so every cross-gadget pair gain is also identical. Thus `A_t` and `B_t` have exactly the same ordered weights and the same complete labeled pair-gain matrix for every `t`.

Both instances fail the C1 decision certificate and both have a strict improvement over unary. The target separation is therefore inside one decision fiber.

## Frozen exact-value theorem

Under the C1 frozen equal-weight structural `SELECT+PREP+WIDTH` objective,

`Delta(A_t)=C_U-C_F=12t-2`,

`Delta(B_t)=C_U-C_F=10t-1`.

Hence the exact-value ambiguity within one complete pair-information fiber is

`Delta(A_t)-Delta(B_t)=2t-1`,

which is unbounded as `t` grows.

## Human-readable proof obligations

For a block `S` of size `s` in a partition with at least two blocks, reuse the exact C1 gain

`T_s(S)=[s(b(s)+2)-2]f(S)-b(s)w(S)`

and set

`h(s)=s-1-d(s)`, `U(S)=T_s(S)+h(s)`.

Then the full gain is

`G(Pi)=sum_{S in Pi} U(S)-max_{S in Pi} b(|S|)`.

### Local gadget maxima

The analyzer and independent verifier must derive `U(S)` from the grammar for all 31 nonempty subsets and all 52 local set partitions, then bind the following concise case result:

- in `A`, the unique maximum local `sum U=12` is the triple `{a,b,c}` (`U=7`) plus the pair `{d,e}` (`U=5`);
- in `B`, the maximum local `sum U=10`; a pair-only maximizer is one pair among `{a,b,c}`, the pair `{d,e}`, and the remaining target singleton. Other local partitions may tie at `sum U=10`, but every tied partition using a block of size at least three pays a larger global `max b` penalty.

### Cross-gadget exclusion

Any block meeting two gadgets has `f(S)=0`. Since every term has weight at least two, such a nonsingleton block has

`U(S)=-b(s)w(S)+h(s)<0`.

Replacing it by singleton blocks raises `sum U` and cannot increase `max b`. Therefore no optimum contains a cross-gadget block, and local maxima compose exactly.

### Global maximum-bit penalty

- Every `A` gadget must use its unique size-three block to reach local sum 12. Across `t` gadgets, `sum U=12t` and `max b=2`, giving `Delta(A_t)=12t-2`.
- Every `B` gadget can reach local sum 10 using pairs and singletons only. Across `t` gadgets, `sum U=10t` and `max b=1`, giving `Delta(B_t)=10t-1`. Any size-three-or-larger tied local choice changes `max b` to at least 2 and is strictly suboptimal globally.

### Exceptional one-block compiler

For `t=1`, direct exact optimization must bind the formula. For `t>=2`, the whole `5t`-term block has zero common factor because gadget coordinates are disjoint. The C1 single-block inequality with `F=0` makes it strictly nonprofitable, so it cannot defeat the composed optima.

## Frozen optimizer-witness consequence

Every optimum for `A_t` contains exactly `t` within-gadget triple blocks `{a_r,b_r,c_r}` and `t` pairs `{d_r,e_r}`. Every optimum for `B_t` uses only pair blocks and singletons, with two pairs and one singleton per gadget. Thus complete pair information does not determine even the presence of an optimal block of size three.

This establishes insufficiency of the pair representation for exact value and optimizer structure. It does not claim that exact value alone never determines an optimizer in arbitrary problems.

## Machine corroboration

Two independent implementations must:

1. construct `A_t,B_t` directly from the frozen column supports;
2. compare every labeled term weight and pair gain exactly;
3. derive every local subset `U` row and enumerate the 52 local partitions;
4. independently verify the cross-gadget inequality and composition algebra;
5. run exact full set-partition optimization for `t=1` (`m=5`) and direct checks for all tractable registered `t` values without using those finite checks as the scalable proof;
6. bind the C1 parent digest and its scope restrictions;
7. pass separate generic and native harness lanes;
8. serialize any contradiction as a refutation.

## Positive terminal

`PAPER_C_C2_COMPLETE_PAIR_INFORMATION_VALUE_GAP_2T_MINUS_1_UNBOUNDED__OPTIMIZER_TRIPLE_VS_PAIR_SEPARATION`

## Honest alternatives

- `PAPER_C_C2_PAIR_INFORMATION_EQUIVALENCE_REFUTED`
- `PAPER_C_C2_VALUE_FORMULA_REFUTED`
- `PAPER_C_C2_OPTIMIZER_STRUCTURE_REFUTED`
- `PAPER_C_C2_GENERIC_NATIVE_DISAGREEMENT`
- `PAPER_C_C2_PARENT_BINDING_FAILED`
- `PAPER_C_C2_CANNOT_CHECK`

## Saturation, donor subtraction, and reopen triggers

The construction is saturated for the exact pair representation because it preserves every labeled pair entry, not just a selected feature vector. It is not literature-saturated. Algebraic-statistics trades, contingency-table fibers, block-design trades, higher-order interaction models, and generic decision/value/witness separations are prior-art threats and require primary-source review.

The possible novelty residual is only the exact compiler-specific scalable realization: constant-support decision, unbounded value ambiguity inside one complete pair-information fiber, and a forced optimizer block-structure change.

Reopen if any pair entry differs, any cross-gadget block can be optimal, a local partition exceeds the registered `sum U` maxima, the one-block compiler wins, or prior work already states this compiler theorem.

## Authority boundary

A passing result establishes an exact unbounded additive value and optimizer-structure separation for the frozen structural compiler. It does not establish a multiplicative approximation lower bound, physical quantum advantage, cross-objective robustness, cross-grammar transfer, novelty, or venue readiness.
