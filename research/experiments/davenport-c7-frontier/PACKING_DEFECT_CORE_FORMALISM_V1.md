# Packing-defect core formalism for multiwise Davenport constants — V1

Status: **proved equivalence and finite-core reduction**. The proposed value of `D_k(C_p^3)` is not proved here. Donor results retain donor ownership; novelty and priority remain `CANNOT_CHECK`.

## 1. One invariant for all multiwise levels

Let `G` be a finite abelian group of exponent `n`. For a zero-sum sequence `B`, let

`z(B)`

be the maximum number of nonempty zero-sum blocks in a factorization of `B`. Equivalently, it is the maximum number of pairwise disjoint nonempty zero-sum subsequences: the zero-sum remainder can always be factored into atoms.

Define the **packing defect at slope `n`** by

\[
\delta_n(B)=|B|-n z(B).
\]

Define the global defect envelope

\[
\mathfrak d_n(G)=\max\{\delta_n(B):B\in\mathcal B(G)\},
\]

where the empty block is allowed with defect zero.

This notation is branch-local. It is not asserted to be new or to be the standard name of an existing factorization invariant.

### Defect-envelope identity

Under the block-monoid convention used in this campaign,

\[
D_k(G)=\max\{|B|:B\in\mathcal B(G),\ z(B)\le k\}.
\]

Then

\[
\boxed{\mathfrak d_n(G)=\max_{k\ge1}\bigl(D_k(G)-kn\bigr).}
\]

Indeed, if `z(B)=m`, then `|B|<=D_m(G)`, so

\[
\delta_n(B)\le D_m(G)-mn.
\]

Conversely, let `B_k` attain `D_k(G)` and put `m=z(B_k)<=k`. Then

\[
D_k(G)-kn
 =\delta_n(B_k)-n(k-m)
 \le\mathfrak d_n(G).
\]

Thus the apparently separate sequence of constants `D_k(G)` has a single upper envelope: its largest intercept above the line of slope `exp(G)`.

The donor theorem that `D_k(G)` is eventually affine-linear with difference `exp(G)` is due to the multiwise-Davenport literature, including Freeze--Schmid. The identity above is elementary and does not require knowing the eventual stabilization index.

## 2. Finite Apéry-box reduction

Let `e_g` denote the coordinate vector of `g in G`. Since `n g=0`, the count vector `n e_g` is a zero-sum block.

Suppose `v_g(B)>=n` and put

\[
B'=B g^{-n}.
\]

Then `B'` is zero-sum and

