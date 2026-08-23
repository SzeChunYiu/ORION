# X1-C derived donor corollary — deficiency-one normal form in C_3^3

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #901

## Statement

Let `k>=4` and let `A` be a multiset over `C_3^3` with

`|A| = 3k + 4`

such that `A` does not contain `k` pairwise-disjoint nonempty zero-sum submultisets.

Then exactly one of the following structural branches applies.

### P — zero-sum-pair branch

If `A` contains a zero-sum submultiset `U` of length 2, then `R=A\U` has

`|R| = 3k+2 = 3(k-1)+5 = D_(k-1)(C_3^3)-1`

and `R` cannot contain `k-1` disjoint zero sums, otherwise those together with `U` give `k` in `A`.

Bhowmik--Schlage-Puchta Proposition 8 therefore applies to `R`: its support is one of the special seven-point sets `B={b_1,...,b_7}`, and its multiplicities are

`2 + 3 kappa_i`,

with `sum kappa_i = (k-1)-3 = k-4`.

Thus the entire pair branch is

`A = U_2 union R_(Prop8,k-1)`.

### T — pair-free triple-stripping branch

Assume `A` has no zero-sum pair.

First, `0` cannot occur in `A`: removing a zero singleton would leave

`3k+3 = D_(k-1)(C_3^3)`

terms, which contain `k-1` disjoint zero sums, and adding the singleton gives `k`.

While a zero-sum submultiset `U` of length 3 exists, remove it. If the current state has parameter `q`, then its size is `3q+4`; after removing `U` the remainder has size

`3(q-1)+4`

and must fail `q-1` disjoint zero sums, otherwise adding `U` contradicts the current failure. Hence the deficiency-one form is invariant under triple stripping.

Stop at a core `C` with parameter `j` and no zero-sum of length 3.

Properties of `C`:
- no zero singleton (inherited);
- no zero-sum pair (inherited);
- no zero-sum triple (by stopping rule);
- hence no zero-sum subsequence of length <=3;
- no element occurs 3 times, since `g^3` is a zero-sum triple in exponent 3;
- the distinct support has size at most 8 because `D^{3*}(C_3^3)=9`, i.e. any 9 distinct points contain a zero sum of length at most 3.

Therefore

`|C| <= 2*8 = 16`.

Since `|C|=3j+4`, this gives `j<=4`. Also `j!=1`, because `|C|=7=D(C_3^3)` would already force one nonempty zero sum, contradicting failure of one zero sum. Thus

`j in {2,3,4}`.

Consequently

`A = U_1 ... U_(k-j) C_j`,

where every `U_i` is a length-3 zero-sum block and `C_j` is pair-free, has no zero sum of length <=3, has size respectively 10, 13 or 16, and fails `j` disjoint zero sums.

## Specialization to the live C45 quotient

For `k=43`, every projected 133-term failure has one of only these forms:

1. **P:** one zero-sum pair plus a fully classified Proposition-8 maximum failure for `k=42`;
2. **T2:** 41 disjoint zero-sum triples plus a 10-term core failing 2;
3. **T3:** 40 disjoint zero-sum triples plus a 13-term core failing 3;
4. **T4:** 39 disjoint zero-sum triples plus a 16-term core failing 4.

This is a major state reduction for X1-C: the quotient combinatorics that are not already Proposition-8 donor structure live in a core of at most 16 terms, independent of `k`.

## Donor provenance / novelty boundary

Ingredients are donor-owned:
- exact `D_k(C_3^3)=3k+6` for `k>=3`;
- Proposition 8 classification at size `D_k-1`;
- `D(C_3^3)=7`;
- `D^{3*}(C_3^3)=9`;
- elementary removal of a disjoint zero-sum block.

The normal form above is recorded as a derived corollary useful to the ORION-RG search. It is **not claimed as a novel theorem** absent external literature review. Any future novelty must come from the mixed-kernel lift constraints, classification of the residual cores beyond donor results, a lift-compatible deficit-repair theorem, or a new Davenport result.
