# X1-B theorem boundary — even two exact cofactor functionals do not eliminate the six k=4 quotient obstructions

Parent: #900. Committed before downstream use.

## Status

**CONSTRUCTIVE REFUTATION OF THE TWO-RESIDUAL-COFACTOR RELAXATION.**

The six quotient obstruction orbits from the prospectively frozen k=4 test all survive not only independent one-functional scalarization, but also a stronger model in which the two residual blocks are embedded in the **same maximal zero-sum-free kernel sequence** and use its exact canonical cofactor functionals.

This does not construct a zero-sum-free 43-term C15 sequence. It proves that a proof using only the two residual deletion functionals and their common maximal block-sum sequence is insufficient.

## Input property of the six obstruction orbits

For each of the six committed 13-position quotient obstruction orbits A:

- A has packing number exactly 2;
- choose any disjoint nonempty quotient-zero-sum pair `(Z,W)`;
- because both Z and W are pair-compatible anchors and the orbit has zero closing anchors, the common-RHS affine system on `A\W` is consistent and the common-RHS affine system on `A\Z` is consistent.

Thus there exist scalar functions

`f_Z : A\W -> F_5`

and

`f_W : A\Z -> F_5`

such that

`sum_{j in C} f_Z(j)=1`

for every nonempty quotient-zero-sum `C <= A\W`, and

`sum_{j in C} f_W(j)=1`

for every nonempty quotient-zero-sum `C <= A\Z`.

In particular, since `Z <= A\W` and `W <= A\Z`,

`sum_Z f_Z = 1`,

`sum_W f_W = 1`.

## Construct a vector-valued residual lift

Choose a kernel basis `e1,e2,e3` of `C_5^3`.

Assign a kernel vector `y_j in C_5^3` to every residual position j as follows.

### First coordinate

For every `j notin W`, set

`(y_j)_1 = f_Z(j)`.

The first coordinates on positions in W are unconstrained by `f_Z`; choose them so that

`sum_{j in W} (y_j)_1 = 0`.

Since `Z` is disjoint from W,

`sum_{j in Z} (y_j)_1 = sum_Z f_Z = 1`.

### Second coordinate

For every `j notin Z`, set

`(y_j)_2 = f_W(j)`.

Choose the second coordinates on positions in Z so that

`sum_{j in Z} (y_j)_2 = 0`.

Then

`sum_{j in W} (y_j)_2 = sum_W f_W = 1`.

### Third coordinate

Set every third coordinate to zero.

Therefore the lifted residual block sums are exactly

`z = sum_{j in Z} y_j = e1`,

`w = sum_{j in W} y_j = e2`.

## Embed in one exact maximal kernel block-sum sequence

Let the ten already-removed quotient triple blocks have kernel block sums

`e1,e1,e1, e2,e2,e2, e3,e3,e3,e3`.

Together with z=e1 and w=e2, the twelve kernel block sums are

`H = e1^4 e2^4 e3^4`.

This is a maximal zero-sum-free sequence in `C_5^3`.

Its common top-coefficient polynomial is

`P_H=u1^4 u2^4 u3^4`,

so `F(H)=1`.

By the committed cofactor formula:

- the canonical deletion cofactor for the distinguished block z=e1 is `q_Z=e1^*`;
- the canonical deletion cofactor for w=e2 is `q_W=e2^*`.

## Exact local replacement constraints are satisfied

Fix W and the other eleven blocks. Every legal replacement of Z contained in `A\W` has quotient sum zero. Its lifted sum c therefore satisfies

`q_Z(c)=sum_{j in C}(y_j)_1=sum_C f_Z=1=q_Z(z)`.

Likewise, fixing Z and replacing W by any quotient-zero-sum `C <= A\Z` gives

`q_W(c)=sum_C f_W=1=q_W(w)`.

Thus the vector assignment satisfies **all residual legal-replacement equations for both distinguished blocks using the exact canonical deletion cofactors of the same maximal H**.

## Consequence

The following proof state is insufficient to eliminate the six k=4 quotient obstructions:

1. one maximal 12-term zero-sum-free kernel block-sum sequence H;
2. exact group-algebra cofactor coupling of its two residual deletion functionals;
3. all legal residual replacements of Z and W;
4. scalar equal-value constraints under both exact cofactors.

Every one of the six quotient obstructions admits such a realization in the standard H.

Therefore the next successful C15 theorem must use information that this relaxation discards.

## What information remains missing

At least one of the following must become load-bearing:

- replacements of the **ten previously removed triple blocks**, not just Z and W;
- exchange cycles that repartition indices across residual blocks and prior triples simultaneously;
- kernel coordinates of the individual original 43 terms, including zero-sum avoidance across block boundaries;
- a stronger global restriction on the entire family of 12-block packings of one projected 43-term sequence;
- a new quotient normalization theorem that rules out the six residual orbits before lifting.

This sharply identifies the next state-coordinate boundary: **block-sum-level cofactor data is not sufficient; original-index exchange structure is required.**

## Claim boundary

The construction is a proof-method counterexample, not a C15 counterexample. It deliberately guarantees only the quotient residual conditions and maximal kernel block-sum/cofactor conditions; it does not claim the resulting individual lifted terms form a globally zero-sum-free C15 sequence.
