# Type-two saturated boundary: generalized remainder selector and uniform overlap closure — V1

Status: **proved prime-uniform generalized remainder selector and complete elimination of every saturated-boundary overlap `c>=7`**. The exact donor inverse theorem fixes the high-multiplicity value's plane. The other value then satisfies a coordinate identity, allowing one explicit power to be completed by saturated basis terms. A fixed fourth multiple of the prime combines with the circular-gap theorem to cover every prime at `c>=7`.

This leaves the lower overlaps and unsaturated boundary outside the complete-closure claim, and does not assert a generalized Davenport equality.

## 1. Statement and exact inverse-theorem gate

Let `p=2H+1>=7` be prime, `m=3H+1`, `u=H+1=2^(-1)` in `F_p`, and use the basis `(e1,e2,g)` with `s=(u,u,1)`.

Consider

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`,

`V=s^c g x^r y^(p-1)`, `r=H-c>0`, `c>=2`.

Suppose `V` is zero-sum and the displayed occurrences are available. Write the exact division identity

`p=2c q+v`, `q=floor(p/(2c))`, `1<=v<=2c-1`.           (1)

The remainder is positive and odd, since `p` is odd and `2c<p`.

> **Theorem.** If
>
> `boxed{q>v,}`
>
> then `UV` contains a nonempty zero-sum of length at most `m-1`.

Assume short-freeness toward contradiction. The actual shared donor contains

`e1^(p-1)e2^(p-1)g^(p-1)s^(c+2)`.

Since `3<=c+2<=H+1`, `A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md` applies. For `c>=2` its sole exceptional non-main alternative is `(p,c)=(11,2)`. That pair has `q=2,v=3` in (1), so it fails the present hypothesis. Thus throughout the theorem's range the exact inverse theorem gives

`y=(A,-A,1)`, `A!=0`.

No plane condition is imposed without this inverse-theorem gate.

## 2. The low-multiplicity value satisfies a fixed coordinate identity

The companion relation is

`r x=y-cs-g`.

The sum of the first two coordinates of its right side equals `-c`; its third coordinate also equals `-c`. Therefore

`x1+x2=x3=-c/r`.

Since `r=H-c==-(2c+1)/2 (mod p)`, this is the exact field identity

`boxed{x1+x2=x3=2c/(2c+1).}`                          (2)

The denominator is nonzero because `1<=2c+1<=p-2` under `r>0`.

## 3. A positive actual power has a small negative third coordinate

Set

`a=q-v`.

The theorem's hypothesis gives `a>=1`. Its upper occurrence capacity holds:

`r-a=(c-1)q+(3v-1)/2-c>=0`.

For example, substituting `q>=v+1` bounds this expression below by

`(c+1/2)v-3/2`,

which is nonnegative for `c>=2,v>=1`. Thus `1<=a<=r` and `x^a` is an actual available subsequence.

By (1),

`q(2c+1)=p+q-v=p+a`.

Multiplying this congruence by the coordinate value in (2) gives

`a x3==2cq==-v (mod p)`.

Hence the target `-a x` has third coordinate equal to the ordinary remainder `v`.

## 4. Complete this power using only saturated basis occurrences

Let

`P=[-a x1]_p`, `Q=[-a x2]_p`.

Equation (2) implies `P+Q==v (mod p)`. Since both are least nonnegative residues and `1<=v<=p-1`, their ordinary sum is one of exactly two possibilities:

`P+Q=v` or `P+Q=p+v`.

Consequently

`boxed{x^a e1^P e2^Q g^v}`                            (3)

is a nonempty zero-sum subsequence. All counts fit: `a<=r`, `P,Q<=p-1`, and `v<=2c-1<p-1`; the shared `g` capacity is `p-1`.

Its length is at most

`a+P+Q+v<=p+a+2v=p+q+v`.

Finally,

`H-1-q-v=(c-1)q-(v+3)/2>=0`.

Indeed `q>=v+1` bounds the right side below by

`((2c-3)v+2c-5)/2`,

which is nonnegative for `c>=2,v>=1`; its lowest endpoint is zero at `c=2,v=1`. Therefore (3) has length at most `p+H-1=m-1`, giving the contradiction.

The certificate itself uses no `s` or `y` occurrences. Their presence first enforces the exact inverse form, which then constrains the other value through the full companion relation.

## 5. A simple all-prime overlap corollary

If `p>=4c^2`, then

`q=floor(p/(2c))>=2c>v`.

Thus the entire rank-three boundary row with `t=p-1`, `r=H-c`, is impossible whenever

`boxed{c>=2, p>=4c^2.}`

The exact remainder condition in Section 1 is stronger and should be retained. For example, it can hold when `p<4c^2`; the proof does not require discarding such rows.

## 6. Remaining interface and review

The updated circular-gap theorem in `A2_RANK3_SATURATED_BOUNDARY_CIRCULAR_GAP_ELIMINATION_V1.md` removes rows satisfying

`p<(c+1)^2`.

The initial `q>v` theorem removes rows including the range `p>=4c^2`. Those two estimates alone leave a middle range. Sections 7--9 below supply a more general selector and close that middle range completely for `c>=7`. The special `c=1` inverse family is outside this note's complete-closure statement.

One useful general interface is explicit in the proof: on the main inverse family, any available power `x^a` with least negative third-coordinate residue `w` satisfying

`a+2w<=H-1`

has a saturated-basis completion below `m`. The selected `a=q-v,w=v` proves existence under the stated remainder condition; universal existence is not asserted.

The root and a separately tasked proof auditor independently checked (2), the actual `x` capacity, both possible ordinary residue sums, the strict score, and the sufficient quadratic bound. The argument is symbolic and prime-uniform. No prime or coordinate enumeration is used as theorem authority.

## 7. Generalized selector using any admissible multiple of the prime

Let `1<=ell<=c-1` and divide

`ell p=2c q_ell+v_ell`, `1<=v_ell<=2c-1`.

The remainder is nonzero: `p` is coprime to `2c`, and `ell` is strictly between zero and `2c`. Suppose

`1<=q_ell-v_ell<=r`,

`q_ell+v_ell<=H-1`.                                  (4)

Then the row is impossible. To prove this, put `a=q_ell-v_ell`. The exact congruence

`q_ell(2c+1)=ell p+a`

replaces the corresponding identity in Section 3, and again gives `-a x3==v_ell`. The same actual occurrence vector (3), with `v_ell` in place of `v`, has length at most `p+q_ell+v_ell<=m-1`.

The exact inverse-theorem exception `(p,c)=(11,2)` does not enter (4): its only permitted `ell` is one, giving `q_ell=2,v_ell=3` and a negative `a`. Thus the inverse-theorem gate to the main family is valid for every row satisfying (4), not only the initial `ell=1` case.

> **Generalized remainder-selector theorem.** If at least one integer `ell` in `[1,c-1]` satisfies the two capacity and score tests (4), the whole rank-three saturated boundary row is empty.

This is a sufficient criterion with explicit arithmetic hypotheses; the proof does not assume that such an `ell` always exists.

## 8. A linear prime threshold for every c>=2

Choose `ell=floor(c/2)`. For every `c>=2`,

`c/3<=ell<=c/2`.

If `p>=12c`, its division quotient satisfies

`q_ell>=floor(p/6)>=2c>v_ell`,

so `a=q_ell-v_ell` is positive. Moreover,

`a<=q_ell<=p/4<=H-c=r`,

where the last inequality follows from `p>=4c+2`, implied by `p>=12c`.

For the score,

`q_ell+v_ell<=p/4+2c-1<=(p-3)/2=H-1`,

because `p>=8c+2`, also implied by `p>=12c`. Thus (4) holds.

> **Linear-threshold corollary.** Every saturated boundary row with `c>=2` and `p>=12c` is impossible.

An earlier valid sharpening, retained for route provenance, is `p>=9c` when `c>=8`: then `floor(c/2)>=4c/9`, so `q_ell>=floor(2p/9)>=2c`, and the same capacity and score estimates apply. Section 9 supersedes the need to use that sharpening in the final large-overlap assembly.

## 9. A fixed fourth multiple closes every overlap c>=7

Assume `c>=7`. If `p<(c+1)^2`, the circular-gap theorem already eliminates the row. It remains to treat

`p>=(c+1)^2`.

In the generalized selector take `ell=4`, which lies in `[1,c-1]`, and write

`4p=2c q+v`, `q=floor(2p/c)`.

The positive remainder is even, hence

`2<=v<=2c-2`.

Also

`q>=2c+4>v`,

so `a=q-v` is positive. The single inequality

`(c-4)p>=c(4c-1)`                                    (5)

implies both remaining requirements in (4). First,

`q+v<=2p/c+2c-2<=(p-3)/2=H-1`,

where the second inequality is exactly (5). Second,

`a<=2p/c-2<=H-c`,

because this latter inequality needs only `(c-4)p>=c(2c-3)`, weaker than (5).

Finally (5) holds throughout the present range. At its lower endpoint,

`(c-4)(c+1)^2-c(4c-1)`

`=c^3-6c^2-6c-4`

`=(c-7)(c^2+c+1)+3>0`.

Since `c-4>0`, increasing `p` preserves the inequality. The generalized selector therefore eliminates every row with `p>=(c+1)^2` as well.

> **Uniform overlap theorem.** For every prime `p>=7`, a type-two first-corridor rank-three companion
>
> `V=s^c g x^(H-c)y^(p-1)`
>
> is impossible whenever `7<=c<=H-1`.

The two analytic arguments cover all primes at these overlaps, with no finite classification. The only overlaps outside this complete result are `c=1,...,6`; for `c=2,...,6`, the generalized remainder criterion and the circular-gap theorem may still eliminate further rows. The separate `c=1` inverse family and the `(p,c)=(11,2)` exception retain their explicit status.

The root, producing agent, and independent proof auditor checked the generalized congruence, the fourth-multiple bounds, the polynomial factorization, and the complete two-range assembly. No brute-force argument is used.
