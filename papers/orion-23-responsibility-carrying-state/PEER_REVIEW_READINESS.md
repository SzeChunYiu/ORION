# P13 Peer-Review Readiness Report

Authority here is split by sub-claim: the two decisions below govern P13B and
P13A respectively, and neither overrides the other.

**Decision (P13B, authenticated-certificate claim):**
`READY_FOR_CONTROLLED_P13B_CLAIM__EXTERNAL_VALIDATION_OPEN`

Active terminal: `P13_CONTROLLED_AUTHENTICATED_CERTIFICATE_AUTHORITY_SUPPORTED`,
from `P13_ACTIVE_CLAIM_AUTHORITY_V2.json`. P13A's self-scored result remains
historical and withheld under `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`.

**Decision (P13A, empirical safety-cost endpoint):**
`NOT_READY__P13A_SELF_SCORED_SAFETY_ENDPOINT`

Active terminal: `P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`, from
`P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`.

## Five-lens hostile review

### Theory / semantics

**Pass.** Exact sufficiency is stated relative to a named responsibility and defined through representation equivalence classes. The manuscript does not infer state-level insufficiency merely from a weak learner.

### Experimental design

**Pass for the bounded P13B finite panel.** Gold support is computed outside the
certificate, and all four corruption worlds have nonzero opportunities before
scoring. This is not externally adjudicated evidence.

### Statistics / reproducibility

**Pass for exact finite-panel reporting.** P13B enumerates all 30 state-task cases
and reports exact denominators rather than a population interval. Two fresh
subprocess payloads are byte-identical.

### Novelty / donor

**Bounded.** The exact core and controlled authenticated-certificate corruption
result are supported; external safety novelty and generalization remain open.

### Referee / reporting

**Pass with scope boundary.** The manuscript distinguishes P13A's self-scored
failure, P13B's locally authored finite-world gold, and external validation.
**Fail for empirical safety.** The historical negative is retained, but the RCS
unsafe-reuse counter is the logical negation of the same declared-support
predicate that selects reuse. Certificate correctness is not independently
graded, and provenance-only duplicates unqualified reuse.

### Statistics / reproducibility

**Pass for exact semantics and historical replay; blocked for the safety
endpoint.** The exact support matrix and byte replay remain valid. The later
outcome-entailment adjudication enumerates 3,840 points: the action changes on
2,304 while the self-scored harm moves on zero and has zero opportunities.

That is a methodological negative, and the distinction matters. The endpoint did
not fail to show a safety effect; it was incapable of showing one. Harm was
scored by the same construction that produced the action, so across all 3,840
enumerated points there is no configuration in which harm could have moved ---
zero opportunities, not zero movements. A self-entailed endpoint cannot
discriminate between a safe system and an unsafe one, so no reading of P13A's
result, favourable or adverse, is licensed about safety. It is preserved for
what it does establish: that the endpoint's construction, not the system's
behaviour, is what the number measured.

### Novelty / donor

**Pass only for the exact conditional core.** The interior safety–cost result is
not authorized until independently graded P13B.

### Referee / reporting

**Fail for an efficacy paper.** The exact/conditional result is reportable, but
the manuscript must not say the protected benchmark empirically eliminates
unsafe reuse.

## Checklist

- [x] old preregistered negative visible
- [x] negative root cause documented
- [x] independent successor protocol
- [x] exact learner-free responsibility support matrix
- [x] confidence-only baseline
- [x] provenance-only baseline
- [x] always-raw safety ceiling
- [x] certificate-independent gold-scored unsafe-reuse primary endpoint
- [ ] independently gold-scored unsafe-reuse primary endpoint
- [x] utility/correctness constraint
- [x] resource cost and unnecessary reopen
- [x] exact CANNOT_CHECK accounting
- [x] V1 replay-gate omission disclosed
- [x] exact runner replayed in two fresh subprocesses
- [x] V2 historical replay adjudication
- [x] active outcome-entailment authority correction
- [x] four corruption worlds with live opportunity denominators
- [x] authenticated-certificate hostile terminal tests
- [x] claim/evidence ledger
- [x] donor subtraction
- [ ] verifier-backed real-system responsibility shift
- [ ] certificate transport/revocation benchmark under real semantic change
- [ ] approximate-support calibration beyond exact finite worlds

## Referee-facing headline

> **Sufficiency is responsibility-scoped authority in the exact registered
> construction.** In P13B's controlled finite panel, authenticated RCS rejects
> omitted, overbroad, forged and stale certificates with zero gold-scored unsafe
> reuse; external witness correctness and real-agent safety remain open.
