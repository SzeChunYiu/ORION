# ORION-16–ORION-18 five-role adversarial review log V1

**Date:** 2026-08-17  
**Status:** active internal research review; not independent peer review.  
**Purpose:** record how each material finding is pressure-tested from multiple expert functions before it enters a manuscript/claim ledger.

The roles below are analytical review functions, not claims that five external human reviewers participated.

## Review roles

1. **Formal logician (FL)** — theorem syntax/semantics, quantifiers, countermodels, proof strength.
2. **Formal-methods engineer (FME)** — executable semantics, finite checking, process/effect models, reproducibility.
3. **Epistemic-navigation theorist (ENT)** — search/planning/partial-observation/representation-change semantics.
4. **Authorization/governance logician (AGL)** — permission, delegation, revocation, information flow, custody, authority laundering.
5. **Scientific editor / novelty auditor (SENA)** — ORION-11–ORION-15 ownership, donor uniqueness, related-work breadth, claim authority and publication boundaries.

---

## Finding R1 — ORION-16 whole-state commutation was over-strong

### Initial statement
Strongly separated deterministic mechanics commute: `tau_n(tau_m(E)) = tau_m(tau_n(E))`.

### Role pressure
- **FL:** false if `E` contains an ordered history `H`; the two runs can encode different event order even when current scientific state is identical.
- **FME:** concurrent/process semantics already distinguish state equivalence from trace equivalence. Use an explicit scientific projection and a partial-order/trace quotient.
- **ENT:** navigation/research replay may care about chronology later, so deleting history merely to rescue equality would weaken the scientific object.
- **AGL:** authorization/revocation can be epoch/chronology dependent; history is not semantically disposable.
- **SENA:** do not turn the repair into a novelty claim; trace equivalence is mature concurrency machinery.

### Disposition
**REPAIR.** Current theorem is:

\[
\pi_{sci}(m;n(E))=\pi_{sci}(n;m(E)),
\qquad H_{mn}\equiv_I H_{nm},
\]

under strong separation. Whole-state equality is struck.

### Remaining falsifier
Construct a later policy whose result differs by event order; show that current-state commutation alone does not imply future-policy equivalence unless chronology is outside that policy's read set.

---

## Finding R2 — ORION-17 “no closure certificate” premise was over-strong

### Initial statement
Any finite history lacking a closure certificate has both a complete and an incomplete observationally indistinguishable extension.

### Role pressure
- **FL:** absence of a named certificate does not logically guarantee two admissible completions. The world class could already exclude one completion for another reason.
- **FME:** the bounded generator intentionally *constructs* a rich extension class; it does not prove every model class has that property.
- **ENT:** the correct navigation object is observational/extension ambiguity, with certificate absence as a practical sufficient route under an explicit richness premise.
- **AGL:** task-stop authority depends on what the contract accepts as discharge, not on a syntactic token called certificate alone.
- **SENA:** abstract/conclusion language must not omit the richness/ambiguity qualification.

### Disposition
**REPAIR.** Theorem is now conditioned on **extension ambiguity**. A separate corollary derives ambiguity from missing closure only under an explicit rich-open-world premise.

### Remaining falsifier
Add a deterministic case with no closure-certificate object but only one admissible completion, proving the concepts are not equivalent by definition.

---

## Finding R3 — ETAS/FAVA are donors, not reasons to abandon width

### Literature pressure
ETAS supplies typed effects, action traces, residual obligations and policy-constrained commit semantics. FAVA supplies Permission IR, evidence-backed permission graphs and deterministic pre-effect authorization.

### Role pressure
- **FL:** ORION-16/ORION-18 must not rederive generic effect or authorization syntax as if new.
- **FME:** both systems should be conservative embedding targets; ORION can reuse their strongest machinery.
- **ENT:** typed effect/permission objects can become route/reframe commit guards but do not solve support transport under a changing atlas.
- **AGL:** ORION-18's domain typing must be compared directly to these systems and classical trust-management logic.
- **SENA:** protect donor uniqueness explicitly in abstract/related work/claim ledger.

### Disposition
**ADOPT + COMPOSE.** The possible ORION residual moves upward to cross-domain epistemic composition, dependency reopening/revocation and evidence/closure transport.

