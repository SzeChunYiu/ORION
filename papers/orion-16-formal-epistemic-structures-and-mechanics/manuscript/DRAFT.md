# Formal Epistemic Structures and Mechanics

**Working manuscript — candidate ORION-16 — 2026-08-17**

## Abstract

Autonomous research systems increasingly combine planning, retrieval, memory, reflection, verification, authorization and tool use, yet these capabilities are usually connected through implementation conventions rather than a common formal contract. This paper asks whether the mechanisms that *change* an agent's epistemic state can themselves be modeled as first-class epistemic objects. We develop a candidate calculus in which a mechanic has typed read/write footprints, preconditions, hard and soft residual obligations, requested and committed effects, dependency/provenance structure, scoped authority, failure terminals, invariants and retained audit history. The formalism deliberately absorbs rather than competes with mature parent ideas: dynamic epistemic logic supplies action/update semantics; belief revision supplies rational change operators; truth-maintenance and recent dependency-guided rollback supply selective invalidation and preservation; separation/process logics supply locality; ETAS supplies typed effects, residual obligations and trace-visible commits; FAVA supplies evidence-backed permission graphs and deterministic pre-effect authorization; recent agent-repair work supplies dependency-aware transition localization. The candidate contribution, if one survives, is therefore not any component in isolation but a history-aware epistemic effect/repair algebra coupling commit authority, dependency-minimal reopening, residual obligations, frame-style preservation and recursive audit. We prove elementary reopening, non-escalation, termination and history-aware commutation properties, give self-authorization countermodels, and specify donor-faithful embeddings and cross-domain falsifiers. ORION-16 remains `CANNOT_CHECK` for distinct novelty until these embeddings, external nearest-work saturation and prospective transfer tests close.

## 1. Introduction

A research agent does more than transform text. It maintains representations of what is known, what remains unresolved, what search universe is currently relevant, which procedure is in force, what evidence licenses which actions, and which prior conclusions depend on assumptions that may later fail. Errors in one of these objects can propagate into later retrieval, reasoning, memory writes, claims and self-modification.

Modern agent architectures expose many of these concerns as modules—memory, planning, reflection, tools, verification, runtime policy—but module names do not specify control semantics. Two systems can both have a planner and a critic while differing fundamentally in what either component may mutate, what evidence is required before committing a change, which conclusions must reopen afterward, and what failures remain in history.

ORION already contains several domain-specific instances of this problem. ORION-11 owns the canonical `K/W/M` epistemic reconstruction, responsibility-targeted reframing, dependency-directed reopening, `MechanicCell.v1` and recursive mechanic self-audit. ORION-12 owns route coverage and stopping. ORION-13 owns source projection and obstruction-preserving integration. ORION-14 owns protected scientific-authority promotion. ORION-15 owns failure-to-method learning and protected self-improvement. ORION-16 therefore cannot acquire novelty by describing these objects at a higher level.

The broader research question is whether these instances—and strong external systems—can be embedded in one formal language of **epistemic transition contracts** without erasing the unique semantics that make each system useful.

## 2. Epistemic states and transition contracts

Let an epistemic signature contain typed state coordinates `C`, value domains `V_c`, claim identifiers `Q`, obligation types, authority types and effect kinds. An epistemic state is provisionally

\[
E=(\nu,s,D,P,O,A,H),
\]

where `\nu` is the current coordinate valuation, `s` records claim/certificate status, `D` is a dependency relation or hypergraph projection, `P` binds provenance/evidence identities, `O` contains active obligations, `A` contains active authority tokens/certificates, and `H` retains requests, commits, failures, invalidations and other audit-relevant history.

A mechanic is

\[
m=(R_m,W_m,Pre_m,Req_m,Eff_m,\tau_m,Emit_m,Fail_m,Inv_m).
\]

The difference from a plain transition function is contractual. A mechanic declares what it may read and write, what hard requirements must be established before a commit, which effects are merely requested versus actually committed, what residual obligations are emitted, what provenance and authority are required, and which invariants must remain true.

The distinction between requested and committed effects is not claimed as new. ETAS (arXiv:2607.17780) already makes typed action traces, residual obligations, requested/handled/denied/committed events and policy safety explicit. FAVA (arXiv:2607.27267) already lowers natural-language permission intent into evidence-backed permission graphs and uses a deterministic SMT authorizer before effectful actions. ORION-16 adopts these as donor mechanisms.

The ORION-16 question is what happens when effect authorization is coupled to **epistemic dependency repair** and recursive scientific workflow state.

