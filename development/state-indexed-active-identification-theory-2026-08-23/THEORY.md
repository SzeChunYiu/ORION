# State-indexed active identification under licensed ambiguity

## A finite controlled-laboratory extension of the risk-vector frontier

**Status.** Mathematical development packet, 2026-08-23. This packet repairs
A1 from the adversarial review of the stationary active-identification theory.
It is finite, bounded-horizon, and known-kernel. Its exact calculations are
local mathematical witnesses only. They are not empirical validation,
protected custody, external review, authorization to randomize a scientific
claim, or evidence that an operational acquisition kernel is correct.

**Novelty boundary.** The theorem is a controlled-state specialization of
finite-horizon POMDP policy-tree/alpha-vector theory combined with finite
Bayes/minimax decision theory. The state-indexed formulation is useful for
joining P3-style licensed ambiguity to P5-style destructive or no-repeat
method revision, but no historical novelty is claimed. The target is a correct
wider interface, not forced novelty.

## 1. Finite controlled laboratory

Let

- \(W\) be a finite nonempty set of latent worlds;
- \(Y\) be a finite target alphabet and \(g:W\to Y\) the authorized target;
- \(S\) be a finite nonempty set of **observable controlled laboratory
  states**, with declared initial state \(s_0\);
- \(D(s)\) be a finite nonempty set of legal terminal actions in state \(s\),
  possibly including a deferral action \(\bot\);
- \(L_s(d,g(w))\in[0,\infty)\) be terminal loss;
- \(E(s)\) be the finite, possibly empty, set of legal acquisitions in state
  \(s\);
