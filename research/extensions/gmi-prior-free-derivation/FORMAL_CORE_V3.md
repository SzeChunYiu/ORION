# A measure-free, architecture-neutral core for general machine intelligence

## Formal note v3

### Abstract

This note isolates the strongest architecture-neutral statements presently justified by the prior-free GMI programme. The word *prior-free* is used in a restricted sense: no probability measure over the admissible ecology and no architecture family is supplied to the derivation. The theory remains conditional on a causal interaction domain, a cognitive obligation, an ecology, a system boundary, and a physical/resource model.

Three corrections are essential. First, minimal predictive state and minimal control state are different objects. The former is a canonical residual quotient; the latter is generally a compatibility/closed-cover problem and need not admit a unique quotient. Second, a common continuation after state merging must be rooted and prefix-blind; otherwise the forgotten history can leak back into the controller. Third, a morphology frontier cannot be claimed merely by defining the set of physically realizable machines. A genuine derivation requires an outer set obtained from necessity theorems and an inner set obtained from explicit constructions. When the two meet at the Pareto boundary, the physical frontier is certified without enumerating architectures.

The resulting framework separates semantic residuals, current-action information, one-time plan information, autonomous controller state, communication cuts, resource-conditioned morphology, and developmental reachability. It also gives an explicit non-leakage condition for architecture-neutral premises and a closure criterion for morphology phase laws.

---

# 1. Domain of discourse

## 1.1 Causal interaction

Let \(\mathcal A\) and \(\mathcal O\) be standard Borel action and observation spaces. A finite interaction history is

\[
h_t=(o_0,a_0,o_1,a_1,\ldots,o_t),
\qquad
h_t\in\mathcal H_t,
\]

and

\[
\mathcal H=\bigcup_{t\ge0}\mathcal H_t.
\]

An environment \(e\) is a structural causal kernel family

\[
e_t(do_{t+1}\mid h_t,a_t).
\]

The kernels are part of the model and are defined on every admitted history, including counterfactual histories of zero probability under a particular run. This avoids ambiguity from arbitrary versions of regular conditional distributions on null events.

The **ecology** is a nonempty set

\[
\mathcal E\subseteq\{\text{admitted structural environments}\}.
\]

No probability measure on \(\mathcal E\) is assumed.

## 1.2 System boundary and free side information

A problem instance specifies a boundary

\[
\mathfrak B=(\mathcal B_{\mathrm{in}},\mathcal B_{\mathrm{out}},\mathcal S_{\mathrm{free}}).
\]

Every task-relevant information-bearing component is either counted inside the machine, placed outside behind an explicit channel, or listed as free side information. A clock, retrieval store, plan table, tool, external agent, or environment marker is not free unless the boundary says so.

This declaration is part of the theorem. Moving information across the boundary changes the resource problem.

## 1.3 Rooted strategies

Fix a root history \(h_t\) and re-index future time from zero. Before local action \(k\), let

\[
\sigma_k=(a^+_0,o^+_1,\ldots,a^+_{k-1},o^+_k),
\qquad
\sigma_0=\varnothing.
\]

A rooted continuation strategy is a causal kernel

\[
\kappa_k(da^+_k\mid \sigma_k,s),
\]

where \(s\in\mathcal S_{\mathrm{free}}\) is explicitly available side information. The pre-root history \(h_t\) is not an argument.

The same \(\kappa\) applied after two roots therefore cannot distinguish them unless a post-root observation or registered side-information variable does so.

This prefix-blindness condition is mandatory in every state-merging theorem below.

## 1.4 Cognitive obligation

Let

\[
\operatorname{Eval}^+_\Omega(h,e,\kappa;s)
\in\mathcal Y_\Omega
\]

be the complete obligation-relevant result of splicing rooted strategy \(\kappa\) after root \(h\) in environment \(e\). The codomain may contain a trajectory-law projection, a vector of losses, a safety predicate, a task score, or another registered outcome object.

For quantitative control, let

\[
\ell_\Omega(h,e,\kappa;s)\in[0,+\infty]
\]

be a declared loss and define robust loss

\[
L_\Omega(h,\kappa;s)
=
\sup_{e\in\mathcal E}
\ell_\Omega(h,e,\kappa;s).
\]

Expected loss inside one stochastic environment is permitted. What is absent is a probability measure selecting environments from \(\mathcal E\).

---

# 2. Canonical predictive residual

For each history \(h\), define the rooted response functional

\[
\mathsf Q_h:(e,\kappa,s)
\mapsto
\operatorname{Eval}^+_\Omega(h,e,\kappa;s).
\]

