# Type `a=3` rank-three shared-donor boundary and negative-even certificates — V1

Status: **proved prime-uniform structural reduction and certificate family**.  In the first maximal corridor, the exceptional canonical type `a=3` rank-three exact-support-six face is reduced to a one-dimensional boundary strip.  On that strip, every even negative scalar satisfying four explicit capacity inequalities gives an occurrence-valid short zero-sum whose length is a closed expression independent of the heavy overlap and of the boundary position.

This is not a complete `a=3` closure.  It is designed as a selector interface for the remaining exceptional-denominator argument.  It does not determine `D_3(C_p^3)` or the all-prime multiwise Davenport formula.

## 1. Setup

Let `p=2H+1>=11` be prime and

`m=p+H=(3p-1)/2`.

Use the canonical type-three maximal atom

`U=e1^(p-1)e2^(p-1)s^3 g^(p-3)`,

with

`e1+e2=3(s-g)`.

Consider a hypothetical first-corridor exact-support-six rank-three companion

`V=s^c g^d x^r y^t`,

where `c,d,r,t>=1`, `c+d+r+t=m`, and `x,y` are the two genuinely new support values.  Assume `UV` has no nonempty zero-sum of length less than `m`.

Two existing exact consequences will be used.

1. The type-three light multi-copy criterion gives

   `c<=floor(H/2)`.

   The proof of this ceiling is the standalone radial/multi-copy calculation in `A3_LIGHT_EXACT_DEPTH_AND_TWO_PARAMETER_FACE_V1.md`; it does not use rank two.

2. Since `U` already contains `p-3` copies of `g`, short-freeness gives

   `d<=2`.

   Otherwise the pair contains `g^p`.

The point of the present note is to use the shared copies themselves as donor resources rather than insisting that every overlap multiple fit inside `U` alone.

## 2. Shared-donor doubling kills the whole interior

Put `S=c+d`.  Suppose first that both new multiplicities exceed `H`.

Write

`q=floor((c-1)/3)`.

Then

`3q<=c-1`

and

`1<=c-3q<=3`.

Double the companion relation.  Since `r,t>H`, the least residues

`R=2r-p`, `T=2t-p`

satisfy

`1<=R<=r`, `1<=T<=t`.

Use the following actual occurrences from `U s^c g^d`:

- `q` copies of `e1` and `q` copies of `e2`;
- `2c-3q` copies of `s`;
- `2d+3q` copies of `g`.

The old-support sum is

`q(e1+e2)+(2c-3q)s+(2d+3q)g`

`=2c s+2d g`.

The resource bounds are automatic:

- `2c-3q=c+(c-3q)<=c+3`, exactly the available `s` capacity;
- `2d+3q<=p-3+d`, because `d<=2`, `3q<=c-1`, and `c<=floor(H/2)` with `H>=5`;
- `q<=p-1` for the saturated coordinates.

Thus these donor occurrences together with `x^R y^T` form a zero-sum.  Its length is

`R+T+2q+(2c-3q)+(2d+3q)`

`=p-1+2q`.

Since `q<=floor((c-1)/3)` and `c<=floor(H/2)`, one has `2q<H+1`, so

`p-1+2q<m`.

This contradicts short-freeness.

> **Shared-donor doubling theorem.** In every surviving type-three rank-three equality face, the smaller new multiplicity is at most `H`.

Order `r<=t`.  Then `r<=H`.  Since `t<=p-1`, there is a unique integer `k` with

`r=H-k`, `t=p-S+k`,

and

`boxed{0<=k<=S-1.}`

Hence the complete surviving multiplicity geometry is the boundary strip `(c,d,k)`; arbitrary `(r,t)` are gone.

## 3. A uniform negative-even scalar certificate

The boundary form admits a closed mixed certificate family.

Let

`epsilon=p mod 3 in {1,2}`,

`Q=(p-epsilon)/3=floor(p/3)`.

Choose a positive even integer `J<p`.  Define

