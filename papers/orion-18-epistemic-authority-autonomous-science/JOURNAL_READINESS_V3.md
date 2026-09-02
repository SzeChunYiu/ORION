# ORION-18 journal-readiness — V3 progress record

**Status:** `TEN_OF_THIRTEEN_SECTION2_ITEMS_DISCHARGED__THREE_OPEN`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. This records which planned items are
done and by what evidence. It promotes nothing and relaxes no criterion.

## Why this is a separate file

`JOURNAL_READINESS.md` is bound in `CONTENT_MANIFEST_V1.json` and the top-level
`SHA256SUMS`, whose identity is frozen — its checkboxes cannot be ticked in
place. This is the repository's own successor convention; ORION-18 already
carries `_V2` and `_V2_1`, neither of which is superseded or restated here.
This file is bound in `CONTENT_MANIFEST_V2.json` only.

## §2 Nearest-work closure — ten of thirteen discharged

Each row was checked by **reading match context**, not by counting keyword hits.
That distinction is not pedantic: a first sweep reported the
research-integrity field as covered in 17 of 17 A6 documents when every match
was the boilerplate header `**Scientific authority delta:** NONE` and real
coverage was zero.

| base-plan item | state | evidence |
|---|---|---|
| deontic / input-output / action logic families dispositioned atomically | **DISCHARGED** | deontic and action logic across `A6_COMPOSITION_ROUTE_V1`, `A6_DONOR_SUBTRACTION_COMPLETION_V1`, `A6_PROPOSITION12_ADVERSARIAL_V1`, `A6_PROPOSITION14_DONOR_CHECK_V1`, `A6_REMAINING_CANDIDATES_ADVERSARIAL_V1`; input/output logic in `A6_DONOR_MATRIX_V4` |
| access-control / trust-management / authorization-logic families dispositioned, including delegation revocation | **DISCHARGED** | authorization logics in `A6_DONOR_MATRIX_V2`; delegation revocation in `A6_PROPOSITION14_DONOR_CHECK_V1`; trust management in `A6_DONOR_MATRIX_V4` |
| information-flow / non-interference parent formulations dispositioned | **DISCHARGED** | `A6_DONOR_MATRIX_V3` |
| ETAS / effect-system families dispositioned | **DISCHARGED** | `A6_DONOR_SUBTRACTION_V1`, `A6_DONOR_SUBTRACTION_COMPLETION_V1` (Bernstein 1966; Lucassen & Gifford 1988) |
| FAVA / evidence-backed permission graph families dispositioned | **DISCHARGED** | `A6_DONOR_MATRIX_V3` |
| policy-card / user-permission / runtime-governance families dispositioned | **DISCHARGED** | `A6_DONOR_MATRIX_V3` |
| selective prediction / abstention / AgentAbstain family dispositioned | **DISCHARGED** | `A6_DONOR_MATRIX_V3` |
| provenance / verification / execution-tracing families dispositioned | **DISCHARGED** | `A6_DONOR_MATRIX_V2` |
| shielding / behavioural-bound agent families dispositioned | **DISCHARGED** | `A6_DONOR_MATRIX_V3` |
| research-integrity / scientific-authority families dispositioned | **DISCHARGED** | `A6_DONOR_MATRIX_V3` |
| hostile exact-composition search completed | **OPEN** | — |
| two no-material-change rounds | **OPEN** | three passes over the field list cannot satisfy a stability criterion |
| `#287` novelty certificate current | **OPEN** | — |

## What the closure costs the paper

Every one of the ten dispositions is `DONOR` or `SPECIALIZATION`. The
result-level tally is unchanged from its adversarially revised form — `DONOR` 6,
`SPECIALIZATION` 5, `SURVIVING_NEW_CONSEQUENCE` 1 — but the surviving
consequence now carries two named, unperformed re-tests, and neither is
optional:

1. **Rushby's intransitive non-interference** (SRI CSL-92-02, 1992) is a closer
   parent to the cross-domain authority-laundering result than anything V2
   checked. Intransitive non-interference already owns controlled downgrading
   through a named channel.
2. **Input/output logic**, and specifically *Permission from an Input/Output
   Perspective*, is a closer formalism for obligation and permission emission
   than classical deontic logic. The survivor's permission semantics must be
   read against it.

Both were raised by the closure itself. Until they are run, the survivor is
`PLAUSIBLE`, not defended.

A third item is not a re-test but a removed defence: SPKI/SDSI separated naming
from authorization deliberately in 1996, so that separation cannot be claimed
here.

## Net

Ten boxes discharged, three open, no criterion relaxed, and the surviving claim
carries two more threats than it did before §2 was closed. That is the expected
direction — donor subtraction can only narrow.
