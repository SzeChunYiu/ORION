# P13 verifier-backed responsibility shift protocol V1

**Programme:** #977

## Goal

Test responsibility-scoped state reuse in a second, exact verifier-backed domain, distinct from the real handwritten-digit responsibility shift.

## Domain

Small CNF formulas with exact exhaustive SAT verification. Each base formula has two satisfying assignments that differ in one prospectively registered free variable. A previously verified model and compact verification certificate are sufficient for the old responsibility:

`R_old = REUSE_PREVIOUSLY_VERIFIED_MODEL_AT_EPOCH_E`.

The formula then changes by one new clause that invalidates the old model while preserving satisfiability through the alternate free-variable assignment. The new responsibility is:

`R_new = PRODUCE_VALID_MODEL_AT_EPOCH_E_PLUS_1`.

The old compact certificate is current/provenanced for epoch E but is not support for R_new at epoch E+1.

## Arms

- **RCS:** reuse the compact certificate for `R_old`; on `R_new`, detect responsibility/epoch mismatch, reopen raw CNF and solve exactly.
- **ALWAYS_RAW:** read/solve raw CNF for both responsibilities.
- **CONFIDENCE_ONLY:** reuse the prior model whenever certificate confidence is 1.0, ignoring responsibility/epoch support.
- **PROVENANCE_ONLY:** reuse whenever provenance is valid, ignoring responsibility/epoch support.

## Frozen cases

The case file registers variable count, fixed-variable pattern, free variable, old model and added clause. Cases are committed before runner/scorer code. Protected cases are disjoint from P12 SAT resource-location instances.

## Exact authority

A separate verifier checks every returned model against the exact CNF and independently enumerates the satisfying set. Candidate arms do not score themselves.

## Endpoints

- exact valid-response rate for `R_old` and `R_new`;
- stale-certificate reuse count after epoch/responsibility change;
- raw clause/literal reads;
- reopen rate;
- equality to ALWAYS_RAW verified correctness;
- independent-verifier agreement;
- deterministic replay.

## Positive gate

`P13_VERIFIER_RESPONSIBILITY_SHIFT_V1_SUPPORTED` requires:

- RCS exact correctness equals ALWAYS_RAW on every old/new responsibility episode;
- RCS performs zero stale-certificate reuse under `R_new`;
- confidence-only and provenance-only each make at least one verifier-detected invalid reuse under `R_new`;
- RCS reads strictly less raw CNF state than ALWAYS_RAW across the paired old/new workload;
- every old compact certificate is valid for `R_old` before the semantic change;
- the old certificate is explicitly revoked/not transported after the added clause;
- independent exhaustive verifier agrees;
- byte replay is deterministic.

A positive result supports verifier-backed responsibility/epoch-scoped reuse and certificate revocation. It does not by itself establish arbitrary semantic-change transport across all scientific domains.