- \(c(s,e)\ge 0\) be the acquisition cost; and
- \(Q_{s,e}(o,s'\mid w)\) be a probability mass function on a finite joint
  outcome--next-state alphabet \(B(s,e)\subseteq O(s,e)\times S\).

The joint kernel is deliberate. The next controlled state may itself be
stochastic and observed, so it can carry information about \(w\). Destructive
or no-repeat tests are represented by a transition to a state in which that
test is absent from \(E(s')\). Replenishment is a legal transition back to a
state where the test is available. Path-dependent resource levels, remaining
specimens, and registered test inventories can be included in \(s\), provided
the resulting state is finite and observable.

Conditional on \(w\), current state, and selected action, the next branch has
law \(Q_{s,e}\). The controlled-state Markov assumption is substantive: if the
recorded state omits a variable on which future kernels, costs, or legality
depend, the recurrence below is not licensed.

A deterministic legal policy tree with **at most \(n\) acquisitions** either
stops in state \(s\) with \(d\in D(s)\), or chooses \(e\in E(s)\) and assigns
a continuation tree of depth at most \(n-1\) to every branch \((o,s')\). A
complete observed history retains states, actions, outcomes, and stopping.
Randomized policies use a world-independent private random seed and perfect
recall. Equivalently in this finite perfect-recall problem, behavioral and
mixed policies induce the same distributions over complete histories.

The total loss is the sum of incurred \(c(s_t,e_t)\) plus terminal loss. A
zero-cost cycle is harmless for every fixed finite horizon; no unbounded or
infinite-horizon conclusion is inferred.

## 2. Licensed prior and posterior objects

Let \(\Pi\subseteq\Delta(W)\) be any nonempty fixed ex-ante credal set. It may
be nonconvex, nonclosed, and nonrectangular. Its active support is

\[
S(\Pi)=\{w:\exists p\in\Pi,\ p(w)>0\}.
\]

For a legal history \(h\), let \(\lambda_h(w)\) be its likelihood under world
\(w\), including every controlled-state transition. The target support
envelope and ordinary posterior credal family are

\[
\mathcal Y(h)=\{g(w):w\in S(\Pi),\ \lambda_h(w)>0\},
\]

\[
\Pi_h=\left\{
 \frac{(p(w)\lambda_h(w))_{w\in W}}
      {\sum_u p(u)\lambda_h(u)}:
 p\in\Pi,\ \sum_u p(u)\lambda_h(u)>0
\right\}.
\]

A history with zero probability under every \(p\in\Pi\) is an invalid
model/interface terminal. The state transition does not manufacture a
posterior when the denominator is zero.

The set \(\Pi\) licenses one prior chosen ex ante. It does not by itself
license nature to select unrelated elements of \(\Pi_h\) independently at
different histories. That stronger move is rectangular ambiguity and is
formalized in Section 7.

## 3. The state-indexed risk-vector recurrence

For \(d\in D(s)\), define

\[
\ell_{s,d}(w)=L_s(d,g(w)).
\]

For action \(e\in E(s)\) and one continuation vector
\(v_{o,s'}\in\mathbb R_+^W\) per branch, define

\[
\mathcal B_{s,e}((v_{o,s'})_{(o,s')\in B(s,e)})(w)
 =c(s,e)+\sum_{(o,s')\in B(s,e)}
 Q_{s,e}(o,s'\mid w)v_{o,s'}(w).
\]

The exact state-indexed frontiers are

\[
\Gamma_{0,s}=\{\ell_{s,d}:d\in D(s)\},
\]

\[
\Gamma_{n,s}=\Gamma_{0,s}\ \cup\!
\bigcup_{e\in E(s)}
\left\{
 \mathcal B_{s,e}((v_{o,s'})_{o,s'}):
 v_{o,s'}\in\Gamma_{n-1,s'}
 \text{ for every }(o,s')\in B(s,e)
\right\}.
\]

A branch impossible in all active worlds may be assigned any legal
continuation; it does not change the risk vector. The continuation still has
to be syntactically legal so that the object is a complete policy tree rather
than a partial informal plan.

### Theorem 1 (exact enumeration of legal controlled policy risks)

For every \(n\ge 0\) and state \(s\), \(\Gamma_{n,s}\) is exactly the set of
world-conditional total-risk vectors of deterministic legal policy trees
starting at \(s\) and using at most \(n\) acquisitions.

**Proof.** At horizon zero, every legal policy stops, giving exactly
\(\Gamma_{0,s}\). Assume the statement for \(n-1\). A depth-\(n\) legal tree
either stops, producing \(\ell_{s,d}\), or selects a legal root action
\(e\in E(s)\). On branch \((o,s')\), its continuation has a vector in
\(\Gamma_{n-1,s'}\) by induction. Conditional expectation in world \(w\)
gives exactly \(\mathcal B_{s,e}\). Conversely, every action and family of
continuation vectors appearing in the recurrence has, by induction, legal
continuation trees; attaching them to the legal root action constructs the
required tree. \(\square\)

This theorem repairs the stationary extension failure. Merely writing a state
label beside the old \(\Gamma_n\) is not enough: legality, kernel, cost, and
next-state continuation are all indexed by the current controlled state.

## 4. Randomization, robust value, and attainment

For a risk vector \(v\), define the ex-ante credal support function

\[
h_\Pi(v)=\sup_{p\in\Pi}p\cdot v.
\]

### Theorem 2 (deterministic and randomized ex-ante robust values)

For a fixed horizon and initial state:

1. the deterministic robust value is
   \[
   V^{\mathrm{det}}_{n,s}=\min_{v\in\Gamma_{n,s}}h_\Pi(v);
   \]
2. the risk vectors of world-independent randomized perfect-recall policies
   are exactly \(\operatorname{conv}(\Gamma_{n,s})\); and
3. the randomized robust value is
   \[
   V^{\mathrm{rand}}_{n,s}
   =\min_{v\in\operatorname{conv}(\Gamma_{n,s})}h_\Pi(v).
   \]

Both policy minima are attained. A prior attaining the inner supremum need not
exist.

**Proof.** Theorem 1 gives finitely many deterministic risk vectors. A finite
behavioral policy can sample all its world-independent local random choices in
advance, producing a mixture over deterministic perfect-recall plans. Conversely
a root mixture over deterministic legal trees is an admissible randomized
perfect-recall policy. Conditional risk is linear in the mixture, so the
randomized risk set is the convex hull. The deterministic set is finite and
the randomized set is compact. For any nonempty \(\Pi\subseteq\Delta(W)\),

\[
|h_\Pi(v)-h_\Pi(u)|\le \lVert v-u\rVert_\infty,
\]

so the policy minima are attained. This continuity does not close \(\Pi\) or
produce a licensed maximizing prior. \(\square\)

### Corollary 1 (what closing the credal set does and does not change)

For every risk vector,

\[
h_\Pi(v)=h_{\overline{\operatorname{conv}}(\Pi)}(v).
\]

Thus closure and convexification do not change any ex-ante robust policy
value. They can change provenance: a maximizer in the closed convex hull may
be a limit or mixture not present in the licensed registry. A least-favourable
**licensed** prior is guaranteed when \(\Pi\) is compact, but not for arbitrary
nonclosed \(\Pi\).

## 5. Singleton-prior controlled Bellman equation

For a prior \(p\), set

\[
r(p,s)=\min_{d\in D(s)}\sum_w p(w)L_s(d,g(w)).
\]

For a legal branch, define

\[
q_{s,e}(o,s'\mid p)=\sum_w p(w)Q_{s,e}(o,s'\mid w)
\]

and, when this is positive,

\[
p_{s,e,o,s'}(w)=
\frac{p(w)Q_{s,e}(o,s'\mid w)}{q_{s,e}(o,s'\mid p)}.
\]

### Theorem 3 (controlled-state Bayes Bellman theorem)

The minimum expected total loss under one prior and at most \(n\) acquisitions
is

\[
V_0(p,s)=r(p,s),
\]

\[
V_n(p,s)=\min\left\{
 r(p,s),
 \min_{e\in E(s)}\left[
 c(s,e)+\sum_{(o,s')\in B(s,e)}
 q_{s,e}(o,s'\mid p)V_{n-1}(p_{s,e,o,s'},s')
 \right]
\right\}.
\]

If \(E(s)=\varnothing\), the inner acquisition minimum is \(+\infty\). A
zero-probability branch posterior may be assigned arbitrarily because its term
has weight zero. A deterministic policy attains the value.

**Proof.** This is backward induction on legal controlled-state policy trees.
At a test node, condition on the joint observed branch \((o,s')\). Finiteness
gives attainment, and root randomization cannot improve a linear Bayes
expectation. Equivalently, scalarizing Theorem 1 by \(p\) yields the same
recursion. \(\square\)

A stochastic next state must appear in the conditioning event. Treating it as
an unobserved nuisance when the laboratory records it can discard decision
information and change the Bellman value.

## 6. Exact target identification with controlled state

Fix a legal finite-horizon acquisition policy and let \(P_w^\pi\) be the law
of its complete state--action--outcome transcript before the terminal action.
Exactly as in the stationary finite model, a target decoder is correct almost
surely in every active world if and only if every transcript with positive
probability in two active worlds has the same \(g\)-value in both. Equivalently,
the positive mixtures of transcript laws within different target classes are
mutually singular.

The controlled state can create separation: an observed next state is part of
the transcript. It cannot create legal authority for an unavailable action.
Full-support joint kernels for a cross-target pair still block finite exact
identification, even if their KL divergence is positive.

## 7. Fixed-prior ambiguity versus rectangular ambiguity

The distinction is about which **path laws** nature may generate, not about a
notational choice in the Bellman equation.

Fix a legal policy \(\pi\) and pad stopping with an absorbing symbol so its
complete path space \(\Omega_\pi\) is finite. Include \(W\) in the probability
space even though the policy does not observe it. Each \(p\in\Pi\) induces a
path law \(P_{p}^{\pi}\). Let

\[
\mathcal M_\pi=\{P_p^\pi:p\in\Pi\},\qquad
\mathcal C_\pi=\overline{\operatorname{conv}}(\mathcal M_\pi).
\]

A set of path laws is **rectangular** for the observed-history filtration if it
is stable under historywise pasting: one may retain a licensed marginal up to
a history and, independently on each positive-probability history atom, attach
a licensed conditional continuation law. Let
\(\operatorname{Rect}(\mathcal C_\pi)\) be the smallest closed convex set
containing \(\mathcal C_\pi\) and stable under all such finite-history pastings.
Only positive-probability conditionals may be pasted.

For the realized total loss \(R_\pi\), define

\[
J_{\rm fix}(\pi)=\sup_{P\in\mathcal M_\pi}\mathbb E_P R_\pi,
\qquad
J_{\rm rect}(\pi)=
\max_{P\in\operatorname{Rect}(\mathcal C_\pi)}\mathbb E_P R_\pi.
\]

### Theorem 4 (exact rectangularization boundary)

For every fixed legal policy:

1. \(J_{\rm fix}(\pi)\le J_{\rm rect}(\pi)\).
2. The two robust expectations agree for **every bounded path loss** if and
   only if
   \[
   \mathcal C_\pi=\operatorname{Rect}(\mathcal C_\pi).
   \]
3. For a particular loss, they differ exactly when its support functional is
   strictly increased by rectangular closure:
   \[
   \sup_{P\in\mathcal C_\pi}\mathbb E_P R
   <
   \max_{P\in\operatorname{Rect}(\mathcal C_\pi)}\mathbb E_P R.
   \]

For any declared policy class \(\mathcal A\) on which both minima are
attained (in particular, a finite deterministic class; also a finite
extensive rectangular game with compact behavioral-strategy sets), let
\(V_{\rm fix}=\min_{\pi\in\mathcal A}J_{\rm fix}(\pi)\) and similarly for
\(V_{\rm rect}\). Then \(V_{\rm fix}\le V_{\rm rect}\), with equality if and
only if some fixed-optimal policy \(\pi^*\) also satisfies
\(J_{\rm rect}(\pi^*)=V_{\rm fix}\). Consequently the control values differ
exactly when rectangularization raises the robust risk of every fixed-optimal
policy.

**Proof.** Set inclusion gives item 1. On a finite path space, bounded losses
are linear functionals of path laws. Two compact convex sets have identical
support functions for all such functionals if and only if the sets are equal,
giving items 2 and 3. For the final claim, if a fixed-optimal \(\pi^*\) retains
value, then \(V_{\rm rect}\le J_{\rm rect}(\pi^*)=V_{\rm fix}\), while item 1
gives the reverse inequality. Conversely, equality and a rectangular-optimal
policy imply that policy is fixed-optimal and retains the common value. \(\square\)

A posterior-local minimax Bellman recursion is valid when the protocol declares
a rectangular family of conditional nature moves. It solves the rectangular
problem above. It does **not** compute the fixed ex-ante \(\Pi\) problem unless
the pasting criterion or the specified-loss equality holds. The risk-vector
frontier in Theorem 2 is the fail-closed computation for arbitrary fixed
ex-ante \(\Pi\).

The receipt's two-prior witness has fixed value \(1/10\) and rectangular value
\(1/2\). It preserves the prior coupling rather than relabelling the larger
adversary as a correction.

## 8. Zero-cost reachability

Let \(\Gamma^{0}_{n,s}\) be the same recurrence as \(\Gamma_{n,s}\), but with
acquisition choices restricted to actions satisfying \(c(s,e)=0\). This is the
exact **zero-cost reachability frontier** within horizon \(n\).

### Proposition 1 (free preprocessing boundary)

If \(\Gamma^{0}_{n,s}\) contains a vector achieving a declared target error
with zero acquisition cost, no strictly positive lower bound on acquisition
cost can hold for that target and horizon. Any information-per-cost theorem
must either assume a strictly positive resource charge for every informative
legal action, or first condition the downstream problem on the full observed
history reached through the zero-cost frontier.

The four-world parity witness has Bayes error \(1/2\) at horizons zero and one,
but zero error after two complementary zero-cost acquisitions. Collapsing the
free path without retaining its outcomes would lose information; treating it
as positively charged would fabricate cost.

This proposition is finite-horizon only. The union
\(\bigcup_n\Gamma^0_{n,s}\) can exhibit nonattainment or improper cycling in an
infinite-horizon model.

## 9. Exhaustive finite witnesses

`finite_controlled_state_harness.py` enumerates every deterministic legal
policy-tree risk vector for seven exact rational witnesses:

1. an initially unavailable perfect test remains unavailable and the value is
   \(1/2\), while the same test in an open state has value 0;
2. a destructive test moves from `fresh` to `spent`, so a second horizon does
   not improve \(1/4\); illegally making it repeatable yields \(7/40\);
3. an observed stochastic next state plus cost \(1/20\) yields risk vector
   \((3/10,3/10)\);
4. two point-mass priors give deterministic minimax risk 1 and fair-randomized
   risk \(1/2\);
5. an open credal set has support supremum 1 with no attaining licensed prior;
6. two complementary zero-cost tests reduce parity error from \(1/2\) to 0;
   and
7. fixed versus rectangular ambiguity yields \(1/10\) versus \(1/2\).

These witnesses test the recurrence and boundaries; they are not a proof of
historical novelty or of any empirical kernel.

## 10. Donor theory and novelty subtraction

The closest inherited structures include:

- Smallwood and Sondik (1973), *The Optimal Control of Partially Observable
  Markov Processes over a Finite Horizon*, DOI `10.1287/opre.21.5.1071`:
  finite policy trees and state-indexed alpha/risk vectors;
- Kuhn (1953), *Extensive Games and the Problem of Information*: mixed versus
  behavioral strategies under perfect recall;
- Epstein and Schneider (2003), *Recursive multiple-priors*, DOI
  `10.1016/S0022-0531(03)00097-8`: rectangularity and dynamic consistency;
- Iyengar (2005), *Robust Dynamic Programming*, DOI
  `10.1287/moor.1040.0129`;
- Nilim and El Ghaoui (2005), *Robust Control of Markov Decision Processes
  with Uncertain Transition Matrices*, DOI `10.1287/opre.1050.0216`;
- Wiesemann, Kuhn and Rustem (2013), *Robust Markov Decision Processes*, DOI
  `10.1287/moor.1120.0566`;
- Nakao, Jiang and Shen (2021), *Distributionally Robust Partially Observable
  Markov Decision Process with Moment-Based Ambiguity*, DOI
  `10.1137/19M1268410`; and
- Chernoff/controlled-sensing/active-hypothesis-testing theory for adaptive
  experiment allocation and KL lower bounds.

Accordingly, generic controlled-state Bellman recursion, policy-vector
enumeration, robust randomization, and rectangularity are donor-owned. The
programme value is the explicit scientific contract: controlled legality and
state transitions remain inside the policy frontier; support, weights, and
dynamic ambiguity provenance remain distinct; and zero-cost or impossible
histories cannot silently authorize a claim.

A future novelty claim requires a systematic full-text audit and a theorem not
obtainable by combining these donors. Candidate residuals include a sharp
state-dependent nonrectangular consistency characterization for target classes,
credal-specific exact pruning complexity, composite-target cost exponents with
matching achievability, or finite-sample joint world/kernel ambiguity.

## 11. Unresolved boundaries

1. **Measurability.** Standard-Borel states/outcomes require regular conditional
   kernels and measurable policy/decoder selection.
2. **Infinite horizon.** Zero-cost cycles, improper policies, nonattainment,
   and undiscounted costs require separate conditions.
3. **Hidden laboratory state.** If \(s\) is not fully observed, the model is a
   larger POMDP over \((w,s)\), not the recurrence stated here.
4. **Kernel uncertainty.** The theory assumes the joint kernels are licensed.
   Estimated kernels require coverage and adaptive-selection correction.
5. **State sufficiency.** An omitted resource, degradation, or carry-over
   variable invalidates the controlled Markov recurrence.
6. **Rectangular protocol.** The nature move must be frozen. Fixed prior,
   posterior pasting, adversarial kernels, and distributionally robust kernels
   are different models.
7. **Authority.** An internally observed state or outcome cannot substitute
   for external authorization or protected custody when the target contains
   such a fact.
