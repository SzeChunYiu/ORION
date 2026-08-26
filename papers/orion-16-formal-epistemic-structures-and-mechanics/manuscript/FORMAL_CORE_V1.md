# ORION-16 formal core V1

**Candidate paper:** Formal Epistemic Structures and Mechanics  
**Authority:** mathematical working object; novelty not yet authorized  
**Date:** 2026-08-17  
**Donor policy:** absorb action/update logic, effect systems, dependency repair and authorization graphs before claiming a residual.

## 1. Typed epistemic signatures

### Definition 1 (epistemic signature)
An **epistemic signature** is a tuple

\[
\Sigma=(C,(V_c)_{c\in C},Q,\mathcal O,\mathcal A,\mathcal F),
\]

where:

- `C` is a finite or countable set of typed state coordinates;
- `V_c` is the value domain of coordinate `c`;
- `Q` is a set of claim/certificate identifiers;
- `\mathcal O` is a set of obligation types;
- `\mathcal A` is a set of authority-token types;
- `\mathcal F` is a set of typed epistemic effect kinds.

A coordinate is not assumed to be a proposition. It may hold a representation, search universe, measurement definition, procedure, memory item, provenance identity, resource state, objective, or other typed object.

### Definition 2 (epistemic state)
A state over `\Sigma` is

\[
E=(\nu,s,D,P,O,A,H),
\]

where:

- `\nu(c)\in V_c` is the current coordinate valuation;
- `s:Q\to\{\mathsf{open},\mathsf{certified},\mathsf{invalid},\mathsf{cannot\_check}\}` is claim status;
- `D\subseteq (C\cup Q)\times Q` is a dependency relation or a projection of a richer dependency hypergraph;
- `P` maps claims, judgments and transitions to provenance/evidence identities;
- `O` is a finite set of active typed obligations;
- `A` is a finite set of active authority tokens/certificates;
- `H` is retained request/transition/failure/invalidation history.

Write

\[
\Delta(E,E')=\{c\in C:\nu_E(c)\neq\nu_{E'}(c)\}.
\]

### Definition 3 (scientific projection)
Let

\[
\pi_{sci}(E)=(\nu,s,D,P,O,A)
\]

omit the ordered audit history `H`. This projection is needed because independent executions can reach the same current scientific state while retaining different event orderings.

## 2. Mechanic contracts and epistemic effects

### Definition 4 (epistemic mechanic)
A mechanic is a contract

\[
m=(R_m,W_m,\mathsf{Pre}_m,\mathsf{Req}_m,\mathsf{Eff}_m,\tau_m,\mathsf{Emit}_m,\mathsf{Fail}_m,\mathsf{Inv}_m),
\]

where:

- `R_m\subseteq C\cup Q` is its read footprint;
- `W_m\subseteq C\cup Q` is its write footprint;
- `\mathsf{Pre}_m(E)` is its precondition;
- `\mathsf{Req}_m(E)` is the set of hard/soft evidence, obligation and authority requirements;
- `\mathsf{Eff}_m(E)` is the typed set of requested effects and their scopes;
- `\tau_m\subseteq \mathcal E_\Sigma\times\mathcal E_\Sigma` is its transition relation;
- `\mathsf{Emit}_m(E,E')` lists newly emitted claims/obligations/provenance and residual obligations;
- `\mathsf{Fail}_m` is a typed failure-terminal set;
- `\mathsf{Inv}_m` is a set of invariants promised by the contract.

A deterministic mechanic has a partial transition function instead of a relation.

### Definition 5 (requested and committed effect)
A requested effect is an intention to change a typed coordinate/action scope. A committed effect is a requested effect for which the mechanic has a valid admissibility/authority derivation at the state epoch in which the commit occurs.

The event trace distinguishes at least:

\[
\mathsf{request},\mathsf{allow},\mathsf{deny},\mathsf{cannot\_check},\mathsf{commit},\mathsf{fail},\mathsf{revoke}.
\]

This request/commit separation is adopted from effect/authorization systems such as ETAS/FAVA; ORION-16 does not claim it as novel.

### Definition 6 (admissible mechanic step)
We write

\[
E\xrightarrow[m]{\mathrm{adm}}E'
\]

