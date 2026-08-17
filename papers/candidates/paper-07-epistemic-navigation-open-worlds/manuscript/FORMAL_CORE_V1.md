# P7 formal core V1

**Candidate paper:** Epistemic Navigation in Open Worlds  
**Authority:** mathematical working object; novelty not yet authorized  
**Date:** 2026-08-17

## 1. Epistemic topologies

### Definition 1 (epistemic topology)
An **epistemic topology** is a tuple

\[
T=(V,E,\lambda,\Omega),
\]

where:

- \(V\) is a set of epistemic locations;
- \(E\subseteq V\times V\) is a directed reachability relation;
- \(\lambda\) assigns typed semantic labels, representations and evidence identities to locations/edges;
- \(\Omega\) is a set of task obligations whose satisfaction conditions are defined over locations, evidence and routes.

The word topology is used operationally: \(T\) may be a graph, hypergraph, transition system, simplicial/relational structure, or another representation with a reachability notion. The manuscript must not imply a topological-space structure unless one is explicitly introduced.

### Definition 2 (route)
A route is

\[
r=(I_r,\delta_r,\sigma_r,\kappa_r),
\]

where \(I_r\) is an interface/source family, \(\delta_r\) is its transition/query mechanism, \(\sigma_r\) is a structural assumption signature, and \(\kappa_r\) is its known coverage/censoring contract.

Two route names are not necessarily two structural routes.

### Definition 3 (navigation state)
A navigation state is

\[
N=(T,x,F,R,O,C,V_h,B,H),
\]

where:

- \(x\) is the current epistemic location or belief over locations;
- \(F\) is the active frontier;
- \(R\) is the registered route set;
- \(O\subseteq\Omega\) is the active obligation set;
- \(C\) records censored, unavailable and unknown-coverage regions/routes;
- \(V_h\) records visited locations and evidence identities;
- \(B\) is remaining resource state;
- \(H\) is observation/action history.

## 2. Observation histories and world extensions

### Definition 4 (observational equivalence)
Let \(h\) be a finite history produced by a navigator. Two worlds/topologies \(T_1,T_2\) are observationally equivalent at \(h\), written

\[
T_1\equiv_h T_2,
\]

when every observation, route response, cost and transition exposed along \(h\) is identical in the two worlds.