### Remaining falsifier
If ETAS/FAVA or a classical authorization/non-interference encoding directly represents all ORION-18 cross-domain cases without semantic loss, ORION-18 collapses into programme synthesis.

---

## Finding R4 — selective reopening/rollback is strongly prior

### Literature/internal pressure
ORION-11 already owns reconstruction-specific dependency reopening. TMS/ATMS and current dependency-guided rollback repair supply justification/dependency repair and preservation of unaffected state.

### Role pressure
- **FL:** the graph-minimality lemma can be formally correct while non-novel.
- **FME:** benchmark against donor-specific rollback, not only full-reset/no-reset strawmen.
- **ENT:** in ORION-17, reopening semantics becomes interesting when the representation/objective changes and support transport is partial.
- **AGL:** the same dependency skeleton may support authority revocation but the semantic terminal differs.
- **SENA:** native ORION-11 reopening stays `MERGE_EXISTING`; only cross-type/cross-domain composition may survive.

### Disposition
**ADOPT / DO NOT CLAIM IN ISOLATION.** Investigate a parameterized dependency-invalidation skeleton across ORION-16/ORION-17/ORION-18.

---

## Finding R5 — ORION-17 must absorb planning abstraction/representation change

### Parent-field pressure
Planning research already studies abstraction, representation-language expressivity, plan-preserving homomorphisms, learned plannable representations and adaptive abstraction.

### Role pressure
- **FL:** `rho:T->T'` is not sufficient novelty; maps need semantic preservation obligations.
- **FME:** donor-native plan preservation should be a conservative embedding test.
- **ENT:** the live discriminator is whether evidence/support, objective meaning and closure authority transport across a chart change.
- **AGL:** the permission to change representation is separate from the validity of the transported closure.
- **SENA:** “dynamic topology” should not be used as a novelty phrase without parent-field comparison.

### Disposition
**WIDEN.** ORION-17 becomes an epistemic atlas with partial chart/objective maps and support/closure transport rules.

### Remaining falsifier
If a standard planning abstraction/homomorphism plus ORION-12 stopping rules reproduces all atlas judgments and benchmark behavior, merge ORION-17 into ORION-11/ORION-12.

---

## Finding R6 — ORION-18 must absorb trust-management/authorization logic

### Parent-field pressure
Delegation Logic frames authorization as proof of compliance. SecPAL supplies logical authorization queries, controlled delegation/revocation and sound/complete/terminating evaluation under stated conditions. Other authorization logics add mechanized proof theory and information-flow constraints.

### Role pressure
- **FL:** typed grants, derivations, delegation and revocation are mature logical objects.
- **FME:** ORION-18 can reuse a trust-management backend rather than inventing one.
- **ENT:** search/task closure is one authority domain, not the whole authorization problem.
- **AGL:** cross-domain coercions must be pressure-tested against policy composition and non-interference; default non-fungibility may be standard typed information flow.
- **SENA:** ORION-18 should be terminated if the cross-domain object is just a renamed authorization logic.

### Disposition
**ADOPT + HOSTILE OVERLAP TEST.** ORION-18's paper-level discriminator is cross-epistemic-domain composition in autonomous-science workflows, not generic authorization.

---

## Finding R7 — ORION-14 already owns local authority laundering

### Internal pressure
ORION-14's current README records a local authority-laundering falsifier for scientific assertion/verification.

### Role pressure
- **FL:** ORION-18 cannot claim the failure class generically from a single-domain restatement.
- **FME:** build cases where producer modules are individually correct and only the *composition* launders authority.
- **ENT:** route-stop -> task-stop/assertion is a natural cross-domain example, but ORION-12 owns the local route judgment.
- **AGL:** define laundering as a derivational type error across domains absent an explicit sound coercion.
- **SENA:** use the term “cross-domain authority laundering” in ORION-18, not unqualified “authority laundering” as a headline novelty.

### Disposition
**NARROW CLAIM, WIDEN TEST.** ORION-18 keeps cross-domain anti-laundering only.

---

## Finding R8 — additive blocker theorem needs a boundedness qualifier

### Initial temptation
“No additive score can represent a hard blocker.”

