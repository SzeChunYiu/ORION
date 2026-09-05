# Type two: the exact plane inverse form needs only H-1 powers

Status: **proved exact prime-uniform classification**. Within the opposite-coordinate plane, the previously saturated inverse form is already forced by `H-1` copies of the new value. The converse covers all subsequences. This reduces the required power range by roughly one half.

## 1. The theorem

Let `p=2H+1>=7` be prime, `m=3H+1`, `u=H+1=2^{-1}` in `F_p`, and `s=(u,u,1)` in a basis `(e1,e2,g)`. Suppose

\[
3\le K\le H+1,\qquad H-1\le t\le p-1,
\qquad B_K=e_1^{p-1}e_2^{p-1}g^{p-1}s^K.
\]

For `y=(A,-A,C)`, the sequence `B_K y^t` has no nonempty zero-sum of length below `m` if and only if one of the following holds:

1. `A!=0` and `C=1`;
2. `A=+/-3^{-1}`, `C=2`, and either `K=3` or `(p,K)=(11,4)`.

No companion relation is assumed. The plane condition is a hypothesis here; its separate unsaturated inverse justification is in `A2_TRUNCATED_POWER_HALF_INTERVAL_RIGIDITY_V1.md`.

## 2. A two-residue Euclidean selector

For every integer `C` in `[1,p-1]` other than `1,2,H+1`, write

\[
p=qC+R,\qquad q=\lfloor p/C\rfloor,\qquad1\le R<C.
\]

Then

\[
\boxed{q\le H-1,\qquad q+R\le H.}
\tag{1}
\]

For `C>=H+2`, one has `q=1` and `R<=H-1`. For `3<=C<=H`, one has `q>=2`. Except at `q=2,C=3`,

\[
(q-1)C\ge2q,
\]

because it holds for `q>=3,C>=3` and for `q=2,C>=4`. Since `p+1<=(q+1)C`, this yields

`p+1<=2q(C-1)`,

which is equivalent to `q+R<=H`. The omitted pair forces `p=7`, where `q+R=3=H`. The bound `q<=H-1` follows from `q<=floor(p/3)` for `C>=3`; it holds directly at `p=7` and from `p/3<=(p-3)/2` at `p>=11`.

## 3. Only third coordinates one and two survive

If `A=0`, then `y=Cg`; its singleton has an available saturated `g` completion of length at most `p`, or is itself zero when `C=0`. Hence `A!=0`. If `C=0`, the completion of `y` by the two axes has length `p+1<m`, so `C!=0`.

For every nonzero `P`, the forced first-coordinate pair at light counts one and two satisfies

\[
[-P-zu]_p+[P-zu]_p=p-z,
\qquad z\in\{1,2\}.
\tag{2}
\]

For `z=2`, this follows by writing `[P]_p=a` in `[1,p-1]`: the two residues are `p-a-1,a-1`. For `z=1`, if `a<=H` the residues are `H-a,H+a`; if `a>=H+1` they are `p+H-a,a-H-1`. Each pair sums to `p-1`.

Take `C` covered by Section 2 and put `z=min(2,R)`. The actual sequence

\[
y^q s^z
e_1^{[-qA-zu]_p}e_2^{[qA-zu]_p}g^{R-z}
\tag{3}
\]

is zero-sum. The power `q<=H-1<=t`, both light copies, and every basis count are available. Its length is

\[
p+q+R-z\le p+H-1=m-1.
\]

This excludes every third coordinate except `1,2,H+1`. For `C=H+1`, use `y s^2`, the pair counts in (2), and `g^{H-2}`. Its length is again `p+H-1`. Thus only `C=1,2` remain.

## 4. The exact exception at third coordinate two

Suppose `C=2`. Use `j=H-1` copies of `y` and three copies of `s`. Since `[-2j]_p=3`, no `g` term is needed. For a nonzero residue `P` with centered magnitude `d`, the pair at three light copies is

\[
[-P-3u]_p+[P-3u]_p=
\begin{cases}p-3,&d\le H-1,\\2p-3,&d=H.\end{cases}
\tag{4}
\]

