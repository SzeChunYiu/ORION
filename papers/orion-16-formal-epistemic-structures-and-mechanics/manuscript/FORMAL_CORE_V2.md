# ORION-16 formal core V2 — closed theory

**Candidate paper:** Formal Epistemic Structures and Mechanics  
**Theory terminal:** `CLOSED_V2`  
**Novelty / external-evidence terminal:** `CANNOT_CHECK`  
**Date:** 2026-08-18

This document replaces the unresolved mathematical targets of V1. It does not claim that the resulting calculus is novel over all prior formal systems. It gives the complete formal object, corrected theorem statements, proofs, countermodels, conservative special cases, and executable obligations used by the candidate manuscript.

## 1. Epistemic signatures and state

### Definition 1 — epistemic signature

An epistemic signature is

\[
\Sigma=(C,(V_c)_{c\in C},Q,\mathcal O,\mathcal A,\mathcal F),
\]

where `C` is a finite or countable typed coordinate set, `V_c` is the value domain of coordinate `c`, `Q` is a set of claim/certificate identities, `\mathcal O` is a set of obligation types, `\mathcal A` is a set of authority types, and `\mathcal F` is a set of typed effect kinds.

Coordinates need not be propositions. They may represent a search universe, representation, measurement definition, method, memory state, provenance object, objective, resource state, or another scientific object.

### Definition 2 — epistemic state

A state is

\[
E=(\nu,s,D,P,O,A,H),
\]

where:

- `\nu(c)\in V_c` is the coordinate valuation;
- `s:Q\to\{\mathsf{open},\mathsf{certified},\mathsf{invalid},\mathsf{cannot\_check}\}`;
- `D\subseteq(C\cup Q)\times Q` is a dependency relation, or a graph projection of a richer dependency hypergraph;
- `P` is content/provenance lineage;
- `O` is the active typed-obligation set;
- `A` is the active authority set;
- `H` is immutable request, transition, failure, invalidation, discharge and revocation history.

Let

\[
Q_{cert}(E)=\{q\in Q:s_E(q)=\mathsf{certified}\}.
\]

The current-scientific-state projection is

\[
\pi_{sci}(E)=(\nu,s,D,P,O,A),
\]

which deliberately omits ordered history.

## 2. Mechanic contracts

### Definition 3 — epistemic mechanic

A mechanic contract is

\[
m=(R_m,W_m,Pre_m,Req_m,Eff_m,\tau_m,Emit_m,Fail_m,Inv_m),
\]

where `R_m,W_m\subseteq C\cup Q` are declared footprints; `Pre_m` is a precondition; `Req_m` is a typed set of hard/soft evidence, authority and obligation premises; `Eff_m` is a typed requested-effect set; `\tau_m` is a transition relation; `Emit_m` emits claims, obligations and lineage; `Fail_m` is the typed failure-terminal set; and `Inv_m` is the invariant set.

### Definition 4 — admissible step

\[
E\xrightarrow[m]{adm}E'
\]

iff:

1. `Pre_m(E)` holds;
2. every hard requirement is satisfied by content-bound admissible evidence or authority;
3. `(E,E')\in\tau_m`;
4. every material mutation lies in the declared write footprint;
5. every effect has an in-scope, fresh commit-authority derivation;
6. all post-state invariants hold;
7. all new claims, discharges and authority changes carry lineage;
8. no authority is minted except by a protected authority-producing transition;
9. every undischarged hard obligation remains active or yields `CANNOT_CHECK`;
10. the audit contract is append-only in `H`.

Computability is therefore strictly weaker than admissibility.

## 3. Root-inclusive dependency repair

For `X\subseteq C\cup Q`, let `Desc_D(X)` be strict transitive downstream reachability in `D`.

### Definition 5 — affected certified set

The affected certified set is

\[
Aff_D(E,X)=
\bigl(X\cap Q_{cert}(E)\bigr)
\cup
\bigl(Desc_D(X)\cap Q_{cert}(E)\bigr).
\]

The first term is essential. A changed certified claim is affected even when it is not its own strict descendant.

### Theorem 1 — root-inclusive reopening sufficiency

Assume `D` is sound for the declared dependency abstraction: whenever changing an element can invalidate certification of `q`, that element is either `q` itself or an ancestor of `q` in `D`. If only `X` is materially changed, reopening every member of `Aff_D(E,X)` leaves no potentially invalidated claim certified.

#### Proof