## 3. Selective reopening as a repair operator

Suppose a set `X` of upstream coordinates changes. A system can reset everything, reset nothing, or reopen only state that depended on the changed coordinates.

Let `Desc_D(X)` be the transitive downstream closure under a dependency graph `D`. Under a dependency-soundness assumption, the reopening operator invalidates every certified descendant of `X`, preserves independent certified state, records the invalidation cause in history, and retains content-bound provenance.

Two elementary results follow.

**Sufficiency.** If `D` contains every semantic support that can affect a certified claim, reopening every certified descendant of `X` prevents stale affected certification.

**Graph-information minimality.** If the only available semantic dependency information is `D` and a strategy must be sound for every semantics compatible with `D`, then every certified descendant of `X` must reopen. Full reset is sound but non-minimal whenever independent certified state exists outside the descendant closure.

These are structural results, not novelty claims. Truth-maintenance systems have long studied justification-dependent retraction, and recent dependency-guided rollback repair for memory-augmented agents (arXiv:2608.10502) explicitly builds a typed memory-to-action graph, removes downstream effects of faulty memories, preserves independently supported benign memories and selectively replays affected computation. ORION-16 must therefore demonstrate a genuine generalization across heterogeneous epistemic coordinates, effects and authority-bearing commits rather than claiming selective rollback itself.

## 4. Composition and history-aware commutation

ORION-16 distinguishes sequential, conditional, separated-parallel and recursive composition.

For separated mechanics `m` and `n`, each write set is disjoint from the other's read/write footprint, and neither mechanic mutates authority, dependencies, obligations, provenance or invariants consumed by the other.

An earlier draft made an over-strong claim: that independent execution orders produce the same entire state. This is false when `H` intentionally records ordered history. The corrected theorem uses a scientific projection

\[
\pi_{sci}(E)=(\nu,s,D,P,O,A)
\]

and a trace equivalence `\equiv_I` generated by swapping adjacent independent events.

For deterministic admissible strongly separated mechanics,

\[
\pi_{sci}(\tau_n(\tau_m(E)))
=
\pi_{sci}(\tau_m(\tau_n(E))),
\]

while the histories satisfy only

\[
H_{mn}\equiv_I H_{nm}.
\]

This distinction matters operationally. Scientific state can commute while audit chronology remains recoverable.

A second composition property is non-escalation. If each mechanic can only retain authority, narrow its scope, or receive authority from a protected root, sequential composition cannot mint stronger untrusted authority. ORION-18 owns the general authority calculus; ORION-16 uses the result as a mechanic-composition invariant.

A further theorem target concerns **residual-obligation preservation**: a hard obligation emitted by one mechanic must survive composition until explicitly discharged by an authorized rule or terminated as `CANNOT_CHECK`. Later computational success cannot erase it implicitly.

## 5. Recursive audit and self-authorization

A mechanic may inspect a representation of itself or its parent composition. Recursive audit is useful but creates immediate termination and governance problems.

If every recursive call strictly decreases a rank in a well-founded order, termination follows by the standard descending-chain argument. Without such a condition, an auditor can recursively invoke the identical unresolved audit state forever.

More importantly, recursive audit cannot be allowed to rewrite both the predicate and all evidence that decide its own promotion if the desired promotion property is external to the candidate. A constant-accepting self-written predicate is an explicit countermodel. ORION-15 already owns the protected self-change/no-self-promotion mechanism; ORION-16 uses this as a boundary condition for recursive mechanic semantics.

## 6. Donor assimilation rather than avoidance

ORION-16 is intentionally constructed from strong donors.

### Dynamic epistemic logic and belief revision
Dynamic epistemic/action logics already provide formal model-changing actions; AGM and iterated-revision theory already provide rational postulates for belief change. ORION-16 treats these as special mechanic families, not novelty targets.

### Truth maintenance and dependency repair
Dependency-directed invalidation is prior art. The contribution question begins only when repair is coupled to typed effects, authority, residual obligations, provenance and recursive mechanic composition.

### Separation, process and effect systems
Locality, frame reasoning, commutation and effect typing are mature. ORION-16 imports these proof patterns and must state exactly where retained ordered history or epistemic obligations change the composition problem.

### Agent architecture and repair
CoALA (arXiv:2309.02427) supplies modular language-agent architecture. The 2026 mechanism-level review (arXiv:2607.23942) already reconstructs mechanisms through state, control, transition, persistence, failure, learning and resource governance. AgentTether (arXiv:2607.06273) introduces Transition Units and a Critical Transition Graph for failure localization and repair. These are direct architecture/repair donors.

