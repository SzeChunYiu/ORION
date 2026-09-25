# Type two: unsaturated inverse rigidity also tolerates the missing g copy

Status: **proved prime-uniform inverse extension and top-overlap eliminations**. The bounded-hole argument remains valid for the actual rank-two donor, which has only `p-2` copies of `g`. It closes a growing multiplicity band on the remaining rank-two top boundary.

## 1. The restricted donor

Use `p=2H+1>=7`, `m=3H+1`, `u=H+1=2^{-1}`, `s=(u,u,1)` in a basis `(e1,e2,g)`, and put

\[
B_K^-=e_1^{p-1}e_2^{p-1}g^{p-2}s^K,
\qquad K\ge2,
\qquad 1\le b\le H-2.
\]

Suppose `B_K^- y^{p-b}` has no nonempty zero-sum of length below `m`, and write `y=(A,B,C)`.

**Theorem.** All three coordinates are nonzero. The lower-half intersection

\[
J=\{j\in\mathbb F_p^*:
          1\le[jA]_p,[jB]_p\le H\}
\]

has size at most `b`. Therefore the centered representatives of `-B/A` and `-A/B` have magnitude at most `2b+1`, and

\[
\boxed{p>(2b+1)^2+1\quad\Longrightarrow\quad A+B=0.}
\tag{1}
\]

The bound `b<=H-2` records the two extra formal-completion indices that must be removed in the zero-coordinate argument. It follows automatically from the displayed prime threshold, but is retained for the stronger centered restrictions below that threshold.

## 2. Nonzero coordinates with the actual missing occurrence

Keep the formal saturated lengths

`L_j=j+[-jA]_p+[-jB]_p+[-jC]_p`.

They are actual completions except when `C!=0` and `j=C^{-1}`, which would require `p-1` copies of `g`. Work in the complementary core `{b,...,p-b}` and remove both `C^{-1}` and `-C^{-1}` when necessary. At least

\[
p-2b-1=2(H-b)\ge4
\]

indices remain, in complementary pairs, and all their formal completions are individually available in `B_K^-`.

Exactly the proof in Section 2 of `A2_TRUNCATED_POWER_HALF_INTERVAL_RIGIDITY_V1.md` now applies on this reduced core. With one nonzero coordinate, the complementary sum is `2p<2m`. With two, it is `3p=2m+1`, so all lengths must be `m` or `m+1`; either the nonzero modular slope makes at least four lengths distinct, or slope zero makes them impossible multiples of `p`. The zero vector is forbidden by its singleton. Hence `ABC!=0`.

## 3. The two substitutions repair the missing-copy seam

Take `j in J` in the original, unreduced core `{b,...,p-b}`. Put

`a=[-jA]_p`, `d=[-jB]_p`, `w=[-jC]_p`.

As before `a,d>=u` and `w>=1`. The one-`s` completion has remaining basis counts

`a-u,d-u,w-1`.

In particular `w-1<=p-2`, even at the formally unavailable index `w=p-1`. Thus this certificate is genuinely available with length `L_j-(p+1)`.

If `w<=p-2`, use two copies of `s` at the complementary index. Its remaining axis counts are `[jA]_p-1,[jB]_p-1`, nonnegative because the coordinates are nonzero. Its remaining `g` count is

\[
p-w-2\in[0,p-3],
\]

which fits the restricted donor, including when the unshortened complementary completion would have required `p-1` copies. Hence `L_{p-j}-2>=m` is valid and the first certificate has length at most `m-2`, contradiction.

Again the only possible member of `J` inside the core is `j=C^{-1}`. Outside it, at most one member lies in each of the `b-1` antipodal pairs. Therefore `|J|<=b`. The interval-stability theorem supplies (1) and both centered bounds.

The missing `g` occurrence has not been silently restored: the two substitutions themselves lower the relevant `g` counts into the actual donor range.

## 4. Exact half-power plane classification survives as well

For

\[
3\le K\le H+1,\qquad H-1\le t\le p-1,
\]

the plane classification in `A2_HALF_POWER_PLANE_INVERSE_CLASSIFICATION_V1.md` holds unchanged with `B_K^-` in place of `B_K`: precisely `y=(A,-A,1)`, `A!=0`, and the stated `C=2,A=+/-3^{-1}` exceptions at `K=3` or `(p,K)=(11,4)` survive.

Here is the complete capacity adjustment. If `A=0` and `C` is neither zero nor one, the singleton completion uses `p-C<=p-2` copies of `g`; if `C=1`, two of the available copies of `y=g` give `g^p` together with `g^{p-2}`. The requirement `t>=H-1>=2` supplies those two copies. At `C=0` there is a singleton zero-sum when `A=0`, or the axis-only certificate when `A!=0`.

Every other necessity certificate in that note uses at most `p-2` copies of `g`: its Euclidean certificate has count `R-min(2,R)`, its inverse-two certificate has count `H-2`, and its third-coordinate-two certificates use zero or one. All powers remain at most `H-1`. Sufficiency follows either from the full all-subsequence proof or simply by deleting one occurrence from its proved short-free donor. This checks both directions.

Together with (1), this is an exact inverse classification without a plane hypothesis whenever `p>(2b+1)^2+1` and `t=p-b` in the stated donor range.

## 5. A new eliminated band on the rank-two top overlap

Consider the remaining rank-two type-two configuration

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad V=s^H x^r y^{p-r},
\qquad1\le r\le H,
\qquad\sigma(V)=0.
\]

The previously proved donor-only argument already excludes odd `H`. For even `H`, write `p=4L+1`, `H=2L`. If

\[
\boxed{p>(2r+1)^2+1,}
\tag{2}
\]

then `UV` contains a nonempty zero-sum shorter than `m`.

Indeed the actual donor is `B^-_{H+2}` and the high value occurs `p-r` times. Condition (2) implies `r<=H-2`, so Section 1 with `b=r` forces `y` into the plane `A+B=0`. The exact top plane-extension theorem in `A2_SHARED_DONOR_PLANE_RIGIDITY_V1.md`, Section 4, permits at most `L` copies of any plane value in a short-free extension of this donor. But

`p-r>=H+1=2L+1>L`.

This is a contradiction. The argument uses the actual `g^{p-2}` donor throughout.

Consequently a surviving rank-two top row must obey both the previous restrictions and the new inequality `p<=(2r+1)^2+1`. This closes a prime-uniform growing band in the smaller new multiplicity; it does not close all values of `r`.

## 6. The corresponding rank-three top band

For a rank-three companion

\[
V=s^H g x^{b-1}y^{p-b},
\qquad 2\le b\le H+1,
\]

the same conclusion holds whenever

\[
\boxed{p>(2b+1)^2+1.}
\tag{3}
\]

Odd `H` is again excluded by the donor-only certificate. With even `H`, apply the full-basis bounded-hole theorem to its actual donor `B_{H+2}`; (3) ensures its required `b<=H-1`. It forces the high value into the plane. The smaller subdonor `B^-_{H+2}` already forbids its `p-b>=H+2>L` available copies by the same exact plane theorem.

In particular the whole `b=2,c=H` rank-three row is excluded for every permitted prime `p>=29`.

These are new eliminated boundary bands. They do not establish emptiness of the full top overlap, the remaining mixed rank-three faces, the full first corridor, or any unproved Davenport value. The proof was checked locally for the reduced core, both repaired seams, every imported plane-certificate capacity, and the exact strict thresholds.