Take any certified `q` whose validity may be changed. If `q\in X`, then `q\in X\cap Q_{cert}(E)` and is reopened. Otherwise dependency soundness gives an `x\in X` with a nonempty path from `x` to `q`, so `q\in Desc_D(X)\cap Q_{cert}(E)`. Hence every potentially invalidated certification lies in `Aff_D(E,X)`. `\square`

### Theorem 2 — graph-only minimality

Assume only the sound graph `D`, current certified set and changed set `X` are available. Any strategy required to be sound for every semantic realization compatible with `D` must reopen every member of `Aff_D(E,X)`.

#### Proof

A changed certified root must be reopened because, absent additional semantic evidence, there is a compatible realization in which its changed content invalidates its former certificate. For a strict descendant `q`, choose a path from `x\in X` to `q` and a compatible realization in which every edge on that path is necessary support. Leaving `q` certified is then stale after changing `x`. Thus omitting any member of `Aff_D(E,X)` breaks uniform soundness. `\square`

This is a minimality result relative to graph-only information, not a claim that all real scientific dependencies are graphs.

## 4. Preservation certificates

Dependency reachability can over-approximate semantic invalidation. ORION-16 therefore allows protected evidence that a downstream certification is invariant under the exact change.

### Definition 6 — preservation certificate

A preservation certificate is

\[
\kappa=(q,X,issuer,scope,epoch,proof,lineage),
\]

and is valid only when:

1. `issuer` is outside the authority of the candidate transition;
2. `X` is exactly the changed set to which the proof applies;
3. scope/content/epoch match the current certification;
4. `proof` establishes that the certificate derivation of `q` remains valid under the change;
5. all proof premises remain valid;
6. `q\notin X`.

The last condition prevents a changed certified root from using a downstream invariance witness to self-preserve its own old certification.

Let `Pres(E,X,K)` be affected claims having a valid certificate in `K`.

### Definition 7 — certificate-aware repair

\[
Reopen_D^K(E,X)
=
Aff_D(E,X)\setminus Pres(E,X,K).
\]

### Theorem 3 — certificate-aware soundness and relative minimality

If `D` is sound and every accepted preservation certificate is semantically sound, reopening exactly `Reopen_D^K(E,X)` is sound. Among strategies using only `D`, `X`, current certification and the accepted preservation certificates, it is inclusion-minimal for uniform soundness.

#### Proof

Every affected claim not reopened has a valid proof of invariance under the exact change, so preserving it is sound. All remaining affected claims are reopened, so Theorem 1 covers them. For minimality, take any reopened claim `q` without a valid preservation certificate. The adversarial compatible-semantics construction from Theorem 2 still applies because no accepted extra semantic fact rules out invalidation. Hence uniformly preserving `q` would be unsound. `\square`

## 5. Full scientific-footprint separation

Read/write separation over ordinary coordinates is insufficient if mechanics interact through obligations, authority, provenance, dependency edges or hidden auxiliary state.

### Definition 8 — semantic footprint

Let `SF(m)` be the full set of current-scientific-state components whose values may affect `m`'s transition or admissibility derivation, including coordinate values, claim statuses, dependency edges, provenance objects, obligations and authority objects.

Let `SW(m)` be the full set of such components `m` may mutate.

Mechanics `m,n` are **semantically separated** when

\[
SW(m)\cap(SF(n)\cup SW(n))=\varnothing
\]

and symmetrically for `n`, and their authorization/provenance derivations have no cross-dependency.

### Definition 9 — independent history equivalence

Two committed events are independent if generated by semantically separated mechanics. `\equiv_I` is the least equivalence on histories generated by swapping adjacent independent events.

### Theorem 4 — history-aware commutation

For deterministic admissible semantically separated mechanics `m,n`, whenever both sequential compositions are defined,

\[
\pi_{sci}(n(m(E)))=\pi_{sci}(m(n(E))),
\]

while generally

\[
H_{mn}\neq H_{nm}
\quad\text{but}\quad
H_{mn}\equiv_I H_{nm}.
\]

#### Proof

Semantic separation guarantees that each mechanic reads the same values and admissibility premises in either order and writes disjoint current-scientific-state components. Therefore each local result is order invariant and the combined scientific projection is equal. The append-only histories record opposite event order; the two adjacent events are independent, hence equivalent under one permitted swap. `\square`

The theorem intentionally does not equate ordered audit histories.

### Composition-form closure

The contract closes four composition forms without claiming a new process
algebra:

