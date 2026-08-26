# Formal Epistemic Structures and Mechanics

**Paper VI candidate — theory-complete manuscript**  
**Version:** 2026-08-18 / V2 closure  
**Scientific scope:** formal theory and deterministic finite-model support  
**No first-of-kind claim is made.**

## Abstract

Scientific agents do more than update propositions. They change representations, search universes, measurements, procedures, claims, evidence bindings, obligations, and sometimes the mechanisms that govern later changes. Existing formalisms already cover important parts of this space: dynamic epistemic logic formalizes informational actions; belief revision formalizes epistemic-state change; truth-maintenance and self-adjusting-computation systems propagate dependency changes; separation and process logics support local composition; effect systems type requested actions and residual effects; authorization systems govern which effects may commit. The remaining problem is not the absence of state-change formalisms, but the interaction between **computational change**, **scientific certification**, **hard epistemic obligations**, **provenance**, and **mutation authority**.

We develop a typed mechanic-contract semantics for this interaction. A mechanic declares semantic read/write footprints, hard evidence and authority requirements, typed requested effects, invariants, emitted obligations, provenance, and failure terminals. We give a corrected root-inclusive dependency-repair operator, extend it with protected preservation certificates, prove history-aware commutation under full scientific-footprint separation, prove sequential authority non-escalation and residual-obligation persistence, and state a protected boundary for recursive audit and self-authorization. The central separation result shows that erasing obligation and authority structure can make two mechanic contracts computationally identical while changing whether their transitions are epistemically admissible. Thus correct incremental computation or dependency repair does not, by itself, determine whether a scientific certificate may survive or whether a mutation may commit.

A standard-library finite checker exercises 960 root-inclusive reopening cases over all forward DAGs on four nodes, 64 preservation-certificate combinations, composition/history cases, hard-obligation persistence, authority non-escalation, recursive-cycle rejection, and typed-erasure counterexamples. The contribution is deliberately scoped: we do not claim novelty for dependency-directed repair, typed effects, authorization, provenance, or recursive agent architectures. Instead, the paper isolates the additional semantics required when those mechanisms are used to maintain **scientifically certified** state.

## 1. Introduction

Autonomous scientific systems increasingly operate as stateful processes rather than one-shot predictors. A research agent can retrieve evidence, infer claims, change the representation in which a problem is posed, reopen earlier conclusions, alter a search strategy, revise an evaluator, or propose a change to its own procedure. These operations share a computational shape—read state, perform an action, update state—but they do not share the same scientific authority.

A search failure may justify expanding the search universe but not rewriting the evaluator. A new representation may invalidate some conclusions without invalidating others. A successful replay may be evidence that a self-change is useful without authorizing that self-change to become the new production method. A downstream computation may be unaffected by an input mutation while a scientific certificate over that computation becomes stale because its validation obligation changed.

This motivates a distinction between two questions that software and agent infrastructure often answer separately:

1. **What changes computationally?**
2. **What remains epistemically admissible after that change?**

The first question has mature answers in truth-maintenance, incremental and self-adjusting computation, dependency-driven rollback, process calculi, and program analysis. The second requires additional objects whenever a state component carries scientific certification, evidence obligations, provenance constraints, or mutation authority.

This paper develops a formal interface between the two. It treats prior mechanisms as donors rather than weak baselines. The goal is not to rename change propagation as epistemic mechanics; it is to make explicit which additional premises are necessary when change propagation is embedded inside evidence-governed scientific reasoning.

### 1.1 Contributions

The paper makes six scoped contributions.

**C1 — typed epistemic mechanic contracts.** We define mechanic contracts whose semantics include ordinary state effects together with hard evidence obligations, provenance, authority and audit history.

**C2 — root-inclusive certificate-aware repair.** We correct a common strict-descendant formulation by including directly changed certified claims in the affected set, then prove soundness and graph-relative minimality. We further permit preservation only through protected, exact-change invariance certificates.

**C3 — history-aware composition.** We separate equality of current scientific state from equality of ordered history and prove commutation under full scientific-footprint separation, using an independence quotient for audit traces.