`tau` to be the unique element of `{0,1,2}` with

`J+tau == 0 (mod 3)`,

and put

`L=(J+tau)/3=ceil(J/3)`.

Assume the following inequalities:

`(A)  L c <= Q,`

`(B)  tau c+epsilon <= c+3,`

`(C)  J S+tau c+epsilon <= p,`

`(D)  (J+1)k+J/2 <= H,`

`(E)  (J+1)(S-k) <= p,`

and the strict score inequality

`(F)  p+2Q-2Lc+J/2 < m.`

Condition (B) is automatic for `tau=0,1`; only the `tau=2` residue class has a small-`c` restriction.

Take the scalar `n=p-J=-J` modulo `p`.  Conditions (D)--(E) show that the actual new-value counts are

`R=J/2+Jk`,

`T=J(S-k)`.

Indeed, because `J` is even,

`-JH == J/2 (mod p)`,

so `[-Jr]_p=J/2+Jk`, while `[-Jt]_p=J(S-k)`.  The displayed inequalities make both residues fit inside the available multiplicities.

Now take from the shared donor `U s^c g^d` the occurrence vector

`E=Q-Lc` copies of each of `e1,e2`,

`z=tau c+epsilon` copies of `s`,

`w=p-JS-tau c-epsilon` copies of `g`.

Conditions (A)--(C) make these counts nonnegative.  The upper `g` capacity is automatic because `J>=2` and `S>=2`, hence `w<=p-5<=p-3+d`.

Using `3Q+epsilon=p` and `3L=J+tau`,

`3E+z=p-Jc`,

`w-3E=-Jd`.

Therefore

`E(e1+e2)+z s+w g=-Jc s-Jd g`,

which exactly cancels the sum of `x^R y^T` coming from the `-J` multiple of the companion relation.

The total occurrence length collapses to

`R+T+2E+z+w`

`=boxed{p+2Q-2Lc+J/2.}`

The heavy overlap `d`, the total overlap `S`, and the boundary coordinate `k` cancel from this score.  Condition (F) therefore produces a forbidden zero-sum.

> **Negative-even certificate theorem.** Every boundary row admitting an even `J` satisfying (A)--(F) is impossible, with the explicit occurrence vector above.

This is a multiplier-existence interface, not a list of multipliers.  Future work only has to prove that an admissible `J` exists in the residual arithmetic ranges.

## 4. The universal `J=2` central band

The first member already gives a useful all-prime elimination.

For `J=2`, one has `tau=1`, `L=1`, and the score is

`p+2Q-2c+1`.

Thus every boundary row satisfying

`3k+1<=H,`

`3(S-k)<=p,`

`3c+2d+epsilon<=p,`

and

`2c>2Q+1-H`

is impossible.

Writing `p=6a+1` or `p=6a+5`, the last inequality is uniformly

`2c>a+1`,

where `a=floor(p/6)`.

This explains the large central region killed experimentally by the scalar `-2`: it is a consequence of one exact certificate, not a prime-by-prime pattern.

## 5. Strategic consequence

The exceptional denominator-three rank-three problem has now been reduced in two ways:

1. all new-multiplicity interiors are removed, leaving the strip `0<=k<S`;
2. on that strip, the mixed zero-sum problem is converted to selecting an even `J` under elementary interval/capacity inequalities, with an exact score independent of `d,k`.

The next target should therefore be a rotation/interval selector for `J`, possibly using two adjacent allowed residue classes modulo three.  A broad search over `x,y` or over primes is no longer the right interface.

## Verification boundary

`check_a3_rank3_shared_donor_negative_even_v1.py` replays the doubling identities and every valid negative-even certificate through prime `401`, using explicit exceptions rather than removable `assert` statements.  It checks resource capacities, congruences, exact lengths, and the `J=2` specialization.  The finite replay is regression only; the theorem authority is the algebra above.

No full first-corridor support-seven theorem, `D_3(C_7^3)` value, all-prime `D_k` formula, novelty, or submission claim is made here.
