# Typed Scientific Authority across Domains: Anti-Laundering, Revocation, and Product Equivalence

**ORION-18 — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** formal cross-domain scientific-authority calculus under declared finite semantics  
**Primary route:** Journal of Automated Reasoning / AIJ Research Note after novelty closure  
**Specialist fallback:** JAAMAS / formal agent-governance venue  
**Authority:** `BOUNDED_FORMAL_CALCULUS_COMPLETE__STANDALONE_NOVELTY_AND_REAL_COERCION_SOUNDNESS_OPEN`

## Abstract

Autonomous scientific systems combine capabilities governed by different evidential standards: reframing a question, stopping a search route, merging constructs, asserting a result, and promoting a self-modification. Authorization, delegation, usage control, effect typing, provenance, abstention, revocation, and multi-authority governance already provide mature mechanisms for controlling actions. The remaining formal question is narrower: when can a valid judgment in one epistemic domain discharge the **different scientific obligation** required by another?

We develop a typed scientific-authority calculus in which every judgment and hard obligation carries domain, kind, scope, content identity, and epoch. Direct discharge requires complete type agreement. Cross-domain transport is possible only through protected coercions whose full output type composes with the next input type; domain-label reachability alone is insufficient. Authorization is non-compensatory: soft utility and generic permissions cannot replace an unresolved hard scientific obligation. `AUTHORIZED`, `DENIED`, and `CANNOT_CHECK` are distinct terminals. Authorization must remain fresh immediately before commit.

The calculus yields four bounded results. First, an anti-laundering theorem shows that every cross-type derivation must contain a valid composable coercion path. Second, alternative-derivation revocation preserves a certificate exactly when at least one complete support set remains unbroken. Third, generic permission can remain valid while the target scientific obligation is `CANNOT_CHECK`. Fourth, a shared authority calculus is extensionally equivalent to an ideal product of correctly typed per-domain gates when both receive the same coercion registry, freshness rules, and derivation/revocation semantics. Centralization is therefore not an inherent scientific advantage.

A deterministic standard-library checker covers the complete 5×5 direct-discharge matrix, scope-incompatible coercion paths, trusted and untrusted controls, stale epochs, terminal distinctions, alternative derivations, non-compensatory blockers, protected self-promotion, and 160 shared/product equivalence cases. The executable checks support transcription and boundary testing; analytic statements carry the formal authority. The paper does not establish the semantic soundness of real coercions, empirical superiority over donor systems, a universally minimal authority ontology, or external scientific authority. Its contribution is a portable anti-laundering interface and exact equivalence boundary for the declared calculus.

## 1. Introduction

An agent can execute an action correctly without possessing the scientific authority to change the state that action affects. A planner may successfully generate a reframe. A search system may exhaust one route. A mapper may find two constructs similar. A verifier may approve an execution. None of those local successes automatically establishes the different premise required to reformulate a question, stop a task, merge measurements, promote a claim, or authorize self-modification.

The recurring error is **authority laundering**: a valid judgment from one layer is converted into permission in another layer without a rule establishing that the target scientific obligation has been discharged.

The donor landscape is broad. Authorization and trust-management logics formalize grants, delegation, scope, credentials, and revocation. Usage control treats authorization as ongoing. Effect systems and evidence-backed permission graphs bind policy to action traces. Provenance and execution receipts establish source and process identities. Abstention systems distinguish action from refusal. Multi-authority governance combines decisions across components.

This paper does not reintroduce those mechanisms under new names. It asks a typed interface question that remains after they are included:

> Under what conditions can a judgment established in one scientific obligation domain license an effect in another?

The answer must distinguish domain, judgment kind, scope, content, and time; preserve alternative complete derivations under partial revocation; and admit a negative theorem showing when a shared architecture has no expressive advantage over a correctly integrated product.

## 2. Authority-relevant scientific effects

Let the registered effect domains be

`{REFRAME, SEARCH_STOP, MAP_MERGE, ASSERT, SELF_MODIFY}`.

An effect request contains

`e=(id, domain, operation, scope, payload, epoch)`.

Every authority-relevant judgment has complete type

`tau=(domain, kind, scope, content, epoch)`.

A hard obligation names the exact judgment type capable of discharging it, together with any additional mandatory premises. The authority context contains active judgments, obligations, grants, registered coercions, revocation state, derivation lineage, and history.

The five domains are a registered finite model of cross-domain scientific effects. They are not claimed to be a universal or minimal ontology.

## 3. Full derivation typing

Typing only the final authorization token is insufficient. A foreign-domain judgment can be converted into a generic intermediate marker and then presented as if the target obligation had been met. Laundering has already occurred before the final check.

The calculus therefore types the complete evidence-to-obligation derivation.

### Direct discharge

Judgment `j:tau_j` directly discharges obligation `o:tau_o` only when the complete types match and every mandatory premise is satisfied.