**C4 — obligation and authority conservation.** We prove that finite composition of non-escalating mechanics cannot mint unrooted authority and that a hard residual obligation cannot disappear merely because later computation succeeds.

**C5 — typed-erasure separation.** We prove that two contracts can have the same bare transition/dependency semantics while differing in epistemic admissibility. This is the paper's main discriminator from pure dependency maintenance.

**C6 — conservative embedding discipline.** We state explicit special cases for ordinary transition systems, dependency maintenance, self-adjusting computation, and typed-effect systems, preventing the general formalism from appropriating the native contributions of those fields.

### 1.2 Non-contributions

We do not claim to invent knowledge-changing actions, belief revision, dependency maintenance, incremental change propagation, effect typing, provenance, authorization, delegation/revocation, separation reasoning, or recursive agent architecture. ORION Paper I already owns mechanic cells, recursive audit, responsibility-based reframing, and dependency-directed reopening inside the ORION programme. The contribution here is the higher-order contract and theorems linking those mechanisms to certified scientific state.

## 2. Related work and donor boundaries

### 2.1 Truth maintenance and dependency repair

Doyle's Truth Maintenance System records justifications and supports dependency-directed revision; de Kleer's ATMS extends maintenance to assumption sets and multiple environments. These systems establish that explicit dependency structure can support selective retraction and consistency maintenance. Contemporary agent-repair systems carry the same basic insight into execution traces: AgentTether builds a dependency-aware critical-transition graph, and Dependency-Guided Rollback Repair traces memory-to-action dependencies, invalidates downstream unsupported state, preserves independently supported state, and selectively replays affected computation.

ORION-16 therefore does not claim selective repair. Its additional question is what counts as *preservable* when a downstream object is not merely a computation but a scientific certificate with evidence, authority and obligation premises.

### 2.2 Self-adjusting and incremental computation

Adaptive functional programming and self-adjusting computation represent execution dependences with dynamic dependence graphs and use change propagation to update a computation after inputs change. Correctness is typically stated against from-scratch recomputation. This is a strong parent for ORION-16's computational repair layer.

ORION-16 explicitly embeds this as a special case by making scientific certification obligations and mutation authority inert. The typed-erasure theorem then identifies the converse limitation: from-scratch computational correctness does not decide certification or commit authority once those dimensions are active.

### 2.3 Dynamic epistemic logic and belief revision

Dynamic epistemic logic provides semantic models for actions that change knowledge; AGM and its descendants formalize rational belief-state revision. These are direct parents for informational mechanics. ORION-16 does not claim a new theory of belief update. Its state coordinates may include propositions, but also representations, measurements, procedures, provenance identities, resource state and authority-bearing certificates.

### 2.4 Separation, effects and process structure

Separation and process formalisms establish locality, independence, concurrency and trace equivalence. Effect systems track computational effects, and algebraic-effect structures separate requests from handlers. ETAS brings these ideas directly into agent systems, making typed actions and traces semantic elements and retaining residual obligations when static proof is incomplete. FAVA constructs evidence-backed permission graphs and checks permission before effectful execution.

ORION-16 adopts rather than claims these mechanisms. Its composition theorem therefore uses a **full scientific footprint**, not only ordinary read/write state, and its main new separation question concerns the admissibility of scientifically certified effects.

### 2.5 Authorization and provenance

Authorization logics, trust management, usage-control systems, provenance models and audit logics already formalize permission, delegation, revocation, lineage and ongoing policy checks. ORION-18 in the ORION programme owns the cross-domain authority theory. ORION-16 uses authority only to constrain mechanic composition and repair.

## 3. Formal setting

Let

\[
\Sigma=(C,(V_c)_{c\in C},Q,\mathcal O,\mathcal A,\mathcal F)
\]

be an epistemic signature. A state is

\[
E=(\nu,s,D,P,O,A,H),
\]

with typed coordinate valuation `\nu`, claim status `s`, dependency relation `D`, provenance `P`, active obligations `O`, authority state `A`, and immutable history `H`.

The current-scientific-state projection

