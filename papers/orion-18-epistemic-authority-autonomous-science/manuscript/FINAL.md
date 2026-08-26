# A Theory of Epistemic Authority for Autonomous Science

**Paper VIII candidate — theory-complete manuscript**  
**Version:** 2026-08-18 / V2 closure  
**Scientific scope:** formal cross-domain scientific-authority theory with deterministic finite support  
**Programme rule:** absorb strong authorization, effect, provenance and abstention donors before narrowing  
**No first-of-kind claim is made.**

## Abstract

Autonomous scientific systems increasingly combine capabilities that are individually useful but governed by different evidential standards: reframing a problem, stopping a search, merging constructs, asserting a scientific result, or promoting a self-modification. Existing work already provides rich theories and systems for authorization, delegation, revocation, usage control, typed effects, policy enforcement, multi-authority governance, abstention, provenance, and protected execution. The unresolved scientific question is not whether agents need permissions. It is how a valid judgment in one epistemic domain may—or may not—discharge the **different scientific obligation** required by another.

We develop a typed scientific-authority calculus in which every authority-relevant judgment carries domain, kind, scope, content identity and epoch. Hard obligations name the exact judgment type capable of discharging them. Cross-domain authority transport is possible only through protected coercions whose entire input/output types compose, not merely their domain labels. Authorization is non-compensatory: soft utility cannot outweigh an unresolved hard obligation. Revocation is represented over support families rather than a naive descendant graph so that independent complete derivations survive partial revocation. `AUTHORIZED`, `DENIED`, and `CANNOT_CHECK` are distinct terminals, and authorization must remain valid immediately before commit.

We prove a typed anti-laundering theorem, exact alternative-derivation revocation, and a separation between generic action permission and scientific-obligation discharge. We also prove a negative result important to the ORION programme: a shared authority calculus is extensionally equivalent to a product of correctly typed per-domain gates when both receive the same coercion, freshness and revocation semantics. Centralization is therefore not a scientific contribution by itself. Any superiority claim must instead concern missing cross-domain discharge rules, consistency, auditability, proof economy or implementation defects.

A deterministic standard-library checker exercises the complete 5×5 source/target-domain matrix, typed coercion composition, alternative-derivation revocation, terminal distinctions, non-compensatory blockers, positive coercion controls, stale epochs, protected self-promotion, and 160 shared/product equivalence cases. The theory is complete; separate-paper novelty and empirical superiority remain independent gates.

## 1. Introduction

Agent capability is expanding faster than the semantics governing when a capability should be allowed to change scientific state. The same system may be able to:

- reframe a question;
- stop a search route;
- merge two constructs;
- assert a scientific conclusion;
- change its own method.

These actions can all be computationally successful while requiring different scientific premises. Planner confidence does not by itself authorize a reframe. Route exhaustion does not prove task completion. Semantic similarity does not settle whether two measurements identify the same construct. Citation support does not establish independent verification. A successful self-change replay does not authorize self-promotion.

The recurring error is **authority laundering**: a valid judgment from one layer is converted into permission in another layer without a rule establishing that the target scientific obligation was actually discharged.

This paper takes a deliberately expansionary approach to prior work. Authorization logics, usage control, ETAS, FAVA, multi-authority governance, provenance systems, abstention benchmarks and ORION Papers I–V are absorbed as donors. The candidate contribution lives only in the interfaces that remain after their strongest structures are included.

### 1.1 Contributions

**C1 — full-derivation epistemic typing.** Every authority-relevant judgment and obligation carries domain, kind, scope, content identity and epoch. Typing is enforced at the evidence-to-obligation layer rather than only on the final authorization token.

**C2 — exact cross-domain coercion composition.** Cross-domain transport requires a protected typed coercion path whose complete output type matches the next input type. Domain-only reachability is insufficient.

**C3 — non-compensatory scientific authorization.** A valid grant and high utility cannot compensate for an unresolved hard scientific obligation. `AUTHORIZED`, `DENIED`, and `CANNOT_CHECK` remain separate.

**C4 — alternative-derivation revocation.** Authorization certificates are supported by families of complete premise sets. Revoking one premise invalidates only certificates for which every complete derivation is broken.

**C5 — generic permission/scientific discharge separation.** We prove that a generic action permission can be valid while a required scientific obligation remains unresolved.

**C6 — product-decomposition theorem.** A shared calculus and a perfectly typed product of per-domain gates are extensionally equivalent when they use the same global rules. This prevents the paper from claiming centralization as inherent expressive superiority.

**C7 — donor-complete challenge programme.** We specify comparisons against the strongest donor-product super-baseline, not weak scalar confidence thresholds.

## 2. Engulfing the parent theories

### 2.1 Authorization and trust management