If an available fact establishes an incompatible type, stale epoch, invalid scope, or blocker, the terminal is `DENIED`. If a mandatory premise cannot currently be established or refuted, the terminal is `CANNOT_CHECK`.

These terminals have different repair routes. Denial is not repaired by collecting unrelated confidence. `CANNOT_CHECK` may be repaired by acquiring the missing evidence or restoring the required evaluator.

## 4. Typed coercions

Cross-domain use is not prohibited. It must be justified by a protected transformation.

A coercion is a partial typed rule

`c:tau -> tau'`

with a trusted registration root, semantic premises, lineage, and validity interval. Two coercions compose only when the entire output type of the first matches the entire input type of the second.

This blocks domain-only paths. A rule may map a `REFRAME` judgment scoped to `map-A` into a `SEARCH_STOP` judgment for `map-A`; another rule may accept a `SEARCH_STOP` judgment for `map-B` and produce `ASSERT`. A domain graph contains a path, but the typed derivation rejects it because the middle scopes do not compose.

### Theorem 1 — typed anti-laundering

Assume ordinary inference preserves judgment type and only registered coercions may change type. Any derivation using source judgment `tau` to discharge target obligation `tau'!=tau` contains a valid composable coercion path from `tau` to `tau'`.

**Proof idea.** Induct on derivation height. The first type change cannot be ordinary inference and must therefore be a registered coercion. Apply the same argument to each later change. Complete type matching is required at every composition boundary. ∎

The theorem is syntactic-semantic within the declared calculus. It does not prove that a proposed real-world coercion is scientifically sound; sound coercion registration is a separate authority obligation.

## 5. Non-compensatory authorization

Authorization requires:

- every hard obligation discharged;
- no active blocker;
- a valid grant;
- scope, content, effect, and epoch identity matched to the proposed commit;
- current validity immediately before commit.

Soft utility and confidence can rank already admissible actions but cannot compensate for a missing hard premise.

### Proposition 2 — finite penalties do not create unbounded vetoes

In an extensible additive score with a finite blocker penalty, sufficiently large positive evidence can overcome the penalty unless the positive range is externally bounded. An absolute blocker therefore requires a conjunctive, lexicographic, or separate veto layer.

The proposition is scoped to extensible additive policies. It does not claim that every finite-dimensional scalar formulation is incapable of encoding a veto.

## 6. Generic permission versus scientific discharge

Access control and scientific authority answer different questions.

### Theorem 3 — permission/discharge separation

There exists a context in which a valid generic permission authorizes an operation at the policy level while the target scientific effect remains `CANNOT_CHECK` because a mandatory scientific obligation is unresolved.

**Construction.** Supply a valid in-scope generic grant and no generic blocker. Require a scientific obligation—such as independent verification of an assertion—for which the necessary evidence is unavailable. The generic action is permitted; the scientific promotion terminal is unresolved. ∎

This is not a criticism of generic authorization. The error occurs only when its native judgment is silently promoted into a different scientific claim.

## 7. Alternative-derivation revocation

A simple descendant graph cannot distinguish conjunctive and alternative support.

- `A AND B` means both premises are required.
- `A OR B` means either complete derivation can support the certificate.

Represent authorization certificate `kappa` by a support family

`S(kappa)={S_1,...,S_m}`,

where each `S_i` is a complete sufficient premise set.

### Theorem 4 — exact revocation

After revoking premise set `R`, certificate `kappa` remains valid if and only if at least one complete support set is entirely valid and disjoint from the revoked premises.

Revoking one line of evidence therefore preserves a certificate supported by an independent complete derivation. If every complete derivation is broken, the certificate is invalidated. ∎

The theorem gives the exact logical object a revocation engine must preserve; it does not claim that real support families are automatically complete or correctly extracted.

## 8. Commit-time validity

An authorization certificate binds the exact effect and state in which the effect will commit. A later refusal cannot retroactively make an irreversible earlier action safe. A certificate from an old epoch cannot be replayed after a relevant policy or evidence change without an explicit freshness proof.

These properties are inherited from ongoing-authorization and modern agent-governance donors. Their role here is to prevent a correct cross-domain derivation from being reused after its bindings change.

## 9. Shared calculus versus ideal product

A shared authority engine may be easier to audit or implement consistently, but centralization is not automatically more expressive.

Define an ideal product with one correctly typed gate per domain and shared global stores for coercions, freshness, derivations, and revocation.

### Theorem 5 — shared/product equivalence

For every registered request and authority context, the shared calculus and the ideal typed product return the same terminal.

**Proof idea.** Both evaluate the same direct-discharge relation, coercion paths, blockers, grants, freshness predicates, support families, and terminal order. Module boundaries differ; inference semantics do not. ∎

This negative result controls the novelty claim. A scientific advantage can arise only if a real product omits or inconsistently implements a required global relation—for example cross-domain coercion composition, shared revocation lineage, scope/epoch matching, or non-compensatory obligations. Architecture alone earns no credit.

