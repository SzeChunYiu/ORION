# Prior-Free Morphology: formal core v0

**Status.** Mathematical framework draft. This note records only statements that can be made without naming a neural, symbolic, Bayesian, program-search, or other architecture as a primitive. It is not a claim that the full GMI programme is empirically closed.

## 0. Scope and claim discipline

The object of the theory is not an architecture label. It is the operational structure that an agent must realize in order to satisfy a declared obligation over a declared ecology under declared resource and developmental constraints.

The word *prior-free* has the following restricted meaning throughout:

> no probability measure over the admissible environment class, and no architecture-specific representation, is supplied as a primitive of the core construction.

The theory is therefore relative to five kinds of data that cannot be removed without changing the problem:

1. a causal interaction structure;
2. an obligation specifying which future differences matter;
3. an admissible environment class;
4. physical, computational, and developmental constraints;
5. an equivalence convention identifying representation changes that are to count as the same operational machine.

Nothing below claims derivation from literal absence of assumptions.

---

## 1. Interaction model

Let time be discrete, `t in N`. Let `A` be an action set and `O` an observation set. A finite history at time `t` is

`h_t = (o_0, a_0, o_1, a_1, ..., o_t)`.

Write `H_t` for the set of such histories and `H = union_t H_t`.

### Definition 1.1 — admissible environment

An environment `e` is a non-anticipating stochastic kernel

`mu_e(do_{t+1} | h_t, a_t)`.

The ecology is a nonempty class `E` of admissible environments. No measure on `E` is assumed.

### Definition 1.2 — continuation

A continuation `c` is an admissible future intervention rule. It may specify actions directly or specify a future policy. The set of continuations relevant to the obligation is denoted `C_Omega`.

### Definition 1.3 — obligation observables

An obligation `Omega` is represented extensionally by a set `Phi_Omega` of bounded measurable functionals of future interaction. Two futures are obligation-equivalent when every `phi in Phi_Omega` gives them the same obligation-relevant law.

This representation is deliberately broad. A terminal utility, a prediction target, a constraint-violation indicator, a vector of task losses, and a finite collection of tests are all special cases.

### Definition 1.4 — obligation-relevant future law

For `e in E`, history `h`, continuation `c in C_Omega`, and `phi in Phi_Omega`, let

`K(e,h,c,phi)`

be the probability law induced on the value of `phi` by starting from `h`, applying `c`, and evolving under `e`.

The construction requires equality of laws, not equality of expectations, unless `Omega` itself declares expectation to be the only relevant observable.

---

## 2. The semantic quotient

### Definition 2.1 — future equivalence

For histories `h,h'` at compatible decision points, define

`h ~_{Omega,E} h'`

iff

`K(e,h,c,phi) = K(e,h',c,phi)`

for every `e in E`, every `c in C_Omega`, and every `phi in Phi_Omega`.

### Lemma 2.2 — equivalence

`~_{Omega,E}` is an equivalence relation.

**Proof.** Reflexivity and symmetry follow from equality of probability laws. If `h~h'` and `h'~h''`, then for every admissible triple `(e,c,phi)`,

`K(e,h,c,phi)=K(e,h',c,phi)=K(e,h'',c,phi)`;

hence `h~h''`. QED.

### Definition 2.3 — canonical semantic state

Define

`S*_{Omega,E} := H / ~_{Omega,E}`

and let

`q : H -> S*_{Omega,E}`

be the quotient map.

An element of `S*` is an obligation-relative future distinction. It is not a neuron, token, rule, program, vector, belief state, or memory address.

### Definition 2.4 — exact sufficient representation

A deterministic representation `z : H -> Z` is exact `Omega`-sufficient over `E` when

`z(h)=z(h')  =>  K(e,h,c,phi)=K(e,h',c,phi)`

for all `e,c,phi` in the declared domains.

### Theorem 2.5 — coarsest exact semantic representation

The quotient `q` is exact `Omega`-sufficient. Moreover, every exact sufficient representation `z` refines `q`: there is a unique map on the image of `z`,

`f : z(H) -> S*_{Omega,E}`,

such that

`q = f o z`.

**Proof.** Sufficiency of `q` is immediate from Definition 2.1: equal quotient classes are precisely histories with equal obligation-relevant future laws.

Let `z` be any exact sufficient representation. If `z(h)=z(h')`, sufficiency gives `h~h'`, hence `q(h)=q(h')`. Therefore `f(z(h)):=q(h)` is well-defined. The factorization `q=f o z` follows by construction. Uniqueness on `z(H)` is forced because every point in `z(H)` has the form `z(h)`. QED.

