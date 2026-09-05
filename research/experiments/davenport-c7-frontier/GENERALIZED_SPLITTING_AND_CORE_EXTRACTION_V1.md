# A generalized splitting criterion and local extraction of defect cores — V1

Status: **proved for every finite abelian group and every nonnegative integer defect threshold**. The global affine packing bound is equivalent to a one-term splitting statement on its exact boundary. Every counterexample contains a contraction core with unit excess and the precise stability laws below. The rank-three numerical target remains unproved.

## 1. The operation before the case structure

Let `G` be a finite abelian group of exponent `n>=2`. Let `z(B)` denote the maximum number of zero-sum factors of a zero-sum block `B`, and write

\[
\delta_n(B)=|B|-n z(B).
\]

Set `z(1)=delta_n(1)=0` for the empty block. Fix an integer `M>=0`.

A contraction replaces disjoint occurrence bundles by distinguished occurrences of their group sums. It preserves the total sum and does not increase the packing number. A pair contraction lowers that number by at most one: in an optimum, its two occurrences belong either to the same atom or to two atoms that can be merged into one zero-sum part.

Consequently, splitting one distinguished occurrence `g` of a zero-sum block `C` into `a,b` with `a+b=g` produces a block `C^{a,b}` satisfying

\[
\boxed{z(C^{a,b})-z(C)\in\{0,1\}.}
\tag{1}
\]

The labels matter when several occurrences have value `g`.

## 2. An exact generalized boundary criterion