- **sequential** `m;n` is defined only when `m`'s postcondition establishes
  `n`'s precondition and every residual hard obligation/authority restriction
  from `m` is present at the input to `n`;
- **conditional** `if g then m else n` requires a footprint-faithful,
  authority-valid guard and a declared join contract satisfied by either
  branch; only the selected branch runs, but its residual obligations and
  provenance cannot be hidden by the join;
- **independent parallel** `m || n` is the independent-history equivalence
  class of the two sequential interleavings, and is defined only under the full
  scientific separation premises of Theorem 4;
- **recursive/self-audit** composition is defined only under the well-founded
  rank or pre-recursion cycle rejection of Definition 12.

A composition is well formed only when every component is admissible at its
actual input, interfaces match, no protected authority is widened without a
root, and no hard obligation or provenance event disappears at a boundary.
Conditional choice and parallel scheduling therefore add no authority of their
own.

## 6. Authority non-escalation

Fix protected roots `A_0`.

### Definition 10 — non-escalating mechanic

A mechanic is non-escalating iff every output authority object is either retained from input, a scope restriction of an input authority, or issued by a protected authority-producing rule rooted in `A_0`.

### Theorem 5 — sequential non-escalation

Finite sequential composition of non-escalating mechanics is non-escalating.

#### Proof

Induct on composition length. The base case is the definition. At each step, new authority is only a restriction of already legitimate authority or is newly rooted in `A_0`. No step creates an unrooted widening, so neither can the composition. `\square`

## 7. Residual obligations are not erased by success

### Definition 11 — authorized discharge

A hard obligation `o` is discharged only by a transition whose rule explicitly consumes `o`, whose evidence/authority premises are valid, and whose lineage records the discharge.

### Theorem 6 — residual-obligation persistence

Let `m_1;\ldots;m_k` be an admissible sequence. If `m_i` emits hard obligation `o` and no later step `m_j`, `j>i`, performs an authorized discharge of `o`, then every later admissible current state retains `o`; if execution terminates without the required information, the terminal is `CANNOT_CHECK` or another explicitly non-success terminal, not silent success with `o` absent.

#### Proof

Admissibility clause 9 forbids an undischarged hard obligation from disappearing. Apply the clause inductively to each transition after `m_i`. Only an authorized discharge can remove `o`. `\square`

This closes the V1 theorem target.

## 8. Recursive audit

### Definition 12 — well-founded audit rank

Each recursively auditable mechanic representation has rank `r(m)` in a well-founded order `(L,\prec)`. Every recursive audit call must either reduce rank or be rejected by a cycle detector before recursion.

### Theorem 7 — audit termination

Every audit satisfying the preceding rule terminates.

#### Proof

Without a detected cycle, an infinite execution would contain an infinite strict descending chain in a well-founded order, impossible. Detected cycles terminate by the alternative branch. `\square`

### Countermodel

If `a(E)` recursively calls the identical `a(E)` with no rank decrease and no cycle guard, the trace is infinite. Therefore recursive self-audit is not self-justifying merely because it is recursive.

## 9. Self-authorization boundary

### Proposition 8 — candidate-controlled admission is vacuous

If candidate mechanic `m` can rewrite both admission predicate `J` and every evidence value read by `J`, with no protected constraint outside `m`'s write authority, then an internally authorizing state is reachable independently of any externally defined correctness property.

#### Proof

Choose a constant-accepting `J'`, or candidate-controlled evidence satisfying an acceptance branch. Since no protected relation binds acceptance to the external property, internal authorization does not imply it. `\square`

## 10. Typed-erasure separation

Let `Erase` map a mechanic contract to its bare computational transition and ordinary dependency graph, deleting hard obligations, commit authority and provenance constraints.

### Theorem 9 — bare transition/dependency semantics is not fully abstract for ORION-16 admissibility

There exist contracts `m_1,m_2` such that

\[
Erase(m_1)=Erase(m_2)
\]

but one transition is admissible and the other is not.

#### Proof by construction

Give both contracts the same deterministic state transition `0\mapsto1` and the same dependency graph. Let `m_1` have a satisfied hard evidence obligation and valid commit authority. Let `m_2` have the identical bare transition but an unsatisfied hard obligation (or, alternatively, missing commit authority). Then the erasures coincide while Definition 4 admits only `m_1`. `\square`

### Corollary 9.1 — computational preservation does not imply epistemic preservation

