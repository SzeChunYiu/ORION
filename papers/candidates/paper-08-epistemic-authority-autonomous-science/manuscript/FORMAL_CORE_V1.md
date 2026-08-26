# ORION-18 formal core V1

**Candidate paper:** A Theory of Epistemic Authority for Autonomous Science  
**Authority:** mathematical working object; novelty not yet authorized  
**Date:** 2026-08-17  
**Donor policy:** absorb effect typing, evidence-backed authorization, abstention and provenance mechanisms; do not relabel them.

## 1. Domains, effects, and judgments

Let `D` be a finite set of epistemic effect domains. The initial ORION embedding uses

\[
D_0=\{\mathsf{REFRAME},\mathsf{SEARCH\_STOP},\mathsf{MAP\_MERGE},\mathsf{ASSERT},\mathsf{SELF\_MODIFY}\},
\]

but the calculus is not restricted to these five domains.

### Definition 1 (effect request)
An effect request is

\[
e=(id,d,op,S,p,epoch),
\]

where `id` is an identity, `d\in D` is the effect domain, `op` the proposed operation, `S` its target scope, `p` its payload/proposed state delta, and `epoch` the state/version against which authorization is requested.

A system may be capable of constructing or executing `e` even when it is not authorized to commit `e`.

### Definition 2 (typed judgment)
A judgment has the form

\[
j=(kind,d,scope,content,prov,epoch),
\]

where `kind` is one of support, blocker, obligation-satisfied, grant, revocation, capability, utility, or closure.

Judgments are domain-typed. A judgment in domain `d` is not automatically usable in another domain `d'`.

### Definition 3 (authority context)
An authority context is

\[
\Gamma=(J,O_h,O_s,G,C,R,P,H),
\]

where:

- `J` is the set of active typed judgments;
- `O_h(e)` is the set of hard/non-compensatory obligations for effect `e`;
- `O_s(e)` is the set of soft/resource obligations/preferences;
- `G` is the set of authority grants/roots;
- `C` is the registry of explicitly allowed cross-domain coercions;
- `R` is the revocation relation/state;
- `P` is the evidence/authority dependency and provenance graph;
- `H` is the retained request/deny/commit/revoke history.

A bare token such as `PASS`, `VERIFIED`, `HIGH_CONFIDENCE` or `DONE` is not an authority judgment without domain, scope, content identity and epoch.

## 2. Requested versus committed effects

ORION adopts the request/commit distinction made explicit by current effect/authorization systems:

\[
\mathsf{REQUEST}(e),\quad \mathsf{ALLOW}(e),\quad \mathsf{DENY}(e),\quad \mathsf{CANNOT\_CHECK}(e),\quad \mathsf{COMMIT}(e).
\]

### Definition 4 (commit rule)
An effect may commit only if an authorization derivation exists for the same effect identity, scope, content identity and valid epoch:

\[
\Gamma\vdash \mathsf{Auth}_d(e)
\quad\Longrightarrow\quad
\mathsf{COMMIT}(e).
\]

Computational success, model confidence, expected utility, a prior successful replay, or a foreign-domain `PASS` is not a commit rule.

### Definition 5 (`CANNOT_CHECK`)
`CANNOT_CHECK(e)` means at least one mandatory authorization premise cannot currently be established or refuted from admissible evidence.

It is not equivalent to `DENY`: `DENY` has a satisfied blocker or failed mandatory condition. It is also distinct from resource `DEFER`.

## 3. Hard obligations and non-compensation

### Definition 6 (hard authorization obligations)
Let

\[
O_h(e)=\{o_1,\ldots,o_k\}.
\]

A hard obligation is satisfied only by a content-bound typed judgment whose scope/epoch match the obligation contract.

Authorization requires

\[
\forall o\in O_h(e):\mathsf{Sat}(o)
\]

and absence of an active blocker. Soft utility/preferences may rank multiple already-admissible actions but cannot discharge a hard obligation.

