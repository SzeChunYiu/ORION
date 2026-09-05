# Type two: the entire rank-two saturated new-value boundary is empty — V1

Status: **proved prime-uniform complete boundary elimination**. For every prime `p>=7`, a rank-two light-share companion cannot have either new value with multiplicity `p-1`. The proof crosses the exact scalar barrier by combining quotient parity, the donor inverse theorem with one missing `g`, and a mixed singleton completion.

## 1. The theorem

Let `p=2H+1>=7` be prime, `m=3H+1`, and

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad e_1+e_2=2(s-g),
\]

where `(e1,e2,g)` is a basis. There is no rank-two zero-sum companion

\[
\boxed{V=s^c x^r y^{p-1},\qquad c+r=H+1,
\qquad c,r\ge1,}
\tag{1}

with distinct new values `x,y`, for which `UV` has no nonempty zero-sum shorter than `m`. By swapping the new values, this excludes saturation of either new multiplicity.

Suppose otherwise. Then `V` is an atom, and its relation is

\[
cs+rx-y=0.
\tag{2}
\]

## 2. At every submaximal overlap, parity forces the exact barrier family

Assume `r>=2`, equivalently `c<H`. Put `d=H-c=r-1`, and project the support plane modulo `<s>`. Equation (2) gives `bar(y)=r bar(x)`, with both projected values nonzero.

For `1<=j<=r-1`, put

\[
b_j=[-j r^{-1}]_p,qquad Y_j=x^j y^{b_j}.
\]

Every `Y_j` is an actual nonempty proper projected-zero subsequence of `R=x^r y^(p-1)`. The exact quotient-window theorem gives a canonical light coefficient `q_j` and a defect

\[
D_j=2q_j-(j+b_j),\qquad 1\le D_j\le d=r-1.
\]

To identify it, write its rank-two coefficient relation as

\[
(-q_j,j,b_j)=\lambda(c,r,p-1)\quad\text{in }\mathbb F_p^3.
\]

The same subtraction as in the quotient-budget theorem gives `D_j==(d+1)lambda=r lambda==j (mod p)`. Both `D_j` and `j` lie in `[1,r-1]`, so this is the ordinary equality

\[
D_j=j,\qquad b_j=2(q_j-j).
\tag{3}
\]

Thus every `b_j` is even. Append `b_0=0` and `b_r=p-1`, which are even as well. The least-residue recurrence is

\[
b_{j+1}=b_j+b_1-\eta_jp,\qquad \eta_j\in\{0,1\}.
\]

All `b_j` and `b_1` are even, whereas `p` is odd. Therefore every `eta_j` is zero: **no wrap is possible anywhere in this entire progression**. It follows that

\[
rb_1=p-1.
\]

At `j=1`, defect one and the lower shifted-depth inequality force `q_1` odd. By (3), `q_1=1+b_1/2`; hence `b_1` is divisible by four. We have proved the exact necessary form

\[
\boxed{p=4rL+1,\qquad
c=2rL+1-r,\qquad L\ge1.}
\tag{4}
\]

In particular, `c>=r+1>=3`. This reduction uses all proper quotient-zero parts, including ones that are not atoms. Applying the atom-length formula to them would not be justified; the coefficient congruence and defect window above suffice.

## 3. The actual donor fixes the high-multiplicity value

The product in (1) contains

\[
e_1^{p-1}e_2^{p-1}g^{p-2}s^{c+2}y^{p-1}.
\]

Under (4), `5<=c+2<=H+1`. The exact theorem in `A2_ONE_MISSING_G_DONOR_INVERSE_CLASSIFICATION_V1.md` therefore forces

\[
\boxed{y=(A,-A,1),\qquad A\ne0.}
\tag{5}
\]

The exceptional family of that theorem exists only at `K=3` or at `p=11,K=4`, so neither exception occurs here. No additional `g` occurrence has been inserted.

## 4. One x occurrence now gives a short zero-sum

In the basis `(e1,e2,g)`, the sum of the first two coordinates of `s` is one, and its third coordinate is one. From (2) and (5),

\[
-x=\delta s-r^{-1}y,\qquad \delta=cr^{-1}.
\]

Using (4), the least residues are

\[
r^{-1}=p-4L,\qquad \delta=p-2L-1.
\]

Thus the first-coordinate sum and third coordinate of `-x` are

\[
w=p-2L-1,\qquad C=2L-1.
\]

They satisfy `H+1<=w<=p-2` and `1<=C<=p-1`. The exact original-donor fiber envelope from `A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md` gives

\[
\rho_U(-x)\le
\begin{cases}
w+1=p-2,&L=1,\\
w+C-1=p-3,&L\ge2.
\end{cases}
\]

Completing one actual occurrence of `x` by that subsequence of `U` yields a nonempty zero-sum of length at most `p-1` or `p-2`, respectively. Both are below `m`. This contradicts the hypothesis and eliminates every `r>=2` row.

The scalar barrier remains correct: a singleton of `x` is not a relation-multiplier certificate with a purely radial target. The inverse theorem has determined its transverse coordinate sum and third coordinate, which is precisely the extra geometric information used here.

## 5. The top singleton row is also empty

It remains to handle `r=1`, `c=H`. Take the subdonor with `K=H+1` from the actual `c+2=H+2` light occurrences. For every prime `p>=7`, the one-missing-`g` inverse theorem at this `K` forces (5): at `p=7`, `K=4` has no exception, and at `p=11`, `K=6` is above the exceptional capacity.

Now `x=y-Hs`, so `-x` has first-coordinate sum `w=H` and third coordinate `C=H-1`. The middle-fiber formula gives

\[
\rho_U(-x)\le H+(H-1)=p-2.
\]

The resulting singleton completion has length at most `p-1<m`. This excludes the last row and proves the theorem.

## 6. Complete-layer and rigid-power consequences

The new theorem has three immediate consequences:

1. **The entire layer `c=H-2` is empty for all primes `p>=7`.** The rigid-cube reduction in `A2_RANK2_H_MINUS_TWO_RIGID_CUBE_REDUCTION_V1.md` leaves only a saturated row, and Section 4 now eliminates it. This closes the endpoint that was deliberately left open in that earlier intermediate note.
2. **Every rigid-power quotient is impossible throughout `1<=c<H`.** Section 4 of `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md` forces exactly a saturated row from any quotient with only one atomic divisor. Thus a surviving quotient must have at least two distinct atomic divisors.
3. **The previous `c=H-1` closure now has a structural proof without the rank-two multiplicity donor.** Its rigid square reduces by the elementary rigid-power theorem to a saturated row, which this theorem eliminates. The old proof and its published computationally assisted donor remain preserved, but that donor is no longer necessary for this complete-layer conclusion. The present chain uses the attributed Bernoulli-pairing theorem and exact structural proofs, with no bounded enumeration input.

Together with the previously proved rank-three saturated-boundary eliminations, neither rank of the exceptional type-two support-six face can now have a new multiplicity equal to `p-1`.

## 7. Audit and remaining boundary

The review checked all proper projected-zero parts in Section 2, the carry parity including the final value `b_r=p-1`, the `c>=3` consequence, every capacity and exceptional case of the smaller-donor inverse theorem, both modular inverses in Section 4, and the distinct top-singleton argument. The final representation uses actual occurrences of the original maximal atom through its proved depth envelope.

This is an internally reviewed prime-uniform proof, not independent referee approval. The unsaturated rank-two high-overlap cases and unsaturated rank-three type-two mixed cases remain. The full first corridor, `D_3(C_7^3)`, and the generalized Davenport formula are not asserted.
