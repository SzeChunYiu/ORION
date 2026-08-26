# P13 manuscript result addendum V1 — responsibility-scoped reuse across real-data and verifier-backed shifts

This addendum updates the submission-facing P13 result story without erasing the historical P14A negative or expanding beyond the current evidence.

## Revised central result

P13 now has two prospectively governed responsibility-shift evaluations with qualitatively different authority:

1. a non-synthetic handwritten-digits responsibility change with learned compact state;
2. an exact verifier-backed CNF responsibility/epoch change with independently checkable correctness and certificate revocation.

Together they support the paper's core claim that **state sufficiency is responsibility-relative** and that confidence/provenance continuity does not by itself authorize reuse after responsibility or semantic state changes.

## Study A — real handwritten digits

A compact state learned for parity responsibility is reused or reopened when the later responsibility becomes exact digit identity. Across 17,970 episodes:

- RCS combined accuracy: `0.9435169727`;
- RCS exact-digit accuracy: `0.9699499165`;
- RCS parity accuracy: `0.9170840289`;
- always-raw has exactly the same task accuracies;
- RCS reads `33` floats/episode versus `64` for always-raw, a `48.4375%` reduction;
- RCS unsupported exact-digit reuse: `0`;
- confidence-only exact-digit accuracy: `0.3956594324`, unsupported reuse `0.7774067891`;
- provenance-only/unqualified exact-digit accuracy: `0.2376182526`, unsupported reuse `1.0`.

The compact representation can therefore be current, provenanced and highly confident for the old responsibility while being structurally inadequate for the stronger one.

## Study B — exact CNF responsibility/epoch shift

Twelve protected CNF cases were frozen before the runner/checker. Each base formula fixes four variables and leaves one free, yielding two satisfying models. The previously verified model/certificate is valid under the old responsibility at epoch `E`.

A new unit clause changes the formula/epoch, invalidates that model, and leaves exactly one alternate model. This creates a precise certificate-transport question rather than a weak-model effect.

Across 24 old/new-responsibility episodes per arm:

| Arm | Exact verifier-correct | Stale reuse | Raw literal reads |
|---|---:|---:|---:|
| RCS | 24/24 | 0 | 60 |
| ALWAYS_RAW | 24/24 | 0 | 108 |
| CONFIDENCE_ONLY | 12/24 | 12 | 0 |
| PROVENANCE_ONLY | 12/24 | 12 | 0 |

RCS matches the always-raw verifier ceiling and reduces raw literal reads by `44.4444%`. The old certificate is explicitly valid before the change and explicitly non-transportable afterward. A second independent implementation reproduces the exact counts.

## What the combined result earns

The two studies jointly establish a cross-domain pattern:

- sufficiency is indexed by responsibility, not by representation alone;
- confidence/provenance are not support certificates for an upgraded responsibility;
- safe reuse need not collapse to always-raw: RCS matches the correctness ceiling while saving state access in both domains;
- semantic/epoch change can revoke an old certificate even when execution/provenance remains healthy;
- exact verifier authority and learned real-data behavior point to the same responsibility-scoped boundary.

## What remains outside the claim

P13 should not imply that all responsibilities form a total ladder, that every semantic change is captured by the CNF construction, or that P13 supplies scientific truth labels for open-ended research agents.

A still-broader research-agent responsibility claim would require independent external scientific adjudication. The current paper can instead present the now-earned claim at the higher but defensible level:

> **Responsibility-scoped state reuse is a cross-domain systems principle:** on both learned real data and exact verifier-backed state transitions, compact state can remain valid for one responsibility while becoming invalid for another, and an explicit support/reopen contract recovers always-raw correctness with lower state-access cost.

## Evidence authority

Canonical evidence:

- `top_tier/P13_REAL_RESPONSIBILITY_SHIFT_PROTOCOL_V1.md` and its execution ledger entry;
- `top_tier/P13_VERIFIER_RESPONSIBILITY_SHIFT_PROTOCOL_V1.md`;
- `top_tier/P13_VERIFIER_RESPONSIBILITY_SHIFT_RESULT_RECEIPT_V1.md`;
- `TOP_TIER_PROMOTION_V1.md`.

The historical finite-sample sentinel negative remains retained and must not be erased or retrospectively retuned.
