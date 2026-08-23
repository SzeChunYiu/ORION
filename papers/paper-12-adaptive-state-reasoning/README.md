# P12 — Adaptive State–Reasoning Co-Design

**Stable ID:** ORION-P12  
**Paper issue:** #665  
**Shared accounting:** #664  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript and supersedes the stale candidate path on draft PR #715.

## Status

`P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED / CONTROLLED_EQUAL_ACTION_WORLD`

`P12_ACTIVE_CLAIM_AUTHORITY_V2.json` is the current authority. It retains the
P12A comparison failure and activates only P12B's equal-action, exact-allocation
signal-complementarity claim.

### Protected result

Under the identical two-unit budget over 16 held-out families:

- joint state–reasoning allocator: **0.858154** mean verified success;
- adaptive state only: `0.463135`;
- adaptive reasoning only: `0.452759`;
- fixed `(1,1)`: `0.515503`;
- mean joint gain over the better one-axis adaptive policy: **+0.334717**;
- family-block 95% CI: **[0.286008, 0.382693]**;
- worst-family joint gain: **+0.158203**;
- two-run replay SHA-256: `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`.

Historical terminal: `P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED`.

Active authority terminal: `P12A_SUPERIORITY_AUTHORITY_WITHHELD`.

A capability-matched replay gives both one- and two-signal arms the same four
allocations. The mean gain is `+0.040771`, its family-block interval is
`[0.031006, 0.050659]`, the worst-family gain is `+0.001953`, and the original
positive gate is not met.

### P12B equal-action successor

P12B gives the two-signal and both one-signal policies the identical four-action
set and two-unit budget, then scores the exact required allocation. Across 32
independent family RNG blocks (1,024 technical episodes each), mean gain over
the stronger one-signal policy is **0.253906**. The prospectively corrected
stratified family-block 95% bootstrap interval is **[0.251221, 0.256653]**;
minimum family gain is **0.196289**, and every fixed noise stratum passes.

Active terminal: `P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED`.

## Strongest paper claim

> In the registered equal-action four-regime world, a policy reading both noisy
> pre-outcome signals selects the exact required allocation more often than the
> stronger policy reading either signal alone.

## Artifacts

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `P12A_MATCHED_BUDGET_RESULT_RECEIPT_V1.json`
- `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`
- `P12_ACTIVE_CLAIM_AUTHORITY_V1.json` (historical P12A boundary)
- `P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1.json`
- `P12_ACTIVE_CLAIM_AUTHORITY_V2.json` (current)
- protected protocol and executable harness

## Boundary

P12B authorizes only controlled equal-action signal complementarity. Real-system
authority still requires matched end-to-end state, model/search, verifier/tool
and latency receipts.
