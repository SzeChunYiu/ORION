# X1-C finding — reverse D7(C15^3) induction route is structurally refuted

Parent: #901. Committed before downstream use.

## Candidate shortcut under test

A possible reverse primary induction for `C_45^3` would use a subgroup/quotient orientation whose kernel demand is governed by

`D_7(C_15^3)`,

because `D(C_3^3)=7`.

For this shortcut to establish the conjectured C45 value directly at length 133, it would require an upper bound at or below

`D_7(C_15^3) <= 133`.

No such exact value surfaced in the initial literature search. Freeze--Schmid's lower-bound theorem rules it out outright.

## Donor lower bound

Freeze--Schmid, *Remarks on a Generalization of the Davenport Constant*, Theorem 4.1:

For

`G=C_n1 ⊕ ... ⊕ C_nr`,

choose `s>=2`, `t in [1,r]` with

`s(s-1)/2 <= r-t+1`.

Then

`D_k(G) >= D*(G) + s floor(n_t/2) + delta + (k-2)n_r`,

where `delta=0` if `n_t` is even and `delta=1` if `n_t` is odd.

## Specialization to C15^3

Take

- `G=C_15^3`;
- `r=3`;
- `n_1=n_2=n_3=15`;
- `t=1`;
- `s=3`, since `3*2/2=3 <= 3`;
- `k=7`.

Also

`D*(C_15^3)=1+3(15-1)=43`,

`floor(15/2)=7`, and `delta=1` because 15 is odd.

Therefore

`D_7(C_15^3) >= 43 + 3*7 + 1 + (7-2)*15`

`= 43 + 21 + 1 + 75`

`= 140`.

Hence

`D_7(C_15^3) >= 140 > 133`.

## Consequence

The reverse ordinary multi-wise induction cannot possibly certify

`D(C_45^3)=133`

by reducing the problem to a `D_7(C_15^3)<=133` statement. The required local statement is mathematically false.

This is the mixed-kernel analogue of the earlier refutation of the sharp ordinary `D_k(C_p^3)` route: **generic k-wise block count carries too strong an obligation and introduces an unavoidable loss.**

The live C45 programme must therefore retain finer lift-compatible structure, such as the already-committed maximal-kernel completion / restricted quotient-block compatibility state.

## Donor source / verification note

Theorem 4.1 and its hypotheses were checked in the Freeze--Schmid PDF; the theorem appears on page 10 of the paper (PDF page index 9 in the inspected copy). This file records only the exact specialization above.

## Claim boundary

- This is a refutation of one proof route, not evidence against `D(C_45^3)=133`.
- The lower bound on `D_7(C_15^3)` is donor mathematics.
- No novelty or C45 theorem authority follows.
