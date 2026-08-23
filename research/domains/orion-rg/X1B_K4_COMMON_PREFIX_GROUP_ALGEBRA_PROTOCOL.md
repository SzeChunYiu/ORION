# X1-B k=4 — prospective full group-algebra common-prefix discriminator

Parent: #900.
Input obstruction: the common rank-2 residual lift committed in `X1B_K4_RANK2_RESIDUAL_LIFT_OBSTRUCTION_2026-08-22.md`.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** No outcome of the linear group-algebra system below has been computed or inspected before this packet is committed.

## Common-prefix necessity

Let `G=C_5^3` and work in the group algebra `F_5[G]`. For a sequence of ten fixed triple-block sums `T=t_1...t_10`, define

`P_T = product_i (1-X^{t_i})`.

The common rank-2 residual lift has only three unordered residual block-sum pair types:

```text
P1=((0,2,0),(3,2,0))
P2=((0,2,0),(0,2,0))
P3=((1,0,0),(2,4,0)).
```

If any of these pairs extends the same T to a maximal zero-sum-free 12-sequence, Geroldinger--Yang Lemma 3.4 and the coefficient-at-zero normalization give the full identity

`P_T (1-X^x)(1-X^y) = Omega`,

where `Omega=sum_{g in G} X^g`.

Therefore an actual C15 counterexample compatible with the common residual lift requires a **single** group-algebra element P satisfying all three linear multiplication equations

`P A_r = Omega`,  r=1,2,3,

with `A_r=(1-X^x)(1-X^y)` for the three pair types.

## Frozen linear relaxation

Forget initially that P must factor as ten terms `(1-X^{t_i})` and that T must be zero-sum-free compatible.

Represent `F_5[G]` in the canonical basis `{X^g : g in F_5^3}` with 125 unknown coefficients for P. Multiplication is convolution modulo 5 on group coordinates.

Build all `3*125` coefficient equations for `P A_r = Omega` and row-reduce exactly over `F_5`.

Required output:
- consistency;
- equation rank;
- affine solution dimension;
- canonical particular solution and nullspace basis if consistent;
- primitive convolution replay for every pair identity;
- digest of the serialized result.

## Scientific interpretation

- **INCONSISTENT:** both final k=4 quotient orbits are eliminated, because no common ten-block prefix can satisfy the necessary full group-algebra identities even before factorability is imposed.
- **CONSISTENT:** serialize the exact affine space and restore, in order, (i) factorability into ten `1-X^t` factors, (ii) zero-sum-free compatibility of each 12-term extension, and (iii) original-index realization.

A consistent relaxed P is not a sequence witness or C15 counterexample. An inconsistency proof is a valid elimination because the full group-algebra identity is necessary.