iff all of the following hold:

1. `\mathsf{Pre}_m(E)`;
2. every hard member of `\mathsf{Req}_m(E)` is satisfied by content-bound evidence or valid authority in `E`;
3. `(E,E')\in\tau_m`;
4. `\Delta(E,E')\subseteq W_m`;
5. every changed coordinate/effect is permitted by an in-scope authority derivation;
6. every invariant in `\mathsf{Inv}_m` holds in `E'`;
7. every new claim/obligation has provenance recorded in `P_{E'}`;
8. no authority token in `A_{E'}\setminus A_E` was minted except by a trusted authority-producing transition explicitly allowed by the contract;
9. every unresolved hard requirement is retained as a residual obligation or a `CANNOT_CHECK` terminal rather than silently erased;
10. request/allow/commit/failure events required by the audit contract are retained in `H`.

A mechanic may be computationally executable while having no admissible commit.

## 3. Dependency semantics and reopening

For `X\subseteq C\cup Q`, let `\operatorname{Desc}_D(X)` be the strict transitive downstream closure under `D`.

### Definition 7 (dependency-soundness)
A dependency relation `D` is **sound for a class of admissible semantics** `\mathfrak S` when, for every certified claim `q`, every semantic support whose change may affect the validity of `q` is represented by an ancestor path to `q` in `D`.

This is relative to an abstraction. A graph can be sound for one abstraction and incomplete for another.

### Definition 8 (selective reopening)
For a changed set `X`, define `\operatorname{Reopen}_D(E,X)` as the state obtained by:

- retaining the new coordinate values;
- changing every certified claim in `\operatorname{Desc}_D(X)` to `\mathsf{open}` or `\mathsf{cannot\_check}` when required support is unavailable;
- preserving claim status outside `\operatorname{Desc}_D(X)` unless an independent authority/provenance rule requires change;
- recording the invalidation cause and prior status in `H`;
- preserving provenance for retained claims and invalidation provenance for reopened claims.

### Theorem 1 (sufficiency of downstream reopening)
Let `D` be sound for `\mathfrak S`. If only elements of `X` are changed before reopening, then after `\operatorname{Reopen}_D(E,X)`, no claim whose certification may have been invalidated by the change remains certified.

#### Proof
Take any claim `q` whose certification may be invalidated by changing `X`. By dependency-soundness, some changed element `x\in X` is an ancestor of `q`; hence `q\in\operatorname{Desc}_D(X)`. The reopening operator removes certified status from every such claim. `\square`

### Theorem 2 (minimality under graph-only information)
Assume the only semantic dependency information available to a reopening strategy is a sound graph `D`. Any strategy that must be sound for every semantics compatible with `D` must reopen every certified claim in `\operatorname{Desc}_D(X)`. Consequently, downstream reopening is inclusion-minimal among uniformly sound graph-based strategies.

#### Proof
Suppose a purportedly uniformly sound strategy leaves some certified `q\in\operatorname{Desc}_D(X)` certified. There is a path from some `x\in X` to `q`. Construct a compatible semantics in which every edge on that path is necessary support and `q` is valid exactly when the original value of `x` holds. Change `x` so the support fails. The retained certification is stale, contradicting uniform soundness. `\square`

### Corollary 2.1 (repair conservation)
Full reset is sound under the same assumptions but is not inclusion-minimal whenever a certified claim exists outside `\operatorname{Desc}_D(X)`.

### Donor boundary
Truth-maintenance systems and the 2026 dependency-guided rollback repair work already establish selective dependency repair/preservation in important settings. ORION-16 must therefore generalize across heterogeneous epistemic coordinates/effects/authority-bearing commits or relinquish this as a headline novelty.

## 4. Mechanic composition

### Definition 9 (strong separation)
Mechanics `m` and `n` are **strongly separated** when

\[
W_m\cap(R_n\cup W_n)=\varnothing
\quad\text{and}\quad
W_n\cap(R_m\cup W_m)=\varnothing,
\]

and neither mechanic changes an authority, provenance object, residual obligation, dependency edge, or invariant consumed by the other.

### Definition 10 (independent trace events)
Two committed trace events are independent when their mechanics are strongly separated and neither event's authorization/provenance derivation depends on the other. Let `\equiv_I` be the smallest equivalence relation on histories generated by swapping adjacent independent events.

