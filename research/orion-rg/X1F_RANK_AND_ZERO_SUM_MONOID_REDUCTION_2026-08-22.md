# X1-F finding — rank-3 and 26-term zero-sum-monoid reduction for D3(C_5^3)=25

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #915

## 1. Rank <=2 support is donor-closed

Freeze--Schmid recall that the standard k-wise lower bound

`D_k(G) >= D*(G) + (k-1) exp(G)`

is optimal for groups of rank at most 2.

For `H=C_5^2`:

- `D*(H)=2(5-1)+1=9`;
- `exp(H)=5`.

Hence

`D_3(C_5^2)=9+2*5=19`.

Any sequence in `C_5^3` whose support spans a subgroup of rank at most 2 and has length at least 19 already contains three pairwise-disjoint nonempty zero-sum subsequences.

Therefore every hypothetical length-25 counterexample to `D_3(C_5^3)=25` must span all of `C_5^3`.

### Symmetry consequence

Every candidate contains three linearly independent occurrences. GL(3,5) acts transitively on ordered bases, so an exact search may fix one selected ordered independent triple to

`e1=(1,0,0), e2=(0,1,0), e3=(0,0,1)`

provided the canonicalization accounts for the choice of basis occurrences and does not multiply-count/omit candidates. This is a search reduction only, not a theorem about multiplicities.

## 2. Length-25 failure <=> length-26 zero-sum sequence with max factorization length <=3

Freeze--Schmid define

`M_k(G) = { B in B(G) : max L(B) <= k }`

and prove the exact characterization

`D_k(G)=max{|B| : B in M_k(G)}`.

For X1-F, a particularly useful elementary correspondence is as follows.

### Forward

Suppose `S` is a length-25 sequence over `G=C_5^3` containing no product of three pairwise-disjoint nonempty zero-sum subsequences.

Set

`x=-sigma(S)`

and

`B=S x`.

Then `sigma(B)=0` and `|B|=26`.

If B admitted a factorization into at least 4 nonempty zero-sum atoms, at most one atom could contain the distinguished occurrence x. The other at least 3 atoms would be pairwise-disjoint nonempty zero-sum subsequences contained entirely in S, contradiction.

Hence

`max L(B) <=3`, so `B in M_3(G)`.

### Reverse

Suppose `B` is a zero-sum sequence of length 26 with `max L(B)<=3`. Remove any one distinguished occurrence x and call the remaining length-25 sequence S.

If S contained three pairwise-disjoint nonempty zero-sum subsequences `Z1,Z2,Z3`, then the leftover sequence

`R=B (Z1 Z2 Z3)^(-1)`

would be nonempty because it contains x, and it is zero-sum because B and all Zi are zero-sum. Factoring R into atoms would give a factorization of B with at least 4 atoms, contradiction.

Therefore S fails three disjoint zero sums.

### Equivalence

Thus:

> There exists a length-25 counterexample to `D_3(C_5^3)=25` iff there exists a zero-sum sequence B over C5^3 with `|B|=26` and `max L(B)<=3`.

This gives two exact solver formulations:

1. direct 25-term disjoint-zero-sum packing;
2. 26-term zero-sum factorization-monoid search for `B in M_3(C_5^3)`.

They should be implemented independently and cross-checked on any positive witness.

## 3. Search consequence

The monoid formulation may be substantially easier to certify because a positive candidate carries a global zero-sum constraint and the failure property is exactly `max L(B)<=3`, matching the donor formalism rather than an ad hoc packing predicate.

The direct formulation remains the independent replay path.

## Claim boundary

Rank-2 k-wise exactness and the M_k characterization are donor-owned. The forward/reverse distinguished-term correspondence is elementary and recorded here as a search reduction, not a novelty claim. Any new result must be the exact D3 value or a new inverse-structure theorem.
