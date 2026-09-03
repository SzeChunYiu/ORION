# Minimal-level defect cores and atomic excess signatures — V1

Status: **proved conditional reduction plus exact `p=7` signature classification**. The condition is the standard first-counterexample induction: the proposed formula is assumed at all lower factorization lengths. No global Davenport value or novelty claim is made.

## 1. First failing factorization length

Let `p>=5`, put

\[
G=C_p^3,
\qquad
M_p=\frac{5p-5}{2},
\qquad
L_k=kp+M_p.
\]

Assume the proposed equality `D_r(G)=L_r` holds for every `2<=r<m`, but fails at `m>=3`. Choose a zero-sum block `B` such that

\[
z(B)=m,
\qquad
|B|=pm+M_p+q
\]

for an integer `q>=1`. Choose a maximum-length atomic factorization

\[
B=U_1\cdots U_m.
\]

The cases `m=1,2` are already controlled by the classical Davenport value and the exact donor-derived `D_2` formula.

### Short-freeness at a first failure

If `A|B` is a nonempty zero-sum subsequence with `|A|<=p`, put `R=BA^{-1}`. Then

\[
z(B)\ge z(R)+1
\]

and

\[
\delta_p(R)
\ge\delta_p(B)+p-|A|
>M_p.
\]

Moreover `z(R)<=m-1`. This would produce a defect overshoot at a lower factorization length, contradicting the choice of `m`. Thus every first-level counterexample is `p`-short-zero-free and lies in the finite multiplicity box.

## 2. Every proper atom subproduct is controlled

For a nonempty proper index set `I subsetneq {1,...,m}`, put

\[
B_I=\prod_{i\in I}U_i,
\qquad r=|I|.
\]

The displayed factorization gives `z(B_I)>=r`. If `z(B_I)>r`, replacing the selected `r` atoms by a longer factorization would give more than `m` factors of `B`, impossible. Hence

\[
z(B_I)=r.
\]

For `r=1`, the classical atom bound applies. For `r=2`, the exact `D_2` result applies. For `3<=r<m`, the first-failure hypothesis gives the proposed value at level `r`. Therefore every proper subproduct satisfies

\[
|B_I|-rp\le M_p.
\]

This is a hereditary defect bound inside a first failing factorization.

## 3. Atomic excess grammar

Define

\[
e_i=|U_i|-p.
\]

Because `B` is `p`-short-zero-free and `D(C_p^3)=3p-2`,

\[
1\le e_i\le2p-2.
\]

The total defect gives

\[
\sum_{i=1}^m e_i=M_p+q.
\]

Apply the hereditary bound to the subproduct omitting `U_i`:

\[
M_p+q-e_i\le M_p.
\]

Hence

\[
\boxed{e_i\ge q\quad\text{for every }i.}
\]

Summing these lower bounds yields

\[
mq\le M_p+q,
\]

or equivalently

\[
\boxed{(m-1)q\le M_p.}
\]

Thus a first failing level has the finite parameter bounds

\[
3\le m\le M_p+1,
\qquad
1\le q\le\left\lfloor\frac{M_p}{m-1}\right\rfloor.
\]

More generally, every proper subset of the excesses has sum at most `M_p`.

For pairs this also follows directly from the exact `D_2` formula:

\[
e_i+e_j\le M_p.
\]

Given `e_l>=q` and total sum `M_p+q`, the pair inequality is automatic when `m>=3`, but it remains a useful hostile cross-check.

## 4. Short-atom insertion principle

The following device imports restricted short-sum information into a maximum-length factorization.

> **Short-atom insertion lemma.** Suppose a first-level counterexample `B` contains an atom `A` of length at most `p+t`, and
>
> \[
> |B|-(p+t)>D_{m-2}(G)
> \]
>
> with `D_1(G)` used when `m=3`. Then `B` has a maximum-length factorization containing `A`. Consequently one may choose an excess signature with `min_i e_i<=t`.

Indeed, the complement `R=BA^{-1}` has length greater than `D_{m-2}`, so `z(R)>=m-1`. On the other hand, `z(R)<=m-1`, since adjoining `A` to `m` factors of `R` would contradict `z(B)=m`. Thus `z(R)=m-1`, and a maximum factorization of `R` together with `A` is a maximum factorization of `B`.