Authorization logics and trust-management systems already formalize policy compliance, delegation, credentials, scope and revocation. ORION-18 imports these structures directly. A grant is not a novel object in this paper.

The scientific addition is that some actions carry obligations not reducible to a generic permission predicate. For example, a system may have permission to write a report while still lacking independent evidence needed to label a claim verified.

### 2.2 Usage control and ongoing authorization

UCON-style usage control treats authorization as ongoing rather than a one-time access decision, incorporates obligations and conditions, and allows attributes to change during use. Modern agent governance similarly emphasizes stale authorization and commit-time validity. ORION-18 therefore cannot claim “continuous authorization” as new.

Commit-time freshness is instead a premise of the scientific-authority calculus: a valid scientific authorization must still bind the exact effect, content, scope and epoch immediately before commit.

### 2.3 Effect systems and FAVA/ETAS

ETAS tracks typed requested actions, policy-visible traces and residual obligations. FAVA builds evidence-backed permission graphs and checks authorization before effectful execution. These are direct donors for the requested/committed effect distinction and evidence-backed policy evaluation.

ORION-18 asks what happens when the target effect belongs to a different **scientific obligation domain** from the source evidence or authorization judgment.

### 2.4 Multi-authority propagation

Systems that combine multiple authority sources, propagate authorization across agents/components, or explicitly model revocation and temporal validity are strong donors for ORION-18's cross-module setting. A cross-component path is not itself the contribution.

The ORION-18 condition is stricter: the path must establish the full target judgment type, including the scientific-obligation kind and content/scope contract.

### 2.5 Abstention

Agent-abstention work distinguishes whether agents know when not to act and exposes post-hoc abstention. ORION-18 imports this competence but does not collapse every non-action into “abstain.” `DENIED`, `CANNOT_CHECK`, resource `DEFER`, `ROUTE_STOP` and `TASK_STOP` have different repair semantics.

### 2.6 Provenance

Source-aware factuality and execution-provenance work show that content and process lineage are independent verification dimensions. ORION-18 treats provenance as typed derivation material. It does not claim provenance itself.

## 3. Formal authority context

Let effect domains include

\[
D_0=\{REFRAME,SEARCH\_STOP,MAP\_MERGE,ASSERT,SELF\_MODIFY\}.
\]

An effect request is

\[
e=(id,d,op,scope,payload,epoch).
\]

Every authority-relevant judgment has a complete type

\[
\tau=(domain,kind,scope,content,epoch).
\]

A hard obligation `o` names an exact expected judgment type `\tau_o` plus additional mandatory premises.

The authority context contains active judgments, hard/soft obligations, grants, coercions, revocation state, derivation lineage and history.

## 4. Full evidence-to-obligation typing

A weak type discipline can type only the final authorization token while allowing foreign-domain evidence to produce a generic intermediate `SAT`. The laundering has already happened before the final check.

ORION-18 therefore types the entire derivation.

### Direct discharge

Judgment `j:\tau_j` directly discharges obligation `o:\tau_o` only when the complete types match and every additional mandatory premise holds.

If the evidence required to decide the obligation is unavailable, the result is `CANNOT_CHECK`. If available evidence establishes an incompatible type, stale epoch, invalid scope or blocker, the attempted discharge is `DENIED`.

## 5. Typed coercions

Cross-domain use is not forbidden. It must be justified.

A coercion is a protected rule

\[
c:\tau\rightharpoonup\tau'
\]

with a trusted registration root, semantic premises, lineage and validity interval.

Two coercions compose only when the **entire output type** of the first matches the entire input type of the next.

This blocks a subtle laundering path. Suppose a rule maps a `REFRAME` judgment into a `SEARCH_STOP` judgment scoped to `map-A`, while a second rule accepts a `SEARCH_STOP` judgment scoped to `map-B` and maps it into `ASSERT`. A domain graph sees `REFRAME→SEARCH_STOP→ASSERT`; the typed calculus rejects the path because the middle scopes do not compose.

### Theorem 1 — anti-laundering

If ordinary inference preserves judgment type and only registered coercions may change it, any derivation using a source judgment of type `\tau` to discharge target obligation `\tau'\neq\tau` must contain a valid composable coercion path from `\tau` to `\tau'`.

The proof is induction on derivation height: the first type change must be a coercion, and each later type change must be another.

## 6. Non-compensatory obligations

Authorization requires all hard obligations discharged, no active blocker, a valid grant, fresh bindings, and content/scope/epoch identity matching the effect being committed.

Soft preferences and confidence may rank already admissible actions but cannot replace a missing hard premise.

### Proposition 2 — finite penalty is not an unbounded veto

In an extensible additive scoring policy with a finite blocker penalty, sufficiently large positive evidence can overcome the penalty. An absolute blocker therefore requires a separate veto/conjunctive/lexicographic layer unless the positive evidence space is externally bounded.

