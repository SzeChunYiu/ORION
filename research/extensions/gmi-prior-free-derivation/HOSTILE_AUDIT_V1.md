# Prior-free GMI: hostile audit of `FORMAL_CORE_V1`

## Status

This record is an adversarial review, not a closure note. It treats every theorem in `FORMAL_CORE_V1.md` as provisional and attempts to produce the smallest countermodel that breaks it. A claim is retained only when its quantifiers survive the countermodel.

The review found that the central direction is viable, but several statements in v1 are too strong. Four defects are theorem-breaking; five others require boundary or typing corrections. The hardened successor should therefore separate predictive sufficiency from control sufficiency, replace naive cut cardinality by a conflict-hypergraph theorem, repair scalarization, and type the morphology/developmental frontiers consistently.

---

## A. Theorem-breaking findings

### A1. Scalarization does not necessarily detect pointwise strict dominance

V1 Proposition 2.3 states, in effect, that a scalar Bayes objective cannot select a uniformly dominated machine when the dominance is strict somewhere. This is false for general measures over an uncountable ecology.

Let \(\mathcal E=[0,1]\) with Lebesgue measure \(\mu\). Let two machines have scalar risk

\[
R_N(e)=0\quad\forall e,
\]

and

\[
R_M(e)=\mathbf 1[e=e_0]
\]

for one fixed \(e_0\). Then \(N\preceq M\) pointwise and the inequality is strict at \(e_0\), but

\[
\int R_N\,d\mu=\int R_M\,d\mu=0.
\]

Thus a \(\mu\)-Bayes objective may tie a pointwise dominated rule whenever the strict improvement is confined to a \(\mu\)-null set.

**Repair.** State scalarization abstractly. If \(\Phi\) is a scalar functional that is *strictly monotone with respect to the declared dominance relation*, then every minimizer of \(\Phi\) is nondominated. An expected-risk scalarization is strictly monotone only under additional support/continuity assumptions, or when the strict improvement occurs on positive measure. Priors remain optional selectors; they are not guaranteed to expose every point of the prior-free order.

### A2. The cut-cardinality theorem is false for a general stochastic channel

V1 Theorem 5.2 infers \(|Y|\ge N\) from the existence of \(N\) histories requiring different continuation behaviour. Distinct continuation laws do not imply zero-error decodability of the history. With a binary signal \(Y=\{0,1\}\), upstream histories can induce arbitrarily many distinct Bernoulli parameters; a downstream randomized policy can therefore induce arbitrarily many distinct action distributions while \(|Y|=2\).

The correct primitive is not “number of distinct behaviours”. It is **incompatibility**: two upstream cases require separation only when no single downstream response can satisfy both exactly.

For a complete causal cut, define a conflict hypergraph \(\mathfrak C_C\) on upstream cases. A subset \(B\) is a hyperedge when there is no single downstream continuation, using the same downstream side information, that satisfies the obligation for every history in \(B\). If a zero-error cut code maps each history \(h\) to a nonempty support \(S_h\subseteq Y\), exactness requires

\[
\bigcap_{h\in B}S_h=\varnothing
\]

in the appropriate deterministic/common-message sense; for pairwise conflicts, adjacent histories must have disjoint message supports. In the graph case this gives a chromatic lower bound; clique size \(N\) recovers \(|Y|\ge N\).

This connects the GMI cut theorem to zero-error information theory rather than ordinary Shannon capacity. Witsenhausen's zero-error side-information formulation is a useful donor: chromatic structure appears precisely because the receiver must distinguish only mutually confusable cases.

### A3. Predictive minimality is not the same theorem as minimal control state

The quotient in v1 Section 3 is valid as a **predictive-response quotient**: if a representation must reconstruct all declared future response laws under all environments and continuations, then histories with different response profiles cannot share one code.

It is not, however, a necessary state partition for every machine that merely satisfies a control obligation.

Counterexample: two histories have different future reward distributions, but the same action is optimal and satisfies the obligation in both. A controller may merge them even though a predictor of the full future response profile may not.

For control, define the feasible continuation correspondence

\[
\Gamma_\Omega(h)
=
\{c\in\mathcal C:\ c\text{ satisfies }\Omega\text{ from }h\text{ over the declared ecology}\}.
\]

A set of histories \(B\) can share one decision state only if

\[
\bigcap_{h\in B}\Gamma_\Omega(h)\ne\varnothing,
\]

subject also to transition-consistency/right-congruence constraints if the shared state is to persist through future observations.

Pairwise mergeability need not be transitive. For example,

\[
\Gamma(h_1)=\{a,b\},\quad
\Gamma(h_2)=\{b,c\},\quad
\Gamma(h_3)=\{a,c\}
\]

has nonempty pairwise intersections but empty triple intersection. Therefore a universal “minimal decision atom” need not be an equivalence quotient at all. The canonical object is the residual-response structure (or its conflict hypergraph); minimal controller partitions are colorings/congruences of that object and need not be unique.