### Corollary 2.6 — exact finite-state lower bound

If `S*_{Omega,E}` is finite with cardinality `N`, every deterministic exact sufficient finite-state representation satisfies

`|Z| >= N`.

Hence any binary encoding needs at least

`ceil(log_2 N)`

bits in the worst case.

**Proof.** Since `q=f o z`, two distinct quotient classes cannot be mapped by `z` to the same representational value. Thus `z(H)` contains at least one distinct value for each quotient class. QED.

### Boundary 2.7

Theorem 2.5 is a semantic minimality theorem. It does **not** imply a unique policy, a unique learning rule, or a unique physical implementation. Those are separate questions.

For stochastic internal encodings, approximate obligations, or continuous state spaces, cardinality is not by itself the correct complexity measure. Those cases require a declared distinguishability or distortion structure before information-theoretic lower bounds are meaningful.

---

## 3. Decision without an environment prior

Let `M` be an admissible machine. For each `e in E`, let

`R_e(M)`

be its obligation-relative risk. The definition of risk is part of `Omega`; no averaging over `E` is implied.

### Definition 3.1 — risk profile

The risk profile of `M` is the function

`R(M) : E -> R_bar`, `e |-> R_e(M)`.

### Definition 3.2 — dominance

Machine `M_1` weakly dominates `M_2` when

`R_e(M_1) <= R_e(M_2)` for every `e in E`,

and strictly dominates it when the inequality is strict for at least one `e`.

When resources are included, domination is applied to the combined risk-resource vector under the declared partial order.

### Definition 3.3 — prior-free decision frontier

The prior-free admissible set is

`A(Omega,E) := { M : no admissible M' strictly dominates M }`.

This is the primitive decision object. It is defined without `pi(e)`.

### Proposition 3.4 — Bayes optima are scalarizations, not foundations

Let `E={e_1,...,e_n}` be finite and let `pi_i >= 0`, `sum_i pi_i=1`. A Bayes objective

`sum_i pi_i R_{e_i}(M)`

is a nonnegative linear scalarization of the risk vector. If all `pi_i>0`, every minimizer is Pareto efficient.

**Proof.** If a minimizer were dominated, a competitor would weakly lower every coordinate and strictly lower at least one coordinate with positive weight, strictly lowering the scalar objective. Contradiction. QED.

### Theorem 3.5 — finite convex supported-frontier representation

Let `C subset R^n` be the closed convex set of achievable risk vectors after any admissible randomization has been included. If `r* in C` is Pareto efficient, then there exists a nonzero vector `w in R^n_+` such that

`w . r* <= w . r` for every `r in C`.

After normalization, `w` can be read as a probability vector with possibly zero coordinates.

**Proof sketch.** Pareto efficiency implies that `C` and the open set `r* - int(R^n_+)` are disjoint. Convex separation gives a nonzero separating normal `w`. Monotonicity of the forbidden cone forces `w>=0`. Normalizing by `sum_i w_i` yields the stated scalarization. QED.

### Boundary 3.6 — what the theorem does not say

1. Without convexity, unsupported Pareto points need not minimize any linear scalarization.
2. Randomization convexifies risk only when the permitted machine class and resource semantics make random mixtures admissible.
3. For infinite `E`, an analogous supporting-functional result needs topological and functional-analytic assumptions.
4. A positive-weight scalarization is not derived by the frontier; choosing one selects a point on the frontier.

### Definition 3.7 — invariant core

For any admitted family `Pi` of scalarizations, define

`C_inv := intersection_{pi in Pi} Opt(pi)`.

`C_inv` may be empty. Non-emptiness is a stronger statement than Pareto efficiency: it means the same solution is optimal under every admitted scalarization.

Thus the zero-prior construction has two distinct outputs:

- the **frontier**, which survives without selecting a prior;
- an **invariant core**, when one exists, which is forced across a declared scalarization family.

---

## 4. Operational morphology and gauge

The decomposition of a machine into "proposal", "learning update", and "morphology change" is not invariant until a timescale convention is fixed. An inference-time state update may itself be a learning algorithm; a persistent memory may be represented either as state or as parameters. The primitive signature must therefore use causal transition structure rather than architecture vocabulary.

### Definition 4.1 — operational realization

An operational realization is a tuple

`X = (S, I, K, D, rho)`

with:

