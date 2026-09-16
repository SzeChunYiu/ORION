# Prior-free GMI: formal core v1

## Status and scope

This note isolates the representation-invariant part of a general machine-intelligence theory. It does **not** claim that a named implementation (Transformer, recurrent network, symbolic prover, Bayesian agent, etc.) is uniquely derivable from logic. The target is narrower and stronger: derive the canonical obligation-relevant state, prior-free decision order, information constraints, and resource-conditioned morphology classes without placing a probability measure over admissible environments or inserting an architecture family into the premises.

The basic domain is a class of causal, computable, interactive machines with finite or countable alphabets. Standard measurable-space extensions can replace sums by stochastic kernels and regular conditional laws; no theorem below relies on a neural or symbolic representation.

The note separates four questions that must not be conflated:

1. **semantic minimality** — what distinctions must an exact machine preserve?;
2. **decision admissibility** — which behaviours are undominated without a prior over environments?;
3. **physical morphology** — which realizations lie on the resource frontier on a declared substrate?;
4. **developmental reachability** — which frontier points can the declared development process actually reach within budget?

A result at one layer is not, by itself, a result at the next.

---

## 1. Interactive setting

Let \(\mathcal A\) be an action alphabet and \(\mathcal O\) an observation alphabet. A finite interaction history is

\[
h_t=(o_0,a_0,o_1,a_1,\ldots,o_t)\in\mathcal H_t,
\qquad
\mathcal H=\bigcup_{t\ge 0}\mathcal H_t.
\]

An **environment** \(e\) is a causal family of stochastic kernels

\[
e_t(o_{t+1}\mid h_t,a_t).
\]

The theory does not assign a probability distribution to environments. It receives only a declared nonempty admissible ecology

\[
\mathcal E\subseteq \{\text{causal environments}\}.
\]

A **machine** \(M\) is a causal interactive transducer. At the behavioural level it induces an action kernel

\[
\pi_M(a_t\mid h_t),
\]

possibly through internal state, learned parameters, external memory, tools, other agents, or any combination thereof.

### 1.1 Obligation

A cognitive obligation \(\Omega\) is a family of trajectory-level tests or losses

\[
\Omega=\{\ell_j:j\in J\}.
\]

For finite horizon \(T\), environment \(e\), and machine \(M\), write

\[
R^{j}_{T}(M,e)=\mathbb E_{M,e}[\ell_{j,T}(H_T)]
\]

whenever the expectation exists. For non-numeric obligations the same construction may be stated with a preorder on outcome laws; the vector-loss form is used here because it makes dominance explicit.

The obligation is external to the machine. Without \(\Omega\), there is no theory-internal fact that one action or outcome is cognitively better than another.

### 1.2 Resources

Let \(\theta\in\Theta\) denote physical/substrate parameters. A resource evaluator returns a vector

\[
\rho_\theta(M,e,T)\in\mathbb R^k_{\ge 0},
\]

whose coordinates may include time, memory, communication, energy, error probability, fabrication cost, sample use, or other declared quantities. No scalarization is assumed.

A developmental/search budget is denoted \(B\); when useful it is treated as one coordinate of the resource specification.

---

## 2. Prior-free decision order

### Definition 2.1 (uniform dominance)

For machines \(M,N\), write \(N\preceq_{\Omega,\mathcal E,\theta} M\) when, for every admissible environment, every declared obligation coordinate, and every declared horizon,

\[
R_T^j(N,e)\le R_T^j(M,e),
\]

and the declared resource coordinates are also no worse:

\[
\rho_\theta(N,e,T)\le_{\mathrm{cw}} \rho_\theta(M,e,T).
\]

Write \(N\prec M\) when \(N\preceq M\) and at least one inequality is strict.

### Definition 2.2 (prior-free frontier)

For a feasible machine class \(\mathcal M\),

\[
\mathcal F(\Omega,\mathcal E,\theta)
=
\{M\in\mathcal M:\nexists N\in\mathcal M\text{ with }N\prec M\}.
\]

This frontier is defined without a prior over \(\mathcal E\).

### Proposition 2.3 (scalarization cannot select a dominated point)