> **Splitting criterion.** The following assertions are equivalent:
>
> 1. Every zero-sum block `B` over `G` satisfies `delta_n(B)<=M`.
> 2. For every zero-sum `C` with `delta_n(C)=M`, every distinguished occurrence `g|C`, and every additive splitting `g=a+b`,
>    \[
>    \boxed{z(C^{a,b})=z(C)+1.}
>    \tag{2}

If assertion 1 holds, a split retaining `z(C)` would have defect `M+1`, which is forbidden. Equation (1) then forces exactly one additional factor.

Conversely, suppose assertion 1 fails and choose a shortest counterexample `B`. Contract any pair to obtain `C`. Lifting gives `z(C)<=z(B)`, so

\[
\delta_n(C)\ge\delta_n(B)-1.
\]

Minimality gives `delta_n(C)<=M`; integrality forces `delta_n(B)=M+1`. In fact

\[
M\ge M+n\bigl(z(B)-z(C)\bigr),
\]

so `z(C)=z(B)` and `delta_n(C)=M`. The original pair is an additive splitting of its aggregate in `C` that creates no extra factor, contradicting assertion 2.

This criterion is a theorem about all finite abelian groups. It is not a proof that the splitting condition holds for the proposed rank-three intercept. In particular, proving it only on the two-factor boundary would just reprove the already known two-factor upper bound.

## 3. A counterexample yields its own core by contraction

Global length minimality can be replaced by a local extraction inside any specified counterexample `B_0`.

Every sequence of contractions is equivalent to one occurrence partition of `B_0`, each part replaced by its sum. There are finitely many such partitions. Among the coarsenings of `B_0` whose defect exceeds `M`, choose one, `B`, of minimum length. Then

\[
\delta_n(B)>M,
\]

and **every strict contraction of `B` has defect at most `M`**. No search over all group sequences, and no lower-level Davenport theorem, is needed for this existence argument.

The pair-contraction proof above applies verbatim. Writing `m=z(B)`, it gives

\[
\boxed{|B|=mn+M+1.}
\tag{3}

For any contraction `B/P` with positive cost `d=|B|-|B/P|`, let `h=m-z(B/P)>=0`. Its defect is exactly

\[
\delta_n(B/P)=M+1-d+nh.
\]

Contraction minimality therefore proves the general cost law

\[
\boxed{d\ge nh+1.}
\tag{4}

In particular, all prescribed disjoint bundles of total cost at most `n` can be contained simultaneously in a maximum atomic factorization. Every subset of at most `n+1` occurrences can be contained in one of its atoms. The lifted factors are atoms because splitting a lifted part would improve `z(B)`.

This is an actual reduction from **each** counterexample to a robust core, not just an assertion that some globally shortest counterexample exists. The process may change support values by addition, but cannot increase the subgroup they span.

## 4. Deleting a zero-sum block is also a contraction

Let `A|B` be a nonempty proper zero-sum divisor, and choose one occurrence `a` of `A`. Contract the bundle

\[
(B A^{-1})a
\]

to its sum, which is `a`. The resulting block is occurrence-isomorphic to `A`. Therefore **every proper nonempty zero-sum divisor of a contraction-minimal core has defect at most `M`**. The empty divisor has defect zero as well.

This observation imports the entire complement/insertion mechanism without assuming global cardinality minimality.

For example, take any occurrence-disjoint specified atoms `A_1,...,A_r` and put

\[
C=B/(A_1\cdots A_r),\qquad
E=\sum_i(|A_i|-n),\qquad
h=m-r-z(C)\ge0.
\]

Then

\[
\delta_n(C)=M+1-E+nh\le M,
\]

so the companion insertion law is

\[
\boxed{E\ge nh+1.}
\tag{5}

If the total specified atomic excess is at most `n`, all those particular atoms extend jointly to a maximum factorization. This is stronger than asserting that their product has some maximum atomization that extends.

Taking one atom of length at most `n` would give `E<=0`, contradicting (5). Thus every extracted core is `n`-short-zero-free. This conclusion is derived from the same operation, rather than added as a separate hypothesis.

## 5. Exact rank-three consequences

For `G=C_p^3`, `p>=5`, put

\[
M=\frac{5(p-1)}2.
\]

Together with the already proved lower line, the conjecture

\[
D_k(C_p^3)=kp+M\qquad(k\ge2)
\]

is equivalent to the splitting property (2). The classical first level has defect strictly below `M`; the two-factor splitting property follows from the verified exact `D_2` bound. It is the higher-factor boundary splitting property that remains open.

If the conjecture first fails at packing level `m`, start from any counterexample at that level and extract the core of Section 3. A bad contraction cannot have a smaller packing number, because that would be an earlier failing level. Therefore extraction preserves `m` and leaves a unit-excess counterexample of the exact length

\[
mp+M+1.
\]

Accordingly, all overshoots `q>1` can be removed from the **existential first-failure search**. This does not assert that every original bad block has unit overshoot, and it does not invalidate earlier overshoot-sensitive theorems about such blocks.

Combining with `GENERAL_FORM_CONSTANT_LEVEL_REDUCTION_V1.md`, it is enough to establish boundary splitting on the remaining finite level range from that note: universally through level `20229`, or through level `7` for sufficiently large underlying primes in its stated scope. No numerical prime threshold is supplied here, and `p=7` is not assigned to the asymptotic range.

At `p=7,m=3`, a putative 37-term packing-three obstruction would give a 36-term block `C` of defect 15 under **every** pair contraction, with the original split producing no new factor. Every prescribed collection of bundles of total cost at most 7 would still fit some three-atom optimum of the obstruction. All atoms of length at most 17 would be insertable by the companion insertion theorem. These conclusions apply before imposing a maximal atom, a support-four form, a corridor, or saturation.

## 6. What remains load-bearing

The one-term splitting criterion, local core extraction, and the two exact cost laws are proved. To obtain the proposed Davenport equality, one must still prove that the higher-factor critical blocks satisfy (2), or equivalently exclude the extracted robust cores. The quotient identity in `QUOTIENT_CARRY_DEFECT_VARIATIONAL_FORM_V1.md` gives a second exact formulation of the required packing gain, retaining the kernel costs that a fixed quotient partition can lose.

No classification of all critical boundary blocks is asserted. No local saturated donor theorem is promoted to such a classification. The first corridor and `D_3(C_7^3)` remain open.

Proof review: the coordinator checked (1) by both partition lifting and merging two optimum factors; checked the two directions of the splitting equivalence; checked closure of coarsenings under contraction; and checked the occurrence-level realization of zero-sum deletion, including the empty-complement convention in (5). The cost laws agree with the independently derived length-minimal laws in the two companion notes. No brute-force computation enters these proofs, and novelty/priority remain `CANNOT_CHECK`.
