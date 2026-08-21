# P13 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_RESPONSIBILITY-SAFE-REUSE_RESULT`

## Five-lens hostile review

### Theory / semantics

**Pass.** Exact sufficiency is stated relative to a named responsibility and defined through representation equivalence classes. The manuscript does not infer state-level insufficiency merely from a weak learner.

### Experimental design

**Pass.** The historical negative is retained. The successor has a new protocol/seed, strong confidence/provenance/always-raw controls and a prospective recoverability decision.

### Statistics / reproducibility

**Pass after explicit correction.** Exact support is deterministic. Hostile PR review found that the V1 efficacy runner omitted the protocol's byte-replay gate from the runner terminal. The V1 terminal is now non-authoritative alone. `verify_p13a_protocol_adjudication_v2.py` re-executes the exact frozen runner twice in fresh subprocess directories and requires all original scientific gates plus byte identity. Both payload SHA-256 values are `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f`. No post-hoc repair of the historical P14A finite-sanity threshold occurs.

### Novelty / donor

**Pass after subtraction.** Confidence gating, provenance, state abstraction, stale-memory detection and proof-carrying actions are donor-owned. The residual is responsibility-scoped support plus reopen/recovery semantics and an interior safety–cost efficacy result.

### Referee / reporting

**Pass for controlled scope.** The abstract reports the old negative and the new positive together. `CANNOT_CHECK` is treated as a valid outcome. Authority separation prevents the state container from self-certifying scientific novelty/safety. The replay adjudication correction is visible in the evidence chain.

## Checklist

- [x] old preregistered negative visible
- [x] negative root cause documented
- [x] independent successor protocol
- [x] exact learner-free responsibility support matrix
- [x] confidence-only baseline
- [x] provenance-only baseline
- [x] always-raw safety ceiling
- [x] unsafe-reuse primary endpoint
- [x] utility/correctness constraint
- [x] resource cost and unnecessary reopen
- [x] exact CANNOT_CHECK accounting
- [x] V1 replay-gate omission disclosed
- [x] exact runner replayed in two fresh subprocesses
- [x] authoritative V2 replay adjudication
- [x] claim/evidence ledger
- [x] donor subtraction
- [ ] verifier-backed real-system responsibility shift
- [ ] certificate transport/revocation benchmark under real semantic change
- [ ] approximate-support calibration beyond exact finite worlds

## Referee-facing headline

> **Sufficiency is responsibility-scoped authority.** A compact state can be current, provenanced and high-confidence while still lacking distinctions needed for a new responsibility. An explicit support/recovery contract eliminates such unsafe reuse in the protected benchmark without paying the cost of always reopening raw state, and the result survives the protocol's replay requirement under an explicit independent adjudicator.
