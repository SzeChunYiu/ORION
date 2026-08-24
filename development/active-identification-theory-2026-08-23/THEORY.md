# Active identification under licensed ambiguity

## A finite decision theory joining epistemic portrait envelopes to adaptive method revision

**Status.** Mathematical development packet, 2026-08-23. All results in this
packet are finite and set-theoretic/probabilistic unless a statement explicitly
says otherwise. The exact witness calculations are local mathematical checks,
not empirical evidence, protected evaluation, external review, or authority for
deployment. The packet does not claim that a negative result became positive.

## 1. Why this is a wider object

Partial identification and adaptive diagnosis are usually presented as
different problems. They are two stages of the same decision problem:

1. a current interface leaves a **decision-relative envelope** of latent worlds;
2. a licensed credal set supplies zero, one, or several probability laws over
   that envelope;
3. an acquisition policy chooses stochastic tests in response to their earlier
   outcomes;
4. the policy stops with a decision or a declared deferral;
5. the scientific objective charges both terminal loss and acquisition cost.

The target need not be the latent world. It can be a mapping decision, a global
portrait query, or a minimal authorized revision front. This distinction is
essential: exact decision identification may be possible without identifying
the world, and a test that distinguishes worlds inside one decision class has
no direct decision value.

The main result is an exact finite **risk-vector Bellman recursion**. It retains
the risk in every active world before applying a licensed prior or credal set.
For a single prior it reduces to the familiar posterior-belief Bellman
recursion. For an arbitrary, possibly nonrectangular credal set, the vector
frontier remains valid while a naive posterior-by-posterior scalar minimax
recursion can fail. This gives a common mathematical interface for P3-style
envelopes and P5-style adaptive discriminators.

## 2. Finite model and conventions

Let

- \(W\) be a finite nonempty set of latent worlds;
- \(Y\) be a finite nonempty target alphabet and \(g:W\to Y\) the
  decision-relevant query;
- \(D\) be a finite nonempty set of terminal actions, possibly containing a
  deferral action \(\bot\);
- \(L:D\times Y\to[0,\infty)\) be a finite terminal loss;
- \(E\) be a finite nonempty set of acquisition actions or tests;
- \(O_e\) be a finite nonempty outcome alphabet for test \(e\);
- \(K_e(o\mid w)\) be the stochastic outcome kernel; and
- \(c_e\ge 0\) be the known acquisition cost.

Conditional on the world and selected test, the next outcome has law \(K_e\).
Thus repeated outcomes are conditionally independent given the world and the
selected action sequence. The displayed recursions assume that every
\(e\in E\) is legally available at every history and that its kernel and cost
are stationary. Merely attaching a policy-state label does not enforce
history-dependent availability. Destructive, replenishing or no-repeat tests
require state-indexed legal sets \(E(s)\), costs, kernels, transitions and
frontiers \(\Gamma_{n,s}\); that extension is retained as a separate successor
problem.

A deterministic policy tree with horizon \(n\) either stops at a node with
some \(d\in D\), or selects \(e\in E\) and assigns a continuation tree of
horizon \(n-1\) to every \(o\in O_e\). A randomized behavioral policy may
randomize at each history using world-independent private randomness and
perfect recall of its complete action--outcome history. Total loss is the sum
of acquisition costs plus terminal loss. Tests may be repeated. A no-repeat
restriction is outside the displayed stationary recursion unless the legal
test set and state transition are made explicit.

The **licensed credal set** \(\Pi\) is any nonempty subset of the probability
simplex \(\Delta(W)\). It need not be convex or closed. Its active support is

\[
 S(\Pi)=\{w\in W:\text{there is a }p\in\Pi\text{ with }p(w)>0\}.
\]

For an observed history \(h\), let \(\lambda_h(w)\) be its likelihood under
world \(w\). The support envelope and the ordinary conditioned credal set are

\[
 \mathcal Y(h)=\{g(w):w\in S(\Pi),\ \lambda_h(w)>0\},
\]

\[
 \Pi_h=
 \left\{
   \left(\frac{p(w)\lambda_h(w)}{\sum_u p(u)\lambda_h(u)}\right)_{w\in W}:
   p\in\Pi,\ \sum_u p(u)\lambda_h(u)>0
 \right\}.
\]

The first object is a P3-style identified set. The second retains licensed
weights needed for Bayes or minimax risk. Equal support envelopes do **not**
in general imply equal risks. These objects are used only for histories with
positive probability under at least one licensed prior. Every other history is
an invalid model/interface terminal; it is not assigned a scientific envelope
by conditioning on a zero denominator.