### Proposition 1 (finite additive penalties cannot encode an absolute blocker)
Consider an authorization score

\[
S(e)=\sum_i w_i x_i-Mb,
\]

with fixed threshold `\theta`, finite blocker penalty `M<\infty`, positive evidence increments, and blocker bit `b=1`. If positive increments are not globally bounded, there exists a finite amount of positive evidence such that `S(e)\ge\theta` while the blocker remains active.

#### Proof
Choose positive evidence total greater than `\theta+M`. Then `S(e)\ge\theta` despite `b=1`. Therefore a finite additive penalty cannot represent an absolute non-compensatory blocker without a separate veto/conjunctive/lexicographic layer or an externally imposed bound. `\square`

### Limitation
A bounded fixed-dimensional scoring system can simulate a veto by choosing a dominating finite weight. The proposition concerns extensible/unbounded evidence accumulation and should not be overclaimed as a result about every scalar policy.

## 4. Authority grants and protected roots

### Definition 7 (grant)
A grant is

\[
g=(issuer,d,scope,premises,epoch,expiry,lineage).
\]

`issuer` is either a trusted root or an entity whose own delegation authority is derivable. A grant may narrow scope; widening requires an explicit authority-producing rule.

### Definition 8 (non-escalating derivation)
A derivation is non-escalating when every authority conclusion is obtained by:

1. retaining a valid in-scope grant;
2. narrowing an existing grant;
3. applying a registered sound coercion; or
4. using a trusted authority-producing rule whose root is outside the candidate effect's write control.

## 5. Cross-domain coercions and authority laundering

### Definition 9 (coercion)
A cross-domain coercion is an explicit rule

\[
c:d\Rightarrow d'
\]

with premises `Prem_c`, a scope map, an evidence-preservation condition, and an issuer/root authorized to register that coercion.

A coercion is not merely semantic similarity between judgments.

Typical non-coercions without additional premises include:

- planner confidence `\not\Rightarrow` reframe authority;
- route exhaustion `\not\Rightarrow` task closure;
- semantic similarity `\not\Rightarrow` merge authority;
- citation support `\not\Rightarrow` verified-science authority;
- replay improvement `\not\Rightarrow` self-promotion authority.

### Definition 10 (authority laundering)
A derivation of `\mathsf{Auth}_{d'}(e)` contains authority laundering when it uses an authority-bearing judgment rooted in `d\neq d'` and no valid registered coercion path from `d` to `d'` appears in the derivation.

### Theorem 2 (typed anti-laundering)
Assume all judgments are domain-typed and the only rules capable of changing authority domain are registered coercions. Then no derivation can conclude `\mathsf{Auth}_{d'}(e)` from authority-bearing premises exclusively rooted in `d\neq d'` unless a valid coercion path from `d` to `d'` occurs.

#### Proof
By induction on derivation height. Base axioms preserve their declared domain. For the induction step, every ordinary rule preserves the authority domain, so a conclusion in `d'` can arise only from premises already in `d'`. The only rules whose conclusion changes domain are registered coercions. Therefore a derivation beginning with authority-bearing judgments in `d` can reach `d'` only through at least one coercion; repeated changes require a coercion path. `\square`

### Corollary 2.1
A generic token such as `PASS`, `SUCCESS`, or high confidence is unsafe as authority currency unless its type includes the domain/scope or it is explicitly interpreted through a sound coercion.

## 6. Provenance, dependency, and revocation

Let `P` be a directed dependency graph over evidence judgments, grants, coercion applications and authorization certificates.

### Definition 11 (authorization certificate)
A certificate is

\[
\kappa=(e,d,scope,roots,premises,derivation,epoch).
\]

Every premise used by the derivation is an ancestor of `\kappa` in `P`.

### Definition 12 (revocation closure)
For revoked object `x`, define

\[
\operatorname{RevDesc}_P(x)
\]

as every authorization certificate or authority-bearing intermediate judgment that depends transitively on `x` and lacks an independent still-valid derivation.

