# P13 — Responsibility-Carrying State

**Stable ID:** ORION-P13  
**Paper issue:** #666  
**RCS interface track:** #668  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript and supersedes the stale candidate path on draft PR #715.

## Status

`P13_EXACT_RESPONSIBILITY_CORE_SUPPORTED / P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`

### Historical negative

The old frozen P14A combined terminal remains permanently negative:

`P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET` because `0.0556640625 > 0.05`.

See `HISTORICAL_P14A_NEGATIVE_ROOT_CAUSE.md`. No threshold or terminal is retuned.

### Historical P13A execution

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

Historical terminal: `P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED`.

Active authority terminal:
`P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`, from
`P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`. The RCS rule reuses exactly when
its certificate says `supported`; the primary harm counter calls a reuse unsafe
exactly when that same certificate says `not supported`. The zero is therefore
self-entailed and has no reachable harm denominator.

## Strongest paper claim

> In the exact registered finite world, sufficiency is relative to a named
> downstream responsibility and the RCS interface refuses reuse when its
> declared support omits that responsibility. Empirical safety–cost superiority
> remains unestablished until P13B grades reuse against support defined
> independently of the certificate.

## Artifacts

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `HISTORICAL_P14A_NEGATIVE_ROOT_CAUSE.md`
- `P13A_RCS_SAFETY_COST_RESULT_RECEIPT_V1.json`
- `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`
- `P13_ACTIVE_CLAIM_AUTHORITY_V1.json`
- protected successor protocol and executable harness

## Boundary

No empirical safety superiority, safety-critical deployment or real-agent
superiority is currently authorized. P13B must make unsafe reuse reachable with
independent gold support before external promotion is considered.
