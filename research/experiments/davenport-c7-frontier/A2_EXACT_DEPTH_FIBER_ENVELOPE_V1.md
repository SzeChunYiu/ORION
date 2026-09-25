# Exact `a=2` representation-depth fiber envelope — V1

Status: **proved prime-uniform exact formula**. For the canonical support-four maximal type `a=2`, the maximum representation depth on every affine fiber with prescribed first-coordinate sum has a closed piecewise-linear form. This compresses a three-dimensional depth search to two scalar residues and supplies the uniform envelope needed by the surviving power-depth problem.

It is a structural depth theorem only. It does not by itself eliminate every `a=2` companion or determine a generalized Davenport constant.

## 1. Canonical coordinates

Let `p=2H+1>=5` be prime, put

`u=2^(-1)=(p+1)/2=H+1`,

and use the basis `(e1,e2,g)`, where

`g=s-u(e1+e2)`.

Then

`s=(u,u,1)`

and the canonical type-`a=2` maximal atom is

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`.

For a target `z=(P,Q,C)` with least residues in `{0,...,p-1}`, the number `k` of selected copies of `s` can only be `0,1,2`. Once `k` is fixed, the selected copies of `e1`, `e2`, and `g` are forced. Hence

`rho_U(P,Q,C)`

`=min_k ([P-ku]_p+[Q-ku]_p+[C-k]_p+k)`,

where `k in {0,1,2}` and the candidate is admitted only when

`[C-k]_p<=p-2`.

Equivalently:

- `k=0` is unavailable only at `C=p-1`;
- `k=1` is unavailable only at `C=0`;
- `k=2` is unavailable only at `C=1`.

## 2. Pair-sum fibers

Fix

`w=[P+Q]_p`

and define

`S0=P+Q`,

`S1=[P-u]_p+[Q-u]_p`,

`S2=[P-1]_p+[Q-1]_p`.

For every available `k`, the third-coordinate contribution plus `k` equals `C`, except that at `C=0` the `k=2` contribution equals `p`. Therefore

- `C=0`: `rho=min(S0,S2+p)`;
- `C=1`: `rho=1+min(S0,S1)`;
- `2<=C<=p-2`: `rho=C+min(S0,S1,S2)`;
- `C=p-1`: `rho=p-1+min(S1,S2)`.

Thus only four elementary pair-sum maxima are needed:

`K0(w)=max min(S0,S2+p)`,

`K01(w)=max min(S0,S1)`,

`K012(w)=max min(S0,S1,S2)`,

`K12(w)=max min(S1,S2)`,

where the maximum is over all `P,Q` with `[P+Q]_p=w`.

## 3. Exact pair-sum table

> **Pair-sum envelope lemma.** The four maxima are exactly:
>
> | fiber `w` | `K0` | `K01` | `K012` | `K12` |
> |---|---:|---:|---:|---:|
> | `0<=w<=H-1` | `p+w` | `p+w-1` | `p+w-2` | `p-1` if `w=0`, else `p+w-2` |
> | `w=H` | `p+H` | `H` | `H` | `p+H-2` |
> | `H+1<=w<=p-2` | `p+w` | `w` | `w-1` | `w-1` |
> | `w=p-1` | `p-1` | `p-1` | `p-2` | `p-2` |

### Proof of the upper bounds

Each `Sk` is a sum of two least residues and is congruent to `w-k` modulo `p`. Hence it can occupy only the corresponding low or high residue-sum level.

The only information beyond this congruence is which side of the thresholds `0`, `1`, and `u=H+1` the two coordinates occupy.

- If `0<=w<=H-1`, the high ordinary sum is `p+w`. On that level `S1<=p+w-1` and, except for the double-zero endpoint, `S2<=p+w-2`. The exceptional fiber `w=0` has `S1=p-1` whenever `S2` takes its double-zero value.
- If `w=H`, an ordinary low sum gives `S0=H`; an ordinary high sum forces both coordinates to be at least `u`, giving `S1=H-1`. Thus `min(S0,S1)<=H`. Independently `S2<=p+H-2`.
- If `H+1<=w<=p-2`, an ordinary high sum forces both coordinates above `u`, so `S1=w-1`. On an ordinary low sum, either `S1<=w-1` or `S2<=w-1`; the only zero-coordinate endpoint still has `S1=w-1`.
- If `w=p-1`, the ordinary sum is always `p-1`. If `S1` reaches its high level `2p-2`, both coordinates equal `H`, and then `S2=p-3`. Hence the three-way and `S1,S2` minima are at most `p-2`.

These observations give every displayed upper bound.

### Sharp witnesses

The bounds are attained by the following explicit pairs (all coordinates are least residues):

- `0<=w<=H-1`: `(P,Q)=(w+1,p-1)` attains `K0,K01,K012`; `(0,w)` attains `K12` for `w>=1`, while `(0,0)` attains the `w=0` value.
- `w=H`: `(H+1,p-1)` attains `K0`; `(0,H)` attains `K01,K012,K12`.
- `H+1<=w<=p-2`: `(w+1,p-1)` attains `K0`; `(w-H,H)` attains `K01`; `(0,w)` attains `K012,K12`.
- `w=p-1`: `(0,p-1)` attains `K0,K012,K12`; `(H,H)` attains `K01`.

This proves the table.

## 4. Closed depth envelope

Define

`M_p(w,C)=max_{[P+Q]_p=w} rho_U(P,Q,C)`.

Substitution into Section 2 gives the exact formula:

> **Exact fiber-envelope theorem.** For every odd prime `p=2H+1>=5`:
>
> **(i) `0<=w<=H-1`:**
> 
> - `M_p(w,C)=p+w` for `C=0,1,2`;
> - `M_p(w,C)=p+w+C-2` for `3<=C<=p-2`;
> - at `C=p-1`, `M_p(0,p-1)=2p-2`, while for `w>=1`,
>   `M_p(w,p-1)=2p+w-3`.
>
> **(ii) `w=H`:**
> 
> - `M_p(H,0)=p+H`;
> - `M_p(H,C)=H+C` for `1<=C<=p-2`;
> - `M_p(H,p-1)=2p+H-3`.
>
> **(iii) `H+1<=w<=p-2`:**
> 
> - `M_p(w,0)=p+w`;
> - `M_p(w,C)=w+1` for `C=1,2`;
> - `M_p(w,C)=w+C-1` for `3<=C<=p-1`.
>
> **(iv) `w=p-1`:**
> 
> - `M_p(p-1,0)=p-1`;
> - `M_p(p-1,C)=p` for `C=1,2`;
> - `M_p(p-1,C)=p+C-2` for `3<=C<=p-1`.

Every maximum is attained by one of the explicit pairs in Section 3, so this is an exact envelope rather than an upper estimate.

## 5. Strategic consequences

The depth of an arbitrary scalar power of a new value can now be bounded without retaining its individual first two coordinates. If the power has first-coordinate sum `w` and third coordinate `C`, then

`rho_U(P,Q,C)<=M_p(w,C)`.

This is especially useful when a companion relation forces an affine family in which `w` and `C` are explicit functions of the scalar multiplier while the remaining parameter is free.

Two singular fibers are now visible:

- `w=H`, where the interior values `1<=C<=p-2` collapse from order `p+H` to `H+C`;
- `w=p-1`, where the `C=0,1,2` values are much shallower than the generic high-sum fibers.

These are precisely the depth drops observed in the surviving maximal-overlap `a=2` lane.

## Verification receipt

`check_a2_exact_depth_fiber_envelope_v1.py` derives `rho_U` directly from the three resource choices. It exhausts every `(P,Q,C)` for every prime through `101`, compares the direct fiber maxima with the closed formula, replays the four `K` tables by direct maximization for every prime through `401`, and verifies all explicit sharp witnesses for every prime through `1009`. It freezes exact row counts and SHA-256 transcripts and rejects mutations that erase either the middle fiber `w=H` or the double-zero endpoint at `(w,C)=(0,p-1)`.

The checker is regression only. The theorem authority is the threshold/carry proof and explicit sharp witnesses above.

## Boundary

- The theorem is specific to maximal type `a=2`.
- It is a maximum over a coordinate fiber; a particular point may be substantially shallower.
- It does not alone prove that every companion power violates the graded depth threshold.
- No generalized Davenport value, all-`k` formula, novelty, or priority claim is made.
