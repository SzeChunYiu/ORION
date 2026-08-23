# X1-E known-answer control — standard C45 rank-3 lower construction under the P5 split route

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #912

## Standard lower construction

Let `e_1,e_2,e_3` be a basis of `C_45^3` and define

`S_0 = e_1^44 e_2^44 e_3^44`.

Then `|S_0|=132=3(45-1)` and S_0 is zero-sum-free: any nonempty subsequence sum has coordinate counts in `[0,44]`, so it cannot be divisible by 45 in every coordinate unless all counts are zero.

This is the standard construction proving the lower bound `D(C_45^3)>=133`.

## P5 quotient structure

Use CRT

`C_45^3 ≅ C_5^3 ⊕ C_9^3`

and project to `C_5^3`.

Five copies of any basis vector have quotient sum zero. From each set of 44 copies of e_i, choose eight disjoint 5-term quotient-zero-sum blocks, leaving four copies unused.

Across i=1,2,3 this gives:

- 24 disjoint quotient-zero-sum blocks;
- 12 residual source terms (four copies of each basis vector).

## Kernel lift sequence

Each five-term quotient block in direction i has kernel sum

`5 e_i in C_9^3`.

Since multiplication by 5 is an automorphism of C_9, each `5e_i` has order 9 and the three are a basis after automorphism.

The 24 block sums are therefore

`T = (5e_1)^8 (5e_2)^8 (5e_3)^8`,

which is the standard maximal zero-sum-free construction in `C_9^3` of length

`3(9-1)=24=d(C_9^3)`.

Thus the P5 split representation maps the standard C45 lower construction exactly to a maximal kernel boundary object, with more quotient blocks (24) than the generic 23-block theorem guarantees.

## Adding one more term closes explicitly

Let x=(x_1,x_2,x_3) be any additional term of C_45^3. For each coordinate choose the unique integer

`a_i in {0,...,44}`

with

`a_i ≡ -x_i (mod 45)`.

Then the subsequence consisting of x together with `a_i` copies of e_i for i=1,2,3 has sum zero. If all a_i=0, then x=0 and the singleton x is already zero-sum.

Therefore every one-term extension of S_0 is zero-sum, as expected for this specific maximal lower construction.

## Harness-control role

Any proposed X1-E exchange/escape theorem or algorithm should include this family as a known-answer positive control:

- it must not label S_0 itself as containing a zero sum;
- on S_0 plus any added x, it must recover a genuine zero-sum witness;
- the P5 packing should be capable of exposing the 24-block / maximal-kernel structure without using hidden target labels.

Failure on this control indicates a weakness of the chosen packing/exchange language, not a counterexample to the C45 theorem.

## Claim boundary

This is the standard Davenport lower construction and an elementary coordinate completion argument. It is a calibration/control, not a novelty claim.