- `S`: internal operational state space;
- `I`: declared input, output, retrieval, communication, and intervention interfaces;
- `K`: a non-anticipating transition kernel producing next internal state and outward action from the current operational state and current interface values;
- `D`: an optional slower developmental kernel that changes the operational realization itself; `D` is present only after a developmental timescale has been declared;
- `rho(theta)`: a resource-response vector under physical/resource condition `theta`.

### Definition 4.2 — admissible gauge

A gauge transformation is a representation change that preserves all declared obligation-relevant external kernels and all resource quantities that the theory has declared observable. At minimum this includes state relabelings. More general invertible reparameterizations are gauges only when they do not change declared resource accounting.

Write `X ~_G X'` for operational realizations related by the admitted gauge groupoid `G`.

### Definition 4.3 — morphology

A morphology is a gauge class

`chi(M) := [X_M]_G`.

It is therefore already representation-quotiented. Architecture names may label convenient representatives of a morphology class, but they are not elements of the primitive language.

### Theorem 4.4 — architecture-label non-identifiability

Let `T` be any theory whose premises and conclusions are invariant under `~_G`. If `chi(M_1)=chi(M_2)`, then no theorem of `T` can distinguish `M_1` from `M_2` by a gauge-variant architecture predicate.

**Proof.** By hypothesis, every admissible transformation taking a representative of `M_1` to an equivalent representative preserves the truth value of every statement expressible in the invariant theory. A predicate that changes between gauge-equivalent representatives is not invariant, so it cannot be a theorem stated solely in the invariant language. QED.

### Consequence 4.5

A zero-architecture-prior theory may uniquely identify an operational morphology class while leaving many syntactically different implementations. Exact recovery of a name such as "Transformer" is not a stronger version of the same theorem; it is a different, representation-dependent question.

---

## 5. Resource-conditioned morphology frontier

Let `Theta` be a set of physical/resource conditions and `B` a developmental budget. Let

`Xfrak(Omega,E,Theta,B)`

be the set of operational morphologies that are causal, realizable on the declared substrate, reachable under the declared development rules and budget, and evaluable under the declared obligation.

### Definition 5.1 — joint performance vector

For `x in Xfrak`, define

`V_x(theta) := ( R_e(x)_{e in E}, rho_x(theta) )`.

The resource vector is not silently collapsed to a scalar.

### Definition 5.2 — morphology frontier

`F(Omega,E,theta,B)` is the set of morphologies in `Xfrak` whose joint performance vector is nondominated under the declared product order.

### Definition 5.3 — identifiability region

A parameter point is morphology-identifying when

`| F(Omega,E,theta,B) / ~_G | = 1`.

More generally, a region `U subset Theta` is identifying for class `C` when every `theta in U` has the same unique frontier class `C`.

This turns architecture selection into a phase-law question: determine the partition of `Theta` into regions with distinct frontier sets, rather than demand one hardware-independent winner.

### Proposition 5.4 — external constants need not be predicted

A theory can be complete *conditional on its declared resource model* by deriving the map

`theta |-> F(Omega,E,theta,B)`

without predicting which `theta` the physical world occupies. Measurement locates the realized system in the derived phase diagram.

This proposition does not license an incomplete `Theta`. If a relevant physical variable has been omitted, the conditional theory may be misspecified.

---

## 6. Realizability and the meaning of sufficiency

Semantic sufficiency and physical realizability are different statements. The former follows from the quotient construction; the latter requires a computational substrate theorem.

### Theorem 6.1 — finite rational transducer realization

Let `S`, `O`, and `A` be finite. Suppose an operational transition kernel

`K(s',a | s,o)`

has rational probabilities. Then there exists a finite randomized digital transducer that realizes `K` exactly.

**Proof sketch.** For each finite conditional distribution, choose a common denominator and implement the transition by a finite uniform draw over that denominator followed by a lookup table. Combining the finite tables over `(s,o)` yields a finite randomized transducer. QED.

### Boundary 6.2

For countably infinite or continuous state spaces, exact realization requires computability assumptions on the kernels and a precise simulation model. Arbitrary real-valued transition probabilities are not automatically computably sampleable. Claims of universal constructive sufficiency must state these assumptions explicitly.

### Corollary 6.3 — representation coverage of implemented classical systems

Any implemented finite digital causal agent with classical interfaces is already a finite causal transducer when its full machine configuration is taken as state. Therefore it admits a map `chi` into the morphology language. Its named architecture is not needed for representation coverage.