### Theorem 3 (dependency-grounded revocation)
If `P` is sound for authorization dependencies, revoking `x` and invalidating `\operatorname{RevDesc}_P(x)` removes every authorization whose derivation necessarily depends on `x`. Certificates with a complete independent derivation not depending on `x` may remain valid.

#### Proof
For any certificate necessarily depending on `x`, soundness places `x` on an ancestor path to that certificate, so it is included in the revocation closure and invalidated. If a certificate has another complete derivation whose premises remain valid and exclude `x`, dependency necessity does not hold for that alternative; preserving it is sound. `\square`

### Corollary 3.1
Full authority reset is unnecessary whenever valid independent derivations exist outside the revoked dependency closure.

## 7. Timing: pre-effect versus post-hoc refusal

### Definition 13 (pre-effect authorization)
An authorization mechanism is pre-effect for effect class `E_f` when every irreversible/effectful commit in `E_f` is preceded by a valid authorization judgment for the exact requested effect identity and epoch.

### Proposition 4 (post-hoc abstention is not preventive authorization)
If an irreversible effect commits before the system emits `DENY` or `CANNOT_CHECK`, the later abstention cannot satisfy pre-effect authorization for that effect.

This is a structural observation. Agentic-abstention work already empirically identifies post-hoc abstention; ORION-18 adopts that failure mode rather than claiming it.

## 8. Self-promotion boundary

### Proposition 5 (candidate-controlled admission cannot guarantee external promotion soundness)
Suppose candidate transformation `m` can rewrite both the predicate deciding its own admission and every evidence value read by that predicate, with no protected invariant/root outside `m`'s write authority. Then for any `m` there exists a reachable admission policy/evidence state that authorizes `m`, independently of an externally defined correctness property.

#### Proof
The candidate may choose a constant-accepting predicate or produce candidate-controlled evidence satisfying its own accepting branch. Because no protected external constraint relates admission to the external property, internal acceptance does not imply that property. `\square`

## 9. ORION ORION-11–ORION-15 embeddings

These embeddings are ownership constraints, not new contributions.

### `REFRAME` — ORION-11
Capability: construct a new formulation/search universe.  
Authority: mutate only coordinates licensed by the responsibility/evidence diagnosis; dependent closures reopen.

### `SEARCH_STOP` — ORION-12
Capability: stop a route or return an answer.  
Authority: route stop and task stop are distinct; unresolved/censored mandatory obligations block global closure.

### `MAP_MERGE` — ORION-13
Capability: propose correspondences or merged constructs.  
Authority: similarity does not discharge referent/context/measurement/obstruction obligations.

### `ASSERT` — ORION-14
Capability: state a claim.  
Authority: protected, content-bound evidence and independent checks govern scientific-authority promotion. ORION-14 owns this within-domain transition.

### `SELF_MODIFY` — ORION-15
Capability: generate/compile/replay a self-change.  
Authority: protected evaluation, fresh transfer, negative-history and non-self-promotion constraints govern admission. ORION-15 owns this within-domain transition.

### Theorem target 6 (conservative gate embedding)
For each ORION-11–ORION-15 domain, instantiate the general calculus so that on the domain's frozen native cases it reproduces the existing gate decisions exactly.

Failure to embed a domain faithfully is evidence against the claimed generality.

## 10. Donor embeddings and protected ownership

ORION-18 explicitly absorbs, but does not relabel:

- **ETAS (arXiv:2607.17780):** typed effects, residual obligations, requested/denied/committed trace semantics, policy safety;
- **FAVA (arXiv:2607.27267):** evidence-backed permission graphs, deterministic SMT authorization and pre-effect enforcement;
- **AgentAbstain (arXiv:2607.10059):** paired act/abstain evaluation and pre/post-effect abstention timing;
- **ProvenanceGuard (arXiv:2606.18037):** source-aware claim/evidence attribution as an independent verification dimension;
- **execution-provenance work (arXiv:2606.04990):** trace/evidence lineage, granularity and recovery/audit structures;
- **Agent-Sentry (arXiv:2603.22868), Policy Cards (arXiv:2510.24383), and user-permission systems (arXiv:2607.13718):** behavioral bounds, intent/policy representation, obligations and runtime enforcement;
- **deontic/action/authorization logics:** permission, obligation, delegation and revocation as mature formal objects.

