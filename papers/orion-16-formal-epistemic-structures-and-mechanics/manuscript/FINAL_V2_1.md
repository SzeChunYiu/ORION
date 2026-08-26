# Formal Epistemic Structures and Mechanics

**Paper VI candidate — final theory manuscript V2.1**  
**Date:** 2026-08-18  
**Normative formal core:** `FORMAL_CORE_V2_1.md`  
**Theory terminal:** `FINISHED_V2_1`

## Abstract

Scientific agents change more than propositional belief. They mutate representations, search universes, measurements, procedures, evidence bindings, certified claims, obligations and sometimes the mechanisms governing later changes. Existing theory already supplies powerful components: dynamic epistemic logic and belief revision formalize epistemic updates; TMS/ATMS and self-adjusting computation propagate dependency changes; process/separation theories support local composition; effect systems track requested and residual effects; authorization and provenance systems constrain effectful action. Rather than avoid these structures, we treat them as donors inside a larger epistemic mechanic contract and ask what additional semantics are required when the maintained state carries **scientific certification**.

A mechanic declares a faithful semantic read/write interface, hard evidence and authority requirements, typed effects, invariants, emitted obligations, provenance and failure terminals. We prove safe root-inclusive reopening under a support-sound dependency abstraction. We show by counterexample that support soundness alone does **not** imply descendant minimality when conservative/spurious edges are allowed, and give a corrected minimax theorem under an explicit affected-realizability condition. Protected exact-change preservation/revalidation certificates can safely avoid unnecessary invalidation. We further prove history-aware commutation under faithful full scientific separation, sequential authority non-escalation, hard-obligation persistence and a recursive-audit boundary. The main separation theorem shows that two contracts can have identical bare computation/dependency semantics but different scientific admissibility because obligation or commit-authority premises differ.

Deterministic finite checkers exercise all forward DAGs on four ordered nodes under all nonempty changed subsets, spurious-edge and affected-realizability countermodels, footprint-fidelity failures, preservation/revalidation cases, obligation persistence, authority composition and recursive cycles. The contribution is intentionally scoped: dependency repair, incremental computation, typed effects, authorization and provenance remain donor-owned. ORION-16 contributes the scientific-admissibility layer over their composition.

## 1. Motivation

A computation can be correct yet scientifically unauthorized. A dependency graph can identify which derived values might change yet not determine which scientific certificates remain entitled to stand. A requested effect can be type-correct yet lack the evidence required to mutate a protected formulation coordinate. A later successful calculation can leave an earlier verification obligation unresolved.

These distinctions become unavoidable in autonomous science because state elements carry different meanings. Some are raw computational values. Others are claims whose standing depends on evidence lineage, coverage, measurement semantics, independent checks or protected evaluation. Treating them all as ordinary mutable state creates a failure mode in which *computational continuity* is silently converted into *epistemic continuity*.

ORION-16 addresses the interface between these layers. It does not replace the donor theories that solve their native problems. It defines the extra contract needed when those mechanisms maintain scientifically certified state.

## 2. Donor-complete stance

The framework explicitly engulfs, rather than excludes, the following parent structures.

### Truth maintenance and dependency repair

TMS/JTMS/ATMS provide justifications, dependency-directed revision and multiple support environments. Modern agent repair work similarly uses trajectory or memory-to-action dependencies to localize failure and preserve independent support. ORION-16 therefore claims no novelty for selective invalidation.

### Self-adjusting and incremental computation

Dynamic dependence/change-propagation systems update computations after inputs change and target from-scratch-consistent results. ORION-16 embeds this as the computational repair layer. Its question is what additional facts are needed before reusing a **scientific certificate**, not whether incremental recomputation is useful.

### Epistemic update and belief revision

Dynamic epistemic logic and AGM-style revision already formalize knowledge/belief change. ORION-16 broadens the state signature to non-propositional scientific coordinates but does not claim a new general theory of belief update.

### Effects, authorization and provenance