\[
\pi_{sci}(E)=(\nu,s,D,P,O,A)
\]

excludes ordered history. This matters because two independent effect orders can agree on all current scientific facts while remaining distinct executions for audit and later policy.

A mechanic is

\[
m=(R_m,W_m,Pre_m,Req_m,Eff_m,\tau_m,Emit_m,Fail_m,Inv_m).
\]

An admissible transition must satisfy its preconditions, hard evidence and authority requirements, declared footprint, invariants, provenance rules, authority-generation restrictions and residual-obligation rules. A mechanic may therefore be executable but not admissible.

The full formal definitions and proofs are frozen in `FORMAL_CORE_V2.md`; this manuscript states their scientific interpretation and key results.

## 4. Root-inclusive repair

### 4.1 Why strict descendants are insufficient

Suppose a changed set `X` may itself contain a certified claim. A strict descendant operator `Desc_D(X)` does not contain its roots. Therefore a rule reopening only certified strict descendants can leave a directly changed certified claim untouched.

The corrected affected set is

\[
Aff_D(E,X)=
(X\cap Q_{cert}(E))
\cup
(Desc_D(X)\cap Q_{cert}(E)).
\]

### Theorem 1 — reopening sufficiency

If the dependency relation is sound for the chosen abstraction, reopening all of `Aff_D(E,X)` removes every certification that may have been invalidated by changing only `X`.

The proof is exhaustive over the two cases: the invalidated certified claim is itself changed or has a changed ancestor.

### Theorem 2 — graph-relative minimality

If the graph is the only semantic dependency information available, no uniformly sound strategy can preserve any member of `Aff_D(E,X)`. For every omitted root or descendant there exists a compatible semantic realization in which it is genuinely invalidated.

The qualifier **graph-relative** is important. Additional semantic evidence can establish that an apparent dependency is irrelevant to a specific change.

## 5. Preservation certificates

To use such evidence safely, we define a preservation certificate

\[
\kappa=(q,X,issuer,scope,epoch,proof,lineage).
\]

The certificate must be issued outside the candidate transition's authority, bind the exact changed set and certified object, prove invariance of the old derivation under that change, remain fresh, and not allow a directly changed certified root to preserve its old status through its own mutation.

The certificate-aware repair set is

\[
Reopen_D^K(E,X)=Aff_D(E,X)\setminus Pres(E,X,K).
\]

### Theorem 3 — certificate-aware soundness and relative minimality

If the dependency graph and accepted preservation proofs are sound, this operator is sound; among strategies restricted to that information, it is inclusion-minimal.

This theorem makes explicit a useful division of labor. Dependency analysis tells us **where invalidation could propagate**. A preservation proof can establish that a particular possible dependency did not invalidate a particular certificate under the actual change.

## 6. Composition and audit history

Ordinary read/write separation is too weak for epistemic mechanics. Two transitions can write disjoint numerical state while interacting through authority, provenance, obligations or dependency edges.

We therefore define a semantic read footprint `SF(m)` and scientific write footprint `SW(m)` over all current-scientific-state components. Two mechanics are separated when neither writes anything read or written by the other and their authorization/provenance derivations are independent.

### Theorem 4 — history-aware commutation

For deterministic admissible semantically separated mechanics `m,n`,

\[
\pi_{sci}(n(m(E)))=\pi_{sci}(m(n(E))),
\]

while their ordered histories generally differ. The histories are equivalent only under the quotient generated by swapping adjacent independent events.

This prevents a subtle loss of provenance: proving that two effects commute on current scientific state does not entitle the system to erase which one occurred first.

## 7. Authority and obligation conservation

### Theorem 5 — sequential non-escalation

If each mechanic may only retain authority, narrow it, or obtain new authority from a protected root, then every finite sequential composition has the same property.

### Theorem 6 — hard-obligation persistence

If a mechanic emits a hard obligation and no later mechanic executes an authorized discharge rule for it, every later admissible state retains that obligation. Later computational success cannot delete it. If required evidence becomes unavailable, the system may terminate `CANNOT_CHECK`, but it may not silently convert the missing discharge into success.

