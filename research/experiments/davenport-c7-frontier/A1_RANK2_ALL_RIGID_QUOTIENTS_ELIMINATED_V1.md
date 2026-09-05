# Type one: every submaximal-overlap rigid quotient is impossible — V1

Status: **proved prime-uniform exclusion of all rigid cyclic quotients for `1<=c<H`**. Consequently every surviving quotient must have at least two atomic count-vector types and atomic-length gcd one.

## 1. Hypotheses

Let `p=2H+1>=7`, `m=3H+1`, and

\[
U=f_1^{p-1}f_2^{p-1}f_3^{p-1}s,\qquad s=f_1+f_2+f_3,
\]

where the `f_i` form a basis. Let `V=s^c x^r y^t` be a rank-two zero-sum companion, with distinct new values, `c+r+t=m`, `1<=c<H`, and `1<=r,t<=p-1`. Assume `UV` has no nonempty zero-sum of length below `m`. Put `d=H-c` and `R=x^r y^t`, so `|R|=p+d`.

Project the support plane modulo `<s>`. The two projected values are nonzero and distinct. Nonzero follows from rank two and the companion relation; coincidence would give `d` copies of a nonzero projected value summing to zero, with `1<=d<p`.

## 2. Rigidity forces an endpoint

Suppose the quotient has one atomic type `Q`, so `pi(R)=Q^k`, `k>=2`. Let `ell=|Q|` and let its canonical lifted light coefficient be `q`. The exact type-one budget in `A1_RANK2_QUOTIENT_BUDGET_AND_QUARTER_LAYER_ELIMINATION_V1.md` gives

\[
kq=p-c,\qquad k\ell=p+d.
\]

Subtracting yields `k|(c+d)=H`. It follows also that

\[
k\mid(p+d)-2H=d+1.
\]

The elementary rigid-power bound in `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md` gives `p+d<=p+k-1`, hence `k>=d+1`. Therefore

\[
\boxed{k=d+1,\qquad k\mid H.}
\]

Equality holds in that bound. Its equality classification forces, after a possible interchange,

\[
r=k,\qquad t=p-1,\qquad c=H+1-k.
\]

## 3. Every forced endpoint is already empty

Write `H=kL`, with integer `L>=1`. If `L=1`, then `c=1`; the entire type-one one-share layer is excluded by `A1_LIGHT_SUPPORT3_ONE_SHARE_ELIMINATION_V1.md`.

If `L>=2`, then `k<=H/2`, so

\[
c=H-k+1\ge H/2+1\ge\left\lceil H/2\right\rceil
=\left\lfloor(p+1)/4\right\rfloor.
\]

The actual donor in `UV` has the three saturated basis values, `c+1` copies of `s`, and `p-1` copies of `y`. The sharp augmentation theorem in `A1_SATURATED_AUGMENTATION_ELIMINATION_V1.md` therefore produces a zero-sum shorter than `m`. Both alternatives are impossible.

## 4. A necessary spectral condition throughout the face

The quotient is nonempty zero-sum, with two distinct nonzero cyclic values, each used fewer than `p` times. By `TWO_VALUE_LATTICE_ATOMS_AND_LENGTH_GCD_DICHOTOMY_V1.md`, exclusion of the rigid alternative implies

\[
\boxed{\gcd\{|P|:P\text{ is an atomic divisor of }\pi(R)\}=1.}
\]

This holds for every `1<=c<H`. It is not a proof that no gcd-one quotient can occur.

## 5. Review and scope

The coordinating researcher derived the divisibility argument. The quotient-structure researcher independently checked both budgets, the strict capacities, the equality classification, and the exact augmentation threshold `ceil(H/2)` in the prior proof. The augmentation theorem retains its attributed Bernoulli-pairing dependency; the new reduction itself is elementary. No prime or vector enumeration was used.

The quotient can have length at most `p` when `c>=H`; those layers are outside this theorem. The other mixed type-one cases and the full first corridor remain unresolved here.