### Definition 5 (admissible extension)
An admissible extension of the observed world is any \(T'\) that preserves every observation in \(h\) while adding or refining unobserved locations, edges, routes, labels or obligations not excluded by a valid closure certificate.

### Definition 6 (closure certificate)
A closure certificate for obligation family \(O\) is an externally or mechanically checkable object \(z\) whose semantics exclude every admissible extension containing an unsatisfied obligation in \(O\).

Examples can include a complete finite manifest, an exhaustive index with content identity and coverage proof, or a theorem proving that every relevant state lies in the enumerated region. Low expected utility, repeated empty responses and budget exhaustion are not closure certificates by definition.

## 3. Impossibility of unlicensed open-world stopping

Let a stopping rule \(\pi\) map finite histories to

\[
\{\mathsf{continue},\mathsf{route\_stop},\mathsf{task\_stop},\mathsf{defer},\mathsf{cannot\_check}\}.
\]

### Theorem 1 (open-world stopping impossibility)
Let \(h\) be a finite history for which no closure certificate excludes unseen relevant states. Then there exist admissible extensions \(T_0,T_1\) such that:

1. \(T_0\equiv_h T_1\);
2. all mandatory obligations are satisfied in \(T_0\);
3. at least one mandatory obligation remains unsatisfied in \(T_1\).

Consequently, no stopping rule depending only on \(h\) can soundly output \(\mathsf{task\_stop}\) for both worlds.

#### Proof
Because no closure certificate excludes unseen relevant states, construct \(T_0\) as any completion consistent with the observed history in which the observed/closed region contains every required witness. Construct \(T_1\) by preserving the complete observed substructure and every response along \(h\), then adding an unobserved location \(u\) that carries a mandatory relevant witness or defeater not present in the explored region. The addition is admissible because it is not excluded by a closure certificate. The two worlds are observationally equivalent on \(h\), but task completion differs. A history-only rule must return the same value on both and therefore cannot soundly certify completion in both. \(\square\)

### Corollary 1.1 (fail-closed completion)
Under the theorem's assumptions, a sound rule must continue, defer with an explicit open obligation, or return \(\mathsf{cannot\_check}\); it cannot convert absence of further observations into global completion.

### Corollary 1.2 (utility is not completion authority)
A route's expected marginal utility may be arbitrarily low in both \(T_0\) and \(T_1\). Therefore utility can govern resource allocation without resolving the completion distinction.

### Remark
The theorem is an indistinguishability result, not a claim that research must continue forever. It identifies the extra authority object required to turn resource stopping into scientific completion.

## 4. Route stopping versus task stopping

### Definition 7 (route-stop judgment)
A route \(r\) may receive \(\mathsf{route\_stop}\) when its frozen local policy establishes that no further action on \(r\) is currently justified under its budget/coverage contract.

### Definition 8 (task-stop judgment)
A task may receive \(\mathsf{task\_stop}\) only when every mandatory obligation is satisfied, validly discharged, or covered by a closure certificate whose scope includes the obligation.

### Proposition 2 (route stop does not imply task stop)
There exists a navigation state in which every executed route has locally stopped while an unexecuted, unavailable or censored route retains an open mandatory obligation. Hence the implication

\[
\bigwedge_{r\in R_{\mathrm{executed}}}\mathsf{route\_stop}(r)
\Rightarrow
\mathsf{task\_stop}
\]

is invalid without an additional coverage premise.

#### Proof
Take two routes \(r_1,r_2\), where \(r_1\) is exhausted and \(r_2\) is unavailable but may contain a required witness. The antecedent over executed routes is true, while the mandatory obligation associated with \(r_2\) is unresolved. \(\square\)

## 5. Route independence and observed overlap

### Definition 9 (structural independence relative to an obligation)
Routes \(r_1,r_2\) are structurally independent relative to obligation \(o\) only when the registered failure/coverage assumptions relevant to \(o\) do not share a single unaccounted common cause sufficient to make both routes miss the same witness. The exact independence relation may be represented by disjoint critical-assumption sets, a causal model, or a stronger contract.

Observed result sets are denoted \(Y_1,Y_2\).

### Proposition 3 (equal output does not imply structural dependence)
There exist structurally independent routes with \(Y_1=Y_2\).

#### Construction
Let two independently maintained indexes contain the same relevant document and retrieve it through different source and ranking mechanisms. Their observed outputs coincide even though their critical failure assumptions differ. \(\square\)

### Proposition 4 (disjoint output does not imply structural independence)
There exist structurally dependent routes with \(Y_1\cap Y_2=\varnothing\).

#### Construction
Let two query templates call the same censored index and partition its visible records by an arbitrary filter. Outputs are disjoint, but one index-coverage failure defeats both routes. \(\square\)

### Consequence
Content overlap is a behavior metric, not an authority proof for route independence.

## 6. Topology-changing reframes

### Definition 10 (reframe)
A reframe is a tuple

\[
\rho=(T,T',\phi,\psi,\Pi),
\]

where:

- \(T\) is the old topology and \(T'\) the proposed topology;
- \(\phi:V\rightharpoonup V'\) is a partial location-preservation map;
- \(\psi:E\rightharpoonup E'\) is a partial relation-preservation map;
- \(\Pi\) is a set of preservation obligations/proofs specifying which labels, evidence identities and semantic relations survive.

A reframe is not merely a transition inside \(T\); it changes the representation that defines locations and reachability.

### Definition 11 (admissible reframe)
A reframe is admissible when it has the required responsibility/authority judgment, preserves every retained evidence identity, and reopens every old closure whose complete support is not preserved by \((\phi,\psi,\Pi)\).

### Theorem 5 (strict expressivity of topology-changing navigation)
There exists a family of tasks for which every policy restricted to an initial topology \(T\) fails, while a policy with one admissible reframe to \(T'\) succeeds.

#### Proof
Let \(T\) contain a start state \(s\) and arbitrary reachable states but no path to any state satisfying goal predicate \(g\). Every fixed-topology policy remains within the reachability closure of \(s\), so it cannot reach \(g\). Let an admissible reframe construct \(T'\) in which a newly represented state \(v_g\) satisfies \(g\) and is reachable from the preserved image \(\phi(s)\). A reframe-enabled policy applies \(\rho\) and follows the new path. Therefore the policy class is strictly more expressive on this family. \(\square\)

### Remark
This theorem is intentionally weak as a novelty claim. Replanning and representation change are established ideas. P7 requires a stronger residual: preservation/reopening plus stopping authority under evolving topology.

## 7. Transfer and reopening across reframes

For a closed obligation \(o\), let \(\operatorname{Supp}_T(o)\) be the complete support substructure used by its certificate: supporting locations, edges, labels, route contracts and evidence identities.

### Definition 12 (support-preserving reframe for an obligation)
A reframe \(\rho\) preserves \(o\) when:

1. \(\phi\) and \(\psi\) are defined on every element of \(\operatorname{Supp}_T(o)\);
2. all predicates/relations used in the certificate are preserved under the maps;
3. evidence identities remain content-bound and unchanged;
4. no new defeater in \(T'\) lies within the certificate's declared completeness scope.

### Theorem 6 (safe transfer criterion)
If \(\rho\) preserves \(o\), the old certificate remains valid in \(T'\). If any preservation condition is absent and no replacement proof is supplied, uniformly sound navigation must reopen \(o\) or assign \(\mathsf{cannot\_check}\).

#### Proof
For the first direction, every object and relation used by the old derivation has a semantics-preserving image in \(T'\), evidence identity is retained, and no in-scope defeater is introduced; transport the derivation along the maps. For the second direction, if a required support element/relation is unmapped or unproved, construct two target topologies consistent with the available mapping: one preserving the derivation and one falsifying the missing element. Retaining closure would be unsound in the latter. \(\square\)

## 8. Stopping authority invariant

### Definition 13 (mandatory open obligation)
An obligation is mandatory-open when its state is not satisfied/discharged and no valid closure certificate covers it.

### Theorem 7 (fail-closed task-stop invariant)
In any navigation trace preserving the rule

\[
\mathsf{task\_stop}\Rightarrow \text{no mandatory-open obligation},
\]

route exhaustion, low utility, budget depletion and repeated observations cannot by themselves derive \(\mathsf{task\_stop}\).

#### Proof
None of those facts changes an obligation from mandatory-open to satisfied/discharged or creates a closure certificate. The invariant's antecedent therefore remains false while any such obligation exists. \(\square\)

## 9. Deterministic checking obligations

The associated finite checker must generate bounded dynamic graphs and verify:

1. indistinguishable complete/incomplete world pairs for Theorem 1;
2. route-stop/task-stop counterexamples;
3. equal-output independent-route and disjoint-output dependent-route constructions;
4. an unreachable fixed topology and reachable reframed topology;
5. transfer versus reopening under complete/incomplete preservation maps;
6. no task stop in the presence of mandatory-open obligations.

No LLM API is needed for any case.

## 10. Nearest-work pressure and nonclaims

This core does **not** claim novelty for:

- graph search or knowledge-graph navigation;
- POMDP belief-space planning;
- information foraging or exploratory search;
- replanning, model revision or representation learning;
- open-world impossibility arguments in general;
- stopping rules or capture-recapture in isolation;
- P2's route/task stopping mechanics.

The candidate residual is the combination:

\[
\text{evolving epistemic topology}
+
\text{support-preserving transfer/reopening}
+
\text{explicit censored obligations}
+
\text{non-escalating task-stop authority}.
\]

If this reduces to a direct composition of P1 and P2 with no distinct theorem, benchmark or cross-domain result, it should merge rather than remain P7.

## 11. What this formal core establishes now

It establishes elementary impossibility, separation and transfer results under the definitions above. It does not yet establish:

- novelty over planning/search/formal-navigation literature;
- that real scientific state spaces satisfy the model;
- that a topology-changing navigator improves real research;
- that route-independence contracts are practically identifiable;
- that P7 is distinct from P1+P2;
- peer-review readiness.