This theorem captures a recurring scientific failure mode: work succeeds operationally, so an earlier verification or coverage obligation disappears from the record. The contract semantics makes that disappearance inadmissible.

## 8. Recursive mechanics and self-authorization

A recursive audit must decrease a well-founded rank or terminate on a detected cycle. This yields the standard well-founded termination theorem and an immediate countermodel for unguarded self-recursion.

More importantly, recursion does not create authority. If a mechanic can rewrite both the predicate deciding its own promotion and every evidence value that predicate reads, an internally accepting configuration is always reachable independently of the external property the promotion is supposed to establish. Protected roots are therefore semantic premises, not implementation decoration.

## 9. The typed-erasure theorem

Define `Erase(m)` to discard hard obligations, commit authority and provenance rules while retaining the bare computational transition and ordinary dependency graph.

### Theorem 7 — bare computational semantics is not fully abstract for epistemic admissibility

There exist `m_1,m_2` with

\[
Erase(m_1)=Erase(m_2)
\]

but different admissibility judgments.

A minimal construction gives both the transition `0\mapsto1`. The first has a satisfied hard evidence obligation and valid authority; the second lacks one of those premises. The underlying computation is identical, yet only the first may commit as an epistemically admissible scientific transition.

This theorem is the paper's main formal discriminator. It does not say dependency systems are deficient for their intended problem. It says that a system maintaining **scientific authority** needs information that is intentionally absent from a pure computation-dependency abstraction.

## 10. Conservative embeddings

The calculus is designed so that donor mechanisms remain recognizable special cases.

**Ordinary transition systems.** Make obligations, authority, provenance and dependency status inert. Admissibility reduces to the declared transition plus ordinary footprint and invariants.

**Truth maintenance / dependency repair.** Make authority and obligation dimensions inert and remove preservation certificates. Repair reduces to root-inclusive affected-set invalidation.

**Self-adjusting computation.** Represent input/computation dependencies and make scientific certification universally admissible. Change propagation becomes an ordinary mechanic-maintenance instance; ORION-16 does not inherit complexity or efficiency results it has not proved.

**Typed-effect systems.** Embed action effects into `Eff_m`, requirements and trace history; if scientific certification/repair is inert, those extra ORION-16 coordinates do not alter the native effect judgment.

This conservative policy is scientifically important: the general formalism is rejected if it requires rewriting a donor's native decision without an explicit stronger premise.

## 11. Deterministic finite-model support

The theory-closure checker uses only the Python standard library. It is not an LLM evaluation and contains no stochastic judge.

It checks:

- all 64 forward DAGs on four ordered nodes under every nonempty changed subset: 960 graph/change cases;
- 2,048 occurrences in which a certified root is itself changed, verifying the root-inclusive repair condition;
- 64 combinations of preservation-certificate trust, validity, invariance and changed-set binding;
- independent composition on distinct state coordinates, verifying equal scientific projection and different-but-equivalent histories;
- all Boolean combinations relevant to residual-obligation persistence;
- bounded authority non-escalation combinations;
- typed-erasure counterexamples;
- acyclic, mutual-cycle and self-cycle recursive audits;
- dependency-maintenance special cases.

All checks pass in the authored closure run. These are bounded consistency/falsifier checks for the mathematical object, not evidence that real research agents improve.

## 12. Discussion

### 12.1 A preservation ladder

The theory suggests that “preserved after change” is underspecified. At least four questions should be separated:

1. may a computation be reused or incrementally repaired?
2. does a content-bound observation remain semantically valid?
3. do the obligations supporting a certificate remain discharged?
4. is the next state mutation still authorized at the present scope and epoch?

ORION-16 formally separates the first from the latter two. Paper VII develops the second-to-third transition across representations/objectives; Paper VIII develops the third-to-fourth authority boundary.

### 12.2 Why this matters for autonomous science

In conventional software, a correct recomputation result may be sufficient for downstream execution. In autonomous science, the object being maintained can encode a claim whose standing depends on a coverage basis, measurement contract, independent checker, provenance lineage or protected evaluator. Recomputing the value does not necessarily recompute those epistemic premises.