Throughout, total variation uses
\(\operatorname{TV}(P,Q)=\sup_A|P(A)-Q(A)|=\tfrac12\lVert P-Q\rVert_1\).
Kullback--Leibler divergence uses natural logarithms and may be infinite.
"Exact" means pointwise or almost-sure correctness in every active world;
"Bayes" means expectation under one declared prior; and "robust" means a
supremum over the declared credal set. These are not interchangeable.

## 3. Exact target identification

### Theorem 1 (adaptive transcript-purity criterion)

Fix an acquisition policy \(\pi\) of finite horizon and let \(P_w^\pi\) be the
law of its complete action--outcome transcript \(T\) in world \(w\). The
following are equivalent on \(S(\Pi)\):

1. there is a terminal decoder \(\delta(T)\) with
   \(P_w^\pi\{\delta(T)=g(w)\}=1\) for every active \(w\);
2. every transcript having positive probability in two active worlds has the
   same target in both worlds;
3. for each \(y\in g(S(\Pi))\), the uniform mixture of the finitely many
   \(P_w^\pi\) with \(g(w)=y\) is mutually singular to every other target-class
   mixture.

For deterministic kernels, condition 2 says exactly that every reachable
terminal leaf is target-pure.

**Proof.** A decoder's inverse images form disjoint target regions of transcript
space. Exactness says that the transcript law of each world is concentrated on
its target region, which gives 1 \(\Rightarrow\) 2. Under finite horizon the
transcript space is finite. If 2 holds, label each positive-probability
transcript by its unique target, giving 2 \(\Rightarrow\) 1. A finite positive
mixture has support equal to the union of its component supports, so disjoint
target supports are equivalent to pairwise mutual singularity of the class
mixtures. \(\square\)

### Corollary 1 (full-support noise blocks finite exactness)