The possible residual is therefore not “agents need permissions.” It is the cross-domain scientific-epistemic composition problem: whether heterogeneous authorization domains can share a typed derivation layer that preserves donor-native decisions while preventing invalid authority transport, enabling dependency-grounded revocation, and distinguishing unresolved authority from refusal.

## 11. Hostile cases required by #341/#353

The deterministic/protected evaluation must include at least:

1. foreign `SEARCH_STOP` pass presented as `ASSERT` authority;
2. correct citation support presented as independent verification;
3. strong semantic similarity presented as merge permission;
4. low expected search value presented as task closure;
5. replay improvement presented as self-change promotion authority;
6. evidence/grant ancestor revoked after authorization but before commit;
7. narrow grant reused on an out-of-scope target;
8. old authorization certificate replayed after relevant state changes;
9. irreversible effect committed before a blocker is recognized;
10. negative control in which every hard obligation is satisfied and refusal is unnecessary;
11. positive control with an explicitly registered sound cross-domain coercion;
12. revocation control where an independent trusted derivation should survive.

Strong baselines must include the existing ORION-11–ORION-15 gates and, where implementation permits, FAVA/ETAS-style typed-policy variants rather than scalar confidence strawmen.

## 12. Deterministic checking obligations

The finite checker must verify at least:

1. cross-domain judgments cannot authorize without a registered coercion;
2. scope narrowing is allowed but widening is not;
3. the additive-blocker counterexample exists for arbitrary finite penalties under extensible evidence;
4. revocation propagates through the dependency closure but preserves independent derivations;
5. a candidate-controlled constant-accept policy defeats internal self-certification;
6. authority-laundering fixtures fail closed;
7. conservative ORION-11–ORION-15 embedding fixtures reproduce native toy decisions.

No LLM API is required.

## 13. Nearest-work pressure and nonclaims

This core does **not** claim novelty for:

- deontic/input-output/dynamic action logic;
- authorization/access-control calculi;
- delegation, scope restriction or revocation;
- typed effects or residual obligations;
- evidence-backed permission graphs or SMT authorization;
- abstention/selective prediction;
- provenance-based action guarding;
- runtime shielding/policy enforcement;
- capability-versus-permission governance frameworks;
- ORION-14's protected scientific-authority transition;
- ORION-15's no-self-promotion/protected-evaluation mechanism.

The widened candidate residual is:

\[
\text{donor-faithful typed authorization across heterogeneous epistemic effects}
+
\text{non-compensatory obligations}
+
\text{explicit sound cross-domain coercions}
+
\text{anti-laundering}
+
\text{dependency-grounded revocation}
+
\text{protected-root semantics}.
\]

This residual must survive #340/#352/#343 and must produce a discriminator beyond vocabulary-level unification.

## 14. What this formal core establishes now

The formal core establishes elementary consequences of its definitions:

- finite additive penalties do not encode an unbounded absolute blocker;
- domain-preserving derivations cannot cross authority domains without an explicit coercion;
- sound dependency lineage supports targeted revocation;
- post-hoc refusal cannot retroactively prevent an already committed irreversible effect;
- candidate-controlled admission cannot guarantee an external promotion property.

It does **not** establish:

- novelty over authorization/deontic/effect-system literature;
- semantic soundness of every trusted root/coercion;
- that one shared calculus is better than independent domain gates;
- that all ORION-11–ORION-15 gates embed without semantic loss;
- peer-review readiness or separate-paper status.

Current novelty/promotion terminal remains `CANNOT_CHECK`.