\[
z(B)\ge z(B')+1.
\]

Consequently

\[
\delta_n(B)
 =|B'|+n-nz(B)
 \le |B'|-nz(B')
 =\delta_n(B').
\]

Repeatedly remove such `n`-blocks. The defect never decreases and the resulting zero-sum count vector lies in the finite box

\[
0\le v_g(B)\le n-1\qquad(g\in G).
\]

Therefore `\mathfrak d_n(G)` is finite and is attained in this box. In affine-semigroup language this is the finite Apéry box of the zero-sum congruence semigroup with respect to the pure kernel generators `n e_g`.

### A shortest maximizer is short-free

Choose, among all blocks attaining `\mathfrak d_n(G)`, one of minimum length. If it contains a nonempty zero-sum subsequence `A` with `|A|<=n`, put `R=BA^{-1}`. Then

\[
z(B)\ge z(R)+1
\]

and hence

\[
\delta_n(B)
 \le \delta_n(R)+|A|-n
 \le \delta_n(R).
\]

Thus `R` is a shorter defect maximizer, a contradiction. Therefore a shortest nonempty maximizer contains no nonempty zero-sum subsequence of length at most `n`.

This proves the exact reduction

\[
\boxed{
\mathfrak d_n(G)
 =\max\{\delta_n(B):B\text{ is zero-sum and }n\text{-short-zero-free}\}.
}
\]

Short-freeness already implies every multiplicity is below `n`, so the displayed domain is finite.

This is the key bridge from the global all-`k` problem to the projective-capacity machinery developed in the present lane.

## 3. Exact specialization to `C_p^3`

Let `p>=5` be prime and `G=C_p^3`. Put

\[
M_p=D_2(G)-2p=\frac{5p-5}{2}.
\]

The donor-derived value

\[
D_2(G)=\frac{9p-5}{2}
\]

and the Freeze--Schmid lower line give

\[
D_k(G)\ge L_k(p):=kp+M_p
       =\frac{(2k+5)p-5}{2}
\qquad(k\ge2).
\]

### Global equivalence theorem

The following are equivalent.

1. For every `k>=2`,

   \[
   D_k(C_p^3)=kp+M_p.
   \]

2. Every zero-sum block `B` over `C_p^3` satisfies

   \[
   \delta_p(B)\le M_p.
   \]

3. Every `p`-short-zero-free zero-sum block in the finite multiplicity box satisfies the same inequality.

Proof that 2 and 3 are equivalent is the shortest-maximizer reduction above. If 2 holds, then for `z(B)=m<=k`,

\[
|B|=pm+\delta_p(B)\le pk+M_p,
\]

so `D_k<=pk+M_p`; the donor lower line gives equality.

Conversely assume 1. If `z(B)=m>=2`, then

\[
|B|\le D_m(G)=pm+M_p.
\]

If `z(B)=1`, then `B` is an atom and the classical p-group value gives

\[
\delta_p(B)\le D(G)-p=2p-2\le M_p.
\]

Thus 2 follows.

Hence the full prime-uniform target is exactly the single inequality

\[
\boxed{
|B|-p z(B)\le\frac{5p-5}{2}
\quad\text{for every zero-sum block }B\text{ over }C_p^3.
}
\]

No induction in `k` is needed once this defect inequality is proved.

## 4. Hilbert-basis minimum-cost formulation

Represent a zero-sum count vector by

\[
x\in S_G:=\{x\in\mathbb N^G:\sum_g x_g g=0\}.
\]

Fix `x`. Let `H_x` be the finite list of all atoms whose count vectors are coordinatewise bounded by `x`, and let `A_x` be the matrix having those atom vectors as columns. A factorization of `x` is a vector

\[
\lambda\in\mathbb N^{H_x},\qquad A_x\lambda=x.
\]

The atoms are precisely the Hilbert-basis elements of the zero-sum congruence semigroup. Moreover

\[
z(x)=\max\{\mathbf1^T\lambda:A_x\lambda=x,\ \lambda\ge0\}.
\]

Assign each atom `h` the cost

\[
c_h=|h|-p.
\]

For every factorization `lambda` of `x`,

\[
c^T\lambda
 =\sum_h |h|\lambda_h-p\mathbf1^T\lambda
 =|x|-p\mathbf1^T\lambda.
\]

Therefore

\[
\boxed{
\delta_p(x)=
\min\{c^T\lambda:A_x\lambda=x,\ \lambda\ge0\}.
}
\]

On a `p`-short-zero-free core every dividing atom has length in

\[
p+1,\ldots,3p-2,
\]

so every atom cost lies in `1,...,2p-2`.

The general Davenport problem is thus a bounded minimum-cost Hilbert-basis factorization problem.

## 5. Exact Graver-augmentation criterion

Let `\mathcal G(A_x)` be the Graver basis of the integer kernel of `A_x`. A move `g in \mathcal G(A_x)` is

- **applicable** to `lambda` if `lambda+g>=0`, equivalently `g^-<=lambda`;
- **positive-gain** if `\mathbf1^Tg>0`.

Because `A_xg=0`, the total term length is preserved, and

\[
c^Tg=-p\mathbf1^Tg.
\]

Thus a positive-gain move increases factorization length and decreases defect cost by an integral multiple of `p`.

> **Terminal-factorization lemma.** A factorization `lambda` has maximum possible length in its fiber if and only if no applicable positive-gain Graver move exists.

One direction is immediate. For the other, suppose a longer factorization `mu` exists. The difference `mu-lambda` lies in the integer kernel and has a sign-compatible decomposition into Graver elements. Every component is applicable because its negative part is bounded by `(mu-lambda)^-<=lambda`, and at least one component has positive coordinate sum because `1^T(mu-lambda)>0`.

Combining this with the minimum-cost identity gives an exact fourth equivalent formulation of the conjectured line:

> For every `p`-short-zero-free box vector `x` and every factorization `lambda` of `x` with
>
> \[
> c^T\lambda>M_p,
> \]
>
> there is an applicable positive-gain Graver move.

Equivalently, there is no Graver-terminal factorization above cost `M_p`.

This condition is finite for each prime: the box vectors, their dividing atoms, their factorization fibers and their Graver bases are all finite. It is not proposed as a practical brute-force algorithm over all `p^3` coordinates; projective geometry and support reductions must be applied before constructing `H_x`.

## 6. Terminal `(p,m,q)` defect cores

A **terminal `(p,m,q)` defect core** is a pair `(x,lambda)` satisfying

1. `x` is a `p`-short-zero-free zero-sum box vector over `C_p^3`;
2. `lambda` is a factorization of `x` with `m=1^T lambda=z(x)`;
3. `lambda` has no applicable positive-gain Graver move;
4. for some integer `q>=1`,

   \[
   |x|-pm=M_p+q.
   \]

The proposed all-`k` formula holds if and only if no such terminal core exists for any `m,q`.

The cases `m=1` and `m=2` are excluded by the classical Davenport value and the verified `D_2` formula, so every terminal defect core has `m>=3`.

### Atomic excess signature

Write a maximum-length factorization as atoms `U_1...U_m` and put

\[
e_i=|U_i|-p.
\]

Then

\[
1\le e_i\le2p-2,
\qquad
\sum_{i=1}^m e_i=M_p+q.
\]

Moreover every selected subproduct of `r` atoms has packing number exactly `r`; otherwise replacing those `r` atoms by more blocks would lengthen the full factorization. In particular, applying the exact `D_2` value to every pair gives

\[
\boxed{e_i+e_j\le M_p\quad(i\ne j).}
\]

This is the factorization-theory signature grammar to apply before any vector enumeration.

## 7. Uniform support and projective consequences

A terminal `(p,m,q)` core has length

\[
N=pm+M_p+q.
\]

The complement-multiplicity lemma in `SHORTFREE_COMPLEMENT_SUPPORT_BARRIER_V1.md` yields a uniform support bound.

> **Terminal-core support bound.** Every terminal defect core satisfies
>
> \[
> |supp(x)|\ge m+4.
> \]

A support of size at most `m+2` has insufficient capacity because

\[
N-(m+2)(p-1)=m+\frac{p-1}{2}+q>0.
\]

For support `s=m+3`, its capacity deficit is

\[
\Delta=s(p-1)-N=\frac{p-1}{2}-m-q.
\]

If `Delta<0`, capacity again fails. Otherwise

\[
s+\Delta=\frac{p+5}{2}-q\le p,
\qquad
2\Delta=p-1-2m-2q\le p-2,
\]

so the embedded `p`-complement is a forbidden short zero-sum.

Every occupied projective direction carries at most `p-1` terms. Hence the number `r` of projective directions satisfies

\[
r\ge
\left\lceil
\frac{pm+M_p+q}{p-1}
\right\rceil
=
\left\lceil
m+\frac52+\frac{m+q}{p-1}
\right\rceil.
\]

Every projective line corresponds to a copy of `C_p^2`; the donor identity `eta(C_p^2)=3p-2` bounds its occupancy by `3p-3`. When Property C is available, the extra rich-plane deficit used in `SUPPORT8_DEFICIT_GEOMETRY_V1.md` applies unchanged.

Thus every terminal core is constrained simultaneously by

- a bounded excess partition;
- support at least `m+4`;
- projective direction capacity;
- plane-incidence deficit;
- a primitive positive modular kernel;
- Graver terminality.

## 8. The current `p=7`, `D_3` frontier is one slice

For `p=7`,

\[
M_7=15.
\]

A hypothetical length-37 obstruction has `z(B)=3` and

\[
\delta_7(B)=37-7\cdot3=16=M_7+1.
\]

It is therefore exactly a terminal-core candidate with signature

\[
(p,m,q)=(7,3,1).
\]

The completed support-seven theorem and support-eight one-projective-collision theorem eliminate bounded subfamilies of this single slice. The surviving support-eight branch has eight actual values on eight distinct projective directions. The two length-19 corridors are terminal-factorization subcases further restricted by the projective line-fiber avoidance theorem.

This reframes the existing computations as verified faces of one general augmentation problem rather than isolated searches.

## 9. Cross-context translations

- **Factorization theory:** `delta_p(B)` is the minimum total atom excess `sum(|U|-p)` among factorizations of `B`.
- **Generalized Noether numbers:** using the donor equality `beta_k(G)=D_k(G)` for abelian groups, the defect envelope is the largest pre-asymptotic degree intercept `beta_k(G)-kp`.
- **Affine semigroups:** short-free maximizers lie in a finite Apéry box and factor through Hilbert-basis elements.
- **Graver theory:** a counterexample is exactly a bounded factorization that is terminal under every positive-gain Graver augmentation while retaining cost above `M_p`.
- **Hypergraph matching:** atom occurrences are algebraic hyperedges; the defect is the minimum total edge excess above `p` in a full atom partition.
- **Coding and finite geometry:** box vectors are positive bounded codewords of a projective parity-check matrix, while factorization is conformal codeword decomposition.

## 10. What remains to prove

The general formalism is now exact, but it does not itself establish the desired inequality. The load-bearing residual is:

> Prove that every `p`-short-zero-free positive kernel vector over `C_p^3` whose terminal atomic excess exceeds `(5p-5)/2` admits a positive-gain conformal/Graver augmentation.

A successful proof may be uniform, or it may first show that all terminal cores fall into finitely many projective exceptional families that can be eliminated or retained explicitly.

## Donor and claim boundary

- The classical p-group Davenport value, the exact `D_2` formula, the Freeze--Schmid lower line and eventual linearity, `eta(C_p^2)`, Property C where invoked, generalized Noether-number identities, and the Graver conformal-decomposition theorem are donor structure.
- The term “packing defect” is descriptive branch notation, not a priority claim.
- No statement here says that `D_3(C_7^3)` or the all-prime formula is solved.
- The theorem proved here is the equivalence and finite-core/augmentation reduction.