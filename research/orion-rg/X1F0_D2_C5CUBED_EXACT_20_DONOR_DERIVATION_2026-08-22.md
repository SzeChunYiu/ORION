# X1-F0 exact result — D_2(C_5^3)=20 by direct donor lemma specialization

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #916

## Result

`D_2(C_5^3)=20`.

This exact value is obtained by combining the classical Freeze--Schmid lower bound with a direct specialization of Zhao's 2025 Lemma 4.4 on short zero-sum subsequences inside zero-sum sequences. It is therefore treated as a **donor-derived corollary**, not ORION novelty.

## Lower bound

Freeze--Schmid Theorem 4.1, specialized to `G=C_5^3`, `k=2`, `r=s=3`, `t=1`, gives

`D_2(C_5^3) >= 20`.

The explicit 19-term lower witness was independently replayed in commit `f2048b9c745aca636b06ffef0153fb844550bc81`; commit `4e4967f58a350acf2e36d63b79b8192180e943c6` additionally records that this specific lower witness is insertion-saturated. Those bounded checks are controls only.

## Upper bound via Zhao 2025 Lemma 4.4

Source: Kevin Zhao, *On zero-sum subsequences in a finite abelian group of length not exceeding a given number*, arXiv:2506.21383, Lemma 4.4.

Lemma 4.4 states: let p be prime, G a finite abelian p-group, and T a zero-sum sequence with `|T|>=2k`. Suppose `2k>=D(G)+2`. If for some

`i in [1, 2k-D(G)]`

one has

`a_i = C(|T|-k, k-i) + (-1)^i C(|T|-k+i-1, k-1) != 0 (mod p)`,

then T has a zero-sum subsequence of length at most `k-1`.

Apply this with

- `p=5`;
- `G=C_5^3`;
- `D(G)=13`;
- `|T|=21`;
- `k=8`.

The size hypotheses are

`21 >= 2*8 = 16`,

`2*8 = 16 >= 13+2 = 15`.

Moreover

`2k-D(G)=16-13=3`,

so `i=2` is admissible. Compute

`a_2 = C(21-8, 8-2) + C(21-8+2-1, 8-1)`

`= C(13,6) + C(14,7)`

`= 1716 + 3432`

`= 5148`

`= 3 (mod 5)`.

Thus `a_2` is nonzero modulo 5. Lemma 4.4 yields:

> Every zero-sum sequence T over C_5^3 of length 21 has a nonempty zero-sum subsequence of length at most 7.

## Conversion to D_2

Commit `301a823907f9bc1389633e7177274d8b8313836a` proved the elementary equivalence:

`D_2(C_5^3)=20`

iff every zero-sum sequence of length 21 has a nonempty proper zero-sum subsequence of length at most 7.

The donor lemma supplies exactly that condition. Hence

`D_2(C_5^3) <=20`.

Together with Freeze--Schmid's lower bound,

`D_2(C_5^3)=20`.

## Consequence for X1-F / D_3(C_5^3)

Let B be a hypothetical length-26 zero-sum sequence with `max L(B)<=3`, equivalent to a length-25 obstruction to `D_3=25`.

For every atom A dividing B, the complement `B A^(-1)` lies in `M_2(C_5^3)` and therefore has length at most `D_2=20`. Hence

`|A| >= 26-20 = 6`.

Since every atom also has length at most `D(C_5^3)=13`, every atom divisor of B has length in `[6,13]`.

This is now an exact donor-derived constraint, not a conditional hypothesis.

## Authority / novelty boundary

The exact D2 value is not claimed as ORION novelty. The decisive upper-bound step is a direct specialization of a published 2025 donor lemma. ORION's contribution here is only detecting the correspondence and binding it correctly into the D3/C45 research state.
