# Length-37 obstruction atom corridor — V1

Status: **analytic structural reduction**, conditional only on named donor results. Novelty/priority: **CANNOT_CHECK**.

Let `G=C_7^3`. Write `z(B)` for the largest number of pairwise disjoint nonempty zero-sum subsequences of a zero-sum sequence `B`.

## Statement

Assume the donor-derived value `D_2(G)=29`, Olson's `D(G)=19`, Zhao Lemma 4.4, and Zhang's exact value `s_{<=12}(G)=26` (Theorem 1.6 specialized to `C_7^3`). If

- `B` is zero-sum,
- `|B|=37`, and
- `z(B)<=3`,

then `z(B)=3`, and `B` has a factorization into three atoms whose sorted lengths belong to the following list of six candidate triples. More precisely, one can first choose a shortest atom in `B`, then a shortest atom in its complement, to obtain such a factorization:

```
(8,10,19)
(9,9,19)
(9,10,18)
(9,11,17)
(9,12,16)
(10,10,17)
```

## Proof

For generalized Davenport constants we use the standard block-monoid characterization: `D_k(G)` is the maximal length of a zero-sum sequence which cannot be factored into `k+1` nonempty zero-sum sequences. Hence `D_2(G)=29` means that a total-zero sequence of length at least 30 has zero-sum packing number at least three.

Since `|B|=37>29`, `z(B)>=3`; by hypothesis `z(B)=3`. Factor `B` into three atoms and let `A` be any atom occurring in such a factorization. The complement `BA^{-1}` is total-zero. If it had packing number at least three, adjoining `A` would give four disjoint zero-sums in `B`; hence its packing number is at most two, so

`37-|A| <= D_2(G)=29`.

Thus every atom dividing `B` has length at least eight.

Apply Zhao Lemma 4.4 to `B` with `p=7`, `k=11`, `i=2`. The coefficient is

`C(26,9)+C(27,10)=11560835 = 6 (mod 7)`,

so `B` has a nonempty zero-sum subsequence of length at most ten. It contains an atom of length at most ten. Choose a shortest atom `A`; therefore

`|A| in {8,9,10}`.

The complement `C=BA^{-1}` is total-zero, has packing number at most two, and has length `29`, `28`, or `27`. Since all three lengths exceed `D(G)=19`, `C` is not an atom. Choose `U` to be a shortest atom dividing `C` and put `V=CU^{-1}`. This complement is nonempty and must be an atom, since a further split would give at least three disjoint zero-sums in `C`. Because `A` was shortest in `B`, `|U|,|V|>=|A|`, and both are at most 19.

### Case `|A|=8`

Then `|C|=29`. Zhao Lemma 4.4 with `k=11,i=2` gives

`C(18,9)+C(19,10)=140998 = 4 (mod 7)`,

so `C` contains an atom of length at most ten. On the other hand, if `|U|<=|V|`, then `|V|<=19` and `|U|+|V|=29`, forcing `|U|>=10`. Thus `(8,10,19)`.

### Case `|A|=9`

Then `|C|=28`. Zhang's theorem gives `s_{<=12}(C_7^3)=26`, hence `C` contains an atom of length at most twelve. With `|U|>=9`, `|V|<=19`, and `|U|+|V|=28`, the possible pairs are

`(9,19),(10,18),(11,17),(12,16)`,

giving the four triples beginning with 9 above.

### Case `|A|=10`

Then `|C|=27`. Zhao Lemma 4.4 with `k=11,i=2` gives

`C(16,9)+C(17,10)=30888 = 4 (mod 7)`,

so `C` contains an atom of length at most ten. But `A` was shortest, hence both atoms of `C` have length at least ten. Therefore the shorter has length exactly ten and the other has length 17, giving `(10,10,17)`.

This exhausts the possibilities for the selected shortest-first factorization. It does not restrict every other factorization of the same sequence to this list.

## Boundary

This is a corridor, not a solution of `D_3(C_7^3)`. Every hypothetical length-37 total-zero packing obstruction must admit at least one factorization in the six-pattern list; no pattern is claimed to be realized. The original wording asserted the list for every factorization, but the proof only selects shortest atoms. That quantifier was corrected in the 2026-09-05 top-face continuation; see `CORRIDOR_FACTORIZATION_QUANTIFIER_AUDIT_V1.md`. The inputs `D_2=29`, Zhao's lemma, Olson's `D=19`, and Zhang's short-zero theorem are donor-owned.