## 10. Embedded domain interfaces

The five registered effect domains connect to earlier bounded ORION objects.

- **REFRAME:** generating a new formulation is separate from evidence that licenses changing a protected responsibility.
- **SEARCH_STOP:** route exhaustion is distinct from task completion; open or censored obligations block global stop.
- **MAP_MERGE:** similarity is not construct identity; referent, measurement, context, and obstruction obligations remain explicit.
- **ASSERT:** content-bound support and independent promotion obligations govern claim authority.
- **SELF_MODIFY:** replay success is candidate evidence; protected evaluation, negative history, and external attestation can remain required.

The calculus must conservatively reproduce native decisions before claiming a useful cross-domain synthesis. Exact embedding and donor saturation remain part of standalone novelty closure.

## 11. Deterministic formal support

A standard-library checker exercises:

- all 25 direct source/target-domain pairs;
- scope-incompatible coercion composition despite domain-level reachability;
- trusted positive and untrusted negative coercion controls;
- stale epochs and post-hoc refusal boundaries;
- `AUTHORIZED`, `DENIED`, and `CANNOT_CHECK`;
- alternative complete derivations under revocation;
- non-compensatory blocker examples;
- protected self-promotion;
- 160 shared-calculus/ideal-product equivalence cases.

The checker imports no production agent framework. It validates the executable interpretation of the finite calculus and includes controls capable of failing. It is same-programme verification, not external proof or empirical replication.

## 12. What the current paper establishes

The bounded formal evidence supports:

1. complete-type anti-laundering under registered coercion semantics;
2. non-compensatory hard obligations and distinct authority terminals;
3. exact preservation of alternative complete derivations under revocation;
4. generic-permission/scientific-discharge separation;
5. extensional equivalence between a shared calculus and an information-equivalent ideal product;
6. deterministic coverage of the registered finite semantics.

It does not establish:

- semantic soundness of real cross-domain coercions;
- empirical superiority or reduced unsafe actions;
- distinct novelty after complete authorization/effect-system saturation;
- exact conservative embeddings of every donor/native domain;
- external scientific authority;
- universal minimality of the type coordinates.

## 13. Relation to prior work

Authorization logic, trust management, usage control, effect systems, evidence-backed permission graphs, multi-authority propagation, provenance, revocation, abstention, non-interference, deontic/action logic, and agent shielding are donor-owned.

The residual candidate is the scientific-obligation interface connecting these mature mechanisms: full derivation typing, cross-domain coercion composition, support-family revocation, permission/discharge separation, and the shared/product equivalence theorem. Whether this residual is sufficient for a standalone paper depends on final nearest-work and internal-overlap closure; the manuscript does not declare that gate solved by prose.

## 14. Limitations

The calculus is finite and declarative. Trusted roots and coercions are premises whose real scientific soundness must be established externally. Support families may be incomplete in natural systems. The embedded domains do not exhaust scientific authority. A perfectly integrated product ties by theorem, so engineering centralization requires separate evidence about consistency, audit cost, or defects.

No protected cross-capability benchmark result is claimed in this paper. Prospective empirical protocols remain future evidence identities.

## 15. Reproducibility and availability

A release should bind:

- formal type and terminal definitions;
- direct-discharge and coercion rules;
- non-compensatory authorization semantics;
- support-family revocation theorem;
- shared/product equivalence proof;
- deterministic checker and negative controls;
- donor/ownership map;
- exact nearest-work and standalone-identity disposition.

The final PDF and package must be rebuilt from one adopted source after current novelty and donor-saturation review.

## 16. Conclusion

A valid judgment in one domain cannot authorize a different scientific effect merely because the two domains are connected in a broad policy graph. Cross-domain authority requires a complete typed coercion path, fresh bindings, and discharge of every hard scientific obligation. Alternative complete derivations must survive partial revocation, and generic action permission can coexist with unresolved scientific authority.

A shared engine and a correctly typed product are extensionally equivalent when they implement the same semantics. The paper's contribution is therefore a portable anti-laundering calculus and a precise boundary on architectural claims. Real coercion soundness, empirical benefit, and standalone novelty remain separate gates.

---

## Editorial production note — not manuscript prose

This final master is a bounded theory paper, not a promotion receipt. Before standalone filing, close the exact nearest-work/novelty and ORION-11–ORION-15 overlap matrices, prove or explicitly premise the claimed coercion soundness conditions, reconcile with `manuscript/FINAL.md`, `FORMAL_CORE_V1.md`, `CLAIM_LEDGER_V1.md`, and the deterministic checker, and rebuild the selected target source, PDF, bibliography, figures, archive and manifests. If donor saturation leaves no distinct residual, merge the formal interface into ORION-14/programme theory rather than forcing a separate submission.