This follows directly by locating `[P]_p` on the two sides of `H,H+1`. In the low case the length is `j+3+p-3=m-1`. Thus `jA=+/-H`, forcing `A=+/-H/(H-1)=+/-3^{-1}` in the field.

When `K>=4`, take `j=H-2`, four copies of `s`, and one copy of `g`, since `[-2j]_p=5`. The pair cost is `p-4` unless the centered magnitude of `jA` is one; this is the same least-residue calculation with even light count four. The low case has length `j+4+1+p-4=m-1`. Since `jA=+/-5/6`, its exceptional magnitude would force `5=+/-6 (mod p)`. The only permitted prime is `p=11`.

At `p=11`, `A=+/-4`. If `K>=5`, use three copies of `y`, five of `s`, and no `g`; the forced axis counts are `2,4` in either order. This has length `14<16=m`.

All powers just used are at most `H-1`. This proves every necessity statement without any access to the missing upper-half powers.

## 5. Converse for all subsequences

It suffices to prove survival even with `t=p-1`. Write a possible zero-sum's counts as `j` for `y`, `z` for `s`, `w` for `g`, and `a,d` for the axes.

For `A!=0`, `1<=j<=p-1`, and `0<=z<p`, the general pair inequality is

\[
a+d=[-jA-zu]_p+[jA-zu]_p\ge p-z.
\tag{5}
\]

The pair is congruent to `-z` and cannot be zero when `z=0` and `jA!=0`; for `z>0` its least nonnegative possible sum is `p-z`. When `j=0` and `z>0`, the same bound follows by the explicit even/odd light count: the pair is `2p-z` or `p-z`. When both `j,z` vanish, the saturated basis counts, each below `p`, force the empty sequence.

If `C=1` and `j>0`, the third-coordinate sum `j+z+w` is a positive multiple of `p`. Together with (5), the total length is at least `2p-z>=2p-K>=m`. Donor-only nonempty zero-sums obey the same lower bound.

If `C=2`, write `2j+z+w=Np` with positive integer `N`. Then the length is at least

\[
(N+1)p-j-z.
\tag{6}
\]

For `K=3`, `N>=2` makes this at least `2p-2>=m`. If `N=1`, a length below `m` would require `j+z>=H+2`, whereas feasibility gives `2j+z<=p`. For `z<=3`, their only possible joint solution is `j=H-1,z=3`. At `A=+/-3^{-1}`, this is the high case of (4), which is not short.

For `(p,K)=(11,4)`, the `N>=2` lower bound is `2p-3=19>m=16`. With `N=1`, the only possible strict-shortness candidates are `(j,z)=(4,3)` and `(3,4)`. The former is the high case of (4); the latter has centered magnitude `|jA|=1` and is the high four-light pair case. Their actual pair costs are respectively `2p-3` and `2p-4`, excluding both. Donor-only zero-sums in these exceptional cases have length at least `2p-K>=m` as well.

These checks exhaust all subsequences and prove the converse.

## 6. Combined unsaturated inverse form

Combining this theorem with the bounded-hole result yields an exact classification for `B_K y^{p-b}` under

\[
1\le b\le H-1,\quad 3\le K\le H+1,
\quad p>(2b+1)^2+1:
\]

the two families in Section 1 are precisely the short-free extensions, now without any plane hypothesis. Indeed the bounded-hole theorem forces the plane and `p-b>=H+2>H-1`, so every certificate above is available; the converse was proved with the larger power `p-1`.

For the unsaturated rank-three face `b=2`, every prime `p>=29` and every `2<=c<=H-1` therefore force

\[
\boxed{y=(A,-A,1),\qquad A\ne0.}
\]

The exact exceptional family cannot occur here because `K=c+2>=4` and `p!=11`. This is a structural inverse form for the remaining mixed problem, not its complete elimination.

All new implications use elementary division, interval boundaries, and actual occurrence certificates. The existing full-power plane proof helped identify which certificates already used at most `H-1` copies; the Euclidean selector proves the missing unrestricted-third-coordinate step. The proof was checked locally without a prime sweep or a claim of separate external review.