A change-propagation or TMS layer can correctly identify which computation/claim is structurally affected without deciding whether a scientifically certified state may remain certified. The latter may additionally depend on obligation, authority and provenance dimensions.

This is ORION-16's formal discriminator from a pure dependency-recomputation semantics; it is not a novelty claim over all richer maintenance logics.

## 11. Conservative special cases

### Proposition 10 — ordinary transition systems

Set hard obligations empty, treat commit authority as universally valid, and make provenance/dependency/history inert. ORION-16 admissibility reduces to the underlying transition relation plus footprint/invariant checks.

### Proposition 11 — dependency-maintenance special case

With authority/provenance/obligation dimensions inert and no preservation certificates, ORION-16 repair reduces to root-inclusive dependency invalidation `Aff_D(E,X)`.

### Proposition 12 — self-adjusting computation special case

Represent changeable inputs and derived computations as dependency nodes, and interpret recomputation as an ordinary mechanic with universal authority and no scientific certification obligations. ORION-16's affected-set layer then contains standard dependency-driven change propagation as a special case. ORION-16 does not inherit or claim the efficiency bounds of self-adjusting-computation systems.

### Proposition 13 — effect-system special case

Requested/handled/denied/committed typed effects embed into `Eff_m`, requirements and history. When scientific certification/repair dimensions are inert, the additional ORION-16 coordinates do not change those effect decisions.

These are representation-level conservative embeddings, not claims that ORION-16 subsumes every theorem or implementation detail of each donor field.

## 12. Preservation ladder

ORION-16 distinguishes four preservation questions after change:

1. **computation reuse:** may a previous computation be reused or incrementally repaired?
2. **evidence preservation:** does a content-bound observation/provenance item remain valid?
3. **certification preservation:** do the obligations supporting a scientific certificate remain discharged?
4. **commit authority preservation:** is the next mutation still authorized at the current scope/epoch?

Theorem 9 proves that level 1 does not imply levels 3–4. ORION-17 studies evidence-versus-closure transport across representation change; ORION-18 studies obligation-versus-authority transport.

## 13. Executable support

`formal/check_theory_closure_v2.py` deterministically checks:

- 960 root-inclusive DAG/change cases, including 2,048 changed certified-root occurrences;
- 64 preservation-certificate combinations;
- current-state commutation with distinct but independent-equivalent histories;
- hard-obligation persistence;
- non-escalation cases;
- typed-erasure counterexamples;
- recursive-cycle rejection;
- conservative dependency-maintenance special cases.

The checker is standard-library only and is a finite proof-support artifact, not empirical evidence.

## 14. Prior-work ownership and claim boundary

The following are treated as donor or pre-existing mechanisms, not ORION-16 inventions:

- dynamic epistemic/action update logics;
- AGM and iterated belief revision;
- TMS/JTMS/ATMS justification maintenance and dependency-directed backtracking;
- separation/frame reasoning and process/concurrency trace theory;
- self-adjusting/incremental computation and dynamic dependence graphs;
- typed/algebraic effects;
- authorization, delegation and revocation logics;
- provenance/audit systems;
- ORION-11 mechanic cells, recursive audit, responsibility-based reframing and dependency reopening;
- 2026 agent-specific effect/authorization/repair systems already named in the donor ledger.

The completed ORION-16 theoretical object is therefore:

\[
\boxed{
\text{history-aware typed epistemic mechanic contracts}
+
\text{root-inclusive certificate-aware repair}
+
\text{hard-obligation persistence}
+
\text{scoped non-escalating commit authority}
}
\]

with the typed-erasure separation theorem identifying why the full object cannot, in general, be replaced by a bare transition/dependency graph.

## 15. Final theory terminal

There are no remaining mathematical `THEOREM TARGET` placeholders in V2.

**Established internally:** definitions, corrected reopening theorems, certificate-aware repair, commutation/trace theorem, non-escalation, obligation persistence, recursive termination boundary, self-authorization countermodel, typed-erasure separation and conservative special cases.

**Not established by mathematics alone:** exhaustive novelty over the literature, empirical superiority, journal acceptance, or independent human verification.

Accordingly:

- `P6_THEORY = CLOSED_V2`
- `P6_NOVELTY = CANNOT_CHECK_UNTIL_LITERATURE_CLOSURE`
- `P6_EMPIRICAL_SUPERIORITY = NOT_REQUIRED_FOR_THEORY / OPEN_IF_CLAIMED`