**Consequence.** The phrase “fundamental cognitive atom” must be narrowed. There is a canonical predictive quotient for a declared query family. There need not be a unique coarsest control-state quotient for an arbitrary obligation.

### A4. The developmental frontier is not the intersection of the global frontier with reachability

V1 defines

\[
\mathcal F_B=\mathcal F_X\cap\mathcal R_B.
\]

This object answers “which globally Pareto-optimal morphologies are reachable?” It does not answer “which reachable morphologies are Pareto-optimal under the budget?” If every global frontier point is unreachable, the intersection is empty even though some reachable candidates are best among all reachable candidates.

The correct pair of objects is

\[
\mathcal F_{\mathrm{global}}^{\mathrm{reachable}}
=
\mathcal F_X\cap\mathcal R_B,
\]

and

\[
\mathcal F_B
=
\operatorname{Min}_{\preceq}
(\mathfrak X_\theta\cap\mathcal R_B).
\]

These coincide only under an additional reachability condition.

---

## B. Formal defects requiring repair

### B1. The morphology frontier is ill-typed

V1 Definition 8.1 defines \(\mathcal F_X\) as a set of performance/resource vectors, but Definition 8.2 quotients \(\mathcal F_X\) by an implementation gauge and Section 9 intersects it with a set of morphology classes. Those operations require \(\mathcal F_X\subseteq\mathfrak X_\theta\), not a subset of the objective image.

**Repair.** Define

\[
x\preceq_\theta y
\iff
\Psi_\theta(x)\le_{\mathrm{cw}}\Psi_\theta(y),
\]

then

\[
\mathcal F_X
=
\{x\in\mathfrak X_\theta:\nexists y\in\mathfrak X_\theta\text{ with }y\prec_\theta x\}.
\]

The objective image \(\Psi_\theta(\mathcal F_X)\) is a different object.

### B2. Nonemptiness of a Pareto frontier is not automatic

The nondominated set is always definable, but can be empty in an infinite feasible class with an endless descending chain. V1 should not say that a nonempty frontier “exists” without compactness/well-foundedness assumptions.

For finite-dimensional objective images, compactness of the feasible image suffices for existence of a Pareto minimum. More general product orders need an explicitly stated topological/order-theoretic condition.

### B3. The approximate-state theorem silently assumes a metric

V1 chooses a generic “discrepancy” \(D\), then uses a triangle inequality. KL divergence, for example, is not a metric and does not satisfy the required triangle inequality.

**Repair.** Require an extended pseudometric \(D\), or state the lower bound in terms of a packing relation explicitly defined by the reconstruction balls of the chosen loss.

### B4. The effective-transducer condition is too weak for countable sampling

Pointwise computability of each transition probability over a countably infinite next-state space does not by itself supply an effective sampler or an effective tail bound. A universal simulator needs a stronger hypothesis.

**Repair.** Use one of:

1. finite branching with uniformly computable probabilities;
2. a uniformly computable probability mass function with effective tail control; or
3. define the transition kernel directly as an effectively samplable kernel.

The realization theorem should then be stated only for that effective subdomain.

### B5. Reachability by positive point probability fails on continuous morphology spaces

If the morphology process has a continuous state space, every individual point can have probability zero while still lying in the support of the process. V1's positive-point-probability definition is therefore topology dependent.

**Repair.** For countable discrete spaces, retain positive-probability reachability. For a topological morphology space with law \(\nu_t\), define

\[
\mathcal R_B
=
\overline{\bigcup_{t\le B}\operatorname{supp}(\nu_t)}.
\]

A confidence-reachable set may additionally be defined by hitting neighborhoods with probability at least \(1-\delta\).

### B6. Worst-case regret must preserve the interactive environment semantics

The notation \(e_{1:T}\in\mathcal E^T\) in v1 changes the object being quantified over: an environment had already been defined as a causal family of kernels. For an adaptive interactive environment, comparator trajectories are counterfactual and differ across agents.

**Repair.** Define

\[
\operatorname{Reg}_T(A;\mathcal E,\mathcal K)
=
\sup_{e\in\mathcal E}
\left[
L_T(A,e)-\inf_{K\in\mathcal K}L_T(K,e)
\right],
\]

where each \(L_T(K,e)\) is evaluated by running \(K\) against an independent copy of the same structural causal kernel \(e\). Stronger adversarial notions should be separately named.

### B7. Off-support histories need counterfactual semantics

The predictive quotient quantifies over future laws after arbitrary histories. A regular conditional distribution need not be uniquely defined on histories of probability zero.

This problem disappears if an environment is treated structurally, as v1 initially does: its causal kernels are defined on every admitted history and therefore determine interventional continuation laws even off the realized path. The successor should say this explicitly. If an environment is supplied only observationally, the quotient must be restricted to histories on which the conditional law is identified.

