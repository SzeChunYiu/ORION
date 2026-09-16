# Prior-free GMI: architecture non-leakage and system-boundary conditions

## 0. Problem

Removing architecture names from notation is not sufficient to obtain an architecture-neutral theory. Architecture bias can re-enter through at least four channels:

1. the system boundary can leave a large memory, oracle, clock, retriever, or planner uncounted;
2. the resource model can assign privileged costs to an implementation family by definition;
3. the operational probe set can preserve distinctions chosen only because a familiar architecture exposes them;
4. the developmental/search process can enumerate one representation earlier than another, making reachability a property of the coding rather than of the operational morphology.

A prior-free claim therefore needs a non-leakage condition on its premises, not merely a statement that no Transformer or neural network appears by name.

---

## 1. Declared system boundary

A GMI problem instance includes a system-boundary declaration

\[
\mathfrak B=(\mathcal B_{\mathrm{in}},\mathcal B_{\mathrm{out}},\mathcal S_{\mathrm{free}}).
\]

Here:

- \(\mathcal B_{\mathrm{in}}\) lists components and persistent degrees of freedom counted as part of the machine whose morphology/resources are being evaluated;
- \(\mathcal B_{\mathrm{out}}\) lists external components accessed through explicit channels;
- \(\mathcal S_{\mathrm{free}}\) lists side information available without crossing a charged channel, such as a declared clock or public task parameter.

Anything capable of carrying task-relevant information must appear in one of these three places.

### Boundary conservation rule

If an implementation moves information from an internal memory to a retriever, precomputed plan table, tool process, external agent, wall clock, or environment marker, the resulting object is not resource-equivalent by default. The information has crossed the system boundary and must be charged through the declared channel/resource model or explicitly admitted as free side information.

This prevents apparent memory reductions obtained by hiding memory in the environment.

---

## 2. Operational quotient

Let \(\mathcal Q\) be the registered family of operational probes: obligation-relevant behavior, resource measurements, and any internal physical interventions required by the claim.

Define

\[
M\simeq_{\mathcal Q}N
\iff
q(M)=q(N)
\quad\forall q\in\mathcal Q.
\]

Let

\[
q_{\mathcal Q}:\mathcal M\to\mathfrak X
\]

be the quotient map from implementations to operational morphology classes.

The quotient resolution is part of the theorem statement. A theory cannot infer distinctions finer than the probes it has declared.

---

## 3. Architecture-neutral premise criterion

### Definition 3.1

A predicate or numerical functional \(F\) on implementations is **architecture-neutral at resolution \(\mathcal Q\)** when it factors through the operational quotient:

\[
\exists\bar F:\mathfrak X\to\mathcal Y
\quad\text{such that}\quad
F=\bar F\circ q_{\mathcal Q}.
\]

Equivalently,

\[
M\simeq_{\mathcal Q}N
\Longrightarrow
F(M)=F(N).
\]

A premise set is architecture-neutral when every implementation-dependent premise used by the derivation satisfies this condition, except for explicitly declared physical coordinates whose purpose is to distinguish the implementations.

### Examples

Architecture-neutral at an appropriate resolution:

- external latency measured in seconds;
- retained physical memory capacity;
- communication alphabet/bandwidth;
- measured energy;
- error probability;
- causal access relation between registered storage locations;
- a task requirement stated only in terms of external trajectories.

Not architecture-neutral without further justification:

- “attention operations cost one unit” while unrelated operations use another ad hoc scale;
- “neural states may update continuously but symbolic states may not”;
- a morphology feature that contains the labels `Transformer`, `RNN`, or `Bayesian` as values;
- a search grammar whose only admissible candidates are instances of one named family.

The issue is not whether a physical substrate favors one realization. Genuine physical asymmetry belongs in \(\theta\). The issue is whether the asymmetry is measured operationally or inserted by naming convention.

---

## 4. Resource non-leakage

Let

\[
\rho_\theta(M)
\]

be the resource-response vector under physical/substrate condition \(\theta\).

A resource model is admissible for an architecture-neutral morphology theorem only if each charged coordinate is operationally defined. The coordinate may distinguish two implementations—indeed that is the purpose of a morphology/resource theory—but the rule used to measure the coordinate must not change merely because the implementation has been renamed or semantics-preservingly re-encoded.

### Representation-change test

For every registered semantics-preserving re-encoding \(g\) that leaves the physical realization unchanged,

\[
\rho_\theta(gM)=\rho_\theta(M).
\]

For a change that alters the physical realization, any resource difference must be traceable to measured operations, storage, communication, error, fabrication, or another registered physical coordinate rather than to the architecture label itself.

---

## 5. Development is a stronger problem

The static morphology frontier can be defined directly on \(\mathfrak X\) and need not specify how a morphology is discovered.

A developmental theorem introduces a transition/search kernel

