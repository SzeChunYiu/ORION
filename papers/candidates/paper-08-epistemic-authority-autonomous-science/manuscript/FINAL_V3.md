# A Compositional Calculus for Cross-Domain Scientific Authority

**Paper VIII current science manuscript — V3 refinement**  
**Date:** 2026-08-20  
**Historical base:** V2/V2.1 formal core and JAAMAS submission bytes retained  
**Successor evidence:** `research/claim_expansion/p8/P8_X4_*`  
**Science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`

V3 preserves the V2.1 blocker, coercion, revocation, and typed-discharge semantics while elevating their constructive consequence: heterogeneous authorization and scientific-verification mechanisms can be composed into one portable scientific-discharge layer without weakening their native authority.

## Abstract

Autonomous scientific systems increasingly combine strong but heterogeneous authority mechanisms: evidence-backed permission graphs, proof-carrying action certificates, delegation provenance, authority narrowing, principal-chain authorization, typed verifier certificates, heterogeneous authorization receipts, scientific release gates, claim-to-evidence verification, contract-governed research artifacts, evidence-calibrated adjudication, and evidence-ledger review. Each mechanism can be correct for its native object while the scientific obligation to be discharged belongs to a different domain, kind, scope, content identity, or epoch. The critical systems question is therefore compositional: **when may one valid local authority judgment acquire scientific force in another domain?**

P8 introduces a typed scientific-discharge calculus over **thirteen donor families**. Native donor verdicts are conserved. Scientific authority propagates through heterogeneous chains when the target type `(domain, kind, scope, content, epoch)` is preserved or narrowed, or when an explicit protected coercion supplies the complete cross-domain bridge. Blockers retain three epistemically distinct states—`REFUTED`, `UNDETERMINED`, and `ESTABLISHED`—so uncertainty remains actionable as `CANNOT_CHECK`. Alternative complete support families make revocation exact: an independent proof can preserve authority after one support route is revoked, while loss of every complete route removes discharge.

The final X4 model exhausts **39,936 exact authority states** with **zero donor-conservativity violations** and **zero mismatches against an equally typed decentralized product**. It contains 65 one-coordinate scientific-type separations, 65 protected-coercion restorations with 65 matched bridge-necessity witnesses, the three-state blocker law across all thirteen donors, 26 independent-support revocation survivals and 13 complete-support revocations, plus **169/169 successful heterogeneous ordered donor-pair compositions** under compatible scientific authority and **169 matched non-widening necessity witnesses**. A second implementation independently reproduces the canonical enumeration and digest.

P8 therefore establishes a positive and architecture-independent result: heterogeneous authorization, delegation, verification, release, and adjudication mechanisms can be composed systematically into a common scientific-discharge layer when authority is explicitly typed, non-widening by default, bridgeable through protected coercion, fail-closed under unresolved blockers, and revocable over complete support families. The exact decentralized-product tie is a portability theorem showing that these semantics can be deployed centrally or in a correctly integrated distributed architecture without changing the scientific judgment.

## Donor-engulfment architecture

P8 retains the strongest useful structure from two neighboring layers and composes them rather than replacing them.

### Action, delegation, and authorization donors

The calculus reuses evidence-backed permission graphs and deterministic authorizers; proof-carrying actions with action identity, approvals, runtime and outcome receipts; append-only human-to-agent delegation provenance; authority narrowing and cascade containment; principal-chain composition with bounded scope; typed verifier certificates; heterogeneous authorization-evidence chains; and generic cross-domain authority relations.

These mechanisms answer local questions such as whether an action is permitted, whether a delegation is valid, whether required evidence certificates are present, and whether receipt chains satisfy an action policy. Their native semantics remain unchanged inside P8.

### Scientific claim, release, and adjudication donors

P8 also reuses domain scientific harnesses that bind evidence to release, claim-to-evidence chains with deterministic grounding and verification, persistent contract-governed research artifacts, evidence-calibrated claim adjudication, and evidence-ledger review that routes unsupported, contradicted, or mixed-evidence claims back for revision.

These mechanisms establish strong local scientific governance. P8's additional object is the interface that determines when one such local judgment can discharge a different scientific obligation.

### The remaining composition problem

The donor mechanisms govern heterogeneous subjects: actions, delegations, receipts, verifier predicates, claim-evidence packets, research artifacts, and domain-specific release decisions. P8 provides the common scientific relation that connects those subjects without silently widening what any local verdict means.

## Scientific-discharge type and lifted terminal

The complete scientific-discharge type is

`tau = (domain, kind, scope, content, epoch)`.

Let `D(a)` denote the native authority, verification, adjudication, or release verdict of donor object `a`. P8 preserves `D(a)`.

The bounded lifted state additionally contains:

- `narrowing_ok`: every relevant authority/delegation/claim-processing hop preserves or narrows `tau`;
- blocker state `b in {REFUTED, UNDETERMINED, ESTABLISHED}`;
- two alternative complete support families `S_A`, `S_B`;
- optional explicit `protected_coercion` binding a source type to the target type and epoch.

A donor-derived judgment reaches `DISCHARGE` when:

1. `D(a)` is valid;
2. the scientific type matches directly or a complete protected coercion is registered;
3. authority is non-widening across the relevant chain;
4. blocker state is `REFUTED`;
5. at least one complete support family survives.

`UNDETERMINED` maps to `CANNOT_CHECK`; `ESTABLISHED` maps to `BLOCK`.

## Theorem V3.1 — donor conservativity

Adding the scientific-discharge layer changes none of the donor-native action, delegation, evidence, adjudication, or release verdicts. Local authority remains available for its native purpose even when it does not yet discharge a broader scientific target.

This is the compatibility foundation: cross-domain scientific governance is additive rather than destructive.

## Theorem V3.2 — typed scientific-discharge separation

For every registered donor family and each non-inert coordinate of `(domain, kind, scope, content, epoch)`, two states can share the same native donor success while differing only in whether that coordinate matches the target scientific obligation. The exhaustive model contains **65 one-coordinate separating witnesses**.

A valid action certificate, verified claim-evidence packet, scientific release decision, or authorization receipt therefore remains reusable without becoming an unrestricted scientific authority token.

## Theorem V3.3 — monotone scientific-authority propagation

Scientific authority composes across heterogeneous chains when each hop preserves or narrows the inherited scientific type. A widening hop requires an explicit protected bridge that establishes the additional authority demanded by the target.

This turns cross-domain scientific governance into a compositional invariant rather than a collection of local exceptions.

## Theorem V3.4 — protected coercion enables cross-domain transport

A complete protected coercion can transform an otherwise incompatible scientific type when it binds the exact source type, target type, subject/content, scope, and epoch required by the target obligation. The model contains **65 protected-coercion restorations** and **65 matched bridge-necessity witnesses** in which the same transfer remains unavailable without the registered bridge.

Cross-domain use is therefore enabled, not prohibited, provided the authority transfer is explicit and typed.

## Theorem V3.5 — three-state blocker law

Under otherwise satisfied conditions:

- `REFUTED` clears the blocker premise and permits discharge;
- `UNDETERMINED` yields `CANNOT_CHECK`;
- `ESTABLISHED` blocks discharge.

The law is instantiated across all thirteen donor families. It preserves the scientific distinction between disproving a blocker and merely lacking evidence about it.

## Theorem V3.6 — exact support-family revocation

When two independent complete support families establish the same target obligation, revoking one family preserves discharge through the other. Revoking every complete support family removes discharge. The finite model contains **26 independent-support survivals** and **13 complete-support revocations**.

The rule is exact in both directions: it preserves valid independent derivations while removing authority when no complete derivation survives.

## Theorem V3.7 — universal pairwise composition in the registered donor envelope

Every ordered pair among the thirteen registered donor families admits a scientifically valid two-hop composition under native-valid local verdicts, compatible or protectedly bridged scientific type, non-widening authority, refuted blockers, and surviving support. This yields **169/169 successful registered donor-pair compositions**.

For every ordered pair, a matched authority-widening variant remains unavailable until the missing scientific authority is explicitly bridged, yielding **169 non-widening necessity witnesses** while both donor-native steps remain valid.

The result shows that heterogeneous authority composition can be systematic without forcing every donor into one receipt format or one centralized implementation.

## Theorem V3.8 — permission, release, and support independence

Action/release permission and scientific proposition support are independent, non-inverse relations. A native denial of one action or release route does not scientifically refute a proposition when an independent complete evidence family establishes it. Conversely, native authorization or release does not automatically discharge a different or broader scientific target.

This is a positive interface theorem: action governance and scientific truth support can coexist without corrupting one another because their relation is explicit and compositional.

## Theorem V3.9 — authorization receipts as reusable scientific infrastructure

Valid composition of authorization receipts, canonical action or subject binding, and successful local policy evaluation remains valuable scientific infrastructure whenever the target obligation requires it. Scientific sufficiency is obtained when those receipts are combined with the target type, blocker, support, and coercion conditions.

P8 therefore preserves the value of receipt chains while controlling exactly how far their authority travels.

## Theorem V3.10 — decentralized portability

A decentralized donor product supplied with the same scientific type, narrowing, blocker, support-family, coercion, and composition rules agrees extensionally with P8 over all **39,936** registered states.

The zero-mismatch result is a portability theorem: scientific-discharge semantics are independent of whether they are implemented in one shared calculus or a correctly integrated decentralized product.

## Final donor envelope and literature fixed point

The final donor envelope contains thirteen families spanning authorization/security and scientific verification/adjudication. Earlier six-donor and ten-donor enumerations remain preserved because later hostile literature searches found stronger scientific-release and heterogeneous-authority donors and forced the architecture to absorb them before the final theorem was stated.

Two post-X4 search rounds produced no further material interface change. This is a dated current-pass fixed point and remains reopenable if a new primary formalism supplies an equivalent or stronger scientific-discharge relation.

## Exact bounded support

Final X4 enumeration:

- exact authority states: **39,936**;
- terminals: **19,968** `NO_DONOR_AUTHORITY`, **15,353** `BLOCK`, **3,328** `CANNOT_CHECK`, **1,287** `DISCHARGE`;
- donor-conservativity violations: **0**;
- one-coordinate scientific-type separations: **65**;
- protected-coercion restorations: **65**;
- bridge-necessity witnesses: **65**;
- blocker-law instances: **13** `REFUTED` discharge cases, **13** `UNDETERMINED` `CANNOT_CHECK` cases, **13** `ESTABLISHED` blocks;
- independent-support revocation survivals: **26**;
- complete-support revocations: **13**;
- heterogeneous ordered-chain composition successes: **169**;
- matched non-widening necessity witnesses: **169**;
- action/release-denied but independently supportable proposition cases: **13**;
- ideal decentralized-product mismatches: **0**;
- canonical row SHA-256: `ed186b824692fd5b3ab31be718c75b84e2126b577ce921ca5cc01b2d08ae19e6`.

A separate checker independently reconstructs the final enumeration.

## Strongest supported claim

> P8 composes thirteen modern authorization, delegation, verifier, receipt, scientific-release, claim-evidence, research-harness, adjudication, and evidence-ledger families into a common scientific-discharge layer. Native donor authority is conserved; every registered donor pair composes under compatible typed authority; cross-domain authority is enabled through protected coercion; unresolved blockers fail closed; independent complete support survives partial revocation; and the semantics are portable to an equally typed decentralized implementation.

This is substantially stronger and more constructive than a simple distinction between generic permission and scientific permission. P8 supplies the typed composition relation that lets strong local authority mechanisms work together without silently widening their scientific meaning.

## Transfer scope

The theorem establishes the registered 13-donor, five-coordinate formal envelope and its complete 39,936-state enumeration. Additional donor families, deployed-agent behavior, and broader authority ontologies are extension targets to be tested separately. The decentralized-product equivalence strengthens the main result by establishing that the semantics are architecture-independent.

## Conclusion

P8 establishes a composition theory for scientific authority. Modern agent systems already provide serious local authority through permission graphs, proof-carrying actions, delegation chains, typed verifier certificates, receipt composition, domain scientific release, claim-evidence verification, research harnesses, and evidence-ledger adjudication. P8 retains those mechanisms and gives them a shared rule for deciding when one local judgment may discharge a different scientific obligation.

The calculus is constructive at every interface. Native donor authority is preserved. Scientific authority composes through type-preserving or type-narrowing chains. Cross-domain transfer is enabled by protected coercion when the full bridge is justified. `UNDETERMINED` blockers remain actionable `CANNOT_CHECK` states. Independent complete support routes survive partial revocation. All **169 ordered donor pairs** compose under the registered compatible conditions, and the equally typed decentralized product matches **all 39,936 states**.

The strongest conclusion is therefore positive and architecture-independent: **cross-domain scientific authority can be composed systematically from heterogeneous local authority mechanisms when scientific discharge is treated as a typed, non-widening, bridgeable, fail-closed, support-aware relation**.

**Current science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`.