### Role pressure
- **FL:** false for a bounded finite-dimensional score space; a sufficiently dominant finite penalty can simulate a veto.
- **FME:** the checker constructs the result only for extensible/unbounded positive evidence.
- **ENT:** unrelated to ORION-17 except as a stopping-gate caution.
- **AGL:** the useful policy point is semantic explicitness of hard blockers, not a universal impossibility claim.
- **SENA:** preserve the limitation in abstract/claim ledger.

### Disposition
**QUALIFY.** The theorem applies to unbounded/extensible positive evidence with finite penalties and a fixed threshold.

---

## Finding R9 — evidence transport and closure transport must be separated

### Synthesis insight
A representation/objective change may preserve a content-bound observation while changing the meaning or completeness condition of the obligation it previously closed.

### Role pressure
- **FL:** define separate maps for evidence/support and obligation semantics; one must not imply the other.
- **FME:** add a fixture where evidence identity is unchanged but closure reopens after goal change.
- **ENT:** this is a plausible central ORION-17 discriminator across SAGA/world-model/planning-abstraction donors.
- **AGL:** any automatic conversion from “valid evidence” to “new-domain closure” is an authority coercion and must be explicit.
- **SENA:** promising synthesis, but still `FORMAL_CONSEQUENCE/CANNOT_CHECK` for novelty until parent fields are saturated.

### Disposition
**KEEP AS CROSS-PAPER HYPOTHESIS.** It links ORION-17 transport to ORION-18 non-fungibility without making either paper own the other's native mechanism.

---

## Finding R10 — repair/reopening and revocation may share one dependency skeleton

### Synthesis insight
ORION-16 state reopening, ORION-17 closure reopening and ORION-18 authority revocation all propagate invalidity downstream while attempting to preserve independent support.

### Role pressure
- **FL:** investigate a parameterized theorem over a dependency relation plus domain-specific validity predicate.
- **FME:** implement one generic finite enumerator with pluggable terminal semantics.
- **ENT:** ORION-17 needs `open/CANNOT_CHECK`, not merely deletion.
- **AGL:** ORION-18 needs alternative derivation support so revoking one path need not revoke a certificate with another valid proof.
- **SENA:** a common theorem could become ORION-16/programme synthesis rather than three duplicate claims.

### Disposition
**OPEN GENERALIZATION TARGET.** Do not yet assign paper ownership.

---

## Finding R11 — width requires negative controls

### Role pressure
- **FL:** greater expressivity is not a universal dominance theorem.
- **FME:** every widened mechanism needs cases where it should remain inactive.
- **ENT:** ORION-17 must be penalized for unnecessary reframes and useless dispersion.
- **AGL:** ORION-18 must preserve clean authorized coverage and avoid security-by-total-refusal.
- **SENA:** positive results without negative controls invite scope inflation.

### Disposition
**MANDATORY.** #353 includes an intentionally hostile domain where the generalization should not help.

---

## Finding R12 — current survival hypotheses

### ORION-16
**Alive but unproven:** donor-faithful history-aware epistemic effect/repair algebra with a genuine composition theorem/transfer result.

**Immediate collapse condition:** all surviving properties reduce to ORION-11 + TMS/effect/process/authorization donors without an additional discriminator.

### ORION-17
**Alive and currently strongest conceptually:** epistemic atlas with representation/objective change, support transport/reopening and fail-closed closure authority.

**Immediate collapse condition:** standard planning abstraction/model revision + ORION-11/ORION-12 reproduces all formal/benchmark behavior.

### ORION-18
**High conceptual leverage / highest overlap pressure:** typed cross-domain coercion, non-fungibility and dependency revocation across heterogeneous epistemic effects.

**Immediate collapse condition:** standard authorization/non-interference/policy composition directly represents the same cases, or independent domain gates perform equally on cross-domain attacks.

---

## Review rule going forward

Every theorem, benchmark metric, donor assimilation and headline sentence should append a short entry to this log or a successor version recording:

- the strongest objection from each relevant role;
- the exact repair or rejection;
- the surviving scope;
- the next falsifier.

This log is an internal adversarial-research artifact and must not be presented as external peer review.