Let \(w\) be strictly positive weights on all obligation/resource coordinates and let \(\mu\) be any probability measure on \(\mathcal E\). If \(M^*\) minimizes the corresponding finite scalarized risk and resource objective, then \(M^*\) is not uniformly dominated.

#### Proof

If \(N\prec M^*\), every scalarized coordinate of \(N\) is no larger for every \(e\), and at least one is strictly smaller. Strictly positive weighting and integration preserve that strict improvement, contradicting optimality of \(M^*\). \(\square\)

The converse requires additional geometry. If the attainable upper image is closed and convex, supported Pareto points are minimizers of positive linear scalarizations by the separating-hyperplane theorem. In nonconvex feasible sets, unsupported nondominated points may exist. Therefore the prior-free frontier is the primary object; Bayesian or utility scalarizations are selectors, not foundations.

### Counterexample 2.4 (intersection of Bayes optima is not the frontier)

Consider two environments \(e_0,e_1\) and two deterministic first actions \(a_0,a_1\) with losses

\[
\ell(a_i,e_j)=\mathbf 1[i\ne j].
\]

A prior concentrated on \(e_0\) selects \(a_0\); a prior concentrated on \(e_1\) selects \(a_1\). Hence

\[
\bigcap_{\pi}\operatorname{Opt}(\pi)=\varnothing,
\]

although neither action uniformly dominates the other. The intersection across priors is therefore only a **prior-invariant core**, not the general zero-prior solution.

---

## 3. Canonical obligation-relevant state

The central object is a quotient of histories, not a neuron, token, rule, parameter tensor, or program instruction.

Let \(\mathcal C\) be a declared class of admissible future intervention programmes. A continuation programme \(c\in\mathcal C\) specifies future actions causally from future observations. For history \(h\), environment \(e\), and continuation \(c\), let

\[
K^{\Omega}_{e}(\cdot\mid h,c)
\]

denote the conditional law of all future observables on which \(\Omega\) depends.

### Definition 3.1 (future-obligation equivalence)