Suppose active worlds \(w,w'\) have \(g(w)\ne g(w')\) and, for every available
test, \(K_e(o\mid w)>0\) if and only if \(K_e(o\mid w')>0\). No finite-horizon
policy exactly identifies the target in both worlds. In particular, strictly
positive kernels have this property.

**Proof.** At every common history the policy selects the same distribution
over tests. Inductively, every transcript possible under one world remains
possible under the other. Theorem 1 then rules out a target-pure decoder.
\(\square\)

This is a support statement, not a claim that approximate learning is
impossible. Distinct full-support kernels can have positive KL divergence and
permit error converging to zero as samples grow, while still forbidding exact
identification at every finite horizon.

## 4. Bayes risk and the ordinary Bellman recursion

For a prior \(p\in\Delta(W)\), define the terminal Bayes risk

\[
 r(p)=\min_{d\in D}\sum_w p(w)L(d,g(w)).
\]

For test \(e\), let

\[
 q_e(o\mid p)=\sum_w p(w)K_e(o\mid w),\qquad
 p_{e,o}(w)=\frac{p(w)K_e(o\mid w)}{q_e(o\mid p)}
\]

when \(q_e(o\mid p)>0\); a zero-probability posterior can be assigned
arbitrarily because its Bellman term is multiplied by zero.

### Theorem 2 (finite-horizon Bayes Bellman theorem)

The minimum expected total loss among policies using at most \(n\) tests is

\[
 V_0(p)=r(p),
\]

\[
 V_n(p)=\min\left\{
   r(p),
   \min_{e\in E}\left[c_e+\sum_{o\in O_e}q_e(o\mid p)
                              V_{n-1}(p_{e,o})\right]
 \right\}.
\]

A deterministic policy attains the minimum. Some optimal policy acquires precisely
when at least one acquisition term is no larger than the stopping term;
stopping is strictly optimal when \(r(p)\) is strictly smaller than every
acquisition term. Conditional on stopping, deferral \(\bot\) is optimal exactly
when

\[
 \sum_w p(w)L(\bot,g(w))
 \le \sum_w p(w)L(d,g(w))\quad\text{for every }d\in D.
\]

**Proof.** At a root node, a policy either terminates or selects one test.
Conditioning on that test's outcome produces the displayed posterior and a
subproblem with horizon \(n-1\). Backward induction proves both the recursion
and attainment. Randomizing the root choice only forms a convex combination of
available expected losses and cannot beat their minimum. \(\square\)

For zero--one terminal loss with \(D=Y\),
\(r(p)=1-\max_y\sum_{w:g(w)=y}p(w)\). The result therefore joins the mixed-fibre
Bayes error formula to a costed adaptive acquisition programme rather than
treating current fibre impurity as final.

## 5. The credal result: vector frontiers before scalar minimax

For terminal action \(d\), define its world-risk vector
\(\ell_d\in\mathbb R_+^W\) by \(\ell_d(w)=L(d,g(w))\). For a test and a family
of continuation vectors \((v_o)_{o\in O_e}\), write

\[
 \mathcal B_e((v_o)_o)(w)
 =c_e+\sum_{o\in O_e}K_e(o\mid w)v_o(w).
\]

Define finite sets recursively:

\[
 \Gamma_0=\{\ell_d:d\in D\},
\]

\[
 \Gamma_n=\Gamma_0\ \cup\!
 \bigcup_{e\in E}
 \left\{\mathcal B_e((v_o)_o):v_o\in\Gamma_{n-1}
                              \text{ for every }o\in O_e\right\}.
\]

For any risk vector \(v\), let the credal support function be
\(h_\Pi(v)=\sup_{p\in\Pi}p\cdot v\).

### Theorem 3 (exact risk-vector Bellman frontier)

1. \(\Gamma_n\) is exactly the set of conditional risk vectors of all
   deterministic policy trees with at most \(n\) tests.
2. The deterministic robust value is
   \[
     \min_{v\in\Gamma_n}h_\Pi(v).
   \]
3. Under the declared world-independent private-randomness and perfect-recall
   convention, the risk vectors of all randomized behavioral policies form
   \(\operatorname{conv}(\Gamma_n)\). Hence their robust value is
   \[
     \min_{v\in\operatorname{conv}(\Gamma_n)}h_\Pi(v),
   \]
   and the minimum is attained.
4. For a singleton credal set \(\Pi=\{p\}\), randomization cannot improve the
   value and scalarization of the vector recursion gives Theorem 2.

**Proof.** For item 1, induction on the tree depth is exact: terminal nodes
give \(\Gamma_0\); a test node incurs \(c_e\) and, in world \(w\), averages
the chosen continuation vector against \(K_e(\cdot\mid w)\). Conversely every
choice in the recursion defines such a tree. A finite behavioral strategy can
be implemented by sampling in advance its action at every possible history,
so it is a mixture over finitely many deterministic trees. Conversely, perfect
recall gives realization equivalence between a world-independent root mixture
over trees and a behavioral strategy. Conditional risk is linear in that
mixture, proving item 3. The convex hull is compact and \(h_\Pi\) is
finite and Lipschitz on finite-dimensional risk space, so the minimum is
attained. For a singleton prior, the objective is linear and has a minimizer at
an extreme point of the policy polytope, giving item 4. \(\square\)

### Consequences

- **Arbitrary licensed ambiguity is allowed.** Convexity, closedness, and
  rectangularity of \(\Pi\) are not needed for the ex-ante finite-horizon
  result.
- **Policy attainment is not prior attainment.** The finite or compact policy
  frontier attains its minimum. If \(\Pi\) is not closed, the displayed
  supremum need not be achieved by any licensed prior; only approximating
  worst priors may exist unless compactness is separately established.
- **Randomization can matter.** With no information, two opposite target
  worlds, zero--one loss, and a credal set containing both point masses, every
  deterministic decision has robust error one while a fair randomization has
  robust error one half.
- **A scalar local robust Bellman rule is unsafe without extra structure.**
  Conditioning each prior and then allowing the worst posterior to be selected
  independently at every later history rectangularizes the ambiguity set. It
  can produce a different, more pessimistic problem. The vector frontier keeps
  the coupling induced by the one ex-ante licensed prior.
- **Safe stopping under ambiguity is a frontier comparison.** A deterministic
  immediate stop is robust-optimal among deterministic policies exactly when
  \[
    \min_{v\in\Gamma_0}h_\Pi(v)
    \le
    \min_{v\in\Gamma_n\setminus\Gamma_0}h_\Pi(v),
  \]
  with the right side interpreted as \(+\infty\) if no acquisition policy is
  available. When randomization is allowed, mixtures of a stopping tree and an
  acquisition tree can strictly improve on each component. Consequently a
  purely terminal randomized policy is robust-optimal exactly when
  \[
    \min_{v\in\operatorname{conv}(\Gamma_0)}h_\Pi(v)
    =
    \min_{v\in\operatorname{conv}(\Gamma_n)}h_\Pi(v),
  \]
  not merely when it beats every acquisition vector separately. A
  posterior-local stopping inequality is equivalent only after a declared
  dynamic ambiguity model, such as rectangular historywise ambiguity, has
  replaced the fixed-prior model.

## 6. Exact risk, total variation, and cost lower bounds

For a fixed policy \(\pi\) and two worlds \(w,w'\) with different targets,
give them equal prior probability and use zero--one target loss. The smallest
binary target-decoding error from the complete transcript is

\[
 R_{w,w'}^\pi=\frac{1-\operatorname{TV}(P_w^\pi,P_{w'}^\pi)}{2}.
\]

This is the exact two-point Bayes risk. It lower-bounds any larger problem
that must also be correct on this pair.

Assume now that every \(c_e>0\), and define

\[
 I_{w,w'}(e)=D_{\mathrm{KL}}(K_e(\cdot\mid w)\Vert
                              K_e(\cdot\mid w')),
 \qquad
 \rho_{w,w'}=\max_e\frac{I_{w,w'}(e)}{c_e}.
\]

### Theorem 4 (adaptive pairwise information-cost lower bound)

Let a bounded-horizon adaptive policy and decoder have error at most
\(\delta<1/2\) in every active world. For every active cross-target pair
\(w,w'\),

\[
 \mathbb E_w[C_\pi]
 \ge
 \frac{\operatorname{kl}(1-\delta\,\Vert\,\delta)}{\rho_{w,w'}},
\]

where \(C_\pi\) is total acquisition cost and

\[
 \operatorname{kl}(1-\delta\,\Vert\,\delta)
 =(1-2\delta)\log\frac{1-\delta}{\delta}.
\]

The quotient is interpreted in the usual extended-real sense. With unit test
costs, it is a sample lower bound. A symmetric result is obtained by reversing
\(w,w'\), and the larger of the two oriented bounds may be used. For this
\(\delta\)-correctness statement, deferral and every non-target terminal output
count as error.

**Proof.** Let \(A\) be the event that the decoder emits \(g(w)\). Uniform
\(\delta\)-correctness gives \(P_w^\pi(A)\ge1-\delta\) and
\(P_{w'}^\pi(A)\le\delta\). Data processing for KL gives

\[
 D_{\mathrm{KL}}(P_w^\pi\Vert P_{w'}^\pi)
 \ge \operatorname{kl}(1-\delta\Vert\delta).
\]

The likelihood-ratio chain rule for an adaptive experiment gives

\[
 D_{\mathrm{KL}}(P_w^\pi\Vert P_{w'}^\pi)
 =\mathbb E_w\sum_t I_{w,w'}(E_t)
 \le \rho_{w,w'}\mathbb E_w\sum_t c_{E_t}.
\]

Actions themselves add no likelihood term because the same policy kernel is
used under both worlds conditional on the common history. Combining the two
inequalities proves the result. \(\square\)

The lower bound is target-relative: it ranges only over pairs with different
\(g\)-values. It also exposes the exact/approximate divide. Positive finite KL
can support decreasing error, not finite exact separation; exact separation is a
mutual-singularity question from Theorem 1.
Strictly positive charged costs are essential: a zero-cost perfect test can
achieve exact error at total cost zero. A resource claim with free tests must
first quotient the zero-cost reachability closure or use a separate strictly
positive resource gauge.

## 7. When greedy information gain is and is not justified

### Proposition 1 (the exact one-step log-loss case)

For this proposition only, relax the finite terminal-action assumption and let
the terminal action range over the probability simplex on finite \(Y\), scored
by extended-valued logarithmic loss. Suppose one test must be selected and then
the policy must stop. For current prior \(p\), the Bayes terminal risk before
testing is \(H_p(Y)\), and the expected risk after test \(e\) is

\[
 H_p(Y\mid O_e)=H_p(Y)-I_p(Y;O_e).
\]

Therefore, with equal test costs, maximizing target mutual information is
exactly Bayes-optimal. With additive costs, the exact rule maximizes
\(I_p(Y;O_e)-c_e\), not information divided by cost.

This proposition is intentionally narrow. It does not extend automatically to
zero--one loss, more than one remaining acquisition, hard knapsack budgets,
credal minimax risk, or information about \(W\) that is irrelevant to \(g(W)\).

### Proposition 2 (an assumption-based approximation regime)

Let the declared acquisition utility \(F\) on partial realizations be
normalized, adaptive monotone and adaptive submodular, and suppose all tests
have equal cost and the objective is to maximize expected \(F\) subject to a
cardinality budget \(k\).
Then the adaptive greedy policy has the standard \(1-1/e\) approximation to
the best adaptive policy. This is an inherited adaptive-submodularity theorem,
not a consequence of the present model alone. Entropy reduction, Bayes
classification risk, and credal worst-case risk must each be proved to satisfy
the required properties before the guarantee is invoked.

## 8. What is new as a programme claim, and what is inherited

The components have strong neighbouring literatures: comparison of
experiments and Bayes decision theory; partial identification and imprecise
probability; sequential design and active hypothesis testing; finite-horizon
POMDP policy trees; robust dynamic programming and rectangular ambiguity;
Le Cam two-point bounds and adaptive KL lower bounds; and adaptive
submodularity. No component theorem is advertised as historically novel
without a dedicated literature audit.

The integration candidate is narrower and defensible:

> A decision-relative epistemic envelope, a licensed credal set, and an
> adaptive discriminator programme can be represented by one finite
> acquisition theory. Exactness is governed by target-class transcript
> singularity; Bayes stopping by a posterior Bellman equation; arbitrary
> ex-ante credal minimax by a risk-vector policy frontier; and approximate
> success by target-pair information-cost lower bounds.

The risk-vector representation is a donor-derived common representation and
an audit object, not a claimed new alpha-vector theorem. It prevents three
silent promotions: support compatibility into calibrated probability,
posterior-by-posterior ambiguity into one fixed licensed prior, and positive
information into finite exact authority.

## 9. Boundaries and unresolved extensions

1. **General measurable spaces.** A standard-Borel extension requires regular
   conditional kernels, measurable policies/decoders, and measurable selection.
   Infinite horizons additionally require compactness, lower semicontinuity or
   contraction/proper-policy conditions. None is inferred from the finite
   proof.
2. **History-dependent scientific interventions.** The stationary recurrence
   does not enforce them. A correct extension needs \(\Gamma_{n,s}\), legal
   action sets \(E(s)\), state-dependent costs and kernels, and an explicit
   next-state transition. A clean minimal sufficient controlled state and a
   verified state-indexed theorem remain open.
3. **Ambiguity semantics.** Fixed-prior, rectangular multiple-prior, adversarial
   kernel, and distributionally robust models answer different questions. A
   protocol must declare which nature move is licensed.
4. **Computational frontier size.** \(\Gamma_n\) grows doubly exponentially in
   the worst case. Dominance pruning is valid when a risk vector is componentwise
   no smaller than another, but stronger credal-set-specific pruning and exact
   complexity bounds remain to be developed.
5. **Asymptotic exactness.** Positive pairwise distinguishability can yield
   consistent decisions, but optimal error exponents and cost allocations need
   Chernoff-style analysis over target classes, not just worlds.
6. **Learning kernels.** The theory assumes licensed kernels. Estimating them
   from the same development traces used for policy choice creates a second
   uncertainty layer and needs finite-sample coverage guarantees.
7. **Authority.** An internally observable stochastic discriminator is not a
   substitute for protected custody when the target itself contains an
   external authorization fact.

## 10. Donor-theory map for a later literature audit

- Blackwell (1953), comparison of experiments, DOI
  `10.1214/aoms/1177729032`.
- Chernoff (1959), sequential design of experiments, DOI
  `10.1214/aoms/1177706205`.
- Smallwood and Sondik (1973), finite-horizon partially observed control and
  policy-vector frontiers, DOI `10.1287/opre.21.5.1071`.
- Berger (1985), *Statistical Decision Theory and Bayesian Analysis*.
- Manski (2003), *Partial Identification of Probability Distributions*.
- Walley (1991), *Statistical Reasoning with Imprecise Probabilities*.
- Iyengar (2005), robust dynamic programming, DOI `10.1287/moor.1040.0129`.
- Nilim and El Ghaoui (2005), robust control of Markov decision processes,
  DOI `10.1287/opre.1050.0216`.
- Wiesemann, Kuhn, and Rustem (2013), robust Markov decision processes, DOI
  `10.1287/moor.1120.0566`.
- Nakao, Jiang, and Shen (2021), distributionally robust POMDPs, DOI
  `10.1137/19M1268410`.
- Epstein and Schneider (2003), recursive multiple-priors, DOI
  `10.1016/S0022-0531(03)00097-8`.
- Naghshvar and Javidi (2013), active sequential hypothesis testing, DOI
  `10.1214/13-AOS1144`.
- Nitinawarat, Atia, and Veeravalli (2013), controlled sensing for
  multihypothesis testing, DOI `10.1109/TAC.2013.2261188`.
- Garivier and Kaufmann (2016), optimal best-arm identification,
  `https://proceedings.mlr.press/v49/garivier16a.html`.
- Golovin and Krause (2011), adaptive submodularity, *Journal of Artificial
  Intelligence Research* 42:427--486.

These entries identify nearest theory families. A same-repository adversarial
audit found the finite core sound but blocked a distinct-theorem novelty claim:
the Bellman/vector and pairwise information-cost components are donor-owned.
The list is still not a systematic full-text priority search or an external
specialist review.
