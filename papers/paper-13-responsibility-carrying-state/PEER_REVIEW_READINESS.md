# P13 Peer-Review Readiness Report

**Decision:** `NOT_READY__P13A_SELF_SCORED_SAFETY_ENDPOINT`

Active terminal: `P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`, from
`P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`.

## Five-lens hostile review

### Theory / semantics

**Pass.** Exact sufficiency is stated relative to a named responsibility and defined through representation equivalence classes. The manuscript does not infer state-level insufficiency merely from a weak learner.

### Experimental design

**Fail for empirical safety.** The historical negative is retained, but the RCS
unsafe-reuse counter is the logical negation of the same declared-support
predicate that selects reuse. Certificate correctness is not independently
graded, and provenance-only duplicates unqualified reuse.

### Statistics / reproducibility

**Pass for exact semantics and historical replay; blocked for the safety
endpoint.** The exact support matrix and byte replay remain valid. The later
outcome-entailment adjudication enumerates 3,840 points: the action changes on
2,304 while the self-scored harm moves on zero and has zero opportunities.

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
- [ ] independently gold-scored unsafe-reuse primary endpoint
- [x] utility/correctness constraint
- [x] resource cost and unnecessary reopen
- [x] exact CANNOT_CHECK accounting
- [x] V1 replay-gate omission disclosed
- [x] exact runner replayed in two fresh subprocesses
- [x] V2 historical replay adjudication
- [x] active outcome-entailment authority correction
- [x] claim/evidence ledger
- [x] donor subtraction
- [ ] verifier-backed real-system responsibility shift
- [ ] certificate transport/revocation benchmark under real semantic change
- [ ] approximate-support calibration beyond exact finite worlds

## Referee-facing headline

> **Sufficiency is responsibility-scoped authority in the exact registered
> construction.** The current RCS interface conditionally refuses reuse outside
> declared support. Whether it prevents unsafe reuse under wrong or stale
> certificates is an open P13B question.
