# Fan length-37 short-free witness and four-factorization — V1

Status: **donor-derived explicit witness plus exact elementary packing certificate**. No novelty claim.

Let `G=C_7^3` with basis `e1,e2,e3`, and abbreviate

- `e12=e1+e2`,
- `e13=e1+e3`,
- `e23=e2+e3`,
- `u=e1+e2+e3`.

Fan--Gao--Wang--Zhong--Zhuang (EJC 19(3) (2012), P31) use

\[
S_3=e_1^6e_2^6e_3^6e_{12}^6e_{13}^6e_{23}^6u^6,
\]

a 7-short-zero-free sequence of length 42. Their Step-3 construction / Proposition-19 proof supplies zero-sum short-free lengths through 39.

Choose `alpha_3=3`, `k1=k2=1`, `k3=3` in their Step-3 family. Equivalently remove

\[
e_1e_2e_3u^2
\]

from `S_3`. The resulting sequence is

\[
F_7=e_1^5e_2^5e_3^5e_{12}^6e_{13}^6e_{23}^6u^4.
\]

It has length 37. Since

\[
\sigma(S_3)=3u
\]

and the removed five terms also sum to `3u`, `F_7` is zero-sum. As a subsequence of the short-free `S_3`, it contains no nonempty zero-sum subsequence of length at most seven. Thus `37 notin C_0(C_7^3)`.

## Explicit four-factorization

Despite being 7-short-zero-free, `F_7` is not a packing obstruction. It factors as

\[
F_7=A_{23}A_{13}A_{12}A_0,
\]

where

\[
A_{23}=e_2e_3e_{23}^6,
\qquad
A_{13}=e_1e_3e_{13}^6,
\qquad
A_{12}=e_1e_2e_{12}^6,
\]

and

\[
A_0=e_1^3e_2^3e_3^3u^4.
\]

Their lengths are `8,8,8,13`, and each sum is zero:

\[
\sigma(A_{ij})=7(e_i+e_j)=0,
\qquad
\sigma(A_0)=7u=0.
\]

Because every zero-sum block in `F_7` has length at least eight, five disjoint nonempty zero-sums would require at least 40 terms. Hence the packing number is exactly

\[
z(F_7)=4.
\]

## Research meaning

This is a useful hostile control for any proposed general mechanism:

- **short-zero forcing is false** at the exact length relevant to `D_3(C_7^3)`;
- nevertheless the canonical donor short-free construction is **exactly four-factorable**;
- therefore the target mechanism must distinguish *spectral short-freeness* from *packing jamming*.

The three length-8 edge blocks consume the pair-direction reservoirs, while the remaining basis/triple-direction core neutralizes at length 13. In the charge-packing picture this is a capacity-compatible medium-cluster decomposition, not a short-cluster phenomenon.

`check_fan_length37_witness_v1.py` independently verifies the arithmetic, exhaustive 7-short-freeness, and the displayed factorization.