This lemma is the precise bridge from restricted sumset/short-zero theorems to the factorization signature. Merely knowing that some short zero-sum exists is not enough unless the complement is long enough to recover the remaining `m-1` blocks.

## 5. Exact `p=7` raw signature universe

For `p=7`,

\[
M_7=15,
\qquad
1\le e_i\le12.
\]

At a first failing level, sort the excesses and enumerate

\[
q\le e_1\le\cdots\le e_m\le12,
\qquad
\sum e_i=15+q,
\qquad
(m-1)q\le15.
\]

The two independent programs

- `check_packing_defect_minimal_signatures_v1.py`, using recursive bounded partitions; and
- `verify_packing_defect_minimal_signatures_independent_v1.py`, using multiplicity-vector dynamic programming,

give exactly **322** raw `(m,q,e)` signatures. Their factorization-length distribution is

| `m` | raw signatures |
|---:|---:|
| 3 | 63 |
| 4 | 64 |
| 5 | 53 |
| 6 | 43 |
| 7 | 31 |
| 8 | 23 |
| 9 | 15 |
| 10 | 11 |
| 11 | 7 |
| 12 | 5 |
| 13 | 3 |
| 14 | 2 |
| 15 | 1 |
| 16 | 1 |

The `63,64` entries are the hostile correction: an earlier scratch distribution had moved one signature from `m=4` to `m=3`. The total 322 was unchanged, but the per-level record was not promoted until independently regenerated.

## 6. Donor short-sum pruning at `p=7`

Zhang's donor value

\[
s_{\le12}(C_7^3)=26
\]

implies that every candidate `B` here, whose length is at least 37, contains a zero-sum subsequence of length at most 12. Because `B` is 7-short-zero-free, such a subsequence contains an atom `A` with

\[
8\le|A|\le12.
\]

The short-atom insertion inequality holds:

- for `m=3`, `|B|-12>=25>D_1(C_7^3)=19`;
- for `m>=4`, the lower-level formula gives

  \[
  D_{m-2}=7(m-2)+15=7m+1,
  \]

  while `|B|-12>=7m+4`.

Thus every first-level candidate admits a maximum factorization with

\[
\min_i e_i\le5.
\]

This removes exactly 8 of the 322 raw signatures.

For the special slice `(m,q)=(3,1)`, the existing atom-corridor theorem strengthens the 19 raw triples to exactly six:

`(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`.

This removes 13 additional signatures, disjoint from the preceding 8. Therefore the donor-pruned first-counterexample universe contains exactly

\[
\boxed{322-8-13=301}
\]

signatures, distributed by factorization length as

| `m` | pruned signatures |
|---:|---:|
| 3 | 42 |
| 4 | 64 |
| 5 | 53 |
| 6 | 43 |
| 7 | 31 |
| 8 | 23 |
| 9 | 15 |
| 10 | 11 |
| 11 | 7 |
| 12 | 5 |
| 13 | 3 |
| 14 | 2 |
| 15 | 1 |
| 16 | 1 |

The signature list is a necessary cover, not a list of realizable vector configurations.

## 7. General-prime use

For a general prime, the same induction provides the finite arithmetic shell

\[
3\le m\le\frac{5p-3}{2},
\qquad
1\le q\le
\left\lfloor\frac{5p-5}{2(m-1)}\right\rfloor,
\]

and bounded partitions

\[
q\le e_1\le\cdots\le e_m\le2p-2,
\qquad
\sum e_i=\frac{5p-5}{2}+q.
\]

Any prime-uniform theorem that forces an atom of length at most `p+t` and satisfies the short-atom insertion inequality prunes this shell further by `min e_i<=t`.

The remaining work is geometric and semigroup-theoretic: realize or exclude the signatures as positive primitive modular kernels, then exhibit a positive-gain conformal/Graver augmentation.

## Boundary

- The 322 and 301 counts are exact only for the declared `p=7` first-counterexample signature domain.
- A signature can survive while no corresponding atom configuration exists.
- The lower-level formula is a hypothesis of the first-failing-level reduction, not a conclusion smuggled into the proof.
- Zhang's theorem and all Davenport inputs are donor-owned.
- No global `D_3(C_7^3)` or all-prime formula is claimed.