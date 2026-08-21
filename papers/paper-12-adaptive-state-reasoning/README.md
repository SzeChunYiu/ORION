# P12 — Adaptive State–Reasoning Co-Design

**Stable ID:** ORION-P12  
**Paper issue:** #665  
**Shared accounting:** #664  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript and supersedes the stale candidate path on draft PR #715.

## Status

`PEER_REVIEW_PACKAGE_READY / CONTROLLED_MATCHED_BUDGET_SUPERIORITY_SUPPORTED / REAL_SYSTEM_GATE_OPEN`

P12 now has a protected empirical terminal rather than only a theory/protocol draft.

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

Terminal: `P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED`.

## Strongest paper claim

> When held-out task families differ in whether marginal computation is valuable for state accessibility, downstream reasoning, both or neither, a frozen policy that can allocate one matched total budget across both loci strictly outperforms policies allowed to adapt only state or only reasoning.

## Artifacts

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `P12A_MATCHED_BUDGET_RESULT_RECEIPT_V1.json`
- protected protocol and executable harness

## Boundary

This is a controlled superiority result. Real LLM/prover/agent superiority remains open until state-construction work, model/search work, verifier/tool calls and latency are jointly receipted under matched end-to-end resources.
