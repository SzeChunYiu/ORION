# ORION-16–ORION-18 expert closure review V2

**Date:** 2026-08-18  
**Purpose:** adversarial closure review after donor-complete expansion.

These are analytical review roles used to force independent objections. They are not represented as external human peer reviewers.

## Panel

1. **Formal epistemologist / KR theorist** — definitions, quantifiers, support/closure semantics, hidden premises.
2. **Programming-languages / formal-methods expert** — effect typing, incremental computation, operational correspondence, finite checking.
3. **Open-world navigation / planning expert** — search, POMDP, representation abstraction/refinement, stopping, goal evolution.
4. **Authorization / security logician** — grants, usage control, coercions, revocation, non-interference, commit-time policy.
5. **Experimental-design / measurement expert** — baselines, negative controls, donor-product comparisons, non-compensatory metrics.
6. **Scientific editor / novelty auditor** — ORION-11–ORION-15 ownership, donor credit, claim ledgers, publication disposition.

---

# ORION-16 review

## Formal epistemologist objection

Strict descendant reopening omits a directly changed certified claim.

**Resolution:** V2 uses root-inclusive affected set

\[
Aff_D(E,X)=(X\cap Q_{cert})\cup(Desc_D(X)\cap Q_{cert}).
\]

Theorem 1 and graph-relative minimality were rewritten accordingly.

**Terminal:** CLOSED.

## Formal-methods objection

Read/write disjointness alone does not prove commutation when history, obligation, authority, provenance or dependency state is shared.

**Resolution:** V2 defines full scientific semantic read/write footprints and proves equality only of current scientific projection; ordered histories are merely independent-trace equivalent.

**Terminal:** CLOSED.

## Formal-methods donor objection

Self-adjusting computation, TMS/ATMS and modern dependency-guided rollback already own major change-propagation/repair structures.

**Resolution:** absorbed as donors. ORION-16 adds no generic selective-repair novelty. The discriminating theorem is typed erasure: identical bare computation/dependency semantics may have different scientific admissibility because obligations/authority/provenance differ.

**Terminal:** CLOSED WITH DONOR OWNERSHIP.

## Authorization objection

A preservation rule controlled by the changing mechanic can become self-authorization.

**Resolution:** preservation certificates bind exact change/scope/content/epoch, require a protected issuer, and cannot preserve a directly changed certified root.

**Terminal:** CLOSED UNDER CERTIFICATE-SOUNDNESS PREMISE.

## Experimental-design objection

ORION-16 can trivially beat a dependency-only baseline by adding fields the baseline never attempts to model.

**Resolution:** donor-complete programme requires comparison against a product containing dependency repair + incremental computation + effect typing + authorization/provenance. ORION-16 superiority is not asserted by the theory manuscript.

**Terminal:** THEORY CLOSED; PERFORMANCE OPTIONAL/OPEN.

## Editorial disposition

ORION-16 is a coherent theory paper if framed as scientific-admissibility semantics over engulfed repair/effect donors, not as the invention of epistemic change or dependency repair.

**Panel recommendation:** KEEP AS INDEPENDENT THEORY CANDIDATE.

---

# ORION-17 review

## Formal epistemologist objection

No closure certificate does not logically imply an observationally indistinguishable incomplete extension.

**Resolution:** stopping theorem is stated directly on extension ambiguity. Deriving ambiguity from missing exclusion evidence requires an explicit extension-richness premise.

**Terminal:** CLOSED.

## Navigation/planning objection

The old “new topology adds a reachable goal” witness proves only that a larger model is more expressive, not that representation change itself matters.

**Resolution:** V2 freezes latent states, actions, dynamics, goals and retained raw sensing. Only the representation map is refined. Coarse aliasing prevents one policy from acting differently on two starts; refinement exposes an already-retained discriminating bit. Reverse coarsening is a harmful-reframe control.

**Terminal:** CLOSED.

## Planning-abstraction donor objection

Planning abstraction, situation-calculus refinement, schema/lens mappings and generalized-planning abstraction already have sound/complete preservation results.

**Resolution:** engulfed as preservation-certificate suppliers. ORION-17 does not re-prove or claim their plan/data preservation; it asks whether their witness also covers evidence identity, target scientific obligation semantics, coverage/defeaters and task-stop authority.

**Terminal:** CLOSED WITH DONOR OWNERSHIP.

## Goal/world-model donor objection

SAGA and self-evolving world models already change objectives/models.

**Resolution:** absorbed. ORION-17's separation theorem states that identical evidence may survive while new objective satisfaction fails; model updates with unchanged vocabulary are separated from representation/objective changes requiring transport analysis.