For histories \(h,h'\in\mathcal H\),

\[
h\equiv_{\Omega,\mathcal E,\mathcal C} h'
\]

iff

\[
\forall e\in\mathcal E,\ \forall c\in\mathcal C:
K^{\Omega}_{e}(\cdot\mid h,c)
=
K^{\Omega}_{e}(\cdot\mid h',c).
\]

Let

\[
S^*_{\Omega,\mathcal E,\mathcal C}
=
\mathcal H/\!\equiv_{\Omega,\mathcal E,\mathcal C}
\]

and let \(q^*: \mathcal H\to S^*\) be the quotient map.

### Definition 3.2 (exact obligation-sufficient representation)

A representation \(\phi:\mathcal H\to Z\) is exact obligation-sufficient when there exists a kernel \(G\) such that for all \(h,e,c\),

\[
K^{\Omega}_{e}(\cdot\mid h,c)
=
G(\cdot\mid \phi(h),e,c).
\]

### Theorem 3.3 (coarsest exact sufficient state)

The quotient \(q^*\) is exact obligation-sufficient. Moreover every exact obligation-sufficient representation \(\phi\) refines \(q^*\):

\[
\phi(h)=\phi(h')
\Longrightarrow
q^*(h)=q^*(h').
\]

Equivalently, there exists a map \(r: \phi(\mathcal H)\to S^*\) such that

\[
q^*=r\circ\phi.
\]

#### Proof

Sufficiency of \(q^*\) follows from Definition 3.1: all members of one equivalence class have identical future obligation laws under every admitted environment and continuation, so the common law is well-defined as a function of the class.

For minimality, suppose \(\phi(h)=\phi(h')\) but \(q^*(h)\ne q^*(h')\). By inequivalence there exist \(e\in\mathcal E\) and \(c\in\mathcal C\) for which the two future obligation laws differ. Exact sufficiency of \(\phi\) would require both laws to equal the same kernel value \(G(\cdot\mid\phi(h),e,c)\), a contradiction. Hence equal \(\phi\)-states imply equal quotient states. The factor map \(r\) is therefore well-defined. \(\square\)

### Corollary 3.4 (uniqueness up to relabeling)

Any two coarsest exact obligation-sufficient representations are isomorphic by a bijection on reachable states.

This is the appropriate representation-independent sense in which a canonical cognitive state exists.

---

## 4. Prior-free memory lower bounds

### Corollary 4.1 (exact finite-state lower bound)

If \(|S^*|=N<\infty\), every exact obligation-sufficient finite representation \(Z\) satisfies

\[
|Z|\ge N.
\]

Thus any binary encoding requires at least

\[
\lceil\log_2 N\rceil
\]

bits in the worst case.

#### Proof

Theorem 3.3 gives a surjection from reachable \(\phi\)-states onto \(S^*\). Therefore the former cannot contain fewer elements. \(\square\)

No visitation distribution and no environment prior is used.

### Definition 4.2 (task-relative discrepancy)

Choose a discrepancy \(D\) on future obligation laws. Define

\[
d_\Omega(h,h')
=
\sup_{e\in\mathcal E,\ c\in\mathcal C}
D\!\left(
K^{\Omega}_{e}(\cdot\mid h,c),
K^{\Omega}_{e}(\cdot\mid h',c)
\right).
\]

This is generally a pseudometric.

### Proposition 4.3 (worst-case approximate state lower bound)

Let \(P_{2\varepsilon}\) be the maximum cardinality of a set of histories with pairwise \(d_\Omega\)-distance greater than \(2\varepsilon\). Any representation whose reconstruction has worst-case discrepancy at most \(\varepsilon\) needs at least \(P_{2\varepsilon}\) distinct code states.

#### Proof

If two members of a \(2\varepsilon\)-packing share one code state, any single reconstructed future law assigned to that code is within distance \(\varepsilon\) of both, contradicting the triangle inequality and pairwise separation greater than \(2\varepsilon\). \(\square\)

Average-case rate-distortion or information-bottleneck statements may be added after a source/visitation law is supplied; they are not required for this worst-case result.

---

## 5. Information-channel necessity

A machine may distribute its state over recurrent variables, attention caches, external memory, retrieved documents, tools, other agents, or physical degrees of freedom. The invariant question is which obligation-relevant distinctions cross which causal cuts.

### Definition 5.1 (distinguishability demand across a cut)

Fix a causal cut \(C\) separating an upstream history fragment from a downstream decision. Let \(H_C=\{h_1,\ldots,h_N\}\) be histories such that the downstream obligation requires different continuation behaviour for every pair under at least one admitted environment.

### Theorem 5.2 (exact cut-capacity lower bound)

Suppose every signal crossing \(C\) takes values in a finite set \(Y\). If an exact solution must distinguish all \(N\) members of \(H_C\), then

\[
|Y|\ge N.
\]

Equivalently the cut must transmit at least \(\lceil\log_2 N\rceil\) bits of worst-case distinguishability.

#### Proof

If \(|Y|<N\), the pigeonhole principle maps two obligation-distinct upstream cases to the same downstream signal. Downstream computation then receives identical cut information in those two cases and cannot be forced to take two distinct required continuations solely from information unavailable across the cut. Exact satisfaction in both cases is impossible. \(\square\)

Approximate stochastic bounds require an explicit error criterion and, if average rather than worst-case error is used, an explicit distribution. The exact cut theorem is genuinely prior-free.

---

## 6. Architecture-free operational morphology

The earlier decomposition into separate proposal, update, and morphology-change operators is not invariant: an operation described as a parameter update in one representation can be described as an ordinary state transition in another, and the distinction changes with the chosen timescale.

### Definition 6.1 (operational signature)

For a machine \(M\), define

\[
\chi_\Omega(M)
=
\bigl[
(S_M,q_M),
\mathcal I_M,
\mathcal T_M,
\mathcal D_M,
\rho_M
\bigr]_G.
\]

The components are:

- \((S_M,q_M)\): reachable operational state together with its map from interaction history;
- \(\mathcal I_M\): causal information-channel graph, including internal, external-memory, tool, and communication channels;
- \(\mathcal T_M\): within-timescale causal transition/action kernel;
- \(\mathcal D_M\): a slower developmental/self-modification transition, **only after** the timescale boundary is explicitly declared;
- \(\rho_M\): resource-response vector as a function of substrate parameters;
- \(G\): the admitted gauge group (state relabelings, invertible coordinates, semantics-preserving compilation, and other explicitly declared representation changes).

The quotient by \(G\) is essential. Syntax is not morphology unless syntax changes behaviour, channel structure, reachability, or resource response in the declared theory.

### Definition 6.2 (behavioural equivalence)

Machines \(M,N\) are obligation-behaviourally equivalent when they induce the same obligation-relevant trajectory laws for every \(e\in\mathcal E\) and every allowed intervention.

Resource equivalence is a separate relation. Two machines may be behaviourally equivalent yet occupy different physical frontier points.

### Theorem 6.3 (architecture-label non-identifiability)

Let \(T\) be any theory invariant under the declared gauge relation \(G\). If

\[
\chi_\Omega(M)=\chi_\Omega(N),
\]

then \(T\) cannot derive a proposition that distinguishes \(M\) from \(N\) solely by an implementation label not encoded in \(\chi_\Omega\).

#### Proof

Gauge invariance means that all premises and admissible transformations assign identical theoretical content to equal equivalence classes. A conclusion separating two members of one class would therefore not be invariant under the same relation and could not follow from invariant premises alone. \(\square\)

Consequently a prior-free, representation-invariant GMI can identify an operational morphology class or resource phase without identifying a privileged architecture name.

---

## 7. Computable realization: what sufficiency does and does not mean

### Definition 7.1 (effective abstract transducer)

An abstract operational system is effective when its state set is finitely describable or recursively enumerable and its causal transition/output probabilities are computable to arbitrary rational precision.

### Proposition 7.2 (behavioural realization)

Every effective abstract transducer has a realization on a universal probabilistic computing substrate (equivalently a deterministic universal machine supplied with random bits), reproducing its finite-horizon output law to arbitrary prescribed precision.

#### Proof sketch

Encode state, input, and a rational approximation routine for each computable transition probability. A universal interpreter computes the required cumulative distribution to sufficient precision and samples it using random bits. Increasing numerical precision makes the finite-horizon induced law arbitrarily close in total variation. Deterministic transducers are the zero-randomness special case. \(\square\)

### Boundary 7.3

Proposition 7.2 is **behavioural sufficiency**, not an exact physical-resource theorem. Universal simulation can add time, memory, communication, and energy overhead. Therefore a substrate-specific morphology frontier must be computed over the realizations actually admitted by \(\theta\); it cannot be obtained from behavioural universality alone.

This distinction blocks the common but invalid inference

\[
\text{universal computability}
\not\Rightarrow
\text{resource-equivalent morphology}.
\]

---

## 8. Resource-conditioned morphology frontier

Let \(\mathfrak X_\theta\) be the set of operational signatures physically realizable on substrate condition \(\theta\). Let \(R_x(e)\) denote the obligation-risk vector of signature \(x\).

### Definition 8.1

\[
\mathcal F_X(\Omega,\mathcal E,\theta)
=
\operatorname{Nondominated}
\left\{
(R_x(\cdot),\rho_x(\theta)):x\in\mathfrak X_\theta
\right\}.
\]

This is the principal morphology object.

The theory may be complete as a conditional phase law

\[
\theta\mapsto\mathcal F_X(\Omega,\mathcal E,\theta)
\]

without predicting the empirical numerical value of \(\theta\). Measurement locates a physical system in the derived phase diagram; it need not be promoted to an axiom of computation.

### Definition 8.2 (identifiable morphology region)

A parameter region \(R\subseteq\Theta\) is morphology-identifiable at quotient level \(G\) when

\[
\forall\theta\in R:
\left|\mathcal F_X(\Omega,\mathcal E,\theta)/G\right|=1.
\]

When the quotient frontier contains multiple incomparable classes, exact morphology identity is not identified by the declared premises.

---

## 9. Developmental reachability

Let \(\mathcal D\) be a declared stochastic or deterministic process on morphology classes, initialized at \(x_0\). Define the budget-\(B\) reachable set

\[
\mathcal R_B(x_0,\mathcal D)
=
\{x:\Pr_\mathcal D(x\text{ is reached by budget }B)>0\}.
\]

### Definition 9.1 (developmentally admissible frontier)

\[
\mathcal F_B
=
\mathcal F_X
\cap
\mathcal R_B(x_0,\mathcal D).
\]

For stochastic development, define the first hitting time

\[
\tau_{\mathcal F}
=
\inf\{t:\chi(M_t)\in\mathcal F_X\}.
\]

Then

\[
\Pr_\mathcal D(\tau_{\mathcal F}\le B)
\]

is a property of the developmental process. It is not a prior over environments.

An optimal but unreachable morphology is not a developmental prediction.

---

## 10. Prior-free learning criterion

A learning theorem should not quietly reintroduce a distribution over worlds. For a comparator class \(\mathcal K\), define worst-case regret

\[
\operatorname{Reg}_T(A;\mathcal E,\mathcal K)
=
\sup_{e_{1:T}\in\mathcal E^T}
\left[
L_T(A,e_{1:T})
-
\inf_{K\in\mathcal K}L_T(K,e_{1:T})
\right].
\]

A prior-free learnability statement can take the form

\[
\operatorname{Reg}_T=o(T)
\]

or a finite-budget minimax bound.

This criterion determines a feasibility/rate envelope. It does not generally identify a unique update algorithm. A unique learning law requires additional assumptions that distinguish implementations or update geometry.

---

## 11. Minimal primitive basis and deletion tests

The object theory requires fewer primitives than a Bayesian-architecture formulation.

### P0. Causal interaction structure \(C\)

Histories, interventions, and non-anticipating composition are defined.

**Deletion test.** If future information may be read acausally, an oracle machine can violate causal cut lower bounds. Therefore the channel theorems require a causal/non-anticipating premise.

### P1. Cognitive obligation \(\Omega\)

Specifies which outcome distinctions count as success, error, or cost.

**Deletion test.** Hold all physical and environmental structure fixed and define two obligations that require opposite terminal actions. The remaining premises are identical while the preferred behaviour reverses. No nontrivial action ordering follows without an obligation or equivalent preference structure.

### P2. Admissible ecology \(\mathcal E\)

Specifies which environments the claim ranges over.

**Deletion test.** Two environments can agree on all past data and require opposite next actions. Any theorem selecting one action therefore depends on excluding one world, weakening the quantifier, or adding a decision criterion. An unrestricted environment class cannot support a universal pointwise-dominant learner.

### P3. Resource/substrate specification \(P=(\Theta,B)\)

Specifies which physical costs and developmental limits distinguish implementations.

**Deletion test.** Behaviourally equivalent implementations can exchange memory for recomputation or communication for local storage. With no resource order they are equivalent at the behavioural layer, so no physical morphology preference is derivable.

### P4. Gauge/extensionality specification \(G\)

Specifies which representation changes are scientifically immaterial.

**Deletion test.** For any machine state code \(s\), apply an arbitrary bijection \(f(s)\). Behaviour is unchanged, but a syntax-sensitive description generates a distinct apparent architecture. Without an extensional quotient, canonical morphology is impossible.

These deletion tests establish irreducibility relative to the declared theorem target. They do not claim that the background metalogic proves itself from nothing.

---

## 12. Coverage theorem for known and future computable forms

### Theorem 12.1 (representation coverage)

Every causal computable interactive architecture admits an operational signature \(\chi_\Omega(M)\) of Definition 6.1.

#### Proof

A causal computable machine has a recursively describable configuration at each interaction step, a causal input/output rule, and a transition procedure. Take its reachable configuration as \(S_M\), its external and internal interfaces as \(\mathcal I_M\), and its one-step computation as \(\mathcal T_M\). If a slower self-modification timescale is declared, factor the corresponding transitions into \(\mathcal D_M\); otherwise absorb them into \(\mathcal T_M\). Evaluate resources under the declared \(\rho\), then quotient by \(G\). This constructs \(\chi_\Omega(M)\). \(\square\)

### Corollary 12.2

Adding a new named architecture does not, by itself, enlarge the primitive vocabulary of the theory. It enlarges the set of known realizations unless it exhibits behaviour or physical interaction outside the declared causal/computable domain.

### Boundary 12.3

Theorem 12.1 is a **representation-completeness theorem**, not a claim that the theory has predicted every known architecture from \((\Omega,\mathcal E,\theta,B)\). Three empirical standards must remain distinct:

1. **coverage:** a known architecture maps into the invariant formalism;
2. **recovery:** its morphology region is derived from obligation/ecology/resources without using the architecture label as input;
3. **prospective prediction:** the theory freezes an unoccupied morphology region before a realization is known, and subsequent search or external discovery produces an inhabitant.

Only the third is a strong prospective GMI test.

---

## 13. Main theorem package

Under primitives \((C,\Omega,\mathcal E,P,G)\):

1. the future-obligation quotient \(S^*\) is the unique coarsest exact sufficient state up to isomorphism (Theorem 3.3, Corollary 3.4);
2. exact and worst-case approximate representation lower bounds follow without an environment prior (Corollary 4.1, Proposition 4.3);
3. exact causal cuts obey distinguishability-capacity lower bounds independent of implementation (Theorem 5.2);
4. a prior-free nondominated behaviour/resource frontier exists without scalarizing environments (Definitions 2.1–2.2);
5. implementation labels below the declared gauge quotient are not identifiable from invariant premises (Theorem 6.3);
6. every effective causal transducer is behaviourally realizable on a universal substrate, but physical-resource equivalence does not follow (Proposition 7.2, Boundary 7.3);
7. substrate parameters induce a conditional morphology phase law \(\theta\mapsto\mathcal F_X\) (Definition 8.1);
8. development restricts the physically optimal frontier by reachability, not by an environment prior (Definition 9.1);
9. every causal computable architecture, including future architectures in the same domain, maps into the operational signature space (Theorem 12.1).

The central chain is therefore

\[
(C,\Omega,\mathcal E,P,G)
\Longrightarrow
S^*_{\Omega,\mathcal E,\mathcal C}
\Longrightarrow
\text{state/channel lower bounds}
\Longrightarrow
\mathfrak X_\theta
\Longrightarrow
\mathcal F_X(\Omega,\mathcal E,\theta),
\]

with developmental prediction obtained by intersecting the frontier with \(\mathcal R_B\).

No architecture family and no probability measure over admissible environments occurs in this chain.

---

## 14. Claims not closed by this note

The following remain open and must not be reported as consequences of the formal core:

- a unique named architecture for a general ecology;
- an exact hardware-resource frontier without a substrate model;
- a unique learning/update law without additional structure;
- a proof that a particular finite feature vocabulary is sufficient to classify all morphology phases;
- prospective prediction of a previously unknown morphology followed by independent realization;
- a quantum-interface extension in which histories and channels themselves must be represented by quantum instruments rather than classical stochastic kernels.

These are successor obligations, not gaps to be hidden by stronger wording.

---

## 15. Immediate hostile tests

The next formalization pass should attempt to break the core in this order:

1. **semantic quotient:** construct non-Markov, partially observable, adversarial, and self-referential environments and check that the continuation quantifiers remain adequate;
2. **gauge quotient:** test whether two implementations can have equal obligation behaviour but inequivalent channel/resource structure, and ensure the theory does not collapse them prematurely;
3. **approximation:** replace exact equivalence by worst-case \(\varepsilon\)-equivalence and derive compositional error accumulation bounds;
4. **resource phase law:** construct explicit time-memory-communication trade families and prove nontrivial frontier transitions;
5. **learning:** identify conditions under which minimax-optimal update geometry is unique up to gauge, and construct counterexamples when it is not;
6. **architecture recovery:** map known architecture families into \(\chi_\Omega\) using a frozen vocabulary, then hold out families before testing recovery;
7. **novel prediction:** preregister an unoccupied region of \(\mathcal F_X\) before architecture search.

The formal core should be treated as provisional until these attacks are recorded with countermodels or proofs.