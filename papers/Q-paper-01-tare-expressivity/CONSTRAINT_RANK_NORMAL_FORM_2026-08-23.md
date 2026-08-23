# Constraint-rank normal form for parity-coupled scientific compilers

**Status:** analytic theorem derived on 2026-08-23. No new empirical outcome is
introduced. The linear-dependence lemma is standard; the scientific content is
the compiler normal form obtained by combining it with a local cost-dominance
condition. The existing R6M theorem is a sharp rank-two corollary.

## 1. Abstract deletion system

Fix one nonzero representation object `R` with finite active coordinate set
`A`. Each active coordinate `q` has a binary constraint signature

\[
v_q\in V,
\]

where `V` is a vector space over `F_2` of dimension `d`. Feasibility requires

\[
\sum_{q\in A}v_q=b,
\qquad b\ne0.
\]

The coordinates of `v_q` may encode any independent binary relations that must
survive deletion: frame anticommutation, one or more Tag syndromes, parity
labels, transport bits, or other linear feasibility checks. Dependent raw checks
do not increase `d`; `d` is the rank of the signature space actually seen by
the object.

A nonempty proper subset `Q subset A` is **null-deletable** when

\[
\sum_{q\in Q}v_q=0.
\]

Deleting `Q` then preserves every encoded binary constraint and leaves `R`
nonzero.

Assume the objective is deletion-dominated: for every null-deletable `Q`, the
loss in the coupled part of the objective is at most the direct support refund,
so

\[
C(R\setminus Q)-C(R)\le0.
\]

A sufficient local condition is coordinate separability together with

\[
\Delta L(Q)\le\sum_{q\in Q}\rho_q
\le\sum_{q\in Q}m_q
\]

for every null-deletable set `Q`, where `m_q` is the direct support multiplier
and `rho_q` bounds that coordinate's contribution to the increase of all coupled
local terms.

## 2. General theorem

### Theorem (constraint-rank support normal form)

Every feasible representation in a deletion-dominated binary system can be
transformed without increasing cost into a feasible representation of support
at most `d`. Consequently every optimum has an equally good representative of
support at most the rank of its preserved constraint signature.

### Proof

Suppose `|A|>d`. The multiset `{v_q:q in A}` contains more vectors than the
dimension of `V`, so it is linearly dependent. Over `F_2`, a nontrivial linear
dependence is exactly a nonempty subset `Q subset A` with

\[
\sum_{q\in Q}v_q=0.
\]

Because the full active set sums to `b != 0`, `Q` cannot equal `A`. Thus `Q` is
nonempty and proper. Deleting it preserves the complete signature sum, leaves
the representation nonzero, and does not increase cost by deletion dominance.
Support strictly decreases.

Repeat whenever support exceeds `d`. The nonnegative integer support decreases
at every step, so the process terminates with support at most `d`. Starting from
an optimum, no step can lower the cost below the optimum; every step therefore
preserves optimality. QED.

## 3. Tightness of the rank bound

The rank bound cannot be improved over this abstract class. For any `d`, take
`V=F_2^d` and exactly `d` available coordinate positions with signatures
`v_i=e_i`, the standard basis vectors. Require
`b=e_1+...+e_d`. A subset of positions is feasible only when its signature sum
is `b`, which forces all `d` positions active. No nonempty proper subset of the
basis sums to zero, and the minimum support is exactly `d`.

This is a general tightness construction for the theorem, not a claim that
every TARE grammar realizes every rank. The existing exact R6O counterexample
does realize tightness for the R6M rank-two case.

## 4. Shared-Tag corollary

For one TARE frame `R`, let one signature coordinate record its symplectic
contribution with its frame partner and let `s` independent coordinates record
its required syndromes against `s` shared Tag/label constraints. Then

\[
d\le s+1.
\]

If the local coupled-cost penalty of deleting a frame coordinate is no larger
than its frame-support refund, an optimum exists with

\[
\operatorname{supp}(R)\le s+1.
\]

Raw Tag count may overstate the bound when syndrome checks are linearly
dependent; the sharp parameter is constraint rank.

For frozen R6M, `s=1`. The two signature bits are

\[
v_q=(\langle R_q,R'_q\rangle,\langle S_q,R_q\rangle)\in F_2^2,
\]

their total has first coordinate one, the three-way Restore penalty is at most
two, and every direct frame refund is two or four. The theorem therefore yields
support at most two. The exact support-one counterexample proves that this
rank-two bound is sharp for R6M:

\[
\kappa_{R6M}=2.
\]

## 5. Objective phase boundary

The theorem isolates the objective dependence that the previous manuscript left
as a qualitative limitation. Let

\[
\lambda_q=\sup \Delta L_q
\]

be the worst coupled-cost increase when coordinate `q` participates in a
constraint-preserving deletion, and let `m_q` be the support refund. The
rank-normal-form proof applies throughout the region

\[
m_q\ge\lambda_q\quad\text{for every deletable coordinate.}
\]

Crossing `m_q=lambda_q` is therefore a theorem-level boundary of the exchange
argument. Beyond it, support greater than constraint rank is not proved
necessary, but it can no longer be removed by this dominance theorem. This
defines the correct next research target for hardware-aware objectives: derive
their local penalty functions, partition objective space by the inequalities
`m_q >= lambda_q`, and construct sharp counterexamples in regions where the
inequalities fail.

## 6. Claim boundary

Authorized analytic claims:

1. support at most binary constraint rank in deletion-dominated systems;
2. tightness over the abstract system class;
3. support at most `s+1` for a shared-Tag family satisfying the stated
   independence and local-cost hypotheses;
4. frozen R6M as the sharp `d=2` corollary.

Not authorized without new work:

- that every multi-Tag TARE grammar satisfies the deletion-dominance hypothesis;
- a sharp TARE lower bound of `s+1` for every `s`;
- support-rank normal forms for nonbinary constraints without replacing the
  linear-dependence argument;
- hardware-resource advantage;
- novelty of the underlying linear-algebra lemma.