**Terminal:** CLOSED.

## Experimental-design objection

A topology-changing system can manufacture gains by reframing every hard task.

**Resolution:** harmful-coarsening controls are mandatory; future comparisons include a donor product with graph/POMDP + abstraction + goal/world-model evolution. Reframe benefit and harmful-reframe rate are separate measures.

**Terminal:** THEORY CLOSED; EMPIRICAL SUPERIORITY OPTIONAL/OPEN.

## Editorial disposition

ORION-17 has the clearest independent scientific object: evidence/closure preservation across changing representations/objectives under open-world stopping constraints.

**Panel recommendation:** KEEP AS INDEPENDENT THEORY CANDIDATE; HIGHEST SEPARATE-PAPER CONFIDENCE.

---

# ORION-18 review

## Authorization expert objection

Typed authorization, delegation, revocation, ongoing/commit-time authorization, multiple authorities and provenance-aware governance are already mature or rapidly developing.

**Resolution:** absorbed: Delegation Logic, SecPAL, UCON, ETAS, FAVA, AgentBound, authorization propagation, provenance systems, abstention systems and recent provenance/non-amplification guards are donors. ORION-18 does not claim those components.

**Terminal:** CLOSED WITH BROAD DONOR OWNERSHIP.

## Authorization expert objection

Typing only the final authorization token misses laundering through an untyped intermediate `SAT` result.

**Resolution:** V2 types evidence-to-obligation discharge by domain/kind/scope/content/epoch. Every type change requires a protected composable coercion.

**Terminal:** CLOSED.

## Authorization expert objection

Domain-level coercion reachability can hide scope/kind/content mismatch.

**Resolution:** coercions compose on the complete type; a finite counterexample rejects a domain-compatible but scope-incompatible chain.

**Terminal:** CLOSED.

## Formal-methods objection

A descendant graph does not distinguish AND from OR derivations during revocation.

**Resolution:** authorization lineage is a family of complete support sets. A certificate survives iff one complete support set remains valid.

**Terminal:** CLOSED.

## Scientific-epistemic objection

Generic permission and target scientific authority are being conflated.

**Resolution:** V2 proves a separation theorem: an in-scope generic grant may be valid while a hard scientific obligation is missing, yielding `CANNOT_CHECK` rather than `AUTHORIZED`.

**Terminal:** CLOSED.

## Experimental-design objection

A shared calculus may appear better only because independent gates were given weak or inconsistent interfaces.

**Resolution:** V2 proves shared/product equivalence when a product uses the same typed discharge, coercion, freshness and revocation semantics. The donor-complete programme therefore treats the ideal typed product as the strongest baseline.

**Terminal:** CLOSED NEGATIVE RESULT.

## Editorial disposition

ORION-18 is theory-complete. Separate-paper value depends on whether the scientific-discharge interface plus product-equivalence theorem is editorially substantial. A later empirical study may test consistency/proof economy/auditability, but is not required to make the theory logically complete.

**Panel recommendation:** KEEP AS THEORY/NEGATIVE-RESULT CANDIDATE; MERGE INTO ORION-14/PROGRAMME ONLY IF EDITORIAL OR STRONG-PRODUCT EVALUATION SHOWS NO DISTINCT VALUE.

---

# Cross-paper panel conclusion

## Shared preservation ladder

The donor-complete envelope separates:

1. identity preservation;
2. computation/support preservation;
3. evidence-meaning preservation;
4. target scientific-obligation discharge;
5. commit authority.

The panel agrees that lower-level preservation must never be silently promoted to a higher level without an explicit witness/coercion.

## “Engulf before narrowing” disposition

The panel rejects a strategy of deleting donor mechanisms to manufacture novelty. Every strong donor structure remains eligible for inclusion in ORION.

Narrowing occurs only at the **claim level** after:

- donor-native judgments are embedded;
- cross-donor challenges are attempted;
- the ideal donor-product baseline is considered;
- the remaining theorem/measurement is identified.

## Theory closure verdict

- `P6_THEORY = CLOSED_V2`
- `P7_THEORY = CLOSED_V2`
- `P8_THEORY = CLOSED_V2`
- `DONOR_COMPLETE_ENVELOPE = SPECIFIED_AND_CHECKED_BY_FINITE_SUITE`
- `BROAD_COMPONENT_NOVELTY = REJECTED`
- `REAL_SYSTEM_SUPERIORITY = NOT CLAIMED`

No remaining panel objection identifies a missing mathematical definition/theorem required by the declared V2 paper scope. Remaining work is submission-format/CI/literature-delta or optional empirical strengthening, not a half theory.