### B8. Gauge should be induced by declared observables when possible

An arbitrary gauge group \(G\) risks hiding a representation prior in the equivalence relation. A cleaner construction is to declare the family \(\mathcal Q\) of operational probes available to the theory—obligation-relevant interventions, resource probes, and any physically meaningful internal cut probes—and define

\[
M\simeq_{\mathcal Q}N
\iff
\forall q\in\mathcal Q:\ q(M)=q(N).
\]

The gauge transformations are then exactly the transformations lying in the kernel of the declared observables. This makes the representation quotient extensional rather than chosen by architecture vocabulary.

---

## C. Hardened decomposition

The formal programme should use three different state objects.

### C1. Predictive response profile

For each history \(h\), define

\[
\mathsf Q_h:(e,c)\mapsto
\operatorname{Eval}_\Omega(h,e,c),
\]

where \(\operatorname{Eval}_\Omega\) is the complete declared obligation-relevant future response object. Then

\[
h\equiv_{\mathrm{pred}}h'
\iff
\mathsf Q_h=\mathsf Q_{h'}.
\]

The quotient \(S_{\mathrm{pred}}=\mathcal H/\equiv_{\mathrm{pred}}\) is canonical and is the coarsest deterministic statistic sufficient to reconstruct \(\mathsf Q_h\).

This is the proper generalization of the Myhill–Nerode/predictive-state/causal-state idea.

### C2. Control feasibility correspondence

For an exact obligation, define \(\Gamma_\Omega(h)\) as the continuation policies that satisfy the obligation from \(h\). The family \(\{\Gamma_\Omega(h)\}\), not equality of future distributions, determines which histories may safely share decision state.

A controller-state cell \(B\) is admissible only if

\[
\bigcap_{h\in B}\Gamma_\Omega(h)\ne\varnothing,
\]

and the state partition must also admit a consistent update under admissible one-step extensions. The minimum state problem is therefore a constrained hypergraph-coloring/congruence problem. Uniqueness is not generic.

### C3. Physical morphology class

Only after behaviour/control constraints are fixed should implementations be compared under substrate resources and operational probes. Let \(\mathfrak X_\theta\) be the realizable morphology space at substrate parameter \(\theta\), modulo the extensional relation induced by the declared probe family. The prior-free physical frontier is the set of nondominated morphology classes in \(\mathfrak X_\theta\).

These three objects answer different questions. A proof about one must not be promoted to another.

---

## D. Literature alignment used in the hardening

The corrected structure has close donors but is not identical to any one of them.

- **Myhill–Nerode:** future distinguishability yields canonical minimal deterministic state for a language. It motivates the residual-response construction but does not by itself solve stochastic control.
- **Predictive state representations:** action-conditional predictions can serve as state without positing hidden generative state; Littman and Sutton (NIPS 2001) establish this explicitly for controlled stochastic systems.
- **Computational mechanics / causal states:** predictive equivalence classes provide minimal predictive structure in stochastic processes.
- **Blackwell comparison:** information structures should be compared by what decision problems they can support, not by syntax of the channel.
- **Zero-error information theory:** exact communication requirements are governed by confusability/conflict structure; graph coloring is the right object in the finite zero-error setting.
- **Sequential/minimax learning:** prior-free learning claims are naturally expressed as worst-case regret or minimax value over a declared environment/comparator class, not by silently supplying a distribution over worlds.

These donors constrain vocabulary and prevent relabeling established structures as new GMI theorems. The GMI contribution, if it survives, is the composition: residual obligation structure -> control conflict structure -> information cuts -> substrate-conditioned morphology -> developmental reachability, with each layer typed separately.

---

## E. Revised closure standard

The following are sufficient for **formal-core closure**, but not for empirical GMI closure:

1. predictive-response quotient theorem proved with structural/off-support semantics;
2. exact controller-state theorem stated as a congruent coloring/cover problem, including a non-uniqueness counterexample;
3. zero-error cut theorem proved from conflict structure rather than raw behavioural distinctness;
4. nondominated morphology frontier correctly typed and accompanied by explicit nonemptiness conditions;
5. developmental reachable frontier distinguished from reachable points on the global frontier;
6. effective realization theorem restricted to effectively samplable kernels;
7. known architecture families mapped into the same operational language without architecture labels in the derivation;
8. at least one held-out architecture family recovered by a frozen reduction vocabulary;
9. a preregistered unoccupied morphology region before architecture search.

Items 1--6 are mathematical. Items 7--9 are empirical/retrodictive/prospective and must retain separate evidence status.

## Audit terminal

`FORMAL_CORE_V1` is **not closed**. Its central prior-elimination programme remains viable, but its strongest universal-state and channel statements require replacement rather than cosmetic qualification. The next version should be built around the predictive quotient plus the control-conflict hypergraph. That pair is strictly more general and removes the largest hidden inference in v1: the assumption that predicting all future-relevant differences is necessary for every successful controller.
