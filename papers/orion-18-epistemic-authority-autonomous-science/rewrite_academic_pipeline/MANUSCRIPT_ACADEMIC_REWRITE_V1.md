# A Compositional Calculus for Typed Scientific Authority

## Abstract

Scientific workflows combine evidence produced in different domains, at different times, and under different scopes. A composition rule is unsafe if it silently widens a donor judgment, treats a blocked premise as established, or lets evidence for one claim discharge another. We present a typed non-widening calculus for composing scientific authority records.

A discharge record is indexed by domain, evidence kind, scope, content identity, and epoch. Native donor judgments are conserved by default. Cross-type reuse requires an explicit protected coercion whose bridge is itself checked. A contradiction revokes every dependent support family, while unresolved premises remain unresolved rather than being collapsed into acceptance or rejection. Independent authority components compose by a product rule that preserves each component's local blockers.

The formal core establishes native conservation, non-widening, bridge necessity, revocation monotonicity, and equivalence of centralized and componentwise product evaluation under the declared rules. The finite validation contains 3,072 distinct authority-state configurations. Replaying each configuration under 13 donor labels yields 39,936 evaluations, but donor identity is not a semantic transition input, so this is replication across labels rather than 13-fold state expansion. Targeted tests include 65 one-coordinate type separations, 65 protected coercion restorations with matching bridge-necessity checks, partial and complete support revocation, and decentralized product comparisons. A 20-case evidence-discharge panel across four domains has exact internal conformance with zero false promotions, but its gold and independent checks remain inside the same research programme.

The contribution is a formal non-widening composition contract and an auditable finite instantiation. It does not establish externally governed scientific authority, deployed-agent superiority, or a general novelty claim for authorization logics.

## 1. Introduction

Evidence does not carry unlimited authority. A result can be valid for one domain, endpoint, population, epoch, or content object and still be inapplicable to another. The problem becomes acute when automated workflows compose many such results. A mechanically valid chain can still be scientifically unsound if one step widens scope or substitutes a nearby claim.

We study authority composition as a typed formal problem. The central question is:

> Under what rules can locally adjudicated scientific judgments be transported and combined without granting a stronger judgment than any authorized path supports?

The goal is not to automate the social institution of scientific authority. It is to define a fail-closed calculus whose transitions can be checked and whose boundaries are explicit.

## 2. Typed discharge records

A scientific discharge record has type
\[
\tau=(d,k,s,c,e),
\]
where:

- \(d\) is the scientific domain;
- \(k\) is the evidence or judgment kind;
- \(s\) is the authorized scope;
- \(c\) is a content identity;
- \(e\) is the epoch or version.

The record also carries a verdict such as established, refuted, or unresolved, together with its support family and provenance.

Two records with similar prose are not interchangeable unless their types match or an explicit coercion is admitted. Content identity prevents a result for one claim from discharging another. Epoch prevents stale support from being transported after a material change.

## 3. Native conservation and non-widening

**Rule 1 (native conservation).** A native donor verdict is preserved when transported within its exact type.

**Rule 2 (non-widening).** A transport or composition may return a judgment no stronger, broader, or newer than the authorized source path.

Non-widening applies to domain, evidence kind, scope, content, and epoch. A local finding cannot become a general finding merely because several records agree.

**Theorem 1 (native conservation).** Under Rules 1 and 2, exact-type transport cannot change a native verdict.

**Theorem 2 (no implicit widening).** No sequence of uncoerced transports can produce a discharge at a type not authorized by every edge in the path.

The proofs follow from type preservation and monotonicity of the admitted scope order.

## 4. Protected coercion

Some scientific reuse is legitimate across types. A mechanistic study can inform a related domain, or a result at one granularity can be specialized to a narrower scope. Such reuse is represented by a protected coercion
\[
\gamma:\tau_1\rightsquigarrow\tau_2.
\]

A coercion is not a cast that erases the mismatch. It carries a bridge obligation stating why evidence of type \(\tau_1\) is valid for \(\tau_2\).

**Theorem 3 (bridge necessity).** Removing the bridge from a protected coercion admits at least one widening transition that the typed calculus rejects.

