# Formal Epistemic Structures and Mechanics

**Working manuscript — candidate ORION-16 — 2026-08-17**

## Abstract

Autonomous research agents increasingly combine planning, memory, retrieval, reflection, verification and tool use, but the mechanisms controlling these capabilities are usually described operationally rather than as first-class epistemic objects. ORION currently represents scientific work using explicit state coordinates, obligations, mechanic cells, dependencies, authority bounds and recursive audit. This paper investigates whether those ingredients admit a reusable formal semantics. We propose to model an epistemic mechanic as a typed state transformer whose read/write domain, evidence obligations, authority, emitted obligations, failure terminals and dependency effects are explicit. We then study composition, selective invalidation and recursive self-audit. The central hypothesis is not that state machines, belief revision or modular cognitive architectures are new. It is that coupling **typed responsibility and obligations to explicit mutation authority and dependency-scoped reopening** may yield a distinct calculus for research-agent mechanics. Novelty and empirical value remain unestablished pending nearest-work saturation and prospective evaluation.

## 1. Introduction

A research agent does more than transform text. It maintains a changing representation of what is known, what remains unresolved, what procedure is currently in force, what evidence licenses which actions, and what prior conclusions depend on assumptions that may later fail.

Contemporary language-agent architectures make many of these elements visible as modules—memory, planning, reflection, tools, verification—but module names do not by themselves specify control semantics. Two systems can both contain a planner and a critic while differing radically in what either component is allowed to change after failure.

ORION's existing papers expose this control problem repeatedly. ORION-11 distinguishes knowledge, epistemic/world obligations and mechanics while using responsibility to decide whether a failure licenses reformulation. ORION-12 distinguishes route exhaustion from task closure. ORION-13 separates semantic similarity from authorized integration. ORION-14 separates evidence accumulation from scientific-authority promotion. ORION-15 separates successful modification from authorization to self-promote.

This manuscript asks whether there is a formal substrate beneath these examples.

The intended contribution, if it survives nearest-work pressure, is a calculus in which a mechanic is not merely a function from input to output. It is a contract over epistemic state.

## 2. State and mechanics

Let an epistemic state be a typed object

`E = (K, W, M, O, D, P, A, H)`

where, provisionally:

- `K` contains content treated as current knowledge/evidence-bearing claims;
- `W` contains problem/world representation and open research coordinates;
- `M` contains active mechanics/procedures;
- `O` contains unresolved obligations and defeaters;
- `D` is a dependency relation over claims, obligations and mechanics;
- `P` records provenance/evidence identity;
- `A` records authority/licensing state;
- `H` retains negative history and prior invalidated states where required.

This tuple is a research hypothesis, not yet the canonical ORION schema. #333 must map every coordinate to actual registry objects or strike it.

A mechanic `m` is tentatively represented as

`m = (R, W, Pre, Ev, T, Emit, Fail, Auth, Inv)`

where `R/W` are readable/writable state domains, `Pre` preconditions, `Ev` evidence obligations, `T` the transition relation, `Emit` newly emitted claims/obligations, `Fail` typed failure terminals, `Auth` authority required or produced, and `Inv` invariants that must survive execution.

The key distinction is between **ability to compute a transition** and **authority to commit it**.

## 3. Composition

We plan to define at least four composition forms.

**Sequential composition.** `m2 ∘ m1` is well formed only if outputs and invariants of `m1` satisfy the preconditions/read requirements of `m2`, and `m2` does not write coordinates for which authority is absent.

**Conditional composition.** A mechanic may branch on explicit evidence/diagnostic state. Branch conditions must be represented rather than hidden in prose or prompting.

**Parallel/independent composition.** Mechanics may execute independently only if their write sets and dependency effects are compatible. Structural independence must not be inferred from superficial naming.

**Recursive self-audit.** A mechanic may inspect a representation of itself or its parent composition. This creates immediate questions about termination, fixed points, authority escalation and whether an auditor can rewrite the contract that grants its own authority.

## 4. Dependency-scoped reopening

When an upstream coordinate changes, a research system can reset everything, reset nothing, or invalidate only dependent closures.

Let `D(x)` denote the transitive downstream dependency set of a changed state element `x`. A selective reopening operator tentatively has the form

`Reopen(E, x) = invalidate(D(x)) + preserve(E \ D(x))`

subject to provenance and authority conditions.

The difficult part is not graph reachability. It is deciding **which change is epistemically licensed** and therefore which dependency relation is relevant. ORION-11 currently owns the empirical reconstruction version of this idea; ORION-16 requires a more general formal property or should be merged into ORION-11.

## 5. Candidate invariants

We will pressure at least these invariants:

1. **Mutation locality:** a mechanic cannot commit writes outside its authorized write domain.
2. **Non-escalation:** successful execution cannot silently grant stronger authority than its evidence obligations permit.
3. **Dependency soundness:** changing an upstream coordinate cannot leave a dependent closure certified without an explicit preservation proof.
4. **Unrelated preservation:** selective reopening should not invalidate independent certified state.
5. **Provenance preservation:** every retained or promoted claim remains traceable to supporting evidence identity.
6. **Negative-history retention:** a failed/rejected transition cannot disappear when that history is needed for recurrence or governance.
7. **No self-authorization:** recursive audit cannot promote changes to the rules that authorize its own promotion without an external/independent authority path.

These are candidate properties, not established theorems.

## 6. Relationship to prior work

ORION-16 sits under heavy prior-work pressure. Dynamic epistemic logic already models knowledge-changing actions and model transformations. AGM and later belief-revision theory formalize expansion, contraction and revision. Truth-maintenance and dependency-directed systems study dependency-aware revision. Hyperintensional approaches weaken idealized equivalence assumptions. Separation and process logics provide tools for local state ownership and compositional reasoning. Cognitive-architecture work and CoALA provide modular descriptions of language agents. Recent mechanism-level reviews explicitly reconstruct agent systems in terms such as state, control, transition, persistence, failure, learning and resource governance.

Therefore the paper cannot claim novelty for formalizing change, modules or dependencies.

The residual question is whether prior formalisms already combine the following relation in one operationally grounded object:

`typed responsibility/evidence obligation -> mutation authority -> dependency-scoped reopening -> recursively composable mechanic contract`.

#334 owns that saturation decision.

## 7. Evaluation plan

A formal paper still needs falsification.

We propose three evidence layers.

**Formal counterexamples/checking.** Generate bounded mechanic/state configurations containing authority escalation, invalid composition, stale dependent closure and recursive cycles; test whether a checker derived from the calculus detects them.

**Executable correspondence.** Map selected current ORION mechanics into the formal representation. Record coverage gaps instead of inventing fields after the fact.

**Discriminating comparison.** Compare against an untyped state-machine/dependency representation on the same hostile cases. The candidate calculus should add value only if typing authority/evidence/dependency relations catches errors or preserves valid state more precisely.

An empirical positive must route through #283; novelty must route through #287.

## 8. Limitations

The formalism may prove to be an explanatory notation rather than a novel calculus. Mapping messy language-agent execution to typed state may require judgment. Formal safety properties do not imply scientific correctness. Bounded model checking does not establish correctness at unrestricted recursion depth. ORION-11 may remain the proper home if the only useful results are reconstruction-specific.

## 9. Conclusion

The candidate thesis is that reliable autonomous research requires explicit semantics not only for knowledge but for the **mechanics that are allowed to change knowledge and problem structure**. ORION-16 will be retained only if that thesis yields a distinct formal residual, nontrivial properties, and evidence beyond a restatement of existing ORION papers or classical belief-change formalisms.
