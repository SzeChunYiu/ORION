# X1-F0 finding — any length-21 M2 obstruction has universal atom-complement structure

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #916

## Setting

Let `G=C_5^3`. By the zero-sum monoid characterization of the k-wise Davenport constant,

`D_2(G)>20`

is equivalent to the existence of a zero-sum sequence

`B in B(G)`

with

`|B|=21`, `max L(B)<=2`.

Here `L(B)` is the set of factorization lengths of B into minimal nonempty zero-sum sequences (atoms).

## Universal atom-complement lemma

Assume such a B exists and let `A|B` be any atom divisor.

Because `D(G)=13`, every atom over G has length at most 13. Hence `|A|<=13<21`, so the complement

`R = B A^(-1)`

is nonempty.

Since B and A are zero-sum, R is also zero-sum.

If R were reducible into two or more atoms, adjoining A would give a factorization of B of length at least 3, contradicting `max L(B)<=2`.

Therefore **R is itself an atom**.

Again using `D(G)=13`, `|R|<=13`, hence

`|A| = 21-|R| >= 8`.

Thus every atom divisor A of B satisfies

`8 <= |A| <= 13`,

and its complement is another atom.

## Factorization-length spectrum

Every factorization of B has exactly two atoms (B cannot itself be an atom because `|B|=21>D(G)=13`). If their lengths are ordered `a<=b`, then

`a+b=21`, `8<=a<=b<=13`.

The only possibilities are

- `(8,13)`,
- `(9,12)`,
- `(10,11)`.

Therefore a length-21 M2 obstruction is not an arbitrary zero-sum sequence: **every** nonempty proper zero-sum subsequence that is minimal has length 8--13 and has a complementary minimal zero-sum subsequence, and all factorizations lie in the three pairs above.

## Solver consequence

The direct length-20 failure search can be replaced by a stricter zero-sum-monoid search:

> Find a length-21 zero-sum sequence B spanning rank 3 with no factorization into three atoms.

A positive B immediately yields a length-20 D2 counterexample by deleting one distinguished occurrence; the reverse construction appends the negative total sum to any length-20 failure.

The global zero-sum constraint and the atom-length spectrum should reduce the master search substantially relative to the first direct CEGIS implementation.

## Claim boundary

The zero-sum monoid characterization and `D(C_5^3)=13` are donor mathematics. The complement lemma is an elementary derived reduction for the search and is not claimed as novelty. A new scientific result requires exact D2 or a new inverse classification.