# ORION-19 causal diagnostic transport protocol V3 (uncertainty-aware target satisfaction)

**Programme:** P9 / ORION-19 revival lane NR-04 residual
**Registered:** 2026-08-28, BEFORE any V3 outcome access
**Predecessors:** `P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md` (frozen), `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V2.md` (frozen)
**Supersedes:** nothing. V1 and V2 artifacts stay immutable; this protocol is registered as the next prospective revival step.

## Why this protocol exists (one-stage failure attribution)

The NR-04 stage-1 attribution (`evidence/P9_NR04_TRANSPORT_STAGE1_ATTRIBUTION.json`)
attributed the D-A protected-cell `CANNOT_CHECK` to the **evaluation channel**, not the
repair channel: the repaired-arm decision margin is `0.0011613` while the single-split
binomial SD is `0.009840` (noise-to-margin ratio `8.47`). The V2 ensemble channel
(mean over R=24 frozen partition re-draws) then restored probe/protected decision
agreement and full diagnostic accuracy (`1.0`), but **failed its own pre-registered
half-draw decision-stability clause**: the D-A protected half-1 mean (`0.9662`) crosses
the frozen `0.965` target while half-0 (`0.9625`) and the full mean (`0.9644`) do not
(`evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_RUN.json`, terminal
`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET`).

The residual failure stage is therefore exactly ONE stage: **the decision rule** — a hard
threshold applied to a point estimate whose ensemble standard error straddles the frozen
target. The repair channel is bitwise-lossless (max abs reconstruction error `0.0`), the
split distribution is not shifted (V2 probe and protected means agree), and the target is
not moving. Only the rule that converts estimated levels into "reaches target" decisions
ignores estimation uncertainty.

## The one lever (mechanic improvement, not outcome tuning)

Replace hard-threshold target satisfaction with **uncertainty-aware target
satisfaction**:

> arm `k` *reaches target* `T` on a split iff
> `LCB95(k) = mean(k) - 1.96 * sd(k) / sqrt(n_draws) >= T`,
> where `mean`/`sd` (ddof=1) are computed over that split's ensemble draws.

The decision is still the **cheapest arm (frozen cost table) among arms that reach the
target**, else `CANNOT_CHECK`. Frozen targets (`D-A 0.965`, `D-I 0.95`, executable `1.0`),
costs (`INFORMATION 8.0`, `ACCESSIBILITY 2.0`, `COMPUTATION 12.0`), cells, arms, draw
count `R=24`, draw seeds (`outer 20261101+k`, `inner 20261201+k`, `k=0..23`), and the full
per-draw pipeline are **identical to V2**. Nothing about the D-A target is relaxed; the
rule simply refuses to claim target transport that the data's own noise cannot support.
This is the standard statistical repair for threshold decisions made inside the noise
band, applied uniformly to every cell and both splits.

## Half-draw decision stability under V3

The V2 stability clause is kept and re-evaluated under the same LCB rule, honestly: each
half (`draws 0..11`, `draws 12..23`) decides **using only that half's own data** —
`halfmean - 1.96 * halfsd(ddof=1) / sqrt(12) >= T` — cheapest-arm rule as above. A cell is
half-stable iff all four half decisions (probe/0, probe/1, protected/0, protected/1)
equal the full-data decision. No sd borrowing from the full set.

## Pre-registered gates (all required)

1. All V1-mirroring clauses of V2 (diagnostic accuracy `>= 4/5` and `> generic`,
   executable accuracy `1.0`, at least one digits cell correct, false compute escalation
   `*2 <= generic false escalations`, every actionable prediction reaches the frozen
   target on protected, mean registered cost regret `<= 1.0`).
2. Probe/protected decision agreement on all five cells.
3. Half-draw decision stability on both digits cells **under the V3 LCB rule**.
4. Zero retuning: the runner reads targets/costs/seeds only from this protocol and V2;
   any difference from V2 in the per-draw pipeline is a protocol violation (asserted by
   digest comparison of the shared pipeline code path).

Terminal: `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_SUPPORTED` iff all gates pass, else
`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_GATE_NOT_MET` with the failing clause named.

## Registered predictions (before outcome access)

- `D-A`: probe and protected LCBs fall below the frozen `0.965` target
  (`mean ~0.964`, `sd ~0.0084`, `SE ~0.0017`, so `LCB ~0.961`); predicted decision
  `CANNOT_CHECK` on both sides, half-stable. The D-A protected cell therefore stays a
  **negative/abstain cell** — this protocol does NOT aim to make D-A pass, only to make
  its abstention decision-stable.
- `D-I`: information LCB `~0.961 >= 0.95` → `INFORMATION` both sides, half-stable.
- Executable cells: sd `0`, LCB = mean, decisions unchanged from V1/V2.
- If any prediction above is wrong, the receipt records the deviation verbatim; the
  terminal is whatever the gates compute.

## Claim boundary

V3 repairs the *decision procedure's* noise-robustness on the same five-cell lattice. It
does not establish a universal resource law, does not touch the protected Qwen scaling
negative (`LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`), and does not convert the D-A
protected cell into a positive: under the frozen V1 gold rule the D-A protected gold
remains `CANNOT_CHECK` (level-target ordering unresolved at this dataset size). What V3
can earn is that the diagnostic **correctly and stably abstains** where its evidence is
inside its own noise band.
