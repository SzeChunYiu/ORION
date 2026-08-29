# ORION-16–ORION-18 cross-paper preservation theory V1

**Date:** 2026-08-17  
**Status:** synthesis target / `CANNOT_CHECK` for novelty; not a fourth paper.  
**Purpose:** state the common structure suggested by ORION-16 incremental repair, ORION-17 representation/objective transport and ORION-18 cross-domain authorization without erasing their distinct semantics.

## 1. Motivation

The breadth pass exposes several mature parent mechanisms:

- self-adjusting computation preserves/reuses unaffected computation after change;
- dependency repair preserves independently supported state;
- schema evolution/lenses preserve data or specified semantics across representation transformations;
- provenance preserves identity/lineage across transformations;
- authorization logics preserve policy compliance and proof validity;
- stateful governance requires authorization to remain valid at commit-time policy state.

ORION should absorb all of these. The remaining cross-paper question is whether **different kinds of preservation are being conflated**.

A state object can survive a transformation while the scientific reason for treating it as a closure, merge, assertion or promotion no longer survives.

## 2. Preservation ladder

For a transformation/event `u` from source situation `X` to target situation `X'`, distinguish five candidate preservation predicates.

### L0 — identity preservation

\[
P_0(o,u)
\]

The relevant object/evidence identity remains content-bound and refers to the same underlying artifact/observation under the frozen identity contract.

Examples:
- same content hash/source span;
- same measurement record;
- same immutable evidence artifact.

### L1 — computational/support preservation

\[
P_1(d,u)
\]

The dependencies or derivation fragments needed to reuse/recompute an object remain valid under the computational/support semantics.

Examples:
- dynamic dependence graph says a node is unaffected;
- one independent proof/support path remains valid;
- an incremental view can be updated without recomputing unrelated state.

### L2 — semantic/evidential preservation

\[
P_2(e,u)
\]

The evidence remains semantically applicable to the same proposition/construct/measurement meaning after the transformation.

Examples:
- a measurement keeps the same referent, construct and measurement semantics;
- a source observation remains true after a chart/world-model change.

### L3 — obligation/discharge preservation

\[
P_3(e,o,u)
\]

The transported evidence/support still satisfies the **target** hard epistemic obligation `o` with the same required meaning/scope.

Examples:
- old evidence still discharges the transformed task's coverage obligation;
- old mapping evidence still satisfies the target merge-equivalence obligation;
- a route-local closure genuinely discharges the target global-coverage requirement through an explicit preservation theorem.

### L4 — authority/commit preservation

\[
P_4(a,u,t)
\]

At target scope/epoch `t`, an authorization derivation remains valid for committing action `a`, including protected-root, revocation, policy-state and timing requirements.

Examples:
- assertion certificate still valid after evidence/policy changes;
- a self-change promotion certificate remains valid at current protected evaluator epoch;
- a commit-time policy is still satisfied after concurrent state changes.

## 3. Directionality

The ladder is intentionally **not** defined as a chain of automatic implications.

The main research hypothesis is that lower-level preservation is often necessary but is not generally sufficient for higher-level preservation:

\[
P_0 \not\Rightarrow P_2,
\qquad
P_1 \not\Rightarrow P_3,
\qquad
P_2 \not\Rightarrow P_3,
\qquad
P_3 \not\Rightarrow P_4.
\]

Some applications may impose additional premises that create valid implications. Those premises are the explicit **transport/coercion proofs** the ORION-16–ORION-18 programme should expose rather than assume.

## 4. Constructive counterexamples

### C1 — identity does not imply semantic applicability
An immutable evidence artifact is unchanged (`P0`) but a schema/measurement interpretation changes so the artifact no longer measures the same construct. `P2` fails.

**Owners/parents:** ORION-13 scientific meaning; schema/ontology evolution.

### C2 — computational reuse does not imply epistemic closure
A dependency graph correctly marks a computed result as unaffected and reusable (`P1`), but a newly introduced hard independent-check obligation remains unresolved. `P3` fails despite successful incremental reuse.

**ORION-16 discriminator:** change propagation is correct; epistemic obligation remains open.

### C3 — evidence truth does not imply new-objective closure
A content-bound observation remains semantically valid after an objective reframe (`P2`), but the new objective requires independent replication not covered by the old certificate. `P3` fails.

**ORION-17 discriminator:** retain evidence, reopen closure.

### C4 — local obligation discharge does not imply foreign-domain discharge
A route's local exhaustion obligation is genuinely satisfied (`P3` in route domain), but global scientific coverage is a different obligation and has no proved coercion. Target-domain `P3` fails.

**ORION-17/ORION-18 discriminator:** source-domain correctness is preserved; target-domain closure is not licensed.

### C5 — obligation discharge does not imply current commit authority
All scientific evidence obligations for an action are satisfied (`P3`), but the authorization certificate is stale after an epoch/policy-state change or the grant scope does not cover the target. `P4` fails.

