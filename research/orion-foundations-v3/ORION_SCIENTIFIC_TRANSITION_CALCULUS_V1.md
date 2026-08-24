# ORION Scientific Transition Calculus V1

## 0. Status

This document gives a complete mathematical formalism for a declared class of auditable scientific workflows. It is a theory object, not a paper-result promotion.

```text
status = THEORY_COMPLETE_FOR_CLASS_W_DAGGER
external_validity = CANNOT_CHECK
paper_authority_delta = NONE
```

The theory distinguishes **availability**, **native validity**, **execution integrity**, **target sufficiency**, **scientific entitlement**, and **support/blocker state**. This prevents computation, provenance, signatures, permission, or agreement from silently becoming scientific authority.

## 1. Expert council and veto functions

Every definition and theorem is pressure-tested through six analytical roles:

1. **Formal semantics lead** — syntax, operational rules, induction, normalization, composition.
2. **Decision/information theorist** — sufficiency, indistinguishability, Bayes risk, responsibility quotients.
3. **Algorithms/complexity lead** — closure, obstruction, minimal repair, synthesis/checking complexity.
4. **Causal scientific-methodologist** — interventions, regime transport, measurement meaning, external validity.
5. **Authority/security logician** — delegation, coercion, attenuation, revocation, self-promotion.
6. **Hostile systems auditor** — occurrence identity, custody, replay, concurrency, key compromise, benchmark leakage.

A result survives only if its statement and nonclaims are acceptable to all relevant roles.

## 2. Typed universes

Let

\[
\mathbb D,\mathbb K,\mathbb S,\mathbb E,\mathbb P,\mathbb R,
\mathbb Q,\mathbb A,\mathbb O,\mathbb B,\mathbb L,\mathbb X
\]

be domains, object kinds, scopes, epochs, principals, responsibilities, terminals, artifacts, obligations, bridge rules, method languages, and execution occurrences.

A scientific object is

\[
X=(id,d,k,s,c,e),
\]

where `c` is an exact content identity. A responsibility is

\[
r=(id,X,question,resolution,loss,authority\_class).
\]

A scientific judgment is `j=(X,r,q)` with typed terminal `q`. The programme-level terminal family includes at least

```text
ESTABLISH, RETAIN, REOPEN, CONTINUE, BLOCK, DENY, CANNOT_CHECK.
```

Paper-specific terminals must project totally into this family.

## 3. Artifacts, execution, obligations, and support

An artifact is

\[
a=(id,subject,native\_type,content,native\_verdict,issuer,
provenance,epoch,occurrence,signature).
\]

Execution integrity is the product

\[
\Xi=(attributable,occurrence\_bound,content\_bound,environment\_bound,
chronology\_valid,replayable,cross\_implementation\_agreement,
attested,custody\_bound,freshness\_bound).
\]

There is no built-in implication from `Xi` to scientific validity or authority.

An obligation is

\[
o=(id,j,predicate,kind,required\_authority,status,deps)
\]

with status in

```text
OPEN, DISCHARGED, BLOCKED, UNDETERMINED, REVOKED.
```

A complete support family is a finite hyperedge

\[
F=(A_F,B_F,U_F,C_F)\Rightarrow j,
\]

containing relied-upon artifacts, bridge applications, authority records, and blocker resolutions. A judgment may have several independent complete support families.

## 4. Scientific state

The state is

\[
\Sigma=(K,W,M,\rho,\mathcal R,\Phi,\mathcal L,
Art,Obl,Sup,Bridge,Auth,Exec,H,\mathbf c).
\]

- `K`: object-level knowledge;
- `W`: world model, relevance relation, route graph, or formulation;
- `M`: governed controller/method state;
- `rho`: ontology, objective, measurement, evaluator, and epoch regime;
- `R`: active responsibilities;
- `Phi`: accessible interface;
- `L`: registered method language and legal closure rules;
- `Art`: artifacts and native judgments;
- `Obl`: obligations;
- `Sup`: support-family hypergraph;
- `Bridge`: inference, identity, transport, promotion, revalidation, coercion, and adoption rules;
- `Auth`: grants, scopes, custody, and protected roots;
- `Exec`: occurrence-level execution facts;
- `H`: append-only negative, null, harmful, and revision history;
- `c`: vector resource ledger.

No scalarization of `c` is permitted without an independently supplied price/preference vector.

## 5. Capability semantics

A capability contract is

\[
\mathcal C=(I,A,C,M,L,P,\beta),
\]

where `I` is semantic information, `A` accessibility transformations, `C` computation/search, `M` model/decoder class, `L` method language, `P` placement/allocation policy, and `beta` a vector resource budget.

For seed artifacts `Seeds(Sigma)` and legal operations `Ops_C`, define

\[
Reach_{\mathcal C}(\Sigma)=\mu Z\,[Seeds(\Sigma)\cup Ops_{\mathcal C}(Z)].
\]

This distinguishes not found, inaccessible, compute-limited, outside method closure, and scientifically unresolved.

## 6. Primitive operational semantics

The workflow language uses primitive events:

```text
OBSERVE, ACQUIRE, RETRIEVE, EXECUTE, VERIFY_NATIVE,
INFER, MAP, MERGE, SPLIT, REFRAME, REVISE,
OPEN_OBLIGATION, BLOCK, REFUTE_BLOCKER, REVOKE,
TRANSPORT, REVALIDATE, DELEGATE, COERCE,
PROPOSE_CHANGE, ISOLATE, REPLAY, FRESH_TRANSFER,
ADOPT_EXTERNAL, PUBLISH, EPOCH_CHANGE.
```

