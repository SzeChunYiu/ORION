# Prior-free GMI: dynamic controller closure and the closed-cover donor

## 0. Purpose

The control-conflict hypergraph gives a sharp one-shot history-encoding problem, but an autonomous finite-state controller has an additional obligation: its next state must be computable from its current retained state and the newly observed input. It cannot ask an external oracle to recolor the entire past history after every step.

This distinction is not new. It is structurally the same distinction that appears in minimization of incompletely specified finite-state machines (ISFSMs), where compatible states must be assembled into a **closed cover**: the cover must represent the states, and every implied successor set must itself be contained in a member of the cover.

This note imports that donor explicitly and states the GMI specialization.

---

## 1. Finite residual control specification

Fix a finite set \(V\) of residual control situations. A residual state may be a finite history, a predictive-response class, or another exact task residual; the theorem below does not depend on its representation.

Let \(\mathcal O\) be a finite observation/input alphabet and \(\mathcal A\) a finite action/output alphabet.

For each \(v\in V\), let

\[
A_\varepsilon(v)\subseteq\mathcal A
\]

be the actions that are admissible at tolerance \(\varepsilon\). For an admissible action \(a\), let

\[
\operatorname{Succ}(v,a,o)\subseteq V
\]

be the set of residual states that may follow after observation/input \(o\). Set-valued successors allow environment nondeterminism or an ecology of possible next states.

This finite specification is assumed to have already absorbed whatever lookahead is required for the declared one-step action admissibility. If success depends on long-term choices, the residual state must carry enough task information for the specification to be Markov at this level.

---

## 2. Compatible sets

### Definition 2.1 (output/action compatible)

A set \(C\subseteq V\) is action-compatible when

\[
A_\varepsilon(C)
:=
\bigcap_{v\in C}A_\varepsilon(v)
\ne\varnothing.
\]

Thus one controller state can choose at least one action acceptable for every residual situation represented by \(C\).

For \(a\in A_\varepsilon(C)\) and input \(o\), define the implied successor set

\[
I(C,a,o)
=
\bigcup_{v\in C}\operatorname{Succ}(v,a,o).
\]

---

## 3. Closed controller cover

### Definition 3.1

A finite family \(\mathcal K=\{C_1,\ldots,C_m\}\) of nonempty subsets of \(V\) is an \(\varepsilon\)-**closed controller cover** when:

1. **cover:**
   \[
   \bigcup_{i=1}^m C_i=V;
   \]
2. **action compatibility:** for every \(C_i\), a witness action
   \[
   a_i\in A_\varepsilon(C_i)
   \]
   is selected;
3. **closure:** for every \(C_i\) and every observation \(o\) for which \(I(C_i,a_i,o)\ne\varnothing\), there exists \(C_j\in\mathcal K\) such that
   \[
   I(C_i,a_i,o)\subseteq C_j.
   \]

The containing class \(C_j\) is the next controller state after observing \(o\).

The cover may overlap. Overlap is important: a residual situation can be compatible with more than one reduced controller state even when no unique quotient partition exists.

---

## 4. Closed-cover realization theorem

### Theorem 4.1

Every \(\varepsilon\)-closed controller cover with \(m\) members induces an autonomous deterministic controller with at most \(m\) internal states satisfying all local admissibility constraints of the finite residual specification.

#### Construction

Create one controller state \(z_i\) for each compatible class \(C_i\). In state \(z_i\), output the witness action \(a_i\). For observation \(o\), choose a class \(C_j\) guaranteed by closure and set

\[
\delta(z_i,o)=z_j.
\]

If the actual residual situation before the transition lies in \(C_i\), every possible successor residual lies in \(I(C_i,a_i,o)\subseteq C_j\). Induction therefore maintains the invariant that the actual residual situation belongs to the controller class represented by its internal state. Since \(a_i\) is admissible for every element of \(C_i\), the controller satisfies the registered local tolerance constraints. \(\square\)

### Theorem 4.2 (converse)

Any autonomous deterministic controller satisfying the finite residual specification induces a closed controller cover whose cardinality is at most the number of reachable controller states.

#### Proof