## Definition 2.1 — predictive equivalence

\[
h\equiv_{\mathrm{pred}}h'
\iff
\mathsf Q_h=\mathsf Q_{h'}.
\]

Let

\[
S_{\mathrm{pred}}
=
\mathcal H/\!\equiv_{\mathrm{pred}}
\]

with quotient map \(q_{\mathrm{pred}}\).

## Definition 2.2 — response-sufficient statistic

A deterministic statistic \(\phi:\mathcal H\to Z\) is response-sufficient if there exists

\[
G:Z\times\mathcal E\times\mathcal K\times\mathcal S_{\mathrm{free}}
\to\mathcal Y_\Omega
\]

such that

\[
G(\phi(h),e,\kappa,s)
=
\mathsf Q_h(e,\kappa,s)
\]

for every admitted argument.

## Theorem 2.3 — coarsest exact predictive statistic

Every deterministic response-sufficient statistic refines \(q_{\mathrm{pred}}\). Equivalently, on reachable codes there is a unique map \(r\) such that

\[
q_{\mathrm{pred}}=r\circ\phi.
\]

### Proof

If \(\phi(h)=\phi(h')\), response sufficiency gives

\[
\mathsf Q_h(e,\kappa,s)
=G(\phi(h),e,\kappa,s)
=G(\phi(h'),e,\kappa,s)
=\mathsf Q_{h'}(e,\kappa,s)
\]

for all \((e,\kappa,s)\). Hence \(h\equiv_{\mathrm{pred}}h'\). Therefore every fiber of \(\phi\) is contained in one predictive equivalence class, which defines \(r\). \(\square\)

## Corollary 2.4

Any two coarsest deterministic exact response-sufficient statistics are isomorphic on reachable states.

## Boundary 2.5

Theorem 2.3 concerns reconstruction of the complete declared response profile. It does not imply that every successful controller must retain every predictive distinction.

---

# 3. Control compatibility is not predictive equivalence

For tolerance \(\varepsilon\ge0\), define

\[
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
=
\{\kappa:
L_\Omega(h,\kappa;s)\le\varepsilon\}.
\]

A set \(B\subseteq\mathcal H\) is **plan-compatible** when

\[
\bigcap_{h\in B}
\Gamma^{\mathrm{plan}}_\varepsilon(h;s)
e\varnothing.
\]

The plan-conflict hypergraph has histories as vertices and the non-plan-compatible sets as hyperedges.

Compatibility need not be transitive. For example, feasible sets

\[
\Gamma(h_1)=\{a,b\},
\qquad
\Gamma(h_2)=\{b,c\},
\qquad
\Gamma(h_3)=\{a,c\}
\]

intersect pairwise while their triple intersection is empty. Hence arbitrary control obligations need not possess a canonical coarsest decision quotient.

The canonical object is the residual feasibility/conflict structure. A controller is one realization of that structure.

---

# 4. Three control-complexity quantities

Assume now a finite Markov residual specification \(V\) at tolerance \(\varepsilon\).

For residual state \(v\), let \(A_\varepsilon(v)\) be the currently admissible actions.

## Definition 4.1 — repeated current-action complexity

A block \(B\subseteq V\) is action-compatible when

\[
\bigcap_{v\in B}A_\varepsilon(v)\ne\varnothing.
\]

Let

\[
\chi_{\mathrm{act}}(\varepsilon)
\]

be the chromatic number of the immediate-action conflict hypergraph.

Operationally, this is the minimum number of messages required when an external encoder may inspect the true residual state again at every step and need only select the current action.

## Definition 4.2 — one-time rooted-plan complexity

Let

\[
\chi_{\mathrm{plan}}(\varepsilon;s)
\]

be the chromatic number of the plan-conflict hypergraph induced by \(\Gamma^{\mathrm{plan}}_\varepsilon\).

Operationally, this is the minimum number of labels required by a one-time root encoder that selects an arbitrary rooted strategy. The decoder-side memory needed to execute the selected strategy is not charged by the label count.

## Definition 4.3 — autonomous dynamic state complexity

Let

\[
N^*_{\mathrm{dyn}}(\varepsilon)
\]

be the minimum number of reachable states of a clock-free autonomous deterministic controller receiving only the declared observation stream and free side information after initialization.

For a finite incompletely specified residual machine, \(N^*_{\mathrm{dyn}}\) is the minimum cardinality of a closed compatible cover: cover members admit a common current output/action, and every implied successor set is contained in a cover member.

## Theorem 4.4 — control-complexity hierarchy

Under aligned residual, tolerance, observation, and side-information semantics,

\[
\boxed{
\chi_{\mathrm{act}}(\varepsilon)
\le
\chi_{\mathrm{plan}}(\varepsilon;s)
\le
N^*_{\mathrm{dyn}}(\varepsilon).
}
\]

### Proof

A common rooted plan has one first action; hence every plan-compatible block is action-compatible, proving the first inequality.

For the second, take any autonomous controller with \(N\) reachable states. For each controller state \(z\), collect all residual situations that can coexist with \(z\). Starting from \(z\), the controller induces one rooted strategy on future suffixes. Thus every such residual set is plan-compatible. These at most \(N\) sets cover all reachable residual situations. Plan compatibility is hereditary, so assigning each residual to one containing set gives a plan coloring with at most \(N\) colors. Minimize over controllers. \(\square\)

Both inequalities can be strict. The two finite witnesses and exhaustive checker are registered separately in `ROOTED_STRATEGY_COMPLEXITY_V2.md`, `control_complexity_hierarchy_checks_v1.py`, and `CONTROL_COMPLEXITY_HIERARCHY_RESULTS_V1.json`.

The distinction is structural: repeated external disclosure, one-time plan selection, and autonomous persistent state are different causal placements of information.

---

# 5. State and communication lower bounds

## 5.1 Predictive-complete memory

If

\[
|S_{\mathrm{pred}}|=N<\infty,
\]

any exact deterministic response-sufficient code has at least \(N\) codewords. A fixed-length binary code therefore requires

\[
\left\lceil\log_2N\right\rceil
\]

bits.

## 5.2 Approximate predictive memory

Let \(D\) be an extended pseudometric on \(\mathcal Y_\Omega\) and define

\[
d(h,h')
=
\sup_{e,\kappa,s}
D\!\left(
\mathsf Q_h(e,\kappa,s),
\mathsf Q_{h'}(e,\kappa,s)
\right).
\]

If \(P_{2\varepsilon}\) is the maximum cardinality of a set of histories pairwise more than \(2\varepsilon\) apart, then every deterministic representation reconstructing each response profile with worst-case \(D\)-error at most \(\varepsilon\) needs at least \(P_{2\varepsilon}\) codewords.

The statement uses the triangle inequality and therefore does not apply unchanged to a generic divergence such as KL.

## 5.3 Pathwise complete-cut theorem

Consider a complete causal cut carrying transcript \(Y\) from a root-history side to a downstream controller. All other downstream side information is explicitly included in \(s\).

Assume a pathwise contract: whenever transcript value \(y\) occurs with positive probability after history \(h\), the rooted strategy selected by \((y,s)\) must achieve loss at most \(\varepsilon\) from \(h\).

For every symbol \(y\), the set

\[
B_y=\{h:\Pr(Y=y\mid h)>0\}
\]

is plan-compatible. Hence, for finite transcript alphabet,

\[
\boxed{
|\mathcal Y|
\ge
\chi_{\mathrm{plan}}(\varepsilon;s).
}
\]

For a tuple of finite cut channels \(Y=(Y_1,\ldots,Y_m)\),

\[
\sum_i\log_2|\mathcal Y_i|
\ge
\log_2\chi_{\mathrm{plan}}(\varepsilon;s).
\]

This is a zero-error/worst-case statement. Average-error Shannon quantities require an additional source law or a different minimax formulation.

---

# 6. Prior-free decision order

Let \(\mathcal M_\theta\) be a declared feasible machine class under substrate parameter \(\theta\). For each machine, collect all registered obligation and resource coordinates into

\[
\Psi_\theta(M)
\in
\overline{\mathbb R}^{\Lambda}.
\]

The index set \(\Lambda\) may include environment, horizon, obligation coordinate, latency, memory, communication, energy, error, development cost, or other registered dimensions.

## Definition 6.1 — dominance

\[
N\preceq_\theta M
\iff
\Psi_\theta(N)_\lambda
\le
\Psi_\theta(M)_\lambda
\quad\forall\lambda\in\Lambda.
\]

Strict dominance, \(N\prec_\theta M\), additionally requires unequal profiles.

The prior-free frontier is

\[
\operatorname{Pareto}(\mathcal M_\theta)
=
\{M:\nexists N\text{ with }N\prec_\theta M\}.
\]

No probability distribution over \(\mathcal E\) is used.

## Proposition 6.2 — scalar selectors

If \(\Phi\) is strictly monotone for the declared coordinatewise order,

\[
x\le y,\quad x\ne y
\Longrightarrow
\Phi(x)<\Phi(y),
\]

then every minimizer of \(\Phi\circ\Psi_\theta\) is nondominated.

An expected-risk Bayes objective is one possible selector, but it need not be strictly monotone for pointwise dominance: a strict improvement confined to a prior-null environment is invisible to the integral.

## Proposition 6.3 — nonempty finite-dimensional frontier

If the registered performance image is nonempty, compact, and finite-dimensional, then a Pareto point exists. Minimize any strictly positive weighted sum of the coordinates.

Without compactness, well-foundedness, or an analogous existence condition, the nondominated set of an infinite feasible class may be empty.

---

# 7. Operational morphology and architecture non-leakage

Let \(\mathcal Q\) be a registered family of operational probes. It contains the behavioral and resource probes relevant to the claim and, when internal topology is itself claimed, the required physical cut/intervention probes.

## Definition 7.1 — operational equivalence

\[
M\simeq_{\mathcal Q}N
\iff
q(M)=q(N)
\quad\forall q\in\mathcal Q.
\]

The morphology class is

\[
\chi_{\mathcal Q}(M)=[M]_{\simeq_{\mathcal Q}}.
\]

A representation-invariant theory cannot identify an implementation label below this observational resolution.

## Definition 7.2 — architecture-neutral premise

A machine-dependent premise \(F\) is architecture-neutral at resolution \(\mathcal Q\) if it factors through the quotient:

\[
F=\bar F\circ\chi_{\mathcal Q}.
\]

Equivalently,

\[
M\simeq_{\mathcal Q}N
\Longrightarrow
F(M)=F(N).
\]

Resource measurements may intentionally distinguish physically different realizations; the measurement rule itself must nevertheless be operational rather than label-dependent.

This criterion blocks architecture priors hidden in feature vocabularies, cost definitions, or candidate grammars.

---

# 8. Necessity–construction sandwich

This section is the central morphology correction.

Let

\[
\mathfrak X^{\mathrm{phys}}_\theta
\]

be the unknown set of operational morphology classes actually realizable under physical/substrate condition \(\theta\).

A theory can usually access this set only from two sides.

## Definition 8.1 — necessary outer set

Let

\[
\mathfrak X^{\mathrm{nec}}_\theta
\]

be the set of morphology signatures satisfying every proved necessary constraint: semantic-state requirements, control compatibility, information-cut lower bounds, physical lower bounds, causal constraints, and any other theorem established for all admissible machines.

Sound necessity gives

\[
\boxed{
\mathfrak X^{\mathrm{phys}}_\theta
\subseteq
\mathfrak X^{\mathrm{nec}}_\theta.
}
\]

## Definition 8.2 — constructive inner set

Let

\[
\mathfrak X^{\mathrm{con}}_\theta
\]

be the set of morphology classes for which an explicit realization has been constructed and its declared resource profile verified under \(\theta\).

Sound construction gives

\[
\boxed{
\mathfrak X^{\mathrm{con}}_\theta
\subseteq
\mathfrak X^{\mathrm{phys}}_\theta.
}
\]

Therefore

\[
\boxed{
\mathfrak X^{\mathrm{con}}_\theta
\subseteq
\mathfrak X^{\mathrm{phys}}_\theta
\subseteq
\mathfrak X^{\mathrm{nec}}_\theta.
}
\]

Merely defining \(\mathfrak X^{\mathrm{phys}}_\theta\) does not derive it. Closure occurs when the inner and outer arguments meet at the claim of interest.

---

# 9. Frontier certification theorem

Let

\[
Y^{\mathrm{con}}_\theta
=
\Psi_\theta(\mathfrak X^{\mathrm{con}}_\theta),
\quad
Y^{\mathrm{phys}}_\theta
=
\Psi_\theta(\mathfrak X^{\mathrm{phys}}_\theta),
\quad
Y^{\mathrm{nec}}_\theta
=
\Psi_\theta(\mathfrak X^{\mathrm{nec}}_\theta).
\]

Then

\[
Y^{\mathrm{con}}_\theta
\subseteq
Y^{\mathrm{phys}}_\theta
\subseteq
Y^{\mathrm{nec}}_\theta.
\]

## Theorem 9.1 — Pareto-profile sandwich closure

Suppose there is a set \(F_\theta\subseteq Y^{\mathrm{con}}_\theta\) such that:

1. **antichain:** no two distinct profiles in \(F_\theta\) strictly dominate one another;
2. **outer domination:** for every \(y\in Y^{\mathrm{nec}}_\theta\), there exists \(f\in F_\theta\) with
   \[
   f\le y.
   \]

Then

\[
\boxed{
\operatorname{Pareto}(Y^{\mathrm{phys}}_\theta)
=F_\theta
}
\]

up to equality of objective profiles.

### Proof

Because \(F_\theta\subseteq Y^{\mathrm{con}}_\theta\subseteq Y^{\mathrm{phys}}_\theta\), every profile in \(F_\theta\) is physically achievable.

Assume \(f\in F_\theta\) is strictly dominated by some \(y\in Y^{\mathrm{phys}}_\theta\). Since \(y\in Y^{\mathrm{nec}}_\theta\), outer domination gives \(f'\in F_\theta\) with \(f'\le y<f\), contradicting the antichain condition. Hence every \(f\in F_\theta\) is physically Pareto-optimal.

Conversely, let \(y\in Y^{\mathrm{phys}}_\theta\) be Pareto-optimal. Outer domination supplies \(f\in F_\theta\) with \(f\le y\). Since \(f\) is physically achievable, physical Pareto optimality of \(y\) forces equality of profiles. \(\square\)

### Interpretation

A physical Pareto frontier can be proved without enumerating all physical machines. It is enough to:

1. derive lower/necessity bounds broad enough to contain every possible realization;
2. build machines that attain a candidate antichain;
3. prove that the candidate antichain dominates the entire necessary outer region.

This is the formal version of “attack from both sides until they meet”.

---

# 10. Morphology identification requires a second theorem

Optimal performance does not identify architecture.

For frontier profile \(f\), define the necessary fiber

\[
\mathcal Z^{\mathrm{nec}}_\theta(f)
=
\{x\in\mathfrak X^{\mathrm{nec}}_\theta:
\Psi_\theta(x)=f\}.
\]

## Definition 10.1 — morphology identifiability at probe resolution

A frontier profile \(f\) identifies morphology class \(C_f\) when

\[
\mathcal Z^{\mathrm{phys}}_\theta(f)
\subseteq C_f
\]

at the declared operational resolution.

A sufficient proof is the stronger outer statement

\[
\mathcal Z^{\mathrm{nec}}_\theta(f)
\subseteq C_f.
\]

If this fiber contains several operationally distinct classes, the correct theoretical answer is a morphology tie/phase coexistence region.

Thus the full derivation has two logically separate parts:

\[
\text{frontier-profile closure}
\quad+
\text{frontier-fiber identification}.
\]

Exact architecture syntax below \(\mathcal Q\)-resolution is not identifiable and should not be claimed.

---

# 11. Resource-conditioned phase law

For each \(\theta\), derive the outer and constructive sets

\[
\mathfrak X^{\mathrm{nec}}_\theta,
\qquad
\mathfrak X^{\mathrm{con}}_\theta.
\]

A **certified phase region** \(R\subseteq\Theta\) is a parameter region for which the hypotheses of Theorem 9.1 hold with a fixed combinatorial/frontier form, together with whatever fiber-identification result is claimed.

The phase law is therefore not merely the definition

\[
\theta\mapsto\operatorname{Pareto}(\mathfrak X^{\mathrm{phys}}_\theta).
\]

It is a collection of proved certificates

\[
\boxed{
\theta\in R_i
\Longrightarrow
\operatorname{Pareto}
\bigl(Y^{\mathrm{phys}}_\theta\bigr)
=F_i(\theta),
}
\]

plus morphology-fiber statements where available.

Exact empirical hardware constants need not be predicted by the theory. They locate a real system in the certified conditional diagram.

---

# 12. Architecture-independent channel law as an example

Consider one stochastic environment with a uniformly located target among \(L\) positions and an independent fair hidden bit. Suppose a primary channel resolves the target bit on an event \(H\) with

\[
\Pr(H)\le r/L,
\]

and on \(H^c\) the machine's entire view is conditionally independent of the bit. Then

\[
\operatorname{Acc}
\le
\frac12+\frac{r}{2L}.
\]

If a secondary rescue channel succeeds on a primary miss with conditional probability at most \(p\), and the residual view after both channels fail is still independent of the bit, then

\[
\operatorname{Acc}
\le
1-
\frac{(1-r/L)(1-p)}2.
\]

These laws follow by conditioning on which information channel resolves the hidden variable. No architecture family appears. The stochastic law is internal to one environment; it is not a prior over \(\mathcal E\).

The complete derivation and failure conditions are registered in `CHANNEL_LAW_RECOVERY_V1.md`.

---

# 13. Developmental reachability

Let \(D\) be a development/search process and \(B\) a budget.

For a countable morphology space define

\[
\mathcal R_B
=
\{x:\Pr_D(\exists t\le B:X_t=x)>0\}.
\]

For a topological morphology space use support reachability

\[
\mathcal R_B
=
\overline{
\bigcup_{t\le B}
\operatorname{supp}(\nu_t)
}.
\]

Two objects must be separated:

\[
\mathcal G_B
=
\mathcal F_X\cap\mathcal R_B
\]

is the subset of globally optimal morphologies that happen to be reachable, while

\[
\mathcal F_B
=
\operatorname{Pareto}
(\mathfrak X^{\mathrm{phys}}_\theta\cap\mathcal R_B)
\]

is the frontier among reachable morphologies. They need not coincide; \(\mathcal G_B\) can be empty while \(\mathcal F_B\) is nonempty.

## Developmental non-leakage

A development process defined on implementation syntax can reintroduce an architecture prior. Let

\[
q_{\mathcal Q}:\mathcal M\to\mathfrak X
\]

be the operational quotient. An implementation-level kernel \(D\) is quotient-compatible when

\[
M\simeq_{\mathcal Q}N
\Longrightarrow
(q_{\mathcal Q})_\#D(\cdot\mid M)
=
(q_{\mathcal Q})_\#D(\cdot\mid N).
\]

Only then does it induce a representation-independent morphology process.

If this condition fails, reachability is search-prior-sensitive. The result may still be valid for that search process, but it is not a zero-architecture-prior developmental theorem.

Universal-program search does not remove this issue: the choice of coding/reference universal machine can materially affect interactive universal-agent behavior. Reference-machine dependence must be exposed as a parameter or eliminated by an invariance theorem.

---

# 14. Effective behavioral realization

A finite or countable causal transducer is **effectively samplable** when an algorithm can sample each next-state/output kernel to arbitrary total-variation precision, uniformly over admitted current states and inputs. Finite branching with uniformly computable transition probabilities is a sufficient special case.

## Proposition 14.1 — finite-horizon universal simulation

Every effectively samplable transducer can be simulated by a universal probabilistic digital machine such that, for every finite horizon \(T\) and \(\delta>0\), the induced external trajectory law is within total-variation distance \(\delta\) of the target law.

### Proof sketch

At step \(t<T\), sample the transition kernel to error \(\varepsilon_t\) with

\[
\sum_{t<T}\varepsilon_t\le\delta.
\]

Couple the target and approximate transition at each step. The probability of any mismatch by time \(T\) is at most the sum of one-step mismatch probabilities, so the trajectory-law total-variation distance is at most \(\delta\). \(\square\)

## Boundary 14.2

Behavioral simulation says nothing about resource equivalence. A universal simulator may incur arbitrary time, memory, communication, precision, or energy overhead. Resource-conditioned morphology requires the sandwich argument of Sections 8–11, not universality alone.

---

# 15. Representation coverage of known machine forms

Every implemented classical causal interactive architecture has a complete physical configuration, a causal input/output rule, and an update procedure. Taking the complete retained configuration as raw state yields a causal transducer. Quotienting by \(\simeq_{\mathcal Q}\) gives an operational morphology class.

This establishes **representation coverage** for the declared classical causal domain. It is deliberately weak: it does not show that the architecture was predicted from \((\Omega,\mathcal E,\theta)\).

The frozen architecture-neutral chart in `REDUCTION_VOCABULARY_V1.md` records persistence, access geometry, update geometry, routing topology, counterfactual structure, composition boundaries, resource response, and approximation contract. `KNOWN_FORM_REDUCTION_V1.md` maps the surveyed architecture families into that chart after the vocabulary was frozen.

Genuinely quantum external interfaces remain outside the classical interaction semantics and require a quantum-instrument extension.

---

# 16. Coverage, recovery, closure, prediction

These terms are reserved as follows.

## 16.1 Coverage

A known architecture \(K\) can be represented in the operational language:

\[
\chi_{\mathcal Q}(K)\in\mathfrak X.
\]

## 16.2 Recovery

The ecology, resource model, probe vocabulary, and reduction protocol are frozen without using the held-out architecture label. A derived region \(R\) is then tested against the held-out realization:

\[
\chi_{\mathcal Q}(K)\in R.
\]

Recovery is retrospective unless the hold-out and derivation were preregistered.

## 16.3 Frontier closure

A necessity–construction sandwich satisfies Theorem 9.1 over a declared parameter region. This closes the optimal **performance/resource profile** there.

## 16.4 Morphology closure

Frontier closure is supplemented by a fiber-identification theorem at resolution \(\mathcal Q\).

## 16.5 Prospective prediction

A nonempty morphology region is derived and frozen before any inhabitant is known, followed by independent construction or discovery of an inhabitant.

Only this final standard directly tests whether the theory predicts a previously unknown form rather than redescribing known forms.

---

# 17. Minimal declaration basis

No nontrivial intelligence theorem follows from literal absence of premises. For the present target the declarations can be reduced to the following classes.

## D0. Causal interaction domain

Defines histories, rooted continuations, intervention timing, free side information, and the system boundary.

Without D0 the continuation and cut statements are undefined; allowing acausal future access invalidates causal information lower bounds.

## D1. Obligation \(\Omega\)

Defines which outcomes and distinctions matter. Two otherwise identical worlds can demand opposite terminal actions under different obligations, so no nontrivial action ordering is derivable without D1 or an equivalent preference/safety constraint.

## D2. Ecology \(\mathcal E\)

Defines the environments over which the claim is quantified. Opposing environments can agree on the entire past and require different next actions; deleting the ecology restriction removes the discriminator required by any nontrivial robust control theorem.

## D3. Physical/resource model \((\Theta,\rho)\)

Defines which physical differences distinguish behaviorally equivalent realizations. Without it, memory/recomputation, communication/locality, energy/latency, and analogous morphology trades have no ordering.

## D4. Operational resolution \(\mathcal Q\)

Defines which implementation distinctions are observable and scientifically claimed. Without it, “same morphology” and architecture-label invariance are undefined.

## D5. Development process \((D,B)\), only for developmental claims

Static feasibility and morphology optimality do not imply discoverability. Developmental reachability needs a search/update process and budget. D5 itself can carry representation bias and therefore requires the quotient-compatibility test when an architecture-neutral developmental claim is made.

Probability calculus, a Bayesian prior over environments, neural units, symbolic rules, attention, gradient descent, program search, and any named architecture family are absent from this declaration basis.

---

# 18. Main theorem package

Within the declared domain:

1. **Predictive residual theorem.** The rooted response functional induces a canonical coarsest deterministic exact predictive statistic.
2. **Control non-quotient result.** General exact/approximate control compatibility need not be transitive; a unique coarsest control quotient is not guaranteed.
3. **Control-complexity hierarchy.** For finite residual systems,
   \[
   \chi_{\mathrm{act}}
   \le
   \chi_{\mathrm{plan}}
   \le
   N^*_{\mathrm{dyn}},
   \]
   and both inequalities can be strict.
4. **Cut theorem.** A pathwise complete cut selecting rooted plans needs at least \(\chi_{\mathrm{plan}}\) transcript symbols.
5. **Prior-free order.** Coordinatewise ecology/resource dominance and its Pareto set require no measure over \(\mathcal E\).
6. **Scalarization boundary.** A scalar selector preserves nondominance only under the appropriate monotonicity/support assumptions.
7. **Architecture non-identifiability.** Implementation labels below the registered operational resolution cannot be derived from invariant premises.
8. **Necessity–construction sandwich.** Verified constructions lie inside the unknown physical set, which lies inside the proved necessary outer set.
9. **Pareto-profile closure theorem.** A constructive antichain that dominates the entire necessary outer profile region equals the true physical Pareto-profile frontier.
10. **Morphology-identification requirement.** Closing the optimal profile does not identify implementation morphology without a separate frontier-fiber theorem.
11. **Developmental boundary.** Best-reachable and reachable-global frontiers are distinct, and representation-sensitive search laws are not architecture-neutral.
12. **Behavioral realization.** Effectively samplable causal transducers admit arbitrary-precision finite-horizon universal simulation, with no resource-equivalence implication.
13. **Representation coverage.** Every implemented classical causal interactive architecture maps into the transducer/operational-morphology language; this is coverage, not recovery.

The architecture-neutral derivation skeleton is therefore

\[
(\mathfrak D,\Omega,\mathcal E,\mathfrak B)
\Longrightarrow
\begin{cases}
S_{\mathrm{pred}},\\
\mathfrak C^{\mathrm{act}},\\
\mathfrak C^{\mathrm{plan}},
\end{cases}
\Longrightarrow
\text{state/channel necessity bounds},
\]

followed by

\[
(\Theta,\rho,\mathcal Q)
\Longrightarrow
\mathfrak X^{\mathrm{con}}_\theta
\subseteq
\mathfrak X^{\mathrm{phys}}_\theta
\subseteq
\mathfrak X^{\mathrm{nec}}_\theta.
\]

A morphology phase is closed when necessity and construction meet under Theorem 9.1 and the required frontier-fiber statement.

That is the mathematically defensible version of the proposed bidirectional vise.

---

# 19. Present closure ledger

| Target | Status | Reason |
|---|---|---|
| Probability measure over ecology | **eliminated from core** | pointwise/minimax/robust statements do not require one |
| Exact predictive residual | **theorem** | Theorem 2.3 |
| Generic unique control atom | **refuted** | compatibility is not transitive |
| Current-action information bound | **theorem in finite residual model** | conflict coloring |
| Rooted-plan information bound | **theorem in finite/pathwise model** | plan conflict coloring and cut theorem |
| Autonomous finite controller minimum | **closed-cover theorem in finite residual model** | donor-aligned FSM result |
| Architecture-independent channel laws | **conditional theorem** | exact assumptions registered separately |
| Prior-free Pareto order | **definition + conditional existence theorem** | no ecology measure required |
| Resource phase law in general | **open** | must derive outer bounds and constructions; definition alone is insufficient |
| All-known-form representation coverage | **closed for classical causal implementations** | raw causal-transducer construction |
| All-known-form top-down recovery | **open** | frozen held-out recovery not yet performed |
| Developmental prior-freedom | **conditional/open** | search kernel must descend to quotient or be coding-robust |
| Prospective unknown morphology | **open** | no preregistered unoccupied region has yet been independently realized |
| Genuinely quantum external interface | **open domain extension** | classical stochastic interface is insufficient |

The formal core is therefore substantially closed as a *framework of necessity, construction, and certification*. The scientific claim requested by full GMI—derivation and prospective prediction of machine morphology across ecologies—is not yet closed.

---

# 20. References and donor boundary

The following results are treated as donors rather than relabeled as GMI novelty.

- D. Blackwell (1951), “Comparison of Experiments,” *Proceedings of the Second Berkeley Symposium on Mathematical Statistics and Probability*, 93–102. Comparison of information structures by attainable decision performance.
- H. S. Witsenhausen (1976), “The zero-error side information problem and chromatic numbers,” *IEEE Transactions on Information Theory* 22(5):592–593, DOI 10.1109/TIT.1976.1055607. Zero-error communication and graph coloring.
- M. L. Littman, R. S. Sutton, S. Singh (2001), “Predictive Representations of State,” *NeurIPS 2001*, 1555–1561. Action-conditional predictive representations.
- J. P. Crutchfield, K. Young (1989), “Inferring Statistical Complexity,” *Physical Review Letters* 63:105, DOI 10.1103/PhysRevLett.63.105. Predictive structure/statistical complexity; used here only as historical neighboring work, not as authority for the present proofs.
- R. Puri, J. Gu (1993), “An efficient algorithm to search for minimal closed covers in sequential machines,” *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems* 12(6):737–745, DOI 10.1109/43.229748.
- I. Ahmad, A. Shoba Das (2001), “A heuristic algorithm for the minimization of incompletely specified finite state machines,” *Computers & Electrical Engineering* 27(2):159–172, DOI 10.1016/S0045-7906(00)00016-1.
- D. H. Wolpert, W. G. Macready (1997), “No Free Lunch Theorems for Optimization,” *IEEE Transactions on Evolutionary Computation* 1(1):67–82, DOI 10.1109/4235.585893.
- N. Tishby, F. C. Pereira, W. Bialek (1999), “The Information Bottleneck Method,” *37th Allerton Conference*, 368–377. Distribution-conditioned compression/relevance tradeoffs; not required by the worst-case core.
- P. A. Ortega, D. A. Braun (2013), “Thermodynamics as a theory of decision-making with information-processing costs,” *Proceedings of the Royal Society A* 469:20120683, DOI 10.1098/rspa.2012.0683.
- J. Leike, M. Hutter (2015), “Bad Universal Priors and Notions of Optimality,” *Proceedings of Machine Learning Research* 40:1244–1259. Reference-machine sensitivity of interactive universal-agent claims.

The candidate GMI contribution is not any one donor theorem. It is the attempted closure of the chain

\[
\text{obligation/ecology residuals}
\to
\text{control information}
\to
\text{causal cut bounds}
\to
\text{resource-conditioned outer constraints}
\leftrightarrow
\text{explicit constructions}
\to
\text{certified morphology phases}
\to
\text{prospective machine-form prediction}.
\]

Every arrow must carry its own necessity, construction, and evidence status.
