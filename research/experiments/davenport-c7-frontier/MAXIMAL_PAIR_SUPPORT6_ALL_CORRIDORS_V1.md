# All-corridor support-six theorem for the prime-uniform maximal-atom family — V1

Status: **proved analytic strengthening**. This replaces the earlier `j<=2` support-six restriction in the maximal-atom corridor theorem by an all-corridor statement. No value of `D_3(C_p^3)` and no novelty/priority claim is made here.

## 1. Setup

Let `p>=5` be prime and work over `G=C_p^3`. At the critical `k=3` completion length

`N_3(p)=(11p-3)/2`,

suppose a three-atom factorization contains a maximal atom `U` of length `3p-2`. Write the other atom lengths as

`|A|=p+j`, `|V|=p+b`, `1<=j<=b`,

so the prime-uniform corridor identity is

`j+b=(p+1)/2`,

hence

`1<=j<=floor((p+1)/4)`.

Put `P=UV`. The existing hereditary argument gives

- `z(P)=2`;
- `P` contains no nonempty zero-sum subsequence of length at most `p+b-1`, and in particular none of length at most `p`.

The previous support-complement lemma excluded `|supp(P)|=5` only for `j<=2`. We now remove that restriction.

## 2. Five-support scalar-complement lemma

Let `p>=11` be an odd prime. Let `Q` be a zero-sum sequence over an exponent-`p` group with exactly five support elements `g_1,...,g_5`, with multiplicities

`1<=m_i<=p-1`.

Set

`a_i=p-m_i`, `A=sum_i a_i`.

Assume

`A <= (3p+7)/4`.

> **Lemma.** `Q` contains a nonempty zero-sum subsequence of length strictly less than `p`.

### Proof

Because `sigma(Q)=0` and `p g_i=0`,

`sum_i a_i g_i = -sum_i m_i g_i = 0`.

Thus every scalar multiple of the coefficient vector `a=(a_i)` modulo `p` is another zero-sum relation. We show that one of the scalars `1,2,3` gives coefficients that fit coordinatewise inside `Q` and have total length `<p`.

### Case 1: every `a_i <= (p-1)/2`

Then `a_i <= p-a_i=m_i` for every `i`, so the relation `a` itself is a subsequence of `Q`. Also

`A <= (3p+7)/4 < p`

for `p>=11`. Contradiction to `p`-short-freeness.

### Case 2: one coefficient `x` satisfies `(p+1)/2 <= x <= 2p/3`

There can be only one coefficient larger than `p/2` because `A<p`. Let `x=a_5` and let

`T=a_1+...+a_4=A-x`.

Since the other four coefficients are positive, each satisfies `a_i<=T-3`. Moreover

`T <= A-(p+1)/2 <= (p+5)/4`,

so

`a_i <= (p-7)/4`

for `i<=4`. Hence `3a_i<=p`, and therefore

`2a_i <= p-a_i=m_i`.

For the large coordinate, the residue of `2x` modulo `p` is `2x-p`, and

`2x-p <= p-x`

is exactly `3x<=2p`, which is the present case assumption.

Thus the residue vector of `2a` is a zero-sum subsequence of `Q`. Its length is

`2A-p < A < p`.

### Case 3: `x>2p/3`

Again `x=a_5` is unique. Since the other four `a_i` are positive,

`x <= A-4 <= (3p-9)/4 < 3p/4`.

Use the scalar `3`. On the large coordinate the residue is `3x-2p`, and

`3x-2p <= p-x`

is equivalent to `4x<=3p`, which follows from `x<3p/4`.

For the four small coordinates,

`T=A-x < (3p+7)/4 - 2p/3 = (p+21)/12`.

Hence each `a_i<=T-3`, so

`4a_i < (p-15)/3 < p`.

Therefore `3a_i <= p-a_i=m_i`, and the residue vector of `3a` embeds in `Q`. Its total length is

