# P8 submission saturation closure

Date: 2026-08-19  
Normative paper: V2.1 / JAAMAS submission object.

## One-sentence contribution

> P8 types the interface between valid judgments and target scientific-obligation discharge across heterogeneous epistemic effects, with protected coercions, fail-closed blocker semantics and exact support-family revocation; it proves that a shared calculus has no inherent expressivity advantage over an ideal equally typed product of domain gates.

## Literature round B — current delegation and authorization composition

A fresh 2026-08-19 primary-source search found one material nearest-work update:

- **Bounded Agents: Delegation Security for Multi-Agent AI Systems** (arXiv:2608.15888, 2026-08-16) introduces an Agentic Principal Chain that carries and restricts delegated authority, evaluates requests against accumulated session state, checks prohibited combinations, and proves Blast Radius Monotonicity and Composition Soundness under its stated restriction/serialization assumptions. This is now a direct donor for authority narrowing and composition-aware multi-agent authorization. It must be cited; P8 may not imply that composition-safe delegated authorization is new.

Other current donors remain load-bearing:

- authorization propagation across multi-agent workflows (arXiv:2605.05440) owns transitive delegation, aggregation inference and temporal validity as an authorization-architecture problem;
- Intent-Governed Access Control (arXiv:2606.22916) makes intent a monotone narrowing policy attribute that may reduce but never expand static authority;
- SentinelAgent (arXiv:2604.02767) supplies verifiable delegation-chain properties and an external Delegation Authority Service;
- UCON/SecPAL own continuing authorization, obligations/conditions, policy proof and delegation;
- ETAS/FAVA/SAGE-Fin/action-evidence systems own typed effects, evidence-backed permission, exact action binding, freshness and pre-commit rechecking.

These papers substantially narrow P8's generic-governance novelty. They do not type **scientific evidential roles** such that a source-domain judgment can discharge a different target scientific obligation only by exact full-type match or an explicit protected coercion, and they do not make generic tool permission equivalent to scientific claim discharge.

Round B terminal: `MATERIAL_CITATION_CHANGE__NO_THEOREM_TERMINAL_CHANGE`.

## Literature round C — revocation, evidence, abstention and origin binding

A second query family targeted revocation, provenance, origin-bound authority, abstention and trust/evidence propagation. It resurfaced the existing donor envelope rather than a P8 replacement:

- provenance/origin-binding/non-amplification systems prevent laundering of authority-bearing evidence or memory;
- abstention benchmarks distinguish acting from justified refusal;
- usage-control and current agent-governance work perform freshness/revocation and ongoing decisions;
- current delegation systems enforce scope narrowing and accumulated-state restrictions.

No surfaced formalism provides P8's complete `(domain, kind, scope, content, epoch)` scientific-discharge typing together with exact support-family alternative-derivation revocation and the shared-vs-product equivalence negative theorem.

Round C terminal: `NO_MATERIAL_CLAIM_CHANGE`.

Saturation therefore closes after the Bounded Agents citation correction. Reopen if a donor-complete formalism establishes the same scientific-discharge relation under equivalent types/coercions/revocation semantics or a new counterexample falsifies V2.1.

## Nearest-parent / theorem audit

| P8 object | Strongest parent pressure | Residual / nonclaim |
|---|---|---|
| generic permission/delegation | UCON, SecPAL, propagation, IGAC, SentinelAgent, Bounded Agents | fully donor-owned |
| effect/evidence governance | ETAS, FAVA, SAGE-Fin, action-evidence chains | fully donor-owned |
| authority narrowing/composition | Bounded Agents + propagation literature | donor-owned generic authorization composition |
| complete judgment type | typed effect/authorization systems | P8 adds scientific role/domain/scope/content/epoch as discharge type across epistemic domains |
| protected coercion | authorization/delegation transformations | only complete-type composable coercion may change scientific-discharge type |
| hard blocker semantics | UCON/authorization/abstention | absence is not refutation; `UNDETERMINED -> CANNOT_CHECK` |
| exact revocation | ongoing authorization + provenance dependency | alternative complete support families avoid both over- and under-revocation |
| permission/scientific-discharge separation | generic authorization vs evidence governance | main conceptual residual: both layers can be correct while disagreeing on whether a scientific effect is currently justified |
| shared/product architecture | distributed vs centralized policy systems | negative theorem: equal semantics imply extensional equivalence; centralization has no inherent scientific expressivity advantage |

