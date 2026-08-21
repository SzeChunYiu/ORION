# P13 — Responsibility-Carrying State

**Stable ID:** ORION-P13  
**Paper issue:** #666  
**RCS interface track:** #668  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript and supersedes the stale candidate path on draft PR #715.

## Status

`PEER_REVIEW_PACKAGE_READY / RCS_SAFETY_COST_SUPERIORITY_SUPPORTED / HISTORICAL_NEGATIVE_RETAINED`

### Historical negative

The old frozen P14A combined terminal remains permanently negative:

`P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET` because `0.0556640625 > 0.05`.

See `HISTORICAL_P14A_NEGATIVE_ROOT_CAUSE.md`. No threshold or terminal is retuned.

### Independent successor

P13A uses exact responsibility equivalence classes plus a new held-out safety–cost benchmark. Across 12,288 protected episodes:

- RCS unsafe reuse: **0**;
- RCS unnecessary reopen: **0**;
- RCS verified correctness: **0.980713**;
- confidence-only unsafe reuse: **0.215576**;
- provenance-only unsafe reuse: **0.396159**;
- RCS mean cost: **2.8747**;
- always-raw mean cost: **5.7319**;
- unsupported/nonrecoverable `CANNOT_CHECK`: **237/237 correct**;
- two-run SHA-256: `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f`.

Terminal: `P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED`.

## Strongest paper claim

> A compact state's authority must be scoped to the downstream responsibility it can actually support. In the registered held-out worlds, an explicit responsibility/recovery contract eliminates structurally unsafe compact-state reuse without degenerating to always reopen, while confidence and provenance alone fail to mark the same boundary.

## Artifacts

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `HISTORICAL_P14A_NEGATIVE_ROOT_CAUSE.md`
- `P13A_RCS_SAFETY_COST_RESULT_RECEIPT_V1.json`
- protected successor protocol and executable harness

## Boundary

No safety-critical deployment or real-agent superiority is claimed. External promotion beyond the controlled result requires a verifier-backed responsibility-shift domain and transport/revocation evidence under real semantic change.