Typed effects, ETAS-like residual obligations, FAVA-like evidence-backed authorization, trust-management/usage-control structures, and provenance/audit systems are all donor mechanisms. They remain visible inside the ORION envelope with their native ownership.

The strongest future comparator is therefore not an isolated TMS or effect system. It is an integrated donor product containing repair + incremental computation + typed effects + authorization + provenance with correct interfaces.

### Non-contributions and internal ownership

The per-donor disclaimers above state what ORION-16 does not claim against the external literature. This subsection states the same for the ORION programme, which the donor stance does not cover.

ORION Paper I already owns mechanic cells, recursive audit, responsibility-based reframing and dependency-directed reopening. In particular, `ORION-11.D2` — the surviving ORION-11 delta after Iris (`arXiv:2608.02143`) and ARTS (`arXiv:2606.21891`) narrowed it — is the **licensing relation**: the *type* of responsibility determines the authority to rewrite a formulation/search-universe coordinate, and the rewritten coordinate then scopes reopening. ORION-16 claims none of it.

The separation is not a difference of vocabulary. `ORION-11.D2` decides *whether a coordinate may be rewritten and on whose authority*; ORION-16 decides *what must be reopened once something has changed, and whether that set can be minimal*. Each settles a case the other cannot see. Holding the dependency graph `D` and the changed set `X` fixed and varying only the responsibility type leaves `Aff_D(E,X)` unchanged, so ORION-16 returns one answer where `ORION-11.D2` returns two. Conversely, the spurious-edge countermodel of §5 varies the admissible semantics class while holding responsibility type and rewritten coordinate fixed, so `ORION-11.D2` returns one answer where ORION-16's minimality verdict differs.

ORION-16 must therefore not restate responsibility-typed authority to rewrite a formulation coordinate; doing so would collapse this paper into `ORION-11.D2` rather than extend it. ORION-15 owns protected self-change promotion and ORION-18 owns the general authority calculus, as noted in §10.

## 3. Epistemic mechanic contracts

Let an epistemic state be

\[
E=(\nu,s,D,P,O,A,H),
\]

where `ν` is typed state, `s` scientific claim/certificate status, `D` dependency structure, `P` provenance, `O` active obligations, `A` authority state, and `H` immutable transition/failure/revocation history.

A mechanic is

\[
m=(R,W,Pre,Req,Eff,\tau,Emit,Fail,Inv).
\]

An admissible commit requires not only a valid computational transition but also satisfied hard requirements, faithful declared mutation scope, valid commit authority, preserved invariants, provenance for newly created scientific objects, and retention of every undischarged hard obligation.

This makes explicit a relation central to the paper:

\[
\text{computationally executable}\not\Rightarrow\text{epistemically admissible}.
\]

## 4. Safe root-inclusive repair

For changed set `X`, a strict descendant closure omits a certified root that is itself changed. We therefore define

\[
Aff_D(E,X)=
(X\cap Q_{cert}(E))
\cup
(Desc_D(X)\cap Q_{cert}(E)).
\]

### Theorem 1 — safety under support soundness

If the dependency abstraction is support-sound—every actual support whose mutation could invalidate a certified claim is represented by the changed claim itself or an ancestor path—then reopening/revalidating every claim in `Aff_D(E,X)` leaves no potentially invalidated certification standing.

This is an over-approximate safety theorem. It deliberately permits conservative graph edges.

## 5. Why soundness is not minimality

A sound dependency graph may contain edges that do not represent actual necessary support.

### Counterexample — spurious edge

Let the graph contain `x→q`, but suppose the entire admissible semantics class says that `q` depends only on independent coordinate `y` and is invariant under changes to `x`. The graph remains support-sound because it omits no real support. Nevertheless, reopening `q` after changing `x` is unnecessary in this class.

Hence:

\[
\text{support soundness alone}
\not\Rightarrow
\text{minimal graph-descendant reopening}.
\]

This correction is important because it separates two roles of a dependency abstraction:

- sound over-approximation for safety;
- realizable uncertainty set for minimax necessity.

## 6. Robust graph-only minimality

Minimality becomes valid only after defining the semantics class against which a graph-only policy must be robust.

### Definition — affected realizability

A compatible semantics class is affected-realizable for `(E,X)` when, for every `q∈Aff_D(E,X)`, there exists a semantics consistent with the same graph-visible information in which the declared change invalidates the old certification of `q`—directly for a changed certified root, or through necessary support along a graph path for a descendant.

### Theorem 2 — minimax minimality under affected realizability

Any strategy that observes only the graph, changed set and pre-change certification and must remain sound for every affected-realizable compatible semantics must invalidate or protectedly revalidate every member of `Aff_D(E,X)`. Root-inclusive affected-set reopening is inclusion-minimal among such uniformly sound graph-only policies.

The proof is adversarial: if a strategy preserves any affected `q` without revalidation, the realizability premise supplies a graph-indistinguishable semantics where that exact decision leaves a stale certificate.

This theorem makes no claim that a real ORION graph is exact or that every recorded edge is realizable. Those are separate modeling/evidence questions.

## 7. Preservation versus revalidation

Conservative dependency structure can reopen too much. A protected proof can sometimes show that a downstream certificate is invariant under the exact change.

A preservation certificate binds:

- the exact changed set;
- claim/content identity;
- scope and epoch;
- protected issuer;
- a proof that the old derivation remains valid.

A directly changed certified claim is treated differently. It cannot simply **preserve its old certification** through continuity; it may end certified only via a new protected revalidation/re-certification derivation after the mutation.

This distinction prevents a changed claim from laundering its previous authority through an old certificate while still allowing legitimate protected re-certification.

## 8. Composition requires faithful footprints

Declared read/write sets are only meaningful if enforced.

A mechanic is read-footprint faithful when all requested effects, output mutations, obligation emissions and failure decisions depend only on declared semantic inputs or explicitly registered external inputs. It is write-footprint faithful when every committed mutation lies inside the declared effect/write interface.

### Counterexample — hidden ambient read

If mechanic `m` secretly reads mutable ambient variable `z` but omits it from its interface, and independent-looking mechanic `n` writes `z`, the two declared footprints can appear separated while execution order changes `m`'s result.

Thus **declared separation without fidelity is not a commutation theorem**.

### Theorem 3 — history-aware commutation

For deterministic admissible footprint-faithful mechanics that are fully scientifically separated—including state, obligations, authority, provenance, dependencies, resources and declared external inputs—the current scientific projection is equal in both sequential orders.

Their ordered histories need not be equal; independent commit events are instead equivalent under a trace congruence that permits swapping adjacent independent events.

This keeps audit chronology available for later policies without mistaking chronology for a current-state difference.

## 9. Obligation and authority conservation

### Sequential non-escalation

If each mechanic may only retain authority, narrow it, or acquire new authority from a protected root, any finite sequential composition has the same property.

### Hard-obligation persistence

If a mechanic emits a hard scientific obligation, later computational success cannot erase it. The obligation remains until a transition executes an authorized discharge with valid evidence and lineage. If the required information becomes unavailable, `CANNOT_CHECK` is an honest terminal; silent success is not.

These laws are especially important after engulfing effect systems and repair systems: a computational effect can finish while a scientific obligation remains open.

## 10. Recursive audit and self-authorization

Recursive audit terminates when each recursive call decreases a well-founded rank or a cycle detector stops repeated states. Unguarded same-state recursion yields an immediate infinite countermodel.

Recursion also cannot create promotion authority. If a candidate controls both its own admission predicate and all evidence inspected by that predicate, an internally accepting state can be manufactured independently of an external correctness property. ORION-16 uses this only as a boundary; ORION-18 develops the general authority calculus and ORION-15 owns protected self-change promotion inside ORION.

## 11. Typed-erasure separation

Define `Erase(m)` to remove hard scientific obligations, commit authority and provenance constraints while keeping the bare computation and ordinary dependency graph.

