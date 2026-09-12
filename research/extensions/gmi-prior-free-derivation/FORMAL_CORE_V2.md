# Prior-free GMI: formal core v2

## 0. Claim discipline

This note develops a prior-free core for general machine-intelligence theory. “Prior-free” has one precise meaning here:

> no probability measure over admissible environments, and no architecture family, is supplied to the derivation.

The theory is not assumption-free. It is conditional on a declared interaction domain, cognitive obligation, admissible ecology, and physical/resource model. Those objects determine the quantifiers of the theorem. Removing them does not produce a more general intelligence theory; it removes the question being answered.

Four levels are kept distinct throughout:

1. **predictive semantics:** which histories have identical obligation-relevant future response profiles?;
2. **control feasibility:** which histories can safely share a controller state?;
3. **physical morphology:** which operationally distinguishable implementations are nondominated under a substrate/resource model?;
4. **development:** which morphologies are reachable, and which are best among the reachable set, under a declared search/development process?

No theorem is promoted across these levels without a separate bridge.

---

## 1. Structural interaction model

Let \(\mathcal A\) and \(\mathcal O\) be standard Borel action and observation spaces. A finite history is

\[
h_t=(o_0,a_0,o_1,a_1,\ldots,o_t)\in\mathcal H_t,
\qquad
\mathcal H=\bigcup_{t\ge0}\mathcal H_t.
\]

An environment \(e\) is a structural causal kernel family

\[
e_t(do_{t+1}\mid h_t,a_t).
\]

The kernels are defined on every admitted history, not merely almost surely on one observational trajectory. This gives counterfactual continuation semantics without invoking an arbitrary version of a regular conditional probability on a null history.

The **ecology** is a nonempty set

\[
\mathcal E\subseteq\{\text{admitted causal environments}\}.
\]

No probability measure on \(\mathcal E\) is assumed.

A continuation policy \(c\in\mathcal C\) is a causal action-kernel family for future times. The class \(\mathcal C\) is part of the declared interaction domain: a theorem quantified over open-loop continuations is not the same theorem as one quantified over all feedback continuations.

### Obligation evaluator

Let \(\Omega\) determine an evaluation map

\[
\operatorname{Eval}_\Omega(h,e,c)\in\mathcal Y_\Omega,
\]

where \(\mathcal Y_\Omega\) is the complete response object relevant to the claim. Examples include a trajectory-law projection, a vector of losses, an accept/reject test vector, or a resource-adjusted outcome profile.

For exact control obligations, let \(\mathcal A_\Omega\subseteq\mathcal Y_\Omega\) be the acceptable set. Then

\[
c\models_\Omega(h,e)
\iff
\operatorname{Eval}_\Omega(h,e,c)\in\mathcal A_\Omega.
\]

This notation is deliberately more general than expected utility.

---

## 2. Canonical predictive response state

For each history \(h\), define its residual response functional

\[
\mathsf Q_h:\mathcal E\times\mathcal C\to\mathcal Y_\Omega,
\qquad
\mathsf Q_h(e,c)=\operatorname{Eval}_\Omega(h,e,c).
\]

### Definition 2.1 (predictive-response equivalence)