This is a Mazurkiewicz-style trace quotient: event order is retained but independent orderings can be identified when reasoning about the current scientific state.

### Theorem 3 (history-aware commutation under strong separation)
Let `m,n` be deterministic admissible strongly separated mechanics. Whenever both sequential compositions are defined,

\[
\pi_{sci}(\tau_n(\tau_m(E)))
=
\pi_{sci}(\tau_m(\tau_n(E))),
\]

while their audit histories need only satisfy

\[
H_{mn}\equiv_I H_{nm},
\]

not literal sequence equality.

#### Proof
Strong separation ensures that each mechanic reads the same local inputs and writes disjoint outputs in either execution order. The additional conditions prevent one mechanic from changing authority, provenance, obligations, dependencies or invariants consumed by the other. Thus the current scientific projection is identical. The retained histories record different event orderings; since the two committed events are independent, those histories are equivalent under one allowed adjacent swap. `\square`

### Why this corrects V1
An earlier formulation asserted equality of the entire states. That was too strong because `H` intentionally records ordered history. The formal object now distinguishes current-state commutation from trace identity.

### Definition 11 (non-escalating mechanic)
Fix a trusted root set `A_0`. A mechanic is non-escalating when every output authority token is either:

1. already present in the input;
2. a scope restriction of an input token; or
3. issued by a trusted authority transition whose issuer is rooted in `A_0`.

### Theorem 4 (sequential non-escalation)
The sequential composition of non-escalating mechanics is non-escalating.

#### Proof
By induction on composition length. The base case is the definition. If a composition of `k` mechanics contains only retained, narrowed, or trusted-root-issued authority, mechanic `k+1` can only retain/narrow those tokens or add another trusted-root-issued token. `\square`

### Theorem target 4.1 (residual-obligation preservation)
If a mechanic emits a hard residual obligation that no later mechanic discharges using an authorized rule, sequential composition must retain that obligation or terminate `CANNOT_CHECK`; it cannot disappear merely because later computation succeeds.

This target is motivated directly by residual-obligation effect systems and is not yet proved for the complete ORION contract language.

## 5. Recursive mechanic audit

Let a mechanic representation include a rank `r(m)` in a well-founded ordered set `(L,\prec)`.

### Definition 12 (rank-decreasing audit)
A recursive audit is rank-decreasing when every recursive call from mechanic representation `m` to `m'` satisfies