`3A-2p < A < p`.

All cases produce a forbidden zero-sum subsequence of length `<p`. This proves the lemma.

## 3. All maximal corridors have pair support at least six

Return to the maximal corridor `C_j(p)`. Assume for contradiction that

`|supp(P)|=5`.

Write the five multiplicities of `P` as `m_i`, and again put `a_i=p-m_i`. Then

`A=sum_i a_i = 5p-|P|`.

Now

`|P|=(3p-2)+(p+b)=4p+b-2`,

so

`A=p-b+2=(p+2j+3)/2`.

Since `j<=floor((p+1)/4)`,

`A <= (3p+7)/4`.

For every `p>=11`, the five-support scalar-complement lemma therefore gives a nonempty zero-sum subsequence of `P` of length `<p`, contradicting the hereditary `p`-short-freeness of `P`.

For `p=5,7`, every existing maximal corridor has `j<=2`, so the earlier support-complement lemma already excludes support five directly.

Therefore:

> **All-corridor support-six theorem.** For every prime `p>=5` and every prime-uniform maximal corridor
>
> `C_j(p)=(p+j, p+(p+1)/2-j, 3p-2)`, `1<=j<=floor((p+1)/4)`,
>
> the maximal pair `P=UV` satisfies
>
> `boxed{|supp(P)|>=6.}`

This removes the previous method boundary at `j=3`; the `j=3` extremal failure of the scalar-1 complement is repaired by scalar `2` or `3`.

## 4. Support-four maximal-atom corollary

If the maximal atom `U` itself has support exactly four, the prime-uniform support-four classification gives its canonical form. Since the whole maximal pair has support at least six, the longer companion contributes at least two actual values outside the support of `U`:

`boxed{|supp(V) \ supp(U)|>=2}`

for **every** corridor index `j`, not only `j<=2`.

## 5. Exact next method boundary: scalar multiples cannot rule out support six

The strengthening above is sharp for the one-dimensional scalar-relation method.

If one assumes instead that a maximal pair has support six, write `a_i=p-m_i` as above. Its total complement weight is

`A_6=6p-|P|=(3p+2j+3)/2`.

Consider the admissible arithmetic profile

`a=(1,1,1,1,c,p-1)`,

where

`c=(p+2j-3)/2`.

The coordinates are positive and sum to `A_6`. The last original multiplicity is `m_6=1`.

For a nonzero scalar `t`, the residue of `t(p-1)` modulo `p` is `p-t`. To fit inside the last coordinate one needs

`p-t<=1`,

hence `t=p-1`. But scalar `p-1` sends every `a_i` to `p-a_i=m_i`, i.e. it recovers the whole sequence rather than a proper short zero-sum subsequence.

Thus this support-six profile has **no proper embedded scalar multiple of the complement relation at all**.

This is an arithmetic method ceiling, not an existence claim for a genuine first obstruction. It shows that any support-seven theorem must use additional rank-three kernel relations, projective incidence, pair-plane information, or augmentation structure; scalarizing the multiplicity relation alone cannot suffice.

## 6. Verification receipt

`check_maximal_pair_support6_all_corridors_v1.py` checks:

- every corridor identity for all primes `5<=p<=401`;
- the all-`j` bound `A<=(3p+7)/4`;
- the symbolic inequalities used by the scalar `1/2/3` proof;
- exhaustive five-part complement partitions for all prime corridors through `p=61`, verifying that the prescribed scalar always embeds and produces length `<p`;
- the support-six scalar-method ceiling profile for every checked corridor.

The finite checks are regression only; the theorem authority is the proof above.

## Boundary

- This does not eliminate support-six maximal pairs.
- It does not determine `D_3(C_p^3)`.
- The support-six arithmetic ceiling is not asserted to be realizable by a rank-three first obstruction.
- Donor-owned values and structural inputs retain their existing attribution and claim ceilings.
