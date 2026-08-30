# Typed Non-Widening Composition for Scientific Authority

## Abstract

Evidence composition becomes unsafe when a valid local judgment is widened across domain, scope, content, or time without an authorized bridge. We define a typed calculus in which a scientific discharge has type
\[
(d,\ k,\ s,\ c,\ e),
\]
recording domain, evidence kind, scope, content identity, and epoch. Exact-type transport conserves the native verdict. Cross-type transport requires an explicit protected coercion. Refuted premises revoke dependent support; unresolved premises remain unresolved. Independent components compose by a product rule that cannot use success in one component to compensate for a blocker in another.

The formal results establish native conservation, absence of implicit widening, bridge necessity, monotone revocation, and centralized–decentralized product equivalence under the declared semantics. The implementation audit enumerates 3,072 distinct authority-state configurations and replays them under 13 donor labels, for 39,936 evaluations. Because donor label is semantically inert in this model, the replay is an invariance check, not 13-fold scientific coverage. The audit also contains 65 one-coordinate separation attacks, 65 bridge-controlled restorations, partial and complete revocation cases, and decentralized product checks. A 20-case, four-domain panel has exact internal conformance and zero internally scored false promotion, but no external authority or independent custodian adjudicates the cases.

The supported contribution is a fail-closed formal composition contract. It does not grant scientific authority to an agent, validate donor judgments, or establish general cross-domain transfer.

## 1. Why evidence composition needs types

Scientific results are bounded. A conclusion may hold for one endpoint, population, apparatus, content object, or protocol version and fail outside it. Automated workflows can nevertheless combine records that look similar and thereby produce a stronger conclusion than any source authorized.

The problem is not solved by provenance alone. Knowing where a record came from does not say what it is allowed to discharge. A safe composition rule needs both identity and scope.

We therefore treat scientific authority as a typed, non-widening relation. The type does not certify that a native judgment is true. It constrains what can be concluded from a judgment already admitted by an authority.

## 2. Discharge type and verdict

A discharge type is
\[
\tau=(d,k,s,c,e).
\]

The coordinates denote domain, evidence kind, scope, content identity, and epoch. A record also carries a verdict in
\[
\{\text{ESTABLISHED},\text{REFUTED},\text{UNRESOLVED}\}
\]
and one or more support families.

Content identity prevents evidence for a neighboring claim from being reused as if it addressed the current claim. Epoch prevents a judgment from crossing a material protocol or object change without a new bridge.

## 3. Native conservation

For exact-type transport, the calculus preserves the source judgment.

**Theorem 1 (native conservation).** If source and target types are equal, transport returns the native verdict.

**Theorem 2 (non-widening).** A sequence of uncoerced transports cannot produce a discharge outside the intersection of the scopes authorized along the path.

These are structural guarantees. They do not depend on how persuasive the evidence appears.

## 4. Protected coercion

Legitimate cross-type reuse is represented by
\[
\gamma:\tau_1\rightsquigarrow\tau_2
\]
together with a bridge obligation. The bridge records the scientific reason the source judgment applies at the target type.

The implementation audit changes each type coordinate one at a time. The unbridged transition is rejected in all 65 registered separations. The corresponding protected bridge restores the authorized transition, and removing the bridge reopens the failure.

The scientific content is not that every bridge is valid. It is that a mismatch cannot disappear invisibly.

## 5. Unresolved is not refuted

Collapsing unresolved evidence into acceptance is unsound. Collapsing it into refutation can destroy valid support before the missing fact is known.

The calculus therefore preserves a third state. An unresolved required premise blocks positive discharge without asserting the opposite conclusion. This rule is central to safe recursive composition because later evidence can resolve the premise without laundering or prematurely revoking the earlier record.

## 6. Revocation by support family

Claims can have multiple independent support families. Revoking one family should remove only conclusions that depend on it. Complete loss of all authorized support must remove establishment.

**Theorem 3 (revocation monotonicity).** Revocation never strengthens a verdict.

**Theorem 4 (complete-support loss).** A conclusion with no remaining authorized support family cannot remain established.

The finite audit includes 26 partial-revocation survivals and 13 complete revocations. These cases check dependency semantics rather than population performance.

## 7. Decentralized product law

Suppose separate authorities discharge separate components. The product rule evaluates each required component locally and combines the results without compensation.

**Theorem 5 (product equivalence).** When local evaluators preserve types and blockers, centralized product evaluation equals the product of local evaluations.

The theorem supports modular checking. It does not imply institutional independence. Several components controlled by one programme remain one custody domain.

## 8. What the finite audit measures

The audit has 3,072 semantically distinct state configurations. Repeating them under 13 donor names yields 39,936 evaluations. Since donor name does not affect the transition function, the repeated axis tests invariance and implementation consistency.

Likewise, complete coverage of donor-pair labels should not be read as many independent composition mechanisms when the same transition profile is reused. The scientifically relevant coverage lies in the state coordinates, blocker patterns, coercions, and support-family changes.

This accounting prevents replication axes from being reported as new semantic diversity.

## 9. Four-domain evidence panel

Twenty internally adjudicated cases instantiate evidence discharge across four domains. The calculus matches the frozen labels, produces no internally scored false promotion, and correctly separates permission to act from authority to promote a claim.

The panel remains an internal conformance test. It has no blinded external gold, independent institutional custodian, or evidence that deployment improves scientific decisions.

## 10. Donor subtraction

Type systems, authorization logics, provenance, truth maintenance, proof-carrying data, and workflow composition provide the donor theory. The residual is their bounded scientific-authority specialization:

- content- and epoch-indexed discharge;
- explicit cross-domain bridges;
- three-valued blockers;
- support-family revocation;
- non-compensatory product composition.

The paper does not claim a generic authorization breakthrough.

## 11. Limits

The calculus cannot validate the truth of native scientific judgments. It assumes authorities, type assignments, and bridge obligations are supplied correctly. Its formal model is smaller than real institutional science.

All empirical adjudication and checking are internal. The work does not establish externally governed authority, organizational independence, agent superiority, or general safety.

## 12. Conclusion

Scientific evidence can be composed without being widened. Typed discharge makes the authorized domain, kind, scope, content, and epoch explicit. Native conservation preserves local judgments, protected coercion exposes every cross-type bridge, three-valued blockers keep unresolved evidence from becoming acceptance or refutation, and revocation and product laws preserve dependencies. The resulting calculus is useful because it limits automated composition. It does not replace the authorities whose judgments it carries.