\[
r(m')\prec r(m).
\]

### Theorem 5 (termination by well-founded descent)
Every rank-decreasing recursive audit terminates.

#### Proof
An infinite audit would generate an infinite descending chain in a well-founded order, contradiction. `\square`

### Countermodel 5.1
If an auditor responds to every unresolved audit of itself by invoking the same audit state with unchanged rank, then

\[
a(E)\to a(E)\to a(E)\to\cdots
\]

is an infinite trace unless an external bound, cycle detector or decreasing measure is imposed.

## 6. Self-authorization boundary

### Proposition 6 (internal self-authorization cannot guarantee promotion soundness)
Suppose candidate mechanic `m` can rewrite both the predicate `J` deciding whether `m` is promotable and all evidence values read by `J`, with no protected external constraint. Then for every `m` there exists an internally reachable pair `(J',E')` such that `J'(m,E')=\mathsf{authorize}`. Hence internal authorization alone cannot guarantee any nontrivial externally defined promotion property.

#### Proof
Choose `J'` as the constant authorization predicate or choose candidate-controlled evidence satisfying an acceptance branch. Since both objects are candidate-writable and no external constraint exists, authorization is reachable independently of the external property. `\square`

ORION-18 owns the general authority calculus; ORION-16 uses this boundary only to state when recursive mechanic audit is structurally unsafe.

## 7. `CANNOT_CHECK` and failure semantics

### Definition 13 (distinct terminals)
For a proposed transition, distinguish:

- `REJECT`: available evidence establishes a blocking condition;
- `CANNOT_CHECK`: a required obligation cannot be established or refuted;
- `FAIL`: execution of an otherwise admissible mechanic failed;
- `UNAUTHORIZED`: the transition is computable but lacks an authority derivation;
- `REVOKED`: a previously valid authority/evidence ancestor was invalidated.

Missing evidence is not evidence of failure, and computational success is not authority.

## 8. Donor-faithful embeddings

ORION-16 now treats the following as required embedding targets:

- **Dynamic Epistemic Logic / action models:** informational/update actions;
- **AGM/iterated revision:** belief-change operators and rationality constraints;
- **truth-maintenance/dependency systems:** justification graphs and selective retraction;
- **epistemic separation/process logics:** locality/frame-style reasoning;
- **CoALA (arXiv:2309.02427):** modular language-agent memory/action/decision architecture;
- **mechanism-level review (arXiv:2607.23942):** state/control/transition/persistence/failure/learning/resource-governance decomposition;
- **ETAS (arXiv:2607.17780):** typed effects, persistent requested-action traces and residual obligations;
- **FAVA (arXiv:2607.27267):** evidence-backed permission graphs and deterministic pre-effect authorization;
- **AgentTether (arXiv:2607.06273):** transition units and dependency-guided failure localization;
- **Dependency-Guided Rollback Repair (arXiv:2608.10502):** typed dependency repair, preservation of independently supported state and selective replay.

### Theorem target 7 (conservative donor embedding)
For each adopted donor, instantiate the relevant ORION-16 structures so that the donor's native update/allow/rollback/locality judgments are preserved when ORION-16-only dimensions are inert.

A generalization that changes donor-native verdicts without an explicit stronger premise is rejected as a false embedding.

## 9. Widened ORION-16 object under test

The candidate is no longer merely

`responsibility -> mutation authority -> reopening -> recursion`.

The wider object is a **history-aware epistemic effect/repair algebra**:

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

Its scientific value must come from composition theorems or cross-domain transfer, not from assembling familiar field names.

## 10. Deterministic checking obligations

The associated checker must verify at least:

1. downstream reopening removes every certified descendant;
2. unaffected certified nodes remain unchanged;
3. full reset is non-minimal when independent certified state exists;
4. strong separation yields equal scientific projections;
5. different independent execution orders retain distinguishable but `\equiv_I`-equivalent histories;
6. non-escalating transitions cannot mint untrusted authority under composition;
7. unresolved hard residual obligations cannot disappear under later success;
8. recursive self-loops are detected;
9. candidate-writable acceptance predicates admit the self-authorization countermodel;
10. donor-native fixtures remain unchanged under conservative embeddings.

Finite enumeration supports the proofs and catches implementation mistakes; it does not replace the general proofs.

## 11. Cross-domain transfer obligations from #353

ORION-16 must be tested outside the original ORION-11 reconstruction setting on at least:

- finite symbolic workflow/state systems with exact ground truth;
- persistent-memory/state repair with selective rollback;
- a tool/agent workflow containing authorization-bearing effects;
- a negative control where full reset or a plain transition graph is sufficient and ORION-16 should not add complexity.

Strong baselines include donor-specific rollback/effect/authorization representations, not only an untyped toy state machine.

## 12. Nearest-work pressure and nonclaims

This core does **not** claim novelty for:

- belief expansion, contraction or revision;
- dynamic epistemic update;
- truth-maintenance/dependency-directed rollback;
- modular/typed transition systems;
- separation/commutation arguments;
- well-founded termination proofs;
- effect systems or residual obligations;
- permission graphs/authorization calculi;
- provenance or retained history in isolation;
- modular cognitive-agent architectures.

The widened candidate residual is the donor-faithful **composition** of these mechanisms around epistemic commit/reopen/recursive-audit semantics. If #334/#352/#343 show that the composition is already established, or if transfer adds no theorem/benchmark discriminator, the formal material should merge into ORION-11/ORION-15 or a technical companion instead of becoming ORION-16.

## 13. What this formal core establishes now

The proofs establish elementary structural properties of the proposed definitions and repair one over-strong commutation claim. They do **not** yet establish:

- novelty;
- semantic completeness of dependency graphs;
- faithful embeddings of every donor;
- that typed contracts improve real research outcomes;
- proof-assistant verification;
- that ORION-16 should remain a separate paper.

Current novelty/promotion terminal remains `CANNOT_CHECK`.