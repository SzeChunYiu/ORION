# JAAMAS information sheet — regular paper

**Manuscript:** *Epistemic Authority for Autonomous Science: Typed Discharge across Heterogeneous Scientific Effects*  
**Author:** Sze Chun Yiu  
**Article type:** Regular Paper

## 1. What is the main claim, and why is it important to autonomous-agent / MAS research?

The main claim is that a valid authorization- or evidence-bearing judgment in one component of an autonomous agent does **not** automatically satisfy the different scientific obligation required by another component. Safe composition therefore requires authority-relevant judgments to retain a complete target-discharge type—domain, evidential kind, scope, content identity, and epoch—and permits cross-domain use only through protected coercions whose full types compose.

This matters because modern agents increasingly combine planning/reframing, search and stopping, semantic integration, assertion, and self-modification within one workflow. Existing authorization, usage-control, effect, provenance, and abstention systems already provide strong runtime controls. The remaining integration failure is semantic: each component can produce a locally valid judgment while a downstream component treats that judgment as authority for a scientific claim it was never designed to establish. Examples include route saturation treated as task completion, citation support treated as independent verification, similarity treated as construct-merge authority, and replay improvement treated as self-promotion authority.

The paper also makes an intentionally negative architectural claim: one centralized authority calculus has no inherent expressive advantage over an ideal product of correctly typed domain gates that shares the same coercion, freshness, blocker, and revocation semantics. This prevents a superficial “single framework is stronger” argument and turns the research question into a precise interface problem.

## 2. What evidence supports the claim? Be precise about main results and implications.

The evidence is formal and deterministic rather than an empirical leaderboard.

1. **Typed anti-laundering theorem.** If ordinary inference preserves complete judgment type and only protected coercions can change it, a source judgment cannot discharge a differently typed target obligation without a composable coercion path. A counterexample shows that domain-only path reachability is insufficient when intermediate scope/content types fail to match.

2. **Generic permission / scientific-discharge separation.** A valid generic permission can coexist with `CANNOT_CHECK` for the scientific action because an independent scientific obligation remains unresolved. Thus access/policy authorization and scientific authority can both be correct while returning different judgments.

3. **Alternative-derivation revocation theorem.** Certificates are supported by families of complete sufficient premise sets. Revoking one premise invalidates a certificate exactly when every complete derivation is broken, preserving independent support rather than applying a naive descendant reset.

4. **Non-compensatory authorization semantics.** All hard scientific obligations must be discharged; soft confidence/utility cannot compensate for a mandatory blocker. `AUTHORIZED`, `DENIED`, and `CANNOT_CHECK` remain distinct repair states.

5. **Shared/product equivalence theorem.** A shared calculus and an ideal correctly typed product return the same terminal when they implement identical semantics. Therefore any claimed engineering advantage must be measured as consistency, audit/proof economy, revocation coverage, or implementation quality rather than centralization itself.

6. **Deterministic executable support.** The frozen checker covers all 25 source/target-domain direct-discharge combinations, typed coercion composition, stale epochs, blockers, alternative derivations, protected self-promotion boundaries, three authority terminals, and 160 shared/product equivalence cases. A separate 17-case manifest contains clean authorized controls in all five domains, paired blockers, five laundering attacks, `CANNOT_CHECK`, and a valid cross-domain coercion.

The implication is a concrete design rule for composed agents: authority APIs should expose what scientific obligation has actually been discharged, not merely return a generic success token.

## 3. What papers by other authors are closest, and how is this paper related?

The paper is deliberately positioned **after** the strongest authorization/governance donors rather than against weak confidence baselines.

- Park and Sandhu's UCON work establishes ongoing authorization, obligations/conditions, and mutable attributes. ORION-18 adopts ongoing/commit-time authority as donor structure; its additional question is whether the source authorization/evidence has the correct scientific discharge type for a heterogeneous target effect.
- Becker, Fournet, and Gordon's SecPAL formalizes decentralized authorization and policy proof. ORION-18 does not claim authorization logic, delegation, or policy proofs; it adds the scientific obligation type carried through heterogeneous agent modules.
- ETAS (Tan et al., arXiv:2607.17780) and FAVA (Zhang et al., arXiv:2607.27267) provide typed effects, residual obligations, evidence-backed permission graphs, and pre-effect authorization. These mechanisms are direct donors.
- AgentBound (Kaul, Lan, Gupta, arXiv:2606.30970) and Authorization Propagation in Multi-Agent AI Systems (Tallam, arXiv:2605.05440) address multiple authorities, delegation, temporal validity, and workflow-level propagation. ORION-18 does not claim multi-authority composition.
- **Context Is Not Authority** (Tang et al., arXiv:2608.09025) is especially close: it binds governance to typed exact effects, records missing/stale obligations, uses exact-artifact receipts, and rechecks authority after state changes. ORION-18 therefore explicitly does not claim the broad principle that evidence/context is not authority, exact-artifact binding, or pre-commit reauthorization. Its narrower object is *cross-epistemic-domain target scientific-obligation discharge* and the associated type/coercion/revocation theorems.
- AgentAbstain and SteerBench-Work motivate bidirectional evaluation: excessive refusal is a governance failure as well as unsafe allow. The ORION-18 evaluation contract therefore includes clean authorized coverage and unnecessary refusal.

The nearest-work relationship is consequently conservative: the manuscript treats these systems as mechanisms that can instantiate portions of the calculus. A donor product with the same scientific discharge semantics should tie the shared implementation.

## 4. Have parts of the paper been published before? What is the added value?

No prior archival conference or journal publication of this ORION-18 manuscript is asserted in the ORION research record. The theory has been developed in a public software/research repository as a candidate manuscript and formal-checking package. That repository history is not presented as a peer-reviewed archival publication.

The journal submission is the first intended archival presentation of the scoped ORION-18 theory: full evidence-to-obligation typing, typed coercion composition, alternative-derivation revocation, generic-permission/scientific-discharge separation, the shared/product equivalence negative theorem, and the executable five-domain authority contract. If the author identifies any prior archival publication containing material from this manuscript before submission, it must be disclosed in the submission system and this sheet must be updated before upload.
