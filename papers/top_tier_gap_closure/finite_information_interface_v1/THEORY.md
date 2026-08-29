# Finite-information interface theorem spine V1

**Applies as shared donor logic to:** ORION-02, ORION-08, ORION-09, ORION-10, ORION-13, ORION-19, ORION-22.  
**Novelty status:** not assessed here.  
**Paper-promotion authority:** none.

## 1. Finite decision interface

Let `X` be a finite nonempty state set, `A` a finite nonempty action set, `w_x>0` state weights, and `L(x,a)` a real loss. An information interface is a map

\[
h:X\to Z.
\]

Its nonempty fibres are `F_z={x:h(x)=z}`. A deterministic policy is `d:Z->A`. With unnormalised weights, its risk is

\[
R_h(d)=\sum_{x\in X}w_xL(x,d(h(x))).
\]

Normalising by `W=sum_x w_x` changes no minimiser or zero/nonzero conclusion.

For each state define

\[
m_x=\min_{a\in A}L(x,a),\qquad e_x(a)=L(x,a)-m_x\ge0.
\]

The full-information optimum is

\[
R_{\mathrm{full}}=\sum_xw_xm_x.
\]

## Theorem 1 — exact partition risk

\[
R^*(h):=\min_dR_h(d)
=\sum_{z:F_z\ne\varnothing}\min_{a\in A}\sum_{x\in F_z}w_xL(x,a).
\]

Therefore the information regret is

\[
\Delta(h)=R^*(h)-R_{\mathrm{full}}
=\sum_z\min_{a\in A}\sum_{x\in F_z}w_xe_x(a)\ge0.
\]

**Proof.** The action chosen on one fibre affects no other fibre. Minimising the finite sum is therefore equivalent to minimising independently on every fibre. Subtracting the statewise minima gives the second display. Every excess is nonnegative. `QED`

## Theorem 2 — common-optimum criterion

The following are equivalent:

1. `Delta(h)=0`;
2. for every nonempty fibre `F`, there exists one action optimal at every state in `F`;
3. for every nonempty fibre,

\[
\bigcap_{x\in F}\operatorname*{argmin}_{a\in A}L(x,a)\ne\varnothing.
\]

**Proof.** A fibre contribution is the minimum of a sum of nonnegative weighted excesses. Positive weights make that minimum zero exactly when one action has zero excess at every state in the fibre. Sum the fibrewise equivalences. `QED`

A mixed fibre is thus not merely a pair of different labels. It is a fibre whose statewise optimal-action sets have empty total intersection. Pairwise intersections alone need not suffice when there are more than two states.

## Theorem 3 — subset and pair lower bounds

For any nonempty subset `S` of one fibre, define

\[
b(S)=\min_{a\in A}\sum_{x\in S}w_xe_x(a).
\]

Then

\[
\Delta(h)\ge b(S).
\]

In particular, every same-fibre pair `{x,y}` yields an exact nonnegative lower bound

\[
\Delta(h)\ge\min_a\{w_xe_x(a)+w_ye_y(a)\}.
\]

**Proof.** For every action, the nonnegative excess sum over the full fibre is at least the sum over `S`; minimisation preserves the inequality. The full regret contains that fibre contribution plus other nonnegative contributions. `QED`

This theorem is useful for falsification: one incompatible same-observation pair certifies positive regret, but a zero pair bound does not prove that a larger fibre has a common optimum.

## Theorem 4 — information refinement monotonicity

Suppose `g:X->Y` refines `h`, meaning `h=phi o g` for some map `phi`. Then

\[
R^*(g)\le R^*(h),\qquad \Delta(g)\le\Delta(h).
\]

Equality holds exactly when every coarse-fibre optimal action can be reproduced, without lower loss, by independently optimising its refined subfibres.

**Proof.** Every `h`-policy induces a `g`-policy by composition with `phi`, so the feasible policy set under `g` contains all coarse policies. The full-information optimum is common to both interfaces. `QED`

A refinement achieves full-information risk exactly when every refined fibre has a common optimum. This separates three questions that papers must not conflate: whether a refinement is informative, whether it is sufficient, and whether its acquisition cost makes it worthwhile.

## Theorem 5 — randomisation cannot improve expected finite-fibre risk

Allow a policy to choose, for each observed fibre, a probability vector `q_z` on `A`, and score expected loss. Then

\[
\inf_{q_z}\sum_aq_z(a)\sum_{x\in F_z}w_xL(x,a)
=\min_a\sum_{x\in F_z}w_xL(x,a).
\]

Thus randomisation does not reduce expected risk below the best deterministic fibre action.

**Proof.** The randomized objective is a convex combination of finitely many deterministic fibre losses and is therefore at least their minimum; a point mass on a minimiser attains equality. `QED`

This statement concerns expected loss with no additional adversarial or fairness constraint. Such extra constraints change the feasible set and require a different theorem.

## Corollary 6 — weighted 0-1 classification

Let each state have a label `y_x` in a finite label set, actions be labels, and `L(x,a)=1[a != y_x]`. For a fibre `F`, write

\[
M_F(c)=\sum_{x\in F:y_x=c}w_x.
\]

Then the optimal fibre error mass is

\[
\sum_{x\in F}w_x-\max_cM_F(c),
\]

and global information regret is the sum of these weighted minority masses. Zero regret holds exactly when every fibre is label-pure, modulo zero-weight states, which are excluded here.

## Theorem 7 — scalar point radius and interval width

Let each state carry a scalar target `t_x in R`. If one point prediction `c` must serve a fibre and loss is worst-case absolute error, then

\[
\min_{c\in\mathbb R}\max_{x\in F}|t_x-c|
=\frac{\max_{x\in F}t_x-\min_{x\in F}t_x}{2}.
\]

The minimisers are the midpoints of the smallest covering interval, and the minimum interval width required to contain all fibre targets is

\[
\operatorname{diam}(F)=\max_Ft-\min_Ft.
\]

**Proof.** Any point is at distance at least half the distance between the minimum and maximum. Their midpoint attains that bound. Every covering interval must contain both extremes, and `[min_F t,max_F t]` attains the diameter. `QED`

Diameter therefore measures unresolved scalar information, while half-diameter is the minimax point-prediction radius. Average-error claims require a different loss-specific calculation.

## Theorem 8 — invariant orbits

Let a group or monoid act on `X`, and suppose `h` is invariant: `h(gx)=h(x)` whenever the action is defined. Every orbit is contained in one information fibre. Consequently every orbit subset and orbit pair supplies a Theorem-3 lower bound. If `h` is a maximal invariant, its fibres are exactly the orbits, so zero information regret is equivalent to a common optimal action on every orbit.

**Proof.** Invariance makes `h` constant along every action path and hence on each orbit. Apply the preceding theorems. `QED`

This is an information boundary, not automatically a novel invariant for a particular scientific domain. A paper-specific contribution must define the scientifically justified action, observation map, cost, and consequence.

## 2. Constructive paper obligations

The exact spine prevents recurring logical errors but does not by itself close any paper's top-tier gap. Each adopting paper must add at least one of the following, prospectively or by proof:

- a minimum-cost refinement that drives `Delta` below a target;
- a sharp impossibility result under its scientifically justified observation map;
- a new domain mechanism predicting which fibres split and which remain mixed;
- transfer to independent units under information-, terminal-, and budget-matched controls;
- a material consequence such as reduced unsafe error, certified compute saving, or a new phase boundary.

The same finite partition identity cannot be counted as independent novelty in seven manuscripts. Each paper must cite the shared donor theorem and isolate its own construction, mechanism, or evidence.