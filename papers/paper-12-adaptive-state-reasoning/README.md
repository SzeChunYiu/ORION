# P12 — Adaptive State–Reasoning Co-Design

**Stable ID:** ORION-P12  
**Paper issue:** #665  
**Shared accounting:** #664  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript and supersedes the stale candidate path on draft PR #715.

## Status

`P12A_SUPERIORITY_AUTHORITY_WITHHELD / P12B_CAPABILITY_MATCHED_SUCCESSOR_REQUIRED`

`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` is the current authority. The
historical protected run and replay remain valid execution records, but they do
not authorize a signal-count superiority claim because the one-axis policies
were also denied half of the winner's allocation set.

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

## Strongest paper claim

> P12A demonstrates a deterministic controlled resource-allocation construction,
> but its observed advantage cannot be attributed to the second signal until a
> prospectively frozen P12B holds the action set fixed across arms.

## Artifacts

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `P12A_MATCHED_BUDGET_RESULT_RECEIPT_V1.json`
- `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`
- `P12_ACTIVE_CLAIM_AUTHORITY_V1.json`
- protected protocol and executable harness

## Boundary

This is historical controlled evidence with current superiority authority
withheld. P12B must first match action capability; real-system authority then
requires matched end-to-end state, model/search, verifier/tool and latency
receipts.
