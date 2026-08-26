# A Theory of Epistemic Authority for Autonomous Science — V3 science update

**Paper VIII current science manuscript overlay**  
**Date:** 2026-08-19  
**Historical base:** V2/V2.1 formal core and JAAMAS submission bytes retained  
**Successor evidence:** `research/claim_expansion/p8/P8_X4_*`  
**Science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`

V3 preserves the V2.1 blocker, coercion, revocation and typed-discharge semantics but widens the paper constructively. Modern authorization, delegation, evidence, scientific-release and claim-adjudication systems are treated as donor authority objects to be retained and composed rather than as novelty threats to route around.

## Replacement abstract for V3

Autonomous scientific systems increasingly operate under strong local authority mechanisms. Agent-governance work provides evidence-backed permission graphs, proof-carrying action certificates, cryptographic delegation provenance, deterministic authority narrowing, accumulated principal-chain authorization, typed verifier certificates and heterogeneous authorization-evidence chains. Scientific-agent systems separately provide evidence-bound release gates, claim-to-evidence verification, contract-governed research artifacts, evidence-calibrated claim adjudication and evidence-ledger review. ORION-18 treats all of these mechanisms as donor-owned local authorities rather than claiming generic authorization or scientific verification as new.

The remaining problem is compositional: when may a local authorization, delegation, verifier, claim-evidence or release verdict establish a different target scientific obligation? ORION-18 introduces a bounded **scientific-authority lifting and composition calculus** over thirteen donor families. The target obligation is typed by `(domain, kind, scope, content, epoch)`. Native donor authority is conserved. Scientific authority propagates across heterogeneous chains only when the scientific type is preserved or narrowed, or when an explicit subject/epoch-bound protected coercion supplies a complete bridge. Blockers use three states: `REFUTED`, `UNDETERMINED`, and `ESTABLISHED`, with `UNDETERMINED` yielding `CANNOT_CHECK` rather than silently disappearing. Alternative complete support families make revocation exact: invalidating one route preserves authority when another complete independent route survives, while destroying all complete routes removes discharge. Action or release permission and scientific support are explicitly non-inverse relations.

The final X4 finite model covers 39,936 exact authority states across thirteen donor families. It has zero donor-conservativity violations and zero mismatches with an ideal equally typed decentralized product. It contains 65 minimal scientific-type separation witnesses, 65 protected-coercion successes and 65 matched unprotected countermodels, the three-state blocker law for all thirteen donor families, 26 single-support-family revocation survivals and 13 all-support-family blocks, plus 169 heterogeneous ordered-chain composition successes and 169 matched scientific-authority-widening countermodels. A second implementation independently reproduces the canonical enumeration. The result is a bounded cross-domain scientific-authority composition semantics, not generic authorization, local scientific verification, deployed-agent superiority, or a claim of centralized expressive advantage.

## Donor-engulfment architecture

V3 explicitly imports the strongest useful structure from two neighboring layers.

### Action, delegation, and authorization donors

ORION-18 reuses evidence-backed permission graphs and external deterministic authorizers; runtime-neutral action certificates carrying action identity, approvals, runtime and outcome receipts; append-only human-to-agent delegation provenance; authority-narrowing and cascade-containment rules; principal-chain composition with bounded scope; typed verifier certificates; heterogeneous authorization-evidence chains; and generic cross-domain authority relations.

These mechanisms answer important local questions such as whether an action is permitted, whether a delegation is valid, whether required evidence certificates are present, or whether heterogeneous authorization receipts jointly satisfy an action policy. ORION-18 claims none of those mechanisms as its own.

### Scientific claim, release, and adjudication donors

ORION-18 also reuses domain scientific harnesses that separate semantic from scientific authority and authorize evidence-bound release; claim-to-evidence chains with deterministic grounding and verification; persistent contract-governed research artifacts; evidence-calibrated claim adjudication; and evidence-ledger review that routes unsupported, contradicted, or mixed-evidence claims back for revision.

These donors establish that scientific claim validation/release can itself be externalized and governed. ORION-18 therefore does not claim novelty merely for separating a model's fluent answer from a scientific release decision.

### The remaining composition problem

The donor mechanisms are powerful but heterogeneous. Their local verdicts concern different objects: an action, a delegation, a receipt chain, a verifier predicate, a claim-evidence packet, a research artifact, or a domain-specific release decision. ORION-18's V3 object is the common relation that governs when such a local authority object is entitled to discharge a target scientific obligation of another type or scope.

## Scientific-discharge type and lifted terminal

The complete scientific-discharge type is

`tau = (domain, kind, scope, content, epoch)`.

Let `D(a)` denote the native authority, verification, adjudication, or release verdict of donor object `a`. ORION-18 does not rewrite `D`.

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

## Theorem V3.2 — cross-donor scientific-discharge separation

For every registered donor family and each non-inert coordinate of `(domain, kind, scope, content, epoch)`, native donor success can coexist with scientific-discharge failure when only that coordinate is incompatible with the target obligation.

Thus a valid action certificate, verified claim-evidence packet, scientific release decision, or cross-domain authorization may be retained without being treated as an unrestricted authority token.

## Theorem V3.3 — monotone scientific authority propagation

Scientific authority may be preserved or narrowed through heterogeneous authority chains. A hop that widens the scientific type beyond inherited authority cannot discharge the widened target merely because each local donor step remains native-valid.

This extends donor narrowing/cascade-containment ideas to the scientific-obligation type rather than replacing them.

## Theorem V3.4 — protected coercion

A complete protected coercion may transform an otherwise incompatible scientific type. The same mismatch without the registered bridge remains blocked. Semantic similarity, intent similarity, common action digest, claim fluency, or ordinary action composability is not sufficient to create a coercion.

## Theorem V3.5 — three-state blockers

Under otherwise satisfied conditions:

- `REFUTED` permits the blocker condition to clear and allows discharge;
- `UNDETERMINED` yields `CANNOT_CHECK`;
- `ESTABLISHED` blocks discharge.

The distinction prevents unknown blocker state from being silently treated as blocker absence.

## Theorem V3.6 — exact support-family revocation

When two independent complete support families establish the same target obligation, revoking one family preserves discharge through the other. Revoking all complete support families removes discharge.

This avoids both over-revocation, in which one failed premise destroys an independently supported result, and under-revocation, in which a broken unique support path is ignored.

## Theorem V3.7 — heterogeneous authority-chain composition

Every ordered pair among the thirteen registered donor families admits a scientifically valid two-hop composition under native-valid local verdicts, compatible or protectedly bridged scientific type, non-widening authority, refuted blockers, and surviving support. The matched chain with a scientific-authority-widening hop is blocked even though both donor-native steps remain valid.

The theorem treats heterogeneous authority composition as a first-class object rather than requiring every donor to adopt one common receipt format.

## Theorem V3.8 — permission, release, and support are not inverse relations

A native denial of one action or release route is not scientific refutation when an independent complete evidence family establishes the proposition. Conversely, native authorization or release does not authorize a different or broader scientific target. The two relations are connected by explicit evidence/type bridges rather than logical inversion.

## Theorem V3.9 — heterogeneous receipt composition is a prerequisite, not scientific sufficiency

Valid composition of authorization receipts, canonical action or subject binding, and successful local policy evaluation may be necessary inputs to a scientific claim, but they do not by themselves establish target scientific sufficiency. Scientific discharge remains governed by the target type, blocker, support, and coercion relation.

## Theorem V3.10 — ideal decentralized-product equivalence

A decentralized donor product supplied with the exact same scientific type, narrowing, blocker, support-family, coercion, and composition rules agrees extensionally with ORION-18. The contribution is therefore the explicit common scientific-discharge calculus, not centralized expressive power.

## Final donor envelope and literature fixed point

The final donor envelope contains thirteen families across authorization/security and scientific verification/adjudication. The research chronology is retained deliberately: early six-donor and ten-donor intermediate enumerations are preserved, because later hostile searches discovered stronger scientific-release and heterogeneous-authority donors and forced the architecture to expand rather than shrink.

Two post-X4 search rounds produced no further material change to the interface. This is a bounded current-pass fixed point, not a claim of global or exhaustive literature saturation. A newly discovered primary formalism with an equivalent target scientific-discharge relation is a reopen trigger.

## Exact bounded support

Final X4 enumeration:

- exact authority states: **39,936**;
- terminals: **19,968** `NO_DONOR_AUTHORITY`, **15,353** `BLOCK`, **3,328** `CANNOT_CHECK`, **1,287** `DISCHARGE`;
- donor-conservativity violations: **0**;
- minimal scientific-type separation witnesses: **65**;
- protected-coercion successes: **65**;
- matched unprotected-coercion countermodels: **65**;
- blocker-law instances: **13** `REFUTED` successes, **13** `UNDETERMINED` `CANNOT_CHECK`, **13** `ESTABLISHED` blocks;
- one-support-family revocation survivals: **26**;
- all-support-family revocation blocks: **13**;
- heterogeneous ordered-chain composition successes: **169**;
- matched scientific-authority-widening chain countermodels: **169**;
- action/release-denied but independently supportable proposition examples: **13**;
- ideal decentralized-product mismatches: **0**;
- canonical row SHA-256: `ed186b824692fd5b3ab31be718c75b84e2126b577ce921ca5cc01b2d08ae19e6`.

A separate checker independently reconstructs the final enumeration.

## Wider ORION-18 claim

> ORION-18 composes modern action authorization, delegation provenance, heterogeneous authorization receipts, cross-domain authority relations, typed verifier certificates, scientific release gates, claim-evidence chains, research harnesses, claim adjudication and evidence-ledger review into a common scientific-discharge calculus. Local donor authority remains intact, while authority to establish a scientific conclusion propagates only through typed non-widening chains or protected coercions, fail-closed blocker semantics and surviving complete support families.

This is deliberately wider than the V2.1 slogan that generic permission differs from scientific permission. The local authority mechanisms are absorbed; the paper's contribution is the cross-domain composition/lifting relation among them.

## Limits

V3 does not claim novelty for any of the thirteen donor mechanisms, universal minimality of the five type coordinates, deployed-agent superiority, a public full-manuscript release gate, or global literature saturation. Native authorization failure is not scientific refutation. The ideal equally typed decentralized product ties exactly.

## Replacement conclusion for V3

ORION-18's strongest form is a composition theory rather than another authorization gate. Modern agent systems already provide serious local authority: permission graphs, proof-carrying actions, delegation chains, typed verifier certificates, receipt composition, domain scientific release, claim-evidence verification, research harnesses, and evidence-ledger adjudication. ORION should use those mechanisms rather than rebuild weaker versions of them.

The missing interface is the authority relation between these local judgments and a target scientific obligation that may differ in domain, kind, scope, content, or epoch. ORION-18 makes that relation explicit. Scientific authority is non-widening by default, transformable only by protected coercion, fail-closed under unresolved blockers, exactly revocable across alternative complete support families, and compositionally reusable across heterogeneous donor systems. An equally typed decentralized implementation has the same expressive power, which keeps the contribution architectural and semantic rather than brand-dependent.

**Current science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`.
