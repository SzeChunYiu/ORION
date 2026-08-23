# X1-C finding — greedy triple extraction yields a 3-case mixed-kernel deficit cascade

Parent: #901. Committed before downstream use.

## Donor inputs

Use the projection

`pi : C_45^3 -> C_3^3`

with kernel `K = C_15^3`, and the donor facts:

- `D(K)=43`, hence `d(K)=42`;
- the Bhowmik--Schlage-Puchta C3^3 analysis used in their proof of `D(Z3⊕Z3⊕Z3d)` removes quotient zero-sums of length 3 greedily and leaves at most 16 quotient terms;
- their proof writes the residual size as `3k+1` with `k<=5`.

No novelty credit attaches to greedy extraction or the donor C3^3 cap bound.

## Exact reduction for a hypothetical C45 counterexample

Assume for contradiction that `S` is zero-sum-free over `C_45^3` with

`|S| = 133 = 3*45-2`.

Project to `C_3^3` and greedily remove disjoint zero-sum triples until none remain. Let the residual have size

`3k+1`, with `k<=5`.

The number of removed triples is exactly

`m = (133-(3k+1))/3 = 44-k`.

Lift the removed triples back to `C_45^3`; each triple has sum in `K`. Let these kernel block sums form a sequence `H` of length `m`.

Because `S` is zero-sum-free, `H` must be zero-sum-free in `K`: if a nonempty subcollection of block sums added to zero in K, the union of the corresponding lifted quotient triples would be a nonempty zero-sum subsequence of S.

Since `d(K)=42`, necessarily

`44-k = |H| <= 42`,

so `k>=2`.

Therefore every hypothetical length-133 counterexample reduces to exactly one of

| k | residual size | |H| | deficiency from d(K)=42 |
|---|---:|---:|---:|
| 2 | 7  | 42 | 0 |
| 3 | 10 | 41 | 1 |
| 4 | 13 | 40 | 2 |
| 5 | 16 | 39 | 3 |

## k=2 is impossible without any new mixed-kernel theorem

A 7-term sequence over `C_3^3` contains a nonempty zero-sum subsequence because `D(C_3^3)=7`. Let C be such a residual quotient zero-sum and let its lifted sum be `c in K`.

If `c=0`, C itself lifts to a zero-sum in S.

If `c!=0`, the maximal zero-sum-free sequence H has length `d(K)=42`. Every nonzero element of K is representable as a nonempty subsequence sum of H: otherwise, if `g!=0` were not representable, adjoining `-g` to H would produce a zero-sum-free sequence of length 43, contradicting `D(K)=43`.

Hence `-c` is represented by a subcollection of H, and combining it with C gives a zero-sum in S.

Thus **k=2 cannot occur**.

## Surviving exact cases

Every hypothetical C45 counterexample therefore reduces to only

- `k=3`: residual 10, H length 41 = d(K)-1;
- `k=4`: residual 13, H length 40 = d(K)-2;
- `k=5`: residual 16, H length 39 = d(K)-3.

The donor proof over a cyclic lift establishes that, in the analogous residuals, one can find `k-2` disjoint quotient zero-sums. Retaining only this quotient-side existence, the mixed-kernel residual naturally matches

`r = k-2 in {1,2,3}`

with

- a zero-sum-free kernel sequence `H` of length `d(K)-r`, and
- `r` disjoint residual quotient zero-sums whose lifted sums are correction values in K.

A counterexample can survive only if **every nonempty combination of the available correction values remains outside the subsequence-sum set Sigma(H)** (up to sign convention).

## New live structural target

The C45 proof no longer needs a global deficiency-one classification of 133 quotient terms. It is enough to close three small residual interfaces:

1. `r=1`: missing-sum geometry of length-41 zero-sum-free sequences in `C_15^3` (directly adjacent to the fresh `nu/nu_p` invariants);
2. `r=2`: missing-sum geometry of length-40 sequences against two residual corrections;
3. `r=3`: missing-sum geometry of length-39 sequences against three residual corrections.

This is a **deficit-matched correction cascade**. The phrase is descriptive only; no novelty is claimed for a new invariant until donor literature is exhausted.

## Claim boundary

- This is a derived reduction, not a proof of `D(C_45^3)=133`.
- The k=2 exclusion is elementary once donor constants are admitted.
- The r=1,2,3 mixed-kernel coverage statements remain OPEN.
- Before defining any generalized missing-sum invariant, search current inverse zero-sum / `nu` / `nu_p` / subsequence-sum literature for an existing parent.