A transition is

\[
\Sigma\xrightarrow{event,receipt}\Sigma'.
\]

Every rule declares its read/write frame, introduced facts, opened/closed obligations, consumed authority, and resource delta. The rules do **not** contain a precomputed `V and S and E and B` flag.

### 6.1 Operational admission rule

A target judgment `j` may be admitted only by an `ADOPT_EXTERNAL`, `PUBLISH`, `TRANSPORT`, `REVALIDATE`, `MERGE`, or registered scientific `INFER` transition whose concrete premises include:

- exact available artifacts;
- donor-native validation records;
- any required occurrence/integrity facts;
- a registered target bridge with exact object/responsibility/scope/content/epoch typing;
- a complete support family;
- explicit blocker state;
- a principal authorized for the transition.

`Admit_tau(Sigma,j)` means that such a transition occurs in the operational semantics. It is not defined by the normal form below.

## 7. Declared workflow class W-dagger

The fundamental theorem is proved for workflows satisfying:

1. every concrete trace is finite;
2. rules are finitary and typed;
3. within an epoch, derivations are positive and stratified;
4. revocation and regime change create a new stratum/epoch rather than mutating history;
5. authority morphisms attenuate unless an explicit protected coercion is used;
6. blocker states are explicit and three-valued;
7. every admitted target has at least one finite complete support family;
8. method operations and resource charges are declared;
9. candidate-controlled proposals have no external adoption authority;
10. execution-integrity coordinates remain orthogonal unless a registered bridge consumes them.

The theory does not assert that all real workflows satisfy these assumptions. Counterexamples outside the class are part of the assumption ledger.

## 8. Six-witness Scientific Advance normal form

A scientific advance certificate is

\[
\Pi=(\pi_R,\pi_V,\pi_X,\pi_S,\pi_E,\pi_B),
\]

where:

- `pi_R`: reachability/availability under `C` and resource budget;
- `pi_V`: donor-native validity for every relied-upon artifact;
- `pi_X`: target-required occurrence, chronology, custody, and integrity facts;
- `pi_S`: target-information-sufficiency witness;
- `pi_E`: typed target-bound entitlement bridge and authority;
- `pi_B`: blocker clearance and one complete non-revoked support family.

Define `ValidSANF_C(Sigma,j,Pi)` by independent structural validation of these witnesses.

### Fundamental Theorem of Auditable Scientific Advance

For every `W` in `W-dagger`:

\[
Advance_{\mathcal C}(\Sigma,j)
\iff
\exists\Pi\;ValidSANF_{\mathcal C}(\Sigma,j,\Pi).
\]

`Advance` means an artifact is first available under the capability semantics and then admitted by an operational scientific-status transition.

For an already-available artifact and a target whose integrity requirements are included in native validity, the theorem reduces to the four-factor Scientific Status Transition Factorization:

\[
Admit(\Sigma,j)\iff V\land S\land E\land B.
\]

Thus the earlier SSTF is a quotient of the complete theory, not a competing law.

## 9. Authority-neutral transformations

A transformation `F` is authority-neutral when it:

- adds no authorized evidence;
- introduces no new sound bridge;
- performs no protected revalidation;
- adds no stronger grant or coercion;
- preserves exact target identity and responsibility;
- does not acquire new protected information.

It may serialize, reorder, summarize, repeat, optimize, replay, or expose consequences already licensed by registered rules.

Let `D_R(A)` be the least discharge closure generated by artifacts `A` and bridges `R`. Then

\[
D_R(F(A))\subseteq D_R(A)
\]

up to representation-equivalent restatement. Equality holds when `F` is fully abstract for the registered decisions.

## 10. Responsibility-relative information

For responsibility `r`, let `T_r:Omega->Q_r` be the correct terminal map. Define

\[
\omega\sim_r\omega'\iff T_r(\omega)=T_r(\omega').
\]

A representation `Phi` is sufficient for `r` iff its fibres refine the `sim_r` classes. For a family `R0`, the minimal decision partition is the common refinement

\[
\bigvee_{r\in R_0}\Pi_r.
\]

A stored state is safely reusable for responsibility `r` exactly when its induced partition refines `Pi_r`, subject to current regime and authority compatibility.

## 11. Regime transport

A regime morphism `f:rho->rho'` contains maps for objects, responsibilities, evidence meaning, measurement semantics, authority, and epoch. A certificate transports only when all required squares commute or an explicit bridge supplies the discrepancy.

For composable `f,g`, transport is path independent exactly when

\[
T_{g\circ f}\cong T_g\circ T_f
\]

on all load-bearing coordinates. A noncommuting square is an explicit path-dependence witness and forces reopen or `CANNOT_CHECK`.

## 12. Recursive scientific evolution

An evolution certificate contains

```text
issue identity,
diagnosis and discriminator,
candidate intervention,
isolated execution,
replay,
fresh transfer,
protected assurance,
negative-history update,
external adoption.
```

A candidate proposal has zero adoption/merge/promotion authority by default. Evolution terminates when every accepted step strictly decreases a well-founded unresolved-obligation rank or consumes a finite protected change budget.

## 13. Claim ceiling

The theory is complete for `W-dagger` as a mathematical class. Remaining uncertainty concerns whether real ORION workflows and external scientific domains satisfy the assumptions, whether implementations conform, and whether the theory yields consequential benefit. Those are execution and adjudication tasks, not missing theoretical definitions.
