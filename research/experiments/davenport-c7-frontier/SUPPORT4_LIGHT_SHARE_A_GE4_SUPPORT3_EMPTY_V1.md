# Light-share support-three equality branch is empty for every maximal type `a>=4` — V1

Status: **proved prime-uniform structural elimination**. In the first maximal corridor, every exact-support-six support-three rank-two companion sharing the light unsaturated maximal-atom value is impossible whenever the canonical support-four maximal type satisfies `a>=4`.

Together with the uniform heavy-share theorem, this reduces the entire rank-two equality problem to the exceptional light types `a=1,2,3`.

No generalized Davenport value or novelty/priority claim is made here.

## 1. Setup

Write

`p=2H+1`, `m=(3p-1)/2=3H+1`,

and

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-u(e1+e2)`, `u=a^(-1) mod p`,

with

`4<=a<=H`.

Assume an exact-support-six first-corridor support-three companion sharing only the light value:

`V=s^c x^r y^t`.

The exact light multi-copy criterion defines `c_light`; compatibility requires

`1<=c<=c_light`.

Let `K=<s,x,y>`. By the first-corridor normal form, `K` has rank two and meets `supp(U)` only in the actual value `s`.

We first sharpen the light-line depth, then factor the quotient sequence modulo `<s>`.

## 2. The light overlap is automatically smaller than `a`

Let

`h=ceil(H/2)`.

The exact multi-copy criterion says that `c_light>=a` would force

`[u(a+r)]_p=[1+ur]_p<=p-h`

for every `0<=r<=a`.

Write

`a u=1+l p`,

where `1<=l<=a-1` and `gcd(l,a)=1`.

Choose `r0 in {1,...,a-1}` with

`l r0 == -1 (mod a)`.

Then

`[u r0]_p=((a-1)p+r0)/a`,

so

`[1+u r0]_p=p+1-(p-r0)/a`.

If this were at most `p-h`, then

`p-r0>=a(h+1)`.

But

`p-r0<=p-1=2H`,

whereas for `a>=4`,

`a(h+1)>2H`.

Contradiction. Hence

> `boxed{c_light<=a-1.}`

In particular every compatible light overlap has `c<=a-1<=H-1`.

## 3. Exact first-corridor `m`-shell on the light projective line

Define

`delta(q)=rho_U(qs)+rho_U(-qs)`, `1<=q<=p-1`.

We prove

> `boxed{delta(q)>=m iff q in [1,c_light] union [p-c_light,p-1].}`

### 3.1 Small scalars

For `1<=q<=a`, the literal representation gives

`rho_U(qs)=q`.

The exact depth formula shows that

`q+rho_U(-qs)>=m`

is precisely the one-copy condition at multiplicity `q`. For `q<=a` its defining residue intervals are nested as `q` grows. Therefore the valid small scalars form the initial interval

`1,...,c_light`.

Section 2 gives `c_light<a`, so every `q` with `c_light<q<=a` has `delta(q)<m`.

By antipodal symmetry, the upper valid interval is exactly

`p-c_light,...,p-1`.

It remains only to exclude

`a<q<p-a`.

### 3.2 Middle scalars as a residue-diameter problem

Fix `a<q<p-a` and put

`R_q={ [u t]_p : q-a<=t<=q }`.

The exact support-four depth formula gives

`rho_U(qs)=q+2 min R_q`.

For the antipode, the relevant index interval is `q,...,q+a`. Since

`u(t+a)==ut+1 (mod p)`,

its residue set is

`{[r+1]_p:r in R_q}`.

The value `p-1` does not occur in `R_q`: `[ut]_p=p-1` would force `t=p-a`, but `t<=q<=p-a-1`.

Therefore the maximum on the antipodal interval is

`max R_q+1`.

Put

`D_q=max R_q-min R_q+1`.

Then

`boxed{delta(q)=3p-2D_q.}`

Thus `delta(q)>=m` would require

`D_q<=(3H+2)/2`.

We show the opposite.

### 3.3 Forced diameter for `a>=5`

Again write `au=1+l p`, `gcd(l,a)=1`.

Among any `a` consecutive integers, the residues `l t mod a` run through all classes `0,...,a-1`. Take the positions `t0,t1` corresponding to classes `0` and `a-1` inside the first `a` indices of `q-a,...,q`.

The explicit residue formula is

`[ut]_p=((l t mod a)p+t)/a`.

Hence

`max R_q-min R_q >= ((a-1)p+t1-t0)/a`

and `t1-t0>=-(a-1)`, giving

`max R_q-min R_q >= (a-1)(p-1)/a=2H(a-1)/a`.

Consequently

`D_q>=2H(a-1)/a+1`.

For `a>=5`,

`2H(a-1)/a+1>(3H+2)/2`.

Therefore `delta(q)<m` throughout the middle interval.

### 3.4 The endpoint type `a=4`

If `p=4k+3`, then `H=2k+1` and `l=1`. Four consecutive indices already give residue diameter at least

`(3p-1)/4=3k+2`,

so

`D_q>=3k+3>(3H+2)/2`.

If `p=4k+1`, then `H=2k` and `l=3`. Four consecutive indices have diameter at least `3k`. Equality can occur only when the class-`3` position is three places before the class-`0` position. The fifth index in `R_q` repeats the first residue class with its residue increased by one; if the first residue was `p-1`, it wraps to zero and enlarges the diameter even more. Hence the full `a+1=5` term block has diameter at least `3k+1`, and

`D_q>=3k+2>(3H+2)/2`.

So `delta(q)<m` also for every middle scalar when `a=4`.

This proves the claimed exact `m`-shell.

## 4. Quotient factorization

Project the companion plane modulo the shared light direction:

`pi:K -> K/<s> ~= C_p`.

Both `pi(x)` and `pi(y)` are nonzero. If one vanished, the projected zero-sum relation would force the other nonzero value to occur a multiple of `p` times, impossible because its multiplicity is at most `p-1`.

The projected sequence

`S=pi(x)^r pi(y)^t`

is zero-sum and has length

`|S|=m-c`.

By Section 2,

`c<=a-1<=H-1`,

hence

`|S|>=p+1`.

Therefore `S` factors into at least two cyclic atoms:

`S=Q_1 ... Q_k`, `k>=2`.

Lift each factor to the corresponding `x,y` subsequence of `V`. Its ambient sum is

`sigma(Q_i)=q_i s`, `q_i!=0`.

Each factor is proper and has `|Q_i|<=p`.

The pair inequalities applied to `Q_i` and its complement imply

`delta(q_i)>=m`.

By Section 3,

`q_i in [1,c_light] union [p-c_light,p-1]`.

The upper interval is impossible. If `q'=p-q_i<=c_light<=a-1`, then the complement `V/Q_i` has sum `q's`, length at least

`m-p=H`,

while

`rho_U(q's)=q'<=a-1<=H-1`.

Thus

`boxed{1<=q_i<=c_light<=a-1.}`

For these small scalars `rho_U(q_i s)=q_i`, so the graded depth inequality gives

`boxed{|Q_i|<=q_i.}`

## 5. Actual-light cancellation and partial-sum crossing

The pair contains exactly `a+c` actual copies of `s` on the shared light value.

If some `q_i>=p-a-c`, then `p-q_i<=a+c`, so

`Q_i s^(p-q_i)`

is an actual zero-sum subsequence of `UV` of length at most

`q_i+p-q_i=p<m`.

Therefore every factor satisfies

`boxed{q_i<=p-a-c-1.}`

Let

`Q=sum_i q_i`

as an ordinary integer. The lifted factors partition the `x,y` terms, whose ambient sum is `-c s`. Thus

`Q==p-c (mod p)`.

Also

`Q>=sum_i |Q_i|=m-c>p-c`,

so `Q>p`.

Set the cancellation threshold

`T=p-a-c`.

It is positive because `a+c<=2a-1<=p-2`.

Take the shortest initial subcollection of factors whose ordinary `q`-sum `R` satisfies `R>=T`. Each summand is at most both `a-1` and `T-1`, so

`T<=R<=T+a-2=p-c-2<p`.

Since the total ordinary sum is `>p`, this subcollection is proper.

Let `W` be its lifted union. Then

`sigma(W)=R s`, `|W|<=R`,

and `p-R<=a+c` actual copies of `s` are available in the pair. Hence

`W s^(p-R)`

is a nonempty zero-sum subsequence of length at most `p<m`, contradiction.

## 6. Theorem

> **Light-share `a>=4` elimination theorem.** For every prime `p>=7` and every canonical support-four maximal type
>
> `4<=a<=(p-1)/2`,
>
> the first maximal corridor has no exact-support-six support-three rank-two companion sharing only the light unsaturated maximal-atom value.

Combining with `SUPPORT4_HEAVY_SHARE_SUPPORT3_EMPTY_V1.md`, every rank-two support-three equality survivor is now forced into one of only three canonical light types:

`boxed{a in {1,2,3}.}`

## Verification receipt

`check_support4_light_share_a_ge4_support3_empty_v1.py` independently evaluates the exact depth formula and verifies the `m`-shell classification for every prime through `199` and every `a>=4`. It also checks `c_light<=a-1` through prime `1009`. As a separate multiplicity-only control, the exact radial multiplier oracle scans all coefficient-compatible light boundary rows through prime `101` for `a>=4` and leaves zero residuals.

The checker is regression only; theorem authority is the residue-diameter and quotient-factorization proof above.

## Boundary

- The exceptional light types `a=1,2,3` remain.
- The rank-three support-four companion remains.
- The theorem assumes the first maximal corridor and a support-four maximal atom.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
