# Cross-Domain Scientific Authority as Typed Composition

**Paper VIII current science manuscript — V3 refinement**  
**Date:** 2026-08-20  
**Historical base:** V2/V2.1 formal core and JAAMAS submission bytes retained  
**Successor evidence:** `research/claim_expansion/p8/P8_X4_*`  
**Science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`

V3 preserves the V2.1 blocker, coercion, revocation, and typed-discharge semantics while making the strongest constructive interpretation explicit. Modern authorization, delegation, evidence, scientific-release, and claim-adjudication systems are retained as donor authority objects and composed through a common scientific-discharge interface.

## Abstract

Autonomous scientific systems increasingly operate under strong but heterogeneous local authority mechanisms: evidence-backed permission graphs, proof-carrying action certificates, delegation provenance, authority narrowing, principal-chain authorization, typed verifier certificates, authorization-evidence chains, scientific release gates, claim-to-evidence verification, contract-governed research artifacts, evidence-calibrated adjudication, and evidence-ledger review. Each mechanism can be valid for its native object while the target scientific obligation belongs to a different domain, kind, scope, content identity, or epoch. P8 addresses that cross-domain composition problem with a typed scientific-authority calculus over thirteen donor families.

Native donor verdicts are conserved. Scientific authority propagates across heterogeneous chains only when the target type `(domain, kind, scope, content, epoch)` is preserved or narrowed, or when a protected subject/epoch-bound coercion supplies the complete bridge. Blockers retain three distinct epistemic states—`REFUTED`, `UNDETERMINED`, and `ESTABLISHED`—so unresolved blockers yield `CANNOT_CHECK` rather than being silently treated as absent. Alternative complete support families make revocation exact: one route can fail while an independent complete route preserves discharge, whereas loss of every complete route removes authority. Action/release permission and scientific proposition support remain independent relations linked only by explicit evidence and type bridges.

The final X4 model exhausts **39,936 exact authority states** across the thirteen donor families with **zero donor-conservativity violations and zero mismatches with an equally typed decentralized product**. It contains 65 one-coordinate scientific-type separations, 65 protected-coercion restorations paired with 65 bridge-necessity witnesses, the three-state blocker law across all thirteen donors, 26 independent-support revocation survivals and 13 complete-support revocations, plus **169 heterogeneous ordered-chain composition successes** paired with 169 authority-widening block witnesses. A second implementation independently reproduces the canonical enumeration and digest.

The resulting claim is constructive and architecture-independent: heterogeneous authorization and scientific-verification systems can be composed into a common scientific-discharge layer without weakening their native semantics, provided scientific authority is explicitly typed, non-widening by default, bridgeable only through protected coercion, fail-closed under unresolved blockers, and revocable over complete support families. The exact tie with the equally typed decentralized product establishes portability of these semantics rather than a centralized expressivity claim.

## Donor-engulfment architecture

V3 explicitly imports the strongest useful structure from two neighboring layers.

### Action, delegation, and authorization donors

P8 reuses evidence-backed permission graphs and external deterministic authorizers; runtime-neutral action certificates carrying action identity, approvals, runtime and outcome receipts; append-only human-to-agent delegation provenance; authority-narrowing and cascade-containment rules; principal-chain composition with bounded scope; typed verifier certificates; heterogeneous authorization-evidence chains; and generic cross-domain authority relations.

These mechanisms answer important local questions such as whether an action is permitted, whether a delegation is valid, whether required evidence certificates are present, or whether heterogeneous authorization receipts jointly satisfy an action policy. P8 claims none of those mechanisms as its own.

### Scientific claim, release, and adjudication donors

P8 also reuses domain scientific harnesses that separate semantic from scientific authority and authorize evidence-bound release; claim-to-evidence chains with deterministic grounding and verification; persistent contract-governed research artifacts; evidence-calibrated claim adjudication; and evidence-ledger review that routes unsupported, contradicted, or mixed-evidence claims back for revision.

These donors establish that scientific claim validation/release can itself be externalized and governed. P8 therefore does not claim novelty merely for separating a model's fluent answer from a scientific release decision.

### The remaining composition problem

The donor mechanisms are powerful but heterogeneous. Their local verdicts concern different objects: an action, a delegation, a receipt chain, a verifier predicate, a claim-evidence packet, a research artifact, or a domain-specific release decision. P8's V3 object is the common relation that governs when such a local authority object is entitled to discharge a target scientific obligation of another type or scope.

## Scientific-discharge type and lifted terminal

The complete scientific-discharge type is

`tau = (domain, kind, scope, content, epoch)`.

Let `D(a)` denote the native authority, verification, adjudication, or release verdict of donor object `a`. P8 does not rewrite `D`.

The bounded lifted state additionally contains:

- `narrowing_ok`: every relevant authority/delegation/claim-processing hop preserves or narrows `tau`;
- blocker state `b in {REFUTED, UNDETERMINED, ESTABLISHED}`;
- two alternative complete support families `S_A`, `S_B`;
- optional explicit `protected_coercion` binding a source type to the target type and epoch.

A donor-derived judgment reaches `DISCHARGE` only when:

1. `D(a)` is valid;
2. the scientific type matches directly or a complete protected coercion is registered;
3. authority is non-widening across the relevant chain;
4. blocker state is `REFUTED`;
5. at least one complete support family survives.

`UNDETERMINED` maps to `CANNOT_CHECK`; `ESTABLISHED` maps to `BLOCK`.

## Theorem V3.1 — donor conservativity

Adding the scientific-discharge layer does not change any donor-native action, delegation, evidence, adjudication, or release verdict. Local authorities remain usable for their native purpose even when they do not discharge a broader scientific target.

This is the compatibility foundation of the calculus: cross-domain scientific governance is added without invalidating correct local authorization or verification semantics.

## Theorem V3.2 — typed scientific-discharge separation

For every registered donor family and each non-inert coordinate of `(domain, kind, scope, content, epoch)`, two states can share the same native donor success while differing only in whether that coordinate matches the target scientific obligation. The exhaustive model contains 65 one-coordinate separating witnesses.

This identifies the scientific target type as independent authority information. A valid action certificate, verified claim-evidence packet, scientific release decision, or cross-domain authorization remains valid for its native purpose without becoming an unrestricted scientific authority token.

## Theorem V3.3 — monotone scientific-authority propagation

Scientific authority is compositional when each heterogeneous hop preserves or narrows the inherited scientific type. A widening hop does not discharge the widened target unless an explicit protected bridge supplies the missing authority, even when every local donor verdict remains valid.

This extends donor narrowing and cascade-containment ideas to the full scientific-obligation type while preserving donor-local semantics.

## Theorem V3.4 — protected coercion restores typed transport

A complete protected coercion transforms an otherwise incompatible scientific type when it binds the exact source type, target type, subject/content, scope, and epoch required by the target obligation. The final model contains 65 such coercion restorations and 65 matched bridge-necessity witnesses in which the same mismatch remains blocked without the registered coercion.

This gives P8 a constructive bridge rule: cross-domain use is not prohibited, but it must be justified by explicit typed authority rather than semantic similarity, intent similarity, common action digest, claim fluency, or ordinary action composability.

## Theorem V3.5 — three-state blocker law

Under otherwise satisfied conditions:

- `REFUTED` clears the blocker premise and permits discharge;
- `UNDETERMINED` yields `CANNOT_CHECK`;
- `ESTABLISHED` blocks discharge.

The law is instantiated across all thirteen donor families. It preserves the scientific difference between disproving a blocker and merely failing to observe one.

## Theorem V3.6 — exact support-family revocation

When two independent complete support families establish the same target obligation, revoking one family preserves discharge through the other. Revoking every complete support family removes discharge. The finite model contains 26 independent-support survivals and 13 complete-support revocations.

The result is exact in both directions: it avoids over-revocation when an independent proof remains and under-revocation when no complete proof survives.

## Theorem V3.7 — universal pairwise composition in the registered donor envelope

Every ordered pair among the thirteen registered donor families admits a scientifically valid two-hop composition under native-valid local verdicts, compatible or protectedly bridged scientific type, non-widening authority, refuted blockers, and surviving support. This yields **169/169 successful registered donor-pair compositions**. For each ordered pair, the matched scientific-authority-widening chain is blocked while both donor-native steps remain valid, providing 169 tight witnesses for the non-widening condition.

The theorem treats heterogeneous authority composition as a first-class object without requiring every donor to adopt one common receipt format.

## Theorem V3.8 — permission, release, and support independence

Action/release permission and scientific proposition support are non-inverse relations. A native denial of one action or release route does not scientifically refute a proposition when an independent complete evidence family establishes it. Conversely, native authorization or release does not discharge a different or broader scientific target.

This turns a potential “negative” observation into a positive interface theorem: action governance and scientific truth support can coexist without corrupting one another because their relation is explicit rather than assumed.

## Theorem V3.9 — receipt composition as a reusable prerequisite

Valid composition of authorization receipts, canonical action or subject binding, and successful local policy evaluation is reusable scientific infrastructure when the target obligation requires it. It becomes scientifically sufficient only when the target type, blocker, support, and coercion conditions are also satisfied. The calculus therefore preserves the value of receipt chains while preventing authority from widening silently beyond what those receipts establish.

## Theorem V3.10 — decentralized-product equivalence and portability

A decentralized donor product supplied with the exact same scientific type, narrowing, blocker, support-family, coercion, and composition rules agrees extensionally with P8 over all 39,936 registered states. The zero-mismatch result is a portability theorem: the scientific-discharge semantics are independent of whether they are implemented in one shared calculus or a correctly integrated decentralized product.

## Final donor envelope and literature fixed point

The final donor envelope contains thirteen families across authorization/security and scientific verification/adjudication. The research chronology is retained deliberately: early six-donor and ten-donor intermediate enumerations are preserved, because later hostile searches discovered stronger scientific-release and heterogeneous-authority donors and forced the architecture to expand rather than shrink.

Two post-X4 search rounds produced no further material change to the interface. This is a bounded current-pass fixed point, not a claim of global or exhaustive literature saturation. A newly discovered primary formalism with an equivalent target scientific-discharge relation is a reopen trigger.

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

> P8 composes thirteen modern authorization, delegation, verifier, receipt, scientific-release, claim-evidence, research-harness, adjudication, and evidence-ledger families into a common scientific-discharge layer. Native donor authority is conserved, every registered donor pair composes under compatible typed authority, cross-domain authority can be restored through protected coercion, unresolved blockers fail closed, independent complete support survives partial revocation, and an equally typed decentralized implementation is extensionally equivalent.

This is substantially stronger and more constructive than the earlier statement that generic permission differs from scientific permission. The paper's contribution is the typed composition/lifting relation that lets strong local authority mechanisms work together without silently widening their scientific meaning.

## Scope of the theorem

The thirteen donor families and five type coordinates define a bounded formal envelope rather than a universal minimal authority ontology. The 39,936-state enumeration proves the registered composition laws, not deployed-agent or population-level safety. The current literature fixed point is dated and reopenable. The exact decentralized-product tie is already part of the theorem: centralization is unnecessary because the semantics themselves are the contribution.

## Conclusion

P8's strongest form is a composition theory for scientific authority. Modern agent systems already provide serious local authority through permission graphs, proof-carrying actions, delegation chains, typed verifier certificates, receipt composition, domain scientific release, claim-evidence verification, research harnesses, and evidence-ledger adjudication. P8 retains those mechanisms and gives them a shared relation for deciding when one local judgment may discharge a different scientific obligation.

The resulting calculus is constructive at every interface. Native donor authority is preserved. Scientific authority composes through type-preserving or type-narrowing chains. Cross-domain transfer is enabled by explicit protected coercion when the full bridge is justified. `UNDETERMINED` blockers remain actionable `CANNOT_CHECK` states rather than disappearing. Independent complete support routes survive partial revocation. All 169 ordered donor pairs compose under the registered compatible conditions, and the equally typed decentralized product matches every one of the 39,936 states.

The strongest supported conclusion is therefore positive and architecture-independent: **cross-domain scientific authority can be composed systematically from heterogeneous local authority mechanisms when scientific discharge is treated as a typed, non-widening, bridgeable, fail-closed, support-aware relation**. The ideal-product equivalence strengthens this claim by showing that the semantics are portable rather than tied to ORION centralization.

**Current science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`.