### 12.3 What would falsify the usefulness of the abstraction

The framework is not useful merely because every field can be named in its tuple. It would collapse into taxonomy if real ORION mechanics could not be embedded without ad hoc exceptions, if the additional obligation/authority coordinates never changed any admissibility judgment, or if a mature parent formalism already supplied the same complete object and theorems under equivalent semantics. The typed-erasure theorem establishes only that such additional coordinates can matter, not how often they matter empirically.

## 13. Limitations

First, dependency graphs are abstractions of richer causal and evidential structure. Hypergraphs, alternative derivations and context-dependent support may be required; Paper VIII explicitly uses support families for this reason.

Second, preservation-certificate soundness is assumed, not generated automatically. A false invariance proof can unsafely preserve a stale certificate.

Third, the finite checker explores small exact structures. It is designed to catch theorem-boundary errors, not to estimate real-world frequency or performance.

Fourth, the paper does not establish global novelty. The field spans decades of truth maintenance, dynamic epistemic logic, belief revision, incremental computation, effects, authorization and provenance, plus rapidly moving agent-specific work. The contribution is therefore stated as a scoped synthesis and separation theorem, without “first” or “only” language.

## 14. Conclusion

Scientific agents need to know not only how to update state but what remains **scientifically entitled** after an update. We introduced a typed mechanic-contract semantics in which dependency repair, evidence obligations, provenance, authority and history interact explicitly. Root-inclusive certificate-aware reopening fixes a direct-certification gap; semantic-footprint separation distinguishes current-state commutation from history identity; obligation and authority conservation prevent success from laundering unresolved requirements; and typed erasure proves that computationally identical changes can differ in epistemic admissibility.

The result is not a replacement for truth maintenance, self-adjusting computation, effect systems or authorization. It is an interface for using those mechanisms when the maintained state carries scientific certification.

**Theory terminal:** `CLOSED_V2`.

## References

1. Jon Doyle. **A Truth Maintenance System.** *Artificial Intelligence* 12(3), 231–272, 1979. DOI: 10.1016/0004-3702(79)90008-0.
2. Johan de Kleer. **An Assumption-Based TMS.** *Artificial Intelligence* 28(2), 127–162, 1986. DOI: 10.1016/0004-3702(86)90080-9.
3. Umut A. Acar, Guy E. Blelloch, and Robert Harper. **Adaptive Functional Programming.** POPL, 2002; later journal development on adaptive functional programming and dynamic dependence graphs.
4. Hans van Ditmarsch, Wiebe van der Hoek, and Barteld Kooi. **Dynamic Epistemic Logic.** Springer, 2007.
5. Carlos E. Alchourrón, Peter Gärdenfors, and David Makinson. **On the Logic of Theory Change: Partial Meet Contraction and Revision Functions.** *Journal of Symbolic Logic* 50(2), 1985.
6. Huiri Tan, Yikun Wang, Puyang Zhang, Shangyu Li, and Jiasi Shen. **ETAS: An Effect-Typed Language for Agent Systems.** arXiv:2607.17780, 2026.
7. Yifan Zhang et al. **FAVA: Formal Authorization for Verified Agents with Evidence-Backed Permission Graphs.** arXiv:2607.27267, 2026.
8. Chenyu Zhao et al. **AgentTether: Graph-Guided Diagnosis and Runtime Intervention for Reliable LLM Agent Operation.** arXiv:2607.06273, 2026.
9. Caili Yu et al. **From Faulty Memories to Corrected Actions: Dependency-Guided Rollback Repair for Memory-Augmented Agents.** arXiv:2608.10502, 2026.
10. Sumers et al. **Cognitive Architectures for Language Agents (CoALA).** arXiv:2309.02427, 2023.

## Artifact map

- Formal definitions/proofs: `FORMAL_CORE_V2.md`
- Deterministic theorem checker: `../formal/check_theory_closure_v2.py`
- Earlier exploratory manuscript: `DRAFT.md`
- Claim authority: `../CLAIM_LEDGER_V2.md`
- Reproduction: `../REPRODUCE.md`