### Effect and authorization languages
ETAS and FAVA sharply raise ORION-16's burden. ORION-16 cannot claim typed actions, residual obligations, policy traces, permission graphs or deterministic authorization. Instead, the candidate must demonstrate a cross-mechanic epistemic repair/composition property that survives when these mechanisms are treated as embedded components.

## 7. A widened candidate object

The current ORION-16 candidate is a **history-aware epistemic effect/repair algebra** with the following coupled structure:

\[
\text{typed state/effects}
+
\text{hard residual obligations}
+
\text{content-bound provenance}
+
\text{scoped commit authority}
+
\text{dependency repair}
+
\text{frame/separation conditions}
+
\text{retained audit history}
+
\text{recursive audit under protected roots}.
\]

This is broader than the original chain from responsibility to reopening, but broader vocabulary is not itself a paper. The scientific burden is to show that these components generate new composition obligations or transfer predictions when combined.

## 8. Donor-faithful embedding requirement

Each adopted donor must have a conservative embedding into the relevant ORION-16 projection. When ORION-16-specific dimensions are inert, the embedding should preserve the donor's decisive native judgments: update, allow/deny, rollback, locality or trace behavior.

A purported generalization that changes a donor's native verdict merely so that ORION can subsume it is invalid.

The same rule applies internally. ORION-11 native `MechanicCell.v1`, recursive-audit and reconstruction fixtures must remain ORION-11-owned and reproduce their existing decisions under the ORION-16 representation.

## 9. Deterministic falsifiers

The first Python-standard-library checker is committed under `papers/candidates/checkers/p6_finite_falsifiers_v1.py`. It currently exercises five bounded cases:

1. affected descendants reopen while independent certified state is preserved;
2. separated mechanics commute on current scientific state but preserve different ordered histories;
3. untrusted authority cannot be minted by the toy composition;
4. a later successful computation does not erase an unresolved hard obligation;
5. recursive self-loop and candidate-controlled admission countermodels are representable.

The current local run is 5/5 PASS. This supports the definitions and catches regressions; it is not a proof of the unrestricted calculus.

The next version should perform exhaustive bounded enumeration rather than only hand-constructed fixtures.

## 10. Cross-domain evaluation

ORION-16 must transfer outside the ORION-11 reconstruction setting. #353 requires at least:

- exact-ground-truth symbolic workflow systems;
- memory/state repair with selective rollback;
- effectful tool workflows with authorization-bearing commits;
- a negative-control family where a simple transition graph or full reset is sufficient and the extra contract should add no benefit.

The comparator set must include donor-specific systems, not merely an untyped strawman. In particular, dependency-guided rollback, effect-typed policy representations and evidence-backed authorization graphs should be treated as strong components/baselines where implementable.

Potential outcomes include invalid-composition detection, stale-state prevention, preservation of unaffected state, unnecessary reopening, unauthorized commits, residual-obligation loss, repair cost and audit recoverability.

## 11. Exact boundary against ORION-11–ORION-15

The V1 ownership matrix marks native ORION-11 mechanic cells, recursive audit and reconstruction reopening as `MERGE_EXISTING`. ORION-14/ORION-15 retain ownership of their authority/promotion mechanisms. ORION-16 survives only if the donor-faithful algebra creates a distinct theorem or transfer behavior beyond these native cases.

This makes a collapse into ORION-11 or a technical companion a scientifically valid terminal.

## 12. Limitations

The formalism may remain explanatory notation rather than a distinct calculus. Dependency graphs can be incomplete. Authority roots can be wrong. Typed state extraction from language-agent execution may require judgment. Local structural soundness does not imply scientific truth. The algebra may be too general to improve implementations, or too implementation-specific to interest formal-methods readers. Bounded finite checking cannot establish unbounded recursive correctness.

Most importantly, several of the strongest-looking ORION-16 components are already owned either by classical theory, current external systems, or ORION-11/ORION-15. A publishable ORION-16 must earn its existence through composition results rather than scope expansion.

## 13. Conclusion

ORION-16 asks whether autonomous research workflows can be treated as compositions of epistemic effect contracts whose commits, residual obligations, dependencies, authority and audit history are explicit. The current programme deliberately absorbs stronger prior mechanisms instead of narrowing around them. The paper remains a candidate until conservative donor embeddings, theorem checking, ORION-11–ORION-15 ownership audit and cross-domain prospective tests show that the composition itself has scientific value.