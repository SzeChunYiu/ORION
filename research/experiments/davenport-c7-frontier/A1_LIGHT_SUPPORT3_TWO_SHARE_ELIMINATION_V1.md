# First-corridor `a=1` two-share support-three face is impossible — V1

Status: **proved prime-uniform branch elimination for `p>=7`, with one bounded `p=13` arithmetic resonance discharged by two exact finite replays**. This advances the previously proved `c!=1` theorem to `c>=3`. It does not close the whole `a=1` face and does not determine a generalized Davenport constant.

## 1. Setup

Let `p>=7` be prime, put

`h=(p-1)/2`, `m=(3p-1)/2=3h+1`,

and consider the first maximal corridor

`C_1(p)=(p+1,m,3p-2)`.

For maximal-atom type `a=1`, use the saturated basis `f1,f2,f3` and write

`U=f1^(p-1) f2^(p-1) f3^(p-1) s`, `s=f1+f2+f3`.

The exact depth is

`rho_U(z)=S(z)-2` if all three saturated coordinates of `z` are nonzero, and

`rho_U(z)=S(z)` otherwise,

where `S(z)` is the sum of the least residues of its coordinates.

Assume an exact-support-six support-three companion reuses the light value exactly twice:

`V=s^2 x^r y^t`, `r<=t`.

The first-corridor support-six normal form says that `V` spans a plane whose intersection with `supp(U)` is exactly `{s}`. The pair `UV` is `(m-1)`-short-zero-free.

The atom relation is

`2s+r x+t y=0`,

and

`r+t=m-2=3h-1`.

Because the pair is `p`-short-zero-free, `t<=p-1=2h`. Hence we may write

`r=h-1+d`, `t=2h-d`,

with

`0<=d<=floor((h+1)/2)`.

## 2. A scalar-depth lifting lemma

For `q in {2,...,p-1}`, put

`C=[2q]_p`, `R=[qr]_p`, `T=[qt]_p`.

Multiplying the atom relation by `q` gives

`C s+R x+T y=0`.

The pair contains three actual copies of `s`: two in `V` and one in `U`. Therefore the minimum declared realization cost of `C s` using only `U` and those actual `s` copies is

`lambda(C)=C` for `C<=3`,

`lambda(C)=3C-6` for `C>=4`.

Indeed, in the second case use all three actual copies of `s`, then represent each of the remaining `C-3` copies of `s` by one copy of each saturated basis vector `f1,f2,f3` from `U`.

Consequently, whenever

`R<=r`, `T<=t`, and `lambda(C)+R+T<m`,

the displayed relation is a forbidden nonempty zero-sum subsequence of `UV` of length at most `m-1`.

This lemma uses the maximal atom only through its saturated-coordinate realization of multiples of `s`; it does not enumerate arbitrary subsequences of `U`.

## 3. All multiplicity rows except one are eliminated symbolically

### Case A: `d>=2`

Take `q=2`. Then

`C=4`, `R=2d-3`, `T=p-2-2d`.

Both `R<=r` and `T<=t` hold, and

`lambda(C)+R+T=6+(2d-3)+(p-2-2d)=p+1<m`.

Thus every row with `d>=2` is impossible.

### Case B: `d=0`

Here

`r=h-1`, `t=p-1`.

If `p=4k+3`, then the coefficient triple is not minimal: with `q=h+1`,

`[2q]_p=1<=2`, `[qr]_p=k<=r`, `[qt]_p=h<=t`.

Hence this row cannot be the coefficient vector of the three-support atom `V`.

If `p=4k+1`, necessarily `p>=13`. Take `q=h+2`. Then

`C=3`, `R=k-2=(p-9)/4`, `T=h-1=(p-3)/2`,

so

`lambda(C)+R+T=3(p-1)/4<m`.

Thus `d=0` is impossible whenever it is atom-compatible.

### Case C: `d=1` and `p=4k+3`

Now

`r=h`, `t=p-2`.

Take `q=h+2`. Then

`C=3`, `R=k=(p-3)/4`, `T=p-3`,

and

`lambda(C)+R+T=5k+3<6k+4=m`.

So this row is impossible.

### Case D: `d=1` and `p=4k+1`

Take `q=h+3`. Then

`C=5`, `R=k-1=(p-5)/4`, `T=p-5`,

and

`lambda(C)+R+T=9+(k-1)+(4k-4)=5k+4`.

Since `m=6k+1`, this is less than `m` for every `k>=4`, equivalently every `p>=17`.

At `p=13` (`k=3`) the length is exactly `m`, so the scalar-depth witness is not short. This leaves the unique arithmetic resonance

`boxed{(p,c,r,t)=(13,2,6,11).}`

No other atom-compatible multiplicity row survives.

## 4. Exact discharge of the `p=13` resonance

At `p=13`, divide the atom relation

`2s+6x+11y=0`

by two. Since `11/2=-1` in `F_13`,

`boxed{y=s+3x.}`

The companion plane contains no saturated coordinate axis. In the saturated basis this is equivalent to the three coordinates of `x` being pairwise distinct. Thus there are exactly

`13*12*11=1716`

ordered structural values of `x`.

For each one, compute `y=s+3x` and apply the exact pair-depth inequality

`ell+rho_U(-z)>=19`

to companion subsequences.

The exact finite funnel is:

- structural `x` values: **1716**;
- values passing both singleton tests for `x` and `y`: **312**;
- values passing every pure-power test `x^j`, `1<=j<=6`, and `y^k`, `1<=k<=11`: **0**.

Therefore the resonance is impossible without needing any mixed `x/y` rectangle sum.

The singleton-survivor set, encoded in lexicographic `x` order, has SHA-256

`1732d0e161660a6bae95d0c2bad1a87f9aa15b3510900236e057d29117291236`.

A structurally independent term-occurrence dynamic program, using an independently generated depth table for the 37-term maximal atom rather than the closed depth formula, also returns zero exact pair-compatible companions.

## 5. Theorem

> **Theorem.** For every prime `p>=7`, an exact-support-six first-corridor maximal pair with support-four maximal atom of type `a=1` cannot have a support-three rank-two companion with
>
> `v_s(V)=2`.

Together with `A1_LIGHT_SUPPORT3_ONE_SHARE_ELIMINATION_V1.md`, every hypothetical `a=1` support-three equality companion now satisfies

`boxed{v_s(V)>=3.}`

## 6. Verification architecture

`check_a1_light_support3_two_share_elimination_v1.py` is the primary replay. It verifies the symbolic case formulas through prime 1009, isolates exactly the `p=13` resonance, and performs the closed-depth 1716-to-312-to-0 finite funnel.

`verify_a1_light_support3_two_share_independent_v1.cpp` deliberately changes both load-bearing finite mechanisms:

- it discovers scalar-depth witnesses by exhaustive `q` search rather than the symbolic case split;
- at `p=13` it builds `rho_U` by occurrence-level dynamic programming on the actual maximal atom and tests all companion subsequence cardinalities by a separate occurrence-level length-bitset dynamic program.

The independent replay therefore does not rely on the primary closed-depth implementation or its pure-power-only shortcut.

## Boundary

- The `a=1` face with shared multiplicity `c>=3` remains open.
- The `a=2` light-share support-three face remains open.
- Rank-three four-support companions remain open.
- The only finite component is the explicitly isolated `p=13` resonance; all other primes are eliminated symbolically.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
