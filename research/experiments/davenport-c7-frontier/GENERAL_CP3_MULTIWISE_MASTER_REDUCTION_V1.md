# Prime-uniform `C_p^3` multiwise Davenport master reduction — V3

Status: **research reduction / program architecture with hostile route correction**. Donor inputs are named below. No global `C_p^3` formula is claimed.

## Scope and donor baseline

Let `p>=5` be prime and `G=C_p^3`.

The donor-derived `D2_PRIME_POWER_COROLLARY_V1.md` gives

\[
D_2(G)=\frac{9p-5}{2}.
\]

The Freeze--Schmid lower bound specializes, for every `k>=2`, to

\[
D_k(G)\ge L_k:=\frac{9p-5}{2}+(k-2)p.
\]

The prime-uniform target under investigation is immediate stabilization at the lower-bound slope `p`:

\[
D_k(C_p^3)=L_k \qquad(k\ge2).
\]

This is a target/conjectural program, not a theorem here.

## Exact-length short-peeling lemma

Use the standard zero-sum block characterization

\[
D_k(G)=\max\{|B|:B\text{ is zero-sum and }z(B)\le k\},
\]

where `z(B)` is the largest number of pairwise disjoint nonempty zero-sum subsequences.

Assume `D_k(G)=L_k` for some `k>=2`. Put

\[
t_k:=D_k(G)+p+1=L_k+p+1.
\]

If every zero-sum sequence of length exactly `t_k` contains a zero-sum subsequence `U` with `|U|<=p`, then

\[
D_{k+1}(G)=L_{k+1}.
\]

Indeed, deleting `U` leaves a zero-sum complement of length at least `D_k+1`, hence with at least `k+1` disjoint zero-sums; adjoining `U` gives at least `k+2` blocks. Freeze--Schmid supplies the reverse inequality.

When `t_k<eta(G)`, the hypothesis is exactly `t_k in C_0(G)`, in the notation of Fan--Gao--Wang--Zhong--Zhuang, EJC 19(3) (2012), P31.

The lemma is correct, but the first `p=7` instance is **not available**: the donor paper explicitly supplies zero-sum short-free sequences at length 37.

## Hostile correction: `37 notin C_0(C_7^3)`

Fan--Gao--Wang--Zhong--Zhuang define, for `G=C_n^r`,

\[
S_r=\prod_{\emptyset\ne I\subset[1,r]}\left(\sum_{i\in I}e_i\right)^{n-1}
\]

and `alpha_r` by `alpha_r == -2^(r-1) (mod n)`, `alpha_r in [0,n-1]`. Their Proposition 19 / Lemma 24 gives, when `alpha_r != 0`,

\[
C_0(C_n^r)\subset[(2^r-1)(n-1)-\alpha_r+1,\eta(C_n^r)-1].
\]

For `r=3,n=7`, `alpha_3=3`, hence

\[
C_0(C_7^3)\subset[40,\eta(C_7^3)-1].
\]

Therefore

\[
\boxed{37\notin C_0(C_7^3)}.
\]

So the earlier idea “prove `D_3(C_7^3)=36` by forcing a zero-sum of length at most 7 in every length-37 zero-sum sequence” is impossible and is retired.

### Explicit donor witness at length 37

Specializing the Step-3 construction gives

\[
F_7=
 e_1^5e_2^5e_3^5
 (e_1+e_2)^6(e_1+e_3)^6(e_2+e_3)^6
 (e_1+e_2+e_3)^4.
\]

It is a subsequence of `S_3`, has length 37, total sum zero, and is 7-short-zero-free. The companion file `FAN_LENGTH37_WITNESS_V1.md` records the specialization and an explicit four-factorization.

This witness is especially informative because it is **not packing-jammed**. It factors into four zero-sum blocks of lengths `8,8,8,13`. Thus low-spectrum exclusion (`no zero-sum <=7`) and four-pack exclusion are genuinely different phenomena.

## Correct `p=7` target

The lower bound gives `D_3(C_7^3)>=36`. To prove equality, it is enough and necessary in the zero-sum-block formulation to show:

> every zero-sum sequence `B` over `C_7^3` of length 37 has `z(B)>=4`.

Because Fan supplies short-free examples, the hard residual is exactly the **short-free long-block packing problem**:

> every length-37 zero-sum 7-short-zero-free sequence has a four-way zero-sum factorization.

The support-7 theorem proves this for all such sequences with support at most seven; hence any packing obstruction must have support at least eight. `SUPPORT8_DEFICIT_GEOMETRY_V1.md` is the current next layer.

## What survives for a general `C_p^3` program

The short-peeling lemma remains a valid sufficient mechanism at exact lengths where `C_0` membership happens to hold, but it is not the general explanation: it fails as a route already at the first `p=7` induction length and a similar strong-threshold idea also fails at `p=5`.

The more robust prime-uniform object is therefore not `C_0` itself but **decomposition of short-free positive kernel vectors**. For fixed projective support matrix `Q` and scalar lift, a total-zero multiplicity vector `m` lies in the nonnegative congruence kernel. The desired conclusion is a conformal decomposition

\[
m=x_1+\cdots+x_{k+1},\qquad Qx_i=0,
\]

with every `x_i` nonzero and coordinatewise bounded by `m`. Short-freeness merely imposes a lower bound on `|x_i|`; it does not prevent many medium/long factors.

This formulation has several borrowed translations:

1. **Block monoid / nonunique factorization.** The question asks whether a block admits a factorization of length `k+1`; a hypothetical obstruction is a product of only `k` atoms with no longer alternative factorization.
2. **Affine semigroup / toric language.** Zero-sum count vectors form a congruence semigroup; atoms are Hilbert-basis elements, and the desired packing is a conformal semigroup decomposition.
3. **Coding / projective geometry.** After projectivizing support, zero-sums are bounded positive kernel vectors of a diagonally scaled projective code. The problem becomes positive/box-constrained codeword decomposition rather than minimum Hamming distance alone.
4. **Hypergraph matching.** Term occurrences are vertices and zero-sum subsequences are hyperedges; short-freeness deletes small hyperedges but the desired matching can still be forced by medium edges.
5. **Invariant theory.** For abelian groups `beta_k(G)=D_k(G)`, so the same question is a degree/factorization threshold for invariant monomials.

These translations are route-selection tools, not novelty claims.

## Current prime-uniform mechanism candidate

`SUPPORT8_DEFICIT_GEOMETRY_V1.md` identifies a more promising mechanism. For a `p`-short-zero-free sequence over `C_p^3`, projective directions and planes have finite occupancy capacities. With rank-two Property C, a plane carrying at least four actual support values loses an extra unit of capacity. The global capacity deficit

\[
\Delta=s(p-1)-N
\]

therefore pays for projective collisions and rich line incidences. This **deficit-incidence + positive-kernel decomposition** architecture is now the preferred general route.

## Boundary

- `37 in C_0(C_7^3)` is **refuted by donor structure**, not an open target.
- The exact short-peeling lemma remains valid but insufficient as a universal mechanism.
- No monotonicity of `C_0(G)` is assumed.
- No global `D_3(C_7^3)` or prime-uniform `D_k(C_p^3)` theorem is claimed here.
- Determining the classical Davenport constant for arbitrary finite abelian groups is a much broader problem and is outside this program.