For each reachable controller state \(z\), let \(C_z\subseteq V\) be the residual situations that can coexist with internal state \(z\). The controller's output action in \(z\) is admissible for every \(v\in C_z\), giving action compatibility. The sets \(C_z\) cover every reachable residual situation. After an observation \(o\), the controller deterministically enters one next internal state \(z'\); therefore every residual successor possible from any \(v\in C_z\) under the common output action and observation \(o\) must lie in \(C_{z'}\). Hence closure holds. \(\square\)

### Corollary 4.3 (exact finite-state complexity)

Within the finite residual specification,

\[
N^*_{\mathrm{dyn}}(\varepsilon)
=
\min_{\mathcal K\ \mathrm{closed}}
|\mathcal K|.
\]

The equality is up to removal of unreachable controller states and relabeling.

---

## 5. Relation to the conflict hypergraph

The static conflict hypergraph records which sets cannot share one admissible output/continuation under the chosen residual semantics. A valid closed cover must first satisfy the compatibility/cover condition and then the successor closure condition.

Therefore

\[
\chi_\Omega(\varepsilon)
\le
N^*_{\mathrm{dyn}}(\varepsilon),
\]

where \(\chi_\Omega\) is the one-shot/history-encoder coloring number when the two constructions use the same residual action semantics.

The inequality can be strict: classical ISFSM minimization requires both cover and closure, and minimum state reduction is not in general solved by a compatibility coloring alone.

This repairs the boundary in `CONTROL_INFORMATION_PROFILE_V1.md`:

- \(\chi_\Omega(\varepsilon)\) is exact for a one-shot encoder that sees the complete current residual/history and can transmit a fresh color;
- \(N^*_{\mathrm{dyn}}(\varepsilon)\) is the autonomous dynamic-state requirement after closure is imposed.

---

## 6. Why overlap is not a defect

A quotient partition forces every residual state into exactly one reduced state. In incompletely specified control problems, compatible classes need not form an equivalence relation. A residual situation can belong to several compatible classes, and the minimal realization can require an overlapping cover.

This gives a stronger version of the non-uniqueness result from `FORMAL_CORE_V2.md`:

\[
\boxed{
\text{general minimal control state is a closed-cover problem, not necessarily a quotient problem.}
}
\]

The canonical top-down object is the compatibility/implication structure; a minimal controller is one closed-cover realization of it.

---

## 7. Donor ownership

The mathematical mechanism in Sections 2--4 belongs to the classical theory of incompletely specified finite-state machine minimization. That literature distinguishes:

- compatible classes;
- cover constraints;
- implied successor sets;
- closure constraints;
- minimal closed covers.

It also establishes that exact minimization of incompletely specified FSMs is computationally hard in general and motivates prime-compatible and covering algorithms.

GMI should therefore cite this theory as the direct donor. The GMI-specific work begins when the compatible/residual specification is **derived from a cognitive obligation and ecology**, rather than supplied as a hardware state table, and when the resulting controller complexity is propagated into physical morphology/resource phase laws.

---

## 8. Developmental consequence

Even after a task's exact minimum controller-state count is characterized by a closed-cover optimization, finding that cover may itself be computationally expensive.

Thus three quantities must remain separate:

1. **information/control lower bound**
   \[
   \chi_\Omega(\varepsilon);
   \]
2. **minimum autonomous controller size**
   \[
   N^*_{\mathrm{dyn}}(\varepsilon);
   \]
3. **development/search cost to discover a controller near that minimum**.

A morphology theorem that identifies an optimum without modeling the cost of finding it has not closed the developmental problem.

---

## 9. Successor theorem target

For a concrete finite GMI ecology, derive the residual control specification from \((\Omega,\mathcal E)\), compute:

\[
\chi_\Omega(\varepsilon),
\qquad
N^*_{\mathrm{dyn}}(\varepsilon),
\]

and exhibit a strict closure gap

\[
N^*_{\mathrm{dyn}}(\varepsilon)
>
\chi_\Omega(\varepsilon).
\]

Then vary substrate cost parameters to determine whether the optimal physical realization stores the extra dynamic state locally, reconstructs it by computation, retrieves it externally, or changes the interaction protocol.

That sequence would connect established closed-cover theory to a genuine morphology phase law.