This corollary establishes **representation coverage**, not optimality, minimality, or successful derivation of the architecture from `Omega`.

### Quantum boundary 6.4

A machine with quantum internals and only classical external interfaces induces a classical stochastic input-output kernel, but a theory that intends to predict its internal physical morphology or quantum resources must replace the classical-kernel category by an appropriate quantum operational category (states, channels, instruments). Classical input-output reduction alone is insufficient for that stronger claim.

---

## 7. Development and reachability

Let `x_0` be a starting morphology and `D` a declared developmental process.

### Definition 7.1 — finite-budget reachable set

`Reach_B(x_0,D)` is the set of morphology classes reachable with positive admissible probability or by an admitted deterministic development path within budget `B`.

### Definition 7.2 — reachable frontier

`F_B := F cap Reach_B(x_0,D)`.

A globally nondominated morphology outside the reachable set is not a developmental prediction.

### Definition 7.3 — stochastic hitting time

For stochastic development,

`tau_F := inf { t : chi(M_t) in F }`.

A developmental theorem must bound quantities such as

`P_D(tau_F <= B)`

or expected hitting cost. Merely defining `Reach_B` does not prove that a proposed search process reaches the frontier.

---

## 8. Relative irreducibility of the primitive basis

The present primitive basis is

`P0 = { C, Omega, E, P, G }`,

where `C` is causal interaction structure, `Omega` the obligation, `E` the ecology, `P` the physical/resource/development specification, and `G` the gauge convention.

The following are **relative necessity arguments**, not yet a model-theoretic proof of global logical independence.

### Proposition 8.1 — obligation cannot be deleted

Remove `Omega`. Take two otherwise identical problems that differ only in which of two terminal outcomes is declared successful. They require opposite optimal actions while sharing every remaining primitive. No remaining datum can select between them.

### Proposition 8.2 — ecology cannot be deleted

Remove `E`. Two environment classes can agree on all remaining primitives but reward incompatible predictors or actions. A morphology theorem that does not quantify or condition on an environment class cannot distinguish them.

### Proposition 8.3 — causality cannot be deleted

Remove non-anticipation. A machine permitted to inspect future observations can solve tasks that violate every causal memory or channel lower bound. Therefore the causal and oracle-augmented model classes have incompatible capability laws.

### Proposition 8.4 — resource/development specification cannot be deleted from morphology selection

Take two implementations with identical external behavior but opposite hardware cost orderings under two substrates. Without the resource condition, the theory cannot select which implementation is efficient. Likewise, without a development specification, reachability is undefined.

### Proposition 8.5 — gauge convention cannot be deleted from representation-invariant morphology

Apply an arbitrary bijection to every internal state label of a machine. External behavior is unchanged. A theory that treats the relabeling as a new morphology generates infinitely many spurious architecture distinctions. Some extensional identification is therefore necessary.

### Boundary 8.6

To claim an *irreducible axiom basis* in the strict logical sense, these primitives must be encoded in a fixed formal language and each independence result proved by models of all other axioms plus the negation or incompatible alternatives of the target axiom. The countermodels above establish necessity for the intended theorem schema; they do not yet constitute that stronger independence result.

---

## 9. Known-form reduction is a validation test, not the completeness proof

Corollary 6.3 already supplies representation coverage for implemented finite classical systems. Named-family reduction is still useful because it can expose a missing operational primitive.

At the morphology level, the principal families reduce as follows:

| family | architecture-free operational residue |
| --- | --- |
| feed-forward / convolutional | transient state, fixed learned transition, interface locality/equivariance, resource response |
| recurrent / LSTM / reservoir | persistent compressed state with sequential transition |
| state-space / selective SSM | structured recurrent state and input-dependent propagation |
| attention / Transformer | transient addressable context with content-dependent many-to-many aggregation |
| graph neural / message passing | distributed state with topology-constrained communication |
| associative / energy based | state with iterative settling dynamics |
| external memory / retrieval / RAG | controller state plus separately addressable persistent store and read/write channels |
| test-time training / learned memory | multiple persistence timescales; operational state itself may undergo an inference-time learning transition |
| Bayesian filter / probabilistic program | belief or sufficient-statistic state with inference/conditioning transition |
| symbolic / production / theorem proving | discrete relational state with rule or search transition |
| program induction / MDL / universal search | hypothesis/program state with enumeration, scoring, compression, or weighting transition |
| model-free reinforcement learning | policy/value/internal state updated from interaction plus action channel |
| world model / planning / tree search | predictive state plus counterfactual simulation/search transition |
| iterative generative / diffusion | partially resolved sample state with stochastic refinement transition |
| evolutionary / population search | population state plus variation and selection transition |
| spiking / neuromorphic | temporally evolving event-driven state and hardware-specific resource response |
| mixture-of-experts / modular | routing channel over component transducers |
| neuro-symbolic | composition of heterogeneous representations through operational interfaces |
| tool / multi-agent | transducer composition through external action and communication channels |

