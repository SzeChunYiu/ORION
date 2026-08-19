# P6-X2 certificate-lifting theorem family V1

Date: 2026-08-19
Parent: #533
Status: FROZEN_BEFORE_ENUMERATION

## Research doctrine
P6 does not merely subtract modern certificate systems from its novelty surface. It absorbs their strongest mechanisms as donor certificates, then asks what additional semantics is required to preserve scientific standing under change.

## Donor certificates absorbed
The donor layer admits certificate kinds that capture, as applicable:
- runtime authorization/path compliance/history integrity/replay (Proof of Execution family);
- proposal-certification-execution and certified trace permissibility (PCE / certified-trace family);
- portable action identity, approval/runtime/outcome receipts and replay-ready proof (PCAA family);
- workflow reproducibility/provenance execution signatures (scientific workflow-signature family);
- structural purity plus signed/attested executor certificates (certified-purity family).

P6 claims none of these donor mechanisms as new.

## Scientific lift coordinates
For the bounded theorem family, a donor certificate may be lifted to preserved scientific standing only when all load-bearing scientific continuity coordinates are discharged:

1. `claim_content_binding` — the certificate/result is bound to the exact scientific claim/content object;
2. `measurement_semantics` — the measurement/operationalization semantics relevant to the claim are preserved or revalidated;
3. `evidence_semantics` — evidential meaning/support remains valid, not merely the bytes or trace;
4. `inferential_obligation` — the inference/verification obligation required for the scientific claim remains discharged;
5. `scientific_epoch` — the standing is current for the relevant evidence/model/evaluator epoch.

These coordinates are not asserted universally minimal. A donor may encode one or more under different names; if the donor exposes equivalent information and rules, the ideal enriched product must tie P6 extensionally.

## Formal objects
Let a donor certificate be `d=(kind, subject, native_validity, native_payload)`.
Let the scientific extension be `s=(c,m,e,i,t)` over the five coordinates above.

Define:

`DonorValid(d)` by the donor-native validator.

`Liftable(d,s) := DonorValid(d) AND c AND m AND e AND i AND t`.

A certificate stack/product may contain multiple donor certificates. Native certificate composition can discharge donor-native obligations, but it does not infer an absent scientific lift coordinate unless an explicit bridge rule binds that coordinate.

## Frozen theorem obligations

### T1 — donor conservativity
Projection from the lifted semantics to the donor certificate never changes the donor-native validity verdict.

### T2 — certificate-lifting separation
For every admitted donor-certificate family and every non-inert scientific lift coordinate, there exist two extensions with the same valid donor certificate and different `Liftable` judgments when only that coordinate differs.

Interpretation: a still-valid runtime/workflow/action certificate need not preserve scientific standing after a scientifically material change.

### T3 — certificate-product non-laundering
Even when all admitted donor certificates in a stack are native-valid, missing any load-bearing scientific lift coordinate blocks scientific lifting unless an explicit bridge rule establishes it.

### T4 — selective revalidation
If a transition changes a nonempty subset `S` of scientific lift coordinates, revalidating every member of `S` restores lifting when all unchanged coordinates and the donor certificate remain valid. Revalidating any proper subset of `S` does not.

This is a bounded exact-change theorem schema, not a claim that every real scientific transition exposes the same five coordinates.

### T5 — ideal enriched-product equivalence
A donor product enriched with the exact same scientific coordinates and lifting predicate is extensionally equivalent to P6 lifting. No centralization or inherent-expressivity claim is permitted.

## Falsifiers
- If a donor family already makes scientific standing a total function of its native certificate fields at the same scope, T2 is inapplicable for that embedding.
- If a claimed lift coordinate never changes any admissibility judgment, it is inert and must be removed from the active theorem instance.
- If a bridge rule from a donor certificate to a scientific coordinate is asserted without evidence/semantics, the checker must treat that coordinate as unresolved rather than true.

## Intended widening
The widest supported target is not merely `computation != scientific admissibility`. It is a reusable **certificate-lifting semantics for dynamic science**: strong execution/workflow certificates are first-class donor objects; P6 characterizes the additional conditions under which their validity can be transported into preservation of scientific standing, plus exact revalidation when transport fails.