The finite one-coordinate tests instantiate this property across every type coordinate. When a single coordinate is changed, native reuse is rejected. Supplying the corresponding registered bridge restores only the authorized transition.

## 5. Blockers and three scientific states

The calculus uses three blocker states:

- established;
- refuted;
- unresolved.

A refuted premise blocks dependent promotion. An unresolved premise does not become refuted, but it also cannot discharge a positive claim. The third state is necessary because absence of authority is not evidence of falsehood.

This treatment prevents optimistic transport, which ignores unresolved premises, and pessimistic transport, which destroys potentially valid support before the uncertainty is resolved.

## 6. Support families and revocation

A claim can depend on several support families. Revocation must track the dependency graph rather than delete an unrelated judgment.

**Rule 3 (partial revocation).** Revoking one support family removes only the conclusions that require that family.

**Rule 4 (complete revocation).** If every authorized support family for a conclusion is revoked, the conclusion is no longer established.

**Theorem 4 (revocation monotonicity).** Revocation cannot create a stronger verdict, and complete loss of support cannot leave the dependent conclusion established.

The finite panel includes both partial survival and complete revocation cases. These are exact conformance checks of the declared dependency semantics.

## 7. Product composition

Scientific authority may be decentralized across independent components. Let
\[
A=A_1\times\cdots\times A_m
\]
be a product of local authority states. A global conclusion is established only when every required component discharges its local obligation.

**Theorem 5 (product equivalence).** Under componentwise non-widening and blocker preservation, centralized evaluation of the product equals composition of the local evaluations.

This result allows decentralized checking without allowing one component's favorable verdict to compensate for another component's blocker.

## 8. Finite validation

The validation enumerates 3,072 distinct authority-state configurations. Each is replayed under 13 donor labels, producing 39,936 evaluations.

The distinction between configurations and labels is important. Donor identity is not read by the transition semantics in this validation. The 13-fold replay checks label invariance and interface compatibility; it does not create 39,936 semantically independent mechanisms.

Targeted tests include:

- 65 one-coordinate type separations;
- 65 protected coercion restorations;
- 65 matching bridge-necessity attacks;
- 26 partial revocation survivals;
- 13 complete revocations;
- all registered decentralized product comparisons.

The formal claims are supported by proof. Enumeration tests implementation agreement and boundary behavior.

## 9. Evidence-discharge panel

A separate 20-case panel spans four scientific domains. It includes positive, negative, unresolved, type-mismatch, revocation, and action-versus-scientific-authority cases.

The calculus matches the internally frozen adjudication on all cases and produces zero internally scored false promotions. Twelve cases explicitly separate permission to perform an action from authority to promote a scientific claim.

The result is bounded conformance. The panel, gold, and checking implementations all remain under the same programme's custody. The outcome does not establish external scientific validity or agreement among independent institutions.

## 10. Donor boundary

Authorization logics, provenance systems, type systems, truth-maintenance systems, access control, proof-carrying data, and formal workflow composition own the underlying ideas. The paper does not claim generic authorization or provenance novelty.

The residual contribution is a scientific specialization: content- and epoch-indexed discharge types, protected cross-domain coercions, support-family revocation, and a product rule that preserves unresolved and refuted blockers.

## 11. Limitations

The calculus assumes that native judgments and bridge obligations are supplied by legitimate authorities. It cannot determine whether an experiment is scientifically correct merely by checking its type. The finite state model does not capture every institutional policy or evidential relation.

All validation is internal. No externally governed adjudication or second custodian is present. The work does not establish deployed-agent superiority, autonomous scientific authority, or broad real-world safety.

## 12. Conclusion

Scientific authority should not widen merely because evidence is composable. A typed discharge record makes domain, kind, scope, content, and epoch explicit; native conservation prevents silent reinterpretation; protected coercions expose the bridge needed for legitimate reuse; and revocation and product rules preserve blockers. The result is a formal contract for auditable scientific composition. Its authority remains exactly where the model places it: in the declared rules and their bounded verification, not in an automated claim to govern science.