A new family falsifies the proposed operational language if no `S,I,K,D,rho` realization can represent the obligation-relevant causal and resource behavior without smuggling the missing structure into an uninterpreted component.

---

## 10. The present theorem chain

The formal core is therefore not

`logic -> probability -> Bayes -> architecture`.

It is the following conditional chain:

1. `C + Omega + E` define obligation-relative future laws.
2. Future-law equality induces the canonical quotient `S*`.
3. `S*` is the coarsest exact semantic representation (Theorem 2.5).
4. The environment-wise risk vector defines dominance without an environment prior.
5. Nondominance defines a prior-free decision frontier.
6. Under additional convexity conditions, priors/weights recover supported points as scalarizations (Theorem 3.5); they are not needed to define the frontier.
7. Operational realizations are quotiented by `G` before morphology claims are made.
8. `P=(Theta,B,D,...)` converts semantic/decision feasibility into resource-conditioned and development-conditioned morphology.
9. Exact architecture syntax is not identifiable from a representation-invariant theory (Theorem 4.4).
10. Constructive realizability is a separate theorem obligation and is currently closed only for explicitly stated substrate classes such as Theorem 6.1.

The corresponding object is

`F : (C,Omega,E,P,G) -> { nondominated operational morphology classes }`.

A unique morphology is a special phase in which this set has one element; it is not assumed globally.

---

## 11. Claims that remain open

The following are not closed by this note.

1. **Constructive semantic quotient.** `S*` may be mathematically defined but computationally inaccessible for a large or unknown `E`.
2. **Approximate quotient.** A canonical distortion notion has not been derived for arbitrary obligations.
3. **Channel lower bounds.** General cut-set theorems connecting obligation distinctions to restricted information channels remain to be formalized.
4. **Infinite-environment complete-class theorem.** The topology and admissible dual functionals must be fixed before extending Theorem 3.5.
5. **Resource completeness.** A phase diagram is only as complete as the physical variables admitted in `Theta` and the realization class admitted in `Xfrak`.
6. **Developmental convergence.** Reachability definitions do not imply a search algorithm reaches the frontier.
7. **Strict axiom independence.** Proposition 8.1--8.5 must be lifted into a fixed formal model class for a genuine minimal-basis theorem.
8. **Quantum-internal morphology.** Classical stochastic transducers do not suffice when the internal quantum resource structure itself is part of the prediction target.
9. **Prospective novelty.** No architecture-free frontier region has yet been frozen before a search that later produced a previously unknown inhabitant.

The last item is the strongest empirical terminal. A theory that merely absorbs all known forms has descriptive coverage. A theory that preregisters a morphology region and subsequently constructs an unknown realization has prospective content.

---

## 12. Falsification obligations for the next pass

The next research wave should try to destroy the framework at the following joints.

1. Construct two histories merged by `S*` that some admissible obligation continuation nevertheless distinguishes. If found, Definition 2.1 is incomplete.
2. Construct an exact sufficient representation that does not factor through `q`. If found, Theorem 2.5 is false.
3. Exhibit a claimed prior-free conclusion that changes only because an unacknowledged scalarization was introduced. Such a result is not prior-free.
4. Exhibit gauge-equivalent implementations whose declared resource vectors differ. This means `G` is too coarse or the resource observables are underspecified.
5. Find a known architecture whose causal operation cannot be represented by `S,I,K,D,rho` without adding a genuinely new operational primitive.
6. Find an allegedly derived unique architecture in a region where the morphology frontier contains more than one gauge class.
7. Find a phase-law prediction reversed by a physically relevant variable absent from `Theta`.
8. Find a developmental claim that relies on global optimality while its target lies outside `Reach_B`.
9. Preregister an empty, architecture-free frontier region and attempt constructive search. Failure after a declared complete search is evidence against the sufficiency side; success is the first genuine prospective GMI test.

Until these attacks are answered, the appropriate claim is **formal-core candidate**, not full GMI closure.