## Blind review round 1

### R1 MAS/normative-AI novelty reviewer
Attack: recent delegation systems already provide authority narrowing, composition checks and revocation.
Resolution: accepted and made explicit; Bounded Agents becomes a direct donor. P8 owns none of generic delegation security. Residual remains target scientific-obligation discharge across heterogeneous epistemic domains.
Verdict: no unresolved major/blocking concern after citation insertion.

### R2 theorem reviewer
Attack: `no active blocker` is fail-open if unobserved blockers count as absent; confidence/utility may be confused with permission; revocation graph may destroy valid alternatives.
Resolution: V2.1 already repairs all three: blocker states are ESTABLISHED/REFUTED/UNDETERMINED with refutation required for authorization; confidence/EU cannot promote denied/unresolved effects; support-family revocation preserves any complete independent derivation.
Verdict: no unresolved major/blocking concern.

### R3 governance/venue reviewer
Attack: why centralize if a correct product of domain gates can do the same thing?
Resolution: the paper's equivalence theorem says exactly that. Centralization is not sold as inherently superior; any practical advantage would need independent evidence about interface consistency/audit burden/revocation coverage.
Verdict: no unresolved major/blocking concern.

## Blind review round 2

- **Reduction attack:** an ideal UCON/SecPAL/ETAS/FAVA/delegation product with the exact same scientific types and coercions ties the shared calculus. Accepted; this is the negative theorem, not a threat hidden from the paper.
- **Deny-all attack:** frozen authority contracts include clean authorized cases and a registered-coercion positive control; blanket refusal cannot pass.
- **Cross-domain laundering attack:** five explicit laundering families require complete-type composition, not domain-only reachability.
- **Self-promotion attack:** protected-root rules block candidate-controlled admission; P5 remains owner of Self-ORION adoption.
- **P9/P10 contamination attack:** #461 method-authority anti-laundering is successor-additive and not retroactive evidence for the frozen P8 paper.

Second round: no new unresolved major/blocking concern.

## Venue/style closure

Primary: **Autonomous Agents and Multi-Agent Systems (JAAMAS)**. Fallback: **Artificial Intelligence (AIJ)**; secondary JAIR if scope fit is preferable.

Presentation rules:

1. distinguish generic permission from scientific discharge in the first page before dense notation;
2. lead the related-work section with delegation/UCON/current agent-authorization donors rather than security strawmen;
3. keep `AUTHORIZED / DENIED / CANNOT_CHECK` examples concrete;
4. present the shared/product equivalence result prominently as scientific knowledge, not buried negative evidence;
5. keep proof assumptions on blocker freshness/coercion completeness/support families explicit;
6. finite contract cases support non-vacuity, not empirical deployed-agent superiority;
7. no P9/P10 or P6 successor semantics imported into current claims.

No venue fallback authorizes hiding the equivalence result or broadening to generic authorization novelty.

## Citation/formal/reproduction audit

- foundational UCON/SecPAL and current ETAS/FAVA/AgentBound/propagation/provenance/abstention donors are already cited;
- Bounded Agents is the one required current citation addition;
- V2.1 checker makes fail-open blocker reading and confidence/utility substitution explicit countermodels;
- full 5x5 evidence-domain matrix, five laundering attacks, clean authorized/blocked cases, `CANNOT_CHECK`, and registered-coercion control remain frozen;
- content binding, deterministic reproduction and JAAMAS PDF audit remain required exact-head gates;
- no decorative significance test is added to exact finite contract results.

## Whole-paper invariant

Forbidden drift:

- authority narrowing/composition -> P8 generic novelty;
- exact artifact/freshness -> P8 novelty;
- high confidence/utility -> permission;
- unobserved blocker -> refuted blocker;
- revoking one premise -> revoke certificate despite another complete derivation;
- shared calculus -> inherently more expressive than ideal typed product;
- term `authority laundering` -> terminological novelty;
- successor #461 -> current P8 evidence.

Terminal: `P8_SATURATION_CONVERGED_PENDING_BOUNDED_AGENTS_CITATION_AND_PACKAGE_REBUILD`.