### Theorem 4 — erasure is not fully abstract for scientific admissibility

There exist mechanic contracts `m1,m2` with identical erasures but different admissibility judgments.

The minimal construction gives both the same state transition. One has satisfied evidence obligations and valid authority; the other lacks a mandatory premise. Computational semantics is identical, but only the first may commit as a scientifically admissible transition.

This is the core ORION-16 discriminator after donor engulfing. It does **not** say TMS, self-adjusting computation or effect systems fail at their own correctness goals. It says scientific certification adds a distinct semantic layer that those goals do not automatically decide.

## 12. Conservative donor embeddings

ORION-16 keeps donor-native mechanisms as special cases.

- **Ordinary transition system:** scientific obligations/authority/provenance inert.
- **TMS/dependency maintenance:** certificate status follows dependency invalidation; extra authority/effect dimensions inert.
- **Self-adjusting computation:** dependencies describe computation reuse/recompute; scientific certification universally admissible in the donor-native special case.
- **Typed effect system:** effect rows, request/allow/commit traces and residual obligations embed directly; scientific certification rules can be inert.
- **Evidence-backed authorization:** permission/provenance dependencies become authority premises; scientific obligation types may be inert when the donor action has no additional scientific claim.

A purported embedding that changes donor-native verdicts without a stronger explicit premise is rejected.

## 13. Deterministic support

Two normative checkers support the final theory.

`check_theory_closure_v2.py` covers root-inclusive DAG enumeration, preservation-certificate combinations, obligation persistence, authority composition, trace commutation, recursive audit and typed erasure.

`check_theory_closure_v2_1.py` adds the assumption regressions:

- safe root-inclusive reopening over all forward four-node DAG/change combinations;
- explicit spurious-edge countermodel;
- affected-realizability minimax omissions;
- footprint-faithful composition;
- hidden-read counterexample;
- preservation-versus-revalidation boundary.

These are bounded mathematical consistency checks, not measurements of real scientific-agent performance.

## 14. Cross-paper preservation ladder

ORION-16 sits inside the wider ORION preservation ladder:

1. identity;
2. computation/support;
3. evidence meaning;
4. target scientific-obligation discharge;
5. commit authority.

ORION-16 establishes that correct computation/support preservation does not automatically establish levels 4–5. ORION-17 studies evidence and closure across representation/objective changes. ORION-18 studies scientific discharge and commit authority across effect domains.

## 15. Falsifiers and empirical path

The theory is complete, but the usefulness of the abstraction remains falsifiable. ORION-16 should lose a separate-paper claim if:

- a donor-complete formalism already proves the same scientific-admissibility result under equivalent semantics;
- ORION mechanic embeddings require ad hoc exceptions that destroy the common contract;
- the extra obligation/authority/provenance dimensions never change any real scientific decision;
- an ideal donor product matches every relevant correctness and engineering measure without additional complexity.

The frozen donor-product protocol therefore compares against an integrated repair + incremental-computation + effect + authorization + provenance baseline rather than isolated donors.

## 16. Conclusion

ORION-16 does not ask ORION to become narrow in order to avoid prior theory. It does the opposite: it engulfs maintenance, incremental computation, epistemic update, effects, authorization and provenance, then identifies the scientific layer their composition still has to respect.

The resulting theory distinguishes safe over-approximation from minimax minimality, requires faithful footprints for composition, separates preservation from revalidation, and proves that computationally identical transitions can differ in scientific admissibility.

**Final terminal:** `P6_THEORY = FINISHED_V2_1`.

## Reference families

Canonical source identities are maintained in `../../CANONICAL_BIBLIOGRAPHY_V2.md`; donor ownership includes Doyle TMS, de Kleer ATMS, AGM/revision, Dynamic Epistemic Logic, adaptive/self-adjusting computation, ETAS, FAVA, AgentTether, dependency-guided rollback repair, provenance/authorization work and ORION ORION-11.