\[
\mathcal D(dx'\mid x)
\]

or, at implementation level,

\[
D(dN\mid M).
\]

This is a genuine source of inductive bias. If the search process is defined over source code, circuits, neural graphs, proof programs, or another representation, reachability can depend on that coding even when the final implementations are operationally equivalent.

### Definition 5.1 (quotient-compatible development)

An implementation-level development kernel \(D\) is **quotient-compatible** when its pushforward to morphology classes depends only on the current morphology class:

\[
M\simeq_{\mathcal Q}N
\Longrightarrow
(q_{\mathcal Q})_\#D(\cdot\mid M)
=
(q_{\mathcal Q})_\#D(\cdot\mid N).
\]

Then there is a well-defined quotient process

\[
\bar D(dx'\mid x)
\]

on \(\mathfrak X\).

### Proposition 5.2

If \(D\) is quotient-compatible, support-reachability sets, hitting probabilities, and best-reachable morphology frontiers depend only on the initial morphology class, not on the implementation representative.

#### Proof

The pushforward transition kernel is identical for every representative of one quotient class. Iterating the same quotient kernel gives identical finite-time laws on \(\mathfrak X\), hence identical supports, hitting probabilities, and functions of those laws. \(\square\)

### Corollary 5.3

If quotient compatibility fails, a developmental result is representation/search-prior-sensitive. It may still be scientifically useful, but it is not a zero-architecture-prior developmental theorem.

---

## 6. Program search and reference-machine dependence

Universal program search does not automatically solve the non-leakage problem. A program enumeration or description-length prior requires a coding/reference universal machine. For passive Kolmogorov complexity and Solomonoff prediction, changing the universal machine affects complexity only up to additive/multiplicative constants in the usual invariance results, but interactive universal-agent behavior can be far more sensitive.

Leike and Hutter showed that adversarial choices of universal Turing machine can make AIXI behave pathologically, and that their examined universal-agent optimality notions are not representation-independent in the hoped-for sense (Leike & Hutter, 2015, *Bad Universal Priors and Notions of Optimality*, PMLR 40:1244–1259).

The correct GMI treatment is therefore one of the following:

1. include the coding/reference machine \(U\) as an explicit developmental parameter;
2. prove the target morphology conclusion invariant over a registered class \(\mathcal U\) of codings;
3. formulate development directly on the operational quotient and provide a physical process that realizes that quotient kernel.

A single preferred universal machine cannot be smuggled in and then called “zero prior”.

---

## 7. No-free-lunch boundary

An unrestricted search or learning theorem cannot identify a universally superior developmental process without an asymmetry in the problem class or evaluation. The classical no-free-lunch results make this precise for broad finite optimization settings: performance advantages over one class are offset elsewhere when problems are averaged under the relevant symmetry assumptions (Wolpert & Macready, 1997, *No Free Lunch Theorems for Optimization*, IEEE TEC 1(1):67–82, DOI 10.1109/4235.585893).

GMI should not use no-free-lunch as a slogan that forbids theory. Its role is narrower: it prevents the developmental process or ecology restriction from being omitted while a nontrivial universal search advantage is claimed.

---

## 8. Static versus developmental prior-free claims

The distinction should be explicit in every terminal.

### Static architecture-neutral theorem

A statement of the form

\[
(\Omega,\mathcal E,\Theta,\rho,\mathfrak B,\mathcal Q)
\Longrightarrow
\mathcal F_X(\theta)
\]

can be architecture-neutral without choosing a search process.

### Developmental theorem

A statement of the form

\[
(\Omega,\mathcal E,\Theta,\rho,\mathfrak B,\mathcal Q,D,B)
\Longrightarrow
\mathcal F_B
\]

inherits whatever representation bias is present in \(D\). It is architecture-neutral only after quotient compatibility or a robust invariance theorem is established.

This removes a hidden ambiguity in the phrase “zero-prior development”. Static morphology can be measure-free and architecture-neutral even when the process that discovers a good morphology is not.

---

## 9. Non-leakage checklist

Before a result is labeled `PRIOR_FREE_ARCHITECTURE_NEUTRAL`, verify:

1. **boundary completeness:** every task-relevant persistent component is internal, external through a charged channel, or explicitly free side information;
2. **root blindness:** a common post-merge strategy cannot inspect the forgotten prefix;
3. **probe extensionality:** morphology equality is induced by declared operational probes;
4. **resource operationality:** costs are measured physical/algorithmic resources, not family labels;
5. **ecology declaration:** the environment class is explicit rather than replaced by an unstated distribution;
6. **no hidden scalar prior:** any scalar selector is identified separately from the nondominated order;
7. **developmental equivariance:** if reachability is claimed architecture-neutral, the search/development process descends to the morphology quotient or the result is invariant over a registered coding class;
8. **external-oracle accounting:** retrievers, tools, clocks, planners, verifiers, and precomputed tables are included in the system/resource boundary appropriate to the claim.

Failure of one item does not necessarily refute the underlying experiment. It changes the claim class.

---

## 10. Consequence for the full GMI target

The strongest defensible zero-prior target is not

\[
\text{nothing}\Longrightarrow\text{one architecture}.
\]

It is a family of invariant conditional theorems:

\[
\boxed{
\text{operational obligation/ecology}
+\text{declared physical boundary/resources}
\Longrightarrow
\text{representation-invariant feasibility and morphology phase laws}.
}
\]

Developmental reachability is an additional layer whose own inductive bias must either be exposed as a parameter or proved irrelevant at the quotient level.