\[
h\equiv_{\mathrm{pred}}h'
\iff
\mathsf Q_h=\mathsf Q_{h'}.
\]

Let

\[
S_{\mathrm{pred}}
=
\mathcal H/\!\equiv_{\mathrm{pred}},
\qquad
q_{\mathrm{pred}}:\mathcal H\to S_{\mathrm{pred}}.
\]

### Definition 2.2 (response-sufficient statistic)

A deterministic statistic \(\phi:\mathcal H\to Z\) is response-sufficient when there exists

\[
G:Z\times\mathcal E\times\mathcal C\to\mathcal Y_\Omega
\]

such that

\[
G(\phi(h),e,c)=\mathsf Q_h(e,c)
\]

for every admitted \(h,e,c\).

### Theorem 2.3 (coarsest exact predictive statistic)

Every response-sufficient statistic refines \(q_{\mathrm{pred}}\). Equivalently, for every response-sufficient \(\phi\), there exists a unique map on reachable codes

\[
r:\phi(\mathcal H)\to S_{\mathrm{pred}}
\]

such that

\[
q_{\mathrm{pred}}=r\circ\phi.
\]

#### Proof

If \(\phi(h)=\phi(h')\), response sufficiency gives

\[
\mathsf Q_h(e,c)
=G(\phi(h),e,c)
=G(\phi(h'),e,c)
=\mathsf Q_{h'}(e,c)
\]

for all \(e,c\). Hence \(h\equiv_{\mathrm{pred}}h'\). Therefore each reachable \(\phi\)-fiber is contained in one predictive equivalence class and the factor map is well-defined. \(\square\)

### Corollary 2.4

Any two coarsest deterministic response-sufficient statistics are isomorphic on their reachable states.

### Boundary 2.5

Theorem 2.3 is a theorem about reconstructing the complete declared response profile. It does **not** state that every successful controller must distinguish every element of \(S_{\mathrm{pred}}\). Prediction and control have different minimality problems.

This distinction is essential.

---

## 3. Exact control state is a conflict problem, not generally a quotient

Define the robust feasible-continuation correspondence

\[
\Gamma_\Omega(h)
=
\{c\in\mathcal C:
\forall e\in\mathcal E,
\ c\models_\Omega(h,e)
\}.
\]

If \(\Gamma_\Omega(h)=\varnothing\), the exact obligation is infeasible from \(h\) against the declared ecology.

### Definition 3.1 (joint controllability)

A set of histories \(B\subseteq\mathcal H\) is jointly controllable when

\[
\bigcap_{h\in B}\Gamma_\Omega(h)\ne\varnothing.
\]

### Definition 3.2 (control-conflict hypergraph)

Let \(\mathfrak C_\Omega\) be the hypergraph with vertex set the admitted histories and hyperedges

\[
\mathcal E_{\mathfrak C}
=
\left\{
B\subseteq\mathcal H:
\bigcap_{h\in B}\Gamma_\Omega(h)=\varnothing
\right\}.
\]

It is sufficient in finite calculations to retain only inclusion-minimal hyperedges.

### Proposition 3.3 (necessary controller-state condition)

Suppose a deterministic controller maps histories to an internal state \(z(h)\), and once two histories have the same state the controller has no other retained information about which history occurred. For exact satisfaction, every state fiber

\[
B_z=\{h:z(h)=z\}
\]

must be jointly controllable.

#### Proof

The continuation implemented from state \(z\) is the same for every history in \(B_z\), modulo future observations handled by that common continuation policy. Exact success therefore requires one continuation belonging to every \(\Gamma_\Omega(h)\), \(h\in B_z\). \(\square\)

### Corollary 3.4 (hypergraph coloring lower bound)

For a finite admitted history set, the number of controller states is at least the chromatic number of \(\mathfrak C_\Omega\), where a valid color class may not contain a conflict hyperedge.

This is only a lower bound for a persistent finite-state controller. The state partition must additionally admit a consistent causal update under admissible one-step extensions; this is a right-congruence/realizability constraint.

### Proposition 3.5 (nonexistence of a generic coarsest control quotient)

Minimal control merging need not be transitive.

#### Witness

Let

\[
\Gamma(h_1)=\{a,b\},\qquad
\Gamma(h_2)=\{b,c\},\qquad
\Gamma(h_3)=\{a,c\}.
\]

Each pair is jointly controllable, but

\[
\Gamma(h_1)\cap\Gamma(h_2)\cap\Gamma(h_3)=\varnothing.
\]

Thus pairwise “may share a state” is not an equivalence relation. Different minimum colorings may exist. There is therefore no theorem asserting a unique coarsest decision-state quotient for arbitrary obligations.

### Consequence

The canonical object at this level is the residual response/feasibility structure. A particular minimal controller is a realization of a valid coloring/congruence of that structure.

---

## 4. Prior-free memory lower bounds

### 4.1 Predictive-complete tasks

If \(|S_{\mathrm{pred}}|=N<\infty\), every deterministic exact response-sufficient code has at least \(N\) reachable codewords and therefore requires at least

\[
\lceil\log_2N\rceil
\]

bits in a fixed-length worst-case binary code.

This follows directly from Theorem 2.3.

### 4.2 Control tasks

For a finite exact control problem, Proposition 3.3 gives

\[
|Z|\ge\chi(\mathfrak C_\Omega),
\]

before transition-consistency constraints are imposed.

Hence the predictive lower bound and the control lower bound are generally different:

\[
\chi(\mathfrak C_\Omega)
\le
|S_{\mathrm{pred}}|
\]

need not be an equality.

### 4.3 Approximate predictive state

Let \(D\) be an extended pseudometric on \(\mathcal Y_\Omega\). Define

\[
d(h,h')
=
\sup_{e\in\mathcal E,c\in\mathcal C}
D(\mathsf Q_h(e,c),\mathsf Q_{h'}(e,c)).
\]

Let \(P_{2\varepsilon}\) be the packing number at separation strictly greater than \(2\varepsilon\). Any deterministic code that reconstructs every response profile with worst-case \(D\)-error at most \(\varepsilon\) needs at least \(P_{2\varepsilon}\) codewords.

The proof is the usual packing argument and uses the triangle inequality. Divergences lacking a triangle inequality require a different ball/separation statement; they are not covered by this proposition.

---

## 5. Causal cut theorem: zero-error form

A channel theorem must specify what information is already available downstream. Let a **complete cut** separate an upstream variable \(H\) from the downstream controller such that every causal influence of \(H\) on the downstream decision that is not fixed common side information passes through a cut transcript \(Y\).

For each history \(h\), let \(P_h\) denote the support of the cut transcript.

### Definition 5.1 (pathwise zero-error obligation at a cut)

The obligation is pathwise zero-error across the cut when every transcript value \(y\) that occurs with positive probability after history \(h\) must induce a downstream continuation belonging to \(\Gamma_\Omega(h)\). Success is not allowed to arise only after averaging incompatible downstream continuations.

### Theorem 5.2 (conflict-hypergraph cut bound)

Under a pathwise zero-error obligation, for every cut symbol \(y\), the set

\[
B_y=\{h:y\in P_h\}
\]

is jointly controllable. Therefore the cut symbols form a coloring cover of the control-conflict hypergraph. For finite \(Y\),

\[
|Y|\ge\chi(\mathfrak C_{\Omega,C}).
\]

In particular, if \(N\) histories are pairwise incompatible, then

\[
|Y|\ge N,
\qquad
\log_2|Y|\ge\log_2N.
\]

#### Proof

Fix \(y\). Downstream receives the same transcript value and the same declared side information for every \(h\in B_y\), hence executes the same continuation conditional on \(y\). Pathwise exactness requires that continuation to lie in every \(\Gamma_\Omega(h)\), so \(B_y\) is jointly controllable. Assigning each history any one transcript in its nonempty support yields a valid hypergraph coloring. \(\square\)

### Boundary 5.3

The theorem does not apply to obligations satisfiable only in expectation by different mixtures over common cut symbols. Those problems require a stochastic information bound and, for average error/information quantities, usually an explicit source distribution or a minimax channel formulation.

The zero-error result is prior-free precisely because it is worst-case and combinatorial.

---

## 6. Prior-free decision order

For each feasible machine \(M\), substrate condition \(\theta\), environment \(e\), horizon \(T\), and obligation coordinate \(j\), collect declared losses and resource costs into a performance profile

\[
\Psi_\theta(M)\in\overline{\mathbb R}^{\Lambda},
\]

where \(\Lambda\) is the declared index set of obligation/resource probes.

### Definition 6.1 (dominance)

\[
N\preceq_\theta M
\iff
\Psi_\theta(N)_\lambda
\le
\Psi_\theta(M)_\lambda
\quad\forall\lambda\in\Lambda.
\]

Write \(N\prec_\theta M\) when \(N\preceq_\theta M\) and the profiles are not identical.

### Definition 6.2 (prior-free frontier)

For feasible class \(\mathcal M_\theta\),

\[
\mathcal F_\theta
=
\{M\in\mathcal M_\theta:
\nexists N\in\mathcal M_\theta\text{ with }N\prec_\theta M\}.
\]

This set is defined without a measure on \(\mathcal E\). It may be empty unless existence conditions are supplied.

### Proposition 6.3 (strictly monotone scalar selectors)

Let \(\Phi\) be a scalar functional on performance profiles satisfying

\[
x\le y,\ x\ne y
\Longrightarrow
\Phi(x)<\Phi(y).
\]

Every minimizer of \(\Phi\circ\Psi_\theta\) is nondominated.

#### Proof

If a minimizer \(M\) were dominated by \(N\), strict monotonicity would give

\[
\Phi(\Psi_\theta(N))<\Phi(\Psi_\theta(M)),
\]

contradiction. \(\square\)

A Bayes expectation is one possible scalar selector, but it is strictly monotone for the pointwise order only under appropriate support conditions. A strict improvement on a prior-null environment may be invisible to expected risk.

### Proposition 6.4 (finite-dimensional nonemptiness)

If the declared objective profile is finite-dimensional and \(\Psi_\theta(\mathcal M_\theta)\) is nonempty and compact, then \(\mathcal F_\theta\ne\varnothing\).

#### Proof

Minimize any strictly positive weighted sum of the finitely many coordinates over the compact image. A minimizer exists and is nondominated by Proposition 6.3. \(\square\)

### Boundary 6.5

A prior-free frontier need not be small. For a rich ecology, many mutually incomparable machines may survive. This is not incompleteness of the order; it is non-identifiability under the declared premises.

---

## 7. Operational morphology without architecture labels

A representation-independent morphology cannot be defined by listing implementation names. It must be defined extensionally by probes.

Let \(\mathcal Q\) be the declared family of operational probes. At minimum it contains:

1. obligation-relevant behavioural probes over \(\mathcal E\) and \(\mathcal C\);
2. substrate/resource probes \(\rho_\theta\);
3. when internal topology is itself claimed, the explicitly declared physically meaningful internal intervention/cut probes.

### Definition 7.1 (operational equivalence)

\[
M\simeq_{\mathcal Q}N
\iff
q(M)=q(N)
\quad\forall q\in\mathcal Q.
\]

The morphology of \(M\) at resolution \(\mathcal Q\) is

\[
\chi_{\mathcal Q}(M)=[M]_{\simeq_{\mathcal Q}}.
\]

This replaces an arbitrary gauge group with the kernel of declared observables. State renaming, invertible coordinate changes, semantics-preserving compilation, and insertion of observationally null bookkeeping are automatically quotiented when no probe distinguishes them.

### Theorem 7.2 (label non-identifiability)

If \(M\simeq_{\mathcal Q}N\), no theory whose premises and conclusions are invariant under \(\simeq_{\mathcal Q}\) can derive an architecture label that separates \(M\) from \(N\) unless that label encodes information absent from \(\mathcal Q\).

This is an extensionality theorem, not an empirical hypothesis.

### Boundary 7.3

Morphology is relative to measurement resolution. A purely behavioural/resource theory cannot infer internal wiring that has no behavioural or resource consequence under its probes. Internal-topology claims require internal instrumentation in \(\mathcal Q\); this is a measurement declaration, not an architecture prior.

---

## 8. Resource-conditioned morphology phase law

Let

\[
\mathfrak X_\theta
=
\{\chi_{\mathcal Q}(M):M\text{ is physically realizable under }\theta\}.
\]

The performance profile descends to \(\mathfrak X_\theta\) because equivalent machines agree on all declared probes.

Define

\[
x\preceq_\theta y
\iff
\Psi_\theta(x)\le_{\mathrm{cw}}\Psi_\theta(y).
\]

### Definition 8.1 (morphology frontier)

\[
\mathcal F_X(\theta)
=
\{x\in\mathfrak X_\theta:
\nexists y\in\mathfrak X_\theta\text{ with }y\prec_\theta x\}.
\]

The conditional phase law is

\[
\theta\longmapsto\mathcal F_X(\theta).
\]

The theory can derive this map without knowing which numerical \(\theta\) nature or a device currently instantiates.

### Definition 8.2 (morphology-identifiable region)

A region \(R\subseteq\Theta\) is identifiable at probe resolution \(\mathcal Q\) when

\[
|\mathcal F_X(\theta)|=1
\quad\forall\theta\in R.
\]

When the frontier has multiple incomparable classes, a unique morphology is not identified.

---

## 9. Development and reachability

Let \(\mathcal D\) be a deterministic or stochastic development process on \(\mathfrak X_\theta\), with initial law \(\nu_0\). For discrete countable morphology spaces define

\[
\mathcal R_B
=
\{x:\Pr_\mathcal D(\exists t\le B:X_t=x)>0\}.
\]

For topological morphology spaces use support reachability

\[
\mathcal R_B
=
\overline{\bigcup_{t\le B}\operatorname{supp}(\nu_t)}.
\]

Two different frontier notions are required.

### Definition 9.1 (reachable global frontier)

\[
\mathcal G_B
=
\mathcal F_X(\theta)\cap\mathcal R_B.
\]

This asks whether globally nondominated morphologies are reachable.

### Definition 9.2 (best reachable frontier)

\[
\mathcal F_B
=
\{x\in\mathfrak X_\theta\cap\mathcal R_B:
\nexists y\in\mathfrak X_\theta\cap\mathcal R_B\text{ with }y\prec_\theta x\}.
\]

This is the correct developmental morphology frontier at budget \(B\).

If \(\mathcal G_B=\varnothing\), development can still have a nonempty best-reachable frontier.

For measurable target sets \(A\subseteq\mathfrak X_\theta\), define

\[
\tau_A=\inf\{t:X_t\in A\}
\]

and study \(\Pr(\tau_A\le B)\). In continuous spaces one should normally use a closed target region or tolerance neighborhood rather than a single point.

---

## 10. Prior-free learning statement

Let \(L_T(A,e)\) be the cumulative declared loss obtained by running learner/controller \(A\) against an independent execution of structural environment \(e\). For comparator class \(\mathcal K\), define

\[
\operatorname{Reg}_T(A;\mathcal E,\mathcal K)
=
\sup_{e\in\mathcal E}
\left[
L_T(A,e)-\inf_{K\in\mathcal K}L_T(K,e)
\right].
\]

A prior-free learnability theorem can establish

\[
\operatorname{Reg}_T=o(T)
\]

or a finite-horizon minimax bound.

Such a theorem identifies a feasibility/rate envelope. It does not in general identify a unique update law. Different algorithms can realize the same regret envelope with different physical costs.

For adaptive adversaries whose response depends on the learner in ways not captured by one reusable structural kernel, policy regret or another explicitly counterfactual notion must be used instead. The quantifier cannot be changed silently.

---

## 11. Effective realization

Behavioural universality and resource equivalence are separate.

### Definition 11.1 (effectively samplable transducer)

A finite/countable-state causal transducer is effectively samplable when there is an algorithm that, given the current encoded state/input and rational \(\varepsilon>0\), samples a next-state/output pair from a distribution within total-variation distance \(\varepsilon\) of the specified transition kernel, uniformly over admitted inputs.

Finite branching with uniformly computable transition probabilities is a sufficient special case.

### Proposition 11.2 (universal behavioural simulation)

Every effectively samplable transducer can be simulated by a universal probabilistic digital machine so that, for any fixed finite horizon \(T\) and \(\delta>0\), the induced length-\(T\) external trajectory law is within total-variation distance \(\delta\) of the target law.

#### Proof sketch

At each transition choose sampling accuracy \(\varepsilon_t\) with

\[
\sum_{t<T}\varepsilon_t\le\delta.
\]

Use the effective sampler at step \(t\). A standard coupling/union bound bounds finite-horizon trajectory-law error by the sum of one-step errors. \(\square\)

### Boundary 11.3

The simulator may incur arbitrary overhead relative to a native realization. Therefore

\[
\text{behavioural universality}
\not\Rightarrow
\text{resource-equivalent morphology}.
\]

Ideal exact-real, noncomputable, acausal, or genuinely quantum-interface systems lie outside Proposition 11.2 unless separately formalized.

---

## 12. Representation coverage of architecture families

### Theorem 12.1 (causal-transducer coverage)

Every classical causal interactive machine defines an external causal transducer and therefore an operational morphology class \(\chi_{\mathcal Q}(M)\). Every digitally implementable such machine lies in the effective subdomain of Section 11, subject to its actual finite-precision implementation.

#### Proof

At each interaction step take the complete physically retained configuration of the implementation as raw state. Causality supplies a transition/output kernel from current configuration and new input to next configuration and output. All architecture-specific objects—weights, caches, recurrent state, symbolic stores, retrieval indices, populations, programs, planners, tool sessions—are components of that raw configuration. Quotient the resulting implementation by \(\simeq_{\mathcal Q}\). \(\square\)

### Corollary 12.2

A new architecture name does not by itself require a new primitive. It requires a new primitive only if it exhibits an operational distinction not expressible by the declared causal interaction, probe, resource, or developmental language.

### Quantum boundary

A quantum device with purely classical external inputs/outputs induces a classical stochastic external transducer after measurement, although its resource profile may be quantum-specific. A theory with genuinely quantum external interfaces, coherent inter-agent channels, or entangled interventions requires a quantum-instrument generalization of the interaction layer.

---

## 13. Coverage, recovery, prediction

Three empirical standards must not be conflated.

### Coverage

Given a known architecture \(K\), construct \(\chi_{\mathcal Q}(K)\). Theorem 12.1 gives broad formal coverage, so this is the weakest standard.

### Recovery

Freeze \((\Omega,\mathcal E,\Theta,\mathcal Q)\) without using the held-out architecture label; derive a morphology region \(R\); then show

\[
\chi_{\mathcal Q}(K)\in R.
\]

A credible recovery study must hold out architecture families and freeze the reduction vocabulary before inspection.

### Prospective prediction

Derive and preregister an unoccupied morphology region

\[
R_{\mathrm{new}}\subseteq\mathfrak X_\theta,
\qquad
R_{\mathrm{new}}\cap\mathcal K_{\mathrm{known}}=\varnothing,
\]

then search independently for a realization. Prospective success is substantially stronger evidence than coverage or retrospective recovery.

---

## 14. Minimal primitive basis

For the formal results above, the irreducible declarations are most cleanly grouped as follows.

### P0. Interaction domain \(\mathfrak D\)

Specifies causal histories, allowed interventions/continuations, admissible machine/interface types, and the background extensional logic needed to state equality and composition.

Delete it and causal-cut, continuation, and machine-realization claims are undefined. Allow acausal future access and the causal information lower bounds fail.

### P1. Obligation \(\Omega\)

Specifies which response distinctions matter and which outcomes are acceptable.

Delete it and two otherwise identical worlds with opposite desired terminal actions are indistinguishable to the theory.

### P2. Ecology \(\mathcal E\)

Specifies the worlds over which the claim is quantified.

Delete or make it unrestricted and no nontrivial pointwise-dominant learning/action rule is generally available; opposing environments can require opposing actions after identical past data.

### P3. Physical/resource model \((\Theta,\rho)\)

Specifies which implementation costs distinguish behaviourally equivalent realizations.

Delete it and memory/recomputation, communication/locality, latency/energy, precision/reliability and related morphology trades have no order.

### P4. Development process \((\mathcal D,B)\), only for developmental prediction

Optimality does not imply attainability. Developmental statements require a search/update process and budget. This primitive is not needed for static semantic or static frontier theorems.

### Probe resolution

The operational probe family \(\mathcal Q\) should be generated from P1--P3 whenever possible. Additional internal morphology probes must be explicitly declared. Their presence changes observational resolution but does not insert a named architecture into the premises.

No Bayesian prior over \(\mathcal E\), neural primitive, symbolic primitive, attention operator, gradient rule, memory architecture, or program-search architecture occurs in this basis.

---

## 15. Probability is optional at the ecology level

The theory permits stochastic environment and machine kernels, but it does not require a probability measure over which environment is “the true one”.

If a separate coherence/valuation theorem derives probability calculus for uncertainty inside a model, Bayes' rule follows from that calculus under its usual conditions. Such results do not determine a unique measure over \(\mathcal E\), and the present frontier theory does not need one.

Algorithmic priors, maximum-entropy updates, logical induction, minimax selectors, and robust Bayes classes are therefore possible *selectors or model classes above the core*. They are not hidden axioms of the prior-free order.

---

## 16. Main theorem package

Under \((\mathfrak D,\Omega,\mathcal E,\Theta,\rho)\):

1. the residual response functional induces a canonical predictive quotient \(S_{\mathrm{pred}}\), unique up to isomorphism among coarsest deterministic response-sufficient statistics;
2. exact control compression is governed by joint feasibility, represented by a control-conflict hypergraph, and need not admit a unique coarsest quotient;
3. predictive-complete memory is lower-bounded by \(|S_{\mathrm{pred}}|\), while exact control memory is lower-bounded by the conflict-hypergraph chromatic number plus any additional transition-congruence requirement;
4. pathwise zero-error information cuts inherit the same conflict structure and therefore obey a chromatic message-alphabet lower bound;
5. the prior-free decision order is the coordinatewise order on declared obligation/resource profiles; its nondominated set requires no measure on \(\mathcal E\);
6. scalar Bayes or utility objectives are optional selectors and exclude all dominated points only when the scalarization is strictly monotone for the declared order;
7. morphology is an extensional operational equivalence class under declared probes, not an architecture label;
8. physical parameters induce a conditional phase law \(\theta\mapsto\mathcal F_X(\theta)\);
9. developmental optimality is the Pareto frontier of the reachable set, distinct from the subset of globally optimal points that happen to be reachable;
10. every classical causal architecture maps into the transducer/morphology language; effectively samplable machines admit universal behavioural simulation, with no resource-equivalence claim.

The hardened chain is

\[
(\mathfrak D,\Omega,\mathcal E)
\Longrightarrow
\begin{cases}
S_{\mathrm{pred}} & \text{predictive semantics},\\
\mathfrak C_\Omega & \text{control conflict},
\end{cases}
\]

\[
\Longrightarrow
\text{state and cut lower bounds}
\Longrightarrow
(\Theta,\rho,\mathcal Q)
\Longrightarrow
\mathfrak X_\theta
\Longrightarrow
\mathcal F_X(\theta),
\]

and, only after a developmental process is declared,

\[
(\mathcal D,B)
\Longrightarrow
\mathcal R_B
\Longrightarrow
\mathcal F_B.
\]

No architecture family and no probability measure over the ecology appears in the derivation.

---

## 17. What is now closed, and what is not

### Formal statements that can be treated as closed within the declared domain

- coarsest exact predictive-response quotient;
- separation of predictive minimality from control minimality;
- control-conflict necessary condition and finite hypergraph coloring lower bound;
- pathwise zero-error cut lower bound;
- prior-free dominance/frontier definition;
- finite-dimensional compact-frontier existence theorem;
- extensional architecture-label non-identifiability;
- best-reachable versus reachable-global frontier distinction;
- effective finite-horizon behavioural simulation under effective sampling;
- representation coverage of classical causal architectures.

### Open scientific obligations

- a general exact characterization of minimal dynamic controller state beyond the necessary conflict coloring, including right-congruence/realizability;
- useful approximate-control analogues of the conflict theorem;
- nontrivial resource phase diagrams for concrete ecology families;
- held-out recovery of architecture families under a frozen probe/reduction vocabulary;
- prospective prediction and construction of an unoccupied morphology region;
- quantum-interface extension;
- evidence that the chosen obligation/ecology/resource declarations capture general intelligence rather than a restricted task family.

The theory should not be called empirically complete before the held-out and prospective obligations are met.

---

## 18. Donor map

The formal vocabulary intentionally overlaps established theory where the objects are already known:

- Myhill--Nerode: residual future distinguishability and minimal deterministic automata;
- predictive state representations: action-conditional future predictions as state;
- computational mechanics: predictive equivalence and causal states;
- Blackwell comparison of experiments: information compared by decision capability rather than channel syntax;
- zero-error information theory: confusability graphs/hypergraphs and chromatic communication bounds;
- minimax/sequential learning theory: prior-free performance envelopes over declared comparator/environment classes;
- universal computation: behavioural simulation separated from physical-resource efficiency.

GMI novelty cannot consist of renaming these donors. The research claim, if established, must lie in the cross-layer closure: deriving task-relative residual/control structure, propagating it through information cuts, and obtaining substrate-conditioned morphology and development phase laws that recover and prospectively predict machine forms.
