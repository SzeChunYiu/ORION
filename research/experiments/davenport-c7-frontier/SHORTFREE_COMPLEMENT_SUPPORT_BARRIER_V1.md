# Prime-uniform short-free complement and support barrier — V1

Status: **proved analytic reduction with arithmetic regression**. This file does not determine any new value of `D_k(C_p^3)` and grants no novelty or priority authority.

## 1. The support-complement lemma

Let `p` be an odd prime, let `G` be an abelian group of exponent `p`, and let `B` be a nonempty zero-sum sequence over `G` containing no nonempty zero-sum subsequence of length at most `p`.

Write

- `N=|B|`,
- `s=|supp(B)|`,
- `m_g=v_g(B)` for `g in supp(B)`, and
- `Delta=s(p-1)-N`.

Short-freeness gives `1<=m_g<=p-1` for every support value.

> **Support-complement lemma.** If
>
> `Delta>=0`, `s+Delta<=p`, and `2 Delta<=p-2`,
>
> then no such `B` exists.

### Proof

Put `d_g=p-1-m_g`. Then `d_g>=0` and

`sum_g d_g=Delta`.

Define the `p`-complement sequence

`C=product_{g in supp(B)} g^[p-m_g]`.

Its multiplicity at `g` is `p-m_g=d_g+1`. Since `d_g<=Delta`,

`p-m_g<=Delta+1`.

On the other hand,

`m_g=p-1-d_g>=p-1-Delta`.

The inequality `2 Delta<=p-2` therefore implies `p-m_g<=m_g` for every `g`, so `C` is a subsequence of `B`. Moreover,

`|C|=sp-N=s+Delta<=p`

and, because `G` has exponent `p`,

`sigma(C)=sum_g p g-sigma(B)=0`.

Thus `C` is a forbidden nonempty zero-sum subsequence of length at most `p`. Contradiction.

The lemma is rank-independent. It is a sufficient obstruction test; failure of one of its inequalities does not assert existence.

## 2. Critical support barrier on the Freeze--Schmid lower line

For `k>=2`, define the candidate stabilized lower line

`L_k(p)=(9p-5)/2+(k-2)p=((2k+5)p-5)/2`

and its zero-sum completion length

`N_k(p)=L_k(p)+1=((2k+5)p-3)/2`.

> **Critical support barrier.** Let `B` be a zero-sum, `p`-short-zero-free sequence over any exponent-`p` group with `|B|=N_k(p)`. Then
>
> `|supp(B)|>=k+4`.

### Proof

A support of size at most `k+2` has capacity at most `(k+2)(p-1)`, while

`N_k(p)-(k+2)(p-1)=(p+2k+1)/2>0`.

It remains to exclude support `s=k+3`. Its capacity deficit is

`Delta=(k+3)(p-1)-N_k(p)=(p-2k-3)/2`.

If `Delta<0`, capacity already fails. Otherwise,

`s+Delta=(k+3)+(p-2k-3)/2=(p+3)/2<=p`

and

`2 Delta=p-2k-3<=p-7<=p-2`.

The support-complement lemma applies. Hence support `k+3` is impossible as well.

For `k=3`, this recovers and conceptually explains the support-seven lower bound at the critical length `(11p-3)/2` used in `CRITICAL_SHORTFREE_SUPPORT_MINIMUM_V1.md`.

## 3. Conditional induction for `D_k(C_p^3)`

Assume the block-monoid convention used throughout this lane: `D_j(G)` is the maximum length of a zero-sum sequence with zero-sum packing number at most `j`.

Suppose

`D_{k-1}(C_p^3)=L_{k-1}(p)`.

Let `B` be a hypothetical zero-sum sequence of length `L_k(p)+1` with packing number at most `k`. If `B` contained a zero-sum subsequence `A` with `|A|<=p`, then the zero-sum complement would have length

`|B|-|A|>=L_k(p)+1-p=L_{k-1}(p)+1`.

By the induction hypothesis, that complement has packing number at least `k`; adjoining `A` gives at least `k+1` disjoint zero-sums, a contradiction. Therefore every first obstruction to the upper bound `D_k(C_p^3)<=L_k(p)` is `p`-short-zero-free, and the critical support barrier forces

`|supp(B)|>=k+4`.

This is a reusable induction gate, not a proof of stabilization. The missing theorem must still convert the surviving large-support, projectively constrained kernel vectors into a conformal decomposition with at least `k+1` zero-sum blocks.

## 4. Projective direction and incidence consequences

A `p`-short-zero-free sequence over `C_p^3` has at most `p-1` terms on each one-dimensional subgroup. Hence a critical sequence of length `N_k(p)` uses at least

`q_min=ceil(N_k(p)/(p-1))`

projective directions. Since

`N_k(p)/(p-1)=k+5/2+(k+1)/(p-1)`,

- if `p>=2k+3`, then `q_min=k+3`;
- if `p<=2k+1`, then `q_min>=k+4`.

For any actual number `q` of occupied projective directions, put

`Delta_q=q(p-1)-N_k(p)`.

If a projective line contains `c` occupied directions, their total occupancy is at least

`c(p-1)-Delta_q`.

The donor identity `eta(C_p^2)=3p-2` bounds every two-dimensional-subgroup occupancy by `3p-3`. Consequently

`c<=floor((3p-3+Delta_q)/(p-1))`.

When the donor Property-C refinement is available, planes containing at least four actual support values can be charged one additional deficit exactly as in `SUPPORT8_DEFICIT_GEOMETRY_V1.md`.

This gives a prime-uniform sequence of reductions:

1. short peeling from the `(k-1)`-st line;
2. support-complement exclusion;
3. projective direction capacity;
4. deficit-incidence geometry;
5. primitive positive-kernel / conformal decomposition.

The first four stages are now explicit formulas. The fifth is the remaining Graver/Hilbert-basis bottleneck.

## 5. Immediate length-19 corridor corollaries at `p=7`

In a hypothetical `(8,10,19)` obstruction, let `U` be the 19-atom and `V` the 10-atom. The existing maximal-atom separation reduction shows that `UV` is zero-sum of length 29 and is 9-short-zero-free. If `|supp(UV)|=5`, then

`Delta=5*6-29=1`,

and its `7`-complement has length `5+1=6`. The coordinate-embedding inequality is `2 Delta=2<=5`. The support-complement proof therefore gives a forbidden zero-sum subsequence of length 6. Thus

`|supp(UV)|>=6`.

For `(9,9,19)`, the analogous product has length 28 and is 8-short-zero-free. Support five would have

`Delta=5*6-28=2`

and an embedded zero-sum `7`-complement of length `5+2=7`. Hence again

`|supp(UV)|>=6`.

These strengthen both length-19 corridors but do not eliminate them.

## 6. Computational receipt

`check_general_shortfree_support_barrier_v1.py` checks all parity and inequality identities above for every prime `5<=p<=401` and every `2<=k<=80`, and separately freezes the two `p=7` corridor calculations. This finite regression supports the symbolic proof; it is not the authority for the all-prime statement.

## Boundary

- No formula for `D_k(C_p^3)` is claimed here.
- The support-complement lemma is elementary and may be donor-reducible; priority is `CANNOT_CHECK`.
- The projective plane bound uses donor zero-sum theory.
- The residual problem is to prove a prime-uniform positive-kernel decomposition theorem, or to retain a verified exceptional family if stabilization fails.
