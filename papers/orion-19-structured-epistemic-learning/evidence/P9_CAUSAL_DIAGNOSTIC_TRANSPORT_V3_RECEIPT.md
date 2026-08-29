# P9 causal-diagnostic transport V3 receipt (uncertainty-aware decision rule)

**Session:** R5 revival, 2026-08-28 (LUNARC wtR5)
**Protocol:** `top_tier/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V3.md` (registered before outcome access)
**Runner:** `top_tier/run_causal_diagnostic_transport_v3.py`
**Run artifact:** `evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_RUN.json`
(receipt_sha256 `8312b62bb30589ee365a2acb6f02beba2348eef8bd010ab691ebd8bf4dfe4b34`,
executed twice, outputs byte-identical)

## Claim chain

| | V1 (frozen) | V2 (frozen) | V3 (this receipt) |
|---|---|---|---|
| decision rule | hard threshold on point estimate | hard threshold on R=24 ensemble mean | LCB95 = mean − 1.96·sd(ddof=1)/√n ≥ target |
| diagnosis accuracy | 0.8 | 1.0 | 1.0 |
| probe/protected agreement | n/a (single split) | True (all 5) | True (all 5) |
| half-draw decision stability | n/a | **False (D-A)** — the failed clause | **True (both digits cells, own-data halves)** |
| terminal | `..._V1_SUPPORTED` | `..._V2_GATE_NOT_MET` | `..._V3_SUPPORTED` |

Everything except the decision rule is frozen from V2: cells, arms, frozen targets
(D-A 0.965, D-I 0.95, executable 1.0), frozen costs (8.0/2.0/12.0), R=24, draw seeds,
and the full per-draw pipeline.

## One-stage failure attribution (carried from NR-04, not re-attributed)

V2's only failing clause was half-draw decision stability on D-A: protected half-1
mean 0.9662 crosses the 0.965 target while half-0 (0.9625) and the full mean (0.9644)
do not. Stage-1 attribution (`evidence/P9_NR04_TRANSPORT_STAGE1_ATTRIBUTION.json`):
decision margin 0.001161 vs single-split binomial SD 0.009840 (noise-to-margin 8.47).
The failing stage is exactly one: the decision rule applies a hard threshold inside
its own noise band. The repair channel is bitwise-lossless (max abs reconstruction
error 0.0); splits, targets, and the pipeline are not the problem.

## The lever (mechanic, not outcome tuning)

Uncertainty-aware target satisfaction: an arm reaches the target iff its ensemble
LCB95 does. Applied uniformly to every cell, every split, and every half — halves
decide from their own data only (no sd borrowing). No target, cost, seed, or cell
changed; the D-A target was NOT relaxed.

## Result (all pre-registered gates green)

- terminal `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_SUPPORTED`, `failing_clauses: []`
- diagnosis accuracy 1.0 (generic 0.2), executable 1.0, digits 1.0
- false compute escalations 0 vs generic 4; mean registered cost regret 0.0
- D-A: probe and protected LCBs below 0.965 → decision `CANNOT_CHECK` on both
  sides; all four half decisions `CANNOT_CHECK` → **stable abstention**
- D-I: `INFORMATION` both sides (protected LCB 0.9609990859868461 ≥ 0.95), half-stable
- Registered predictions matched observed outcomes in every particular.

## Verdict

**POSITIVE vs the strongest parent (V2), on the parent's own failed clause.** V3
keeps every V2 success (agreement, accuracy 1.0, escalation control) and repairs the
one failed clause. The D-A protected cell is NOT converted to a pass: under the frozen
V1 gold rule it remains `CANNOT_CHECK` — now as a decision-stable, mechanistically
grounded abstention rather than a threshold artifact. Claim boundary unchanged: no
universal resource law, no touch on the Qwen scaling negative.