The proposition is intentionally scoped; it does not claim that every finite-dimensional scalar policy cannot emulate a veto.

## 7. Three authority terminals

`AUTHORIZED` means every hard premise is established and current.

`DENIED` means an available fact establishes a blocker or violated mandatory condition.

`CANNOT_CHECK` means at least one mandatory premise cannot currently be established or refuted.

This distinction matters operationally. `CANNOT_CHECK` may license evidence acquisition or restoring a verifier; `DENIED` licenses neither merely by collecting more unrelated confidence.

## 8. Revocation with alternative derivations

A plain dependency graph often conflates two structures:

- `A AND B` are both required;
- `A OR B` provides two independent complete derivations.

ORION-18 represents an authorization certificate `κ` by a support family

\[
\mathcal S(\kappa)=\{S_1,\ldots,S_m\}
\]

where each `S_i` is a complete sufficient premise set.

### Theorem 3 — exact revocation

After revoking premise set `R`, `κ` remains valid iff at least one complete support set remains entirely valid and unrevoked.

Thus revoking one evidence line does not destroy a certificate supported by another independent complete derivation. Conversely, if every derivation is broken, the certificate must be invalidated.

## 9. Commit-time authority

Authorization is bound to the exact proposed effect and the state in which it will commit.

A later refusal cannot retroactively make an irreversible earlier action safe. A certificate from an old epoch cannot be replayed after a relevant policy/evidence change unless a freshness proof revalidates it.

These are imported constraints from usage-control and modern agent-governance work, not ORION-18 novelty.

## 10. Generic permission is weaker than scientific authority

### Theorem 4 — generic grant/scientific-discharge separation

There exists a context where a generic permission grant validly authorizes an operation at the security/policy level while the ORION-18 scientific effect remains `CANNOT_CHECK` because a mandatory scientific obligation is unresolved.

Construction: give the action a valid in-scope generic grant and no blockers; require one scientific obligation—for example independent verification of an assertion—for which the evidence is missing. Generic permission is true, scientific authorization is not.

This is not a criticism of access control. The two policies answer different questions. ORION-18's purpose is to make the interface explicit so success in one cannot silently masquerade as success in the other.

## 11. ORION ORION-11–ORION-15 as embedded authority domains

### REFRAME — ORION-11

The capability to construct a reframe is separate from responsibility/evidence authority to mutate the relevant formulation coordinate. Dependent closures reopen.

### SEARCH_STOP — ORION-12

Route stop and task stop are different scientific judgments. Censored/open obligations block global completion.

### MAP_MERGE — ORION-13

Similarity is not sufficient merge authority. Referent, construct, context, measurement and obstruction obligations remain explicit.

### ASSERT — ORION-14

Content-bound support and protected independent checks govern scientific-authority promotion.

### SELF_MODIFY — ORION-15

Replay success is candidate evidence; protected evaluation, fresh transfer, negative history and external attestation govern promotion.

ORION-18 may generalize the interface but must reproduce these native decisions on their frozen cases.

## 12. Product-decomposition theorem

It is tempting to argue that one shared authority calculus is inherently stronger than five separate gates. That claim is false if the separate gates are integrated correctly.

Define an ideal typed product with one gate per domain, but a shared coercion registry, freshness semantics and derivation/revocation store.

### Theorem 5 — shared/product equivalence

For every request and authority context, the shared implementation and the ideal typed product return the same terminal.

The proof is extensional: they evaluate the same typed discharge relation, blockers, grants, freshness predicates and support families. Code organization changes; inference semantics do not.

### Consequence

ORION-18 cannot claim centralization as superior expressivity. The strongest baseline is the ideal donor product.

A real advantage can only come from something the product lacks or implements inconsistently: an absent cross-domain coercion, mismatched obligation schemas, duplicated policy logic, incomplete global revocation lineage, inconsistent freshness, larger audit/proof burden, or implementation defects.

## 13. Engulf-before-narrowing experiment design

The programme therefore attempts to engulf all donor structures before deciding the final publication boundary.

The comparison ladder is:

1. each donor-native mechanism;
2. ORION-18's conservative embedding of that mechanism;
3. the full ORION shared calculus;
4. the ideal typed donor product;
5. deliberately naive products exposing common integration mistakes.

Primary measures for protected evaluation include:

- unauthorized scientific commits;
- unnecessary refusal;
- `CANNOT_CHECK` calibration;
- clean authorized coverage;
- revocation correctness under alternative derivations;
- stale authorization reuse;
- cross-domain coercion accuracy;
- interface inconsistency count;
- derivation/proof size and audit cost.

No gain on a soft measure can compensate for violating a protected hard-authority condition.

## 14. Deterministic theory support

The V2 checker, using only the Python standard library, verifies:

- all 25 source-domain/target-domain direct-discharge pairs;
- a scope-incompatible coercion path rejected despite domain-level reachability;
- trusted positive and untrusted negative coercion controls;
- alternative-derivation revocation;
- `AUTHORIZED`, `DENIED`, and `CANNOT_CHECK` terminals;
- finite additive-blocker counterexamples;
- 160 shared-calculus/ideal-product equivalence cases;
- stale-epoch/post-hoc-refusal boundaries;
- protected self-promotion boundary.

The programme-wide donor-envelope checker further exercises repair+authority, representation+obligation, goal+provenance, revocation, chronology and censoring/resource combinations. It intentionally shows two things at once: the envelope fixes several naive integration errors, and it ties an ideal donor product when both implement the same correct semantics.

## 15. Discussion

### 15.1 Authority laundering is an interface failure

The important unit is not a monolithic “agent confidence.” It is a typed claim that some premise has been established for some target effect. Once interfaces are explicit, several familiar mistakes become type errors: route completeness used as task completeness; source support used as independent verification; similarity used as construct identity; replay improvement used as promotion authority.

### 15.2 Engulfing is compatible with honest credit

Absorbing a donor means retaining both its mechanism and its ownership. ORION-18 becomes broader by importing UCON, authorization logics, ETAS/FAVA, multi-authority propagation, provenance and abstention—not by claiming them. The possible contribution is the common scientific-discharge interface and the theorems about how those structures compose.

### 15.3 A tie can still be informative

If an ideal donor product ties ORION-18 exactly, the theory has still identified the conditions under which the two architectures are equivalent. The engineering question then becomes whether the shared representation reduces inconsistency or verification cost. If it does not, ORION-18 should merge into the programme synthesis or ORION-14 rather than forcing a separate paper.

## 16. Limitations and falsifiers

The calculus assumes that trusted coercions and scientific-obligation schemas are correctly specified. A bad coercion can formally authorize a bad transfer.

Support-family revocation can be expensive in large proof graphs; this manuscript proves semantics, not optimal algorithms.

The deterministic checker is small and exact. It does not establish real-agent performance.

The separate-paper hypothesis is falsified if the strongest donor product matches ORION-18 behaviorally and there is no measurable gain in consistency, proof economy, auditability or defect rate. In that case the correct publication disposition is merge/synthesis, while the theory remains complete.

## 17. Conclusion

Capability is not authority, but neither is authority a single scalar. Autonomous scientific systems combine multiple effect domains whose obligations are heterogeneous. By engulfing mature authorization, usage-control, effect, provenance and abstention mechanisms, we isolate the remaining scientific interface: **what exact target obligation does a source judgment discharge, under what scope, content identity and epoch?**

The typed calculus prevents authority laundering by construction, preserves independent derivations under revocation, distinguishes missing knowledge from established denial, and requires commit-time validity. Its negative product-equivalence theorem prevents an easy but false centralization claim and forces any future performance claim to face the strongest integrated donor baseline.

**Theory terminal:** `CLOSED_V2`.

## References

1. Alexander Pretschner et al. **Usage Control Enforcement: Present and Future.** Usage-control/UCON lineage; ongoing authorization, obligations and mutable attributes are treated as parent mechanisms.
2. Moritz Y. Becker, Cédric Fournet, and Andrew D. Gordon. **SecPAL: Design and Semantics of a Decentralized Authorization Language.** *Journal of Computer Security*, 2010.
3. Ninghui Li, Benjamin N. Grosof, and Joan Feigenbaum. **Delegation Logic: A Logic-Based Approach to Distributed Authorization.** *ACM TISSEC*, 2003.
4. Huiri Tan et al. **ETAS: An Effect-Typed Language for Agent Systems.** arXiv:2607.17780, 2026.
5. Yifan Zhang et al. **FAVA: Formal Authorization for Verified Agents with Evidence-Backed Permission Graphs.** arXiv:2607.27267, 2026.
6. **AgentAbstain.** arXiv:2607.10059, 2026. Paired act/abstain competence is treated as a donor, not a ORION-18 invention.
7. **ProvenanceGuard.** arXiv:2606.18037, 2026. Source attribution/provenance is treated as an independent donor dimension.
8. ORION Papers I–V. Native owners of reframe, search-stop, merge, assertion and self-modification authority gates embedded here.

## Artifact map

- Closed formal theory: `FORMAL_CORE_V2.md`
- Deterministic theorem checker: `../formal/check_theory_closure_v2.py`
- Donor-complete programme: `../../DONOR_COMPLETE_ORION_ENVELOPE_V1.md`
- Earlier exploratory draft: `DRAFT.md`
- Claim authority: `../CLAIM_LEDGER_V2.md`
- Reproduction: `../REPRODUCE.md`