**ORION-18 discriminator:** commit-time authority must be re-established.

### C6 — one support path can fail without destroying all derivability
Evidence path A is revoked, but independent path B remains complete. A naive descendant-node deletion would mark the certificate dead; proof-sensitive preservation recognizes a valid alternate derivation.

**ORION-16/ORION-18 discriminator:** dependency invalidation requires derivation semantics, not only node reachability, when alternative supports exist.

## 5. Transport certificate

A generic transport attempt from source judgment `j` to target judgment/action `y` may be represented by a certificate

\[
\Theta=(src,dst,I,S,O,A,T,\Pi),
\]

where:

- `src`, `dst` identify source and target representation/domain;
- `I` proves required identity preservation;
- `S` proves required support/derivation preservation;
- `O` proves target obligation/discharge preservation;
- `A` proves target authority/root/scope preservation;
- `T` proves target epoch/policy-state freshness where required;
- `\Pi` records provenance of all premises.

The fields are **typed and optional by contract**: a purely computational reuse operation may require only `I/S`; a scientific closure transport may require `I/S/O`; an effectful commit may additionally require `A/T`.

No absent field is inferred from a lower-level PASS.

## 6. Candidate transport rule

For an action whose contract requires levels `R \subseteq {0,1,2,3,4}`, transport is authorized only when every required preservation judgment is established:

\[
\frac{\forall k\in R:\;\Gamma\vdash P_k}{\Gamma\vdash \mathrm{TRANSPORT}_R}.
\]

If a required judgment is refuted, the domain-specific terminal is `DENY/REOPEN/REVOKED` as defined by the owning mechanism. If a required judgment cannot be established or refuted, the terminal is `CANNOT_CHECK` rather than implicit preservation.

This rule is a research scaffold. It must be pressure-tested against lens laws, incremental-computation correctness, proof-carrying authorization, trust management and non-interference.

## 7. Paper projections

### ORION-16 projection
ORION-16 studies transitions where `P1` support/computational reuse interacts with hard residual obligations, certification state, provenance and history. It should show that correct incremental propagation can coexist with an unresolved `P3` obligation.

### ORION-17 projection
ORION-17 studies transformations where `P0/P2` evidence may survive chart/objective change while `P3` closure does not. Its strongest benchmark should make this separation observable under a faithful schema/lens/planning-transform baseline.

### ORION-18 projection
ORION-18 studies cases where a valid source-domain `P3` or evidence judgment does not imply target-domain `P3/P4`; explicit target-obligation-preserving coercion plus commit-time authority is required.

## 8. Internal ORION embedding

The ladder is compatible with existing ORION invariants without relabeling them:

- ORION-11 `REOPEN` supplies domain-specific invalidation after changed coordinates;
- ORION-12 route/task stop supplies a concrete `P3` non-implication;
- ORION-13 meaning projection supplies `P2` semantic-preservation checks;
- ORION-14 hard gates/protected authority supply `P3/P4` requirements;
- ORION-15 fresh/protected readiness supplies strong `P4` epoch/custody requirements;
- runtime provenance/history/dependency objects supply candidate `P0/P1` infrastructure.

The common ladder is only useful if it preserves these native verdicts exactly.

## 9. External parent pressure

Potentially overlapping formalisms include:

- incremental/self-adjusting computation and dynamic dependence graphs;
- truth-maintenance/justification systems;
- bidirectional transformations/lenses and schema evolution;
- ontology/belief-signature revision;
- provenance and proof reconstruction;
- proof-carrying/stateful authorization;
- information-flow/non-interference;
- policy composition and multi-valued authorization;
- effect systems and residual obligations.

If one mature formalism already represents all required preservation levels and transport rules without loss, the ORION synthesis should adopt it rather than claim a new calculus.

## 10. Cross-paper falsifier suite

Freeze matched cases in which:

1. `P1` true, `P3` false — computation reusable, hard scientific obligation unresolved;
2. `P2` true, `P3` false — evidence semantically valid, new task closure invalid;
3. source-domain `P3` true, target-domain `P3` false — local gate valid, foreign discharge invalid;
4. `P3` true, `P4` false — evidence complete but authority stale/out of scope;
5. all required levels true — transport must succeed, preventing fail-closed total refusal.

A system that cannot distinguish these pairs does not implement the preservation semantics claimed by the candidate programme.

## 11. Novelty and ownership terminal

This document does **not** create a new candidate paper. It is a programme-level synthesis object that may:

- provide common notation/lemmas to surviving ORION-16/ORION-17/ORION-18 papers;
- show that two candidates should merge;
- reveal that a mature external formalism already subsumes the structure.

Current terminal: `CANNOT_CHECK` for external novelty and `SYNTHESIS_ONLY` for publication identity.